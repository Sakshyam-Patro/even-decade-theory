"""Fetch demographic baseline: world births (OWID/UN, 1950+) and world
population (OWID/HYDE+UN, 1700+) for the pre-1950 births approximation."""
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
SOURCES = {
    "owid_births.csv":
        "https://ourworldindata.org/grapher/number-of-births-per-year.csv?v=1&csvType=full&useColumnShortNames=true",
    "owid_population.csv":
        "https://ourworldindata.org/grapher/population.csv?v=1&csvType=full&useColumnShortNames=true",
}
HEADERS = {"User-Agent": "EvenDecadeTheory/1.0 (research)"}


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for fname, url in SOURCES.items():
        out = RAW / fname
        if out.exists():
            print(f"cached: {out}")
            continue
        r = requests.get(url, headers=HEADERS, timeout=120)
        r.raise_for_status()
        out.write_bytes(r.content)
        print(f"wrote {out} ({out.stat().st_size/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
