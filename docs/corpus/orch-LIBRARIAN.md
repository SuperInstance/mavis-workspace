# orch-LIBRARIAN — the index, and what it found

**Lane:** front door / index maintenance. **Not** a content lane.
**Generated:** 2026-10-02T17:12Z · **Machine-readable twin:** `INDEX.librarian.json`
**Regenerate:** `python3 tools/librarian.py --root . --clone <fresh-clone> --out INDEX.librarian.json`

Every number below was computed at run time by `tools/librarian.py`. Nothing is
remembered. If a figure is not in the JSON, it is not in this file.

---

## 0. The answer to the failure you actually observed

You lost a lane to "the document does not exist." It was not the agent. It was this:

| | fresh `git clone` | this working tree |
|---|---:|---:|
| total files | **17** | **73,224** |
| top-level `.md` | **7** | **116** |
| tracked `.md` in `HEAD` | 7 | 24 |

**109 of 116 top-level documents do not exist for an arriving agent.** The
fresh-clone check is the finding, exactly as you predicted. An agent that clones
the repo gets `AGENT-ENTRY.md`, `AGENTS.md`, `HOLLOW.md`, `README-PROPOSAL.md`,
`midi-SURVEY.md`, `naming-DOOR.md`, `orch-SCOREBOARD.md`, `r1-NOENGINE.md`,
`r1-SYNCOPATION.md`, `r1-TYPEFUNC.md`, `r2-NOTBOOK.md`, `tool-SURFACES.md` — and
nothing else. `ORIENTATION.md`, `INDEX.md`, `BOARD.md`, `DOCTRINE.md`,
`AGENT-ENTRY.md`'s entire referenced world: absent.

### The specific claim you asked me to check

> *"it was there, 6,759 bytes, on disk and on `main`"*

The file is `ROLES.md`, 6,759 bytes, on disk. Measured:

```
$ git cat-file -e main:ROLES.md
fatal: path 'ROLES.md' exists on disk, but not in 'main'
$ git cat-file -e origin/main:ROLES.md
fatal: path 'ROLES.md' exists on disk, but not in 'origin/main'
```

**It is on disk. It is not on `main`, and not on `origin/main`.** It is an
untracked file. The belief that it was on `main` is what produced the wrong
reassurance; the agent was right to report it missing *from a clone*, and wrong
only about the working tree. `repos/`, `stubs/`, `readmes/`, `_cache/` are
`.gitignore`d, so the corpus the lanes cite is not distributed at all.

**The fix is one command, and it is yours to make, not mine:** `git add` the
documents. I am not pushing.

---

## 1. Live contradictions: **4**

One claim, four mutually exclusive live statements. Every one is `measured`-adjacent
but none carries a run.

| # | Doc | What it asserts | Status |
|---|---|---|---|
| 1 | `RESOLVER-FINAL.md:18` | `\| BattenSpline \| the router \| 10 \| **0** \|` — 10 hits, 0 in code | **stale** |
| 2 | `BOARD.md:94` | "`BattenSpline` 10 all prose" | **stale** |
| 3 | `INDEX.md:50` | "`BattenSpline` 10 prose" | **stale** |
| 4 | `CLOSE-LOOP.md:234` | "**0 occurrences across all 275 fleet repos.** `BattenSpline` (12)" | **stale** |
| — | `CORRECTION-CONSERVATION.md:15` | "**RETRACTED — 136 code hits, it is real**" | **see below** |
| — | `ORIENTATION.md:46,123` | "`BattenSpline` has 136 code hits and I published that it was [wrong]" | **see below** |

### The correction is itself wrong. I re-measured it.

You retracted "10 prose" toward "**136 code hits, it is real**." I ran it:

```
$ grep -rn "BattenSpline" /workspace/projects/            # all 34 projects
88 hits, 30 distinct files
$ ... filtered to executable code extensions (.py .go .rs .ts .js .cpp .c .h .java .rb)
3 hits — of which:
   2  repos/quilt-llvm/experiments/batten-spike/src/kernel.rs   → BOTH are `//!` doc-comments
   1  fleet-triage/VERIFY-CONSERVATION.md                       → a doc *citing* a filename
