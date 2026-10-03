# Scout 1 of 4 — `SuperInstance/superinstance-papers` → `white-papers/`

**Question:** Which of these papers states a theorem, which states a design, which states a
measurement — and does the repo itself know which is which?

**Method note.** Every math claim below was re-derived *before* the paper was read
(`/workspace/projects/fleet-triage/derive/*.py`), then compared. Scripts: `exact.py`, `thm21.py`,
`lattice.py`, `table.py`, `cascade.py`, `thm21_counter.py`, `ocds.py`, `ratestate.py`.

**Repos read:** `SuperInstance/superinstance-papers` (shallow clone, HEAD), plus
`SuperInstance/constraint-theory-core` (shallow clone, HEAD `df9ce63`) for the cross-check in §3.
No token needed. `cargo` is not installed in this sandbox, so the crate was read, not executed;
every claim about it below is from source + independent re-implementation of its algorithm in
Python.

---

## 0. Headline numbers

| Question | Answer |
|---|---|
| Files in `white-papers/` | 42 `.md` + 5 subdirectories |
| Classified **THEOREM** (≥3 formal theorem headers) | **9** |
| Classified **DESIGN** | **28** |
| Classified **MEASUREMENT** | **5** |
| Files carrying **any falsifier** (what would make the claim wrong) | **2 / 42** (4.8%) |
| Total `**Theorem` headers across the slice | 128 |
| Total `**Proof` headers | 119 |
| READMEs examined claim-vs-paper | 7 |
| READMEs that are **promotional** rather than honest abstracts | **7 / 7** |
| Single most overstated claim | `04-Pythagorean-Geometric-Tensors.md:79-85` — see §4 |

**The repo does not know which is which.** There is no front-matter, no `Status: Theorem|Design|
Measurement` field, no machine-readable manifest, and no single document that classifies the
papers. The *only* self-classification signal in the entire directory is a per-README
`Paper Statistics` table, and that table tracks a metric — "**Theorems & Proofs: N formal
proofs**" — which is wrong in **4 of the 7** READMEs that carry it (§2.3). The one axis the
repo chose to publish a number for is the axis it gets wrong most often.

---

## 1. Classification — 42 files

Method: a file is THEOREM if it carries ≥3 `**Theorem` headers; MEASUREMENT if it carries ≥5
empirical/simulation/benchmark markers and few theorems; otherwise DESIGN. Full table in
`derive/../` — the per-file counts are reproducible with the script in §6.

### THEOREM (9)
| File | Thms | Proofs |
|---|---|---|
| `06-Tile-Algebra-Formalization.md` | 27 | 7 |
| `rate_based_change_mechanics_mathematical_appendix_round6.md` | 25 | 23 |
| `01-SuperInstance-Universal-Cell_mathematical_appendix.md` | 15 | 14 |
| `04-Pythagorean-Geometric-Tensors.md` | 11 | 12 |
| `round13-08-Tile-Algebra-Formalization-COMPLETE.md` | 11 | 1 |
| `03-Confidence-Cascade-Architecture.md` | 11 | 3 |
| `rate_based_change_mechanics_section_round6.md` | 7 | 2 |
| `05-SMPbot-Architecture.md` | 6 | 1 |

### MEASUREMENT (5)
`02-SuperInstance-Type-System.md` · `29-Spreadsheet-as-Cell.md` ·
`03-Confidence-Cascade-Architecture-README.md` · `PAPER_ROADMAP_REMAINING.md` ·
`SMPbot_Architecture_White_Paper_7.md`

### DESIGN (28)
Everything else, including `16-Five-Laws-of-Cellular-Architecture.md`, `11-Cell-Model-Older-Than-
Spreadsheets.md`, `02-Visualization-Architecture.md`, and all 20 numbered `1x`–`2x` Quilt papers.

**Two observations that matter more than the counts:**

