# ADVERSARY — the strongest objection to our own thesis

Lane 3. 2026-10-01. Written to be believed if it is true, including the parts
that say cut the thing you like.

**Verdict up front: NARROW, do not drop.** Two of your three clauses survive
contact and get stronger; one clause (agent flow-state / CRDT) is dead weight
built on a layer that has never executed. The general formulation exists, and
it is not "claims" — it is **lost update on a declared aggregate**, which is a
50-year-old problem with a known correct answer. That reframing is worth more
than the rest of this document.

---

## 0. I checked your receipt. Two of your three facts are wrong, and the one
## that is right is not the load-bearing one.

Verified against `api.github.com` (no `GITHUB_TOKEN` in env; unauthenticated
worked fine, 200).

**WRONG — "blind keep-both produced invalid syntax."** Confirmed, but *not for
the reason you think, and not safely checkable with the command in your own
evidence directory.*

`nextgen-git-evidence/*.js` are ESM modules (`referral_graph.pins.mjs` upstream,
top-level `await import`). `node --check` on a **`.js`** path is a **silent
no-op** in node v22.19.0 — it returns `EXIT=0` on a file I poisoned with
`const POISON = {syntax error here;`. Your entire evidence directory checks
green under the wrong invocation. Renamed to `.mjs` (control: poison now fails,
`EXIT=1`), the real result:

| file | `node --check` (.mjs) |
|---|---|
| `pins_pr32` | 0 |
| `pins_pr33` | 0 |
| `pins_merged` | 0 |
| `pins_KEEPBOTH` | **1** — `missing ) after argument list` @ L110 |
| `pins_NAIVE_MERGE` | **1** — `Unexpected token '<<'` @ L50 |

So the claim holds. But the break is at **L110, inside a single ~20-line
`check('seed: view ranks all N repos', …)` statement** that *both* branches
rewrote. The union interleaved PR32's tail into PR33's template literal. That
is statement-level hunk conflict — the thing git has always done — not "two
true claims about one fact that the merge cannot represent." You are one step
away from a claim git already handles.

**WRONG — and this is the one that matters.** **Both PRs merged.**
`#32` merged `2026-10-01T20:08:03Z` (`fb2e0411f`). `#33` merged `20:29:03Z`
(`01014092b`), and its `base_sha` **is `fb2e0411f`** — the `#32` merge commit.
It was rebased. The resolution commit is `175a398c`: *"union world-state 15
VERIFIED — assertions re-derived empirically from pin."* And `#33`'s body
predicted it a day early: *"if #32 lands first, this branch rebases."*

Your receipt is not a merge failure. It is **git working**, 21 minutes apart,
with the failure mode named in advance by the agent doing it. That is the
strongest possible evidence *against* the thesis, and it is sitting in your own
cited PR.

**RIGHT, and actually load-bearing — but it is not what you wrote.** Both
branches independently write **`exactly fourteen VERIFIED edges`**. Against
their own base each is correct. After both land, the truth is **15**. That is a
**lost update on a monotonic counter**: two writers each set the value to 14,
and 14 is right for exactly one of them. The prose, the `v.length === 13` vs
`=== 12`, the mass-share recomputation, the md ordinals — all of it is
*downstream of one integer*. This is the receipt. It is not semantic merging.
It is the oldest unsolved-by-git problem in concurrent systems, and it is why
the general formulation below works.

---

## 1. "Adjudication is undecidable at scale" — **concede the framing, keep the
## number**

`${CLOUDFLARE_TOKEN}` is not in my env and I did not deploy (sibling lanes own
the namespace). **I have no measured latency and will not invent one.**

What I can give is the construction that makes the objection moot, and it is
not "most merges are uncontested":

> **The judge is not in the merge path. The *merge operator* is.**

Declare the aggregate and give it an operator from a small algebra:
`+` (monotonic counters), `∪` (sets), `max` (ranks/ordinals), `⊔` (chain tips).
A counter merge is O(1) arithmetic on a 3-field G-Counter. **No agent, no
model, no network, no latency.** 100,000 agents touching 100,000 *different*
aggregates pay exactly zero.

The judge runs only where the operator is **not provably total and
commutative** — and that set is *detectable statically from the type
signature*, not statistically from traffic. You never need the "most merges
are uncontested" empirical claim. You need `is_commutative(op)`, which is a
property of the operator, checkable once per operator type, not once per merge.

The cost model flips from *O(agents) judge calls* to *O(distinct non-commutative
operator types) judge calls*. That is a small constant, and it is the number
the entry should quote.

## 2. "An LLM in the merge path" — **this is the objection that lands, and the
## fix inverts it**

Yes, and the fleet's own measurement is why: **n_eff = 2.18**, best single judge
beats the panel. A judge that is confidently wrong is worse than a conflict
marker — and your instinct is right, but the *remedy* is the thing you already
built and then demoted to a feature.

**The recorded losers are not a logging feature. They are the rollback path.**

- Conflict marker: wrong merge costs a human. Unbounded.
- Authoritative judge: wrong merge is *invisible*. Unbounded and silent.
- **Adjudication event with the loser recorded and reversible:** wrong merge
  costs **one superseding event**. O(1), auditable, no human in the loop.

This answers objection 4's kill-shot — *"is keeping the losers an architecture
or a logging feature?"* — head-on. It is the **safety mechanism**, and it is
**measurable**: the entry should report *the cost of a wrong adjudication*, not
the cost of a right one. A competitor cannot copy that without adopting a
reversible-merge discipline they have no reason to adopt.

