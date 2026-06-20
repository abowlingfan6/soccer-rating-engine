import os
import pandas as pd
import numpy as np
from rating.formulas import rating as calc_rating


def clean_columns(df):
    df.columns = df.columns.str.strip().str.replace(".", "", regex=False)
    return df


def run(match_name):

    file_path = f"data/{match_name}.csv"

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    print(f"=== Running {file_path} ===")

    df = pd.read_csv(file_path)
    df = clean_columns(df)
    df = df.fillna(0)

    if "player" not in df.columns:
        print("❌ Missing player column")
        return

    df["rating"] = df.apply(calc_rating, axis=1)

    # FINAL SAFETY CLAMP (THIS FIXES YOUR HIGH RATINGS)
    df["rating"] = df["rating"].clip(3.5, 8.8)

    out_path = f"data/{match_name}_ratings.csv"
    df.to_csv(out_path, index=False)

    print(f"✅ Saved: {out_path}")
    print("Done.")


if __name__ == "__main__":
    import sys
    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run(match_name)
