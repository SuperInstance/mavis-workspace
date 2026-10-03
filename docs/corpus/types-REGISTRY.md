# types-REGISTRY — a type is a schema plus an executable invariant

**STATUS: complete for this lane. 9 types formalised · 48 invariant clauses · 48 watched going red · 0 unwitnessed · 0 hard failures.**

2026-10-02. Lane: build the type registry. Start with the 48, not the 988.

Source: `attachments/0a8430e65b20e823/spreadsheettypesnotcomplete.md` —
verified **988 entries** (`grep -c "^- "` = 988, 1188 lines, 98 sections,
**914 unique names** — 58 names repeat, covering 132 entries).

Run everything:

```
cd /workspace/experiments/types && ./run_all.sh     # exit 0
```

Files: `core.py` (the gate) · `registry.py` graph/linear · `registry2.py`
diagnostic · `registry3.py` canary/logic · `registry4.py` workflow/closure ·
`registry5.py` fixed-width record · `test_types.py` (mutation runner) ·
`gate_test.py` (the gate, and its own mutation) · `mine.py` (the 988) ·
`ratio.py` (the measurement).

---

## 1. The type

```
type T = {
  schema:    (rows, cols, dtype, widths)      // plato-tile-encoder has this
  algebra:   (what operations are legal)
  invariant: (what must hold for a valid instance)    // REQUIRED, EXECUTABLE
  witness:   (how you know an instance is well-formed)
  residual:  (rows/columns that are judgment, not algorithm)
}
```

`invariant` is a **tuple of `Clause`**, and a clause is
`(name, check: Callable -> bool, prose, where)`. Prose is *kept beside* the
machine form, never instead of it.

`core.register()` raises `TypeUncompilable` when the tuple is empty, when any
`check` is not callable, when `status="VERIFIED"` and there is no witness, or
when `status="UNVERIFIED"` and no reason is given. You may file an
unverified type, but only by saying which part you could not execute.

### The gate, proven

`gate_test.py` compiles four bad types and one honest unverified one:

| attempt | result |
|---|---|
| no invariant, `VERIFIED` — the 6.8× constant, typed | **REFUSED** |
| prose invariant (`"the matrix should be symmetric"`) | **REFUSED** |
| `VERIFIED` with no witness | **REFUSED** |
| `UNVERIFIED` with no reason | **REFUSED** |
| `UNVERIFIED` + a real reason (BayesTable) | ACCEPTED, marked `UNVERIFIED` |
| a well-formed type | COMPILED, clause executes |

And then it **neuters its own gate** (`register` → a validator that accepts
anything) and confirms the file goes red: all four bad types compile, the
test reports `MUTATION DETECTED -- gate test has teeth`, exit 0.
A gate test that cannot fail is another canary.

---

## 2. How many of the 988 state a check

The "48 of 988" is not a property of the list. It is a property of the list
**and the rule**, so `mine.py` applies three and reports all of them:

| rule | count | share |
|---|---|---|
| **A.** the line *asserts a property in words* (`rows sum to 1`, `symmetric`, `invertible`, `deterministic`, `no contradiction`) | **12** | 1.2% |
| **B.** the *name* imports an unstated constraint (`closure`, `Cayley`, `parity-check`, `lattice`, `stochastic`, `Betti`, …) | **79** | 8.0% |
| A or B | **86** | 8.7% |
| neither | **902** | 91.3% |

Rule A verbatim, all twelve: `Stochastic matrix` (rows sum), `Marginal
probability table` (col sum), `Cayley table`, `Lie group table`,
`Univalent foundations table` (equivalence = identity), `Consistency proof
table` (no contradiction), `Symmetric cipher table`, `Asymmetric cipher
table`, `Reversible cellular automaton table` (invertible), `DFA table`
(deterministic), `NFA table` (nondeterministic), `Conservation table`.

**The 48 sits inside [12, 86] depending on whose vocabulary you use, and I
am not going to tune a regex to land on it.** The number that survives every
rule is the useful one: **at most 8.7% import any constraint at all, and only
1.2% wrote one down.** Eight of the twelve that did write one down are in
AUTOMATA, CRYPTOGRAPHY, PROOF THEORY and LINEAR ALGEBRA — the sections where
the constraint is famous enough to need no author.

---

## 3. The nine types

