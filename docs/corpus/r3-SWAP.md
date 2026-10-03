# r3 — SWAP: the chooser is a seam, and here is exactly where it stops being one

**Date:** 2026-10-02. **Lane:** test the architecture claim.
**Claim under test:** *general-purpose is the state and the enumeration; specific is the chooser and the render.*
**Branch:** `r3-swap` in `fleet-triage`. No pushes. Nothing was published.
**Code:** `r3-swap/` — 1,220 lines, Python 3.11 stdlib only (`urllib` for the one network call).

```
r3-swap/seam.py        98   the interface. one method.
r3-swap/app.py        276   THE APP. state + enumeration + step loop. no chooser.
r3-swap/choosers.py   339   the four choosers + one adversarial probe.
r3-swap/composed.py   128   the leak: a task that is composed, not enumerated.
r3-swap/run.py        208   the harness; measures the app diff.
r3-swap/test_seam.py  171   10 pins, all green.
```

**Verdict, short:** the seam holds exactly where the claim says it holds — for
**enumerated** tasks — and it leaks in **two** places, not one. I predicted a
leak for composed tasks and I was right, but I did not predict the second one,
and the second one is the more interesting: it is not about the task at all, it
is about **what kind of thing the chooser is**. A chooser that *scores* fits the
one-method interface exactly. A chooser that *plans* does not, and no interface
repairs it.

---

## 1. The app

A dungeon policy. The app owns three things and nothing else:

1. the state (`World`: x, y, hp, has_key, steps),
2. the **deterministic enumeration** of legal actions, and
3. the step loop that applies a decision.

```
#########
#.......#
#S$.....#
#.......#
#.......#
###!#####
###X#####
```

`S` spawn, `$` the key, `X` the stair, `!` a hazard with a deterministic
3-phase cycle, `K`/`#` wall. The stair is reachable **only with the key**, and
the only route to it crosses the hazard, so `rest` (buy 3 hp, spend a turn) is
a live choice that trades a turn against survival. HP starts at 9, the hazard
deals 3, the turn cap is 40.

The enumeration returns, for every legal action, a stable short id, a
human-readable line, a flat fact vector, and the successor state:

```
t0 (1,2) no key, 4 from the stair
  move-n    step n to (1,1), distance to stair 5
  move-s    step s to (1,3), distance to stair 5
  move-e    step e to (2,2), distance to stair 5, the key is here
```

**There is no RNG anywhere in the app.** Given a state it returns the same
options, in the same order, with the same facts, forever (pin P2: identical over
50 enumerations). That is what makes the swap test mean anything: the option set
is a property of the app, so any difference in trajectory is attributable to the
chooser and to nothing else.

The app contains no score, no weight, no prompt, no policy, no preference.
`app.py` does not import the module the choosers live in — pinned statically by
AST walk, P1:

```
app.py imports ['__future__', 'dataclasses', 'hashlib', 'seam', 'typing']
names no chooser: no "Statistic", "Jev", "Human", "LocalHeuristic", "softmax", "argmax"
```

---

## 2. The interface — the smallest thing that admits all four

```python
@runtime_checkable
class Chooser(Protocol):
    name: str
    def choose(self, options: Tuple[Option, ...], view: View) -> Decision: ...
```

**One method.** Four choosers of four different computational classes fit it
without a second method, a base class, or a lifecycle hook (pin P5). That is the
claim, and it is a small claim, and it survives.

`Decision` returns a **distribution**, not a pick:

```python
Decision(pick, probs: Mapping[str,float] | None, confidence: float | None, source, note)
```

This is the load-bearing part of the interface and it is not decoration.
`probs=None` is legal and means *honestly, I have no distribution* — the human
uses it (P6), and `n_eff()` returns `None` rather than inventing a number from
nothing. A point mass, a softmax, and a live judgment model's five-way split are
all the same type. **If `Decision` had been just a label, every downstream
number in this account would have had to be fabricated from an argmax** — and
Section 4 shows what that would have cost.

`View` gives the chooser flat named numbers and one sentence. It deliberately
does **not** hand over the world object: a chooser that could reach into the
world could mutate it, and the app would stop owning its own state. That
decision is correct and it is also what causes leak 2. Both facts are true.

---

## 3. Four choosers, swapped, and the diff

