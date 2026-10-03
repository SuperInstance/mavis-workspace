# SCOUT — `SuperInstance/quilt-in-git` vs. the adjudication entry

**Lane:** read the competitor, decide merge-or-compete for October 14.
**Verdict up front:** it **composes**. Neither of us should compete. Details in §7, and I name the
weaker entry in §6 without hedging.

**Method.** Cloned at depth 50 (`6a1ae48`, 3 commits), read **all 11 files, 12,034 bytes** — every
script, both pins logs, the whole test harness. Then I **executed** it: ran its pins on a second git
(2.39.5 vs. the 2.43.0 it recorded), **mutated its core equation**, and **built the merge case it
never tests**. Everything below marked MEASURED was produced by running its code, not by reading it.
No pushes. Nothing was sent to GitHub.

---

## 1. The README, quoted

> **"The entire simplified Quilt lives inside a plain Git repository: dials are
> files, ticks are commits, rewind is checkout, and Git hooks are the runtime.**
> Every cell is a directory under `cells/`; its state is 16 dial files (one
> float each) plus a body. Changing a dial and committing it is a *tick*; a
> `post-commit` hook turns that tick into a receipt, an entanglement cascade,
> and a watch-log line. Because everything is ordinary Git content, the repo is
> simultaneously the Sheet, the journal, and the collaboration bus — clone,
> push, bundle, branch, and time travel all come free."

Three things in the README deserve credit before I criticise it, because they are rare:

- Its **"Honest limits"** section lists five defects *against its own thesis* — including that
  `core.hooksPath` is local so **hooks are inert in a fresh clone**, and that the cascade commit
  "sweeps any dirty `cells/` files." Most repos in this fleet hide that section.
- `pins/failfirst.log` is a **real red**: `PINS: 0/6 pins pass`. It ran the harness before the
  runtime existed. That is genuine FAIL-first, not a retrofitted red.
- The dial map is stated as an **equation**: dial 14 = `max(src dial 1 × weight)`.

And the layout section is accurate. I checked every path it claims. All 11 exist.

---

## 2. What actually runs, what is asserted, what is untested

**Runs (5 executable shell scripts, ~10 KB, all of it read):**

| file | what it really does |
|---|---|
| `.quilt/bin/quilt-init` | `mkdir -p`, `git config core.hooksPath .quilt/hooks`, then **writes both hooks as heredocs** |
| `.quilt/hooks/pre-commit` | freeze only: staged `cells/` → read **committed** `HEAD:cells/<a>/dials/15` → `>0.5` ⇒ exit 1 |
| `.quilt/hooks/post-commit` | `diff-tree` probe → receipt → cascade → maybe auto-commit → append watch line |
| `.quilt/bin/quilt-cascade` | awk one-pass `max(src_dial1 × weight)`, rewrite only if numerically different |
| `.quilt/bin/quilt-receipt` | JSON `{commit, changed_cells, key_dials, ts}`, `ts` = **git commit time** |

**No drift:** the checked-in `.quilt/hooks/*` are byte-identical to what `quilt-init` generates.
Hooks are generated from the script, so they cannot rot apart. That is a correct design choice.

**Test count: 6 pins / 23 checks.** MEASURED, re-run by me:

```
P1 receipt+watch on dial commit : PASS      P4 rewind                  : PASS
P2 freeze enforcement           : PASS      P5 clone needs quilt-init  : PASS
P3 cascade                      : PASS      P6 non-cell commit silent  : PASS
PINS: 6/6 pins pass (23 checks pass, 0 checks fail)   exit 0
```

**Does any test execute the product, or only its helpers? — The product, genuinely.** This is the
question I was told to be suspicious about, and the honest answer cuts the other way. The pins do
not import functions and assert on them. They `git init` scratch repos, `cp -R` the runtime in,
run `quilt-init`, write real dial files, run **real `git commit`** so the **real hooks fire**, then
count receipt files and watch lines off disk. P5 clones a real repo and proves hooks are inert
before `quilt-init`. These are integration pins, not unit tests.

**The mutation test — the one equation, multiplied by zero.** I took the README's own equation and
killed it (`.quilt/bin/quilt-cascade:35`, `val = v * w` → `val = v * w * 0`):

```
P3 cascade : FAIL
PINS: 5/6 pins pass (21 checks pass, 2 checks fail)   exit 1
```

