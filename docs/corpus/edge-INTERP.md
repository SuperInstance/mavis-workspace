# edge-INTERP — interpretability, superposition, and the limits of any observation

**Scout 2 · 2026-10-01 · fleet-triage**
Question put to me: *is our doctrine — "every observation is a projection, every projection is lossy,
and no downstream cleverness recovers what the looking never carried" — made precise and measurable
by the mechanistic-interpretability literature, or is it a citation-shaped decoration?*

**Short answer: the doctrine is right about the conclusion and wrong about the content.** Two of the four
questions have rigorous answers in the literature, one is a clean negative, and one is partial. The
sentence as we write it is unfalsifiable because it is missing a condition — and the missing condition
is the same one that killed three of my own instruments tonight. Details below.

---

## 0. Method, and the instrument that lied on me first

Per the bar, I re-derived before I read. Every derivation is in
`derive/interp_rederive.py` (numpy only; no torch/sklearn in this sandbox). Output is
reproducible: `python3 derive/interp_rederive.py`.

Two things happened that belong in the report because they are the report's own thesis:

**(a) I do not remember arXiv IDs.** I wrote down ten IDs from memory for the core SAE papers and
resolved all ten through the arXiv API. **Two were correct.** The other eight resolved to
hep-th, cond-mat, math.CO, cs.CV and cs.NE papers that have nothing to do with the question:

| recalled ID | what it actually is |
|---|---|
| `2309.00512` | *Relativistic hydrodynamic fluctuations from an effective action* (hep-th) |
| `2310.04864` | *Empirical Exploration of Deformation Mechanisms in Deep Rock* (cond-mat.mtrl-sci) |
| `2403.19603` | *Semantic Map-based Generation of Navigation Instructions* (cs.CL) |
| `2404.19756` | *KAN: Kolmogorov-Arnold Networks* (cs.LG) |
| `2303.13556` | *ProtoCon: Pseudo-label Refinement* (cs.CV) |
| `1811.04131` | *Platonic solids and high genus covers of lattice surfaces* (math.GT) |
| `1902.10186` | *Attention is not Explanation* — correct paper, **wrong ID** |
| `2305.03003` | *All Kronecker coefficients are reduced Kronecker coefficients* (math.CO) |

Correct: `2209.10652` (Toy Models of Superposition) and `1810.03292` (Sanity Checks for Saliency Maps).

A citation written from memory is not a citation. Every ID in this report was resolved by
title search against the arXiv API and, for the load-bearing one, read out of the PDF.

**(b) My own negative-result harness lied to me twice, and I nearly published both lies.**

- **MI estimator violated the data-processing inequality.** A joint-histogram MI estimator on
  continuous variables reported `I(X;Y)=0.0049 < I(X;Z)=0.0716`. DPI is a theorem; the estimator
  was wrong (binning bias, larger for the noisier variable). I replaced it with a discrete
  binary channel whose MI is `1 − H₂(err)` in closed form, so the instrument can be hand-checked.
  It now agrees to 4 decimals: closed-form 0.278072 / empirical 0.278024.
- **A search parser reported zero results on pages that had results.** `arxiv.org/search` returns
  result blocks my regex didn't match. I reported "Fisher information × mechanistic
  interpretability: nothing" — then a positive-control query on the same code path returned
  1,516 results, and a raw page dump showed the original query had **4 results**. The negative was
  an artifact of my parser. The real negative (below) is 4 results, none on point.

- **A silent broadcast bug.** `(N,) − (N,1)` in NumPy gives an `N×N` matrix, not an error. A scoring
  line read `R² = −7998` while the underlying fit was `L = 6.3e-06` (essentially perfect). The
  model was right; the ruler was wrong. This is a fourth instance in this fleet of *a confident
  number from a broken instrument*, and it is the exact structure of the question-4 problem.

---

## Part A — the derivations (done before reading)

### D0. Is a coordinate change a projection? **The objection lands on the word, not on the claim.**

```
invertible 9x9 coordinate change A:  det = -15.05,  rank 9, ||AA^-1 - I|| = 3.3e-15   -> bijective
rank-3-of-9 observation B:          ||x1 - x2|| = 3.7000,  ||Bx1 - Bx2|| = 1.7e-15 -> IDENTICAL
```

