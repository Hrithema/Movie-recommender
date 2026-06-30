# utils.py
# Data loading and helper functions.
#
# DATASET STRATEGY:
# We use TMDB as the primary source because it has the richest data
# (genres as JSON, ratings, runtime, language, overview).
# If TMDB is missing, we fall back to Kaggle metadata, then IMDB.

import json
import os
import pandas as pd

from config import (
    TMDB_MOVIES_PATH, METADATA_PATH, IMDB_BASICS_PATH, IMDB_RATINGS_PATH,
    MIN_VOTES, MIN_RATING
)


# ── Main loader ────────────────────────────────────────────────────────────────

def load_movies() -> pd.DataFrame:
    
    if os.path.exists(TMDB_MOVIES_PATH):
        print(f"  Using: {TMDB_MOVIES_PATH}")
        df = pd.read_csv(TMDB_MOVIES_PATH)
        return _clean_tmdb(df)

    if os.path.exists(METADATA_PATH):
        print(f"  Using: {METADATA_PATH}")
        df = pd.read_csv(METADATA_PATH, low_memory=False)
        return _clean_metadata(df)

    if os.path.exists(IMDB_BASICS_PATH):
        print(f"  Using: {IMDB_BASICS_PATH}")
        df = pd.read_csv(IMDB_BASICS_PATH, sep="\t", na_values="\\N", low_memory=False)
        return _clean_imdb(df)

    # Nothing found — tell the user exactly what we looked for
    raise FileNotFoundError(
        "\nCould not find any dataset. Looked for:\n"
        f"  {TMDB_MOVIES_PATH}\n"
        f"  {METADATA_PATH}\n"
        f"  {IMDB_BASICS_PATH}\n"
        "Make sure at least one of these files exists."
    )


# ── Dataset cleaners ───────────────────────────────────────────────────────────

def _clean_tmdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    TMDB stores genres as a JSON string:
      '[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}]'
    We parse it into a plain Python list: ['Action', 'Adventure']
    """
    df = df.copy()
    df["genres"] = df["genres"].apply(_parse_json_genres)

    df = df.rename(columns={
        "original_language": "language",
        "vote_average":      "rating",
        "vote_count":        "votes",
    })

    keep = ["title", "genres", "language", "runtime", "rating", "votes", "overview", "release_date"]
    df = df[[c for c in keep if c in df.columns]]

    df = _apply_quality_filter(df)
    print(f"  Loaded {len(df):,} movies after quality filter.")
    return df


def _clean_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Kaggle metadata — same genre format as TMDB."""
    df = df.copy()
    df = df.rename(columns={
        "original_language": "language",
        "vote_average":      "rating",
        "vote_count":        "votes",
    })
    if "genres" in df.columns:
        df["genres"] = df["genres"].apply(_parse_json_genres)

    keep = ["title", "genres", "language", "runtime", "rating", "votes", "overview", "release_date"]
    df = df[[c for c in keep if c in df.columns]]

    df = _apply_quality_filter(df)
    print(f"  Loaded {len(df):,} movies after quality filter.")
    return df


def _clean_imdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    IMDB title_basics has no ratings — those are in title_ratings.tsv.
    We try to merge them if that file also exists.
    IMDB genres are comma-separated strings: "Action,Drama,Crime"
    """
    df = df.copy()

    # Keep only movies (not TV episodes, shorts, etc.)
    if "titleType" in df.columns:
        df = df[df["titleType"] == "movie"]

    df = df.rename(columns={
        "primaryTitle":   "title",
        "runtimeMinutes": "runtime",
    })

    # Convert IMDB genre string to list
    if "genres" in df.columns:
        df["genres"] = df["genres"].apply(
            lambda g: g.split(",") if isinstance(g, str) else []
        )

    # Try to merge ratings from title_ratings.tsv
    if os.path.exists(IMDB_RATINGS_PATH):
        ratings = pd.read_csv(IMDB_RATINGS_PATH, sep="\t", na_values="\\N")
        ratings = ratings.rename(columns={
            "averageRating": "rating",
            "numVotes":      "votes",
        })
        df = df.merge(ratings[["tconst", "rating", "votes"]], on="tconst", how="left")
        df["rating"] = df["rating"].fillna(0.0)
        df["votes"]  = df["votes"].fillna(0)
    else:
        df["rating"] = 0.0
        df["votes"]  = 0

    df["runtime"] = pd.to_numeric(df["runtime"], errors="coerce")

    keep = ["title", "genres", "runtime", "rating", "votes"]
    df = df[[c for c in keep if c in df.columns]]

    df = df.dropna(subset=["title"]).reset_index(drop=True)
    print(f"  Loaded {len(df):,} IMDB titles.")
    return df


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_json_genres(genre_str) -> list:
    """
    '[{"id": 28, "name": "Action"}]'  →  ['Action']
    Returns [] if the input is missing or malformed.
    """
    try:
        items = json.loads(genre_str)
        return [item["name"] for item in items if "name" in item]
    except (json.JSONDecodeError, TypeError, ValueError):
        return []


def _apply_quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Remove low-vote and low-rated movies to keep recommendations meaningful."""
    if "votes" in df.columns:
        df = df[pd.to_numeric(df["votes"], errors="coerce").fillna(0) >= MIN_VOTES]
    if "rating" in df.columns:
        df = df[pd.to_numeric(df["rating"], errors="coerce").fillna(0) >= MIN_RATING]
    return df.dropna(subset=["title"]).reset_index(drop=True)


# ── Display formatters ─────────────────────────────────────────────────────────

def format_genres(genres) -> str:
    if isinstance(genres, list):
        return ", ".join(genres) if genres else "Unknown"
    return str(genres) if genres else "Unknown"


def format_runtime(minutes) -> str:
    try:
        m = int(float(minutes))
        return f"{m // 60}h {m % 60}m"
    except (ValueError, TypeError):
        return "N/A"


def format_rating(rating) -> str:
    try:
        return f"{float(rating):.1f}/10"
    except (ValueError, TypeError):
        return "N/A"
    
def numbered_menu(options, prompt: str) -> str:
    options = list(options)  
    
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    while True:
        raw = input(f"\n  {prompt}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Please enter a number between 1 and {len(options)}.")

def multi_select_menu(options, prompt: str) -> list:
    options = list(options)
    
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    raw = input(f"\n  {prompt} (e.g. 1,3): ").strip()
    
    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit() and 1 <= int(part) <= len(options):
            selected.append(options[int(part) - 1])
    
    return selected

def display_recommendations(results) -> None:
    """
    Pretty-prints the top recommended movies.
    Called from app.py after recommend() returns results.
    """
    print("\n" + "="*50)
    print("   🎬  YOUR TOP RECOMMENDATIONS")
    print("="*50)

    if results.empty:
        print("\n  😕 No movies matched your preferences.")
        print("  Try selecting 'any' for some options.\n")
        return

    for rank, (_, row) in enumerate(results.iterrows(), 1):
        title    = row.get("title", "Unknown")
        genres   = format_genres(row.get("genres", []))
        runtime  = format_runtime(row.get("runtime", None))
        rating   = format_rating(row.get("rating", None))
        score    = int(row.get("score", 0))
        overview = str(row.get("overview", ""))[:120]
        year     = str(row.get("release_date", ""))[:4]

        print(f"\n  #{rank}  {title} ({year})")
        print(f"       Genres:  {genres}")
        print(f"       Runtime: {runtime}   Rating: {rating}   Match score: {score}")
        if overview:
            print(f"       {overview}...")

    print("\n" + "="*50 + "\n")