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
# COLUMN MAPPING (CRITICAL FIX)
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
# SAFE VALUE EXTRACTOR
# =========================================================
def f(row, key):

    # direct match
    if key in row:
        try:
            return float(row.get(key, 0))
        except:
            return 0.0

    # mapped match
    if key in COLUMN_MAP:
        mapped = COLUMN_MAP[key]
        try:
            return float(row.get(mapped, 0))
        except:
            return 0.0

    return 0.0


# =========================================================
# RATING FUNCTION
# =========================================================
def calculate_rating(row):

    pos = str(row.get("Pos.", row.get("Pos", "UNKNOWN"))).strip().upper()

    if pos == "DF":
        rating = defender_rating(row, lambda k: f(row, k))

    elif pos == "MF":
        rating = midfielder_rating(row, lambda k: f(row, k))

    elif pos == "FW":
        rating = forward_rating(row, lambda k: f(row, k))

    elif pos == "GK":
        rating = gk_rating(row, lambda k: f(row, k))

    else:
        rating = (
            6
            + 0.5 * f(row, "G")
            + 0.3 * f(row, "A")
            + 0.2 * f(row, "xG")
            + 0.1 * f(row, "SCA")
        )

    # normalization (stability layer)
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.30)

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

    # =====================================================
    # DEBUG (optional - remove later)
    # =====================================================
    # print(df.columns)
    # print(df.iloc[0].to_dict())

    df["rating"] = df.apply(calculate_rating, axis=1)

    os.makedirs("data", exist_ok=True)

    out_file = f"data/{match_name}_ratings.csv"
    df.to_csv(out_file, index=False)

    print("\n=== TOP PLAYERS ===")
    print(df[["player", "rating"]].head(20))

    print("\nSaved:", out_file)
    print("DONE")


# =========================================================
# CLI ENTRY POINT
# =========================================================
if __name__ == "__main__":

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run_match(match_name)
