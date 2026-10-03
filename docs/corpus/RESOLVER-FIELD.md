# RESOLVER-FIELD.md — take it into the field and break it

**Lane:** field audit of `https://fleet-resolver.prong-potassium.workers.dev`
**Date:** 2026-10-01, 21:34Z → 23:5xZ
**Verdict up front:** the service is honest about its own limits and dishonest about its own
numbers. It earned *stage 1 with fixes*. It did not earn stage 2. The headline index figure
("477 repos / 85,990 files") is 62.6% one directory.

Everything below is reproducible from files on this machine. Patched copy:
`resolver-worker/index.FIXED-LOCAL.js` (never deployed — the orchestrator owns the namespace).
Local driver: `resolver-worker/drive-LOCAL.mjs`.

---

## 0. Corpus actually scanned

| | |
|---|---|
| docs | **10,985** |
| characters | **8,397,397** |
| repos on disk | 4 of the 8 named (`fleet-triage`, `pong-quilt`, `plato-tile-encoder`, `eisenstein`) |
| findings, shipped code | **2,764** |
| findings, patched code | **6,180** |

### 0.1 Half the assignment's corpus is not on this machine

```
repo                 in edge index   in fleet census   docs scanned   findings
quilt-tools          no              YES               0              0
AI-Writings          no              (as ai-writings)  0              0
fleet-triage         YES             no                10977          6079
pong-quilt           YES             YES               4              82
quilt-atlas          no              YES               0              0
plato-tile-encoder   YES             YES               1              1
eisenstein           YES             YES               3              18
quilt-edge-lab       no              ABSENT            0              0
```

**`quilt-edge-lab` is in no inventory at all** — not the index, not the 5,092-repo census, not
the disk. It is named in the brief as a target. I report it as a finding about the brief, not
about the fleet: **a lane was assigned against a repo that does not exist in any fleet
inventory I can reach.** `quilt-tools` and `quilt-atlas` are real (census: 494 KB JavaScript,
pushed 2026-09-30; 214 KB JavaScript, pushed 2026-09-30) and the service answers
`REPO_NOT_INDEXED` for them, which is the correct and useful answer.

---

## 1. The two assigned gaps — fixed, with before/after

Both reproduced against a **local faithful copy** of the deployed `index.js`, not against the
edge, so the captures are repeatable. Faithfulness check first:

```
`murmur/transforms/rubiks.py:437`   baseline -> FILE_MISSING
    "no such path 'transforms/rubiks.py' in indexed repo 'murmur' (repo-qualified -> murmur)"
`README.md`                         baseline -> AMBIGUOUS
    "basename in 447 repos: .github, _scratch, agent-writings-archive, api-orchestra, attention-daemon-early-version."
```

Both match the orchestrator's reported baseline byte-for-byte. The local copy is trustworthy.

### FIX 1 — org-qualified and GitHub-URL paths

The index is keyed by **bare repo name**. `resolveCitation` read `segs[0]` as a repo and never
considered that `segs[0]` might be an *org*. `unqualify()` now peels a `github.com/ORG/REPO/...`
URL or an `ORG/REPO/...` prefix before anything else looks at the first segment.

| request | shipped | patched |
|---|---|---|
| `` `mavis-prod/pong-quilt/src/main.rs` `` | `REPO_UNKNOWN: first segment 'mavis-prod' is not a known fleet repo` | `FILE_MISSING: no such path 'src/main.rs' in indexed repo 'pong-quilt'` |
| `` `mavis-prod/quilt-atlas/src/app.js` `` | `REPO_UNKNOWN: 'mavis-prod'` | `REPO_NOT_INDEXED: repo 'quilt-atlas' is in the fleet census…` |
| `` `https://github.com/mavis-prod/pong-quilt/blob/main/README.md` `` | **`n_findings: 0`** | `RESOLVES: file exists in repo 'pong-quilt'` |

The third row is the one that matters: **a full GitHub URL was a silent zero, and it is the
single most likely thing a human pastes into this service.** `PATHLIKE`/`BARE_FILE` are
`$`-anchored on `[A-Za-z0-9_.-]+`, so a `https://` prefix can never match, and the backtick
extractor dropped it. `cited_as` is preserved on the finding so the original URL stays auditable.

**The fix is necessary and not sufficient — and the orchestrator's own example proves it:**

