# SCOUT PASS 2 — attacking the survivors

**Scout session:** 447591767552112 · **Date:** 2026-10-01 · **Target:** `docs/F1-F2-DIFFUSION.md` (read, not modified)
**Status:** nothing pushed. No other agent's file touched.
**Citation rule:** every citation below is one I opened this pass, or it is marked `UNVERIFIED`.

---

## 0. VERDICT FIRST — what fell

You asked me to say it first. **Three of the four load-bearing claims are dead, and one of them
is dead because of an internal contradiction inside your own document that costs zero citations
to demonstrate.**

| # | Claim | Verdict |
|---|---|---|
| 1 | F1 vs F2 is a distinction between **kinds of operator**, not degrees of tuning | **DEAD.** They are two points in one convex family. The axis is not randomness. |
| 2 | Stochastic recombination **restores** variance in one step | **DEAD, and miscomputed.** F2 recovers exactly **half** the parental variance. Your own formula contradicts your own F1 premise. |
| 3 | A **discontinuous** update is the strongest card for escaping the fixed point | **DEAD.** §3 already escapes it with continuous Gaussian noise. Contradiction is internal. |
| — | "The F1 uniform state is reachable and **absorbing**" (your falsification table) | **DEAD as stated.** False for a continuous weight space — the one you are actually writing about. |
| — | `micromoth-quilt` is the F2 substrate | **DEAD.** Not a mean field, not a population, stdlib PRNG, and its randomness is the **inverse** of your requirement. |
| 1' | Mean-field machinery never pointed at this | **SURVIVES.** Unattacked this pass. |
| 2' | Framing gap: non-IID never framed as information loss | **SURVIVES.** Unattacked this pass. |
| 3' | The sociology sentence | **SURVIVES — and is now sourced.** Not Granovetter. Opinion dynamics. |
| 4' | The operator distinction, **restated spectrally** | **SURVIVES in a narrower, correct form.** See §1.4. |

**The pattern you should notice, because it is now three for three:** `σ²/2k` was
mutation–selection balance; the phenomenon was already named (vanishing variance); and now
`Var_n = Var₀·2^(−n)` turns out to be **Wright's inbreeding coefficient**, the third
textbook result in the same family. Two of the document's four pillars are now standard
results under other names. The document is thinner than it was, and it should be.

**The one thing I found that is worth more than anything I took away** is in §5.3: there is
already a receipt in your own fleet that states the elitism-vs-archive claim, in your own
vocabulary, and tests it. You had a better instance of your thesis than the one you were
reaching for, and it was in `micromoth-quilt` the whole time — in a subdirectory, not in the
framework.

---

## 1. LANE A1 — "stochastic recombination" is not a different kind of operator

**Your three ways to break it. The first one broke it. Here is the argument, self-contained —
it needs no citation, only definitions.**

### 1.1 Both operators are doubly stochastic, and doubly stochastic operators are convex

Averaging over `n` participants is a **doubly stochastic operator** (a bistochastic kernel):
rows sum to 1, columns sum to 1, so it preserves both the uniform distribution and the mean.
Random recombination — draw a genotype from the population — is *also* doubly stochastic: a
uniform input distribution maps to a uniform output distribution under any doubly stochastic
kernel.

So both of your operators live in the same set: the bistochastic operators on a finite space.
And that set is **convex**: if `P` and `Q` are bistochastic, so is `(1−t)P + tQ` for any
`t ∈ [0,1]`. (The extreme points of the bistochastic set are the permutation matrices — the
Birkhoff–von Neumann picture, which Sinkhorn's scaling machinery is built on. I attempted to
pin a specific citable Sinkhorn paper and **failed to resolve one cleanly this pass; treat the
convexity fact as a standard theorem, not as a claim I have footnoted.**)

**Therefore: you can move from "averaging" to "recombination" by changing one scalar `t`.**

That is precisely "degrees of tuning." The distinction you wanted to make categorical is a
statement about a mixing coefficient. The convex-combination operator `P_t = (1−t)·A + t·R`,
where `A` is your averaging matrix and `R` a recombination kernel, is a one-parameter family
of bistochastic operators, and `t = 0` gives you F1 and `t = 1` gives you F2.

### 1.2 The representation theorem you asked me to find: it is stronger than you hoped

