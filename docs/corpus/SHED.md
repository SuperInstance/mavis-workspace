# SHED — what this fleet should stop doing

**Lane: decide what to stop. Stub at T+9min; this is the full pass at T+~35min.**

Every number below is traceable to a file in this directory. Nothing is inferred from stars,
README enthusiasm, or repo descriptions. Where I could not measure, I say so.

**Nothing was deleted. Nothing was pushed. All API access was read-only and, in the event, unavailable.**

---

## 0. The bar I could not meet — stated first, because it gates everything

The brief requires: *"Every deletion proposal needs a user count. Read the API."*

**I have no API access.** Verified, not assumed:

```
$ echo ${#GITHUB_TOKEN}   -> 0
$ which gh                -> not found
$ ls ~/.netrc ~/.git-credentials   -> No such file
```

I then went looking for the counts in this morning's cache. They are not there. `allrepos.json`
is a bare list of 5,113 names. `fleet_meta.json` — the 5,092-repo live sweep, the richest
artifact available — carries `name, pushed_at, size, language, description, topics, fork,
default_branch` and **no** `stargazers_count`, `forks_count`, `subscribers_count`,
`open_issues_count`, and **no** `archived` flag.

**So: this fleet currently has no user count for any repo, in any artifact I can reach.**

This is not a footnote. It means **no deletion in this document is decidable today**, including
the one I recommend. What I can do is make the proposals *auditable the moment a token exists* —
each is backed by a content hash, not by a vibe. That is the difference between a proposal and a
guess, and it is the most this lane can honestly deliver without a token.

**The one command that unblocks the whole lane** (run once, ~50s, 51 pages):

```bash
gh api --paginate /orgs/SuperInstance/repos -f per_page=100 \
  --jq '.[] | {name,archived,disabled,fork,stargazers_count,forks_count,subscribers_count,open_issues_count,pushed_at}' \
  > /workspace/projects/fleet-triage/users.json
```

Until that file exists, §2 is a proposal and not a verdict.

---

## 1. Three of the brief's headline numbers are already false, and two are still in circulation

This is the most expensive finding in the lane, and it is not a deletion.

### 1.1 "5 byte-identical CRDT copies" — **inverted**

`fleet-triage/sprint-CRDT.md` §A.2 measured the `src/lib.rs` bytes of all five by git blob digest.
**Zero of five are byte-identical.** Digests `e972cdae…`, `b57d66db…`, `0ec437162…`, `2e6be8ad…`,
`11d37ed32…`; sha256 all distinct; LOC 57/61/64/78/69. They are five *different* implementations of
five *different* CRDT types.

What **is** identical is scaffolding — `ci.yml`, `.gitignore`, `LICENSE-APACHE`, `LICENSE-MIT` — plus
a 17-line FNV-1a block. **The duplicated bytes carry no science; the science is precisely the part
that differs.** A prior lane read the surface and reported it as the substance, and the claim has
propagated as a load-bearing premise ever since.

### 1.2 "11 of 17 autopublishers have no tests" — **inverted, and the real defect is worse**

`AUTOPUBLISH.md:39-48` shows they *do* have tests: ccc-os 236, cocapn-health 113, cocapn-plato 95,
construct-coordination 39, flux-js 172, flux-runtime **2755**, flux-vm-v3 94, plato-core 78,
quilt-fleet 148, websocket-fabric 321. The real finding is the doc's own words at line 52:

> it was not "no tests" — it was "**tests exist and never run on the release path.**"

Worse, the `untested` signal in `triage.json` (338 of 500 repos) is an **artifact of a bug at
`triage.py:118`** — an `elif` that swallows the case. It is not a measurement of the fleet. It is a
measurement of a typo, and it has been cited as a number.

### 1.3 "13 HOLLOW repos" — **mostly a classifier that cannot tell a spec from a shell**

Of the 13, seven are non-forks with `src=0`. Read their own descriptions:

| repo | blobs | size | its own description |
|---|---|---|---|
| `agent-priming` | 1 | 5 KB | "The Mechanic Doctrine — **a system prompt**" |
| `agent-priming-toolkit` | 1 | 16 KB | "The Agent Priming Toolkit — 4 layers, 3 jobs" |
| `algebra-explorer` | 1 | 7 KB | "An **interactive demo** of the 4-move pipeline" |
| `synesis-agents` | 8 | 24 KB | "Agent **persona specifications**" |
| `synesis-architecture` | 6 | 14 KB | "**architecture specs**" |
| `synesis-research` | 506 | 2.1 MB | "Design research for ~58 planned Rust crates" |
| `brand-assets` / `health` | 37 / 22 | 13 / 37 MB | "brand assets" / "System for monitoring" |

