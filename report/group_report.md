# Group Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin bài nộp

| Thông tin | Nội dung |
| --- | --- |
| Khóa/Lớp | K4 |
| Tên nhóm | A1 |
| Repository | [Github](https://github.com/tuantruong1607/DAY10-2A202601842-NguyenTuanTruong) |
| Ngày hoàn thành | 2026-08-06 |

### Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò chính | Module/deliverable sở hữu |
| --: | --- | --- | --- | --- |
| 1 | Nguyễn Minh Hiếu | 2A202601816 | TV3 — Observability Owner | `src/observability/quality.py`, `reporting.py` |
| 2 | Nguyễn Văn Đức | 2A202601422 | TV4 — Corruption & Repair Owner | `src/ingestion/corruption.py` |
| 3 | Đào Hải Đăng | 2A202601814 | TV2 — Cleaning & Evaluation Set Owner | `src/ingestion/cleaning.py`, `src/evaluation/testset.py` |
| 4 | Nguyễn Tuấn Trường | 2A202601842 | TV1 — Source Owner | `src/ingestion/crossref.py` |
| 5 | Vũ Xuân Đức | 2A202601668 | TV5 — Pipeline Integration Owner | `src/pipelines/phase1.py`, `corruption_flow.py` |

## 2. Tóm tắt kết quả

Nhóm A1 đã xây dựng thành công quy trình data pipeline 3 trạng thái end-to-end cho hệ thống RAG bài báo học thuật từ Crossref. Baseline pipeline lấy 24 bài báo thô, làm sạch thành 24 record chuẩn, tạo vector embedding 384 chiều với `all-MiniLM-L6-v2` và nạp vào ChromaDB `papers-baseline`. Đánh giá baseline trên 16 câu hỏi test đạt `retrieval_hit_rate` 1.0 (100%), `mean_token_f1` 0.8306, `judge_accuracy` 0.8125, và `mean_judge_score` 4.125. Khi mô phỏng corruption dữ liệu (xóa bài, blank summary, nhiễu text, cắt ngắn title, làm cũ ngày), chất lượng RAG giảm nghiêm trọng: `retrieval_hit_rate` giảm xuống 0.5000 (-50%), `mean_token_f1` giảm xuống 0.4157 (-41.49%), `judge_accuracy` còn 0.3750 (-43.75%), và data quality checks thất bại. Khi thực hiện repair dữ liệu bằng cách tải lại snapshot thô (`crossref_records.json`) và chạy lại pipeline cleaning, các chỉ số đã phục hồi 100% về mức baseline ban đầu (`retrieval_hit_rate` 1.0, `token_f1` 0.8306).

## 3. Kiến trúc và luồng dữ liệu

### Luồng end-to-end

```text
Crossref API (https://api.crossref.org/works)
    -> raw response (crossref_response.json) & raw records (crossref_records.json)
    -> cleaning & data modeling (papers_clean.csv/json)
    -> embedding (all-MiniLM-L6-v2) + ChromaDB index (papers-baseline)
    -> evaluation baseline (baseline_metrics.json, test_set.json)
    -> quality/freshness reports (quality_baseline.json, freshness_report.json)
    -> data corruption (corruption_log.json, papers_clean_corrupted.csv)
    -> corrupted index (papers-corrupted) & evaluate (corrupted_metrics.json)
    -> repair from raw records lineage (papers_clean_repaired.csv)
    -> repaired index (papers-repaired) & evaluate (repaired_metrics.json)
    -> comparison report (corruption_report.md) & RAG demo (rag_demo.md)
```

### Trách nhiệm của từng khối

| Khối | Input | Xử lý chính | Output/artifact | Owner |
| --- | --- | --- | --- | --- |
| Ingestion | Settings (query, filter, max_results) | Fetch HTTP Retry, JATS XML strip, parse `PaperRecord` | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | Nguyễn Tuấn Trường (TV1) |
| Cleaning | Raw `PaperRecord` list | Deduplicate DOI, clean text, compute `age_days`, build `text_for_embedding` | `data/clean/papers_clean.csv`, `data/clean/papers_clean.json` | Đào Hải Đăng (TV2) |
| Embedding/index | Cleaned DataFrame | MiniLM 384-dim embedding + ChromaDB HNSW cosine | `data/embeddings/papers_embeddings.json`, `data/chroma/` | Đào Hải Đăng (TV2) / TV4 |
| Evaluation | Cleaned DataFrame / Index | Build ground-truth test set, compute hit rate, token F1 & LLM judge | `data/eval/test_set.json`, `data/results/baseline_metrics.json` | Đào Hải Đăng (TV2) |
| Observability | Clean/Corrupted/Repaired DF | Data quality checks (5 rules), freshness monitoring, markdown report | `data/quality/*`, `data/reports/phase1_report.md` | Nguyễn Minh Hiếu (TV3) |
| Corruption/repair | Clean DataFrame / Raw JSON | Inject 6 corruption types, log details, repair from raw lineage | `data/results/corruption_log.json`, `papers_clean_corrupted.csv`, `papers_clean_repaired.csv` | Nguyễn Văn Đức (TV4) |
| Orchestration | All modules | End-to-end baseline flow, corruption flow, comparison CLI & demo | `src/pipelines/phase1.py`, `corruption_flow.py`, `run_rag_demo.py` | Vũ Xuân Đức (TV5) |

## 4. Cách tái hiện kết quả

### Cấu hình không chứa secret

| Biến/cấu hình | Giá trị sử dụng |
| --- | --- |
| `LLM_PROVIDER` | `gemini` (hoặc heuristic fallback) |
| `LLM_MODEL` | `gemini-2.5-flash` |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` |
| Số lượng Crossref records | 24 |
| Retrieval `top_k` | 4 |
| Freshness threshold | 180 days |
| Random seed | 42 (deterministic corruption) |

### Lệnh cài đặt

```bash
uv sync
```

### Lệnh chạy

Baseline Pipeline:
```bash
uv run python script/run_phase1.py
```

Corruption Flow & Repair Pipeline:
```bash
uv run python script/run_corruption_flow.py
```

CLI Demo & Integration Unit Tests:
```bash
uv run python script/run_rag_demo.py
uv run python script/test_pipeline_integration.py
```

### Kết quả tái hiện

| Lệnh | Trạng thái | Thời điểm chạy gần nhất | Bằng chứng |
| --- | --- | --- | --- |
| Baseline pipeline | Thành công 100% | 2026-08-06 15:31:24 | `data/results/baseline_metrics.json` (hit_rate: 1.0) |
| Corruption flow | Thành công 100% | 2026-08-06 15:31:58 | `data/results/corrupted_metrics.json` & `repaired_metrics.json` |
| RAG Demo CLI | Thành công 100% | 2026-08-06 15:32:10 | `data/reports/rag_demo.md` & CLI output |
| Unit Tests | Passed (5/5 tests) | 2026-08-06 15:32:34 | `script/test_pipeline_integration.py` |

## 5. Ingestion, cleaning và data contract

### Nguồn dữ liệu

| Thuộc tính | Giá trị |
| --- | --- |
| Source | Crossref REST API (`https://api.crossref.org/works`) |
| Query/filter | Query: `agentic retrieval augmented generation large language model` |
| Thời điểm lấy dữ liệu | 2026-08-06 |
| Số record nhận được | 24 bài báo học thuật có DOI |
| Cơ chế retry/backoff | Exponential backoff retry (total=5, backoff_factor=1, status 429/500/502/503/504) |

### Clean Schema

| Trường | Kiểu dữ liệu | Bắt buộc? | Ý nghĩa | Xử lý khi thiếu/sai |
| --- | --- | --- | --- | --- |
| `paper_id` | string | Có | DOI định danh bài báo cố định | Bỏ qua nếu thiếu DOI |
| `title` | string | Có | Tiêu đề bài báo | Strip JATS XML tags, bỏ row nếu rỗng |
| `summary` | string | Có | Tóm tắt abstract | Strip JATS XML tags & unescape HTML |
| `published` | string (YYYY-MM-DD) | Có | Ngày xuất bản | Fallback về 1970-01-01 nếu parse lỗi |
| `authors_joined` | string | Có | Danh sách tác giả ghép chuỗi | Ghép tên `given + family` |
| `categories_joined` | string | Có | Chuyên mục/chủ đề | Lấy `subject` hoặc fallback `type` |
| `text_for_embedding` | string | Có | Chuỗi tổng hợp dùng để embed | `{title}. {summary} Authors: {...}. Categories: {...}.` |
| `age_days` | integer | Có | Tuổi bài báo tính theo ngày | `(run_date - pub_date).days` |
| `summary_chars` | integer | Có | Độ dài ký tự summary | Bỏ qua nếu `summary_chars == 0` |

## 6. Evaluation setup

| Thành phần | Cấu hình thực tế |
| --- | --- |
| Số câu hỏi test | 16 sample questions |
| Các `question_type` | `summary`, `authors`, `date`, `categories` |
| Ground-truth document ID | DOI duy nhất từ clean dataset |
| Embedding model | `sentence-transformers/all-MiniLM-L6-v2` (384 dim) |
| Vector store / collections | `papers-baseline`, `papers-corrupted`, `papers-repaired` |
| Retrieval `top_k` | 4 |
| Test set dùng chung | `data/eval/test_set.json` (cố định cho cả 3 trạng thái) |

## 7. Kết quả baseline

### Artifact checklist

| Artifact | Đường dẫn thực tế | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| Raw response/records | `data/raw/crossref_response.json`, `crossref_records.json` | Có | 238 KB & 58 KB snapshot |
| Cleaned dataset | `data/clean/papers_clean.csv`, `papers_clean.json` | Có | 24 clean records |
| Embedding manifest/index | `data/embeddings/papers_embeddings.json` | Có | 24 vectors in `papers-baseline` |
| Evaluation set | `data/eval/test_set.json` | Có | 16 ground-truth questions |
| Baseline metrics | `data/results/baseline_metrics.json` | Có | hit_rate = 1.0, f1 = 0.8306 |
| Quality/freshness | `data/quality/quality_baseline.json` | Có | All 5 checks passed |
| Baseline report | `data/reports/phase1_report.md` | Có | Phase 1 markdown report |

### Baseline metrics

| Metric | Giá trị | Diễn giải |
| --- | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 100% câu hỏi truy xuất được tài liệu đúng |
| `mean_token_f1` | 0.8306 | Độ tương đồng token cao so với ground truth |
| `judge_accuracy` | 0.8125 | 81.25% câu trả lời đạt chuẩn chính xác |
| `mean_judge_score` | 4.1250 | Điểm đánh giá trung bình 4.125 / 5.0 |

## 8. Data quality và freshness

### Quality checks (Baseline)

| Check | Quality dimension | Ngưỡng/kỳ vọng | Kết quả baseline | Bằng chứng |
| --- | --- | --- | --- | --- |
| `row_count` | Completeness | Total rows > 0 | PASSED (24 rows) | `quality_baseline.json` |
| `paper_id_valid` | Uniqueness & Validity | Non-null & unique | PASSED (24 unique DOIs) | `quality_baseline.json` |
| `title_valid` | Validity | Non-empty string | PASSED (24 valid titles) | `quality_baseline.json` |
| `summary_valid` | Completeness | `summary_chars > 0` | PASSED (24 valid abstracts) | `quality_baseline.json` |
| `freshness` | Timeliness | `age_days <= 180` | PASSED (0 stale rows) | `quality_baseline.json` |

### Freshness

| Thuộc tính | Giá trị |
| --- | --- |
| Timestamp mới nhất | `2026-07-28` |
| Oldest published | `2026-03-01` |
| Ngưỡng freshness | 180 ngày |
| Trạng thái baseline | FRESH (0 stale rows) |

## 9. Corruption scenarios và repair

| Corruption | Cách tạo | Record bị tác động | Quality signal kỳ vọng | Tác động thực tế | Cách repair |
| --- | --- | ---: | --- | --- | --- |
| Drop latest records | Xóa 2 bài báo mới nhất | 2 | Retrieval miss trên câu hỏi liên quan | Hit rate giảm 50% | Reload raw snapshot |
| Blank summary | Xóa trắng abstract summary | 3 | `summary_valid` check FAIL | Mất context trả lời câu hỏi | Reload raw snapshot |
| Noise injection | Chèn chuỗi nhiễu `[CORRUPTED NOISE]` | 3 | Token F1 giảm | Embedding vector lệch khoảng cách | Reload raw snapshot |
| Truncate title | Cắt ngắn tiêu đề còn 12 ký tự | 3 | `title_valid` check cảnh báo | Mất khả năng exact title lookup | Reload raw snapshot |
| Aged date | Đổi ngày về `2000-01-01` | 3 | Freshness check FAIL (`STALE`) | Bị đánh dấu dữ liệu quá cũ | Parse lại publication date thô |
| Duplicated rows | Nhân bản bản ghi trùng DOI | 2 | `paper_id_valid` check FAIL | Duplicate document in vector DB | Deduplicate theo `paper_id` |

Corruption log file: `data/results/corruption_log.json` (tồn tại và hợp lệ).

## 10. So sánh baseline, corrupted và repaired

| Metric/signal | Baseline | Corrupted | Repaired | Thay đổi do corruption ($\Delta$) | Mức phục hồi | Nhận xét |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | -0.5000 | +0.5000 (100%) | Phục hồi hoàn toàn |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | -0.4149 | +0.4149 (100%) | Phục hồi hoàn toàn |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | -0.4375 | +0.4375 (100%) | Phục hồi hoàn toàn |
| `mean_judge_score` | 4.1250 | 2.5000 | 4.1250 | -1.6250 | +1.6250 (100%) | Phục hồi hoàn toàn |
| Quality checks status | PASSED | FAILED | PASSED | Check Failed | Restored | Trở lại 5/5 check pass |
| Freshness status | FRESH | STALE | FRESH | Stale (3 rows) | Restored | Trở lại 0 stale rows |

### Kết luận nhân quả:
1. **[Corruption -> Signal -> Metric]**: Việc xóa bản ghi mới nhất và làm trống abstract dẫn trực tiếp đến thất bại ở Quality Checks (`summary_valid` & `paper_id_valid` FAIL) và làm giảm `retrieval_hit_rate` từ 100% xuống 50%.
2. **[Repair Lineage -> Recovery]**: Hành động repair tái tạo dữ liệu trực tiếp từ snapshot thô (`crossref_records.json`) thay vì copy lại CSV lỗi, giúp khôi phục hoàn toàn 100% các chỉ số retrieval hit rate và token F1 về đúng mức baseline ban đầu.

## 11. Vấn đề tích hợp quan trọng

- **Triệu chứng:** Khi khởi chạy pipeline lần đầu trên Windows PowerShell, tiến trình bị treo do tải model `sentence-transformers/all-MiniLM-L6-v2` và warning symlink HuggingFace Hub.
- **Nguyên nhân:** Windows mặc định không bật Developer Mode nên HuggingFace Hub không thể tạo symlink cache.
- **Cách xử lý:** Thêm xử lý fallback tự động trong `MiniLMEmbeddings` và hiển thị thông báo rõ ràng trong CLI demo `run_rag_demo.py`.
- **Cách xác minh:** Chạy `uv run python script/run_rag_demo.py` sinh ra kết quả side-by-side lập tức.

## 12. Checklist hoàn thành

- [x] Thông tin nhóm và repository chính xác.
- [x] Phân công khớp với module, artifact và kết quả thực tế.
- [x] Lệnh tái hiện đã được chạy lại trên phiên bản nộp.
- [x] Baseline, corrupted và repaired dùng cùng evaluation set.
- [x] Bảng metrics khớp với các file trong `data/results/`.
- [x] Quality/freshness conclusions khớp với `data/quality/`.
- [x] Các đường dẫn báo cáo và artifact truy cập được.
- [x] Mỗi thành viên đã hoàn thành báo cáo vai trò riêng.
- [x] Không có `.env`, API key, token hoặc secret trong source, report, log hay ảnh.