You asked for a representation theorem showing a stochastic update is a *mixture* of a
deterministic operator and independent per-agent draws. Here it is, and it is trivially
available:

> **A doubly stochastic operator `P` is exactly the one-step transition kernel of a random
> walk on the finite space.**

So **averaging is already a stochastic operator.** Your "deterministic averaging" F1 is a
random walk whose kernel happens to be a barycentric, low-rank matrix. Conversely, every
bistochastic operator is a discrete operator, and its small-step limit
`P_ε = (1−ε)I + εA` converges to the continuum operator

```
∂φ/∂t = D∇²φ − k(φ − φ*) + σξ
```

— which **is your §3 equation.** So the F2 operator in §3 is already the continuum limit of a
discrete stochastic operator. There is no gap of *kind* to cross. There is a scaling parameter
`ε`, and you have already written down its limit.

### 1.3 The intuition that saves the distinction is a category error

The felt reason for the distinction is "F1 is a *mixture*, F2 is a *draw*." But a mixture of
distributions **is** a draw from the mixture — that is what inverse-CDF sampling does, and it
is exactly what `micromoth.py` does (see §5.2). Sampling from `(p+q)/2` and mixing
`p` and `q` are the same operation performed at different levels of the stack. §1 of your
document already says this: *"Cross is mixture."* Recognising that a mixture can be *executed*
as a draw is not a new kind of operator; it is a different implementation of the old one.

### 1.4 🔴 What actually survives, restated correctly

There **is** a real distinction here, and it is not randomness. It is **rank / idempotence**:

- **Averaging is idempotent.** A barycentric/projection kernel satisfies `P² = P`. Its image
  is one-dimensional — the consensus. The uniform state is absorbing **in a single step**, and
  no amount of iteration helps, because the operator has already annihilated the subspace
  holding the private directions.
- **An ergodic bistochastic operator is not idempotent.** It has full-rank image and a
  **non-degenerate stationary distribution**. The uniform state is unreachable as a limit.

So the correct claim is:

> **The difference between F1 and F2 is not the presence of randomness. It is whether the
> mixing kernel is idempotent (a projection onto consensus, which annihilates the private
> directions) or ergodic (which has a non-degenerate stationary distribution).**

This is **narrower, correct, and defensible.** It is also, I am sorry to say, a well-known
property of bistochastic operators, so the *fact* is not yours. What may still be yours is
the **transfer**: nobody has pointed this at a federated weight lattice and said "your FedAvg
is a projection, and here is exactly what it projects away."

### 1.5 A gap your requirements expose but the document never states

Your F2 must inject variance while injecting **no information** — independent of `e_i`. Fine.
But you also want it to **hold variance at a set level** at `σ²/2k`. Those two requirements
together have a consequence you never wrote down:

> `k` (the restoring/selection strength) must be computable from **public consensus state
> only**. If `k` is a function of any participant's private data, then `k` leaks, and the
> "information-free" injection is no longer information-free.

That is a real design constraint — and it is the actual content of the F2 requirement, as
opposed to "add noise." Stating it would make the contribution sharper, not weaker. It also
gives a clean reason the F2 operator "is the one a federated system does not have": the
selection signal it needs does not exist in a federation that by construction holds only
consensus.

---

## 2. LANE A2 — Mendel's ratios are special, and yours are miscomputed

### 2.1 🔴 "Restores it in one step" is wrong by a factor of 2, in the very case it is derived from

My own arithmetic, single locus, two alleles, purely additive (no dominance), parents are pure
lines. Genotypic value = allele count, so `AA = 0`, `Aa = 1`, `BB = 2`.

| Generation | Composition | Mean | **Var** |
|---|---|---|---|
| P | ½ `AA`, ½ `BB` | 1 | **1** |
| F1 | all `Aa` | 1 | **0** |
| F2 | ¼ `AA`, ½ `Aa`, ¼ `aa` | 1 | **0.5** |

**F2 recovers exactly one half of the parental variance.** The halving does not stop; it
continues. "Stochastic recombination restores it in one step" is false in the only case you
gave. The correct statement is *recombination makes the variance non-zero again*, and the
`1/2` is not an accident — it is the same halving, now inside the operator.

This is a four-line calculation you can check by hand. It is worth more than any citation
against it.

### 2.2 🔴 Your §1 formula contradicts your own §1 premise

