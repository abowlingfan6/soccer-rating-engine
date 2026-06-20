def defender_rating(row, f):
    rating = 6

    rating += 1.10 * f("Tk")
    rating += 0.20 * f("AP")
    rating += 0.10 * f("P")
    rating += 0.05 * f("C")

    rating -= 1.50 * f("YC")
    rating -= 3.00 * f("RC")
    rating -= 0.70 * f("FC")
    rating -= 0.25 * f("O")

    rating += 0.08 * f("SCA")

    return rating


def midfielder_rating(row, f):
    rating = 6

    rating += 0.45 * f("AP")
    rating += 0.35 * f("P")
    rating += 0.35 * f("Tk")
    rating += 0.25 * f("SCA")

    rating -= 1.30 * f("YC")
    rating -= 2.60 * f("RC")
    rating -= 0.60 * f("FC")

    return rating


def forward_rating(row, f):
    rating = 6

    rating += 1.10 * f("G")
    rating += 0.45 * f("xG")
    rating += 0.40 * f("S")
    rating += 0.40 * f("SOG")

    rating += 0.30 * f("xA")
    rating += 0.20 * f("A")
    rating += 0.20 * f("SCA")

    rating -= 0.50 * f("chance_missed")
    rating -= 0.10 * f("dribb_fail")

    rating -= 1.40 * f("YC")
    rating -= 2.80 * f("RC")

    return rating


def gk_rating(row, f):
    rating = 6

    rating += 0.35 * f("SAV")
    rating -= 0.25 * f("SOG")
    rating -= 0.15 * f("S")

    rating += 0.08 * f("AP")

    return rating