The orchestrator's counter-argument — "most of what we call projection is a chosen coordinate
system, and coordinate changes are reversible" — **is correct and does damage the sentence.**
Two distinct properties are being run together:

- **Idempotence** `P² = P` is what makes a map *a projection* in the linear-algebra sense.
- **Non-injectivity** `ker(P) ≠ {0}` is what makes it *lossy*.

They are not the same property. A genuine 9×9 rank-3 projection is both (measured
`‖P²−P‖_F = 7.8e-16`). A rank-3-of-9 map that is *not* idempotent is still lossy. And a
full-rank observation is a coordinate change: bijective, zero loss, and it is still an observation.

> **An observation channel `P: ℝⁿ → ℝᵐ` is lossy ⟺ rank(P) < n ⟺ ker(P) ≠ {0}.** This is invariant
> under relabeling, so loss is not a coordinate artifact. But a full-rank channel is lossless, so
> "**every** observation is lossy" is false as written.

### D1. "No downstream cleverness recovers discarded information" — the exact statement

Let `P: ℝⁿ→ℝᵐ` be the channel, `h: ℝⁿ→ℝᵏ` the target. Then

> **⟺ [ ∃ g : ℝᵐ→ℝᵏ with `g(Px) = h(x)` ∀x ] ⟺ [ `h = h̃ ∘ P` for some `h̃` ] ⟺ [ `h` is constant on cosets of `ker(P)` ]**

*Proof.* (⇐) take `h̃ = h|im(P)`. (⇒) if `x − x' ∈ ker(P)` then `Px = Px'`, so `h(x) = g(Px) = g(Px') = h(x')`;
`h` is constant on cosets of `ker(P)`, i.e. factors through `im(P)`. ∎

Measured, with a 2-layer tanh MLP (universally approximating, so this is not a capacity claim):

| target `h` | reads the discarded subspace? | best `R²` on `P(x)` |
|---|---|---|
| `h = w₁` (a discarded coordinate) | yes | **+0.13** (≈ the conditional mean; the best constant is 0) |
| `h = 0.7 sin(2z₀) + 0.5z₁²` | no | **+0.999994** |

The second row is the finding. **The loss is a property of the pair `(P, h)`, never of `P` alone.**
Our doctrine says "no downstream cleverness recovers what the looking never carried" — true, but
only because the target *reads the discarded subspace*. If it doesn't, recovery is exact and the
projection discarded nothing relevant. **That condition is what we are missing, and it is the
entire content of the slogan.**

### D2. Data-processing inequality, hand-checkable

Discrete binary channel, `I(X;Y) = 1 − H₂(err)`:

```
err 0.50 | closed 0.000000 bits | empirical 0.000000 | g=identity 0.000000 | g=const 0.000000
err 0.20 | closed 0.278072      | empirical 0.278024 | g=identity 0.278024 | g=const 0.000000
err 0.05 | closed 0.713603      | empirical 0.712582 | g=identity 0.712582 | g=const 0.000000
err 0.00 | closed 1.000000      | empirical 1.000000 | g=identity 1.000000 | g=const 0.000000
```

The strongest *legal* post-processor achieves **equality, never more**. And I measured the cheat:
`g(Y) = 1[Y = X]` scores 1.0 bits of "information about X" and is pure label leakage — `g` is not
a function of `Y`, it is a function of `(X, Y)`.

> **"Downstream cleverness" is not forbidden by cleverness. It is forbidden by the single condition
> that `g` sees only the observation.** State the condition or the sentence is a slogan.

### D3. Does an SAE recover "the" feature? **No — and the proof is four lines.**

If `f` is a dictionary and `A` is invertible, then `(fA)A⁻¹` is the same dictionary, with the same
reconstruction error. Measured, `F = 40` atoms, `d = 12`, `K = 6`-sparse codes:

```
||a - f_true h||²        = 0.000e+00
||a - f_rot  h_rot||²    = 2.488e-26      (f_rot = f_true Q, h_rot = h Q, Q orthogonal)
max|f_true h - f_rot h_rot| = 1.7e-15       -> bit-for-bit identical
```

