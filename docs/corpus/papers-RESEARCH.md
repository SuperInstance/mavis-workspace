# Scout 3 of 4 — `SuperInstance/superinstance-papers`, the `research/` tree

**Question:** which research results survived into code, and what happened to the ones that didn't?
**Method:** re-derive constants and bounds *before* reading the claim; cite `path:line` or a commit sha; a negative is a result.
**Read-only.** Nothing was patched. Live defects are reported with evidence only.

Clone: `git clone --depth 50`, 95 commits, 4,986 tracked files, HEAD `efbc664` (2026-09-26).
Cross-repo: 20 fleet repos cloned to `/tmp/scout/r` (CRDT family, `substrate-foundation`, `quilt-i2i`, `quilt-nn`, `quilt-attention`, `xruntime-conformance`).

---

## 0. The measurement problem, stated first

**This repo cannot establish forward trace by commit ordering, and that is itself the first finding.**

`research/`, `src/`, `docs/`, `simulations/` and `papers/` **all first appear in the same commit**, `8dc65c5` (2026-03-16, "Create SECURITY.md") — 4,888 files, 2,376,550 insertions, in one commit whose subject names a file that has nothing to do with its contents.

```
research: 8dc65c5 2026-03-16   src: 8dc65c5 2026-03-16
docs:     8dc65c5 2026-03-16   simulations: 8dc65c5 2026-03-16
```

Across 95 commits, `research/` is touched by 6, `docs/` by 3, `src/` by 2. **The commit graph is not a history of the work; it is a history of uploads.** There is no "claim" commit and no "code" commit to order. Every forward trace below is therefore established by *content* matching (does the constant/identifier/type appear in shipped code?), not by ancestry — and I say which method was used on every row.

**Consequence for the whole fleet:** a "research doc → implementation" question cannot be answered from `superinstance-papers`' git log. It can only be answered by re-deriving each claim and grepping the tree. That is expensive, which is probably why the question has gone unasked.

---

## 1. The forward-trace table

11 documents examined, 11 specific findings traced. **4 landed as code (1 with field-level fidelity), 7 left no forward trace.**

| # | Document | Finding traced | Landed? | Evidence |
|---|----------|----------------|---------|----------|
| 1 | `research/CRDT_Research/VALIDATION_FRAMEWORK.md:23` | "LWW resolution deterministic — 100% deterministic" | **YES, and then VIOLATED** | `crdt-lwwreg/src/lib.rs:30-35` has no tie-break → row 4 below |
| 2 | `docs/research/spreadsheet/CELL_ONTOLOGY.md:56-147` | head / body / tail cell paradigm | **YES — highest fidelity in the repo** | `src/spreadsheet/core/CellHead.ts` (792 lines, 54 tests), `CellBody.ts` (497, 33), `CellTail.ts` (618, 63) |
| 3 | `research/phase6_advanced_simulations/EMERGENCE_TAXONOMY.md` | emergence scoring w/ novelty factors | **YES** | `src/core/emergence/detector.ts:5` names the doc in its own header ("Based on EMERGENT_GRANULAR_INTELLIGENCE research"); `detector.ts:172-174` implements the 0.4/0.3/0.3 novelty weights; `__tests__/detector.test.ts` exists |
| 4 | `docs/research/DREAMING_TEST_FIXES.md` | "52/52 tests passing", with line citations | **YES — verified exactly** | `src/core/__tests__/dreaming.test.ts` = 52 `it(` blocks; doc's cited lines 221 and 317 both land on the named tests |
| 5 | `docs/research/spreadsheet/REASONING_EXTRACTION_SPECS.md:1955-1988` | 15-type step taxonomy | **NO — 27% overlap, different taxonomy** | row 2.1 |
| 6 | `docs/research/spreadsheet/CONFIDENCE_SCORING_SPECS.md:44-140` | 6 weighted dimensions + presets | **NO — 0 of 6 identifiers exist** | `patternStability` appears in 3 files, **all markdown**, none in `src/` |
| 7 | `research/phase6_advanced_simulations/EMERGENCE_PREDICTION_SUMMARY.md:19-31` | 83.7% accuracy, 63.7 ms | **NO — the function returns zeros** | row 2.2 |
| 8 | `research/phase6_advanced_simulations/THEORETICAL_LIMITS.md:78` | Bekenstein bound `I ≤ 2πER/(ħc ln2)` | **NO — code inverts it to a product** | row 2.3 |
| 9 | `research/CRDT_Research/MATHEMATICAL_REVIEW.md:462-478` | Theorem 6, `N_max = α/(γ'-β) ≈ 16 cores` | **NO — the theorem's precondition is false** | row 2.4 |
| 10 | `research/CRDT_Research/README.md:9-16` | 98.4% latency, 100% hit rate, 23x | **NO — both headline metrics are literals** | row 2.5 |
| 11 | `docs/archive/research-breakdown/*` (59 files) | R2–R8 "Ready for Implementation" | **NO — 0 of 11 concepts in `src/`** | row 3 |

