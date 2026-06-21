import numpy as np

# =========================
# SAFE GET + HELPERS
# =========================

def get(row, col):
    val = row[col] if col in row else 0
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0
    return float(val)


def clamp(x):
    return max(0, min(10, x))


def scale_minutes(row):
    mp = max(get(row, "MP"), 1)
    return min(1.3, 90 / mp)


def log_stat(x):
    return np.log1p(max(x, 0))


# =========================
# MIDFIELDER MODEL
# =========================

def midfielder_rating(row):
    s = scale_minutes(row)

    rating = 6.0

    # ball control (diminishing returns)
    rating += 0.35 * log_stat(get(row, "P"))
    rating += 0.25 * log_stat(get(row, "C"))

    # creation output
    rating += 0.6 * get(row, "A")
    rating += 0.25 * get(row, "SOnT")

    # defensive work
    rating += 0.2 * get(row, "Tk")
    rating += 0.2 * get(row, "INT")

    # contribution
    rating += 0.1 * get(row, "FW")

    # mistakes
    rating -= 0.2 * get(row, "FC")
    rating -= 0.2 * get(row, "O")

    return clamp(rating * s)


# =========================
# DEFENDER MODEL
# =========================

def defender_rating(row):
    s = scale_minutes(row)

    rating = 6.0

    rating += 0.3 * get(row, "Tk")
    rating += 0.3 * get(row, "INT")
    rating += 0.2 * get(row, "PW")

    rating += 0.15 * log_stat(get(row, "P"))

    rating += 0.1 * get(row, "SOnT")

    rating -= 0.2 * get(row, "FC")
    rating -= 0.25 * get(row, "YC")
    rating -= 0.7 * get(row, "RC")

    return clamp(rating * s)


# =========================
# FORWARD MODEL
# =========================

def forward_rating(row):
    s = scale_minutes(row)

    rating = 6.0

    rating += 0.9 * get(row, "G")
    rating += 0.4 * get(row, "A")
    rating += 0.3 * get(row, "SOnT")

    rating += 0.2 * log_stat(get(row, "BS"))
    rating += 0.15 * log_stat(get(row, "P"))

    rating -= 0.2 * get(row, "O")
    rating -= 0.3 * get(row, "FC")

    # must show threat
    if get(row, "G") == 0 and get(row, "SOnT") < 2:
        rating -= 0.6

    return clamp(rating * s)


# =========================
# SUB MODEL (FIXED - NO MORE INFLATION)
# =========================

def sub_rating(row):
    s = min(1.2, scale_minutes(row))  # HARD CAP

    rating = 5.8

    rating += 0.8 * get(row, "G")
    rating += 0.4 * get(row, "A")
    rating += 0.25 * get(row, "SOnT")

    rating += 0.1 * get(row, "Tk")
    rating += 0.1 * get(row, "INT")

    rating += 0.05 * log_stat(get(row, "P"))

    rating -= 0.2 * get(row, "YC")
    rating -= 0.7 * get(row, "RC")

    return clamp(rating * s)

    return round(rating, 1)