1. **`02-SuperInstance-Type-System.md` is 47,577 bytes and contains zero theorems, zero proofs and
   zero lemmas** — it is classified MEASUREMENT, but grepping it finds no sample size, no dataset,
   no n, no error bars. It is a taxonomy with numbers in it, not a measurement. The classification
   is the best available given no manifest, and it is wrong.

2. **`16-Five-Laws-of-Cellular-Architecture.md` presents five things called "Laws" and gives each
   one a justification section of the form "This law is true because it emphasizes the importance
   of…"** (lines 16, 42, 71, 95, 121). A law that cannot be violated is not a law. These are
   design principles wearing the grammar of theorems, and the paper never says so.

---

## 2. The READMEs are promotional, not honest abstracts

Seven READMEs sit next to papers. I traced a claim in each to the passage it summarises.
**7 of 7 are stronger than, different from, or unsupported by the paper.** None is weaker. Not one
adds a caveat the paper does not contain.

### 2.1 PGT — "Theorem 2.1: Proven orthogonality" (README stronger than paper, paper FALSE)

- README `04-Pythagorean-Geometric-Tensors-README.md:32`: "**Theorem 2.1**: Proven orthogonality via
  Frobenius inner product"
- Paper `04-Pythagorean-Geometric-Tensors.md:77-85`: states the theorem, gives a two-sentence
  "proof" ending "…ensuring that the integral of their product over all orientations vanishes."

**Re-derived first, then checked.** Definition 2.1 (`04-Pythagorean-Geometric-Tensors.md:68-73`)
defines `T_ij = (a_i a_j + b_i b_j)/c` where `a`, `b` are *orthogonal unit vectors*. Then:

- `T : T = (a·a)² + (b·b)² = 1 + 1 = 2` — for **every** triple. The `1/c` cancels; `c` never
  appears in the result.
- The theorem asserts `T : T = c²` — i.e. 25 for (3,4,5), 169 for (5,12,13).
- **The theorem contradicts the paper's own definition by a factor of c²/2.** Measured in
  `derive/thm21.py`.

Worse, the orthogonality is **false**. With `T_θ = u uᵀ + v vᵀ` for an orthonormal pair at angle θ,
the cross term is `cos(2Δ)`, not 0:

- `T_(3,4,5) : T_(5,12,13) = cos(2 × 14.25°) = 0.8788` — the theorem claims 0. (`derive/thm21.py`)
- The Gram matrix of the 4-triple basis is full-rank and has off-diagonal entries 0.936–0.995.
  Four mutually orthogonal vectors cannot exist in 2-D. The basis is over-complete by construction.

The "proof" invokes "the integral of their product over all orientations," but no integral, no
measure, and no orientations are ever defined. **The README's word "Proven" is doing work the
paper does not do, and the paper itself is wrong.**

### 2.2 Confidence Cascade — README numbers are in no table in the paper (README unsupported)

- README `03-Confidence-Cascade-Architecture-README.md:52-60` publishes a 4-row results table:
  Fraud "3.2% → 0.4%, 8× reduction"; Quality Control "12s → 2.1s, 5.7× faster"; Network Security
  "47% → 6%"; Manufacturing "23 → 2 false alarms/day, 91% fewer".
- Paper `03-Confidence-Cascade-Architecture.md:374-382` has a **different** table: False Positive
  Rate "3.2% → 1.1%, **65%** reduction"; User Complaints "2,847 → 458/month, 84%"; Average Speed
  "2.3s → 1.1s, 52% faster".
- The README's `3.2%` is the paper's *before* value, but the README's `0.4%` / `8×` exists nowhere.
  Same for `12s`, `2.1s`, `5.7×`, `47%`, `6%`, `23/day`, `2/day`.
- The `91%` in the README is lifted from a *different experiment* entirely:
  `03-Confidence-Cascade-Architecture.md:480` reports "Transition oscillations eliminated | 91% | 82%"
  for an **autonomous-driving** table. The README presents it as a manufacturing false-alarm count.

**The README is not a summary. It is a different table.** "5.7× faster" and "8× reduction" have no
provenance in the paper.

### 2.3 SMPbot — "94% hallucination reduction" is a metric substitution (README WRONG, not just strong)

