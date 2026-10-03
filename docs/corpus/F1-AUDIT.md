# F1-AUDIT — adversarial audit of `docs/F1-F2-DIFFUSION.md`

**Auditor:** Mathematics/analysis lane.
**Date:** 2026-10-01.
**Thesis audited:** `docs/F1-F2-DIFFUSION.md` (11,214 bytes, "nothing here has been measured").
**Code:** `F1/` — pure `python3` stdlib, no numpy/scipy. `python3 F1/run_all.py` reproduces every number below.
**Raw output:** `F1/out/results.json`, `F1/out/geometry.csv`, `F1/out/run.log`, 8 SVG plots.

---

## 0. Verdict up front

**The derivation is not unusually solid. There are seven errors, two of them
load-bearing, and the strongest claim does not survive.**

But the audit also found a real, defensible core, and I want to be as clear
about that as about the failures. Section 9 states it.

Ranked by damage:

| # | Claim | Verdict |
|---|---|---|
| 1 | "Cross is mixture" (§1) | **False.** Cross is a product/tensor. This is the root error. |
| 2 | F1 variance = Var₀/2 (§1) | **False.** It is exactly **0**. The law is a different operator. |
| 3 | Collapse rate 2⁻ⁿ, "not slow" (§1) | **Wrong by ~10³.** True rate is `1 − 4D sin²(π/N)`, scaling as **N²/D**. |
| 4 | `Var(∞) = σ²/2k`, "not by the topology" (§3) | **1-D: correct. Extended: wrong by up to 6.4×, and topology-dependent.** |
| 5 | F2 = `σξ` in that equation (§3) | **Self-contradictory.** `σξ` is a noisy F1 — the thing §6 says it isn't. |
| 6 | "Unreachable rather than slow" (§6, §7) | **False as stated.** Refuted for all 8 operators tested. |
| 7 | "Randomness must be independent of eᵢ" (§6) | **Inverted.** The thesis-compliant operator is the *only* one that collapses. |

---

## 1. Claim 1 — the variance identity. The algebra is right; the biology is not.

**The identity is exactly correct.** `Var((p+q)/2) = (Var p + Var q + 2·Cov)/4`,
verified by direct sampling to relative error **4.5e-16**. The i.i.d.
specialisation `Cov = 0 ⇒ V/2` is correct. Measured ratio 0.49950.

**But §1's sentence "In distributions, that is not a metaphor. Cross is
mixture" is false, and everything downstream leans on it.**

- A **cross** is `p ⊗ q` — a *product* (a coupling, a fixed linkage phase).
- The **mixture** is `(p+q)/2` — a *marginal*, the result of **forgetting the
  phase**.

These are different objects. The paper's own §4 argument — "the mean is not
invertible" — is an argument about the *mixture*. The F1 analogy is about the
*product*. The paper needs them to be the same object for §2 to work, and they
are not. The mixture is what you get by *projecting away* the very phase
information that F1 creates.

### The F1 variance is 0, not Var₀/2

The law `Var_n = Var₀·2^(−n)` describes **i.i.d. sampling of parents with
replacement** from a population of size N. The F1 cross is a different
sampling scheme: **two fixed, distinct, homozygous lines, no sampling at
all.** Every F1 individual gets one allele from each and is therefore
*identical to every other F1 individual*.

```
predicted by §1:  Var(F1) = Var₀/2 = 0.4995
actual:            Var(F1) = 0.0        exactly, in ONE generation
```

The population becomes a **single clone**. §1's own prose — "all the
between-parent variance is gone in one generation" — is right and *stronger*
than the formula printed beneath it. The formula is for a different process.

There is also a third rate, between the two, which the paper doesn't have:

| sampling scheme | variance ratio per generation | N=2 | N=8 | N→∞ |
|---|---|---|---|---|
| with replacement, i.i.d. | 1/2 | 0.5 | 0.5 | 0.5 |
| without replacement (disjoint pairing) | (1/2)(1−1/(N−1)) | **0** | 0.4286 | 0.5 |
| **F1 cross (fixed parents)** | — | **0** | **0** | **0** |

### §7's falsification table is unfalsifiable as written

