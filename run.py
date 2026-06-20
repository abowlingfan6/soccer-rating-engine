import os
import pandas as pd
import numpy as np
from rating.formulas import rating as calc_rating


# =========================================================
# CLEAN COLUMN FIXER
# =========================================================
def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(".", "", regex=False)
    )
    return df


# =========================================================
# MAIN PIPELINE
# =========================================================
def run(match_name):

    file_path = f"data/{match_name}.csv"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"=== Running {file_path} ===")

    df = pd.read_csv(file_path)
    df = clean_columns(df)

    # ensure player exists
    if "player" not in df.columns:
        print("❌ Missing 'player' column in dataset")
        return

    # fill missing values
    df = df.fillna(0)

    # compute ratings
    df["rating"] = df.apply(calc_rating, axis=1)

    # clamp final output (extra safety)
    df["rating"] = df["rating"].clip(3, 9.5)

    # save output
    out_path = f"data/{match_name}_ratings.csv"
    df.to_csv(out_path, index=False)

    # top players
    print("\n🏆 TOP PLAYERS")
    print(df[["player", "rating"]].sort_values("rating", ascending=False).head(15))

    print(f"\n✅ Saved: {out_path}")


# =========================================================
# ENTRY POINT
# =========================================================
if __name__ == "__main__":
    import sys

    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run(match_name)
