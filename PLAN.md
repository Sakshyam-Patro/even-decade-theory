# PLAN — Even-Decade Theory research project

Goal: rigorously test whether "greats" are disproportionately born in even decades
(tens digit even), per PREREGISTRATION.md, and produce REPORT.md + blog_post.md.

## Pipeline (single entry point: `run.py`)

```
run.py
 ├─ src/fetch_pantheon.py    # download Pantheon 2.0 person dataset → data/raw/, cache
 ├─ src/fetch_wikidata.py    # SPARQL: humans by sitelinks, chunked queries → data/raw/
 ├─ src/fetch_nobel.py       # api.nobelprize.org laureates → data/raw/
 ├─ src/fetch_baseline.py    # world births (OWID/UN) + population (pre-1950) → data/raw/
 ├─ src/clean.py             # dedupe, drop bad birth years, eligibility window → data/processed/*.parquet
 ├─ src/analysis.py          # all pre-registered tests → output/results.json
 ├─ src/figures.py           # all figures → figures/*.png + *.svg
 └─ src/report.py            # inject numbers into output/REPORT.md skeleton (final prose hand-written)
```

## Order of work
1. PREREGISTRATION.md (done, locked before data)
2. Fetch + cache all raw data (each fetcher skips if cache exists → reproducible offline)
3. Clean → parquet
4. Analysis battery (order: primary binomial → offset test → permutation → per-field
   BH-corrected → Bayesian beta-binomial → fame-weighted → temporal splits)
5. Figures (7 pre-listed in the brief)
6. REPORT.md, blog_post.md, X thread
7. DECISIONS.md updated continuously

## Fallbacks
- Pantheon URL dead → try GitHub mirrors / dataverse; log substitution.
- Wikidata SPARQL timeouts → chunk by birth-year ranges + sitelink floor; if still failing,
  reduce to threshold-only query without occupations.
- OWID births CSV shape changes → Gapminder births/population fallback.

## Non-goals
- No causal story-hunting if the effect is null; the offset test verdict is final.
- No interactive dashboard (static figures only) for v1.
