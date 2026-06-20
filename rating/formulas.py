import numpy as np


# =========================================================
# SAFE GETTERS
# =========================================================
def f(row, key):
    try:
        return float(row.get(key, 0))
    except:
        return 0.0


def per90(v, mp):
    if mp <= 0:
        return 0.0
    return (v / mp) * 90


# =========================================================
# MATCH REALISM LAYER
# =========================================================
# This fixes inflation / makes games comparable

def match_context(row):
    mp = f(row, "MP")

    total_actions = (
        f(row, "P") +
        f(row, "C") +
        f(row, "Tk") +
        f(row, "INT") +
        f(row, "FW")
    )

    # possession proxy (pass involvement)
    possession_proxy = f(row, "P") / max(mp, 1)

    # defensive intensity proxy
    defensive_load = (f(row, "Tk") + f(row, "INT")) / max(mp, 1)

    return {
        "tempo": np.tanh(total_actions / 80),          # 0–1
        "possession": np.tanh(possession_proxy / 60),  # 0–1
        "defense": np.tanh(defensive_load / 2.5)       # 0–1
    }


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
# DISCIPLINE (OPTION A FIX)
# =========================================================
def discipline(row):
    return 0.8 * f(row, "YC") + 1.0 * f(row, "RC")


# =========================================================
# ROLE MODELS WITH REALISM LAYER
# =========================================================
def defender_rating(row, mp):
    ctx = match_context(row)

    impact = (
        attack(row, mp) * 0.45 +
        build(row, mp) * 0.8 +
        defense(row, mp) * 1.35 -
        negative(row, mp) -
        discipline(row)
    )

    # realism adjustment (defenders benefit from high defensive games)
    impact *= (0.85 + 0.3 * ctx["defense"])

    return _normalize(6 + impact)


def midfielder_rating(row, mp):
    ctx = match_context(row)

    impact = (
        attack(row, mp) * 0.9 +
        build(row, mp) * 1.25 +
        defense(row, mp) * 1.0 -
        negative(row, mp) -
        discipline(row)
    )

    # midfielders benefit from tempo + possession control
    impact *= (0.9 + 0.2 * ctx["tempo"] + 0.2 * ctx["possession"])

    return _normalize(6 + impact)


def forward_rating(row, mp):
    ctx = match_context(row)

    impact = (
        attack(row, mp) * 1.45 +
        build(row, mp) * 0.65 +
        defense(row, mp) * 0.4 -
        negative(row, mp) -
        discipline(row)
    )

    # forwards benefit from tempo (more chances in open games)
    impact *= (0.9 + 0.25 * ctx["tempo"])

    return _normalize(6 + impact)


def gk_rating(row, mp):
    ctx = match_context(row)

    impact = (
        1.5 * per90(f(row, "SAV"), mp) +
        1.2 * per90(f(row, "PSAV"), mp) -
        0.8 * per90(f(row, "GC"), mp) -
        discipline(row)
    )

    # goalkeepers are affected by defensive load
    impact *= (0.9 + 0.3 * ctx["defense"])

    return _normalize(6 + impact)


# =========================================================
# FINAL NORMALIZER (PREVENTS 10s / OUTLIERS)
# =========================================================
def _normalize(x):
    x = 6 + np.tanh((x - 6) / 2.2) * 2.3
    return max(3.2, min(9.6, round(x, 2)))
