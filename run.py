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
# LOAD MATCH FILE
# =========================================================
def load_match(match_name):
    file_path = f"data/{match_name}.csv"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    df = pd.read_csv(file_path)
    df = df.fillna(0)

    # standardize column name
    if "Pos." not in df.columns:
        if "Pos" in df.columns:
            df.rename(columns={"Pos": "Pos."}, inplace=True)

    return df


# =========================================================
# ROLE MAP
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
# MAIN CALCULATION
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
# RUN PIPELINE
# =========================================================
def run(match_name):

    df = load_match(match_name)
    if df is None or df.empty:
        print("❌ No data loaded")
        return

    df["rating"] = df.apply(calculate, axis=1)

    df = df.sort_values("rating", ascending=False)

    os.makedirs("data", exist_ok=True)

    output = f"data/{match_name}_ratings.csv"
    df.to_csv(output, index=False)

    print("\n🏆 TOP PLAYERS")
    print(df[["player", "Pos.", "rating"]].head(20))

    print("\nSaved:", output)


# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "match"
    run(match_name)
