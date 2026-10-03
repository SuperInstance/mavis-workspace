# play-fix-01 — BUILDER LANE

**Three defects reproduced, three fixed, each on a branch, none pushed.**

The brief said stub this file inside ten minutes with the first defect reproduced. That
part went to plan; the other two took longer because reproducing them turned up things
nobody had found yet. The stub is still in the git history of this file's early state if
you want to see the order things were learned in.

**Rule I played by:** reproduce before you fix, and *mutate the fix back* before believing
the test. Every claim below has a command you can run. Three of the tests I wrote
initially passed against the broken code; all three are named below, because a triage
report that hides its own false passes is the thing it is complaining about.

| repo | branch | commit | tests |
|---|---|---|---|
| `selectlib` | `fix/harness-validates-the-run` | `4f405e2` | 17 pass (was 10) |
| `plainsong` | `fix/strict-fails-closed` | `1a91617e` | 821 pass, 0 fail |
| `quilt-adjudication` | `fix/hook-fails-closed` | `2db2b7b` | 11/11 + 14/14 pins |

Working copies: `/tmp/work/selectlib`, `/tmp/work2/plainsong`, `/tmp/work3`.
Evidence scripts: `/tmp/repro`, outputs in `/tmp/evi`.

---

# D1. `selectlib` — three defects, one file, one shape

The player filed two (`harness.py`'s controls never see your selectors; `seeds=(0,)` makes
a ranking out of one draw). Both reproduce. **Reproducing them turned up a third in the
same file that nobody had found, and it is the worst of the three**, because it is not a
wrong number — it is a *missing* number, rendered so that it looks present.

## D1a. `Result.table()` prints one row out of sixteen, and it is the last one

### Reproduce

```
$ python3 /tmp/repro/r1_single_seed.py
=== A. THE DEFAULT: seeds=(0,).  This is what a reader gets. ===
controls: 5/5 controls fired
     budget     seed selector    calls      mae
         32        0IGNORES field        0   0.0295
```

Sixteen rows went in — 4 selectors × 4 budgets. **One row came out, and it is
`IGNORES field` at the largest budget: the worst selector on the hardest setting, alone
under a header that implies a table.** The blank lines are the other fifteen rows,
rendered as nothing.

### Cause — `selectlib/harness.py:24-34`

```python
for r in self.rows:
    cells = []
for c in cols:              # <-- dedented out of the loop, runs ONCE on the leaked `r`
    v = r[c]
```

`r` is the last row. Every earlier row appends an empty list and is discarded. The
function returns a non-empty list, raises nothing, and the existing test suite is green
because **no test calls `table()`**.

This is the project subject wearing a costume the other two were not: the other two are
checks that measure the wrong thing; this one is a report that *silently discards the
measurement*.

## D1b. The default `seeds=(0,)` makes a ranking out of one draw

### Reproduce — the seed where the ranking flips

```
$ python3 /tmp/repro/r1b_flips.py
seed 0 ranking (the DEFAULT the library ships):
    oracle           0.00000
    local_noise      0.00134
    ANTI-oracle      0.01151
    IGNORES field    0.03158

distinct orderings across 30 seeds: 2
  29/30 seeds  oracle > local_noise > ANTI-oracle > IGNORES   seeds=[0,1,2,3,5,6,...]
   1/30 seeds  oracle > ANTI-oracle > local_noise > IGNORES   seeds=[4]

seeds whose ranking DIFFERS from the default: 1/30  [4]
```

**Seed 4.** A selector whose stated purpose is to *spend budget making the field worse*
beats the library's own "bar to beat" — and the shipped default would have said the
opposite, confidently, because the shipped default shows one row (D1a) and that row came
from seed 0.

I did **not** go looking for a seed count that makes the original ordering come out right.
The fix makes the number look *worse*: `vs bar` for the oracle is 88/120, not a clean sweep,
and every row now says `overlaps` because every distribution overlaps the oracle's. That
is the honest reading of 30 draws.

## D1c. The number cannot separate a good selector from a hostile one

```
$ python3 /tmp/repro/r1c_full.py
  selector             mean      min      max   overlap w/ oracle range?
  oracle            0.00603  0.00000  0.02871   OVERLAPS
  local_noise       0.00816  0.00000  0.03748   OVERLAPS
  ANTI-oracle       0.01998  0.00451  0.04051   OVERLAPS
  IGNORES field     0.03596  0.02378  0.05525   OVERLAPS
```

The player's claim holds. **A range can honestly say "these are not separable"; a point
estimate cannot say anything.**

## D1d. The controls never receive your selectors

