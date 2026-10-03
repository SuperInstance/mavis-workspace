# ORG2.md — the thing the PR queue can't see

**Author:** Organizer lane, iteration 2 · **Date:** 2026-10-01
**Nothing was merged. Nothing was pushed.** All evidence: `projects/fleet-triage/org2/`

---

## 0. First line, as asked

> **68.8 : 1** — direct-to-`main` commits to PR merges, across 268 active repos in the
> last 48 hours. Over 5 days: **10.6 : 1**. Lifetime: **18.6 : 1**.
>
> The low PR count is **not** merge-fast hygiene. It is a queue that is empty because
> 212 of 268 repos landed work with no pull request at all.

**But the method you specified would have told you the opposite.** Counting *merge
commits* and comparing against *merge commits that reference a PR number* gives
**0.22 : 1** — i.e. PRs outnumber direct merges 4-to-1, and your finding threshold
is nowhere near. That number is wrong, and the reason is a blind spot worth more
than the ratio:

```
$ git log --merges        # only commits with >= 2 parents
```

`--merges` cannot see squash merges, fast-forwards, or plain pushes. In this fleet
**93% of everything that lands on `main` has exactly one parent.** The population
you asked me to count is 5% of the population that actually lands. Any fleet-level
ratio computed from merge commits alone is measuring a minority and calling it the
culture. I got 0.22:1 from that method first, and it was the answer I would have
reported if you had not asked for the denominator to be checked.

**Correction to my own first pass:** I initially bucketed 99 merges as
`other_merge` and treated them as noise. They were not noise — they split cleanly
into `Merge branch 'p54' (ioredis 5.11.1→6.0.0)`, `Merge branch 'dependabot/…'`,
and `Merge PR #85: …`, i.e. hand-merges of real PR branches. Reporting a 0.22:1
ratio without noticing that bucket would have been the same error, one level down.

---

## 1. How much work bypasses PRs

**Method.** `git clone --bare --filter=tree:0` (full commit graph, no blobs — 560 KB
for `fleet-murmur`, seconds even for a 3.6 GB repo), then walk
`git log --first-parent` for the default branch and classify every commit by parent
count and subject shape. No API budget consumed.

GitHub mints PR merge commits itself with a fixed subject
(`Merge pull request #N from user/branch`); that shape is the evidence. A squash
merge carries `(#N)`. Anything else with one parent and no `(#N)` is work that
landed without a PR.

| window | direct-to-main | formal PR merges | hand-merged PRs | **ratio** |
|---|---|---|---|---|
| 48 h (≥ 2026-09-29) | **1,582** | 19 | 4 | **68.8 : 1** |
| 5 d (≥ 2026-09-25) | 2,085 | 193 | 4 | **10.6 : 1** |
| lifetime | 9,267 | 462 | 35 | **18.6 : 1** |

### Control: this is authoring, not replaying a tarball

`direct_push` is dominated in most repos by *construction*, and construction is not
bypass. The discriminator is author date vs commit date: a bulk import preserves
original author timestamps; an agent writing into `main` right now mints both.

```
48h, one-parent commits:   fresh_author 1576   replayed_author 9
```

**99.4% fresh.** This is not 5,000 files landing from a tarball. It is agents
committing and pushing, one file per commit, seconds apart:

```
voxelglyph  425b746  the verification layer did not verify the product
            8eb8eec  the 7 pins never executed the product. Now 11 tests...
            ac0022b  the product now RETURNS its result, and its hardcoded
                     absolute path is gone
            16175a3  Merge branch 'pr1'          <- parents: c03c78b 6553863
```

### It is a bifurcation, not a uniform culture

The aggregate hides the shape. Across 268 repos:

| | count |
|---|---|
| repos with **≥1 direct push**, lifetime | **268 / 268** |
| repos with **≥1 formal PR merge**, lifetime | **49 / 268** |
| 48h: direct-only / PR-only / both | **205 / 1 / 7** |
| 48h direct-push concentration | top-8 repos = 1,100 of 1,582 (70%) |

And the repos that *do* use PRs use them properly:

```
pong-quilt      0.11 : 1     71 PR merges vs 8 direct (5d)
quilt-tools     0.11 : 1     28 vs 3
jev-quilt       0.06 : 1     24 vs 3
fleet-murmur    0.14 : 1      7 vs 1
quilt-gpu-lab 129.00 : 1     3 vs 387
fleet-seeds   105.00 : 1     1 vs 105
```

So the real answer to "is the low PR count hygiene or debt?" is: **both, and they do
not talk to each other.** A dozen repos run a disciplined PR queue. ~200 do not open
one. The coordination problem is invisible in the aggregate because the disciplined
repos are the loud ones.

### Your own four merges are in this data

I checked, because you said you did not open a PR for any of them.

| PR | landed as | parents | classification |
|---|---|---|---|
| `fleet-murmur#9` | `f671198` "refusal-ledger R67 currency…" | **1** | `direct_push` — fast-forwarded; **no merge commit exists** |
| `pong-quilt#87` | `4f887f4` "Merge branch 'pr87'" | 2 | `hand_merge_feature` |
| `pong-quilt#88` | `70af7f0` "Merge branch 'pr88'" | 2 | `hand_merge_feature` |
| `voxelglyph#1` | `16175a3` "Merge branch 'pr1'" | 2 | `hand_merge_feature` |

All three merges landed in a **2-second window** at `2026-10-01 01:40:32–34Z`, and
`voxelglyph` then took three more direct pushes on top of its own merge commit.
`fleet-murmur#9` is the worst of the four: with one parent there is no merge commit
at all, so nothing in the repo's history records that a PR was ever reviewed.

---

## 2. Where the debt is

### The one pin I can verify is stale, verified by hand

`fleet-murmur` pins its refusal corpus to `pong-quilt` `d51631e`
(`docs/ietf-kamimura-refusal-events-ledger.md:54`). Against the real repository:

```
pin says:     d51631e   d51631eb35ecd297914370e71a4cc1c1760acec0
              Merge pull request #85 from SuperInstance/playtest-round-67
pong-quilt main head: 70af7f0
first-parent commits since the pin:  2
  70af7f0  2026-10-01T01:40:33  Merge branch 'pr88'
  4f887f4  2026-10-01T01:40:32  Merge branch 'pr87'
```

**The two commits that made the pin stale are precisely the two PRs you merged after
it.** The causal chain you hypothesised is now measured, not inferred: you ordered
`fleet-murmur#9` correctly *by its own rule* (it must land while `d51631e` is head),
and then landing R68/R69 retired that rule. A pin cannot survive the thing it pins.

The superseded pin `52b42b4` is 5 first-parent commits behind.

**Did merging in that order break anything downstream? Yes — 4 of 10 anchors.**
I re-checked every line anchor in the corpus table:

| pinned kind | anchor | at pin | at main | |
|---|---|---|---|---|
| `SAVE/COEV-EMPTY` | index.html:396 | ✓ | line 397 | **stale** |
| `LOAD/COEV-MALFORMED` | index.html:425 | ✓ | line 426 | **stale** |
| `WAL-EXPORT/REFUSED` | index.html:416 | ✓ | line 417 | **stale** |
| `WAL-EXPORT/EMPTY` | index.html:422 | ✓ | line 423 | **stale** |
| `QA-REFUSAL` | index.html:248 | ✓ | ✓ | ok |
| `byo-qpam` | index.html:247 | ✓ | ✓ | ok |
| `SEAL/REFUSED` | prerun.js:144,152,203 | ✓ | ✓ | ok |
| `SEAL/REFUSED` | wal-session.js:185 | ✓ | ✓ | ok |

All ten kinds are still present and unmodified; four line numbers moved by exactly
+1. **This reproduces ORG1's drift measurement independently, and corrects it: the
denominator is 10 anchors, not 7, and 4 of 10 are stale rather than 4 of 7.** The
kinds are fine. The precision is not. `voxelglyph#1` is unrelated to the other three
and breaks nothing.

### The fleet-wide pin census, and the part I will not claim

433 cross-repo SHA pins extracted from 577 recently-pushed repos, every target
confirmed to be a real repo in the census, every sha resolved against a full
(non-shallow) clone.