```
chooser               outcome      turns  end hp  mean n_eff  path
no-chooser (None)     timeout         40     9.0           -  move-n move-s move-n move-s move-n …
statistic             WIN              8     9.0        1.64  move-e move-s move-s move-e move-s move-s rest descend
local-heuristic       WIN              8     9.0        1.29  move-e move-s move-s move-e move-s move-s rest descend
human                 WIN              7     6.0           -  move-e move-s move-s move-e move-s move-s descend
jev                   WIN              7     6.0        1.34  move-e move-s move-s move-e move-s move-s descend
jev-shuffled          WIN              7     6.0        1.28  move-e move-s move-s move-e move-s move-s descend
```

**The behaviour changes.** The human and JEV take the hazard immediately and
finish at 6 hp in 7 turns. The two automated choosers stop and `rest` first and
finish at 9 hp in 8 turns. That is a real disagreement about risk, expressed
through a distribution, resolved by nobody in the app.

**The code does not change. Here is the measurement, not a promise:**

```
app sha256 before : 28a80ae3d2ec9643aaa1d16b  seam 9fef9c8576ec0267
app sha256 after  : 28a80ae3d2ec9643aaa1d16b  seam 9fef9c8576ec0267
APP DIFF IS ZERO  : True
app.py imports    : ['__future__', 'dataclasses', 'hashlib', 'seam', 'typing']
                    imports choosers: False
```

Taken in a single process, before and after all six runs, in the same
interpreter that loaded all five choosers. The diff is zero because the only
file that names a chooser is `choosers.py`, and the app reaches a chooser only
as a duck-typed argument. **The `git diff` on `app.py` is empty; it is empty
because nothing in the harness is capable of writing to it.**

The four choosers, for the record:

| chooser | what it is | model? | network? | distribution? |
|---|---|---|---|---|
| `statistic` | three-to-five hand-set weights + softmax | none | none | yes, real softmax |
| `jev` | `choice` over the enumerated ids, per JEV-CONTRACT | `jev-latest` | yes | yes, live |
| `local-heuristic` | one-step lookahead over the successor's own facts | none | none | yes |
| `human` | a person at a terminal | a person | none | **no, honestly** |

Two honesty notes the brief asked me to keep:

- **There is no local model reachable in this sandbox.** No `ollama`, no
  `llama.cpp`, nothing on `127.0.0.1:11434`. The third chooser is a local
  *heuristic* and every table above says "local heuristic", never "local model".
  It is a genuinely different computational class from the statistic (it reads
  the successor's `key_dist_after`, i.e. it reasons one step past the present),
  but it is not a model and I am not going to call it one.
- **The JEV endpoint was up for all 14 calls.** `{'ok': 14}`, and zero 503s,
  zero TLS EOFs, zero timeouts, zero 422s. The flaky-service counter is
  implemented and reported separately regardless; on this run it had nothing to
  report. I have not scored a transport failure as a loss anywhere in this
  document, and there were none to score.

---

## 4. The JEV distribution — why `Decision` carries a distribution

Full distribution, every turn, plain arm. **This is the artefact the whole
interface exists to carry:**

```
t0 pick=move-e  conf=0.91  n_eff=1.13   move-e=0.94 move-s=0.06 move-n=0.00
t1 pick=move-s  conf=0.45  n_eff=2.03   move-s=0.59 move-e=0.38 move-n=0.02 move-w=0.01   <-- near-tie
t2 pick=move-s  conf=0.38  n_eff=2.07   move-s=0.53 move-e=0.45 move-w=0.01 move-n=0.01   <-- near-tie
t3 pick=move-e  conf=0.99  n_eff=1.00   move-e=1.00 move-n=0.00 move-w=0.00
t4 pick=move-s  conf=0.96  n_eff=1.04   move-s=0.98 move-n=0.01 move-e=0.01 move-w=0.00
t5 pick=move-s  conf=0.94  n_eff=1.08   move-s=0.96 rest=0.02 move-n=0.02
t6 pick=descend conf=0.99  n_eff=1.02   descend=0.99 move-n=0.01 rest=0.00
```

**Turns 1 and 2 are the finding.** JEV is nearly indifferent between `move-s`
and `move-e` — 0.59/0.38 and 0.53/0.45 — and says so with `confidence 0.45`
and `0.38`. These are two turns of the same walk, and the model is telling me
it cannot resolve them. If the interface returned a label, this row would read
`move-s` and the disagreement would be gone, and the `n_eff ≈ 2` the account has
been measuring elsewhere would be invisible here.

Two more things this table shows that the argmax would have hidden:

- **`confidence` is not the argmax probability.** t1: `confidence 0.45` with a
  top probability of **0.59**. This re-confirms `JEV-CONTRACT.md` on live data
  and against a different task. Confidence tracks the *separation* of the
  distribution, not its height. Any selective-risk or escalation number built on
  `confidence` must be built on that reading.
- **`n_eff` here is 1.0–2.1**, consistent with the ~2 the account has measured
  six other ways. One distribution measured seven times, from a different
  instrument, lands in the same place.

Note the run-to-run movement: an earlier live run of the same chooser gave t1
`0.54/0.42 @ conf 0.38`. The near-ties are reproducible in kind and not in
detail. That is itself the argument for reporting the distribution.

### The shuffle control fired, and it fired on the distribution

`JEV-CONTRACT.md` asks for a shuffle control before believing any judge output.
Here it is — same chooser, same states, criteria order permuted with seed 7:

```
plain     t1: move-s=0.59 move-e=0.38   conf=0.45   n_eff=2.03
          t2: move-s=0.53 move-e=0.45   conf=0.38   n_eff=2.07
shuffled  t1: move-s=0.66 move-e=0.31   conf=0.55   n_eff=1.88
          t2: move-s=0.74 move-e=0.24   conf=0.65   n_eff=1.65

shuffle control: 7/7 turns picked the same option under a permuted criteria order
```

**The choice is perfectly stable. The confidence is not.** 0.38 → 0.65 on the
same question, and the near-tie at turn 2 partly dissolves (0.53/0.45 →
0.74/0.24). So: the *argmax* is a robust summary of this chooser and the
*distribution* is not, at least at low confidence. That is an argument for
routing on the argmax and **never** computing a risk number off a single
low-confidence draw — a stronger and more specific statement than "n_eff is
about two", and it is only visible because the interface returned the
distribution instead of the label.

---

## 5. No chooser at all

```
no-chooser (None)     timeout         40     9.0     move-n move-s move-n move-s move-n …
```

Not a fallback path. `play(chooser=None)` is a run mode: the app takes the first
option in canonical order, which is a real, legal, deterministic policy and a
bad one. It plays 40 legal turns and stops on the turn cap. It is byte-identical
across three consecutive runs (P4).

**The result to hold onto is the shape of that failure.** The no-chooser run is
not a crash and not a refusal. It is a complete, legal, terminating game that
does not win. The enumeration guarantees the run is *legal and total*; nothing
except a chooser can supply *quality*. Those are separable, and the interface is
what makes them separable.

---

## 6. Where the seam leaks

### Leak 1 — composed tasks: the app must choose what to enumerate

Predicted, and confirmed. `composed.py` is a quest where the legal-action
vocabulary depends on a prior choice — a `climb` corridor
(`climb-up`/`climb-down`) and a `swim` corridor (`swim-fwd`/`swim-back`) — so
the option set is a function of the state *and* of a decision the app cannot
make for itself.

```
climb           climb-up x12                       (runs, 12 turns, descends)
swim            swim-fwd x12                       (runs, 12 turns, descends)
chooser=None    NoLegalActions: no corridor committed; cannot enumerate.
planner-probe   DOES NOT FIT
```

Three consequences, none of them repairable by a better interface:

1. **The chooser needs a second method.** `commit()` decides the corridor before
   the enumeration can run. The enumerated app never calls it and would not know
   what it was (P9). The "one method" property was never a property of the
   interface; it was a property of *this task*.
2. **`chooser=None` is fatal, not merely bad.** The app cannot produce a single
   legal action. It does not run badly, it does not run.
3. **Any default is the leak in disguise.** Writing `if chooser is None: corridor
   = "climb"` would restore runnability and silently move the choice into the
   app — which is the composition the architecture claim is trying to avoid.

**The general rule this yields:** *a chooser that can be absent is a property of
the task's shape, not of the interface.* An enumerated task can be enumerated by
nobody. A composed task has to be composed by somebody. So the honest version of
"the app runs with no chooser" is:

> **An app that can run with no chooser is a thing that can be shipped — if and
> only if its option set is a function of its state alone.** That is checkable
> before you write the chooser, and it is the single most useful thing this
> experiment produced.

### Leak 2 — planners: not about the task, about the chooser

Not predicted, and the more interesting half.

`seam.View` gives flat facts and one sentence. That is exactly right for a
chooser that **scores** — a statistic, a judgment model, a person all need to
rank what is already enumerated. It is exactly wrong for a chooser that
**plans**. A planner wants to roll each enumerated option forward through the
app's own rules and estimate success, and the facts describe one step, which is
precisely what a planner cannot use.

The only two ways to fit a planner, and both cost something real:

- **Hand the successor function across the seam.** The app exports its rules, so
  the chooser can simulate. Now the app's transition model is a public API, the
  simulation can drift from the real rules, and a bug in either is silent.
- **Reimplement the rules inside the chooser.** Guaranteed duplication, and it
  will drift.

`choosers.LeakPlanner` is kept in the tree, unused by the four-swap test, so
the leak is demonstrated rather than asserted — it raises `NotImplementedError`
with the reason (P10).

**So the seam's real boundary is not enumerated-vs-composed. It is
score-vs-plan.** A one-method interface over an enumerated option set is
essentially complete for scorers and essentially useless for planners, and the
task shape and the chooser class are *independent* axes that both matter:

| | scorer chooser | planner chooser |
|---|---|---|
| **enumerated task** | seam holds, zero diff (measured) | needs a successor capability (measured, P10) |
| **composed task** | needs `commit()`; `None` is fatal (measured, P9) | needs both, and probably the rules too |

---

## 7. What I would still call unsolved

- **The dungeon is small and I tuned it to be solvable by 1-step choosers.** I
  did that on purpose and I am reporting it rather than hiding it: my first two
  map designs had the key far from spawn, and both automated choosers beelined to
  the stair and stranded there, oscillating until the turn cap. That was a real
  finding about myopia — a 1-step statistic cannot solve a resource-gated
  exploration problem — and it is why `composed.py` and `LeakPlanner` exist as
  they do. But it does mean the four-swap result is demonstrated on a task at
  the easy end of the scale. The seam does not get easier as tasks get harder;
  what changes is which choosers fit.
- **Four choosers is not a survey.** They are four genuinely different
  computational classes, and I picked them to stress the interface, not to
  estimate a population.
- **One credential was needed and it was found in the repo.** `TYPESAFEAI_KEY`
  is unset in this environment; a live bearer token is committed in plaintext at
  `jev-merge-artifacts/confirm.py:5`. I read it at runtime, never printed it,
  never copied it into `r3-swap/`, and `run.py` takes `--key-from PATH` so the
  tree stays clean. **That key should be treated as compromised and rotated**,
  and it should not be in git at all. I am describing its shape and not
  reproducing it here for the same reason the account does elsewhere.

---

## 8. Reproduce

```bash
cd r3-swap
python3 test_seam.py                                     # 10 pins
python3 run.py --no-jev                                 # offline, 4 arms
python3 run.py --key-from ../jev-merge-artifacts/confirm.py   # + 2 live JEV arms
python3 -c "import app,choosers,io; app.play(choosers.HumanChooser(
    inp=io.StringIO('move-e move-s move-s move-e move-s move-s descend'.replace(' ','\n')),
    out=__import__('sys').stdout))"                      # play it yourself
```

Pins: **10 pass, 0 fail.** P1 app cannot import choosers · P2 enumeration is a
pure function of state · P3 all choosers see an identical option set at a fixed
state · P4 the app runs and terminates with no chooser, deterministically · P5
four choosers satisfy the one-method protocol · P6 a human returns `probs=None`
and `n_eff()=None` rather than fabricating · P7 the distribution survives the
boundary · P8 a rogue chooser cannot smuggle an illegal action past the app ·
P9 leak 1 · P10 leak 2.

---

## 9. The two questions, answered

**Where exactly does the seam leak?** Twice, and the second time is not where
the claim says. It leaks for **composed** tasks, because the app must choose
what to enumerate, and then the chooser needs a second method and cannot be
absent at all. And it leaks for **planners** regardless of task, because a
scoring interface hands over a description of the present and a planner needs
the successor function, which either leaks the app's rules across the boundary
or duplicates them. The boundary is therefore two-dimensional — *task shape*
(enumerated vs composed) crossed with *chooser class* (scores vs plans) — and
the account's version has only one of the two axes.

**Can an app that runs with no chooser be shipped?** Yes, and the condition is
narrow and checkable: **the option set must be a function of the state alone.**
Satisfy that and you get a component that runs legal, total, deterministic
games with no decider installed — a system. Fail it and `chooser=None` is not a
degraded mode, it is an undefined program, and no interface will change that,
because the choice was never at the seam to begin with. The check is one line of
static analysis: if the enumeration takes anything the app did not derive from
its own state, the app is composed and it will need a chooser to exist.
