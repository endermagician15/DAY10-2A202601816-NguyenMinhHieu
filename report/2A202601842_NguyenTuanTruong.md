# Member Role Report — Day 10: Data Pipeline & Data Observability

## 1. Thông tin cá nhân

| Thông tin         | Nội dung                  |
| ------------------ | -------------------------- |
| Họ và tên       | Nguyễn Tuấn Trường |
| MSSV               | 2A202601842 |
| Khóa/Lớp         | K4 |
| Tên nhóm         | Nhóm A1 |
| Vai trò chính    | TV1 — Source Owner (Data Ingestion) |
| Repository         | https://github.com/tuantruong1607/DAY10-2A202601842-NguyenTuanTruong |
| Ngày hoàn thành | 2026-08-06 |

## 2. Vai trò và phạm vi công việc

### Phần việc sở hữu

| Module/deliverable | File/hàm phụ trách | Input nhận vào | Output bàn giao  | Trạng thái |
| ------------------ | --------------------- | ---------------- | ----------------- | -------------------------------------------- |
| Crossref Ingestion & API Parsing | `src/ingestion/crossref.py` (`fetch_source_records`, `parse_crossref_payload`, `load_raw_records`) | `settings.source_query`, `settings.source_filter`, `settings.max_results` | `data/raw/crossref_response.json`, `data/raw/crossref_records.json`, `list[PaperRecord]` | Hoàn thành |

### Việc hỗ trợ ngoài phạm vi chính

| Hoạt động | Thành viên/module được hỗ trợ | Kết quả |
| ------------------------------------ | ------------------------------------ | ---------------------------- |
| Khởi tạo & Đóng gói Môi trường Python | Cả nhóm (TV1-TV5) | Setup môi trường ảo `.venv` bằng `uv sync`, bổ sung các thư viện tương thích (`langchain-community<0.4.0`, `langchain-google-vertexai`) đảm bảo cả nhóm chạy không bị lỗi import |
| Kiểm tra & Chốt Data Contract | TV2 (Cleaning Owner) | Đảm bảo `PaperRecord` cung cấp đầy đủ các thuộc tính chuẩn (`paper_id`, `title`, `summary`, `authors`, `categories`, `published`, v.v.) để TV2 tiến hành cleaning |

## 3. Kết quả theo vai trò

| Nhiệm vụ đã thực hiện | File/hàm/artifact liên quan | Kết quả bàn giao | Cách xác minh |
| --------------------------- | ----------------------------- | ------------------------- | ----------------------- |
| Lấy dữ liệu bài báo học thuật từ Crossref API | `src/ingestion/crossref.py`::`fetch_source_records` | Tải thành công 24 bài báo học thuật khớp với query RAG | `uv run python -c "from ingestion.crossref import fetch_source_records; ..."` |
| Lưu Raw Response Payload & Records Snapshot | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | File raw API response (238 KB) và file parsed records JSON (58 KB) | `ls data/raw` |
| Parse & Làm sạch dữ liệu thô từ JATS/XML | `src/ingestion/crossref.py`::`parse_crossref_payload` | Chuyển đổi payload phức tạp từ Crossref thành danh sách `PaperRecord` nhất quán | Đọc thử 1 record từ `data/raw/crossref_records.json` |

## 4. Giải thích phần kỹ thuật đã thực hiện

### Vấn đề cần giải quyết

Trong một data pipeline RAG chuyên nghiệp, việc lấy dữ liệu thô từ nguồn bên ngoài (External Data Source - Crossref REST API) đòi hỏi tính ổn định, khả năng chịu lỗi (resilience), và phải bảo toàn được vết dữ liệu thô (raw data traceability). Phần việc của TV1 giải quyết các thách thức:
1. Kết nối đến REST API công khai, xử lý rate limiting / lỗi mạng tạm thời (429/503).
2. Lưu trữ vết dữ liệu gốc (`crossref_response.json`) trước khi xử lý để phục vụ audit và data lineage.
3. Chuyển đổi dữ liệu thô chứa định dạng JATS XML (`<jats:p>`, `<jats:title>`) và ký tự mã hóa HTML thành các đối tượng `PaperRecord` chuẩn hóa.

### Cách triển khai

