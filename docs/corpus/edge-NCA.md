# EDGE SCOUT 1 — learned cellular automata and neural substrates

**Scout:** General (edge-NCA) · **Date:** 2026-10-01 · **Question:** is the Quilt doctrine
"the cell is the irreducible unit, a scar; the substrate is grown, not designed" (a) already
established elsewhere, or (b) false?

**Verdict up front: (b) — and the failure is sharper than "not established".** The
learned-CA literature does not produce cells at all. It produces **a shared update rule plus
a thresholded view of a continuous state tensor**. Where it does produce persistent entities
(ALife branch: Flow-Lenia, parameter localisation, mass conservation), it gets them by
*hand-injecting a conserved quantity* — i.e. by design. This is evidence **for** the fleet's
position on one axis (nothing in the learned-CA world has a causally load-bearing per-entity
id) and evidence **against** it on another (the CA literature's cell is an *address*, and
the fleet's own cell convention is a *record*; the two are being conflated).

Everything below is either a **primary-source citation with arXiv ID + version + date**, or a
**number I computed on this box** (CPU only, no CUDA anywhere in this report).

---

## 0. METHOD — and a methodology finding that matters more than any result here

The instruction was "re-derive before you read". Good. I did, and the first thing I found was
that **my own recall of arXiv IDs is worthless: 8 of 8 IDs I wrote down from memory were
wrong papers.** Every one of these was fetched, had its `citation_title` read, and rejected:

| ID I recalled | what it actually is (verified via `citation_title`) |
|---|---|
| `2004.06556` → "Emergence of Complex Structure in a Cellular System of Elementary Rules" | *Fundamental relations for the velocity dispersion of stars in the Milky Way* |
| `2012.11317` → Gilpin, "Self-organizing criticality in NCA" | *Two geometric proofs of the classification of algebraic supergroups…* |
| `2108.05179` → Distelgo, "Growing Neural Cellular Automata" | a paper on critical transitions / regime shifts in complex systems |
| `2204.04068` → "Particle Lenia, an Amalgam" | *Declipping of Speech Signals Using Frequency Selective Extrapolation* |
| `1904.10964` → "Towards a differentiable simulator of biological development" | *Master integrals for the NNLO virtual corrections to q̄q→tt̄* |
| `1906.09663` → "Unsupervised Egocentric Spatial Structure…" | *Rejuvenation and Shear-Banding in model amorphous solids* |
| `2305.10757` → "Diversity and Similarity of NCA" | *Temporal and Latitudinal Variation in Penumbra-Umbra Ratios of the Sunspots* |
| `2310.16032` / `2503.20714` → I-JEPA / Genie 2 | *Physics of (good) LDPC Codes* / *force feedback in XR robot datagloves* |

Tooling notes, for whoever repeats this: the arXiv **API ignores quoted multi-word phrases**
(returns generic cellular-automata results); the arXiv **search UI rate-limits to HTTP 400**
after a handful of queries; Semantic Scholar returned empty result sets for every query.
What *did* work reliably: `arxiv.org/abs/<id>` (title + date), `arxiv.org/html/<id>` or
`ar5iv…/html/<id>` (full text), and **primary source code on GitHub**.

**Rule this implies for the fleet: an arXiv ID in a report is not a citation until the title
on the page has been read back.** A citation whose title you have not verified is a rumour.

---

## 1. WHAT A TYPICAL NCA ACTUALLY IS (learned vs hand-designed)

**Primary source for the architecture: `arXiv:2103.08737v1`, 2021-03-15, "Growing 3D
Artefacts and Functional Machines with Neural Cellular Automata".** Verbatim from its text:

> "Every cell within the CA encodes cell state information using a continuous size-16 state
> vector, representing the RGB values, whether a cell is alive, and hidden channels for
> simulating local morphogens concentrations. Sobel filters estimate the partial derivatives
> of cell state channels, which are then concatenated with individual cell state vectors to
> form the 'perception vector' of the cell. This perception is fed into a series of neural
> layers to evoke a potential update of the cell. Sharing the neural network layers throughout
> the CA enforces a uni[formity]…"

Also from it: the initial state is "**a single living cell**", updates are stochastic
per cell, and a **sample pool of size 32** is required to stop catastrophic forgetting.

`arXiv:2607.15726v2` (2026-07-22) restates the same architecture in the present tense:

> "each cell carries a 16-dimensional state vector, of which the first four channels
> correspond to RGBA values and the remaining twelve serve as hidden channels. At each time
> step, every cell perceives its local neighbourhood via fixed filters (identity and Sobel
> filters) and updates its state through a small neural network shared across all cells. A
> stochastic cell update mask is applied at each step…"

and `arXiv:2607.12403v1` (2026-07-14) adds what the hidden channels are allowed to be:

> "the remaining 12 channels are hidden state channels with **no predefined semantics, which
> the model is free to use as an internal communication and memory substrate**."

### The decomposition, stated precisely

An NCA is `A ← F(A)` iterated T times, where `F` is one shared MLP applied per cell to a
fixed 3×3 Sobel perception. Two consequences that the fleet should internalise:

- **There is exactly one learned object per substrate, and zero per cell.** The cell is a
  coordinate `(i,j)` carrying a 16-vector. Its "parameters" are the shared MLP's. A cell is
  not a parameter and does not have one.
- **The thing that reproduces the target is not the rule; it is the T-step unrolled program.**
  Per-step the rule is 3×3 (radius 1). The *program* has radius ≈ T.

### My measurement of the census (CPU, torch 2.14.1+cpu, 1 thread, no CUDA)

Scaled-down but architecture-faithful: 12×12 grid, 16 channels, 48-feature Sobel perception,
shared MLP 48→24→24→24→16, last layer zero-initialised (identity at init), stochastic
per-cell update mask at rate 0.5, 24 steps, **one living cell planted at the centre**.
2000 Adam iterations, 112 s. Final loss **0.0148** (frozen mask schedule) against a
**control "do nothing" of 0.1503** — the substrate reproduces a hand-drawn target 10× better
than emitting its own seed.

| quantity | value |
|---|---|
| learned parameters (the entire learned content) | **2 776** |
| hand-designed target image | 2 304 values |
| hand-designed structural constants | 15 items, incl. 27 Sobel coefficients, seed values, step count, mask rate, alive-channel index, zero-init |

Ratio learned-params : target-pixels = **1 : 0.83**. The learned rule is *smaller than the
specification of what it is supposed to produce*.

### Mutation tests (batch 16, stochastic mask on) — the decisive table

| condition | loss | vs. trained |
|---|---|---|
| **CONTROL: do nothing (emit the single planted cell)** | 0.15025 | 8.3× worse |
| trained, full architecture | **0.01799** | 1.0× |
| **ALL learned weights zeroed (identity rule)** | **0.15025** | **exactly the control** |
| **NO SEED (start from an empty grid)** | **0.15164** | **≈ the control** |
| seed planted at corner (2,2) instead of the centre | 0.19269 | **10.7× worse** |
| whole grid alive at t=0 | 0.34822 | 19× worse |
| no stochastic per-cell mask | 0.12386 | 6.9× worse |
| alive-masking on (dead cells frozen) | 0.14966 | 8.3× worse |

Three results here, in order of how much they should worry the fleet:

1. **Zeroing every learned weight returns the loss to the control, to five decimal places.**
   The hand-designed scaffold — the 3×3 Sobel filters, the seed, the mask, the step count,
   the zero-init — contributes *nothing* on its own. The claim "the substrate is grown, not
   designed" is **half true**: the rule is 100% grown, and 100% of the behaviour is in it.
2. **The substrate cannot start itself.** Remove the hand-planted single cell and the
   learned substrate emits nothing (0.1516 ≈ do-nothing 0.1503). "Cells that grow
   themselves" is, in the primary source's own construction, **cells that are grown from a
   cell someone planted.** The seed is a hand-designed constant at the centre of the grid.
3. **The learned rule memorised the seed's position.** Plant the same seed one corner away
   and the error goes up 10.7×. The substrate is not translation-invariant about its own
   seed: the designer's choice of *where* to plant is load-bearing and is baked into the
   weights. This is evidence **for** the fleet's position-dependence doctrine and against the
   "self-organising" reading.

---

## 2. DOES THE LOCAL-RULE / GLOBAL-OBJECTIVE DECOMPOSITION SURVIVE? (No.)

Two independent measurements, mine and the literature's, agree.

**Mine — halo truncation** (zero the state outside radius *k* of the seed at every step):

| k | 0 | 1 | 2 | 3 | 4 | 6 | 8 | 12 |
|---|---|---|---|---|---|---|---|---|
| loss | 0.1497 | 0.1387 | 0.1163 | 0.0725 | 0.0302 | 0.01487 | 0.01478 | 0.01478 |
| × untruncated | 1012% | 938% | 787% | 491% | 204% | 100.6% | 100% | 100% |

**Deleting the halo to radius 4 on a 12-cell grid more than doubles the error; full
behaviour is only recovered at radius 6–8, i.e. more than half the field.** Cumulative
influence of the initial state on the final image, by radius: 2.1% (r0), 8.9% (r1), 20.4%
(r2), 44.3% (r3), 67.7% (r4), 85.4% (r5), 95.9% (r6), 99.7% (r7) — so 50% of the influence
sits within radius 4, and 95% needs radius 6.

**The literature's, and it is stronger than mine** — `arXiv:2607.12403v1` (2026-07-14),
"Structured Fluctuations and the Information Dynamics of Self-Maintenance in Growing Neural
Cellular Automata":

> "Suppressing distributed small-magnitude updates outside a permissive radius encompassing
> approximately **74% of alive cells** significantly impairs recovery, suggesting that
> micro-fluctuation-related update activity contributes to repair at a **near-global scale**."

Their substrate is 72×72. **Repair in a learned NCA is a near-global operation.** There is a
"local update rule" in the formal sense and no locality in the functional sense. Anyone
claiming a learned CA is interpretable *cell-by-cell* is reading the 3×3 filter, not the
computation.

---

## 3. DO LEARNED CELLS STAY INTERPRETABLE? — the honest answer, and it is a *negative*

**The 2026 state of the art is a paper whose central move is to *impose* cell types on a
continuum.** `arXiv:2607.15726v2` (2026-07-22), Sato, Masumori & Ikegami, "Transient State
Reorganization and Cell Differentiation in the Developmental Dynamics of Growing Neural
Cellular Automata". Its abstract concedes the state of the field:

> "Growing Neural Cellular Automata (GNCA) develop complex morphologies from a single seed
> cell through shared local rules, **yet the internal dynamics of this process remain poorly
> understood**."

Its method: build an ε-nearest-neighbour graph over L2-normalised 16-dim cell-state vectors,
run community detection, and

> "community extraction was applied to identify communities, **which are interpreted as cell
> types**."

And the result that should stop the fleet cold:

> "The number of detected communities decreased monotonically with ε, from **over 1,500 at
> ε=0.005 to fewer than 50 at ε=0.2**."

**On the same trained model, the "cell census" spans 1,500 → <50 — a factor of 30 — purely as
a function of the analyst's distance threshold.** The paper is admirably honest about this
("a fixed ε threshold may resolve communities at different effective granularities"), and its
geometric finding explains why: cell states diversify **"within a low-dimensional, smooth
manifold"**. A smooth manifold has no cells in it until you choose a resolution. The fleet's
"cell" is a resolution.

**My own measurement finds the same thing in both families, independently:**

*Lenia* — Orbium unicaudatus, the flagship creature, field decoded from
`Chakazul/Lenia` `animals.json` (catalogue entry `O2u`; params `{R:13, T:10, b:'1', m:0.15,
s:0.015, kn:1, gn:1}`):

| occupancy threshold | 0.01 | 0.05 | 0.10 | 0.20 | 0.50 |
|---|---|---|---|---|---|
| "cells" at t=0 | **220** | 206 | 184 | 135 | **57** |

**The same creature has 220 cells or 57 cells depending on a threshold nobody argues about.**
Over 400 steps at threshold 0.10 the count takes 18 distinct values (range 163–184,
σ = 1.7%): it is not an integer invariant. Chan's own catalogue entry for this animal stores
the payload in a field literally named **`cells`**, and that field contains a run-length-coded
**continuous 20×20 raster** — 222 sites above zero, mass 76.86 — with **no cell
decomposition anywhere in it**. The flagship dataset of the flagship Lenia paper does not
contain cells.

*NCA* — my trained substrate: alive channel takes **exactly 2 distinct values** {0,1} (a
2-symbol Life-like alphabet); RGB occupancy is 67 / 64 / 57 / 55 cells at thresholds
0.05 / 0.1 / 0.2 / 0.4 against a target of 52; **144 sites, only 48 distinct 3×3
neighbourhood states**; and over the 64 live cells the update-increment covariance has a top
eigenvalue holding **69.4%** of the variance with the top three holding **100%** — i.e. the
live cells have essentially *one* update behaviour. The "cells" are tokens of a small
alphabet stamped onto a grid, not individually-specified entities.

**Verdict for Q3: negative, and it is the most useful thing in this report.** The learned-CA
literature does not deliver interpretable cells. It delivers an interpretable *rule* (16
weights, which nobody reads) applied to a *continuous* state whose "cells" are a
resolution-dependent thresholding. The 2026 papers are honest about the gap; the 2021–2023
papers generally are not.

---

## 4. IS A CELL A SCAR? — the two experiments that answer the doctrine's own question

The doctrine says a cell is a **scar**: a persistent, causally load-bearing record of what
happened. Testable version: *write a mark into one cell; where does the mark go?* Run
identically on both families. CPU, verified port.

**Lenia (Orbium, gliding at 0.148 cells/step).** Write a Gaussian mark (amp 0.05, σ = 0.8
cells) into one lattice site at t = 0:

| t | deviation mass | deviation-CM moved | organism moved | deviation at the mark's own site |
|---|---|---|---|---|
| 1 | 0.499 | 1.62 | 0.69 | **0.00000** |
| 10 | 0.575 | 6.51 | 6.50 | 0.00146 |
| 100 | 1.608 | **62.16** | **62.71** | **0.00000** |

**At t = 100 the mark's centre of mass has travelled 62.16 cells while the organism travelled
62.71 — a ratio of 0.991. The mark is carried by the pattern, at the pattern's own speed, and
the site it was written into forgets it within 2 steps (deviation exactly 0.00000).** In a
Lenia glider the *address* looks persistent — a fixed site stays inside the organism for
~150 consecutive steps — but the *material* is not: anything you write into a cell is picked
up and carried away by the pattern. **The apparent cell-persistence is an artefact of the
address.** A Lenia cell is a co-moving phase of a wave, not a scar.

**NCA.** A mark written into one cell at t = 11 survives at its own site for 2 steps and is
then **erased** (deviation at the mark = 0 by t = 16, having spread ~0.8 cells). The NCA's
memory depth is one step, and `arXiv:2607.12403v1` independently confirms this formally: it
computes transfer entropy between neighbouring cells with **history length k = 1**.

**So: neither family has a scar.** Lenia transports the mark (the site is not the entity);
the NCA destroys it (the site is not a memory). The formal reason is the same in both: the
update is `A ← F(A)` with `F` shift-commuting and memoryless, so **a cell's content is fully
recomputed from its neighbourhood every tick and is never carried by the cell itself.**

The one place the literature *does* get persistence is instructive, and it is in §6.

---

## 5. LENIA: WHAT LEARNING ADDS, AND WHERE HAND-TUNING STILL WINS

`arXiv:1812.05433v3` (2018-12-13, Complex Systems): Lenia is "a two-dimensional cellular
automaton with **continuous space-time-state** and generalized local rule"; "more than 400
species in 18 families have been identified, **many discovered via interactive evolutionary
computation**". `arXiv:2005.03742v1` (2020-05-07): semi-automatic search (genetic
algorithms) found "self-replication, emission, growth by ingestion … and … 'virtual
eukaryotes' that possess internal division of labor and type differentiation".

