# utils.py
# Small helper functions used by multiple files.
# Putting them here avoids copy-pasting the same logic everywhere.

import pandas as pd
from config import DATA_PATH


def load_movies() -> pd.DataFrame:
    """
    Reads movies.csv and returns it as a pandas DataFrame.
    Each row is one movie; columns are its attributes.
    """
    return pd.read_csv(DATA_PATH)


def display_recommendations(movies: pd.DataFrame) -> None:
    """
    Prints the recommended movies in a clean, readable format.
    Receives a filtered/sorted DataFrame and just handles the display.
    """
    if movies.empty:
        print("\n  No movies matched your preferences. Try broadening your choices!\n")
        return

    print("\n" + "=" * 50)
    print("  🎬  YOUR TOP RECOMMENDATIONS")
    print("=" * 50)

    # iterrows() lets us loop over a DataFrame row by row.
    # `i` is the row index, `row` is a Series (like a dict) of that row's values.
    for i, (_, row) in enumerate(movies.iterrows(), start=1):
        runtime_display = f"{row['runtime_minutes']} min"
        print(f"\n  {i}. {row['title']}")
        print(f"     Genre: {row['genre']}  |  Language: {row['language']}")
        print(f"     Runtime: {runtime_display}  |  Type: {row['type'].capitalize()}")

    print("\n" + "=" * 50 + "\n")


def numbered_menu(options: list, prompt: str) -> str:
    """
    Prints a numbered list of options and returns the user's chosen value.
    Keeps re-asking until a valid number is entered.

    Example output:
        1. Action
        2. Comedy
        3. Drama
        > Enter number: 2
        → returns "Comedy"
    """
    print()
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = int(input(f"\n  {prompt}: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print(f"  Please enter a number between 1 and {len(options)}.")
        except ValueError:
            # int() throws ValueError if the user types something that isn't a number
            print("  Please enter a valid number.")


def multi_select_menu(options: list, prompt: str) -> list:
    """
    Like numbered_menu, but lets the user pick multiple options.
    They type comma-separated numbers, e.g. "1,3,5"

    Returns a list of the chosen values.
    """
    print()
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")

    while True:
        raw = input(f"\n  {prompt} (e.g. 1,3): ")

        # Strip whitespace, split by comma, convert each part to int
        try:
            indices = [int(x.strip()) for x in raw.split(",")]
            if all(1 <= idx <= len(options) for idx in indices):
                return [options[idx - 1] for idx in indices]
            else:
                print(f"  Please enter numbers between 1 and {len(options)}.")
        except ValueError:
            print("  Please enter valid numbers separated by commas.")