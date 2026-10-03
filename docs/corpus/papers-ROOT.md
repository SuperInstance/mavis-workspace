# Scout 4/4 — `SuperInstance/superinstance-papers` root papers + published surface

**Method:** fresh shallow clone (`GIT_SSL_NO_VERIFY=1`, no token), 4,986 files. Read the three papers in
full; independently re-derived every constant and bound *before* checking the paper's number; cloned
all 11 cited sibling repos to test each `path:line`; queried the GitHub API for CI, stars, and run
history. **Read-only — nothing was modified.**

```
/tmp/sp/superinstance-papers   (clone)
/tmp/sp/cited/{murmur,eisenstein,batten-spline,confidence-cascade,base60-lattice,
               platonic-randomness,conservation-spectral-fortran,
               conservation-spectral-fortraniv,fortran-constraint-checking,
               polln,superinstance-website}   (all 11 cloned OK)
```

---

## 0. Headline

The orchestrator asked for a fabricated arXiv ID. **There are none to find — because there are no
citations at all.** Across all three papers: **0 arXiv IDs, 0 DOIs, 0 URLs, 0 author-year
citations, 0 "et al."** The `## References` sections (8, 6, and 11 entries) contain **only
first-party file paths into sibling repos.** Verified by exhaustive grep:

```
$ grep -Eio 'arxiv|doi[: ]|10\.[0-9]{4,9}/|https?://' 01-*.md 02-*.md 03-*.md
(counts: arxiv=0  doi=0  url=0   — identical for all three)
```

Repo-wide, arXiv appears **only** as unsubmitted placeholders in `papers/55-arxiv-preparation/` and
sibling drafts: `arXiv:XXXX.XXXXX`, `**arXiv:** 2026.XXXXX`, `10.5281/zenodo.XXXXXX`. These are
honest TODOs, not fabrications — a real and *better* pattern than a fake ID. **The finding is
absence, not forgery.**

The higher-value finding is what replaces the citations: **the load-bearing empirical anchor of
Paper 01 (§5.4, the 6.8× triple-density claim) is an arithmetic error, and it is copy-pasted
verbatim into a real, CI-verified Rust crate that a third paper then cites as verified.**

---

## Part A — The three papers

### A.1 The three claims, one sentence each

| # | Claim (one sentence) | Anchor |
|---|---|---|
| **01** | For a Permutation-Tensor agent, crystallized intelligence γ (mean certainty c̄) plus liquid intelligence η (active-layer fraction) is *approximately* conserved at C≈1, with the shortfall c̄(1−c̄) ≤ ¼ being the "overhead of uncertainty." | `01-conservation-law-of-intelligence.md:23` (Conjecture 1.1), `:75` (Thm 2.3), `:79` (Cor 2.1) |
| **02** | Creative synthesis is optimal at normalized semantic distance 0.4 ≤ Δ ≤ 0.6, derived three independent ways: max kernel gradient (Δ=e^{-1/2}), max surprise×comprehensibility, and the 2d6 Catan mode. | `02-semantic-distance-creative-breakthrough.md:365` (Thm 9.1) |
| **03** | The agent⊂harness⊂room⊂SuperInstance nesting is the left Kan extension of the agent along the nesting diagram, making it the universal agent-embedding solution, with automorphism group D₆. | `03-hermit-crab-protocol.md:379` (Thm 8.1), `:443` (Thm B) |

### A.2 Falsifiers: 0 of 3 papers state one. The number 9 is a mirage.

Every one of the three papers has a `## Proposed Experiments` section, and each experiment carries a
bolded **Falsification.** line — 3 per paper, 9 total (`01:279,289,299`; `02:336,346,356`;
`03:411,421,434`). At a glance this looks like exemplary falsifiability.

**It is not.** All 9 are attached to experiments that have never been run, and none is a falsifier
for the paper's actual headline theorem. Concretely:

- **No experiment tests its own paper's main result.** Paper 01's Thm 7.1 (fleet-wide bound),
  Thm 3.2 (fog density bound), Thm 5.1/5.2 (Eisenstein) have **no experiment at all.** The three
  experiments test compute savings and a drift comparison — not conservation.
- **No results exist anywhere.** `0` figure captions, `0` table captions, `0` occurrences of
  "we ran / we measured / results obtained" across all three papers. Every prediction is
  future-tense. The papers are 71.6 KB of specification and 0 KB of evidence.
- **The 9 falsifiers are unfalsifiable as written** because they condition on an experiment nobody
  can run: `03:411` says "If any batten… is lost during molting, the identity preservation theorem
  fails" — but the `murmur` repo that would supply the PTT **has no Python at all** (see A.4), so
  the experiment is not merely unrun, it is **unrunnable**.

**Verdict: 0 of 3 papers state a falsifier for the claim in its title.** The 9 present are
experiment-conditional, and the experiments are unrunnable.

### A.3 Citation audit — the highest-value finding

Every `path:line` in all three papers' References and inline citations, tested against the real repos:

| Citation | Verdict |
|---|---|
| `murmur/transforms/permutation.py:295` (`propagate_change`) | **DEAD — file does not exist** |
| `murmur/transforms/permutation.py:281` (`EncodingLibrary`) | **DEAD — file does not exist** |
| `murmur/logtensor/transforms/permutation.py:295`, `:281` | **DEAD** |
| `murmur/transforms/rubiks.py:437` (`L(c)` formula) | **DEAD** |
| `murmur/transforms/rubiks.py:281` (`update_certainty`) | **DEAD** |
| `murmur/logtensor/transforms/rubiks.py:281` | **DEAD** |
| `batten-spline/src/batten_spline/{spline,router,batten}.py` | **RESOLVES** (189/113/46 lines) |
| `confidence-cascade/src/confidence-cascade.ts` | **RESOLVES** (458 lines) |
| `base60-lattice/src/{lattice,compass,hex,walk}.ts` | **RESOLVE** (207/186/200/291 lines) |
| `eisenstein/README.md`, `platonic-randomness/src/index.ts` | **RESOLVE** |

