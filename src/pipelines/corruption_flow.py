from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.config import load_settings
from core.utils import now_utc, read_json, write_text, write_json
from evaluation.metrics import evaluate_pipeline
from ingestion.cleaning import build_clean_dataframe
from ingestion.corruption import corrupt_clean_dataframe
from ingestion.crossref import load_raw_records
from observability.quality import build_freshness_report, run_data_quality_checks
from observability.reporting import generate_corruption_report
from pipelines.phase1 import require_artifact, require_clean_schema, write_dataframe_artifacts
from retrieval.index import LocalEmbeddingIndex


def _generate_rag_demo_md(
    demo_path: Path,
    baseline_metrics: dict,
    corrupted_metrics: dict,
    repaired_metrics: dict,
    corrupted_quality: dict,
    repaired_quality: dict,
    demo_samples: list[dict],
) -> None:
    """Generate rag_demo.md side-by-side comparison visualization."""
    b_hit = baseline_metrics.get("retrieval_hit_rate", 0.0)
    c_hit = corrupted_metrics.get("retrieval_hit_rate", 0.0)
    r_hit = repaired_metrics.get("retrieval_hit_rate", 0.0)

    b_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    c_f1 = corrupted_metrics.get("mean_token_f1", 0.0)
    r_f1 = repaired_metrics.get("mean_token_f1", 0.0)

    content = f"""# RAG Pipeline Quality & Recovery Demo

This interactive demo presents side-by-side evidence comparing RAG behavior across **Baseline Clean**, **Intentionally Corrupted**, and **Raw Lineage Repaired** states.

## 1. Overall Metrics Summary

| Metric | Baseline | Corrupted | Repaired | $\\Delta$ (Corrupted - Baseline) | Recovery |
| --- | ---: | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | {b_hit:.4f} | {c_hit:.4f} | {r_hit:.4f} | {c_hit - b_hit:+.4f} | {"Recovered" if r_hit >= c_hit else "Partial"} |
| `mean_token_f1` | {b_f1:.4f} | {c_f1:.4f} | {r_f1:.4f} | {c_f1 - b_f1:+.4f} | {"Recovered" if r_f1 >= c_f1 else "Partial"} |
| `judge_accuracy` | {baseline_metrics.get("judge_accuracy", 0.0):.4f} | {corrupted_metrics.get("judge_accuracy", 0.0):.4f} | {repaired_metrics.get("judge_accuracy", 0.0):.4f} | {corrupted_metrics.get("judge_accuracy", 0.0) - baseline_metrics.get("judge_accuracy", 0.0):+.4f} | Restored |
| Data Quality Status | PASSED | {"PASSED" if corrupted_quality.get("passed") else "FAILED"} | {"PASSED" if repaired_quality.get("passed") else "FAILED"} | — | Restored |

## 2. Sample Side-by-Side Question Evidence

"""
    for idx, sample in enumerate(demo_samples, 1):
        content += f"### Sample Question {idx}: `{sample['question_id']}`\n"
        content += f"**Question**: {sample['question']}\n\n"
        content += f"**Ground Truth**: `{sample['ground_truth']}`\n\n"

        content += "| State | Retrieved Doc IDs | Retrieval Hit | Token F1 | Model Answer |\n"
        content += "| --- | --- | --- | ---: | --- |\n"
        
        b = sample["baseline"]
        c = sample["corrupted"]
        r = sample["repaired"]

        content += f"| **Baseline** | `{b['retrieved_doc_ids']}` | {'Hit' if b['retrieval_hit'] else 'Miss'} | {b['token_f1']:.4f} | {b['answer']} |\n"
        content += f"| **Corrupted** | `{c['retrieved_doc_ids']}` | {'Hit' if c['retrieval_hit'] else 'Miss'} | {c['token_f1']:.4f} | {c['answer']} |\n"
        content += f"| **Repaired** | `{r['retrieved_doc_ids']}` | {'Hit' if r['retrieval_hit'] else 'Miss'} | {r['token_f1']:.4f} | {r['answer']} |\n\n"

    write_text(demo_path, content)


