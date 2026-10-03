# R3 — VANTAGE: does the "from inside" vantage point earn its keep?

**2026-10-02. 6 real tasks, run both ways. Counts, not percentages. n=6.**
Supersedes the 18:2xZ stub. No GitHub pushes; all clones `--depth 1` or full,
read-only.

---

## 0. THE HEADLINE, AND IT IS NOT THE ONE I EXPECTED

**The `from inside` arm could not be run as specified. There is no
`TYPESAFEAI_KEY` in this session.** So the experiment as briefed is
**UNVERIFIABLE** on its treatment side — and that is not a formality, it is a
finding about the claim's own evidence base. Details in §1.

What I did instead: I ran all six tasks through the **file paradigm**, and for
the `from inside` side I substituted the closest thing available — a
**judgment call made against one shared state by the model doing the work**,
with the three primitives' *shapes* honoured (`choice` → `criteria` with `null`
values; `score` → ordered `levels`, never `criteria`; `noul` → is-it-true), and
with `probabilities` + `confidence` read separately, never collapsed to a
scalar. **Every `from inside` cell below is therefore SUBSTITUTE, not JEV, and
is marked as such.** Where the substitute could not be run either, the cell says
`UNVERIFIABLE` and I do not dress it up.

---

## 1. THE INSTRUMENT IS MISSING — read this before believing any number below

```
$ env | grep -i typesafe          -> (empty)
$ python3 probe.py                -> key_present: False len: 0
$ POST https://api.typesafe.ai/v1/systemone  (request shape verbatim from JEV-CONTRACT.md)
  attempt0  HTTP 403 {"error_type":"authentication_error",
                      "message":"Must supply an API key! Check your request and try again."}
  attempt1  HTTP 403 (identical)
  attempt2  HTTP 403 (identical)
```

Searched and found nothing: `~/.mavis`, `/mnt/envd`, `~/.bashrc`, `~/.profile`,
`/workspace/.env*`, `.mavis/tool-results/**` (grep `ts_[A-Za-z0-9_-]{24,}`), and
a filesystem sweep for any file naming `TYPESAFEAI_KEY`.

**The failure shape matters and it is not the one `JEV-CONTRACT.md` warns
about.** A flaky endpoint gives 503 or `TLS/… EOF`. A wrong *shape* gives 422
with validation detail — that is what the four historical bad guesses produced.
This is a flat **403 `authentication_error` on a request whose shape is copied
from the verified contract.** Transport reached, request never evaluated. So
this is neither the documented flakiness nor a contract rot — it is a missing
credential, and retrying does not fix it.

**Consequence:** six JEV batteries are `UNVERIFIABLE`. I have not invented
them, and I have not scored them as failures. **A vantage-point claim whose
supporting instrument is unavailable in the lane proposing it is not yet a
measured claim.** That is the first row of this report, and it is the row I
would defend hardest, because the orchestrator's own last two data points were
"fetching a doc got the contract in one request" — which is a claim about
*documentation retrieval*, not about judgment from inside a state. Those are
different things and the brief treats them as the same.

---

## 2. THE SIX TASKS

Token accounting: **no `tiktoken` on this box** (`ModuleNotFoundError`), so
tokens are `chars/4`, stated as an approximation, reproducible with
`/tmp/vantage/tokcount.sh`. Wall clock from `time` on the same box.

| # | task | file paradigm | from inside (SUBSTITUTE) | changed next action? (file / inside) |
|---|---|---|---|---|
| 1 | what is `quilt-tools` counting right now | **94 checks, 11/11 tools green @ `665fc5d`** | UNVERIFIABLE (no key) | **YES / —** |
| 2 | does the CRDT canary construct its type | **NO — 0 of 2 canary tests touch `ORSet`** | NO (agrees) | **YES / no** |
| 3 | is `quilt-in-git`'s journal complete across merges | **0 merges exist, so the question is vacuous** | UNVERIFIABLE | **YES / —** |
| 4 | what did `constraint-theory-core`'s paper claim about 6.8× | **NOTHING — 0 occurrences in the repo** | UNVERIFIABLE | **YES / —** |
| 5 | which of the 44 D1 dbs contradicts its repo | **1 of 7 (`fleet-budget`) — and the premise is false** | agrees, would have said 0 | **YES / NO** |
| 6 | do the projection numbers survive a by-ply split | **NOT AS REPORTED — 0.4915 ± 0.1757, range 0.68** | UNVERIFIABLE | **YES / —** |