- README `06-SMPbot-Architecture-README.md:21` — "**Hallucination Reduction** | 94% improvement"
- README `06-SMPbot-Architecture-README.md:67` — "Hallucination Rate | 23% | 1.4% | **94% reduction**"
- The paper's only 94%: `05-SMPbot-Architecture.md:637` — "**Results**: 94% diagnostic consistency,
  72% reduction in contradictory suggestions."

**94% diagnostic consistency ≠ 94% hallucination reduction.** These are unrelated quantities;
the README appears to have taken the numeral 94 and attached a different metric to it. Note also
that the README's `23% → 1.4%` is itself arithmetically a 93.9% reduction, i.e. the 94% may be
derived from the README's own invented numbers rather than the paper's.

The README also claims "**Stability Proofs** | 9 formal proofs" (`06-SMPbot-Architecture-README.md:20`).
The paper has 6 theorem headers and **1** `**Proof` marker. **Overstated by 9×.**

### 2.4 OCDS — README invents a worse baseline to manufacture a speedup (README WRONG)

- README `08-Origin-Centric-Data-Systems-README.md:205-211` — Message Complexity: traditional
  `O(n³)` → OCDS `O(k)`, "**1000× reduction**"
- Paper `07-Origin-Centric-Data-Systems.md:118` — "Message complexity: `O(d)` per update (vs **`O(n²)`**
  for consensus)"
- The paper's *own* comparison table at `07-Origin-Centric-Data-Systems.md:239` says Raft `2n`,
  PBFT `O(n²)` — **never O(n³)**.

The README inflates the baseline by one power of `n` to reach a round number. At the paper's own
largest measured node count the true figures are: vs `O(n²)` → 1,275×; vs the README's `O(n³)` →
12,750,060× (`derive/ocds.py`). "1000×" is not the honest number under either baseline at n=10,000;
it is reachable only by picking n≈8,000 against an `O(n²)` baseline.

### 2.5 OCDS — theorem renumbering, and "O(log n)" is contradicted by the paper's own data

- README `08-Origin-Centric-Data-Systems-README.md:63` and `:212` — "**Theorem 3.1**: Proven
  convergence without global coordination"
- Paper `07-Origin-Centric-Data-Systems.md:108` — the same theorem is **Theorem 1**, and its proof
  is labelled "**Proof Sketch**" (line 110), not a proof.

The README's "Proven" upgrades a proof sketch. It also renumbers it, so a reader following the
README to "Theorem 3.1" in the paper finds nothing.

**Separately — the paper contradicts itself, which no README mentions.** The paper predicts
`O(log n / log d)` convergence (`07-Origin-Centric-Data-Systems.md:121`), then reports
`07-Origin-Centric-Data-Systems.md:216-220`:

| n | 10 | 100 | 1,000 | 10,000 |
|---|---|---|---|---|
| time (ms) | 12 | 47 | 89 | 156 |
| **time / ln n** | 5.21 | 10.21 | 12.88 | 16.94 |

If `T = c·log n` then `T/ln n` must be constant. It varies **3.25×** across the table, monotonically
increasing. The best fit is `T ~ n^0.371` (`derive/ocds.py`). The paper's own sentence — "Results
show O(log n) scaling as predicted" (`:220`) — is not supported by the four numbers printed directly
above it. **This is the only place in the slice where the repo's own data falsifies its own claim
without anyone external having to do the work — and no falsifier section exists to say so.**

### 2.6 Rate-Based — "5–10× faster" appears in the README and nowhere in the paper

- README `05-Rate-Based-Change-Mechanics-README.md:9` — "**Core Insight**: Rates reveal system
  changes 5-10× faster than state monitoring." Repeated as a stat at `:20` ("Performance Gains |
  5-10× faster detection").
- Grepping both paper files (`rate_based_change_mechanics_section_round6.md`,
  `rate_based_change_mechanics_mathematical_appendix_round6.md`) for `5-10`, `10×`, `5×`, `faster`
  returns **one** hit — `rate_based_change_mechanics_section_round6.md:13`, a qualitative claim
  ("Rates reveal system behavior changes before they manifest in state deviations") with **no
  multiplier attached**.

