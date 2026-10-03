# Fleet STRUCTURE — the space between 5,113 repos

**Scout 3, cut-edge. Read-only. Nothing pushed.**
Scope: relationships *between* repos. Three prior audits found single-repo
defects (`claw`, `forgemaster`, the `murmur/transforms/rubiks.py:437` citation,
the 6.8× Eisenstein constant). Those are not re-reported here. What follows is
what only becomes visible when the repos are placed next to each other.

---

## 0. The census had to be fixed first, and the brief's number is stale

The brief says **5,127** repositories. The account has **5,113**.

| route | result |
|---|---|
| HTML scrape of `?tab=repositories` (171 pages × 30) | 5,113 unique |
| REST `GET /users/SuperInstance` → `public_repos` | 5,113 |
| prior `census.log` in this workspace | 5,108 (truncated) |
| prior `allrepos.json` in this workspace | 5,113 (correct) |

The scrape carries a self-test that fails loudly on a silently-truncating
census — every page except the last must hold exactly 30 repos, no duplicate
slugs, no empty interior pages. It passed: `short_pages_but_last: []`,
`empty_pages_but_last: []`, `dupes: 0`. The two independent routes agree to
zero, so 5,113 is the real denominator and the brief's 5,127 is 14 repos stale.

**The self-test earned its keep immediately.** The first parser dropped a real
repo: it used a denylist of reserved GitHub routes, and one of those routes is
actually a repo name. `SuperInstance/discussions` exists (API id 1246968664) and
is **unreachable at its own URL**, because `github.com/<owner>/discussions` is
GitHub's discussions page. Its canonical URL serves someone else's route. The
parser was fixed by switching to a positive rule (a repo row is an `<a>` whose
href target equals its own visible text), so nothing can be silently filtered.
`discussions` is the only such collision in the fleet.

### What was measured, and what was not

| population | n | note |
|---|---|---|
| universe | **5,113** | census above |
| forks | **815** | every parent resolved, 1 repo renamed out of census |
| first-party | **4,298** | universe − forks |
| README available | **4,861** (95.1%) | 252 repos have no README |
| last-commit date | **5,052** (98.8%) | commits Atom feed |
| current tree measured | **5,051** | 179 hit the 12 MB cap → **lower bound only** |
| tree errored | 62 | no tree on `main` or `master` |
| unmeasured | 0 | every repo in the census was attempted |

**GitHub's REST `size` field is unusable here and I did not use it.** Measured
across 5,092 repos it saturates at 3.6 MB and totals 0.05 GB — irreconcilable
with `AI-Writings` at 19.7 MB of tree and a 658 MB repo documented in
`ORG.md`. It also counts git *history*, not the current tree. Every byte figure
below comes from streaming the codeload tarball of the default branch, which
measures the working tree and carries each member's exact size in the header.
Totals are therefore **lower bounds** wherever the 12 MB cap applied, and the
cap count (179) is stated rather than absorbed.

---

## 1. Forks: 815 of 5,113, every one of them external, and 73% from one account

**815 forks. Zero internal forks.** No repo in the fleet is a fork of another
repo in the fleet. So "the fleet" is 4,298 independent first-party trees plus
815 inherited ones, and inherited defects are not first-party defects. That
separation is the first structural fact, and it changes what any quality number
over "the fleet" means.

Prior work in this workspace knew **45** fork parents (`fork_parents.json`).
All 815 are now resolved, from the `forked from` banner on each repo's own page
— 815/815 resolved, 0 pages 404, 0 repos flagged as a fork whose page lacked
the banner. That is a 18× completeness improvement, and the 40-repo control
re-fetch confirmed 40/40.

### The fork population is not 815 independent artifacts

| | |
|---|---|
| fork parents resolved | 816 (815 in-census + `claudesclaude`, renamed) |
| distinct upstreams | 816 (one upstream forked twice) |
| distinct upstream *owners* | 195 |
| **`Lucineer`** | **598 of 816 forks = 73.3%** |

One GitHub account accounts for more than two-thirds of the fleet's entire fork
population. Those are not 598 independent adoptions of third-party code; they
are one bulk operation.

### And most of that bloc is not fork work at all

Fork lag (upstream tip date − fork tip date, n=801 paired):

| lag | count | share |
|---|---|---|
| **fork ahead of upstream** | 556 | **69.4%** |
| 0–30 d | 139 | 17.4% |
| 31–180 d | 98 | 12.2% |
| >180 d | 8 | 1.0% |

