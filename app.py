import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profiles import login_menu, get_watch_history
from utils import load_movies, display_recommendations
from recommender import recommend
from feedback import add_to_watch_later, prompt_seen_ratings

def main():
    # login
    prefernces, username = login_menu()
    
    print("\n Loading movies...")
    
    # load the datasets
    try:
        movies = load_movies()
    except FileNotFoundError as e:
        print(f"\n❌  {e}")
        sys.exit(1)
        
    # exclude watched movies only for users with saved history
    if username:
        
        watched = get_watch_history(username)
        if watched:
            before = len(movies)
            movies = movies[~movies["title"].isin(watched)].reset_index(drop=True)
            excluded = before - len(movies)
            if excluded:
                print(f"Excluded {excluded} already-watched movie(s) from results.")
    # recommend
    
    results = recommend(movies, prefernces)
    
    # Display
    display_recommendations(results)
    
    if not results.empty and username:
        titles = results["title"].tolist()
    
    # watch later
    add_to_watch_later(username, titles)
    
    # already seen? collect feedback
    prompt_seen_ratings(username, titles)
    
    # # update watch history
    # if username and not results.empty:
    #     recommended_titles = results["title"].tolist()
    #     update_watch_history(username, recommended_titles)
    
    # offer to run again
    print("\n"+"-"*50)
    again = input("Would you like to try different preferences? (yes/no): ").strip().lower()
    if again in ("yes", "ye", "y"):
        main()
    else:
        print("\n Enjoy your watch 🍿\n")
        
if __name__ == "__main__":
    main()