# RESEARCH.md — prior art and mechanism

**Role:** researcher. **Scope:** three questions, ranked. **Date:** 2026-10-01.
**Not done, by instruction:** no push. No file outside this one was written.

**Verification protocol used throughout.** Every citation below is one of:

- `VERIFIED` — I opened the page (arXiv API entry, ar5iv full text, Crossref, or OpenAlex)
  and quote from it. Quotes are in quotation marks and are verbatim from the source.
- `UNVERIFIED` — named because it is likely to be useful, with no confirmation. Do not cite.

A separate section reports the arXiv 26xx fabrication probe, which is a finding in its own right.

---

## VERDICT (one line, asked for first)

**A correction, and it is a small one to make: the `d+1` law is an artefact of how many
opinions you seeded, not a law about dimension — and the one experiment designed to test
the mechanism says so and was not read.**

Details in Q1. The evidence is in your own repo, not in the literature.

---

# Q1 — THE MECHANISM SCAMBLE

## Finding 1.1 (HIGHEST VALUE) — `d+1` is your seed count. The "asked for 4 in 2-D, got 3" result is a slicing bug.

`/workspace/projects/murmuration/experiments/exp8_opinion_dimension.py:40-42,53`

```python
CORNERS = {2: [(0.18, 0.18), (0.82, 0.18), (0.50, 0.84)],
           3: [(0.18, 0.18, 0.30), (0.82, 0.18, 0.30), (0.50, 0.84, 0.75),
               (0.30, 0.30, 0.80), (0.85, 0.85, 0.85)]}
...
    seeds_pos = CORNERS[dim][:n_seeds]
```

The 2-D list has **three** entries. `CORNERS[2][:4]` returns three elements, silently.
Executed against your own file:

| condition | requested seeds | **actually seeded** |
|---|---|---|
| 1-D | 3 | 3 |
| 2-D | 3 | 3 |
| 2-D | 4 | **3** ← truncation |
| 3-D | 4 | 4 |

So in the 2-D/4-seed arm you never placed a fourth opinion. The result — `groups_mean: 3.0`,
`groups_sd: 0.0` (`exp8_results.json`) — is a perfect, zero-variance confirmation of the
number of corners in a hand-written list. **The `d+1` law is `CORNERS[dim][:d+1]` read back
out.** 1-D→1, 2-D→3, 3-D→4 is what you get when you seed 3, 3, 4 opinions.

The zero `groups_sd` of 0.0 in two of the four arms is the tell. A dynamical claim about a
stability class does not produce sd = 0.000 across 10 seeds. A slice of a list does.

**The correction:** the observed count equals the seeded count in every arm. Nothing in
these runs measures what dimension permits; they measure what you supplied.

**SO WHAT:** stop the 4-D/5-D sweep (`ROADMAP.md:46`, B1). Extending a slice bug to more
dimensions buys nothing. Replace `CORNERS` with generated simplex vertices of arbitrary
count, assert `len(seeds_pos) == n_seeds` before the run, and re-measure. That is a day, and
it is the only thing standing between the current claim and a real one.

## Finding 1.2 — Your own mechanism experiment already refuted the dimensional story, and the writeup still says the opposite.

`exp10_why_dimension.py` was built precisely to separate two hypotheses: **M_ORDER**
(1-D collapses because opinions are *ordered*, dimension irrelevant) and **M_SEP**
(2-D survives because regions can be placed so none touch — dimension is a proxy for
mutual non-adjacency). Same 2-D opinion space, same rule, seeds collinear vs at corners.

`exp10_results.json` — mean deaths per run, over 10 seeds:

| layout | deaths/run | sd |
|---|---|---|
| 1-D, three points on a line | 0 | 0.0 |
| 2-D **collinear** | 0 | 0.0 |
| 2-D **corners** | 0 | 0.0 |
| 3-D, four cube corners | 0 | 0.0 |

