# SUBSTRATE-FIX — the `substrate-*` family, fixed and demonstrated

> Status: **10 of 10 fail-open harnesses fixed, 11 of 11 CI'd, 0 remain.**
> The number in the brief was 13. Measured, it is **10**, and all 10 are `substrate-*`.
> Nothing is left unfixed in this family except one hole I could not close without a
> decision from you, named in §5a.

**No GitHub push was made.** Every change is on a local branch
`fix/fail-closed-harness` in `/workspace/projects/fleet-triage/repos/substrate-*`, working
tree clean, `origin/main` untouched. Combined patch: `substrate-fix-artifacts/substrate-failclosed.patch`
(11 repos); split and individually verified per repo in `substrate-fix-artifacts/per-repo/`.
Push command is in §7.

---

## 1. The enumeration, re-derived by execution instead of by regex

Four reports found this. I did not trust any of them, and neither did I trust the
detector. I measured the property directly.

`substrate-fix-artifacts/census_all_harnesses.py` — for **every** harness in the fleet
(**330** of them, discovered with the sibling lane's `is_harness()` predicate, not a
new competing rule), copy the repo to a temp dir, inject a guaranteed top-level throw,
run it, and read `$?`.

```
harnesses probed: 330
FAIL-OPEN (poisoned harness still exits 0): 0
indeterminate (timeout/err): 0  []
```

That single number is the most important result in this document and it is worth being
precise about what it does and does not say. A throw injected *before* any handler cannot
be swallowed, so `0` here proves the following and nothing more:

> **Every one of the 330 harnesses in this fleet that does not have a top-level
> `try`/`except` already fails closed.**

That is a real, previously-unmeasured result: the fail-open defect is not diffuse. It is
confined to harnesses that catch.

`substrate-fix-artifacts/census_inside_try.py` then targets exactly the population census 1
cannot reach — the harnesses that *do* have a column-0 handler — and injects the failure
**inside the `try` block**, which is what an actual product failure looks like. One
instrument, run on two trees:

```
######## BEFORE (pristine main HEAD) ########     ######## AFTER (my diff) ########
try/catch harnesses probed : 10                    try/catch harnesses probed : 10
FAIL-OPEN  (exit 0 on failure): 10                 FAIL-OPEN  (exit 0 on failure): 0
   substrate-bundle       test.js                      substrate-bundle       exit=1
   substrate-canary-pin   test.js                      substrate-canary-pin   exit=1
   substrate-contest      test.js                      substrate-contest      exit=1
   substrate-delegate     test.js                      substrate-delegate     exit=1
   substrate-membership   test.js                      substrate-membership   exit=1
   substrate-merger       test.js                      substrate-merger       exit=1
   substrate-revoke       test.js                      substrate-revoke       exit=1
   substrate-traverse     test.js                      substrate-traverse     exit=1
   substrate-withdraw     test.js                      substrate-withdraw     exit=1
   substrate-witness-log  test.js                      substrate-witness-log  exit=1
fail-closed (non-zero)     : 0                      fail-closed (non-zero)     : 10
```

**10 of 10 fail-open before. 0 of 10 after.** Ten harnesses in the entire fleet have a
top-level handler and all ten are `substrate-*`. **Zero fail-open harnesses remain.**

#### A correction I had to make to my own instrument, and it nearly cost me the finding

The first run of `census_inside_try.py` reported **2 fail-open after the fix**
(`substrate-canary-pin`, `substrate-membership`) — the two repos that actually pass. That
would have been a false accusation of a fix that works, so I ran the poisoned file by hand
instead of trusting the number:

```js
 4  } catch (e) {
 5    throw new Error('CENSUS: injected failure inside try');   <-- poison is HERE
 7    console.error('FAIL:', e.message);
 8    process.exit(1);
 9  }
```

`CATCH_RE` matches the **catch**, not the **try**, so the first `{` after its match start is
the handler's own brace and my poison landed in the handler. A handler that never runs is a
no-op: the try succeeded, the throw was dead code, and the harness correctly returned 0.
The instrument was measuring nothing and reporting it as a defect. Fixed to `rfind("try")`
and verified by self-test before the numbers above were taken.

