"""Pre-registered statistical battery for the Even-Decade Theory.

Every test defined in PREREGISTRATION.md sections 3-6. Writes output/results.json.
Seed fixed at 42 for the permutation/bootstrap draws.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PROC, OUT = ROOT / "data" / "processed", ROOT / "output"
SEED = 42
WINDOW = (1700, 1989)
N_PERM = 10_000


# ---------------------------------------------------------------- helpers
def group_a(years: np.ndarray, offset: int = 0) -> np.ndarray:
    """Even-decade membership. offset shifts the decade boundary: offset 0 is
    the XX00 boundary (pre-registered split), offset d groups years with
    (year - d) mod 20 in [0, 10)."""
    return (years - offset) % 20 < 10


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple:
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return center - half, center + half


def binom_vs_null(k: int, n: int, p0: float) -> dict:
    lo, hi = wilson_ci(k, n)
    p_hat = k / n
    return {
        "k": int(k), "n": int(n), "share": p_hat, "null_share": p0,
        "diff": p_hat - p0,
        "ci95": [lo, hi],
        "odds_ratio": (p_hat / (1 - p_hat)) / (p0 / (1 - p0)),
        "p_one_sided": float(stats.binomtest(k, n, p0, alternative="greater").pvalue),
        "p_two_sided": float(stats.binomtest(k, n, p0, alternative="two-sided").pvalue),
    }


def eligible(df: pd.DataFrame, window=WINDOW) -> pd.DataFrame:
    return df[(df.birthyear >= window[0]) & (df.birthyear <= window[1])].copy()


# ---------------------------------------------------------------- test blocks
def primary_and_sensitivity(pool: pd.DataFrame, metric: str) -> dict:
    """Top-N vs internal baseline (full eligible pool share), N in {100,500,1000,5000}."""
    pool = pool.sort_values(metric, ascending=False)
    p0 = pool.group_a.mean()
    res = {"baseline_share": p0, "pool_n": len(pool), "by_n": {}}
    for n in (100, 500, 1000, 5000):
        if n > len(pool):
            continue
        top = pool.head(n)
        res["by_n"][n] = binom_vs_null(int(top.group_a.sum()), n, p0)
    return res


def demographic_null_share(base: pd.DataFrame, window=WINDOW) -> float:
    b = base[(base.birthyear >= window[0]) & (base.birthyear <= window[1])]
    return float(b.births[group_a(b.birthyear.values)].sum() / b.births.sum())


def offset_test(pool: pd.DataFrame, metric: str, top_n: int = 1000) -> dict:
    """Delta (top-N share minus pool share) of the 'A-like' group at all 10
    possible decade-boundary offsets. Theory predicts offset 0 is the max."""
    pool = pool.sort_values(metric, ascending=False)
    top = pool.head(top_n)
    deltas = []
    for d in range(10):
        a_top = group_a(top.birthyear.values, d).mean()
        a_pool = group_a(pool.birthyear.values, d).mean()
        deltas.append(float(a_top - a_pool))
    rank = int(1 + sum(deltas[d] > deltas[0] for d in range(1, 10)))  # 1 = most extreme
    return {"deltas": deltas, "offset0_delta": deltas[0], "offset0_rank": rank}


def permutation_test(pool: pd.DataFrame, metric: str, top_n: int = 1000) -> dict:
    """Null distribution of Group A count in a random draw of top_n from the pool
    (label permutation == hypergeometric draw, generated exactly)."""
    rng = np.random.default_rng(SEED)
    k_pool = int(pool.group_a.sum())
    null_counts = rng.hypergeometric(k_pool, len(pool) - k_pool, top_n, size=N_PERM)
    obs = int(pool.sort_values(metric, ascending=False).head(top_n).group_a.sum())
    return {
        "observed_k": obs, "top_n": top_n,
        "null_mean": float(null_counts.mean()), "null_sd": float(null_counts.std()),
        "p_perm_one_sided": float((null_counts >= obs).mean()),
        "z": float((obs - null_counts.mean()) / null_counts.std()),
        "null_counts_hist": np.bincount(null_counts, minlength=top_n + 1).tolist(),
    }


def glm_parity(pool: pd.DataFrame, metric: str, top_n: int = 1000,
               offset: int = 0, degree: int = 5) -> dict:
    """Binomial GLM: logit P(in top-N | birth year) = poly(year, degree) + beta*A.
    The polynomial absorbs smooth canonization/recency trends at every scale;
    beta isolates the alternating-decade signal. Hand-rolled IRLS (no statsmodels).
    """
    pool = pool.sort_values(metric, ascending=False)
    top_idx = np.zeros(len(pool), dtype=bool)
    top_idx[:top_n] = True
    agg = pd.DataFrame({"year": pool.birthyear.values, "top": top_idx})
    agg = agg.groupby("year").agg(n=("top", "size"), k=("top", "sum")).reset_index()

    ys = (agg.year - agg.year.mean()) / agg.year.std()
    X = np.column_stack([ys**p for p in range(degree + 1)] +
                        [group_a(agg.year.values, offset).astype(float)])
    n, k = agg.n.values.astype(float), agg.k.values.astype(float)

    beta = np.zeros(X.shape[1])
    for _ in range(60):
        eta = X @ beta
        mu = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
        w = np.clip(n * mu * (1 - mu), 1e-10, None)
        z_work = eta + (k - n * mu) / w
        XtW = X.T * w
        beta_new = np.linalg.solve(XtW @ X + 1e-8 * np.eye(X.shape[1]), XtW @ z_work)
        if np.max(np.abs(beta_new - beta)) < 1e-10:
            beta = beta_new
            break
        beta = beta_new
    eta = X @ beta
    mu = 1 / (1 + np.exp(-np.clip(eta, -30, 30)))
    w = np.clip(n * mu * (1 - mu), 1e-10, None)
    cov = np.linalg.inv((X.T * w) @ X + 1e-8 * np.eye(X.shape[1]))
    b, se = beta[-1], np.sqrt(cov[-1, -1])
    z = b / se
    return {
        "beta_parity": float(b), "se": float(se), "z": float(z),
        "odds_ratio": float(np.exp(b)),
        "or_ci95": [float(np.exp(b - 1.96 * se)), float(np.exp(b + 1.96 * se))],
        "p_one_sided": float(stats.norm.sf(z)),
        "p_two_sided": float(2 * stats.norm.sf(abs(z))),
        "degree": degree,
    }


def era_matched_permutation(pool: pd.DataFrame, metric: str, top_n: int = 1000,
                            offset: int = 0, align: int = 0) -> dict:
    """Trend-proof test (DECISIONS.md D7). Null top-Ns are drawn from the pool
    block-by-block, matching the observed top-N's count in each 20-year block
    aligned to the offset's decade boundary. Each block spans one A-like and one
    B-like decade, so any smooth birth-year trend cancels; only parity survives."""
    rng = np.random.default_rng(SEED + offset + 100 * align)
    pool = pool.sort_values(metric, ascending=False)
    top = pool.head(top_n)
    # align=0: blocks start on the A-like decade; align=1: on the B-like decade.
    # A within-block canonization gradient biases the two alignments in opposite
    # directions, so a genuine parity effect must survive BOTH.
    block = (pool.birthyear.values - offset - 10 * align) // 20
    a_pool = group_a(pool.birthyear.values, offset)
    top_block = (top.birthyear.values - offset - 10 * align) // 20
    obs = int(group_a(top.birthyear.values, offset).sum())

    null = np.zeros(N_PERM, dtype=int)
    for b in np.unique(top_block):
        n_b = int((top_block == b).sum())
        in_b = block == b
        K, N = int(a_pool[in_b].sum()), int(in_b.sum())
        if K == N:  # parity deterministic in truncated edge blocks (all A)
            null += n_b
            continue
        if K == 0:  # all B
            continue
        null += rng.hypergeometric(K, N - K, n_b, size=N_PERM)
    sd = null.std() if null.std() > 0 else 1.0
    return {
        "observed_k": obs, "top_n": top_n,
        "null_mean": float(null.mean()), "null_sd": float(null.std()),
        "z": float((obs - null.mean()) / sd),
        "p_one_sided": float((null >= obs).mean()),
        "p_two_sided": float(min(1.0, 2 * min((null >= obs).mean(), (null <= obs).mean()))),
        "null_counts_hist": np.bincount(null, minlength=top_n + 1).tolist(),
    }


def per_field(pool: pd.DataFrame, top_k: int = 500) -> dict:
    """Primary test within each Pantheon domain: domain top-500 by HPI vs the
    domain's own full eligible population share. BH-FDR across domains."""
    out = {}
    for dom, g in pool.groupby("domain"):
        if len(g) < 2 * top_k:  # need headroom between top and pool
            continue
        p0 = g.group_a.mean()
        top = g.sort_values("hpi", ascending=False).head(top_k)
        out[dom] = binom_vs_null(int(top.group_a.sum()), top_k, p0)
        out[dom]["glm"] = glm_parity(g, "hpi", top_n=top_k)
    pvals = [v["p_two_sided"] for v in out.values()]
    rejected = bh_reject(pvals, q=0.05)
    for (dom, v), rej in zip(out.items(), rejected):
        v["bh_significant_q05"] = bool(rej)
    return out


