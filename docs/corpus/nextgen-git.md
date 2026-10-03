# nextgen-git — version control for concurrent claims

**Status: STUB — §0 verification + §1 thesis + §2 steelman are done and checked against real
commits. §3–§7 are TODO.** Written 2026-10-01T20:52Z. Deadline **2026-10-14**.

> **Headline finding, verified:** the brief's thesis is right but *understated*, and the brief's
> supporting detail about the failure mode is **wrong**. Git's conflict detector is a text-identity
> detector. On this merge it raised **5 conflicts, exactly 1 of which was semantically
> load-bearing** — and the single most important fact in the entire merge, *the edge count is 18 on
> both branches but 19 after merging*, **produced zero conflict markers**, because both agents had
> independently written the identical literal `18`. Git flagged the prose and missed the
> arithmetic. That is the demo, and it is reproduced from real commits in
> `nextgen-git-evidence/`.

---

## 0. Verification — `quilt-tools#32` / `#33`, checked not trusted

Sources: `SuperInstance/quilt-tools`, commits `a98a5c5` (#32), `7caf5a3` (#33), `35d3482` (merge).
PRs #32 and #33 both **merged** (2026-10-01T20:08:03Z and 20:29:03Z). Evidence artifacts saved to
`nextgen-git-evidence/`; the three-way merge was re-run locally with `git merge-file`.

### 0a. What the three states actually assert

`experiments/referral_graph.pins.mjs` — the fleet's own invariant checker:

| assertion | #32 `a98a5c5` | #33 `7caf5a3` | merged `35d3482` |
|---|---|---|---|
| `seedBooked === 18 && seed.rows.length === 18` | **18** | **18** | **19** |
| `byRepo['fleet-murmur']` | **2 × VERIFIED** | **3 × VERIFIED** | 3 × VERIFIED |
| `v[0].weight` (top of view) | 2 × | 3 × | 3 × |
| `v[4].repo` (4th in view) | **`delta-shape`** | **`git-agent`** | `delta-shape` |
| view length | 13 | 12 | 13 |

**Every cell in columns #32 and #33 was correct against its own base tip.** They descend from a
common main. #33's PR body says so outright: *"Counts here assume main without it; if #32 lands
first, this branch rebases."* The brief's core claim is **TRUE**: merged truth is 19 edges /
15 VERIFIED / 4 PENDING, exactly as stated in the merge commit message.

Three findings sharper than the brief's version:

**F1 — the two branches agreed, and both were wrong.** Both wrote the identical literal `18` on the
identical line 28. `git merge-file` reported **no conflict there**, because there was no textual
change. Yet after the merge the true value is 19, so **both branches' assertions were false the
instant they combined.** Two agents, independent, correct — and mutually incompatible. Git cannot
represent that, because the representation *is* the text, and the texts match.

**F2 — the merged view is a state neither branch ever asserted.** `35d3482` takes `fleet-murmur =
3×VERIFIED` from #33 and `delta-shape` at `v[4]` from #32. Neither agent ever believed that
combination. It is a *novel* state, and it was produced by a human picking sides.

**F3 — conflict detection on this merge: 5 hunks, 1 load-bearing.**

| # | lines | content | semantically load-bearing? |
|---|---|---|---|
| 1 | 50–57 | `// Pin 3` narrative prose about fm mass | **no** — inside a `//` comment, inert |
| 2 | 97–103 | `v[0].weight === 2 *` vs `=== 3 * VERIFIED_WEIGHT` | **YES — the real disagreement** |
| 3 | 128–132 | byte-identical `check('…exactly fourteen VERIFIED edges…')` on both sides | **no** — identical text, spurious |
| 4 | 485–542 | Pin 3o vs Pin 3p blocks | additive; "keep both" is correct here |
| 5 | 791–797 | `currency` panel string | no — display prose |

Git's one true positive is hunk 2, and it fired **only because the two branches happened to write
different literals for the same quantity.** Had either computed the value instead of hardcoding it,
git would have seen identical source and stayed silent. **Recall on this class of disagreement is
accidental, not structural.** Meanwhile hunk 3 shows the opposite failure: git flagged two
textually identical lines. So the detector is not merely weak here — it is **unreliable in both
directions**, and its errors are not correlated with which conflicts matter.

### 0b. Corrections to the brief

**CORRECTION 1 — "blind keep both produced invalid syntax" is false. I tested it.**
Stripping the markers and keeping both sides (`pins_KEEPBOTH.js`) → **`node --check` passes, the
file parses.** More than that: keep-both is *loud*. It yields two `check('…fm leads with triple
mass…')` calls, one asserting `2*VERIFIED_WEIGHT` and one `3*`, and it splices
`v[4].repo === 'delta-shape'` together with `v[4].repo === 'git-agent'` in a single `&&` chain —
always false. The suite goes **RED**. That is the *good* outcome.

The dangerous outcome is the one that actually happened: a human **picked a side**, and the
resolution is now byte-indistinguishable from a merge that was never contested. The correct threat
model is **not** "keep both breaks the build." It is: **git hands you a merge that looks exactly
like a clean merge, and only you know which of the 5 conflicts mattered.** So the entry must not
be "we catch bad merges." It must be: **we make it impossible to resolve a disagreement by
picking a side, because the disagreement is an object and picking a side is not an operation on it.**

**CORRECTION 2 — a human was in the loop and the commit says so.** `35d3482` is authored by
`Z User <z@container>` and titled *"the wave-63 **determinizer**."* The fleet's answer to this
problem was a person hand-deriving the semantic merge. Data point for the thesis; but it also means
our demo must not read as "a fancier determinizer." The claim is narrower: **the determinizer step
should be a machine-checkable operation on a first-class object, not a human judgement call.**

**CORRECTION 3 — prior art inside the fleet, which a judge will find.** #33's body: *"md ordinals
follow merge order — the chain hash, not prose, is canonical."* The fleet already has a **chain
hash over ordered state** and merge-order ordinals. That is half the proposal and it predates us.
See §2.2 — this is the strongest objection to the thesis.

### 0c. Tooling — two blockers, flagged not worked around

- **`GITHUB_TOKEN` is unset in this sandbox** (verified against `env`). I used the unauthenticated
  API and a partial clone. Enough to verify; **not** enough to push or open PRs.
- **`CLOUDFLARE_TOKEN` is unset.** `api.cloudflare.com` returns **403** unauthenticated and there is
  **no `wrangler` binary on `PATH`** (only stale logs from a prior lane under
  `~/.config/.wrangler/`). The brief's claim that a `wrangler` CLI "is already authenticated" **does
  not reproduce here.** I am not deploying to Workers regardless (sibling lanes own those
  namespaces) — but the Durable Objects coordination layer is currently **unbuildable, not merely
  unbuilt.** §5/§6/§7 are blocked on this token landing.
- `plato-tile-relation` (`CONTRADICTS`) and the 8 CRDT ports are **not** in the local `repos/`
  cache and I cannot inspect them without the token. Those claims are **UNVERIFIED from this
  sandbox** and are carried forward as asserted, not established. Per the brief, the CRDT layer is
  to be treated as unproven regardless.

---

## 1. The thesis — 54 words, no jargon

> Git stores the changes. It has no way to store a claim — a statement about what is true, who
> believes it, and on what evidence. So when many agents state the same fact differently, Git can
> only pick one and discard the rest. We make claims the object you merge, not the lines.

**Refined by the evidence (§0), for the demo title card:**

> Git's conflict detector compares text. So when two agents independently reach the *same*
> conclusion, Git sees agreement — and the moment they combine, that conclusion becomes false. We
> merge the claims, so the disagreement survives instead of disappearing into a clean merge.

---

## 2. The steelman, and the answer

### 2.1 "This is a linter, not a version control system"

> Git merges text well. `35d3482` was resolved. Pins went green. The fleet moved on in twenty
> minutes. A conflict caught by a merge tool is a conflict caught by a linter, and linters lose to
> `pre-commit` plus a code owner. The load-bearing disagreement was 1 line. That is not a new kind
> of problem, it is a careful merge.

Strong, and I do not think it is *wrong* — it is wrong about which resource is scarce. The merge
was the cheap part; `35d3482` changed **2 files, 54 insertions, 18 deletions**, and the human
re-derived the fleet's global invariant (19/15/4, fm at 3×, delta-shape at v[4], both receipts
live, 119 pins) before writing it down. Delete that human and there is no process at that commit.

