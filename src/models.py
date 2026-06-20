def defender_rating(s):
    return 6 + s["goals"] * 0.5 - s["red_cards"]

def midfielder_rating(s):
    return 6 + s["assists"] * 0.6

def forward_rating(s):
    return 6 + s["goals"] * 1.2 + s["shots_on_target"] * 0.3
