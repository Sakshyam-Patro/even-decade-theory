# The Even-Decade Theory: a pre-registered test

**Verdict up front: the theory is refuted.** After controlling for when people were
born, being born in an even decade changes the odds of ranking among the top-1000
most eminent humans by a factor of **0.99** (95% CI 0.87–1.12). The pre-registered
decision rule fails on all three of its conditions. But the road to that answer turned
up something better than the hypothesis: two opposite-signed statistical traps, either
of which would have produced a confident, publishable, and wrong result.

## 1. The hook

Michael Jordan, 1963. LeBron, 1984. Bolt, 1986. Messi, 1987. Pelé, 1940. Napoleon,
1769. Newton, 1643. Every one born in an even decade — a decade whose tens digit is
even (00–09, 20–29, 40–49, 60–69, 80–89; call this **Group A**). The hypothesis: the
higher you climb the all-time rankings, the more Group A dominates.

The base rate for Group A is roughly one half, so seven remembered examples are also
exactly what confirmation bias produces from nothing. Hence this project: a
pre-registered test where the analysis choices were locked before any data was seen
(`PREREGISTRATION.md`), with every later judgment logged in `DECISIONS.md`.

## 2. Pre-registered predictions and decision rule

The theory **survives** only if all three hold:

1. **Primary test:** Pantheon top-1000 by HPI (born 1700–1989) shows a Group A share
   significantly above the share in the full eligible Pantheon population
   (exact binomial, one-sided, α = 0.05).
2. **Offset test:** the XX00 decade boundary (offset 0) is the most extreme of the 10
   possible ways to cut years into alternating decades.
3. **Direction replicates** in an independent fame metric (Wikidata sitelinks).

## 3. Data

| Dataset | Role | N (eligible, born 1700–1989) | Fame metric |
|---|---|---|---|
| MIT Pantheon 2.0 (2020) | primary | 67,198 | HPI |
| Pantheon 2025 update | replication | 91,441 | HPI |
| Wikidata (≥60 sitelinks) | replication | 5,126 | sitelink count |
| Nobel laureates (official API) | sanity check | 990 laureate-prizes | none (whole list) |

Baselines: (a) **internal** — the full eligible Pantheon population, which shares every
documentation and notability bias with the top-N; (b) **demographic** — world births per
year (UN WPP from 1950, HYDE population × slowly-varying crude birth rate before).

One pre-registration error is disclosed up front (DECISIONS.md D6): the 1700–1989
window contains 15 even decades but 14 odd ones, so it is not parity-balanced as
claimed. This inflates raw Group A shares mechanically; the internal baseline and the
GLM absorb it, and the robustness windows agree with the main result.

## 4. Results

### 4.1 Primary test: fails — and in the *opposite* direction

The top-1000 is 51.4% Group A (514/1000). The full famous population is 56.0%. The
pre-registered one-sided test fails completely (p = 0.999); two-sided, the top-1000 is
significantly *under*-represented in even decades (p = 0.003, permutation z = −2.95).

Sensitivity across cutoffs (share of Group A, vs pool 56.0%): top-100 = 54.0%,
top-500 = 52.2%, top-1000 = 51.4%, top-5000 = 53.3%. Robustness windows 1800–1989 and
1500–1989 agree. Bayesian posterior probability that Group A is over-represented vs
the internal baseline: 0.002. The theory's strong form — "the effect grows as you
approach the top" — is inverted: the elite are *less* even-decade than the merely
famous (fig7).

Against the demographic births baseline the top-1000 is simply null: 51.4% observed
vs 52.6% expected (p = 0.47).

### 4.2 The offset test: fails, and reveals the real culprit

Pre-registered criterion: offset 0 must be the most extreme of the 10 possible decade
boundaries. Observed: offset 0 ranks 10/10 — the most extreme *negative* delta. But the
tell is the pattern: the deltas rise smoothly from −4.6pp at offset 0
to +3.5pp at offset 9 (fig2, left). A genuine parity effect would make offset 0 a
discontinuous outlier. A smooth gradient across offsets is the fingerprint of a
**birth-year trend**, not a parity effect.

The trend is real and enormous: the top-1000's mean birth year is 1870; the full
pool's is 1931. Canonization takes time, and the famous pool is stuffed with people
born in the 1970s–80s who will never be canonized. The 1980s — an even decade, and the
pool's largest (11,823 people) — single-handedly drags the pool's Group A share up and
makes the older-skewing top-1000 look anti-even-decade.

### 4.3 The mirror artifact: how the same trend fakes both verdicts

