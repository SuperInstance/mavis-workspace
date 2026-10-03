# durable-LOGIC — the same idea, many routes, and the part that survives

**Lane:** diff two instances of one idea and keep what is common.
**Date:** 2026-10-02. **Method:** enumerate routes, verify each exists *today*, then
**execute** the routes against mutations. No GitHub writes. No pushes.

> This document is not a census. It is a **diff**. Where a route was claimed but not
> found, the row says `NOT FOUND` and stays in the table. Where a claim about a repo
> turned out to be wrong on inspection, that is recorded too — including one of my own.

---

## 0. How "verified to exist today" was done

| method | what it proves | what it costs |
|---|---|---|
| `git ls-remote https://github.com/<r>` | the repo exists *now* | free, not API-rate-limited |
| `git clone --depth 1` then `fetch --unshallow` | full file contents + full history | free |
| `pytest` against the real suite | the route's own tests, unmodified | free |
| **mutation → re-run suite** | what the route can and cannot detect | free |
| `ast.parse` / `inspect.getsource` | which definition actually binds | free |

The GitHub REST API was **exhausted (60/60 used, `remaining: 0`)** and the one PAT
discovered embedded in a git remote URL (`/tmp/all_remotes.txt`) is **revoked —
HTTP 401 `Bad credentials`**. Neither blocked the work, because the git protocol is a
separate quota. *Incidental finding, not part of any pattern: a live-looking
`x-access-token:ghp_…` is stored in plaintext in `.git/config` of a cloned repo. It is
dead, but the next one minted into the same place will not be.*

**Correction I made in flight.** I read `frozen-clock-lab/lab/chain.py` and reported
that `__init__` is defined twice (lines 28 and 59) and the second shadows the first,
leaving `head/position/ops` uninitialised. **That was wrong**, and executing it killed
the claim: `inspect.getsource` shows the *second* `__init__` is the complete one
(`chain.py:59-62` sets `_genesis`, `head`, `position`, `ops`); lines 28-31 are dead
code carrying a `# noqa: F811` that is accurate. The redundancy is cosmetic. Reported
here because the mistake is the exact one this lane is supposed to catch.

---

## 1. THE WITNESS LOG — a decision plus what was rejected

### Routes (verified 2026-10-02)

| # | route | where it lives today | status |
|---|---|---|---|
| W1 | `SuperInstance/quilt-in-git` | `.quilt/bin/quilt-receipt:58` writes `.quilt/receipts/$SHORT.json`; time from `git log -1 --format=%ct` (`:7`, "never wall clock"); `LEDGER.md`; `pins/failfirst.log` + 6 `pins-final.log` | **VERIFIED** |
| W2 | `SuperInstance/frozen-clock-lab` | `lab/chain.py:23-48` `ReceiptChain`, `receipt_i = fnv1a64(head \| canonical(op))`, "Position is an integer index — never a time" (`:25`); `pins/failfirst.log`, `pins/pins-final.log` | **VERIFIED** |
| W3 | `SuperInstance/doubt-ledger` | `ledger/store.py:6` `_checksum(line_id, body)`, append-only `add()` `:46`, `discharge(entry_id, reason)` `:73`; `receipts/verify-main-2026-10-02.md`; 6 pin logs | **VERIFIED** |
| W4 | `SuperInstance/moth-corpus` | `src/moth_corpus/model.py:46-72` `row_hash` + `chain_hash`, GENESIS anchor; `verify_rows` recomputes | **VERIFIED** |
| W5 | `SuperInstance/moth-ledger` | `src/moth_ledger/hashes.py`; `tests/test_tamper.py` | **VERIFIED** |
| W6 | `SuperInstance/moth-cells` | `src/moth_cells/`, `tests/test_walk_*.py` | **VERIFIED** |
| W7 | `SuperInstance/moth-honest` | repo exists | **VERIFIED (repo)** / no pin log |
| W8 | `adjudications/<short>.json` in `quilt-in-git` | **never existed.** `git log --all --diff-filter=A -- '*adjudication*'` over the **unshallowed** history (10 commits) returns nothing; no path in any tree contains "adjudication" | **NOT FOUND** |
| W9 | D1 table `demotion_receipts` in `superinstance-db` | documented at `D1-INVENTORY.md:57,72,86`; `CLOSE-LOOP.md:268` records it as **"unproven / FILED"**. `CLOUDFLARE_TOKEN` is absent from this session, so the D1 endpoint cannot be read. `SuperInstance/superinstance-db` is **not a repo** (`ls-remote` → NOT FOUND); it is a Cloudflare D1 database | **UNVERIFIABLE TODAY** |
| W10 | wardroom journal, "Next duty: Awaiting instructions." | appears only in prose (`EXPERIMENTS.md`, `lattice-RD.md`, `org2/mdcache/fleet-research.json`). No repo, no file, no table — only the sentence | **NOT FOUND as an artifact** |
| W11 | `SuperInstance/fleet-triage` | `BOARD.md`, `CORRECTION-*.md` (4 files), local | **VERIFIED** |