### 1.1 The two rows that matter most

**Row 2 — `CELL_ONTOLOGY.md` is the repo's only clean research→code trace, and it is clean at field level, not just name level.** The spec declares `interface CellHead { inputs: InputChannel[]; sensations: Sensation[]; recognizers: PatternRecognizer[]; validators: Validator[] }` (`CELL_ONTOLOGY.md:98-109`) and `src/spreadsheet/core/CellHead.ts:203-215` declares the same four fields with the same names and the same imported types, plus a test file with 54 cases. `CellBody` and `CellTail` follow the same three-way split. This is what a forward trace looks like when it works — and it is the *only* one in 890 research files.

**Row 1 is the interesting inversion.** The research doc's criterion was written first and the code that claims to satisfy it does not. See §2.1.

---

## 2. Four findings, re-derived before reading, then shown wrong or unsupported

Every constant below was computed from first principles *before* opening the document that claims it.

### 2.1 STALE — the LWW-determinism criterion, and the commit that made it wrong

**The claim** (`research/CRDT_Research/VALIDATION_FRAMEWORK.md:23`, dated 2026-03-13):

> | **Conflict Resolution** | ∀ conflicts: LWW resolution deterministic | Conflict injection test | **100% deterministic** |

The accompanying test `test_ta_crdt_lww_determinism()` (`VALIDATION_FRAMEWORK.md:51-68`) only ever writes timestamps 100 then 200, i.e. it never constructs a tie — so it cannot fail.

**What shipped.** `crdt-lwwreg/src/lib.rs:30-35`:

```rust
pub fn merge(&mut self, other: &Self) {
    if other.timestamp > self.timestamp {   // strict >, no tie-break
        self.value = other.value.clone();
        self.timestamp = other.timestamp;
    }
}
```

Timestamps come from `SystemTime::now().as_millis()` (`lib.rs:12`) — **millisecond** resolution, from two independent replicas.

**Re-derived:** with a tie, `merge` keeps `self`.

```
merge(A,B) = 'a-from-A'      merge(B,A) = 'b-from-B'     -> DIVERGES
```

Merge is therefore not commutative under ties, and the value two replicas hold depends on the order they happened to merge in. The criterion is false in the code that exists to satisfy it.

**The commit pair:**
- `crdt-lwwreg` `4b2472a` (2026-06-11) "fix: add lib.rs content + Cargo.toml fixes" — the merge lands with no tie-break.
- `crdt-map` `75f3b6a` (2026-06-06) already had the correct rule, and `crdt-core` `2cd6a0f`/`dacaaeb` (2026-06-08) fixed it too.

So: **the research claim of 2026-03-13 was true of no implementation, and one sibling repo got it right 8 weeks before the sibling that got it wrong shipped.** `crdt-core/src/lww.rs:46-54` and `crdt-map/src/lib.rs:201-212` both break ties on `node_id`/`replica_id`. Only `crdt-lwwreg` does not.

**This is the same shape as the orchestrator's `lossShaOf` row, and it is worse.** `lossShaOf` was a real bug that got fixed. This one is a research criterion that was never met by the code named after it, and the fix exists in a sibling repo that nobody copied from.

### 2.2 The 83.7% accuracy claim has no producer

**The claim** (`EMERGENCE_PREDICTION_SUMMARY.md:19-31`): "Prediction Accuracy **83.7%** ✅ EXCEEDED", "Real-Time Performance **63.7ms** ✅ MET", "Overall Grade: A", "**Status**: COMPLETE AND VALIDATED", "**Recommendation**: READY FOR DEPLOYMENT".

**What exists** (`emergence_prediction.py:1076-1089`):