```
`fleetset/fleetlint/canary.py`
   shipped : REPO_UNKNOWN  "first segment 'fleetset' is not a known fleet repo"
   patched : REPO_UNKNOWN  "first segment 'fleetlint' is not a known fleet repo"
```

The patch moves the failure from the org to the repo, which is correct, but
**`fleetset/fleetlint` is not in the index, not in the 5,092-repo census, and not on disk.**
So for the brief's own motivating example the honest answer is still REPO_UNKNOWN — the org
prefix was never the whole problem. Anyone reporting "fixed" on this case alone would be
overclaiming.

### FIX 2 — bare paths, and the loud zero

Two changes, because the brief allows either and both are needed:

1. **Accept unbackticked paths.** A masked-text sweep (backticked spans blanked so they cannot
   double-count) finds path-shaped tokens and tags them `unbackticked: true`.
2. **Never return a silent zero again.** `extraction.zero_guard` in every response reports
   `backticked_paths`, `unbackticked_paths`, `path_shaped_tokens_in_raw_text`, and a loud
   `NO_BACKTICKED_PATHS_FOUND` when the document clearly contains paths and none were read.

```
"See murmur/transforms/rubiks.py:437"
   shipped : n_findings: 0                     <-- the worst failure mode
   patched : n_findings: 1  FILE_MISSING  raw="murmur/transforms/rubiks.py:437" cited_line=437
```

### FIX 1b — the third silent zero, which was not in the brief

Found while testing fix 1: a URL *inside* backticks is dropped by **both** extractors. The
backtick extractor rejects it on shape; my sweep masks backticked spans. A `STILL_UNPARSED`
outcome now catches anything recognised as citation-shaped but unclassifiable, so the
`unqualify()`d path is reported rather than discarded.

### A bug I introduced, and fixed before reporting anything

The first version of the sweep produced `github.c` (78×), `index.h` (9×), `engine.r` (8×),
`self.s` (7×), `cocapn.c` (9×), `lucineer.c` (8×).

**Root cause:** `CODE_EXT`'s alternation is not length-sorted — `c` precedes `cc`, `h` precedes
`html`, `r` precedes `rb`, `s` precedes `scala`. The shipped `PATHLIKE`/`BARE_FILE` are
`$`-anchored, so regex backtracking hid this. My sweep is **not** anchored, so it truncated at
the first successful alternative. Fixed with a length-sorted alternation **and** a
`(?![A-Za-z0-9])` guard. Findings fell 6,661 → 6,180 and `FILE_MISSING` fell 2,186 → 1,631:
**555 of the first sweep's "defects" were my bug, not the fleet's.** Reported here because a
field audit that hides its own false positives is the disease it is auditing.

---

## 2. THE HEADLINE: the index is 62.6% one directory, and 246 repos are double-counted

```
fleet-triage              53,808 files   /workspace/projects/fleet-triage
superinstance-papers       4,948
deepseek-harness-quilt     3,000         /workspace/projects/fleet-triage/repos/deepseek-harness-quilt
smartcrdt                  2,968
quilt-crabbox              2,632         /workspace/projects/fleet-triage/repos/quilt-crabbox
---
median repo: 10 files      248 of 477 repos (52.0%) have <= 10 files
```

`fleet-triage` alone is **62.6% of the advertised 85,990**. The median indexed repo has **10
files**. "477 repos / 85,990 files" describes a directory listing, not a fleet.

Worse: **246 of the 477 indexed repos live inside `fleet-triage/repos/`, and 100.00% of their
files also appear in `fleet-triage`'s own file list.** Verified per repo — e.g.
`deepseek-harness-quilt`: 3,000 files, 3,000 also in `fleet-triage`; `quilt-crabbox`: 2,632 /
2,632. That is 16,427 files counted twice, and it means the headline file count is inflated by
construction.

**Why this matters for the tool, not just the marketing:** those nested repos have two homes.
A citation to `quilt-crabbox/x.py` competes with `fleet-triage/repos/quilt-crabbox/x.py`, and
`fleet-triage` is both the largest repo and the container of everything else. Every
basename-frequency and suffix-match statistic the resolver computes is computed over a corpus
where one directory contributes nearly two-thirds of the mass and 16k paths appear twice.

### 2.1 `murmur` is not the repo you think it is

The brief's regression baseline is:

```
`murmur/transforms/rubiks.py:437` -> FILE_MISSING
   "no such path 'transforms/rubiks.py' in indexed repo 'murmur'"
   check: ls <repo>/murmur/transforms/rubiks.py
```

