# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Tuấn Trường |
| MSSV | 2A202601842 |
| Khóa/Lớp | K4 |
| Tên nhóm | A1 |
| Vai trò chính | TV1 — Source Owner (Data Ingestion) & Tích hợp Pipeline (Member 5 support) |
| Repository | https://github.com/tuantruong1607/DAY10-2A202601842-NguyenTuanTruong |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Crossref Ingestion & API Parsing | `src/ingestion/crossref.py` (`fetch_source_records`, `parse_crossref_payload`, `load_raw_records`) | `settings.source_query`, `settings.source_filter`, `settings.max_results` | `data/raw/crossref_response.json`, `data/raw/crossref_records.json`, `list[PaperRecord]` | Hoàn thành |
| Pipeline Orchestration & Observability Integration | `src/pipelines/phase1.py`, `corruption_flow.py`, `quality.py`, `reporting.py` | Toàn bộ module upstream | Baseline, Corrupted, Repaired metrics JSON, Markdown reports, CLI Demo | Hoàn thành |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Lấy dữ liệu bài báo học thuật từ Crossref API | `src/ingestion/crossref.py`::`fetch_source_records` | Tải thành công 24 bài báo học thuật khớp với query RAG | `uv run python script/run_phase1.py` |
| Lưu Raw Response Payload & Records Snapshot | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | File raw API response (238 KB) và file parsed records JSON (58 KB) | `ls data/raw` |
| Ghép nối Pipeline & Đo lường 3 Trạng thái | `src/pipelines/phase1.py`, `corruption_flow.py` | Chạy end-to-end 3 trạng thái baseline, corrupted, repaired | `uv run python script/run_corruption_flow.py` |
| CLI Demo & Visual Evidence | `script/run_rag_demo.py`, `data/reports/rag_demo.md` | Hiển thị đối chiếu side-by-side kết quả retrieval và câu trả lời | `uv run python script/run_rag_demo.py` |

## 4. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | Giảm 50% khi dữ liệu lỗi, phục hồi 100% sau repair |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | Giảm từ 83.06% xuống 41.57%, phục hồi 100% sau repair |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | Giảm từ 81.25% xuống 37.50%, phục hồi 100% sau repair |
| `mean_judge_score` | 4.1250 | 2.5000 | 4.1250 | Điểm judge trung bình khôi phục hoàn toàn về 4.1250 |
| Quality checks | PASSED | FAILED | PASSED | Phát hiện 5/5 check pass ở baseline và repair |
| Freshness status | FRESH | STALE | FRESH | Trở lại 0 stale rows sau khi repair từ raw snapshot |

### Kết luận từ số liệu

1. **[Raw Ingestion Lineage]**: Data snapshot thô tại `data/raw/crossref_records.json` bảo toàn 100% thông tin chính xác từ nguồn ban đầu.
2. **[Chuỗi tác động thực tế]**: Khi làm lỗi dữ liệu (xóa bản ghi/null summary/nhiễu text) → Quality checks phát hiện FAILED → `retrieval_hit_rate` giảm từ 1.0 xuống 0.5000 (-50%). Khi repair từ `data/raw/crossref_records.json` → Quality checks PASSED → Metrics khôi phục 100% về mức baseline.

## 5. Cam kết của thành viên

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.

**Họ và tên:** Nguyễn Tuấn Trường  
**Ngày xác nhận:** 2026-08-06  
