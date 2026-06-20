# src/main.py

import pandas as pd
from src.models import defender_rating, midfielder_rating, forward_rating


def rate_player(row):
    s = row.to_dict()
    pos = s.get("Pos", "")

    if pos == "DF":
        return defender_rating(s)
    elif pos == "MF":
        return midfielder_rating(s)
    elif pos == "FW":
        return forward_rating(s)
    else:
        return 6


def run(file_path):
    df = pd.read_csv(file_path)

    df["Rating"] = df.apply(rate_player, axis=1)

    df = df.sort_values("Rating", ascending=False)

    return df


if __name__ == "__main__":
    result = run("data/mexico_vs_south_africa.csv")

    print("\nTOP PLAYERS:\n")
    print(result[["player", "Pos", "Rating"]])

    result.to_csv("output_ratings.csv", index=False)
    print("\nSaved: output_ratings.csv")
