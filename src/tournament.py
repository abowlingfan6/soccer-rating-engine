import argparse
from pathlib import Path

import pandas as pd

from models import (
    defender_rating,
    midfielder_rating,
    forward_rating,
    sub_rating,
)


# Statistics normalized within each individual match.
# This matches the behavior of Alex's original main.py.
NORMALIZE_COLS = ["P"]


def rate_player(row):
    """
    Calculate a player's match rating using Alex's
    existing position-specific models.
    """

    pos = str(row.get("Pos", "")).strip().upper()

    if pos == "DF":
        return defender_rating(row)

    if pos == "MF":
        return midfielder_rating(row)

    if pos == "FW":
        return forward_rating(row)

    if pos == "SUB":
        return sub_rating(row)

    if pos == "GK":
        # Matches the current behavior in main.py.
        return 6.0

    # Fallback for an unexpected position.
    return midfielder_rating(row)


def add_match_normalization(df):
    """
    Normalize selected statistics within one match.
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
    Read one match CSV and calculate a rating
    for every player.
    """

    print(f"Rating: {csv_file.name}")

    df = pd.read_csv(csv_file)

    # Remove accidental spaces from headings.
    df.columns = df.columns.str.strip()

    # -------------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # -------------------------------------------------

    # Alex's Opta files use Player.
    if "Player" in df.columns:
        df = df.rename(columns={"Player": "player"})

    # Accept either Pos or Pos.
    if "Pos." in df.columns:
        df = df.rename(columns={"Pos.": "Pos"})

    # Also tolerate lowercase player.
    if "PLAYER" in df.columns:
        df = df.rename(columns={"PLAYER": "player"})

    # -------------------------------------------------
    # CHECK REQUIRED COLUMNS
    # -------------------------------------------------

    required = {"player", "Pos"}

    missing = required - set(df.columns)

    if missing:
        print("\nColumns found in this CSV:")
        print(list(df.columns))

        raise ValueError(
            f"{csv_file.name} is missing required column(s): "
            f"{', '.join(sorted(missing))}"
        )

    # -------------------------------------------------
    # CLEAN STATISTICS
    # -------------------------------------------------

    for col in df.columns:

        if col not in ["player", "Pos"]:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            ).fillna(0)

    # -------------------------------------------------
    # NORMALIZE MATCH DATA
    # -------------------------------------------------

    df = add_match_normalization(df)

    # -------------------------------------------------
    # CALCULATE MATCH RATINGS
    # -------------------------------------------------

    df["Rating"] = df.apply(
        rate_player,
        axis=1
    )

    # Ratings stay on Alex's 0-10 scale.
    df["Rating"] = (
        df["Rating"]
        .clip(0, 10)
        .round(1)
    )

    # Use the filename as the match identifier.
    df["Match"] = csv_file.stem

    return df.sort_values(
        "Rating",
        ascending=False
    )


def primary_position(group):
    """
    Determine the player's primary tournament position.

    If a player is listed as SUB in one match but has
    a normal field position in another match, use the
    field position for the tournament leaderboard.
    """

    positions = (
        group["Pos"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    non_sub_positions = positions[
        positions != "SUB"
    ]

    if not non_sub_positions.empty:
        return non_sub_positions.mode().iloc[0]

    if not positions.empty:
        return positions.mode().iloc[0]

    return ""


def build_tournament_table(all_ratings, team):
    """
    Combine all match ratings into a tournament
    leaderboard for one team.

    Tournament Rating is weighted by minutes played.
    """

    rows = []

    for player, group in all_ratings.groupby(
        "player",
        sort=False
    ):

        best_idx = group["Rating"].idxmax()
        worst_idx = group["Rating"].idxmin()

        # Simple average of game ratings
        average_rating = group["Rating"].mean()

        # -----------------------------------------
        # MINUTES PLAYED
        # -----------------------------------------

        if "MP" in group.columns:
            minutes = pd.to_numeric(
                group["MP"],
                errors="coerce"
            ).fillna(0)
        else:
            minutes = pd.Series(
                [0] * len(group),
                index=group.index
            )

        total_minutes = minutes.sum()

        # -----------------------------------------
        # MINUTES-WEIGHTED TOURNAMENT RATING
        # -----------------------------------------

        if total_minutes > 0:

            weighted_rating = (
                group["Rating"] * minutes
            ).sum() / total_minutes

        else:
            # Fallback in case a file has no
            # usable minutes data.
            weighted_rating = average_rating

        rows.append(
            {
                "Player": player,

                "Team": team.replace(
                    "_",
                    " "
                ),

                "Position": primary_position(
                    group
                ),

                "Games": len(group),

                "Minutes": int(
                    total_minutes
                ),

                "Average Rating": round(
                    average_rating,
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

                "Tournament Rating": round(
                    weighted_rating,
                    2
                ),
            }
        )

    tournament = pd.DataFrame(
        rows
    )

    # Rank primarily by the minutes-weighted
    # Tournament Rating.
    tournament = tournament.sort_values(
        [
            "Tournament Rating",
            "Minutes"
        ],
        ascending=[
            False,
            False
        ]
    )

    tournament = tournament.reset_index(
        drop=True
    )

    tournament.insert(
        0,
        "Rank",
        range(
            1,
            len(tournament) + 1
        )
    )

    return tournament


def main():
    """
    Process every CSV for one team.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Rate every match for one team and "
            "create a tournament leaderboard."
        )
    )

    parser.add_argument(
        "team",
        help=(
            "Team folder inside data. "
            "Example: Cabo_Verde"
        )
    )

    args = parser.parse_args()

    team = args.team.strip()

    # -------------------------------------------------
    # FIND TEAM DATA
    # -------------------------------------------------

    input_dir = Path("data") / team

    if not input_dir.exists():

        raise FileNotFoundError(
            f"\nCould not find: {input_dir}\n\n"
            f"Expected a folder such as:\n"
            f"data/{team}/"
        )

    csv_files = sorted(
        input_dir.glob("*.csv")
    )

    if not csv_files:

        raise FileNotFoundError(
            f"\nNo CSV files were found in:\n"
            f"{input_dir}"
        )

    # -------------------------------------------------
    # CREATE OUTPUT FOLDERS
    # -------------------------------------------------

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

    # -------------------------------------------------
    # PROCESS MATCHES
    # -------------------------------------------------

    print()
    print("=" * 60)
    print(f"{team.replace('_', ' ').upper()} TOURNAMENT ENGINE")
    print("=" * 60)

    print(
        f"\nFound {len(csv_files)} match file(s).\n"
    )

    rated_matches = []

    for csv_file in csv_files:

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

    # -------------------------------------------------
    # COMBINE ALL MATCH RATINGS
    # -------------------------------------------------

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

    # -------------------------------------------------
    # BUILD TOURNAMENT LEADERBOARD
    # -------------------------------------------------

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

    # -------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("TOURNAMENT LEADERBOARD")
    print("=" * 60)
    print()

    display_columns = [
    "Rank",
    "Player",
    "Position",
    "Games",
    "Minutes",
    "Average Rating",
    "Tournament Rating",
]

    print(
        tournament[
            display_columns
        ].to_string(
            index=False
        )
    )

    print()
    print("=" * 60)
    print("FILES CREATED")
    print("=" * 60)

    print(
        f"\nIndividual match ratings:\n"
        f"  {match_output_dir}"
    )

    print(
        f"\nAll match ratings:\n"
        f"  {all_match_file}"
    )

    print(
        f"\nTournament leaderboard:\n"
        f"  {tournament_file}"
    )

    print()
    print("Tournament processing complete!")
    print()


if __name__ == "__main__":
    main()