**What the learned-parameter literature adds:** gradient descent on the rule instead of GA
search. `arXiv:2505.13058v2` (2025-05-19, GECCO '25 Companion) trains toward a *continuous
universal* CA by gradient descent — universality, which Lenia's hand-tuning cannot reach at
all. `arXiv:2601.01932v1` (2026-01-05) then attacks the hand-tuning problem from the
structure side: it classifies Lenia into four dynamical classes and finds the parameter space
is **fractal** (building on Yevenko 2024, "Classifying the fractal parameter space of the
lenia orbium"). Learning adds *reach*; it does not add *legibility*.

**Where hand-tuning still wins — and my own number, which corrects a common overstatement.**
The received wisdom is "Lenia is a needle". My 891-probe scan around the published Orbium
parameters (δm ∈ ±0.030 = ±20% of m, δs ∈ ±0.006 = ±40% of s, 250 steps each):

- survived (mass within ±15%, ≥ half the cells retained): **378/891 = 42%**
- glided (survived and |v| > 0.05 cells/step): **351/891 = 39%**
- and of those that survive, 93% also glide

**So the basin is wide, not a needle.** Hand-tuning wins not because the creature is fragile
but because of what the primary source says about *finding* it:
`arXiv:2212.07906v2` (Flow-Lenia, 2023-03-24) — "those creatures are found in **only a small
subspace of the Lenia parameter space and are not trivial to discover**, necessitating
advanced search algorithms". **Finding is hard; staying is easy.** And staying is what
interpretability is made of: a hand-tuned Orbium is a *named, plottable, publishable object*
with a stable code (`O2u`) in a shared catalogue, and a gradient-trained Lenia rule is a
vector. Reproducibility and addressability — the two things a scar is for — are exactly what
learning gives up.

---

## 6. THE BEST CASE *FOR* LEARNED CELLS — AND WHY IT IS A DESIGN CHOICE

I am required to find the strongest opposition, and here it is, stated at full strength.

The ALife branch **does** produce entities with persistence, and it does it by an explicit
mechanism. Flow-Lenia (`arXiv:2212.07906v2`): the failure mode of plain Lenia is stated in
their own abstract — "each of these creatures exist only in worlds governed by specific
update rules and thus cannot int[eract]" — and the fix is named:

> "We propose in this work a mass-conservat[ing] … **adding mass conservation is a key
> ingredient** to address the aforementioned challenges. Such a constraint could (i) constrain
> emerging creatures to spatially localized ones, (ii) allow for the design of multi-species
> simulations…"

plus **parameter localisation** (a per-region field of rules). Add a conserved quantity and
you get persistent, interacting, mergeable things. `arXiv:2305.13043v1` (2023-05-22) shows
the same substrate yielding self-replication with "spontaneous, inheritable mutations and
exponential genetic drift … **even when the automaton is deterministic**" — a lineage, from
a rule nobody designed for lineage.

**This is the strongest published support for the cell doctrine, and it is support for the
opposite of what the doctrine says.** Persistent identity in this literature is *injected*:
you hand the substrate a conserved mass, or a localised parameter field, and entities
follow. It is not *grown*. The doctrine says the cell is a scar — an irreducible, not a
parameter. In the only systems where the learned-CA world produces anything scar-like, the
scar is a parameter that someone conserved on purpose.

`arXiv:2205.01681v3` (Growing Isotropic NCA, published 2022-05-03, v3 2022-06-01) and
`arXiv:2604.24990v2` (published 2026-04-27, v2 2026-05-12)
(2026-04-27, review + reference implementation) round out the picture; the latter's own
framing is telling — it opens by noting that after two decades "Cellular Automata have still
been waiting for a substantial breakthrough in scientific applications".

---

## 7. WORLD MODELS: DOES "LEARNING ITS OWN DYNAMICS" DISSOLVE THE CELL, OR SHARPEN IT?

**It sharpens it, but by the opposite mechanism: it *manufactures* the cell.** Verified
primary sources (abstracts, titles and dates read back from the abs pages):

- `arXiv:2402.15391v1`, 2024-02-23, **Genie**: "a spatiotemporal video tokenizer, an
  autoregressive dynamics model, and a simple and scalable latent action model", 11B
  parameters. Its unit is a **token** from a tokenizer — i.e. a cell decomposition produced by
  a *separate learned model*, then handed to the dynamics model as a substrate.
- `arXiv:2301.08243v3` (published 2023-01-19, v3 2023-04-13), **I-JEPA**: predicts in
  representation space, not pixel space.
- `arXiv:2506.09985v1`, 2025-06-11, **V-JEPA 2**: action-free JEPA pre-trained on >1M hours
  of video, then an action-conditioned world model (V-JEPA 2-AC) for planning.
- `arXiv:2411.04983v1`, 2024-11-07, **DINO-WM**: "model visual dynamics **without
  reconstructing the visual world**" by predicting future DINOv2 patch features. Spatial
  patches are carried into the world model as units.

Three properties, all checkable from the architectures, and all of which make a world-model
token *more* cell-like and *less* scar-like than a Quilt cell:

1. **The cell count is set by architecture, not by the substrate.** A 16×16 latent grid is
   256 tokens whether the scene contains one object or forty. There is no population with
   membership events, no births, no deaths — so no census, and nothing to attest to.
2. **The update is global.** A transformer over all tokens with a global receptive field; no
   local shared rule, no 3×3 perception. The "locality" that NCAs at least *formally* have is
   absent by construction.
3. **Token identity is positional and non-persistent.** Identity comes from a positional
   embedding, exactly as an NCA cell's identity comes from its grid coordinate — the same
   address-not-entity situation as §4, only with a learned coordinate system.

**"A model that learns its own dynamics" does not dissolve the cell. It manufactures a cell,
loses the identity, and hands the dynamics to a global attention operator.** The cell
survives as an *artefact of tokenisation* — which is, notably, the same status the Lenia
catalogue's `cells` field has.

---

## 8. THE STRONGEST CASE AGAINST THE DOCTRINE (required, and it is partly self-inflicted)

**8.1 The cell is a naming convention, and the fleet's own substrate breaks on a name.**
From the fleet's corpus scan (`quilt-cell-scout-2026-10-01.md`, verified over 4,891 repos):
the `{id, kind, inputs, params}` record shape is emitted by **three** JS-era repos
(`quilt-nn/src/cellgraph.mjs:12`, `quilt-attention/README.md:11`,
`quilt-ml-recipes/recipes/r2-cellgraph-mlp-training/index.mjs:12`) while the older
BIND/LINK/EFFECT/VIEW/TICK opcode convention — a *different algebra* — is used across ~20 more.
And `substrate-foundation/index.js:5,18` destructures `MERGER` from `@superinstance/opcode-canon`,
which exports `MERGE`; `MERGER` appears in that file only in a comment recording the drift.
**If the cell is the irreducible unit, a one-character rename of an opcode should not be able
to break every substrate that inherits from it. It did.** A unit that fails on a spelling is
a label.

**8.2 Mathematically, a CA cell is an address — by definition, not by neglect.** The standard
object of study in every primary source above is the *rule*: Lenia as "continuous
space-time-state and generalized local rule" (1812.05433), an NCA as "a small neural network
shared across all cells" (2607.15726). A rule is a function on a state space. Cells index
that space. My measurements are the quantitative form of the same point: the flagship Lenia
creature has 220 or 57 cells depending on a threshold (3.9×), and a trained NCA has
1 500-to-<50 possible "cell types" depending on ε (30×). **If the census of a substrate's
cells is a free parameter of the observer, the cell is not an intrinsic unit of that
substrate.**

**8.3 Nothing in the learned-CA world ever reads a cell's identity.** That is the load-bearing
half of the argument and it survives everything I threw at it: perturbation tests (§4) show
that a mark written into a cell is either transported by the pattern (Lenia, ratio 0.991) or
erased (NCA, 0 by t=16); the ALife branch's one success at persistence is mass conservation,
i.e. a hand-added conserved parameter (2212.07906). **A cell whose id is never read is not a
scar; it is a coordinate.** This is the point on which the fleet is *right* and the literature
is *empty*.

**8.4 The strongest attack on 8.1–8.3, which the fleet should take seriously: the doctrine may
be answering a different question, and the comparison is category-confused.** NCA and Lenia
are *dynamical systems*. The Quilt cell is an *accounting primitive* — a row in a witness log
with a stable `id`, a `kind`, `inputs[]`, `params`, a row-level digest, and a `VIEW` opcode
that projects it. A scar is precisely a record whose value is that it is **readable later**.
The learned CA has no "later": its state is overwritten every tick, by design. So nothing in
this report refutes the doctrine — the CA literature simply is not talking about receipts.

**But that rescue is self-defeating, and here is the sharpest thing I can say against the
fleet's own position:** if the cell is only an accounting primitive, then *"the cell is the
irreducible unit"* is false **of the substrate**, and true only **of the record**. The
doctrine's load-bearing sentence conflates two objects that the fleet's own opcode algebra
already separates — `EFFECT` is the dynamics, `VIEW`/`ATTEST` is the record. §4 just proved
that the dynamics half has no cells: a mark in a cell is transported or erased. What survives
§4 is the record half: a stable `id` that a receipt can cite. **The honest doctrine is "the
cell is the irreducible unit of the record, and the substrate is a continuous field that the
record samples."** That is weaker, more defensible, and it is the version I would sign.

---

## 9. WHAT I COULD NOT VERIFY

- **`Particle Lenia, an Amalgam`** (Plantec et al., ALife 2022) — **UNVERIFIABLE**. No arXiv ID
  resolved through any route I have; `2204.04068` is a speech-declipping paper. My only
  verified touchpoint for particle-identity Lenia is the perturbation-response study
  `arXiv:2305.16706v1` (2023-05-26), which I cite by ID and title from the arXiv API listing
  but whose full text I did not read. **The strongest cell-identity counterexample in the
  literature is therefore the one I checked least.** Flagging it as the highest-value follow-up.
- **"Towards a differentiable simulator of biological development"** (Lezama, Ibarz,
  Mordvintsev) and **"Unsupervised Egocentric Spatial Structure from Sensorimotor
  Prediction"** — **UNVERIFIABLE as arXiv IDs** (`1904.10964` and `1906.09663` are QCD and
  amorphous-solids papers respectively). These are the canonical differentiable-Lenia
  references, so **Q2's "differentiable Lenia" half rests on secondary mentions and on
  Flow-Lenia, which I did verify.** I did not summarise them from memory.
- **Mordvintsev et al. 2020** (the original Golly-wire NCA) — the ID I recalled (`2004.06556`)
  is an astronomy paper and I did **not** resolve the correct one. The companion **Ruiz et al.
  2021, "Neural Cellular Automata Manifold" is `arXiv:2006.12155` (v3, updated 2021-03-02,
  published 2020-06-22)** — title verified — but I did not read its full text, so I make no
  claim about its contents.
- **Genie 2 / Genie 3** — no arXiv record found; treated as a blog release, not a paper.
- The 12×12 NCA is a **scaled-down** reproduction. Absolute losses are not comparable to the
  literature's 72×72 or 48×48 results. The structural measurements (census, locality,
  identity, mark transport) are scale-robust; the loss values are not, and I do not claim they
  are.

