import numpy as np
from src.config import MAX_RATING, MINUTES_BASE

def normalize(value, minutes):
    if minutes == 0:
        return 0
    return value * (MINUTES_BASE / minutes)


def clamp(value):
    return max(0, min(MAX_RATING, value))


# -------------------------
# DEFENDER
# -------------------------
def defender_rating(row):
    mp = row["MP"]

    rating = 6

    rating += 1.25 * normalize(row["Tk"], mp)
    rating += 0.5 * normalize(row["INT"], mp)
    rating += 0.4 * normalize(row["GC"] - 0.5, mp)
    rating += 0.5 * normalize(row["PW"], mp)

    rating += 0.1 * normalize(row["C"], mp)
    rating += 0.075 * normalize(row["P"], mp)

    rating += 0.5 * normalize(row["FW"], mp)

    rating -= 0.2 * normalize(row["YC"], mp)
    rating -= 1.0 * normalize(row["RC"], mp)

    rating -= 0.8 * normalize(row["SAV"], mp)

    return clamp(rating)


# -------------------------
# MIDFIELDER
# -------------------------
def midfielder_rating(row):
    mp = row["MP"]

    rating = 6

    rating += 1.25 * normalize(row["G"], mp)
    rating += 0.5 * normalize(row["A"], mp)
    rating += 0.4 * normalize(row["P"], mp)

    rating += 0.4 * normalize(row["Tk"], mp)
    rating += 0.4 * normalize(row["INT"], mp)

    rating += 0.2 * normalize(row["FW"], mp)
    rating += 0.075 * normalize(row["FC"], mp)

    rating += 0.5 * normalize(row["C"], mp)

    rating -= 0.2 * normalize(row["YC"], mp)
    rating -= 1.0 * normalize(row["RC"], mp)

    return clamp(rating)


# -------------------------
# FORWARD
# -------------------------
def forward_rating(row):
    mp = row["MP"]

    rating = 6

    rating += 1.25 * normalize(row["G"], mp)
    rating += 0.5 * normalize(row["A"], mp)

    rating += 0.4 * normalize(row["SOnT"], mp)
    rating += 0.2 * normalize(row["BS"], mp)

    rating += 0.5 * normalize(row["FW"], mp)

    rating -= 0.3 * normalize(row["FC"], mp)
    rating -= 0.2 * normalize(row["O"], mp)

    rating -= 1.0 * normalize(row["RC"], mp)

    return clamp(rating)
