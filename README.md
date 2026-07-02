# 🎬 Movie Recommender

A CLI-based movie recommendation system built in Python. Answer a short quiz about your mood and preferences, and get 5 personalised movie picks from a dataset of 3,000+ films.

---

## 📁 Project Structure

```
Movie-recommender/
│
├── app.py              ← Entry point — run this
├── quiz.py             ← Quiz questions and user input
├── recommender.py      ← Filtering and scoring engine
├── utils.py            ← Data loading, cleaning, display helpers
├── config.py           ← All settings, paths, and constants
├── requirements.txt
│
└── data/
    ├── tmdb/
    │   ├── tmdb_5000_movies.csv
    │   └── tmdb_5000_credits.csv
    ├── metadata/
    │   └── movies.csv
    └── IMDB/
        ├── title_basics.csv
        ├── title_ratings.csv
        ├── title_crew.csv
        ├── title_episode.csv
        ├── title_principals.csv
        └── name_basics.csv
```

---

## 🚀 Setup

**1. Clone or download the project**

**2. Install dependencies**
```bash
pip install pandas
```

**3. Add your dataset files** into the correct subfolders under `data/` (see structure above).

**4. Run the app**
```bash
python app.py
```

---

## 🎯 How It Works

### Quiz (`quiz.py`)
Asks 7 questions and returns a preferences dictionary:

| Question | Key | Example value |
|----------|-----|---------------|
| Movie or show? | `type` | `"movie"` |
| Favourite genres | `genres` | `["Thriller", "Action"]` |
| Preferred language | `language` | `"English"` |
| How much time? | `runtime` | `"medium"` |
| Happy ending? | `happy_ending` | `"yes"` |
| Family friendly? | `family_friendly` | `"no"` |
| Fast or slow paced? | `pace` | `"fast"` |

### Data Loading (`utils.py`)
Automatically detects which dataset you have and loads it in this priority order:

```
1. data/tmdb/tmdb_5000_movies.csv     ← preferred (richest data)
2. data/metadata/movies.csv           ← fallback
3. data/IMDB/title_basics.csv         ← last resort
```

Movies with fewer than 100 votes or a rating below 5.0 are filtered out to keep recommendations meaningful.

### Recommendation Engine (`recommender.py`)
Filters and scores movies against your preferences:

- **Language filter** — matches your language choice to TMDB's language codes (`"English"` → `"en"`)
- **Runtime filter** — short (under 90 min), medium (90–130 min), long (130+ min)
- **Genre scoring** — counts how many of your preferred genres appear in each movie; more matches = higher rank
- **Rating tiebreaker** — when two movies have the same genre score, the higher-rated one wins

> Note: `happy_ending`, `family_friendly`, and `pace` are collected in the quiz but not yet used in filtering — these fields don't exist in standard datasets and will be wired into the Phase 5 scoring engine.

### Settings (`config.py`)
All tuneable constants live here — no need to dig into other files:

| Constant | Default | Purpose |
|----------|---------|---------|
| `TOP_N` | `5` | Number of recommendations to show |
| `MIN_VOTES` | `100` | Minimum votes to include a movie |
| `MIN_RATING` | `5.0` | Minimum average rating |
| `RUNTIME_OPTIONS` | short/medium/long | Runtime bucket definitions |

---

## 📊 Datasets Used

| Dataset | Source | Used for |
|---------|--------|----------|
| TMDB 5000 Movies | [Kaggle](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) | Primary — genres, language, runtime, ratings |
| TMDB 5000 Credits | Kaggle (same) | Reserved for Phase 6 (cast/director similarity) |
| Kaggle Movie Metadata | [Kaggle](https://www.kaggle.com/datasets/ashishkumarjayswal/movies-dataset) | Fallback |
| IMDB Title Basics | [IMDB Datasets](https://www.kaggle.com/datasets/kunwarakash/imdbdatasets) | Last resort |
| IMDB Title Ratings | IMDB Datasets | Merged with basics for ratings |

---

## 🗺️ Roadmap

- [x] **Phase 1** — CLI quiz + rule-based filtering ← *you are here*
- [x] **Phase 2** — User profiles (save preferences to JSON)
- [ ] **Phase 3** — Watch history (don't recommend already-watched movies)
- [ ] **Phase 4** — Ratings and feedback (likes, dislikes, favourites)
- [ ] **Phase 5** — Scoring engine (weighted points per signal)
- [ ] **Phase 6** — Similar movie recommendations (content-based)
- [ ] **Phase 7** — Machine learning (collaborative filtering, TF-IDF)

---

## 🧠 What I Learned Building This

- Structuring a Python project across multiple modules
- Using `pandas` to load, clean, and filter real-world CSV data
- Parsing JSON stored inside CSV cells (TMDB genre format)
- Separating concerns: quiz / data / logic / display each in its own file
- Using a `config.py` as a single source of truth for all settings