```python
def compute_accuracy_metrics(self) -> Dict[str, float]:
    if len(self.prediction_history) < 2:
        return {}
    # This would be populated with validation results
    # For now, return placeholder structure
    return {"overall_accuracy": 0.0, "high_confidence_accuracy": 0.0,
            "average_lookahead_error": 0.0, "type_distribution": {},
            "false_alarm_rate": 0.0}
```

Verified by AST, not by reading — every value in the returned dict is a `Constant` node:

```
values=[Constant(0.0), Constant(0.0), Constant(0.0), Dict(keys=[], values=[]), Constant(0.0)]
```

And the function is **never called**. `grep -rn compute_accuracy_metrics` over the whole repo returns the definition and two README mentions — zero call sites.

**So the document's success table is a table of numbers that no code in the repository can produce.** Not "measured and later invalidated" — never measured. The 63.7 ms timing has the same status: no benchmark harness, no results file, no timing code.

`prediction_results.json` in the same directory confirms the real behaviour — a single prediction at `confidence: 0.5`, `novelty_score: 0.0`, `te_trend: "unknown"`, which is a *demo* output, not a validated one.

### 2.3 Bekenstein: the markdown is right and the code multiplies instead of divides

**The claim** (`THEORETICAL_LIMITS.md:78`): `I ≤ 2πER/(ħc ln2)`, with a worked example "I ≤ ~2.6×10⁴² bits". The formula in the markdown is correct.

**The code** (`impossible_simulations.py:454-457`):

```python
# Bekenstein bound: I ≤ 2πER / (ħc ln2)
limits['bekenstein_bound'] = (2 * math.pi * self.fundamental_constants['h'] *
                              self.fundamental_constants['c'] * math.log(2))
```

**Re-derived:**

| | value |
|---|---|
| code produces `2πhc ln2` | **8.6513e-25** |
| correct, 1 kg collapsed to Schwarzschild radius, `2πER/(ħc ln2)` | **3.83e16 bits** |
| ratio | **2.26e-41** |

The code multiplies by `c` where it should divide by it, and drops `E` and `R` entirely. It is not a bound on anything — and it is reported as one, in `FUNDAMENTAL_LIMITS` output, and used as `max_density` for the `memory` phenomenon (`impossible_simulations.py:484`).

The markdown (`THEORETICAL_LIMITS.md:78`, `IMPOSSIBLE_SIMULATIONS_SUMMARY.md:150`, `IMPOSSIBLE_SIMULATIONS_README.md:119`) states the correct formula in all three places. **The docs are right and the executable contradicts them; nothing caught the divergence because the executable's output is never compared to the docs.**

For contrast, the other three constants in the same block *do* re-derive: Landauer `kT ln2` @300 K = 2.8710e-21 J (reports 2.8717e-21, 0.02% off), Shannon `log2(11)` = 3.4594 (exact), Margolus–Levitin `h/4` = 1.6565e-34 (exact, though `E` is implicit — it silently assumes E = 1 J). **Three correct, one inverted.**

### 2.4 Theorem 6: the theorem's own precondition is false in the repo's own data

**The claim** (`MATHEMATICAL_REVIEW.md:462-478`): `N_max = α/(γ'-β)`, "For typical AI workload parameters: **N_max ≈ 16 cores**", "Beyond 16 cores, CRDT traffic exceeds MESI traffic", marked "**Correctness: ✅ VERIFIED**".

The theorem is stated *conditionally*: the bound applies **when γ' > β**.

**Re-derived from the repo's own `traffic_bounds.json`**, fitting the two traffic series:

```
mesi(N)  = 70400 + 14400·N
crdt(N)  = 64000 +  6400·N
        ⇒ γ' = 6400  <  β = 14400      precondition γ' > β is FALSE
        ⇒ N_max = α/(γ'-β) = -8.8      (negative: no crossover exists)
```

Direct solve: `70400 + 14400N = 64000 + 6400N` → `N* = -0.8`. **CRDT traffic is lower at every core count**, and the reduction *grows* with N (22.6% → 52.3% from 2 to 64 cores). The repo's own data file prints `status: "MESI_TRAFFIC_HIGHER"` on all six rows — i.e. the data contradicts the theorem, in the same directory, and the review cites that same data as confirming the theorem ("52.2% reduction at 64 cores, less than expected" — it is the *best* result in the table, not the worst).

**A theorem whose stated precondition is false, marked ✅ VERIFIED, contradicted by the artifact in its own directory.** This is the "validated" in `README.md`'s "Simulation results confirm trend".