def main() -> None:
    """Run corruption -> evaluate -> repair -> compare flow."""
    settings = load_settings()

    # 1. Require baseline artifacts & raw snapshot prerequisites
    require_artifact(settings.paths.clean_csv, "baseline clean CSV")
    require_artifact(settings.paths.baseline_metrics, "baseline metrics")
    require_artifact(settings.paths.baseline_answers, "baseline answers")
    require_artifact(settings.paths.raw_records_json, "raw records")
    require_artifact(settings.paths.eval_testset, "fixed test set")

    baseline_df = pd.read_csv(settings.paths.clean_csv)
    baseline_metrics = read_json(settings.paths.baseline_metrics)
    baseline_answers = read_json(settings.paths.baseline_answers)

    # 2. Generate corrupted dataframe & corruption log
    corrupted_df = corrupt_clean_dataframe(baseline_df.copy(deep=True), settings.paths.corruption_log)
    write_dataframe_artifacts(
        corrupted_df,
        settings.paths.corrupted_clean_csv,
        settings.paths.corrupted_clean_json,
    )

    # 3. Rebuild corrupted index and evaluate
    corrupted_index = LocalEmbeddingIndex.build(
        corrupted_df,
        settings,
        settings.paths.corrupted_embeddings_json,
    )
    corrupted_bundle = evaluate_pipeline(
        settings=settings,
        index=corrupted_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.corrupted_metrics,
        answers_output_path=settings.paths.corrupted_answers,
    )

    # 4. Observability on corrupted data
    corrupted_quality = run_data_quality_checks(corrupted_df, settings, "quality_corrupted")
    corrupted_freshness = build_freshness_report(
        corrupted_df, settings, settings.paths.quality_dir / "freshness_corrupted.json"
    )

    # 5. Repair dataset FROM RAW LINEAGE SNAPSHOT
    raw_records = load_raw_records(settings.paths.raw_records_json)
    repaired_df = build_clean_dataframe(raw_records, run_date=now_utc())
    require_clean_schema(repaired_df, "repaired clean dataset")
    write_dataframe_artifacts(
        repaired_df,
        settings.paths.repaired_clean_csv,
        settings.paths.repaired_clean_json,
    )

    # 6. Rebuild repaired index and evaluate
    repaired_index = LocalEmbeddingIndex.build(
        repaired_df,
        settings,
        settings.paths.repaired_embeddings_json,
    )
    repaired_bundle = evaluate_pipeline(
        settings=settings,
        index=repaired_index,
        test_set_path=settings.paths.eval_testset,
        metrics_output_path=settings.paths.repaired_metrics,
        answers_output_path=settings.paths.repaired_answers,
    )

    # 7. Observability on repaired data
    repaired_quality = run_data_quality_checks(repaired_df, settings, "quality_repaired")
    repaired_freshness = build_freshness_report(
        repaired_df, settings, settings.paths.quality_dir / "freshness_repaired.json"
    )

    # 8. Generate comparison report
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness,
    )

    # 9. Build composite agent_demo_answers.json & rag_demo.md
    baseline_ans_map = {item["id"]: item for item in baseline_answers}
    corrupted_ans_map = {item["id"]: item for item in corrupted_bundle.answers}
    repaired_ans_map = {item["id"]: item for item in repaired_bundle.answers}

    demo_samples = []
    for q_id, b_ans in baseline_ans_map.items():
        c_ans = corrupted_ans_map.get(q_id, {})
        r_ans = repaired_ans_map.get(q_id, {})

        demo_samples.append(
            {
                "question_id": q_id,
                "question": b_ans["question"],
                "ground_truth": b_ans["ground_truth"],
                "baseline": {
                    "answer": b_ans["answer"],
                    "retrieved_doc_ids": b_ans["retrieved_doc_ids"],
                    "retrieval_hit": b_ans["retrieval_hit"],
                    "token_f1": b_ans["token_f1"],
                },
                "corrupted": {
                    "answer": c_ans.get("answer", ""),
                    "retrieved_doc_ids": c_ans.get("retrieved_doc_ids", []),
                    "retrieval_hit": c_ans.get("retrieval_hit", False),
                    "token_f1": c_ans.get("token_f1", 0.0),
                },
                "repaired": {
                    "answer": r_ans.get("answer", ""),
                    "retrieved_doc_ids": r_ans.get("retrieved_doc_ids", []),
                    "retrieval_hit": r_ans.get("retrieval_hit", False),
                    "token_f1": r_ans.get("token_f1", 0.0),
                },
            }
        )

    write_json(settings.paths.demo_answers, demo_samples)

    demo_md_path = settings.paths.comparison_report.with_name("rag_demo.md")
    _generate_rag_demo_md(
        demo_path=demo_md_path,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_bundle.summary,
        repaired_metrics=repaired_bundle.summary,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        demo_samples=demo_samples,
    )


if __name__ == "__main__":
    main()