Any objective that is a function of reconstruction loss is **invariant along the entire GL(F) group**
— a 40×40, uncountable orbit of "features", all equally good. I then exhibited a *specific*
alternative direction: a unit vector in `span(f_true)` orthogonal to atom 0 (`⟨A,B⟩ = +0.0000`).
The dictionary explaining the data is unchanged. So A and B are both "the feature" **by the only
criterion the data can apply.**

> The word "the" is not sloppy English here. It is a category error: the data constrains the
> **span**, and the span has an `(F²−F)`-dimensional family of bases.

Also derived, because capacity claims get read as modelling results when they are arithmetic:
`log₂ C(n,K) ≥ d` gives, at `d = 32`: `K=2 → n ≈ 102,908` (3216×), `K=4 → n ≈ 582` (18×),
`K=8 → n ≈ 64` (2×), `K=32 → n ≈ 45` (1.4×). **Any "d=512 hosts 50,000 features (98×)" claim is a
statement about `C(n,K)`, not about a network.** The ratio is a function of `K` and `d` and should
be checked as multiplication.

### D5 / D6 — the fleet's own canary

`FNV-1a 64` on a fixed string. Measured: `P(collision) ≤ N²/2⁶⁵`, so `N = 10⁶ → 2.7e-08` (safe),
`N = 10⁹ → 2.7e-02` (not safe). Demonstrated an actual collision at 32-bit width
(`payload-1888` and `payload-130586` → `0xf323bb81`, 130,585 tries). At 64-bit the same attack is
~540 years single-core. FNV-1a is not a cryptographic PRF, so that bound is optimistic.

The structural point is sharper than the arithmetic:

> A canary detects a change in `H(x)`. **It cannot certify `x`.** Two different `x` with the same `H`
> are indistinguishable to it *forever* — not probabilistically, forever, because the information is
> gone. In that exact sense the canary **is** a projection, and in that exact sense it is **not a
> measurement of the artifact's content.**

And the fleet's own finding, formalized. Let an instrument `I` certify property set `S_I`.
An instrument cannot detect defect `D` unless `D ∈ S_I`. Fleet instruments certify
`{existence, callability, hash-stability, schema-conformance, test-pass-count}`. None of those
contains *"the headline mechanism is executed"* or *"the equation has the claimed coefficient."*
Multiply the guidance equation by `0.0`: canary **green**, 88 tests **green**, artifact **wrong**.

> The measurement-vs-construction error is a **mismatch between `S_I` and the claim class**, and it is
> cheap to check: mutate the headline line; if the suite stays green, the defect was never in `S_I`.

---

## Part B — Q1. Superposition and identifiability. **The rigorous version exists. It is recent.**

**`arXiv:2605.31245v1` — "Toward Identifiable Sparse Autoencoders", Nelson, Karaletsos, Locatello
(ISTA + Pyramidal Inc.). ICML 2026, PMLR v306. Published 2026-05-29. 18 pp. Read from the PDF.**

This is the paper the fleet needs. Three results, quoted:

**Definition 3.1 (SAE Identifiability).** Two `k`-sparse SAEs `(f,D)`, `(f',D')` trained
independently on data from `P(x)` are *nearly identifiable* if there exist `ε_f, ε_D ≥ 0` with
`‖f(x) − Σf'(x)‖₂ ≤ ε_f` a.e. and `‖D − D'Σ‖ ≤ ε_D` for some **signed permutation matrix** `Σ`.

The word is **not** "the feature." It is: *the same features, up to the ordering and sign of atoms,
if and only if four conditions hold.* The trivial ambiguities are named and excluded. That is a
precise equivalence class, and it is the smallest one the data can support.

**Theorem 3.2 (Identifiability Impossibility).** *There exists* a normalized dictionary `D ∈ ℝ^{N×K}`
such that for **any** `k`-sparse continuous encoder `f` with reconstruction tolerance `ε ≥ 0` and
`‖Df(x) − x‖ ≤ ε` a.e. on `P(x)`, and assuming every atom is activated with positive probability,
**there exists another continuous encoder `f'` with the same reconstruction accuracy** that differs
from `f` on a positive-probability set, with sparsity patterns differing too.

