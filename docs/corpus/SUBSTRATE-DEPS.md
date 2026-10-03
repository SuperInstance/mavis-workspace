# SUBSTRATE-DEPS — the 9 red harnesses, made to actually run

> **9 of 9 green. 11 of 11 family green. 0 red.**
> The fix that turned them red is still in place in every tree — verified, not assumed.
> And the tests, running for the first time in their lives, say four things. Two of them
> are worse than the bug we started with.

**No push was made.** All 11 repos are on local branch `fix/fail-closed-harness`, working
tree clean, `origin/main` untouched. Push command in §8.

---

## 1. The first thing: the previous lane's central premise was wrong, and it was wrong in a way that inverted the conclusion

`SUBSTRATE-FIX.md` §5a says, in a recommendation that shaped the whole lane:

> `observation-primitive` **is not a repository in this fleet** — `find /workspace` returns
> nothing, and **it is not published**.

The first half is true. The second half is false, and it is false in the way that matters.

```
GET https://api.github.com/repos/SuperInstance/observation-primitive   ->  HTTP 200
  full_name:  SuperInstance/observation-primitive
  description: The canonical substrate atom: observation as fundamental primitive.
                FNV-1a signed, type-safe, federation-ready.
  default_branch: main      pushed_at: 2026-09-21T23:57:20Z      size: 7
  contents:  index.d.ts (1257)  index.js (4178)  package.json (560)  test.js (1006)
  HEAD: bc98ee4  "feat: observation-primitive v0.1.0"
```

It is published. It has been since 21 September. It ships `index.js` and it exports
**every symbol the family asks for**:

```
Observation, OPCODES, EVIDENCE, FORGETTING, fnv1a64, fnv1a64Hex, int16Dials,
FNV_OFFSET, FNV_PRIME
```

against a call-site requirement of `fnv1a64`, `fnv1a64Hex`, `int16Dials`, `Observation`.

**The reason for the wrong conclusion is the part worth keeping.** `observation-primitive`
was simply never cloned into `/workspace/projects/fleet-triage/repos/`. `find /workspace`
returned nothing, and *absence from this disk was read as absence from existence*. One
`curl` settled it. This is the fleet's own standing lesson — **a search miss does not prove
non-existence** — and it is the first time in this fleet I have watched it fire on a
conclusion that was about to drive eleven real decisions.

I checked before acting, so nothing was built on the error. But note what it would have
cost: I had already worked out, and was about to execute, a plan to re-point the family at
`substrate-canary-pin` and to **hand-write the missing `Observation` class** from the shape
of its three call sites. That plan was reasonable, it was internally consistent, and it
would have replaced a real, published, 4.2KB implementation with a plausible forgery of
one, and then reported 11/11 green. **A search miss that gets promoted to a finding becomes
a stub that gets promoted to a green tick.** That is the whole shape of this family, in one
step.

I have left the 12th repo out of the fleet clone set as a **separate, smaller** observation
rather than fixing it here — see §7.

---

## 2. The fix: one field per repo

The family declares siblings as `file:../X`. That path resolves only if a directory named
`X` happens to sit next to this one. It is unresolvable from a fresh clone, from CI, and
from anyone's laptop. The siblings are all published, so npm can fetch them itself.

```diff
-    "@superinstance/observation-primitive": "file:../observation-primitive"
+    "@superinstance/observation-primitive": "github:SuperInstance/observation-primitive"
```

`substrate-traverse` gets two, and its second is the one that was always going to be
missed:

```diff
-    "@superinstance/substrate-witness-log": "file:../substrate-witness-log"
+    "@superinstance/substrate-witness-log": "github:SuperInstance/substrate-witness-log"
```

**The entire change is the `dependencies` block of `package.json`.** No product code, no
test, no harness, no assertion, no CI file was touched. `index.js` appears in no diff.
The `process.exit(1)` from the previous lane is present in all 10 harnesses that have a
handler (`substrate-attest` never had one — it is the shape-B vacuous harness, and it was
already exiting 1 on a crash).

Per-repo patches, each verified to apply to a pristine `main`:
`substrate-fix-artifacts/dep-fix-per-repo/substrate-*.patch`.
Both lanes combined: `substrate-fix-artifacts/substrate-deps-linked.patch` (661 lines, 11 repos).

---

## 3. Proof — two independent routes, because one would have been an assertion

**Route A — a stranger.** `git clone -b main` from **GitHub**, not from the local mirror.
No sibling checkouts present, no `node_modules`, no local anything. Then the previous
lane's fail-closed patch, then my dependency fix, then the exact two commands CI runs.