1. **Gửi HTTP Request có Retry (`fetch_source_records`)**:
   - Sử dụng `requests.Session()` kết hợp `urllib3.util.Retry` với cơ chế Exponential Backoff (total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504]).
   - Thiết lập `User-Agent` đúng chuẩn Crossref Polite Pool để tránh bị giới hạn băng thông.

2. **Xử lý & Chuẩn hóa Text (`parse_crossref_payload`)**:
   - Sử dụng Regular Expression `re.sub(r"<[^>]+>", " ", text)` để loại bỏ toàn bộ các thẻ JATS/HTML XML.
   - Sử dụng `html.unescape()` để giải mã các ký tự HTML mã hóa (ví dụ: `&amp;` thành `&`, `&lt;` thành `<`).
   - Xử lý ngày tháng: Trích xuất `date-parts` từ các trường `published-print`, `published-online`, `created`, `deposited` và định dạng thành chuẩn ISO `YYYY-MM-DD`.
   - Trích xuất tác giả: Ghép `given` và `family` name hoặc lấy thuộc tính `name` / `family`.

3. **Lưu trữ & Khôi phục Snapshot (`load_raw_records`)**:
   - Ghi dữ liệu ra đĩa theo mã hóa `utf-8` và `ensure_ascii=False`.
   - Cung cấp hàm `load_raw_records()` cho phép tái tạo danh sách `PaperRecord` từ file snapshot `data/raw/crossref_records.json` mà không cần gọi lại API ngoài.

### Input, output và contract

| Thành phần                   | Mô tả |
| ------------------------------ | ------------------------------------------- |
| Input                          | `settings.source_query`, `settings.source_filter`, `settings.max_results` |
| Output                         | `data/raw/crossref_response.json`, `data/raw/crossref_records.json`, `list[PaperRecord]` |
| Module phụ thuộc             | `src/core/config.py` (`Settings`, `Paths`) |
| Module sử dụng output        | `src/ingestion/cleaning.py` (TV2 sử dụng `list[PaperRecord]` hoặc đọc file raw JSON) |
| Điều kiện lỗi cần xử lý | Mạng ngắt kết nối, Crossref API trả về HTTP 429/503, dữ liệu thiếu DOI hoặc title |

### Cách xác minh

```bash
uv run python -c "from core.config import load_settings; from ingestion.crossref import fetch_source_records, load_raw_records; s = load_settings(); r = fetch_source_records(s); print('Fetched:', len(r)); l = load_raw_records(s.paths.raw_records_json); print('Loaded:', len(l)); assert len(r) == len(l)"
```

- **Kết quả mong đợi:** Lấy thành công 24 bản ghi bài báo từ API, lưu đủ 2 file artifact trong `data/raw/`, hàm `load_raw_records` đọc lại đúng 24 bản ghi.
- **Kết quả thực tế:** `Fetched: 24`, `Loaded: 24`, file `crossref_response.json` (238 KB) và `crossref_records.json` (58 KB) được tạo thành công.
- **Artifact/log:** `data/raw/crossref_response.json`, `data/raw/crossref_records.json`.

## 5. Một quyết định kỹ thuật quan trọng

- **Bối cảnh:** Lựa chọn `paper_id` cho đối tượng `PaperRecord`.
- **Các phương án đã cân nhắc:**
  1. Phương án A: Tự sinh mã UUID hoặc index tự tăng (`paper_001`, `paper_002`).
  2. Phương án B: Sử dụng DOI (`item["DOI"]`) làm `paper_id` cố định.
- **Phương án đã chọn:** Phương án B (dùng DOI).
- **Lý do:** DOI là định danh duy nhất và ổn định toàn cầu của công bố học thuật. Việc dùng DOI làm `paper_id` giúp đảm bảo tính nhất quán (deterministic) khi TV2 tạo test set và ground truth document IDs, đồng thời giúp TV4 và TV5 đo lường retrieval hit rate chính xác qua các lần chạy lại pipeline mà không bị xáo trộn ID.
- **Bằng chứng quyết định phù hợp:** `paper_id` trong `crossref_records.json` có dạng chuẩn `10.47576/2949-1894.2026.7.7.023`, duy nhất và có thể truy vết được.

## 6. Một lỗi hoặc blocker đã xử lý

