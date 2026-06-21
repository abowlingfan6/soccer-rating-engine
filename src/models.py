import numpy as np

# ---------- SAFE GET ----------
def get(row, col):
    val = row[col] if col in row else 0
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0
    return val


# ---------- BASE MODEL ----------
def base_outfield_rating(row):
    rating = 6

    # attacking output
    rating += 1.1 * get(row, "G")
    rating += 0.5 * get(row, "A")
    rating += 0.3 * get(row, "SOnT")
    rating += 0.15 * get(row, "BS")

    # passing / involvement
    rating += 0.04 * get(row, "P")
    rating += 0.08 * get(row, "C")
    rating += 0.06 * get(row, "Tk")
    rating += 0.06 * get(row, "INT")

    # duels / work rate
    rating += 0.15 * get(row, "FW")
    rating += 0.15 * get(row, "PW")

    # negatives
    rating -= 0.1 * get(row, "FC")
    rating -= 0.15 * get(row, "YC")
    rating -= 0.6 * get(row, "RC")
    rating -= 0.25 * get(row, "O")

    return rating


# ---------- POSITION MODELS ----------
def defender_rating(row):
    rating = base_outfield_rating(row)

    # defenders need defensive contribution emphasis
    rating += 0.2 * get(row, "Tk")
    rating += 0.2 * get(row, "INT")
    rating -= 0.2 * get(row, "SOnT")

    return rating


def midfielder_rating(row):
    rating = base_outfield_rating(row)

    # prevents passive 10/10 midfielders
    if get(row, "G") == 0 and get(row, "A") == 0:
        rating -= 0.7

    return rating


def forward_rating(row):
    rating = base_outfield_rating(row)

    # forwards must show threat
    if get(row, "G") == 0 and get(row, "SOnT") < 2:
        rating -= 0.8

    return rating


# ---------- SUB MODEL ----------
def sub_rating(row):
    minutes = max(get(row, "MP"), 1)
    scale = min(2.5, 90 / minutes)  # HARD CAP to stop inflation

    rating = 6

    rating += 1.2 * get(row, "G") * scale
    rating += 0.6 * get(row, "A") * scale
    rating += 0.25 * get(row, "SOnT") * scale

    rating += 0.08 * get(row, "Tk") * scale
    rating += 0.08 * get(row, "INT") * scale
    rating += 0.04 * get(row, "P") * scale
    rating += 0.06 * get(row, "C") * scale

    # discipline
    rating -= 0.15 * get(row, "YC")
    rating -= 0.6 * get(row, "RC")

    # final clamp
    rating = min(10, max(0, rating))

    return round(rating, 1)
