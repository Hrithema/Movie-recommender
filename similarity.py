# similarity.py
# Phase 6 — Content-Based Similar Movie Recommendations

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from profiles import load_profile


def get_similar_movies(username: str, movies_df: pd.DataFrame,
                       exclude_titles: set, top_n: int = 3) -> list:
    seeds = _get_seeds(username, movies_df)
    if not seeds:
        return []

    # Reset index so positional indexing matches TF-IDF matrix rows
    movies_clean = movies_df.reset_index(drop=True)
    tfidf_matrix, _ = _build_tfidf(movies_clean)

    results = []
    seen_recommendations = set(exclude_titles)

    for seed_title, reason in seeds:
        similar = _find_similar(
            seed_title, movies_clean, tfidf_matrix, seen_recommendations, top_n
        )
        if similar:
            results.append({
                "seed":            seed_title,
                "reason":          reason,
                "recommendations": similar,
            })
            seen_recommendations.update(m["title"] for m in similar)

    return results


def display_similar(similar_results: list) -> None:
    if not similar_results:
        return

    print("\n" + "="*50)
    print("   🎯  BECAUSE YOU WATCHED...")
    print("="*50)

    for group in similar_results:
        print(f"\n  📽️   '{group['seed']}'  ({group['reason']})")
        print(f"  {'─'*46}")

        for movie in group["recommendations"]:
            title    = movie["title"]
            genres   = ", ".join(movie["genres"]) if movie["genres"] else "Unknown"
            rating   = movie["rating"]
            overview = movie["overview"][:100]

            print(f"  ➤  {title}")
            print(f"       Genres: {genres}   Rating: {rating:.1f}/10")
            if overview:
                print(f"       {overview}...")

    print("\n" + "="*50 + "\n")


def _get_seeds(username: str, movies_df: pd.DataFrame) -> list:
    try:
        profile = load_profile(username)
    except FileNotFoundError:
        return []

    history = profile.get("watch_history", {})
    if isinstance(history, list) or not history:
        return []

    known_titles = set(movies_df["title"].tolist())
    seeds = []
    seen  = set()

    def _add(title, reason):
        if title and title not in seen and title in known_titles:
            seeds.append((title, reason))
            seen.add(title)

    all_titles = list(history.keys())
    if all_titles:
        _add(all_titles[-1], "recently watched")

    rated = {t: f.get("rating", 0) for t, f in history.items()
             if isinstance(f, dict) and f.get("rating")}
    if rated:
        best = max(rated, key=rated.get)
        _add(best, f"your {int(rated[best])}★ rating")

    favourites = [t for t, f in history.items()
                  if isinstance(f, dict) and f.get("favourite")]
    if favourites:
        _add(favourites[-1], "one of your favourites")

    return seeds


def _build_tfidf(movies_df: pd.DataFrame):
    overviews = movies_df["overview"].fillna("").astype(str)
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000,
        ngram_range=(1, 2),
    )
    tfidf_matrix = vectorizer.fit_transform(overviews)
    return tfidf_matrix, vectorizer


def _find_similar(seed_title: str, movies_df: pd.DataFrame,
                  tfidf_matrix, exclude: set, top_n: int) -> list:
    # movies_df must have a clean 0-based index matching tfidf_matrix rows
    seed_rows = movies_df[movies_df["title"] == seed_title]
    if seed_rows.empty:
        return []

    # Use iloc position, not the index label, to index into tfidf_matrix
    seed_pos     = movies_df.index.get_loc(seed_rows.index[0])
    seed_vec     = tfidf_matrix[seed_pos]
    tfidf_scores = cosine_similarity(seed_vec, tfidf_matrix).flatten()

    max_val = tfidf_scores.max()
    if max_val > 0:
        tfidf_scores = tfidf_scores / max_val

    seed_genres = seed_rows.iloc[0].get("genres", [])
    if not isinstance(seed_genres, list):
        seed_genres = []

    def _genre_score(genres):
        if not isinstance(genres, list) or not seed_genres:
            return 0.0
        return sum(1 for g in genres if g in seed_genres) / len(seed_genres)

    genre_scores = np.array([_genre_score(g) for g in movies_df["genres"]])
    combined     = 0.5 * genre_scores + 0.5 * tfidf_scores

    scored = movies_df.copy()
    scored["_sim"] = combined
    scored = scored[scored["title"] != seed_title]
    scored = scored[~scored["title"].isin(exclude)]
    scored = scored.sort_values("_sim", ascending=False).head(top_n)

    return [
        {
            "title":    str(row["title"]),
            "genres":   row["genres"] if isinstance(row["genres"], list) else [],
            "rating":   float(row.get("rating", 0) or 0),
            "overview": str(row.get("overview", "")),
        }
        for _, row in scored.iterrows()
    ]