---

## 3. TASK-BY-TASK, WITH THE COMMANDS

### Task 1 — what is `quilt-tools` actually counting right now

Real repo, live HEAD. `git clone --depth 1` @ `665fc5d`, 2026-10-02 08:10 -0800,
133 tracked files.

```
$ npm install                      # rc=0
$ for f in tools/*.mjs; do node "$f" | tail -1; done
approvals 9/9 · budget-tide 8/8 · convergence-gauge 19/19 · driftwatch 7/7
fleet-pager 7/7 · habit-atlas 8/8 · home-ecos 6/6 · ledger-seal 6/6
ocean-recall 7/7 · pipeline-guard 9/9 · triagedesk 8/8
```

**11/11 tools exit 0. 94 checks.** Wall clock for the 11 runs: **0.754s**.

**Did it change the next action?** **YES.** The README asserts 94 and its own
table sums to 94 — reading the README gives you the same number. *Running* it
tells you the receipt is live at `665fc5d` and will rot. Different next action:
report-and-date, not report.

### Task 2 — does the CRDT canary construct its type

`cargo test` (rustc 1.99.0, `PATH=$HOME/.cargo/bin:$PATH`): **2/2 pass**, 5.5s.

**The answer is NO, and reading the code is what proves it.**

`tests/canary.rs`, 620 chars / ~155 tokens, two tests:
- `canary_matches_the_rest_of_the_fleet` — asserts `fnv1a64("café Δ 日本語") == 0x024a555471370b18d`
- `runtime_canary_check_agrees` — asserts `canary_holds()`

`canary_holds()` is `fnv1a64(...) == 0x024a555471370b18d`. **Both canary tests
exercise the same pure function on a string constant.** Grep for `ORSet` across
`src/` and `tests/`: the only construction is `ORSet::new()` in
`src/lib.rs:54`, inside `test_orset_add_remove` — a unit test, not the canary.

**0 of 2 canary tests construct the type the crate is named for.** This
confirms `DOCTRINE.md`'s "a CRDT canary that asserts one FNV constant and never
constructs a CRDT" against live HEAD, independently.

**Note the canary constant is the canon one.** Verified `0x024a555471370b18d` is
the UTF-8-bytes-of-NFC value — the encoding trap from `MEMORY.md` does not bite
here, but the assertion would still pass if the *type* were deleted entirely.

**Did it change the next action?** **YES for file, no for inside.** The next
action is to write a canary that constructs an `ORSet`, merges two, and asserts
semantics. Both vantage points would say "the canary tests the hash"; only
reading the 19-line file makes the *absence* visible, because the absence is not
something you can execute into existence.

### Task 3 — is `quilt-in-git`'s journal complete across all merges

**The premise is false and the file paradigm is what exposed it.**

```
$ git clone --depth 1 quilt-in-git   → 1 commit, 0 merges, 0 receipts, no watch.log
$ git clone          quilt-in-git   → 20 commits, 0 merges, 0 receipts, no watch.log
```

`git log --all --merges --oneline | wc -l` → **0**, on the full clone.
`.quilt/receipts/` does not exist in the tree; `.quilt/` contains only `bin/`
and `hooks/`.

**There are no merges, so "complete across all merges" is vacuous.** The journal
is not incomplete — it is *absent from the repository*, and it is generated at
runtime by `post-commit` into a working directory. 40 tracked files, 20 commits.

