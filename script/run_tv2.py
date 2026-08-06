"""Script chạy riêng phần TV2: cleaning + test set generation."""
from __future__ import annotations

import json
from datetime import datetime, UTC

from core.config import load_settings
from core.utils import write_csv, write_json
from ingestion.crossref import load_raw_records
from ingestion.cleaning import build_clean_dataframe
from evaluation.testset import build_test_set


def main() -> None:
    settings = load_settings()
    run_date = datetime.now(UTC)

    # 1. Load raw records từ TV1
    print(f"[TV2] Loading raw records from {settings.paths.raw_records_json} ...")
    records = load_raw_records(settings.paths.raw_records_json)
    print(f"[TV2] Loaded {len(records)} raw records.")

    # 2. Clean
    print("[TV2] Building clean dataframe ...")
    df = build_clean_dataframe(records, run_date)
    print(f"[TV2] Clean dataframe: {len(df)} rows, columns: {list(df.columns)}")

    # 3. Save CSV
    write_csv(df, settings.paths.clean_csv)
    print(f"[TV2] Saved CSV -> {settings.paths.clean_csv}")

    # 4. Save JSON
    write_json(settings.paths.clean_json, json.loads(df.to_json(orient="records", force_ascii=False)))
    print(f"[TV2] Saved JSON -> {settings.paths.clean_json}")

    # 5. Build test set
    print("[TV2] Building test set ...")
    questions = build_test_set(df, settings.paths.eval_testset)
    print(f"[TV2] Test set: {len(questions)} questions -> {settings.paths.eval_testset}")

    # 6. Quick validation
    assert df["paper_id"].is_unique, "paper_id not unique!"
    assert "age_days" in df.columns, "age_days column missing!"
    assert all(
        all(k in q for k in ["id", "question_type", "question", "ground_truth", "ground_truth_doc_ids"])
        for q in questions
    ), "Test set missing required keys!"

    print()
    print("=== TV2 DONE ===")
    print(f"  papers_clean.csv : {settings.paths.clean_csv}")
    print(f"  papers_clean.json: {settings.paths.clean_json}")
    print(f"  test_set.json    : {settings.paths.eval_testset}")
    print(f"  Rows: {len(df)}, Questions: {len(questions)}")


if __name__ == "__main__":
    main()