You assert both:

- `Var_n = Var_0 · 2^(−n)` — "geometric collapse"
- the F1 is **uniform**, i.e. `Var_1 = 0`

Those cannot both hold: the formula at `n = 1` gives `Var_0/2 ≠ 0`. The standard result the
formula is gesturing at is the **inbreeding-coefficient decay**, which is anchored so the
**limit** is zero rather than the first term — Wright's `F_t`, the decay of identity by
descent. Anchor citation, opened and verified:

**Slatkin (1991), "Inbreeding coefficients and coalescence times", *Genetics* —
DOI `10.1017/s0016672300029827` · 657 citations — VERIFIED.** From the abstract:

> *"…It is also possible to express **Sewall Wright's FST** as the ratio of average
> coalescence times of different pairs of genes."*

So: **§1's central geometric-collapse formula is a third textbook result**, in exactly the
same way `σ²/2k` was the second. That is now **three of your four pillars** that are standard
results under other names. Please say so in the document.

### 2.3 "Absorbing in one step" is false in the space you are actually writing about

Your falsification table says: *"The F1 uniform state is **reachable and absorbing** under
deterministic averaging."* How many steps that takes depends entirely on the state space:

- **Two pure lines** (your case): one step. The mean is a one-shot sufficient summary.
- **`n` pure lines:** `⌈log₂ n⌉` rounds under pairwise bisection averaging.
- **A continuous weight space** — which is what §3, §4 and the whole federated motivation
  are about: **never.** Geometric decay toward zero, never attained.

**In the continuous case your own document is about, the uniform state is asymptotically
attracting, not absorbing.** This is a table row a reviewer will check, and it currently
fails. Fix it to "asymptotically attracting in continuous spaces; attained in finitely many
rounds only on finite state spaces."

### 2.4 Where the variance-return claim *does* survive — and the caveat nobody stated

**Survives for multi-locus additive systems, and robustly.** The strongest practical evidence
is that plant breeders use F2 populations *specifically to estimate additive and dominance
variance components* — you cannot estimate a variance component from a population whose
variance is zero. The F2 having variance is a load-bearing empirical fact in quantitative
genetics. So "variance returns in F2" generalises past the two-allele case.

**Epistasis does not break it either — it breaks your arithmetic, in your favour's
opposite direction.** Under epistasis, F2 variance can *exceed* the additive prediction, which
is the basis of transgressive heterosis in wide crosses. So the clean "halving" story is
falsified, but "variance returns" survives. Net: your *qualitative* claim survives, your
*quantitative* one does not.

### 2.5 🔴 The load-bearing caveat that is not in the document at all

> **The F1-uniformity law is a law about *inbred lines*. It requires homozygous parents.**

Every F1-hybrid result — Levites' limitation paper, the whole seed industry — is about
crossing **inbred** parents. Your federated participants are **not** inbred. Each holds a
*distribution* over a hypothesis space, not a genotype. There is no literal F1, and the
premise the analogy rests on (two pure, maximally distant lines) has no counterpart in a
federation.

**This is the most serious limitation of the entire analogy, and it is absent from the
document.** It should be stated as a boundary condition on the thesis, not buried. The
variance-halving arithmetic survives; the *setup* does not transfer.

---

## 3. LANE A3 — the projector card is contradicted by your own §3

### 3.1 🔴 The kill costs zero citations, because you already did the work

Your §3 stationary-variance equation is

```
∂φ/∂t = D∇²φ − k(φ − φ*) + σξ
```

with **`σξ` described as additive stochastic noise** and the drift `D∇²φ` as a **diffusion
operator** — i.e. *continuous*. At `σ > 0` and `k > 0` the stationary variance is
`σ²/2k > 0`, **strictly positive**.

**So a continuous stochastic system already escapes the uniform state — in your own equation,
one section before you claim you need a discontinuity to do it.**

§6 asserts: *"Discontinuous updates. A projector is not a small step… the F1 collapse — which
is a *continuum* result — may not happen at all."* §3 asserts: continuous additive noise
produces a strictly positive equilibrium plateau. **Both cannot be true.** §3 wins, and it is
yours.

### 3.2 Is the projector claim a theorem, a heuristic, or false?