Two further silent traps in the same ten minutes, both caught by executing rather than
reasoning: `git clone <local-path>` takes the **checked-out branch**, so my "pristine HEAD"
tree was quietly my *fixed* tree and reported 0 fail-open before the fix (fixed with
`-b main`); and the earlier D1 panel in §3 was captured before the branch existed, so it
was valid, but it has been re-run under `-b main` anyway. The lesson is the one already
learned elsewhere in this fleet: **the census tool is code, so its first output is a claim
about code, and the way to settle a claim about code is to run it.**

Artifacts, both re-verified after the fix:
`census_all_harnesses.py` (330 probes) · `census_inside_try.py` (10 probes × 2 trees).

### 1a. Why the brief says 13 and the truth is 10

Reconciling the four reports against what I measured:

| Repo's "13" | Measured | Why |
|---|---|---|
| 11 `substrate-*` | **11 exist; 10 fail open, 1 (`substrate-attest`) never did** | `substrate-attest/test.js` has **no** `try`/`catch`. A crash propagates and node exits 1. It was already honest. It is a *vacuous* harness, not a fail-open one — a different defect (§5b). |
| + `scrap-voice` | not fail-open | runs `node --test`, exits non-zero (per `sprint-FAILOPEN.md` §1; I did not re-derive) |
| + `recovered-copy-20260824-scrap-voice` | not a repo | byte-identical clone of `scrap-voice` at `b1117d8f`; inflates the count by exactly 1 |
| + `fleet-static-host` | not fail-open | chains two `node --experimental-strip-types` files, exits non-zero |
| + `quilt-cell` | not fail-open | `node --test` + `assert` |

11 + 4 = 15 named, reported as 13, of which **10 genuinely returned exit 0 on a failing
test**. `syn-HARNESS2.md` had already flagged this number as unreconciled; I am settling
it. **The true count is 10, and it is 10/10 `substrate-*`.** There was never a non-substrate
fail-open repo in the set, which is why four agents kept reporting a number they could not
close.

### 1b. The table, verified file by file

Two distinct shapes, and the difference matters for the fix:

**Shape A — fail-open (10 repos).** The handler observes the failure and discards it.

```js
try {
  const r = require('./index.js');
  console.log('OK: ' + Object.keys(r).join(', '));
} catch (e) {
  console.error('FAIL:', e.message);      // <-- prints FAIL, returns 0
}
```

| # | Repo | `catch` at | Variant | Committed-tree behaviour |
|---|---|---|---|---|
| 1 | `substrate-bundle` | `test.js:4` | 6-line | `FAIL: Cannot find module '@superinstance/observation-primitive'`, **exit 0** |
| 2 | `substrate-contest` | `test.js:5` | 7-line | same, **exit 0** |
| 3 | `substrate-delegate` | `test.js:4` | 6-line | same, **exit 0** |
| 4 | `substrate-membership` | `test.js:4` | 6-line | `OK: membershipIn`, **exit 0** |
| 5 | `substrate-merger` | `test.js:4` | 6-line | same as #1, **exit 0** |
| 6 | `substrate-revoke` | `test.js:5` | 7-line | same as #1, **exit 0** |
| 7 | `substrate-traverse` | `test.js:4` | 6-line | `FAIL: Cannot find module '@superinstance/substrate-witness-log'`, **exit 0** |
| 8 | `substrate-withdraw` | `test.js:4` | 6-line | same as #1, **exit 0** |
| 9 | `substrate-canary-pin` | `test.js:5` | 7-line | `OK: CANARY_INPUT, …`, **exit 0** |
| 10 | `substrate-witness-log` | `test.js:5` | 7-line | same as #1, **exit 0** |

Two variants (6-line and 7-line) — a leading `// quick smoke test` comment. **One** defect.
The whole of the fix is one line, and it is the same one line in both variants.

**Shape B — vacuous, not fail-open (1 repo).** `substrate-attest/test.js`, 21 lines,
`console.log` only, no handler. Exits 1 on a crash. Left alone; see §5b.

**What a real failure produced, for the record:** the committed tree as merged, with no
mutation anywhere, on a clean clone. `node_modules` is never installed in this family and
`@superinstance/observation-primitive` **is not a repository in this fleet** (`find` over
`/workspace` returns nothing). Eight of the eleven harnesses print `FAIL: Cannot find module`
and return **0**. They have never once loaded their own product. That is the honest reading
of the baseline and it is not constructed.