The sharper loss is on the *detector*, not the merge. §0a F3 is the real damage: **5 conflicts
raised, 1 load-bearing, and the most consequential fact in the merge flagged zero times.** A linter
tells you when *text* collides. It cannot tell you when two agents' conclusions collide, because at
the instant of merging, theirs look identical. At 100,000 agents this inverts: the more redundant
the fleet — the *better* it is working — the more disagreement is textually invisible. **Redundancy
is what makes agent fleets safe, and it is exactly what defeats a text-identity detector.** That is
not a linter gap. It is the wrong data type.

And the human who "caught it" is not a defence at 100k agents: the merge that was handled carefully
here was handled carefully *by a person who had ten minutes and the whole fleet in context.* There is
no such person at scale, so the disagreement does not get resolved — it gets **picked**, silently,
and becomes a clean merge.

### 2.2 The objection that bites: "the chain hash already exists in the fleet — you are late"

#33: *"the chain hash, not prose, is canonical."* If a chain hash over ordered state is adjudication,
the thesis is dead.

It is not, and the distinction is the entry. **A chain hash is a total order.** It answers *which
ordering came first* and nothing else. It cannot answer *which ordering was true* — because on this
fleet `18` and `19` are **both true**, at `a98a5c5` and at `35d3482` respectively, and a total
order makes one of them the current answer while the other is, formally, false forever. Nothing in
a hash chain can say *"this was believed, and is now known false."*

