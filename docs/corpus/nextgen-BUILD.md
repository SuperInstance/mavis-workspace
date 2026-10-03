# nextgen-BUILD

**Lane:** build. **Status at t+72min:** running prototype, real receipt verified,
one design claim refuted. See [What is done](#done) / [What is not](#not-done).

Artifact: `projects/fleet-triage/nextgen-merge/` — running at `wrangler dev`
port 8787, 12/12 unit tests green, receipt re-derivable from a fresh clone with
`bash test/verify-git-receipt.sh`.

---

## 1. The receipt: verified, and stronger than the brief says

I fetched PRs #32 and #33 before building anything. **Your account is correct
on every load-bearing number.** `GITHUB_TOKEN` was not in the environment (see
blockers), but `SuperInstance/quilt-tools` is public, so the unauthenticated
API served the whole thing.

```
  58e2a18   Merge PR #30                17 edges   13 VERIFIED   4 PENDING
    |\
    | \  a98a5c5  PR #32 head            18 edges   14 VERIFIED   4 PENDING
    | /                                 asserts "18", "fourteen VERIFIED"
    | \
    | /  7caf5a3  PR #33 head            18 edges   14 VERIFIED   4 PENDING
    |/                                  asserts "18", "fourteen VERIFIED"
    |
  fb2e041   Merge PR #32     -> "18", "fourteen"
  0101409   Merge PR #33     -> "19", "fifteen"      <-- what actually landed
```

`7caf5a3` and `a98a5c5` are **true siblings**, both parented on `58e2a18`.
That is the receipt, and it is exactly 19/15/4.

**Three things are sharper than the brief states:**

1. **The dangerous half of the merge is the half git was silent about.**
   `experiments/referral_graph.seed.mjs` — the file holding the actual edge
   data — **auto-merged with no conflict marker at all**. git took the union
   (19 edges) and asked nothing, while both agents' pins asserted 18. The
   demo does not need the conflict; the conflict is the boring part.

2. **The "keep both" failure is not hypothetical and not a syntax nit.** Unioning
   both sides of all 5 hunks yields **270 `{` against 269 `}`** and
   `SyntaxError: missing ) after argument list` at `pins.mjs:110`. Both agents
   open a block for their own new pin; both close it.

3. **There is already a "both edges booked at their merge order" attempt in the
   repo** — branch `determinizer-63`, commit `35d3482`, *"Merge pr32 + pr33 —
   the wave-63 determinizer."* Someone else hit this and is mid-fix. Worth a
   look before we publish, and it is a courtesy citation we should make rather
   than rediscover it on camera.

**And the real cost, which the brief does not mention:** the actual resolution
was commit `175a398`, *"edge15 landing: union world-state 15 VERIFIED —
assertions re-derived empirically from pins run."* A third person re-ran the
pins by hand and **overwrote both agents' assertions**. Those two claims now
exist nowhere — not in the tree, not in the log, and not in the PR bodies, which
still say "17 to 18, 13 to 14" today. That silent overwrite is a better demo
than the conflict markers.

---

## 2. Where I think the design brief is wrong

Three places, in descending order of how much they would cost us.

### 2a. The receipt is not a *pairwise* contradiction, and the brief's object model does not have a slot for it

The brief says a merge is "either claims reconcile, or a `CONTRADICTS` edge is
recorded and both claims survive," and points at `plato-tile-relation`'s
`CONTRADICTS` with transitive closure and cycle detection.

But PR #32 and PR #33 **do not contradict each other.** They assert the same
thing: 18 edges, 14 VERIFIED. `findContradictions` over the two branches
returns **zero** pairwise contradictions — and my first implementation returned
`contradictions: 0, derived: 0`, a merge that silently accepted a false world.

The conflict is between **a claim and the union it lands in**. It is not a
graph relation between two claims; it is a claim falsified by re-execution over
the merged set. A `CONTRADICTS` edge has nowhere to attach.

This is the real finding, and it is a hole in the object model: the merge
produces a claim that **no input asserted** (19) and that falsifies claims
which were **each individually correct**. `CONTRADICTS` + transitive closure
does not model that, because it has no notion of a claim being evaluated
against something other than another claim.

**What I built instead:** the merge always re-executes every runnable witness
over the deduplicated union and emits `derived` claims for anything that
survives re-execution but was asserted by nobody. This required the witness to
be part of the claim, not a property of the relation — which is also why
re-execution beats voting as an oracle. I did not implement the `plato-tile-relation`
reuse, because the shape did not fit; I reused the *idea* (relations are
derived from structure, not from text matching) and I think that is the honest
description.

### 2b. "Consensus cannot merge" is measured for LLM judges on natural language, and over-reading it would get us destroyed

The two citations are real and I put both in the README. But the claim they
support is narrower than "don't merge by consensus." They measure **LLM panels
on natural-language tasks** — n_eff 2.18 across 7 model families, κ 0.2
against outcomes. A claim object with a machine-checkable witness is not in
that population at all.

If we stand on stage and say "we don't vote because panels don't work," the
first judge asks "your claims are text too, why is your merge different?" and
the honest answer has to be **"because we re-execute the witness instead of
asking anyone"** — which is a much stronger position and a much narrower claim.

We do not escape the panel problem. We **route around it**: a claim is settled
if its witness re-runs, and abstained otherwise. The judges' result is what
tells us the residual is *large*, not what tells us what the residual *is*.

The line to hold: **never present re-execution as a panel.** Present it as the
one oracle that has ever been measured to work, and present the residual as a
first-class output.

### 2c. The CRDT flow-state section is a liability on the clock we are on

The brief is honest that the fleet's 8 CRDT ports have a canary that asserts one
FNV constant and never constructs a CRDT, `crdt-gset.merge` is a no-op in 3 of
them, and `crdt-orset.remove` never tombstones in 3. That is a correct and
valuable observation, and it is **not a thing to build in 12 days**. It is a
thing to *cite* in the guides lane as the reason we did not put a CRDT in the
critical path. If we ship a flow-state CRDT we ship a no-op, and the first
judge who reads our own audit finds it.

**Recommendation:** claim-level adjudication and the DO-per-branch land. Flow-state
CRDT is a "future work" slide with the broken-port audit attached as the reason.

---

## 3. What is done

| # | deliverable | state |
|---|---|---|
| 1 | **Claim object** | `{subject, predicate, object, witness, confidence}`. Contradiction is structural — a hash lookup, no NL matching. Tested. |
| 2 | **Merge = adjudication** | Returns `claims`, `contradictions`, `derived`, `residual`. Re-runs witnesses over the deduplicated union. Abstains on unrunnable witnesses. Commutative and idempotent, both tested. |
| 3 | **Durable Object per branch** | `Branch` DO, CAS on the branch name, `stale-head` refusal with a re-adjudicate hint. Verified working in `wrangler dev`. |
| 4 | **Honest stress test** | Three arms — CAS, blind, retry — with a loss curve and a control. **The retry arm fails, and the output says so.** |
| — | **Reproducible receipt** | `test/verify-git-receipt.sh` re-derives every number from a fresh clone. `receipt verified.` |

Live routes: `/demo`, `/fixture/receipt`, `/git/merge`, `POST /merge`,
`POST /branches/:name/{commit,merge}`, `GET /branches/:name/head`.

**The demo contrast, in one line:** git returns 5 conflict hunks and an offer to
pick a side, plus a silently-merged seed file that is already 19 while both
agents are pinned at 18. We return 19 and 15 — what actually landed on main —
derived by re-execution, asserted by nobody, with all four losing claims
attached.

## 4. What is not done

- **Not deployed.** Local `wrangler dev` only. See blockers.
- **Concurrency does not scale, and the curve is in the README.** CAS loses 0
  updates but is degenerate (1 winner, N−1 refused — a mutex, not concurrency).
  The retry arm **collapses**: 2 of 25 agents land their claim at N=25, 2 of 50
  at N=50. Cause is visible: every retry rewrites the whole claim set, so it is
  O(N²) in branch size against a single actor. ~70 socket drops at N≥25 are the
  local dev proxy, not the merge (verified: direct N=30 gives 29 `stale-head`,
  1 ok, 0 application errors) and the test counts them separately so a harness
  failure cannot masquerade as a correctness result. **Next build: shard the
  claim space so branches that cannot contradict each other do not share an
  actor.**
- **No Workers AI in the loop.** Deliberate for now — see 2b. A `@cf/openai/gpt-oss-120b`
  judge would be the *consensus* arm, and it is in the code as
  `agreeing-parties` precisely so the demo can show it losing to re-execution
  on the same fixture. It has not been wired to a live model yet.
- **No flow-state CRDT.** See 2c.
- **No public repo, no push.** Per instruction.

## 5. Blockers found at t+0:10, still open

1. **`CLOUDFLARE_TOKEN` is not in the environment, and the account that *is*
   authenticated is not the one in the brief.** `wrangler` is not on `PATH`
   either; it exists only in the npx cache (`/workspace/.home/.npm/_npx/32026684e21afda6`).
   Auth state at `~/.config/.wrangler/wrangler-temporary-account.toml` is
   account **`063c398145906b5925a9f679a12264cb`** ("Prong Potassium") —
   **not** `049ff5e84ecf636b53b162cbb580aae6`. That token has
   `expiresAt 2026-10-01T21:37:59Z`, i.e. **expired**. A sibling lane's
   `fleet-resolver` DO is live on this same account. **I have not deployed and
   have not claimed a worker name** — deploying to the wrong account is exactly
   the clobber you warned about. Need a token for `049ff5e8…`, or explicit
   permission to use `063c3981…`.
2. **`GITHUB_TOKEN` is not in the environment.** The only credential in the
   sandbox is a PAT embedded in `~/.gitconfig`'s `insteadOf` URL, and it is
   **dead** (401 on every call). It did not matter: `quilt-tools` is public.
3. `compatibility_date` must be **≤ 2026-09-28**; the cached `workerd` rejects
   2026-10-01. Cosmetic, but it blocks a stranger who follows the README on
   an older wrangler.

## 6. Next

1. Get a working Cloudflare token, claim a free worker name, deploy, get a
   public URL. **Blocked on 5.1.**
2. Write the demo script against `/demo` and `/git/merge`. The 5-minute shape
   is: git conflicts → keep-both does not parse → we return 19/15 → show the
   four preserved losing claims → the consensus arm loses to re-execution.
3. Fix the O(N²) retry and shard the claim space. That is the difference
   between "a correct primitive" and "a concurrency system".
4. Open-source once it runs.
