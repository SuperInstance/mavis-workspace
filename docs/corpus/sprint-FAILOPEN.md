# SPRINT-FAILOPEN — the fail-open harness family

**Lane:** fail-open harness census + family fix + recurrence rule
**Date:** 2026-10-01
**Pushes:** none. All work is local. No CI was added to any repo.
**Repos touched:** zero. Every reproduction was made in `/tmp` copies and deleted.

---

## 0. Headline

The reported finding is **right and, in one respect, understated.**

> *"13 repos in this fleet fail open — silently. A crashing or failing test produces exit 0."*

Three corrections, all measured:

1. **The count is 12, not 13.** `recovered-copy-20260824-scrap-voice` is a byte-identical
   clone of `scrap-voice` — same commit `b1117d8fd7da2f905469a3c44eca70ad96b52f88`, same 17
   files. The playtest sweep counted one repository twice.
2. **Only 10 of the 12 actually fail open.** `scrap-voice`, its clone, and `fleet-static-host`
   all run under `node --test`, which exits non-zero on failure. They are *vacuous*, not
   *fail-open*. That is a real defect but a different one, and folding it into this number
   overstates the family.
3. **The mechanism is worse than "fails open".** Nine of the ten harnesses do not fail open —
   they report **success**. They print `OK: <export>` and exit 0 when the product is a
   landmine. See reproduction R1. The `try/catch` is the *smaller* of the two defects; the
   larger one is that the harness never calls the product, so it has nothing to fail about.

The claim that `substrate-*` has zero CI across all 13 repos is **confirmed** — and it is
worse than "no CI": **all 11 `substrate-*` repos have no `test` script in `package.json`
either**, so `npm test` is a hard error and the only way anyone runs the harness is by hand.

---

## 1. The census

`substrate-*` family, all 11 repos, mechanism identical modulo two cosmetic variants.

| # | Repo | File:line | Mechanism | A real failure produces | CI | `npm test` |
|---|------|-----------|-----------|------------------------|----|------------|
| 1 | `substrate-bundle` | `test.js:4` | `catch(e){console.error('FAIL:',e.message)}` — no exit | `OK: bundle`, **exit 0** | none | missing script |
| 2 | `substrate-contest` | `test.js:5` | same (7-line variant) | `OK: contest`, **exit 0** | none | missing script |
| 3 | `substrate-delegate` | `test.js:4` | same | `OK: delegate`, **exit 0** | none | missing script |
| 4 | `substrate-membership` | `test.js:4` | same | `OK: membershipIn`, **exit 0** | none | missing script |
| 5 | `substrate-merger` | `test.js:4` | same | `OK: merge`, **exit 0** | none | missing script |
| 6 | `substrate-revoke` | `test.js:5` | same (7-line variant) | `OK: revoke`, **exit 0** | none | missing script |
| 7 | `substrate-traverse` | `test.js:4` | same | `OK: traverse`, **exit 0** | none | missing script |
| 8 | `substrate-withdraw` | `test.js:4` | same | `OK: withdraw`, **exit 0** | none | missing script |
| 9 | `substrate-canary-pin` | `test.js:5` | same (7-line variant) | `OK: CANARY_INPUT, …`, **exit 0** | none | missing script |
| 10 | `substrate-witness-log` | `test.js:5` | same (7-line variant) | `OK: WitnessLog`, **exit 0** | none | missing script |
| 11 | `substrate-attest` | — | **no** try/catch (exits 1 on crash) but zero assertions | uncaught throw, exit 1 | none | missing script |

### Not this family, despite being in the 13

| Repo | Why it is in the 13 | Verdict |
|------|--------------------|---------|
| `scrap-voice` | mutation survived | **Vacuous, not fail-open.** `node --test` in `package.json:9`. Exits non-zero correctly. Its problem is that the suite is shallow. |
| `recovered-copy-20260824-scrap-voice` | mutation survived | **Not a separate repo.** Byte-identical clone of `scrap-voice` at `b1117d8`. Should be deleted or marked. |
| `fleet-static-host` | mutation survived | **Vacuous, not fail-open.** `npm test` chains two `node --experimental-strip-types` files, which exit non-zero. |
| `quilt-cell` | 1/3 mutations caught | **Best in the set.** `test/test.js` uses `node --test` + `assert`. Caught the `return-falsy` mutation; missed two. |

### Ownership

All 15 repos are `github.com/SuperInstance/*`, authored by `Mavis <Mavis@superinstance.dev>` or
committing under the fleet's own history. No third-party forks were touched. The two
repos the orchestrator was worried about clobbering (`fleet-kit`, `Murmur`) were not
modified — `fleet-kit` exists locally but was not opened for write.

---

## 2. Reproductions