### 2.5 The 98.4% headline: both halves are literals, not measurements

**The claim** (`research/CRDT_Research/README.md:9-16`): Average Latency 122.6 → 2.0 cycles (98.4% reduction), Hit Rate 4.4% → 100% (23x).

The arithmetic is right — I recomputed 98.37% and 22.73x. **The problem is what is being averaged.**

- **Latency 2.0 is a constant, not a distribution.** `CRDTSimulator.read` (`:374`) and `.write` (`:402`) both `return self.config.CRDT_LOCAL_ACCESS_CYCLES` — a class attribute set to `2` (`:40`). `merge()` (`:406-419`) returns `CRDT_MERGE_CYCLES` (also 2) but **never appends it to `latency_history`** — `grep -n "latency_history.append"` returns 8 sites, all in MESI, plus the two CRDT local-access ones. **152,370 merges were performed across the 98 CRDT runs and none of them contributed a cycle to the reported latency.**

  In `raw_results.json` all 98 CRDT runs have `avg_latency`, `p50_latency` and `p99_latency` **all exactly 2.0**. p99 = p50 = mean is not a measurement; it is the signature of a constant. A p99 equal to the mean is the tell.

- **Hit rate 100% is a literal.** `get_stats()` (`:433-435`) returns `'misses': 0, 'hit_rate': 1.0, 'efficiency': 1.0` — hardcoded, never computed. The sibling simulator does the same at `crdt_vs_mesi_simulator.py:647` with the comment `hit_rate = 1.0  # Always local`.

So the 98.4% is `(MESI measured − 2) / MESI measured`, where the numerator's CRDT term is a class constant. **The 2.0 cycles would be unchanged if the merge cost were 2,000 cycles per merge.**

I re-ran `thirty_round_simulation.py` end to end to confirm reproducibility: it prints `MESI Average Latency: 122.6 cycles / CRDT Average Latency: 2.0 cycles / Latency Reduction: 98.4%` and `✓ 70% latency reduction claim VERIFIED`. **The simulation verifies its own hardcoded constant.** This is the same defect class as the `logtensor` row in memory: the suite certifies that the model runs, not that the mechanism is exercised.

*(One real defect, reported not fixed: `impossible_simulations.py:797` writes to the hardcoded relative path `research/phase6_advanced_simulations/impossible_simulations_report.txt` and raises `FileNotFoundError` unless cwd is the repo root. It is why my first run crashed after printing all results.)*

---

## 3. `docs/archive/research-breakdown/` — what got archived, and why

**59 files, R2–R8** (R2:8, R3:7, R4:9, R5:8, R6:10, R7:8, R8:9). There is a stated reason. It is one reason for all 59.

`docs/RESEARCH_ARCHIVE_INDEX.md:143-148`:

> **Archived**: 2026-03-09
> **Reason**: Repository cleanup and organization
> **Method**: Moved historical research to dedicated archive structure
> **Retention**: All research preserved indefinitely

**Distribution of reasons: `Repository cleanup and organization` × 59 (100%). `Superseded by implementation` × 0. `Never implemented` × 0. `Refuted` × 0.**

Per item, there is nothing. I checked four ways: a `Reason:`/`Status:`/`Disposition:` front-matter field (the only `reason:` hits are TypeScript interface fields inside code blocks, e.g. `BREAKDOWN_R2_ORCHESTRATOR_PROTOCOL.md:281`); an `archived/superseded/deprecated` statement (10 files match, and all 10 are false positives — `modelDeprecated: boolean` at `R2_MODEL_CASCADE.md:540`, a prose "No longer bound by…" at `R7_ASCENSION.md:195`, an enum comment at `R6_IMMORTALITY.md:151`); and any inbound link from elsewhere in the tree (4 files reference the directory, all navigation).

**The only per-file metadata is a `Status:` line, and its distribution is the finding:**

| Status | count |
|---|---|
| Design Complete (all phrasings, ✅ and not) | 45 |
| Complete / Research Complete | 5 |
| Design Specification / Design Document / Design Phase / Research & Design | 4 |
| Ready for Use | 1 |
| **"Ready for Implementation"** (in status text) | **~24** |
| **Any statement of why it was archived** | **0** |

**So 59 documents were archived while 24 of them still declared themselves ready for implementation, and not one records what became of that.** The no-deletion doctrine kept the bytes and dropped the disposition. Keeping everything is not the same as recording why — and the `Status:` field actively works against you here, because it preserves the *aspiration* ("Ready for Implementation") and discards the *outcome*.

