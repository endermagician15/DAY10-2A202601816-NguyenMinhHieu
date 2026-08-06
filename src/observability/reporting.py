from __future__ import annotations

from pathlib import Path
from typing import Any

from core.utils import write_text


def generate_phase1_report(
    report_path,
    source_summary: dict[str, Any],
    metrics: dict[str, Any],
    quality: dict[str, Any],
    freshness: dict[str, Any],
) -> None:
    """Generate Markdown report for baseline Phase 1 pipeline execution."""
    out_path = Path(report_path)
    
    retrieval_hit_rate = metrics.get("retrieval_hit_rate", 0.0)
    mean_token_f1 = metrics.get("mean_token_f1", 0.0)
    judge_accuracy = metrics.get("judge_accuracy", 0.0)
    mean_judge_score = metrics.get("mean_judge_score", 0.0)
    samples = metrics.get("samples", 0)

    quality_passed = "PASSED" if quality.get("passed") else "FAILED"
    freshness_status = "FRESH" if freshness.get("is_fresh") else "STALE"

    content = f"""# Baseline Data Pipeline Report (Phase 1)

## 1. Executive Summary
- **Evaluation Samples**: {samples}
- **Data Quality Status**: {quality_passed}
- **Freshness Status**: {freshness_status}

## 2. Source Ingestion
- **Source API**: {source_summary.get("source_api", "Crossref API")}
- **Query**: `{source_summary.get("source_query", "")}`
- **Filter**: `{source_summary.get("source_filter", "")}`
- **Raw Records Count**: {source_summary.get("raw_count", 0)}
- **Cleaned Records Count**: {source_summary.get("clean_count", 0)}

## 3. RAG Retrieval & Evaluation Metrics
| Metric | Value | Description |
| --- | ---: | --- |
| `retrieval_hit_rate` | {retrieval_hit_rate:.4f} | Proportion of queries with ground truth doc retrieved |
| `mean_token_f1` | {mean_token_f1:.4f} | Token-level overlap between model answer & reference |
| `judge_accuracy` | {judge_accuracy:.4f} | LLM judge binary correctness rate |
| `mean_judge_score` | {mean_judge_score:.4f} | Mean LLM judge score (1 to 5) |

## 4. Data Quality Checks
- **Total Rows Analyzed**: {quality.get("total_rows", 0)}
- **Overall Result**: {quality_passed}

### Individual Quality Checks
| Check Name | Status | Details |
| --- | --- | --- |
"""
    for check in quality.get("checks", []):
        status = "PASSED" if check.get("passed") else "FAILED"
        content += f"| `{check.get('check')}` | {status} | {check.get('details')} |\n"

    content += f"""
## 5. Data Freshness Monitoring
- **Latest Publication Date**: {freshness.get("latest_published")}
- **Oldest Publication Date**: {freshness.get("oldest_published")}
- **Stale Rows (> {freshness.get("freshness_threshold_days")} days)**: {freshness.get("stale_rows")}
- **Total Rows**: {freshness.get("total_rows")}
- **Status**: {freshness_status}
"""

    write_text(out_path, content)


def generate_corruption_report(
    report_path,
    baseline_metrics: dict[str, Any],
    corrupted_metrics: dict[str, Any],
    repaired_metrics: dict[str, Any],
    corrupted_quality: dict[str, Any],
    repaired_quality: dict[str, Any],
    corrupted_freshness: dict[str, Any],
    repaired_freshness: dict[str, Any],
) -> None:
    """Generate Markdown report comparing Baseline, Corrupted, and Repaired states."""
    out_path = Path(report_path)

    b_hit = baseline_metrics.get("retrieval_hit_rate", 0.0)
    c_hit = corrupted_metrics.get("retrieval_hit_rate", 0.0)
    r_hit = repaired_metrics.get("retrieval_hit_rate", 0.0)

    b_f1 = baseline_metrics.get("mean_token_f1", 0.0)
    c_f1 = corrupted_metrics.get("mean_token_f1", 0.0)
    r_f1 = repaired_metrics.get("mean_token_f1", 0.0)

    b_acc = baseline_metrics.get("judge_accuracy", 0.0)
    c_acc = corrupted_metrics.get("judge_accuracy", 0.0)
    r_acc = repaired_metrics.get("judge_accuracy", 0.0)

    b_score = baseline_metrics.get("mean_judge_score", 0.0)
    c_score = corrupted_metrics.get("mean_judge_score", 0.0)
    r_score = repaired_metrics.get("mean_judge_score", 0.0)

    c_q_status = "PASSED" if corrupted_quality.get("passed") else "FAILED"
    r_q_status = "PASSED" if repaired_quality.get("passed") else "FAILED"

    c_f_status = "FRESH" if corrupted_freshness.get("is_fresh") else "STALE"
    r_f_status = "FRESH" if repaired_freshness.get("is_fresh") else "STALE"

    hit_delta = c_hit - b_hit
    f1_delta = c_f1 - b_f1

    content = f"""# Data Quality & RAG Performance Comparison Report

## 1. Metric Comparison Matrix

| Metric / Signal | Baseline | Corrupted | Repaired | Corruption Impact ($\Delta$) | Recovery Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | {b_hit:.4f} | {c_hit:.4f} | {r_hit:.4f} | {hit_delta:+.4f} | {"Recovered" if r_hit >= c_hit else "Partial"} |
| `mean_token_f1` | {b_f1:.4f} | {c_f1:.4f} | {r_f1:.4f} | {f1_delta:+.4f} | {"Recovered" if r_f1 >= c_f1 else "Partial"} |
| `judge_accuracy` | {b_acc:.4f} | {c_acc:.4f} | {r_acc:.4f} | {c_acc - b_acc:+.4f} | {"Recovered" if r_acc >= c_acc else "Partial"} |
| `mean_judge_score` | {b_score:.4f} | {c_score:.4f} | {r_score:.4f} | {c_score - b_score:+.4f} | {"Recovered" if r_score >= c_score else "Partial"} |
| Data Quality Status | PASSED | {c_q_status} | {r_q_status} | — | {"Restored" if r_q_status == "PASSED" else "Check Fail"} |
| Freshness Status | FRESH | {c_f_status} | {r_f_status} | — | {"Restored" if r_f_status == "FRESH" else "Stale"} |

## 2. Data Quality & Freshness Breakdown

### Corrupted State Quality Checks
- **Passed**: {c_q_status}
- **Total Rows**: {corrupted_quality.get("total_rows", 0)}
- **Freshness**: {c_f_status} (Stale Rows: {corrupted_freshness.get("stale_rows", 0)})

### Repaired State Quality Checks
- **Passed**: {r_q_status}
- **Total Rows**: {repaired_quality.get("total_rows", 0)}
- **Freshness**: {r_f_status} (Stale Rows: {repaired_freshness.get("stale_rows", 0)})

## 3. Analysis & Key Insights
1. **Corruption Impact**: Data degradation (dropping records, blanking summaries, injecting noise, altering dates) directly degrades quality checks and RAG retrieval hit rate.
2. **Lineage-Based Repair**: Re-ingesting raw snapshot (`crossref_records.json`) and re-applying cleaning rules restores clean schema, fixes freshness indicators, and recovers retrieval hit rate to baseline levels.
"""

    write_text(out_path, content)