| verdict | n | what it means |
|---|---|---|
| `BEHIND_HEAD` | **304** | real ancestor, not head — the target has moved |
| `AT_HEAD` | 20 | current |
| `DANGLING` | 94 | sha not found in the named target |

Of the 304 behind-head pins, **286 could be measured on first-parent**: median **7**
merges behind, **78 are 20+ merges behind**, worst is `quilt-gpu-lab` at **321**.

**I am not reporting a count of broken pins, and here is why.** I hand-audited the
DANGLING bucket in the artifacts that matter, and **2 of 2 turned out to be valid
pins that my extractor had bound to the wrong repository:**

- `quilt-tools → git-agent 8d6c31a`. The pin is **correct**: `git-agent` has
  `8d6c31a Merge pull request #4 from SuperInstance/docs/quilt-opcode-provenance`.
  My first probe said DANGLING because the clone directory had been deleted
  underneath a running fetch.
- `quilt-tools → jev-quilt a3feccca`. The pin is **correct**: the real commit is
  `a3feccca89a3b66b9f6031383932376c1b65c2be` in **`quilt-cowboy`**, which is what the
  prose says. My nearest-citation rule bound it to `jev-quilt`, mentioned nearby.
  I then "confirmed" it was broken by grepping 7-character prefixes against an
  8-character needle. Two errors, stacked, both pointing the same way.

I revised the extractor five times (UUID fragments; markdown-table row spanning;
multiple citations per line; hex-shaped English words; nearest-citation binding).
It went 768 → 561 → 474 → 433 extracted pins, and the negative control passed only
at the end. **A DANGLING verdict from a text extractor is not evidence that a pin is
broken — it is evidence that the extractor could not attribute a sha to a repo, and
at this sentence-level precision I cannot separate the two.** Publishing "94 broken
pins" would have been the most quotable number in this report and it would have been
false.

**Which result I produced: small and verified.** One stale pin, ten anchors, one
verified drift chain — all checkable by hand in a minute. Plus a census that
establishes *currency debt* (304 pins behind, 78 of them badly) without claiming
*correctness debt* I cannot support.

---

## 3. The conflict-resolution rule

You have the first half already. Here is the whole rule, the discriminator, and the
control — with the control's blind spot demonstrated rather than described.

### The rule

Two PRs touching one file are one of two things, and it decides whether
concatenation is even a legal operation:

- **ADDITIVE** — each side contributes lines the other lacks. The union is correct.
  Concatenation is correct.
- **COMPETING** — both sides edited *the same slot*: the same line, the same value
  position, a different number in it. There is one slot and two candidate values.
  Concatenation does not "keep both sides"; it emits two values into one slot, which
  in a template literal or a counter silently destroys the file or silently doubles
  a count.

### The discriminator (mechanical, no judgement)

For each conflict hunk, normalise both sides — strip comment chrome and quoting, map
number words to digits, replace every integer with `#` — then align **line by line**:

- both sides have a line at the same index **and** they normalise identically
  → **COMPETING**: one slot, two values;
- otherwise → **ADDITIVE**.

Judging the hunk as a whole is not good enough. Hunk 1 of `referral_graph.pins.mjs`
is a competing number *and* new prose in the same block; a hunk-level verdict throws
away exactly the information you need, which is *which line to re-derive*.

### Applied to `quilt-tools#32` / `#33` — your diagnosis, reproduced

Three files touched by both. Six conflict hunks:

| file | hunk | verdict | the slot |
|---|---|---|---|
| `referral_graph.pins.mjs` | 1 | **COMPETING** | `thirteen VERIFIED edges` vs `fourteen VERIFIED edges` |
| | 2 | **COMPETING** | `v[0].weight === 2 * VERIFIED_WEIGHT` vs `=== 3 * VERIFIED_WEIGHT` |
| | 3 | **COMPETING** | `verified.length === 13` vs `=== 14` |
| | 4 | ADDITIVE | new "FOURTEENTH edge" narrative |
| | 5 | **COMPETING** | `kv('edges','17 — 13 VERIFIED · 4 PENDING')` vs `'18 — 14 …'` |
| `REFERRAL_GRAPH.md` | 1 | ADDITIVE | two distinct "Fourteenth edge" bullets |

