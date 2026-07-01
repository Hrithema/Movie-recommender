import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from profiles import login_menu, update_watch_history, get_watch_history
from utils import load_movies, display_recommendations
from recommender import recommend

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
                print
    
    
    
    # offer to run again
    again = input("Would you like to try different preferences? (yes/no): ").strip().lower()
    if again in ("yes", "ye", "y"):
        main()
    else:
        print("\n Enjoy your watch 🍿\n")
        
if __name__ == "__main__":
    main()