```
REPO                       cloned  fail-closed  install  test
------------------------------------------------------------------
substrate-attest           main    applied      0        0    <- was RED
substrate-bundle           main    applied      0        0    <- was RED
substrate-contest          main    applied      0        0    <- was RED
substrate-delegate         main    applied      0        0    <- was RED
substrate-merger           main    applied      0        0    <- was RED
substrate-revoke           main    applied      0        0    <- was RED
substrate-traverse         main    applied      0        0    <- was RED
substrate-withdraw         main    applied      0        0    <- was RED
substrate-witness-log      main    applied      0        0    <- was RED
substrate-canary-pin       main    applied      0        0    (was green)
substrate-membership       main    applied      0        0    (was green)
------------------------------------------------------------------
9 of 9 previously-red repos are green.  0 red.
```

**Route B — the real branches.** `rm -rf node_modules`, then the real `npm install` and
`npm test` in `/workspace/projects/fleet-triage/repos/substrate-*` on
`fix/fail-closed-harness`, working tree as committed. **11 green, 0 red.** Not a simulation.

**Route C — the whole family at once**, as a stranger would actually use a substrate:

```
npm install github:SuperInstance/{observation-primitive,substrate-attest,substrate-bundle,
  substrate-canary-pin,substrate-contest,substrate-delegate,substrate-membership,
  substrate-merger,substrate-revoke,substrate-traverse,substrate-withdraw,
  substrate-witness-log}
-> added 24 packages in 16s
```

Driver: `substrate-fix-artifacts/rollout_deps.py`. Raw output:
`substrate-fix-artifacts/rollout_results.json`.

---

## 4. What the tests then say

They had never run. Here is what they say now. **Three of the four findings below are
invisible to the suites, which are all green** — that is the point of reporting them.

### F1 — six of the substrate's own eight products cannot be written into the substrate's own memory

`substrate-witness-log` is described in its own header as *"the substrate's typed memory."*
`WitnessLog.append()` does:

```js
const o = observation instanceof Observation ? observation : new Observation(observation);
```

and `Observation`'s constructor **hard-requires four fields**, throwing otherwise
(`observation-primitive/index.js:57`):

```js
if (!subject || !predicate || object === undefined || !issuer) {
  throw new Error('observation requires subject, predicate, object, issuer');
}
```

So I asked the only question nobody in this family has ever asked — *can each product's
output go back into the log?* — and ran it:

```
PRODUCER                 APPENDS?   missing required fields
Observation (external)   OK         (none)
merge()                  OK         (none)
attest()                 THROWS     subject, predicate, object, issuer
contest()                THROWS     subject, predicate, object, issuer
revoke()                 THROWS     subject, predicate, object, issuer
withdraw()               THROWS     subject, predicate, object, issuer
delegate()               THROWS     subject, predicate, object, issuer
bundle()                 THROWS     subject, predicate, object, issuer

appendable: 2    not appendable: 6
```

The scars do not use `issuer`; they use `attestor`, `contestor`, `revoker`, `withdrawer`,
`from`, `name`. The two survivors survive by coincidence: `merge()` renames `merger` to
`issuer`, and an `Observation` is already an `Observation`.

**Six of eight opcodes produce records the substrate's own ledger rejects.** The witness log
is where the family says scars persist forever — `withdraw` literally sets
`is_audit_trail: true` on a record that cannot be appended to the audit trail.

This is a **finding, not a regression**, and I have left it exactly as it is. It is also
structurally invisible to the current suites and always was: every harness loads one repo
and prints its export names, so a contradiction that exists *only between* two repos has no
test that could ever reach it. It appeared the first time I composed the family, which is
the first time anything has.

**Not fixed. It needs a decision about the canon** — whether a scar *is* an observation, or
is a second type that the log must accept. That is a design call, not a packaging call.

### F2 — the canary self-check is structurally incapable of failing

`substrate-canary-pin` exists to pin one hash. It ships a function that verifies that hash.
It cannot detect that hash being wrong.

```js
const CANARY_HASH = 0x024a555471370b18dn;                 // 17 hex digits
const expected: '0x024a555471370b18d',                     // 19-char string
match: h === CANARY_HASH,                                  // bigint vs bigint
```

`0x024a555471370b18dn` is a **bigint literal**, so the parser drops the leading zero and
`CANARY_HASH === 0x24a555471370b18d`. `match` therefore compares a number to itself and is
`true` by construction. The `expected` **string** — the field a human actually reads — is
compared to nothing, ever:

```
verifyCanary():
  hash_hex : 0x24a555471370b18d     (18 chars)
  expected : 0x024a555471370b18d    (19 chars)
  match    : true
  hash_hex === expected ?  false      <-- the pair a reader checks disagrees
```

