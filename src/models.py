import numpy as np

# ---------- SAFE COLUMN ACCESS ----------
def get(row, col):
    return row[col] if col in row and not np.isnan(row[col]) else 0


# ---------- CORE ENGINE ----------
def base_outfield_rating(row):
    rating = 6

    # attacking output
    rating += 1.25 * get(row, "G")
    rating += 0.5 * get(row, "A")
    rating += 0.4 * get(row, "SOnT")
    rating += 0.2 * get(row, "BS")

    # passing / involvement
    rating += 0.05 * get(row, "P")
    rating += 0.1 * get(row, "C")
    rating += 0.075 * get(row, "Tk")
    rating += 0.075 * get(row, "INT")

    # duels / work rate proxies
    rating += 0.2 * get(row, "FW")
    rating += 0.2 * get(row, "PW")

    # negatives
    rating -= 0.1 * get(row, "FC")
    rating -= 0.2 * get(row, "YC")
    rating -= 0.8 * get(row, "RC")
    rating -= 0.3 * get(row, "O")

    return rating


# ---------- POSITION MODELS ----------
def defender_rating(row):
    return base_outfield_rating(row)


def midfielder_rating(row):
    return base_outfield_rating(row)


def forward_rating(row):
    return base_outfield_rating(row)


# ---------- SUB MODEL (NEW + FIXED) ----------
def sub_rating(row):
    minutes = max(get(row, "MP"), 1)
    scale = 90 / minutes  # per 90 adjustment

    rating = 6

    # impact weighted heavily per minute
    rating += 1.5 * get(row, "G") * scale
    rating += 0.8 * get(row, "A") * scale
    rating += 0.4 * get(row, "SOnT") * scale

    rating += 0.1 * get(row, "Tk") * scale
    rating += 0.1 * get(row, "INT") * scale
    rating += 0.05 * get(row, "P") * scale
    rating += 0.1 * get(row, "C") * scale

    # discipline penalties (not scaled)
    rating -= 0.2 * get(row, "YC")
    rating -= 0.8 * get(row, "RC")

    return rating
