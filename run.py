import sys
from rating.engine import run_match

if __name__ == "__main__":
    match_name = sys.argv[1] if len(sys.argv) > 1 else "mexico_sa"
    run_match(match_name)