Hunk 2 is verbatim the line you described. Note the last row: **additive by form,
competing by claim.** Two PRs can append without conflicting at the diff level and
still contradict each other in the sentence. The discriminator cannot see that. Only
the control can.

### The control — and where it fails

Your proposal: *after resolving, re-derive every pinned number from the merged tree
and assert it equals what the pin says.* I built it and ran it on three candidate
resolutions:

| resolution | rows | VERIFIED | `#32`'s edge | `#33`'s edge | **your control** |
|---|---|---|---|---|---|
| **R1** git's own clean merge | 18 | 14 | **MISSING** | present | **PASS** |
| **R2** union of both PRs | 19 | 15 | present | present | **FAIL** |
| **R3** mechanical keep-both | — | — | — | — | file does not parse |

**The control passes the wrong file and fails the right one.**

And the reason is the finding I did not expect:

```
$ git merge-file -p --diff3 <base> pr32 pr33 experiments/referral_graph.seed.mjs
exit 0        # NO CONFLICT
<<<<<<< count: 0

#32's edge in the output:  0 occurrences
#33's edge in the output:  3 occurrences
```

**`git` reports the seed file as a clean merge and silently drops one of the two
edges the PRs exist to add.** Both PRs append a LINK row at the end of the same
array; git resolves the two insertions as one and discards the other, with no marker
and no exit code. The result parses, passes `node --check`, and satisfies every
numeric pin in the file — because the pins were written by each side for a tree
containing only that side's edge.

`git merge-tree --write-tree` does the same thing: it reports conflicts in the doc and
the pins file, and lists the seed under *Auto-merging*. This is the exact case your
merge is heading into, and it fails **silently** where your mechanical merge failed
**loudly**. Loud is better. This is worse.

### The decision procedure

1. **Merge normally.** Never hand-resolve before the tool has told you the shape.
2. **Classify every hunk** with the normalise-and-align discriminator. Record
   COMPETING slots explicitly — a count of them, not a verdict.
3. **Re-derive** the counts from the merged *data* file, by parsing rows — never from
   the prose, and never by arithmetic on the two sides.
4. **Assert `derived == asserted`** for every pinned number. *(your control)*
5. **Assert set containment** — the missing half:
   > for every file both PRs touched, the set of rows in the merged result must be a
   > **superset** of the rows each side added.

Step 4 is necessary and not sufficient. Counts agree when one side's addition is
lost and the other's replaces it; set containment cannot. **Do step 5 and step 4 in
that order** — 5 catches the loss, 4 catches the arithmetic.

Then: a `git merge-file` exit of 0 is not a merge result. On this fleet, treat "no
conflict" on a file that both PRs *appended to* as a claim to be verified, not a
result to be accepted.

### One thing my own discriminator cannot decide

R2 gives 19 rows / 15 VERIFIED, which matches ORG1's "19 edges / 15 VERIFIED" — so
ORG1 took the union by hand and was right. But the seed on `main` already contains
`fm-honesty-receipts → mw-floor-gate` **twice**, the second copy with no `weight` line.
Rows ≠ edges, and the pins file's own guard
(`new Set(verified.map(r => r.to)).size === 13`) counts distinct **to-nodes**, not
distinct edges, so a duplicated row walks straight past it. Someone who owns the
graph should decide which of the two copies is real before anyone re-derives 15.

---

## 4. The queue has moved

Full census, 5,092 repos, `git ls-remote --refs 'refs/pull/*/merge'`, 0 errors.
**10 open PR merge-refs across 7 repos.** Every verdict re-checked by **ancestry**
against a full commit graph — ref presence is discovery, ancestry is authority.

| repo | PRs | verdict | pairwise |
|---|---|---|---|
| `quilt-pincher` | #12, #13, #14 | all OPEN | **#12↔#13 CONFLICT**, **#13↔#14 CONFLICT**, #12↔#14 clean |
| `quilt-tools` | #32, #33 | OPEN | **CONFLICT** (2 files) |
| `quilt-gpu-lab` | #6 | OPEN, 393 commits | — |
| `quilt-research-canons` | #4 | OPEN, 223 commits | — |
| `Patchwork-experts` | #1 | OPEN, 7 commits | — |
| **`chiaroscuro`** | **#1** | **OPEN, 14 commits, 13 files** | **NEW since ORG1** |
| `pong-quilt` | #88 | **MERGED** — stale merge-ref, exactly as ORG1 found | — |

