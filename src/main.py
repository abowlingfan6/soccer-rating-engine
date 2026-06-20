import pandas as pd
import argparse

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)


# ---------- POSITION ROUTER ----------
def rate_player(row):
    pos = str(row.get("Pos", "")).upper()

    if "GK" in pos:
        return 5.5

    if "DF" in pos:
        return defender_rating(row)

    if "FW" in pos:
        return forward_rating(row)

    if "SUB" in pos:
        return sub_rating(row)

    return midfielder_rating(row)


# ---------- CLEAN OUTPUT ----------
def clean_ratings(df):
    df["Rating"] = df["Rating"].clip(0, 10).round(1)
    return df


# ---------- MAIN ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file",
        type=str,
        default="data/mexico_vs_southafrica.csv"
    )

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    # FIX COLUMN ISSUES
    df.columns = df.columns.str.strip()
    df.rename(columns={"Pos.": "Pos"}, inplace=True)

    # DROP EMPTY ROWS
    df = df.dropna(subset=["player", "Pos"])

    # APPLY MODEL
    df["Rating"] = df.apply(rate_player, axis=1)

    # CLEAN OUTPUT
    df = clean_ratings(df)

    # SORT
    df = df.sort_values("Rating", ascending=False)

    print(df[["player", "Pos", "Rating"]])


if __name__ == "__main__":
    main()