A count is a claim. These are demonstrations. All in `/tmp` copies, all deleted.

### R0 — the committed tree, unmutated, already fails and reports 0

`observation-primitive` is declared as `file:../observation-primitive` by all 11 repos. It is
**not in the fleet checkout** and `node_modules` is never installed anywhere in the family.
So on a clean clone, every harness dies on line 2:

```
$ cd repos/substrate-traverse && node test.js
FAIL: Cannot find module '@superinstance/substrate-witness-log'
$ echo $?
0
```

Not constructed. Not a mutation. The tree as committed.

### R1 — the product is a landmine, the harness says OK  ← *the headline*

```
$ node test.js
OK: bundle
$ echo $?
0
```

with `bundle()` opening `throw new Error('boom: witness log unreachable')`.
Confirmed independently: `bundle('x',['a'],{id:'jane'})` throws. **Every call fails. The
harness prints OK.** The `catch` never fires because the harness never calls the function.

### R2 — the science deleted, module still loads

`bundle`'s entire body replaced by `return { type: 'bundle' }` — validation gone, hashing
gone, `member_count` gone:

```
$ node test.js
OK: bundle          $ echo $? -> 0
$ bundle('x',['a','b'],{id:'jane'})   ->   {"type":"bundle"}
```

### R3 — a contract inverted

`substrate-revoke`: `if (!observation?.id) throw` → `if (!observation?.id) return {silently:'accepted'}`.
The "scars persist, refuse malformed input" invariant deleted.

```
$ node test.js
OK: revoke          $ echo $? -> 0
$ revoke(null,null,null)  ->  {"silently":"accepted a null observation"}
```

### R4 — the whole family at once

Every exported function in each repo given an immediate `throw`:

| Repo | Functions gutted | Exit | Harness says |
|------|------------------|------|--------------|
| substrate-bundle | 1 | **0** | `OK: bundle` |
| substrate-contest | 1 | **0** | `OK: contest` |
| substrate-delegate | 1 | **0** | `OK: delegate` |
| substrate-membership | 1 | **0** | `OK: membershipIn` |
| substrate-merger | 1 | **0** | `OK: merge` |
| substrate-revoke | 1 | **0** | `OK: revoke` |
| substrate-traverse | 1 | **0** | `OK: traverse` |
| substrate-withdraw | 1 | **0** | `OK: withdraw` |
| substrate-canary-pin | 3 | **0** | `OK: CANARY_INPUT, CANARY_HASH, fnv1a64, …` |
| substrate-witness-log | class ctor | **0** | `OK: WitnessLog` |
| substrate-attest | 3 | 1 | uncaught throw (the honest one) |

**10 of 11 report success on a product that is entirely non-functional.**

### R5 — a second family, found at the edge: the ✓-printer

`quilt/qgit/npm/test.js` has **zero assertions** and ends:

```js
console.log('✓ tick a');
...
console.log('All tests passed!');
```

With `tickCell()` reduced to `return;` — the tick is never written to disk:

```
✓ init
✓ add cell a
✓ add cell b
✓ tick a
✓ create room alpha
✓ status: 2 cells, 0 rooms
All tests passed!          $ echo $? -> 0
```

And note the **unmutated** baseline already contradicts itself: it creates `room alpha` and
then reports `status: 0 rooms`, and still prints `All tests passed!`. The bug is visible in
the output the harness is printing. It also requires `./src/index.js` when the file is
`./index.js`, so **it has never run successfully.**

### Negative control for all reproductions

A correct harness over the same gutted product:

```js
// test.js — real assertions
const assert = require('node:assert/strict');
const b = bundle('observation-set', ['o1','o2'], {id:'jane'});
assert.equal(b.member_count, 2);
assert.match(b.id, /^[0-9a-f]{16}$/);
```
```
intact product  -> OK: 4 assertions passed            exit 0
gutted product  -> Error: GUTTED                      exit 1
```

Same mutation. Opposite result. The reproductions are measuring the harness, not node.

---

## 3. The fix, as a family

One line, ten files.

```diff
--- a/test.js
+++ b/test.js
 try {
   const r = require('./index.js');
   console.log('OK: ' + Object.keys(r).join(', '));
 } catch (e) {
   console.error('FAIL:', e.message);
+  process.exit(1);
 }
```

The 7-line variant (`substrate-contest`, `-revoke`, `-canary-pin`, `-witness-log`) is
identical apart from `const r` → `const result`.

### Verified: does it work?

| Scenario | Before | After |
|----------|--------|-------|
| intact product | exit 0 | exit 0 ✓ |
| broken `file:../` dep, unmutated | **exit 0** | **exit 1** ✓ |
| same, 8 of 10 repos that import the dep | **exit 0** | **exit 1** ✓ |
| `substrate-membership`, `substrate-canary-pin` | exit 0 | exit 0 — *correct*, they have no external dep |
| product gutted but loadable | **exit 0** | **exit 0** ✗ |

