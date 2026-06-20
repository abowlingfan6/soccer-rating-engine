import pandas as pd
import os

from rating.formulas import rating


# =========================================================
# RUN ALL FILES
# =========================================================
def run_all():

    files = [f for f in os.listdir("data") if f.endswith(".csv")]

    if not files:
        print("❌ No CSV files found in /data")
        return

    for file in files:

        path = os.path.join("data", file)
        print(f"\n=== Running {file} ===")

        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()

        if "player" not in df.columns:
            print(f"❌ Skipping {file}: missing player column")
            continue

        df["rating"] = df.apply(rating, axis=1)

        out = path.replace(".csv", "_ratings.csv")
        df.to_csv(out, index=False)

        print("✅ Saved:", out)

        print(df[["player", "Pos.", "rating"]].head(10))


# =========================================================
# ENTRY
# =========================================================
if __name__ == "__main__":
    run_all()

    print("\n🏆 TOP PLAYERS")
    print(df[["player", "Pos.", "rating"]].head(20))

    print("\n💾 Saved:", output_file)


# =========================================================
# CLI
# =========================================================
if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "match"
    run(match_name)