**A heuristic, and a weak one**, resting on an unstated premise: that the collapse result
depends on *continuity of the update*. It does not. The geometric collapse is a property of
the **stationary distribution of a Markov kernel**, and a projector is a Markov kernel like
any other — one that happens to be idempotent and rank-deficient. Non-continuity does not
prevent absorption; it usually *helps* it. A deterministic discrete projector on a finite
space is the most absorbing operator there is.

**The intuition "break continuity → different system" is a non-sequitur.** Continuity of the
update step is not what creates the fixed point. The fixed point comes from the **rank** of
the mixing operator. Break the rank and you have your escape; break the step size and you have
a rescaling.

### 3.3 And the external literature already showed a continuous system escapes — a century ago

In the exact model family you are borrowing from, the escape is classical and named:

**Goyal, Desai & Fisher (2012), "Dynamic Mutation–Selection Balance as an Evolutionary
Attractor", *Genetics* — DOI `10.1534/genetics.112.141291` · 128 citations — VERIFIED**, abstract:

> *"…any stable evolutionary state of a population in a static environment must involve a
> **dynamic mutation–selection balance**, where accumulation of deleterious mutations is on
> average offset by the influx of beneficial mutations."*

That is: a **continuous diffusion** process, whose stable state is a **non-zero-variance
attractor** explicitly framed as an *attractor*. It is the "chaotic-diffuse equilibrium" you
want, already published, already named, and reached by **adding continuous noise** — no
projector, no discontinuity.

**Your strongest card is gone.** Continuous diffusion escapes the uniform state, has done so
for a century, and the escape is not even exotic — it is the standard picture.

### 3.4 What survives of the quantum argument, demoted

Not the escape — only the **shape**. "Non-Gaussian amplitude structure" survives as a claim
about the *form of the stationary distribution*, not about reaching it. Rewrite §6 from
*"the strongest version of the claim"* to:

> A quantum measurement-based update is not required to escape the uniform state — continuous
> noise does that, and the stationary variance `σ²/2k` already reflects it. What a quantum
> update would change is the **shape** of the equilibrium distribution: `σξ` would be
> amplitude-structured rather than Gaussian, and the plateau would not be `σ²/2k`.

That is still a real, testable claim. It is much smaller. Its falsification test is now
**"measure the stationary distribution and check Gaussianity"**, not "check the uniform state
is unreachable."

---

## 4. LANE B — it is not made up, and it is not Granovetter

**Plain answer: it is a real body of work, you were reading it correctly, and the name you
want is *opinion dynamics* / *consensus formation*. The canonical model is DeGroot's, and
DeGroot's operators literally are weights.**

### 4.1 The primary source

**DeGroot (1974), "Reaching a Consensus", *Journal of the American Statistical Association* —
DOI `10.1080/01621459.1974.10480137` · 3,595 citations — VERIFIED** (also indexed
`10.2307/2285509`, 1,010 citations).

DeGroot's model: each agent holds an opinion; at each round it updates to a **weighted
average** of its own opinion and those of its network neighbours, with a mixing parameter.
That is **your F1 operator, with a knob, studied socially since 1974.** "The movement of
information across weight" is the movement of information across a **weighted network**, and
the weights in DeGroot's update rule are precisely the weights of the averaging. This is as
close to a source for your sentence as I can find, and I think it is the one.

### 4.2 The dynamic version — matches "sees and reflects" better than DeGroot does

**Friedkin & Johnsen (1990), "Social influence and opinions", *Journal of Mathematical
Sociology* — DOI `10.1080/0022250x.1990.9990069` · 1,200 citations — VERIFIED.**

An explicit dynamical system of opinions over a network, with a parameter trading **conformity
against independence** — which is the exact axis of "how much does averaging destroy what was
private." This is the closest thing in the literature to your §5, and it is a *dynamical
system*, not a static tie-strength taxonomy.

### 4.3 The one that studies the escape you are looking for

**Hegselmann & Krause (2002), "Opinion Dynamics and Bounded Confidence: Models, Analysis and
Simulation" — VERIFIED via OpenAlex title search (2,398 citations; OpenAlex carries no DOI
for the journal version, so no DOI is given).** In the bounded-confidence model agents average
**only with agents they already agree with**, and the central result is a **cascade to a small
number of factions**.

