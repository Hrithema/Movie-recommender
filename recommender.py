import pandas as pd
from config import RUNTIME_OPTIONS, TOP_N, LANGUAGE, LANGUAGE_MAP

def recommend(movies: pd.DataFrame, preferences: dict) -> pd.DataFrame:
    df = movies.copy()

    # ── Language filter ────────────────────────────────────────────────────────
    # Quiz returns "English" but TMDB stores "en".
    # We use LANGUAGE_MAP to convert before comparing.
    if preferences["language"] != "any":
        lang_code = LANGUAGE_MAP.get(preferences["language"], "")
        if lang_code:
            df = df[df["language"] == lang_code]

    # ── Runtime filter ─────────────────────────────────────────────────────────
    # preferences["runtime"] is already normalised to "short"/"medium"/"long"/"any"
    # by the split(" ")[0] line in quiz.py
    runtime_key = preferences["runtime"]
    if runtime_key in RUNTIME_OPTIONS:
        min_rt, max_rt = RUNTIME_OPTIONS[runtime_key]
        df = df[
            (pd.to_numeric(df["runtime"], errors="coerce") >= min_rt) &
            (pd.to_numeric(df["runtime"], errors="coerce") <= max_rt)
        ]

    # ── Genre scoring ──────────────────────────────────────────────────────────
    # TMDB "genres" is a list e.g. ["Action", "Adventure"]
    # We count how many of the user's preferred genres appear in each movie.
    # A movie with 2 matching genres scores higher than one with 1 match.
    preferred_genres = preferences.get("genres", [])

    if preferred_genres:
        df["genre_score"] = df["genres"].apply(
            lambda g: sum(1 for genre in preferred_genres if genre in g)
            if isinstance(g, list) else 0
        )
    else:
        # User picked no genres — all movies score equally
        df["genre_score"] = 0

    # ── Note on happy_ending, family_friendly, pace ────────────────────────────
    # These fields don't exist in TMDB or any standard dataset.
    # We skip filtering on them for now — Phase 5 (scoring engine) is the
    # right place to handle these via genre/keyword proxies instead.

    # ── Sort and return top N ──────────────────────────────────────────────────
    df = df.sort_values(
        by=["genre_score", "rating"],   # genre match first, then rating as tiebreaker
        ascending=[False, False]
    )

    df = df.drop(columns=["genre_score"])

    return df.head(TOP_N).reset_index(drop=True)