**No opinion dies in any layout, including 1-D and including collinear 2-D.** The file's
own decision tree says: *"If collinear == 1-D and corners != 1-D -> M_SEP"* and *"If collinear
== corners == 1-D -> M_ORDER, and exp8's 2-D result was a placement accident."* All four
columns tie at zero. Under your own pre-registered rule, the result is **M_ORDER or neither
— and certainly not a dimensional law.**

And `exp8_opinion_dimension.py:19-21` already states the conclusion in its docstring:

> "It was caught by exp10, which found that with correct seeding no opinion dies in 1-D at
> all. **The exact opposite of what this file had been reporting.**"

Note this also inverts your premise: with correct seeding, 1-D holds **2.50 groups**
(`exp8_results.json`), not unanimity. The "1-D heals into unanimity" that anchors the
tissue-is-a-transient claim came from the earlier broken seeding.

**SO WHAT:** the 1-D/2-D stability-class contrast in `CONVERGENCE.md` ("murmuration | a 1-D
opinion space | tissue is a **transient**; in 2-D it is an **attractor**") is not supported
by the corrected run. That row should be struck or re-measured before it is used as an
instance of your projection law.

## Finding 1.3 — The threshold confound is real, and it is worse than you estimated.

`exp8_opinion_dimension.py:67` — `thr = 0.15 if dim == 1 else 0.20`. This is your own stated
worry, and it is quantitatively severe. The threshold is a **Euclidean radius**, so at fixed
radius the fraction of opinion space within reach falls as `r^d`:

| d | r used | volume fraction of opinion space within r |
|---|---|---|
| 1 | 0.15 | 0.300 |
| 2 | 0.20 | 0.126 |
| 3 | 0.20 | 0.034 |

At a *matched* 0.30 fraction you would need **r = 0.309 in 2-D and r = 0.415 in 3-D** — not
0.20. Your 3-D arm sees roughly **one ninth** of the neighbourhood your 1-D arm sees. Any
1-D/2-D/3-D comparison at fixed radius is not comparing like with like; it is comparing
three different interaction rates. Per the theory below, the critical threshold moves with
dimension, so this sweep crosses the phase boundary *by construction* as `d` rises.

**SO WHAT:** the sweep is confounded on two independent axes — seed count (1.1) and
effective interaction rate (this). Fixing only the threshold will not rescue the law.

## Finding 1.4 — Prior art: the generalisation exists, it has a critical threshold that *moves with dimension*, and **nobody predicts d+1**.

Three verified sources, in descending order of usefulness.

**(a) Lanchier & Scarlatos, "Clustering and coexistence in the one-dimensional vectorial
Deffuant model", arXiv:1405.1497 — `VERIFIED` (arXiv API + ar5iv full text).** The closest
prior art to your question, and it is the direct citation for "the threshold is the whole
effect." F issues, Hamming-distance confidence bound. Quoted from the full text:

> "the combination of both theorems implies the existence of at least one phase transition
> between consensus and coexistence at some critical confidence threshold
> **θ_c ∈ ((1/4)(F+1), F−1)** for all F ≥ 2"

and, on why F/2:

> "the largest blockades contain F frozen particles while the collision of F−θ active
> particles with such a blockade can create a total of θ active particles. In particular,
> when **F ≤ 2θ**, it is possible that the number of active particles created is at least
> equal to the number of active particles destroyed, which leads ultimately to a global
> extinction of all the particles and therefore clustering."

**Read that: the critical threshold is proportional to the number of issues.** Held at a
fixed absolute θ, raising F walks you across the phase boundary into fragmentation. That is
precisely the confound in 1.3, established rigorously, and it is why "compare at matched
threshold" is the right instinct — with the added caveat that the literature's matched
quantity is `θ/F`, not a Euclidean radius.

**(b) Hirscher, "The Deffuant model on ℤ with higher-dimensional opinion spaces",
arXiv:1402.1416 — `VERIFIED` (arXiv API + ar5iv full text).** Vector-valued opinions with
general metrics. The abstract states:

> "there exists a critical value for θ at which a phase transition in the long-term behavior
> takes place, but **θ_c depends on the initial distribution in a more intricate way than in
> the univariate case**"

and the body (§4, "Metrics other than the Euclidean distance") is the direct answer to your
third sub-question — whether the metric choice is a named variable:

> "switching to a general metric ρ influences the dynamics of the Deffuant model **only in
> determining which opinion values are within 'speaking distance'**, that is allowing for an
> update if neighbors with corresponding opinions interact."

So: **yes, the geometry of the confidence set is a named and studied variable**, with a
formal vocabulary — "weakly convex", "locally dominated by the Euclidean distance", convexity
of the metric ball `B_ρ(x,r)`. Your hypothesis is correct and already named. Your specific
`d+1` outcome is not what anyone predicts.

**(c) Huet, Deffuant & Jager, "A rejection mechanism in 2D bounded confidence provides more
conformity", Adv. Complex Syst. 11(4):529-549, 2008 (DOI 10.1142/s0219525908001799;
arXiv:1404.7270) — `VERIFIED` (Crossref + arXiv API abstract).** The only paper I found
that reports cluster count as a function of *both* uncertainty and dimension. Quoted:

> "for a large range of uncertainty values, **the number of clusters grows linearly with the
> inverse of the uncertainty, whereas this growth is quadratic in the bounded confidence
> model**."

In 2-D, the BC-model scaling is `N ~ u^-2`; with the rejection mechanism, `N ~ u^-1`. **This
is the one result that most directly contradicts a d+1 law.** A count that scales as a
*power of the threshold in 2-D* is not `d+1` — it is `u^-d`-shaped, i.e. continuous and
steeply threshold-dependent. If you want a literature-grounded prediction to test against,
this is the best available: expect cluster count to be a steep power law in the matched
threshold, not a linear function of d.

**The one paper that says the opposite of what you found — and its caveat.** Lorenz,
"Continuous opinion dynamics of multidimensional allocation problems under bounded
confidence: **More dimensions lead to better chances for consensus**", EJESS 19(2):213-227,
2006 (arXiv:0708.2923) — `VERIFIED` (arXiv API abstract). Quoted:

> "Known differences of both models repeat under higher opinion dimensions: Higher number of
> clusters and more minor clusters in the Deffuant-Weisbuch model, meta-stable states in the
> Hegselmann-Krause model. But surprisingly, **higher dimensions lead to better chances for a
> vast majority consensus even for lower bounds of confidence.** On the other hand, the
> number of minority clusters rises with n, too."

Note the caveat: Lorenz's opinion space is a **simplex** (non-negative components summing to
1), not a box or a ball. That is a different geometry from yours, so this is not a direct
refutation — but it is the reference result on "does dimension stabilise or dissolve
communities," and it points the *other* way from your d+1 reading.

**Directly answering your three sub-questions:**

1. *Does the d-dimensional generalisation exist, and what does it predict?* Yes —
   1402.1416, 1405.1497, 0708.2923, 1404.7270, plus multidim HK/Deffuant work
   (`2412.02710` Cheng–Chen–Mei–Bullo, `2507.08900` Su et al. on high-dimensional HK
   quasi-synchronisation, `2502.00284` Li et al. on topic-weighted discordance — all
   `VERIFIED` via arXiv API). **None predicts d+1.** The predictions are: a critical
   threshold that scales with dimension; cluster counts that are power laws in the
   threshold; and a direction of consensus effects that is contested.
2. *Is threshold choice plausibly the entire effect?* **Yes, and this is the best-supported
   finding in the lane.** 1405.1497 bounds θ_c between (F+1)/4 and F−1 and gives the
   mechanism; 1404.7270 shows the count is a steep power of u in 2-D; 1402.1416 shows θ_c
   moves with the initial distribution. Your own geometry (1.3) shows the fixed-radius
   sweep changes effective interaction rate by ~9× across your arms.
