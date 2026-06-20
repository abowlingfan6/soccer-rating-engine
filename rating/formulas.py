import numpy as np


def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


def per90(value, mp):
    mp = max(float(mp), 1)
    return (value / mp) * 90


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

    # ===== ATTACK =====
    attack = (
        1.25 * per90(f(row, "G"), mp) +
        0.75 * per90(f(row, "A"), mp) +
        0.20 * per90(f(row, "SOnT"), mp) +
        0.15 * per90(f(row, "BS"), mp)
    )

    # ===== PROGRESSION =====
    build = (
        0.15 * per90(f(row, "P"), mp) +
        0.10 * per90(f(row, "C"), mp) +
        0.10 * per90(f(row, "FW"), mp)
    )

    # ===== DEFENSE =====
    defense = (
        0.20 * per90(f(row, "Tk"), mp) +
        0.20 * per90(f(row, "INT"), mp)
    )

    # ===== MISTAKES =====
    mistakes = (
        0.25 * per90(f(row, "FC"), mp) +
        0.20 * per90(f(row, "O"), mp)
    )

    # ===== DISCIPLINE (IMPORTANT FIX) =====
    discipline = (
        -0.5 * f(row, "YC") +
        -1.0 * f(row, "RC")   # EXACT -1 penalty
    )

    return attack + build + defense - mistakes + discipline


def rating(row):

    r = role(row.get("Pos", row.get("Pos.", "")))
    mp = f(row, "MP")

    base = impact(row)

    # ===== PER 90 CONTROL (light touch, not flattening) =====
    time_factor = np.sqrt(min(mp / 90, 1.0))  # keeps subs from exploding

    score = 6 + base * 1.05 * time_factor

    # ===== ROLE BIAS (very small, just realism) =====
    if r == "DEF":
        score -= 0.1
    elif r == "FWD":
        score += 0.15

    return float(score)
