"""Fetch famous humans from Wikidata by sitelink count, chunked by birth decade.

Sitelink floor of 60 Wikipedia editions targets roughly 15k-25k people born
1800-2000 (per PREREGISTRATION.md section 2). Queries are chunked into 10-year
birth windows to stay under the SPARQL endpoint's 60s timeout.
"""
import json
import time
from pathlib import Path

import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
OUT = RAW / "wikidata_sitelinks.json"
ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "EvenDecadeTheory/1.0 (research; sakshyampatro1103@gmail.com)"}
SITELINK_FLOOR = 60

QUERY = """
SELECT ?person ?personLabel ?birth ?sitelinks WHERE {{
  ?person wdt:P31 wd:Q5 ;
          wdt:P569 ?birth ;
          wikibase:sitelinks ?sitelinks .
  FILTER(?sitelinks >= {floor})
  FILTER(?birth >= "{y0}-01-01T00:00:00Z"^^xsd:dateTime &&
         ?birth <  "{y1}-01-01T00:00:00Z"^^xsd:dateTime)
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
"""


def fetch_chunk(y0: int, y1: int, retries: int = 3) -> list:
    q = QUERY.format(floor=SITELINK_FLOOR, y0=y0, y1=y1)
    for attempt in range(retries):
        try:
            r = requests.get(ENDPOINT, params={"query": q, "format": "json"},
                             headers=HEADERS, timeout=120)
            r.raise_for_status()
            return r.json()["results"]["bindings"]
        except Exception as e:  # noqa: BLE001 - retry any transport/parse failure
            if attempt == retries - 1:
                raise
            print(f"  retry {y0}-{y1} after error: {e}")
            time.sleep(10 * (attempt + 1))
    return []


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"cached: {OUT}")
        return
    rows = []
    for y0 in range(1700, 2000, 10):
        chunk = fetch_chunk(y0, y0 + 10)
        for b in chunk:
            rows.append({
                "qid": b["person"]["value"].rsplit("/", 1)[-1],
                "name": b.get("personLabel", {}).get("value", ""),
                "birth": b["birth"]["value"],
                "sitelinks": int(b["sitelinks"]["value"]),
            })
        print(f"  {y0}-{y0+9}: {len(chunk)} rows (total {len(rows)})")
        time.sleep(1)
    OUT.write_text(json.dumps(rows))
    print(f"wrote {OUT}: {len(rows)} rows")


if __name__ == "__main__":
    main()
