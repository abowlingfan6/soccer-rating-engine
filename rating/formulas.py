import numpy as np


# =========================================================
# SAFE CONVERSIONS
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


def per90(value, mp):
    if mp <= 0:
        return 0.0
    return (value / mp) * 90


# =========================================================
# COMMON IMPACT BLOCKS
# =========================================================
def attack_block(row, mp):
    return (
        1.4 * per90(f(row, "G"), mp) +
        0.8 * per90(f(row, "A"), mp) +
        0.4 * per90(f(row, "SOnT"), mp) +
        0.2 * per90(f(row, "BS"), mp)
    )


def build_block(row, mp):
    return (
        0.25 * per90(f(row, "P"), mp) +
        0.20 * per90(f(row, "C"), mp)
    )


def defense_block(row, mp):
    return (
        0.30 * per90(f(row, "Tk"), mp) +
        0.25 * per90(f(row, "INT"), mp) +
        0.20 * per90(f(row, "PW"), mp) +
        0.15 * per90(f(row, "FW"), mp)
    )


def negative_block(row, mp):
    return (
        0.25 * per90(f(row, "FC"), mp) +
        0.15 * per90(f(row, "O"), mp)
    )


def discipline_block(row, mp):
    return (
        1.2 * f(row, "YC") +
        3.5 * f(row, "RC")
    )


# =========================================================
# ROLE FORMULAS
# =========================================================
def defender_rating(row, mp):
    impact = 0

    impact += attack_block(row, mp) * 0.6
    impact += build_block(row, mp) * 0.8
    impact += defense_block(row, mp) * 1.2
    impact -= negative_block(row, mp)
    impact -= discipline_block(row, mp)

    return 6 + impact


def midfielder_rating(row, mp):
    impact = 0

    impact += attack_block(row, mp) * 0.9
    impact += build_block(row, mp) * 1.2
    impact += defense_block(row, mp) * 1.0
    impact -= negative_block(row, mp)
    impact -= discipline_block(row, mp)

    return 6 + impact


def forward_rating(row, mp):
    impact = 0

    impact += attack_block(row, mp) * 1.4
    impact += build_block(row, mp) * 0.7
    impact += defense_block(row, mp) * 0.4
    impact -= negative_block(row, mp)
    impact -= discipline_block(row, mp)

    return 6 + impact


def gk_rating(row, mp):
    impact = 0

    impact += 1.5 * per90(f(row, "SAV"), mp)
    impact += 1.2 * per90(f(row, "PSAV"), mp)
    impact -= 0.8 * per90(f(row, "GC"), mp)

    impact -= discipline_block(row, mp)

    return 6 + impact