**CAUGHT.** The suite constrains the semantics, not merely the presence of the code. This repo is
not the vacuous-suite failure mode. Say that plainly on October 14 if anyone asks, because it is the
thing that makes the rest of this document credible.

**CI: none. Zero. MEASURED from the clone:** no `.github/` directory, no workflow files, no
Actions runs. (The API call returned `Bad credentials` — the token in git config clones but has no
API scope — so I verified CI from the tree itself, which is the stronger source anyway.) The pins
are run by a human, manually, and their output is committed to `pins/`. That is the whole
verification story: 23 checks, no automation, no gate.

**What is untested — and this is the entire finding:**

- **No pin performs a merge.** All six are single-branch, linear, one writer.
- **No pin has two agents.** P5 is the only multi-repo test and it only proves a clone is *inert*.
- **No pin ever runs the cascade after a merge**, or the freeze across a merge.
- **No pin checks receipt *content*** — only that the file exists and contains the hash and alias.
  It would pass if `key_dials` were `{}`.
- **No pin checks the watch line's second field**, which is the field the README names.

---

## 3. Strongest version of *their* argument — and the strongest objection

**Their case, at full strength, no hedging:** The brief asks how hundreds of thousands of agents
work on changes concurrently. The naive answer is "build a new coordination substrate." That answer
has failed every time, because you now have to re-implement branching, merging, rewind, transport,
durability, and the entire review surface — badly. `quilt-in-git` declines to re-implement any of
it. It maps the Quilt onto git's existing semantics and *inherits* them, which means it gets 25
years of adversarial hardening for free, and the repo is simultaneously the Sheet, the journal,
and the collaboration bus with no synchronisation layer to write. Critically, it is **not a
proposal**. Six pins, 23 checks, green, FAIL-first log committed, on a second git version. The
dial-as-file encoding is not incidental — one float per file means **git's line merge is trivially
correct on dials**, because there is nothing to conflict inside a one-line scalar. For a fleet
nudging 16 knobs across thousands of cells, that is the right primitive, and the cascade is
deterministic and single-pass by construction.

**Strongest objection — and it is severe, because it is a code defect, not a taste dispute:**

> **The central operation of the brief — the merge — is structurally invisible to the entire
> runtime.** I did not infer this; I triggered it.

`post-commit:21` is the gate every tick passes through:

```sh
CELL_PATHS=$(git diff-tree --root --no-commit-id --name-only -r HEAD -- cells/)
[ -n "$CELL_PATHS" ] || exit 0
```

`git diff-tree -r HEAD` **without `-m` returns nothing for a merge commit.** MEASURED, on a
two-parent merge commit that demonstrably changed a cell:

```
HEAD parents: 25a62b9 15429f1 7101258
diff-tree -r HEAD -- cells/  =>  []            <-- empty; hook exits 0 here
diff-tree -m ...  -- cells/  =>  [cells/auth/body cells/auth/dials/1]
git show --stat HEAD:  cells/auth/body | 2 +-
```

Consequence, in receipts, walking every commit in the history I built:

```
25a62b9  receipt=NO <<<  merge: agentB
15429f1  receipt=NO <<<  merge agentA
7101258  receipt=YES     tick: agentB claims TTL=3600
```

**Every merge — clean, conflicted, fast-forward or `--no-ff` — produces no receipt, no watch line,
and no cascade re-evaluation.** I confirmed the human-resolution path too: I resolved a real
conflict, committed, and the resolution commit `d2f3830` got `receipt=NO, watch lines=3`. There is
no `post-merge`, no `pre-push`, no `pre-receive` hook — `ls .quilt/hooks/` returns exactly
`post-commit` and `pre-commit`. A repo whose thesis is "git hooks are the runtime" has **no hook
for the one operation that makes concurrent editing concurrent.**

Compounding, all MEASURED:

- **There is no hash anywhere in the codebase.** `grep -rniE "sha|hash|md5|digest|checksum"`
  over every non-`.git` file returns only the *word* "hash" in comments. The receipt binds nothing.
- **The README's watch format is false.** README:74 says `tick <short> <receipt-hash> <cells>`.
  Code, `post-commit:36` and `quilt-init:90`, identical: `printf 'tick %s %s %s\n' "$SHORT"
  "$SHORT" "$CELLS"`. The second field is **not a receipt hash — it is the commit short hash
  printed twice.** Its own committed log shows the duplication: `tick a353076 a353076 auth`. A
  field named `receipt-hash` that is a copy of a different field is a tampered receipt waiting to
  be trusted.
