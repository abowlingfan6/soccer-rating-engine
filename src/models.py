import numpy as np

# -----------------------------
# SAFE GET
# -----------------------------
def get(row, col):
    val = row[col] if col in row else 0
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0
    return val


# -----------------------------
# PER 90 NORMALIZER
# -----------------------------
def per90(row, value):
    mp = max(get(row, "MP"), 1)
    return value * (90 / mp)


# -----------------------------
# BASE OUTFIELD MODEL
# -----------------------------
def base_outfield_rating(row):
    r = 6

    # attacking (scaled per 90 lightly)
    r += per90(row, 1.0 * get(row, "G"))
    r += per90(row, 0.5 * get(row, "A"))
    r += per90(row, 0.25 * get(row, "SOnT"))

    # passing contribution (heavily damped)
    r += 0.02 * get(row, "P")
    r += 0.03 * get(row, "C")

    # defensive actions (small but stable)
    r += per90(row, 0.05 * get(row, "Tk"))
    r += per90(row, 0.05 * get(row, "INT"))

    # duels / activity
    r += per90(row, 0.08 * get(row, "FW"))
    r += per90(row, 0.08 * get(row, "PW"))

    # negatives
    r -= per90(row, 0.08 * get(row, "FC"))
    r -= per90(row, 0.10 * get(row, "YC"))
    r -= per90(row, 0.60 * get(row, "RC"))
    r -= per90(row, 0.20 * get(row, "O"))

    return r


# -----------------------------
# DEFENDERS
# -----------------------------
def defender_rating(row):
    r = base_outfield_rating(row)

    # defensive bias
    r += per90(row, 0.15 * get(row, "Tk"))
    r += per90(row, 0.15 * get(row, "INT"))

    # reduce attacker-style inflation
    r -= per90(row, 0.20 * get(row, "SOnT"))

    return r


# -----------------------------
# MIDFIELDERS (FIXED INFLATION)
# -----------------------------
def midfielder_rating(row):
    r = base_outfield_rating(row)

    # 🔥 KEY FIX: passing volume no longer over-inflates rating
    pass_involvement = get(row, "P") + get(row, "C")
    r += 0.005 * pass_involvement  # very small scaling

    # creativity must be output-based, not volume-based
    r += per90(row, 0.25 * get(row, "A"))
    r += per90(row, 0.20 * get(row, "SOnT"))

    # anti-9.7 control: prevents passive high-pass midfielders
    if get(row, "G") == 0 and get(row, "A") == 0:
        r -= 0.6

    # possession-only inflation clamp
    if pass_involvement > 60 and get(row, "A") == 0 and get(row, "G") == 0:
        r -= 0.4

    return r


# -----------------------------
# FORWARDS
# -----------------------------
def forward_rating(row):
    r = base_outfield_rating(row)

    # must show goal threat
    if get(row, "G") == 0 and get(row, "SOnT") < 2:
        r -= 0.7

    r += per90(row, 0.20 * get(row, "SOnT"))

    return r


# -----------------------------
# SUBS (FIXED OVERPOWERING ISSUE)
# -----------------------------
def sub_rating(row):
    mp = max(get(row, "MP"), 1)
    scale = min(1.6, 90 / mp)  # HARD CAP prevents 20–30 min chaos

    r = 6

    r += 1.0 * get(row, "G") * scale
    r += 0.5 * get(row, "A") * scale
    r += 0.2 * get(row, "SOnT") * scale

    r += 0.05 * get(row, "Tk") * scale
    r += 0.05 * get(row, "INT") * scale

    r -= 0.10 * get(row, "YC")
    r -= 0.50 * get(row, "RC")

    # clamp FINAL OUTPUT (critical fix)
    r = max(0, min(10, r))

    return round(r, 1)
