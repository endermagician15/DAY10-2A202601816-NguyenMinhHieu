from __future__ import annotations

from datetime import datetime, timezone
import random
from pathlib import Path
import pandas as pd

from core.utils import write_json


def corrupt_clean_dataframe(df: pd.DataFrame, output_log_path: str | Path) -> pd.DataFrame:
    """Simulate multiple types of data corruption deterministically.

    Steps:
    1. Drop latest records.
    2. Blank summary on selected rows.
    3. Inject noise into text.
    4. Truncate titles.
    5. Make published date old (aged date).
    6. Add duplicate rows.
    7. Rebuild helper columns & `text_for_embedding`.
    8. Write corruption log to output_log_path.
    """
    if df.empty:
        write_json(
            Path(output_log_path),
            {
                "initial_count": 0,
                "corrupted_count": 0,
                "dropped_paper_ids": [],
                "blanked_summary_ids": [],
                "noisy_text_ids": [],
                "truncated_title_ids": [],
                "aged_date_ids": [],
                "duplicated_ids": [],
            },
        )
        return df.copy()

    corrupted_df = df.copy()
    initial_count = len(corrupted_df)
    rng = random.Random(42)

    # 1. Drop latest records (drop top newest 2 papers)
    if "published" in corrupted_df.columns:
        corrupted_df = corrupted_df.sort_values("published", ascending=False).reset_index(drop=True)

    drop_count = min(2, len(corrupted_df) // 4) if len(corrupted_df) >= 4 else 1
    dropped_rows = corrupted_df.iloc[:drop_count]
    dropped_paper_ids = list(dropped_rows["paper_id"])
    corrupted_df = corrupted_df.iloc[drop_count:].reset_index(drop=True)

    available_indices = list(range(len(corrupted_df)))

    # 2. Blank summary
    blank_k = max(1, len(available_indices) // 6)
    blank_indices = rng.sample(available_indices, min(blank_k, len(available_indices)))
    blanked_summary_ids = [corrupted_df.loc[idx, "paper_id"] for idx in blank_indices]
    for idx in blank_indices:
        corrupted_df.loc[idx, "summary"] = ""
        corrupted_df.loc[idx, "summary_chars"] = 0

    # 3. Inject noise into text
    noise_indices = [i for i in available_indices if i not in blank_indices]
    noise_k = max(1, len(noise_indices) // 5) if noise_indices else 0
    noise_targets = rng.sample(noise_indices, min(noise_k, len(noise_indices))) if noise_indices else []
    noisy_text_ids = [corrupted_df.loc[idx, "paper_id"] for idx in noise_targets]
    for idx in noise_targets:
        corrupted_df.loc[idx, "summary"] = str(corrupted_df.loc[idx, "summary"]) + " [CORRUPTED NOISE: NULL_POINTER_SYS_ERR_9999]"

    # 4. Truncate title
    trunc_indices = [i for i in available_indices if i not in noise_targets]
    trunc_k = max(1, len(trunc_indices) // 5) if trunc_indices else 0
    trunc_targets = rng.sample(trunc_indices, min(trunc_k, len(trunc_indices))) if trunc_indices else []
    truncated_title_ids = [corrupted_df.loc[idx, "paper_id"] for idx in trunc_targets]
    for idx in trunc_targets:
        title_str = str(corrupted_df.loc[idx, "title"])
        corrupted_df.loc[idx, "title"] = title_str[:12] + "..." if len(title_str) > 12 else title_str

    # 5. Make published date old (aged_date)
    age_indices = [i for i in available_indices if i not in trunc_targets and i not in noise_targets]
    age_k = max(1, len(age_indices) // 5) if age_indices else 0
    age_targets = rng.sample(age_indices, min(age_k, len(age_indices))) if age_indices else []
    aged_date_ids = [corrupted_df.loc[idx, "paper_id"] for idx in age_targets]
    for idx in age_targets:
        corrupted_df.loc[idx, "published"] = "2000-01-01"

    # 6. Add duplicate rows
    dup_k = min(2, len(corrupted_df))
    dup_sources = corrupted_df.iloc[:dup_k].copy()
    duplicated_ids = list(dup_sources["paper_id"])
    corrupted_df = pd.concat([corrupted_df, dup_sources], ignore_index=True)

    # 7. Rebuild age_days, summary_chars, and text_for_embedding
    run_date_only = datetime.now(timezone.utc).date()

    updated_text_for_embedding = []
    updated_summary_chars = []
    updated_age_days = []

    for _, row in corrupted_df.iterrows():
        title = str(row["title"])
        summary = str(row["summary"])
        authors_joined = str(row.get("authors_joined", ""))
        categories_joined = str(row.get("categories_joined", ""))

        summary_chars = len(summary)
        updated_summary_chars.append(summary_chars)

        pub_str = str(row.get("published", ""))
        try:
            pub_date = datetime.strptime(pub_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            pub_date = datetime(1970, 1, 1).date()
        age_days = (run_date_only - pub_date).days
        updated_age_days.append(age_days)

        tfe = f"{title}. {summary} Authors: {authors_joined}. Categories: {categories_joined}."
        updated_text_for_embedding.append(tfe)

    corrupted_df["summary_chars"] = updated_summary_chars
    corrupted_df["age_days"] = updated_age_days
    corrupted_df["text_for_embedding"] = updated_text_for_embedding

    # 8. Log corruption details
    log_data = {
        "initial_count": initial_count,
        "corrupted_count": len(corrupted_df),
        "dropped_paper_ids": dropped_paper_ids,
        "blanked_summary_ids": blanked_summary_ids,
        "noisy_text_ids": noisy_text_ids,
        "truncated_title_ids": truncated_title_ids,
        "aged_date_ids": aged_date_ids,
        "duplicated_ids": duplicated_ids,
    }
    write_json(Path(output_log_path), log_data)

    return corrupted_df