That is your F1 collapse, complete with an F2-shaped repair built into the model: the
confidence bound is a set-valued, per-agent admissibility rule. **Fifty years of sociology
on precisely your fixed point and precisely your escape.**

### 4.4 The Granovetter family is real but is the wrong one

You listed bridging/bonding capital, weak ties, structural holes. All real, all heavily
cited, all **about which edges carry information — not about averaging destroying it**:

- **Granovetter (1973), "The Strength of Weak Ties", *American Journal of Sociology* — DOI
  `10.1086/225469` · 39,118 citations — VERIFIED.**
- **Friedkin (1980), "A test of structural features of Granovetter's strength of weak ties
  theory", *Social Networks* — DOI `10.1016/0378-8733(80)90006-4` · 299 citations —
  VERIFIED.**
- **Marsden (1984), "Measuring Tie Strength", *Social Forces* 63(2) — DOI
  `10.1093/sf/63.2.482` · 1,267 citations — VERIFIED.** The operationalisation.
- **Burt's structural holes** — I did not resolve a clean citable record this pass.
  **UNVERIFIED. Do not cite without opening it.**

### 4.5 🔴 But here is the cut, and it goes the other way

Lane B is **double-edged**, and you should take both edges:

- **It confirms the sentence is not a fabrication.** You did not make it up. Credit where due.
- **It also means the operator is not new as an object of study.** DeGroot's weighted
  averaging *is* the F1 operator; its cascade-to-consensus failure mode has been studied since
  1974; bounded-confidence models are established repairs. "The averaging fixed point and how
  to escape it" is a **solved problem in a neighbouring field**, not a gap.

So: keep the sentence, cite DeGroot and Friedkin–Johnsen, and **delete the implication that it
points at untapped territory.** If anything the citation makes the gap claim *worse*, not
better, and you should know that before the document goes out.

---

## 5. LANE C — `micromoth-quilt` and "MOTHquantum"

### 5.0 First: `MOTHquantum` is not a repository

I tried six spellings against `api.github.com` — `MOTHquantum`, `MothQuantum`, `mothquantum`,
`moth-quantum`, `MOTH-quantum`, `MOTH` — **all HTTP 404.**