- **Freeze is not enforced where it matters.** The cascade auto-commit runs `git add cells/` then
  `git commit --no-verify` (`post-commit:31-32`). So cascade sweeps *any* dirty cell file into a
  commit that skips the freeze check. The README admits this in limits 3 and 4, which is honest, and
  it still means the one guard that looks like a lock can be side-stepped by a hook.
- **The body is never parsed by any code.** `grep -rn "body" .quilt/bin/* .quilt/hooks/*` (comments
  excluded) returns **0 hits**. And `grep -rniE "claim|contradict|assert|disagree|conflict"` over
  `.quilt/` and `README.md` returns **0 hits**. There is no vocabulary for a claim at all.

---

## 4. Strongest version of *my* argument — and the strongest objection to it

**Mine, at full strength:** The scarce resource in a fleet where hundreds of thousands of agents
touch the same facts is not storage, not branching, not transport. Git solved all of those decades
ago. The scarce resource is **deciding which competing claim is true — and being able to say
afterwards why, and to keep the losers.** Today the loser's reasoning is destroyed by the merge:
it either conflicts (requiring a human, which does not scale to 10^5 agents) or it silently
overwrites. Adjudication must itself be a committed, hash-chained artifact, and the losing claims
must be **preserved, not discarded** — because the record of what was rejected and why is the only
thing that makes a fleet's output auditable rather than merely consistent. `quilt-in-git` inherits
git's *storage* semantics and none of git's *truth* semantics, and the gap is exactly where my
entry lives.

**Strongest objection to mine, and it is the one that should worry you before October 14:**

> **Mine is a thesis. Theirs is a repository with 23 green checks.** Their artifact runs, is
> reproducible on a second git version, survived a mutation of its core equation, and ships a
> committed FAIL-first log. If my entry is prose arguing that contradiction deserves a first-class
> representation, then on the day, a judge comparing a working 13 KB system to an argument will
> pick the working system — and my argument, however correct, will read as a critique of a repo
> they can run in thirty seconds. Their README's *first* claim is also the one thing I am not
> competing for: cells-as-directories, commits-as-ticks, git's semantics free. That is not an
> alternative to adjudication. It is the floor adjudication stands on.
>
> Worse: my strongest empirical point against them — merges are invisible — is a **one-line fix**
> (`diff-tree` → `diff-tree -m`, plus a `post-merge` hook). Once someone in this fleet applies it,
> my objection evaporates and what remains is a feature request, not a competing answer.

I want that on the record, because it is the honest shape of the risk and it is the reason §6 comes
out the way it does.

---

## 5. Do they actually conflict? — No. I checked the hard way.

I built their exact stated hazard — two agents, both green against `main`, asserting contradictory
values for one fact (the `quilt-tools#32/#33` shape) — and ran it:

```
$ git merge --no-ff agentB
Auto-merging cells/auth/body
CONFLICT (content): Merge conflict in cells/auth/body

<<<<<<< HEAD
claim: TTL=900  (src A)
=======
claim: TTL=3600 (src B)
>>>>>>> agentB
```

**Answer to your direct question: their `post-commit` cascade would not catch it, and would not even
see it.** Two independent reasons, both structural rather than a missing feature:

1. **The conflict stops the commit.** A conflicted merge never produces a merge commit, so no
   `post-commit` fires. Git hands a conflicted tree to a human, and the runtime is not in that loop.
2. **Even a clean merge is invisible** (§3), so the cascade would not re-run afterward either.

And here is the deeper point, which is the strongest thing I can say on your behalf: **dial files
cannot represent the disagreement, so the runtime cannot detect it.** One float per file means a
contradiction is not a value — it is the *absence* of a value, and git resolves that by picking one.
The dialect is closed. Their data model is *right for knobs* and *provably unable to hold a claim*.
That is not a missing feature; it is a typing decision. It also means the conflict is invisible in
the journal: `watch.log` stayed at 3 lines through the whole contradiction. A fleet cannot audit a
disagreement it never recorded.

Note the asymmetry that makes this compose rather than compete: **dials and claims are different
types, and the fix does not touch the dial design.** A claim is a multi-line, named, attributed
record in `body` — a type the format already has room for and that **zero lines of code currently
read**.