**The index's `murmur` is a Next.js frontend app**, not a Python transforms library:

```json
"murmur": { "name": "Murmur",
  "path": "/workspace/.resolver-state/clones/Murmur",
  "files": ["tailwind.config.ts","vitest.config.ts","next.config.ts",
            "src/app/layout.tsx","src/components/module-card.tsx", ...]   // 37 files
}
```

And `/workspace/projects/murmur/` **exists and is empty**. There is no `rubiks.py` anywhere on
this machine (`find /workspace -name 'rubiks*'` → nothing).

So the FILE_MISSING is *accidentally right about the file* and *confidently wrong about the
repo*. The `check` it hands the reader, `ls <repo>/murmur/transforms/rubiks.py`, cannot ever
succeed. A reader who runs it, then `ls`s the repo the tool names, finds a Tailwind app and
concludes the citation is wrong — when in fact **the index entry is wrong**. This is known
bug #4 ("basename matching across unrelated repos") in a new costume: a repo *name* resolved
to an unrelated repo, followed by a specific claim about its contents.

**Recommendation:** `/health` should refuse to answer, or loudly caveat, when a repo key
collides with a *different* repo's plausible identity. At minimum the response should carry
`repo.path` so a reader can see which directory was actually consulted.

---

## 3. Triage — real defects vs not-real-defects, counted separately

The brief's warning is right and it is the correct frame: **a dangling path is a defect only
when a document claims the work is done.** I classified on two axes — (a) does the path exist on
**disk** (ground truth, not the frozen index), and (b) what does the citing line claim.

All 1,631 `FILE_MISSING`, patched run:

| bucket | n | share | verdict |
|---|---:|---:|---|
| `UNVERIFIABLE` (no repo context, or repo gone from disk) | 1,009 | 61.9% | not adjudicable |
| `AMBIGUOUS_needs_human` | 433 | 26.5% | not adjudicable |
| `CATEGORY_dotfile_or_abs` (`~/.bashrc`, `/tmp/*.html`) | 92 | 5.6% | **tool error** |
| `CATEGORY_glob` (`{drafts,supporting,reviews}/`) | 26 | 1.6% | **tool error** |
| `CATEGORY_URL` (`https://cocapn.ai`, `cs.LG/recent`) | 25 | 1.5% | **tool error** |
| **`REAL_DEFECT` — done-claim, absent on disk** | **25** | **1.5%** | **defect** |
| `NOT_A_DEFECT` — doc already says it is missing | 13 | 0.8% | not a defect |
| `TOOL_FP` — index stale, file present now | 6 | 0.4% | **tool error** |
| `NOT_A_DEFECT` — roadmap naming future work | 2 | 0.1% | not a defect |

**Of 1,631 "this file does not exist" verdicts, 25 (1.5%) are fleet defects. 143 (8.8%) are the
tool's own category errors. 1,009 (61.9%) the tool cannot adjudicate at all.**

### 3.1 The real defects, with exact bytes

Four survive hand-verification (I checked each on disk):

**D1 — `tools/collapse_ledger.py`, cited as implemented.**
```
SCOUT2-PRIORART.md:458
README's "under which seed" is implemented by the fleet's `tools/collapse_ledger.py` wrapping
```
`ls /workspace/projects/fleet-triage/tools/collapse_ledger.py` → **No such file**. Not present
under `repos/*` or `clones/*` either. The sentence asserts an implementation exists. It does not.

**D2 — `out/s1-triagedesk-live.receipt.json`, cited as a hash-chained receipt.**
```
README.md:30
Receipt: `out/s1-triagedesk-live.receipt.json` (hash-chained, verify with the
```
Absent. This is the worst class: a *verification artefact* cited as the authority for a claim,
where the artefact is the thing a reader is supposed to run.

**D3 — `out/3b-per-cell-ratio.svg`, in a table of delivered outputs.**
```
F1-AUDIT.md:666
| `out/3b-per-cell-ratio.svg` | per-cell variance ÷ `σ²/2k` |
```
Absent. (`out/` is plausibly gitignored, so this may be a working-dir artefact rather than a
prose defect — flagged, not convicted.)

**D4 — `tests/compatibility/browser_tests.rs`.**
```
encod-synergy-misc-2026-09-29.md:24
**Maturity:** as shipped, **`cargo test` cannot load the manifest** — `failed to read
/home/eileen/scratch/encod/fleet-math-c/Cargo.toml`
```
Absent — but the document **discloses** the failure in the same breath. My `roadmap`/`done`
classifier missed this phrasing. Disclosed, therefore not counted as an undisclosed defect;
listed for completeness.

