from __future__ import annotations

import sys
import unittest
from pathlib import Path
import pandas as pd

# Ensure src/ is in python path
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from pipelines.phase1 import require_artifact, require_clean_schema


class TestPipelineIntegration(unittest.TestCase):

    def test_require_clean_schema_valid(self):
        df = pd.DataFrame(
            [
                {
                    "paper_id": "doi_1",
                    "title": "Title 1",
                    "summary": "Summary 1",
                    "published": "2026-01-01",
                    "abs_url": "http://abs.com/1",
                    "pdf_url": "http://pdf.com/1",
                    "authors_joined": "Author A",
                    "categories_joined": "Cat A",
                    "text_for_embedding": "Title 1. Summary 1 Authors: Author A. Categories: Cat A.",
                    "age_days": 10,
                    "summary_chars": 9,
                }
            ]
        )
        # Should pass without exception
        require_clean_schema(df, "test valid df")

    def test_require_clean_schema_missing_column(self):
        df = pd.DataFrame(
            [
                {
                    "paper_id": "doi_1",
                    "title": "Title 1",
                    # missing summary and others
                }
            ]
        )
        with self.assertRaises(ValueError) as cm:
            require_clean_schema(df, "test missing col")
        self.assertIn("missing required columns", str(cm.exception))

    def test_require_clean_schema_duplicate_id(self):
        df = pd.DataFrame(
            [
                {
                    "paper_id": "doi_1",
                    "title": "Title 1",
                    "summary": "Summary 1",
                    "published": "2026-01-01",
                    "abs_url": "http://abs.com/1",
                    "pdf_url": "http://pdf.com/1",
                    "authors_joined": "Author A",
                    "categories_joined": "Cat A",
                    "text_for_embedding": "Text 1",
                    "age_days": 10,
                    "summary_chars": 9,
                },
                {
                    "paper_id": "doi_1",  # duplicate
                    "title": "Title 2",
                    "summary": "Summary 2",
                    "published": "2026-01-01",
                    "abs_url": "http://abs.com/2",
                    "pdf_url": "http://pdf.com/2",
                    "authors_joined": "Author B",
                    "categories_joined": "Cat B",
                    "text_for_embedding": "Text 2",
                    "age_days": 10,
                    "summary_chars": 9,
                },
            ]
        )
        with self.assertRaises(ValueError) as cm:
            require_clean_schema(df, "test dup id")
        self.assertIn("duplicate paper_id", str(cm.exception))

    def test_require_clean_schema_blank_embedding_text(self):
        df = pd.DataFrame(
            [
                {
                    "paper_id": "doi_1",
                    "title": "Title 1",
                    "summary": "Summary 1",
                    "published": "2026-01-01",
                    "abs_url": "http://abs.com/1",
                    "pdf_url": "http://pdf.com/1",
                    "authors_joined": "Author A",
                    "categories_joined": "Cat A",
                    "text_for_embedding": "   ",  # blank
                    "age_days": 10,
                    "summary_chars": 9,
                }
            ]
        )
        with self.assertRaises(ValueError) as cm:
            require_clean_schema(df, "test blank text")
        self.assertIn("blank text_for_embedding", str(cm.exception))

    def test_require_artifact_missing(self):
        non_existent = Path("does_not_exist_file.json")
        with self.assertRaises(FileNotFoundError) as cm:
            require_artifact(non_existent, "test label")
        self.assertIn("Missing required artifact", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
