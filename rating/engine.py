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
# COLUMN MAP
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
    elif pos == "MF":
        return "MID"
    elif pos == "FW":
        return "FWD"
    elif pos == "GK":
        return "GK"

    return "MID"


# =========================================================
# MATCH IMPACT (FIXED RED CARD HANDLING)
# =========================================================
def match_impact(row, f):

    minutes = f(row, "MP")
    if minutes <= 0:
        minutes = 90

    impact = 0

    # ================= OFFENSE =================
    impact += 1.3 * per90(f(row, "G"), minutes)
    impact += 0.7 * per90(f(row, "A"), minutes)
    impact += 0.5 * per90(f(row, "xG"), minutes)
    impact += 0.4 * per90(f(row, "SCA"), minutes)

    # ================= BUILD =================
    impact += 0.25 * per90(f(row, "AP"), minutes)
    impact += 0.2 * per90(f(row, "C"), minutes)

    # ================= DEFENSE =================
    impact += 0.3 * per90(f(row, "Tk"), minutes)

    # ================= NEGATIVE =================
    impact -= 0.3 * per90(f(row, "FC"), minutes)
    impact -= 0.25 * per90(f(row, "O"), minutes)

    # ================= DISCIPLINE (FIXED) =================
    impact -= 1.8 * per90(f(row, "YC"), minutes)

    # 🚨 FIX: red card is NOT per90 anymore
    impact -= 2.5 * f(row, "RC")

    return impact


# =========================================================
# RATING FUNCTION
# =========================================================
def calculate_rating(row):

    role = get_role(row.get("Pos.", row.get("Pos", "UNKNOWN")))

    impact = match_impact(row, f)

    # ================= ROLE WEIGHT =================
    if role == "DEF":
        rating = 6 + impact * 0.85
    elif role == "MID":
        rating = 6 + impact * 1.00
    elif role == "FWD":
        rating = 6 + impact * 1.15
    elif role == "GK":
        rating = 6 + impact * 0.90
    else:
        rating = 6 + impact

    # ================= FIXED RED CARD PENALTY =================
    if f(row, "RC") > 0:

        minutes = f(row, "MP")
        minutes_factor = max(0.25, minutes / 90)

        # realistic punishment instead of hard cap
        rating -= 1.8 * minutes_factor

    # ================= STABILITY NORMALIZATION =================
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.15)

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
    # ENSURE MP EXISTS
    # =====================================================
    if "MP" not in df.columns:
        df["MP"] = 90

    df["MP"] = df["MP"].fillna(90)
    df["MP"] = df["MP"].clip(lower=1)

    # =====================================================
    # RATING
    # =====================================================
    df["rating"] = df.apply(calculate_rating, axis=1)

    # =====================================================
    # SAVE
    # =====================================================
    os.makedirs("data", exist_ok=True)

    output_file = f"data/{match_name}_ratings.csv"
    df.to_csv(output_file, index=False)

    print("\n=== TOP PLAYERS ===")
    print(df[["player", "rating"]].sort_values("rating", ascending=False).head(20))

    print("\nSaved:", output_file)
    print("DONE")


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run_match(match_name)
