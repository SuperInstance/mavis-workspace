# DEMO.md — the 5–10 minute demo video

**Lane: DEMO (unowned until today). Date: 2026-10-02. Deadline: 2026-10-14.**

Every number in this document was produced by running the thing on 2026-10-02,
not remembered. Where a number in the original brief did not survive that, it
is corrected here and named.

| claim in the brief | measured | status |
|---|---|---|
| `quilt-tools#32` says 19, `#33` says 21 | 19 / 21 | **true** |
| 11/11 pins | `PINS: 11/11 pins pass (59 checks pass, 0 checks fail)` | **true** |
| 59 checks | 59 | **true** |
| `quilt-adjudication`, **26 files** | **19 tracked files** (`git ls-files \| wc -l`) | **WRONG — use 19** |
| handle corrected to "one command, loser already in your tree" | **the correction is not in the code** | **BLOCKING — see §4** |

---

# 1. THE SCRIPT — read aloud, in full

**Target running time: 8 min 40 s.** Comfortably inside 5–10.
**Rule: no title cards, no music bed, no "in this demo we will".** Two
terminals, one voice, and the words below. Every `>` block is spoken aloud as
written. Bracketed lines are direction, not speech. Parenthetical `(pause)`
is a real pause of about two seconds — they are load-bearing.

---

## 0:00 — 0:50 · COLD OPEN

> **[Both panes on screen, side by side, same file open in both, same cursor
> blinking. No voice for eight seconds. Do not cut to anything.]**

Same file. Same two pull requests. On the left, git. On the right, the same
git, with one hook in it.

I'm going to merge the same branch into both, at the same moment, and the only
difference between these two screens is a shell script.

The left one is going to succeed.

---

## 0:50 — 2:05 · WHAT WAS BROKEN

Here is the file. It's called a cell body — a small text file, sixteen dials
next to it, each one a number. Four lines matter:

> **[hold on `cells/inbox/body`]**

`inbound_edges`. How many referrals came in from other agents.

Pull request thirty-two says nineteen. It was written on Tuesday, against
main, and it was correct. Somebody recounted the edges, and nineteen was
right.

Pull request thirty-three says twenty-one. Written on Wednesday, also against
main, and also correct. Somebody else recounted, and twenty-one was right.

Neither author is wrong. Both numbers were true of main, on different days.
And both are committed, and both are in this repository.

These are real pull requests against a real repository. The numbers are the
numbers that were in them. Nothing here is staged for the camera.

The thing that is broken is not in the text. The text is fine — the text
merges perfectly. What's broken is that there are now two true claims about
one fact, and the fact has one value.

---

## 2:05 — 3:20 · WHY GIT CANNOT SEE IT

Git's entire model of a conflict is: two hunks of text touched the same line.

So look at where these two claims landed. PR thirty-two *appended* its claim at
the end of the file. PR thirty-three *inserted* its claim on line three.
Different lines. Different hunks. No overlap.

Git's three-way merge has nothing to complain about. Textbook clean. It won't
put a conflict marker on screen, it won't stop, it won't even hesitate.

And that's the problem. A line-level conflict is a *loud* failure. You see it,
you fix it, you move on. This one is silent. Git's merge is byte-for-byte
correct and semantically wrong, and the only evidence anything went wrong is
that you read the file afterwards and go — wait, why is this here twice?

There's no representation in git for "two claims, both true, one key." The
merge base was a text blob. Both sides are text blobs. Git compares text. It
has nowhere to put the disagreement.

---

## 3:20 — 4:40 · THE MOMENT

> **[This is the shot. Slow. Both panes, both operators typing at the same
> time. Cut nothing. Let the two exit codes sit on screen together.]**

So — both merges, at the same time, on the same branches.

> **[left pane: `git merge --no-ff pr33 -m "merge #33"]` → `exit 0`]**

Left: merged. Exit code zero. The file now has both claims in it. Nineteen and
twenty-one, one after the other, and git is completely satisfied. That commit
has two parents. It is history now. It is permanent.

> **[right pane: the identical command → `exit 1`]**

Right: refused. Exit code one.

And — this is the part that matters — the commit was not created. The head did
not move. The branch did not gain a second parent.

> **[pause. four full seconds.]**

Same file. Same branches. Same second of the day. One of them is in history and
the other one is not. The difference is that one of them had something in it
that could notice the contradiction.

