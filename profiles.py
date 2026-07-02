import json
import os

from config import DATA_DIR
from quiz import run_quiz
from utils import numbered_menu

PROFILES_DIR = os.path.join(DATA_DIR, "profiles")

# Login menu
def login_menu()-> tuple[dict, str | None]:
    print("\n"+"="*50)
    print("       MOVIE RECOMMENDER")
    print("="*50)
    
    choice = numbered_menu(
        ["Login", "New User", "Guest"], "Enter number"
    )
    if choice == "Login":
        return _handle_login()
    elif choice == "New User":
        return _handle_new_user()
    else: #guest
        print("\n Continuing as Guest. Your preferences won't be saved.\n")
        prefs = run_quiz()
        return prefs, None
    
# Login flow
def _handle_login() -> tuple[dict, str]:
    existing = _list_profiles()
    
    if not existing:
        print("\n No profiles found. Let's create one!\n")
        return _handle_new_user()
    print("\n Existing profiles: ")
    username = numbered_menu(existing+["<- Back"], "Enter Number")
    
    if username == "<- Back":
        return login_menu()
    
    profile = load_profile(username)
    print(f"\n Welcome back, {username}!")
    print(f"     Genres:   {', '.join(profile['preferences'].get('genres', [])) or 'None set'}")
    print(f"     Language: {profile['preferences'].get('language', 'any')}")
    print(f"     Runtime:  {profile['preferences'].get('runtime', 'any')}")
    print(f"     Watched:  {len(profile.get('watch_history', []))} movies\n")
    
    action = numbered_menu(
        ["Used saved preferences", "Edit preferences"],
        "Enter number"
    )
    
    if action == "Edit preferences":
        print("\n Running quiz with your saved answers as a refernce... \n")
        profile["preferences"] = run_quiz()
        save_profile(username, profile)
        print(f"\n Preferences updated for {username}")
        
    return profile["preferences"], username

# New user flow

def _handle_new_user() -> tuple[dict, str]:
    print("\n Choose a username (letters and numbers only, no spaces)")
    while True:
        username = input("Username: ").strip()
        
        if not username:
            print("Username can't be empty.")
            continue
        if not username.replace("_", "").isalnum():
            print("Invalid username, only letters, numbers and underscores are allowed.")
            continue
        if _profile_exists(username):
            print(f"{username} already exists. Choose a different username.")
            continue
        break
    
    print(f"\n Hi {username}! Let's setup your profile preferences.\n")
    prefs = run_quiz()
    
    profile = {
        "username" : username,
        "preferences" : prefs,
        "watch_history" : [],
    }
    
    save_profile(username, profile)
    print(f"\n Profile created and saved for {username}!")
    
    return prefs, username

# Watch history

def update_watch_history(username: str, recommended_titles: list) -> None:
    if not recommended_titles:
        return
    print("\n Have you already seen these?")
    print("(We'll remove them form future recommendations)\n")
    options = recommended_titles+["None of these"]
    
    from utils import multi_select_menu
    
    seen = multi_select_menu(options, "Enter numbers (e.g. 1,3)")
    
    seen = [s for s in seen if s != "None of these"]
    
    if not seen:
        return
    
    profile = load_profile(username)
    existing_history = set(profile.get("watch_history", []))
    existing_history.update(seen)
    profile["watch_history"] = sorted(existing_history)
    
    save_profile(username, profile)
    print(f"\n Added {len(seen)} movie(s) to your watch history.")


def get_watch_history(username: str) -> set:
    profile = load_profile(username)
    return set(profile.get("watch_history", []))

# file i/o

def save_profile(username: str, profile: dict) -> None:
    os.makedirs(PROFILES_DIR, exist_ok=True)
    path = _profile_path(username)
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)
        
def load_profile(username: str) -> dict:
    path = _profile_path(username)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No profile found for {username}")
    with open(path, "r") as f:
        return json.load(f)
    
def _profile_path(username: str) -> str:
    return os.path.join(PROFILES_DIR, f"{username}.json")

def _profile_exists(username: str) -> bool:
    return os.path.exists(_profile_path(username))

def _list_profiles() -> list:
    if not os.path.exists(PROFILES_DIR):
        return[]
    files = [f for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]
    return sorted([f.replace(".json", "") for f in files])