These were bucketed HOLLOW because `language: null` and `src == 0`. **A repo of prose specifications
with no `.rs` files is a document, not a shell.** `synesis-research` is a *plan for 58 crates* — a
plan with no code is a plan doing exactly what a plan does.

**This is the same bug class as §1.2**, and it is the third instance in this directory tonight: a
census that measures the wrong thing, produces a confident number, and gets cited. **A bucket label
from an instrument that cannot distinguish a spec from a stub is not evidence of emptiness.**

> **The general rule this lane turns on: an artifact is not a finding until it has survived one
> attempt to prove it is not the thing it was accused of.** By that standard, 3 of the 4 headline
> numbers I was handed did not survive.

---

## 2. Deletion class A — the 2026-08-24 recovery copies (**56 of 69 recommended**)

This is the one class where the argument is arithmetic rather than judgement.

On 2026-08-24 a fleet-wide recovery operation created **69 repos**, all pushed 2026-08-25:
`recovered-copy-20260824-*` (58) and `rc-20260824-*` (11). **None is a fork** — every one is
first-party, inside this account, not inherited. Combined size 158 MB.

```
recovery copies total : 69
  size == 0 (empty)   : 39     <- nothing to lose; the repo has no content at all
  size  > 0           : 30
    of those, content-PROVEN byte-identical to a live sibling : 17
    of those, unproven — DO NOT DELETE BLIND                  : 13
```

### 2.1 The 39 empty ones — delete, on evidence already held

`size == 0` is GitHub's own API number for repository size. A 0 KB repository is an empty shell.
**There is no content to lose and no provenance to preserve.** This is the "13 files, no consumers"
argument in its strongest possible form: *zero files*.

### 2.2 The 17 proven duplicates — delete, on hash, not on name

Proven via `code_dups.json` → `exact` groups (shared git blob digests, not filename similarity):

| recovery copy | files | byte-identical to |
|---|---|---|
| `rc-20260824-01` | 53 | `fleet-static-host`, `si-papers-new`, `ternary-rom` |
| `recovered-copy-20260824-fleet-jepa-midi` | 23 | `fleet-jepa-midi` |
| `recovered-copy-20260824-fleet-ensemble` | 16 | `fleet-ensemble` |
| `recovered-copy-20260824-fleet-memory` | 15 | `fleet-memory` |
| `recovered-copy-20260824-scrap-quilt` | 11 | `scrap-quilt` |
| `recovered-copy-20260824-elephant-sim-worker` | 8 | `elephant-sim-worker` |
| `recovered-copy-20260824-scrap-voice` | 8 | `scrap-voice` |
| `recovered-copy-20260824-operational-fiction` | 7 | `operational-fiction` |
| `recovered-copy-20260824-mist-quilt` | 6 | `mist-quilt` |
| `recovered-copy-20260824-fleet-embed` | 4 | `fleet-embed` |
| `recovered-copy-20260824-tap-gamenight` | 4 | `tap-gamenight` |
| `…-DigitalTwin-RobotStudio…`, `…-study-smartcomponent` | 2 each | `study-smartcomponent` |
| `…-ideation-games`, `…-mist-lab`, `…-superinstance-ai`, `…-wesley` | 1–2 each | live siblings |

`rc-20260824-01` is worth a second look before it goes: it shares 53 files with **three different**
repos. That is not a copy of one project — it is a repo that absorbed three. It is the single
largest dup-holder in the fleet and deserves a read, not a blind `rm`.

### 2.3 The 13 that must survive until someone looks

`rc-20260824-06`, `…-agent-writings-archive`, `…-captain-console`, `…-fishinglog-ai`,
`…-fleet-weather`, `…-mist-game`, `…-mist-voice`, `…-scrapcraft-world`,
`…-search-superinstance-ai`, `…-si-exocortex-rs`, `…-ternary-experiment`, `…-ternary-rom`,
`…-zeroclaw-dissertation`.

Non-empty, **not** proven identical to anything. Several (`ternary-rom`, `zeroclaw-dissertation`)
carry real mass. **A recovery copy is the one artifact where "it has the same name as a live repo"
is not evidence — the recovery may be the reason the live repo exists.** Verify content before
touching these.

