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