To remove the trend we ran an era-matched permutation: null top-1000s drawn from the
pool matching the real top-1000's counts within 20-year blocks, each block spanning
one even and one odd decade. Result: z = **+2.63** (p = 0.005). The theory looked
*confirmed*.

It wasn't. In blocks aligned `[1700–1719, 1720–1739, …]`, the even decade is always
the block's *first* half — and because canonization favors earlier births *within*
blocks too, any monotone trend leaks in as a fake pro-even signal. Realigning the
blocks to start on odd decades flips the bias: z = **−2.74**. Same data, same test,
opposite "finding" (fig4). Two z-scores near ±2.7 that mirror under a nuisance
realignment are not evidence; they are the trend photographed from two angles.

### 4.4 The referee: trend-controlled GLM

The decisive test aggregates by birth year and fits a binomial GLM:
logit P(top-1000 | year) = smooth polynomial in year + β·(even decade). The polynomial
absorbs the trend at every scale; β captures only the alternating signal.

**β = −0.010, odds ratio 0.990 (95% CI 0.872–1.123), z = −0.16, p = 0.87.**

Stable under polynomial degree 3/5/8 (z = −0.22 / −0.16 / −0.09). In the
trend-controlled offset test, offset 0 ranks 3/10 and no offset reaches |z| = 1.4
(fig2, right) — exactly the flat profile the null predicts.

### 4.5 Replications

| Dataset | Trend-controlled OR (95% CI) | z |
|---|---|---|
| Pantheon 2020 (primary) | 0.99 (0.87–1.12) | −0.16 |
| Pantheon 2025 | 1.04 (0.92–1.18) | +0.59 |
| Wikidata sitelinks | 1.06 (0.92–1.22) | +0.82 |

Both replications also reproduce the mirror artifact (2025: era-matched +3.36 vs
flipped −2.07), confirming it is structural, not a quirk of one dataset.

Nobel laureates: 52.4% Group A vs 53.4% expected from births (p = 0.55, n = 990).
No prize category deviates (all p ≥ 0.36).

### 4.6 Per-field breakdown

Naively, Sports shows a striking −8.1pp gap (BH-significant) — top athletes appear to
*avoid* even decades. It is the same era artifact in miniature: sports fame is
concentrated in recent, even-heavy decades, and the all-time greats skew earlier.
Trend-controlled, Sports gives OR 1.11 (CI 0.93–1.33), and **every domain's CI crosses
1** (Arts 1.18, Public Figure 1.14, Sports 1.11, Science 1.10, Humanities 1.10,
Institutions 1.06) (fig5). The heatmap (fig6) shows why the naive numbers wobble:
entire decade-columns move together across all fields — eras get over- or
under-canonized wholesale, with no alternating rhythm.

### 4.7 Fame-weighted analysis

HPI-weighting every eligible person shifts the Group A share by −1.4pp
(bootstrap CI −1.5 to −1.3) — the era artifact again, in the naive direction; it
vanishes under trend control. Weighting by fame intensity does not rescue the theory.

### 4.8 Temporal stability

Within every birth half-century, the top-1000's Group A share tracks its era's pool
share closely, with small gaps of mixed sign (e.g. 1700–49: 58.5% vs 62.2%;
1750–99: 40.4% vs 38.4%; 1900–49: 60.6% vs 63.1%). No era shows a consistent parity
effect.

## 5. Verdict against the pre-registered rule

1. Primary test rejects in the predicted direction: **No** (opposite direction).
2. Offset 0 most extreme in the predicted direction: **No** (most extreme negative;
   smooth gradient diagnostic of trend).
3. Replication of direction: **No** (all trend-controlled estimates within noise of 1).

**The Even-Decade Theory is refuted.** The tightest honest statement: among people
famous enough to enter Pantheon, being born in an even decade multiplies the odds of
top-1000 eminence by 0.99 (CI 0.87–1.12) — indistinguishable from nothing, and the
confidence interval rules out anything beyond a ±13% effect.

## 6. The apex steelman: testing the theory where it lives

A fair objection to everything above: the theory was never about the top-1000. It is
about the GOAT — the #1 of each field, maybe the top-3. Small-N means low power, so
a real apex effect could hide from population tests. We therefore ran a battery
designed *in the theory's favor* (DECISIONS.md D10):

- **The GOAT test.** The single highest-HPI person in each of 93 Pantheon
  occupations — Jordan (basketball), Pelé (soccer), Ali (boxing), Einstein (physics),
  Beethoven (composers), Kant (philosophy), no human curation. Result: **49 of 93
  even-decade (52.7%)** vs 51.4% expected from a within-field-elite null
  (z = +0.27, p = 0.44). A coin flip (fig9, `output/goat_list.csv`).
