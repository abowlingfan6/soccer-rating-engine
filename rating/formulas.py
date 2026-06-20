import numpy as np


def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


def role(pos):
    pos = str(pos).upper()
    if "GK" in pos:
        return "GK"
    if "DF" in pos:
        return "DEF"
    if "FW" in pos:
        return "FWD"
    return "MID"


# ---------------- SAFE per90 (FIXED) ----------------
def per90(val, mp):
    mp = float(mp)

    if mp <= 0:
        return 0

    # 🚨 KEY FIX: prevents tiny minutes from exploding
    scale = min(mp / 90, 1.0)

    return val * scale


def impact(row):

    mp = f(row, "MP")

    attack = (
        1.4 * per90(f(row, "G"), mp) +
        0.9 * per90(f(row, "A"), mp) +
        0.2 * per90(f(row, "SOnT"), mp)
    )

    build = (
        0.10 * per90(f(row, "P"), mp) +
        0.08 * per90(f(row, "C"), mp)
    )

    defense = (
        0.25 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp)
    )

    mistakes = (
        0.35 * per90(f(row, "FC"), mp) +
        0.30 * per90(f(row, "O"), mp)
    )

    discipline = (
        -0.6 * f(row, "YC") +
        -1.0 * f(row, "RC")
    )

    return attack + build + defense - mistakes + discipline


def rating(row):

    r = role(row.get("Pos", row.get("Pos.", "")))
    mp = f(row, "MP")

    base = impact(row)

    # ---------------- MINUTES REALISM PENALTY (CRITICAL FIX) ----------------
    # prevents subs from competing with full 90s
    minutes_factor = (mp / 90) ** 1.3

    score = 6 + base * minutes_factor * 1.6

    # role bias (small)
    if r == "DEF":
        score -= 0.1
    elif r == "FWD":
        score += 0.15

    return float(score)
