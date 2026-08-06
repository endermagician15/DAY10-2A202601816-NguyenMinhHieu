from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from core.utils import ensure_parent


def build_test_set(df: pd.DataFrame, output_path) -> list[dict[str, Any]]:
    """Tao bo evaluation set tu cleaned dataframe.

    Steps:
    1. Kiem tra so luong document toi thieu.
    2. Chon mot so paper dai dien.
    3. Tao nhieu loai cau hoi:
       - summary   → fallback trong _extract_answer()
       - authors   → trigger "Who authored" / "list the authors"
       - date      → trigger "published on" / "publication date" / "when was"
       - categories→ trigger "what categories"
    4. Moi row can co:
       - id
       - question_type
       - question
       - ground_truth
       - ground_truth_doc_ids
    5. Ghi file JSON vao output_path.
    """
    # 1. Kiểm tra số lượng tối thiểu
    if len(df) < 2:
        raise ValueError(
            f"Need at least 2 papers to build a meaningful test set, got {len(df)}."
        )

    # 2. Chọn paper đại diện — lấy tối đa 4 paper, trải đều qua toàn bộ DataFrame
    n_sample = min(4, len(df))
    step = max(1, len(df) // n_sample)
    sample = df.iloc[::step].head(n_sample)

    questions: list[dict[str, Any]] = []
    q_idx = 1

    for _, row in sample.iterrows():
        pid = str(row["paper_id"])
        title = str(row["title"])

        # 3a. summary — _extract_answer() fallback: first_sentence(metadata["summary"])
        # Lưu ý: ground_truth dùng full summary vì LLM judge và token_f1 đều so flexible.
        # Để retrieval_hit chắc chắn, ground_truth_doc_ids đặt đúng paper_id.
        questions.append(
            {
                "id": f"q{q_idx:03d}",
                "question_type": "summary",
                "question": f"What is '{title}' about?",
                "ground_truth": str(row["summary"]),
                "ground_truth_doc_ids": [pid],
            }
        )
        q_idx += 1

        # 3b. authors — trigger "Who authored"
        questions.append(
            {
                "id": f"q{q_idx:03d}",
                "question_type": "authors",
                "question": f"Who authored '{title}'?",
                "ground_truth": str(row["authors_joined"]),
                "ground_truth_doc_ids": [pid],
            }
        )
        q_idx += 1

        # 3c. date — trigger "published on"
        questions.append(
            {
                "id": f"q{q_idx:03d}",
                "question_type": "date",
                "question": f"When was '{title}' published on?",
                "ground_truth": str(row["published"]),
                "ground_truth_doc_ids": [pid],
            }
        )
        q_idx += 1

        # 3d. categories — trigger "What categories"
        questions.append(
            {
                "id": f"q{q_idx:03d}",
                "question_type": "categories",
                "question": f"What categories does '{title}' belong to?",
                "ground_truth": str(row["categories_joined"]),
                "ground_truth_doc_ids": [pid],
            }
        )
        q_idx += 1

    # 5. Ghi file JSON
    output_path = Path(output_path)
    ensure_parent(output_path)
    output_path.write_text(
        json.dumps(questions, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    return questions
