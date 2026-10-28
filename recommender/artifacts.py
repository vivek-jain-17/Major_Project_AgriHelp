"""Build TF-IDF vectorizer + E5 embeddings + scheme index artifacts.

Run once:  python -m recommender.artifacts

Reads:  data/agriculture_schemes.csv
Writes: artifacts/tfidf_vectorizer.pkl
        artifacts/e5_embeddings.npy
        artifacts/scheme_index.parquet
"""

from __future__ import annotations

import sys

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer

from .config import (
    ARTIFACTS_DIR,
    E5_BATCH_SIZE,
    E5_EMBEDDINGS_PATH,
    E5_MODEL_NAME,
    SCHEME_INDEX_PATH,
    TFIDF_PARAMS,
    TFIDF_VECTORIZER_PATH,
)
from .metadata import load_scheme_metadata


def build(force: bool = False) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    if (
        not force
        and TFIDF_VECTORIZER_PATH.exists()
        and E5_EMBEDDINGS_PATH.exists()
        and SCHEME_INDEX_PATH.exists()
    ):
        print("Artifacts already exist. Use force=True to rebuild.")
        return

    meta = load_scheme_metadata()

    # Only rows with non-empty scheme_text contribute to retrieval.
    # We keep the scheme_id so lookups stay aligned with the raw CSV.
    usable = meta[meta["scheme_text"].str.strip() != ""].copy()
    print(f"Total schemes: {len(meta)}")
    print(f"Usable schemes (non-empty scheme_text): {len(usable)}")

    if len(usable) == 0:
        raise RuntimeError("No usable schemes — every scheme_text is empty.")

    # ---- TF-IDF --------------------------------------------
    print("\nFitting TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(**TFIDF_PARAMS)
    vectorizer.fit(usable["scheme_text"].tolist())
    print(f"  vocabulary size: {len(vectorizer.vocabulary_)}")

    import pickle

    with open(TFIDF_VECTORIZER_PATH, "wb") as fh:
        pickle.dump(vectorizer, fh)
    print(f"  saved -> {TFIDF_VECTORIZER_PATH}")

    # ---- E5 embeddings -------------------------------------
    print(f"\nLoading E5 model: {E5_MODEL_NAME}")
    model = SentenceTransformer(E5_MODEL_NAME)

    documents = ["passage: " + t for t in usable["scheme_text"].tolist()]

    print("Encoding scheme passages (this is the slow step)...")
    embeddings = model.encode(
        documents,
        batch_size=E5_BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    ).astype(np.float32)

    print(f"  embedding shape: {embeddings.shape}")
    np.save(E5_EMBEDDINGS_PATH, embeddings)
    print(f"  saved -> {E5_EMBEDDINGS_PATH}")

    # ---- Scheme index --------------------------------------
    index = usable.reset_index()[["scheme_id"]]
    index["row_position"] = range(len(index))
    index.to_parquet(SCHEME_INDEX_PATH, index=False)
    print(f"  saved -> {SCHEME_INDEX_PATH}")

    print("\nDone. Artifacts ready.")


if __name__ == "__main__":
    build(force="--force" in sys.argv)