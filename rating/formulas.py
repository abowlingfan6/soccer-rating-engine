import numpy as np


# =========================================================
# SAFE GETTER
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


# =========================================================
# PER 90 SCALING (ONLY NORMALIZATION USED)
# =========================================================
def per90(value, mp):
    if mp <= 0:
        return 0.0
    return (value / mp) * 90


# =========================================================
# CORE STAT BLOCKS
# =========================================================
def attack(row, mp):
    return (
        1.4 * per90(f(row, "G"), mp) +
        0.8 * per90(f(row, "A"), mp) +
        0.4 * per90(f(row, "SOnT"), mp) +
        0.2 * per90(f(row, "BS"), mp)
    )


def build(row, mp):
    return (
        0.25 * per90(f(row, "P"), mp) +
        0.2 * per90(f(row, "C"), mp)
    )


def defense(row, mp):
    return (
        0.3 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp) +
        0.2 * per90(f(row, "FW"), mp)
    )


def negative(row, mp):
    return (
        0.25 * per90(f(row, "FC"), mp) +
        0.15 * per90(f(row, "O"), mp)
    )


# =========================================================
# DISCIPLINE (OPTION A ONLY)
# =========================================================
def discipline(row):
    return 0.8 * f(row, "YC") + 1.0 * f(row, "RC")


# =========================================================
# ROLE MODELS
# =========================================================
def defender_rating(row, mp):
    impact = (
        attack(row, mp) * 0.5 +
        build(row, mp) * 0.8 +
        defense(row, mp) * 1.3 -
        negative(row, mp) -
        discipline(row)
    )

    return _normalize(6 + impact)


def midfielder_rating(row, mp):
    impact = (
        attack(row, mp) * 0.9 +
        build(row, mp) * 1.2 +
        defense(row, mp) * 1.0 -
        negative(row, mp) -
        discipline(row)
    )

    return _normalize(6 + impact)


def forward_rating(row, mp):
    impact = (
        attack(row, mp) * 1.4 +
        build(row, mp) * 0.7 +
        defense(row, mp) * 0.4 -
        negative(row, mp) -
        discipline(row)
    )

    return _normalize(6 + impact)


def gk_rating(row, mp):
    impact = (
        1.5 * per90(f(row, "SAV"), mp) +
        1.2 * per90(f(row, "PSAV"), mp) -
        0.8 * per90(f(row, "GC"), mp) -
        discipline(row)
    )

    return _normalize(6 + impact)


# =========================================================
# STABLE NORMALIZER (NO 10 SPAM)
# =========================================================
def _normalize(x):
    x = 6 + np.tanh((x - 6) / 2.0) * 2.2
    return max(3.0, min(9.5, round(x, 2)))
