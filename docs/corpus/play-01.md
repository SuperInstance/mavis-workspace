# play-01 — PLAYER LANE

**Adopted four tools with no fleet context and found where each stops being usable.**

**Rule I played by:** no README until the end. Clone, don't browse. Every number below
is a command I ran and what it did.

**Environment:** `/tmp/play01`, empty. `git node python3 curl jq gcc` present. Egress
works. Python 3.11.2, numpy 1.24.2. **No fluidsynth, no ffmpeg, no soundfont, no audio
device** — which turns out to matter for exactly one of the four findings.

**One process finding before the findings:** **there is no `ROLES.md`.** The brief says
read it first and it is the file that defines the kill criterion. I searched
`/workspace` to depth 4 and found nothing. `find / -maxdepth 4 -iname "*ROLES*"` — nothing.
I played the lane from the prompt alone. If a lane-defining file is missing, that is a
lane-defining problem, not a clerical one.

---

## The table

| tool | steps to first real result | undocumented steps | works on MY data? | Q3 (tells me when I'm wrong) | verdict |
|---|---|---|---|---|---|
| **quilt-adjudication** | **3** (`clone`, `demo.sh`, `quilt-init`) | 0 | **YES** — my own cell, my own key, my own attributions | **NO — worse than no** | **fail-open.** See F1. |
| **plainsong** | **2** to real audio | 0 | **YES** — 4 bars I wrote, first try | **YES — best in fleet** | **clean yes.** |
| **live resolver** | never | — | — | **NO — route absent** | **silent zero.** |
| **selectlib** | **3** | 0 | **YES** — my own selector | **NO — confident** | **the controls judge the wrong thing.** |

Zero undocumented steps on all three that exist. That is a genuinely good fleet and I
want that on the record: **the problem here is not onboarding. It is that three of these
tools are well-formed, checkable, and wrong.**

---

# F1. quilt-adjudication: the refusal is a fail-open, and the way you check it is what breaks it

This is the thing I shipped, and it is the one I broke the most.

## F1a. `| grep -q` defeats the entire guarantee

`.quilt/hooks/pre-merge-commit`, lines 25–36, verbatim:

```sh
.quilt/bin/quilt-adjudicate --index
rc=$?

if [ "$rc" -eq 1 ]; then
  ...print the refusal...
  exit 1
fi

exit 0
```

**The guard tests `rc -eq 1`, not `rc -ne 0`.** Every other status — 2 (usage), 126/127
(not executable), 128+n, and **141 (SIGPIPE)** — falls through to `exit 0`. `exit 0` from
a pre-merge-commit hook means *proceed*. The hook cannot tell "no conflict found" from
"the checker died", and it treats the second as the first.

`quilt-adjudicate` writes its refusal to **stderr**. When the reader downstream closes the
pipe, the shell running the refusal block takes SIGPIPE, dies 141, and never reaches its
own `exit 1`.

Deterministic fixture, my own cell `cells/slo/body`, my own key
`p99_latency_ms = 412` (alice) vs `= 388` (bob). Two runs, identical fixture:

```
UNTRUNCATED -> HEAD='2858a55 merge A'  contradictions_committed=1  records=1
TRUNCATED   -> HEAD='5e890a0 merge B'  contradictions_committed=2  records=1
```

`contradictions_committed=2` means the committed tree of HEAD contains both contradictory
values. **The merge commit landed.**

The command that does it is the most ordinary command in the world:

```sh
git merge --no-ff prB -m "merge B" 2>&1 | grep -q "REFUSING"
```

Also: `| head -1`, `| less`, `| tail -f`, any CI runner that truncates job output, any
editor task runner, any wrapper that does `$(git merge ...)` into a bounded buffer.

**Note the `records=1` on both lines.** The detector fired both times. The tool *detected
the contradiction, wrote the JSON record, and then the merge happened anyway.* The failure
is entirely in the last 30 milliseconds — between "we found it" and "we said so."

And here is the shape I find genuinely nasty: **the only way to observe the refusal is a
way that can destroy it.** You cannot check whether the guard fired without risking
silently not firing it. A CI check that greps for the refusal string is a check that can
turn the guard off.

**Fix, one character of semantics:**
```sh
.quilt/bin/quilt-adjudicate --index || exit 1
```

**The README delta is the sharpest part.** Line 247 documents the behaviour as
*"writes `.quilt/adjudications/<short>.json` and **exits 1**."* Line 96 says
*"**No merge commit is created. HEAD does not move, the branch never gains a** [parent]."*
Line 264 acknowledges a bypass — *"`git merge --no-verify` skips `pre-merge-commit`"* —
so the author already knew hooks have holes. The README documents the invariant the
fail-open breaks, documents the exact exit code that makes the break invisible, and names
one bypass while missing the one a user triggers by accident. **A stranger reading this
README has no way to learn this exists.**

## F1b. The demo that proves it works prints a crash from inside it

Line 29 of `demo.sh`'s own transcript, in PANE 2 — the pane that is supposed to be the
tool catching a bad merge:

```
  .quilt/bin/quilt-adjudicate: 207: cells/slo/body: Permission denied
  quilt: REFUSING the merge — the result asserts one key twice with two values.
```

`.quilt/bin/quilt-adjudicate:207` is a stray dangling word:

```sh
      printf '      "to_accept_the_winner": "git checkout %s -- %s && ..."' \
        "$TREE" "$wpath" "$key" "$wval"
      "$wpath"          # <-- line 207: executes the cell file as a command
    printf '\n    }'
```

`"$wpath"` is `cells/slo/body`, mode 644. The shell runs it, fails, prints to stderr,
moves on. Reproduced 3/3 in the demo and 1/1 on **my own repo** — not a fixture artifact.

Why it's the worst shape rather than a cosmetic nit: the enclosing block is
`{ ... } > "$OUT"`, so **stdout** goes to the JSON record and **stderr does not**. The
error *cannot* contaminate the record, and the record is valid, complete, and shows no
trace. `.quilt/adjudications/*.json` is a perfectly well-formed artifact.

`demo.sh:129` is what surfaces it to a human:
```sh
mout=$(git -C "$D2" merge --no-ff pr33 -m "merge #33" 2>&1)
```
`2>&1` folds the tool's internal stderr into the same variable as its user-facing
refusal. **A stranger reading PANE 2 concludes the tool hit a merge conflict.** It did
not. It crashed inside its own JSON writer while the thing it was refusing was perfectly
fine.

## F1c. The console and the record give opposite advice, and the source says the console is wrong

The refusal prints to the terminal:

```
  No judge ran. If the losing number is the right one:
    git checkout HEAD -- cells/slo/body && git merge --abort && git merge <branch>
```

The JSON record for the same refusal says:

```
"loser_status":     "already in your working tree; the refusal left the tree untouched, so keeping it is a no-op"
"to_accept_the_winner": "git checkout 6f3e20fb... -- cells/slo/body && git commit --no-verify -q -m \"adjudicated: p99_latency_ms=388\""
```

And `.quilt/bin/quilt-adjudicate:194-197` carries a comment dated **2026-10-02** saying
the console's version is wrong in **both halves**:

> `FIX 2026-10-02: the old field was "to_accept_the_loser": "git checkout HEAD -- <path>
> && git merge --abort" and BOTH halves were wrong. (1) 'git merge --abort' ALWAYS fails
> ... (2) 'git checkout HEAD -- <path>' restores the BASE text, which is the LOSER's value,
> and the refusal left the tree untouched -- so it restored the state the reader was
> already in. The record offered a handle to nowhere and named the wrong target.

**Someone found this, wrote it up correctly, and fixed the JSON. They did not fix the
console.** I ran the console's advice verbatim:

```
s1: git checkout HEAD -- cells/slo/body   rc=0
s2: git merge --abort                     rc=128  "fatal: There is no merge to abort (MERGE_HEAD missing)"
s3: git merge --no-ff prB                 -> REFUSING again
```

Step 2 is a hard error in the state step 1 creates, and step 3 re-triggers the refusal, so
the captain's step-1 work is discarded and they are exactly where they started. The JSON's
`to_accept_the_winner` is correct and is one command.

**A captain reads the terminal, not the JSON.** The artifact that was fixed is the one
nobody reads at the moment of decision.

## F1d. The tool is in a hidden directory

`ls` of a fresh clone: `README.md demo.sh docs pins tests graph` and one dotdir. The
entire tool is `.quilt/bin/` (6 files) and `.quilt/hooks/` (4 files). The one executable
at top level is a *demo* that deletes its work. Nothing at the top level says "this is a
git hook package; run `.quilt/bin/quilt-init`."

## Captain's chair — 3 of 4 questions answered from the artifact alone

1. **What happened?** — YES, and it is the best copy I have read in this fleet. *"PANE 1:
   git merged both PRs and exited 0 over a tree that asserts one fact twice with two
   different values. It never noticed."* That sentence is the tool.
2. **What was the alternative?** — YES. PANE 1 runs plain git on the identical fixture and
   shows the silent merge. Side by side, same two PRs. Genuinely rare and worth keeping.
3. **How do I take it?** — YES in the record, **NO on the terminal** (F1c). The record's
   one-liner is correct; the console's is the known-broken one. For a human at the moment
   of decision, the answer is no.
4. **What did the system not know?** — **PARTIAL, and this is where it stops being
   usable.** The record is scrupulous — `"judge": "none — no model is in this loop, by
   design"`, `"adjudication": "mechanical"`, *"That is an ordering, not a judgment about
   which is true."* So it is honest that it does not know. **But it names the two
   attributions it cannot resolve (`alice@corp.example`, `bob@corp.example`) and there is
   nothing in the entire artifact mapping an attribution to a person, a PR, or a
   measurement.** A captain holding this has a refusal, two email addresses, and no next
   move except "pick one." The fourth question is answered for the *machine* ("I have no
   judge") and left blank for the *human* ("so who do I ask?").

**The sentence a stranger needs:** *"Install `.quilt/bin/quilt-init` in a git repo, and
any merge that would leave two attributed `claim: <key> = <value> by <who>` lines with
different values for one key will be refused with a record naming both — but do not pipe
its output, and treat the record, not the terminal, as the thing to read."*

---

# F2. plainsong: a clean yes, and it refutes two of the three claims in my brief

**Two steps to real audio from a text file I wrote by hand.** No install, no deps, no
README. `python3 -m plainsong --help` then `python3 -m plainsong compile`.

I wrote four bars in C at 132bpm from `docs/notation.md` — my own melody, my own lyrics,
my own velocity row, my own `@bass` player — and compiled first try:

```
Cold Start  --  C, 132 bpm, 4/4
46 notes across chords (24), melody (14), bass (8)
length 7.27s
```

The arithmetic is right: 4 bars of 4/4 at 132bpm is 7.2727s. The MIDI is real — `MThd`
header, 4 track chunks, 1 tempo event, 60 note-ons, 106 note-offs. Not a stub, not an
empty-but-valid file.

**And I got sound.** The `play` command failed — but only on the *player*, and the
renderer had already written a WAV through the `builtin/numpy` backend, with zero external
dependencies, using the numpy already on the machine:

```
cold-start.wav  8.47s  44100Hz mono 16-bit
peak amplitude: 29162   rms: 4959.2
samples above 200: 84.2%
```

**This is a real signal, not silence.** Two steps, hand-written text, real audio.

**`doctor` is the best behaviour I have seen from any tool in this fleet.** It does not
pretend. It says `fluidsynth: no`, `audio_playback: no`, and then for each one tells me
the exact package to install. It reports its own limits as a first-class feature.

### Two of the three claims in my brief do not reproduce

| briefed claim | what actually happened |
|---|---|
| `--strict` does not exist | **TRUE.** `unrecognized arguments: --strict`, exit 2. |
| total garbage exits 0 with a valid, empty, playable MIDI | **FALSE.** exit 1, and the error is excellent: `error /tmp/.../garbage.song:1: nothing to play: no chord, melody or player rows` + `hint: add a row such as 'Chords: \| Am \| F \|'` |
| `-q` silences the only instrument | **MISLEADING.** `-q` does mute the compile summary (confirmed, prints nothing). But the instruments are **separate commands**: `check` (`ok 1 file(s) checked, 0 warning(s)`) and `stage` (*"declares no [Stage] block, so every voice is heard where it is written"*) and `info` and `doctor`. `-q` is a per-invocation flag, not the only way to see anything. |

**A briefed defect report that does not reproduce is worth as much as one that does.** Two
of the three things I was told were broken are not broken, and the one that is broken
(`--strict`) is a missing flag, not a silent wrong answer. **I would rather be sent to
check claims than be handed them.**

### The one real friction

`compile` wrote to `/tmp/play01/plainsong/.plainsong/workspace/output/cold-start.mid` —
**into the package directory I happened to be standing in, not next to my input file.** I
ran the command from the plainsong checkout and my output landed in the checkout. There is
a `-o/--midi PATH` flag and I did not need it, but nothing told me the default was
relative to CWD rather than to the `.song` file. Minor, and it is untracked so it does not
dirty the repo — but if I had been standing in a directory I cared about, I would have
scattered `.plainsong/workspace/` through it. It is a one-line fix in the help text:
*"output defaults to ./.plainsong/workspace/output/ relative to the current directory."*

**The sentence:** *"Write a `.song` file — header, sections, `|`-separated bars, any rows you
like — and `python3 -m plainsong compile my.song` gives you a real MIDI, and `play` gives
you a real WAV through a numpy backend, on a machine with nothing installed."*

---

# F3. The live resolver: the route does not exist, and the failure is indistinguishable from "no results"

```
$ getent hosts fleet-resolver.prong-potassium.workers.dev
NXDOMAIN / no A record
$ getent hosts workers.dev
104.18.12.15    workers.dev          <-- the wildcard zone is UP
$ curl -X POST https://fleet-resolver.prong-potassium.workers.dev -d '{...}'
curl: (6) Could not resolve host
HTTP=000  t=0.001s
```

**I hit it without being told, in the sense that matters: I could not confirm the briefed
bug, because there is nothing to test.** A dead host, a silent zero, and a correct
"no matches" are all `HTTP=000` with an empty body from out here. Egress is open, TLS works,
the wildcard resolves. The specific route is absent.

This independently reproduces PLAYTEST-OUTSIDER's 2026-10-01 finding, from a different
session, a day later, on a different machine. **Two independent confirmations of a dead
public endpoint is not a bug report, it is a decommission that nobody announced.**

**Answering the briefed question — does it tell me when my `path:line` is wrong?** I cannot
say, and that is the finding. If a lane is fixing the no-backticks silent zero, **there is
nothing to fix until the route is up.** An agent told "use the resolver" has no liveness
signal it can read, and the honest move is to silently produce nothing. For a public tool
whose entire job is to be a check on other people's citations, **failing indistinguishably
from success is the one failure mode it must not have.**

**The sentence:** *"This endpoint does not resolve. It cannot be evaluated, and it must not
be advertised until it answers `GET /` with something, because a caller cannot tell dead
from clean."*

---

# F4. selectlib: 10/10 onboarding, and the controls do not measure the thing they are printed next to

**Three steps. Zero setup. Zero deps. 10/10 as a first-30-minutes experience, and I want
that stated plainly because the finding below is not about onboarding.** I imported it,
read no README, read the API out of the source, and ran **my own** selector against
**my own** field. First try.

## F4a. A selector that actively works against the goal scores 5/5 controls

`harness.run()` runs every control before it computes a number and raises `ControlFailure`
if one does not fire. That is a real mechanism and it really works — the brief called
"beats free local noise" *a sentence in a docstring, not an implementation*, and that
understates it. Here is what is actually there.

The catch is in `harness.py:52-57`:

```python
ctrls = controls if controls is not None else control_suite()
passed = 0
for c in ctrls:
    c.check()
    passed += 1
```

**`ctrls` is built from the library's own hardcoded fixtures. The `selectors` argument is
never passed to any control.** The five controls are `oracle_fires`, `noise_fires`,
`oracle_is_ceiling`, `free_statistic_is_blind_where_it_must_be`,
`split_differs_from_clean` — and every one of them imports `oracle()` and `local_noise()`
from the library and tests *those*. The control names say so out loud: they guard *"the
ceiling is real"* and *"the bar can be cleared"* — **the ceiling and the bar, not your
selector.**

So I built two selectors that should never survive a serious harness:

```python
anti   = Selector("ANTI-oracle", lambda f: sorted(f.cells(),
                 key=lambda c: -f.render[c[0]][c[1]]))   # spends budget making it WORSE
ignore = Selector("IGNORES field", lambda f: f.cells()) # order carries zero information
```

```
controls in the suite: 5
VERDICT LINE: 5/5 controls fired

  oracle                                     calls=0   mae=0.01577
  local_noise                                calls=0   mae=0.01623
  ANTI-oracle (spends budget making it worse) calls=0   mae=0.01717
  IGNORES the field entirely                 calls=0   mae=0.01724
```

**5/5 controls fired for a selector whose stated purpose is to make the field worse.**

## F4b. And the number cannot tell them apart either

One seed is the default (`seeds=(0,)`) and it is the most flattering possible
presentation: 0.01577 vs 0.01717 reads like a ranking. Over 30 seeds:

```
selector       mean      min       max       vs oracle
oracle         0.01404   0.01176   0.01613   --
local_noise    0.01440   0.01188   0.01658   OVERLAPS
ANTI-oracle    0.01522   0.01229   0.01717   OVERLAPS
IGNORES field  0.01545   0.01261   0.01809   OVERLAPS
```

**Every distribution overlaps the oracle's.** A selector that works against the goal and a
selector that ignores the field entirely are, on the number this library produces,
**statistically indistinguishable from the ceiling.** All four get 5/5.

So the failure is not one gap, it is two independent ones pointing the same way: **the
controls do not measure your selector, and the statistic cannot separate a good one from a
hostile one.** Either alone would be survivable. Together, "5/5 controls fired" printed
directly above a table row is a **confident, well-formatted, wrong** result — which is the
exact subject of this entire project.

**The fix is small and honest:** thread `selectors` into the controls so `oracle_fires` and
`oracle_is_ceiling` run against *the caller's* selectors, and have `Result.table()` print
seed spread (min–max or a stddev column) instead of a single-seed point estimate. The
control suite's *philosophy* is right and is the best-written thinking in the four tools I
played — the wiring just doesn't connect it to the thing being judged.

**Bar 1 — "could the work not easily be done without it?"** The harness *skeleton* clears
it: the refuse-until-controls-fire shape, the `Control` dataclass, the docstring *"A
control that cannot fail is worse than no control"*, the two post-mortems in the README
about controls that caught real bugs. **The validation it advertises does not clear it**,
because right now the thing it prints is not a statement about your selector. A well-built
jig, then — but the load-bearing part is the one that isn't connected.

**The sentence:** *"selectlib gets you running in three steps and its control philosophy is
the sharpest thinking in the fleet, but `harness.run()`'s controls are hardcoded to the
library's own oracle and never touch the selectors you pass, and a deliberately hostile
selector scores 5/5 — so read the number as a smoke test, not a measurement, until the
controls take your selectors as an argument."*

---

# The three questions, answered

**1. Steps to first working invocation, and how many undocumented?**
quilt-adjudication 3/0. plainsong 2/0. selectlib 3/0. Resolver never.
**Zero undocumented steps across the fleet. That is the good news and it is real.** The
problems are not onboarding.

**2. Does it work on MY data, or only the author's example?**
**All three that exist: yes, on my own data, first try.** My own cell and key and
attributions. My own four bars of music. My own adversarial selector. Not one of them
needed an edit to the library or an accommodation to my input. **This fleet is unusually
good at accepting strangers' data and unusually bad at telling the truth about the
result.**

**3. When I do something wrong, does it tell me?**
Split, and the split is the finding.
- **plainsong: yes, and it is the fleet's best error reporting.** Names the file, the line,
  what is missing, and a concrete hint. `doctor` volunteers its own limits.
- **selectlib: confident.** 5/5 controls fired next to a hostile selector's row.
- **quilt-adjudication: the worst kind — confident *and* broken.** It printed a complete,
  correct-looking, well-formatted refusal containing a shell error from inside itself and
  an instruction its own source comments call wrong, and under `| grep -q` it printed
  nothing and merged the contradiction.
- **the resolver: silent.** Not available, not diagnosable.

# The README delta

Read last, as instructed. In all three cases the README **described the intended behaviour
correctly and completely.** The problem is not that the docs lie to me.

- **quilt-adjudication:** documents "exits 1" and "no merge commit is created, HEAD does
  not move" — precisely the invariant the fail-open breaks. Names the `--no-verify` bypass
  and misses the one you trigger by piping. Documents the broken console advice at line 91,
  two hundred lines from the comment saying it is wrong. **The README is accurate and I
  would still have shipped a broken tool having read it.**
- **plainsong:** accurate throughout. The one thing it does not say is that `-o` exists and
  that output defaults to CWD.
- **selectlib:** accurate, and structurally misleading. Line 18 — *"`harness.run()` executes
  every control before it computes a single number"* — is **true**, and it is the exact
  sentence that makes a reader believe the number is validated. The control table lists
  what each guards and the honest answer is visible in the names: the ceiling, the bar. Not
  your selector. **Accurate sentences in a misleading arrangement.**

---

# Hand-off to the scout lane

**The most annoying thing I hit, phrased so it generalises:**

> **A guard written as `if rc -eq 1 then refuse; else allow` treats every abnormal exit of
> its own checker as "no problem found." The checker's own output being truncated by
> anything downstream — `head`, `less`, `grep -q`, a CI log cap, a task runner — kills it
> with SIGPIPE, it exits 141 instead of 1, and the guard **allows the thing it exists to
> block.** And the failure is invisible: the tool still detects the problem and still
> writes its receipt. Only the last 30ms, between "we found it" and "we said so," are
> lost.**

**Why that phrasing and not a bug number:** because `rc -eq 1` instead of `rc -ne 0` is not
a typo, it is a **shape**, and it will be in twenty other places. The tell is always the
same: *a check that treats "I don't know" as "everything is fine."* Concretely, the scout
should look for:

1. **Comparisons against a specific nonzero code** where the sensible test is "any nonzero."
   `rc -eq 1`, `status == 2`, `if [ "$x" -eq 3 ]`. One grep across the fleet.
2. **Demos and reports that capture `2>&1` into a variable and re-echo it as prose.** That
   is what laundered quilt-adjudication's internal crash into its own success narrative at
   `demo.sh:129`. It is a fleet-wide habit and it hides internal errors in *every* tool
   that has one.
3. **Guards that are checked but whose subject is not threaded in.** selectlib's
   `control_suite()` never receives the `selectors` argument, so "5/5 controls fired" is a
   self-test printed above someone else's result. Same shape as the `rc` bug: *the check
   runs, passes, and is about something else.*
4. **Single-seed point estimates presented as rankings.** `harness.run()` defaults to
   `seeds=(0,)` and prints one number per selector. Thirty seeds and the ranking is gone.

All four are the same defect wearing four costumes: **a check that runs, passes, and is
measuring the wrong thing.** Which is this project's entire subject, found three times
over in one hour, in a fleet I otherwise like.

**And the thing I want on the record, because the lane is judged on friction:** **plainsong
is a clean yes and selectlib is a clean 10/10 for onboarding.** Two steps to real audio
from a hand-written text file, with a `doctor` that volunteers its own limits. The negative
results here are not "this fleet is unusable" — they are **"these three tools are
confident, well-formatted, and wrong, in ways their own READMEs do not disclose."** That is
a much more specific and much more fixable problem than bad onboarding, and it is worth
saying so the triage does not read this file as a general verdict on the work.