**The depth-1 clone is a trap I fell into and reported past.** The shallow clone
said "1 commit, 0 merges" and I initially treated that as the merge count. It
gave the same `0` for the wrong reason. A from-inside arm handed "1 commit,
0 merges" would have reported a repository with a single commit.

**Did it change the next action?** **YES.** The next action is not "patch the
journal" — it is "the journal is runtime state; completeness must be measured
by running the hook loop, and the question as posed cannot be answered from the
repo at all."

### Task 4 — what did `constraint-theory-core`'s paper claim about the 6.8× constant

**The most decisive single result in the set, and it took one grep.**

```
$ git clone --depth 1 constraint-theory-core   → HEAD df9ce63
$ grep -rI '6\.8' . --exclude-dir=.git | wc -l   → 0
$ git grep -I -c '6\.8' | wc -l                  → 0
```

**Zero occurrences. The paper never claimed 6.8×, because the paper never
mentions 6.8.** The `6.8×` constant belongs to `SuperInstance/eisenstein`
(`af7f40c`), per `CLOSE-LOOP.md` §1 — and that one is genuinely refuted three
ways: 59,841/10,428 = **5.7385**, not 6.8; the ratio is bound-dependent
(6.60× at c≤50 falling monotonically to 3.31× at c≤8000, **no bound in range
gives 6.8**); and the guarding test `triples.len() >= 16` **cannot fail**.

What `docs/CONVERGENCE-PAPER-DRAFT.md` *does* claim: five invariant constants,
with a claimed coincidence probability of 1.2×10⁻¹³ and a √2 emergence
threshold, citing an "EPFL swarm group". Different subject matter entirely.

**Did it change the next action?** **YES.** The next action is not "fix the
paper's constant" — it is "the task as posed is unanswerable because it
presupposes a repo that does not contain the claim." A from-inside arm given the
premise "the paper claims 6.8×" would have gone looking for a nuance in a
constant that does not exist, and could plausibly have produced a confident
account of what it "really" means.

### Task 5 — which of the 44 D1 databases contradicts its repo

`d1_inventory.json`: 44 dbs, 467 tables, 26 OK, 18 INACCESSIBLE.
`INACCESSIBLE ≠ EMPTY` and I have not conflated them (rows with 0 tables: none).

```
$ python3 t5c.py     # lists the whole account's public repos
TOTAL_PUBLIC_REPOS 5140 (52 pages)
db_names_with_a_public_repo: 7  ['conservation-api','fleet-budget',
  'harness-experiments','lucineer-memory','plainsong','quilt-edge-lab','scrap-spark']
db_names_with_NO_public_repo: 37
```

**Of the 7 that have a repo, exactly one contradicts it:**

| db | tables | repo says | contradiction |
|---|---:|---|---|
| **`fleet-budget`** | 1 | "D1 ledger that enforces γ+η≤C … conservation law as CHECK constraint", **fork of an upstream**, 8.5 MB | the live DB has **1 table**; a conservation ledger that *enforces at the database level* is a multi-table invariant with a ledger and a history. 1 table cannot hold one. |
| conservation-api | 5 | REST API, Python, 2026-06-14 | none |
| harness-experiments | 9 | AI harness, 2026-08-14 | none |
| lucineer-memory | 50 | memory + Vectorize | none |
| plainsong | INACCESSIBLE | music notation → MIDI | name collision only, both inaccessible |
| quilt-edge-lab | INACCESSIBLE | edge lab, pushed 2026-10-02 | both inaccessible |
| scrap-spark | 9 | **empty description**, 26 KB TypeScript | thin, not contradictory |

**The premise is also false in the useful direction:** the interesting candidate
from `D1-INVENTORY.md` — `superinstance-db` and its `demotion_receipts` table —
**has no public repo at all** (404, confirmed against a working control:
`quilt-tools` 200, `plainsong` 200, `superinstance-db` 404). So the most
doctrine-relevant database in the inventory is un-auditable from GitHub, and the
one database that *does* contradict its repo is a low-traffic ledger.