```

**Zero executable-code hits of `BattenSpline` in the entire corpus.** Not 10,
not 12, not "0 occurrences", and emphatically **not 136**. All 88 hits trace to a
single paper, `scout-foundational.md`, replicated across 5 archives and
HTML-rendered 3 more times — which is precisely what inflates a naive grep count
to 136 while never once touching code.

The `stale`/`fixed` split in the JSON reports 4 live and 0 repaired because my
detector treats "136 code hits" as the correction. **It is not the correction. It
is a fifth, worse number**, and I have not laundered it into truth. The honest
statement is:

> `BattenSpline` is prose. There are 88 hits, not 10 or 12. The original "10 prose"
> was right in kind and wrong in count; the "136 code hits" correction is wrong in
> kind. `ORIENTATION.md` — the front door — currently carries the wrong one.

This is the finding I would fix first. It is also the second time this session
that a correction to an unverified count became the published claim.

---

## 2. Stale citations: **4** — and the detector that finds them is not the one you asked for

You asked for "anything older than N days." **That detector returns zero and is
worthless here.** Measured age buckets of the 116 top-level documents:

```
older_than_0d: 28     older_than_3d: 0
older_than_1d: 0      older_than_7d: 0
```

Every document in the tree is under three days old, because the tree was
materialised recently. An N-day rule would report a clean corpus on a corpus that
is actively contradicting itself. **mtime measures when a file was last written;
staleness here is a property of what was written *relative to its neighbours*.**

So the detector is **content currency**: a document is stale if it asserts a claim
that a *strictly newer* document explicitly withdrew.

| Stale doc | Cites as current | Corrected by | Superseded by |
|---|---|---|---|
| `RESOLVER-FINAL.md` | `BattenSpline` 10 / 0 | `ORIENTATION.md` | 0.46 d |
| `BOARD.md` | `BattenSpline` 10 all prose | `ORIENTATION.md` | 0.23 d |
| `INDEX.md` | `BattenSpline` 10 prose | `ORIENTATION.md` | 0.10 d |
| `CLOSE-LOOP.md` | 0 occurrences / (12) | `ORIENTATION.md` | 0.02 d |

All four are superseded by a document **less than half a day old**. That is the
humiliation: these did not rot in July, they rotted this morning, and three
documents — `BOARD.md`, `INDEX.md`, `RESOLVER-FINAL.md` — are exactly the
front-door set you rewrite by hand.

The retraction landed in three places (`CORRECTION-CONSERVATION.md`,
`ORIENTATION.md`, `VERIFY-CONSERVATION.md`) and propagated to **zero** of the
four documents that assert the claim. A retraction written in a new file does not
reach the files that repeat the claim. That is the structural gap: **the corpus
has no mechanism that makes a correction cost anything at the citation site.**

---

## 3. Two contradictions I could not confirm — and one detector bug that would have convicted an innocent doc

I am reporting these because you told me to, not because they survived.

**"Diversity of evidence beats diversity of opinion" — NOT a live contradiction.**
You said both statements are still in the tree. Measured: one document mentions
the rule, and it retracts on the next line.

```
DOCTRINE.md:106-108
  I predicted that **diversity of evidence beats diversity of opinion.** It does
  not; the difference is +0.02, inside the noise. **Retracted.**
INDEX.md:42
  | 4 | does a quilt gain independence from evidence or from judges? |
        no. 0.17 vs 0.15, inside the noise | **prediction refuted** |
