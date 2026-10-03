# BUILD-01 — BUILDER lane

Two artifacts shipped. Both handles were run; both cold clones verified.
Kill criterion satisfied: **the handle was executed, and it caught two bugs the
test suite did not.**

```
ARTIFACT 1  plainsong compile --strict   branch build/strict-gate  commit 2ff8589
ARTIFACT 2  fleetset/fleetlint n_eff     commit f637c9a
```

---

## Kill criterion, and what running the handle actually caught

> **Run the primary affordance before you ship it.** Not the suite. The handle.

This was worth more than a green suite twice, and both times the thing it
caught was in the *message*, on a path no test would ever have been written
for:

1. `compile --strict --no-midi` announced **"refusing to write MIDI"** — for a
   MIDI that `--no-midi` had already said it would not write. The gate list
   and the write list were two separately-maintained expressions of the same
   intent, and they had drifted. Fixed by mirroring `midi=None if args.no_midi
   else midi_path`. There is no test for the wording of an error message; there
   is a `grep`.
2. `fleetlint`'s first detector produced **13 findings on 3 fixture files, 12
   of them noise** — the word "panel" in a docstring, a neural-network
   `ensemble`, a dict called `votes`. Every one of them would have shipped. A
   test suite written against that detector would have passed, because the
   tests would have been written to match it.

---

# ARTIFACT 1 — `plainsong compile --strict`

**What you can now do that you could not before:** a build step can refuse to
produce a MIDI file from notation the compiler itself says it did not
understand.

**Repo:** `SuperInstance/plainsong` @ `653eba2` (v1.6.0), branch
`build/strict-gate`, commit `2ff8589`. **Not pushed** — not my repo.

### The seam, reproduced before a line was changed

```
$ plainsong compile garbage.song
Garbage Test  --  Am, 96 bpm, 4/4
7 notes across chords (3), melody (4), bogus (0)
midi  .../garbage-test.mid
warn  garbage.song:6: warning: [V1] chords covers 1 bar(s), the section runs 4
warn  garbage.song:7: warning: melody row: nothing understood QQQQ; silence there instead
... 11 more
EXIT=0

$ plainsong -q compile garbage.song -o out.mid
EXIT=0                                    <-- and now: nothing at all
$ python3 -c "import struct;print(struct.unpack('>HHH',open('out.mid','rb').read()[8:14]))"
(1, 3, 480)                               <-- a valid format-1 MIDI, 231 bytes

$ plainsong compile --strict garbage.song
plainsong: error: unrecognized arguments: --strict
```

Three lines, one defect:

| line | what was true |
|------|---------------|
| `plainsong/interfaces/cli.py:169` | `compile_file()` writes the artifact; diagnostics are read **after**, at `:191` |
| `plainsong/interfaces/cli.py:186` | `if not args.quiet:` drops the only trace; `return 0` at `:205` regardless |
| `plainsong/interfaces/cli.py:1278-1303` | `compile` had no `--strict`. It existed on `check` (`:1334`) — the command no build runs |

**The brief's note is confirmed and explains itself:** *total* garbage fails
earlier (`result.ok` is False at `:187`), so a gate on the exit path catches
nothing. The case that matters is **partial** garbage — it parses, emits
notes, emits eleven warnings, exits 0.

### The handle, run

```
$ plainsong -q compile --strict garbage.song -o out.mid
error  --strict: 11 warning(s) -- refusing to write MIDI
warn  garbage.song:7: warning: melody row: nothing understood QQQQ; silence there instead
  ... and 3 more
>>> EXIT=1
>>> artifact present? no
```

```
$ plainsong -q compile garbage.song -o old.mid          # default, unchanged
>>> EXIT=0  artifact: WRITTEN
$ plainsong -q compile --strict clean.song -o clean.mid # a real song
>>> EXIT=0  artifact: WRITTEN  bytes: 280
$ plainsong -q compile --strict garbage.song --no-midi
error  --strict: 11 warning(s)                          # <- was "refusing to write MIDI"
$ plainsong -q compile --strict garbage.song -o a.mid --audio a.wav
error  --strict: 11 warning(s) -- refusing to write MIDI and audio
$ plainsong compile --strict --json garbage.song
{"compiled": false, "blocked_by": "--strict", "written": {"midi": null, ...}}
```

### Design, and the part worth copying