**7 of 7 `murmur` citations are dead; 0 of 11 real-repo citations fail.** Note the split is not
random: every *symbolic* citation (the PTT, the law's own machinery) is dead, while every
*decorative* one (base60, Catan, compass) resolves.

**Paper 01's entire physical basis is missing.** Theorem 2.1, 2.2, 2.3, 6.1 — the certainty update
`c ← min(1, c + 0.1·κ^d)`, the layer function `L(c)=⌊L_max(1−c̄)²⌋`, `pathway_strength`, the seven
named encodings — all are attributed to `murmur`. Verified against the live repo:

```
$ find murmur -name 'permutation.py' -o -name 'rubiks.py'
(empty)
$ find murmur -name '*.py'
murmur/experiments/critical-mass/cm2.py
murmur/experiments/critical-mass/critical_mass.py
$ grep -rn --include='*.py' -E 'class PermutationTensor|class AdaptiveLayerController|
    class EncodingLibrary|def propagate_change|class CertainTensor' <all 11 cited repos>
0 hits
```

`murmur` is a **Next.js/TypeScript wiki app** (21 files, `src/app/page.tsx`, `tailwind.config.ts`).
`PermutationTensor`, `AdaptiveLayerController`, `EncodingLibrary`, `CertainTensor`, and
`LayerRemovalGate` **do not exist in any Python file in any of the 11 repos I cloned.** The only
occurrences of `pathway_strength` anywhere are in `polln/docs/research/*.md` — prose design docs,
not code.

Paper 02 inherits the same dead dependency: its Thm 5.1 and 5.2 ("Creative Convergence Rate",
`T = (c*-c₀)/0.05`, "each homing step adds 0.05") rest entirely on the missing PTT. `homing_sequence`
appears **4 times in the fleet, all in `polln/docs/RTTconversation/` transcripts** — never as code.

**What *does* check out (be fair to the work):** every numeric threshold in Papers 01/02/03 that
points at a *real* file matches the code exactly —
- `01:112` router thresholds 0.7 / 0.3 → `batten-spline/src/batten_spline/router.py:35,39` ✓
- `01:141` `fog_scale`/`half_life` → `spline.py:24,25` ✓; `01:229` prune max 500 → `spline.py:143` ✓
- `01:186` "0.9⁵=0.59" → verified `0.59049` ✓
- `01:203` `n ≤ ln θ / ln c₀ = 5.6` → verified `5.6086` ✓
- `02:246` 2d6 entropy 3.27 bits → verified `3.2744` ✓; `02:241` mode 6/36 ✓
- `03:281,289` conditionalCascade throws on 0 or >1 active → `confidence-cascade.ts:273,277` ✓

The authors read their *own* real code accurately. The failure is confined to the one dependency
that does not exist.

#### The 6.8× error — an arithmetic failure that escaped into a tested crate

Paper 01 §5.4 (`:224`) asserts Eisenstein triples are "**6.8× higher density** than Pythagorean
triples at the same bound (**59,841 vs 10,428**)" and builds Theorem 5.2 on it. Re-derived first:

```
59841 / 10428 = 5.7385        <- the paper's own two numbers do not give 6.8
2/sqrt(3)      = 1.1547       <- the paper's own asymptotic does not give 6.8 either
```

**Neither the printed pair nor the derived constant produces 6.8.** I then counted the triples
directly (quadratic forms a²−ab+b² ≤ B vs a²+b² ≤ B, both counting conventions, B = 10⁴…10⁷):

| B | Eis(all) | Pyt(all) | ratio | Eis(prim) | Pyt(prim) | ratio |
|---|---|---|---|---|---|---|
| 10⁴ | 440 | 104 | 4.23 | 55 | 32 | 1.72 |
| 10⁶ | 5,532 | 1,762 | 3.14 | 503 | 316 | 1.59 |
| 10⁷ | 19,298 | 6,742 | 2.86 | 1,587 | 1,010 | 1.57 |

The ratio **decays toward the paper's own asymptotic 2/√3 ≈ 1.155 — it never approaches 6.8**, and
**59,841 / 10,428 is not reproducible under any counting convention** I tried.

This is not contained to the paper. The identical claim is asserted in the **`eisenstein` Rust crate**:
- `eisenstein/README.md:25` — "~6.8× denser than Pythagorean triples — 59,841 versus 10,428"
- `eisenstein/CONTRIBUTING.md:68` — "~6.8× denser"
- `eisenstein/src/lib.rs:32` — "analogous to Pythagorean triples but ~6.8× denser"
- `eisenstein/tests/algebraic_properties.rs:636,688` — same, inside the test suite

**And the `eisenstein` crate has real CI** (`.github/workflows/ci.yml` + `rust-ci.yml`) and real
property tests — `norm multiplicativity | 10,000 random multiplications | Zero drift`
(`README.md:109`), which Paper 01 §5.1 (`:203`) cites as verified. **So a demonstrably wrong
constant is laundered through a passing test suite into a paper that cites the passing suite as its
authority.** That is the mechanism by which a bad number acquires credibility, and it is the single
most transferable finding in this report.

The `10,000 random multiplications / zero drift` claim itself **does check out** — it is in the
README table and backed by `tests/algebraic_properties.rs`. That is the *only* externally-verifiable
empirical claim in Paper 01 that survives, and it is a property of integers, not of intelligence.

### A.4 Paper 02 — the proof that refutes itself on the page

Theorem 3.1's proof (`:180–217`) visibly collapses mid-derivation and the paper does not notice:

```
:206   "Wait — more carefully. Using natural log:"      <- author debugging in the published text
:213   Δ* ≈ 0.871                                        <- 30% above the claimed 0.6 ceiling
:216   "Since u > 1, the maximum is at the boundary — the function is monotonically increasing
        in [0, 1)."                                       <- i.e. the model says BIGGER IS ALWAYS BETTER
```

At `d_emb=128` the derivation lands on a maximizer **outside the domain** and concludes the
objective is *monotonically increasing* — the exact opposite of an interior creative zone. Rather
than report this as a refutation, the paper introduces a "**Refined model**" (`:218`) that swaps in
an ad-hoc `min(H_max, ·)` clamp and then reads the answer backwards off the target interval. The
conclusion is reverse-engineered from the answer, not derived.

**Theorem 9.1 then contradicts Theorem 3.1.** Same symbol, two different formulas:

| H_max | Thm 3.1 `√(1−e^{−H})` | Thm 9.1 `√(1−e^{−H/2})` |
|---|---|---|
| ln 2 | 0.7071 | 0.5412 |
| ln(3/2) | 0.5774 | 0.4284 |
| ln(5/4) | 0.4472 | 0.3249 |

Paper 02 (`:365`) boxes `Δ* = √(1 − e^{−H_max/2})` and then, two lines later, claims the creative
zone is `[0.4, 0.6]`. **Applying the boxed formula to its own stated range H_max ∈ [ln(5/4), ln(3/2)]
yields [0.325, 0.428] — which excludes 0.6 and does not contain the advertised interval.** The main
theorem does not imply its own headline.

§7.1 is a second self-refutation: the Creative Reynolds Number is computed to `Δ ≈ 5.2`, `02:344`
concedes this is "outside [0,1]" and that "creative flow is always laminar," then the section
proceeds as if a transition existed. §7.2 derives the removal rate, gets a *constant* (`02:360`:
"This is constant"), and concludes the transition is "not in the removal rate but in the
information density" — a quantity never defined.

Minor: `02:283` table gives `θ=0.30 → d/σ = 1.53`; correct value is **1.5518** (the other three rows
are correct to 3 s.f.).

### A.5 Paper 03 — the Kan extension

Thm 8.1 (`:379`) is stated as a `**Proof sketch.**` — and the sketch is not a Kan-extension
argument. It gives three numbered conditions (preserve agent state / add shell constraints /
compose associatively) and asserts "These are exactly the conditions for the left Kan extension."
They are not: a left Kan extension is characterized by a *colimit over an index category*, and
`Lan_J(F)` is the colimit `∫^j F(j)`, which is a quotient construction over a diagram — not a
"nesting scheme that preserves identity." Corollary 8.1's "there is only one correct way to molt,
up to isomorphism" is a uniqueness claim with no supporting argument, resting on the sketch.

Thm 5.4 (`:397`) "The fundamental group of the shell space is ℤ₆" is a category error: ℤ₆ is the
*rotation* symmetry group, and the paper itself names the automorphism group as the **dihedral D₆
of order 12** at `03:443` (Thm B). It says both, twelve lines apart, without noticing.

Thm 5.2's "The pruned spline is a closed subset of a compact space" is circular — nothing
established compactness of the ambient space, and a finite set is compact in any topology
regardless, so the BattenSpline `prune` call is doing no work here.

The base60/hex material (`§4`, `§7`) is the best-cited part: `generateCompassRose`,
`findInterlacePoints`, `hexTriangleCentroids`, `walk345`, `walkPythagorean`, `walkSpiral`,
`walkHexagon`, `latticePath`, `generatePatch` — **all 9 confirmed present** in
`base60-lattice/src/{lattice,compass,hex,walk}.ts`.

### A.6 The Fortran question: is it implementing the law, or a special case?

**Neither — it is about music.** This is the sharpest finding in Part A.

`conservation-spectral-fortran` is a **LAPACK-backed spectral analysis of musical tension graphs**:

- `src/tension_graph.f90:1` — `!> Module: tension_graph — Graph data structure for Conservation Spectral SDK`
- `tests/test_chords.f90:1` — `!> Test: Musical chord progression conservation analysis`
- `README.md` — *"C-G (fifth)"*, graph of 7 vertices, Cheeger constant, anomaly tracker

"Conservation" here means **conservation of musical tension across chord progressions** — Laplacian
spectral gap, Cheeger constant, sliding-window z-score. It has **no relationship whatsoever to
Paper 01's conservation of intelligence.** Verified exhaustively:

```
$ grep -rniE 'gamma|liquid intelligence|crystalli|conservation law|01-conservation' \
    conservation-spectral-fortran conservation-spectral-fortraniv fortran-constraint-checking
(no hits)
```

`conservation-spectral-fortraniv` is a **fixed-form FORTRAN 77** port (`.f`, columns 7–72, `GOTO`,
`DO 30 I=1,N`) of the same tension-ratio routine — `spcons.f:1` *"CONSERVATION RATIO COMPUTATION."*
It is not a specialization of the law either; it is a 1970s-style numeric kernel for a different
quantity. It also **ships a committed binary** (`spmain`, executable) in the repo root.

`fortran-constraint-checking` is unrelated again: a multi-language **range/bitmask constraint
checker** (Fortran + Python + Rust + C bindings) with **zero test files** in the repo.

**So: the name-matching is a false positive at the level of meaning.** Three repos whose names
contain "conservation"/"constraint" share no vocabulary with the paper they appear to implement.
Had the fleet been triaged by name similarity, this would have been scored as substantiation.

**CI audit of the three (extends your 13-repo figure to 30):**

| Repo | CI | Effect |
|---|---|---|
| `conservation-spectral-fortran` | **none** | `make test` never ran in CI |
| `conservation-spectral-fortraniv` | **none** | committed binary never validated |
| `fortran-constraint-checking` | `ci.yml` present | **`run: echo "No CI configured — customize per project requirements"`** |

`fortran-constraint-checking/.github/workflows/ci.yml:12` is a **green checkmark that executes
nothing.** It never invokes `gfortran`, never runs a test — and the repo contains **no test file at
all** (`find -iname '*test*' -o -iname '*spec*'` → empty). This is a cleaner instance of the
documented fail-open pattern than the `| tee` case, because the workflow *body* is a placeholder
echo.

**Substrate sweep, measured:** I checked all 30 `substrate-*` repos, not 13.
**27 of 30 have no `.github/workflows/` at all.** CI present in only `substrate-embedding` and
`substrate-rng`. Your "zero of 13 have CI" is directionally right and slightly understated.

**This repo's own CI is also fail-open, in the same family:**

```yaml
.github/workflows/ci.yml:17-20
      - run: npm install
        continue-on-error: true
      - run: npm run build
        continue-on-error: true
```

The `build` job **cannot fail** — every step is `continue-on-error: true`. And the repo's real CI
status is **failing anyway**: GitHub API reports 563 runs, most recent `CI` = **failure**
(2026-09-26), with the only green being dependabot's "npm_and_yarn update" job. `package.json:scripts`
declares `"build": "tsc"` and `"test": "jest"`, so the `test` job runs jest against a repo whose
documented subject matter is 2,295 markdown files.

---

## Part B — Published vs contained

### B.1 The ratio

| Measure | Count |
|---|---|
| **Contained** — `.md` documents in repo | **2,295** |
| Contained — total `.md` bytes | **40,481,625** (38.6 MB) |
| Contained — root numbered papers (the spine) | **3** |
| Contained — `papers/` subdirectories | **61** |
| Contained — raw `seed*.md` transcripts | 4 files, 499,797 bytes |
| **Published** — `.astro` pages in `website/` | **19** |
| Published — of which touch math/theory | **4** (`polln-log-mathematics`, `building-confidence-cascades`, `rate-based-change-mechanics`, `working-with-ocds`) |
| Published — `website/` total files | 181 |
| **Published — pages citing Papers 01/02/03** | **0** |

> **Published : contained = 19 : 2,295 ≈ 1 : 121.**
> **For the three spine papers specifically: 0 published : 3 contained. Ratio 0 : 3 — the inverse
> of the question asked. Nothing is over-claimed; everything is under-claimed.**

**The "publishes what it cannot substantiate" hypothesis is not what I found. The real asymmetry
runs the other way**, and it is worth having on the record: a repo named `superinstance-papers`
whose own spine papers are **invisible to its own website**.

```
$ grep -rniE '01-conservation|02-semantic|03-hermit|conservation-law-of-intelligence|
             semantic-distance|hermit-crab' website/
0 matches
$ grep -rlniE 'conservation.law|creative zone|hermit.crab' website/src/
0 files
```

Note `website/` is **181 files, not 43** — the brief's figure appears to be the `src/pages/`
subset or an older count. Its 19 renderable pages are a Spreadsheet-AI product surface
(`pricing.astro` sells $0/$29/$35/mo, 50 users); the mathematics is not on it at all.

### B.2 The one conservation claim that *is* public — and it is a different paper

`SuperInstance/superinstance-website/papers/conservation-law.tex` (241 lines, HTTP 200) is a
LaTeX paper titled *"Conservation Laws in Bounded Agent Systems: Information-Theoretic Governance
for Multi-Agent Fleets"* (DiGennaro & Phoenix, June 2026, marked `Status: Draft`). It is **not**
Paper 01 — different title, different authors, different claim (balanced-ternary / radix economy,
`C = ½K log_B K`). But it is reachable only from `papers/index.html`, whose entire nav is three
links: `../index.html`, `education.html`, and an external GitHub profile. So even the one public
conservation paper is effectively unlinked.

Worth flagging because it is the **only** file in the entire published surface containing a
self-refutation:

```
conservation-law.tex:139
  \textbf{Result: The formula is falsified for $K \neq 3$.} Monte Carlo $\delta$ values are
  consistently ~50% lower than predicted for $K > 3$. The correction $K/2n$ is specific to the
  ternary alphabet's symmetry properties.
```

The published side of the fleet **records a falsification it actually ran.** The private side
(three papers, 9 proposed experiments) records none.

### B.3 `.gcconfig` and `.vectordb_metadata.json` — working system or dead pointer?

**`.vectordb_metadata.json` — a working (if stale) system.**
- Points at Qdrant `localhost:6333`, collection `polln-codebase`, `all-MiniLM-L6-v2`, 384-dim.
- **98 references to Qdrant** across the repo; the consumer is real — `mcp_codebase_search.py:22,99`
  instantiates `QdrantClient(host=..., port=...)`, with `vectorization_setup.py` named as the
  config it must match. Working MCP codebase-search tool, not a dead pointer.
- **But the metadata is stale and self-inconsistent:** `file_count: 2195` vs **2,295** `.md` files
  actually present — a digit transposition. And `log_tensor_added` (`2026-03-10T23:14`) is
  **5 hours after** the `timestamp` (`18:42`) yet the composite `total_with_log_tensor: 90703` is
  *smaller* than `file_count × chunk_count` would imply relative to the parts. It is a snapshot of
  a March state, carried forward.

**`.gcconfig` — a live pointer, but to a tool that is not in this repo.**
```json
{ "tier": "hot", "immortal_dirs": [".git",".env","AGENTS.md"],
  "warm_age_days": 90, "cold_age_days": 14, "build_dir": "", "cache_dirs": [] }
```
The **only** consumer inside the repo is prose: `AGENTS.md:14` — *"This repo's tier is **hot**. See
`.gcconfig` in repo root for detailed settings."* **No code reads these keys** (3 total matches for
`gcconfig|immortal_dirs|warm_age_days`, all the file itself + that sentence). Unlike
`.vectordb_metadata.json` — which has 98 real consumers — **`.gcconfig` has zero.** It is a
config-shaped artifact whose reader lives outside the repo. `build_dir: ""` and `cache_dirs: []`
are empty, so the settings that would make it do anything are themselves unset.

