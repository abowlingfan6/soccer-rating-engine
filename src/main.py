import pandas as pd
import os
import glob

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)


def rate_player(row):
    pos = str(row["Pos"]).strip().upper()

    if pos == "DF":
        return defender_rating(row)

    elif pos == "MF":
        return midfielder_rating(row)

    elif pos == "FW":
        return forward_rating(row)

    elif pos == "GK":
        return 6.0  # Placeholder until you create a GK formula

    else:  # SUB or anything else
        return sub_rating(row)


def main():

    # Find all CSV files in data folder
    csv_files = glob.glob("data/*.csv")

    if not csv_files:
        raise FileNotFoundError(
            "No CSV files found in the data folder."
        )

    # Use most recently uploaded CSV
    newest_file = max(csv_files, key=os.path.getctime)

    print(f"Reading file: {newest_file}")

    df = pd.read_csv(newest_file)

    # Remove accidental spaces from column names
    df.columns = df.columns.str.strip()

    # Verify required column exists
    if "Pos" not in df.columns:
        raise ValueError(
            f"Missing 'Pos' column. Found columns: {list(df.columns)}"
        )

    # Calculate ratings
    df["Rating"] = df.apply(rate_player, axis=1)

    # Clean ratings
    df["Rating"] = df["Rating"].clip(0, 10)
    df["Rating"] = df["Rating"].round(1)

    # Sort highest first
    df = df.sort_values(
        by="Rating",
        ascending=False
    )

    # Create output folder if needed
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create output filename from match filename
    match_name = os.path.splitext(
        os.path.basename(newest_file)
    )[0]

    output_file = os.path.join(
        output_dir,
        f"{match_name}_ratings.csv"
    )

    # Save file
    df.to_csv(output_file, index=False)

    print(f"Saved ratings to: {output_file}")


if __name__ == "__main__":
    main()
