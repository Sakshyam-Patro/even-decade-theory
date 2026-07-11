# DECISIONS log

- **D1 (2026-07-11):** Pre-registration written and locked before any data download.
  Eligibility window 1700–1989; ceiling at end of a complete decade pair so truncation
  cannot bias parity. Primary baseline = full Pantheon eligible population (internal),
  secondary = demographic births baseline.
- **D2 (2026-07-11):** Primary confirmatory N fixed at 1000 (top-1000 by HPI). N ∈
  {100, 500, 5000} demoted to sensitivity analyses to avoid multiple-comparisons
  ambiguity in the headline claim.
- **D3 (2026-07-11):** Decision rule requires the offset test (offset 0 must be the max
  of 10 offsets) in addition to the primary p-value — a significant primary result alone
  is treated as insufficient, since smooth temporal trends can leak into any fixed
  parity split.
- **D4 (2026-07-11, before any analysis):** GCS bucket listing revealed a
  `person_2025_update.csv.bz2` in addition to the pre-registered 2020 file. Keeping
  **2020 as the primary** dataset (as pre-registered) and adding the **2025 update as a
  replication** dataset. No person-level data had been inspected at the time of this
  amendment.
- **D5 (2026-07-11):** Pantheon person CSV lacks a `domain` column; occupation→domain
  mapping fetched from the official `api.pantheon.world/occupation` endpoint (8 domains)
  rather than hand-built, to avoid subjective field assignment.
- **D6 (2026-07-11):** Arithmetic error found in the pre-registration: the 1700–1989
  window contains 15 even decades but 14 odd ones (the 1980s is unpaired), so it is NOT
  parity-balanced as claimed. The internal baseline absorbs this mechanically (both
  top-N and pool face the same window), but the raw pool share (~0.56 Group A) must not
  be read as evidence of anything. Window kept as pre-registered; error disclosed.
- **D7 (2026-07-11, post-hoc, disclosed):** After the first run, the 10 offset deltas
  formed a smooth monotone gradient — the signature of a birth-year trend (top-1000 mean
  birth year 1870 vs pool 1931), not a parity effect. Added an **era-matched permutation**:
  null top-1000s are drawn block-by-block from the pool matching the real top-1000's
  counts in 20-year blocks (each block = one even + one odd decade), so era cancels and
  only parity remains. This test is direction-symmetric: it can rescue the theory from a
  spurious refutation exactly as easily as it can bury it. It supersedes the naive
  internal-baseline z as the most trustworthy single number.
- **D8 (2026-07-11):** The era-matched test itself proved trend-contaminated (its z
  flipped from +2.63 to −2.74 when block alignment moved from even-first to
  odd-first). Final referee analysis: binomial GLM with a degree-5 polynomial in
  birth year plus a parity indicator, checked at degrees 3 and 8 and at all 10
  offsets. Both alignments of the era-matched test are reported as the "mirror
  artifact" exhibit rather than as evidence.
- **D9 (2026-07-11):** Nobel API v2.1 timed out repeatedly; substituted the official
  v1 bulk endpoint (same publisher). Wikidata sitelink floor of 60 yielded 5,126
  eligible people instead of the pre-registered 15k-25k target; kept as-is rather
  than lowering the floor post-hoc, and treated as a smaller replication set.
- **D10 (2026-07-11, user-requested steelman):** User clarified the theory targets the
  APEX (the #1 / top-3 of each field), not top-1000 populations. Added src/apex.py:
  (a) GOAT test — the highest-HPI person in every Pantheon occupation, tested against
  a within-field elite null (draw 1 of the field's top-10), which is era-proof by
  construction; (b) escalation curve across rank tiers k = 10,5,3,1; (c) extended
  window past 1700 for religious figures/ancients, gated by a round-number
  (birth years ending in 0/5) artifact check. Exploratory and disclosed; designed to
  give the theory its maximum chance.