**And none of it shipped.** I grepped `src/` for the distinctive vocabulary of all seven rounds:

| concept | files in `src/` |
|---|---|
| fractured / box_cascade / morphism | 0 / 0 / 1 |
| morphogen / mythopoet / apophatic | 0 / 0 / 0 |
| omega_point / box_culture / box_dream / temporal_dynam | 0 / 0 / 0 / 0 |

`BREAKDOWN_R2_FRACTURED_BOXES.md:8` frames R2 as superseding "Round 1 … parsing LLM responses into 18 step types". The reasoning-extraction spec (row 5) did ship — but as **8 step types with 27% overlap** (§4.1). So even the thing the archive claims as prior art was rebuilt differently.

**Two defects in the index itself** (reported, not fixed):
- It claims `wave-reports: 15 files`, `simulation-results: 18`, `agent-reports: 25`; actual counts are **17, 17, 27** (`research-breakdown: 59` is correct).
- It documents an `archive/test-outputs/` with "**102 directories** — LoRA Training Outputs". That path **does not exist**; 0 tracked files. Total archive is 121 files, not the ~219 the index's own statistics table implies.
- It dates the archive **2026-03-09**; git records the directory arriving **2026-03-16** in `8dc65c5`. The index asserts a housekeeping event seven days before any history of it exists.

---

## 4. The CRDT question: does the research match the implementation, and is there a fifth port?

### 4.1 Does the research match the code? — Mostly no, and the mismatch is countable

**The research** (`MATHEMATICAL_REVIEW.md`, `VALIDATION_FRAMEWORK.md`, dated 2026-03-13) specifies a catalog: TA-CRDT, LWW-Register, Version Vectors, G-Counter, OR-Set, G-Set, PN-Counter — with a semilattice join for each, and SEC convergence as a goal. It reviews a *hypothetical* implementation; the fleet later built ~8 independent ones.

**Where research and code agree:** nothing measurable. Where they can be compared, they diverge:

**The step taxonomy.** `REASONING_EXTRACTION_SPECS.md:1955-1988` defines 15 step types in three tiers (5 foundational / 5 complex / 5 special). The shipped `src/spreadsheet/core/types.ts:109-118` defines 8:

```
spec 15 → code 8.  In spec, not in code (11): ASSUMPTION CITATION COMPARISON CONTINGENCY
DECOMPOSITION DEFINITION EXAMPLE METACOGNITION SYNTHESIS UNKNOWN VERIFICATION
In code, not in spec (4): DECISION EXPLANATION PREDICTION VALIDATION
Overlap: 4/15 = 27%
```

`METACOGNITION` and `DECOMPOSITION` — two of the five "Complex Types" — appear in **zero** files under `src/`. The spec's own `ReasoningStep` interface shipped, and all 8 shipped enum members are genuinely used (`ANALYSIS` 10 sites, `OBSERVATION` 5, `VALIDATION` 3, the rest 1 each). So this is not a dead enum; it is a **different taxonomy** built by someone who did not have the spec open.

**The one place research and code agree exactly is the FNV canary — and I re-derived it before reading it:**

```
fnv1a64("café Δ 日本語".encode()) = 0x024a555471370b18d     [computed from FNV-1a 64 spec]
crdt-pnvector/src/lib.rs:68 claims 0x024a555471370b18d    MATCH
substrate-foundation/index.js:39 FLEET_CANARY_HASH = '0x024a555471370b18d'   MATCH
```

The canary is the one piece of the fleet's research-derived discipline that is verifiably, byte-exactly reproduced. It is also the only thing in `superinstance-papers` that has *nothing* to do with this repo — `grep -rni "fnv|0x024a5554|café"` over all 4,986 papers-repo files returns **one hit, and it is unrelated** (`docs/research/spreadsheet/GAP_DETECTION_FILLING.md:2299`, a test fixture string). The research that produced the discipline is not in the papers repo.

### 4.2 Is there a fifth port? — There are **eight**, and yes, `crdt-core` is the canonical one

I counted every CRDT implementation in the fleet, not just the ones I was told about:

| repo | lines | types | FNV canary | date |
|---|---|---|---|---|
| `crdt-gcounter` | 120 | GCounter | ✅ | 2026-06-11 |
| `crdt-gset` | 128 | GSet | ✅ | 2026-06-11 |
| `crdt-lwwreg` | 134 | LWWReg | ✅ | 2026-06-11 |
| `crdt-orset` | 162 | ORSet | ✅ | 2026-06-11 |
| `crdt-pnvector` | 144 | PNVector | ✅ | 2026-06-11 |
| **`crdt-map`** | 1140 | GCounter, PNCounter, LWWRegister, ORSet, CRDTMap | ❌ | 2026-06-06 |
| **`crdt-core`** | 754 | GCounter, GSet, LWWRegister, ORSet, PNCounter | ❌ | 2026-06-07 |
| `oxide-crdt` | 876 | + kernel/agent-assignment | ❌ | 2026-06-05 |
| `lau-calm-crdt` | 1820 | ~35 incl. all 5 | ❌ | 2026-05-31 |
| `constraint-crdt` | 4686 | ~35, constraint-preserving | ❌ | 2026-05-09 |
| `cuda-crdt` | 614 | all 5 | ❌ | 2026-04-10 |
| `fleet-crdt` | 1388 | constraint-native merge | ❌ | — |

**The five "one type per crate" siblings are byte-identical below the type definition.** I md5'd the extracted FNV block, the canary test (crate name normalised) and the CI workflow:

```
FNV block   d3ec1afddcefa25a  ×5   (crdt-gcounter, gset, lwwreg, orset, pnvector)
canary.rs   6ff5d4a70b64b713  ×5
ci.yml      59b0056094dcd01c  ×5
```

Five copies of the same 14 lines, five copies of the same test, five copies of the same workflow, for five data types. **That is the four-implementations pattern the fleet already knows about, at 5×.**

**The canonical port is `crdt-core`, and the reason is measurable, not aesthetic.** It is the only crate that is (a) complete — all five catalog types in one place, (b) semantically correct on the two properties that actually decide whether a CRDT is a CRDT:

```rust
// crdt-core/src/lww.rs:46-54  — ties broken deterministically
} else if other.timestamp == self.timestamp && other.node_id > self.node_id {

// crdt-core/src/lww.rs:12  — timestamp is a PARAMETER, so ties are injectable and testable
pub fn new(value: T, timestamp: u64, node_id: u64) -> Self {
```

versus `crdt-lwwreg/src/lib.rs:12`, which calls `SystemTime::now()` internally and therefore **cannot be tested for ties at all**, and `:30`, which doesn't resolve them.

It is also the only one with a real test suite: `.github/workflows/ci.yml` runs `cargo check && cargo test && cargo clippy -- -D warnings`. The five siblings' identical `ci.yml` does the same but each has 1–2 tests.

**Recommendation (not applied, per instructions):** `crdt-core` should be the canonical crate, the five single-type crates should become thin re-exports of it, and the FNV block + canary test should live in `crdt-core` with the other four depending on it rather than each carrying a copy. That converts 5 copies of 14 lines into 1. Note this would *lose* something: the five siblings' per-crate canary is currently what makes the fleet's polyformalism claim checkable crate-by-crate. The correct shape is canary-in-`crdt-core`, re-exported — not canary-copied-five-times.

### 4.3 A live defect in the majority implementation — reported, not patched

**Six of the eight ship an OR-Set. Four of them mint a tag that is not unique across replicas.**

An OR-Set's add-wins guarantee comes from tags being **replica-unique**: if replica A adds X and replica B concurrently adds X, A's remove must not tombstone B's add. That requires the tag to be `(replica, counter)`, not a bare local counter.

| repo | tag scheme | verdict |
|---|---|---|
| `crdt-orset` `src/lib.rs:16-17` | `self.counter` (bare) | **broken** |
| `crdt-map` `src/lib.rs:261-262` | `self.tag_counter` (bare) | **broken** |
| `crdt-core` `src/orset.rs:29-30` | `self.next_tag` (bare) | **broken** |
| `lau-calm-crdt` `src/crdt_state.rs:97-99` | `self.next_tag` (bare) | **broken** |
| `constraint-crdt` `src/orset.rs:47-50` | `(node.to_string(), *seq)` | correct |
| `cuda-crdt` `src/lib.rs:138` | `tag: String` (caller-supplied) | correct by construction |

**Re-derived** (replica A and B both start at counter 0, both add X, A removes X, then merge):

