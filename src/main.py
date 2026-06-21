import pandas as pd
import pathlib

from src.models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating
)

# ---------- CONFIG ----------
INPUT_FILE = "data/mexico_vs_southafrica.csv"
OUTPUT_FILE = "output/rated_players.csv"


# ---------- POSITION LOGIC ----------
def rate_player(row):
    # handle both Pos and Pos.
    pos = str(row.get("Pos", row.get("Pos.", ""))).strip().upper()

    if pos == "DF":
        return defender_rating(row)

    elif pos == "MF":
        return midfielder_rating(row)

    elif pos == "FW":
        return forward_rating(row)

    elif pos == "SUB":
        return sub_rating(row)

    else:
        # fallback (prevents crashes on weird labels)
        return midfielder_rating(row)


# ---------- MAIN ----------
def main():
    # load dataset
    df = pd.read_csv(INPUT_FILE)

    # clean column names (fix hidden spacing issues)
    df.columns = df.columns.str.strip()

    # compute ratings
    df["Rating"] = df.apply(rate_player, axis=1)

    # clamp formatting (1 decimal, max 10)
    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    # ensure output folder exists (CI-safe)
    pathlib.Path("output").mkdir(parents=True, exist_ok=True)

    # save output
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n✅ Ratings complete")
    print(df[["player", "Pos", "Rating"]].head())


if __name__ == "__main__":
    main()