## 10. REPRODUCTION

Everything ran **CPU only — there is no CUDA in this sandbox** (1 core, 2 GB RAM).
`torch 2.14.1+cpu`, `numpy 2.4.6`, `scipy 1.17.1`, Python 3.11.2. Scripts and JSON outputs
in `edge-NCA-artifacts/`.

- `chan_LeniaF.py` — Chan's `Board`/`Automaton` classes extracted verbatim (lines 120–676)
  and used as ground truth; `extract.py` re-executes that extraction with stubbed GUI/GPU
  imports.
- `chan_ref.py` — my independent numpy port. **Validated against Chan's own code: kernel
  max|Δ| = 3.9e-18, field max|Δ| = 1.2e-15 after 5 steps** (`e1d_stepdiff.py`). The RLE
  decoder round-trips 532/548 catalogue entries exactly (the 16 misses are non-Lenia
  Life-like rules with a different trailing-zero convention).
- `e1e2_cells.py` → `e1e2.json` — Lenia cell census (§3) and mark transport (§4). ~5 s.
- `e7_lenia_sens.py` → `e7_lenia_sensitivity.json` — 891-probe (m,s) basin scan (§5). ~6 min.
- `e3_nca.py` → `e3_nca.json`, `nca.pt` — NCA training, census, mutation table (§1). 112 s.
- `e4e5e6.py` → `e4e5e6.json` — locality, cell alphabet, mark transport (§2, §3, §4). ~2 s.