### THE ARGUMENT AGAINST deleting all 69 at once

1. **The name is the only thing that makes them a class.** The `recovered-copy-` prefix is a
   *convention I inferred*, not a guarantee. 13 of 69 are demonstrably not duplicates by hash. If
   the prefix was applied by a script that also caught repos mid-recovery, the class is real; if it
   was applied by hand during an incident, some may hold unique salvage. **Hash, don't trust the
   prefix** — which is why §2.3 exists.
2. **I have no user counts (§0).** Zero, in principle, for a repo named `rc-20260824-01` — but
   "in principle" is not "measured," and someone may have bookmarked one.
3. **Recovery copies are the artifact you want during an incident.** Deleting the only backup is
   how a fleet discovers its backups were the backups. **Archive them, don't delete them** — this
   is the one class where the `archived` flag is the correct instrument and removal is not.

**Recommended action: archive all 69; delete the 39 empty ones only after the 17 hashes are
re-verified against a live pull. This is a proposal. Nothing was executed.**

---

## 3. Duplication that is not insurance

The brief asks which copies are genuine insurance and which are one mistake in N folders. Measured
against content, not names.

### 3.1 Keep the 5 CRDT singletons — they are not duplicates

Per §1.1, zero of five are byte-identical. `crdt-core` is the 709-LOC / 37-test superset dated
2026-07-12; the five singletons are ~60 LOC / 3 tests each, dated **2026-09-30 — 79 days later**.
The singletons are newer, not older, and deleting them to keep the monolith means preferring the
older artifact on age alone.

**The real defect is the canary, and deleting repos would hide it.** `sprint-CRDT.md` §A.3: each
`tests/canary.rs` asserts one FNV-1a constant. The constant is *correct* (independently verified).
But it references no `GCounter`, no `merge`, no convergence law — **the type is never constructed**.
The canary sits on the wrong side of the boundary.

> **Deleting the repos removes the evidence that the CRDT boundary is untested. The instrument is
> the bug report. Do not file the bug report.**

**Correct action: one commit, not five deletions.** Replace the 17-line FNV block in each with a
law test that constructs the type and checks merge commutativity/associativity/idempotence. The
duplication here is *scaffolding*, and scaffolding is a template, not a fleet.

### 3.2 The 24 `fleet-midi-*` repos — this is the real "same mistake in N folders"

All 24 pushed **2026-07-12**. `code_dups.json` shows **8 of them sharing a byte-identical
`lib/go/process.go`**, plus a second exact group of 4 sharing `lib/rust/src/lib.rs`.

| group | n | size | language | note |
|---|---|---|---|---|
| Go `lib/go/process.go` | 8 | 5 KB | Go | byte-identical |
| Rust `lib/rust/src/lib.rs` | 4 | 2,570 KB | Rust | byte-identical |
| Makefile group | 5 | 2,274 KB | Makefile | 2,273/2,274 KB — near-identical |
| `null` group | 4 | 4 KB | — | `delay`/`gliss`/`reverb`/`tremolo`, 4 KB each |

Note the inverse relationship: **the byte-identical ones are the 5 KB stubs, and the 2.5 MB ones
are the substantial repos.** The 8 identical `process.go` files are 5 KB shells. This is the same
shape as the CRDTs — the copies are the cheap parts — but here the copy count is 8, not 5, and the
repo count is 24, not 5.

### 3.3 The 40 MIRROR repos — keep all 40, and here is the argument

**All 40 are forks. So are 45 of the 62 census repos.** A fork is not a maintenance liability:

- No CI runs in it unless you run it. Nothing to keep green.
- No issues to triage. Nobody files against a fork of `libgdx`.
- Upstream keeps developing regardless; the fork is a pointer, not a dependency.
- The provenance — *what we looked at, and when* — is destroyed by deletion and cannot be
  reconstructed from git alone.

Shedding 40 forks saves **zero engineering hours** and costs the record. This is the clearest case
in the fleet where "it would be cleaner" is the entire argument, and the bar explicitly rejects it.
**Keep. Optionally, mark `kind: mirror` (§5) so the census stops re-deriving the fact every census.**

### 3.4 The fleet-level number

- **452 exact byte-identical file groups across 100 repos** (`code_dups.json`); group sizes:
  437 pairs, 5 triples, 5 quads, 1×5, 1×6, 2×7.