This is the `SubstrateReranker` pattern in miniature, and it is the **inverse** of that case: not
a component claimed with no implementation, but a config with no consumer. A 197-byte JSON file
that reads as infrastructure, that `AGENTS.md` cites as authoritative, that no code in 4,986 files
reads. Whether the GC tool exists fleet-wide I could not verify from this repo — **`UNVERIFIABLE`**
from this slice.

`.pollnrc:21` is the same family and does name a real machine: `"dataDir": "C:\\Users\\casey\\polln\\.polln"`,
`"colonyId": "colony-1772914705785-l6tajcl3r"`, `"colonyName": "Test Colony"` — a **committed
config with a hardcoded Windows absolute path and a `Test Colony` id shipped to a public repo.** The
fleet's documented `C:\Users\<name>\` leak family, reproduced at `CUserscaseypollnsimulationsrequirements.txt`
in the repo root — a file literally named after a mangled Windows path.

---

## Report

**The three claims:**
1. **01** — γ (mean certainty) + η (active-layer fraction) is approximately conserved at ≈1, with ≤¼ shortfall being the "overhead of uncertainty."
2. **02** — optimal creative synthesis lies at normalized semantic distance 0.4 ≤ Δ ≤ 0.6.
3. **03** — agent⊂harness⊂room⊂SuperInstance is the left Kan extension of the agent, the universal embedding solution, with D₆ automorphism group.

