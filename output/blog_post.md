# I tested my "Even-Decade Theory" of greatness. It died twice.

For years I noticed a pattern. Jordan, born 1963. LeBron, 1984. Bolt, 1986. Messi,
1987. Pele, 1940. Napoleon, 1769. Newton, 1643. All born in even decades: the 40s,
the 60s, the 80s. My theory was that all-time greats cluster there, and that the
effect gets stronger as you go from top-100 to top-10 to top-1.

So I built a real test. Pre-registered hypotheses before touching data. 67,198
famous people from MIT's Pantheon dataset, ranked by their Historical Popularity
Index. Two replication datasets (Pantheon's 2025 update and Wikidata) plus all 990
Nobel laureates. A birth-rate baseline so population booms could not fake the
result. The decision rule was locked in advance.

The theory is false. But the way it died is the interesting part. It produced two
convincing wrong answers before it produced the right one.

## Wrong answer #1: the theory is backwards

First test: are the top-1000 greats more even-decade than the other 66,000 famous
people? No. They are less. 51.4% versus 56.0%, and the gap is "significant" at
p = 0.003. For a day the data said greatness avoids even decades.

That was an artifact. All-time greats skew old (mean birth year 1870). The famous
pool skews young (mean 1931), because Wikipedia is full of athletes and actors born
in the 1980s. The 1980s is an even decade. So the pool looks even-heavy and the
greats look even-light, purely because of when they were born, not what decade digit
they were born under.

The tell is the offset test. There are ten ways to slice years into alternating
decades, and only one of them is the real 0-to-9 decade. If the theory were real,
the real slicing should stand out. Instead the effect slides smoothly across all ten
offsets. That smooth slide is the fingerprint of a trend, not a decade effect.

![Offset test](../figures/fig2_offset_test.png)

## Wrong answer #2: the theory is confirmed

So I controlled for era. I compared the greats only against famous people born in
the same 20-year window. The result flipped hard: z = +2.63, p = 0.005. The theory
looked alive and significant.

Also an artifact, and a nastier one. My 20-year windows started on even decades, so
the even decade was always the older half of each window. Older within the window
means more canonized. I re-ran the identical test with windows starting on odd
decades. The result flipped again: z = -2.74. Same data. Same method. One arbitrary
alignment choice, two opposite discoveries.

![The mirror artifact](../figures/fig4_mirror_artifact.png)

## The real answer: nothing

The honest test is a regression that soaks up the birth-year trend with a smooth
curve and then asks whether an alternating even-odd signal remains on top of it.

It does not. Odds ratio 0.990, confidence interval 0.87 to 1.12. Being born in an
even decade does nothing to your odds of all-time greatness. The same null holds in
the 2025 dataset (OR 1.04), in Wikidata (OR 1.06), in every field from sports to
science, at every fame cutoff, in every half-century since 1700, and among Nobel laureates (52.4%
even-decade, expected 53.4%). The strongest version of my theory, that the top of
the top is where the effect lives, is where it is deadest: Beethoven (1770) and
Mozart (1756), the two highest-ranked musicians in the dataset, are both odd-decade.

![Nothing left in any field](../figures/fig5_forest_fields.png)

## "But the theory is about the GOAT, not the top-1000"

That was my own objection, so I tested it. I took the #1 most eminent person in
each of 93 fields, picked by the data, not by me. Jordan for basketball. Pele for
soccer. Ali for boxing. Einstein for physics. Beethoven for composers. Kant for
philosophy. Result: 49 of 93 GOATs born in even decades. That is 52.7% against an
expected 51.4%. A coin flip.

I also tested my sharpest claim, that the effect grows as you climb from top-10
toward top-1 of each field. The observed curve across tiers 10, 5, 4, 3, 2, 1:
51.0%, 49.9%, 50.8%, 49.5%, 50.0%, 52.7%. Flat. The replication dataset wiggles the
other way and is also flat. Full disclosure: one tier in one dataset (top-4 in the
2025 data) touches p = 0.046. That is 1 of 12 uncorrected tests, so one such blip
is expected by pure chance. It does not appear in the primary data, and it fades at
top-1, exactly where the theory needs it to peak. And this whole test is immune to
the era problem, because each GOAT is compared only against their own field's
elite. Jordan gets compared to LeBron and Kareem, not to Kant.

![The GOAT test](../figures/fig9_apex_goats.png)

One more trap worth knowing about. I extended the test to the ancients, because
Newton (1643) and the great religious teachers were part of my original hunch. It
turns out 60% of recorded birth years before 500 CE end in 0, versus 9% in modern
data. Ancient birth years are estimates rounded to round numbers, and a year ending
in 0 always lands in an even decade. So ancient data fakes evidence FOR the theory
mechanically. Taking the recorded years at face value, the apex ancients still split like
coin flips: Muhammad, Aristotle, and Plato odd, Confucius and Luther even. And
most ancient birth years (Moses, the Buddha, Jesus) are tradition or estimates
anyway, so antiquity cannot testify either way.

## What I actually learned

Half of everyone is born in an even decade. Memory keeps the hits and drops Einstein
(1879), Babe Ruth (1895), Kobe (1978), and Brady (1977). Greats do cluster in time,
but they cluster by era, not by decade digit: whole generations get over-canonized
together, in long waves with no alternating rhythm.

And the bigger lesson: I got a publishable-looking p-value in one direction, then a
publishable-looking p-value in the other direction, from the same dataset, before
getting the truth. Both artifacts came from one confound wearing two disguises. If I
had stopped at either point I would have written a confident and wrong blog post.
The pre-registered offset test is what saved me both times.

The theory was fun. The autopsy was better.

Everything is reproducible, from raw downloads to every figure:
**github.com/Sakshyam-Patro/even-decade-theory** (one command: `python run.py`).

---

## X thread version

**Tweet 1**
I spent years believing the GOATs are born in even decades. Jordan 1963, LeBron
1984, Messi 1987, Pele 1940, Napoleon 1769. So I pre-registered a test on 67,198
famous people. The theory died twice before I understood what killed it. 🧵

**Tweet 2**
First result: the opposite. The top-1000 all-time greats are LESS even-decade than
other famous people (51.4% vs 56.0%, p = 0.003). But there are 10 ways to slice
years into alternating decades, and the "effect" slides smoothly across all 10.
That's a trend, not a decade effect.
[attach fig2_offset_test.png]

**Tweet 3**
So I controlled for era. Result flipped: theory CONFIRMED, z = +2.63, p = 0.005.
Then I moved the 20-year comparison windows by exactly 10 years. z = -2.74. Same
data, same test, opposite discovery. One confound, two disguises.
[attach fig4_mirror_artifact.png]

**Tweet 4**
The honest test: absorb the birth-year trend with a smooth curve, then ask if an
even-odd decade signal remains. Odds ratio 0.99 (CI 0.87 to 1.12). Nothing. And at
the very top? The #1 GOAT of each of 93 fields: 49 even, 44 odd. A coin flip.
Jordan says yes, Einstein says no.
[attach fig9_apex_goats.png]

**Tweet 5**
Lessons: half of everyone is born in an even decade, memory keeps the hits and
drops Einstein (1879) and Kobe (1978). I got significant p-values in BOTH directions
before the truth. Pre-registration saved me twice. Full writeup + one-command repro:
[repo link]