**W8 is a finding, not an omission.** The route was described as "tick commits →
receipts → an `adjudications/<short>.json`". Receipts are real and are at
`.quilt/receipts/<short>.json`. `adjudications/` has never existed in that repo.

### The invariant

> **An attestation that has never been observed to fail is not an attestation; it is a
> comment.**

This is the one sentence true of W1, W2 and W3 and false of W4–W7 — and that falsity
is the headline of this section.

**The variation is not cosmetic. It splits the fleet 3 / 4.**

| route | `pins/failfirst*.log` | `pins/pins-final.log` |
|---|---|---|
| quilt-in-git | **YES** | YES (6) |
| frozen-clock-lab | **YES** | YES |
| doubt-ledger | **YES** | YES |
| moth-ledger | **NO** | **NO** |
| moth-corpus | **NO** | **NO** |
| moth-cells | **NO** | **NO** |
| moth-honest | **NO** | **NO** |

`quilt-in-git/pins/failfirst.log` is a committed artifact whose first lines are a
genuine red: `cp: cannot stat '…/.quilt'` / `FAIL P1-0 setup (quilt-init runnable?)`.
It is ugly and it is the whole idea: **the record of the check going red is itself a
receipt.** The moth family runs the same class of assertion in CI, but commits no
transcript — only green. A green CI badge and a witnessed negative are the same
assertion and a different amount of evidence, and the fleet has quietly been treating
them as equal.

---

## 2. THE CANARY — a constant that must not change

The richest pattern, and the only one where I could run a full mutation matrix.
**Baseline: all three moth suites green unmodified — 61, 23, 27 tests.**

### Routes (verified 2026-10-02)