| # | type | source line | clauses | red | status |
|---|---|---|---|---|---|
| 1 | `AdjacencyMatrix` | LINEAR ALGEBRA | 4 | 4 | VERIFIED |
| 2 | `PermutationMatrix` | the brief's `rows @ rows == I` | 5 | 5 | VERIFIED |
| 3 | `ConfusionMatrix` | LINEAR ALGEBRA | 7 | 7 | VERIFIED |
| 4 | `CovarianceMatrix` | LINEAR ALGEBRA | 5 | 5 | VERIFIED |
| 5 | `FnvHashTable` | the fleet's own canary | 6 | 6 | VERIFIED |
| 6 | `TruthTable` | LOGIC | 4 | 4 | VERIFIED |
| 7 | `StateTransitionTable` | LOGIC | 7 | 7 | VERIFIED |
| 8 | `TransitiveClosure` | RELATIONS & FUNCTIONS | 6 | 6 | VERIFIED |
| 9 | `FixedWidthRecord` | plato-tile-encoder | 4 | 4 | VERIFIED |

(48 clauses is a coincidence with the "48 of 988". It is not the same 48.)

### A correction to the brief, made executable

The brief offered `assert rows @ rows == I` as **the adjacency matrix**
invariant. It is not — that is the **permutation/orthogonal** invariant, and it
is **false for every real adjacency matrix**: a 4-vertex path graph has
`A @ A` with a zero diagonal where `I` has ones. Both are now typed
separately, and `PermutationMatrix`'s negative is fed a *perfectly valid
adjacency matrix* and watched go red. Conflating the two is itself a schema
with no resolvable authority.

### The clause family that matters: DERIVABLE

Three types carry a clause that **recomputes from an input** rather than
checking the claim against itself:

- `CovarianceMatrix` — `C == numpy.cov(X, rowvar=False)`. A symmetric PSD
  matrix that is nobody's data goes red.
- `ConfusionMatrix` — `C == counts(y_true, y_pred)`. A structurally perfect
  confusion matrix that no prediction run produced goes red.
- `FnvHashTable` — `digest == fnv1a64(constructor(k))`. A well-formed table
  of 64-bit constants that nothing constructs goes red.
- `TransitiveClosure` — `R == closure(base)`.
- `FixedWidthRecord` — the layout re-derived from the source.

> A hash chain proves ORDER and INTEGRITY. Only RE-EXECUTION proves the CLAIM.
> A receipt that re-hashes its own output is circular. So each claim is
> committed to its **inputs**, and the verifier **recomputes**.

Each of these negatives is a table that passes every structural clause it has.

---

## 4. plato-tile-encoder: a schema with no resolvable authority, in three parts

The brief called this repo "a good example". It is better than that, and all
three parts are executable. Parsed live from
`.resolver-state/clones/plato-tile-encoder/src/lib.rs`:

**(a) The comment is right and its derivation is wrong.**
`src/lib.rs:163` declares
`id(64)+question(128)+answer(128)+domain(32)+tags(24)+confidence(4)+ghost(4)+use_count(4) = 384`.
Those eight numbers **sum to 388**. The stated total (384) is *correct*; the
stated composition is *wrong* — `tags` is **20** in the code, not 24. A
comment that is simultaneously correct and wrong can never be caught by
checking its number. Only re-deriving it catches it.
`FixedWidthRecord.DECLARED FIELDS SUM TO THE RECORD SIZE` → **RED**.

**(b) The repo's own size test cannot fail.**
```rust
let bytes = encode_binary(&sample_tile());
assert_eq!(bytes.len(), 384);
```
`encode_binary` is declared `-> [u8; BINARY_SIZE]` with `BINARY_SIZE: usize =
384` (`src/lib.rs:160`). The assertion compares a value's length against its
own type parameter. It is green, it is in CI, and it verifies nothing — the
identical shape to the 6.8× constant and the `>= 16` property test.

**(c) `write_str` truncates silently.**
`bytes.len().min(max)`, no `Result`, no error, no flag. `decode(encode(x)) != x`
for any overlong field and nothing reports it. `FixedWidthRecord.ROUNDTRIP` →
**RED** on a 25-byte tag string in a 20-byte field.

---

## 5. The algebraic/judgment ratio — two answers, and the gap is the point

The question "what fraction of this table is a program" has two defensible
answers and they differ by a factor of 2.4. Quoting one without saying which
is how "95% algorithmic" gets said.

