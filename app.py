from quiz import run_quiz
from utils import load_movies, display_recommendations
from recommender import recommend

def main():
    # asking user their preferences
    prefernces = run_quiz()
    
    print("\n Loading movies...")
    
    # load the datasets
    movies = load_movies()
    
    # run recommenation engine
    results = recommend(movies, prefernces)
    
    # display results
    display_recommendations(results)
    
    # offer to run again
    again = input("Would you like to try different preferences? (yes/no): ").strip().lower()
    if again in ("yes", "ye", "y"):
        main()
    else:
        print("\n Enjoy your watch 🍿\n")
        
if __name__ == "__main__":
    main()