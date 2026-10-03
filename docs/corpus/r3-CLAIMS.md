# r3 — CLAIM AUDIT: `SuperInstance/quilt-adjudication`

Auditor: scout lane, independent of the author. Date: 2026-10-02.
Fresh clone: `git clone https://github.com/SuperInstance/quilt-adjudication.git`
HEAD `b755e41` "fix, third time, and the measured reason: only the SECOND clause was wrong".
26 tracked files. Environment: git 2.39.5 (same version the README names), linux, no network used by the entry.

**Bottom line: the entry's load-bearing claim — "no model is in the loop" — VERIFIES, and I could not
break it. But the README is materially stale in three places, the repo ships a failing test the
README never mentions, and the winner rule is applied backwards on the post-merge path. A judge who
runs only the README's command sees green. A judge who reads the code sees a shipped FAIL and a
rule that inverts. Four things must be fixed before October 14.**

---

## Method

Everything below was executed against a fresh clone unless marked `asserted`. Nothing is taken from
a comment. Where I say "the code says X" I mean the code emitted X on this machine today.

---

## Part 1 — The claim list

`M` = measured (I ran it, re-runnable) · `C` = cited (primary source) · `A` = asserted (only written down)

| # | Claim, in the entry's own words | Class | Verdict |
|---|---|---|---|
| 1 | "The entire simplified Quilt lives inside a plain Git repository: dials are files, ticks are commits… Git hooks are the runtime." (README:3) | M | **holds** — pins P1–P4 exercise exactly this, 59/59 |
| 2 | "You need **git and a POSIX shell**. That is the entire dependency list — no Node, no Python, no network, no account, no API key, no install step." (README:19) | M | **holds** — swept all 14 executables; no interpreter, no network client, no URL literal in `.quilt/` or `demo.sh` |
| 3 | "It is three commits on top of `6a1ae48`" (README:14) | A | **FALSE.** `6a1ae48` does not exist in this repo (`git cat-file -t 6a1ae48` → `fatal: Not a valid object name`). There are **6** commits, not 3. See F-1. |
| 4 | "`bash tests/pins_quiltgit.sh` # 11 pins, 59 checks. exit 0." (README:28) | M | **holds** — 3.7s, `PINS: 11/11 pins pass (59 checks pass, 0 checks fail)`, exit 0 |
| 5 | "`./demo.sh` # the two-PR refusal, both panes. exit 0." (README:29) | M | **holds** — exit 0, both panes behaved as described |
| 6 | "a `post-commit` hook turns that tick into a receipt, an entanglement cascade, and a watch-log line" (README:5) | M | **holds** — P1 |
| 7 | "the substrate's own `post-commit` probe could not have caught a merge anyway: `git diff-tree` prints nothing for a merge commit unless you pass `-m`" (README:36) | M | **holds** — mechanism verified in `post-merge:9-13`; `pins/failfirst-merge.log` is red as claimed |
| 8 | "Receipts gained `parents` and `merge` fields so a merge receipt is distinguishable from a tick receipt. Pinned by P7" (README:47) | M | **holds** — P7 PASS |
| 9 | "the red against the untouched substrate is in `pins/failfirst-merge.log`" (README:47) | M | **holds** — log ends `PINS: 7/9 pins pass (26 checks pass, 2 checks fail)` / `FAILURES PRESENT` |
| 10 | "Two claims **conflict** when they name the same key, carry different values, and come from different attributions." (README:57) | M | **holds** — implemented `quilt-adjudicate:124-133`; P8k/P8l |
| 11 | "One author restating a number is a retraction, not a contradiction (P8k). An unattributed line is not adjudicable at all (P8l)." (README:60-61) | M | **holds** — P8 PASS |
| 12 | "When a merge would produce a conflict, the merge is **refused**" (README:63) | M | **PARTLY FALSE** — true for 3-way merges; **false for a fast-forward** (F-2) and **exit-code-invisible on the post-merge path** (F-3) |
| 13 | "No merge commit is created. HEAD does not move, the branch never gains a second parent, and the contradiction stays a file on disk instead of becoming history." (README:95) | M | **holds on the `--no-ff` path**; **FALSE on a plain `git merge` fast-forward** — contradiction lands in history, `git merge` exits 0 (F-2) |
| 14 | "**There is no judge here.** No model is in the loop, by design, and every record says so in two fields you can read" (README:101) | M | **HOLDS. This is the claim the whole entry rests on, and it survives.** Full sweep in F-6. |
| 15 | `"adjudication": "mechanical"` / `"judge": "none — no model is in this loop, by design"` (README:104-106) | M | **holds** — both fields present verbatim in every record I produced |
| 16 | "The winner is whichever claim arrived on the side being merged. That is an *ordering*, not a judgment about truth." (README:108) | M | **holds on the `--index` path; INVERTED on the `--head`/post-merge path** — the record names the *base* claim as `"side": "incoming"` (F-4) |
| 17 | "No judge ran. If the losing number is the right one: `git checkout HEAD -- cells/inbox/body && git merge --abort && git merge <branch>`" (README:90-91) | A | **FALSE. This string does not exist anywhere in the runtime and cannot work.** See F-5. This is the single most quotable block in the README. |
| 18 | "`post-merge` re-runs the check for a `--no-verify` merge and says plainly that it is **too late to refuse**" (README:127) | M | **holds, and is honestly worded** — but see F-3: the record it writes is wrong |
| 19 | "Measured on git 2.39.5: with only `pre-merge-commit` installed, that merge commit was created and the hook never ran." (README:118) | M | **holds** — this machine is git 2.39.5, and P8m passes on the `git commit`-concludes-a-merge path |
| 20 | "`quilt-init` now writes `.quilt/.gitignore` and the journal is untracked." (README:165) | M | **holds** — `.quilt/.gitignore` present |
| 21 | "**This is the one change here that alters a substrate property**, and it is what made merging possible at all." (README:170) | A | **asserted** — plausible, not measured. Low risk; it is a scoping statement, not a number. |
| 22 | "**P10 pins that the generated hooks are byte-identical to the checked-in ones**" (README:206) | M | **holds** — P10a/b/c PASS |
| 23 | "Field 2 is now the content hash of the receipt… **prefixed with its algorithm**" (README:144) | M | **holds** — observed `tick f61894a sha256:45994c08…`; P9b–P9g PASS incl. independent recompute and mutation |
| 24 | "P9 recomputes the digest with coreutils rather than with `quilt-hash`, so it is a check and not a tautology" (README:156) | M | **holds** — P9e PASS |
| 25 | "`ts` is the git commit time (`git log -1 --format=%ct`), never wall clock, so receipts reproduce deterministically from history." (README:281) | M | **holds** — demo record hash `47bee50` identical across 3 consecutive runs |
| 26 | "The refusal is enforced from **two doors**, because one is not enough." (README:113) | M | **holds** — there is a third door (`--no-ff --no-verify`) where neither door can veto, and the entry does not count it as a refusal failure because it discloses it (F-3) |
| 27 | "`P1–P6`… `P7`… `P8`… `P8m`… `P9`… `P10`… `P11`" — the pin table, README:290-299 | M | **INCOMPLETE** — the repo also ships `tests/pins_undo_handle.sh` (P12), absent from the table, absent from the Run-it block, and **it fails**. See F-7. |
| 28 | "`pins/failfirst-merge.log`, `failfirst-refusal.log` and `failfirst-hash.log` … They are red, and they are committed" (README:302) | M | **holds** — all three red |
| 29 | "No CI. There is no `.github/` in this repo either." (README:277) | M | **holds** — no `.github/` in the tree |
| 30 | "The original six pins still pass." (README:16) | M | **holds** — P1–P6 all PASS |

