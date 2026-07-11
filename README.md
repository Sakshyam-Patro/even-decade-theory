# The Even-Decade Theory

A pre-registered, reproducible test of the hypothesis that historically "great" people
are disproportionately born in even decades (birth years ending 00-09, 20-29, 40-49,
60-69, 80-89).

**Verdict: refuted.** Trend-controlled odds ratio for even-decade birth among the
top-1000 most eminent people: **0.99** (95% CI 0.87-1.12). Full story in
[output/REPORT.md](output/REPORT.md), short version in
[output/blog_post.md](output/blog_post.md).

## Reproduce

```bash
python3 -m venv .venv
.venv/bin/pip install pandas numpy scipy matplotlib requests pyarrow
.venv/bin/python run.py
```

`run.py` downloads ~80 MB of raw data into `data/raw/` (gitignored) and caches it;
re-runs are offline. The cleaned parquet files in `data/processed/` are committed, so
you can skip the fetch steps and run `analysis.py` + `figures.py` directly. All
statistical draws are seeded, so every number in the report reproduces exactly.

## Layout

- `PREREGISTRATION.md` — hypotheses, tests, and decision rule, locked before any data
- `PLAN.md`, `DECISIONS.md` — approach and a log of every judgment call
- `src/` — pipeline: fetch → clean → analyze → figures
- `data/raw/`, `data/processed/` — cached raw downloads, analysis-ready parquet
- `output/results.json` — every statistic in the report
- `output/REPORT.md`, `output/blog_post.md` — full write-up and blog version
- `figures/` — all charts, PNG + SVG

## Data sources

- [MIT Pantheon 2.0](https://pantheon.world) person dataset (2020 primary, 2025 replication), HPI fame metric
- Wikidata SPARQL: humans with ≥60 Wikipedia language editions (n=5,333)
- [Nobel Prize API](https://api.nobelprize.org) (v1), 990 laureate-prizes
- Our World in Data: world births (UN WPP) and population (HYDE) for the demographic baseline