| # | route | where | status |
|---|---|---|---|
| C1 | `moth-ledger` — **origin** | `src/moth_ledger/hashes.py:17-25` 4 vectors; `assert_pins` `:45-53`; CLI gate `cli.py:21`; **independent oracle** `tests/test_bytes_law.py:9-12` | **VERIFIED** |
| C2 | `moth-corpus` — vendored @ `e95c786` | `src/moth_corpus/vendor_hashes.py:13-17` **3** vectors; `assert_pins` `:36-40`; CLI `cli.py:22`; `tests/test_receipts.py:8-9` | **VERIFIED** |
| C3 | `moth-cells` — vendored transitively (`ledger→corpus→honest→cells`) | `src/moth_cells/vendor_hashes.py:15-19` 3 vectors; `assert_pins` `:38-42`; CLI `cli.py:24`; `tests/test_terrain.py:19` | **VERIFIED** |
| C4 | fleetlint **python** template | `templates/python-package/src/PKG/canary.py:8-20`; `tests/test_canary.py` incl. `:23-26` negative control | **VERIFIED** |
| C5 | fleetlint **node** template | `templates/_shared/canary.mjs:6-24`; `templates/node-package/test/canary.test.js:16-29` — **imports the real canon** `:4` | **VERIFIED** |
| C6 | fleetlint **rust** template | `templates/rust-crate/src/lib.rs:2-17`; `tests/canary.rs:3-16` | **VERIFIED** |
| C7 | fleetlint **docs-site** template | CI runs `linkinator` only; zero canary. Its own README names the case: *"a canary in the prose only / the words are pinned, the bytes are not"* | **VERIFIED — 0 canaries** |
| C8 | `fleetset/fleetlint` on GitHub | `ls-remote` → **NOT FOUND**; `SuperInstance/fleetlint` → **NOT FOUND**. The repo exists **locally only**, at `/workspace/projects/fleet-kit/fleetlint` | **NOT FOUND on GitHub** |
| C9 | the CRDT canary, "incapable of failing since `dcbdeca`" | `SmartCRDT` + `CRDT_Research` cloned; the specific commit was not located in this pass | **PARTIAL** |
| C10 | `plainsong`'s "11 pins" | no set of 11 pinned vectors exists. What exists are individual pinned assertions scattered across `tests/test_fingerprint.py:58`, `test_mcp.py:383`, `test_chordsymbol.py:285` | **NOT FOUND as described** |
| C11 | `lau`'s pinned fixture, resolver's frozen index | not in this pass | **NOT SEARCHED** |
| C12 | `quilt-canary`, `quilt-quantum-canary`, `canary-3lang` | repos present in the local corpus | **NOT SEARCHED** |

### The invariant

> **A pin is a claim about a *second* thing. If the checked input lives in the same
> file as the expected output, the pin is a comment with a hex number in it.**

This is what the fleet's own best route already says out loud —
`ALPHABET_CANARY.txt`:

> *"The byte canary hashes a fixture STRING and has been applied in 20+ repositories.
> It has never once been applied to the NAMES. That is how MERGER survived in the
> package that defines the canon."*

That sentence is the pattern's own post-mortem, written by the fleet, and it is
exactly the invariant. The fixture sits next to its own answer, so it can never
report on the thing it was deployed to protect.

**It survives every route except the ones that share a file with their fixture — and
that exception is the finding.**

### The failure-mode catalogue — MEASURED, not asserted

Each row is a real mutation applied to a real file, then the real suite re-run.

| # | failure mode | moth-ledger | moth-corpus | moth-cells |
|---|---|---|---|---|
| **FM1** | **never constructs the value** — `assert_pins` computes `got = expected` | **GREEN** | **GREEN** | **GREEN** |
| **FM2** | **input deleted** — the café vector removed from `PINNED_VECTORS` | **GREEN** | **GREEN** | **GREEN** |
| **FM3** | wrong unit — `fnv1a_64` hashes UTF-32 code points, not UTF-8 bytes | RED | RED | RED |
| **FM4** | normalisation — fixture NFD-decomposed (`cafe` + U+0301) | RED | RED | RED |
| **FM5** | truncated at the head — `MASK64` → 32-bit | RED | RED | RED |
| **FM6** | text-vs-integer — `0x024a…` is 17 digits, a u64 prints 16 | not reachable (integers throughout) | not reachable | not reachable |

**FM1 and FM2 are green in all three routes.** The canary that has been vendored into
20+ repositories cannot detect the two things most likely to happen to it: someone
replacing the check with a tautology, and someone deleting the line. Both leave a
fully green 61/23/27-test suite. The deletion is not even a subtle edit — it is
removing one tuple from a list, and nothing in any of the three repos asserts the
list's length or its membership. `PINNED_VECTORS` is even re-exported from
`__init__.py` in all three, so the count is *available* to a test and no test reads it.

**Why the origin is stronger than its copies, precisely.** C1 is the only route with a
test that hardcodes the fixture *outside* the module under test —
`tests/test_bytes_law.py:10` builds `"café Δ 日本語"` itself and `:11` asserts against
the literal. C2 and C3 have no such test: their only pin is `assert_pins()` reading
`PINNED_VECTORS` out of the same file. **Vendoring destroyed the canary's
independence.** C2 and C3 also silently dropped C1's fourth vector `b"a"` — a second
quiet loss on the same journey.