Forks cannot be ahead of their upstream unless someone committed *to the fork*.
Median lag is −3 days fleet-wide and **−5 days in the `Lucineer` bloc**, where
**86.7% are ahead of upstream**.

The cause is a single batch. **436 of the 596 dated `Lucineer`-bloc forks share
a last-commit date of exactly 2026-04-13.** Reading the HEAD commit of that day:

```
captains-log-academy   (fork of Lucineer/captains-log-academy)
  2026-04-12T17:16:16Z  Lucineer       (the fork point)
  2026-04-13T17:17:02Z  SuperInstance   chore: add MIT license
  2026-04-13T17:17:02Z  SuperInstance   add: tests/test_validator.py
  2026-04-13T17:17:02Z  SuperInstance   add: tests/test_reader.py
```

A 30-repo random sample of that 436 block: **30/30 tip commits authored by
`SuperInstance`, 30/30 subject `chore: add MIT license`.** These are
third-party repositories that the account forked and then stamped with a
mechanical licensing commit, at one identical timestamp, by script.

**The scope is bounded, and I checked the boundary.** The stamp is *not*
fleet-wide. The wider fork population is mixed — a 30-repo sample of
non-`Lucineer` forks gave 13/30 `SuperInstance`-authored tips, 4 further
license adds, several still-upstream-authored, some with genuine local PRs
(`Merge pull request #17 from SuperInstance/fix/cano`), and one commit authored
by `claude`. And `SuperInstance/libgdx` is a direct counter-example: it retains
its upstream **Apache-2.0** LICENSE and was never stamped.

**What I could not establish, and am not claiming:** whether the generated
tests are real. In `captains-log-academy` they are genuinely repo-specific
(I²C register reads, vessel logs, a scoring rubric) — not a template. But
sampling 14 repos from the block, **12 have zero test files at all**. So the
block contributes tree weight and license assertions, and in most members
contributes no tests. I have no evidence of copy-pasted test templates; I also
have no evidence the generated tests were ever run.

---

## 2. The citation graph: 18.5% of it is a copy-pasted footer, and it is not honest about what it points at

4,861 READMEs were parsed for explicit inter-repo references. "Citation" is
tiered, because an unqualified count conflates a hyperlink with a stray word:
**strong** = `github.com/SuperInstance/<slug>` URL or a markdown link to
`<slug>`; **medium** = link-to-path or backticked slug; **weak** = a bare word
equal to a repo name.

**The weak tier was measured and then discarded.** It ranked `agent` (1,859
READMEs), `fleet` (1,724), `tests` (1,529), `state` (1,325), `memory` (753),
`docs` (502) — ordinary English words that happen to be fleet repo names. It
measures nothing. It is not reported as a number anywhere below.

### The top of the ranking is a footer

| strong edges | 6,363 |
|---|---|
| of which boilerplate | **1,175 (18.5%)** |
| READMEs citing ≥1 fleet repo | 1,514 |
| READMEs citing ≥1 **non-boilerplate** repo | 1,369 |

144 READMEs contain a byte-identical 8-item "Related repos" list. It
manufactures the entire top of the inbound ranking:

```
- [⏱️ tminus-dispatcher](https://github.com/SuperInstance/tminus-dispatcher) — Temporal heartbeat for agent coordination
- [🔌 tminus-client](https://github.com/SuperInstance/tminus-client) — Client SDK + CLI
- [🌉 fleet-bridge](https://github.com/SuperInstance/fleet-bridge) — A2A dual-transport com…
- [🎼 symphony-runtime](…/symphony-runtime) — Cognitive orch…
- [🧠 composite-headspace](…/composite-headspace) — Dual-she…
- [📡 i2i-bottle-agent](…/i2i-bottle-agent) — Inter-agent bo…
- [🧮 constraint-tminus-bridge](…/constraint-tminus-bridge)
- [🎻 symphony-orchestrator](…/symphony-orchestrator)
```

8 repos × 144 READMEs = 1,152 edges. **145 of the 1,514 citing repos cite
nothing but this block.** So the honest answer to "do the top-cited repos
deserve it" is: *the top eight do not, and that is a measurement about the
template, not about the repos.*

### Genuine inbound, boilerplate removed