```
  harness.run() signature: (selectors, field_factory, budgets, seeds=(0,), ask=None, controls=None)
  does 'selectors' reach the controls? -> False
  control_suite() arity: () -> 'list'
```

`control_suite()` takes no arguments. All five controls construct `oracle()` /
`local_noise()` internally. The player's hostile selector gets `5/5 controls fired`
printed above its own row.

## The fix

```
$ python3 /tmp/repro/r1_after.py
=== A. THE HOSTILE SELECTORS ARE NOW REFUSED (was: 5/5 controls fired) ===
  ControlFailure: entrant_beats_the_free_statistic
  -> no number is produced. The control now fires about YOUR selectors.

=== B. A REAL SELECTOR, DEFAULT SEEDS.  Spread, not one number. ===
controls: 7/7 controls fired | ranked: True | seeds: 30
  seeds=30
     selector      calls          n       mean        min        max     vs bar  separable
       oracle          0        120    0.00603    0.00000    0.02871     88/120   overlaps
    judge-ish          0        120    0.00607    0.00000    0.02871     86/120   overlaps
  local_noise          0        120    0.00816    0.00000    0.03748          -   overlaps

=== C. A DELIBERATE single-seed run is still allowed, and SAYS SO ===
  seeds=1  [SINGLE SEED -- NOT A RANKING]
     selector      calls          n       mean        min        max     vs bar  separable
       oracle          0          1    0.00670    0.00670    0.00670        1/2separated *
  * one seed is one draw. Re-run with more seeds before reading these as an ordering.
```

- `table()`'s loop restored; it now prints `mean/min/max/vs bar/separable` per selector
  and every row, and a one-seed run is stamped `[SINGLE SEED -- NOT A RANKING]`.
- `seeds=None` → `DEFAULT_SEEDS = 30`. A deliberate one-seed run is still allowed.
- `control_suite(entrants)` gained **`entrant_fires`** and
  **`entrant_beats_the_free_statistic`** — the docstring's "a selector that does not beat
  `local_noise` is not a finding" is now a gate, not a sentence. 5/5 → 7/7.
- `local_noise` is always measured, so "does not beat the bar" has something to compare to.

### Three of my own tests lied, and I am naming them

| what I wrote | why it passed against broken code | fix |
|---|---|---|
| `test_the_table_prints_every_row_and_not_just_the_last` built the run through `run()`, so the new control refused it and the test never reached the renderer | the test was measuring the controls, not the table | build the `Result` by hand — the renderer is the subject |
| `test_the_default_cannot_be_read_as_a_ranking` read `inspect.signature(run).default` | a mutation putting `seeds = (0,)` back *inside the body* left the signature at `None` | assert `r.n_seeds == DEFAULT_SEEDS` — behaviour, not declaration |
| my first mutation (`seeds = (0,)` inserted above `seeds = tuple(range(...))`) was **equivalent** — the next line overwrote it | equivalent mutant; low kill count ≠ no coverage | mutate the line that actually decides |

The second one is the sharpest: **a test that reads the declaration instead of running the
thing is the defect this whole branch is about, reproduced inside the fix for it.**

Every remaining fix was mutation-checked: reverting the table loop fails 1 test; reverting
the seed default fails 1; making the suite stop looking at the entrant fails 3.

---

# D2. `plainsong` — `--strict`, and the brief's premise is wrong

**The brief said: "the garbage case still exits 0, because the compile path fails earlier
than my gate." That is not true and I did not work around it.** Garbage fails closed on
master, with a good error and no artifact:

```
$ python3 -m plainsong compile -o out/x.mid garbage.song
error  garbage.song:1: error: no sections found
    hint: start a section with a header such as [Verse]
error  compilation failed
EXIT=1
```

The player's F2 said the same and said it better. **The real defect is one severity down.**

## The defect: a warned-about source still writes an artifact

### Reproduce

```
$ python3 -m plainsong compile -o out/x.mid warned.song
(untitled)  --  A, 120 bpm, 4/4
101 notes across chords (12), melody (89)
midi  out/x.mid
warn  warned.song:18: warning: [Bridge - 2 bars] chords covers 2 bar(s), the section runs 4
    hint: short rows stop early rather than stretching to fill the section
EXIT=0
--- out/ ---
-rw-r--r-- 1 root root 1055 out/x.mid

$ python3 -m plainsong -q compile -o out2/x.mid warned.song
EXIT=0
$ # ... and ZERO bytes of output
-rw-r--r-- 1 root root 1055 out2/x.mid
```

Two bars of that song are silence, the tool says so, and it writes the file anyway. **Under
`-q` it writes the file and says nothing at all.** In a build script there is no way to
tell that from a good compile. And `compile --strict` did not exist: `exit 2`,
`unrecognized arguments`.