- **Triệu chứng/lỗi nguyên văn:** `UnicodeEncodeError: 'charmap' codec can't encode characters in position ...: character maps to <undefined>` khi chạy lệnh trên Windows terminal.
- **Lệnh hoặc bước tái hiện:** Chạy thử lệnh print hoặc ghi log dữ liệu bài báo chứa ký tự unicode (ví dụ tên tác giả hoặc abstract tiếng nước ngoài) ra console chuẩn Windows (cp1252).
- **Nguyên nhân gốc:** Console mặc định của Windows PowerShell/CMD sử dụng codepage `cp1252`, không hỗ trợ đầy đủ các ký tự UTF-8 đa ngôn ngữ từ Crossref API.
- **Cách xử lý:** Đảm bảo tất cả các thao tác đọc/ghi file JSON trong `crossref.py` đều truyền tham số mở rộng `encoding="utf-8"` và `ensure_ascii=False`.
- **Cách xác minh sau khi sửa:** Chạy lại `fetch_source_records()` sinh ra file `data/raw/crossref_records.json` hiển thị đúng tiếng Việt và ký tự quốc tế UTF-8 không bị lỗi font hay crash.
- **Điều học được:** Khi xây dựng data pipeline trên hệ điều hành Windows, bắt buộc phải khai báo rõ ràng encoding UTF-8 ở mọi ranh giới I/O.

## 7. Hiểu biết về luồng end-to-end

**Câu trả lời:**

1. **Dữ liệu đi từ Crossref đến vector index như thế nào?**
   Dữ liệu từ Crossref REST API được TV1 fetch và parse thành `PaperRecord` (lưu snapshot tại `data/raw/`). Sau đó TV2 làm sạch, chuẩn hóa text, tính `age_days` và tạo cột `text_for_embedding` (lưu tại `data/clean/papers_clean.csv`). Tiếp theo, module `embeddings.py` dùng mô hình `all-MiniLM-L6-v2` để chuyển `text_for_embedding` thành vector embedding 384 chiều, và `index.py` đưa danh sách vector này kèm metadata vào ChromaDB Vector Store.

2. **Evaluation set và ground-truth document IDs dùng để đo retrieval/answer quality ra sao?**
   Evaluation set bao gồm danh sách các câu hỏi test, câu trả lời mẫu (`ground_truth`) và danh sách DOI của tài liệu chứa câu trả lời (`ground_truth_doc_ids`). Khi đánh giá, hệ thống thực hiện retrieval lấy top-k document. Nếu bất kỳ document ID nào trả về trùng với `ground_truth_doc_ids`, `retrieval_hit_rate` được tính điểm (Hit). Sau đó LLM trả lời câu hỏi và được chấm điểm F1 token hoặc LLM-as-a-judge so với `ground_truth`.

3. **Quality checks khác freshness monitoring ở điểm nào trong bài lab?**
   - *Quality checks* (Great Expectations): Kiểm tra tính toàn vẹn và hợp lệ của dữ liệu tĩnh (như schema có đủ cột không, `paper_id` có bị null/duplicate không, `summary` có bị rỗng không).
   - *Freshness monitoring*: Kiểm tra độ tươi của dữ liệu theo thời gian (dựa trên cột `published` và `age_days` so với ngưỡng `freshness_threshold_days`, ví dụ 180 ngày) để phát hiện dữ liệu quá cũ không còn phù hợp.

4. **Vì sao phải dùng cùng test set cho baseline, corrupted và repaired?**
   Để đảm bảo tính công bằng (controlled experiment) và khả năng so sánh nguyên nhân - kết quả. Việc cố định câu hỏi và ground truth giúp cô lập biến số duy nhất là **chất lượng dữ liệu trong Vector DB**, từ đó thấy rõ tác động giảm điểm của data lỗi và sự phục hồi điểm số sau khi repair.

5. **Repair được xem là thành công dựa trên artifact và metric nào?**
   Repair thành công khi dữ liệu được khôi phục nguyên vẹn từ nguồn thô `data/raw/`, tạo lại collection `papers-repaired`, các bài test data quality vượt qua 100%, và các chỉ số đo lường (`retrieval_hit_rate`, `mean_token_f1`, `judge_accuracy`) quay trở lại tiệm cận hoặc bằng mức `baseline`.

