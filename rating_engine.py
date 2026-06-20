import pandas as pd
import numpy as np
import os

# -------------------------
# LOAD BOTH CSV FILES
# -------------------------
stats_file = "data/mexico_sa_stats.csv"
events_file = "data/mexico_sa_events.csv"

stats = pd.read_csv(stats_file)
events = pd.read_csv(events_file)

# Clean column names
stats.columns = [c.strip() for c in stats.columns]
events.columns = [c.strip() for c in events.columns]

# Remove totals / empty rows
stats = stats[stats.iloc[:, 0].notna()]
events = events[events.iloc[:, 0].notna()]

# -------------------------
# STANDARDIZE PLAYER NAME COLUMN
# -------------------------
stats.rename(columns={stats.columns[0]: "player"}, inplace=True)
events.rename(columns={events.columns[0]: "player"}, inplace=True)

# -------------------------
# MERGE BOTH DATASETS
# -------------------------
df = pd.merge(stats, events, on="player", how="outer")

# Fill missing values
df = df.fillna(0)

# -------------------------
# SAFE NUMBER FUNCTION
# -------------------------
def num(x):
    try:
        return float(x)
    except:
        return 0.0

BASE = 6.0

# -------------------------
# RATING FUNCTION
# -------------------------
def calculate_rating(row):

    pos = row.get("Pos.", "")

    # ---- stats file ----
    xg = num(row.get("xG", 0))
    shots = num(row.get("SOB", 0))
    sot = num(row.get("HS", 0))
    duels = num(row.get("SIB", 0))
    aerial = num(row.get("HW", 0))

    # ---- events file ----
    goals = num(row.get("G", 0))
    assists = num(row.get("A", 0))
    passes = num(row.get("P", 0))
    tackles = num(row.get("Tk", 0))
    interceptions = num(row.get("O", 0))
    crosses = num(row.get("C", 0))
    saves = num(row.get("SAV", 0))
    yellows = num(row.get("YC", 0))
    reds = num(row.get("RC", 0))

    rating = BASE

    # -------------------------
    # GOALKEEPER
    # -------------------------
    if pos == "GK":
        rating += 0.15 * saves
        rating += 0.05 * passes
        rating -= 0.20 * shots
        rating += 0.5 if goals == 0 else -0.3
        rating -= 0.5 * yellows
        rating -= 1.0 * reds

    # -------------------------
    # DEFENDER
    # -------------------------
    elif pos == "DF":
        rating += 1.5 * goals
        rating += 0.75 * assists
        rating += 0.20 * tackles
        rating += 0.20 * interceptions
        rating += 0.15 * (aerial - 50) / 100
        rating += 0.10 * passes
        rating += 0.10 * shots
        rating -= 0.30 * yellows
        rating -= 0.80 * reds

    # -------------------------
    # MIDFIELDER
    # -------------------------
    elif pos == "MF":
        rating += 1.25 * goals
        rating += 0.75 * assists
        rating += 0.20 * tackles
        rating += 0.20 * interceptions
        rating += 0.15 * passes
        rating += 0.40 * xg
        rating += 0.10 * sot
        rating += 0.05 * shots
        rating += 0.10 * crosses
        rating -= 0.30 * yellows
        rating -= 0.80 * reds

    # -------------------------
    # FORWARD
    # -------------------------
    elif pos == "FW":
        rating += 1.0 * goals
        rating += 0.50 * assists
        rating += 0.40 * xg
        rating += 0.15 * duels
        rating += 0.10 * sot
        rating += 0.10 * shots
        rating += 0.10 * crosses
        rating -= 0.20 * yellows
        rating -= 0.60 * reds

    else:
        rating += goals + assists * 0.5

    return round(rating, 2)

# -------------------------
# APPLY MODEL
# -------------------------
df["rating"] = df.apply(calculate_rating, axis=1)

df = df.sort_values("rating", ascending=False)

# -------------------------
# SAVE OUTPUT
# -------------------------
os.makedirs("data", exist_ok=True)

df.to_csv("data/player_ratings.csv", index=False)

# -------------------------
# OUTPUT
# -------------------------
print("\n=== PLAYER RATINGS ===")
print(df[["player", "Pos.", "rating"]].head(20))

print("\nSaved: data/player_ratings.csv")
