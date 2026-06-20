import numpy as np
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

    # -----------------------------------------------------
    # SAFE ACCESSOR
    # -----------------------------------------------------
    def f(key):
        return safe_float(row, key)

    # =====================================================
    # GOALKEEPER
    # =====================================================
    if pos == "GK":
        rating = gk_rating(row, f)

    # =====================================================
    # DEFENDER
    # =====================================================
    elif pos == "DF":
        rating = defender_rating(row, f)

    # =====================================================
    # MIDFIELDER
    # =====================================================
    elif pos == "MF":
        rating = midfielder_rating(row, f)

    # =====================================================
    # FORWARD
    # =====================================================
    elif pos == "FW":
        rating = forward_rating(row, f)

    # =====================================================
    # UNKNOWN POSITION (SAFE FALLBACK)
    # =====================================================
    else:
        rating = (
            6
            + 0.5 * f("G")
            + 0.3 * f("A")
            + 0.2 * f("xG")
            + 0.1 * f("SCA")
            - 0.2 * f("RC")
            - 0.1 * f("YC")
        )

    # =====================================================
    # NORMALIZATION (STABILITY LAYER)
    # prevents extreme outliers / broken games
    # =====================================================
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.30)

    # clamp to 0–10
    rating = max(0, min(10, rating))

    return round(rating, 2)


# =========================================================
# OPTIONAL: BULK APPLY FUNCTION (KEEP IF YOU USE IT)
# =========================================================
def apply_ratings(df):
    df["rating"] = df.apply(calculate_rating, axis=1)
    return df

output_file = f"data/{match_name}_ratings.csv"
df.to_csv(output_file, index=False)

# =========================================================
# OUTPUT
# =========================================================
print("\n=== TOP PLAYERS ===")
print(df[["player", "rating"]].head(20))

print("\nSaved:", output_file)
print("DONE")
if __name__ == "__main__":
    import sys
    import os
    import pandas as pd

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"

    stats_file = f"data/{match_name}_stats.csv"
    events_file = f"data/{match_name}_events.csv"

    from rating_engine import safe_read, normalize_schema
    from rating.engine import calculate_rating

    stats = safe_read(stats_file)
    events = safe_read(events_file)

    stats = normalize_schema(stats)
    events = normalize_schema(events)

    if stats.empty and events.empty:
        print("No data found")
        exit()

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

    print(df[["player", "rating"]].head(20))
    print("Saved:", output_file)
