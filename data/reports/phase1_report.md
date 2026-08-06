# Baseline Data Pipeline Report (Phase 1)

## 1. Executive Summary
- **Evaluation Samples**: 16
- **Data Quality Status**: PASSED
- **Freshness Status**: FRESH

## 2. Source Ingestion
- **Source API**: Crossref REST API
- **Query**: `agentic retrieval augmented generation large language model`
- **Filter**: `from-pub-date:2026-02-07,has-abstract:true`
- **Raw Records Count**: 24
- **Cleaned Records Count**: 24

## 3. RAG Retrieval & Evaluation Metrics
| Metric | Value | Description |
| --- | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | Proportion of queries with ground truth doc retrieved |
| `mean_token_f1` | 0.8306 | Token-level overlap between model answer & reference |
| `judge_accuracy` | 0.8125 | LLM judge binary correctness rate |
| `mean_judge_score` | 4.1250 | Mean LLM judge score (1 to 5) |

## 4. Data Quality Checks
- **Total Rows Analyzed**: 24
- **Overall Result**: PASSED

### Individual Quality Checks
| Check Name | Status | Details |
| --- | --- | --- |
| `row_count` | PASSED | Total rows: 24 |
| `paper_id_valid` | PASSED | paper_id non-null and unique |
| `title_valid` | PASSED | title non-empty |
| `summary_valid` | PASSED | summary_chars > 0 |
| `freshness` | PASSED | age_days <= 180 |

## 5. Data Freshness Monitoring
- **Latest Publication Date**: 2026-08-01
- **Oldest Publication Date**: 2026-02-12
- **Stale Rows (> 180 days)**: 0
- **Total Rows**: 24
- **Status**: FRESH