- **187 repos sit in near-duplicate clusters of ≥4** (`neardups.json`). Largest: 24 `fleet-midi-*`,
  19 (`active-probe`/`cat-agent`/`collective-inference`/`desire-loop`…), 16 (`cell-doctrine`/
  `opcode-canon`/`substrate-attest`…), 16 more `fleet-midi-*`, 13 `cocapn-*`.
- **3,101 of 5,092 repos (60.9%) sit in just 82 name families** — `ternary-*` (372), `fleet-*` (337),
  `lau-*` (333), `plato-*` (283), `quilt-*` (229), `flux-*` (218), `cuda-*` (143).

The CRDT "5 copies" is real but it is **position ~47 by family size**. The count that is actively
harmful is not 5 — it is 69 recovery copies and 24 `fleet-midi` shells, and neither was named in
the brief.

---

## 4. "Costs more to keep than to rewrite" — and the one class where the answer is *rename*

### 4.1 The 21 `*-early-version` repos: my deletion candidate that I withdrew

17 of 21 were pushed on **the same day, 2026-07-12**. That signature — a bulk snapshot, one day,
`-early-version` suffix — is exactly what "superseded snapshot, safe to delete" looks like.

**I checked for a live counterpart before proposing, and there is none. Zero of 21.**

| | |
|---|---|
| `*-early-version` repos | 21 |
| with a live non-suffixed sibling | **0** |
| are forks | 1 of 21 |

`flux-engine-early-version` has no `flux-engine`. `plato-calibration-early-version` has no
`plato-calibration`. **The suffix is a lie: there is no current version. These are the only copy.**

Had I filed this on the signature alone, I would have destroyed 21 unique artifacts. This is the
exact failure mode the brief's own discipline is designed to catch, and it is why the sibling check
ran before the proposal.

**Correct action: RENAME, do not delete.** 21 renames, zero content risk, and the fleet stops
lying about which of its projects are unfinished. The real cost here is not maintenance — it is
that 21 projects have been permanently stuck in a state they were never going to leave, and the
name is the only thing anyone can see.

### 4.2 The one genuine consolidation: `synesis-*` (3 repos → 1)

`synesis-agents` (8 blobs, 24 KB), `synesis-architecture` (6 blobs, 14 KB), `synesis-research`
(506 blobs, 2.1 MB) — **all pushed 2026-09-22, all one project, all `src=0`, all documents.**

This is the honest "delete and rebuild" case inverted: not a rewrite, a **merge**. Three repos, one
day, one project, zero code. One commit merges them into `synesis` and two repos go. Cost: an
afternoon, mostly prose reorganisation. And note `synesis` **already exists** as a live repo (it
appears in `code_dups.json` with 70 shared files), so this is a merge into a live target, not a
new one.

### 4.3 The distinction the brief asked me not to confuse

| | 90% dead, **has** a user | 90% dead, **no** user |
|---|---|---|
| Action | deprecate, keep serving, add a notice | delete or archive |
| Risk of deleting | **outage for someone real** | none |
| Fleet examples | unknown — **§0 blocks this** | the 39 empty recovery copies |
| What I can say | nothing, honestly | the content is already gone |

**I cannot populate the left column without user counts.** That is the honest state of this lane,
and it is why §2 stops at "propose."

---

## 5. The 16 archived repos — the question I could not answer, and why that matters

The brief asks whether archiving is provenance or a dumping ground. **I could not audit it.**

`census.log` says `live: 5092, archived: 16`. `allrepos.json` (5,113) minus `fleet_meta.json`
(5,092) leaves **22** candidates — neither 16 nor 0. And the diff is **demonstrably contaminated**:
`fleet-triage` itself, an actively-pushed repo I am sitting in, is **absent from the live cache**.
The snapshot predates its own subject. So the 22 cannot be resolved to the 16 offline.

**What I can offer instead is a governance smell, and it is a real one.** There are **18 repos
named `*archive*`** — `SuperInstance-archive`, `ternary-archive`, `tripartite-rs-archive`,
`usemeter-archive`, `quilt-agent-memory-archive`, `model-registry-archive`,
`recovered-copy-20260824-agent-writings-archive`, …

A repo whose name says *archive* is a repo that was retired **by renaming** rather than by the
`archived` flag. Those are different states with different consequences: an archived repo is
excluded from search and read-only; a repo named `-archive` is **fully live, fully public, and
still open to PRs** — which is the opposite of what the name implies to the next reader.