| genuine | raw | repo | what it is |
|---|---|---|---|
| 281 | 281 | **`SuperInstance`** | a repo named exactly like its owner; 229 cite one file, `ARCHITECTURE.md` |
| 148 | 148 | **`AI-Writings`** | prose repo, 1,045 files / 13 code files |
| 90 | 90 | **`OpenConstruct`** | **a fork of `NVIDIA/OpenShell`**, renamed |
| 50 | 50 | `exocortex` | |
| 49 | 49 | `constraint-theory-core` | the crate with the 6.8× Eisenstein constant |
| 47 | 47 | `openconstruct-docs` | documents the renamed fork above |
| 45 | 45 | `flux-runtime` | claims 2,037 Python tests |

The 3rd most-cited repo in the fleet is a renamed NVIDIA fork, and 148
citations point at a repository with 13 source files. The hub is a repo whose
name collides with its owner's.

### 7.6% of inter-repo link occurrences point at nothing

192 distinct `blob`/`tree` link targets, 737 occurrences. Resolved serially
against `github.com` (see §6 for why the first instrument was wrong):

| | targets | occurrences |
|---|---|---|
| alive | 153 | 681 |
| **dead (404)** | **39 (20.3%)** | **56 (7.6%)** |

Concentrated, and concentrated on repos whose *entire* file-link surface is
gone:

| repo | dead occurrences | of total | share |
|---|---|---|---|
| **`hermes-avatar`** | 14 | 14 | **100%** |
| `agent-knowledge` | 7 | 15 | 47% |
| `oracle1-workspace` | 6 | 6 | **100%** |
| `plato-training` | 5 | 5 | **100%** |
| `forgemaster` | 4 | 7 | 57% |
| `constraint-theory-ecosystem` | 3 | 3 | **100%** |

#### `hermes-avatar`: 14 fleet documents describe a subsystem that does not exist

Fresh codeload tarball of `main`. The entire repository:

```
       469  README.md
 2,636,731  screenshots/hermes_multi_monitor_capture.png
     1,729  sensory-blueprints/README.md
     1,835  sensory-blueprints/social_profiles_hermes.md
```

Four files. **99.9% of the repo is one PNG.** No `src/`, no TypeScript, 0 code
files. Yet 14 inter-repo links across the fleet cite
`hermes-avatar/main/src/{perception-log, sounder-detector, perception-midi,
unconscious-sync, reference-frame}.ts`. Every one is a 404. This is the
`murmur/transforms/rubiks.py:437` failure class exactly — and it is
**invisible to a single-repo audit**, because the repo is internally
consistent. It only fails when you follow a citation into it.

### The citation graph is not uniformly dishonest, and the contrast is the point

`SuperInstance/SuperInstance/ARCHITECTURE.md` is the fleet's declared
"Definitive Ecosystem Reference" (v2.0, dated 2026-07-12). It makes
inter-repo claims that are **precisely checkable**, and I checked them:

- All **5** commit SHAs it cites as conformance repairs resolve:
  `plato-engine-block-c@8811a2a`, `@a6505ee`, `plato-engine-block@fbd8642`,
  `@2b1aa49`, `plato-engine-block-zig@0002847` — 5/5 HTTP 200.
- `constraint-theory-core`'s two most specific sub-claims match **exactly**:
  claimed 54 module-coverage tests → `tests/module_coverage_tests.rs` holds 54
  `#[test]`; claimed 30 integration → `tests/integration_tests.rs` holds 30.
  Measured 229 `#[test]` + 66 doc-comment fences against a claimed 262, which
  I **cannot adjudicate** without running `cargo` — doc-tests are not countable
  from a tarball.
- "14,000+ tests" is **not refutable** from file counts. The fleet holds 24,169
  test files (10,465 of them in the first 1,629 repos measured). A test *file*
  is not a test. I am not claiming this claim is false.
- "4,000+ repos" is **true and understated** (5,113).

So: the central document's commit-level claims verify, while the peripheral
README link surface is 7.6% dead. The defect is not in the flagship.

---

## 3. Abandoned lineages: a 2026-08-24 recovery event that left 69 repos behind

This is the reverse-lineage direction — a fleet-wide event, invisible repo by
repo. **69 repos carry a 2026-08-24 recovery stamp:** 59
`recovered-copy-20260824-<name>` and 10 `rc-20260824-NN`. The brief's example
(`WAVE_4_IMPLEMENTATION_GUIDE.md` with no `src/`) is a single-repo shape; this
is the set-level version, and it is larger.

