"""Reproduce the entire Even-Decade Theory analysis: raw download -> figures.

Usage:  .venv/bin/python run.py
Each fetch step caches to data/raw/ and is skipped when the cache exists, so
re-runs are offline and deterministic (seed 42 for permutation/bootstrap draws).
"""
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"
STEPS = [
    "fetch_pantheon.py",
    "fetch_occupations.py",
    "fetch_wikidata.py",
    "fetch_nobel.py",
    "fetch_baseline.py",
    "clean.py",
    "analysis.py",
    "apex.py",
    "figures.py",
    "fig_apex.py",
]


def main() -> None:
    for step in STEPS:
        print(f"\n=== {step} ===")
        subprocess.run([sys.executable, str(SRC / step)], check=True)
    print("\nDone. Results: output/results.json, figures: figures/")


if __name__ == "__main__":
    main()
