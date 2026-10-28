"""Hybrid TF-IDF + E5 recommender with Reciprocal Rank Fusion.

Public API:
    engine = HybridRecommender.get()
    results = engine.recommend("I need help buying seeds", top_k=10)

Each result dict:
    {
        "scheme_id": int,
        "scheme_name": str,
        "category": str,
        "beneficiary_type": str,
        "score": float,          # RRF score
        "tfidf_rank": int | None,
        "e5_rank": int | None,
        "tfidf_similarity": float,
        "e5_similarity": float,
    }
"""

from __future__ import annotations

import pickle
import threading
from functools import lru_cache

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .config import (
    DEFAULT_TOP_K,
    E5_EMBEDDINGS_PATH,
    E5_MODEL_NAME,
    RRF_K,
    SCHEME_INDEX_PATH,
    TFIDF_VECTORIZER_PATH,
)
from .metadata import load_scheme_metadata


class HybridRecommender:
    _instance: "HybridRecommender | None" = None
    _lock = threading.Lock()

    @classmethod
    def get(cls) -> "HybridRecommender":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------
    def __init__(self) -> None:
        for path in (TFIDF_VECTORIZER_PATH, E5_EMBEDDINGS_PATH, SCHEME_INDEX_PATH):
            if not path.exists():
                raise FileNotFoundError(
                    f"Missing artifact {path}. "
                    f"Run: python -m recommender.artifacts"
                )

        with open(TFIDF_VECTORIZER_PATH, "rb") as fh:
            self._vectorizer = pickle.load(fh)

        self._embeddings = np.load(E5_EMBEDDINGS_PATH)

        index = pd.read_parquet(SCHEME_INDEX_PATH)
        # row_position is the position inside self._embeddings.
        # scheme_id is the id in the raw CSV.
        self._scheme_ids = index["scheme_id"].to_numpy()
        self._row_positions = index["row_position"].to_numpy()

        self._meta = load_scheme_metadata()
        self._model = SentenceTransformer(E5_MODEL_NAME)

    # ------------------------------------------------------
    def _tfidf_ranked(self, query: str, depth: int) -> list[tuple[int, float]]:
        q = self._vectorizer.transform([query])
        sims = cosine_similarity(q, self._vectorizer.transform(
            self._meta.loc[self._scheme_ids, "scheme_text"].tolist()
        )).flatten()
        top = np.argsort(sims)[::-1][:depth]
        return [(int(self._scheme_ids[i]), float(sims[i])) for i in top]

    def _e5_ranked(self, query: str, depth: int) -> list[tuple[int, float]]:
        q = self._model.encode(
            ["query: " + query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        sims = cosine_similarity(q, self._embeddings).flatten()
        top = np.argsort(sims)[::-1][:depth]
        return [(int(self._scheme_ids[i]), float(sims[i])) for i in top]

    # ------------------------------------------------------
    def recommend(self, query: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string")

        # Retrieve deeper than top_k so RRF has room to fuse.
        depth = max(top_k * 3, 30)
        tfidf_ranked = self._tfidf_ranked(query, depth)
        e5_ranked = self._e5_ranked(query, depth)

        tfidf_rank = {sid: r for r, (sid, _) in enumerate(tfidf_ranked, start=1)}
        e5_rank = {sid: r for r, (sid, _) in enumerate(e5_ranked, start=1)}

        tfidf_sim = {sid: s for sid, s in tfidf_ranked}
        e5_sim = {sid: s for sid, s in e5_ranked}

        all_ids = set(tfidf_rank) | set(e5_rank)

        scored = []
        for sid in all_ids:
            rrf = 0.0
            if sid in tfidf_rank:
                rrf += 1.0 / (RRF_K + tfidf_rank[sid])
            if sid in e5_rank:
                rrf += 1.0 / (RRF_K + e5_rank[sid])
            scored.append((sid, rrf))

        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:top_k]

        results = []
        for sid, rrf in scored:
            meta = self._meta.loc[sid]
            results.append(
                {
                    "scheme_id": int(sid),
                    "scheme_name": meta["name"],
                    "category": meta["category"] or "",
                    "beneficiary_type": meta["beneficiary_type"] or "",
                    "score": round(float(rrf), 6),
                    "tfidf_rank": tfidf_rank.get(sid),
                    "e5_rank": e5_rank.get(sid),
                    "tfidf_similarity": round(tfidf_sim.get(sid, 0.0), 6),
                    "e5_similarity": round(e5_sim.get(sid, 0.0), 6),
                }
            )
        return results