def bh_reject(pvals: list, q: float = 0.05) -> list:
    m = len(pvals)
    order = np.argsort(pvals)
    thresh = np.zeros(m, dtype=bool)
    max_i = -1
    for rank_i, idx in enumerate(order, start=1):
        if pvals[idx] <= q * rank_i / m:
            max_i = rank_i
    for rank_i, idx in enumerate(order, start=1):
        thresh[idx] = rank_i <= max_i
    return thresh.tolist()


def bayesian(pool: pd.DataFrame, metric: str, top_n: int = 1000) -> dict:
    """Beta(1,1)-binomial posterior for the top-N Group A share vs pool share."""
    p0 = pool.group_a.mean()
    k = int(pool.sort_values(metric, ascending=False).head(top_n).group_a.sum())
    a, b = 1 + k, 1 + top_n - k
    post = stats.beta(a, b)
    return {
        "posterior_alpha": a, "posterior_beta": b,
        "p_effect_positive": float(1 - post.cdf(p0)),
        "effect_mean": float(post.mean() - p0),
        "effect_ci95": [float(post.ppf(0.025) - p0), float(post.ppf(0.975) - p0)],
    }


def fame_weighted(pool: pd.DataFrame, metric: str) -> dict:
    """Weight every eligible person by fame intensity; bootstrap the weighted
    Group A share minus the unweighted pool share."""
    rng = np.random.default_rng(SEED)
    w = pool[metric].values.astype(float)
    w = w - w.min() + 1e-9  # ensure positive weights
    a = pool.group_a.values
    s_unw = a.mean()
    s_w = float((w * a).sum() / w.sum())
    n = len(pool)
    boots = np.empty(N_PERM)
    for i in range(N_PERM):
        idx = rng.integers(0, n, n)
        boots[i] = (w[idx] * a[idx]).sum() / w[idx].sum() - a[idx].mean()
    return {
        "weighted_share": s_w, "unweighted_share": float(s_unw),
        "diff": s_w - s_unw,
        "diff_ci95": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
    }