---

## 2. The fix

Three parts. **No product code was touched in any repo** — verified: `index.js` is absent
from `git diff --name-only` in all 11.

**(a) The exit code. One line, ten times.**

```diff
 } catch (e) {
   console.error('FAIL:', e.message);
+  process.exit(1);
 }
```

Nothing else changes. The message still prints, the ordering is unchanged, the success path
is byte-identical. This is the whole of the behavioural change and it is confined to the
failure path — which is the only path that was wrong.

**(b) The entrypoint (rule C).** All 11 had `"scripts"` absent from `package.json`.

```diff
+  "scripts": {
+    "test": "node test.js"
+  },
```

**(c) CI.** All 11 had zero workflows. Added `.github/workflows/ci.yml` to all 11:

```yaml
name: CI
on:
  push:      { branches: [ "main" ] }
  pull_request: { branches: [ "main" ] }
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "22" }
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
```

There is deliberately **no** `continue-on-error`, **no** `|| true`, and **no** `set +e` in
any of the eleven files, and there is a comment in each saying why. A green tick on a
harness that never ran is the same defect wearing better manners; the comment is there so
the next person does not add one for kindness.

**The detector's verdict, before and after** (same rule, `fleetlint_failopen.py`, extended
not replaced):

| Rule | Before | After |
|---|---|---|
| **A** top-level handler cannot fail | 10 | **0 fleet-wide** |
| **C** harness present, no `test` script | 11 | **0 fleet-wide** |
| **B** no assertion primitive | 11 | 11 (see §5b) |

Full fleet re-run after the change: `python3 fleetlint_failopen.py repos/*/` → **23
findings, down from 44**, and **zero** of them are rule A.

---

## 3. Proof

Four demonstrations. A fix without one is an assertion.

### D1 — the whole family, before and after, one experiment run twice

Same script both times. Clone pristine `HEAD`, inject a **real throw into the product
(`index.js`)** — not a mutation of the harness, a product that genuinely fails to load —
then run the committed harness and read `$?`.

Cloned with `-b main` (see the `git clone` trap in §1), product poisoned identically both times:

```
REPO                     BEFORE   AFTER
substrate-attest         exit=1   exit=1
substrate-bundle         exit=0   exit=1
substrate-canary-pin     exit=0   exit=1
substrate-contest        exit=0   exit=1
substrate-delegate       exit=0   exit=1
substrate-membership     exit=0   exit=1
substrate-merger         exit=0   exit=1
substrate-revoke         exit=0   exit=1
substrate-traverse       exit=0   exit=1
substrate-withdraw       exit=0   exit=1
substrate-witness-log    exit=0   exit=1
```

**10 of 11 return 0 on a product that throws. 11 of 11 return 1 after the fix.**
`substrate-attest` is unchanged at 1 in both columns because it was never fail-open —
which is also the measurement that keeps the fleet count at 10 and not 11.

### D2 — same broken module, old harness vs new harness (`substrate-membership`)

Isolates the change to the harness itself. A genuine defect injected into `index.js`
(a require of a module that does not exist), then both harness versions run against the
identical broken module:

```
  OLD (committed) harness: exit=0      <-- prints "FAIL: Cannot find module", returns success
       FAIL: Cannot find module './missing-dependency.js'
  NEW (fixed)     harness: exit=1
       FAIL: Cannot find module './missing-dependency.js'

  control: unbroken module, NEW harness -> exit=0  OK: membershipIn
```

The control matters: the new harness is not simply always-red. It is red on failure and
green on success.

### D3 — the real committed tree, zero mutation (`substrate-bundle`)

Not a constructed failure. This is `HEAD` exactly as merged, on a clean clone, on a
machine where `node_modules` has never been installed:

```
  OLD (committed) harness: exit=0
       FAIL: Cannot find module '@superinstance/observation-primitive'
  NEW (fixed)     harness: exit=1
       FAIL: Cannot find module '@superinstance/observation-primitive'
```

The family had never loaded its own product and had been reporting success.

### D4 — the CI gate can actually fail

A CI file that has never gone red is an assertion about a CI file. I ran each workflow's
exact two commands in a pristine clone across all 11:

```
substrate-membership   install=0 test=0  PASSED
substrate-canary-pin   install=0 test=0  PASSED
substrate-bundle       install=0 test=1  FAILED   t.log:FAIL: Cannot find module '@superinstance
substrate-witness-log  install=0 test=1  FAILED
substrate-revoke       install=0 test=1  FAILED
substrate-attest       install=0 test=1  FAILED
substrate-merger       install=0 test=1  FAILED
substrate-delegate     install=0 test=1  FAILED
substrate-traverse     install=0 test=1  FAILED
substrate-withdraw     install=0 test=1  FAILED
substrate-contest      install=0 test=1  FAILED
```

**2 green, 9 red.** See §5 — that red is the finding, not a regression I introduced.

### D5 — the honest counter-example: what the fix does **not** catch

`substrate-canary-pin` is a hash library whose entire purpose is a canary value. I break
the FNV prime, which makes every hash it computes wrong:

```
  harness says:     OK: CANARY_INPUT, CANARY_HASH, fnv1a64, fnv1a64Hex, verifyCanary
  harness exit =    0
  actual behaviour: match = false   hash = 0xe8896a5ab1c1aa11   expected = 0x024a555471370b18d
```

Green. The exit-code fix is real and it is not sufficient, because the harness's entire
body is `Object.keys(r).join(', ')` — **it never calls the product.** There is nothing for
it to assert. I am reporting this rather than hiding it: the fix converts the family from
*fail-open* to *honest-and-vacuous*, and vacuous is a smaller defect, not an absent one.

---

## 4. Diff

Per repo, `git diff main..fix/fail-closed-harness`. Files touched, complete list:

```
substrate-attest        .github/workflows/ci.yml  package.json
substrate-bundle        .github/workflows/ci.yml  package.json  test.js
substrate-canary-pin    .github/workflows/ci.yml  package.json  test.js
substrate-contest       .github/workflows/ci.yml  package.json  test.js
substrate-delegate      .github/workflows/ci.yml  package.json  test.js
substrate-membership    .github/workflows/ci.yml  package.json  test.js
substrate-merger        .github/workflows/ci.yml  package.json  test.js
substrate-revoke        .github/workflows/ci.yml  package.json  test.js
substrate-traverse      .github/workflows/ci.yml  package.json  test.js
substrate-withdraw      .github/workflows/ci.yml  package.json  test.js
substrate-witness-log   .github/workflows/ci.yml  package.json  test.js
```

The `test.js` diff is the same two characters-plus-semicolon in all ten:

```diff
 } catch (e) {
   console.error('FAIL:', e.message);
+  process.exit(1);
 }
```

`index.js` appears in no diff. Combined patch:
`substrate-fix-artifacts/substrate-failclosed.patch`, split per repo into
`substrate-fix-artifacts/per-repo/substrate-*.patch`.

**The patches were verified to apply.** Each per-repo patch was applied with
`git apply -p1` to a fresh `git clone -b main` of its own repo, and the resulting
harness was run:

```
substrate-attest       APPLIES CLEANLY  files_changed=2  harness exit=1
substrate-bundle       APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-canary-pin   APPLIES CLEANLY  files_changed=3  harness exit=0
substrate-contest      APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-delegate     APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-membership   APPLIES CLEANLY  files_changed=3  harness exit=0
substrate-merger       APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-revoke       APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-traverse     APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-withdraw     APPLIES CLEANLY  files_changed=3  harness exit=1
substrate-witness-log  APPLIES CLEANLY  files_changed=3  harness exit=1

clean: 11   failed: 0
```

The two zeros are the two repos whose product has no unresolvable dependency, and the exit
codes match §4 of this document exactly.

---

## 5. Still broken — read this before you push

### 5a. Nine of the eleven CI jobs will be red on first run. **That is correct.**

All 11 `package.json` declare `"@superinstance/observation-primitive": "file:../observation-primitive"`.
`observation-primitive` **is not a repository in this fleet** — `find /workspace` returns
nothing, and it is not published. `npm install` exits 0 (npm tolerates the missing `file:`
target) but the module is absent, so `npm test` exits 1. `substrate-traverse` additionally
declares `"@superinstance/substrate-witness-log": "file:../substrate-witness-log"`, which
*does* exist in the fleet but is not a sibling checkout on a fresh runner.

