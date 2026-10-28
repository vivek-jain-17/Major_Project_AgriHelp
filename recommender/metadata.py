"""Source-of-truth scheme metadata.

The Phase 1 scripts assign `scheme_id = np.arange(len(raw_df))`
*before* dropping empty rows, so `scheme_id` == row index in the raw
CSV. This module loads that raw CSV once and exposes a lookup that
is guaranteed to return name/category/beneficiary_type for *every*
scheme_id, not just the ones that happened to appear in a top-10.
"""

from __future__ import annotations

import re
from functools import lru_cache

import pandas as pd

from .config import SCHEMES_CSV


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MD_RE = re.compile(r"[*#>`_]")


def clean_text(text: str) -> str:
    """Same normalization as phase1a_tfidf.py / phase1b_semantic.py."""
    text = str(text)
    text = _HTML_TAG_RE.sub(" ", text)
    text = _URL_RE.sub(" ", text)
    text = _MD_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


@lru_cache(maxsize=1)
def load_scheme_metadata() -> pd.DataFrame:
    """Return a DataFrame indexed by scheme_id with all metadata columns.

    Columns: name, scheme_text, category, beneficiary_type.
    Rows with empty scheme_text are kept (so scheme_id stays aligned
    with the raw CSV), but the engine will skip them at retrieval time.
    """
    df = pd.read_csv(SCHEMES_CSV)

    for col in ("name", "scheme_text"):
        if col not in df.columns:
            raise ValueError(
                f"Required column '{col}' missing from {SCHEMES_CSV}"
            )

    df["scheme_id"] = range(len(df))

    df["scheme_text"] = (
        df["scheme_text"].fillna("").apply(clean_text)
    )

    for col in ("category", "beneficiary_type"):
        if col not in df.columns:
            df[col] = ""

    df = df.set_index("scheme_id", drop=True)

    return df[["name", "scheme_text", "category", "beneficiary_type"]]


def get_metadata(scheme_id: int) -> dict:
    """Return one scheme's metadata as a dict."""
    df = load_scheme_metadata()
    row = df.loc[scheme_id]
    return {
        "scheme_id": int(scheme_id),
        "scheme_name": row["name"],
        "category": row["category"] or "",
        "beneficiary_type": row["beneficiary_type"] or "",
    }