def temporal(pool: pd.DataFrame, metric: str, top_n: int = 1000) -> dict:
    """Primary comparison within birth half-centuries."""
    pool = pool.sort_values(metric, ascending=False)
    top = pool.head(top_n)
    out = {}
    for y0 in range(WINDOW[0], WINDOW[1], 50):
        y1 = min(y0 + 49, WINDOW[1])
        sub_pool = pool[(pool.birthyear >= y0) & (pool.birthyear <= y1)]
        sub_top = top[(top.birthyear >= y0) & (top.birthyear <= y1)]
        if len(sub_top) < 20:
            continue
        out[f"{y0}-{y1}"] = binom_vs_null(
            int(sub_top.group_a.sum()), len(sub_top), sub_pool.group_a.mean())
    return out


def battery(pool: pd.DataFrame, metric: str, label: str, base: pd.DataFrame) -> dict:
    res = {
        "label": label, "metric": metric,
        "internal": primary_and_sensitivity(pool, metric),
        "offset": offset_test(pool, metric),
        "offset_pool_vs_births": None,  # filled below
        "permutation": permutation_test(pool, metric),
        "era_matched": era_matched_permutation(pool, metric),
        "era_matched_flip": era_matched_permutation(pool, metric, align=1),
        "era_matched_offsets": [
            {k: v for k, v in era_matched_permutation(pool, metric, offset=d).items()
             if k != "null_counts_hist"} for d in range(10)],
        "glm": glm_parity(pool, metric),
        "glm_degrees": {deg: glm_parity(pool, metric, degree=deg) for deg in (3, 8)},
        "glm_offsets": [glm_parity(pool, metric, offset=d) for d in range(10)],
        "bayes": bayesian(pool, metric),
        "fame_weighted": fame_weighted(pool, metric),
        "temporal": temporal(pool, metric),
    }
    # demographic baseline: top-1000 and the WHOLE famous pool vs births share
    p_dem = demographic_null_share(base)
    top = pool.sort_values(metric, ascending=False).head(1000)
    res["demographic"] = {
        "births_share_A": p_dem,
        "top1000": binom_vs_null(int(top.group_a.sum()), len(top), p_dem),
        "whole_pool": binom_vs_null(int(pool.group_a.sum()), len(pool), p_dem),
    }
    # offset test for the whole pool against births baseline (documentation-level check)
    b = base[(base.birthyear >= WINDOW[0]) & (base.birthyear <= WINDOW[1])]
    deltas = []
    for d in range(10):
        a_pool = group_a(pool.birthyear.values, d).mean()
        a_births = float(b.births[group_a(b.birthyear.values, d)].sum() / b.births.sum())
        deltas.append(float(a_pool - a_births))
    res["offset_pool_vs_births"] = {"deltas": deltas,
                                    "rank": int(1 + sum(x > deltas[0] for x in deltas[1:]))}
    return res


