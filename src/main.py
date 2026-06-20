import pandas as pd
import numpy as np


# ----------------------------
# POSITION DETECTION
# ----------------------------
def get_position(pos):
    if pd.isna(pos):
        return "SUB"

    pos = str(pos).upper().strip()

    if "DF" in pos:
        return "DF"
    elif "MF" in pos:
        return "MF"
    elif "FW" in pos:
        return "FW"
    elif "GK" in pos:
        return "GK"
    else:
        return "SUB"


# ----------------------------
# PERCENTILE CONVERSION
# ----------------------------
def percentile_rank(series):
    return series.rank(pct=True)


# ----------------------------
# ROLE WEIGHTS (SIMPLIFIED CORE)
# ----------------------------
def base_attack_score(row):
    return (
        row["G"] * 4 +
        row["A"] * 3 +
        row["SOnT"] * 1.5 +
        row["BS"] * 1.2 -
        row["SOffT"] * 0.5
    )


def base_mid_score(row):
    return (
        row["P"] * 0.2 +
        row["C"] * 0.3 +
        row["Tk"] * 0.8 +
        row["INT"] * 0.8 +
        row["FW"] * 0.5
    )


def base_def_score(row):
    return (
        row["Tk"] * 1.2 +
        row["INT"] * 1.2 +
        row["FW"] * 0.7 -
        row["FC"] * 0.5
    )


def base_gk_score(row):
    return row.get("SAV", 0) * 2 + row.get("PSAV", 0) * 3


def base_sub_score(row):
    return (
        row["G"] * 3 +
        row["A"] * 2 +
        row["C"] * 0.5 +
        row["Tk"] * 0.5
    )


# ----------------------------
# MAIN RATING FUNCTION
# ----------------------------
def rate_players(df):

    df["Pos"] = df["Pos"].apply(get_position)

    # compute raw base scores
    df["raw_attack"] = df.apply(base_attack_score, axis=1)
    df["raw_mid"] = df.apply(base_mid_score, axis=1)
    df["raw_def"] = df.apply(base_def_score, axis=1)
    df["raw_gk"] = df.apply(base_gk_score, axis=1)
    df["raw_sub"] = df.apply(base_sub_score, axis=1)

    # pick role score
    def choose(row):
        if row["Pos"] == "FW":
            return row["raw_attack"]
        elif row["Pos"] == "MF":
            return row["raw_mid"]
        elif row["Pos"] == "DF":
            return row["raw_def"]
        elif row["Pos"] == "GK":
            return row["raw_gk"]
        else:
            return row["raw_sub"]

    df["raw_score"] = df.apply(choose, axis=1)

    # ----------------------------
    # PERCENTILE NORMALIZATION (KEY FIX)
    # ----------------------------
    df["pct"] = percentile_rank(df["raw_score"])

    # convert to 0–10 football rating scale
    df["Rating"] = 5 + (df["pct"] * 5)

    # clamp + round
    df["Rating"] = df["Rating"].clip(0, 10).round(1)

    return df


# ----------------------------
# RUN
# ----------------------------
def main():

    # IMPORTANT: your actual file
    df = pd.read_csv("data/mexico_vs_southafrica.csv")

    df.columns = df.columns.str.strip()

    df = rate_players(df)

    print(df[["player", "Pos", "Rating"]])

    df.to_csv("output_ratings.csv", index=False)


if __name__ == "__main__":
    main()
