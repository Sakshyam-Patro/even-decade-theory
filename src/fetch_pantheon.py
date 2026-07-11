"""Fetch MIT Pantheon 2.0 person dataset (2020 update) and cache to data/raw/."""
import bz2
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
BASE = "https://storage.googleapis.com/pantheon-public-data"
# 2020 = pre-registered primary; 2025 = replication (see DECISIONS.md D4)
FILES = ["person_2020_update.csv", "person_2025_update.csv"]


def fetch(name: str) -> None:
    csv_path, bz2_path = RAW / name, RAW / (name + ".bz2")
    if csv_path.exists():
        print(f"cached: {csv_path}")
        return
    if not bz2_path.exists():
        url = f"{BASE}/{name}.bz2"
        print(f"downloading {url}")
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        bz2_path.write_bytes(r.content)
    csv_path.write_bytes(bz2.decompress(bz2_path.read_bytes()))
    print(f"wrote {csv_path} ({csv_path.stat().st_size/1e6:.1f} MB)")


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        fetch(name)


if __name__ == "__main__":
    main()
