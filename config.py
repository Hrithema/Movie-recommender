import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ── Correct paths matching your actual folder structure ────────────────────────
TMDB_MOVIES_PATH    = os.path.join(DATA_DIR, "tmdb",     "tmdb_5000_movies.csv")
TMDB_CREDITS_PATH   = os.path.join(DATA_DIR, "tmdb",     "tmdb_5000_credits.csv")
METADATA_PATH       = os.path.join(DATA_DIR, "metadata", "movies.csv")
IMDB_BASICS_PATH    = os.path.join(DATA_DIR, "IMDB",     "title_basics.csv")
IMDB_RATINGS_PATH   = os.path.join(DATA_DIR, "IMDB",     "title_ratings.csv")

# ── Recommendation settings ────────────────────────────────────────────────────
TOP_N      = 5
MIN_VOTES  = 100
MIN_RATING = 5.0

# ── Runtime buckets (minutes) ──────────────────────────────────────────────────
RUNTIME_OPTIONS = {
    "short":  (0,   90),
    "medium": (90,  130),
    "long":   (130, 9999),
}

# ── Language codes ─────────────────────────────────────────────────────────────
LANGUAGE = [
    "English",
    "French",
    "German",
    "Japanese",
    "Korean",
    "Spanish",
    "Hindi",
    "Italian",
    "Portuguese",
]

LANGUAGE_MAP = {
    "English":    "en",
    "French":     "fr",
    "German":     "de",
    "Japanese":   "ja",
    "Korean":     "ko",
    "Spanish":    "es",
    "Hindi":      "hi",
    "Italian":    "it",
    "Portuguese": "pt",
}
GENRES = [
    "Action",
    "Adventure",
    "Comedy",
    "Drama",
    "Fantasy",
    "Horror",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
    "Animation",
    "Crime"
]