---

## Part 2 — Findings, in severity order

### F-1 · `README.md:14` cites a commit that does not exist and the wrong commit count — **ASSERTED, presented as fact**
> "It is three commits on top of `6a1ae48`"

Measured: `git cat-file -t 6a1ae48` → `fatal: Not a valid object name 6a1ae48`. The object is not in
this repository at all. `git rev-list --count HEAD` = **6**. The commit actually named in the three
sub-headers — `104f9e0`, `dc547b8`, `01197a0` — **none of the three exist either**
(`fatal: Not a valid object name` for each).

This is the "cited" class failing hardest: six specific, checkable, wrong identifiers in the opening
paragraph and the three feature headers. A judge who checks *one* of them finds nothing, and the
natural conclusion is that the rest was not checked either. Fix: cite `c7a3362` / `a6c3508` / `b755e41`,
and say "six commits, of which three are fixes to a handle I got wrong twice."

### F-2 · A plain `git merge` writes the contradiction into history, silently, and exits 0 — **the headline claim does not generalize**
> README:95 "No merge commit is created… the contradiction stays a file on disk instead of becoming history."

The demo uses `--no-ff` on both panes, which forces a real merge commit and therefore fires
`pre-merge-commit`. A normal fast-forward creates **no merge commit**, so **no pre-merge hook runs at
all**. Measured, runtime fully active, hooks installed via `quilt-init`:

