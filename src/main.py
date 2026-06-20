import pandas as pd
from models import defender_rating, midfielder_rating, forward_rating


def rate_player(row):
    pos = row["Pos"]

    # Convert row to dict so your formulas can use keys
    s = row.to_dict()

    if pos == "DF":
        return defender_rating(s)
    elif pos == "MF":
        return midfielder_rating(s)
    elif pos == "FW":
        return forward_rating(s)
    else:
        return 6  # default fallback rating


def run(file_path):
    df = pd.read_csv(file_path)

    # apply rating function
    df["Rating"] = df.apply(rate_player, axis=1)

    # sort best players first
    df = df.sort_values("Rating", ascending=False)

    return df


if __name__ == "__main__":
    file_path = "data/mexico_vs_south_africa.csv"

    result = run(file_path)

    print("\nTOP PLAYERS:\n")
    print(result[["player", "Pos", "Rating"]])

    result.to_csv("output_ratings.csv", index=False)

    print("\nSaved: output_ratings.csv")