The headline quantitative claim of the README's entire "Paper Statistics" table is **absent from
the paper**. The qualitative claim is also weaker than the README's framing: "before they manifest
in state deviations" is a definitional consequence of integrating rates, not an empirical speedup.

### 2.7 Tile Algebra — "17 formal proofs" against 7, and the counterexample contradicts Theorem 15

- README `07-Tile-Algebra-Formalization-README.md:19` — "**Theorems & Proofs** | 17 formal proofs"
- Paper `06-Tile-Algebra-Formalization.md` — 27 theorem headers, **7** `**Proof` markers.
  **Overstated by 2.4×.**
- README `:71` — "Confidence Monotonicity | Unpredictable | **Proven** ✅ Theorem 4.2"
- The paper's Theorem 2 is Confidence Monotonicity (`:108`); there is no Theorem 4.2 in the
  paper at all. Another renumbering.

**The most interesting finding in this README is one the README hides.** The paper contains
`06-Tile-Algebra-Formalization.md:385-400`, "### 7.2 Counterexample", which is a genuine
falsifier — the only one in the whole 42-file slice. It demonstrates the **Composition Paradox**:

> `safe(T₁) ∧ safe(T₂) ⊬ safe(T₁ ; T₂)` — round to 2 decimals, then multiply by 100:
> `3.14159 → 3.14 → 314` vs `3.14159 → 314.159 → 314.16`.

This directly contradicts **Theorem 15 (Compositional Safety)** at
`06-Tile-Algebra-Formalization.md:324`: "If T₁ and T₂ are individually safe … and their composition
is well-typed, then T₁ ; T₂ is also safe." The paper asserts the theorem at line 324 and refutes
it 60 lines later. **Theorem 15 is never retracted, and the README at
`07-Tile-Algebra-Formalization-README.md:135` reports only the favourable half: "Tile algebra
formally proves confidence propagation rules."** The repo contains its own counterexample to its
own theorem and chose to file it in a section rather than act on it.

---

## 3. Q3 — Pythagorean Geometric Tensors vs `constraint-theory-core`

This was the sharpest test, and the answer is the most interesting one: **the paper's own math
predicts the crate's bug, and the paper never notices.**

### 3.1 Does the paper know about inexactness? No. Does its math predict it? Yes.

The paper repeatedly promises exactness that its own definitions cannot deliver:

- `04-Pythagorean-Geometric-Tensors.md:35-36`: "preserving exact arithmetic throughout geometric
  computations"
- `:39`: "Rather than representing angles through trigonometric functions, we represent them
  through Pythagorean ratios that maintain exact arithmetic throughout"
- `:80-83`: "The snap operation can be implemented without trigonometric calculations … This
  discrete optimization problem has an efficient solution using continued fraction expansions,
  **avoiding floating-point arithmetic entirely.**"

"**avoiding floating-point arithmetic entirely**" is a prescription for exact rational arithmetic
— and it is the *correct* prescription. The crate does not follow it. And crucially, the paper
**never mentions representability, rounding, or numerical error as a limitation anywhere**. Not
once in 35,480 bytes. The paper is not silent because it knows; it is silent because it never
asked.

**The prediction chain:** if you implement Definition 2.1 (`T_ij = (a_i a_j + b_i b_j)/c`) in f64 —
which is the obvious reading, and which the crate's own doc comments describe — you must store
`a/c` and `b/c`, and **every non-dyadic rational is inexact in binary floating point**. Re-derived
first in `derive/exact.py`: of 15 primitive triples, **15/15 have at least one coordinate that does
not round-trip to its stated rational**. `3/5` round-trips to
`5404319552844595/9007199254740992`, not `3/5`. Only denominators that are powers of two survive.

So the paper's "exact arithmetic" claim and a binary-float implementation are **mutually
exclusive**. The crate picked floats. The result is the behaviour I measured.

