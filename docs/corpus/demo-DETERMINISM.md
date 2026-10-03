# demo-DETERMINISM.md — the demo is now filmable

**Branch:** `demo-determinism` in `/workspace/projects/fleet-triage/quilt-in-git-adj`
(commit `11f0c50`, branched off `adjudication` at `4239837`). **No push.**
Nothing was published to `quilt-adjudication` and nothing went to GitHub.

Two questions, two answers, both measured:

1. **Are two cold clones byte-identical?** **Yes.** Output and record file,
   same sha256, same filename, empty diff.
2. **Which handle is correct?** **`git checkout HEAD -- <path> && git commit`.**
   Neither the one in the record nor the replacement is.

---

## 0. One correction to the brief, because it changes what had to be fixed

The brief says the record's name `<short>.json` "changes on every run." It
does not. `<short>` is the first 7 hex of `git write-tree` at
`pre-merge-commit`, and a tree hash is a pure function of file names, modes
and blob contents. Across every run I measured it was `f544b35.json`, every
time, on this machine.

What *does* change on every run is the **rest of the record** and the two
HEAD prefixes printed above it:

```
  HEAD before the merge : 7b554922          <- varies
  HEAD after  the merge : 7b554922          <- varies
      "head_before": "7b5549221d1d77f6..."  <- varies
      "merge_head":  "7b5549221d1d77f6..."  <- varies
      "ts": 1790934962,                     <- varies
```

`head_before` and `merge_head` are commit ids, and a commit id is a hash of
its author and committer timestamps. `ts` is `git log --commit-time` of HEAD,
which is history rather than wall clock — correct as designed, but the
history it reads was built with wall-clock dates.

So the lie on screen was the same lie either way, one line lower than
described. Pinning the inputs fixes the filename, the record and the printed
HEADs together, and it also closes a filename hole that *was* real (§3).

---

## 1. What changed. Inputs only.

`demo.sh` gained a determinism block and **not one byte of output was
edited**. No compositing, no re-capture, no post-processing, no renamed file.

```sh
PIN_EPOCH=1767603600            # 2026-01-05T09:00:00Z
export GIT_AUTHOR_DATE="$PIN_EPOCH +0000"
export GIT_COMMITTER_DATE="$PIN_EPOCH +0000"
umask 022
LC_ALL=C
TZ=UTC
export LC_ALL TZ
```

Three notes on why each is there and what it was doing.

**Dates.** Git's raw `<epoch> <offset>` form is used rather than a formatted
string so this does not need GNU `date` and does not break on a judge's
macOS. Every commit the script makes — skeleton, seed, both PRs, both merges
— inherits the pin, so the tree, the commits, the record and the printed
HEADs are all functions of the repository.

**umask.** See §3 — this one is not cosmetic.

**Locale/zone.** `sort` collation and any zone-dependent formatting should not
be left to the machine. `LC_ALL=C` does not touch the UTF-8 the script prints;
it only fixes collation.

One addition, which changes nothing by default:
`QUILT_DEMO_KEEP=1` keeps the scratch tree and prints its path instead of
deleting it. It is the difference between proving the record is the same *on
screen* and proving the bytes *on disk* are the same. With the flag unset the
output is byte-identical to before the flag existed.

The filename scheme is untouched. `<short>` is still a content hash of the
tree the refusal judged.

---

## 2. The proof: two cold clones, empty diff

Both clones made with `git clone --branch demo-determinism` from the repo,
same commit `11f0c50948d7029c77804d391777cc9d7de1c0bd`, run independently.

### 2a. `demo.sh` output

```
$ sha256sum A.out B.out
3b3d2094135d3d7dec5966514f3ae82da79332431246a8d034162a765a81a94d  A.out
3b3d2094135d3d7dec5966514f3ae82da79332431246a8d034162a765a81a94d  B.out

$ diff -u A.out B.out
$ echo $?
0
```

**The empty diff is the deliverable.** 4378 bytes, exit 0 both runs.

### 2b. The record file on disk

```
A: quilt/.quilt/adjudications/f544b35.json   (1340 bytes, sha256 7cdb115358902d04...)
B: quilt/.quilt/adjudications/f544b35.json   (1340 bytes, sha256 7cdb115358902d04...)

$ diff -u A.json B.json
$ echo $?
0
```

Same name, same bytes. The name the video will show is the name the judge gets.

### 2c. The whole suite, re-verified from both clones

| harness | clone A | clone B |
|---|---|---|
| `tests/pins_quiltgit.sh` | **11/11 pins, 59 checks, 0 fail** | **11/11 pins, 59 checks, 0 fail** |
| `tests/pins_undo_handle.sh` | **29 checks, 0 fail** | **29 checks, 0 fail** |
| `tests/pins_determinism.sh` | **7 checks, 0 fail** | **7 checks, 0 fail** |

