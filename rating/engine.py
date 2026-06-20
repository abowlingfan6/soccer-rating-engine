import pandas as pd
import numpy as np
import os

from rating.formulas import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    gk_rating
)


# ================= SAFE READER =================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# ================= MAIN RATING =================
def calculate_rating(row):

    pos = str(row.get("Pos", "UNKNOWN")).upper()

    if pos == "DF":
        rating = defender_rating(row, lambda k: f(row, k))

    elif pos == "MF":
        rating = midfielder_rating(row, lambda k: f(row, k))

    elif pos == "FW":
        rating = forward_rating(row, lambda k: f(row, k))

    elif pos == "GK":
        rating = gk_rating(row, lambda k: f(row, k))

    else:
        rating = 6

    # normalize
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.3)
    return max(0, min(10, round(rating, 2)))


# ================= RUN MATCH =================
def run_match(match_name):

    stats_path = f"data/{match_name}_stats.csv"
    events_path = f"data/{match_name}_events.csv"

    stats = pd.read_csv(stats_path) if os.path.exists(stats_path) else pd.DataFrame()
    events = pd.read_csv(events_path) if os.path.exists(events_path) else pd.DataFrame()

    if stats.empty and events.empty:
        print("No data found")
        return

    if stats.empty:
        df = events
    elif events.empty:
        df = stats
    else:
        df = pd.merge(stats, events, on="player", how="outer")

    df = df.fillna(0)

    df["rating"] = df.apply(calculate_rating, axis=1)

    os.makedirs("data", exist_ok=True)

    out = f"data/{match_name}_ratings.csv"
    df.to_csv(out, index=False)

    print(df[["player", "rating"]].head(20))
    print("Saved:", out)