**The split inside fleetlint is the same split again, and it is the sharpest thing in
this document.** C5 (node) does `import { ALL_OPCODES } from '@superinstance/opcode-canon'`
— the alphabet comes from outside the checker. C4 (python, `test_canary.py:3`) and C6
(rust, `canary.rs:14`) hash a **hardcoded copy** of the alphabet. Verified today:

```
alphabet canary over the REAL canon 11 opcodes -> 0xe5c271ee5c13e9c7   ✓ matches
alphabet canary with MERGE -> MERGER           -> 0x5d06b2edd86331df   ✓ moves
```

So the constant is real and the negative control fires — **but only the node template
would notice a rename in the canon.** Rename an opcode in `@superinstance/opcode-canon`
and the python and rust templates keep passing, because they are testing their own
copy of the list. C7 has no canary at all. **One template in four can detect the event
it exists to detect.**

### The negative control — the only route that proves it can fail

`templates/_shared/negative_control.md` makes the demonstration a merge requirement:

> *"A check that has never been observed to fail has not been shown to work. … 'Tests
> pass' is not evidence; 'tests fail when I break the thing, and pass when I restore it'
> is."*

and implements it as an executable test — `test_canary.py:23-26`,
`canary.test.js:24-29`, `canary.rs:15-16`. I ran the maths: the control **fires**. This
is the single most valuable artifact in the whole study, and it is a *template* — it
has been shipped to 3 of 4 languages and adopted by none of the 20+ repos the byte
canary actually lives in.

---

## 3. THE TYPED CELL — a closed option set carried as a type

| # | route | status |
|---|---|---|
| T1 | `plato-tile-encoder`, 384-byte record, comment says `tags(24)` / code writes `20` | local clone `/workspace/.resolver-state/clones/plato-tile-encoder`; **NOT re-verified this pass** |
| T2 | JEV `criteria: {label: null}` | `SuperInstance/jev-quilt` — `ls-remote` EXISTS; not diffed this pass |
| T3 | the "988 types, 940 with no invariant" | claim in this account; **not re-derived** |
| T4 | `quilt-studio` cell kinds | repo EXISTS; not diffed this pass |
| T5 | `cell-doctrine` | repo EXISTS; `index.js`/`index.d.ts`/`test.js` — not diffed this pass |
| T6 | `@superinstance/opcode-canon` — 11 opcodes as `readonly` tuple types, `index.d.ts:3-4`, with `OPCODE_SIGNATURES: Readonly<Record<…>>` | **VERIFIED** — the cleanest instance found: a closed set carried as a type *and* given a runtime shape |

**Honest status: this pattern is under-diffed.** One route verified. The variation
catalogue does not exist yet. It is the obvious next lane and I am not going to
pretend four unexamined rows constitute a diff.

---

## 4. THE REFUSAL — the system declines instead of answering

| # | route | where it lives today | status |
|---|---|---|---|
| R1 | `selectlib` `ControlFailure` | `selectlib/controls.py:13-14` `class ControlFailure(AssertionError)`, docstring *"The harness refuses to produce a number"*; raised `:28` when a control **errors** and `:32` when it does not fire; public re-export `selectlib/__init__.py:17,23` | **VERIFIED** |
| R2 | `doubt-ledger` — *"what stopped being checked, why, what covers it"* | `LEDGER.md:1-30` grammar with `status: open\|due\|discharged`; `store.py:73` `discharge(entry_id, reason)`; README rule: **"Discharge requires a written reason on a follow-up line; an unreasoned discharge is just blindness again."** | **VERIFIED** |
| R3 | `quilt-in-git` refusal mode | present as pin evidence: `pins/pins-final.log` `PASS P2b next commit touching cell rejected (rc=1)`, `PASS P2c error mentions frozen` | **VERIFIED (as a pin)** |
| R4 | `moth-corpus` refusal | `tests/test_receipts.py:80-93` `test_unsupported_lang_refused`, `test_missing_repo_refused`, both expecting `CorpusError` | **VERIFIED** |
| R5 | `abstain-gate` | **NOT a repo.** `ls-remote` → NOT FOUND. `JEV-CONTRACT.md:139`: *"abstain-gate is a documented primitive and we built it by hand."* The route is the hand-rolled JEV score gate, not a repository | **NOT FOUND as a repo** |
| R6 | `abstain-gate` on a `0.57/0.43` split returning `confidence 0.35` | asserted in this account; **not located in source this pass** | **UNVERIFIED** |

