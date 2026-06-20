# src/models.py

def clamp_rating(x):
    return round(max(0, min(10, x)), 1)


# -----------------------
# DEFENDERS
# -----------------------
def defender_rating(s):
    rating = 6 + (
        (1.25 * s.get("G", 0)) +
        (0.5 * s.get("A", 0)) +
        (0.15 * s.get("C", 0)) +
        (0.4 * s.get("Tk", 0)) +
        (0.4 * s.get("INT", 0)) +
        (0.2 * s.get("FW", 0)) +
        (0.075 * s.get("FC", 0)) +
        (0.05 * s.get("O", 0)) -
        (0.05 * s.get("YC", 0)) -
        (1.0 * s.get("RC", 0)) +
        (0.2 * s.get("PW", 0)) -
        (0.3 * s.get("GC", 0))
    )

    return clamp_rating(rating)


# -----------------------
# MIDFIELDERS
# -----------------------
def midfielder_rating(s):
    rating = 6 + (
        (1.25 * s.get("G", 0)) +
        (0.5 * s.get("A", 0)) +
        (0.1 * s.get("P", 0)) +
        (0.15 * s.get("C", 0)) +
        (0.4 * s.get("Tk", 0)) +
        (0.4 * s.get("INT", 0)) +
        (0.2 * s.get("FW", 0)) -
        (0.05 * s.get("YC", 0)) -
        (1.0 * s.get("RC", 0)) +
        (0.075 * s.get("recoveries", 0))
    )

    return clamp_rating(rating)


# -----------------------
# FORWARDS
# -----------------------
def forward_rating(s):
    rating = 6 + (
        (1.25 * s.get("G", 0)) +
        (0.5 * s.get("A", 0)) +
        (0.5 * s.get("SOnT", 0)) +
        (0.4 * s.get("SOffT", 0)) +
        (0.4 * s.get("BS", 0)) -
        (0.2 * s.get("O", 0)) -
        (0.05 * s.get("FC", 0))
    )

    return clamp_rating(rating)
