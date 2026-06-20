import pandas as pd

from src.models import defender_rating, midfielder_rating, forward_rating
from src.config import DECIMALS


# -----------------------------
# CORE RATING ROUTER
# -----------------------------
def rate_player(row):
    pos = str(row.get("Pos.", "")).strip().upper()

    try:
        if pos == "DF":
            rating = defender_rating(row)
        elif pos == "MF":
            rating = midfielder_rating(row)
        elif pos == "FW":
            rating = forward_rating(row)
        else:
            rating = 6  # default baseline for unknown positions

        return round(rating, DECIMALS)

    except Exception as e:
        # If something breaks in a row, don't crash entire dataset
        print(f"Error processing player {row.get('player', 'UNKNOWN')}: {e}")
        return 6.0


# -----------------------------
# MAIN EXECUTION
# -----------------------------
def main():

    # Load dataset
    df = pd.read_csv("data/match.csv")

    # Ensure numeric safety (prevents string issues)
    numeric_cols = df.columns.drop(["player", "Pos."])
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Apply rating system
    df["Rating"] = df.apply(rate_player, axis=1)

    # Final formatting rule: 1 decimal place + cap safety
    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    # Sort best to worst
    df = df.sort_values("Rating", ascending=False)

    # Save output
    df.to_csv("data/output_ratings.csv", index=False)

    # Print clean output
    print("\nTOP PLAYER RATINGS\n")
    print(df[["player", "Pos.", "Rating"]].to_string(index=False))


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    main()
