# rating/formulas.py

def defender_rating(row, f):
    rating = 6

    rating += 1.10 * f("Tk")
    rating += 0.25 * f("FW")

    rating += 0.20 * f("AP")
    rating += 0.10 * f("P")
    rating += 0.05 * f("C")

    rating -= 0.70 * f("FC")
    rating -= 1.50 * f("YC")
    rating -= 3.00 * f("RC")

    rating -= 0.25 * f("O")

    rating += 0.08 * f("SCA")

    rating += 0.04 * f("G")
    rating += 0.03 * f("A")
    rating += 0.01 * f("xG")

    return rating


def midfielder_rating(row, f):
    rating = 6

    rating += 0.45 * f("AP")
    rating += 0.35 * f("P")

    rating += 0.35 * f("Tk")
    rating += 0.20 * f("FW")

    rating += 0.25 * f("SCA")

    rating += 0.10 * f("C")
    rating += 0.05 * f("xG")

    rating += 0.03 * f("G")
    rating += 0.02 * f("A")

    rating -= 1.30 * f("YC")
    rating -= 2.60 * f("RC")
    rating -= 0.60 * f("FC")
    rating -= 0.20 * f("O")

    return rating


def forward_rating(row, f):
    rating = 6

    rating += 1.10 * f("G")
    rating += 0.45 * f("xG")
    rating += 0.35 * f("S")
    rating += 0.40 * f("SOG")

    rating += 0.30 * f("xA")
    rating += 0.20 * f("A")
    rating += 0.20 * f("SCA")

    rating += 0.10 * f("C")
    rating += 0.20 * f("pens_won")
    rating += 0.10 * f("fouled")

    rating -= 0.25 * f("chance_missed")
    rating -= 0.50 * f("pen_missed")
    rating -= 0.15 * f("dispossessed")
    rating -= 0.10 * f("dribb_fail")

    rating -= 1.40 * f("YC")
    rating -= 2.80 * f("RC")
    rating -= 0.70 * f("FC")

  def gk_rating(row, f):

    rating = 6

    # ================= SHOT STOPPING (MOST IMPORTANT) =================
    rating += 0.35 * f("SAV")

    # shots faced pressure (if available)
    rating -= 0.15 * f("S")
    rating -= 0.25 * f("SOG")

    # shot quality faced (rough proxy)
    rating -= 0.10 * f("SIB")
    rating -= 0.08 * f("SOB")
    rating -= 0.05 * f("HS")

    # ================= DISTRIBUTION (SMALL BUT REAL) =================
    rating += 0.08 * f("AP")
    rating += 0.03 * f("P")

    # ================= DISCIPLINE =================
    rating -= 1.00 * f("RC")
    rating -= 0.40 * f("YC")

    # ================= BASIC FLOOR CONTROL =================
    rating += 0.5  # baseline composure bonus

    return rating

    return rating