## The fix

```
$ python3 -m plainsong compile --strict -o out/s1.mid warned.song
error  --strict: 1 warning(s) in this arrangement; refusing to write out/s1.mid.
       Nothing was written. First: warned.song:18: warning: [Bridge - 2 bars] ...
warn  nothing was written. Drop --strict to compile anyway.
EXIT=1
$ ls out/            # empty

$ python3 -m plainsong -q compile --strict -o out/s2.mid warned.song
error  --strict: 1 warning(s) in this arrangement; refusing to write out/s2.mid. ...
EXIT=1
$ ls out/            # empty
```

**The one architectural decision that matters: the gate is in `compile_text()`, between
`arrange()` and `write_midi()`.** The brief's diagnosis — "the compile path fails earlier
than my gate" — is right about the symptom and wrong about the cause. The compile path
doesn't fail earlier, it **writes** earlier. A gate placed after `compile_file()` returns
is a gate that runs, passes, and measures the wrong thing: the artifact it is refusing is
already on disk, and the honest options are to delete it afterwards or to lie about it.
`arrange()` returning is the only moment where the warning exists and the bytes do not.

Two consequences that fall out of putting it there:
- the library API (`compile_text(..., strict=True)`) fails closed too, not just the CLI;
- `CompileResult.ok` now also considers `strict_refusal`. It used to mean only "no errors",
  which is the same class of bug as selectlib's controls.

Also: the refusal prints even under `-q` (`-q` means "no progress", not "no news"), and
`doctor` lists it under **failing closed** — a limit you can turn on but cannot discover is
a limit nobody hears about.

### Tests — `tests/test_strict.py`, 9 tests

Each verified by re-introducing the defect: gate falling through to the write → **3 fail**;
`ok` ignoring the refusal → **3 fail**; refusal suppressed under `-q` → **1 fail**.
Full suite **821 tests, 0 failures**.

`test_garbage_fails_closed_with_and_without_strict` exists specifically to record that the
brief's premise was wrong, so the two paths cannot drift apart silently.

---

# D3. `quilt-adjudication` — the live one, and the shape is in five places

**Two of the player's three quilt findings are already fixed upstream.** That is a real
result and it belongs on the record:

| finding | status on `SuperInstance/quilt-adjudication` @ `f92d2a5` |
|---|---|
| F1a the `rc -eq 1` fail-open | **LIVE.** still in `.quilt/hooks/pre-merge-commit:27` |
| F1b the stray `"$wpath"` printing `Permission denied` | already fixed, `f92d2a5` "fix: an orphaned argument line…" |
| F1c console giving the advice its own source calls wrong | already fixed, `a6c3508` |

The player found three defects; two were fixed by someone else in the interim and the
third — the headline one, the one they spent the most time on — was not. **The most
elaborate finding is the one that survived**, which is worth saying out loud to anyone
triage-by-effort.

## D3a. Reproduce

```
$ git merge --no-ff prB -m "merge B" 2>&1 | grep -q "REFUSING"
  pipeline rc=0  (1 = grep found nothing)
  HEAD parents: 3  -> *** MERGE COMMIT LANDED ***
  contradictions_committed: 2 claim lines
    claim: p99_latency_ms = 412 by alice
    claim: p99_latency_ms = 388 by bob
  records written: 1
```

Exactly the player's numbers. **Both contradictory values are in the committed tree, and
the tool still wrote the record.** Only the last 30 ms were lost.

## D3b. The shape is in five places, and two of them are in the installer