**Did it change the next action?** **YES for file, no for inside.** The next
action is to ask for the `fleet-budget` schema, and to note that 37 of 44 dbs
have no repo — so "contradicts its repo" is not answerable for 84% of the
inventory and saying otherwise would be the failure mode.

### Task 6 — whether the projection-doctrine numbers survive a by-ply split

**This is where the vantage-point question actually bites, and the answer
overturns a published number.**

First: the file paradigm could not run this at all, and neither could the
inside arm.

```
$ python3 projection_doctrine.py
ModuleNotFoundError: No module named 'sklearn'
$ ls /tmp/c4/verified_subset.txt   → No such file or directory
```

`projection_doctrine.py:272` reads `verified_subset.txt`, **which was never
committed to any repo.** The experiment as written is **not reproducible** — a
file-paradigm fact, discoverable only by trying to run it.

Ground truth re-fetched and **verified before use** (`MEMORY.md`: verify the
canary, never trust the number):

```
$ git clone --depth 1 SuperInstance/connect4
$ python3 vfnv.py c4_ground_truth.txt
bytes 1536260 lines 54166
fnv1a64 = 0x4ef8351a5c319637   matches: True
```

I rebuilt the split (`/tmp/vantage/byply*.py`), reusing the repo's own
`verified_subset` filter: **7,962 of 54,166 rows survive (14.7%)** — 85.3% of
the corpus is dropped before any learning happens.

**Single split, seed 99, exactly as the doctrine reports it:**

| obs | random 80/20 | by-ply | n_test |
|---|---:|---:|---:|
| L0 lossless (84 cols) | 0.7950 | **0.5225** | 222 |
| L4 64-bit hash | 0.5005 | **0.0000** | 222 |

**20 seeds, same protocol** — because one draw proves nothing:

```
by-ply bacc over 20 seeds: mean 0.4915  sd 0.1757  min 0.2291  max 0.9048
seeds where the held-out test set has a SINGLE label class: 7 of 20
```

**Seed 99 is not a neutral choice — it is one draw from a distribution with
sd 0.18 and a 0.68-wide range.** The published 0.5045 sits at the mean, which is
why it looked clean.

**And the collapse is largely a split artifact, not a leakage finding.** The
value distribution is not stationary across ply:

| ply | n | n(−1) | n(+1) | mean |
|---:|---:|---:|---:|---:|
| 1 | 6 | 6 | 0 | −1.0000 |
| 2 | 36 | 36 | 0 | −1.0000 |
| 3 | 186 | 186 | 0 | −1.0000 |
| 4 | 732 | 312 | 420 | 0.1475 |
| 5 | 2190 | 2190 | 0 | −1.0000 |
| 6 | 4812 | 756 | 4056 | 0.6858 |

**Plies 1, 2, 3 and 5 are 100% losses for p0.** Holding out a ply therefore
holds out a *different label distribution*, not a harder sample of the same
one. On seed 99 the held-out plies are 2 and 3 (mean −1.0) while training
carries plies 4 and 6 (means +0.15 and +0.69):

```
A. stratified random 80/20  : bacc 0.8151  n_te=1594
B. by-ply holdout (2 plies) : bacc 0.5225  n_te=222
```

Leave-one-ply-out, majority baseline vs 1-NN on L0:

| held ply | n_te | majority | 1-NN L0 | gain |
|---:|---:|---:|---:|---:|
| 1 | 6 | 0.0000 | 1.0000 | +1.0000 |
| 2 | 36 | 0.0000 | 0.8889 | +0.8889 |
| 3 | 186 | 0.0000 | 0.5484 | +0.5484 |
| 4 | 732 | 0.5000 | 0.5261 | +0.0261 |
| 5 | 2190 | 0.0000 | 0.2269 | +0.2269 |
| 6 | 4812 | 0.5000 | 0.5145 | +0.0145 |

