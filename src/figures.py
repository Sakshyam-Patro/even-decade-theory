"""All figures for the Even-Decade Theory report. PNG + SVG to figures/."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROC, OUT, FIG = ROOT / "data" / "processed", ROOT / "output", ROOT / "figures"
WINDOW = (1700, 1989)

# reference palette (dataviz skill) — light mode
SURFACE = "#fcfcfb"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, BASELINE = "#e1e0d9", "#c3c2b7"
BLUE, RED, AQUA, YELLOW, VIOLET = "#2a78d6", "#e34948", "#1baf7a", "#eda100", "#4a3aa7"
EVEN_SHADE = "#2a78d6"  # used at low alpha for even-decade bands

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
    "axes.edgecolor": BASELINE, "axes.linewidth": 0.8,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.labelcolor": INK2, "text.color": INK,
    "axes.titlesize": 12, "axes.titleweight": "bold", "axes.titlecolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False,
})


def save(fig, name: str) -> None:
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"figures/{name}.png|svg")


def shade_even_decades(ax, y0, y1) -> None:
    for d in range(y0 - y0 % 10, y1 + 1, 10):
        if (d // 10) % 2 == 0:
            ax.axvspan(d, d + 10, color=EVEN_SHADE, alpha=0.08, lw=0)


def load():
    res = json.loads((OUT / "results.json").read_text())
    pool = pd.read_parquet(PROC / "pantheon_2020.parquet")
    pool = pool[(pool.birthyear >= WINDOW[0]) & (pool.birthyear <= WINDOW[1])]
    pool = pool.sort_values("hpi", ascending=False)
    base = pd.read_parquet(PROC / "births_baseline.parquet")
    return res, pool, base


# ---------------------------------------------------------------- figures
def fig1_birthyears(res, pool, base):
    top = pool.head(1000)
    decades = np.arange(1700, 1990, 10)
    obs = top.groupby("decade").size().reindex(decades, fill_value=0)
    pool_exp = pool.groupby("decade").size().reindex(decades, fill_value=0)
    pool_exp = pool_exp / pool_exp.sum() * 1000
    b = base[(base.birthyear >= 1700) & (base.birthyear <= 1989)].copy()
    b["decade"] = (b.birthyear // 10) * 10
    births_exp = b.groupby("decade")["births"].sum()
    births_exp = births_exp / births_exp.sum() * 1000

    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    shade_even_decades(ax, 1700, 1989)
    ax.bar(decades + 5, obs.values, width=8.6, color=BLUE, label="Top-1000 greats (observed)")
    ax.plot(decades + 5, pool_exp.values, color=INK, lw=2,
            label="Expected if parity-blind (all 67k famous)")
    ax.plot(decades + 5, births_exp.values, color=RED, lw=2, ls=":",
            label="Expected if proportional to world births")
    ax.set_xlim(1700, 1990)
    ax.set_xlabel("Birth decade (shaded = even decades, Group A)")
    ax.set_ylabel("People per decade")
    ax.set_title("Where the top-1000 greats were born")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "fig1_birth_decades")


def fig2_offset(res):
    r = res["datasets"]["pantheon_2020"]
    deltas = np.array(r["offset"]["deltas"]) * 100
    glm_z = [o["z"] for o in r["glm_offsets"]]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    ax = axes[0]
    colors = [BLUE if d == 0 else BASELINE for d in range(10)]
    ax.bar(range(10), deltas, color=colors, width=0.72)
    ax.axhline(0, color=INK, lw=0.8)
    ax.set_xticks(range(10))
    ax.set_xlabel("Decade-boundary offset (0 = the real XX00 boundary)")
    ax.set_ylabel("Top-1000 minus pool, Group-A share (pp)")
    ax.set_title("Naive offset test — a smooth gradient,\nthe fingerprint of a trend, not parity")
    ax.annotate("offset 0", (0, deltas[0]), xytext=(0.4, deltas[0] - 0.9),
                fontsize=9, color=BLUE, fontweight="bold")

    ax = axes[1]
    colors = [BLUE if d == 0 else BASELINE for d in range(10)]
    ax.bar(range(10), glm_z, color=colors, width=0.72)
    ax.axhline(0, color=INK, lw=0.8)
    for y in (-1.96, 1.96):
        ax.axhline(y, color=RED, lw=1, ls=":")
    ax.text(9.4, 1.96, "z = ±1.96", color=RED, fontsize=8, va="bottom", ha="right")
    ax.set_xticks(range(10))
    ax.set_xlabel("Decade-boundary offset")
    ax.set_ylabel("GLM parity z (trend controlled)")
    ax.set_title("Trend-controlled offset test —\noffset 0 is unremarkable")
    ax.set_ylim(-3, 3)
    save(fig, "fig2_offset_test")


def fig3_permutation(res):
    r = res["datasets"]["pantheon_2020"]["permutation"]
    hist = np.array(r["null_counts_hist"])
    ks = np.arange(len(hist))
    m = hist > 0
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(ks[m], hist[m], width=1.0, color=BASELINE, label="Null: 10,000 random top-1000s")
    ax.axvline(r["observed_k"], color=BLUE, lw=2.5)
    ax.annotate(f"observed = {r['observed_k']}\n(z = {r['z']:+.2f})",
                (r["observed_k"], hist.max() * 0.75), xytext=(r["observed_k"] - 42, hist.max() * 0.75),
                ha="right", fontsize=10, color=BLUE, fontweight="bold")
    ax.axvline(r["null_mean"], color=INK, lw=1.2, ls="--")
    ax.text(r["null_mean"] + 1.5, hist.max() * 0.95, f"null mean = {r['null_mean']:.0f}",
            fontsize=9, color=INK2)
    ax.set_xlabel("Even-decade births among 1000 (draws from the famous pool)")
    ax.set_ylabel("Frequency")
    ax.set_title("Permutation test: the top-1000 has FEWER even-decade births than chance\n(before trend control — see the mirror figure)")
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "fig3_permutation")


def fig4_mirror(res):
    r = res["datasets"]["pantheon_2020"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    for ax, key, title, color in [
        (axes[0], "era_matched", "Blocks start on EVEN decades\nera-matched z = +2.63 — “confirmed!”", AQUA),
        (axes[1], "era_matched_flip", "Same test, blocks start on ODD decades\nz = −2.74 — “refuted!”", RED),
    ]:
        em = r[key]
        hist = np.array(em["null_counts_hist"])
        ks = np.arange(len(hist))
        m = hist > 0
        ax.bar(ks[m], hist[m], width=1.0, color=BASELINE)
        ax.axvline(em["observed_k"], color=color, lw=2.5)
        ax.text(em["observed_k"], hist.max() * 1.02, f" observed (z = {em['z']:+.2f})",
                color=color, fontsize=9, fontweight="bold")
        ax.set_title(title, fontsize=10.5)
        ax.set_xlabel("Even-decade births among top-1000")
    axes[0].set_ylabel("Frequency")
    fig.suptitle("The mirror artifact: one within-block trend, two opposite “findings”",
                 fontweight="bold", y=1.04)
    save(fig, "fig4_mirror_artifact")


def fig5_forest(res):
    pf = res["datasets"]["pantheon_2020"]["per_field"]
    doms = sorted(pf, key=lambda d: pf[d]["glm"]["odds_ratio"])
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 0.55 * len(doms) + 1.8), sharey=True)

    ax = axes[0]  # naive difference in proportions
    for i, d in enumerate(doms):
        v = pf[d]
        lo, hi = (np.array(v["ci95"]) - v["null_share"]) * 100
        c = RED if v["bh_significant_q05"] else MUTED
        ax.plot([lo, hi], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(v["diff"] * 100, i, "o", color=c, ms=6)
    ax.axvline(0, color=INK, lw=0.9)
    ax.set_yticks(range(len(doms)))
    ax.set_yticklabels([d.title() for d in doms], fontsize=10)
    ax.set_xlabel("Naive: top-500 minus pool, Group-A share (pp)")
    ax.set_title("Naive per-field gap\n(red = “significant” after BH… but era-confounded)",
                 fontsize=10.5)

    ax = axes[1]  # GLM odds ratio
    for i, d in enumerate(doms):
        g = pf[d]["glm"]
        lo, hi = g["or_ci95"]
        sig = not (lo <= 1 <= hi)
        c = BLUE if sig else MUTED
        ax.plot([lo, hi], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(g["odds_ratio"], i, "o", color=c, ms=6)
        ax.text(hi * 1.02, i, f"OR {g['odds_ratio']:.2f} (n={pf[d]['n']})",
                fontsize=8.5, va="center", color=INK2)
    ax.axvline(1, color=INK, lw=0.9)
    ax.set_xscale("log")
    ticks = [0.9, 1.0, 1.1, 1.2, 1.4]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{t:g}" for t in ticks])
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xlabel("Trend-controlled: GLM odds ratio for even-decade birth (95% CI)")
    ax.set_title("Same fields, trend controlled\n(every CI crosses 1 — nothing left)",
                 fontsize=10.5)
    save(fig, "fig5_forest_fields")


def fig6_heatmap(pool):
    top_k = 500
    decades = np.arange(1700, 1990, 10)
    doms = [d for d, g in pool.groupby("domain") if len(g) >= 2 * top_k]
    mat = np.full((len(doms), len(decades)), np.nan)
    for i, d in enumerate(doms):
        g = pool[pool.domain == d]
        top = g.head(top_k)  # pool is HPI-sorted
        n_pool = g.groupby("decade").size().reindex(decades, fill_value=0)
        obs = top.groupby("decade").size().reindex(decades, fill_value=0) / len(top)
        exp = n_pool / len(g)
        with np.errstate(divide="ignore", invalid="ignore"):
            row = np.log2(obs.values / exp.values)
        row[n_pool.values < 30] = np.nan  # too little data to say anything
        mat[i] = row
    mat = np.clip(mat, -2, 2)
    fig, ax = plt.subplots(figsize=(11, 0.5 * len(doms) + 2))
    cmap = plt.get_cmap("RdBu_r").copy()
    cmap.set_bad("#eceae4")
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=-2, vmax=2)
    ax.set_xticks(range(0, len(decades), 2))
    ax.set_xticklabels(decades[::2], fontsize=8)
    ax.set_yticks(range(len(doms)))
    ax.set_yticklabels([d.title() for d in doms], fontsize=9)
    ax.grid(False)
    cb = fig.colorbar(im, ax=ax, shrink=0.8)
    cb.set_label("log2(top-500 share / pool share)", fontsize=9)
    ax.set_title("Over/under-representation by decade x field (x labels are the even decades)\n"
                 "Red = era over-canonized, gray = too few people. Columns move together — era, not parity")
    save(fig, "fig6_heatmap")


def fig7_sensitivity(res, pool):
    ns = np.unique(np.geomspace(50, len(pool), 60).astype(int))
    a = pool.group_a.values
    shares = [a[:n].mean() for n in ns]
    p0 = a.mean()
    lo = p0 - 1.96 * np.sqrt(p0 * (1 - p0) / ns)
    hi = p0 + 1.96 * np.sqrt(p0 * (1 - p0) / ns)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.fill_between(ns, lo * 100, hi * 100, color=BASELINE, alpha=0.45,
                    label="Parity-blind 95% band around pool share")
    ax.axhline(p0 * 100, color=INK, lw=1, ls="--")
    ax.plot(ns, np.array(shares) * 100, color=BLUE, lw=2, label="Observed Group-A share of top-N")
    ax.axhline(50, color=MUTED, lw=0.8, ls=":")
    ax.text(ns[0], 50.3, "50%", fontsize=8, color=MUTED)
    ax.set_xscale("log")
    ax.set_xlabel("Top-N cutoff by HPI (log scale)")
    ax.set_ylabel("Group-A (even decade) share, %")
    ax.set_title("Fame-threshold sensitivity: the elite are LESS even-decade than the merely famous\n(driven by era, not parity — see GLM)")
    ax.legend(loc="lower right", fontsize=9)
    save(fig, "fig7_sensitivity")


def fig8_rolling(pool, base):
    top5000 = pool.head(5000)
    years = np.arange(1800, 1990)
    counts = top5000.groupby("birthyear").size().reindex(years, fill_value=0)
    b = base.set_index("birthyear")["births"].reindex(years)
    rate = (counts / b * 1e6).rolling(10, center=True).mean()
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    shade_even_decades(ax, 1800, 1989)
    ax.plot(years, rate.values, color=BLUE, lw=2)
    ax.set_xlim(1800, 1990)
    ax.set_xlabel("Birth year (shaded = even decades)")
    ax.set_ylabel("Top-5000 greats per million births\n(10-year centered rolling mean)")
    ax.set_title("Greats per million births: a long slide, no alternating rhythm")
    save(fig, "fig8_rolling_rate")


def main() -> None:
    FIG.mkdir(exist_ok=True)
    res, pool, base = load()
    fig1_birthyears(res, pool, base)
    fig2_offset(res)
    fig3_permutation(res)
    fig4_mirror(res)
    fig5_forest(res)
    fig6_heatmap(pool)
    fig7_sensitivity(res, pool)
    fig8_rolling(pool, base)


if __name__ == "__main__":
    main()
