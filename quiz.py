from config import GENRES, LANGUAGE , RUNTIME_OPTIONS
from utils import numbered_menu, multi_select_menu

def run_quiz() -> dict:
    print("\n"+"-"*50)
    print("MOVIE RECOMMENDER - PREFRENCE QUIZ")
    print("-"*50)
    print("\n Answer a few questions and we'll find your perfect watch. \n")
    
    prefernces={}
    
    # Question 1
    print("What are you in mood for?")
    prefernces["type"] = numbered_menu(
        ["movie", "show", "any"], 
        "Enter number"
    )
    
    # Question 2
    print("\n Which genres do you enjoy?")
    prefernces["genres"] = multi_select_menu(
        GENRES,
        "Enter numbers (you can pick more than one)"
    )
    
    # Question 3
    print("\n Preferred language?")
    prefernces["language"] = numbered_menu(
        LANGUAGE + ["any"],
        "Enter number"
    )
    
    # Question 4
    print("\n How much time do you have?")
    prefernces["runtime"] = numbered_menu(
        {**RUNTIME_OPTIONS , "any" : (0, 9999)},
        "Enter number"
    )
    # Normalising the choise to match our RUNTIME_OPTIONS keys
    # short (under 90 min) -> short
    prefernces["runtime"] = prefernces["runtime"].split(" ")[0] 
    
    # Question 5
    print("\n  Do you prefer a happy ending?")
    prefernces["happy_ending"] = numbered_menu(
        ["yes", "no", "any"],
        "Enter number"
    )
    
    # Question 6
    print("\n Should it be family friendly?")
    prefernces["family_friendly"] = numbered_menu(
        ["yes", "no", "any"],
        "Enter number"
    )
    
    # Question 7
    print("\n Do you prefer fast-paced or slow-paced?")
    prefernces["pace"] = numbered_menu(
        ["fast", "slow", "any"],
        "Enter number"
    )
    
    return prefernces