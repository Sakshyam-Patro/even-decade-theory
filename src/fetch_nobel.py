"""Fetch all Nobel laureates (official API, v1 bulk endpoint) to data/raw/.

The v2.1 paginated endpoint times out from some networks (DECISIONS.md D8);
v1 returns the full list in one response.
"""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = RAW / "nobel_v1.json"
API = "https://api.nobelprize.org/v1/laureate.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (research pipeline; even-decade-theory)"}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"cached: {OUT}")
        return
    r = requests.get(API, headers=HEADERS, timeout=120)
    r.raise_for_status()
    OUT.write_bytes(r.content)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