- **The gate is in `compile_text()`, before the first byte is written** — not in
  the CLI after. A gate that reports the problem and leaves the artifact on
  disk has not gated anything; it has annotated.
- **It reads warnings, not info**, matching `check --strict`. Gating on info
  would make the flag unpassable for every valid file carrying a remark, which
  is a gate that trains people to pass the flag somewhere else.
- **It ignores `-q`.** "Only print what was asked for" is reasonable for a
  success and unreasonable for a refusal, so the gate borrows an unquiet `Out`
  rather than reaching past it. `--json` gets `compiled: false` with null paths.
- **Off by default.** `plainsong compile` on the same file still exits 0 and
  still writes.

`docs/verification.md` §1 already documented this exact failure class —
*"`plainsong spec` printed `no specs found` and exited 0 … It exits 1 now."*
The change is in the repo's own house style, not imposed on it.

### The tests, and proof they die

`tests/test_strict.py`, 19 tests. **The suite was mutated three ways and each
mutation was checked to turn a test red before I believed the suite:**

| mutation | result |
|----------|--------|
| gate removed entirely | **killed** — 7 failures, 1 error |
| gate moved *after* the write | **killed** — 4 failures |
| gate made quietable by `-q` again | **killed** — 1 failure, the right one |

The third is the one that matters: the only test it kills is
`test_quiet_cannot_hide_a_refusal`. That test exists because the original defect
was `-q` making the only trace disappear.

**No behaviour change, measured not asserted:**

| | tests | result |
|---|-------|--------|
| `master` (baseline) | 812 | OK, 1 skipped |
| `build/strict-gate` | 831 | OK, 1 skipped |

Delta is exactly +19. **Zero pre-existing tests changed outcome.**

### Files

`plainsong/pipeline.py` (+strict, `blocked`, `strict_violations`) ·
`plainsong/interfaces/cli.py` (+`--strict`, the gate block) ·
`tests/test_strict.py` (new) · `tools/demo_strict_gate.py` (new, one command) ·
`CHANGELOG.md` · `docs/verification.md` §1 · `AGENTS.md`

### One command, from a cold clone

```bash
git clone -b build/strict-gate <repo> && cd plainsong && python3 tools/demo_strict_gate.py
# 6/6 expectations, exits non-zero if any is violated
```

**Hand-off → PLAYER:** `compile --strict` refuses a file that *parses* but
warns. The thing to try to break is the **warning taxonomy**: find a `.song`
in your own data that is genuinely fine and gets refused, or — worse — one that
is genuinely broken and produces no warning at all. A gate is only as good as
the signals under it, and I did not audit those, I only gated on them.

---

# ARTIFACT 2 — `fleetset/fleetlint` (rule `n_eff`)

**What you can now do that you could not before:** point a zero-cost, zero-
dependency linter at a repository and get told which panels are worth fewer
independent votes than they claim — including the ones nobody ever measured.

**Repo:** created at `/workspace/projects/fleetlint`, commit `f637c9a`. I
created it; it is not pushed anywhere.

```bash
git clone <repo> && cd fleetlint && make demo
```

### The rule, in one line

`n_eff/k ≥ 0.5  ⟺  ρ ≤ 1/(k−1)`. The published warning line and the
correlation ceiling are the same statement, and it inverts the intuition:

| k | correlation ceiling | at ρ=0.1, efficiency |
|--:|-------------------:|---------------------:|
| 3  | 0.500 | 83% |
| 5  | 0.250 | 71% |
| 10 | 0.111 | 53% |
| 20 | 0.053 | 35% |

**The bigger the panel, the tighter the independence it must clear.** "We used
twenty judges" is a claim about how much of the twenty survived.

### The handle, run

```
$ python3 -m fleetlint n_eff tests/fixtures
FAIL tests/fixtures/bad_panel.py:8
      k=5, rho=0.5 -> n_eff=1.67 of 5 votes (33% efficient). Below 0.5:
      treat this as ~1.7 votes, not 5. Needs rho <= 0.250.
ok   tests/fixtures/good_panel.py:3
      k=3, rho=0.1 -> n_eff=2.50 of 3 votes (83% efficient). Clears 0.5.
warn tests/fixtures/unsized_panel.py:7
      k=5, correlation never stated. ... k=5 needs rho <= 0.250 to clear 0.5.

3 panel(s): 1 refused, 1 unevaluated, 0 ok
$ echo $?
1
```

