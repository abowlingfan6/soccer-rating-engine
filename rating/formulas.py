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

    # ---------------- ATTACK (more selective now) ----------------
    attack = (
        1.4 * per90(f(row, "G"), mp) +
        0.9 * per90(f(row, "A"), mp) +
        0.25 * per90(f(row, "SOnT"), mp) +
        0.15 * per90(f(row, "BS"), mp)
    )

    # ---------------- BUILDUP (lower weight to reduce inflation) ----------------
    build = (
        0.10 * per90(f(row, "P"), mp) +
        0.08 * per90(f(row, "C"), mp) +
        0.05 * per90(f(row, "FW"), mp)
    )

    # ---------------- DEFENSE (slightly stronger separation) ----------------
    defense = (
        0.25 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp)
    )

    # ---------------- NEGATIVE EVENTS (VERY IMPORTANT FIX) ----------------
    mistakes = (
        0.35 * per90(f(row, "FC"), mp) +
        0.30 * per90(f(row, "O"), mp)
    )

    # ---------------- DISCIPLINE (your rule kept) ----------------
    discipline = (
        -0.6 * f(row, "YC") +
        -1.0 * f(row, "RC")   # hard -1
    )

    return attack + build + defense - mistakes + discipline


def rating(row):

    r = role(row.get("Pos", row.get("Pos.", "")))
    mp = f(row, "MP")

    base = impact(row)

    # ---------------- KEY FIX: spread amplifier ----------------
    time_factor = np.sqrt(min(mp / 90, 1.0))

    score = 6 + base * 1.2 * time_factor

    # ---------------- ROLE DIFFERENTIATION (slightly stronger now) ----------------
    if r == "DEF":
        score -= 0.15
    elif r == "FWD":
        score += 0.20

    # ---------------- FINAL SPREAD CONTROL (THIS FIXES 9.3 CLUSTERING) ----------------
    # pushes average toward 6.5 instead of everyone drifting high
    score = 6.5 + (score - 6.5) * 0.75

    return float(score)