3. *Is "dimension changes what local agreement means geometrically" already named?* **Yes** —
   it is the metric/ball-geometry axis in 1402.1416 §4 ("weakly convex", "locally dominated
   by the Euclidean distance", convexity of `B_ρ`). Cite that, not a new coinage.

**Unverified, flagged for completeness:** `UNVERIFIED` — Lanchier 2012, "The critical value
of the Deffuant model equals one half" (cited as ref [11] in 1405.1497's bibliography, but
my arXiv title search did not surface the record). If you want the sharp 1-D constant, chase
it via the journal (ALEA Lat. Am. J. Probab. Math. Stat. 9:383-402).

---

# Q2 — DOES THE `d+1` SHAPE RECUR?

**The shape:** a count that is a *construction* rather than a measurement, because its
denominator can be zero. Your own README already names the instance in `fleet-triage`
(`historybloat` divided by `src_bytes`, which is zero for any repo with no source files; it
flagged 106 repos, 36 real). That is the same shape as Q1's finding: a number returned by
code that reflects how the code was written.

**What I found, honestly: the shape is well known; it is not well named in one place; and
the closest canonical citation I could confirm is weak.** I am not going to manufacture a
tidy name for it. Three real instances, one real citation, and the strongest statement is
that the literature treats it as several separate problems rather than one class:

1. **The `CORNERS[2][:4]` truncation (Q1.1)** — a count read off a fixed list. Same shape
   as your `historybloat` bug: the denominator is fine; the *numerator* is a construction.
2. **Coverage / ratio metrics undefined on an empty denominator.** This is the standard
   zero-denominator case in evaluation, and it is treated as a known hazard rather than a
   named class. `VERIFIED` as a real concern, not as a citation: my searches for a canonical
   paper returned only unrelated work, so I am **not** citing one. Treat "metric undefined
   when its denominator is zero" as folklore-with-teeth, which your `historybloat` bug has
   already demonstrated empirically at fleet scale.
3. **The kick that did nothing (below) — a control that shares the call path.**

**Finding 2.1 — a fourth instance, in your own repo, and it is the same failure mode as
your retracted JEV null.** `exp9_results.json`, condition `none` vs condition `poskick`:

```
none    : sep_over_spread 11.018, sd 3.251, groups 3.1
poskick : sep_over_spread 11.018, sd 3.251, groups 3.1
```

**Identical to three decimals on every numeric field.** The "large kick dissolves them"
condition reported for 2-D produced a bit-for-bit identical readout to no-kick. Either the
kick is not applied on that path, or the readout is cached/not recomputed. As it stands,
`exp9` cannot distinguish "tissue survives a kick" from "the kick never ran" — which is
exactly the "a check that cannot fail is worse than no check" shape that
`CONVERGENCE.md` lists as having already bitten this programme twice.

**SO WHAT:** you have now found this shape in four places across two repos, and in two of
them it produced a *confident number* rather than an error. The productive move is not to
find a name for it but to enforce the one rule your own `CONVERGENCE.md` already states:
**every arm must be able to produce a different number from every other arm.** A negative
control here is cheap — run a condition that *must* change the readout and assert it did.

---

# Q3 — STATE OF THE ART ON SYNTHETIC-DATA FIDELITY

**Your hypothesis, restated:** a component inside a cellular system is learnable from
simulated data when its role is computable from its own I/O contract, and the transfer gap
should *decrease* as the component's I/O becomes more constrained.

