import os
import pandas as pd

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)


# ---------- POSITION ROUTER ----------
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


# ---------- LOAD DATA ----------
def load_data():
    file_path = "data/mexico_vs_southafrica.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Missing dataset: {file_path}")

    return pd.read_csv(file_path)


# ---------- MAIN ----------
def main():
    df = load_data()

    df["Rating"] = df.apply(rate_player, axis=1)

    # safety clamp
    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    # ---------- FIXED OUTPUT PATH (IMPORTANT) ----------
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "rated_players.csv")

    df.to_csv(output_path, index=False)

    print("Ratings complete!")
    print("Saved file to:", output_path)
    print("Output folder contains:", os.listdir(output_dir))


if __name__ == "__main__":
    main()
