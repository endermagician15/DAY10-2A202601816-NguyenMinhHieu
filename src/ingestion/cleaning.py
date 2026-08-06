from __future__ import annotations

from datetime import datetime

import pandas as pd

from core.utils import compact_join, normalize_whitespace
from ingestion.crossref import PaperRecord


def build_clean_dataframe(records: list[PaperRecord], run_date: datetime) -> pd.DataFrame:
    """Clean raw records thanh dataframe san sang de embed.

    Steps:
    1. Normalize title, summary, authors, categories.
    2. Parse published/updated date.
    3. Tinh age_days.
    4. Tao cot helper:
       - authors_joined
       - categories_joined
       - summary_chars
       - text_for_embedding
    5. Drop duplicates va filter row xau.
    6. Sort dataframe va return.
    """
    rows = []
    run_date_only = run_date.date()

    for r in records:
        # 1. Normalize text
        title = normalize_whitespace(r.title)
        summary = normalize_whitespace(r.summary)

        # Bỏ record không có title
        if not title:
            continue

        # 2. authors_joined / categories_joined
        authors_joined = compact_join(r.authors)        # "Alice Smith, Bob Lee"
        categories_joined = compact_join(r.categories)  # "Machine Learning, NLP"

        # 3. Parse published → age_days
        try:
            pub_date = datetime.strptime(r.published, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pub_date = datetime(1970, 1, 1).date()
        age_days = (run_date_only - pub_date).days

        # 4. summary_chars
        summary_chars = len(summary)

        # 5. text_for_embedding — chuỗi dùng để tạo vector embedding
        text_for_embedding = (
            f"{title}. "
            f"{summary} "
            f"Authors: {authors_joined}. "
            f"Categories: {categories_joined}."
        )

        rows.append(
            {
                "paper_id": r.paper_id,
                "title": title,
                "summary": summary,
                "published": r.published,   # giữ nguyên string YYYY-MM-DD
                "updated": r.updated,
                "abs_url": r.abs_url,
                "pdf_url": r.pdf_url,
                "authors_joined": authors_joined,
                "categories_joined": categories_joined,
                "text_for_embedding": text_for_embedding,
                "age_days": age_days,
                "summary_chars": summary_chars,
            }
        )

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # 6a. Drop duplicates theo paper_id (DOI là stable ID)
    df = df.drop_duplicates(subset=["paper_id"])

    # 6b. Filter row xấu: bỏ paper không có abstract
    df = df[df["summary_chars"] > 0]

    # 7. Sort mới nhất lên đầu
    df = df.sort_values("published", ascending=False).reset_index(drop=True)

    return df
