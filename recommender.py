import pandas as pd
from config import RUNTIME_OPTIONS, TOP_N, LANGUAGE_MAP

def recommend(movies: pd.DataFrame, preferences: dict, username: str = None) -> pd.DataFrame:
    
    df = movies.copy()
    # print(f"  [debug] Start: {len(df)} movies")
    df = _filter_language(df, preferences)
    df = _filter_runtime(df, preferences)
    
    if df.empty:
        return df
    
    liked_genres = []
    disliked_genres = []
    highly_rated_genres = []
    low_rated_genres = []
    favourite_genres = []
    
    if username:
        signals = _build_feedback_signals(username, movies)
        liked_genres = signals["liked"]
        disliked_genres = signals["disliked"]
        highly_rated_genres = signals["highly_rated"]
        low_rated_genres = signals ["low_rated"]
        favourite_genres    = signals["favourite"]
    
    quiz_genres = preferences.get("genres", [])
    
    df["score"] = df.apply(
        lambda row: _score_movie(
            row,
            quiz_genres,
            liked_genres,
            disliked_genres,
            highly_rated_genres,
            low_rated_genres,
            favourite_genres,
        ),
        axis = 1,
    )            
    
    df = df.sort_values(by=["score", "rating"], ascending = [False, True])
    
    return df.head(TOP_N).reset_index(drop = True)
    

def _filter_language(df:pd.DataFrame, preferences: dict) -> pd.DataFrame:
    lang = preferences.get("language", "any")
    if lang == "any":
        return df
    lang_code = LANGUAGE_MAP.get(lang, "")
    if not lang_code:
        return df
    return df[df["language"] == lang_code]

def _filter_runtime(df: pd.DataFrame, preferences: dict)-> pd.DataFrame:
    key = preferences.get("runtime", "any")
    if key not in RUNTIME_OPTIONS:
        return df
    lo, hi = RUNTIME_OPTIONS[key]
    runtime = pd.to_numeric(df["runtime"], errors="coerce")
    return df[(runtime>= lo) & (runtime<hi)]

def _score_movie(row, quiz_genres, liked_genres, disliked_genres, highly_rated_genres, low_rated_genres, favourite_genres) -> int:
    score = 0
    movie_genres = row.get("genres", [])
    if not isinstance(movie_genres, list):
        movie_genres = []
    
    # for what user explicitly asked for
    score += _genre_overlap(movie_genres, quiz_genres) *20
    
    # learned preferences
    score += _genre_overlap(movie_genres, liked_genres)*15
    score += _genre_overlap(movie_genres, highly_rated_genres) *10
    score += _genre_overlap(movie_genres, favourite_genres) *25
    
    # for negetive feedback
    score -= _genre_overlap(movie_genres, disliked_genres) *20
    score -= _genre_overlap(movie_genres, low_rated_genres) *10
    
    try:
        tmdb_rating = float(row.get("rating", 0) or 0)
        score += int((tmdb_rating - 5.0)*3)
    except (ValueError, TypeError):
        pass
    
    return score

def _genre_overlap(movie_genres: list, signal_genres: list) -> int:
    # Count how many genres from signal_genres appear in movie_genres.
    if not signal_genres:
        return 0
    return sum(1 for g in signal_genres if g in movie_genres)


def _build_feedback_signals(username: str, movies_df: pd.DataFrame) -> dict:
    from profiles import load_profile
    try:
        profile = load_profile(username)
    except FileNotFoundError:
        return _empty_signals()
    
    history = profile.get("watch_history", {})
    
    if isinstance(history, list):
        return _empty_signals()
    
    liked_titles =[]
    disliked_titles = []
    highly_rated_titles = []
    low_rated_titles = []
    favourite_titles = []
    
    for title, feedback in history.items():
        if not isinstance(feedback, dict):
            continue
        
        rating = feedback.get("rating")
        liked = feedback.get("liked")
        favourite = feedback.get("favourite", False)
        
        if liked is True:
            liked_titles.append(title)
        elif liked is False:
            disliked_titles.append(title)
            
        if favourite:
            favourite_titles.append(title)
        
        if isinstance(rating, (int, float)):
            if rating >= 4:
                highly_rated_titles.append(title)
            elif rating <= 2:
                low_rated_titles.append(title)
    
    return{
        "liked" : _titles_to_genres(liked_titles, movies_df),
        "disliked" : _titles_to_genres(disliked_titles, movies_df),
        "highly_rated" : _titles_to_genres(highly_rated_titles, movies_df),
        "low_rated" : _titles_to_genres(low_rated_titles, movies_df),
        "favourite" : _titles_to_genres(favourite_titles, movies_df),
    } 

def _titles_to_genres(titles: list, movies_df: pd.DataFrame) -> list:
    if not titles:
        return[]
    
    matched = movies_df[movies_df["title"].isin(titles)]
    
    genres = []
    for g in matched["genres"]:
        if isinstance(g, list):
            genres.extend(g)
    return genres

def _empty_signals()->dict:
    return{
        "liked": [], "disliked": [], "highly_rated" : [],
        "low_rated": [], "favourite" : [],
    }