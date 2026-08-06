# Phân công nhóm 5 người — Day 10 Data Pipeline

Nguồn: [report/README.md](report/README.md) (bảng nhóm 5) + timeline 7 checkpoint trong `phan-cong-day-10-data-pipeline-4h(2).html`.

## 0. Trạng thái codebase (đọc trước khi nhận việc)

| Phần | Trạng thái |
| --- | --- |
| `src/core/` (config, paths, utils) | **Đã xong** — mọi path artifact lấy từ `settings.paths`, không hard-code |
| `src/retrieval/` (embeddings, index, llm, agent, qa) | **Đã xong** — chỉ đọc hiểu + verify, không sửa |
| `src/evaluation/metrics.py` | **Đã xong** — `evaluate_pipeline()` gọi được ngay |
| 12 hàm còn lại trong 9 file | **Phải viết** — xem bảng phân công |

```bash
rg -n "TODO\(student\)|NotImplementedError" src   # 12 chỗ
```

## 1. Cấu trúc thư mục

```text
.
├── src/
│   ├── core/            config.py (Settings/Paths), utils.py        [ĐÃ XONG]
│   ├── ingestion/       crossref.py, cleaning.py, corruption.py     TV1, TV2, TV4
│   ├── retrieval/       embeddings, index, llm, agent, qa           [ĐÃ XONG] TV4 verify
│   ├── evaluation/      testset.py (TV2) | metrics.py [ĐÃ XONG]
│   ├── observability/   quality.py, reporting.py                    TV3
│   └── pipelines/       phase1.py, corruption_flow.py               TV5
├── script/              run_phase1.py, run_corruption_flow.py       [ĐÃ XONG]
├── data/                artifact sinh ra khi chạy (đã có sẵn .gitkeep)
│   ├── raw/ clean/ embeddings/ eval/ chroma/ quality/ results/ reports/
└── report/
    ├── group_report.md          1 bản chung của nhóm
    ├── individual_report.md     mẫu, giữ nguyên
    └── members/                 <MSSV>_HoTen.md — mỗi người 1 bản
```

Mỗi thành viên tạo báo cáo cá nhân của mình:

```bash
cp report/individual_report.md report/members/2A202601842_NguyenTuanTruong.md
```

Không tạo thêm thư mục mới. Không đổi `Paths` trong `src/core/config.py`.

## 2. Phân công 5 thành viên

| TV | Vai trò | File sở hữu | Input nhận | Output bàn giao | Lệnh xác minh |
| --- | --- | --- | --- | --- | --- |
| **TV1** | Source owner | `src/ingestion/crossref.py` (3 hàm) | `settings.source_query/filter/max_results` | `data/raw/crossref_response.json`, `data/raw/crossref_records.json` | `ls data/raw` + đọc 1 record |
| **TV2** | Cleaning & test-set owner | `src/ingestion/cleaning.py`, `src/evaluation/testset.py` | `list[PaperRecord]` từ TV1 | `data/clean/papers_clean.csv/.json`, `data/eval/test_set.json` | `ls data/clean data/eval` |
| **TV3** | Observability owner | `src/observability/quality.py`, `reporting.py` (4 hàm) | clean DataFrame (TV2), metrics (TV5) | `data/quality/*`, `data/reports/phase1_report.md`, `corruption_report.md` | `ls data/quality data/reports` |
| **TV4** | Corruption, repair & RAG owner | `src/ingestion/corruption.py`; verify `src/retrieval/` | clean DataFrame (TV2) | `data/clean/papers_clean_corrupted.*`, `data/results/corruption_log.json`, 3 collection Chroma tách biệt | smoke test `index.search()` + `index.lookup()` |
| **TV5** | Pipeline integration & evidence owner | `src/pipelines/phase1.py`, `corruption_flow.py` | tất cả module trên | `baseline/corrupted/repaired_metrics.json`, answers, chạy được end-to-end | `uv run python script/run_phase1.py` |

Cân bằng khối lượng: TV1 nặng nhất về code lẻ (API + retry + parse), TV5 nặng nhất về tích hợp, TV4 nhẹ phần code nên gánh thêm verify RAG/index + chứng minh repair đúng lineage.

