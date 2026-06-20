import sys
import pandas as pd
import numpy as np
import os

# =========================================================
# INPUT
# =========================================================
match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"

stats_file = f"data/{match_name}_stats.csv"
events_file = f"data/{match_name}_events.csv"

print("\n=== SCHEMA-SAFE RATING ENGINE ===")
print("Match:", match_name)

# =========================================================
# SAFE CSV LOADER
# =========================================================
def safe_read(file):
    if not os.path.exists(file):
        print(f"[WARN] Missing file: {file}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file)
        if df.empty:
            print(f"[WARN] Empty file: {file}")
        return df
    except Exception as e:
        print(f"[ERROR] Cannot read {file}: {e}")
        return pd.DataFrame()

stats = safe_read(stats_file)
events = safe_read(events_file)

# =========================================================
# SCHEMA NORMALIZER (CORE FIX)
# =========================================================
def normalize_schema(df):
    if df.empty:
        return df

    # clean headers
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(".", "", regex=False)
    )

    # unify possible position column names
    rename_map = {
        "Pos": "Pos",
        "position": "Pos",
        "POSITION": "Pos",
        "Pos ": "Pos",
    }

    df.rename(columns=rename_map, inplace=True)

    # ensure player column exists
    if df.columns[0] != "player":
        df.rename(columns={df.columns[0]: "player"}, inplace=True)

    return df

stats = normalize_schema(stats)
events = normalize_schema(events)

# =========================================================
# MERGE SAFE
# =========================================================
if stats.empty and events.empty:
    print("No data found — exiting")
    exit()

if stats.empty:
    df = events.copy()
elif events.empty:
    df = stats.copy()
else:
    df = pd.merge(stats, events, on="player", how="outer")

df = df.fillna(0)

# =========================================================
# SAFE GET FUNCTION (IMPORTANT)
# =========================================================
def get(row, key):
    return row.get(key, 0) if key in row else 0

def num(x):
    try:
        return float(x)
    except:
        return 0.0

BASE = 6.0

# =========================================================
# RATING FUNCTION (SCHEMA SAFE)
# =========================================================
def calculate_rating(row):

    # SAFE POSITION HANDLING
    pos = str(row.get("Pos", "UNKNOWN")).strip().upper()

    # ---------------- STATS ----------------
    xg = num(get(row, "xG"))
    shots = num(get(row, "SOB"))
    sot = num(get(row, "HS"))
    aerial = num(get(row, "HW"))
    duels = num(get(row, "SIB"))

    # ---------------- EVENTS ----------------
    goals = num(get(row, "G"))
    assists = num(get(row, "A"))
    passes = num(get(row, "P"))
    tackles = num(get(row, "Tk"))
    interceptions = num(get(row, "O"))
    crosses = num(get(row, "C"))
    saves = num(get(row, "SAV"))
    yellows = num(get(row, "YC"))
    reds = num(get(row, "RC"))

    rating = BASE

    # =====================================================
    # GK
    # =====================================================
    if pos == "GK":
        rating += 0.15 * saves
        rating += 0.05 * passes
        rating -= 0.20 * shots
        rating += 0.5 if goals == 0 else -0.3

    # =====================================================
    # DEF
    # =====================================================
    elif pos == "DF":
        rating += 1.5 * goals
        rating += 0.75 * assists
        rating += 0.20 * tackles
        rating += 0.20 * interceptions
        rating += 0.10 * passes
        rating += 0.10 * shots
        rating += 0.15 * ((aerial - 50) / 100)

    # =====================================================
    # MID
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

    # =====================================================
    # FW
    # =====================================================
    elif pos == "FW":
        rating += 1.0 * goals
        rating += 0.50 * assists
        rating += 0.40 * xg
        rating += 0.15 * duels
        rating += 0.10 * sot
        rating += 0.10 * shots
        rating += 0.10 * crosses

    # =====================================================
    # UNKNOWN POSITION (SAFE FALLBACK)
    # =====================================================
    else:
        rating += goals + assists * 0.5 + xg * 0.5

    # =====================================================
    # NORMALIZATION (NO MORE EXPLOSIONS)
    # =====================================================
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.3)
    rating = max(0, min(10, rating))

    return round(rating, 2)

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
print(df[["player", "rating"]].head(20))

print("\nSaved:", output_file)
print("DONE")
