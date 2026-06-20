import sys
import os
import pandas as pd
import numpy as np

# =========================================================
# OPTIONAL IMPORTS
# =========================================================
from rating.formulas import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    gk_rating
)

# =========================================================
# SAFE COLUMN MAP
# =========================================================
COLUMN_MAP = {
    "SOG": "SOnT",
    "S": "SIB",
    "Tk": "Tk",
    "AP": "AP",
    "P": "P",
    "C": "C",
    "G": "G",
    "A": "A",
    "xG": "xG",
    "xA": "xA",
    "FC": "FC",
    "YC": "YC",
    "RC": "RC",
    "SCA": "SCA",
    "O": "O",
    "SAV": "SAV",
    "MP": "MP"
}

# =========================================================
# SAFE FETCH
# =========================================================
def f(row, key):

    if key in row:
        try:
            return float(row.get(key, 0))
        except:
            return 0.0

    if key in COLUMN_MAP:
        mapped = COLUMN_MAP[key]
        try:
            return float(row.get(mapped, 0))
        except:
            return 0.0

    return 0.0


# =========================================================
# PER 90
# =========================================================
def per90(value, minutes):
    if minutes <= 0:
        return 0.0
    return (value / minutes) * 90


# =========================================================
# ROLE
# =========================================================
def get_role(pos):
    pos = str(pos).upper()

    if pos == "DF":
        return "DEF"
    if pos == "MF":
        return "MID"
    if pos == "FW":
        return "FWD"
    if pos == "GK":
        return "GK"

    return "MID"


# =========================================================
# RAW IMPACT MODEL (NO NORMALIZATION HERE)
# =========================================================
def match_impact(row, f):

    minutes = f(row, "MP")
    if minutes <= 0:
        minutes = 90

    impact = 0

    # ATTACK
    impact += 1.3 * per90(f(row, "G"), minutes)
    impact += 0.7 * per90(f(row, "A"), minutes)
    impact += 0.5 * per90(f(row, "xG"), minutes)
    impact += 0.4 * per90(f(row, "SCA"), minutes)

    # BUILDUP
    impact += 0.3 * per90(f(row, "AP"), minutes)
    impact += 0.25 * per90(f(row, "C"), minutes)

    # DEFENSE
    impact += 0.3 * per90(f(row, "Tk"), minutes)

    # NEGATIVE EVENTS
    impact -= 0.3 * per90(f(row, "FC"), minutes)
    impact -= 0.25 * per90(f(row, "O"), minutes)

    # DISCIPLINE
    impact -= 0.2 * f(row, "YC")

    # RED CARD HARD PENALTY (realistic)
    if f(row, "RC") > 0:
        minutes_factor = f(row, "MP") / 90 if f(row, "MP") > 0 else 1
        impact -= 4.0 * (1 + (1 - minutes_factor))

    return impact


# =========================================================
# PERCENTILE RATING (THIS FIXES 10s COMPLETELY)
# =========================================================
def percentile_rank(value, series):
    return np.mean(series <= value)


# =========================================================
# MAIN ENGINE
# =========================================================
def run_match(match_name):

    stats_file = f"data/{match_name}_stats.csv"
    events_file = f"data/{match_name}_events.csv"

    stats = pd.read_csv(stats_file) if os.path.exists(stats_file) else pd.DataFrame()
    events = pd.read_csv(events_file) if os.path.exists(events_file) else pd.DataFrame()

    if stats.empty and events.empty:
        print("No data found")
        return

    if stats.empty:
        df = events.copy()
    elif events.empty:
        df = stats.copy()
    else:
        df = pd.merge(stats, events, on="player", how="outer")

    df = df.fillna(0)

    # =====================================================
    # RAW IMPACT FIRST
    # =====================================================
    df["raw"] = df.apply(match_impact, axis=1, f=f)

    # =====================================================
    # ROLE ADJUSTMENT (SLIGHT, BEFORE RANKING)
    # =====================================================
    def role_adjust(row):
        role = get_role(row.get("Pos.", row.get("Pos", "UNKNOWN")))
        if role == "DEF":
            return row["raw"] * 0.95
        if role == "FWD":
            return row["raw"] * 1.05
        if role == "GK":
            return row["raw"] * 0.90
        return row["raw"]

    df["adj_raw"] = df.apply(role_adjust, axis=1)

    # =====================================================
    # PERCENTILE SCORING (KEY FIX)
    # =====================================================
    series = df["adj_raw"]

    df["rating"] = df["adj_raw"].apply(lambda x: percentile_rank(x, series) * 10)

    # =====================================================
    # FINAL CLEANING
    # =====================================================
    df["rating"] = df["rating"].round(2)

    os.makedirs("data", exist_ok=True)

    output_file = f"data/{match_name}_ratings.csv"
    df.to_csv(output_file, index=False)

    print("\n=== TOP PLAYERS ===")
    print(df.sort_values("rating", ascending=False)[["player", "rating"]].head(20))

    print("\nSaved:", output_file)
    print("DONE")


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run_match(match_name)