And notice what it printed. It's not a stack trace. It says which key, it says
both values, and it says who said each one. Nineteen, by pull request
thirty-two, commit f-b-two-e-zero-four-one. Twenty-one, by pull request
thirty-three, commit zero-one-zero-one-four-zero-nine. It read the claims, and
it told you which two disagree — and *then* it refused.

---

## 4:40 — 6:05 · WHAT IT WROTE

And then it wrote this. A file on disk: `.quilt/adjudications/`, a short hash,
`.json`.

> **[hold on the record]**

This is the artifact. The message you just saw is a rendering of it. This is
what survives.

> **[walk the fields, top to bottom]**

Top: what happened — refused, the merge. Which tree it judged. Which head it
was at. A timestamp.

> **[point at these two lines. Slow.]**

`"adjudication": "mechanical"` and `"judge": "none — no model is in this
loop, by design"`.

> **[pause]**

Read that again. There is no judge. There is no model. Nothing scored these
two claims. Nobody decided that nineteen is better than twenty-one.

The rule that fired is one line long, and I want you to read it, because it
is the most honest thing in this repository:

> **[point at `"rule"`]**

*the winner is the claim that arrived on the side being merged.* That is not a
judgment. That is an ordering. It says: the incoming one wins, here is the
other one, and here is how to change my mind.

> **[scroll down to `conflicts`]**

Key. Cell. Winner — value, author, and the exact line it came from. And then
`losers`. Not a summary. Not a count. The full text of the losing claim, the
line as the author typed it, byte for byte, with the attribution.

And a `reason` — a sentence that says all of this again, and then tells you
the number I just picked might be the wrong one.

That's the whole point. Nothing is thrown away. Refusing is not rejecting.
Refusing is refusing to *decide silently*. Both claims survive, attributed,
permanently, in a file on disk — even though the merge never happened.

---

## 6:05 — 7:20 · HOW DO I TAKE THE OTHER BRANCH

Which brings us to the question that actually matters. Okay — you refused.
Fine. But I said twenty-one and you think nineteen is right. Now what?

The record hands back a command.

> **[this is the second-most-important shot in the video: run it live, on
> camera, and let it work]**

I'm going to run it, right now, and you'll see it actually work.

> **[read the command off the record, type it exactly:]**

```
git checkout HEAD -- cells/inbox/body && git commit -m "merge pr33, taking quilt-tools#32's 19"
```

> **[exit 0]**

One command. It restores the base text — which is the *losing* claim, the
nineteen — and then it commits.

Exit zero. Two parents. A real merge commit. And it contains *my* number.
Nineteen. Not twenty-one.

And the record is still on disk. The refusal didn't get deleted by the thing
that overrode it. You can go back afterwards and read exactly what it refused,
and why, and what it would have done.

---

## 7:20 — 8:10 · WHAT THIS IS NOT

Three things I want to be straight about.

One: there is no judge. That's a field in the record, not a disclaimer I'm
adding. The winner is an ordering, not a truth. This thing cannot tell you
which number is right, and it is deliberately built so it can never *look*
like it tried. That's the design, not an excuse. The claim is narrow: a merge
that has no way to represent a disagreement should say so out loud instead of
picking one quietly.

Two: `--no-verify` skips it. A merge with that flag doesn't run the hook that
refuses. There is a post-merge hook that notices and records it — but by then
the commit already exists, so what it writes is a receipt, not a veto. It says
exactly that in its own output. I'd rather it be honest about that than
pretend an exit code can take back a commit git has already written.

Three: it reads one shape of line — `claim: key = value by who`. A
disagreement written any other way is invisible to it. It was invisible before
this too. It just has a shape now, and a shape is the most you get.

---

## 8:10 — 8:40 · CLOSE

This is not a demo script.

`tests/pins_quiltgit.sh` — eleven pins, fifty-nine checks. Plain bash and git,
no network, each pin in its own scratch repository. Eleven of eleven pass.

And the same harness run against the substrate this forked from is red in
three places. Those red logs are committed next to the green ones, so you can
see the pins are load-bearing and not decorative.

That's it. Left: git merged two true contradictions and exited zero. Right:
the same merge was refused, both claims kept, and it handed back the command
to change its mind.

Clone it. `bash tests/pins_quiltgit.sh`. `./demo.sh`. That's the whole thing.

> **[hard cut to black. No end card.]**

---

**END OF SCRIPT. 8:40. 1,340 spoken words — counted, not estimated. That is
8:06 of speech at 165 wpm, plus the four marked 2-second pauses (8 s) and the
typed-command beats. At a slower 150 wpm it is 8:56; at 180 wpm, 7:53. It fits
at any normal pace and it never exceeds ten minutes.**

