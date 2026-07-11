# PREREGISTRATION — The Even-Decade Theory

**Date locked:** 2026-07-11 (before any data was downloaded or inspected)
**Author:** Automated analysis pipeline (Claude Code), on behalf of Sakshyam Patro

## 1. Hypothesis

**Claim under test (H1):** Historically "great" individuals are disproportionately born in
*even decades* — birth years whose tens digit is even (years ending 00–09, 20–29, 40–49,
60–69, 80–89 within any century). Call this **Group A**. Odd decades (10–19, 30–39, 50–59,
70–79, 90–99) are **Group B**.

**Null (H0):** Decade parity of birth year is independent of eminence. The expected Group A
share among "greats" equals the Group A share of the relevant baseline population (see §4),
not necessarily 50/50.

The stronger folk version of the claim ("the effect intensifies as you go from top-100 to
top-10 to top-1") is tested via the fame-threshold sensitivity analysis (§6.6), but the
**primary** confirmatory test is at fixed N (§5).

## 2. Datasets (inclusion criteria fixed here)

1. **Primary — MIT Pantheon 2.0** (`person_2020_update`, ~88k individuals). Fame metric:
   **HPI (Historical Popularity Index)**, as published; no re-derivation. "Greats" = top-N
   by HPI among eligible individuals.
2. **Secondary — Wikidata**: humans (P31=Q5) with a known birth date, ranked by
   **sitelink count** (number of Wikipedia language editions). Target: everyone above a
   sitelink threshold chosen *before analysis* to yield roughly 15k–25k people born
   1800–2000. Used as an independent-fame-metric replication.
3. **Tertiary — curated lists** (small-N sanity checks only, no confirmatory claims):
   Nobel laureates (official API), plus whatever consensus GOAT lists are cleanly
   obtainable (e.g., halls of fame). Each kept as a separate labeled dataset.

**Eligibility window (main analysis):** birth years **1700–1989** inclusive.
- Pre-1700 excluded: calendar/records unreliability and sparse coverage.
- Post-1989 excluded: recency/eligibility — people born in the 1990s+ have not had time to
  accumulate "GOAT" status by 2026, and the truncation would artificially favor whichever
  parity the last complete decades have.
- The ceiling is set at the end of a *complete decade pair* (1970s+1980s), so truncation
  itself cannot bias parity.
- Exclusions: unknown or estimated-only birth years; duplicate persons (dedupe on
  name+birth-year, and on Wikidata QID where available).

**Robustness windows (pre-declared):** 1800–1989 and 1500–1989.

## 3. Primary confirmatory test

- **Population:** Pantheon top-**1000** by HPI, born 1700–1989.
- **Statistic:** observed Group A share.
- **Null model:** Group A share of the *baseline* (§4).
- **Test:** exact binomial test, **one-sided** (H1: Group A overrepresented), α = **0.05**.
  Two-sided p also reported. Effect size: difference in proportions with 95% CI
  (Wilson), and odds ratio.
- N = 1000 is the single pre-registered confirmatory N. N ∈ {100, 500, 5000} are
  pre-declared sensitivity analyses, not additional confirmatory tests.

## 4. Baseline (the critical control)

The naive 50/50 null is wrong if births differ by decade. Two baselines, in order:

1. **Primary baseline — internal:** the Group A share of the **full eligible Pantheon
   population** (all ~tens of thousands of individuals born 1700–1989, not just top-N).
   This automatically controls for birth-rate variation, documentation/coverage effects,
   and Wikipedia-notability drift, because top-N and baseline are drawn from the same
   fame-generating process. The question becomes: *given that you're famous enough to be
   in Pantheon, does extreme greatness prefer even decades?*
2. **Secondary baseline — demographic:** world births (UN WPP 1950+) chained to world
   population estimates (Gapminder/HYDE) for pre-1950 decades, giving expected Group A
   share proportional to births per decade. Used to check the theory at the
   "famous at all vs born at all" margin.

If the two baselines disagree on the verdict, both results are reported and the
disagreement is discussed; the internal baseline is authoritative for the headline claim.

## 5. Decision rule (what confirms vs refutes)

The theory **survives** only if ALL of:
1. Primary test (§3) rejects H0 at α = 0.05 (one-sided) with Group A overrepresented;
2. **Offset test:** decade parity defined at offset 0 (the XX00 boundary) produces a more
   extreme Group A-equivalent share than at least **9 of the 10** possible offsets
   (i.e., offset 0 is the maximum of the 10); and
3. The direction replicates (point estimate favoring Group A) in the Wikidata secondary
   dataset.

The theory is **refuted** if the primary test fails to reject H0, or if offset 0 looks
like a typical draw among the 10 offsets (rank ≤ 7 of 10). Intermediate outcomes
(significant primary but unremarkable offset rank, or non-replication) are reported as
"not supported / likely artifact."

## 6. Pre-declared robustness & secondary analyses

1. Sensitivity to fame threshold: N ∈ {100, 500, 1000, 5000}.
2. **Offset test** (all 10 boundary offsets), on top-1000 and full eligible population.
3. **Permutation test:** 10,000 draws of size N from the eligible Pantheon pool
   (sampling birth years without replacement), null distribution of Group A share.
4. **Per-field breakdown:** primary test within each Pantheon occupation domain;
   Benjamini–Hochberg FDR at q = 0.05 across fields. Forest plot.
5. **Bayesian:** Beta(1,1)-binomial; posterior P(Group A share > baseline share) and
   posterior of the effect size.
6. **Fame-weighted:** HPI-weighted (and log-sitelink-weighted) Group A share vs
   weighted baseline; bootstrap CI (10,000 resamples).
7. **Temporal stability:** primary test within birth half-centuries
   (1700–49, 1750–99, ..., 1950–89).
8. Alternate windows: 1800–1989, 1500–1989.

## 7. What we will NOT do

- No post-hoc redefinition of "even decade," the eligibility window, or the fame metric.
- No dropping of fields, eras, or datasets after seeing results (all pre-declared cuts
  are reported regardless of outcome).
- No promotion of a secondary analysis to headline result if the primary fails.

## 8. Outputs

`REPORT.md` (full methods/results/limitations) and `blog_post.md` + X thread, stating
plainly whether the theory survived the decision rule in §5.