| class | n | evidence |
|---|---|---|
| **empty shells** | **39** | GitHub's own page: *"This repository is empty"*; `size=0KB` |
| has content | 30 | codeload tarball of the default branch |
| — of those, byte-identical duplicates of a live repo | **10** | content-hash confirmed |
| — of those, hijack a former canonical name via 301 | **4** | non-following HTTP client |

### The 39 empty ones are not a failed upload; they are a failed fleet

`recovered-copy-20260824-elephant`, `-hermes-reader`, `-fleet-tts` all report
`default_branch=main`, `size=0KB`, and `pushed_at` within five minutes of each
other on **2026-08-25 03:05–03:09 UTC**. GitHub records repo creation as a push
event, which is why a repo with no commits still has a `pushed_at`. A recovery
sweep created 39 empty repositories in one five-minute window.

### 10 of them are duplicates of repos that never stopped existing

Content-hash confirmed, not inferred from names. The largest:

```
ternary-rom                          245 files  sig=f83f9a093f1e41bd
recovered-copy-20260824-ternary-rom  245 files  sig=f83f9a093f1e41bd   ← identical
```

Others: `recovered-copy-20260824-fleet-memory` ≡ `fleet-memory`,
`-fleet-ensemble` ≡ `fleet-ensemble`, `-elephant-sim-worker` ≡
`elephant-sim-worker`, `-scrap-voice` ≡ `scrap-voice`, `-mist-quilt` ≡
`mist-quilt`, `-operational-fiction` ≡ `operational-fiction`, `-fleet-embed` ≡
`fleet-embed`, `-tap-gamenight` ≡ `tap-gamenight`, `-zeroclaw-dissertation` ≡
`zeroclaw-dissertation`. **The original is still there and still live. These are
redundancy, not recovery.**

### 4 repos lost their canonical name

`Constraint-Theory`, `DigitalTwin-RobotStudio-SmartComponent`, `fishinglog-ai`
and `fleet-weather` were **renamed** into `recovered-copy-20260824-*`; their old
URLs now 301-redirect into the new names.

**A correction to my own first pass, because it changes the severity.** I
initially read the API `size` field as bytes and reported these as "4 bytes of
git objects, empty, data destroyed." The `size` field is **KB**, and the
targets are not empty — `recovered-copy-20260824-fleet-weather` contains four
real files on `master` including a 15,782-byte `src/worker.ts`. **No code was
destroyed.** The real damage is narrower and still real: the project's identity
is gone, and the name that identified it now redirects to a repository whose
name advertises it as a failed recovery.

### Duplicated lineage outside the recovery family

25 `(code_files, code_bytes)` fingerprints are shared by more than one repo,
covering 55 repos. Some are renames; some are **content collisions under
unrelated names**:

- `plato-correlator` ≡ `plato-policy` (3 files, 18.3 KB) — different projects,
  identical bytes
- `fisher-information` ≡ `opcode-canon` (3 files, 4.9 KB)
- **9 repos** in the `fleet-midi-*` family split into two identical-content
  groups: `{looper, morph, prob, rand, sequencer}` and
  `{blend, decode, encode, filter}` — 9 names, 2 blobs
- `memory` and `forgemaster-memory-archive` share 51 code files and 325.8 KB of
  source but have **different** content hashes (194 vs 205 files): copies that
  have since drifted, which is the state that later makes them disagree

---

## 4. Technical debt: 40% of substantial first-party repos have no tests — after correcting my own classifier

First pass said 40.6%. That number was **wrong**, and the reason matters: my
vendor filter excluded `dist/`, `build/`, `target/` but not committed build
output living outside them. The #1 and #2 "largest untested repos" were:

- `Projectionist` — "1,650 KB of source in 31 files" was hashed Vite chunks:
  `level-2/assets/Game-C8_Hw6nO.js.p0.js`. A built site, no source.
- `fleet-static-host` — "1,200 KB in 17 files" was 4.2 MB `.wav` files and PNG
  art. An asset bucket.

So 16 repos were being scored as "large and untested" when they contain no
source at all. I re-measured the whole population (1,084 repos) with two
independent bundle tests — a name test (content-hashed bundles, `*.p0.js` vite
chunks, `*.min.js`, generated roots) and a shape test (a `.js`/`.css` with no
newline in its first 8 KB, or mean line length > 2,000). A file is dropped only
if both agree, so a genuinely dense source file is never lost to a name
heuristic.