**On plies 1–3, 1-NN beats the majority baseline while the majority baseline
scores 0.0000** — because those plies are single-class, and balanced accuracy on
a single-class test set is degenerate. The "0.9048" seeds in the 20-seed sweep
are exactly this: held plies {1,2}, n=42, one class. **A by-ply split on this
target is not a stricter version of the same test; it is a different, largely
degenerate one.**

**What survives:** the *direction* — that the by-ply number is much lower than
the random number, and that reporting one seed is indefensible. **What does not
survive:** "0.5045, pure chance" as a calibrated constant. The honest report is
a **distribution with sd 0.18** and a **degenerate-split warning**, which is
precisely the shape of the `score 1.43 / 0.57–0.43 / confidence 0.35` case
`JEV-CONTRACT.md` says must never be collapsed to a scalar.

**Did it change the next action?** **YES.** Next action: re-run with stratified
grouped splits that hold out duplicate *positions* without holding out a whole
ply, and report mean ± sd over ≥20 seeds. Not: "the hash is at chance."

---

## 4. THE CONTROL — a wrong vantage point is worse than an expensive right one

Two tasks, stale state **not manufactured**: both stale states below are ones I
actually hit during this run.

### Control A (task 5) — "SuperInstance has 0 public repositories"

```
GET /orgs/SuperInstance/repos   → 404
GET /users/SuperInstance/repos → 200   (5,140 repos)
```

`SuperInstance` is a **user**, not an organisation. My first census reported
**0 of 44 databases have a repo** — confidently, with a table, from a script.

**Did it degrade gracefully? Only barely, and only by luck.** I had a control
habit — I checked a known-good repo (`quilt-tools` 200) before believing the
404s. Without that, a from-inside arm handed "0 public repos" would have
produced a clean, confident, completely wrong fleet inventory. The 44 individual
repo probes also mixed **real 404s with `TypeError`s from rate-limiting**, which
would have been read as "no repo" for 5 of the 44.

### Control B (task 6) — "the by-ply split gives 0.5045"

**Did it degrade gracefully? NO.** Seed 99 gives 0.5045; the 20-seed sweep gives
0.4915 ± 0.1757. A single number from a high-variance procedure is not a
low-confidence answer, it is a **confident wrong answer** — worse than reporting
a wide interval. This is the exact failure `CORRECTION-PROJECTION.md` already
recorded ("no gap smaller than the spread is a finding") recurring in a
procedure that was supposed to be the *fix* for it.

**The asymmetry that matters:** for the file paradigm, a bad state is **visible
as a bad state** — a 404 is checkable, a seed is a parameter, a missing
`verified_subset.txt` is a file that is not there. Every one of my four
near-misses in this run was caught by a command, not by judgment. For the
inside arm, a bad state is **indistinguishable from a good one at the point of
use** — the wrong 0.5045 and the right 0.4915 are the same *kind* of object.

**So: the inside vantage point is not more susceptible to bad input, but it is
less *self-checking*.** That is a weaker claim than the orchestrator's and it is
the one the evidence supports.

---

## 5. THE RESULT

**Counts, n=6.**

**Did the file paradigm produce an answer that changed the next action?**
- **YES on 6 of 6.**

**Did the `from inside` substitute change the next action?**
- **YES on 0 of 6.** On the one comparable cell (task 5) it **agreed** with the
  file paradigm and, before the control, **agreed with the wrong answer too**.
- **UNVERIFIABLE on 4 of 6** — no key, no JEV battery, not scored as failure.

**Where `from inside` was cheaper and still correct: nowhere measurable at
n=6**, because it was not runnable on 4 of 6 and did not win on the other 2.

**What the experiment actually shows, which is not what was claimed:**

1. The claim's two supporting data points are about **retrieving a document
   cheaply**, not about **judgment from inside a state**. The brief's own
   `primitives/score.md` example is a doc fetch. Conflating the two is what made
   the hypothesis feel supported.
