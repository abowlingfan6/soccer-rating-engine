import pandas as pd
import numpy as np
import os

# -------------------------
# LOAD DATA
# -------------------------
FILE_PATH = "data/mexico_sa.csv"

df = pd.read_csv(FILE_PATH)

# Clean column names
df.columns = [c.strip() for c in df.columns]

# Remove empty rows
df = df[df["Pos."].notna()]
df = df[df["Pos."] != "Total"]

# -------------------------
# SAFE NUMBER CONVERTER
# -------------------------
def num(x):
    try:
        return float(x)
    except:
        return 0.0


BASE = 6.0


# -------------------------
# RATING MODEL
# -------------------------
def rating(row):

    pos = row["Pos."]

    ap = num(row.get("AP", 0))
    hw = num(row.get("HW", 0))
    sib = num(row.get("SIB", 0))
    sob = num(row.get("SOB", 0))
    hs = num(row.get("HS", 0))
    xg = num(row.get("xG", 0))
    fa = num(row.get("FaA", 0))
    sca = num(row.get("SCA", 0))

    r = BASE

    # GK
    if pos == "GK":
        r += 0.10 * hs
        r += 0.05 * ap
        r -= 0.05 * sob
        r += 0.5 if sob == 0 else -0.2

    # DEF
    elif pos == "DF":
        r += 1.50 * xg
        r += 0.75 * sca
        r += 0.20 * (hw - 50) / 100
        r += 0.15 * (sib - 50) / 100
        r += 0.15 * (ap - 60) / 100
        r += 0.20 * hs
        r += 0.05 * sob
        r += 0.05 * fa

    # MID
    elif pos == "MF":
        r += 1.25 * xg
        r += 0.50 * sca
        r += 0.20 * (sib - 50) / 100
        r += 0.15 * (hw - 50) / 100
        r += 0.15 * (ap - 60) / 100
        r += 0.40 * xg
        r += 0.10 * hs
        r += 0.05 * sob
        r += 0.075 * fa

    # FW
    elif pos == "FW":
        r += 1.00 * xg
        r += 0.50 * sca
        r += 0.40 * xg
        r += 0.20 * (hw - 50) / 100
        r += 0.15 * (sib - 50) / 100
        r += 0.10 * hs
        r += 0.05 * sob
        r += 0.10 * sca
        r += 0.10 * fa

    else:
        r += xg + sca * 0.5

    return round(r, 2)


# -------------------------
# APPLY MODEL
# -------------------------
df["rating"] = df.apply(rating, axis=1)

df = df.sort_values("rating", ascending=False)

# -------------------------
# SAVE OUTPUT
# -------------------------
os.makedirs("data", exist_ok=True)

df.to_csv("data/player_ratings.csv", index=False)

print("\n=== TOP PLAYERS ===")
print(df[["Pos.", "rating"]].head(20))

print("\nSaved: data/player_ratings.csv")