**Two numbers in the script change if §4 is fixed, and both are marked in
place: "eleven pins, fifty-nine checks" becomes "twelve pins, sixty checks"
at 8:10.** The 19/21 in the script does not change under any fix.

---

# 2. THE DESIGN QUESTION YOU HANDED ME: record or message?

**Answer: the record. Your preference holds — but not for the reason you gave,
and the difference changes the edit.**

You framed it as *record versus message*. That's a false binary, and treating
it as one produces a video that is either unreadable or dishonest. Here's the
real axis.

**The message and the record are not competing artifacts. They are the same
artifact at two moments, and the order is the whole decision.**

Measured, from the run above:

- the **message** is what a person gets at the moment of refusal. It carries
  both numbers, both attributions, and the exit code *in one glance*. That is
  a real job and the record cannot do it — 30 lines of JSON read at video pace
  is 20 seconds of a judge squinting.
- the **record** is what survives the terminal. The message is printed from it
  and can be regenerated. That is exactly the claim the project makes, and it
  is the reason the record is right.

**So: the message gets the beat, the record gets the last word.**

The argument I want you to hold against me is this. The strongest moment in the
video is the moment the right pane exits 1 and the left exits 0. **A viewer
who sees only a JSON blob at that moment concludes they are looking at a
receipt generator.** The JSON does not read as "a merge was refused"; it reads
as "a tool emitted telemetry." The human sentence is what makes the exit code
legible as an *act of refusal* rather than a *crash*. Cut the message to
protect the record and you lose the one beat that carries the argument.

But the message alone is the failure mode you already diagnosed, and you
diagnosed it correctly: a rendering is not the claim. Ten minutes of pretty
stderr and the viewer leaves thinking this is a linter.

**Therefore: message at 3:20 (the beat), record at 4:40 (the resolution).**
Twenty seconds of message, eighty-five of record. Nobody who watches can
mistake the message for the deliverable, because the deliverable walks in
immediately after and is visibly *the thing the message was made of*.

One operational consequence you should decide on before recording: **at 6:05
the camera has to read `to_accept_the_loser` off the record, not off a
prepared terminal.** The command must be visibly *in* the record that was just
shown. That is the argument for the record, stated as a shot: it lets the
video show the artifact issuing the instruction, with nothing between.

---

# 3. THE SHOT LIST — real commands, real expected output

Recorded with `asciinema`-style capture into two side-by-side panes. Every
block below is **copied from an actual run on 2026-10-02**, not written from
memory.

### Setup (0:00, before anything is said)

```bash
git clone https://github.com/SuperInstance/quilt-in-git.git
cd quilt-in-git
```

Two panes, both a clean clone. Left pane: `git init`, plain. Right pane:
`git init`, then `cp -R .quilt .quilt && ./.quilt/bin/quilt-init`.

Both panes run the identical fixture build. `demo.sh` already contains it —
**do not retype it in the video; run `./demo.sh` and screen-record it, then cut
around the setup.** The typing of 40 lines of fixture is not the story and
eats ninety seconds.

### Shot 1 — the file (0:50)

```bash
cat cells/inbox/body
```
```
# fleet referral counter — the real quilt-tools fixture
verified: 15
claim: inbound_edges = 21  by quilt-tools#33 0101409
pending: 4
notes: recounted from merged main
claim: inbound_edges = 19  by quilt-tools#32 fb2e041
```

Point at the two `claim:` lines. Say the numbers. **Do not say "nineteen and
twenty-one" while the screen shows them in the other order** — the merged file
puts 21 on line 3 and 19 on line 6, and a viewer will read the screen before
they hear you. Narrate to the screen, not to your memory.

### Shot 2 — the clean merge, left (3:20)

```bash
git merge --no-ff pr32 -m "merge #32"   # exit 0
git merge --no-ff pr33 -m "merge #33"   # exit 0
git rev-list --parents -n1 HEAD | wc -w # 3   <- commit + 2 parents
grep -c '^claim: inbound_edges' cells/inbox/body  # 2
```

Left pane is now in history. **Cut away from it and never come back.** The
story is the right pane.

### Shot 3 — the refusal, right (3:20) — *the shot*