"MothQuantum" appears in fleet metadata only inside a **description string** ("springboard
lab (JEV/MothQuantum experiments)") and in the description of `quilt-quantumaudio-demo`. The
real repository is **`SuperInstance/MicroMoth-quilt`** (capital `M`), 498 files, Python, a
fork, last pushed 2026-09-30. I read it from a fresh clone at
`/workspace/scratch/scout2/mmq.log`.

**If `F1-F2-DIFFUSION.md` names `MOTHquantum` as a substrate, that name does not exist.**

### 5.1 🔴 It is not a mean field. It is not a population. It is a shot-based sampler.

You gave me an out — "if it's a mean field with extra steps, say so plainly." **It is not that
either, and that is the wrong diagnosis.** `micromoth.py` is 289 lines and is a **statevector
quantum circuit simulator**, a fork of MicroQiskit. Its entire mechanism:

- `simulate(qc, shots=1024, get='counts', noise_model=[])` — `micromoth.py:118`
- Build a `2^n` statevector `k` of `[real, imag]` pairs, initialised to `|0…0⟩`
- Apply gates as **deterministic linear maps on pairs of amplitudes**: `x`, `h`
  (`superpose`), `rx`, `rz` (`phaseturn`), `cx`, `crx`, `swap`, `init`
- Convert by Born rule — `probs = [e[0]**2 + e[1]**2 for e in k]`, `micromoth.py:222`
- **Sample** — `micromoth.py:255-258`: per shot, one `r = random.random()`, then an
  inverse-CDF walk over `probs` to pick a bitstring

A grep for `population|federated|mean.field|consensus|recombin` across **every `.py` in the
repo** returns **2 hits, both inside `receipts/` experiment scripts, neither in the
framework.** The word *agent* does not appear in the framework at all.

**There is no per-participant private state, no lattice, no averaging operator, no consensus
step, and no cross-agent interaction anywhere in the file.**

So the direct answer to Lane C question 3: **no, a discrete event process here does not
escape an averaging fixed point, because there is no averaging and no fixed point.** There is
one statevector per circuit. Your variance-collapse story has **no home in this substrate**,
because the substrate contains no aggregation.

### 5.2 🔴 The randomness is not independent of the private state. It is the inverse of your requirement

Your requirement: **inject variance, inject no information, independent of the private
signal.** In micromoth:

- The **draw** `r = random.random()` is `U(0,1)` with no argument and no dependence on
  anything. ✓ on the letter of the requirement.
- **But `r` is mapped through a distribution that is a deterministic function of the encoded
  private state.** `probs[j] = |U_j ψ⟩²` where `U` is the circuit and `ψ` is whatever was
  `init`-ed. The output bitstring is a **sample from the private posterior.**

**Your requirement is not "weakly satisfied." It is exactly inverted.** micromoth's
stochasticity is the *canonical information-bearing* stochasticity — drawing a sample is the
standard way to *extract* information. It is the opposite of `σξ`, and it cannot serve as
`σξ` for any amount of reinterpretation.

**And the `noise_model` is not a random draw at all.** `micromoth.py:226-236` applies
measurement error as a **deterministic reweighting** of the probability vector:

```python
probs[b0] = (1-p_meas)*p0 + p_meas*p1
probs[b1] = (1-p_meas)*p1 + p_meas*p0
```

That is a fixed linear channel. **It injects zero randomness.** If §6 treats
`noise_model` as the `σξ` term, that is a misreading of the code, and it should be corrected
before anyone builds on it.

### 5.3 🔴 The randomness is a Python standard-library PRNG, not a quantum source

A grep across every `.py` in the repo for
`quantum.?random|qrng|qutip|os.urandom|secrets.|numpy.random|default_rng` returns
**0 hits.** The complete RNG surface in the repository is:

| call | count |
|---|---|
| `random.seed(` | 27 |
| `random.random(` | 2 |
| `random.setstate(` / `random.getstate(` | 1 each |

That is the **Mersenne Twister from the standard library**. There is no quantum random
number source in `MicroMoth-quilt`. It is a classical PRNG wearing a quantum simulator's
interface, and any claim that the substrate supplies "quantum randomness" is unsupported by
the code.

Also: **`simulate()` takes no `seed` parameter** (`grep -c seed micromoth.py` → `0`). The
README's "under which seed" is implemented by the fleet's `tools/collapse_ledger.py` wrapping
the global `random`, not by the core. The core is not reproducible without monkey-patching
the global RNG.

### 5.4 🟢 But there IS a real population in that repo — in a receipt — and it states your thesis

This is the most useful thing I found this pass. There is exactly one place in
`MicroMoth-quilt` with a genuine population, stochastic per-individual operators and
recombination: **`receipts/exp015-illumination/exp015_qd_mapelites.py`**, a MAP-Elites
quality-diversity archive over quantum-circuit genomes.

And its own header comment states **your F1/F2 claim, independently, in fleet language**:

> *"one genome owns the population; a child that is interesting but not better-than-champion
> is **DISCARDED** every generation… If the archive holds elites at held-out balance > 0
> that champion search never promoted, **the freeze is partly an ELITISM artifact, not engine
> law.**"*

Read that against your document: **elitist selection is a deterministic
averaging-in-the-max operator** (everything not the champion is discarded → geometric
diversity collapse), and **the MAP-Elites archive is a set-valued replacement for it** that
holds diversity at a level rather than collapsing it. That is F1 versus F2, formulated in
receipt style, with a named experiment and a stated hypothesis.

**So the thesis does have a home in the fleet — but not in the repository the document
names, and not in the framework. It has a home in `exp015`, as a claim about elitism versus
archives, already in receipt form, with its own falsification criterion already written down.**

That is a better instance of your argument than micromoth is, because it is (a) a real
population, (b) with real per-individual stochasticity, (c) with a measurable diversity
quantity, and (d) already under test. The honest move is to make `exp015` the case study and
drop micromoth from the substrate argument.

---

## 6. CITATION HYGIENE — two things I nearly cited and did not

Both are new instances of the fabrication signature you already have on the record, and both
would have been undetectable without opening them:

- **`arXiv:1306.2081` is NOT Sinkhorn.** I believed it was *"Sinkhorn fixed points."* It
  resolves to **"model retrieval using global and local radial distances."** Not cited in this
  document. This is the round-number-adjacent failure mode again — a plausible arXiv ID
  recalled from memory rather than resolved.
- **`10.1086/323084` is NOT Hegselmann–Krause.** It resolves to a **pneumococcal immunology
  paper** — *"Immune-Mediated Phagocytosis and Killing of Streptococcus pneumoniae Are
  Associated with Direct and Bystander Macrophage Apoptosis"*, *J. Infect. Dis.*, 2001, 134
  citations. The `10.1086` prefix is shared across many journals (*AJS*, *JASA*, ASM
  titles), so **any plausible-looking `10.1086` DOI recalled from memory is likely wrong.**
  The Hegselmann–Krause reference above is cited from a title search with **no DOI attached**.

**Generalised rule, and I propose you adopt it: the `10.1086` prefix and any arXiv ID that
"feels" like a famous paper are the two highest-risk citation surfaces in this fleet.** Both
of today's near-misses were a real-looking ID bound to the wrong paper.

---

## 7. WHAT SURVIVES — the document, rewritten to what is true

If you want the smallest honest version of `F1-F2-DIFFUSION.md`, it is this. Four claims:

1. **Averaging is a projection.** FedAvg and consensus are idempotent, rank-deficient
   bistochastic operators whose image is the consensus subspace. They annihilate exactly the
   private directions. This is a statement about **rank**, not about randomness.
2. **The result is about information, not convergence.** Every treatment of non-IID
   heterogeneity frames it as slow convergence or client drift; the concept-space quantity
   is a different object from gradient variance. *(Unattacked this pass — see §0.)*
3. **The escape is spectral, and it is old.** A non-idempotent (ergodic) kernel has a
   non-degenerate stationary distribution, and continuous noise reaches it — that is
   mutation–selection balance, a century old, and it needs no discontinuity.
4. **The transfer is the contribution.** None of this is new as mathematics. What may be new
   is pointing it at a federated weight lattice, naming the projector, and using the
   difference between an idempotent and an ergodic mixing kernel as a **design criterion
   rather than a convergence diagnostic.**

**What must be deleted or restated:**

| Currently in the document | Action |
|---|---|
| "F1/F2 = different *kinds* of operator" (§2) | **Delete.** Replace with the idempotent-vs-ergodic statement (§1.4 above). |
| "restores it in one step" (§2) | **Delete.** F2 recovers **half** the parental variance (§2.1). |
| `Var_n = Var_0·2^(−n)` as your derivation (§1) | **Concede** to Wright's inbreeding coefficient, as `σ²/2k` was conceded. |
| "F1 uniform state reachable and absorbing" (§7 table) | **Restate** as asymptotically attracting in continuous spaces. |
| "discontinuous update is the strongest version" (§6) | **Demote** to a claim about the *shape* of the equilibrium distribution. |
| `noise_model` as the `σξ` term (§6) | **Correct.** It is deterministic (`micromoth.py:226-236`); it injects no randomness. |
| "quantum randomness" as substrate property (§6) | **Delete.** It is `random.random()`, stdlib Mersenne Twister. |
| `micromoth-quilt` as the F2 substrate (§6) | **Replace** with `exp015_qd_mapelites.py`, which is a real population and already tests the claim. |
| The sociology sentence (§5) | **Keep, cite DeGroot 1974 + Friedkin–Johnsen 1990.** Drop the "untapped" implication. |
| F1-uniformity as a general law | **Add the boundary condition:** it requires **inbred** parents. Federated participants are not inbred (§2.5). |
| — | **Add** the unstated design constraint: `k` must be computable from public state only (§1.5). |

---

## 8. WHAT I DID NOT DO

- I did not push anything, and did not touch another agent's file.
- I did not resolve a clean citable Sinkhorn paper for the bistochastic-convexity fact in §1.1.
  The claim stands as a standard theorem; the citation does not. Someone should pin it.
- I did not open **Burt, "Structural Holes"** — left `UNVERIFIED` rather than cite from memory,
  after two memory-recall failures this pass.
- I did not re-run the eight searches behind the framing-gap claim (§0, survivors 1' and 2').
  It was not pointed at this pass, and I am not re-asserting it as though I had attacked it.
- I have not read the `docs/F1-AUDIT.md` audit file or `F1/` in this repo; the falsification-table
  claims above are audited against `docs/F1-F2-DIFFUSION.md` only. If the audit already concedes
  some of these, §7 gets shorter, not longer.