Three verdicts. **The third is the point:** a panel whose correlation was never
stated is **not** a pass. `Panel.trusted` returns `None`, and the type is built
so it cannot collapse into a `True`. `--strict` makes unevaluated panels fail
the exit code *without relabelling them refused* — calling an unmeasured panel
"refused" would be a lie dressed as strictness, and it is the kind of lie that
ends up quoted.

### What it found in the real world, and how I know the instrument works

| corpus | files | findings |
|--------|------:|---------:|
| `SuperInstance/fleet-triage` | 3,547 | 0 |
| `SuperInstance/plainsong` | 151 | 0 |
| **a 7-judge panel planted in `plainsong`** | 1 | **2 (1 refused, 1 unevaluated)** |

**The third row is the one that makes the other two mean anything.** Zero
findings is also exactly what a dead instrument reports, and I was one line of
`return None` away from shipping a green "0 findings" as a clean bill of
health. The planted panel was found on first run — and it landed at
`k=7, ρ=0.4 → n_eff=2.06`. **The fleet's own "worth about two votes" constant,
reproduced from arithmetic alone.** That is either a coincidence or the reason
six independent measurements landed in the same place.

### The suite, and the two holes the mutation test found

43 tests. Eight deliberate breakages, each required to turn a test red:

| mutant | killed |
|--------|--------|
| threshold inverted | 7 |
| formula replaced with a plausible wrong one | 9 |
| scan window narrowed to one line | 3 |
| panel-word requirement deleted | 3 |
| unmeasured panel reported as a pass | 1 |
| comments stripped along with strings | 3 |
| correlation detection broken | 7 |
| exit code hardwired to zero | 3 |

**Two of the eight survived the first run, and both survivors were holes in my
tests rather than in the rule:**

- **The scan window was decoration.** Narrowing ±4 lines to the single line
  changed *no* result on any fixture — so no fixture exercised the window. The
  first test I wrote to close this passed for the wrong reason: it named the
  size `N_JUDGES`, and that name is *its own panel word*, so it passed whether
  or not the window existed. Renaming it to bare `k` made it bite.
- **The panel-word guard was untestable as written.** Deleting it changed
  nothing, because none of my decoys had a bare integer assignment for it to
  protect. `k = 8` in a numerical solver is the construct it exists to reject,
  and nothing tested it. That fixture now exists and is called
  `not_a_panel.py`.

Both are the same shape: *a test that cannot fail is worse than no test,
because it reports a coverage number.*

### Known limitations, stated not buried

- A comment explaining that something is **not** a panel contains the word
  "panel", and the rule believes it. Put it in a docstring.
- `k = 8` in a solver survives only because no panel word is nearby. Name the
  variable `n_judges` and the rule believes you. It reads code, not intent.
- **Panels assembled at runtime are invisible.** `len(candidates)` is not a
  literal. For a panel you actually *execute*, call
  `Panel(k=len(judges), rho=measured).explain()` and print it.
- JS/TS get a line scanner, not a tokenizer; it can misjudge a regex literal.
  Failure direction there is a *missed* finding, not an invented one.

**Hand-off → PLAYER:** point it at a repository that is nothing but machine
learning and see whether `ensemble` and `majority` survive the size
requirement — that is the false-positive rate, and it is the number I could
not measure honestly on a corpus I did not write. Then take a `ρ` that was
guessed rather than measured: the rule treats a confident wrong number
exactly as it treats a missing one, **which is wrong**, and that is the first
thing to attack.

---

# ARTIFACT 3 — WAITING ON THE SCOUT

No briefing received. Per the brief, that outranks anything I picked myself,
and both artifacts above were already named. If the scout's line is more load-
bearing than `--strict`, say so and I will drop to it.

# Notes for the next lane

- **`/tmp` is wiped.** The `--strict` patch the brief described as "patched in
  a local clone but not yet pushed" was **gone** — the clone was clean at
  `origin/master`. It has been rebuilt from the seam and is committed to a
  branch. This is the 35th time.
- **No `pip` in this sandbox.** `plainsong` needs `pytest` for its own config
  and has none. I ran its 812 tests with `python3 -m unittest` via a loader
  (`run_suite.py`, deliberately **not committed** — it is my instrument, not
  the repo's). `fleetlint` has no such problem by design.
- **Wall-clock on `/workspace` is I/O-bound.** 3,547 files is ~13s of CPU but
  ~100s of wall clock on the NAS. Do not read that as a slow linter.