**Stated plainly: this fix does not make the harness a test.** It converts *import failure*
from silent to loud. Reproduction R4 still passes on the fixed harness, because a module
whose functions all throw still loads fine. The one-liner is worth applying — it is the
minimal change requested and it closes the real-world failure — but it is **not** the whole
fix. The whole fix is R5-style: assert on behaviour. That is repo-by-repo work and I have
not done it, because you did not ask for it and it would mean inventing expected values for
10 opcodes.

### Not done, deliberately

- No commit. No push. The diff above is the proposal; the working tree is untouched.
- No `test` script added to any `package.json`. That is a finding (§4, C), not a licence.
- No CI added. Reported, not acted on.

---

## 4. The recurrence rule

`fleetlint_failopen.py` — three checks, because the defect has three shapes.

```
A  FAIL-CLOSED     a TOP-LEVEL exception handler with no exit/throw/assert path
B  NO-ASSERT       a harness that no runner collects and that has no assertion
                   primitive at all — it can print OK and can never print NOT-OK
C  UNREACHABLE     test files exist, package.json declares no `test` script   [WARN]
```

A is a special case of B wearing a try/catch. B is the rule that generalises.

### The negative control, and the three attempts it took

**Attempt 1 — over-fired 16 times in `pong-quilt`, a demonstrably correct repo.**
The rule matched every nested `catch`. All 16 were the *right* idiom: run a CLI subprocess
that is supposed to fail, catch the non-zero exit, assert on it after.

> ```js
> try { execFileSync(process.execPath, [TOOL], …) }
> catch (e) { status = e.status; out = e.stderr; }   // ← correct!
> assert.equal(status, 1, "marker fixture must exit 1");
> ```
> **Fix:** only a **column-0** handler is a failure sink. A nested catch is control flow.

**Attempt 2 — over-fired on 49 repos.**
Three bugs: python's `assert x == y` has no paren so my pattern missed it; `__init__.py`,
`conftest.py` and `fixtures/` were being treated as harnesses; and vendored trees
(`FastGen4quilt/.agents/skills/…/fixtures/*.ts`) were being walked.
**Fix:** bare-assert pattern, a real harness predicate, `git ls-files` instead of `rglob`.

**Attempt 3 — over-fired on 6 more, and this one is the interesting one.**
`FastGen4quilt/tests/test_trainer.py` has **zero asserts** and is not fail-open: it asserts
*"the trainer runs two iterations without raising"*, which is a legitimate (if weak) smoke
test. **Absence of an explicit `assert` is not absence of an assertion** — a runner supplies
an implicit fail-on-exception assertion to anything it collects.
**Fix:** B only fires on the standalone-script shape — no assertion primitive **and** not
under `tests/` **and** not pytest-named. Config dirs (`configs/`, `experiments/`, `scripts/`)
are excluded, which also killed the `config_dmd2_test.py` name collision.

