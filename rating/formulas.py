import numpy as np


# =========================================================
# SAFE FETCH
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# =========================================================
# PER 90
# =========================================================
def per90(value, mp):
    mp = max(mp, 1)
    return (value / mp) * 90


# =========================================================
# ROLE
# =========================================================
def role(pos):
    pos = str(pos).upper()
    if "GK" in pos:
        return "GK"
    if "DF" in pos:
        return "DEF"
    if "FW" in pos:
        return "FWD"
    return "MID"


# =========================================================
# IMPACT MODEL
# =========================================================
def impact(row):

    mp = f(row, "MP")

    attack = (
        1.5 * per90(f(row, "G"), mp) +
        0.9 * per90(f(row, "A"), mp) +
        0.4 * per90(f(row, "SOnT"), mp)
    )

    build = (
        0.25 * per90(f(row, "P"), mp) +
        0.2 * per90(f(row, "C"), mp)
    )

    defense = (
        0.35 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp) +
        0.2 * per90(f(row, "FW"), mp)
    )

    mistakes = (
        0.25 * per90(f(row, "FC"), mp) +
        0.15 * per90(f(row, "O"), mp)
    )

    yc = -0.4 * f(row, "YC")
    rc = -1.0 * f(row, "RC")   # your fixed rule

    return attack + build + defense - mistakes + yc + rc


# =========================================================
# FINAL RATING
# =========================================================
def rating(row):

    r = role(row.get("Pos.", ""))

    base = impact(row)

    if r == "DEF":
        score = 6 + base * 1.0
    elif r == "MID":
        score = 6 + base * 1.1
    elif r == "FWD":
        score = 6 + base * 1.2
    else:
        score = 6 + base * 0.9

    # smooth distribution (prevents 10 spam)
    score = 6 + (score - 6) * 0.65

    return float(np.clip(score, 3.0, 9.5))