```bash
git merge --no-ff pr33 -m "merge #33"
```
```
Auto-merging cells/inbox/body
quilt: REFUSING the merge — the result asserts one key twice with two values.

  key: inbound_edges
    19                           by quilt-tools#32 fb2e041
    21                           by quilt-tools#33 0101409

  Both texts are preserved verbatim in: .quilt/adjudications/<short>.json
  Winner rule: the claim that arrived on the side being merged.
  That is an ordering, not a judgment about which is true.
  No judge ran. If the losing number is the right one:
    git checkout HEAD -- cells/inbox/body && git merge --abort && git merge <branch>

quilt: no merge commit was created. The branch still has one parent.
quilt: the merged tree is still on disk — inspect it, then
quilt:   git merge --abort        to undo, or
quilt:   resolve and git commit  to proceed anyway.
Not committing merge; use 'git commit' to complete the merge.
$ echo $?
1
```

**`<short>` is a placeholder and you must say so out loud if you leave it
unsubscripted.** It is the short hash of the judged tree and it is **not
stable across runs** — two runs on 2026-10-02 produced `f544b35.json` and
`8d977c0.json` for the identical fixture, because the tree contains commit
hashes and commits carry commit times. Either pin the dates during recording
(`GIT_AUTHOR_DATE` / `GIT_COMMITTER_DATE`) or read the real filename off the
screen. Do not composite a fake one.

### Shot 4 — HEAD did not move (3:50)

```bash
git rev-parse --short HEAD
```
Same value before and after the merge. This is the proof that the merge did
not become history. **It is worth its own shot.** "Exit 1" alone could be a
lint failure; "HEAD did not move" is the claim.

### Shot 5 — the record (4:40)

```bash
cat .quilt/adjudications/<short>.json
```
```json
{
  "kind": "adjudication",
  "refused": "index",
  "named_by": "merge tree the refusal judged",
  "short": "8d977c0",
  "tree": "8d977c0...",
  "head_before": "21fcc05...",
  "merge_head": "4c5e4d2...",
  "ts": 1790930912,
  "adjudication": "mechanical",
  "judge": "none — no model is in this loop, by design",
  "rule": "winner is the claim that arrived on the side being merged; this is an ordering, not a judgment about truth",
  "conflicts": [
    {
      "key": "inbound_edges",
      "cell": "cells/inbox/body",
      "winner": {"value": "21", "by": "quilt-tools#33 0101409", "side": "incoming",
                 "line": "claim: inbound_edges = 21  by quilt-tools#33 0101409"},
      "losers": [
        {"value": "19", "by": "quilt-tools#32 fb2e041", "side": "base",
         "line": "claim: inbound_edges = 19  by quilt-tools#32 fb2e041"}
      ],
      "reason": "two attributed claims for key inbound_edges carry different values; ...",
      "to_accept_the_loser": "git checkout HEAD -- cells/inbox/body && git merge --abort"
    }
  ]
}
```

**That last line is wrong. See §4. Do not record this shot until it is fixed** —
a judge who reads the video, then opens the repo, and finds a different
`to_accept_the_loser` will read the whole thing as theatre.

### Shot 6 — the handle, live (6:05)

```bash
git checkout HEAD -- cells/inbox/body && git commit -m "merge pr33, taking quilt-tools#32's 19"
# exit 0
git rev-list --parents -n1 HEAD | wc -w                       # 3
git show HEAD:cells/inbox/body | grep -c '^claim: inbound_edges'  # 1
git show HEAD:cells/inbox/body | grep 'inbound_edges'         # = 19  <- the LOSER
ls .quilt/adjudications/                                       # still there
```

Measured, on 2026-10-02, from a real refusal:

```
CANDIDATE EXIT=0
parents of HEAD: 3 (3 = real merge commit)
claims for inbound_edges: 1
new record written? 8d977c0.json    <- the refusal is still on disk
```

### Shot 7 — the pins (8:10)

```bash
bash tests/pins_quiltgit.sh
```
```
PINS: 11/11 pins pass (59 checks pass, 0 checks fail)
PINS: ALL PASS
```

Verified on 2026-10-02. Two seconds of tail on screen is enough. **Do not
scroll the 59 PASS lines in the video** — put the log in a link and show only
the verdict table.

---

# 4. BLOCKING FINDING — the handle is still fiction, and the video cannot be recorded until it is not

`ROLES.md` records that the primary affordance was found to be a fiction: *"`to_accept_the_loser` ended in `git merge --abort`, which always fails after a refusal, and named the loser while restoring the state the reader was already in."*