```
[orset] merge(A,B).contains(X)=False  merge(B,A).contains(X)=False
        -> B's concurrent add WAS KILLED (add-loses)      merge commutative: True
[map]   same result
```

Both replicas mint tag 0 for X. A's remove tombstones tag 0, which on merge also kills B's independent add. **The add is lost.**

`crdt-map` states the correct behaviour in its own docstring, `src/lib.rs:222-224`:

> `- If replica A adds element X and replica B removes X concurrently, the add wins (because B hasn't observed A's tag yet)`

**The code contradicts its own documentation, and the docstring describes a property the implementation does not have.** `crdt-map` holds a `replica_id: String` field (`:245`) and never uses it in tag construction.

The failure is *not* a merge-commutativity failure — both directions agree — so it would survive any property-based test that only checks convergence. It is a **semantic** failure, and it is invisible to the only kind of test these crates have (their canaries, and `crdt-orset`'s single add/remove test). To expose it you must assert add-wins on a *concurrent* add, which nothing in the fleet does.

**Why this matters beyond CRDTs:** the same add-wins-on-concurrent-write property is the entire basis of the `MERGE` opcode that `substrate-foundation/index.js:34` exposes to the fleet. The canary proves the fleet agrees on a *hash*. It does not prove the fleet agrees on a *merge*. Those are different claims, and the fleet is currently treating the first as evidence for the second.

---

## 5. The one STALE row the orchestrator asked me to generalise — plus a second

The orchestrator's exemplar checks out and I verified it independently: `xruntime-conformance/CONFORMANCE.md:225` says `quilt-nn` `lossShaOf` **"NO — latin1→UTF-8"**, and `quilt-nn` commit **`84f8551` (2026-09-30 15:28 UTC) "v0.1.1: lossShaOf portable preimage"** rewrote it to `sha256hex(\`${DTYPE_TAG}|8|${f64hex(loss)}\`)` (`src/cellgraph.mjs:75-77`). `CONFORMANCE.md`'s last touch was `9beafab`, 2026-09-30 **07:07:51 -0800 = 15:07:51 UTC** — 20 minutes before the fix. The document is stale by exactly the width of the fix, and nobody went back. Same for `quilt-attention` `scalarSha` (`CONFORMANCE.md:225`, row 2).

**Second instance, same class, in a different direction — a *research* doc made stale by fleet code, with the commit pair:**

| | |
|---|---|
| **Claim** | `research/CRDT_Research/VALIDATION_FRAMEWORK.md:23` — "LWW resolution deterministic … **100% deterministic**" (2026-03-13) |
| **Made wrong by** | `crdt-lwwreg` **`4b2472a`** (2026-06-11) — merge shipped with a strict `>` and no tie-break (`src/lib.rs:30-35`), with millisecond timestamps from `SystemTime::now()` (`src/lib.rs:12`) |
| **Already correct in** | `crdt-map` **`75f3b6a`** (2026-06-06, `src/lib.rs:201-212`) and `crdt-core` (2026-06-08, `src/lww.rs:46-54`) |

**Third instance, and this one is a claim invalidated by a file added to the same directory:**

| | |
|---|---|
| **Claim** | `MATHEMATICAL_REVIEW.md:462-478` — Theorem 6, `N_max = α/(γ'-β) ≈ 16 cores`, "✅ VERIFIED" |
| **Made wrong by** | `simulation/results/traffic_bounds.json` — its own `alpha: 70400, beta: 14400` give `γ' = 6400 < β = 14400`, so `N_max = -8.8` and the `γ' > β` precondition is false; all six rows say `MESI_TRAFFIC_HIGHER` |

I found no more, and I want to be explicit about why rather than imply exhaustiveness: **the `8dc65c5` single-commit structure means a research doc and the code that contradicts it almost never have separable provenance in this repo.** The two staleness rows above were findable only because the claim had a checkable constant in it. Research claims that are purely prose cannot be dated against code by any method available from this repository. **The measurement technique for this question is currently limited to claims that contain a number.**

---

## 6. Most surprising divergence

**A research document's headline result is a hardcoded class constant, and the simulation that produced it re-verifies the constant every run.**

`research/CRDT_Research/README.md` claims CRDT latency is 2.0 cycles against MESI's 122.6, an O(1) vs O(√N) win and a 98.4% reduction. But 2.0 is `Config.CRDT_LOCAL_ACCESS_CYCLES` (`thirty_round_simulation.py:40`), returned unconditionally by both `read` (`:374`) and `write` (`:402`). `merge()` computes a real merge cost (`:419`) and **never records it** — 152,370 merges, zero cycles. Every one of the 98 CRDT runs in `raw_results.json` has `avg_latency = p50 = p99 = 2.0` exactly.

So the fleet's headline intra-chip result compares a *measured* MESI number against a *literal*. I ran it: it prints `CRDT Average Latency: 2.0 cycles` and `✓ Near-constant latency for CRDT VERIFIED` — the 30-round framework's final validation asserts the property that the constant was chosen to have.

What makes it the most surprising rather than merely the most serious: the arithmetic is **correct**. 98.37% really is the reduction from 122.6 to 2.0. Every derived number, the JSON, the summary table and the theorem citations are all internally consistent. The defect is not in any computation — it is that the quantity being computed is named `avg_latency` and does not contain the operation that dominates the cost model. **A research package can be arithmetically flawless, self-consistent across 30 rounds and 196 simulations, and still measure nothing**, because the thing it varies is a constant on one side of the ratio.

This is the same shape as the `lossShaOf` family, one level up. There, the preimage was not what the docstring said. Here, the measurement is not what the metric name says.

---

## 7. Counts

- **Documents examined:** 11 findings traced across 7 trees — 2 in `research/CRDT_Research/`, 2 in `research/phase6_advanced_simulations/`, 3 in `docs/research/spreadsheet/`, 1 in `docs/research/`, 1 in `docs/archive/research-breakdown/` (59 files as one unit). Plus 12 fleet CRDT repos and 2 conformance repos.
- **Findings that left a forward trace into shipped code:** **4 of 11** (36%). `CELL_ONTOLOGY` is the only one faithful at field level; `EMERGENCE_TAXONOMY` and `DREAMING_TEST_FIXES` are real but the first cites a doc that measures nothing and the second is a status report, not a finding.
- **Findings with no forward trace:** **7 of 11** (64%) — including the three with the most quotable numbers in the repo (83.7%, 98.4%, N_max≈16).
- **Now stale, with the commit that staled them:** **3.**
  1. `VALIDATION_FRAMEWORK.md:23` (LWW 100% deterministic) ← `crdt-lwwreg` `4b2472a`, 2026-06-11
  2. `MATHEMATICAL_REVIEW.md:462-478` (Theorem 6, N_max≈16) ← `traffic_bounds.json`'s own `alpha`/`beta`
  3. *Orchestrator's exemplar, confirmed:* `xruntime-conformance/CONFORMANCE.md:225` (`lossShaOf` NO) ← `quilt-nn` `84f8551`, 2026-09-30 15:28 UTC
- **Live defects found, reported not patched:** 4 — OR-Set non-replica-unique tags in 4 repos (§4.3); Bekenstein bound inverted in `impossible_simulations.py:454-457` (§2.3); cwd-dependent crash at `impossible_simulations.py:797`; `RESEARCH_ARCHIVE_INDEX.md` file counts wrong and a documented `archive/test-outputs/` that does not exist (§3).
- **Archive reasons:** 1 reason, applied to 59/59 items. 0 per-item dispositions. 24 items still say "Ready for Implementation" at the moment they were filed.
- **CRDT ports found:** 8 in Rust (not 4), of which 5 are byte-identical below the type. Canonical candidate: `crdt-core` — the only one with all 5 catalog types, deterministic LWW tie-breaking, injectable timestamps, and a CI that runs `cargo test`.

## 8. If you only do three things

1. **Re-derive before you read.** Every single serious finding in §2 was found by computing a constant *first*. The three docs whose numbers survive re-derivation (Landauer, Shannon, Margolus–Levitin) are the three that are correct; the one that does not (Bekenstein) is the one that is wrong. That is a cheap, high-yield filter and it generalises to any research corpus.
2. **Look for `p99 == p50 == mean`.** A reported distribution with zero variance is a constant. It took one line of `set()` over `raw_results.json` to expose the 98.4% headline, and it generalises: any perf claim in the fleet should be checked for variance before its mean is believed.
3. **Make `crdt-core` canonical before adding a ninth port.** The canary proves the fleet agrees on a hash. It does not prove the fleet agrees on a merge, and §4.3 shows 4 of 6 OR-Sets cannot satisfy add-wins. Those are separate claims and the fleet is currently spending effort on the one it can check.