The proof is in this same repo, three commits earlier: `df733e7` — **"edge #14 rebuilt PENDING."**
An edge was booked VERIFIED, lost, and rebuilt, all on one linear history that gives you no way to
distinguish "we changed our mind" from "this was never true." Total order + hash cannot represent
a belief that changed. **Canon can.**

So the chain hash is our **floor, not our ceiling** — we inherit it as the witness log. It is not
the product. Best question we will get; the answer is `df733e7`.

---

## 3. User-first guides (agentic user) — TODO

- **3.1 The agent working alone** — TODO
- **3.2 The agent inheriting another's branch at hour 3** — TODO. Must answer brief Q1–Q4.
  **Hypothesis to attack:** flow-state and claim-adjudication are **one object**. A live hypothesis
  *is* an unadjudicated claim about the repo; at compaction it becomes a claim that was never
  adjudicated and never recorded — which is exactly F1. If that holds it collapses two features
  into one and is a much stronger entry. §0a F1 is the first empirical instance: `18` was a claim
  that two agents held and neither could see.
- **3.3 The human adjudicating a conflict between two agents** — TODO

## 4. Mapping table — TODO

Carry the brief's six rows, each justified or cut. **Predicted cut: `branch = named pointer` →
`claim`.** A branch is not a claim; a branch is a *locus of claims*. If the mapping cannot survive
that distinction it is a relabel, and relabels do not win.

## 5. Concurrency design, one paragraph — TODO (blocked on CF token)

Required: unit of contention, what a merge is, what a conflict is. **If I cannot answer these the
thesis is not a design and the demo will not land.** Intended, unproven: unit of contention = **the
claim**, not the file. Merge = **adjudication of a claim set under a canon gate**. Conflict = **an
unrefuted CONTRADICTS edge a gate cannot decide** — kept and surfaced, never silently dropped.
Durable Objects give a natural serialization point per claim key. **Cannot be built or tested
without `CLOUDFLARE_TOKEN` (§0c).**

## 6. Demo script, 5–10 minutes — TODO (spine already fixed)

Run the real `git merge-file` on `pins_pr32.js` / `pins_pr33.js`, live, in the demo. Show:
git raises 5 conflicts → all 5 resolved by picking a side → `node --check` passes, suite green,
**and the 18→19 disagreement was never among the 5.** Then our system: refuses, and shows the two
claims side by side with receipts and a gate that records which is canon **and why**. Both halves
already exist in `nextgen-git-evidence/`. No narration needed — the artifacts speak.

## 7. 3-week plan, highest risk first — TODO

Highest risk is **not** storage (D1/R2 are adequate). It is **not being a one-trick anecdote** — if
the demo only works on `#32/#33` a judge will say so. Need a second, adversarial instance, and a
fallback if the CRDT layer stays unproven.

---

## Next actions

1. Land `GITHUB_TOKEN` + `CLOUDFLARE_TOKEN` in the sandbox. *(blocking §5/§6/§7)*
2. Verify `plato-tile-relation` `CONTRADICTS` and the 8 CRDT ports — unverifiable from here.
3. Answer §3.2 Q1–Q4 and test flow-state ≡ claim. Biggest single prize.
4. Build the second, non-rigged demo instance before writing §7.