**Attempt 4 — clean.** (It also took one debugging round on a stale NAS read of the rule
file itself, which produced phantom results until I ran it from `/tmp`. Worth knowing if you
run anything here: `python3 ../file.py` returns *yesterday's* file.)

### The control, final form

**Arm 1 — correct harness → silent.**
```
$ fleetlint_failopen.py mut/good
    SILENT
```
**Arm 2 — the *same file*, wrapped in a fail-open try/catch and nothing else changed → fires A.**
```
  FAILOPEN-HARNESS/A  test.js:11  top-level exception handler has no exit/throw/assert path
```
**Arm 3 — the *same file* with its assertions stripped and no try/catch (the substrate shape) → fires B.**
```
  FAILOPEN-HARNESS/B  test.js:1  harness contains no assertion primitive; …
```

One file, three states, and the rule tracks the change and nothing else. That is the
property that has to hold or the rule gets switched off.

### Fleet-wide result — 275 repos

**16 FAIL, 3 WARN.** 44 findings total. That is 5.8% of the fleet, and 14 of the 16 are the
family we already knew about.

### Negative control against real repos — 14 repos, all silent on A and B

`pong-quilt` (61/61 harnesses use assert) · `opcode-canon` · `live-canon-npm` (9 real
assertion groups, byte-exact hash checks) · `quilt-cell` · `FastGen4quilt` (NVIDIA, pytest) ·
`dojo-alchemist` · `dojo-builder` · `dojo-scribe` · `LLMs-from-scratch-early-version` ·
`quilt-apps` · `scrap-voice` · `recovered-copy-20260824-scrap-voice` · `fleet-static-host`
(DIY `pass++/fail++` counter — recognised, see below)

### Honest limits of this rule

- **A is high-confidence. B is a prompt, not a verdict.** A hand-rolled assertion in a shape
  I did not anticipate will read as B. `fleet-static-host` uses a DIY `pass++/fail++`
  counter with a hand-rolled `ok()` helper — I had to add a pattern for it explicitly, which
  is a confession that B's false-positive rate is not zero and only moves when I look.
- **B is scoped to JS/TS and Python.** Rust, Go and TypeScript-runner files are not covered.
- **C is advisory and I would leave it at WARN.** Three repos (all `scripts: null`):
  `madlibs-gan-npm`, `peanut-gallery-npm`, `opcode-canon`. `opcode-canon`'s harness is
  excellent — it just cannot be invoked by the conventional command. This is a packaging
  finding, not a correctness one.
- I would gate **A** on in CI and leave **B** advisory until it has been run over the fleet
  by someone willing to read each hit. That is the same characterisation the playtest agent
  reached for its own tool, and I think it is the correct one.

---

## 5. What was not in the 13 — the sweep's edge

### 5a. A second family that prints "All tests passed!" with zero assertions

`quilt/qgit/npm/test.js` — 26 lines, no `assert`, no `expect`, no runner. See R5.
It is not a `try/catch` family; it is a **✓-printing** family, and it is arguably more
dangerous because the success string is the one a human skimming CI output looks for.
It has also never run: `require('./src/index.js')`, but the file is `./index.js`.

**Rule A would never have caught this. Rule B did.**

### 5b. Four more printing scripts, same shape as `substrate-attest`

| Repo | `test.js` | Note |
|------|-----------|------|
| `witness-is-prediction` | 3 lines | the smallest harness in the fleet; pure `console.log` |
| `three-forms-of-forgetting` | 5 lines | pure `console.log` |
| `three-forms-of-evidence` | 7 lines | pure `console.log` |
| `cell-doctrine` | 7 lines | `// quick smoke test`, pure `console.log` |

None can fail. `substrate-attest` is in the same bucket (21 lines, `console.log` only) but
happens to crash loudly because it actually calls the product — the one accidental honest
harness in the family.

### 5c. 18 `recovered-copy-20260824-*` repos, 13 sharing a byte-identical HEAD

`recovered-copy-20260824-scrap-voice` is one of them, and it is **one of the 13 in the
reported census** — the number is inflated by exactly one because of it. The rest
(`fleet-embed`, `fleet-memory`, `fleet-ensemble`, `fleet-jepa-midi`, `mist-lab`, `mist-quilt`,
`elephant-sim-worker`, `ideation-games`, `scrapcraft-world`, `study-smartcomponent`,
`operational-fiction`, `agent-writings-archive`, `scrap-quilt`, `wesley`, `superinstance-ai`,
`DigitalTwin-RobotStudio-SmartComponent`, `tap-gamenight`) double the surface area of any
fleet-wide census and are not in any of them.

**Recommendation:** delete them, or rename with a `.dup` suffix and exclude from counts.
This is the same class of hazard as the two clobbered repos — a name that looks free.

### 5d. The `file:../` dependency chain is unresolvable by construction

Every `substrate-*` `package.json` declares `"@superinstance/observation-primitive": "file:../observation-primitive"`.
`observation-primitive` **is not a repo in this fleet**. `npm install` cannot work for any
of the 11 without hand-building a sibling directory, and no CI exists to do it. This is
prior to, and independent of, the exit-code bug — fixing the exit code makes this failure
*visible* (reproduction R0, fixed: exit 1) but does not make it *go away*.

### 5e. The substrate harness is not fail-closed by accident — it is fail-closed by never running

Worth stating because it inverts the obvious fix. The instinct is "add assertions to the
6-line file". But the 6-line file's entire body is `Object.keys(r).join(', ')` — it never
calls the product. There is nothing to assert against. **The harness is a module-load
smoke test wearing a test file's name**, and the one-line fix only makes the module-load
smoke test honest about module loads.

---

## 6. Deliverables

| Artifact | Path |
|----------|------|
| This report | `projects/fleet-triage/sprint-FAILOPEN.md` |
| Lint rule (calibrated, 4 attempts) | `projects/fleet-triage/fleetlint_failopen.py` |
| Full fleet output (275 repos, 44 findings) | reproduced by `python3 fleetlint_failopen.py repos/*/` |

Note on running the rule in this sandbox: `python3 ../fleetlint_failopen.py` reads a **stale
copy** of the rule from the NAS mount. Copy it to `/tmp` and run it from there, or you will
be reading a two-versions-old detector and drawing conclusions from its phantom findings.