**Design consequence you must accept:** the judge is **advisory, never
authoritative**. It proposes; the append-only log disposes. Any wording that
puts a model between a claim and the canon is a bug.

## 3. "One anecdote is not a design" — **the general form, stated**

> **Git's merge operator is defined on text, and text has no algebra. The unit
> of contention is not the claim — it is the *declared aggregate*: any value
> that is a function of state the writer did not fully observe.** Counters,
> ranks, ordinals, "N of M" summaries, chain tips, sets of receipts, and
> share/percentage recomputation are all the same object.

Two instances, both pre-2011, both with known correct answers:

- **Lost update on a monotonic counter** — the `quilt-tools` receipt. 1976.
- **Hash-chain fork** — two tips from two bookings. Your `moth-honest` /
  `quilt-jepa` reseal-forgery work is the *same shape*: a chain proves order,
  not truth, and the seal binds the ledger, not the science.

This is not "our fleet's counter problems." It is the reason git has no
`git merge-count`. The contribution is **making the aggregate declared and its
operator checked for commutativity, with fail-closed behaviour when it is
not** — plus the adjudication record when it fails.

## 4. "Semantic merge already exists" — the difference is determinism, and it
## is a real difference

CodeMerge / git-imerge / SAP merge by a **learned per-project model**: a
probabilistic suggestion, unauditable, silently wrong is the normal case.

This design merges by a **declared operator with a totality check**: either
provably commutative (merge, no model) or **defined to fail closed** (adjudicate,
record both). No model in the path for the common case, and the failure case is
*loud* rather than *confident*. That is the difference, and it is exactly the
axis objection 2 pushes on — so you should make objection 2's answer and
objection 4's answer the same paragraph.

## 5. "Flow-state is not versionable" — **cut this clause**

Three reasons, and the third is fatal:

1. It is the only clause that depends on the broken CRDT layer.
2. It is enormous, perishable, and mostly wrong by the end — versioning cost
   with no correctness value.
3. **It is the clause the one-line thesis does not need.** The thesis survives
   without it. Keeping it buys one sentence of "agents are special" and
   carries every liability in the entry.

`NEXTGEN-GIT-CONCURRENCY.md` currently spends its most confident paragraph
("Agent flow-state is a CRDT, and that is the shippable version") on the least
defensible claim in the document. **That is where a judge will look, and it is
currently undefended.** Demote it to a "future work" line.

## 6. "Your CRDT layer is broken" — **your account is stale, and the truth is
## worse**

You said *"the canary never constructs a CRDT."* **That is no longer true.**
`crdt-canary/crdt-gset__tests__laws.rs` opens:

```rust
//! MERGE-LAW CANARY for crdt-gset. Constructs the type; asserts the CRDT algebra.
use crdt_gset::GSet;
fn mk() -> GSet<u32> { GSet::new() }
```

and asserts four real laws — union cardinality, commutativity (divergence
check), idempotence, associativity. Law 1 (`a.len() == 4` after merging
disjoint `{1,2}` and `{3,4}`) **would** catch a no-op `merge`. Law 2 compares
both directions. It is a good spec, and it is better than the "asserts one FNV
constant" canary you remember.

**The real problem:** `crdt_gset` **does not exist anywhere in the fleet.**
Zero `repos/*crdt*`. Zero matches for `struct GSet` / `impl GSet` in any `.rs`
in the tree. No `Cargo.toml`. **No `rustc` or `cargo` installed** (`which`
returns nothing).

**The canary has never been compiled and has never run.** It cannot fail because
it cannot execute. A law test against a crate that does not exist is a comment
written in Rust. Your "8 ports, 5 byte-identical" framing is the *charitable*
version of the story; the canary does not even have a subject.

### The version that ships without CRDTs — **this is the one to build**

**You do not need a replicated data type. You need an append-only log of
immutable objects.**

```
aggregate := (value, op)          op ∈ {+, ∪, max, ⊔}
merge(a, b) := if total(op) && commutative(op) then a.op(b) else FAIL_CLOSED
adjudication := {claim_a, claim_b, winner, loser, reason, confidence, supersedes?}
```

Everything is **appended, never mutated in place**, so convergence is trivially
satisfied and there is no replica to reconcile. A G-Counter is three integers. A
`FAIL_CLOSED` is not an error path — it is the trigger for appending an
adjudication event, which is the product.

Concretely, the prototype `nextgen-BUILD.md` should target is **~200 lines, zero
CRDT dependencies**, and it demonstrates all of: lost update (the #32/#33
counter), chain fork, fail-closed totality, reversible wrong adjudication, and
replay-from-log. **If a 200-line build with no CRDT library cannot show the
contest judges, the thesis is wrong and we should find out on day 3, not day
12.**

---

## The three sentences that would have changed my mind

1. **Both PRs merged, 21 minutes apart, with #33 rebased onto #32's merge
   commit — and the agent predicted the rebase in the PR body a day early. Your
   receipt is git succeeding, not git failing.**
2. **`node --check` on your evidence directory is a silent no-op because the
   files are ESM saved as `.js`; it returns 0 on a file I deliberately broke.
   The keep-both claim survives only under a `.mjs` check, and the break is
   inside one 20-line statement both branches rewrote — ordinary hunk conflict,
   not unrepresentable meaning.**
3. **The real evidence is one integer: both branches write "14 VERIFIED" when
   the truth is 15. That is a lost update, it is general, and git has never
   solved it — which is the actual thesis, and it needs none of the CRDT work.**

---

**Keep building, but narrow it: ship the declared-aggregate algebra + the
reversible adjudication log, and cut the flow-state/CRDT clause.**
