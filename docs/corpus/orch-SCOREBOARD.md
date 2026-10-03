# ORCH SCOREBOARD — round 1, gh-dungeons

**Status: THE ROUND IS EMPTY. 0 of 4 lanes are scoreable.** Written 2026-10-02, minutes
after the four briefs went out. All four lanes filed `Status: STUB`. None filed a receipt.
The table below is empty *on purpose* and this file will not fill it with adjectives.

**The scoreboard itself is not a canary that cannot fail.** It has been run against a
negative control and produced a number: **2 of 4 reference lanes scored, 2 disqualified,
1 tie left unbroken.** Paste of that run is §5. Emptiness is a property of the round, not
of the board.

---

## 1. How to run it

```bash
cd /workspace/projects/fleet-triage/orch-score
python3 score.py --receipts r1-receipts --label "ROUND 1"   # the real round
python3 score.py --lanes A-full,A-twin,B-null,C-honest       # the negative control
```

Files: `SEEDS.json` (frozen seeds + fault catalogue) · `RECEIPT.schema.json` (the
fillability contract) · `harness.py` (injects faults, measures catches) · `score.py`
(scores, or refuses to) · `gaps.py` (what each lane is missing) · `fixtures/` (controls).

## 2. THE SEED MANIFEST — the most important thing here, and it is unglamorous

`SEEDS.json` is **mine, not a lane's.** Seeds `20261001…20261005`, plus the nine fault
ids `F1…F9` and their nine surfaces. A lane may not choose seeds. **A lane that ran a
different set has voided its own score, and the void is reported as a void — not as a low
score, and not silently dropped.** Without this the entire comparison is void and the rest
of this file is decoration.

*What each lane has actually run so far, read mechanically from the four reports:*

| lane | report | names a seed | run evidence § | claims no-model | own code dir |
|---|---|---|---|---|---|
| JEVSAMPLER | 8.8 KB | **no** | claimed, not shown | no | no |
| SYNCOPATION | 9.4 KB | yes | claimed, not shown | no | **yes** (`r1-syncopation/`) |
| TYPEFUNC | 6.4 KB | yes | no | no | no |
| NOENGINE | 5.9 KB | **no** | no | **yes (claimed)** | no |

**One lane has code. Zero lanes have a receipt. So the board is empty, and the emptiness
is the correct reading, not a placeholder.**

## 3. The criteria — mechanical, with the number each one produces

Nothing here is "better architecture". Each is a count someone else can re-run.

| # | criterion | measured as | gate? |
|---|---|---|---|
| C1 | runs with no model at all | dungeon completes with the model **forbidden by construction**, not stubbed | **GATE** — fail ⇒ unscored |
| C2 | steps to first playable frame | median over the 5 seeds, steps | — |
| C3 | decisions made | Σ over seeds | — |
| C4 | **justified vs least resistance** | unjustified = decisions − justified; a lane defines justified *mechanically* or it is 0 | — |
| C5 | **checks that can be made to fail** | n_falsifiable — **tested, never asked** | **GATE** — 0 falsifiable ⇒ unscored |
| C6 | injected faults caught | n / 9, **measured by the harness, not self-reported** | — |
| C7 | **faults caught silently** | caught but `reported=false` — **counted and shown separately, never folded into C6** | — |

**C5 is the one that matters.** A check declares which fault surface it is sensitive to;
the harness injects that fault and requires the check to go red. A check that claims
sensitivity and never fires is **CANARY-NULL** and disqualifies the lane. This is the
mechanical form of "a check that cannot fail" — and it is the single most common way a
fleet convinces itself it is verified.

**The lane's own claim is kept, and compared.** `SELF_REPORT` never enters the score. If a
lane says 9 and the harness measures 4, that is a **reported finding**, not a rounding
error. The receipt binds the ledger; only re-execution proves the claim.

## 4. The board

```
ROUND 1 — 2026-10-02 — scored=0 of 4 · unscored=4 · voids=0
┌──────────────┬────────┬────────┬─────────┬────────┬────────┬─────────┬──────────┬───────┐
│ lane         │ C1     │ C2     │ C3      │ C4     │ C5     │ C6      │ C7       │ rank  │
│              │ no-mdl │ steps  │ decs    │ un-just│ fals/chk│ caught  │ silent   │       │
├──────────────┼────────┼────────┼─────────┼────────┼────────┼─────────┼──────────┼───────┤
│ JEVSAMPLER   │   —    │    —   │    —    │    —   │  —/—   │   —/9   │    —     │UNFILLED│
│ SYNCOPATION  │   —    │    —   │    —    │    —   │  —/—   │   —/9   │    —     │UNFILLED│
│ TYPEFUNC     │   —    │    —   │    —    │    —   │  —/—   │   —/9   │    —     │UNFILLED│
│ NOENGINE     │   —    │    —   │    —    │    —   │  —/—   │   —/9   │    —     │UNFILLED│
└──────────────┴────────┴────────┴─────────┴────────┴────────┴─────────┴──────────┴───────┘
every cell is — because no lane produced a number. Not one cell is a guess.
```

## 5. THE NEGATIVE CONTROL — the number, pasted

Same tool, same seeds, same faults, on four **reference lanes I wrote**, not the real ones:

```
A-full    SCORED    c1=True  falsifiable 9/9  caught 9/9  silent 0  value 100.0
A-twin    SCORED    c1=True  falsifiable 9/9  caught 9/9  silent 0  value 100.0
          -> TIE-1, margin 0.0 <= noise floor 0. TIE LEFT UNBROKEN. ✔ rule 3 fires
B-null    UNSCORED  c1=True  falsifiable 0/4  caught 0/9
          ! CANARY-NULL: 4/4 checks cannot be made to fail
          ! SELF-REPORT DIVERGES: claims 9 caught, harness measured 0
C-honest  UNSCORED  c1=False
          ! C1 no-model run FAILED — the dungeon halts without a model
          ! SELF-REPORT DIVERGES: claims 4 caught, harness measured 0
```
```
noise floor: axis = per-seed (5 seeds), spread = 0 on deterministic fixtures
scored=2   unscored=2          <-- the board produces a number, and it can produce zero
```

**What this proves, and what it does not.** It proves the scorer **discriminates**: a green
board that cannot fail is caught, an honest failure is caught, a self-report that
overclaims is caught, and a tie is not broken. It does **not** prove the noise floor is
right — on deterministic fixtures the per-seed spread is 0, so the tie rule was exercised
only on an exact tie. **The floor is currently degenerate and I am not going to pretend
0.0 is a measurement.** It becomes meaningful the first time two real lanes land on
different seeds' worth of variance, and until then *no margin should be trusted*.

**Two real bugs the control caught in the scorer itself**, both fixed and both of the same
family: `importlib.import_module("lane")` returned the **first** lane's module for all four
(sys.path import + a shared module name ⇒ three different architectures silently scored as
one), and a `split('    return {')` patch truncated a fixture's `checks()` because the same
string occurs inside `meta()`. **A fan-out evaluator that loads its subjects by name will
happily score one subject four times and report it as four results.** Load by file path with
a namespaced module name.

## 6. THE FILLABILITY CONTRACT — what each lane must expose, exactly

`RECEIPT.schema.json` is the contract; `gaps.py` computes the gap. Required of all four:

1. **`entrypoint`** — the ONE command that runs the dungeon headless. Not a description.
2. **LaneAdapter** — `make(seed, faults)`, `meta(seed, world)`, `checks(world)`,
   `needs_model()`. **The harness calls the lane; a lane that only describes itself is not
   reachable and scores nothing.**
3. **All 5 frozen seeds**, echoed in the receipt. Fewer ⇒ **VOID**, reported as a void.
4. **C2/C3/C4 as numbers** — `steps_to_first_playable_frame`, `decisions`,
   `justified_decisions`, with the *rule* that separates justified from least-resistance
   stated as code, not prose.
5. **checks{ name → {sensitive_to: [...surface ids from SEEDS.json]} }** — a check with no
   declared surface is judged NULL and counts against the lane.
6. **C1 evidence** — a run with the model unavailable *by construction*.
7. **`SELF_REPORT`** — the lane's own claim, kept only to be compared against measurement.
8. **`honest_failures`** — **allowed to be non-empty.** A lane that lists what it does not
   meet has done the thing this whole lane is for.

**Per-lane, from the four reports as they stand:**

| lane | the one thing it is closest to having | what is missing |
|---|---|---|
| JEVSAMPLER | typed/preference cell split; §7 promised | no seed named, no run shown, no adapter |
| SYNCOPATION | **real Go code, vendored upstream, three worlds per the lag design** | no run output, no adapter, no measured blind-interval |
| TYPEFUNC | option-set-as-state-function; a justified/least-resistance split | no run evidence, no seed contract, no adapter |
| NOENGINE | the strongest *stated* no-model claim — `f(state, script)` and nothing else | **claim is unbacked**: it has never run, so C1 is asserted, not measured |

## 7. Where a design with no score goes

**Unranked is a first-class outcome and it is not a loss.** Three buckets, all reported:

- **SCORED** — passed both gates, ranked.
- **UNSCORED · C1 FAILED** — could not run model-free. *An honest failure here is worth more
  than a passing C5, because C1 failing is a fact and a passing check that cannot fail is
  not.* (C-honest is the fixture that proves the board can say this.)
- **UNSCORED · CANARY-NULL** — reported N/9 caught, and zero of its checks can go red.
  **The claim is void, not the score bad.** This is the worst state and it is currently
  reachable by a lane that never runs a single fault injection.

## 8. What this buys the team, stated against the three flaws

- *Lanes die when briefs are broad* → the contract is mechanical, so a lane can be wrong
  **specifically** instead of vaguely. Fillability is checkable in seconds.
- *No lane has a second turn* → the receipt is a **stable handle**. Round 2 re-runs the
  same adapter on the same seeds, so a lane is a *series*, not a one-shot, and the scoreboard
  becomes a time series instead of a fresh reading.
- *I am the only integration point* → I do not rank. `score.py` ranks, or refuses to. My only
  remaining job is running it, and it is one command.

**And the honest limit:** this ranks *four dungeons on nine injected faults and five seeds.*
It is a floor, not a verdict on the architectures. The seeds and the fault catalogue are
mine, so a lane could in principle be tuned to them — which is why C4 and the syncopation
question ("which of its own decisions was never justified, and did system-two notice") are
**not** in the score and belong in round 2, where a lane gets a second turn on the same
seeds and the interesting comparison is its own trajectory, not a single number.

---

*Board: `orch-SCOREBOARD.md` · Tool: `orch-score/` · Branch: `orch-scoreboard` · No pushes.*