```
$ git merge pr33
Updating 7f531d6..8291e43
Fast-forward (no commit created; -m option ignored)
 cells/inbox/body | 1 +
quilt: REFUSING the merge — the result asserts one key twice with two values.   <- post-merge, too late
quilt: this merge commit ALREADY EXISTS and contradicts itself.
quilt: post-merge is too late to refuse. Undo it with:
quilt:   git reset --hard ORIG_HEAD

git merge exit code seen by a script/CI : 0
contradictory claims now in HISTORY     : 2
```

The refusal fires, prints a correct warning, writes a record — and the merge still **succeeds**. Honest
limits #3 (README:271) discloses the `--no-verify` hole but says nothing about the plain
fast-forward, which requires no bypass flag at all. The entry's own title is "the merge that cannot be
committed silently"; on its most common merge shape it is committed silently.

This is a **disclosure gap, not a lie** — but it is the gap most likely to be found by a judge who
types `git merge` instead of copying the demo.

### F-3 · `post-merge`'s exit code never reaches the caller, and the record it writes is inverted
Two separate defects on the `--no-verify` / fast-forward door.

**(a) The exit code is swallowed.** `post-merge:77` does `[ "$ADJ" -eq 1 ] && exit 1`, and the hook is
correct. But git does not propagate a `post-merge` hook's status into the `git merge` command's exit
code. Measured: `git merge --no-ff --no-verify pr33` → **exit 0** with a contradictory merge commit
created and both claims in the committed tree. A CI gate built on this repo sees green.

**(b) The record's winner is the wrong one, and mislabels its own `side`.** Measured on the same run:

```json
"winner": {"value": "19", "by": "quilt-tools#32 fb2e041", "side": "incoming", …}
"losers": [ {"value": "21", "by": "quilt-tools#33 0101409", "side": "base",     …} ]
```

`19` was in the base before the merge; `21` arrived *with* the merge. The documented rule is "the
winner is the claim that arrived on the side being merged" (README:108). The record names the **base**
claim as the winner and hardcodes `"side": "incoming"` onto it.

Cause, and it is precise: `tag()` (`quilt-adjudicate:108-118`) decides `side` by asking whether the
claim's verbatim text is already in `git show HEAD:<path>`. In `--head` mode HEAD has **already moved
past the merge**, so both lines are present and both get tagged `base`. The `incoming` filter at
`quilt-adjudicate:163` therefore matches nothing, the fallback at `:164` takes the first row, and
`:175` prints `"side": "incoming"` as a **hardcoded string literal** regardless of what the TSV says.
The `side` field in `--head` records is therefore not measured — it is asserted by the printer.

The `rule` string sits one line above it claiming an ordering rule was applied. It was not.

### F-4 · The record's own handle is a no-op on the `--head` path — the exact defect the code says it fixed
`quilt-adjudicate:195-203` documents a fix for a handle that "restored the state the reader was already
in". That fix landed **only on the `--index` path**. On the `--head` path the record still emits:

```
"to_accept_the_loser": "git checkout HEAD -- cells/inbox/body && git commit"
```

Measured, by extracting that string from the record and `eval`-ing it in the repo the record describes:

```
$ git checkout HEAD -- cells/inbox/body && git commit
On branch main
nothing to commit, working tree clean
HEAD before handle: bd0e2ae4   HEAD after: bd0e2ae
claims in body now: 2  (the contradiction is still there)
```

`git checkout HEAD --` restores the file from the commit that *already contains both claims*, then
`git commit` finds nothing. The handle is a no-op that reports success. The self-assessment at
`:199-202` ("the loser is ALREADY the working tree") is correct for the `--index` path and was never
applied here.

### F-5 · `README.md:91` is the retracted handle, still in the README — **the thing you suspected, confirmed**
> "No judge ran. If the losing number is the right one:
> `git checkout HEAD -- cells/inbox/body && git merge --abort && git merge <branch>`"