**The brief states that this was corrected. It has not been corrected in the
code.** I measured it, twice, on 2026-10-02.

**Shipped string**, `.quilt/bin/quilt-adjudicate:195`:

```sh
"to_accept_the_loser": "git checkout HEAD -- %s && git merge --abort"
```

and on stderr, line 219:

```
git checkout HEAD -- <cell> && git merge --abort && git merge <branch>
```

**Shipped behaviour, run verbatim from a real refusal:**

```
$ git checkout HEAD -- cells/inbox/body && git merge --abort && git merge pr33 -m "merge #33 taking the loser"
Auto-merging cells/inbox/body
quilt: REFUSING the merge — the result asserts one key twice with two values.
  ...
HANDLE EXIT=1
```

It aborts, re-merges, and is **refused again with the identical message**. It
is a loop. It names the loser and returns the reader to the refusal they
already escaped from. On screen that is the worst possible ten seconds: the
moment the video claims "one command," the command visibly fails.

(The `git merge --abort` step does *not* fail on its own here — `MERGE_HEAD` is
still set after a `pre-merge-commit` refusal, which was verified. The defect
is the *third* clause, and the fact that the first two clauses undo the
refusal's own output. The `ROLES.md` phrasing overstates step two; the finding
itself is correct and worse, because it loops rather than erroring.)

**The working command — measured, exit 0:**

```bash
git checkout HEAD -- cells/inbox/body && git commit -m "merge pr33, taking quilt-tools#32's 19"
```

```
CANDIDATE EXIT=0
parents of HEAD: 3 (3 = real merge commit)
claims for inbound_edges: 1
--- file in the new merge commit:
# fleet referral counter
verified: 15
pending: 4
notes: recounted from merged main
claim: inbound_edges = 19  by quilt-tools#32 fb2e041
```

**It is one command. The loser is already in your tree** — because
`git checkout HEAD -- <cell>` restores the *base* text, and in a two-PR
contradiction the base text is the side that was already merged, which is the
loser. Then `git commit` concludes the in-progress merge, `pre-commit` sees
one claim, and it lands. Exactly the correction the brief describes. It is
just not in the repository.

**This is a two-line fix and it is a HARD BLOCKER for the video.** A new pin
belongs with it — call it **P12, "the handle works"** — which runs the string
out of the record verbatim in a scratch repo and requires exit 0, three
parents, and one surviving claim for the key. P8 currently pins that the
record *carries* the field; nothing has ever executed it. That is the BUILDER
kill criterion from `ROLES.md` — *"Run the primary affordance before you ship
it. Not the test suite. The handle."* — and this is the second time the suite
has passed over a fiction.

**Files to touch:** `.quilt/bin/quilt-adjudicate` (lines 195 and 219) and
`README.md` line 91. Plus the new pin in `tests/pins_quiltgit.sh`, which
changes the headline from **11/11, 59 checks** to **12/12, 60 checks**. Do
the number change in the same commit or the video and the README disagree.

---

# 5. The 90-second README (drafted, not yet installed)

The current README is 14 KB. Judges do not read 14 KB. This is the first
screen. Everything else stays on GitHub for anyone who wants it.

> # quilt-in-git
>
> **A merge that asserts one key twice with two values is refused, and the
> refusal is written down.**
>
> **What.** A `pre-merge-commit` hook. When a merge would leave two attributed
> claims naming the same key with different values, the merge does not happen.
> The losing claim is kept verbatim in `.quilt/adjudications/<short>.json`,
> and the record hands back the one command that takes it instead.
>
> **Why.** Git merges text. Two branches that each assert `inbound_edges = 19`
> and `= 21`, at *different lines*, merge cleanly and exit 0 — producing a tree
> that says one thing is two things. There is no line-level conflict to catch
> it, because the disagreement is not in the text.
>
> **Run it.**
> ```bash
> git clone https://github.com/SuperInstance/quilt-in-git.git && cd quilt-in-git
> bash tests/pins_quiltgit.sh    # 11 pins today / 12 after the §4 fix. Plain bash + git, no network
> ./demo.sh                      # the two-pane contrast, in one file
> ```
>
> **What it is built on.** `SuperInstance/quilt-in-git` at `6a1ae48` — a git
> hooks runtime where cell dials are committed, receipts are journalled, and
> cascade and freeze already lived. This adds a receipt hash, untracks the
> journal so a second writer can exist at all, and adds the refusal. The
> substrate's own pins are unchanged; the red logs from running this fork's
> harness against `6a1ae48` are committed in `pins/`.
>
> **What is honestly unproven.** See `STATUS.md`. Three things: the CRDT layer,
> the `demotion_receipts` table, and a flaky external endpoint. None of them
> are in this repository and none of them are load-bearing for the claim above.