Row 1 reads: *"Averaging variance decays geometrically, `2^(-n)`. If it fails,
my model of the operator is wrong. Check whether the real operator is a mean."*
The escape hatch is built into the prediction — an operator that doesn't decay
at 2⁻ⁿ is declared not-a-mean, but a mean-field update over a lattice, a global
FedAvg round, and a voter-model step are *all* means and *none* decay at 2⁻ⁿ.
Three of the paper's own §2 examples ("FedAvg, any weighted consensus, any mean
field update over a lattice") fail the paper's own test.

**Correction:** replace `2^(−n)` with the operator's actual spectrum.
`Var_n = Σ_q |λ_q|^{2n} Var_q(0)`, where `λ_q` is the operator's eigenvalue on
spatial mode `q`. Rate is a **spectrum**, not a constant.

---

## 2. Claim 1 applied — the collapse rate is ~10³× slower than claimed, and scales the *wrong way* with fleet size

This is the most quantitatively damaging finding, and it survives a direct
measurement.

For the diffusive averaging operator on an N-ring,

```
φ_i ← (1−2D)φ_i + D(φ_{i−1} + φ_{i+1})
```

Fourier mode `q` has amplification `a(q) = 1 − 4D sin²(q/2)`; the **variance**
is `|a|²`, so `V(t) = a(q)^{2t}`. The slowest mode is the smallest nonzero
`q = 2π/N`, so the collapse time is set by the **largest** length scale:

> **T½ = ln(1/2) / (2·ln(1 − 4D sin²(π/N))) ≈ 0.0088 N² / D**

Measured by **bisection on single pure Fourier modes** (exact arithmetic, no
fitting, no Monte Carlo), N = 256:

| D | mode | measured T½ | theory T½ | ratio |
|---|---|---|---|---|
| 0.125 | 2π/N | 4602.5 | 4602.7 | 0.99996 |
| 0.25 | 2π/N | 2301.5 | 2301.3 | 1.00011 |
| 0.4 | 2π/N | 1438.5 | 1438.2 | 1.00020 |
| 0.25 | 4π/N | 575.5 | 575.3 | 1.00040 |
| 0.25 | 8π/N | 143.5 | 143.8 | 0.99809 |

**For a 256-cell lattice at D = 0.25, the variance half-life is 2301
generations, not 1.** The paper's §1 — "It is not slow" — is wrong by a factor
of ~2.3 × 10³, and §7's "geometric collapse… not slow, and it does not plateau
at anything useful" is wrong about the speed.

And the direction of the error matters more than the factor:

```
T½ ≈ 0.0088 N²/D
N=64    →      909 generations
N=256   →    4,602 generations
N=1024  →   73,646 generations
N=4096  → 1,179,000 generations
```

**More participants ⇒ collapse quadratically slower.** The paper's framing has
"the more averaging, the faster the F1 state" and "more rounds" as the
remedy. The actual physics of a mean-field update is the opposite: **scale
makes the F1 state slower to reach, not faster.** A 4096-cell lattice is about
five hundred times *further* from uniform than a 256-cell one, per round, than
the paper's model says.

**Caveat, stated honestly:** the paper may have meant the *genealogical*
process (each generation a fresh i.i.d. draw of two parents), where 1/2 per
generation is exactly right. That process is not FedAvg and is not a mean-field
update over a lattice. Either reading is wrong for the operator the paper
actually names in §2. The document has to pick one, and it currently mixes them.

---

## 3. Claim 2a — `σ²/2k` in one dimension. **Correct.** Confirmed.

The user's suspicion was that the constant is unverified. It is right.

Direct simulation of `x ← (1−kΔt)x + σ√Δt·z` with the **exact** OU transition
(zero discretisation bias), 120 independent runs per point, batch-means error
bars:

| k | measured | exact | z-score |
|---|---|---|---|
| 2.0 | 0.25010 ± 0.00249 | 0.25025 | −0.06 |
| 0.5 | 0.99278 ± 0.01960 | 1.00025 | −0.38 |
| 0.2 | 2.36306 ± 0.06776 | 2.50025 | −2.02 |

**`Var(∞) = σ²/2k` in 1-D is confirmed.** Three qualifications, none fatal:

1. **Convention-dependent.** It requires `⟨ξ(t)ξ(t′)⟩ = δ(t−t′)`. With the
   physicist's `2δ`, the answer is `σ²/k`. The paper does not state the
   convention. Worth one sentence.
2. **Discretisation bias is O(kΔt).** Exact discrete answer is
   `σ²Δt/(1−(1−kΔt)²) = σ²/(2k − k²Δt)`. At `kΔt = 1` it is `σ²/k`, a factor
   of 2. So a *quantum-discontinuous* update (§6) does not inherit the
   continuum constant — a real, if small, point in the paper's favour.
3. **It is a per-degree-of-freedom answer.** One mode, or one cell with no
   spatial coupling. Not the field. That is §3b.

---

## 4. Claim 2b/3 — the d-dimensional form. **The user is right, and the error is large.**

The paper's instinct to doubt this was correct. `σ²/2k` is **not** the
stationary variance of the field.

### The exact answer

On a periodic box, the Laplacian is diagonalised by the Fourier basis, so each
mode is an **independent** OU process with its own relaxation rate

```
λ_q = k + D q²            (not k — the diffusion term contributes)
Var(mode q) = σ² / (2 λ_q)
V_field = Σ_q σ² / (2(k + D q²))          by Parseval
```

`σ²/2k` is recovered **only if `λ_q = k` for every mode**, i.e. only if
`k ≫ D q_max²`. It is a statement about **one mode**, not about a field.

### The geometry factor

Define `G = V_field / (σ²/2k)`. Measured from the paper's own equation
(exact OU transition, 40,000-step time average, N=128):

| k (=D) | simulated V_field | closed form | sim/exact | **per-cell ratio to σ²/2k** |
|---|---|---|---|---|
| 0.1 | 100.749 | 99.951 | 1.0080 | **0.156** (off by 6.4×) |
| 1.0 | 28.647 | 28.622 | 1.0009 | **0.447** (off by 2.2×) |
| 10.0 | 5.411 | 5.409 | 1.0004 | **0.845** (off by 1.2×) † |
| 100.0 | 0.6278 | 0.6276 | 1.0004 | **0.981** |

The simulation reproduces the closed form to 0.1–0.8% across four decades, so
this is a test of the paper's formula, not of my integrator. † the `k = 10`
row is from the same routine run separately; `run_all.py` sweeps `k = 0.1, 1,
100` and `out/results.json → sde_sim` holds all four.

And `G` is not a small correction. It ranges over **six orders of magnitude**:

| system | G at k/D=1e−4 | G at k/D=1 | G at k/D=1e3 | limit k≫Dq² |
|---|---|---|---|---|
| d=1, N=64 | 1.03 | 28.6 | 63.9 | → N = 64 |
| d=1, N=256 | 1.49 | 114.5 | 255.5 | → N = 256 |
| d=1, N=1024 | 5.12 | 457.9 | 1022 | → N = 1024 |
| d=2, N=32 (1024 cells) | 1.06 | 260.1 | 1020 | → N² = 1024 |

**`G → N^d`**, i.e. `V_field = N^d · σ²/2k`. The paper's answer is the
*per-cell* answer, and only in the top regime.

### Three consequences the paper does not draw

**(a) The paper's k-dependence is wrong where it says the interesting regimes are.**
Measured `d(log v)/d(log k)`:

| regime | d=1, N=1024 | d=2, N=32 |
|---|---|---|
| `k ≫ Dq_max²` (the paper's regime) | −1.000 | −0.999 |
| **crossover** | **−0.520** | **−0.200** |
| far IR | −0.985 | −1.000 |

The paper says *"the interesting regimes are the ones in between."* Those are
exactly the regimes where the exponent is **−0.52 and −0.20**, not −1. The
formula is right only where the paper says nothing interesting happens.

**(b) "Not by the topology" is flatly false.** `G` depends on `N`, on `d`, and
on `D/L²`. There is a critical selection strength

```
k_crit = D · 4 sin²(π/N)   (  d=1, N=256, D=1 → 6.0e-4  )
```

Below it the per-cell plateau becomes **independent of `k` entirely** — set by
geometry alone. "Diversity is set by the ratio of noise amplitude to selection
strength — not by the data, not by the topology" is wrong on the topology
clause, in a large part of parameter space.

**(c) The single-mode answer describes two different physical quantities.**
At small `k` the whole field variance is the **`k = 0` (mean) mode** drifting:
`V_field ≈ σ²/2k` is the variance of the *fleet centroid*, not of the spread
between agents. At large `k` it is the *per-cell* spread. Same formula, two
quantities. §6 asks "check whether the equilibrium is Gaussian" — in a unimodal
OU it **always is**, so that test has no power. The discriminating observable is
**bimodality**, or the scaling of `V` with `σ` (unimodal: `V ∝ σ²`; bimodal:
`V ∝ σ⁰` below the barrier).

### Ablation — is any term inert? No, and that is the point

| k | D | regime | V_field | per-cell | paper |
|---|---|---|---|---|---|
| 0 | any | **no stationary state at all** | ∞ | ∞ | — |
| 0.5 | 0 | each cell an independent OU | 128.0 | **1.000** | 1.000 |
| 0.5 | 1 | full equation | 42.67 | **0.333** | 1.000 |
| 2.0 | 0 | each cell an independent OU | 32.0 | **0.250** | 0.250 |
| 2.0 | 1 | full equation | 18.48 | **0.144** | 0.250 |

`D = 0` reproduces the paper exactly. Adding the paper's *own* diffusion term
changes the plateau by 3× and bends the slope. **The diffusion term is not
inert, and §3's formula assumes it away without saying so.**

**And `k → 0` is wrong in kind.** §3: *"`k→0` recovers total diffusion into one
blob."* At `k = 0` there is **no stationary distribution**; the `k=0` mode is a
free particle and `V` grows as `σ²t` without bound. That is **delocalisation**,
the opposite of a blob.

---

## 5. Claim 4 — "the F1 collapse is a theorem about continuous averaging."
**A heuristic, not a theorem. Three independent failures.**

The paper flags this as its strongest claim and its least supported. It is
also, as stated, **false**.

### Failure 1 — "unreachable" is a category error

§7's last row, the load-bearing one: *"Quantum-discontinuous update makes the
uniform state **unreachable**, not merely slow."*

Every operator I tested has the constant field as an explicit fixed point.
Feeding a constant field returns a constant field in **zero steps**:

| operator | discontinuous? | uniform state reachable? |
|---|---|---|
| global mean | no | **yes** |
| neighbour mean, D=0.25 | no | **yes** |
| neighbour mean, max step | no | **yes** |
| **median-3** | **yes** | **yes** |
| **quantised mean** | **yes** | **yes** |
| **rank-1 projector** | **yes** | **yes** |
| **orthocomplement projector** | **yes** | **yes** |
| **random rank-4 projector** | **yes** | **yes** |

**8/8 reachable.** The claim that is cheap to test (§7: *"the last row is the
load-bearing one and it is cheap to test"*) fails the cheapest possible test.

"Unreachable" requires an invariant — a conserved quantity, a projection, a
constraint — that *excludes* the uniform state. **Nothing in a discontinuous
update supplies one.** What discontinuity can do is make the uniform state
**non-attracting**, which is a different and much weaker claim.

### Failure 2 — the paper's own mechanism is the average

§6 proposes **"discontinuous updates. A projector is not a small step."** But:

> **A rank-1 projector onto the uniform direction *is* the average operator.**
> Measured: `V = 0` after **one step**, from any initial condition.

Orthogonal projection onto the uniform direction is `φ ↦ mean(φ)·1`. It is
linear, idempotent, mean-reverting, and the fastest collapse in the whole
study. A projector is the paradigm case of a *destructive, mean-reverting*
operator, not an escape from one.

Worse, the *other* projector — onto the **complement** of the uniform
direction — is the one that genuinely makes the uniform state unreachable in
one step. And it is **the single most information-destroying operator
available**: its kernel is the entire uniform direction. Measured: it holds
`V = 0.947` forever while the system is now completely determined by the
projector.

> **The mechanism the paper proposes for reaching a non-uniform state is the
> one operator that maximally destroys the between-participant information
> that §4 spends the whole document defending.**

This also shows "variance" is the wrong observable: the most destructive
operator in the study shows a *permanently high* variance.

### Failure 3 — a real phenomenon, attached to the wrong conclusion

Two non-uniform absorbing states do exist, and I should report them because
they are the strongest thing on this side of the ledger:

**(a) Median-3 converges to a non-uniform fixed point at V = 0.318 in ~10
generations and stays there forever.** These are the *root signals* of median
filtering — a well-known ringing pathology of the median operator, not a
diversity mechanism.

**(b) The max-step averaging operator `φ_i ← ½(φ_{i−1}+φ_{i+1})` has an
exact non-uniform fixed point: the alternating pattern.** Amplification is
`|a(q)| = |cos q|`, which equals 1 at `q = π`. Measured: alternating init,
`V(t) = 1.000000000000` at t = 0, 1500, 3000. **A pure, continuous,
deterministic averaging operator with a non-uniform absorbing state.**

Both are **repelling, not unreachable.** The uniform state remains a fixed
point, trivially reachable, in every case.

**Where the paper has a real instinct:** the paper's §6 intuition that
"a small-diffusion limit does not apply" to a discontinuous update is *correct*
— but it is a statement about the **geometry factor crossover** of §4b, and it
points the wrong way. Discontinuity doesn't make the uniform state unreachable;
it **removes the constraint (`k ≫ Dq²`) that made the formula well-defined.**
The honest version of the claim is about the *validity of a constant*, not
about reachability.

---

## 6. Claim 5 — the model's F2 is a noisy F1. **Self-contradictory, and central.**

This is the finding I did not expect, and it is the most damaging.

§2's generalisation: *"Deterministic averaging collapses variance
geometrically. Stochastic recombination restores it in one step and can hold it
at a set level."*

§3 then models stochastic recombination as **`σξ`, additive noise in the
diffusion equation.**

**Additive noise in a diffusion equation is a noisy F1.** It is a continuous
perturbation of the same operator. §6 says explicitly that F2 must be
*"not a noisy F1"*, and then §3's equation is exactly one. The document
criticises the quantum case for doing what its own central model does.

Concretely, there are **three** different operators hiding under "F2", with
three different behaviours, and the paper treats them as one:

| # | operator | what it is | measured behaviour |
|---|---|---|---|
| 1 | blend: `x_i ← (x_a+x_b)/2` | **averaging** | variance **halves** — this is the F1 |
| 2 | crossover: `x_i ← x_a` or `x_b` | resampling | collapses by drift, half-life ~N |
| 3 | additive: `x_i ← x_i + σz` | perturbation | `V` grows **without bound**; no plateau |

**Operator 1 is what "recombination" naively means, and it is an averaging
operator — an F1, not an F2.** Measured (`pop_blend`, §7 below): the
paper's `2^(−n)` reproduced exactly, `selfavg → 0`.

### The real F2 knob is different, and bounded

In a finite population the honest F2 stationary variance is a **Wright–Fisher**
quantity:

```
Var(p*) = μ(1−μ) / (2N + 1)                       (neutral)
Var(p*) = μ(1−μ) / (1 + 8 N ν(1−ν))                (symmetric mutation/recombination rate ν)
```

Two structural differences from `σ²/2k`:

- **It is bounded by `μ(1−μ) ≤ 1/4`.** `σ²/2k` is unbounded in `σ` — you can
  crank noise to any diversity. **A recombination model over a finite set of
  parental values cannot manufacture diversity beyond the parental spread.**
  The paper's knob is a knob that exists *only because it smuggles in
  continuous noise* — the very F1-ish operation it claims to replace.
- **The knob is `N`, not `σ/k`.** The loss rate is drift, `1/(2N)`; the gain
  rate is `ν`. **More participants ⇒ more diversity preserved.**

### The mechanism mismatch

F2's 1:2:1 is **heterozygote advantage**: a **bimodal** fitness landscape. The
paper's `−k(φ−φ*)` is a **unimodal**, mean-attracting potential. A bimodal
potential has no single attractor; the interior point is a **saddle**. **The
paper's model cannot represent F2's actual mechanism**, which is why it needs a
plateau to come out right and why the plateau is Gaussian when F2's is not.

### And: F2 is not a plateau, it is a timescale

Measured directly, diploid Wright–Fisher, N=32, 300 replicates, started in the
F1 state (every individual heterozygous, phenotypically identical — exactly as
§1 describes), self-averaged variance:

| w_Aa | s | diversity half-life | ×neutral | variance at gen 3000 |
|---|---|---|---|---|
| 1.0 | 0 | **41.7 gen** | 1.0 | 0.000 |
| 1.1 | 0.1 | 64.9 | 1.6 | 0.000 |
| 1.3 | 0.3 | 116.1 | 2.8 | 0.000 |
| 2.0 | 1.0 | 647.4 | 15.5 | 0.005 |
| 4.0 | 3.0 | **8444.0** | **202** | **0.066** |

F2's "set level" is a **half-life of order N/s generations**, not a stationary
level. §7's prediction *"The equilibrium variance is σ²/2k, Gaussian"* has no
corresponding finite-population object.

---

## 7. The controls. **These are the deliverable, and they invert §6.**

### 7a. Mismatched-recombination control — the requirement is **inverted**, not merely weaker

The user asked: if correlated recombination also holds the variance, the
independence requirement is weaker than claimed. **Run it, and the answer is
much worse than that.**

The thesis (§6) requires: *"the randomness must be independent of eᵢ. That is
a real, checkable constraint."*

Measured, N=32, 1000 generations, self-averaged variance (the between-participant
diversity — what §4 says *is* the information):

| recombination operator | correlated with eᵢ? | self-averaged V at end | spread at end |
|---|---|---|---|
| independent crossover — **thesis-compliant** | no (as required) | **0.0000** | 0.995 |
| crossover + independent recombination (rate 0.01 / 0.10) | no (as required) | **0.0000** | 1.012 / 0.941 |
| **disassortative** (recombine maximally *dissimilar* parents) | **yes** | **2.2298** | 3.313 |
| assortative (recombine maximally *similar*) | **yes** | **0.0000** | 0.160 |

> **The thesis-compliant operator is the only one that collapses. The
> forbidden correlated operator is the only one that holds diversity.**

**The §6 constraint, applied to a finite population, is a guarantee of the
collapse it exists to prevent.**

The mechanism is not subtle. Recombination among a finite set of existing
values is **resampling**. It conserves the allele frequency and destroys
within-population diversity to drift, at rate `(N−1)/N` per generation
(half-life `0.69N` generations — 21.8 for N=32; the paper claims 1). Adding
independent recombination does not help, because independent recombination is
still resampling. What holds diversity is **state-dependent diversifying
selection** — negative frequency dependence / disassortative mating /
heterozygote advantage — which is *by construction* a function of the current
state, hence correlated with the private signal.

**The honest reframing of §6:** independence is not required for the
*diversity*; it is only required for the diversity to be **uninformative about
eᵢ**. Those are separable, and the paper conflates them. Correlated
recombination does buy a plateau — it also buys a *different equilibrium shape*
(non-Gaussian, structured, and genuinely informative about `eᵢ`). That is a real
and testable difference, and it is a much weaker claim than §6 makes.

### 7b. Seed / initial-condition control

| seed | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| self-averaged V after 1000 gen | 1.9e−31 | — | — | — | — | — | — | — |

mean 1.963e−31, stderr 2.88e−32 — the collapse is not a seed artifact.

Diffusive averaging, N=256, 3000 steps, five qualitatively different starts:

| initial condition | V₀ | V_final |
|---|---|---|
| Gaussian | 0.947 | 0.00507 |
| bimodal ±1 | 1.000 | **0.000** (annihilated in one step) |
| single spike | 38.91 | 0.132 |
| linear ramp | 0.336 | 0.084 |
| constant (already uniform) | 3.2e−30 | 3.2e−30 (fixed, as it must be) |

The last row is the §4/claim-4 test again: a constant field is a fixed point of
the diffusion operator too. **The uniform state is reachable and absorbing for
the continuous operator as well** — which is precisely why the paper's
"continuity is what causes the collapse" framing is wrong.

### 7c. Null control — is any term inert?

No. Table in §4. Every term does substantial work, `D=0` is the only row that
reproduces the paper, and `k=0` has no stationary state at all. The paper's
formula is the answer *with one of its own three terms switched off.*

---

## 8. Claim 3 — averaging is many-to-one. **Correct, but weaker than stated, and in tension with the paper's own premise.**

The user was confident here, and is right to be. But two things need fixing.

**The sharp version is a theorem and it's good:** the mean is the orthogonal
projection onto `span{1}`; its kernel is the `n−1`-dimensional zero-sum
subspace. Verified: rank 1, fibre dimension 5 for n=6, two federations
differing by a kernel vector give bit-identical means (|Δmean| < 1e−16) while
sitting √1.83 apart in L². Stronger than the paper states and defensible as
stated: **not just the final average but the entire trajectory of the average
is a deterministic function of the initial state, so the trajectory carries no
recovering information either.**

**But the paper's version is trivially true of every non-injective map.**
*"Two federations with completely different private knowledge can produce
identical averages"* is a property of having a non-trivial kernel — true of
`max`, of a median, of a 1-bit sketch, of a hash, of every lossy aggregator
that has ever existed. It does **not** distinguish averaging. As a critique it
targets the problem class (aggregation that outputs only a mean), not the
operator. Alternatives exist — per-participant anchors, multiple sketches,
secure aggregation returning the multiset, low-rank+residual — and they do not
suffer it. §7's "directly checkable and I am confident" is checkable and
passes, but it would pass for almost any system.

**The internal tension:** §4 assumes **sparse** per-participant information.
Sparsity means the private data is low-dimensional. **Sparsity is precisely
the condition under which the mean is closest to injective.** If only one
participant is active per round and the active set is known, the mean
*locates* the active data. The paper uses sparsity to motivate the problem in
the same paragraph where it destroys its own argument.

**A more useful quantity the paper does not give:** the mean retains
approximately **one participant's worth** of information about the typical
value. Averaging conserves `1/n` of the private data, not 0. That is a
quantitative resource statement, it is true, and it is more actionable than
"destroyed."

---

## 9. What survives, stated as clearly as if I had written it

The user asked for this explicitly. Here it is.

**S1. Averaging is a linear projection with a non-trivial kernel, and the
between-participant component of the private data is annihilated by it. This
is a theorem, not a heuristic.** The fibre is the zero-sum subspace; two
federations differing by any zero-sum vector are indistinguishable to the
federation forever, including through the average's whole trajectory. §4 is
correct and is the most solid part of the document. *Recommendation: keep it,
and add the resource statement ("conserves 1/n") and drop the claim that this
is distinctive of averaging.*

**S2. There is a genuine design knob, and it is worth being explicit about —
but it is not `σ²/2k`.** The equilibrium is a balance between an injection rate
and a loss rate, and:

- in the **unimodal** (additive-noise) model the plateau is `σ²/2k` **per
  degree of freedom**, times a geometry factor `G(N, d, D/k)` that ranges over
  six orders of magnitude, and only equals 1 for `k ≫ D(L/π)²`;
- in the **recombination** model the plateau is `μ(1−μ)/(1 + 8Nν(1−ν))` —
  bounded by ¼, set by **N**, and not unbounded in any noise amplitude;
- in the **F2** model there is no plateau, only a **half-life of order N/s**.

The paper's most valuable instinct — *that the equilibrium is a designed
balance rather than a property of the data* — is **correct and is the part of
§3 worth keeping.** The specific formula is not.

**S3. Deterministic averaging does reach the uniform state, and the paper is
right that no amount of further averaging recovers what it destroyed (S1).**
The paper is wrong about *how fast* — by a factor of ~2.3×10³, with the rate
`∝ N²/D`, i.e. **larger fleets are further from uniform, not closer**. This
corrects §1 and §7 row 1 and it is a genuinely important result for
`micromoth-quilt`: scale buys time.

**S4. Discontinuity is not what saves you, but something adjacent to the
paper's instinct is real.** Non-uniform absorbing states exist under
discontinuous operators (median root signals: `V = 0.318` permanent) and even
under a *continuous* averaging operator at its max stable step (the
alternating mode: `V = 1.000000000000` exactly). But in all 8 operators tested
the uniform state remains **reachable in zero steps and absorbing**. The
useful reframing is not "break the continuity" but **"break the attractor"** —
which needs a *conserved constraint excluding the uniform direction*, and the
cheapest such constraint is a projector, which is the most destructive operator
in the study. §6.2's instinct that a projector changes the operator is right;
its conclusion is backwards.

**S5. §5 is untouched by this audit and appears sound.** The two readings of
"movement of information across weight" are well posed, and the observation that
(b) changes the *operator* rather than the parameters is the right one. It is
also the only part of the document where the paper correctly distinguishes
"changes the operator" from "noisy version of the same one" — a distinction it
then fails to apply to its own §3.

---

## 10. Priority list for the corrected document

1. **Delete "Cross is mixture"** and replace §1 with the product/mixture
   distinction. Replace `2^(−n)` with the operator's spectrum; state which
   operator is meant.
2. **Fix the F1 variance to 0**, not `Var₀/2`. The prose was right; the formula
   under it was not.
3. **Replace §3's formula** with `V = (σ²/2)Σ_q 1/(k + Dq²)`, state the
   `k ≫ Dq_max²` condition, give the geometry factor, and either delete
   "not by the topology" or qualify it hard.
4. **Drop `k→0` = "one blob."** It is delocalisation; there is no stationary
   state.
5. **Split "F2" into three operators** and say which one is meant. §3's `σξ`
   is a noisy F1 — the document already says that is not F2.
6. **Rewrite the §6 discontinuity claim** from "unreachable" to "not
   attracting," and add: a projector onto the uniform direction *is* the mean.
7. **Invert the §6 independence constraint.** Correlated recombination is what
   holds diversity; the constraint only buys a non-informative plateau, not a
   plateau. Replace `σ²/2k` as the knob with `N` and `s`.
8. **Fix §6.1's test.** Gaussianity has no power under a unimodal OU — it is
   always Gaussian. Use bimodality, or the `V ∝ σ²` vs `σ⁰` scaling.
9. **Rewrite §7's table** so each row is falsifiable without an escape hatch.
   Add the row that actually settles §6: *feed a constant field; if it stays
   constant, the uniform state is reachable and absorbing.*
10. **Soften §4's distinctiveness claim** and add the "conserves 1/n"
    formulation. Note the tension with the sparsity premise.

---

## Appendix — reproducing this

```bash
cd F1
python3 run_all.py            # ~5 min, full
python3 run_all.py --quick    # ~1.5 min
```

| file | contents |
|---|---|
| `f1_core.py` | claim-1 algebra, F1 operator, Wright–Fisher closed forms, projection kernel |
| `f1_core2.py` | OU verification, **geometry factor** `V_field/σ²/2k`, overdominance fixed points |
| `f1_sim.py` | lattice operators (8), population operators (7), uniform-state reachability test |
| `f1_plot.py` | SVG plotting, stdlib only |
| `run_all.py` | driver; writes `out/results.json`, `out/geometry.csv`, 8 SVGs |
| `out/1-collapse-operators.svg` | variance trajectories, 8 deterministic/discontinuous operators |
| `out/2-sde-vs-paper.svg` | the paper's equation, simulated, vs `σ²/2k` |
| `out/3-geometry-factor.svg` | G vs k/D — the omitted factor, 1 to N^d |
| `out/3b-per-cell-ratio.svg` | per-cell variance ÷ `σ²/2k` |
| `out/4-population-two-variances.svg` | the two meanings of "variance" |
| `out/5-control-mismatched-recombination.svg` | **§6 inverted** |
| `out/6-control-initial-conditions.svg` | five initial conditions |
| `out/7-f2-mechanism.svg` | F2's real mechanism, with and without state dependence |
| `out/8-ablation.svg` | is any term inert? |

**Methodological notes, including two corrections to my own work:**

- The first OU estimator used a naive variance on a strongly autocorrelated
  series and read 0.93 against a true 1.0. Replaced with independent replicates
  and batch means.
- A first pass at the diffusion half-life was off by exactly 2× because the
  **variance is the square of the amplification factor**. The simulation was
  right; the analytic line was wrong. All numbers above are post-fix, and the
  bisection check now agrees with theory to ≤ 2e−4.
- The SDE time-average was initially taken over 13 log-spaced snapshots of a
  slowly-mixing quantity, reading 40% high. Replaced with a per-step
  accumulator; now agrees with the closed form to 0.1–0.8%.