**The product knows it is wrong and the harness ignores it.** I changed the FNV prime by one
bit — valid JavaScript, identical exports, nothing else touched:

```
FNV_PRIME = 0x100000001b3n   ->   0x100000001b4n

harness output :  OK: CANARY_INPUT, CANARY_HASH, fnv1a64, fnv1a64Hex, verifyCanary
harness exit   :  0
product output :  verifyCanary() -> {"hash_hex":"0x0ba6a5677a2d8778",
                                      "expected":"0x024a555471370b18d","match":false}
```

The product reported its own catastrophic failure, in clear text, on stdout, in the same run
that returned success. This is stronger than the previous lane's D5, and it is the same
disease seen from the other side: D5 found that the harness never calls the product. **F2
finds that even when the product is called, is wrong, and says so, the harness is still a
module-load smoke test wearing a test file's name.**

### F3 — one hash, three renderings, and the parity claim is verified by nothing

```
substrate-canary-pin  .fnv1a64Hex("x")  ->  "0xaf63f54c86021707"   0x-prefixed
observation-primitive .fnv1a64Hex("x")  ->  "af63f54c86021707"     bare
Observation.id                          ->  "9d08880d85196095"     bare, 16 hex
canary-pin .expected                    ->  "0x024a555471370b18d"  0x, 17 digits
```

**Every identifier in the substrate is one of these strings.** Two sibling packages export a
function of the same name that returns different formats, and nothing in the fleet compares
them. I looked for the comparison the READMEs promise and want to be precise about what I
found, because the honest answer is more interesting than the accusation I was ready to
make.

All 11 READMEs say: *"Verified by `tests/stress/01_fnv1a64_fuzz.js` (29 pathological
inputs, all green)."* That file **exists** — at
`research/cargo-line-tycoon/tests/stress/01_fnv1a64_fuzz.js`, 144 lines, 29 cases, genuinely
cross-language (TS / Rust / Python / C99). It is a real test and I am not claiming otherwise.
But it lives in a different repo, so the relative path in 11 READMEs **does not resolve from
any of the 11 substrate repos** — a stranger who follows the citation finds nothing. And:

1. **It has no exit code.** `grep -c 'assert|process.exit|throw'` → **0**. Line 133 prints
   `✗` on failure and the process still exits 0. It is a report to no one — the exact defect
   the previous lane fixed in the harnesses, still live in the parity test.
2. **Its canary check cannot fail.** Line 129:
   `const cv = tsHash === '0x024a555471370b18d' || tsHash === '0x24a555471370b18d' : true;`
   Both the correct 16-digit form and the 17-digit form satisfy it. The `||` exists to
   tolerate a known ambiguity, which guarantees it can never resolve it.
3. **It normalises the very thing under test away.** Lines 130–131 compare languages via
   `.replace(/^0x0/, '0x')` before comparing — leading zero stripped, so cross-language
   disagreement about it is invisible by construction.
4. **It passes when the language is absent.** `const pyMatches = !pyHash || ...` — if the
   Python half fails to run and produces nothing, the check is `true`. An undeclared failure
   selects the weaker path, and the weaker path is the default.
5. **It does not run for a stranger.** Line 48 hardcodes
   `/workspace/research/cargo-line-tycoon/substrate/py` — a path on this machine.

So the cross-language parity claim is **relationally** verified (the four implementations do
agree with each other, modulo leading zeros) and **absolutely** verified by nothing. "Pinned
to the fleet canary" is asserted in 11 READMEs and checked against a constant that is wrong
in one rendering and accepted in both.

### F4 — measured: 0 of 11 harnesses would notice a wrong hash

I replaced `fnv1a64Hex` with a constant returning `0xdeadbeefdeadbeef` in every product. Every
identifier in the family becomes the same wrong string. The products still load and still
export the same names.

```
10 of 11 harnesses: exit 0, printing OK.
```

(The 11th, `substrate-canary-pin`, went red on my mutation — but because my regex mangled
the function *definition* into a duplicate declaration, i.e. a `SyntaxError`. Re-run fairly
with a one-bit prime change, it also exits 0. **0 of 11 detect a wrong hash.**)

This is the honest boundary of this lane. **Green here means the module loaded.** It does not
mean the product works, because the family has no test that calls a product and compares a
result to anything. The previous lane called this §5b and declined to fix it as out of scope;
I agree it is out of scope, and I am reporting it as the ceiling on every green in §3.

---

## 5. Which of the 9 are actually runnable at all

