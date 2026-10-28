from pathlib import Path

# ---- Paths -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
ARTIFACTS_DIR = BASE_DIR / "artifacts"

SCHEMES_CSV = DATA_DIR / "agriculture_schemes.csv"

TFIDF_VECTORIZER_PATH = ARTIFACTS_DIR / "tfidf_vectorizer.pkl"
E5_EMBEDDINGS_PATH = ARTIFACTS_DIR / "e5_embeddings.npy"
SCHEME_INDEX_PATH = ARTIFACTS_DIR / "scheme_index.parquet"

# ---- Model -------------------------------------------------
E5_MODEL_NAME = "intfloat/multilingual-e5-base"
E5_BATCH_SIZE = 32

# ---- TF-IDF (must match phase1a_tfidf.py) ------------------
TFIDF_PARAMS = dict(
    min_df=1,
    max_df=0.95,
    ngram_range=(1, 2),
    max_features=30_000,
    norm="l2",
    stop_words="english",
)

# ---- Fusion ------------------------------------------------
RRF_K = 60
DEFAULT_TOP_K = 10