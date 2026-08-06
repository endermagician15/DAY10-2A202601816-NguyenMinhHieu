# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin | Nội dung |
| --- | --- |
| Họ và tên | Nguyễn Minh Hiếu |
| MSSV | 2A202601816 |
| Khóa/Lớp | K4 |
| Tên nhóm | A1 |
| Vai trò chính | TV5 — Pipeline Integration & Evidence Owner (Tích hợp & Điều phối Pipeline End-to-End) |
| Repository | [Github](https://github.com/endermagician15/DAY10-2A202601816-NguyenMinhHieu) |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao | Trạng thái |
| --- | --- | --- | --- | --- |
| Baseline Pipeline Orchestration | `src/pipelines/phase1.py` (`main`, `require_clean_schema`, `require_artifact`, `write_dataframe_artifacts`) | Raw records (TV1), Clean DF (TV2), Quality/Freshness checks (TV3), Index builder (TV4) | `data/results/baseline_metrics.json`, `data/results/baseline_answers.json`, `data/reports/phase1_report.md` | Hoàn thành |
| Corruption & Repair Orchestration | `src/pipelines/corruption_flow.py` (`main`, `_generate_rag_demo_md`) | Baseline artifacts, Corrupted DF (TV4), Raw records snapshot (TV1), Test set (TV2) | `data/results/corrupted_metrics.json`, `repaired_metrics.json`, `corruption_report.md`, `rag_demo.md` | Hoàn thành |
| Command-line Execution Scripts | `script/run_phase1.py`, `script/run_corruption_flow.py` | Pipeline entry points | Tự động hóa khởi chạy pipeline end-to-end qua CLI | Hoàn thành |
| Visual Evidence CLI & Integration Tests | `script/run_rag_demo.py`, `script/test_pipeline_integration.py` | Composite answers & metric artifacts | CLI demo side-by-side và 5/5 unit test kiểm tra tích hợp | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| --- | --- | --- |
| Thắt chặt Data Contract Assertions | TV2 (Cleaning Owner), TV4 (Corruption Owner) | Xây dựng hàm `require_clean_schema()` kiểm tra 11 cột bắt buộc và tính duy nhất của `paper_id`, ngăn chặn lỗi vỡ schema khi chuyển giao dữ liệu giữa các module |
| Tự động hóa Visual Evidence Demo | Cả nhóm (TV1-TV4) | Viết module generator tạo `data/reports/rag_demo.md` và script `script/run_rag_demo.py` giúp cả nhóm dễ dàng trình chiếu và kiểm chứng tác động của Data Corruption & Repair |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --- | --- | --- | --- |
| Ráp nối & khởi chạy Baseline Phase 1 Pipeline | `src/pipelines/phase1.py`, `script/run_phase1.py` | Chạy thành công end-to-end baseline, thu thập 24 bản ghi, build Chroma DB `papers-baseline`, đạt `retrieval_hit_rate` 1.0000 và `mean_token_f1` 0.8306 | `uv run python script/run_phase1.py` |
| Ráp nối Corruption, Lineage Repair & Comparison | `src/pipelines/corruption_flow.py`, `script/run_corruption_flow.py` | Thực thi tự động 3 trạng thái (Baseline -> Corrupted -> Repaired), tạo `corrupted_metrics.json` và `repaired_metrics.json` | `uv run python script/run_corruption_flow.py` |
| Xây dựng CLI Demo & Báo cáo so sánh trực quan | `script/run_rag_demo.py`, `data/reports/rag_demo.md` | Xuất bảng đối chiếu side-by-side từng câu hỏi test giữa Baseline, Corrupted và Repaired | `uv run python script/run_rag_demo.py` |
| Kiểm thử tích hợp tự động (Integration Testing) | `script/test_pipeline_integration.py` | Bộ 5 unit test kiểm tra contract schema, sự tồn tại của artifact và độ khớp của kết quả | `uv run python script/test_pipeline_integration.py` |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong một hệ thống RAG Data Pipeline hoàn chỉnh, công việc của **Pipeline Integration & Evidence Owner (TV5)** giải quyết các thách thức kỹ thuật cốt lõi:
1. **Ráp nối luồng thực thi (Pipeline Orchestration)**: Kết nối các module xử lý dữ liệu độc lập từ Ingestion (TV1), Cleaning & Evaluation (TV2), Observability (TV3) đến Corruption & Indexing (TV4) thành một workflow tự động, tuân thủ nghiêm ngặt thứ tự phụ thuộc.
2. **Kiểm soát Data Contract & Schema Drift**: Đảm bảo dữ liệu chuyển giao giữa các tầng tuân thủ 100% schema đã chốt, phát hiện sớm các lỗi mất cột hoặc rỗng dữ liệu trước khi nạp vào Vector Database.
3. **Bảo tồn Data Lineage & Khả năng tái hiện (Reproducibility)**: Đảm bảo quá trình Repair phục hồi dữ liệu từ đúng snapshot thô gốc (`data/raw/crossref_records.json`) chứ không copy lại CSV lỗi, đồng thời giữ nguyên fixed test set (`data/eval/test_set.json`) để thực hiện controlled experiment.
4. **Phân tách không gian Vector Storage**: Đảm bảo các collection trong ChromaDB (`papers-baseline`, `papers-corrupted`, `papers-repaired`) hoạt động hoàn toàn độc lập, không làm nhiễm bẩn dữ liệu giữa các lượt đánh giá.

### Cách triển khai

1. **Điều phối luồng Phase 1 Baseline (`src/pipelines/phase1.py`)**:
   - Hàm `main()` kiểm tra cài đặt từ `load_settings()`. Nếu cần refresh hoặc chưa có raw data, gọi `fetch_source_records()`, ngược lại load từ `data/raw/crossref_records.json`.
   - Thực thi `build_clean_dataframe()`, qua cổng kiểm tra `require_clean_schema()` trước khi xuất artifact `papers_clean.csv` và `papers_clean.json`.
   - Gọi `LocalEmbeddingIndex.build()` nạp dữ liệu vào Chroma collection `papers-baseline`.
   - Khởi tạo fixed evaluation set `data/eval/test_set.json` và chạy `evaluate_pipeline()`.
   - Chạy Observability audit (`run_data_quality_checks`, `build_freshness_report`) và tổng hợp ra `data/reports/phase1_report.md`.

2. **Điều phối luồng Corruption & Repair (`src/pipelines/corruption_flow.py`)**:
   - Kiểm tra điều kiện tiền đề (Prerequisites Assertions) qua `require_artifact()` đảm bảo đầy đủ các file baseline.
   - Thực thi `corrupt_clean_dataframe()`, xuất `papers_clean_corrupted.csv` và `corruption_log.json`.
   - Nạp dataframe lỗi vào Chroma collection `papers-corrupted` và gọi `evaluate_pipeline()` thu về `corrupted_metrics.json`.
   - **Tái thiết kế luồng Repair chuẩn Lineage**: Load lại `data/raw/crossref_records.json`, gọi `build_clean_dataframe()` tạo lại `papers_clean_repaired.csv`, nạp vào collection `papers-repaired` và gọi `evaluate_pipeline()` thu về `repaired_metrics.json`.
   - Tổng hợp báo cáo so sánh `corruption_report.md` và file đối chiếu side-by-side demo `rag_demo.md`.

3. **Thắt chặt Data Contract Guard (`require_clean_schema`)**:
   - Kiểm tra 11 cột chuẩn: `paper_id`, `title`, `summary`, `published`, `abs_url`, `pdf_url`, `authors_joined`, `categories_joined`, `text_for_embedding`, `age_days`, `summary_chars`.
   - Assert `df['paper_id']` không bị rỗng, null và phải có giá trị duy nhất (unique DOIs).
   - Assert `df['text_for_embedding']` không chứa chuỗi rỗng.

### Input, output và contract

| Thành phần | Mô tả |
| --- | --- |
| Input | Raw JSON (`data/raw/`), Clean DF (`data/clean/`), Fixed Testset (`data/eval/`), Quality modules, Corruption module |
| Output | `baseline_metrics.json`, `corrupted_metrics.json`, `repaired_metrics.json`, `phase1_report.md`, `corruption_report.md`, `rag_demo.md`, `agent_demo_answers.json` |
| Module phụ thuộc | `src/core/config.py`, `src/ingestion/*`, `src/retrieval/*`, `src/evaluation/*`, `src/observability/*` |
| Điều kiện lỗi cần xử lý | Mất file prerequisite, thiếu cột schema, trùng lặp DOI, số lượng mẫu evaluation lệch với test set size |

### Cách xác minh

```bash
# 1. Chạy Baseline Phase 1 Pipeline
uv run python script/run_phase1.py

# 2. Chạy Corruption, Lineage Repair & Comparison Flow
uv run python script/run_corruption_flow.py

# 3. Chạy CLI Demo Trực quan
uv run python script/run_rag_demo.py

# 4. Chạy Bộ Kiểm thử Tích hợp (Integration Tests)
uv run python script/test_pipeline_integration.py
```

- **Kết quả mong đợi:** Cả 4 lệnh đều kết thúc thành công (Exit Code 0), sinh đủ 9 file artifact kết quả trong `data/results/` và 3 file markdown report trong `data/reports/`.
- **Kết quả thực tế:** Pipeline chạy hoàn hảo 100%, 5/5 unit tests pass, các chỉ số khôi phục hoàn toàn từ 50% lên 100% sau repair.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn phương pháp phục hồi dữ liệu (Data Repair Mechanism) trong luồng `corruption_flow.py`.
- **Các phương án đã cân nhắc:**
  1. *Phương án A (In-place CSV Patching)*: Sửa trực tiếp file CSV lỗi `papers_clean_corrupted.csv` bằng cách dùng hàm fill missing values cho cột summary rỗng, hoặc xóa bớt các dòng bị noise.
  2. *Phương án B (Raw Lineage Reconstruction)*: Thực hiện Data Lineage Repair — bỏ qua hoàn toàn file corrupted, load lại 100% raw records snapshot từ `data/raw/crossref_records.json` (do TV1 lưu ở CP0), và tái thực hiện quá trình cleaning từ nguồn thô ban đầu.
- **Phương án đã chọn:** Phương án B (Raw Lineage Reconstruction).
- **Lý do:** Phương án A không thể khôi phục lại các bài báo đã bị xóa (dropped records) hoặc các đoạn title/summary bị cắt ngắn mất thông tin. Phương án B đảm bảo nguyên tắc **Single Source of Truth** và **Data Lineage Traceability** trong Data Engineering chuyên nghiệp. Khi dữ liệu bị nhiễm bẩn ở tầng downstream, cách duy nhất để khôi phục chuẩn xác 100% là replay pipeline từ tầng raw immutable storage.
- **Bằng chứng quyết định phù hợp:** Kết quả đánh giá trong `repaired_metrics.json` cho thấy `retrieval_hit_rate` và `mean_token_f1` phục hồi 100% về đúng mức baseline (1.0000 và 0.8306), Quality checks quay lại 5/5 PASSED.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `RuntimeError: Metric sample count (12) does not match test set size (16)` xảy ra khi chạy bước evaluation trong `corruption_flow.py`.
- **Lệnh hoặc bước tái hiện:** Khởi chạy `uv run python script/run_corruption_flow.py` sau khi module corruption thực hiện xóa một số bản ghi bài báo.
- **Nguyên nhân gốc:** Khi module corruption loại bỏ 2 bài báo mới nhất, nếu pipeline nạp trực tiếp danh sách bài báo còn lại vào ChromaDB mà không kiểm tra độ tương thích với `ground_truth_doc_ids` trong test set, một số câu hỏi test sẽ bị trỏ đến document ID không còn tồn tại trong vector index, gây lệch sample count khi tính toán metrics.
- **Cách xử lý:** 
  1. Trong `src/pipelines/phase1.py` và `corruption_flow.py`, bổ sung assertion kiểm tra tính nhất quán mẫu:
     ```python
     if eval_bundle.summary.get("samples") != len(test_set_items):
         raise RuntimeError(...)
     ```
  2. Cấu hình Chroma Vector Store nạp đủ các document IDs ngay cả khi nội dung bị bóp méo, đảm bảo tất cả 16 câu hỏi test trong `test_set.json` đều được truy vấn và tính điểm minh bạch (trả về Hit hoặc Miss).
- **Cách xác minh sau khi sửa:** Chạy lại `script/run_corruption_flow.py`. Tiến trình không còn văng exception, toàn bộ 16/16 câu hỏi test đều được đánh giá đầy đủ ở cả 3 trạng thái.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   Dữ liệu từ Crossref REST API được TV1 fetch và parse thành `PaperRecord` (lưu snapshot tại `data/raw/`). Sau đó TV2 làm sạch, chuẩn hóa text, tính `age_days` và tạo cột `text_for_embedding` (lưu tại `data/clean/papers_clean.csv`). Tiếp theo, TV5 ráp nối đưa dữ liệu này qua `embeddings.py` dùng mô hình `all-MiniLM-L6-v2` chuyển `text_for_embedding` thành vector embedding 384 chiều, và nạp vào ChromaDB Vector Store với các collection riêng biệt (`papers-baseline`, `papers-corrupted`, `papers-repaired`).

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Evaluation set (`data/eval/test_set.json`) bao gồm danh sách 16 câu hỏi test, câu trả lời mẫu (`ground_truth`) và danh sách DOI của tài liệu chứa câu trả lời (`ground_truth_doc_ids`). Khi đánh giá, hệ thống thực hiện retrieval lấy top-k ($k=4$) document. Nếu bất kỳ document ID nào trả về trùng với `ground_truth_doc_ids`, `retrieval_hit_rate` được tính điểm (Hit). Sau đó LLM trả lời câu hỏi và được chấm điểm Token F1 hoặc LLM-as-a-judge so với `ground_truth`.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - *Quality checks* (Great Expectations): Kiểm tra tính toàn vẹn và hợp lệ cấu trúc của dữ liệu tĩnh (như schema có đủ 11 cột không, `paper_id` có bị null/duplicate không, `summary` có bị rỗng không).
   - *Freshness monitoring*: Kiểm tra độ tươi của dữ liệu theo thời gian (dựa trên cột `published` và `age_days` so với ngưỡng `freshness_threshold_days` = 180 ngày) để phát hiện dữ liệu quá cũ không còn phù hợp với bối cảnh thực tế.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Để đảm bảo tính công bằng (controlled experiment) và khả năng so sánh nguyên nhân - kết quả (causal inference). Việc cố định 16 câu hỏi và ground truth giúp cô lập biến số duy nhất là **chất lượng dữ liệu trong Vector DB**, từ đó thấy rõ tác động giảm điểm của data lỗi và sự phục hồi điểm số sau khi repair.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   Repair thành công khi dữ liệu được khôi phục nguyên vẹn từ nguồn thô `data/raw/`, tạo lại collection `papers-repaired`, các bài test data quality đạt 5/5 PASSED, và các chỉ số đo lường (`retrieval_hit_rate`: 1.0000, `mean_token_f1`: 0.8306, `judge_accuracy`: 0.8125) quay trở lại tiệm cận hoặc bằng 100% mức baseline ban đầu.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| --- | ---: | ---: | ---: | --- |
| `retrieval_hit_rate` | 1.0000 | 0.5000 | 1.0000 | Giảm 50% khi dữ liệu bị xóa/nhiễu, phục hồi 100% sau repair |
| `mean_token_f1` | 0.8306 | 0.4157 | 0.8306 | Giảm từ 83.06% xuống 41.57%, phục hồi 100% sau repair |
| `judge_accuracy` | 0.8125 | 0.3750 | 0.8125 | Giảm từ 81.25% xuống 37.50%, phục hồi 100% sau repair |
| `mean_judge_score` | 4.1250 | 2.5000 | 4.1250 | Điểm judge trung bình khôi phục hoàn toàn về 4.1250 / 5.0 |
| Quality checks | PASSED | FAILED | PASSED | Phát hiện 5/5 check pass ở baseline và repair; 2 checks failed ở corrupted |
| Freshness status | FRESH | STALE | FRESH | Trở lại 0 stale rows sau khi repair từ raw snapshot |

### Kết luận từ số liệu

1. **[Tầng Integration & Orchestration (TV5)]**: Đã hoàn thành 100%. Đã xây dựng pipeline end-to-end tự động, kiểm soát dữ liệu đi từ Crossref API qua 3 trạng thái thực nghiệm chuẩn xác, sinh đủ tất cả 9 file JSON metrics/answers và 3 file Markdown report.
2. **[Chuỗi tác động thực tế (Impact & Recovery)]**: Khi TV4 chèn 6 loại corruption (xóa 2 bài mới nhất, làm trống abstract, chèn noise text, cắt ngắn title, đẩy lùi ngày xuất bản, duplicate DOI) $\rightarrow$ Quality checks phát hiện FAILED $\rightarrow$ `retrieval_hit_rate` giảm từ 1.0 xuống 0.5000 (-50%) và `mean_token_f1` suy giảm nghiêm trọng xuống 0.4157 (-41.49%). Khi TV5 điều phối repair tái tạo từ raw lineage snapshot (`data/raw/crossref_records.json`) $\rightarrow$ Quality checks PASSED $\rightarrow$ Tất cả các chỉ số RAG khôi phục 100% về mức baseline.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline & Orchestration**: Việc ráp nối các module dữ liệu đòi hỏi thiết kế **Data Contract** chặt chẽ giữa các tầng. Khi có schema assertion ở mỗi ranh giới I/O, pipeline sẽ fail-fast ngay lập tức nếu dữ liệu đầu vào không đạt chuẩn, tránh làm hỏng vector database.
2. **Về Data Lineage & Recovery**: Luôn luôn lưu giữ **Raw Immutable Snapshot** (`crossref_records.json`). Khi dữ liệu downstream bị hỏng hoặc nhiễm bẩn, phương pháp phục hồi tin cậy duy nhất là replay lại pipeline từ nguồn thô gốc.
3. **Về Controlled Experimentation trong RAG**: Cố định Evaluation Test Set là điều kiện bắt buộc để đo lường chính xác tác động của Data Quality. Nếu không có test set cố định, ta không thể chứng minh được liệu sự suy giảm hiệu năng là do LLM hay do chất lượng dữ liệu.

### Nếu có thêm thời gian

Tích hợp framework điều phối DAG chuyên nghiệp (như Apache Airflow hoặc Prefect) thay cho script Python đơn thuần, đồng thời tự động hóa quy trình CI/CD testing bằng GitHub Actions để tự động chạy `script/test_pipeline_integration.py` mỗi khi có Pull Request mới.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Minh Hiếu  
**Ngày xác nhận:** 2026-08-06  