```

The retraction propagated. **This is the correction working, and I am counting it
as such.** It is pinned in the JSON so it cannot silently return.

**"64-bit hash scored 0.9586" — NOT a live contradiction either.** My first
detector flagged `cf-EMBED.md` as stale. It is not. It reads: *"On a random split
FNV-1a scored 0.9586 and beat the complete board — that is the trap."* That is
the trap being *named correctly*, and every other carrier (`syn-AUDITORS.md:179`,
`syn-HARNESS.md:14`, `ORIENTATION.md:51`, `doctrine-RECHECK.md:138`) pairs it with
the honest `0.5045`. No document asserts 0.9586 as a valid result. **I removed
the rule from the detector rather than publish a defect that does not exist.**

---

## 4. `measured / cited / asserted` — where the tree stands

| Class | Count | Meaning |
|---|---:|---|
| `measured` | **0** | re-executed by this lane, reproducible from the tree |
| `cited` | 0 | a second document repeats it (unverified) |
| `asserted` | **116** | prose claim, no run attached |

**Every one of the 116 top-level documents is `asserted`.** Not one carries a
re-executable receipt. `measured` is empty because the only thing I could
recompute was *counts and kinds*, not the claims themselves.

This is the honest shape of the corpus and I will not dress it up. The
`measured/cited/asserted` convention you maintain in prose is correct, and it is
currently `asserted: 116, measured: 0`. The convention is ahead of the tree.

**Per-entry marking lives in `INDEX.librarian.json`**, every document with
`bytes`, `lines`, `sha256[:16]`, `mtime_utc`, `age_days`, and `in_HEAD` /
`on_disk_but_not_in_HEAD`. An agent reads that one file and knows what exists,
what is distributed, and what is merely claimed.

---

## 5. The tree is mutating while it is indexed

Observed directly, in one lane, inside ~25 minutes:

| | first read | final read |
|---|---|---|
| branch | `r1-jevsampler` | `r2-notebook` |
| commits | 7 | 12 |
| tracked files | 17 | 95 |
| untracked entries | 181 | 178 |
| working-tree files | 73,179 | 73,224 |

Another lane committed five times and checked out a different branch while this
index was being built. **Any count in any hand-written document is stale on the
order of minutes.** The JSON is stamped `generated_utc` for exactly this reason:
read that field before trusting any number in it, and re-run rather than copy.

---

## 6. What I could not verify

Stated plainly, because you asked for it and because a short index with honest
gaps beats a complete one with guesses.

1. **The 136 claim's origin.** I cannot reproduce 136 from any corpus I can see.
   It may have been measured against `org:SuperInstance` on GitHub, or a fuller
   checkout. `repos/` here is 277 repos and `.gitignore`d. **I am reporting 88
   and 0 code hits as what I measured, not as proof 136 is unreachable.** If 136
   came from a corpus I do not have, the correction may be right and my
   measurement wrong. I flag this as genuinely open.
2. **The contradiction detector is a claim ledger, not a semantic model.** It
   detects the two contested claims I encoded plus a generic retraction scan. It
   will not find a contradiction nobody has written down. **4 is a floor, not a
   census.** It caught 4 of the 6 `BattenSpline`-bearing documents; the other two
   (`papers-ROOT.md`, prose-only mention; and `ORIENTATION.md`, which carries both
   the stale and the false correction) are hand-classified.
3. **I did not verify any scientific claim** — n_eff, the 0.9586 trap, the
   conservation law, the 91/74 MIDI census. I indexed them. I did not re-run them.
4. **I did not test `lau-git-render`.** You said it has been switched off since
   June. I found it absent from this tree and did not go looking. **If the front
   door is to be rendered rather than read, that is the unstarted work**, and it
   depends on §0 being fixed first — there is nothing to render for 109 of 116
   documents.
5. **Subdirectory corpora (`org2/` 25,608 files, `org_scratch/` 8,554,
   `readmes/` 4,836) are not indexed.** They are inside `.gitignore`d territory
   and out of scope for this stub.
6. **`mtime` here is not trustworthy as authorship time.** Files were clearly
   copied or regenerated. Every age figure in the JSON is "last write," not
   "when the thinking happened."

---

## 7. Recommended order, cheapest first

1. `git add` the documents. Until then every other fix is invisible to a
   fresh clone, and every round repeats your missing-file incident.
2. Fix the five `BattenSpline` numbers to the measured `88 hits / 30 files /
   0 code hits`, front door first. `ORIENTATION.md` currently carries the wrong
   correction.
3. Put the retraction **at the citation sites** — `BOARD.md:94`,
   `INDEX.md:50`, `RESOLVER-FINAL.md:18`, `CLOSE-LOOP.md:234` — or re-run
   `tools/librarian.py` and let the detector report them until they are gone.
4. Turn on `lau-git-render` only after (1). Rendering 7 of 116 documents is not a
   front door.

---

## Bottom line

- **Live contradictions: 4.** All four are the same claim, in four documents,
  mutually inconsistent, and the published correction to it is a fifth
  inconsistency.
- **Stale citations: 4.** All four superseded by a document under 12 hours old.
- **`measured`: 0. `asserted`: 116.** The convention is right; the tree has not
  caught up.
- **The missing-file bug is not an agent bug.** It is 109 of 116 documents
  absent from a fresh clone, and `ROLES.md` on disk but on no branch at all.
