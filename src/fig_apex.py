"""Figure 9: the apex steelman — escalation curve and the 93-GOAT tally."""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from figures import save, SURFACE, INK, INK2, MUTED, GRID, BASELINE, BLUE, RED, AQUA

ROOT = Path(__file__).resolve().parent.parent
OUT, FIG = ROOT / "output", ROOT / "figures"


def main() -> None:
    res = json.loads((OUT / "apex_results.json").read_text())
    goats = pd.read_csv(OUT / "goat_list.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6),
                             gridspec_kw={"width_ratios": [1, 1.3]})

    # Panel A: escalation curve
    ax = axes[0]
    tiers = ["top-10", "top-5", "top-4", "top-3", "top-2", "GOAT\n(top-1)"]
    x = np.arange(6)
    for key, color, label in [("escalation", BLUE, "Pantheon 2020 (primary)"),
                              ("escalation_2025", AQUA, "Pantheon 2025 (replication)")]:
        t = res[key]
        ax.plot(x, [v["share"] * 100 for v in t], "-o", color=color, lw=2, ms=6,
                label=label)
    null = res["escalation"]
    ax.fill_between(x, [v["null_ci95_share"][0] * 100 for v in null],
                    [v["null_ci95_share"][1] * 100 for v in null],
                    color=BASELINE, alpha=0.4, label="Field-elite null, 95% band")
    ax.plot(x, [v["null_mean_share"] * 100 for v in null], ls="--", color=INK, lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(tiers)
    ax.set_ylabel("Even-decade share, %")
    ax.set_xlabel("Rank tier within each field (93 fields; 88 for top-10)")
    ax.set_title("The escalation test: the theory predicts a climb\ntoward the GOAT tier. There is none.", fontsize=10.5)
    ax.legend(fontsize=8, loc="lower left")

    # Panel B: 93 GOATs as a dot grid
    ax = axes[1]
    g = goats.sort_values("birthyear").reset_index(drop=True)
    cols = 16
    for i, r in g.iterrows():
        xx, yy = i % cols, i // cols
        c = BLUE if r.even_decade else "#d5d3ca"
        ax.scatter(xx, -yy, s=210, color=c, edgecolors=SURFACE, linewidths=1.5, zorder=3)
    n_even = int(g.even_decade.sum())
    ax.set_title(f"The GOAT of each of {len(g)} fields, oldest to newest\n"
                 f"{n_even} even-decade ({n_even/len(g):.0%}) vs 51% expected — a coin flip",
                 fontsize=10.5)
    ax.text(0, -(len(g) // cols) - 1.2,
            "blue = even decade (Jordan '63, Pelé '40, Ali '42, Napoleon 1769…)\n"
            "gray = odd decade (Einstein 1879, Beethoven 1770, Gauss 1777, Elvis '35…)",
            fontsize=8.5, color=INK2)
    ax.set_xlim(-0.7, cols - 0.3)
    ax.axis("off")
    save(fig, "fig9_apex_goats")


if __name__ == "__main__":
    main()