**Negative control: PASS.** `quilt-tools#32`↔`#33` is re-detected as a conflict from
scratch by a method that was not told about it, in the same two files, with the
same template-literal shape. `fleet-murmur#9` → `pong-quilt#87` is re-detected as
an ordering constraint by the pin census, independently (§2). Both controls fire.

`chiaroscuro#1` touches 13 files (`edge/`, `js/`, `shaders/`, `tools/`, `webgpu.html`)
and **shares no file with any other open PR**. It is independent — but note it is a
14-commit, 13-file PR with no conflict surface at all, which under the §1 measurement
is exactly what a PR that never needed to exist looks like.

**Your four merges, re-checked:**

| PR | ancestry | state |
|---|---|---|
| `fleet-murmur#9` | `pr9` is an ancestor of `main` | **MERGED** — but see §2: it is now stale by exactly the two merges that followed it |
| `pong-quilt#87` | ancestor of `main` | **MERGED** (hand merge) |
| `pong-quilt#88` | ancestor of `main` | **MERGED** (hand merge) |
| `voxelglyph#1` | ancestor of `main` | **MERGED** (hand merge) — unrelated to the others, breaks nothing |

**Nothing downstream broke except the pin you already knew about**, and it broke in
the direction you predicted. The ordering was right. The pin is the cost.

---

## 5. What I could not do, and what I got wrong

**Gaps, stated as gaps:**

- **No PR metadata.** No labels, reviews, or discussion — those are API-only and the
  budget is 60/hr with no token. Every verdict here comes from git objects.
- **7 repos unscanable** for pins (`AI-Writings`, `quilt-gpu-lab`, `lucineer-system`,
  `sunset-ecosystem` truncated as gzip bombs; `datadog-forwarder`, `etcd-client`,
  `multiagent-project-archive` have empty trees). `quilt-gpu-lab` has an open PR **and**
  an acknowledged pin gap.
- **Pin corpus is 577 recently-pushed repos, not 5,092.** Older repos are lower risk
  (a pin in a dormant repo cannot become newly wrong) but they are unscanned.
- **A fast-forwarded PR is invisible to me.** It lands with one parent and no `(#N)`,
  so I count it as a direct push. This inflates the direct side of §1 by an unknown
  amount. I could not measure it without the API, and I am not going to pretend the
  ratio is exact to more than one significant figure.
- **`(#N)` is a convention, not proof.** No API means no authoritative "this PR was
  merged" ledger.

**What I got wrong, in order:**

1. Reported the ratio from merge commits alone (0.22:1) before checking that the
   population was 5% of what lands. That number was wrong by two orders of magnitude
   and in the opposite direction.
2. My first pin extractor bound the target from an adjacent word, so it read
   `SuperInstance/pong-quilt, main d51631e` as a pin on `main`. **The negative control
   caught it.** 399 of 768 extracted pins named a non-repository. Fixed; needed four
   more revisions (UUID fragments, table-row spanning, multiple citations per line,
   hex-shaped English words like `feedbac` and `ed25519`).
3. The pin verifier ran 12 threads against shared clone directories and compared
   ancestry against an unborn `HEAD`, producing 233 false `DANGLING` verdicts.
   Hand-checking one of them is what exposed it.
4. Twice declared a valid pin broken, including an 8-vs-7-character prefix
   comparison. Both were caught by re-running the check, not by confidence.

**The through-line:** every wrong number in this report was produced by a method
whose failure mode was *silent*, and every one was caught by a control that was
*boring* — a hand check against the actual repository. The §3 finding is the same
shape: git reported a clean merge, exit 0, and dropped an edge. The fleet's
characteristic failure mode is not merging in the wrong order. It is **producing an
artifact that is well-formed, checkable, and wrong, and having no instrument that can
say so** — which is why §1 matters: 68.8:1 means the queue cannot be the place where
that gets caught, because the queue is not where the work happens.