**Three of my own harness bugs are recorded rather than hidden**, because each nearly produced
the wrong answer: (i) my first Lenia port used a 3-D-then-summed kernel and reported a
*non-gliding* Orbium — caught only by diffing against Chan's class; (ii) my first NCA
`seed_state` set the alive channel to 1 on **every** site, so the "NO SEED" mutation was
actually measuring "all cells dead vs all cells alive" and would have supported the opposite
conclusion; (iii) `e4e5e6.py` computed the influence-radius quantiles from a *double* cumulative
sum, printing "50% within radius 3, 90% within radius 4" while its own correct per-radius
table said 44.3% at r3 and 67.7% at r4. The two printed lines disagreed, the quantiles were
recomputed from the saved `infl`/`D` arrays in `e4e5e6.json` (50% → r4, 90% → r6, 95% → r6,
99% → r7), and **the report carries the corrected values**. The script is fixed in the
artifacts directory. All three bugs were caught by cross-checking two independent
computations against each other — which is the only reason they are not in the conclusions.

---

## 11. THREE-LINE VERDICT

1. **What the literature already gives us:** a shared, learned, 3×3-local *rule* applied to a
   continuous state tensor — plus a 2026 result that a grown NCA's cell census is 1,500-to-<50
   depending on the analyst's ε (2607.15726v2), and my confirmation that the flagship Lenia
   creature has 220 or 57 cells depending on a threshold and that a mark written into a cell
   is carried away by the pattern at 0.99× the glider's speed.
2. **What it costs us:** every claim that the learned-CA world is doing what "cells that grow
   themselves" says. It cannot start itself (0.1516 vs 0.1503 do-nothing), it memorised the
   hand-planted seed's position (10.7× worse one corner away), its repair is near-global
   (74% of alive cells, 2607.12403v1), and its one route to persistent cells is hand-added
   mass conservation — so the scar is a parameter, not an irreducible unit.
3. **What we should stop claiming:** stop claiming the cell is the irreducible unit *of the
   substrate* — it is a resolution-dependent thresholding of a continuous field, and §4 shows
   a cell's content is recomputed every tick; keep the claim only in the form the evidence
   actually supports, "**the cell is the irreducible unit of the record, and the substrate is
   a continuous field the record samples**", and stop implying the CA literature is our
   competitor — it is not even talking about the same object.