**This is our doctrine, with a theorem attached.** "No downstream cleverness recovers what the
looking never carried" is true *as an impossibility result* for the pair (encoder, dictionary) —
and it is false without the assumptions: the dictionary must be normalized, every atom live, and the
error tolerance positive. §3 of the paper also notes the coherent-dictionary barrier: in the
superposition regime, `d` and `d̃` are near-maximally similar, "a known barrier to identifiability"
(citing Candès et al. 2005).

**Theorem 3.6 (near-identifiability).** Under `aRIP` (their data-driven relaxation of the restricted
isometry property, Def 3.3), reconstruction error `ε`, and Assumptions 3.4/3.5, for two SAEs with
dictionaries `D, D'` and codes `z, z'`:

```
‖D − D'Σ‖_F ≤ ε_D        ‖z − Σz'‖ ≤ ε_z        for some signed permutation Σ
ε_D, ε_z → 0   as   ε, σ, k → 0
```

The RIP condition is equation (5): `(1−σ)‖z‖² ≤ ‖Dz‖² ≤ (1+σ)‖z‖²` for any `k`-sparse `z`.
Figure 1 states the **four ingredients** of identifiability: (a) the approximation is good enough,
(b) the manifold is sampled densely enough, (c) co-occurring concepts are distinct enough (aRIP),
(d) concept co-occurrence patterns are diverse enough.

And the line that should be quoted by the fleet verbatim:

> *"if run-to-run identifiability is poor, identifiability of some ground-truth is necessarily poor as well."*

**The classical ancestor** — and the fleet's best upgrade path. `arXiv:1911.00771`, "Sparse Regression
Codes" (Ahlswede & Verdú, *Foundations and Trends in Communications and Information Theory* 15(1–2):
1–195, 2019, DOI 10.1561/0100000092). Verified in the PDF: for i.i.d. Gaussian sources the
rate–distortion function is `R*(D) = ½ log(σ²/D)` for `D < σ²`, `0` otherwise (eq. 6.5), and
**Theorem 6.2** is a large-deviations bound on excess distortion showing SPARCs *attain the optimal
rate–distortion function and the optimal excess-distortion exponent*. Companion:
`arXiv:1202.0840`, "Lossy Compression via Sparse Linear Regression: Performance under
Minimum-distance Encoding" (2012).

This is the correct frame for superposition. **"Many features in few dimensions" is not an
interpretability problem that happens to have an information-theoretic flavour; it is the Gaussian
broadcast/spreading problem, and it has had a rigorous achievable-rate theory since the 1960s
(Ahlswede–Berlekamp), consolidated by 2019.** The fleet has been citing a 2022 interpretability
paper for a fact that is 60 years old and better formalized elsewhere. `arXiv:2512.13568v1`
("Superposition as Lossy Compression", TMLR 2025 — journal_ref confirmed) supplies the modern
bridge: Shannon entropy of SAE activations → **effective degrees of freedom** → "the minimum neurons
needed for interference-free encoding," correlating with intrinsic dimensionality on Pythia-70M.

**Answer to Q1: the rigorous version exists, is peer-reviewed, and it says the projection doctrine
is correct — with a RIP condition attached.** Our phrasing was the decoration; this is the
structure.

---

## Part C — Q2. The "lost information" claim. **Partial: the general theorem exists, the SAE-specific one exists, the slogan does not.**

Three distinct claims hide inside our sentence, with three different statuses:

| claim | status | source |
|---|---|---|
| post-processing cannot increase information | **theorem, exact** | DPI; measured D2 |
| discarded info is unrecoverable **for a target that reads it** | **theorem with a condition** | my D1 iff; Thm 3.2 |
| superposition in NNs is lossy compression, with a rate | **theorem, different literature** | SPARC R*(D), Thm 6.2 |

**The precise conditions, assembled.** All four of these must hold or the slogan fails:

1. **The channel is non-injective.** `ker(P) ≠ {0}`. (D0)
2. **The target reads the kernel.** `h` non-constant on cosets of `ker(P)`. (D1) — without this, recovery is exact (measured `R² = 0.999994`).
3. **The post-processor sees only the observation.** `g` is a function of `P(x)` alone, i.e. `X → P(X) → g` is a Markov chain. (D2, DPI)
4. **The dictionary is overcomplete/coherent, and reconstruction error is positive.** (Thm 3.2, Thm 3.6)