---

## 6. What each one is missing

**`quilt-in-git` is missing, in priority order:**

1. **A `post-merge` hook, and `-m` on the diff probe** (one line + ~15 lines). Without this, the
   runtime cannot observe the operation its entire thesis is about. *This is the gap.*
2. **Any integrity binding.** No hash is computed anywhere. A receipt that no one hashes is a
   receipt that anyone can edit. The `ts` = git-commit-time decision is good (deterministic); it
   just needs to be hashed.
3. **An honest second watch field.** Either compute the receipt hash, or rename the field. Right now
   the README documents a field the code does not produce.
4. **A claim type with contradiction semantics** — the §5 gap, inherited from the dialect.
5. **CI.** 23 checks, zero automation. One `bash tests/pins_quiltgit.sh` workflow would close it.

**My adjudication entry is missing:**

1. **A running artifact.** This is the real deficit and it is the one that decides the slot.
2. **Everything git already solved.** Branching, rewind, transport, durability — I would be
   re-litigating solved problems if I competed head-on, which is the strongest argument for
   *not* competing.
3. **Dial values and propagation.** `max(src × weight)` one-pass is a genuinely decent
   entanglement rule. I have no equivalent.

**Verdict on the two entries, plainly:** *their* mechanism is real and *my* target is real, and I am
the weaker entry **as of today, by the only measure a judge can check in a minute** — 23 green
checks against an argument. But the merge finding means my target is the one they structurally
cannot hold, which is the only reason to think this is not a loss.

---

## 7. Recommendation: **do not compete — compose, and take their substrate**

Ship **one** entry: their repo, plus the adjudication layer on top. Concretely, three commits:

1. `diff-tree -m` + a `post-merge` hook, so **merges are journaled** like any other tick. *(Fixes
   their worst defect; makes the journal trustworthy for the first time.)*
2. Give `post-merge` a **refusal mode**: if the merged tree contains two attributed `claim:` lines
   for the same key with different values, do **not** commit silently — write
   `.quilt/adjudications/<short>.json` naming the winner, **both losing claims verbatim, and the
   reason**, and exit non-zero. That is your entry, expressed in ~40 lines, in their dialect,
   without touching one dial file.
3. Hash the receipt; make the watch line's second field the actual hash. Closes §3 and §6-3.

This is a better outcome than either of us winning: it takes the strongest existing artifact as the
floor, and puts the one idea they provably cannot express on top of it. **Do not enter as two
answers to the same brief on October 14 — enter as one repo that has both, and let their pins be
the evidence that the substrate was real before you built on it.**

---

**composes — and the composition takes `quilt-in-git` as substrate, with the missing `post-merge`
adjudication hook as the delta; my entry alone is the weaker one as of tonight.**

---
### Receipts (all reproduced locally, no pushes)
- `6a1ae48` · clone depth 50 · 11 files · 12,034 B read in full · 3 commits · **no `.github/`, zero CI**
- Pins re-run by me on git **2.39.5** (repo recorded 2.43.0): **6/6 pins, 23 checks, exit 0**
- Mutation `val = v*w` → `val = v*w*0`: **P3 FAIL, 5/6, exit 1** — the suite is not vacuous
- Merge probe: `diff-tree -r HEAD -- cells/` ⇒ `[]` on a 2-parent merge ⇒ `post-commit:21` exits 0
- `git show --stat` on that merge: `cells/auth/body | 2 +-` — the change existed; the hook never saw it
- Receipts over full history: both merge commits `receipt=NO`; resolved-conflict commit `receipt=NO`
- `grep -rniE "sha|hash|md5|digest|checksum"` (excl. `.git`): **no hashing anywhere**
- `post-commit:36` / `quilt-init:90`: `printf 'tick %s %s %s\n' "$SHORT" "$SHORT"` — README:74 calls
  the 2nd field a `receipt-hash`; it is a duplicate of the 1st
- `ls .quilt/hooks/`: `post-commit`, `pre-commit` only — **no `post-merge`, no `pre-push`**
- Contradiction repro: `CONFLICT (content)` on `cells/auth/body`; `watch.log` unchanged at 3 lines
- `grep -rniE "claim|contradict|assert|disagree|conflict"` over `.quilt/` + `README.md`: **0 hits**