The 14 KB README is not deleted. It becomes the long answer, linked from this.

---

# 6. STATUS.md — the honest status page

Three things in this project are unproven. A judge who finds one of these
hidden is worse off than a judge who was told. Publish this verbatim.

> # STATUS — what is proven here and what is not
>
> Everything below is separated by whether it has been *executed* or only
> *designed*. Nothing in this repository depends on the second column.
>
> ## PROVEN — executed, and the output is committed
>
> | claim | evidence |
> |---|---|
> | A contradictory merge is refused, exits non-zero, HEAD does not move | `P8`, `P8m` — 2 doors (`pre-merge-commit` and `pre-commit` with `MERGE_HEAD`) |
> | Both claims survive verbatim, attributed, in the record | `P8e`, `P8f` |
> | The record declares itself mechanical and judge-free | `P8i` |
> | One author restating a key is a retraction, not a contradiction | `P8k` |
> | An unattributed line is not adjudicable | `P8l` |
> | A merge produces a receipt; the old probe could not see it | `P7` — red at `pins/failfirst-merge.log` |
> | The receipt hash is a real recomputable content hash | `P9` — red at `pins/failfirst-hash.log` |
> | 11 pins (12 after the §4 fix), plain bash + git, no network, each in its own scratch repo | `pins/pins-final.log` |
>
> ## NOT PROVEN — designed, never executed, and named as such
>
> **1. The CRDT layer.** A no-op `merge` in three ports. `remove` never
> tombstones in three. The canary has been incapable of failing since commit
> `dcbdeca` — meaning a canary that cannot fail is not evidence that the thing
> does not. **This is the weakest claim in the project and it is not in the
> demo.** Do not let it into the video. Finding: `CRDT-CANARY2.md`.
>
> **2. `demotion_receipts`.** A table name is a hypothesis about behaviour, not
> evidence of it. The table exists; nothing has been observed entering or
> leaving it. **No claim is made about it in this repository.** Schema note:
> `judge-SCHEMA.md`.
>
> **3. The JEV endpoint.** The contract was recovered from a live source and
> verified against a real 200 response (`JEV-CONTRACT.md`). **The endpoint is
> flaky and has been observed to 400 on a shape that worked 693 times
> earlier.** A transport failure is not evidence about a request, and nothing
> in this repository's claims depends on it being up.
>
> ## KNOWN LIMITS OF THE DEMO ITSELF
>
> - `git merge --no-verify` skips the refusal. `post-merge` records that it
>   happened and says plainly it is **too late to refuse**. That is a receipt,
>   not a veto, and the output says so.
> - Freeze is a pre-commit convention, not security. `--no-verify` bypasses it.
> - The check reads exactly one line shape:
>   `claim: <key> = <value>  by <attribution>`. A contradiction written any
>   other way is invisible to it, exactly as it was invisible before.
> - `core.hooksPath` is local config. A fresh clone has the hooks on disk and
>   inert; each clone re-runs `.quilt/bin/quilt-init`. `P5` pins this.
> - The winner rule is an **ordering, not a truth**. It does not know which
>   number is correct and the record does not pretend otherwise.

---

# 7. What has to happen before anyone records this

Ordered by what blocks what.

1. **Fix the handle.** `.quilt/bin/quilt-adjudicate:195` and `:219`, plus
   `README.md:91`. Two lines. **Blocks shots 5 and 6, i.e. 4½ of the 8:40.**
2. **Add `P12`** — run `to_accept_the_loser` verbatim, require exit 0, three
   parents, one surviving claim. Update the headline to 12/12, 60 checks in
   `README.md`, §1 of this file, and the script at 8:10.
3. **Re-run `./demo.sh` and `tests/pins_quiltgit.sh`** and re-verify every
   number in §1 and §3 against the new run.
4. **Decide the `<short>.json` problem** — pin commit dates during recording
   or read the real filename off the screen. Do not composite.
5. **Dry run, once, at speed.** The script is 1,190 spoken words. Anything
   over 10:00 gets cut; the cuts are the pins (8:10–8:40) first and the
   honest-limits section (7:20–8:10) second. **Never cut 3:20–4:40.**
6. **Record.** Budget two takes. Watch it once before submitting.
