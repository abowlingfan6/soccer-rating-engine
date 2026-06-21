import pandas as pd
import os
import glob

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)


NORMALIZE_COLS = [
    "P", "C", "Tk", "INT", "FW", "FC", "PW", "SOnT", "BS"
]


def rate_player(row):
    pos = str(row.get("Pos", row.get("Pos.", ""))).strip().upper()

    if pos == "DF":
        return defender_rating(row)
    elif pos == "MF":
        return midfielder_rating(row)
    elif pos == "FW":
        return forward_rating(row)
    elif pos == "SUB":
        return sub_rating(row)
    elif pos == "GK":
        return 6.0
    else:
        return midfielder_rating(row)


def add_match_normalization(df):
    for col in NORMALIZE_COLS:
        if col not in df.columns:
            df[col] = 0

        max_value = df[col].max()

        if max_value == 0:
            df[f"{col}_norm"] = 0
        else:
            df[f"{col}_norm"] = df[col] / max_value

    return df


def main():
    csv_files = glob.glob("data/*.csv")

    if not csv_files:
        raise FileNotFoundError("No CSV files found in the data folder.")

    newest_file = max(csv_files, key=os.path.getctime)

    print(f"Reading file: {newest_file}")

    df = pd.read_csv(newest_file)

    df.columns = df.columns.str.strip()

    if "Pos." in df.columns:
        df = df.rename(columns={"Pos.": "Pos"})

    for col in df.columns:
        if col not in ["player", "Pos"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = add_match_normalization(df)

    df["Rating"] = df.apply(rate_player, axis=1)

    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    df = df.sort_values("Rating", ascending=False)

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    match_name = os.path.splitext(os.path.basename(newest_file))[0]
    output_file = os.path.join(output_dir, f"{match_name}_ratings.csv")

    df.to_csv(output_file, index=False)

    print(f"Saved ratings to: {output_file}")
    print(df[["player", "Pos", "Rating"]].to_string(index=False))


if __name__ == "__main__":
    main()