Your retraction is real and is on `main`: `quilt-adjudicate:195-196` states the old field was
`… && git merge --abort` and that **"BOTH halves were wrong"** — (1) `git merge --abort` always fails
because `pre-merge-commit` runs after git has cleared `MERGE_HEAD`; (2) `git checkout HEAD -- <path>`
restores the base text, which is the loser's value. Commit `a6c3508` "fix: the record's handle pointed
at nowhere and named the wrong target" did it.

**But `README.md` was last modified at `c7a3362` — the first commit.** The three fix commits
(`a6c3508`, `f92d2a5`, `b755e41`) landed after and never touched it. `git log -3 -- README.md` returns
`c7a3362` and nothing else.

So the README's most quotable block — the one a judge will copy, and the one that answers the entry's
headline question — advertises a command the author has publicly retracted as *always failing*. I ran
it. On the demo fixture it does not error out, which is worse than failing: it fast-forwards
(`git merge pr33` at the tail), the fast-forward path writes **both** claims into history, and the
refusal fires again afterwards. Net effect of following the README exactly: the contradiction the
entry exists to prevent becomes permanent history.

Two further stale numbers in the same transcript block:
- **README:87** quotes `.quilt/adjudications/177f885.json`. Today the demo deterministically produces
  `47bee50.json` (verified identical across 3 runs). I also checked out the first commit `c7a3362` and
  re-ran the demo: it produces `f544b35.json`. **`177f885` does not reproduce at any commit I can
  reach.**
- **README:80-95** omits four lines the code now prints (`quilt: no merge commit was created. The
  branch still has one parent.` / `quilt: the merged tree is still on disk — inspect it, then` /
  `quilt:   git merge --abort        to undo, or` / `quilt:   resolve and git commit  to proceed
  anyway.`). The transcript is verbatim output of a build that no longer exists.

### F-6 · "No model is in the loop" — **VERIFIES. Attacked on every path; nothing found.**
This is the claim the entry rests on, so I swept it hard rather than reading the string.

- Enumerated every executable in the repo from `git ls-files` (14 of them). Every one is `#!/bin/sh`
  or `#!/usr/bin/env bash`.
- Grepped the entire runtime (`.quilt/` + `demo.sh`) for `curl|wget|http://|https://|api.|openai|
  anthropic|claude|gpt|llm|sk-|bearer|Authorization|typesafe|jev`. **Four hits, all of them the literal
  string `"none — no model is in this loop, by design"` or a comment asserting its absence.** No
  client, no endpoint, no key.
- Grepped for external interpreters/launchers (`node|npm|python3?|ruby|perl|go|docker|gh|aws|ssh|…`).
  **Exactly one hit: `openssl`**, at `quilt-hash:34-35`, used as a sha256 fallback —
  `openssl dgst -sha256 "$1"`, no `-connect`, no network.
- No URL or hostname literal appears anywhere in the runtime.
- **The refusal path specifically** (your instruction): `quilt-adjudicate` computes conflicts with
  `awk`/`grep`/`git show` and formats JSON with `printf`. There is no branch in the file that could
  call anything. The refusal output I captured byte-for-byte in F-5 came from the same code path a
  merge takes, and contains no network artifact.
- 503-irrelevance note: no endpoint was contacted at any point in this audit, so nothing here depends
  on `api.typesafe.ai` being up.

**Verdict: the strongest claim in the entry is the one that survives intact. It is safe to publish.**

### F-7 · The repo ships a failing test that the README never mentions
`tests/pins_undo_handle.sh` exists, is labelled **P12**, and **fails on a fresh clone**:

```
FAIL: the record carries a winner-side handle (got 'n' want 'y')
P12 verdict: handle executes and moves 19 -> 21, or nothing else matters: 4 pass, 1 fail
EXIT=1
```

Root cause: `tests/pins_undo_handle.sh:39` greps the record for a field named **`to_accept_the_winner`**.
The producer writes **`to_accept_the_loser`** (`quilt-adjudicate:204`). The field the test looks for
does not exist, so `$h` is empty.

This matters twice over:
1. The failing test is a **shipped red** in a repo whose README's Run-it block shows only green. A
   judge who runs `ls tests/` and runs both gets a FAIL. Nothing in the README mentions P12 at all —
   not in the pin table (README:290-299), not in the Run-it block (README:28).
