# Data Quality & RAG Performance Comparison Report

## 1. Metric Comparison Matrix

| Metric / Signal | Baseline | Corrupted | Repaired | Corruption Impact ($\Delta$) | Recovery Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | -0.5000 | Recovered |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | -0.4148 | Recovered |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | -0.4375 | Recovered |
| `mean_judge_score` | 4.1250 | 2.5000 | 4.1250 | -1.6250 | Recovered |
| Data Quality Status | PASSED | FAILED | PASSED | — | Restored |
| Freshness Status | FRESH | STALE | FRESH | — | Restored |

## 2. Data Quality & Freshness Breakdown

### Corrupted State Quality Checks
- **Passed**: FAILED
- **Total Rows**: 24
- **Freshness**: STALE (Stale Rows: 4)

### Repaired State Quality Checks
- **Passed**: PASSED
- **Total Rows**: 24
- **Freshness**: FRESH (Stale Rows: 0)

## 3. Analysis & Key Insights
1. **Corruption Impact**: Data degradation (dropping records, blanking summaries, injecting noise, altering dates) directly degrades quality checks and RAG retrieval hit rate.
2. **Lineage-Based Repair**: Re-ingesting raw snapshot (`crossref_records.json`) and re-applying cleaning rules restores clean schema, fixes freshness indicators, and recovers retrieval hit rate to baseline levels.
