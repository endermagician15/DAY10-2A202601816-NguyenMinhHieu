from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from core.config import Settings
from core.utils import now_utc, write_json


def run_data_quality_checks(df: pd.DataFrame, settings: Settings, report_name: str) -> dict[str, Any]:
    """Run comprehensive data quality checks on a cleaned/corrupted dataframe and write results."""
    total_rows = len(df)
    
    check_row_count = total_rows > 0
    check_paper_id = bool("paper_id" in df.columns and df["paper_id"].notna().all() and df["paper_id"].is_unique)
    check_title = bool("title" in df.columns and not df["title"].isna().any() and (df["title"].astype(str).str.strip().str.len() > 0).all())
    check_summary = bool("summary_chars" in df.columns and (df["summary_chars"] > 0).all())
    check_freshness = bool("age_days" in df.columns and (df["age_days"] <= settings.freshness_threshold_days).all())

    checks = [
        {"check": "row_count", "passed": check_row_count, "details": f"Total rows: {total_rows}"},
        {"check": "paper_id_valid", "passed": check_paper_id, "details": "paper_id non-null and unique"},
        {"check": "title_valid", "passed": check_title, "details": "title non-empty"},
        {"check": "summary_valid", "passed": check_summary, "details": "summary_chars > 0"},
        {"check": "freshness", "passed": check_freshness, "details": f"age_days <= {settings.freshness_threshold_days}"},
    ]

    all_passed = all(c["passed"] for c in checks)

    payload = {
        "report_name": report_name,
        "timestamp": now_utc().isoformat(),
        "total_rows": total_rows,
        "checks": checks,
        "passed": all_passed,
    }

    # Ensure output path ending in .json
    out_file = settings.paths.quality_dir / (f"{report_name}.json" if not report_name.endswith(".json") else report_name)
    write_json(out_file, payload)
    return payload


def build_freshness_report(df: pd.DataFrame, settings: Settings, report_path) -> dict[str, Any]:
    """Build and write data freshness report payload."""
    report_file = Path(report_path)
    total_rows = len(df)

    if total_rows == 0:
        payload = {
            "timestamp": now_utc().isoformat(),
            "latest_published": None,
            "oldest_published": None,
            "stale_rows": 0,
            "total_rows": 0,
            "freshness_threshold_days": settings.freshness_threshold_days,
            "is_fresh": False,
        }
    else:
        latest = str(df["published"].max()) if "published" in df.columns else "N/A"
        oldest = str(df["published"].min()) if "published" in df.columns else "N/A"
        stale_count = int((df["age_days"] > settings.freshness_threshold_days).sum()) if "age_days" in df.columns else 0
        
        payload = {
            "timestamp": now_utc().isoformat(),
            "latest_published": latest,
            "oldest_published": oldest,
            "stale_rows": stale_count,
            "total_rows": total_rows,
            "freshness_threshold_days": settings.freshness_threshold_days,
            "is_fresh": stale_count == 0,
        }

    write_json(report_file, payload)
    return payload
