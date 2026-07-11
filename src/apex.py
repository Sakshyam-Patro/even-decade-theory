"""The apex steelman (DECISIONS.md D10): test the theory where it actually lives —
the #1 (GOAT) and top-k of every field, not top-1000 populations.

Design choices all favor the theory getting detected if real:
- GOATs are selected objectively (highest HPI per Pantheon occupation).
- The null compares each GOAT only against their own field's top-10, so era,
  field size, and documentation effects cancel by construction.
- An escalation curve tests the user's exact claim: the effect should grow
  from top-10 to top-5 to top-3 to top-1.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
SEED = 42
N_SIM = 20_000
WINDOW = (1700, 1989)


def group_a(years) -> np.ndarray:
    return (np.asarray(years) // 10) % 2 == 0


def field_tops(pool: pd.DataFrame, min_n: int) -> dict:
    """occupation -> its top-min_n people by HPI (occupations with >= min_n people)."""
    tops = {}
    for occ, g in pool.groupby("occupation"):
        if len(g) >= min_n:
            tops[occ] = g.sort_values("hpi", ascending=False).head(min_n)
    return tops


def tier_test(pool: pd.DataFrame, k: int, null_pool: int, rng) -> dict:
    """Even-decade share of the union of per-field top-k, vs a null where each
    field contributes k people drawn uniformly from its own top-null_pool."""
    tops = field_tops(pool, null_pool)
    obs, n_total = 0, 0
    null = np.zeros(N_SIM, dtype=int)
    for occ, t in tops.items():
        a = group_a(t.birthyear.values)
        obs += int(a[:k].sum())
        n_total += k
        e, npool = int(a.sum()), len(a)
        null += rng.hypergeometric(e, npool - e, k, size=N_SIM) if 0 < e < npool \
            else (k if e == npool else 0)
    share, null_share = obs / n_total, null / n_total
    return {
        "k": k, "null_pool": null_pool, "n_fields": len(tops),
        "observed_even": obs, "n": n_total, "share": share,
        "null_mean_share": float(null_share.mean()),
        "null_sd_share": float(null_share.std()),
        "z": float((share - null_share.mean()) / null_share.std()),
        "p_one_sided": float((null >= obs).mean()),
        "null_ci95_share": [float(np.quantile(null_share, 0.025)),
                            float(np.quantile(null_share, 0.975))],
    }


def goat_list(pool: pd.DataFrame) -> pd.DataFrame:
    tops = field_tops(pool, 10)
    rows = [{"occupation": occ, "name": t.iloc[0]["name"],
             "birthyear": int(t.iloc[0].birthyear),
             "even_decade": bool(group_a([t.iloc[0].birthyear])[0])}
            for occ, t in tops.items()]
    return pd.DataFrame(rows).sort_values("occupation")


def rounding_artifact(df: pd.DataFrame) -> dict:
    """Estimated ancient birth years are rounded to 0/5 endings; a year ending in
    0 always sits in an even-parity decade, so ancient parity is contaminated."""
    out = {}
    bins = [(-800, 500), (500, 1200), (1200, 1500), (1500, 1700), (1700, 1989)]
    for y0, y1 in bins:
        g = df[(df.birthyear >= y0) & (df.birthyear < y1)]
        if len(g) < 30:
            continue
        ends0 = (g.birthyear % 10 == 0).mean()
        ends05 = (g.birthyear % 5 == 0).mean()
        out[f"{y0}..{y1}"] = {"n": len(g), "pct_ending_0": float(ends0),
                              "pct_ending_0_or_5": float(ends05),
                              "share_even_decade": float(group_a(g.birthyear.values).mean())}
    return out


def main() -> None:
    rng = np.random.default_rng(SEED)
    results = {}
    p20 = pd.read_parquet(PROC / "pantheon_2020.parquet")
    pool = p20[(p20.birthyear >= WINDOW[0]) & (p20.birthyear <= WINDOW[1])]

    # 1. escalation curve: k = 10 (of top-20), then 5/4/3/2/1 (of top-10)
    results["escalation"] = [tier_test(pool, 10, 20, rng)] + [
        tier_test(pool, k, 10, rng) for k in (5, 4, 3, 2, 1)]

    # 2. the GOAT list itself
    goats = goat_list(pool)
    goats.to_csv(OUT / "goat_list.csv", index=False)
    results["goats"] = {
        "n": len(goats), "even": int(goats.even_decade.sum()),
        "share": float(goats.even_decade.mean()),
    }

    # replication on 2025 data
    p25 = pd.read_parquet(PROC / "pantheon_2025.parquet")
    pool25 = p25[(p25.birthyear >= WINDOW[0]) & (p25.birthyear <= WINDOW[1])]
    results["escalation_2025"] = [tier_test(pool25, k, np_, rng) for k, np_ in
                                  [(10, 20), (5, 10), (4, 10), (3, 10), (2, 10), (1, 10)]]

    # 3. ancients / religious figures, with the rounding-artifact gate
    results["rounding_artifact"] = rounding_artifact(p20)
    rel = p20[p20.occupation.isin(["RELIGIOUS FIGURE", "PHILOSOPHER"])]
    rel_top = rel.sort_values("hpi", ascending=False).head(25)
    results["religious_philosophy_top25_alltime"] = [
        {"name": r["name"], "birthyear": int(r.birthyear), "occupation": r.occupation,
         "even_decade": bool(group_a([r.birthyear])[0]),
         "round_year": bool(r.birthyear % 5 == 0)}
        for _, r in rel_top.iterrows()]

    (OUT / "apex_results.json").write_text(json.dumps(results, indent=1))

    print(f"GOATs (1 per field, n={results['goats']['n']}): "
          f"{results['goats']['even']} even-decade = {results['goats']['share']:.1%}")
    print("\nEscalation curve (2020 primary): does the effect grow toward the top?")
    for t in results["escalation"]:
        print(f"  top-{t['k']:>2} of each field: {t['share']:.1%} even "
              f"(null {t['null_mean_share']:.1%}, z = {t['z']:+.2f}, "
              f"p(one-sided) = {t['p_one_sided']:.3f}, fields = {t['n_fields']})")
    print("\nEscalation (2025 replication):")
    for t in results["escalation_2025"]:
        print(f"  top-{t['k']:>2}: {t['share']:.1%} even (z = {t['z']:+.2f}, "
              f"p = {t['p_one_sided']:.3f})")
    print("\nRound-year artifact by era (pct of birth years ending in 0):")
    for era, v in results["rounding_artifact"].items():
        print(f"  {era:>12}: n={v['n']:>5}  ends-in-0 = {v['pct_ending_0']:.1%}  "
              f"even-decade share = {v['share_even_decade']:.1%}")


if __name__ == "__main__":
    main()