## 3. Contract chung — chốt ở CP0, không ai tự đổi

Ba contract này **đã bị code có sẵn ràng buộc**, đọc từ `index.py`, `qa.py`, `metrics.py`:

**a. `PaperRecord`** (`src/ingestion/crossref.py`, đã định nghĩa sẵn):
`paper_id, title, summary, authors[], categories[], primary_category, published, updated, abs_url, pdf_url, comment`
→ `paper_id` phải **stable** (dùng DOI), vì test set và retrieval hit đều so bằng ID này.

**b. Cột bắt buộc của clean DataFrame** — thiếu 1 cột là `LocalEmbeddingIndex.build()` crash:

```
paper_id, title, summary, published, abs_url, pdf_url,
authors_joined, categories_joined, text_for_embedding,
age_days, summary_chars
```

`authors_joined` / `categories_joined` / `published` là câu trả lời trực tiếp của agent (`qa.py::_extract_answer`) → format phải khớp với `ground_truth` mà TV2 sinh ra trong test set.

**c. Test set** (`metrics.py::evaluate_pipeline` đọc đúng 5 khóa):
`id, question_type, question, ground_truth, ground_truth_doc_ids`
→ `ground_truth_doc_ids` lấy từ `paper_id` của clean data, không tự bịa.

Quy tắc khác: giữ nguyên test set + top_k + evaluator khi so 3 trạng thái; corrupted/repaired dùng path và collection riêng, **không ghi đè baseline**; repair = chạy lại cleaning từ `data/raw/`, không sửa tay CSV/metrics.

## 4. Quy trình làm việc

### Thứ tự phụ thuộc (không chạy song song được)

```
TV1 raw ──> TV2 clean ──┬──> TV4 index/corruption ──> TV5 evaluate ──> TV3 report
                        └──> TV2 test set ──────────┘
```

### Timeline 7 checkpoint (4h)

| CP | Thời gian | Mục tiêu | Điều kiện qua mốc |
| --- | --- | --- | --- |
| CP0 | 00:00–00:30 | Chốt contract mục 3, setup `.env`, TV1 code ingestion | raw response + raw records tồn tại |
| CP1 | 00:30–01:05 | TV2 cleaning; TV3 quality checks | clean CSV đọc được, `paper_id` unique, có `age_days` |
| CP2 | 01:05–01:35 | TV2 test set; TV4 build index + smoke test agent | `test_set.json` + collection `papers-baseline` trả về kết quả |
| CP3 | 01:35–02:00 | TV5 ráp `phase1.py`, chạy baseline; TV3 phase1 report | `baseline_metrics.json` + report khớp artifact |
| CP4 | 02:00–02:15 | Nghỉ | — |
| CP5 | 02:15–03:15 | TV4 corruption; TV5 corruption flow; TV3 quality corrupted | corruption log + corrupted metrics, baseline còn nguyên |
| CP6 | 03:15–04:00 | Repair từ raw, comparison report, review, demo | `repaired_metrics.json` + `corruption_report.md` có delta 3 trạng thái |

### Git

- 1 nhánh / 1 người: `feat/tv1-crossref`, `feat/tv2-cleaning`, … merge vào `main` sau mỗi checkpoint.
- Không commit `.env`, `data/chroma/`, hay file `.egg-info` (đã có trong `.gitignore` — kiểm tra `git status` trước khi commit).
- Merge theo thứ tự phụ thuộc ở trên: TV1 → TV2 → TV3/TV4 → TV5.

### Definition of Done (theo [Rubric.md](Rubric.md))

- [ ] `uv run python script/run_phase1.py` chạy hết, sinh đủ artifact
- [ ] `uv run python script/run_corruption_flow.py` chạy sau baseline
- [ ] Số trong report = số trong JSON thật (mở file đối chiếu)
- [ ] Chứng minh được bằng số: corruption làm giảm `retrieval_hit_rate`/`mean_token_f1`, repair phục hồi
- [ ] `group_report.md` + 5 file trong `report/members/`
- [ ] `git ls-files | grep -i env` không ra `.env`
