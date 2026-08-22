import argparse
from pathlib import Path
import pandas as pd

try:
    from src.models import (
        defender_rating,
        midfielder_rating,
        forward_rating,
        sub_rating,
    )
except ModuleNotFoundError:
    from models import (
        defender_rating,
        midfielder_rating,
        forward_rating,
        sub_rating,
    )


# This matches the normalization currently used in main.py
NORMALIZE_COLS = ["P"]


def rate_player(row):
    """
    Use Alex's existing position-specific rating models.
    """
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
        # This matches the current main.py behavior
        return 6.0

    else:
        # Same fallback currently used in main.py
        return midfielder_rating(row)


def add_match_normalization(df):
    """
    Normalize selected statistics within each individual match.
    This matches Alex's current main.py.
    """
    for col in NORMALIZE_COLS:

        if col not in df.columns:
            df[col] = 0

        max_value = df[col].max()

        if max_value == 0:
            df[f"{col}_norm"] = 0

        else:
            df[f"{col}_norm"] = df[col] / max_value

    return df


def rate_match(csv_file):
    """
    Read one match CSV and calculate a rating for every player.
    """
    df = pd.read_csv(csv_file)

    # Clean up column names
    df.columns = df.columns.str.strip()

    # Accept Pos. as well as Pos
    if "Pos." in df.columns:
        df = df.rename(columns={"Pos.": "Pos"})

    # Make sure the file contains the two essential columns
    required = {"player", "Pos"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{csv_file.name} is missing required column(s): "
            f"{', '.join(sorted(missing))}"
        )

    # Convert statistics to numbers
    for col in df.columns:

        if col not in ["player", "Pos"]:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    # Normalize statistics within this match
    df = add_match_normalization(df)

    # Calculate rating
    df["Rating"] = df.apply(
        rate_player,
        axis=1
    )

    # Keep scores between 0 and 10
    df["Rating"] = (
        df["Rating"]
        .clip(0, 10)
        .round(1)
    )

    # Record which match this row came from
    df["Match"] = csv_file.stem

    return df.sort_values(
        "Rating",
        ascending=False
    )


def primary_position(group):
    """
    Find the player's normal tournament position.

    If someone appears as SUB in one game but MF in another,
    use MF rather than SUB as the tournament position.
    """
    positions = (
        group["Pos"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    non_sub = positions[
        positions != "SUB"
    ]

    if not non_sub.empty:
        return non_sub.mode().iloc[0]

    if not positions.empty:
        return positions.mode().iloc[0]

    return ""


def build_tournament_table(all_ratings, team):
    """
    Combine all individual match ratings into one
    tournament leaderboard.
    """
    rows = []

    for player, group in all_ratings.groupby(
        "player",
        sort=False
    ):

        best_idx = group["Rating"].idxmax()
        worst_idx = group["Rating"].idxmin()

        average = group["Rating"].mean()

        rows.append(
            {
                "Player": player,
                "Team": team,
                "Position": primary_position(group),

                "Games": len(group),

                "Average Rating": round(
                    average,
                    2
                ),

                "Best Rating": round(
                    group.loc[
                        best_idx,
                        "Rating"
                    ],
                    1
                ),

                "Best Match": group.loc[
                    best_idx,
                    "Match"
                ],

                "Worst Rating": round(
                    group.loc[
                        worst_idx,
                        "Rating"
                    ],
                    1
                ),

                "Worst Match": group.loc[
                    worst_idx,
                    "Match"
                ],

                # Version 1:
                # tournament rating = average match rating
                "Tournament Rating": round(
                    average,
                    2
                ),
            }
        )

    tournament = pd.DataFrame(rows)

    tournament = tournament.sort_values(
        [
            "Tournament Rating",
            "Games"
        ],
        ascending=[
            False,
            False
        ]
    )

    return tournament.reset_index(
        drop=True
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Rate every match for one team "
            "and create a tournament leaderboard."
        )
    )

    parser.add_argument(
        "team",
        help=(
            "Team folder name inside data. "
            "Example: Scotland"
        )
    )

    args = parser.parse_args()

    team = args.team.strip()

    input_dir = (
        Path("data") /
        team
    )

    # Make sure the team folder exists
    if not input_dir.exists():

        raise FileNotFoundError(
            f"Could not find {input_dir}. "
            "Create that folder and put "
            "the team's CSV files inside it."
        )

    # Find every CSV in the team's folder
    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    if not csv_files:

        raise FileNotFoundError(
            f"No CSV files found in "
            f"{input_dir}."
        )

    # Output locations
    output_dir = (
        Path("output") /
        team
    )

    match_output_dir = (
        output_dir /
        "match_ratings"
    )

    match_output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    rated_matches = []

    print(
        f"\nProcessing "
        f"{len(csv_files)} match(es) "
        f"for {team}...\n"
    )

    # -------------------------
    # RATE EACH MATCH
    # -------------------------

    for csv_file in csv_files:

        print(
            f"Rating: "
            f"{csv_file.name}"
        )

        rated = rate_match(
            csv_file
        )

        rated_matches.append(
            rated
        )

        match_output_file = (
            match_output_dir /
            f"{csv_file.stem}_ratings.csv"
        )

        rated.to_csv(
            match_output_file,
            index=False
        )

    # -------------------------
    # COMBINE ALL MATCHES
    # -------------------------

    all_ratings = pd.concat(
        rated_matches,
        ignore_index=True
    )

    all_match_file = (
        output_dir /
        f"{team}_all_match_ratings.csv"
    )

    all_ratings.to_csv(
        all_match_file,
        index=False
    )

    # -------------------------
    # TOURNAMENT RATINGS
    # -------------------------

    tournament = build_tournament_table(
        all_ratings,
        team
    )

    tournament_file = (
        output_dir /
        f"{team}_tournament_ratings.csv"
    )

    tournament.to_csv(
        tournament_file,
        index=False
    )

    # -------------------------
    # DISPLAY RESULTS
    # -------------------------

    print(
        "\nTournament leaderboard:\n"
    )

    print(
        tournament[
            [
                "Player",
                "Position",
                "Games",
                "Average Rating",
                "Tournament Rating",
            ]
        ].to_string(
            index=False
        )
    )

    print("\nSaved:")

    print(
        f"  Individual match ratings: "
        f"{match_output_dir}"
    )

    print(
        f"  All match ratings:        "
        f"{all_match_file}"
    )

    print(
        f"  Tournament leaderboard:   "
        f"{tournament_file}"
    )


if __name__ == "__main__":
    main()