| level | algebraic | judgment | what is counted |
|---|---|---|---|
| **DECISION** | **42.2%** | **57.8%** | the choices you must make to write the table down |
| **CELL** | **98.7%** | **1.3%** | the numbers that end up in the table |

Per-type decision spread: **0.25 … 0.67**. Nothing is 95% algorithmic and
nothing is 95% judgment.

**The finding: the table is a program; the act of writing one down is not.**
Once you have decided what the rows and columns mean, filling the cells in is
a program — 98.7% of them. But producing the instance requires a majority of
human decisions, and those decisions are almost never written down. The
"compile the algorithm, keep the residual" thesis is in much better shape
than 95%-algorithmic would suggest: **the residual is not a residue of the
table, it is the table's entire provenance.**

**The one type where the cells themselves are judgment is the one this fleet
keeps getting wrong.** `StateTransitionTable`: 3 states × 2 inputs = 6 cells,
and **every single one is a business rule**. No cell is computable. The
algorithm can enumerate the table and check that it is total, closed,
reachable and terminating — which is exactly what the "23 workflows that
cannot fail" needed and did not have. The clauses are:

- `TOTAL` — every (state, input) pair has a next state. *A hole here is a
  workflow that cannot fail, and cannot be shown to succeed either.*
- `all states reachable` — an unreachable state is a table nothing can arrive at.
- `has at least one terminal state` — the machine can actually finish.
- `NOT identity` — `delta` is not the identity. *An identity table succeeds
  forever and is indistinguishable from a hung process.*

---

## 6. What the harness caught in my own work

The runner rejects a negative that fails to trip its own clause as a **hard
failure** (equivalent mutant), and treats a clause that *raises* as RED rather
than a crash. Both earned their keep. **It found 10 real defects in the
registry I was writing**, of which four are worth recording because they are
the general disease:

1. **A clause implied by a sibling clause is a comment.** I wrote
   `diag(C) <= rowsum(C)` for the confusion matrix. `diag[i]` is one of the
   summands of `rowsum[i]`, so non-negativity already implies it. My negative
   (`C[0,0] = 99`) failed to trip it because raising the diagonal raises the
   row sum with it. **Deleted**, and replaced with the one non-vacuous
   constraint a confusion matrix has: derivability from real predictions.
2. **Same disease in the truth table.** `COMPLETE` and `CONSISTENT` are not
   separable in a 2ⁿ×(n+1) table — completeness *implies* consistency. Merged
   into one clause.
3. **Indices vs names.** `_reachable` and `_has_terminal` tested `t in idx`
   where `idx` was keyed by state **names** and `t` was a state **index**, so
   the test was permanently false. Reachability was vacuous; terminal-detection
   was vacuously *true* for every table. Both were green and both meant
   nothing.
4. **A threshold I guessed and then measured.** The FNV avalanche floor: I wrote
   `>= 8` and it failed the good instance, which meant the true floor was
   lower. Measured: fnv1a64 → **7**, 8-bit truncation → **1**, constant → 0.
   Threshold set to the measured 7, negative set to a realistic truncation bug.

Also: a negative that moves a permutation's `1` rather than duplicating it is
still a permutation; `np.eye(2)` is square, so it is not a `square` negative;
assigning `2` into a `bool` array silently yields `True`; `bytes([n])` raises
past 255. None of these are exotic. They are what happens when you write 48
invariants in an afternoon, and they are exactly what a reviewer's eye misses.

---

## 7. What is NOT here

39 of the 48 are not formalised. The obvious next ten, all with a stated
constraint in the source list: `StochasticMatrix` (rows sum to 1),
`CayleyTable` (associativity, Latin square), `PartitionTable` (blocks disjoint
and covering), `IncidenceMatrix` (Betti-number computability),
`ReversibleCellularAutomaton` (invertibility), `ConsistencyProofTable`
(no contradiction), `DFATable`/`NFATable` (determinism), `ParityCheckMatrix`
(codewords in the kernel), `ConservationTable`.

Two honest `UNVERIFIED` filings to start the negative space, with reasons
rather than excuses: `BayesTable` (posterior is a ratio of sums over the
joint; no closed form without the likelihood table) and `KGCompletionTable`
(the scoring function is the judgment; there is no invariant to execute
without naming the model, and naming the model is the thing that is undecided).

And the 902: **not one of them is a registry entry, and that is the correct
outcome.** A registry of invariant-less types is the thing we are trying to get
away from.