### 3.2 The crate's table: 22 of 23 rationals are inexact, and one entry is irrational

`SuperInstance/constraint-theory-core/src/hidden_dimensions.rs:288-316` and
`src/quantizer.rs:409-432` hold a 26-element `&[f64]` table of "Pythagorean ratios". Re-derived in
`derive/table.py`:

- **22 of the 23 rational-labelled entries are not exactly representable in f64.** Only `0.5`
  survives. (The orchestrator's prior measurement of "12 of 15" was an undercount — the table is
  larger than 15 and nearly every entry fails.)
- The final entry is `0.7071067811865476, // sqrt(2)/2` at `src/hidden_dimensions.rs:315` and
  `src/quantizer.rs:431`. **√2/2 is irrational.** It is not a Pythagorean coordinate; no integer
  triple generates it. It sits in a table whose declared purpose is exact rational Pythagorean
  snapping, and it is the one entry that *cannot* be exact.
- The table also contains `0.0` and `1.0` (`src/hidden_dimensions.rs:289-290`) — degenerate
  endpoints, not points of the unit circle.

The crate's own README states the claim plainly:
`SuperInstance/constraint-theory-core/README.md:9` — "maps continuous 2D vectors to **exact
Pythagorean coordinates** on the unit circle, so a direction is defined by **integers, not
floats**." Restated at `src/lib.rs:29` and `README.md:208`.

**It is defined by floats.** `src/manifold.rs:21-27`:
```rust
pub struct PythagoreanTriple {
    pub a: f32,   // not i32
    pub b: f32,
    pub c: f32,
}
```
The struct that is supposed to carry the integers is three `f32`s. `src/manifold.rs:69-71`:
`is_valid()` is `(a*a + b*b - c*c).abs() < 1e-6` — a tolerance test, which is the definition of
*not* exact. No code path anywhere in the crate stores an integer leg.

### 3.3 The deeper defect: `snap_to_lattice` does not preserve the constraint it exists to enforce

This is worse than a precision complaint, and it is a direct consequence of the paper's framing.

`src/hidden_dimensions.rs:264-270` snaps **each component independently** against the scalar table
and then rescales:

```rust
.point.iter().map(|&x| snap_to_rational(x / norm) * norm).collect()
```

For a point on the unit circle, the two snapped ratios are `(a₁, b₁)` and `(a₂, b₂)` chosen
separately. **Nothing forces `a₁² + b₁² = 1`.** Re-derived in `derive/lattice.py`: feeding 31,207
grid points that are *already exactly on the unit circle* through this function, **31,203 (99.99%)
come off the circle.** Worked example: `(0.1, 0.9)` → `(0.1633, 0.9055)`, norm 0.9201 ≠ 1.

A function named `snap_to_lattice` that maps the unit circle overwhelmingly *off* the unit circle
is not an approximation of a Pythagorean manifold. It is a per-axis rounding function. The
`ConstraintBlock` in `src/tile.rs:136-138` does carry a `snap_target: [f32; 3]` labelled
"Pythagorean snap target (a, b, c)" — but it is `f32`, and nothing checks it.

**So: a paper that derives the wrong thing, and a crate that implements the wrong thing,
consistently.** The crate's error is not an independent implementation bug — it is the *same*
error the paper makes. The paper asserts exactness without specifying a representation, the crate
silently picks the one representation that cannot deliver it, and the README advertises the
result as exact. **The paper's §2.2 "avoiding floating-point arithmetic entirely" is the only
sentence in either repository that would have prevented the bug, and it is in the paper, not the
crate — where nobody implementing the crate would look for it.**

### 3.4 The paper's angle table is the one part that checks out

