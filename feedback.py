from utils import numbered_menu, multi_select_menu
from profiles import load_profile, save_profile


def add_to_watch_later(username:str, recommended_titles: list)-> None:
    if not recommended_titles:
        return
    print("\n Which of these do you want to watch?")
    options = recommended_titles+ ["None of these"]
    selected = multi_select_menu(options, "Enter numbers (e.g. 1,3)")
    
    selected = [s for s in selected if s!= "None of these"]
    if not selected:
        return
    profile = load_profile(username)
    watch_later = set(profile.get("watch_later", []))
    watch_later.update(selected)
    profile["watch_later"] = sorted(watch_later)
    save_profile(username, profile)
    
    print(f"\n ✅ Added {len(selected)} movie(s) to your Watch Later list.")
    
    # Login time rating prompt
def prompt_watchlater_ratings(username:str) ->None:
    profile = load_profile(username)
    watch_later = profile.get("watch_later", [])
        
    if not watch_later:
        return
    print(f"\n 📋  You have {len(watch_later)} movie(s) on your Watch Later list:")
    
    for i, title in enumerate(watch_later, 1):
        print(f"       {i}. {title}")
        
    answer = numbered_menu(["Yes", "No"], "Have you watched any of these?")
    
    if answer == "No":
        return
    
    options = watch_later + ["Done"]
    watched_now = multi_select_menu(options, "Which ones did you watch? (e.g. 1,3)")
    watched_now = [w for w in watched_now if w != "Done"]
    
    if not watched_now:
        return
    
    watch_history = _migrate_history(profile.get("watch_history", {}))
    for title in watched_now:
        print(f"\n 🎬  '{title}'")
        feedback = _collect_feedback(title)
        watch_history[title] = feedback
    
    remaining = [t for t in watch_later if t not in watched_now]
    profile["watch_later"] = remaining
    profile["watch_history"] = watch_history
    save_profile(username, profile)
    
    print(f"\n ✅ Saved feedback for {len(watched_now)} movie(s).")
    
    # Feedback
    def prompt_seen_ratings(username: str, recommended_titles: list) -> None:
        if not recommended_titles:
            return
        
        print("\n 👀  Have you already seen any of these?")
        options = recommended_titles + ["None of these"]
        seen = multi_select_menu(options, "Enter numbers (e.g. 1,3)")
        seen = [s for s in seen if s != "None of these"]
        
        if not seen:
            return
        
        profile = load_profile(username)
        watch_history = _migrate_history(profile.get("watch_history", {}))
        for title in seen:
            print(f"\n 🎬  '{title}'")
            
            feedback = _collect_feedback(title)
            watch_history [title] = feedback
            
        remaining = [t for t in watch_history if t in watched_now]
        profile["watch_later"] = remaining
        profile["watch_history"] = watch_history
        save_profile(username, profile)
        
        print(f"\n ✅ Saved feedback for {len(watched_now)} movie(s).")

# Feedback for already watched movies

def prompt_seen_ratings(username: str, recommeded_titles: list) -> None:
    if not recommeded_titles:
        return
    
    print("\n 👀  Have you already seen any of these?")
    options = recommeded_titles + ["None of these"]
    seen = multi_select_menu(options, "Enter number (e.g. 1,3)")
    seen = [s for s in seen if s != "None of these"]
    
    if not seen:
        return
    
    profile = load_profile(username)
    watch_history = _migrate_history(profile.get("watch_history", {}))
    for title in seen:
        print(f"\n 🎬  '{title}'")
        feedback = _collect_feedback(title)
        watch_history[title] = feedback
    
    profile["watch_history"] = watch_history
    save_profile(username, profile)
    print(f"\n ✅ Saved your feedback for {len(seen)} movie(s).")
    
    
# Feedback collector

def _collect_feedback(title:str) -> dict:
    print("     ⭐  Rate it:")
    rating_choice = numbered_menu(
        ["★★★★★  (5 — Amazing)",
         "★★★★☆  (4 — Great)",
         "★★★☆☆  (3 — Good)",
         "★★☆☆☆  (2 — Meh)",
         "★☆☆☆☆  (1 — Terrible)"],
        "Enter number"
    )
    # Map choice text back to number
    star_map = {
        "★★★★★  (5 — Amazing)": 5,
        "★★★★☆  (4 — Great)":   4,
        "★★★☆☆  (3 — Good)":    3,
        "★★☆☆☆  (2 — Meh)":     2,
        "★☆☆☆☆  (1 — Terrible)": 1,
    }
    rating = star_map.get(rating_choice, 3)
    
    print("       👍  Did you like it?")
    
    liked_choice = numbered_menu(["👍  Like", "👎  Dislike", "👎  Dislike"], "Enter number")
    liked = liked_choice == "👍  Like"
    
    print("     ❤️   Add to favourites?")
    fav_choice = numbered_menu(["❤️   Yes", "No"], "Enter number")
    favourtie = fav_choice == "❤️   Yes"
    
    return{
        "rating" : rating,
        "liked": liked,
        "favourtie" : favourtie,
    }    
    
def _migrate_history(watch_history) -> dict:
    
    if isinstance(watch_history, list):
        # Old format — convert each title to a dict with unknown feedback
        return {title: {"rating": None, "liked": None, "favourite": False}
                for title in watch_history}
    return watch_history  # already a dict, nothing to do
 
 
# ── Read helpers (used by recommender in Phase 5) ─────────────────────────────
 
def get_liked_genres(username: str, movies_df) -> list:
    profile = load_profile(username)
    history = _migrate_history(profile.get("watch_history", {}))
 
    liked_titles = [t for t, f in history.items() if f.get("liked")]
    if not liked_titles or movies_df is None:
        return []
 
    liked_movies = movies_df[movies_df["title"].isin(liked_titles)]
    genres = []
    for g in liked_movies["genres"]:
        if isinstance(g, list):
            genres.extend(g)
    return genres
 
 
def get_favourites(username: str) -> list:
    profile = load_profile(username)
    history = _migrate_history(profile.get("watch_history", {}))
    return [t for t, f in history.items() if f.get("favourite")]