2. Had the name matched, the test would have been **vacuous anyway**. Every meaningful check — "the
   winner is present", "the loser is kept verbatim", "the handle committed", "the tree is clean" — is
   wrapped in `if [ -n "$h" ]` (`:40-51`). With `$h` empty, all four are skipped and the pin reports
   its headline line, "handle executes and moves 19 -> 21, **or nothing else matters**". The test
   whose entire purpose is *"an unrun handle is a fiction"* never runs the handle.

So the test written specifically to prevent this class of defect is itself an instance of it.

---

## Part 3 — What I did not attack, and why

- The 59 checks were not mutation-tested. A pin that passes for the wrong reason is possible; I found
  no evidence of it in the four logs I read, and the P11 self-attribution pin (`verdict_of`, with the
  `P1`/`P10` substring trap handled correctly) is genuinely careful work.
- The substrate-relative red logs (`pins/failfirst-*.log`) were verified *red*, not re-generated
  against `6a1ae48` — that object is not in this repo (F-1), so they are not independently
  re-runnable from this clone. Classify as **cited, unverifiable here**.
- `graph/REFERRAL_GRAPH.json` and `graph/pins-graph.sh` are out of scope for this entry's headline
  claims; `graph/pins/final.log` reports `5 ok, 0 FAIL` and was not re-run.

---

## Part 4 — Required before publication

1. **Rewrite `README.md:80-95`** from a real `./demo.sh` run, or delete the transcript. At minimum
   replace line 91 with the handle the code actually prints. *(F-5 — highest risk: a retracted,
   always-failing command is published as the entry's headline.)*
2. **Fix or delete `tests/pins_undo_handle.sh`**, and add P12 to the pin table and the Run-it block. A
   repo must not ship a red test its README does not disclose. Un-wrap the `if [ -n "$h" ]` block so
   a missing field is a hard failure, not a skip. *(F-7)*
3. **Fix the `side` inversion on the `--head` path**: `quilt-adjudicate:108-118` must compare against
   the pre-merge commit (`ORIG_HEAD`/`HEAD_BEFORE`), not post-merge `HEAD`, and `:175` must print the
   measured `side` rather than the literal `"incoming"`. *(F-3b)*
4. **Fix the `--head` handle** to be a real command, and give the two paths different handles —
   `HEAD` is the wrong restore source once the commit exists. *(F-4)*
5. **Replace the six dead commit hashes** at `README.md:14` and in the three sub-headers with real
   ones. *(F-1)*
6. **Disclose the fast-forward door** in Honest limits #3, and say plainly that `post-merge`'s exit
   code does not reach the caller's `$?`. *(F-2, F-3a)*

Items 1, 2 and 5 are pure text or a rename. Items 3 and 4 are real code.

**After 1-6 the entry can make every one of its 30 claims defensibly.** Right now it can make about
twenty-four, and two of the remaining six are things a judge can disprove in under five minutes.

---

## The answer to your closing question

**The claim a judge is most likely to call a lie is `README.md:91`** — the refusal's own remedy
command, `git checkout HEAD -- cells/inbox/body && git merge --abort && git merge <branch>`.

**I reproduced it — that is the problem.** It is not a stale number; it is a live command in the
README that the author has already retracted in the source, and the retraction's own comment says it
"ALWAYS fails." Running it on the demo fixture does not fail loudly: the trailing `git merge <branch>`
fast-forwards, the fast-forward door writes both contradictory claims into history, and the refusal
fires *after* the damage. The README does not merely describe an older build; it documents a fix that
reverted three commits ago, on the one line a judge is most likely to trust and copy.

**Runner-up, and the one I would actually worry about: F-3b.** Not a lie in the README — the README's
rule statement is correct — but the *record* the runtime writes on the `post-merge` path names the
wrong claim as the winner while stamping `"side": "incoming"` on it by hardcoded literal. The entry's
credibility rests on the record being honest about what it did. On that path the record is confident,
well-formatted, and wrong. It is more dangerous than the README error precisely because it is harder
to check and reads as instrumentation rather than prose.

**And the thing you should feel best about: F-6.** "No model is in the loop, by design" is the claim
everything else leans on, and it held under a full sweep of every executable, every string, and the
refusal path specifically. Nothing in this entry talks to a network.
