import sys
import pandas as pd
import numpy as np
import os

# =========================================================
# MATCH INPUT (DYNAMIC)
# =========================================================
match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"

stats_file = f"data/{match_name}_stats.csv"
events_file = f"data/{match_name}_events.csv"

print("\n=== RATING ENGINE START ===")
print(f"Match: {match_name}")

# =========================================================
# SAFE FILE LOADING
# =========================================================
def safe_read(file):
    if not os.path.exists(file):
        print(f"Missing file: {file}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file)
        if df.empty:
            print(f"Empty file: {file}")
        return df
    except Exception as e:
        print(f"Error reading {file}: {e}")
        return pd.DataFrame()

stats = safe_read(stats_file)
events = safe_read(events_file)

# If both are empty → stop safely
if stats.empty and events.empty:
    print("No data found — exiting")
    exit()

# =========================================================
# CLEAN HEADERS
# =========================================================
stats.columns = [c.strip() for c in stats.columns] if not stats.empty else []
events.columns = [c.strip() for c in events.columns] if not events.empty else []

# Remove blank rows
stats = stats.dropna(how="all") if not stats.empty else stats
events = events.dropna(how="all") if not events.empty else events

# =========================================================
# STANDARDIZE PLAYER COLUMN
# =========================================================
if not stats.empty:
    stats.rename(columns={stats.columns[0]: "player"}, inplace=True)

if not events.empty:
    events.rename(columns={events.columns[0]: "player"}, inplace=True)

# =========================================================
# MERGE DATASETS
# =========================================================
if stats.empty:
    df = events.copy()
elif events.empty:
    df = stats.copy()
else:
    df = pd.merge(stats, events, on="player", how="outer")

df = df.fillna(0)

# =========================================================
# SAFE NUMBER CONVERTER
# =========================================================
def num(x):
    try:
        return float(x)
    except:
        return 0.0

BASE = 6.0

# =========================================================
# RATING FUNCTION (YOUR MODEL)
# =========================================================
def calculate_rating(row):

    pos = str(row.get("Pos.", ""))

    # -------------------------
    # STATS FILE
    # -------------------------
    xg = num(row.get("xG", 0))
    shots = num(row.get("SOB", 0))
    sot = num(row.get("HS", 0))
    aerial = num(row.get("HW", 0))
    duels = num(row.get("SIB", 0))

    # -------------------------
    # EVENTS FILE
    # -------------------------
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

    # =====================================================
    # GOALKEEPER
    # =====================================================
    if pos == "GK":
        rating += 0.15 * saves
        rating += 0.05 * passes
        rating -= 0.20 * shots
        rating += 0.5 if goals == 0 else -0.3
        rating -= 0.5 * yellows
        rating -= 1.0 * reds

    # =====================================================
    # DEFENDER
    # =====================================================
    elif pos == "DF":
        rating += 1.5 * goals
        rating += 0.75 * assists
        rating += 0.20 * tackles
        rating += 0.20 * interceptions
        rating += 0.10 * passes
        rating += 0.10 * shots
        rating += 0.15 * (aerial - 50) / 100
        rating -= 0.30 * yellows
        rating -= 0.80 * reds

    # =====================================================
    # MIDFIELDER
    # =====================================================
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

    # =====================================================
    # FORWARD
    # =====================================================
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

    # fallback
    else:
        rating += goals + assists * 0.5 + xg

    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.3)

return round(min(max(rating, 0), 10), 2)

# =========================================================
# APPLY MODEL
# =========================================================
df["rating"] = df.apply(calculate_rating, axis=1)

df = df.sort_values("rating", ascending=False)

# =========================================================
# SAVE OUTPUT
# =========================================================
os.makedirs("data", exist_ok=True)

output_file = f"data/{match_name}_ratings.csv"
df.to_csv(output_file, index=False)

# =========================================================
# OUTPUT
# =========================================================
print("\n=== TOP PLAYERS ===")
print(df[["player", "Pos.", "rating"]].head(20))

print(f"\nSaved: {output_file}")
print("DONE")