`pins_quiltgit.sh` is unchanged and still 11/11 / 59 checks, same as before
this branch. Nothing regressed to make the demo deterministic.

### 2d. The negative control

Two runs agreeing proves nothing unless two runs *can* disagree. So
`tests/pins_determinism.sh` D4 strips the pins and requires the output to
move. It does:

```
  -  HEAD before the merge : 3eb23e52
  +  HEAD before the merge : 78c48afb
  -      "head_before": "3eb23e527affbd4f07a912d4562241b0d66a3b6e",
  +      "head_before": "78c48afb617507dc5d5efa5bcf753c1e993e391a",
  -      "ts": 1790935298,
  +      "ts": 1790935299,
```

The control earned its keep on the way: its first version inherited the
pinned dates from the harness's own environment and reported the output as
*identical* without the pins. That is exactly the false green it exists to
catch, and it now runs its children under `env -u GIT_AUTHOR_DATE
-u GIT_COMMITTER_DATE`.

---

## 3. The umask hole was real, and it is not the one I first claimed

The brief's filename concern is not hypothetical — it is just not caused by
the clock. `.quilt` is installed with `cp -R`, and without `-p` the mode is
source-mode masked by umask. Those bits are **tree entries**:

```
.quilt/bin/quilt-adjudicate  100755  ->  tree 8d977c0
.quilt/bin/quilt-adjudicate  100644  ->  tree 61ba351
```

I claimed in my first commit message that a judge on `umask 077` would be
handed a different filename. **That was wrong and I amended it.** Measured
across six umasks:

| umask | unpinned demo | pinned demo |
|---|---|---|
| 022 | `f544b35.json` | `f544b35.json` |
| 077 | `f544b35.json` | `f544b35.json` |
| 027 | `f544b35.json` | `f544b35.json` |
| **111** | **no record at all** | `f544b35.json` |
| **177** | **no record at all** | `f544b35.json` |
| **777** | **no record at all** | `f544b35.json` |

077 and 027 are already safe: `cp -R` masks group and other bits, and git
records only the **owner** execute bit, which survives. The hole opens at
**0111 and stricter**, where the hooks land non-executable, git skips
`pre-merge-commit`, the veto never fires, the merge **succeeds**, and:

```
  PANE 2: UNEXPECTED (exit=0, HEAD moved: 47ff1708... -> b04baf04...)
  NO ADJUDICATION RECORD — expected one under .quilt/adjudications/
```

That is the honest part worth saying plainly: the demo **fails loudly**,
exit 1, naming the problem. It does not lie. But the judge is holding a
broken demo, and a restrictive umask is not exotic enough to wave away. With
the pin, all six umasks produce `f544b35.json`.

---

## 4. The handle. Settled, with the command that proves it.

New harness: `tests/pins_undo_handle.sh` — 5 pins, 29 checks, all green. It
builds the two-PR fixture, runs it into the refusal, then runs each candidate
handle and measures the same three things: did pr33 land, how many parents
does HEAD have, how many claims survive and which value.

The record's promise: **the loser is 19** (base, `quilt-tools#32`). The
runtime picked **21** (incoming, `quilt-tools#33`).

### A — the handle in the record today

```sh
git checkout HEAD -- cells/inbox/body && git merge --abort
```

```
PASS P2a clause 1 succeeds (0)
PASS P2b clause 2 succeeds (0)
PASS P2c MERGE_HEAD is cleared afterwards (absent)
PASS P2d pr33 did NOT land — nothing was accepted (no)
PASS P2e HEAD did NOT gain a second parent (3)
PASS P2f the loser survived in HEAD (19)
PASS P2g the advertised third clause is refused again (1)
```

**`git merge --abort` works.** rc=0, `MERGE_HEAD` cleared, tree restored. The
earlier claim that it always fails after a refusal was wrong, and measuring
it is what turned up the real defect.

It is a clean **undo**, not an acceptance. pr33 is left unmerged, HEAD never
gains a parent, and the 21 never entered history. Nothing was accepted.

And the stderr ships a *third* clause — `&& git merge <branch>`. Running the
full advertised sequence: **exit 1, the identical refusal again.** Same index,
same rule, same conflict. The reader is sent in a circle by a field whose job
is to get them out of one.

### B — the replacement (`git checkout <TREE> -- <path> && git commit`)

Worse than I expected, in two independent ways.

```
PASS P3a clause 1 succeeds (0)
PASS P3b it stages the merge tree's claims (2)
PASS P3c the value it stages is the WINNER (21,19)
PASS P3d it only commits with the veto disabled (0)
PASS P3e pr33 landed (yes)
PASS P3f the SURVIVING value is the WINNER (21,19)
```

