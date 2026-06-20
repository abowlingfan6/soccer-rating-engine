import numpy as np


# =========================================================
# SAFE GET
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# =========================================================
# PER 90 NORMALIZATION
# =========================================================
def per90(val, mp):
    mp = max(float(mp), 1)
    return (val / mp) * 90


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
# CORE IMPACT MODEL
# =========================================================
def impact(row):

    mp = f(row, "MP")

    attack = (
        1.6 * per90(f(row, "G"), mp) +
        0.9 * per90(f(row, "A"), mp) +
        0.3 * per90(f(row, "SOnT"), mp)
    )

    build = (
        0.25 * per90(f(row, "P"), mp) +
        0.2 * per90(f(row, "C"), mp)
    )

    defense = (
        0.35 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp)
    )

    errors = (
        0.3 * per90(f(row, "FC"), mp) +
        0.2 * per90(f(row, "O"), mp)
    )

    discipline = (
        -0.4 * f(row, "YC") +
        -1.0 * f(row, "RC")   # FIXED: red card = -1
    )

    return attack + build + defense - errors + discipline


# =========================================================
# FINAL RATING (DISTRIBUTION CONTROL)
# =========================================================
def rating(row):

    r = role(row.get("Pos", row.get("Pos.", "")))

    base = impact(row)

    # role scaling
    if r == "DEF":
        score = 6 + base * 0.95
    elif r == "MID":
        score = 6 + base * 1.05
    elif r == "FWD":
        score = 6 + base * 1.15
    else:
        score = 6 + base * 0.9

    # spread correction (THIS fixes “everyone same rating”)
    score = 6 + (score - 6) * 0.6

    # squash extremes into realistic soccer range
    score = 6 + np.tanh(score - 6) * 3.2

    return float(np.clip(score, 3.5, 9.3))
