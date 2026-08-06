from __future__ import annotations

import dataclasses
from dataclasses import dataclass
import html
import json
from pathlib import Path
import re
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from core.config import Settings


@dataclass(frozen=True)
class PaperRecord:
    paper_id: str
    title: str
    summary: str
    authors: list[str]
    categories: list[str]
    primary_category: str
    published: str
    updated: str
    abs_url: str
    pdf_url: str
    comment: str


def _clean_text(text: str) -> str:
    if not text:
        return ""
    # Strip XML/HTML tags (such as <jats:p>, <jats:title>, etc.)
    cleaned = re.sub(r"<[^>]+>", " ", text)
    # Unescape HTML entities
    cleaned = html.unescape(cleaned)
    # Normalize whitespace
    return re.sub(r"\s+", " ", cleaned).strip()


def _extract_date(item: dict[str, Any], date_field: str = "published-print") -> str:
    for field in [date_field, "published-online", "published", "issued", "created", "deposited"]:
        val = item.get(field)
        if isinstance(val, dict) and "date-parts" in val:
            dp = val.get("date-parts")
            if dp and isinstance(dp[0], list) and len(dp[0]) > 0:
                parts = dp[0]
                y = parts[0]
                m = parts[1] if len(parts) > 1 else 1
                d = parts[2] if len(parts) > 2 else 1
                return f"{y:04d}-{m:02d}-{d:02d}"
    return "1970-01-01"


def parse_crossref_payload(payload: dict) -> list[PaperRecord]:
    """Parse Crossref payload into a list of PaperRecord objects."""
    items = payload.get("message", {}).get("items", [])
    records: list[PaperRecord] = []

    for item in items:
        doi = item.get("DOI", "").strip()
        if not doi:
            continue

        titles = item.get("title", [])
        title = _clean_text(titles[0]) if titles else ""
        if not title:
            continue

        abstract_raw = item.get("abstract", "")
        summary = _clean_text(abstract_raw)

        authors: list[str] = []
        for a in item.get("author", []):
            if isinstance(a, dict):
                given = a.get("given", "").strip()
                family = a.get("family", "").strip()
                name = a.get("name", "").strip()
                if given and family:
                    authors.append(f"{given} {family}")
                elif family:
                    authors.append(family)
                elif name:
                    authors.append(name)
            elif isinstance(a, str):
                authors.append(a.strip())

        categories = item.get("subject", [])
        if not categories:
            item_type = item.get("type", "")
            categories = [item_type] if item_type else ["General"]

        primary_category = categories[0] if categories else "General"

        published_date = _extract_date(item, "published-print")
        updated_date = _extract_date(item, "deposited") or published_date

        abs_url = item.get("URL", f"https://doi.org/{doi}")

        pdf_url = ""
        for link in item.get("link", []):
            if isinstance(link, dict):
                ct = link.get("content-type", "")
                link_url = link.get("URL", "")
                if ct == "application/pdf" or ".pdf" in link_url.lower():
                    pdf_url = link_url
                    break
        if not pdf_url:
            pdf_url = abs_url

        comment = item.get("publisher", "")

        record = PaperRecord(
            paper_id=doi,
            title=title,
            summary=summary,
            authors=authors,
            categories=categories,
            primary_category=primary_category,
            published=published_date,
            updated=updated_date,
            abs_url=abs_url,
            pdf_url=pdf_url,
            comment=comment,
        )
        records.append(record)

    return records


def fetch_source_records(settings: Settings) -> list[PaperRecord]:
    """Call Crossref API, save raw response, parse and save raw records."""
    url = "https://api.crossref.org/works"
    params = {
        "query": settings.source_query,
        "filter": settings.source_filter,
        "rows": settings.max_results,
    }
    headers = {
        "User-Agent": "Day10-Data-Observability-Lab/1.0 (mailto:student@example.com)"
    }

    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    response = session.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    payload = response.json()

    # Save raw API response
    settings.paths.raw_api_response.parent.mkdir(parents=True, exist_ok=True)
    with open(settings.paths.raw_api_response, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Parse payload
    records = parse_crossref_payload(payload)

    # Save raw records JSON
    settings.paths.raw_records_json.parent.mkdir(parents=True, exist_ok=True)
    dict_records = [dataclasses.asdict(r) for r in records]
    with open(settings.paths.raw_records_json, "w", encoding="utf-8") as f:
        json.dump(dict_records, f, ensure_ascii=False, indent=2)

    return records


def load_raw_records(path: Path) -> list[PaperRecord]:
    """Load JSON snapshot and map into PaperRecord objects."""
    if not path.exists():
        raise FileNotFoundError(f"Raw records file not found at: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw_list = json.load(f)

    records: list[PaperRecord] = []
    for item in raw_list:
        records.append(PaperRecord(**item))

    return records

