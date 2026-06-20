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
# SAFE CONVERTER
# =========================================================
def safe_float(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# =========================================================
# MAIN RATING FUNCTION
# =========================================================
def calculate_rating(row):

    pos = str(row.get("Pos", "UNKNOWN")).strip().upper()

    def f(key):
        return safe_float(row, key)

    if pos == "GK":
        rating = gk_rating(row, f)

    elif pos == "DF":
        rating = defender_rating(row, f)

    elif pos == "MF":
        rating = midfielder_rating(row, f)

    elif pos == "FW":
        rating = forward_rating(row, f)

    else:
        rating = (
            6
            + 0.5 * f("G")
            + 0.3 * f("A")
            + 0.2 * f("xG")
            + 0.1 * f("SCA")
        )

    # =====================================================
    # NORMALIZATION (stability layer)
    # =====================================================
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.30)

    rating = max(0, min(10, rating))

    return round(rating, 2)


# =========================================================
# PIPELINE RUNNER (CLI ENTRY POINT)
# =========================================================
def run_match(match_name: str):

    stats_file = f"data/{match_name}_stats.csv"
    events_file = f"data/{match_name}_events.csv"

    # load safely
    stats = pd.read_csv(stats_file) if os.path.exists(stats_file) else pd.DataFrame()
    events = pd.read_csv(events_file) if os.path.exists(events_file) else pd.DataFrame()

    if stats.empty and events.empty:
        print(f"No data found for {match_name}")
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