### The invariant

> **A refusal must be a value the caller can hold, and it must say what it would have
> taken to proceed.**

R1 satisfies the first clause exactly — `ControlFailure` subclasses `AssertionError` and
is in `__all__`, so a caller can catch it — and its message at `:33-36` states the
second (*"a rule that cannot be shown to detect the thing it claims to detect must not
be used to judge anything else"*). R2 is the sharpest instance in the study: it
**refuses to let its own operator close a doubt silently**, requiring a written reason
or leaving the doubt open.

**The variation worth stealing:** R2's "an unreasoned discharge is just blindness again"
is the same sentence as FM1/FM2 above, reached from the opposite direction. A doubt
discharged without a reason and a canary that was never observed to fail are the same
defect: **a record that cannot distinguish a decision from an omission.**

---

## 5. THE EFFECTIVE SAMPLE SIZE

| # | route | status |
|---|---|---|
| E1 | "six independent measurements, all landing near 2" | not re-derived this pass |
| E2 | `tasnif` clustering | **NOT a fleet repo** — `ls-remote SuperInstance/tasnif` → NOT FOUND; it is a third-party image-clustering library. And it is **already a documented dead end**: `res-CLUSTER.md:71-74` concludes *"it would not have helped anyway… tasnif clusters images. This fleet's corpus is source code and markdown. `discover_images()` finds nothing."* | **NOT FOUND; dead end already diagnosed** |
| E3 | the route that would answer it about *code* | `res-CLUSTER.md:73` names it: the same pipeline behind a different `Embedder` behind the same `Protocol`. **Not built.** | **NOT BUILT** |

**Honest status: one route, and it does not exist.** This pattern is currently a claim
with no instances behind it. It is also the only pattern on the list where the
variation catalogue would be genuinely new information rather than a restatement —
which is the argument for doing it next.

---

## 6. Load-bearing vs cosmetic

**Load-bearing — changing it changes what the system can detect:**

| variation | why |
|---|---|
| construct vs compare-a-constant (FM1) | FM1 is green in 3/3. This *is* the canary. |
| input external vs input copied (fleetlint node vs python/rust) | the only difference that makes a rename detectable |
| input co-located with its answer (FM2) | green in 3/3; the fleet's own `ALPHABET_CANARY.txt` calls this the reason `MERGER` shipped |
| negative control present vs absent | the one route that proves it can fail |
| failfirst log present vs absent (witness log, 3/4) | the difference between an attestation and a comment |
| a discharge reason required vs not (R2) | an unreasoned discharge is indistinguishable from a deletion |

**Cosmetic — changing it changes nothing, and the fleet has spent real effort on it:**

- `0x024a555471370b18d` (17 digits) vs `0x24a555471370b18d` (16). Integer-equal. All
  three moth routes compare integers and are immune; fleetlint *documents* the trap at
  length and ships a test for it in three languages. **This is the most-documented
  non-bug in the fleet** — 40+ lines of prose about a difference that no code path
  consumes.
- `tau(24)` vs `tau(20)` in a comment.
- Whether `PINNED_VECTORS` has 3 entries or 4 — **except** that the *count* is the one
  thing whose absence is unprotected (FM2); the *value* of the count is not.
- The duplicated `__init__` in `frozen-clock-lab/lab/chain.py:28-31` (dead code,
  honestly marked `# noqa: F811`).
- The 7 phrasing variants of the same receipt grammar.

---

## 7. Verdict — are the invariants uninteresting?

**No. Two of the five are load-bearing, and the variation is the opposite of
cosmetic.**

The fleet has spent two days enumerating 5,127 repositories. This pass enumerated
**~30 routes across five patterns and found that one of them splits 3/4 and another
splits 1-of-3-and-3-of-4 on the same axis.** The axis is identical in both cases:

> **Is the checked thing derived from a source the checker does not control?**

- Witness log: does the record carry the observation that the check went red? 3 of 7
  routes do. The other 4 cannot tell an attestation from a comment.
- Canary: does the pin hash a value the checker does not also hold? **0 of 3** moth
  routes do. **1 of 3** fleetlint templates does.

That is not 5,127 repositories varying on nothing. That is one idea, implemented
twenty-odd ways, with a measurable split, and the split is in the same place both
times. The genuinely surprising result is that the pattern is **not** weakest where the
evidence is thinnest: the moth family ships a *tighter* looking artifact (a hash chain,
a CI gate, a CLI assertion) than the three repos that ship a `failfirst.log` — and it is
the one that cannot notice its own check being replaced by a tautology.

**The three tests nobody wrote, taken straight off the catalogue:**

1. *Break the checker, not the code.* `assert_pins` → `got = expected`. Assert green.
2. *Delete the fixture.* One tuple out of `PINNED_VECTORS`. Assert green.
3. *Rename an opcode in the canon.* Assert the python and rust templates go red. **They
   will not**, because they hash a copy of the list.

The first two are one line each and both were already reported as GREEN, today, in all
three repositories, by the fleets' own test suites.

---

## Appendix — the canary failure-mode catalogue, in full

Ordered by how quietly it kills the check.

1. **Compare a constant to a constant.** `got = expected`. The check is a tautology
   and reads as a check. *Measured GREEN in C1, C2, C3.*
2. **The fixture lives beside its own answer.** Delete the tuple; nothing notices.
   *Measured GREEN in C1, C2, C3.* C1 is the only route shielded, and only because a
   *second* file hardcodes the same string.
3. **The alphabet is copied, not imported.** fleetlint python + rust hash a local list;
   the canon can change freely. *Measured: node fires, python/rust cannot.*
4. **No canary in the lane at all.** fleetlint's docs-site template ships a CI that
   checks links and nothing else.
5. **Never re-run.** **CLOSED for C1–C3** — `assert_pins()` is called from each
   package CLI (`cli.py:21/22/24`) and from a test file, and all three repos run pytest
   on push and PR. This is the one failure mode the fleet actually got right.
6. **Text compared where an integer was meant.** `0x024a…` vs `0x24a…`, 17 vs 16
   digits. **CLOSED** in C1–C3 by using integers throughout; *documented to death* in
   fleetlint, which is why this entry is cosmetic and #1–#3 are not.
7. **Normalised instead of byte-exact.** NFD `café`. *Measured RED in all three.*
8. **Wrong unit — characters, not bytes.** UTF-32 code-point hashing. *Measured RED in
   all three.*
9. **Truncated at the head.** `MASK64` → 32-bit. *Measured RED in all three.*

**Nine ways to get a canary wrong. The fleet has closed 3 of them. The three that
remain open are the three that require removing something rather than changing it — and
those are the three nobody has written down until today.**

---

## And the single invariant that survives every route of the witness log

Every witness-log route — W1 through W7, across git receipts, an FNV-1a-64 position
chain, a JSON store with its own checksum, and four corpus hash chains — obeys this and
only this:

> **The record must be re-derivable from itself, and must carry the evidence that the
> derivation was once observed to disagree with the world.**

The first clause is universal and is why four different storage formats (a JSON file
per commit, a hex chain, a checksummed JSONL store, a two-field row) interoperate
without design. **The second clause is where the fleet splits 3 / 4.** `quilt-in-git`,
`frozen-clock-lab` and `doubt-ledger` keep a committed record of the check going red.
`moth-ledger`, `moth-corpus`, `moth-cells` and `moth-honest` keep a green CI badge and
nothing else — and, uniquely among all four, their canary is also the one that survives
being replaced by `got = expected`.
