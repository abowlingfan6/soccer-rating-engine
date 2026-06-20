import sys
import os
import pandas as pd

from rating.formulas import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    gk_rating
)

# =========================================================
# COLUMN MAP (fixes CSV mismatches)
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
    "SAV": "SAV"
}

# =========================================================
# SAFE VALUE FUNCTION
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
# MATCH IMPACT SYSTEM
# =========================================================
def match_impact(row, f):

    impact = 0

    # ---------- POSITIVE ----------
    impact += 1.2 * f(row, "G")
    impact += 0.6 * f(row, "A")
    impact += 0.4 * f(row, "xG")
    impact += 0.3 * f(row, "SCA")

    impact += 0.25 * f(row, "Tk")
    impact += 0.15 * f(row, "SAV")

    impact += 0.1 * f(row, "P")
    impact += 0.1 * f(row, "AP")

    impact += 0.2 * f(row, "C")

    # ---------- NEGATIVE ----------
    impact -= 1.5 * f(row, "YC")
    impact -= 4.0 * f(row, "RC")   # MASSIVE IMPACT
    impact -= 0.3 * f(row, "FC")
    impact -= 0.2 * f(row, "O")

    return impact


# =========================================================
# MAIN RATING FUNCTION
# =========================================================
def calculate_rating(row):

    pos = str(row.get("Pos.", row.get("Pos", "UNKNOWN"))).strip().upper()

    # compute base impact
    impact = match_impact(row, f)

    # position weighting
    if pos == "DF":
        rating = 6 + impact * 0.9

    elif pos == "MF":
        rating = 6 + impact * 1.0

    elif pos == "FW":
        rating = 6 + impact * 1.1

    elif pos == "GK":
        rating = 6 + impact * 0.95

    else:
        rating = 6 + impact

    # ================= RED CARD CAP =================
    if f(row, "RC") > 0:
        rating = min(rating, 3.0)

    # ================= NORMALIZATION =================
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.25)

    return max(0, min(10, round(rating, 2)))


# =========================================================
# RUN MATCH
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

    df["rating"] = df.apply(calculate_rating, axis=1)

    os.makedirs("data", exist_ok=True)

    output_file = f"data/{match_name}_ratings.csv"
    df.to_csv(output_file, index=False)

    print("\n=== TOP PLAYERS ===")
    print(df[["player", "rating"]].head(20))

    print("\nSaved:", output_file)
    print("DONE")


# =========================================================
# CLI ENTRY
# =========================================================
if __name__ == "__main__":

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run_match(match_name)