def main() -> None:
    OUT.mkdir(exist_ok=True)
    base = pd.read_parquet(PROC / "births_baseline.parquet")
    results = {"window": WINDOW, "seed": SEED, "n_perm": N_PERM, "datasets": {}}

    p20 = eligible(pd.read_parquet(PROC / "pantheon_2020.parquet"))
    results["datasets"]["pantheon_2020"] = battery(p20, "hpi", "Pantheon 2.0 (2020, primary)", base)
    results["datasets"]["pantheon_2020"]["per_field"] = per_field(p20)

    p25_path = PROC / "pantheon_2025.parquet"
    if p25_path.exists():
        p25 = eligible(pd.read_parquet(p25_path))
        results["datasets"]["pantheon_2025"] = battery(p25, "hpi", "Pantheon (2025, replication)", base)
        results["datasets"]["pantheon_2025"]["per_field"] = per_field(p25)

    wd_path = PROC / "wikidata.parquet"
    if wd_path.exists():
        wd = eligible(pd.read_parquet(wd_path))
        results["datasets"]["wikidata"] = battery(wd, "sitelinks", "Wikidata sitelinks", base)

    nb_path = PROC / "nobel.parquet"
    if nb_path.exists():
        nb = eligible(pd.read_parquet(nb_path))
        k, n = int(nb.group_a.sum()), len(nb)
        # Nobel: whole-list test vs demographic baseline only (no fame ranking exists)
        results["datasets"]["nobel"] = {
            "label": "Nobel laureates (whole list)",
            "vs_births": binom_vs_null(k, n, demographic_null_share(base, (1800, 1989))),
            "by_category": {c: binom_vs_null(int(g.group_a.sum()), len(g),
                                             demographic_null_share(base, (1800, 1989)))
                            for c, g in nb.groupby("category") if len(g) >= 50},
        }

    # robustness windows on the primary dataset
    for w in [(1800, 1989), (1500, 1989)]:
        p = eligible(pd.read_parquet(PROC / "pantheon_2020.parquet"), w)
        pool_share = p.group_a.mean()
        top = p.sort_values("hpi", ascending=False).head(1000)
        results.setdefault("windows", {})[f"{w[0]}-{w[1]}"] = binom_vs_null(
            int(top.group_a.sum()), 1000, pool_share)

    (OUT / "results.json").write_text(json.dumps(results, indent=1))
    # console verdict summary
    r = results["datasets"]["pantheon_2020"]
    prim = r["internal"]["by_n"]["1000"] if "1000" in r["internal"]["by_n"] else r["internal"]["by_n"][1000]
    print(f"PRIMARY  top-1000 share A = {prim['share']:.4f} vs baseline {prim['null_share']:.4f}  "
          f"p(one-sided) = {prim['p_one_sided']:.4f}")
    print(f"OFFSET   delta at offset0 = {r['offset']['offset0_delta']:+.4f}, "
          f"rank {r['offset']['offset0_rank']}/10 (1 = most extreme, theory needs 1)")
    print(f"PERM     z = {r['permutation']['z']:+.2f}, p = {r['permutation']['p_perm_one_sided']:.4f}")
    em = r["era_matched"]
    print(f"ERA-MATCHED  z = {em['z']:+.2f}, p(one-sided) = {em['p_one_sided']:.4f}, "
          f"p(two-sided) = {em['p_two_sided']:.4f}")
    em_z = [o["z"] for o in r["era_matched_offsets"]]
    print(f"ERA-MATCHED OFFSETS z: {[round(z, 2) for z in em_z]} "
          f"(offset0 rank {1 + sum(z > em_z[0] for z in em_z[1:])}/10 by z)")
    emf = r["era_matched_flip"]
    print(f"ERA-MATCHED (flipped blocks) z = {emf['z']:+.2f}, p1s = {emf['p_one_sided']:.4f}")
    g = r["glm"]
    print(f"GLM      beta = {g['beta_parity']:+.4f} (OR {g['odds_ratio']:.3f}, "
          f"CI {g['or_ci95'][0]:.3f}-{g['or_ci95'][1]:.3f}), z = {g['z']:+.2f}, "
          f"p2s = {g['p_two_sided']:.4f}")
    gz = [o["z"] for o in r["glm_offsets"]]
    print(f"GLM OFFSETS z: {[round(z, 2) for z in gz]} "
          f"(offset0 rank {1 + sum(z > gz[0] for z in gz[1:])}/10)")
    for deg, gg in r["glm_degrees"].items():
        print(f"GLM deg={deg}: z = {gg['z']:+.2f}, p2s = {gg['p_two_sided']:.4f}")
    print(f"BAYES    P(effect>0) = {r['bayes']['p_effect_positive']:.4f}")


if __name__ == "__main__":
    main()
