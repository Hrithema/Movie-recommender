# config.py
# Stores all constants used across the project.
# Keeping them here means if you ever want to add a new genre or language,
# you change it in ONE place instead of hunting through every file.

GENRES = [
    "Action",
    "Animation",
    "Comedy",
    "Drama",
    "Horror",
    "Mystery",
    "Romance",
    "Sci-Fi",
    "Thriller",
]

LANGUAGES = [
    "English",
    "French",
    "German",
    "Japanese",
    "Korean",
    "Spanish",
    "Hindi"
]

# Runtime buckets — user picks a preference, we map it to a minute range
RUNTIME_OPTIONS = {
    "short":  (0, 90),      # under 1.5 hrs
    "medium": (91, 130),    # 1.5 – 2 hrs
    "long":   (131, 999),   # over 2 hrs
    "any":    (0, 999),
}

TOP_N_RECOMMENDATIONS = 5

DATA_PATH = "data/matadata/movies.csv"