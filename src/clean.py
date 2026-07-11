"""Clean raw datasets into analysis-ready parquet files in data/processed/.

Eligibility rules per PREREGISTRATION.md section 2: integer birth year required,
main window 1700-1989, dedupe on wd_id / (name, birthyear).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"


def add_parity(df: pd.DataFrame) -> pd.DataFrame:
    """Group A = tens digit of birth year is even (1963 -> 6 -> even -> A)."""
    tens = (df["birthyear"] // 10) % 10
    df["group_a"] = (tens % 2 == 0)
    df["decade"] = (df["birthyear"] // 10) * 10
    return df


def clean_pantheon(csv_name: str, out_name: str) -> None:
    df = pd.read_csv(RAW / csv_name, low_memory=False)
    occ = pd.DataFrame(json.loads((RAW / "pantheon_occupations.json").read_text()))
    df = df.merge(occ, on="occupation", how="left")
    df["birthyear"] = pd.to_numeric(df["birthyear"], errors="coerce")
    df = df.dropna(subset=["birthyear", "hpi"])
    df["birthyear"] = df["birthyear"].astype(int)
    df = df[df.get("is_group", 0) != 1.0]  # people, not bands/groups
    df = df.sort_values("hpi", ascending=False)
    df = df.drop_duplicates(subset=["wd_id"]).drop_duplicates(subset=["name", "birthyear"])
    df = add_parity(df)
    keep = ["name", "wd_id", "birthyear", "decade", "group_a", "hpi",
            "occupation", "industry", "domain", "gender", "bplace_country"]
    df[keep].to_parquet(PROC / out_name, index=False)
    n_elig = ((df.birthyear >= 1700) & (df.birthyear <= 1989)).sum()
    print(f"{out_name}: {len(df)} rows, {n_elig} in 1700-1989 window")


def clean_wikidata() -> None:
    rows = json.loads((RAW / "wikidata_sitelinks.json").read_text())
    df = pd.DataFrame(rows)
    df["birthyear"] = pd.to_numeric(df["birth"].str[:4], errors="coerce")
    df = df.dropna(subset=["birthyear"])
    df["birthyear"] = df["birthyear"].astype(int)
    df = df.sort_values("sitelinks", ascending=False).drop_duplicates(subset=["qid"])
    df = add_parity(df)
    df[["qid", "name", "birthyear", "decade", "group_a", "sitelinks"]].to_parquet(
        PROC / "wikidata.parquet", index=False)
    print(f"wikidata.parquet: {len(df)} rows")


def clean_nobel() -> None:
    laureates = json.loads((RAW / "nobel_v1.json").read_text())["laureates"]
    rows = []
    for p in laureates:
        birth = p.get("born", "") or ""
        if birth[:4] in ("", "0000") or p.get("gender") == "org":
            continue
        for prize in p.get("prizes", []):
            rows.append({
                "name": f"{p.get('firstname', '')} {p.get('surname') or ''}".strip(),
                "birthyear": int(birth[:4]),
                "category": prize.get("category", ""),
            })
    df = pd.DataFrame(rows).drop_duplicates(subset=["name", "birthyear", "category"])
    df = add_parity(df)
    df.to_parquet(PROC / "nobel.parquet", index=False)
    print(f"nobel.parquet: {len(df)} laureate-prizes")


def clean_baseline() -> None:
    """Births per year, world. UN births 1950+; before 1950, approximate births as
    world population x a linearly interpolated crude birth rate anchor (parity
    comparisons only need relative decade-to-decade levels, and CBR moves slowly)."""
    births = pd.read_csv(RAW / "owid_births.csv")
    births.columns = [c.lower() for c in births.columns]
    bcol = [c for c in births.columns if c.startswith("births")][0]
    wb = births[births["entity"] == "World"][["year", bcol]].rename(columns={bcol: "births"})
    wb = wb.dropna(subset=["births"])

    pop = pd.read_csv(RAW / "owid_population.csv")
    pop.columns = [c.lower() for c in pop.columns]
    pcol = [c for c in pop.columns if "population" in c][0]
    wp = pop[pop["entity"] == "World"][["year", pcol]].rename(columns={pcol: "population"})
    wp = wp[(wp.year >= 1600) & (wp.year <= 2000)]
    # OWID/HYDE population is sparse pre-1800 (decadal/50y points): interpolate to yearly
    wp = wp.set_index("year").reindex(range(1600, 2001)).interpolate(method="linear").reset_index()

    # Crude birth rate: ~40/1000 (pre-industrial, 1600-1900) declining to the
    # UN-implied world CBR by 1950. Used ONLY to scale population into births pre-1950.
    anchor_1950 = wb.loc[wb.year == 1950, "births"].iloc[0] / \
        wp.loc[wp.year == 1950, "population"].iloc[0] * 1000
    years = np.arange(1600, 1950)
    cbr = np.where(years <= 1900, 40.0, 40.0 + (anchor_1950 - 40.0) * (years - 1900) / 50)
    pre = pd.DataFrame({"year": years})
    pre = pre.merge(wp, on="year")
    pre["births"] = pre["population"] * cbr / 1000
    base = pd.concat([pre[["year", "births"]], wb[wb.year >= 1950]], ignore_index=True)
    base = base.rename(columns={"year": "birthyear"}).sort_values("birthyear")
    base.to_parquet(PROC / "births_baseline.parquet", index=False)
    print(f"births_baseline.parquet: {base.birthyear.min()}-{base.birthyear.max()}")


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    clean_pantheon("person_2020_update.csv", "pantheon_2020.parquet")
    if (RAW / "person_2025_update.csv").exists():
        clean_pantheon("person_2025_update.csv", "pantheon_2025.parquet")
    if (RAW / "wikidata_sitelinks.json").exists():
        clean_wikidata()
    if (RAW / "nobel_v1.json").exists():
        clean_nobel()
    clean_baseline()


if __name__ == "__main__":
    main()