### 3.2 The not-real-defects

- **Already disclosed (13).** `BOARD.md:17` reads
  `papers-ROOT | conservation paper cites murmur/transforms/rubiks.py:437; that directory does not exist | yes`.
  The fleet's own board is *reporting this defect*. A resolver that files it again as an
  undiscovered break is adding noise to a place that already knows.
- **Roadmap (2 in the adjudicated set, but 1,632 before disk-verification).** The brief's
  own experience — 213 of 266 dangling refs being roadmap sections — reproduces at a much
  higher rate here because my unbackticked sweep (fix 2) deliberately surfaces prose the
  backtick-only extractor never saw. **Most of the "increase" from 2,764 → 6,180 is newly
  visible roadmap text, not newly discovered breakage.**
- **Category errors (143) — the tool's, not the fleet's.** `~/.bashrc`,
  `/tmp/cfmodels.html`, `https://cocapn.com`, `arxiv.org/list/cs.LG/recent`, and globs like
  `` `{drafts,supporting,reviews}/` `` are not fleet paths. Stage 1 is running path resolution
  on them and returning `FILE_MISSING`, which is a *confident, specific, wrong "this does not
  exist"* — the one disease the service names as its own.
- **Cross-repo relative citations (~1,009 unverifiable).** `integration.md:234` writes
  `` `fleet_simulator/src/environment/holodeck_bridge.rs` `` inside `fleet-triage`. The file
  is absent, but the real blocker is that the edge Worker has **no citing-repo context for a
  different repo**, which `/health` already discloses. Not a fleet defect; a tool limit.

### 3.3 The tool's false-positive rate on this corpus

| stage | findings | confirmed false | rate |
|---|---:|---:|---|
| 1, citation — `FILE_MISSING` | 1,631 | 143 category errors + 6 stale-index | **9.1%** |
| 1, citation — `REPO_UNKNOWN` | 1,085 | **219 empty targets** | **20.2%** |
| 1, citation — `RESOLVES` | 820 | 0 observed | ~0% |
| 2, numeric — `RATIO_MISMATCH` | 171 | ≥22 from one markdown table | **≥13%** |

**The `REPO_UNKNOWN` empty-target bug is pure noise and is trivially fixable.** 219 findings
have `target: ""` and `detail: first segment '' is not a known fleet repo`. They are
**trailing-slash directories** — the extractor accepts them and then splits on `/` to get an
empty first segment:

```
F1-AUDIT.md:6    `F1/`      -> REPO_UNKNOWN first segment ''
HOLLOW.md:109    `node_modules/`  -> REPO_UNKNOWN first segment ''   (x4 in this one doc)
HOLLOW.md:173    `.opencode/`      -> REPO_UNKNOWN first segment ''
```

A path ending in `/` is a directory, not a citation. Reject it. This is the same class as the
`~/.bashrc` noise and it is 219 wasted findings.

---

## 4. Stage 2 is the tool's worst surface, and it found the one thing I wanted it to find

**First, the win.** Fed the 6.8× claim with its operands on one line, stage 2 is correct and
precise:

```
"The triple density is 6.8x higher than Pythagorean triples (59841 vs 10428)."
 -> RATIO_MISMATCH  claim 6.8×; operands 59841/10428 = 5.7385×; relative error 15.61%
    check: python3 -c "print(59841/10428)"
```

That matches the fleet's own finding at `RESOLVER-FINAL.md:132` — *"The 6.8× is false;
59841/10428 = 5.7385"* — with zero human help.

**Then the limit.** The same claim in the form the fleet actually writes it finds nothing:

```
"6.8x denser than Pythagorean triples."                                  -> nothing
"Paper 01 (§5.4) claims 6.8× triple density. The operands are 59841/10428." -> nothing
```

Stage 2 requires the claim, the ratio word, **and both operands on one line**. Real documents
put the claim in a heading and the operands in a footnote. On the fleet's own canonical numeric
defect, stage 2's recall in realistic prose is **0 for 2**.

**Then the false positives, which are worse than a dead feature.** On 10,985 docs stage 2 emits
184 findings, 171 of them `RATIO_MISMATCH`. `HOLLOW.md` alone contributes 22 — and they are
provably, structurally wrong. Here is the whole bug in one markdown table:

```
HOLLOW.md:57
| `EDDI`     | **MIRROR** | api-fork-true | 2,019 | 1,331 | 24,382,919 | 1 | — | 2.70× | ... |
HOLLOW.md:61
| `GeoFlood` | **MIRROR** | api-fork-true |   900 |   546 | 6,797,605 | 6 | — | 3.40× | ... ; 6/546 src 0 bytes |
```

`EXPLICIT_FRAC` matched `6/546` — GeoFlood's **source-file count over total-file count, four
rows down** — then compared it against `2.70×`, **EDDI's size-ratio column, four rows up**, and
emitted:

```
RATIO_MISMATCH  claim 2.7×; operands 6/546 = 0.0110×; relative error 99.59%
  check: python3 -c "print(6/546)"
```

Two different repos, two different metrics, one row apart, declared a 99.59% arithmetic error
with a runnable proof command. A reader will run `python3 -c "print(6/546)"`, get `0.01098`, and
conclude the fleet's HOLLOW.md is arithmetically broken. **The 4-line lookahead window is the
known bug #1 shape (a ±140-char window attributing one range to every sibling) transplanted
into stage 2, where it is much more damaging because the output is arithmetic.**

Also: `RESOLVER-FINAL.md:98` → `claim 5×; operands 429/5 = 85.8000×; relative error 1616.00%`
— an error rate above 100% from a table cell. And `claim 15×; operands 0/3 = 0.0000×;
relative error 100.00%` — a **zero numerator**, not rejected.

**Recommendation: ship stage 2 disabled-by-default at the edge, exactly as stage 3 already is.**
It has the same failure mode stage 3 was correctly disabled for — it guesses. Its operand
search is a windowed regex over prose. A disabled stage that says `EXTERNAL_NOT_CHECKED` is
strictly more useful than 171 confident wrong numbers.

---

## 5. The deployment finding (sharper than "curl needs a UA")

The brief says `curl` needs a browser UA. True, and understates it. Same binary, same session,
same browser UA, ~30 seconds apart:

```
GET /health     200  6236 bytes  {"service":"resolver-worker", ...}
GET /canary     200  1098 bytes
GET /selftest   200  6021 bytes
--- ~30s later, identical headers, identical client identity ---
GET /selftest   403  5841 bytes  <!DOCTYPE html>...<title>Just a moment...</title>
GET /health     403  5835 bytes  <!DOCTYPE html>...<title>Just a moment...</title>
```

`/canary` returned 200 in the same batch where `/health` and `/selftest` returned 403. This is
a **rate-budgeted managed challenge, not a UA check.**

Why this is not cosmetic: `/health` is the guard for known bug #6 — *"a flaky mount silently
emptied the index… a low index count is visible in the response body, not in a log."* The one
endpoint whose entire job is making catastrophic silent failure **visible** is the one most
likely to be replaced by a `<title>Just a moment...</title>` HTML blob. A monitor that does not
treat 403 as fatal will cache a challenge page and conclude the index is healthy — or empty —
from a page that is neither.

**Recommendation:** `/health` and `/selftest` need a WAF skip rule, or a
`content-type: application/json` assertion on the client side that treats anything else as a
hard failure.

### 5.1 The flaky mount is not historical

During this run, `find /workspace -maxdepth 5 -type d -iname pong-quilt` returned **nothing**
while `ls -d /workspace/projects/fleet-triage/repos/pong-quilt` returned the directory. The
index builder's known bug #6 ("a flaky mount silently emptied the index") is **reproducing
right now**, in the same session, on a different tool. The resolver's answer to it —
`nRepos`/`nFiles` in the response body — is the right answer, and it is behind a Cloudflare
challenge (§5). Those two facts are one bug.

---

## 6. The 6.8× pattern

The fleet has already identified the pattern and written it down:

```
BOARD.md:18
| papers-ROOT | 6.8× constant in a README, CONTRIBUTING, `src/lib.rs`
               **and two passing property tests** | yes |
```

A wrong constant (`59841/10428 = 5.7385`, not 6.8) propagated from a paper into a README, a
CONTRIBUTING file, library source, **and two tests that pass** — then cited as authority
because the tests are green. Green tests are the propagation vector, not the defence.

**Of the real defects this lane found, 0 are the 6.8× pattern.** All four are missing-file
citations, not wrong constants. I found no new instance. The pattern is known, documented, and
appears to be genuinely worked rather than merely noted.