| | before fix | after fix |
|---|---|---|
| files dropped as build output | — | 4,998 by name, 262 by shape |
| ranking population (first-party, ≥50 KB real source) | 1,128 | **1,068** |
| population source mass | 437.9 MB | **311.3 MB** |
| **zero test files** | 458 (40.6%) | **427 (40.0%)** |
| untested source mass | 58.0 MB (13.2%) | **47.6 MB (15.3%)** |

The *rate* barely moved and the *mass* moved a lot: 127 MB of the original
"source" was build output. The correct headline is that **47.6 MB of genuine
first-party source — 15.3% of all substantial source in the fleet — sits in 427
repositories with no test file at all.**

### Largest genuine first-party source with zero tests

| source KB | files | tree MB | repo |
|---|---|---|---|
| 1,539.1 | 323 | 2.25 | `SuperInstancecore1` |
| 1,400.7 | 40 | 7.89 | `quilt-murmur` |
| 904.8 | 99 | 3.26 | `constraint-theory-backup` |
| 804.5 | 88 | 1.16 | `quilt-dba` |
| 793.8 | 131 | 2.53 | `pasture-ai` |
| 765.9 | 79 | 1.50 | `quilt-cellular-arch` |
| 739.2 | 71 | 13.71 | `fleet-seeds` |
| 723.8 | 29 | 1.27 | `quilt-jepa` |
| 707.1 | 32 | 0.88 | `flux-os` |
| 696.3 | 45 | 1.20 | `quilt-llvm` |
| 555.5 | 3 | 0.61 | `fleet-dashboard-api` |

`SuperInstancecore1` is verified real: 501 files, 274 `.ts`, genuine modules
(`memory/src/graph.ts` 21 KB, `memory/src/semantic.ts` 18.3 KB), zero tests.
Its name also looks like a typo of "SuperInstance core" — unresolvable from
outside, so flagged rather than asserted.

For contrast, the tested end of the same ranking: `nexus-runtime` 48.4%
test-bytes/code-bytes, `SmartCRDT` 33.2%, `flux-runtime` 27.5%,
`holodeck-studio` 45.3%. **The fleet is bimodal, not uniformly undertested** —
which is a more actionable finding than a single average would have been.

---

## 5. Maintained or accumulated: a 40.9% single-day answer

Last-commit dates for 5,052 dated repos (98.8%):

| bucket | count | share |
|---|---|---|
| ≤30 d | 620 | 12.3% |
| 31–90 d | 2,626 | 52.0% |
| 91–180 d | 1,722 | 34.1% |
| >180 d | 39 | 0.8% |

Ninety-nine percent of the fleet was touched within 180 days, and 1% within a
month. That reads as a healthy fleet and is not one:

- **2,067 repos — 40.9% — share a single last-commit date, 2026-07-12.**
- The **top 10 days hold 75.0%** of all dated repos.
- 2026-07-12 is also the date on `SuperInstance/ARCHITECTURE.md` v2.0.

A single day carrying 41% of the fleet's history is a batch script, not 2,067
maintainers. Combined with §1 (436 forks stamped `chore: add MIT license` on one
day) and §3 (39 empty repos created in a five-minute window), the picture is
consistent: **this fleet is maintained by scheduled automation over a large
corpus, and accumulated by a small number of high-leverage batch events.**

The 39 repos older than 180 days are the interesting minority — they are what
the fleet looks like when nothing automated touches it.

---

## 6. Controls, and the four times a re-run changed my answer

Eight controls, each re-deriving a headline figure by a *different* route.
**Six passed, two failed, and both failures changed published numbers.**

| control | result |
|---|---|
| census size: HTML scrape vs REST `public_repos` | PASS — 5,113 vs 5,113, delta 0 |
| fork flag: re-fetch 40 repo pages for the banner | PASS — 40/40 |
| tree bytes: re-stream the 10 largest repos | PASS — +0.000% |
| no internal forks: every parent owner ≠ SuperInstance | PASS — 0 |
| 4 renamed names, non-following client | PASS — 4/4 × HTTP 301 |
| census contains no 301 rows (no double-counted renames) | PASS — 0/60 |
| **first-party = universe − forks** | **FAIL → fixed** |
| **dead-link rate** | **FAIL → fixed** |

**Control 7 failed.** 5,113 − 816 = 4,297, but 4,298 non-forks. One fork key,
`claudesclaude`, is in the resolved parent map but not in the census: its page
301-redirects, i.e. it was renamed out from under the snapshot the fork list
came from. Corrected figures: **815 forks in census, 4,298 first-party.**

