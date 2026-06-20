import sys
import os
import glob
import pandas as pd

from rating.formulas import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    gk_rating
)

# =========================================================
# AUTO FILE FINDER (FIXES YOUR ERROR)
# =========================================================
def find_file(match_name):
    patterns = [
        f"data/{match_name}.csv",
        f"data/{match_name}_stats.csv",
        f"data/{match_name}*.csv"
    ]

    for p in patterns:
        matches = glob.glob(p)
        if matches:
            return matches[0]

    return None


# =========================================================
# LOAD DATA
# =========================================================
def load_match(match_name):
    file_path = find_file(match_name)

    if file_path is None:
        print(f"❌ No file found for: {match_name}")
        print("👉 Make sure your CSV is inside /data folder")
        return None

    print(f"✅ Using file: {file_path}")

    df = pd.read_csv(file_path)
    df = df.fillna(0)

    # standardize position column
    if "Pos." not in df.columns and "Pos" in df.columns:
        df.rename(columns={"Pos": "Pos."}, inplace=True)

    return df


# =========================================================
# ROLE CLASSIFIER
# =========================================================
def get_role(pos):
    pos = str(pos).upper()

    if pos == "GK":
        return "GK"
    elif pos == "DF":
        return "DEF"
    elif pos == "FW":
        return "FWD"
    else:
        return "MID"


# =========================================================
# SAFE VALUE
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# =========================================================
# MAIN RATING
# =========================================================
def calculate(row):

    mp = float(row.get("MP", 90))
    if mp <= 0:
        mp = 90

    role = get_role(row.get("Pos.", row.get("Pos", "MID")))

    if role == "GK":
        return gk_rating(row, mp)
    elif role == "DEF":
        return defender_rating(row, mp)
    elif role == "MID":
        return midfielder_rating(row, mp)
    else:
        return forward_rating(row, mp)


# =========================================================
# RUN MATCH
# =========================================================
def run(match_name):

    df = load_match(match_name)
    if df is None or df.empty:
        print("❌ No data loaded")
        return

    df["rating"] = df.apply(calculate, axis=1)

    df = df.sort_values("rating", ascending=False)

    os.makedirs("data", exist_ok=True)

    output_file = f"data/{match_name}_ratings.csv"
    df.to_csv(output_file, index=False)

    print("\n🏆 TOP PLAYERS")
    print(df[["player", "Pos.", "rating"]].head(20))

    print("\n💾 Saved:", output_file)


# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "match"
    run(match_name)