## 8. Phân tích kết quả

### Metrics chính

| Metric/signal          | Baseline | Corrupted | Repaired | Nhận xét của cá nhân |
| ---------------------- | -------: | --------: | -------: | ------------------------- |
| `retrieval_hit_rate` | [Đang chờ TV5] | [Đang chờ TV5] | [Đang chờ TV5] | Sẽ đo lường sau khi TV5 tích hợp và chạy `script/run_phase1.py` |
| `mean_token_f1`      | [Đang chờ TV5] | [Đang chờ TV5] | [Đang chờ TV5] | Sẽ đo lường sau khi TV5 chạy RAG evaluation |
| `judge_accuracy`     | [Đang chờ TV5] | [Đang chờ TV5] | [Đang chờ TV5] | Đánh giá bởi LLM-as-a-judge trên cùng bộ test set |
| `mean_judge_score`   | [Đang chờ TV5] | [Đang chờ TV5] | [Đang chờ TV5] | Điểm chất lượng trung bình từ LLM judge |
| Quality checks         |   [PASSED] | [Đang chờ TV4] | [Đang chờ TV5] | Đã verify thành công tầng Raw Ingestion (`data/raw/` sinh đủ 2 file artifact 24 bản ghi) |
| Freshness status       |   [PASSED] | [Đang chờ TV4] | [Đang chờ TV5] | Data lấy từ Crossref trong khoảng 180 ngày qua |

### Kết luận từ số liệu

1. **[Tầng Raw Ingestion (TV1)]**: Đã hoàn thành 100%. Đã thu thập 24 bản ghi bài báo học thuật chuẩn từ Crossref API, làm sạch JATS XML tags, lưu vết tại `data/raw/crossref_response.json` (238 KB) và `data/raw/crossref_records.json` (58 KB).
2. **[Chuỗi tác động dự kiến]**: Khi TV4 làm lỗi dữ liệu (xóa bản ghi/null summary) → Quality checks phát hiện FAILED → `retrieval_hit_rate` giảm. Khi repair từ `data/raw/crossref_records.json` → Quality checks PASSED → Metrics phục hồi.

## 9. Điều học được và hướng cải thiện

### Ba điều quan trọng nhất

1. **Về Data Pipeline**: Data pipeline phải đảm bảo lưu trữ raw artifacts (`crossref_response.json`) nguyên bản để làm "single source of truth", phục vụ việc khôi phục dữ liệu (data recovery) mà không cần gọi lại external API.
2. **Về Data Quality / Observability**: Data Observability không chỉ dừng lại ở log lỗi code, mà phải chủ động giám sát chất lượng dữ liệu (Data Quality Checks & Freshness Monitoring) trước khi đẩy vào Vector DB.
3. **Về RAG Agent**: Chất lượng của RAG Agent phụ thuộc trực tiếp vào chất lượng dữ liệu ("Garbage in, Garbage out"). Dữ liệu lỗi làm suy giảm khả năng retrieval và câu trả lời của LLM.

### Nếu có thêm thời gian

Tự động hóa pipeline ingestion bằng cách tích hợp lịch trình định kỳ (cron job/Airflow) để tự động crawl dữ liệu mới từ Crossref theo khoảng thời gian thực, đồng thời áp dụng Pydantic để validate schema mạnh mẽ hơn ngay tại tầng `parse_crossref_payload`.

## 10. Cam kết của thành viên

Đánh dấu sau khi tự kiểm tra:

- [x] Nội dung báo cáo phản ánh đúng phần việc và mức hiểu của tôi.
- [x] Tôi có thể giải thích luồng end-to-end, không chỉ module mình phụ trách.
- [x] Mọi kết luận về kết quả đều có artifact hoặc metric để đối chiếu.
- [x] Tôi không ghi “đã chạy thành công” cho phần chưa được kiểm chứng.
- [x] Báo cáo không chứa `.env`, API key, token hoặc secret.
- [x] Báo cáo này không phải bản sao nguyên văn của báo cáo nhóm hoặc báo cáo thành viên khác.

**Họ và tên:** Nguyễn Tuấn Trường  
**Ngày xác nhận:** 2026-08-06  
