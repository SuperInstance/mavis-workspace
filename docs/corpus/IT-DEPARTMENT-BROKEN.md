# IT-DEPARTMENT: the harness is broken, and that is the report

2026-10-02 04:45Z. I built a three-arm A/B loop experiment (single JEV call vs.
refracted 3-call iteration vs. a free local lexical arm), scored it against both
a JEV judge and ground truth, with a cumulative ledger that was supposed to be
the "gets better every time" part.

**It did not run. Every JEV call failed. The ledger is empty, and the numbers it
printed — 0/10 truth-correct on every arm, 0 judge scores ≥4 anywhere — are
artifacts of my own broken harness, not findings.**

## What the first run printed, and why none of it is real

```
arm             answered   truth-correct   judge>=4
A_single              10            0/10          0
B_refracted           10            0/10          0
C_free                10            1/10          0
```

`0 ≥ 4` **for every arm including the free lexical one** is not a finding, it is
a signal that the judge block never ran. **A result where the instrument scores
nothing at all is the instrument failing, and I should have said so before
writing the next line of code.**

## The actual cause

Every `jev()` call returned `__err__`. Probing the endpoint directly:

```
no model field      -> 422 {"loc":["body","model"],"msg":"Field required"}
model=jev-1.13.0    -> 400 {"error_type":"api_usage_error","message":"Invalid request."}
```

So the contract **now requires `model`** — and supplying it still fails. I
tried six model ids and four question shapes. None were accepted.

**The JEV-MERGE lane ran 693 calls earlier tonight with zero malformed responses,
using `model: jev-1.13.0` and `{q: {type, instructions, criteria}}` — the exact
shape I sent.** It is not reproducible now.

## Why this is worth recording rather than hiding

**An API contract rotted inside a single session.** A lane documented a working
shape, I read the documentation and the report, built to spec, and the spec no
longer works. That is not a subtle failure and it is not the lane's fault.

> **A recorded interface is a claim about a moment, not a fact about a duration.**

This is the same shape as the stale `RESOLVER-DEFECT.md`, the same shape as the
conservation paper citing a directory that never existed, and the same shape as
`CLOUDFLARE_API_TOKEN` versus `CLOUDFLARE_TOKEN` — a name or shape believed
correct and never re-checked against the running service.

**Three lanes in this project died on exactly this** and I attributed it to
scope. It was partly this.

## What is left of the idea, and what I will not claim

The design is sound and I still think it is worth running when the contract is
restored:

- **A single call, a refracted 3-call iteration, and a free local arm** on the
  same prompts, so that "does iterating help" is measured rather than asserted.
- **Ground truth on the checkable prompts**, so the judge cannot grade itself.
- **A ledger that retires components that do not earn their place** rather than
  accumulating cleverness. Self-improvement measured as *which parts get turned
  off*.

**And the prediction stands, untested:** iterating a 2-vote signal converges to
a bland point, so **B should lose to C on ground truth even if B wins on the
judge.** If that is what happens, the judge is the part that needs retiring —
and the ledger should say so.

## The one thing I will fix before re-running

**Never let a scoring block report zeros.** If the judge returns nothing, the
run is `INVALID` and says so. A failed instrument must be loud, because this
project's entire subject is instruments that report success while broken.

```python
if judged == 0:
    raise SystemExit("INVALID RUN: the judge produced no scores. "
                     "Do not report a ledger from this.")
```

That check goes in before the next attempt, not after.