- **The escalation test.** The theory's sharpest prediction: the even-decade share
  should climb monotonically toward the top. Observed (2020), tiers top-10 → 5 →
  4 → 3 → 2 → 1: 51.0% → 49.9% → 50.8% → 49.5% → 50.0% → 52.7%. No climb; every
  tier sits inside the null band. The 2025 replication wiggles the other way
  (51.8% → 54.5% → 55.3% → 55.0% → 55.3% → 52.1%) — its top-4 tier grazes nominal
  significance (z = +1.74, p = 0.046 one-sided), which we disclose and discount:
  it is 1 of 12 uncorrected tier tests (≈1 such blip expected by chance), it does
  not replicate in the primary dataset (top-4 there: z = −0.30), and it *recedes*
  at top-1, exactly where the theory needs it to peak (fig9). Crucially, this
  null compares each GOAT only against their own field's elite (Jordan vs LeBron
  and Kareem, not vs Kant), so the era confound from §4 cannot operate here.
- **The ancients, and a trap in the theory's favor.** Extending to religious
  figures and philosophers of antiquity (the Buddha, Confucius, Muhammad) requires
  care: among people born before 500 CE, **59.9% of recorded birth years end in
  0** — because they are estimates rounded to round numbers — versus 9.4% for
  post-1700 births. A year ending in 0 always lands in an even decade, so ancient
  data mechanically favors the theory regardless of truth (even-decade share 57.9%
  pre-500 CE, falling to ~50% exactly as record-keeping improves). Taking the
  recorded years at face value, the apex ancients still split (Muhammad,
  Aristotle, Plato odd-decade; Confucius, Luther even-decade), but most ancient
  birth years — Moses, Abraham, the Buddha, Jesus — are tradition or scholarly
  estimates, so antiquity cannot testify either way.

The apex is where the theory had its last, best chance. It is null there too.

## 7. Why the examples felt so convincing

- **Base-rate neglect:** ~half of everyone is born in an even decade, so a handful of
  remembered hits (Jordan 1963, Maradona 1960, Bolt 1986) is the expected output of
  memory, not evidence. The misses never get tallied: Beethoven 1770 and Mozart 1756 —
  the #1 and #3 most eminent people in the entire dataset — are odd-decade, along with
  Einstein 1879, Babe Ruth 1895, Magic Johnson 1959, Kobe Bryant 1978, and Tom Brady
  1977.
- **Era clustering mistaken for parity:** greats genuinely cluster (fig6's columns,
  fig8's long arcs) because opportunity clusters — postwar sports economies, the
  physics revolution, recorded music. Some celebrated clusters happen to sit in even
  decades (the 1980s football generation), and the pattern-matching mind promotes a
  cluster into a rule.
- **Decade round-number salience:** "born in the 60s" is a natural category; "born
  1955–1964" is not. Categories that are easy to name are easy to over-count.

## 8. Limitations

- **Fame ≠ greatness.** HPI and sitelinks measure Wikipedia-mediated memory, which is
  Western- and recency-skewed. But the parity hypothesis must show up in any
  reasonable eminence metric to be a law; it shows up in none of three.
- The pre-1950 births baseline uses population × approximated crude birth rate; it
  matters only for the demographic-baseline tests, and parity contrasts are
  insensitive to smooth baseline error.
- The Wikidata replication (n = 5,126 eligible) is smaller than planned (sitelink
  floor of 60 yielded fewer people than estimated; DECISIONS.md D9).
- The era-matched permutation and GLM were added after seeing the first results
  (disclosed, D7). They are direction-symmetric — each could have rescued the theory
  as easily as buried it — and the pre-registered tests alone already refute.
- 1990s+ births are excluded by design; nothing here speaks to whether the *current*
  generation's eventual greats will favor even decades. (The null predicts: no.)

## 9. Conclusion

The data decide, and they decide clearly. There is no even-decade effect on greatness:
not overall, not in any field, not at any fame threshold, not in any century, not
under any of ten decade boundaries, not in four datasets. What exists instead is a
powerful *era* effect — greatness per birth cohort rises and falls in long waves — and
a pair of alternating-decade traps that can manufacture a ±2.7σ "discovery" in either
direction depending on an arbitrary alignment choice. The theory dies; the methods
lesson survives.

---

*Reproduce everything: `python run.py` from the repo root. All statistics live in
`output/results.json`; every analysis decision is logged in `DECISIONS.md`.*