For completeness, and to be fair: the README's angle reference table
(`04-Pythagorean-Geometric-Tensors-README.md:132-138`) is numerically correct. All 10 angles
verified against `atan2` to within 0.005° (`derive/table.py`). And Theorem 3.1's angle-addition
formula **is right** — and the closure property it gestures at is real, which I verified
independently: for primitive triples `(a,b,c)`, `(d,e,f)`, the identity
`(ad+bc)² + (bd−ac)² = c²f²` guarantees the angle sum is always Pythagorean. Confirmed 10/10 on
distinct triple pairs. The paper at `04-Pythagorean-Geometric-Tensors.md:180-190` states the
formula correctly but then weakens it with "if and only if … forms a Pythagorean triple", which is
a tautology (a triple is defined by that property) and misses the clean unconditional result. So
the paper has a true theorem and does not prove it properly.

---

## 4. Q4 — Tile Algebra vs the 384-byte `plato-tile-encoder` record

**Answer: the formal algebra does not license the fixed-width record. The paper contains no field
width, no byte count, no serialisation, and no memory-layout discussion anywhere. The record is a
pure implementation compromise, and the formalisation does not mention it.**

Evidence from `06-Tile-Algebra-Formalization.md`:

- **Definition 1 (Tile)**, `:39-47`: `T = (I_T, O_T, f_T, c_T, τ_T)` — a 5-tuple of *types and
  functions*. `I_T, O_T ∈ Type`, `f_T : I_T → O_T`, `c_T : I_T → [0,1]`, `τ_T : I_T → String`.
- The most concrete type statement in the paper is the TypeScript block at `:64-75`:
  ```typescript
  type TileType = {
    input: TypeSchema; output: TypeSchema; constraints: ConstraintSet;
    confidenceBounds: [number, number]; traceFormat: TraceSchema;
  }
  ```
  `TypeSchema` is *recursive and unbounded* (`:68-74`: `ArrayType<TypeSchema>`,
  `ObjectType<Record<string, TypeSchema>>`, `UnionType<TypeSchema[]>`, `DependentType`). It is a
  type language with no size bound expressible in advance.
- `c_T` has codomain `[0,1]` — a continuum. `τ_T` has codomain `String` — unbounded length.
  A fixed-width record must quantise both. The algebra never does.
- Grepping the whole 26,754-byte paper for `byte|width|record|384|serial` returns **no field-width
  table and no byte count**. The words appear only in `confidenceBounds`/`TypeSchema` contexts.

**The record layout is not in the paper, and cannot be derived from it.** The
`plato-tile-encoder` 384-byte record (id 64 / q 128 / a 128 / domain 32 / tags 20 / conf 4 /
ghost 4 / use_count 4) has a field table matching **neither** the paper's 5-tuple **nor** the
crate's actual `Tile`. For the record, the crate's `Tile` in `src/tile.rs:20-58` *is* 384 bytes —
`src/tile.rs:223` asserts `mem::size_of::<Tile>() == 384` at compile time, and
`src/tile.rs:9-19` documents the layout (Origin 64 / Input-Output 16 / Confidence-Safety 8 /
Pointers 16 / Tensor payload 64 / Provenance 4 / Self-play 2 / Hydraulic flux 4 / Constraints 192 /
padding). **That is a third, entirely different 384-byte layout**, sharing only the total. It is
`#[repr(C, align(64))]`, i.e. **cache-line aligned with explicit padding to 384** — the signature of
a deliberate hardware compromise, the opposite of what a formal algebra would license.

**On the `tags(24)` vs `tags 20` discrepancy:** the doc comments say 24, the code writes 20. The
paper cannot arbitrate, because **the paper has no `tags` field at all.** There is nothing in the
formalisation to check either number against. This is the general shape of the problem: the
formalisation is silent on every question the implementation actually had to answer.

---

## 5. Q2 — Falsifiers: 2 of 42

**Method:** grep across all 42 files for `falsifi | would be (false|wrong) | refut | disprov |
counter-example | contradicts | however, if | but this fails`.

| File | Falsifier? |
|---|---|
| `06-Tile-Algebra-Formalization.md:385-400` | **YES** — §7.2 Composition Paradox, genuinely refutes Theorem 15 |
| `round13-08-Tile-Algebra-Formalization-COMPLETE.md:233` | **YES** — same counterexample, developed |
| the other 40 files | **none found** |

