import pandas as pd
import os

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)


# ---------- SAFE POSITION HANDLER ----------
def rate_player(row):
    pos = str(row.get("Pos", "")).strip()

    if pos == "DF":
        return defender_rating(row)
    elif pos == "MF":
        return midfielder_rating(row)
    elif pos == "FW":
        return forward_rating(row)
    elif pos == "Sub":
        return sub_rating(row)
    else:
        return 0


# ---------- LOAD DATA SAFELY ----------
def load_data():
    file_path = "data/mexico_vs_southafrica.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"CSV not found at {file_path}. "
            "Make sure your dataset is inside the /data folder."
        )

    return pd.read_csv(file_path)


# ---------- MAIN PIPELINE ----------
def main():
    df = load_data()

    # apply rating engine
    df["Rating"] = df.apply(rate_player, axis=1)

    # final safety clamp (prevents any edge-case 10+)
    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    # ensure output folder exists
    os.makedirs("output", exist_ok=True)

    # export results
    output_path = "output/rated_players.csv"
    df.to_csv(output_path, index=False)

    print(f"Ratings complete. File saved to: {output_path}")


if __name__ == "__main__":
    main()