`grep -rn "rc.*-eq 1"` over `.quilt/` finds the verdict test in `pre-merge-commit`,
twice in `post-merge`, and **twice more inside `quilt-init`, which writes the buggy hook
into every new repository.** Fixing only the checked-in file would have left every
subsequent `quilt-init` reinstalling the bug — and pin P10 ("the hooks quilt-init writes
are byte-identical to the checked-in copies") would have caught it, which is a good sign
about this repo.

There is a **sixth** instance one level up, which the player did not name:

```sh
[ -x .quilt/bin/quilt-adjudicate ] || exit 0
```

"The check could not run" read as "the check passed." My first fix passed P14a-while-
refusing-to-run and I only found it because the pin I wrote for the *other* case kept
passing for the wrong reason. It is the same sentence one level up.

## D3c. The fix

The checker now runs with its output going to a **file**; the **decision is taken from the
exit code**; the text is replayed afterwards with failures ignored (`|| :`). A closed pipe
downstream can no longer reach the verdict. `rc -ne 0`, not `rc -eq 1`, and a missing or
non-executable checker refuses with an explanation instead of allowing.

```
$ git merge --no-ff prB -m "merge B" 2>&1 | grep -q "REFUSING"
   pipeline rc=1   refused (correct)
$ git merge --no-ff prB -m "merge B" 2>&1 | head -1 >/dev/null
   refused (correct)
$ mout=$(git merge --no-ff prB -m "merge B" 2>&1)      # what demo.sh does
   refused (correct)
$ git merge --no-ff prC -m "merge C"                   # no contradiction
   clean, merges
```

`tests/pins_hook_fails_closed.sh`, P13–P18, 14 checks, same style as the existing pin
harness. Reverting `quilt-init`'s template to the original hook text **fails 6 of the 14**.
Existing suite still 11/11.

### The pin file caught my own harness lying

`P14b` **passed against the broken hook.** Not because the pin was weak but because
`unset_repo` reset to *whatever HEAD had drifted to* — so a merge that an earlier pin was
supposed to prevent stayed in history, and the next pin measured a repository that
already contained the contradiction. It now resets to a recorded base commit. (The base
marker lives in `$SCRATCH`, not the repo, because `git clean -qfd` deletes untracked files
— found the hard way.)

This is the same lesson as the selectlib signature test, and I would rather it be in the
report than quietly fixed.

### Also: the README was still teaching the broken advice

The console and the record were fixed together in `a6c3508`. **The README transcript was
not**, so the tool said the right thing and the documentation said the wrong one:

```
  No judge ran. If the losing number is the right one:
    git checkout HEAD -- cells/inbox/body && git merge --abort && git merge <branch>
```

Both halves are broken — `git merge --abort` always fails at `pre-merge-commit` time (no
`MERGE_HEAD` to abort), and `git checkout HEAD -- <path>` restores the *base*, which is
the loser's value the tree is already on. Corrected, with the reason kept in the file.

---

# Which of the player's four findings is not actually a defect

They asked for this and the brief demands it, so it gets argued rather than asserted.

**The answer is F3, the live resolver — but not for the reason that makes it tempting.**

`fleet-resolver.prong-potassium.workers.dev` does not resolve. That is real, it is now two
independent confirmations a day apart from different machines, and "a decommission nobody
announced" is a fair characterisation. **It is not a defect in the code, though.** There
is no code to audit: no route, no handler, nothing that ran and returned a wrong answer.
It is an *operational* gap, and the honest triage is "this is not triagable today" — the
scout lane cannot find a bug in a host that does not exist, and a lane told to fix the
no-backticks silent zero has nothing to fix until the route answers `GET /` with something.

Its *real* finding is a design requirement, not a bug: **a public checker must not fail
indistinguishably from success.** `HTTP=000` with an empty body is exactly that, and the
player's own framing — "failing indistinguishably from success is the one failure mode it
must not have" — is the correct sentence. But you cannot regression-test a requirement
against an endpoint that does not answer, so it belongs in a service-level agreement, not
in a defect list where it will be re-triageable every time and never fixed.

**The other three are defects, and they are worse than the player says, not better.**
They are not onboarding problems — the player is emphatic and correct that onboarding was
10/10 — they are cases where the instrument ran, passed, and measured the wrong thing.
D1a is the sharpest of everything in this report and the player never saw it: `table()`
prints **one row out of sixteen** and nobody noticed for the life of the library, because
the missing number is not a wrong number.

**One finding I have to push back on is the player's own summary, not one of the four.**
They write *"All four are the same defect wearing four costumes."* Three of them are, and
the fourth (F3) is not a defect at all. Four findings, three instances, one of them not
code. The pattern is real and it is the right pattern — it is just being asked to carry
one more thing than it can.

---

# Handing back

- **Three branches, local, unpushed.** No push was attempted to anything.
- `selectlib` needs a real `pip`-less test story noticed: it already has `run_tests.py`,
  which is why its suite could be run here at all. `plainsong` declares `pytest` in its
  `dev` extra and there is no `pip` in this sandbox, so I ran its 821 tests through a
  `unittest` loader. **That is a real onboarding defect of the kind the player said does
  not exist**: a repo whose declared test command cannot run in its own environment.
  Worth a look, and I did not fix it because it is outside the three briefs.
- **`tests/pins_undo_handle.sh` P12 fails 8/9** on the unmodified base commit `f92d2a5` as
  well as on my branch. **Pre-existing, not caused by this work, and left alone.**
- The three repos are at `/tmp/work/selectlib`, `/tmp/work2/plainsong`, `/tmp/work3`.
  If `/tmp` is wiped before the branches are harvested, they are gone — the two
  reproduction directories are small enough to re-derive, the fix commits are not.