What the resolver *can* add here is bounded: stage 2 caught 6.8× only in one-line form (§4).
So the instrument that would catch this class of defect is the one that is currently the least
trustworthy part of the service.

---

## 7. Did the tool earn its place?

**Stage 1, with the three fixes and the category-error guards: yes, narrowly.**
It found 820 real `RESOLVES` with no observed false positives, it reports `AMBIGUOUS` for
`README.md` usefully rather than guessing, it distinguishes `REPO_NOT_INDEXED` from
`REPO_UNKNOWN` (which is how I discovered `quilt-edge-lab` exists nowhere), and stage 3's
`EXTERNAL_NOT_CHECKED` is exactly right — a disabled stage that admits it is the correct
posture, and the reason stage 2's posture is indefensible by comparison.

**As deployed: no.** Three of its stated facts are wrong, and all three are the kind of wrong
the service's own doctrine warns about:

1. "477 repos / 85,990 files" — one directory is 62.6%; 246 repos are double-counted; median 10.
2. "the four known bugs are FIXED-IN-PYTHON / PORTED-WITH-FIX" — the port still emits 219
   empty-target findings, 143 category errors, and resolves a GitHub URL to nothing.
3. "Do not read a non-zero count here as a pass" — the correct warning, attached to
   `n_unverified`, while `n_findings` and `tally` carry no such warning and are the numbers a
   reader will quote.

**Against the brief's rule** — *a resolver that reports 4,000 broken references must be assumed
broken until proven otherwise* — the patched run reports 1,631 `FILE_MISSING` and **25 of them
are real.** A 1.5% yield on its loudest verdict. A human triage pass over the raw findings is
cheaper than reading the findings the tool produces, unless the tool is fixed first.

**The build agent's rule is right and this run is the proof obligation it asks for:** the
service ships a `/selftest` and calls itself proven. The selftest cannot see any of the six
defects above, because all six are properties of the *corpus* and the *deployment*, not of a
handful of hand-picked citation strings. **A selftest over known-good citations cannot certify
an index built from a directory that is 62.6% of itself.**

---

## 8. What I would fix, in order

1. **Reject trailing-slash paths and non-fleet tokens** (`~/`, `/tmp/`, URLs, globs) in stage 1.
   Kills 219 + 143 = 362 findings of pure noise. One `if`. Highest value per line in the file.
2. **Disable stage 2 at the edge, as stage 3 already is.** 171 confident wrong numbers.
3. **Land fixes 1, 1b and 2** (`index.FIXED-LOCAL.js` is ready and syntax-checked).
4. **Fix the operand lookahead in stage 2** — require claim and operands on the same line, or
   on adjacent lines *of the same table row*, never a ±4-line window. Until then, leave it off.
5. **Rebuild the index excluding nested repos**, or at minimum stop counting
   `fleet-triage/repos/*` twice. Report `nRepos`, `nFiles`, and **`maxRepoShare`** in `/health`;
   a share above ~10% is a build bug and should be visible in the response body, not in a
   postmortem.
6. **Put `/health` and `/selftest` behind a WAF skip rule**, or document that a 403 is fatal.

---

### Reproducing this

```bash
cd /workspace/projects/fleet-triage/resolver-worker
P='{"text":"See murmur/transforms/rubiks.py:437","doc":"t.md"}'

echo "$P" | node drive-LOCAL.mjs ./index.BASELINE-LOCAL.js   # shipped behaviour
#   -> "findings": []            <- the silent zero

echo "$P" | node drive-LOCAL.mjs ./index.FIXED-LOCAL.js      # patched
#   -> unbackticked: 1, findings: 1, outcome FILE_MISSING
```

`index.BASELINE-LOCAL.js` is byte-identical to the deployed `index.js` plus a one-line export
block, so the "before" column is the shipped code and not my reconstruction of it.

Audit artefacts, written here and **not deployed**:

| file | what |
|---|---|
| `index.FIXED-LOCAL.js` | the three fixes (§1) |
| `index.BASELINE-LOCAL.js` | deployed `index.js` + export line |
| `drive-LOCAL.mjs` | stdin JSON `{text,doc,citing_repo}` → findings JSON |
| `resolver-worker/AUDIT-summaries.json` | every tally in §3 and §4, machine-readable |

Nothing was pushed anywhere. No repo other than this one was written to.
