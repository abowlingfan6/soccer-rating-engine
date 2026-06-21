import numpy as np


def get(row, col):
    val = row[col] if col in row else 0
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0.0
    return float(val)


def clamp(x, low=0, high=10):
    return max(low, min(high, x))


def normalized(row, col):
    return get(row, f"{col}_norm")


def defender_rating(row):
    rating = 6.0

    rating += 0.8 * normalized(row, "Tk")
    rating += 0.8 * normalized(row, "INT")
    rating += 0.4 * normalized(row, "P")
    rating += 0.3 * normalized(row, "C")
    rating += 0.3 * normalized(row, "FW")
    rating += 0.3 * normalized(row, "PW")
    rating += 0.4 * get(row, "A")
    rating += 0.2 * get(row, "SOnT")

    rating -= 0.3 * normalized(row, "FC")
    rating -= 0.3 * get(row, "YC")
    rating -= 1.0 * get(row, "RC")
    rating -= 0.2 * get(row, "O")

    return clamp(rating)


def midfielder_rating(row):
    rating = 6.0

    rating += 0.7 * normalized(row, "P")
    rating += 0.7 * normalized(row, "C")
    rating += 0.5 * normalized(row, "Tk")
    rating += 0.5 * normalized(row, "INT")
    rating += 0.3 * normalized(row, "FW")

    rating += 0.8 * get(row, "A")
    rating += 1.2 * get(row,"G")
    rating += 0.4 * get(row, "SOnT")
    rating += 0.1 * get (row, "SOffT")
    rating += 0.3 * get(row, "BS")

    rating -= 0.3 * normalized(row, "FC")
    rating -= 0.3 * get(row, "YC")
    rating -= 1.0 * get(row, "RC")
    rating -= 0.2 * get(row, "O")

    if get(row, "G") == 0 and get(row, "A") == 0:
        rating -= 0.2

    return clamp(rating)


def forward_rating(row):
    rating = 6.0

    rating += 1.2 * get(row, "G")
    rating += 0.7 * get(row, "A")
    rating += 0.7 * normalized(row, "SOnT")
    rating += 0.3 * noramlized(row, "SOffT")
    rating += 0.4 * normalized(row, "BS")
    rating += 0.3 * normalized(row, "FW")
    rating += 0.2 * normalized(row, "P")

    rating -= 0.3 * normalized(row, "FC")
    rating -= 0.3 * get(row, "O")
    rating -= 0.3 * get(row, "YC")
    rating -= 1.0 * get(row, "RC")

    if get(row, "G") == 0 and get(row, "SOnT") == 0:
        rating -= 0.3

    return clamp(rating)


def sub_rating(row):
    rating = 5.8

    rating += 0.9 * get(row, "G")
    rating += 0.5 * get(row, "A")
    rating += 0.5 * normalized(row, "SOnT")
    rating += 0.2 * normalized(row, "SOffT")
    rating += 0.3 * normalized(row, "Tk")
    rating += 0.3 * normalized(row, "INT")
    rating += 0.2 * normalized(row, "P")

    rating -= 0.2 * get(row, "YC")
    rating -= 0.8 * get(row, "RC")

    minutes = get(row, "MP")

    if minutes < 15:
        rating = min(rating, 8.0)
    elif minutes < 30:
        rating = min(rating, 8.5)
    elif minutes < 45:
        rating = min(rating, 9.2)

    return clamp(rating)