So: **1 independent falsifier exists in the slice**, and it appears twice because two files
duplicate it. It is the strongest single piece of scholarship in the directory — a worked
counterexample that a reviewer wrote to break the authors' own Theorem 15. **The repo's response was
to file it in §7.2 and leave Theorem 15 standing at line 324**, and to omit it from the README.

This is the finding. Not that the papers lack falsifiers — that a falsifier was *produced*,
*verified*, *placed in the document*, and then **deliberately not connected to the theorem it
kills**. A paper that never had a falsifier is merely unrigorous. This one had one and suppressed
it.

The near-misses that are **not** falsifiers:
- `04-Pythagorean-Geometric-Tensors.md:565` — "Is the set of Pythagorean angles denser than random
  rational angles? … a formal density theorem is needed." An open question, not a falsifier.
- `07-Origin-Centric-Data-Systems.md:220` — "Results show O(log n) scaling as predicted" — a
  claim, with data under it that refutes it (§2.5), but no falsifier *stated*.
- `16-Five-Laws-of-Cellular-Architecture.md` — five "Laws", each with a violation-consequence
  section, none of which says what observation would show the law is false.

---

## 6. Reproduction

```bash
GIT_SSL_NO_VERIFY=1 git clone --depth 1 https://github.com/SuperInstance/superinstance-papers
GIT_SSL_NO_VERIFY=1 git clone --depth 1 https://github.com/SuperInstance/constraint-theory-core
cd /workspace/projects/fleet-triage/derive && python3 exact.py thm21.py lattice.py table.py \
     cascade.py thm21_counter.py ocds.py ratestate.py
```
No `cargo` in sandbox; crate claims are source-read + Python re-implementation, not execution.
No files in either repo were modified.

---

## 7. Answers to the four questions, condensed

1. **Do the READMEs know what the papers say?** No. **7 of 7 promotional.** Worst: SMPbot's "94%
   hallucination reduction" is a metric substitution for the paper's "94% diagnostic consistency";
   OCDS inflates a baseline from O(n²) to O(n³) to reach a round "1000×"; Confidence Cascade
   publishes four numbers, of which the paper contains none.
2. **Falsifiers?** **1 in 42** (0.5 files if you count the duplicate), and it refutes a theorem the
   same paper states 60 lines earlier. **0 of 7 READMEs mention it.**
3. **PGT vs the crate:** the paper promises exact arithmetic and never mentions representability;
   the crate uses `f32` legs, a table where **22 of 23 rationals are inexact**, an irrational
   `√2/2` entry, and a `snap_to_lattice` that moves **99.99%** of unit-circle inputs *off* the
   circle. **The paper's "avoiding floating-point arithmetic entirely"
   (`04-Pythagorean-Geometric-Tensors.md:83`) would have prevented all of it, and lives in the paper
   where implementers never looked.**
4. **Tile Algebra vs the 384-byte record:** the paper defines an unbounded recursive 5-tuple with
   no widths, no bytes, and no serialisation. **The record is unlicensed.** The crate has a *third*
   384-byte layout, cache-aligned with padding — an explicit hardware compromise the formalisation
   does not mention. And the paper has no `tags` field, so it cannot arbitrate `24` vs `20`.

**Single most overstated claim:**
`SuperInstance/superinstance-papers/white-papers/04-Pythagorean-Geometric-Tensors.md:77-85` —
*"Theorem 2.1 (Orthogonality of Pythagorean Basis) … T : T′ = c² if same, 0 otherwise"* — certified
to a reader by `04-Pythagorean-Geometric-Tensors-README.md:32` as *"Proven orthogonality via
Frobenius inner product."*

It is false twice over: the paper's own Definition 2.1 makes `T : T = 2` for every triple (never
`c²`), and the cross terms are `cos(2Δ) ≈ 0.879`, never 0. Four basis vectors in a 2-D space cannot
be mutually orthogonal. The "proof" is one sentence citing an integral that is never defined.