**Control 8 failed, and it was the worst instrument error of the run.** I
checked links with `raw.githubusercontent.com`. That endpoint **returns 404 for
directories**, so every link pointing at a *directory* scored as dead — including
`AI-Writings/main/prose` (53 citers), `quilt/main/packages/sdk`,
`forgemaster/main/docs`, `forgemaster/main/memory`, `fleet-jepa-midi/main/docs`.
Re-measured serially against `github.com`, which serves files and directories
alike: **21 of my 60 "dead" links were live directories.** The dead rate fell
from **19.4% to 7.6% of occurrences** (60→39 dead targets). My first positive
control passed because it checked a *file*, which is the one case both
endpoints agree on — a control that cannot fail with the bug is not a control.

Three further self-corrections, all caught before publication:

1. **Boilerplate detector truncated names.** The emoji prefix `.{0,4}` in the
   link-text regex ate the first characters, capturing `eet-bridge` for
   `fleet-bridge`. The boilerplate set was therefore garbage, removed nothing,
   and the run confidently reported **0.0% boilerplate**. Fixed by capturing the
   slug from the URL, plus a self-test that refuses to run if any captured name
   is not a real fleet repo.
2. **`size` field units.** I read GitHub's `size` as bytes; it is KB. This
   inflated one finding from "destroyed" to "renamed" (§3).
3. **`urlopen` follows redirects**, so the 4-rename test silently found zero
   301s. Re-run with a non-following opener.

**Re-runs that did not change anything:** census size, fork flags, tree bytes
(+0.000% on the 10 largest), no-internal-forks, 4 renames, no 301 rows in the
census.

---

## 7. The three repos that most deserve attention

**1. `hermes-avatar` — because it is the fleet's cleanest inter-repo falsehood.**
The repo is four files, 99.9% of it a screenshot. Fourteen references across the
fleet cite five specific TypeScript modules in a `src/` directory that does not
exist; all 14 are 404. It is 100% dead on its file-link surface, and no
single-repo audit will ever flag it, because the repo is internally consistent.
It is the cheapest possible demonstration that the fleet's failure mode lives in
the edges, not the nodes.

**2. `SuperInstance/SuperInstance` — because it is where every measurement
terminates.** 281 genuine inbound citations, the most-cited repo in the fleet,
and the target of 229 of them is a single file. It is the fleet's declared
"Definitive Ecosystem Reference." Its commit-level claims verify cleanly (5/5
SHAs, and `constraint-theory-core`'s 54 and 30 sub-counts match exactly), which
is why it is trusted — and it is dated 2026-07-12, the same day 2,067 repos were
stamped. It is simultaneously the fleet's most authoritative document and a
snapshot of one automated afternoon. Every claim the fleet publishes about
itself routes through a file that is already ~3 months stale and describes
4,000 repos when there are 5,113.

**3. `SuperInstancecore1` — because it is the largest concentration of untested
genuine source.** 1,539 KB across 323 files, verified real TypeScript
(274 `.ts` files, `memory/src/graph.ts` at 21 KB), **zero test files**. It is
the top of a 427-repo population holding 47.6 MB of first-party source with no
tests at all. The name also appears to be a typo of "SuperInstance core," which
if true means the fleet's own core has a shadow duplicate nobody is tracking.

---

## 8. One sentence

The fleet looks **accumulated and then maintained by script** — 40.9% of its
history is one automated afternoon, 73% of its forks are one bulk operation
stamped with a mechanical license commit, a 2026-08-24 recovery left 39 empty
repos and 4 hijacked names behind, and 7.6% of its cross-references point at
nothing — but its single most-cited document is honest at the commit level,
which is precisely what makes the edges around it worth auditing.

---

### Reproducibility

All instruments, caches and intermediate JSON are under `/tmp/scout3/`
(`census.py`, `forks.py`, `tips.py`, `readmes.py`, `cite.py`, `boiler.py`,
`linkcheck.py`, `trees.py`, `q4fix.py`, `duplines.py`, `recovery.py`,
`forklag.py`, `controls.py`). Raw outputs: `allrepos.txt`,
`fork_parents_full.json`, `tips.json`, `trees/*.json` (5,113),
`citation_decomp.json`, `linkfinal.json`, `recovery.json`, `q4_fixed.json`,
`duplines.json`, `controls.json`.

No repository was pushed to, renamed, or modified. All writes were to
`/tmp/scout3/` and to this file.
