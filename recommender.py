import pandas as pd
from config import RUNTIME_OPTIONS, TOP_N_RECOMMENDATIONS

def recommend(movies: pd.DataFrame, preferenes:dict) -> pd.DataFrame:
    df = movies.copy()
    
    # Filtering user's preferences
    if preferenes["type"] != "any":
        df = df[df["type"]== preferenes["type"]]
    
    if preferenes["language"] != "any":
        df = df[df["language"] == preferenes["language"]]
        
    runtime_key = preferenes["runtime"]
    min_rt, max_rt = RUNTIME_OPTIONS[runtime_key]
    df = df[(df["runtime_minutes"] >= min_rt) & (df["runtime_minutes"] <= max_rt) ]
    
    if preferenes["happy_ending"] != "any":
        df = df[df["happy_ending"] == preferenes["happy_ending"]]
    
    if preferenes["pace"] != "any":
        df = df[df["pace"] == preferenes["pace"]]
    
    # For each movie match the preferred genre get a score 1 else 0;
    # We add this as a column so we can sort by it.
    
    preferred_genres = preferenes["genres"]
    df["genre_score"] = df["genre"].apply(
        lambda g: 1 if g in preferred_genres else 0
    )
    
    # now we'll sort the list of preferred genre movies
    # first by score then alphabetically
    
    df = df.sort_values(
        by=["genre_score", "title"],
        ascending=[False, True]
    )
    
    df = df.drop(columns=["genre_score"])
    
    return df.head(TOP_N_RECOMMENDATIONS)