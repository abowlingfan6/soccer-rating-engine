import sys
import os
import pandas as pd
import numpy as np


# =========================================================
# SAFE LOAD
# =========================================================
def safe(df, col):
    if col in df.columns:
        return pd.to_numeric(df[col], errors="coerce").fillna(0)
    return 0


# =========================================================
# PER 90
# =========================================================
def per90(value, mp):
    if mp <= 0:
        return 0
    return (value / mp) * 90


# =========================================================
# ROLE CLASSIFIER
# =========================================================
def get_role(pos):
    pos = str(pos).upper()

    if pos == "GK":
        return "GK"
    elif pos == "DF":
        return "DEF"
    elif pos == "MF":
        return "MID"
    elif pos == "FW":
        return "FWD"
    return "MID"


# =========================================================
# CORE RATING MODEL
# =========================================================
def calculate_rating(row):

    mp = float(row.get("MP", 90))
    if mp <= 0:
        mp = 90

    role = get_role(row.get("Pos.", row.get("Pos", "MID")))

    # ---------------- PER 90 STATS ----------------
    g = per90(safe(row, "G"), mp)
    a = per90(safe(row, "A"), mp)
    sonT = per90(safe(row, "SOnT"), mp)
    soffT = per90(safe(row, "SOffT"), mp)
    bs = per90(safe(row, "BS"), mp)

    passes = per90(safe(row, "P"), mp)
    crosses = per90(safe(row, "C"), mp)

    tackles = per90(safe(row, "Tk"), mp)
    intercept = per90(safe(row, "INT"), mp)
    forward_won = per90(safe(row, "FW"), mp)
    possession_won = per90(safe(row, "PW"), mp)

    fouls_committed = per90(safe(row, "FC"), mp)
    offsides = per90(safe(row, "O"), mp)

    yc = safe(row, "YC")
    rc = safe(row, "RC")

    gc = per90(safe(row, "GC"), mp)

    sav = per90(safe(row, "SAV"), mp)
    psav = per90(safe(row, "PSAV"), mp)

    # =====================================================
    # BASE IMPACT SCORE
    # =====================================================
    impact = 0

    # ATTACK
    impact += 1.4 * g
    impact += 0.8 * a
    impact += 0.4 * sonT
    impact += 0.2 * bs
    impact -= 0.25 * soffT

    # PROGRESSION
    impact += 0.2 * passes
    impact += 0.15 * crosses

    # DEFENSE
    impact += 0.3 * tackles
    impact += 0.25 * intercept
    impact += 0.2 * possession_won
    impact += 0.15 * forward_won

    # NEGATIVE EVENTS
    impact -= 0.25 * fouls_committed
    impact -= 0.15 * offsides

    # DISCIPLINE
    impact -= 1.2 * yc
    impact -= 3.5 * rc

    # =====================================================
    # ROLE SCALING
    # =====================================================
    if role == "GK":
        impact += 1.2 * sav
        impact += 1.0 * psav
        impact -= 0.8 * gc

    elif role == "DEF":
        impact *= 0.95

    elif role == "MID":
        impact *= 1.0

    elif role == "FWD":
        impact *= 1.1

    # =====================================================
    # BASE RATING
    # =====================================================
    rating = 6 + impact

    # =====================================================
    # SOFASCORE DISTRIBUTION CLAMP
    # =====================================================
    rating = 6 + np.tanh((rating - 6) / 2.0) * 2.3

    # FINAL LIMITS
    rating = max(3.0, min(9.8, rating))

    return round(rating, 2)


# =========================================================
# RUN MATCH
# =========================================================
def run_match(match_name):

    stats_file = f"data/{match_name}_stats.csv"
    events_file = f"data/{match_name}_events.csv"

    stats = pd.read_csv(stats_file) if os.path.exists(stats_file) else pd.DataFrame()
    events = pd.read_csv(events_file) if os.path.exists(events_file) else pd.DataFrame()

    if stats.empty and events.empty:
        print("No data found")
        return

    if stats.empty:
        df = events.copy()
    elif events.empty:
        df = stats.copy()
    else:
        df = pd.merge(stats, events, on="player", how="outer")

    df = df.fillna(0)

    # ensure MP exists
    if "MP" not in df.columns:
        df["MP"] = 90

    df["rating"] = df.apply(calculate_rating, axis=1)

    df = df.sort_values("rating", ascending=False)

    os.makedirs("data", exist_ok=True)
    df.to_csv(f"data/{match_name}_ratings.csv", index=False)

    print("\nTOP PLAYERS")
    print(df[["player", "Pos.", "rating"]].head(20))


# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "match"
    run_match(match_name)