**So the answer to "dumping ground?" is: probably not a dumping ground, but a *third* state nobody
declared.** The fleet has *live*, *archived*, and *named-archive*, and only the first two are
things GitHub knows about. Note also the interactive instruction in the brief — "5,111 open to
PRs" — which is true of the 18 named-archives too. **Either flag them or stop calling them
archives. The name is currently a lie of omission.**

---

## 6. The gate — one precondition, composed with the sibling lane

**The smallest gate that would have prevented the 13 HOLLOW, the untested autopublishers, and the
5 CRDT copies. It is one field.**

> ### A repo declares what it is. The declaration is checked against the tree.
> ```yaml
> # .fleet.yaml, required at creation
> kind: code | document | mirror | data
> ```

| `kind` | precondition | which failure it would have prevented |
|---|---|---|
| `code` | ≥1 test that **executes a symbol from `src/`**, and the release path gates on it | the 5 CRDT copies (canary never constructs the type); the autopublishers (tests exist, never run) |
| `document` | ≥1 prose file; **exempt from `src` counts** | the 13 HOLLOW — 7 of them are documents, and the census mis-bucketed them |
| `mirror` | must be a **fork**, and the upstream is recorded | the 40 MIRRORs; stops a mirror masquerading as first-party work |
| `data` | must carry a schema or manifest | the 39 empty recovery copies |

**Why this composes with the sibling lane instead of competing with it:** `can-fail-ci` already
computes "can this gate ever go red." `kind: code` **consumes that output as its precondition** —
it adds no new measurement, only a classification that routes repos to the right test. The sibling
lane's `fail-open-harness` is the instrument; `kind:` is the label that says which repos the
instrument applies to. **One new field, zero new machinery.**

**The second, smaller gate — the one that actually stops 5,127:**

> **Before creating a repo, check whether its content already exists.**
> `codedup.py` already clones and hashes. Reuse it: hash the new repo's files, compare against the
> fleet, and **refuse creation above a similarity floor.**

This is the only rule that would have stopped the 69 recovery copies, the 24 `fleet-midi` shells,
and the 5 CRDT singletons at the moment of creation. It is also the only rule that scales — every
other check in this document is downstream of a repo existing.

**Together they invert the current economics.** Today: *starting* a repo is free, *keeping* one has
no deadline. The gate makes starting cost one file, and makes the empty/unproven classes
unrepresentable rather than merely detectable.

---

## 7. Summary of proposals — nothing executed

| # | Action | Count | Evidence | Blocked on user count? |
|---|---|---|---|---|
| 1 | Delete (empty) | 39 | `size == 0` from API cache | yes |
| 2 | Delete (proven dup) | 17 | 943 exact blob-digest matches, `code_dups.json` | yes |
| 3 | **Archive, do not delete** | 13 | non-empty, unproven | yes — and don't delete |
| 4 | **Rename** (drop `-early-version`) | 21 | 0/21 have a live sibling | no — rename is safe |
| 5 | **Merge** `synesis-*` → `synesis` | −2 | 3 repos, one day, one project | no — merge is safe |
| 6 | Add law tests to CRDT canaries | 5 | canary never constructs the type | no |
| 7 | Flag the 18 `*archive*` repos | 18 | name/flag state divergence | no |
| 8 | **KEEP** 40 MIRROR forks | 40 | forks; zero maintenance cost | — |
| 9 | **KEEP** 5 CRDT singletons | 5 | 0/5 byte-identical | — |
| 10 | Fix `triage.py:118` | 1 | `elif` breaks a fleet-wide signal | no |

Rows 1–3 are the only deletions, and all three are gated on `users.json`. **Rows 4–7 need no
user count and can proceed this week.**

---

**Maintenance cost per week, and the one change that would cut it most:**
This fleet's weekly cost is not disk (158 MB of recovery copies is nothing) — it is **re-derivation:
40 reports this week, and of the four headline numbers handed to this lane, three were already
falsified in this directory** (the byte-identical CRDTs, the untested autopublishers, the 338-repo
`untested` artifact that is a typo at `triage.py:118`), because no lane could cite a receipt and
every lane re-ran the census from scratch. The single change that cuts it most is **the `.fleet.yaml`
`kind:` field**, because it converts the census from inference into a declaration — it is what would
have stopped a 69-repo recovery dump and a spec repo being reported as a hollow shell, and it is the
cheapest possible answer to "starting a repo has no cost": make every repo state what it is before
it is allowed to exist.