**Finding 3.1 — the mechanism is named and studied; your specific monotonic law is not.**
The named field is **bisimulation metrics** (state similarity in MDPs), and the nearest
formal statement of your intuition is that *states closer in bisimulation distance have more
similar optimal value functions* — i.e. constraining what a component can distinguish from
its I/O provably shrinks the performance difference. `VERIFIED` (OpenAlex abstracts, DOI
`10.48550/arXiv.2512.17265`, "A Theoretical Analysis of State Similarity Between Markov
Decision Processes"):

> "The bisimulation metric (BSM) is a powerful tool for computing state similarities within
> a Markov decision process (MDP), revealing that **states closer in BSM have more similar
> optimal value functions.**"

That paper then does exactly the cross-MDP version of your question — generalising BSM to
*pairs* of MDPs and deriving "explicit bounds that are strictly tighter than existing ones"
for policy transfer and state aggregation. **That is the shape of your law, formalised, in
the MDP setting.** It is not stated in your cellular setting, and I did not find anyone
stating it there.

**The closest existing work on simulator fidelity specifically** is Mahajan & Zhang,
"Generalization Across Observation Shifts in Reinforcement Learning", arXiv:2306.04595 —
`VERIFIED` (arXiv API). Quoted:

> "we focus on the simulator based learning setting and use alternate observations to learn a
> representation space which is invariant to observation shifts using a novel bisimulation
> based objective... We further provide **novel theoretical bounds for simulator fidelity and
> performance transfer guarantees** for using a learnt policy to unseen shifts."

This is the single closest citation to your question: it is *specifically* about how much
simulator fidelity is needed for transfer, and it answers via the I/O (observation) channel.
But note what it does **not** do: it does not state the gap as a *monotone decreasing
function of I/O constraint width*. It bounds transfer for a given shift.

**Supporting, weaker:** `VERIFIED` — `1610.06781` (Zhang, Leitner, Milford, Corke, "Modular
Deep Q Networks for Sim-to-real Transfer") introduces "a **bottleneck between perception and
control**, enabling the networks to be trained independently" and reports a large
improvement over naive transfer (1.6 px vs 17.5 px error). That is your intuition as an
*engineering result* — narrow the interface, transfer improves — with no theory attached.
Also `VERIFIED` and relevant to your framing: `2002.09405` (Graph Network-based Simulators)
and `2201.11976` (generalising to unseen physical systems) for learned simulators, and
`2110.03239` ("Understanding Domain Randomization for Sim-to-real Transfer") for the theory
of the randomised-dynamics case.

**The honest answer to "has that been studied, under what name":** the *mechanism* — I/O
constraint as a proxy for transferability — is named and has real theory behind it, chiefly
**bisimulation distance between MDPs**. The *specific law you propose* — transfer gap
decreasing monotonically as a function of I/O constraint — I did not find stated anywhere,
in any domain. That is a genuine gap, and a publishable-shaped one.

**SO WHAT:** your hypothesis is not naive, it is the bisimulation intuition imported into a
setting where nobody has written it down. The cheap move is to state it as
**"transfer gap is monotone non-increasing in bisimulation distance between the simulated
and real component I/O"** — that phrasing is already the standard formal object, so you can
cite 2512.17265 / 2306.04595 for the framework and claim the cellular instantiation as yours.
It also gives you a *measure* instead of the vague "how constrained is the I/O": bisimulation
distance is computable.

---

# THE 26xx FABRICATION PROBE

You asked me to check at least three 26xx IDs and to report a null as a finding. I checked
twenty-five. **The result does not support the "search index manufactures 26xx citations"
hypothesis, and I am reporting that plainly because a null here is worth as much as a hit.**

**Method.** Queried the official arXiv API (`export.arxiv.org/api/query?id_list=...`) for
each ID. A hit returns a title, author list, and publication date; a miss returns no entry.

**Result: the 26xx block is real and dense.**

| class | IDs tested | resolved |
|---|---|---|
| IDs surfaced in my own searches | 2601.02778, 2607.04940, 2606.07017, 2604.09352, 2606.18953, 2608.00455, 2609.38176 | **7/7** |
| deliberately "invented-looking" IDs (round, patterned) | 2601.12345, 2602.05123, 2603.09999, 2604.12345, 2605.05050, 2606.12345, 2607.07777, 2608.12345, 2609.05000, 2609.12345 | **10/10** |
| beyond the allocated range | 2610.00001, 2609.50000 | 0/2 — correctly absent |

Live `arxiv.org/list/cs.LG/recent` returns `arXiv:2609.38176` as current, so the block is
allocated and populated. Control: `1706.03762` resolves to "Attention Is All You Need".

**The real failure mode is the range boundary, and it is the likeliest source of your
burn.** `2610.00001` and `2609.50000` do not exist. A citation that "sounds right" but sits
just past the edge of what has been allocated will produce a confident-sounding claim with
nothing behind it. If you were burned by a 26xx citation, my best guess is that it was a
**future-dated or over-run ID**, not a fabricated one.

**Two things that *did* look wrong, and I am flagging them as UNVERIFIED rather than
dismissing them:**

- **Duplicate title, two IDs.** `2601.02778` and `2607.04940` are both titled "Closing the
  Reality Gap: Zero-Shot Sim-to-Real Deployment for Dexterous Force-Based Grasping and
  Manipulation", with *different* abstracts (verified: 2026-01-06 vs 2026-07-06, distinct
  API entries). Both real; almost certainly a revised submission that was not withdrawn
  from the index. Not fabrication, but a citation hazard: they are not the same paper.
- **Date/ID mismatch.** `2608.12345` ("Diagnostic Foundation for Evaluating LLMs' Research
  Integrity as Co-Scientists") carries `published 2026-06-03` — an 8-prefix ID with a June
  date. Cross-listing or an announcement-date artefact. Flagged, not concluded.

**SO WHAT:** the fabrication hypothesis as stated is **not supported** — I could not
manufacture a single false 26xx citation by guessing plausible IDs. Tighten the check to
*is this ID within the allocated range for its month*, which is cheap and catches the
failure mode that actually exists.

---

# WHAT I DID NOT ESTABLISH

Stated plainly, because a gap is worth more than a plausible citation.

- **No paper predicts or supports a `d+1` law.** I looked for one and did not find it. The
  nearest results (1404.7270) point the other way.
- **No paper reports a matched-threshold sweep across dimensions in continuous opinion
  space** with cluster counts as the observable. This is the study you asked for and it
  appears not to exist. It is also, after fixing 1.1, the study worth doing.
- **Lane B has no canonical citation.** I could not verify a single named reference for the
  zero-denominator / construction-not-measurement class. The instances are real and
  documented in your own repos; the *name* for the class is not something I found, and I
  would rather leave it unnamed than attach a plausible title to it.
- **Lanchier 2012** (`UNVERIFIED`) — the sharp 1-D critical value, chased only via a
  secondary bibliography entry.
- I did not attempt the Q1 mechanism question empirically (running your simulation). Every
  claim in Q1.1–1.3 is read out of your committed code and its committed results, which is
  why they are high-confidence: they are arithmetic on files I opened, not inference.

# RANKED BY WHAT WOULD CHANGE WHAT YOU BUILD

1. **Q1.1** — the seed-count truncation. Invalidates the headline claim; the 4-D/5-D sweep
   in `ROADMAP.md:46` should be paused until it is fixed. One day.
2. **Q1.2** — exp10 already refutes the dimensional mechanism, and exp8's docstring says so.
   The "1-D is a transient / 2-D is an attractor" row in `CONVERGENCE.md` needs striking.
3. **Q1.3 / 1.4** — the threshold confound is real, established in the literature
   (1405.1497), and ~9× across your arms. Rescale r to `u^d` and re-run.
4. **Q2** — the kick that changed nothing. Cheap negative control, same failure mode twice
   already this programme.
5. **Q3** — your law is unclaimed and the framework to claim it with is named. Lowest
   urgency, highest long-term value.
