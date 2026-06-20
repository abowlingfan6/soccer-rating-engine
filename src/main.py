from src.models import defender_rating, midfielder_rating, forward_rating
from src.parser import load_data

def rate_player(row):
    stats = row.to_dict()

    role = stats["Pos"]

    if role == "DF":
        return defender_rating(stats)
    elif role == "MF":
        return midfielder_rating(stats)
    elif role == "FW":
        return forward_rating(stats)
    else:
        return 6

def run(file):
    df = load_data(file)
    df["Rating"] = df.apply(rate_player, axis=1)
    return df.sort_values("Rating", ascending=False)

if __name__ == "__main__":
    result = run("data/mexico_vs_south_africa.csv")
    print(result[["player", "Pos", "Rating"]])
