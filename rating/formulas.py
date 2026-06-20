import numpy as np


def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


def per90(val, mp):
    mp = max(float(mp), 1)
    return (val / mp) * 90


def role(pos):
    pos = str(pos).upper()
    if "GK" in pos:
        return "GK"
    if "DF" in pos:
        return "DEF"
    if "FW" in pos:
        return "FWD"
    return "MID"


def impact(row):

    mp = f(row, "MP")

    attack = (
        1.2 * per90(f(row, "G"), mp) +
        0.7 * per90(f(row, "A"), mp) +
        0.2 * per90(f(row, "SOnT"), mp)
    )

    build = (
        0.15 * per90(f(row, "P"), mp) +
        0.1 * per90(f(row, "C"), mp)
    )

    defense = (
        0.2 * per90(f(row, "Tk"), mp) +
        0.15 * per90(f(row, "INT"), mp)
    )

    errors = (
        0.25 * per90(f(row, "FC"), mp) +
        0.2 * per90(f(row, "O"), mp)
    )

    discipline = (
        -0.5 * f(row, "YC") +
        -1.0 * f(row, "RC")   # EXACT -1 as requested
    )

    return attack + build + defense - errors + discipline


def rating(row):

    r = role(row.get("Pos", row.get("Pos.", "")))

    base = impact(row)

    # 🔥 LOWER BASELINE TO FIX INFLATION
    score = 6 + base * 0.75

    # role tuning (slight only)
    if r == "DEF":
        score *= 0.98
    elif r == "FWD":
        score *= 1.02

    # distribution control (prevents everyone clustering high)
    score = 6 + (score - 6) * 0.55

    # squash extremes properly
    score = 6 + np.tanh(score - 6) * 2.8

    return float(np.clip(score, 3.8, 8.8))
