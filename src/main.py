import pandas as pd

from src.models import defender_rating, midfielder_rating, forward_rating
from src.parser import get_position


def rate_player(row):
    pos = get_position(row.get("Pos"))

    if pos == "DF":
        return defender_rating(row)
    elif pos == "MF":
        return midfielder_rating(row)
    elif pos == "FW":
        return forward_rating(row)
    else:
        # SUB / GK fallback model
        base = (
            6 +
            0.5 * row.get("G", 0) +
            0.3 * row.get("A", 0) +
            0.05 * row.get("P", 0)
        )
        return max(0, min(10, base))


def main():
    # ✅ FIXED: dynamic dataset support
    df = pd.read_csv("data/mexico_vs_southafrica.csv")

    # clean column names (fixes your KeyError issues)
    df.columns = df.columns.str.strip()

    # ensure Pos exists even if missing
    if "Pos" not in df.columns:
        raise ValueError("CSV missing 'Pos' column")

    df["Rating"] = df.apply(rate_player, axis=1)

    # round to 1 decimal
    df["Rating"] = df["Rating"].round(1)

    # final clamp safety
    df["Rating"] = df["Rating"].clip(0, 10)

    print(df[["player", "Pos", "Rating"]])

    df.to_csv("output_ratings.csv", index=False)


if __name__ == "__main__":
    main()
