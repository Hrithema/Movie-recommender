import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profiles import login_menu, get_watch_history, load_profile
from utils import load_movies, display_recommendations
from recommender import recommend
from feedback import add_to_watch_later, prompt_seen_ratings
from similarity import get_similar_movies, display_similar


def main():
    # ── Step 1: Login ──────────────────────────────────────────────────────────
    preferences, username = login_menu()

    # ── Step 2: Load full dataset ──────────────────────────────────────────────
    print("\n  Loading movies...")
    try:
        full_movies = load_movies()
    except FileNotFoundError as e:
        print(f"\n❌  {e}")
        sys.exit(1)

    # ── Step 3: Exclude watched + watch later from recommendation pool ──────────
    watched    = set()
    watch_later = set()

    if username:
        watched = get_watch_history(username)
        try:
            profile     = load_profile(username)
            watch_later = set(profile.get("watch_later", []))
        except FileNotFoundError:
            pass

    exclude_from_recs = watched | watch_later
    movies = full_movies.copy()

    if exclude_from_recs:
        before = len(movies)
        movies = movies[~movies["title"].isin(exclude_from_recs)].reset_index(drop=True)
        excluded = before - len(movies)
        if excluded:
            print(f"  Excluded {excluded} already-watched/saved movie(s).")

    # ── Step 4: Recommend ──────────────────────────────────────────────────────
    results = recommend(movies, preferences, username=username)

    # ── Step 5: Display main recommendations ───────────────────────────────────
    display_recommendations(results)

    # ── Step 6: Similar movies ─────────────────────────────────────────────────
    similar = []
    if username:
        shown_titles = set(results["title"].tolist()) if not results.empty else set()
        exclude_from_similar = watched | shown_titles

        similar = get_similar_movies(
            username, full_movies, exclude_titles=exclude_from_similar, top_n=3
        )
        display_similar(similar)

    # ── Step 7: Watch Later + Feedback ─────────────────────────────────────────
    if username:
        # Combine main recs + similar movie titles for watch later
        main_titles = results["title"].tolist() if not results.empty else []
        similar_titles = [m["title"] for g in similar for m in g["recommendations"]]
        all_titles = main_titles + similar_titles

        if all_titles:
            add_to_watch_later(username, all_titles)

        if not results.empty:
            prompt_seen_ratings(username, main_titles)

    # ── Step 8: Run again? ─────────────────────────────────────────────────────
    print("\n" + "─"*50)
    again = input("  Try different preferences? (y/n): ").strip().lower()
    if again in ("y", "yes"):
        main()
    else:
        print("\n  Enjoy your watch 🍿\n")


if __name__ == "__main__":
    main()