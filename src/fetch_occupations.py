"""Fetch Pantheon occupation -> domain/industry mapping from api.pantheon.world."""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = RAW / "pantheon_occupations.json"
URL = "https://api.pantheon.world/occupation?select=occupation,industry,domain"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"cached: {OUT}")
        return
    r = requests.get(URL, timeout=60)
    r.raise_for_status()
    OUT.write_bytes(r.content)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