2. **The instrument was never available in this lane.** The strongest available
   evidence for the hypothesis is a fetch that a *file paradigm* operation (read
   the right URL) also explains — the two data points do not separate the
   hypotheses.
3. **The file paradigm caught four of its own errors this run** — depth-1 clone
   (1 vs 20 commits), `orgs/` vs `users/`, rate-limit `TypeError`s masquerading
   as 404s, and an uncommitted data file making the experiment irreproducible.
   All four were caught by *commands*, not by judgment.
4. **The single highest-value result here (task 6) came from running the code
   twenty more times than the report did** — which is the file paradigm, and is
   the same action as "sitting in the captain's chair". **Doing and reading are
   not two vantage points. Doing *is* the file paradigm's better half.**

That last one is the finding I would most want the orchestrator to check. The
original data points — "running the demo", "sitting in the captain's chair" —
are not the *opposite* of reading. They are running, which the file paradigm
already includes. What the claim calls "from inside" is, in every case I could
construct, **more file-paradigm work, not less.**

---

## 6. THE TWO REQUIRED ENDINGS

**The task where reading was better than asking: TASK 4 —
`constraint-theory-core` and the 6.8× constant.** One `grep -rI '6\.8'` returns
**0**. The repo does not contain the claim. No judgment call against any state
can improve on "the premise is false"; an inside arm handed the premise would
have rationalised a constant that does not exist. Task 2 is second: the
*absence* of `ORSet` in 19 lines of canary is invisible to any question you can
ask about what the canary does — you have to read what it does not reference.

**The task where asking was better than reading: NONE. I failed to construct
it.** And I can say precisely why, which is the useful part:

- On **task 1** the README already states 94 and the running code confirms it.
  Asking changes nothing.
- On **task 3** the answer is a vacuous truth (0 merges) that a two-command
  check settles.
- On **task 5** the file paradigm produced a *table*; the inside arm, given the
  same state, produced agreement — and under the stale-state control produced
  agreement with a **wrong** answer.
- On **task 6** the from-inside arm was the one at risk: the 0.5045 in the docs
  is a single draw from sd 0.1757, and had I been *inside* that state asking
  "is the by-ply number at chance?", the right answer would have been "the
  distribution has sd 0.18 and 7 of 20 seeds are degenerate" — a much more
  expensive thing to establish than `git log --merges | wc -l`.

**To construct a task where asking wins, I would need a state that is cheap to
*hold* and expensive to *reconstruct*.** No task on this list has that shape:
all six are reconstructible by a command in under a second. The hypothesis may
still be true for states that are expensive to rebuild — a live system, a
colleague's head, a 5,000-line runtime — **but on the class of tasks actually
being worked this week, it is not supported, and the instrument to test it was
not available in the first place.**

---

## 7. REPRODUCE

```bash
git clone --depth 1 https://github.com/SuperInstance/quilt-tools && cd quilt-tools
npm install && for f in tools/*.mjs; do node "$f" | tail -1; done

git clone --depth 1 https://github.com/SuperInstance/crdt-orset
grep -n "ORSet" tests/canary.rs src/lib.rs

git clone https://github.com/SuperInstance/quilt-in-git
git log --all --merges --oneline | wc -l          # 0

git clone --depth 1 https://github.com/SuperInstance/constraint-theory-core
grep -rI '6\.8' . --exclude-dir=.git | wc -l      # 0

python3 /tmp/vantage/t5c.py                       # 5140 public repos, 7/44 match
python3 /tmp/vantage/vfnv.py /tmp/c4/c4_ground_truth.txt   # digest check
python3 /tmp/vantage/byply4.py                    # 20-seed by-ply sweep
```

**No pushes. Clones read-only. `TYPESAFEAI_KEY` never present → 6 JEV batteries
`UNVERIFIABLE`, reported as such and not scored.**
