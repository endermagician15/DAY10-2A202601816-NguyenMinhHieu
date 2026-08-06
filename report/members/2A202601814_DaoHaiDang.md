# Member Role Report — Day 10: Data Pipeline & Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Đào Hải Đăng |
| MSSV | 2A202601814 |
| Khóa/Lớp | K4 |
| Tên nhóm | A1 |
| Vai trò chính | TV3 — Observability Owner (Data Quality & Reporting) |
| Repository | https://github.com/tuantruong1607/DAY10-2A202601842-NguyenTuanTruong |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Data Quality Checks | `src/observability/quality.py` (`run_data_quality_checks`, `build_freshness_report`) | Clean DataFrame (TV2), Corrupted DataFrame (TV4), Repaired DataFrame (TV4) | JSON quality & freshness reports cho 3 trạng thái (baseline, corrupted, repaired) | Hoàn thành |
| Pipeline Reporting | `src/observability/reporting.py` (`generate_phase1_report`, `generate_corruption_report`) | Quality/freshness payloads, Metrics JSON (TV5) | Markdown reports: `phase1_report.md`, `corruption_report.md` | Hoàn thành |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Kiểm tra chất lượng dữ liệu 5 tiêu chí | `src/observability/quality.py::run_data_quality_checks` | JSON reports: `quality_baseline.json`, `quality_corrupted.json`, `quality_repaired.json` | Baseline: 5/5 PASSED; Corrupted: 2/5 PASSED; Repaired: 5/5 PASSED |
| Theo dõi tính mới của dữ liệu | `src/observability/quality.py::build_freshness_report` | JSON reports: `freshness_baseline.json`, `freshness_corrupted.json`, `freshness_repaired.json` | Baseline: FRESH (0 stale); Corrupted: STALE (4 stale); Repaired: FRESH (0 stale) |
| Tạo báo cáo Phase 1 baseline | `src/observability/reporting.py::generate_phase1_report` | `data/reports/phase1_report.md` | Hiển thị metrics, quality checks, freshness monitoring baseline |
| Tạo báo cáo so sánh corruption | `src/observability/reporting.py::generate_corruption_report` | `data/reports/corruption_report.md` | So sánh 3 trạng thái với chi tiết từng quality check và delta metrics |

## 4. Phân tích kết quả

### Metrics chính (3 trạng thái)

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | Corruption giảm 50%, phục hồi 100% |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | Giảm 41.49 điểm %, phục hồi hoàn toàn |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | Giảm 43.75%, recovery 100% |
| `mean_judge_score` | 4.1250 | 2.5000 | 4.1250 | Điểm LLM judge phục hồi từ 2.5 → 4.125 |
| Quality Checks | 5/5 PASSED ✅ | 2/5 PASSED ❌ | 5/5 PASSED ✅ | Phát hiện: paper_id duplicate, summary blank, freshness stale |
| Freshness Status | FRESH (0 stale) | STALE (4 stale) | FRESH (0 stale) | 4 bài báo bị mark cũ sau corruption |

### Chi tiết Quality Checks Baseline (5/5 PASSED)

| Check Name | Status | Details |
| --- | --- | --- |
| `row_count` | PASSED ✅ | Total rows: 24 |
| `paper_id_valid` | PASSED ✅ | paper_id non-null and unique |
| `title_valid` | PASSED ✅ | title non-empty |
| `summary_valid` | PASSED ✅ | summary_chars > 0 |
| `freshness` | PASSED ✅ | age_days <= 180 days |

### Chi tiết Quality Checks Corrupted (2/5 PASSED)

| Check Name | Status | Details | Tác động |
| --- | --- | --- | --- |
| `row_count` | PASSED ✅ | Total rows: 24 | Số record vẫn đúng |
| `paper_id_valid` | FAILED ❌ | paper_id non-null and unique | Duplicate DOI xuất hiện |
| `title_valid` | PASSED ✅ | title non-empty | Tiêu đề vẫn có nội dung |
| `summary_valid` | FAILED ❌ | summary_chars > 0 | 3 bài báo có summary bị xóa trắng |
| `freshness` | FAILED ❌ | age_days <= 180 | 4 bài báo bị set về 2000-01-01 (STALE) |

### Chi tiết Quality Checks Repaired (5/5 PASSED)

| Check Name | Status | Details |
| --- | --- | --- |
| `row_count` | PASSED ✅ | Total rows: 24 |
| `paper_id_valid` | PASSED ✅ | paper_id non-null and unique |
| `title_valid` | PASSED ✅ | title non-empty |
| `summary_valid` | PASSED ✅ | summary_chars > 0 |
| `freshness` | PASSED ✅ | age_days <= 180 days |

### Kết luận từ số liệu

1. **[Quality as Filter]**: 5 checks baseline đảm bảo dữ liệu sạch. Khi corruption xảy ra, checks phát hiện lỗi ngay lập tức (paper_id, summary, freshness FAIL).
2. **[Corruption → Metric Degradation]**: Việc xóa trắng summary (3 records) + aged dates (4 records) + duplicate IDs dẫn trực tiếp đến:
   - Quality checks: 5/5 → 2/5 (FAIL 60%)
   - Retrieval hit rate: 1.0 → 0.5 (-50%)
   - Token F1: 0.8306 → 0.4157 (-50%)
3. **[Repair Lineage → Full Recovery]**: Tái tạo từ `data/raw/crossref_records.json` + chạy lại cleaning logic → Tất cả checks PASSED, metrics phục hồi 100%.
4. **[Observability Value]**: Quality checks và freshness monitoring có khả năng phát hiện và định lượng tác động của data degradation, hỗ trợ quyết định repair strategy.

## 5. Artifact Output Checklist

| Artifact | Đường dẫn | Kích thước/nội dung | Trạng thái |
| --- | --- | --- | --- |
| Baseline quality report | `data/quality/quality_baseline.json` | 5/5 checks, 24 rows | ✅ |
| Baseline freshness | `data/quality/freshness_baseline.json` | 0 stale, FRESH status | ✅ |
| Corrupted quality report | `data/quality/quality_corrupted.json` | 2/5 checks, 24 rows | ✅ |
| Corrupted freshness | `data/quality/freshness_corrupted.json` | 4 stale, STALE status | ✅ |
| Repaired quality report | `data/quality/quality_repaired.json` | 5/5 checks, 24 rows | ✅ |
| Repaired freshness | `data/quality/freshness_repaired.json` | 0 stale, FRESH status | ✅ |
| Phase 1 report | `data/reports/phase1_report.md` | Baseline pipeline + metrics | ✅ |
| Corruption report | `data/reports/corruption_report.md` | 3-state comparison + quality detail | ✅ |

## 6. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc TV3 (Observability Owner).
- [x] Tất cả 4 hàm trong `quality.py` và `reporting.py` đã được implement đầy đủ.
- [x] JSON output khớp với metrics thực tế từ `data/results/`.
- [x] Markdown reports có chi tiết đầy đủ từng quality check cho cả 3 trạng thái.
- [x] Số liệu trong báo cáo được xác minh bằng file JSON tương ứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.

**Họ và tên:** Đào Hải Đăng  
**Ngày xác nhận:** 2026-08-06  
