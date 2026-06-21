import pandas as pd
import numpy as np


# ----------------------------
# CLEAN POSITION HANDLING
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
# PERCENTILE FUNCTION
# ----------------------------
def percentile(series):
    return series.rank(pct=True)


# ----------------------------
# BASE ROLE MODELS
# (simple + stable, no inflation)
# ----------------------------

def fw_score(r):
    return (
        r.get("G", 0) * 4 +
        r.get("A", 0) * 3 +
        r.get("SOnT", 0) * 1.5 +
        r.get("BS", 0) * 1.2 -
        r.get("SOffT", 0) * 0.5
    )


def mf_score(r):
    return (
        r.get("P", 0) * 0.2 +
        r.get("C", 0) * 0.3 +
        r.get("Tk", 0) * 0.9 +
        r.get("INT", 0) * 0.9 +
        r.get("FW", 0) * 0.5 -
        r.get("FC", 0) * 0.3
    )


def df_score(r):
    return (
        r.get("Tk", 0) * 1.2 +
        r.get("INT", 0) * 1.2 +
        r.get("FW", 0) * 0.7 -
        r.get("FC", 0) * 0.6 -
        r.get("RC", 0) * 2.0
    )


def gk_score(r):
    return (
        r.get("SAV", 0) * 2 +
        r.get("PSAV", 0) * 3
    )


def sub_score(r):
    return (
        r.get("G", 0) * 3 +
        r.get("A", 0) * 2 +
        r.get("C", 0) * 0.5 +
        r.get("Tk", 0) * 0.5
    )


# ----------------------------
# MAIN RATING ENGINE
# ----------------------------
def rate_players(df):

    df.columns = df.columns.str.strip()

    df["Pos"] = df["Pos"].apply(get_position)

    # raw scores
    df["raw"] = df.apply(
        lambda r:
        fw_score(r) if r["Pos"] == "FW" else
        mf_score(r) if r["Pos"] == "MF" else
        df_score(r) if r["Pos"] == "DF" else
        gk_score(r) if r["Pos"] == "GK" else
        sub_score(r),
        axis=1
    )

    # ----------------------------
    # IMPORTANT FIX: CONTEXT SCALING
    # ----------------------------
    df["pct"] = percentile(df["raw"])

    # curved scaling (prevents automatic 10s)
    df["Rating"] = 4.5 + (df["pct"] ** 1.6) * 4.8

    # final constraints
    df["Rating"] = df["Rating"].clip(0, 9.5)
    df["Rating"] = df["Rating"].round(1)

    return df


# ----------------------------
# RUN
# ----------------------------
def main():

    df = pd.read_csv("data/mexico_vs_southafrica.csv")

    df = rate_players(df)

    print(df[["player", "Pos", "Rating"]])

    df.to_csv("output_ratings.csv", index=False)


if __name__ == "__main__":
    main()
