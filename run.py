import sys
import pandas as pd
import numpy as np
import os

# =========================================================
# LOAD DATA
# =========================================================
def load_data(match_name):
    path = f"data/{match_name}.csv"

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ File not found: {path}")

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    return df


# =========================================================
# ROLE CLASSIFIER
# =========================================================
def get_role(pos):
    pos = str(pos).upper()

    if "GK" in pos:
        return "GK"
    if "DF" in pos:
        return "DEF"
    if "FW" in pos:
        return "FWD"
    return "MID"


# =========================================================
# PER 90 NORMALIZER
# =========================================================
def per90(val, mp):
    if mp <= 0:
        return 0
    return (val / mp) * 90


# =========================================================
# CORE RATING MODEL
# =========================================================
def compute_rating(row):

    mp = float(row.get("MP", 90))
    mp = max(mp, 1)

    role = get_role(row.get("Pos.", ""))

    # =========================
    # OFFENSIVE
    # =========================
    g = per90(row.get("G", 0), mp)
    a = per90(row.get("A", 0), mp)
    sot = per90(row.get("SOnT", 0), mp)
    soff = per90(row.get("SOffT", 0), mp)
    bs = per90(row.get("BS", 0), mp)

    attack = (
        1.5 * g +
        1.0 * a +
        0.2 * sot +
        0.1 * soff +
        0.2 * bs
    )

    # =========================
    # MIDFIELD / CONTROL
    # =========================
    p = per90(row.get("P", 0), mp)
    c = per90(row.get("C", 0), mp)
    tk = per90(row.get("Tk", 0), mp)
    inte = per90(row.get("INT", 0), mp)
    fw = per90(row.get("FW", 0), mp)

    midfield = (
        0.03 * p +
        0.10 * c +
        0.20 * tk +
        0.18 * inte +
        0.12 * fw
    )

    # =========================
    # DEFENSE
    # =========================
    fc = per90(row.get("FC", 0), mp)
    o = per90(row.get("O", 0), mp)

    defense = (
        0.25 * tk +
        0.20 * inte -
        0.15 * fc -
        0.10 * o
    )

    # =========================
    # GK
    # =========================
    sav = per90(row.get("SAV", 0), mp)
    psav = per90(row.get("PSAV", 0), mp)

    gk = 0.9 * sav + 0.6 * psav

    # =========================
    # DISCIPLINE (FIXED EXACT RULE)
    # =========================
    yc = row.get("YC", 0)
    rc = row.get("RC", 0)

    discipline = (-0.4 * yc) + (-1.0 * rc)   # EXACT red card = -1 impact unit

    # =========================
    # BASE IMPACT BY ROLE
    # =========================
    if role == "GK":
        impact = gk
    elif role == "DEF":
        impact = defense + attack * 0.25
    elif role == "MID":
        impact = midfield + attack * 0.35
    else:
        impact = attack + midfield * 0.15

    # =========================
    # MINUTES STABILITY (IMPORTANT)
    # prevents tiny-minutes inflation
    # =========================
    minutes_factor = np.tanh(mp / 70)

    impact = (impact * minutes_factor) + discipline

    # =========================
    # FINAL SCALING (FIXES YOUR "MAX 7" PROBLEM)
    # =========================
    rating = 6 + impact * 2.8   # stronger spread

    # soft stabilization (NOT compression trap)
    rating = 6 + (rating - 6) / (1 + abs(rating - 6) * 0.08)

    # boost standout performances
    if impact > 1.5:
        rating += 0.35
    if impact > 2.5:
        rating += 0.60

    # final realistic bounds
    rating = max(3.5, min(9.7, rating))

    return round(rating, 1)


# =========================================================
# RUN PIPELINE
# =========================================================
def run(match_name):

    df = load_data(match_name)

    df["rating"] = df.apply(compute_rating, axis=1)

    print("\n=== RATINGS ===")
    print(df[["player", "Pos.", "MP", "rating"]])

    out_path = f"data/{match_name}_ratings.csv"
    df.to_csv(out_path, index=False)

    print("\n✅ Saved:", out_path)


# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run(match_name)
