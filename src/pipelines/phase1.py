from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.config import Settings, load_settings
from core.utils import now_utc, read_json, write_csv, write_json
from evaluation.metrics import evaluate_pipeline
from evaluation.testset import build_test_set
from ingestion.cleaning import build_clean_dataframe
from ingestion.crossref import fetch_source_records, load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_phase1_report
from retrieval.index import LocalEmbeddingIndex

REQUIRED_CLEAN_COLUMNS = [
    "paper_id",
    "title",
    "summary",
    "published",
    "abs_url",
    "pdf_url",
    "authors_joined",
    "categories_joined",
    "text_for_embedding",
    "age_days",
    "summary_chars",
]


def require_artifact(path: Path, label: str) -> None:
    """Verify that an artifact path exists."""
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact '{label}' at: {path}")


def require_clean_schema(df: pd.DataFrame, label: str) -> None:
    """Validate that dataframe complies with clean schema contracts."""
    if df is None or df.empty:
        raise ValueError(f"Clean schema validation failed for '{label}': DataFrame is empty.")

    missing_cols = [col for col in REQUIRED_CLEAN_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Clean schema validation failed for '{label}': missing required columns {missing_cols}"
        )

    if df["paper_id"].isna().any() or (df["paper_id"].astype(str).str.strip() == "").any():
        raise ValueError(f"Clean schema validation failed for '{label}': blank or null paper_id found.")

    if not df["paper_id"].is_unique:
        raise ValueError(f"Clean schema validation failed for '{label}': duplicate paper_id values found.")

    if (df["text_for_embedding"].astype(str).str.strip() == "").any():
        raise ValueError(
            f"Clean schema validation failed for '{label}': blank text_for_embedding found."
        )


def write_dataframe_artifacts(df: pd.DataFrame, csv_path: Path, json_path: Path) -> None:
    """Helper to write both CSV and JSON artifacts for a dataframe."""
    write_csv(df, csv_path)
    write_json(json_path, df.to_dict(orient="records"))


def main() -> None:
    """Run baseline Phase 1 pipeline end-to-end."""
    settings = load_settings()

    # 1. Load or fetch raw records
    if settings.refresh_source or not settings.paths.raw_records_json.exists():
        records = fetch_source_records(settings)
    else:
        records = load_raw_records(settings.paths.raw_records_json)

    # 2. Clean data & validate schema
    clean_df = build_clean_dataframe(records, run_date=now_utc())
    require_clean_schema(clean_df, "baseline clean dataset")
    write_dataframe_artifacts(clean_df, settings.paths.clean_csv, settings.paths.clean_json)

    # 3. Build Chroma vector index for baseline
    index = LocalEmbeddingIndex.build(clean_df, settings, settings.paths.embeddings_json)

    # 4. Load or build evaluation test set
    if settings.refresh_test_set or not settings.paths.eval_testset.exists():
        build_test_set(clean_df, settings.paths.eval_testset)
    require_artifact(settings.paths.eval_testset, "baseline test set")

    # 5. Run evaluation pipeline
    eval_bundle = evaluate_pipeline(
        settings=settings,
        index=index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.baseline_metrics,
        answers_output_path=settings.paths.baseline_answers,
    )

    # Post-evaluation audit assertion
    test_set_items = read_json(settings.paths.eval_testset)
    if eval_bundle.summary.get("samples") != len(test_set_items):
        raise RuntimeError(
            f"Metric sample count ({eval_bundle.summary.get('samples')}) does not match test set size ({len(test_set_items)})."
        )

    # 6. Observability: Data Quality & Freshness
    quality_payload = run_data_quality_checks(clean_df, settings, "quality_baseline")
    freshness_payload = build_freshness_report(clean_df, settings, settings.paths.freshness_report)

    # Save extra copy to quality_dir/freshness_baseline.json for consistency
    write_json(settings.paths.quality_dir / "freshness_baseline.json", freshness_payload)

    # 7. Generate Phase 1 markdown report
    source_summary = {
        "source_api": settings.source_api,
        "source_query": settings.source_query,
        "source_filter": settings.source_filter,
        "raw_count": len(records),
        "clean_count": len(clean_df),
    }
    generate_phase1_report(
        report_path=settings.paths.baseline_report,
        source_summary=source_summary,
        metrics=eval_bundle.summary,
        quality=quality_payload,
        freshness=freshness_payload,
    )

    # 8. Build initial demo answers from baseline (first 3 samples)
    demo_samples = []
    for item in eval_bundle.answers[:3]:
        demo_samples.append({
            "question_id": item["id"],
            "question": item["question"],
            "ground_truth": item["ground_truth"],
            "baseline": {
                "answer": item["answer"],
                "retrieved_doc_ids": item["retrieved_doc_ids"],
                "retrieval_hit": item["retrieval_hit"],
                "token_f1": item["token_f1"],
            }
        })
    write_json(settings.paths.demo_answers, demo_samples)


if __name__ == "__main__":
    main()