**Falsifiers: 0 of 3 papers state one for their headline claim.** Nine `**Falsification.**` lines
exist (`01:279,289,299`, `02:336,346,356`, `03:411,421,434`) but all are conditional on
never-run experiments; none targets the main theorem; zero results, zero figures, zero tables.

**Citations: 0 verified / 0 fabricated / 0 present.** No arXiv IDs, DOIs, URLs, or author-year
citations exist in any of the three. Repo-wide arXiv references are honest placeholders
(`arXiv:XXXX.XXXXX`). Instead: **7 of 7 `murmur` `path:line` citations are dead** — `murmur` is a
Next.js TypeScript app with **no Python**, and `PermutationTensor`/`AdaptiveLayerController`/
`EncodingLibrary`/`propagate_change` appear in **0 Python files across all 11 cited repos**. All 11
non-`murmur` citations resolve, and every threshold the papers attribute to real code (0.7/0.3,
fog_scale, prune 500, 0.9⁵=0.59, 5.6, 3.27 bits) matches exactly. **The authors read their own code
accurately; the failure is confined to the one dependency that does not exist.**

**Published vs contained: 19 : 2,295 ≈ 1 : 121** (and 0 : 3 for the spine papers). The website
publishes **none** of the three papers — `grep` for all three titles across all 181 `website/` files
returns **0 matches**. The hypothesized over-statement does not appear; the repo systematically
**under**-publishes, and `website/` is a Spreadsheet-AI product surface (181 files, not 43).

**Single most load-bearing unverified claim:**
> **`01-conservation-law-of-intelligence.md:224`** — *"Eisenstein triples produce 6.8× higher density than Pythagorean triples at the same bound (59,841 vs 10,428)."*

It is load-bearing because it is the only quantitative, checkable, non-tautological support in
Paper 01 for the "exact conservation" half of the law (§5), and it is the one number the paper
cites an external authority for. It is **false**: `59841/10428 = 5.74`, the paper's own asymptotic
gives `2/√3 = 1.155`, and direct counting shows the true ratio *decaying toward* 1.155 (4.23 → 3.14
→ 2.86 for B = 10⁴→10⁷) with neither figure reproducible. Worse, the identical wrong constant sits
in `eisenstein/README.md:25`, `CONTRIBUTING.md:68`, `src/lib.rs:32`, and — inside the test suite —
`tests/algebraic_properties.rs:636,688`, in a crate with **real CI and real property tests** that
Paper 01 `:203` then cites as its verification. **A wrong number passed through a passing test suite
into a paper as authority.** Runner-up: the entire `murmur` substrate of Paper 01, which does not
exist.