Run honestly, with hooks live and no `--no-verify`, **B is refused** — it
checks out the contradictory merge tree, and `pre-commit` finds the same
conflict. It only commits if you add `--no-verify`, which switches off the
veto this repository exists to demonstrate. And when it does commit, it
commits **the winner, 21**, over a tree still carrying **both** claims.

It is named `to_accept_the_loser`. It accepts the loser of nothing and leaves
both lines standing. A field that reverses the rule by applying the rule is
not a handle.

### C — the handle that is correct

**A's first clause, with the second clause replaced:**

```sh
git checkout HEAD -- <path> && git commit
```

```
PASS P4a clause 1 succeeds (0)
PASS P4b clause 1 stages the LOSER's text (19)
PASS P4c the veto does NOT re-fire on a one-claim tree (0)
PASS P4d the merge landed (yes)
PASS P4e HEAD gained a second parent (3)
PASS P4f ONE claim survives (1)
PASS P4g the surviving claim is the LOSER (19)
PASS P4h MERGE_HEAD is cleared (absent)
```

One clause survives from A, and it is the load-bearing one: `git checkout
HEAD -- <path>` is what writes the loser's text into the index. Only the
second clause was wrong. `--abort` discards the merge; `git commit` finishes
it. The veto does not re-fire because the tree no longer contradicts itself,
so this goes back through the same check rather than around it.

### The one-line change to `quilt-adjudicate`

```diff
-    printf '      "to_accept_the_loser": "git checkout HEAD -- %s && git merge --abort"' \
+    printf '      "to_accept_the_loser": "git checkout HEAD -- %s && git commit"' \
       "$wpath"
```

and the matching stderr line:

```diff
-    echo "    git checkout HEAD -- $wpath && git merge --abort && git merge <branch>"
+    echo "    git checkout HEAD -- $wpath && git commit"
```

**Not applied.** Per the brief, no pushes to `quilt-adjudication`, and one
unverified second fix there is worse than the first wrong one. This is
branch-local and unverified against the wider suite — it changes the record's
bytes, so it must be re-recorded before anything is filmed.

---

## 5. `MERGE_HEAD` — the two moments, and why the record is right

Worth pinning down, because it is the fact both earlier attempts tripped on.

| when | `.git/MERGE_HEAD` |
|---|---|
| **while `pre-merge-commit` runs** | **absent** — `.git/MERGE_MSG` and `MERGE_MODE` too |
| **after the refusal returns** | **present**, and the merge is still in progress |

Git writes the merge state *after* the hook returns. So the comment in
`quilt-adjudicate` — *"at pre-merge-commit time git has already cleared
MERGE_HEAD"* — is **correct**, and the `ORIG_HEAD` fallback is doing real
work. `merge_head == head_before` in the record is not a missing field; it
is the accurate value for a `pre-merge-commit` refusal. P5 pins both halves.

This is also why C works: by the time the reader runs the handle,
`MERGE_HEAD` exists, so `pre-commit`'s guard fires and the check runs again.

---

## 6. Open, found on the way, not fixed

**`"side": "base"` is hardcoded for every loser** in the record writer:

```sh
printf '        {"value": "%s", "by": "%s", "side": "base", "line": "%s"}' ...
```

The winner is the *incoming* claim, so losers are normally base claims and
the label is true. But a conflict can have two incoming claims for one key —
two attributed `claim:` lines with different values arriving on the merged
side — and then a loser is labelled `base` while being incoming. The label
would be a lie, and `git checkout HEAD -- <path>` would restore the wrong
text, because the loser's line is not in HEAD.

Not reachable in this fixture, so no pin is red over it, and I did not want
to invent a pin I had not observed fail. It is a real generality gap in a
field the demo puts on screen, and it belongs in the queue before the
handle change lands. **Flagging rather than fixing** — the handle fix in §4
should land with it, not before it.

---

## 7. Reproduce all of it

```sh
git clone <repo> quilt && cd quilt
git checkout demo-determinism
bash tests/pins_determinism.sh    #  7 checks
bash tests/pins_undo_handle.sh     # 29 checks
bash tests/pins_quiltgit.sh        # 11/11 pins, 59 checks
./demo.sh                          # the thing being filmed
```

Requirements: `git` and a POSIX shell. The handle measurements are on
**git 2.39.5**; the two `MERGE_HEAD` moments in §5 are a git implementation
detail and are worth re-measuring on whatever a judge is holding.

## 8. State of the tree

```
11f0c50  demo: QUILT_DEMO_KEEP=1 keeps the scratch ...
ef1fc45  demo: pin the fixture so two cold clones are byte-identical
4239837  (base, adjudication) README: document the three commits ...
```

`quilt-adjudication` is untouched. `README.md`, `demo.sh`'s prose and the
recorded demo timing are untouched. No fixture was renamed and no record was
edited — the two things the brief ruled out are the two things that were not
done.