All nine. **None needed a stub, because none of them needed a sibling that does not exist.**

| # | Repo | Was missing | Found where | Runnable |
|---|---|---|---|---|
| 1 | `substrate-bundle` | `observation-primitive` | published, `bc98ee4` | **yes** |
| 2 | `substrate-contest` | `observation-primitive` | published | **yes** |
| 3 | `substrate-delegate` | `observation-primitive` | published | **yes** |
| 4 | `substrate-merger` | `observation-primitive` | published | **yes** |
| 5 | `substrate-revoke` | `observation-primitive` | published | **yes** |
| 6 | `substrate-withdraw` | `observation-primitive` | published | **yes** |
| 7 | `substrate-attest` | `observation-primitive` (+`int16Dials`) | published, all four exports present | **yes** |
| 8 | `substrate-witness-log` | `observation-primitive` (+`Observation`) | published, real class | **yes** |
| 9 | `substrate-traverse` | `substrate-witness-log` | published, real package | **yes** |

`substrate-attest`'s `int16Dials` — destructured, never called — exists. It does not need
a stub and I did not give it one.

---

## 6. The packaging pattern, fixed for a stranger

The defect was structural, not local, and it was in `package.json` rather than in any
sibling's checkout, so fixing it fixes it for everyone:

- `file:../X` → `github:SuperInstance/X`. npm resolves it on any machine, any CI runner,
  any single-repo clone.
- `npm install` in all 11 now exits 0 **and actually installs the product**, which is the
  difference between §3 and the previous lane's D4.
- `substrate-traverse` → `substrate-witness-log` was a second, independent instance of the
  same bug and is fixed the same way.

**One residual, not fixed, flagged for your call:** `package-lock.json` is **gitignored** in
all 11 (`.gitignore:2`). So `github:` resolves to whatever `main` is *at install time* — today
`bc98ee4701f646d168c6f444c36b2163532cb580`, tomorrow whatever ships next. The family is
therefore **not byte-pinned in CI**, which sits badly next to a doctrine of byte-exact
cross-language parity. Two fixes, both one line, both a policy decision I am not making for
you:

- pin in the spec: `"github:SuperInstance/observation-primitive#bc98ee4"`
- or commit the lockfile (it is already generated and correct, and it already pins the SHA)

---

## 7. Left undone, deliberately

- **F1 is not fixed.** It is a canon decision: is a scar an observation, or a second type
  the log must accept? I did not touch product code to make a suite pass, and I did not
  invent a second record type to make the log accept a scar.
- **F2/F3 are not fixed.** Choosing the canonical canary rendering and making
  `verifyCanary()` able to fail is a one-line change in `substrate-canary-pin`, but it
  changes a published constant's surface, and it is a claim about the fleet's canon that
  should be made deliberately and in the open.
- **`observation-primitive` is not in the fleet clone set.** It is a real, published member
  of this family and 11 of its 12 siblings are mirrored locally. Worth adding; it is a
  clone, not a decision, so I did not fold it into a lane about dependency resolution.
- **§5c of the previous lane stands** — 8 of 11 declare `"types": "index.d.ts"` and do not
  ship it. Unchanged by this lane.

---

## 8. Push

Not pushed. All 11 on local `fix/fail-closed-harness`, working tree clean, `origin/main`
untouched. Both lanes are on the same branch, in order: the fail-closed fix, then the
dependency fix.

```bash
cd /workspace/projects/fleet-triage/repos
for d in substrate-*; do git -C $d push -u origin fix/fail-closed-harness; done
```

Or without history, each verified to apply to a pristine `main`:

```bash
cd /workspace/projects/fleet-triage/substrate-fix-artifacts/dep-fix-per-repo
for p in substrate-*.patch; do (cd ../../repos/${p%.patch} && git apply -p1 /"$(realpath $p)"); done
```

---

## 9. The three sentences

**A missing sibling and a missing clone look identical from inside the workspace, and only
one of them is a bug.** I came into this lane one `curl` from replacing a published 4KB
implementation with a plausible forgery of it and reporting 11/11 green.

**The fix made the family honest and immediately proved that honest and green are different
words.** 9 of 9 green is true and worth having. It is also worth exactly this much: 0 of 11
harnesses detect a wrong hash, and 6 of 8 products cannot be written into the substrate's
own memory.

**A substrate that can now fail has told us, for the first time, what it is made of.** The
canary is pinned to a constant that is wrong in one of its renderings and checked by a
predicate that accepts both. The scars are supposed to live forever in a log that rejects
them on construction. Neither fact was hidden by a green tick. Both were hidden by one —
and now both are simply on the table, which is what the exit code was for.