The failure was always there. The harness was eating it. **I have not papered over it and
I am not going to.** Three options, all yours:

1. **Land the red.** Honest, and it puts the unresolvable dependency in front of whoever
   owns it. Cost: 9 permanently-red badges until it is fixed.
2. **Land the exit-code fix now, hold the CI file.** Green stays green, the honesty is
   banked, and the red arrives with the dependency fix. Cost: the regression window stays
   open until CI lands — which is precisely what you told me not to accept.
3. **Publish or vendor `observation-primitive` first**, then land all of it. Cost: scope
   beyond the lane, and it is a real API decision.

My recommendation is **(1)**, on branches rather than main, because the whole point of this
lane is that a red that is true is worth more than a green that is not. **But this is a
judgement call about red badges and it is yours, not mine** — I have put the changes on
`fix/fail-closed-harness` in all 11 repos precisely so you can take (1), (2) or (3) without
rewriting anything.

### 5b. Every harness in the family is still vacuous (rule B, 11/11)

`sprint-FAILOPEN.md` §5e got this right and I have re-confirmed it by execution (D5). The
6-line file is a **module-load smoke test wearing a test file's name**. It asserts nothing
because it has nothing to assert: it never calls a single exported function. Adding real
assertions means writing tests against the products' contracts, which is a behaviour change
well beyond "the exit code" and therefore **outside this lane by your own rule**. It is
also the only thing that would make rule B go to zero, and the only thing that would catch
D5. Flagged, not done.

### 5c. Pre-existing packaging bug, untouched

8 of 11 declare `"types": "index.d.ts"` and **do not ship `index.d.ts`**:
`substrate-bundle`, `substrate-canary-pin`, `substrate-contest`, `substrate-delegate`,
`substrate-merger`, `substrate-traverse`, `substrate-withdraw`, `substrate-witness-log`.
(`attest`, `membership`, `revoke` were fixed in a prior PR — `be1b280`, `a837d99` — which
confirms this is a known class, not a new one.) Out of scope, but it is the same disease:
a field that claims something exists, and nothing checks.

---

## 6. The one rule, so the fourteenth never appears

> **A test harness is not a test. It is a program whose only required behaviour is to
> return non-zero when it observes a failure. `console.log('FAIL')` is not a report; the
> exit code is the report. And a harness nothing runs is a report to no one.**

Three clauses, each from a thing that actually bit:

- **The exit code is the report.** Printing `FAIL:` and returning 0 is a harness that
  *observed* its own failure and *discarded* it. Ten of them did. Print and return are
  different channels; only one of them reaches CI. → **the bug.**
- **No handler, no defect; a handler, a burden.** 330 harnesses, 0 fail-open outside the
  ten with a top-level `catch`. A `catch` at column 0 is not a style question, it is a
  demand: *if you can catch it, you owe the process an exit code.* Nested handlers for
  control flow are fine — the sibling lane already calibrated this correctly, column-0
  only, after 16 false positives. I did not touch it.
- **A harness nothing runs is a report to no one.** All 11 had zero CI and no `test`
  script, so even a correct exit code is only observed when a human remembers. That is
  the same defect wearing better manners, which is why CI shipped in the same change.

And the detector stays as it is. `fleetset/fleetlint/fleetlint_failopen.py` found all of
this in four separate passes and was never run as a fix — **the rule was never the
bottleneck.** It is extended here by nothing; it is *executed*. A, the sharp rule, now
gates: **0 findings fleet-wide.**

---

## 7. Push

Not pushed. All 11 repos are on local branch `fix/fail-closed-harness`, working tree clean,
`origin/main` untouched. On your word:

```bash
cd /workspace/projects/fleet-triage/repos
for d in substrate-*; do
  git -C $d push -u origin fix/fail-closed-harness
done
```

Branches, not main — 9 of these go red on arrival and that is a decision to make in the
open, not to land silently. All 11 repos were confirmed to exist and to have
`github.com/SuperInstance/substrate-*.git` as origin before any file was written.

If you would rather apply without git history, per-repo patches are in
`substrate-fix-artifacts/per-repo/` and each is verified to apply to a clean `main`.