**Without conditions it is a slogan.** With them it is a theorem, and condition 2 — which nobody in
our doctrine mentions — is the one that makes it true. Condition 3 is the one that makes it
falsifiable: it is exactly the line between a probe and label leakage.

---

## Part D — Q3. Measurement and its limits. **CLEAN NEGATIVE. This does not exist.**

The orchestrator asked whether anyone connects *observation budget, projection, and downstream
performance*, and whether anyone has made the canary idea rigorous. Searched, with a positive
control on the same code path:

| query | total results | on point? |
|---|---|---|
| `Fisher information mechanistic interpretability` | 4 | **no** — PEFT selection, parameter identifiability in data-driven models, quantum error-correcting codes, trust/evidence accumulation |
| `Fisher information probing neural representations` | 4 | **no** — sim-to-real PDE surrogates, neural sensitivity geometry, information-geometric probe of many-body systems, principal distortions |
| `rate-distortion interpretability measurement budget` | 1 | **no** — adversarial transferability in medical imaging |
| `data processing inequality neural network representation information loss` | **0** | — |
| `negative control interpretability verification` | 6 | **no** |

**There is no Fisher-information, observation-budget, rate-distortion, or experimental-design
formalism for mechanistic interpretability.** I could not find one, and the negative survived a
parser-bug scare and a positive control. This is the finding, and it is worth more than a summary.

What exists instead, and it is a different shape than the orchestrator imagined:

- **V-usable information**, made operational by `arXiv:2109.09234v1` (Hewitt & Liang, "Conditional
  probing: measuring usable information beyond a baseline", EMNLP 2021). The key move: instead of
  comparing a probe against a baseline as a *point comparison*, **condition on the baseline** and
  measure the information the representation holds that the baseline does not. The formalism is
  V-information (Xu et al.); its arXiv ID is **UNVERIFIABLE** (see §Ledger), but the formalism is
  attested second-hand by two verified papers that use it.
- **V-information as a data-testing instrument**: `arXiv:2408.02919v1` (Hewitt et al., "Data Checklist:
  On Unit-Testing Datasets with Usable Information", **COLM 2024**). This is the closest thing in the
  literature to the orchestrator's Q4, and it is the closest thing to making the canary rigorous.
  It gives a **taxonomy of unit tests for datasets**, built on V-information, and — critically — it
  "discover[s] previously unknown artifacts in preference datasets for LLM alignment" **before**
  any downstream model failure. Testing the instrument before trusting the reading.
- **A budget, but a geometric one, not an informational one**: `arXiv:2609.37857v2`, "Active Budget Can
  Kill Sensitivity: Diagnosing and Repairing TopK Sparse Autoencoder Reliability" (2026-09-30). A
  controlled width×k factorial identifies the **active budget `k`** as the root cause of feature
  instability; degradation "arises from the selection boundary rather than dictionary width alone."
  The **active margin** — the distance to the TopK cutoff — "predicts feature loss **without
  thresholds**." Repairs rare-feature sensitivity by 8.83 points. Note what this is: not a Fisher
  information, but a *geometric margin* that is predictive of instrument failure. It is the
  canary idea done properly inside one architecture.
- **The one place observational measurement is validated against ground truth**:
  `arXiv:2111.05299v1` (NeurIPS 2021, "Can Information Flows Suggest Targets for Interventions in
  Neural Circuits?") measures `M`-information flow about a protected attribute and checks it against
  *actual pruning interventions*. That is the right pattern and it is rare.

**On the canary specifically:** making `H(x)` rigorous means saying *what `H` is a function of and
what set it is injective on*. "Injective on a set of size `N` with probability ≥ 1 − N²/2⁶⁵" is
rigorous. A cryptographic commitment to the artifact's **content** (not a hash of metadata) is
rigorous. A 64-bit FNV over a *fixed string about the repo* is neither: it is injective on nothing
that matters, and it certifies a constant. No paper makes the fleet's version rigorous. That is
because the fleet's version is not a measurement.

---

## Part E — Q4. Instruments vs conclusions. **Partial. The vocabulary exists; the unified account does not.**

The characteristic fleet failure — *a well-formed, checkable, wrong artifact with no instrument that
can say so* — **is** a recognized failure mode in interpretability, and it has been named, measured,
and given failure cases. What does not exist is a single account that ties it together.

Verified instances, strongest first:

1. **`arXiv:2408.02919v1` (COLM 2024, Data Checklist).** The dataset is the instrument, not the
   model. The checklist finds artifacts *before* they cause a model failure. This is the strongest
   answer to Q4 and it is the one the fleet should adopt.
2. **`arXiv:1810.03292v3` (Adebayo et al., "Sanity Checks for Saliency Maps", NeurIPS 2018;
   v3 dated 2020-11-06, comment: *"Updating Guided Backprop experiments due to bug. The results and
   conclusions remain the same"*).** The canonical negative-control paper: methods that appear to
   explain a trained model must be shown to *fail* to explain a randomized one. An instrument that
   does not degrade when the science is destroyed was never measuring the science. **That is the
   fleet's guidance-equation mutation, published in 2018.**
3. **`arXiv:2506.16678v2` (EMNLP 2025, "Mechanisms vs. Outcomes").** 32 open-weight transformers;
   syntactic features extracted by probing **fail to predict** outcomes on targeted syntactic
   evaluations. A probe that finds a mechanism and a model that does not use it are compatible.
4. **`arXiv:2109.09234v1` (EMNLP 2021, Conditional probing).** A representation can be more useful
   than a baseline and still encode *nothing the baseline lacks*; and after conditioning, POS
   "is accessible at deeper layers of a network than previously thought." A measurement whose value
   changes when you subtract the confound is a measurement you did not understand.
5. **`arXiv:2502.16681v1` ("Are Sparse Autoencoders Useful? A Case Study in Sparse Probing", 2025).**
   Across four regimes (data scarcity, class imbalance, label noise, covariate shift): SAEs
   occasionally beat baselines on individual datasets, but no ensemble combining SAEs with baselines
   consistently beats an ensemble of baselines alone, and the apparent wins on spurious-correlation
   detection "we are able to achieve similar results with simple non-SAE baselines as well."
6. **`arXiv:1902.10186v3` (Jain & Wallace, "Attention is not Explanation", NAACL 2019).** The
   existence of an explanation-shaped object does not imply the explanation of the behaviour.
7. **The abstraction-theoretic line**, where faithfulness is defined formally rather than checked:
   `arXiv:2209.03013v1` ("Quantitative probing: Validating causal models using quantitative domain
   knowledge", *J. Causal Inference*), `arXiv:2301.05893v2` (CLeaR 2023, consistent causal abstractions
   over multiple interventional distributions), `arXiv:2602.24266v2` (Causal Mechanism Reduction).
   An abstraction is a claim that two models *commute with interventions*. That is a real formal
   standard for "the high-level model really is the computation," and the fleet has no equivalent.

**The negative:** `negative control interpretability verification` returns 6 results, none on point.
"Negative control" is **not established vocabulary** in the interpretability literature. The idea
exists (sanity checks, conditional probing, data checklists); the *account* does not. There is no
paper that states a general criterion distinguishing a measurement from a construction, and there is
no published taxonomy of verifier failure modes.

That absence is itself a finding, and it is a bit uncomfortable: the fleet arrived at
"a checkable, wrong artifact with no instrument that can say so" **empirically, by getting burned,
and arrived at it before or alongside the literature.** We have been doing interpretability
methodology without citing it.

---

## Verdict table

| Q | question | verdict |
|---|---|---|
| 1 | superposition / SAE identifiability | **PRECISE, RECENT, PEER-REVIEWED.** ICML 2026 `2605.31245`: impossibility theorem + RIP-conditioned near-identifiability up to signed permutation. Classical home = SPARC rate–distortion (`1911.00771`). |
| 2 | the "lost information" claim | **CONDITIONAL, NOT A SLOGAN.** DPI is exact; the target-side condition is the iff in D1; the SAE-specific form is Thm 3.2. Four conditions required. |
| 3 | measurement budget / Fisher / rate–distortion | **NEGATIVE. DOES NOT EXIST.** 4 results, none on point, positive control passed. Closest: V-information, and a geometric "active margin" in TopK SAEs. |
| 4 | instruments vs conclusions | **PARTIAL.** Strong instances (sanity checks, conditional probing, data checklists, mechanisms-vs-outcomes) but **no unified account**; "negative control" is not the field's vocabulary. |
| — | is a coordinate change a projection? | **The objection lands on the word.** Loss ⟺ `ker(P) ≠ {0}`, and a full-rank observation is lossless. "**Every** observation is lossy" is false. |

---

## Our doctrine, rewritten precisely

**Before** (current fleet phrasing):
> Every observation is a projection, every projection is lossy, and no downstream cleverness recovers
> what the looking never carried.

**After:**
> An observation is a channel `P`. It is **lossy exactly when it is non-injective** —
> `ker(P) ≠ {0}` — and a full-rank observation is a lossless coordinate change, so "every
> observation is lossy" is false. Loss is a property of the **pair `(P, h)`**, never of `P` alone:
> the information about a target `h` is unrecoverable from `P(x)` **iff `h` reads the discarded
> subspace**, and if `h` does not, recovery is exact. No post-processor can do better than the
> conditional mean, because **`g` must be a function of the observation alone** — a `g` that reads
> the target is leakage, not cleverness. The named ambiguities are **exactly the trivial ones**:
> ordering and sign of atoms. Residual ambiguity is not slack in the method; it is the *data's*
> non-identifiability, and it has a name — a **restricted isometry** failure — and a measurable
> certificate. **When the certificate fails, the correct output is not a weaker claim; it is the
> claim that two things are indistinguishable, stated as such.**

The single most useful change: **"no downstream cleverness" is replaced by "the information is not in
the observation"** — and the second is checkable, the first is unfalsifiable.

---

## What would falsify it

Our rewritten doctrine is falsifiable in five specific ways. Each is a concrete experiment, not a
gesture:

1. **Show a lossy observation that is lossless for a class of targets.** Construct `P` with
   `ker(P) ≠ {0}` and a target `h` that is constant on cosets of `ker(P)` but is *not* of the form
   `h̃ ∘ P` for any measurable `h̃`. **This is impossible** — the iff is proved. So this falsification
   route is closed, which is a sign the statement is now a theorem and not a slogan.
2. **Refute Thm 3.2.** Exhibit an SAE with a normalized dictionary, every atom live, positive
   tolerance `ε`, and a **unique** continuous `k`-sparse encoder at that tolerance. Per the theorem
   the second encoder exists, so the falsifier is a dictionary where it provably fails. If a
   construction succeeds, the paper is wrong and our doctrine weakens.
3. **Measure `aRIP` on a real trained SAE and find it far from satisfied.** The identifiability claim
   is conditional. If σ is large, run-to-run dictionary disagreement is not a bug to be tuned away —
   it is the theorem being obeyed. **We should check this before quoting any SAE feature as "the"
   feature.** This is the cheapest experiment on this list and we have not done it.
4. **Find a full-rank observation we call "projected."** Any instrument the fleet labels a projection
   with `rank(P) = n` is a category error in our own vocabulary, and finding one invalidates the
   claim that the doctrine is *load-bearing* rather than *decorative*.
5. **The one that would actually hurt us.** Demonstrate a downstream system that **recovers a target
   reading the discarded subspace** from `P(x)` alone. DPI forbids it. The only ways out are: the
   "discarded" subspace was never actually discarded (the projection was full-rank — falsification 4),
   or the recovery read the target (condition 3 violated). A third way out — that the recovered
   quantity is not `h` but a *sufficient statistic* for the decision actually made — is **not** a
   counterexample. It is the one escape hatch, and it is where the interesting work is.

**The uncomfortable corollary, stated plainly:** for our own instruments — a canary, a hash, a test
count — the condition-2 test is not available. We cannot exhibit a target our instruments do not
read, because they read almost nothing. The rewrite is not yet a reformulation of the fleet's
practices. **It is a standard the fleet's current instruments are measured against, and they fail it.**
The next thing worth building is a `aRIP`-style certificate for the fleet's claims: not "is the
canary green" but "which property set does this instrument certify, and is the headline claim in it."

---

## Ledger

### Verified primary sources (ID resolved by title search; version and date from the arXiv API)

| arXiv ID | ver | title | venue |
|---|---|---|---|
| `2605.31245` | v1, 2026-05-29 | Toward Identifiable Sparse Autoencoders | **ICML 2026**, PMLR v306 — *read from PDF* |
| `1911.00771` | v1, 2019-11-02 | Sparse Regression Codes | F&T in Comm. & Info. Theory 15(1–2):1–195, DOI 10.1561/0100000092 — *read from PDF* |
| `1202.0840` | — | Lossy Compression via Sparse Linear Regression | 2012 |
| `2512.13568` | v1, 2025-12-15 | Superposition as Lossy Compression | **TMLR 2025** (journal_ref) |
| `2209.10652` | v1, 2022-09-21 | Toy Models of Superposition | transformer-circuits.pub |
| `2309.08600` | v3, upd 2023-10-04 | Sparse Autoencoders Find Highly Interpretable Features in LMs | ICLR 2024 |
| `2406.04093` | v1, 2024-06-06 | Scaling and evaluating sparse autoencoders | — |
| `2502.16681` | v1, 2025-02-23 | Are Sparse Autoencoders Useful? A Case Study in Sparse Probing | — |
| `2408.02919` | v1, 2024-08-06 | Data Checklist: On Unit-Testing Datasets with Usable Information | **COLM 2024** |
| `2109.09234` | v1, 2021-09-19 | Conditional probing: measuring usable information beyond a baseline | **EMNLP 2021** |
| `2506.16678` | v2, upd 2025-11-08 | Mechanisms vs. Outcomes | **EMNLP 2025** |
| `1810.03292` | v3, 2020-11-06 | Sanity Checks for Saliency Maps | NeurIPS 2018 |
| `1902.10186` | v3, 2019-05-08 | Attention is not Explanation | NAACL 2019 |
| `2609.37857` | v2, 2026-09-30 | Active Budget Can Kill Sensitivity | — |
| `2111.05299` | v1, 2021-11-09 | Can Information Flows Suggest Targets for Interventions in Neural Circuits? | NeurIPS 2021 |
| `2209.03013` | v1, 2022-09-07 | Quantitative probing: Validating causal models using quantitative domain knowledge | *J. Causal Inference* |
| `2301.05893` | v2, upd 2023-05-07 | Jointly Learning Consistent Causal Abstractions | CLeaR 2023 |
| `2602.24266` | v2, 2026-07-06 | Causal Mechanism Reduction | — |

### UNVERIFIABLE — cited by the literature or widely believed, ID not resolved tonight

- **Xu et al., V-information** ("Information, Computational Constraints, and Evaluation in
  Representation Learning", ICLR 2020). arXiv ID not found; `1802.00900` resolves to a
  superconductivity paper. The formalism is attested by `2109.09234` and `2408.02919` (both verified).
  **Do not cite an ID. Cite the concept via those two.**
- **Adebayo et al., "The Unreasonable Ineffectiveness of Feature Attribution"** (ICML 2018). Not
  returned by arXiv author search; `proceedings.mlr.press/v80/adebayo18{a,b}.html` both 404; no
  Crossref match. The **companion** paper `1810.03292` is verified and carries the same sanity-check
  argument. Use `1810.03292`; treat the ICML paper as unconfirmed.
- **Hewitt & Manning, "A Structural Probe for Finding Syntax in Word Representations"** (NAACL 2019).
  ACL Anthology ID not resolved — `N19-1127` is a different paper. Do not cite from memory.

### What this lane produced that is not a citation

`derive/interp_rederive.py` — 7 derivations, numpy-only, ~30 s. D0 coordinate-vs-projection;
D1 the recovery iff + MLP measurements; D2 DPI on a hand-checkable discrete channel; D3 the GL(F)
invariance and a concrete orthogonal alternative "feature"; D4 capacity arithmetic `log₂C(n,K) ≥ d`;
D5 the canary's birthday bound with a demonstrated 32-bit collision; D6 the `S_I` formalization of
measurement-vs-construction. Three of the seven were wrong on first run and were caught by the
divergence, the DPI violation, and the positive control. **The three bugs are the finding.**
