# lattice-RD — R&D lane: the Living Repository Lattice

**Status: STUB (written inside the 10-minute window, before any build).**
Read of `SuperInstance/cf-native-backend` README + one objection. Everything
below is either pinned or labelled speculation, per the receipts rule.

Lane: R&D. Owns the **network layer**. The protocol layer is published at
`SuperInstance/quilt-adjudication` (verified from a cold clone this session:
11/11 pins, demo green). Do not re-derive it. No pushes to `quilt-in-git`
or `quilt-adjudication`, ever.

---

## 0. Environment reality, pinned 2026-10-02T03:2xZ

Stated in the brief and **not true in this sandbox**. This is a finding, not
an excuse, and it changes what this lane can honestly claim.

| assumed | measured here | how |
|---|---|---|
| `${CLOUDFLARE_TOKEN}` on acct `049ff5e8…` | **absent** — no CF/GH/token env var of any name | `env \| grep -oE '^[A-Z_]*(TOKEN\|KEY\|SECRET)[A-Z_]*'` → empty |
| `wrangler` authenticated | **not authenticated**; `wrangler whoami` → "You are not authenticated" | `npx wrangler@4.146.0 whoami` |
| `fleet-resolver` live | **000, exit 6 (DNS)** — unresolvable from here | `curl -o /dev/null -w %{http_code}` |
| GitHub reachable | **200** on api.github.com; anonymous `git clone` works | cold clone of quilt-adjudication, exit 0 |

**Consequence:** items 1–3 of the brief (a real deployed Worker, a real push,
a real Durable Object) are **UNVERIFIABLE from this sandbox, not false.** Per
`ORIENTATION.md`: *"A failed fetch is `UNVERIFIABLE`, not false. Keep the two
apart."* This lane therefore ships **executable design + local test harness +
the exact deploy command**, and labels the deployed result as untested rather
than claiming it. The right failure here is a labelled gap, not a demo that
lies.

---

## 1. Read of the existing README

The README is **good and the orchestrator's take is correct.** Four things in
it are load-bearing and I take all four without re-arguing:

1. **It frames from the user's side, not the technology's.** "Agents made the
   *production* side of software native; the *consumption* side is unchanged."
   That is a market-shaped claim, and it is the one a competition judge can
   score. Most agent-infra repos in this fleet are shaped backwards.
2. **The asset inventory is verified, not aspirational.** Six rows, each naming
   a repo and the specific thing it contributes. `frozen-clock-lab`'s FNV-1a-64
   chain, `quilt-in-git` as the witness-log instance, `doubt-ledger` as the
   relocated-trust surface, `quilt-tools#32/#33` as the contested-claims case,
   the resolver as claim verification, the wardroom as the evaluation
   reservoir. **I have not yet independently re-verified all six** — that is
   work queued below, not work claimed.
3. **It states its own coordination honestly** — "This repo supports that entry
   first; a competing second entry is a later question, not a now question."
   Taking that at face value is correct and it saves a fork war. My lane is the
   *network* layer, which is downstream of both entries, not a second entry.
4. **The receipts rule is stated in the repo, not imposed on it** — "every
   design claim gets a pin or gets labeled speculation." Adopted verbatim as
   this lane's own rule.

Its **three open questions are the right three**, and Q1 is the best-posed
design question any repo in this fleet has asked. Q1 is not "should we use
Cloudflare", it is **"where does the durable log actually live, and what is CF
for?"** — which is a question about failure modes, not about products. That is
the question to answer.

**One gap in the README:** it lists `plainsong`/`chiaroscuro`-class assets by
*role* ("receipt chain", "relocated trust") and never once names a **format**.
The lattice cannot be built from roles. Roles are a design; a format is a
contract. The 64-Bit Quilt Word is named in the vision but appears nowhere in
the README's inventory — so the word is currently specified by
`plato-tile-encoder`, whose own comments say `tags(24)` while the code writes
`20`, in a crate whose doctest has never compiled, under a paper with no
`tags` field. **The inventory is a list of nouns; a lattice needs verbs.**

---

## 2. One objection to the vision (the strongest one I have)

The brief carries three measured objections. Here is a fourth, and it is
different in kind: **the three objections are all about *correctness*. Mine is
about *observability*, and it is fatal to the discovery layer, not to the
cells.**

> *"any repo wakes, executes a task, logs its structural transformations as a
> commit, and dissolves… the commit is the only durable artifact."*

**The commit is the only durable artifact, and it is a POSITIVE artifact. A
hash chain is total over the commits that exist and completely silent about
the commits that do not.** Therefore, in the lattice's own vocabulary:

> **"cell woke, executed, and disagreed" and "cell was dispatched and died" are
> the same observation: nothing.**

The verifier can report `chain valid, tip T, N cells committed` and **N is not
evidence that N cells woke** — it is a count of successes, presented next to a
denominator nobody measured. That is not a new disease. It is the fleet's
signature, in three known instances:

- the `6.8×` constant — a property test that asserts `>= 16` and therefore
  **passes at any value whatsoever**, including zero;
- `INACCESSIBLE` vs `EMPTY` — 18 D1 databases that are *unexplained*, reported
  next to 26 that are *empty*, and the two must not be merged;
- the 13 repos "failing open" — a failing test and a passing test emit the same
  exit code, so the pass count is a constant, not a measurement.

**This is why "heal one another" cannot be a lattice property at 477-repo
scale.** At n repos the lattice's failure mode is not that a cell commits a bad
transform — a hash chain catches that. The failure mode is that **a cell is
silently absent**, and since absence produces no commit, absence produces no
hash, and a hash chain over a set with holes is *still a valid chain*. The
verifier is a **total** function over its input and therefore blind to the
input it did not get. At 1 cell you notice. At 477 you do not.

**The consequence, and this is the design's real cost:** the rule "the commit is
the only durable artifact" is **wrong at exactly one place**, and that place is
the dispatcher's intent. To distinguish *silent* from *loud* you need a record
written **before** the work starts and resolved **after** it ends:

```
   DISPATCH LOG (durable, monotonic, one row per intent)
   ┌──────────────────────────────────────────────────────────┐
   │ id   cell   intent      dispatched_at   outcome   tip    │
   │ i-1  repoA  refactor    t0              COMMIT    3f2a…  │
   │ i-2  repoB  refactor    t0              LOST      —      │  ← the one the
   │ i-3  repoC  refactor    t0              (absent)  —      │    lattice
   └──────────────────────────────────────────────────────────┘  must be able
                                                                    to write
```

`i-3` is the row that does not exist yet, and **the row that does not exist is
the finding.** Two independent, cheap ways to close it, both of which keep the
commit as the only *content* artifact:

- **lease + expiry** — a dispatch carries a lease; expiry is itself a recordable
  event, so a lost cell produces a *negative* receipt instead of a hole. This is
  a liveness argument, and a liveness property needs a **fairness** assumption
  that a safety property does not: you are promising that a lease is eventually
  re-admitted, and that promise is about the scheduler, not the cell.
- **witness-cell quorums** — because `n_eff ≈ 2`, a *majority vote* over cells
  is worth about 1.5 votes. So quorum is the wrong primitive here and the
  477-repo lattice must not pretend otherwise. But a **presence** quorum is a
  different question from a **correctness** quorum: you are not asking 477
  cells whether an answer is right (worth ~2 votes), you are asking whether a
  cell is *awake* (a liveness fact, not a judgment, and not subject to the
  correlation problem at all — a cell that did not wake is not correlated with
  the cell that did).

**So the objection reduces to one sentence: a lattice built on positive-only
receipts cannot tell silence from success, and silence is the failure mode that
matters when you have 477 cells.** Everything else in the vision — the quilt
word, the CRDT, the healing — is downstream of fixing that.

---

## 3. What I built, and what it measures

`SuperInstance/lattice-cell` — **21 files, 140 KB, dependency-free Node 22 and
real git.** Name confirmed free (404 on the API) before anything was created;
`quilt-cell` was already taken (200), so the brief's obvious name was not.

Full protocol, invariants and the Q1 argument: `lattice-cell/protocol/LATTICE.md`.
Everything below was executed here. Receipts in `lattice-cell/pins/`, all
regenerated by `pins/generate.sh` — nothing in `pins/` is hand-written.

```
node tests/invariants.mjs   →  32 pass, 0 fail
node tests/contest.mjs      →  14 pass, 0 fail
node tests/mutation.mjs     →   6/6 killed (100%)
./harness/crash-matrix.sh   →  6 checkpoints, hard kill, reconciled
```

### 3.1 The two-plane design, in one line

**Plane A is git** (the commit, the frame, the postcondition — written *after*
the work, durable because it was pushed). **Plane B is a dispatch ledger**
(written and fsync'd *before* the work — the only departure from "the commit is
the only durable artifact"). They are joined by `Dispatch-Id:` in the commit
message, which is what makes Plane B a **cache that git can rebuild**, and
therefore what lets the Durable Object be disposable.

### 3.2 The liveness question, answered by measurement, not by argument

The brief asked: *what happens if the Worker dies between execute and commit?*
I did not reason about it. `harness/crash-matrix.sh` forks a child per
checkpoint and kills it with `process.exit(137)` — no `finally`, no `atexit`, no
flush — then reads the substrate afterwards. Full table in
`pins/crash-matrix.log`:

| killed at | ledger | local tip | remote tip | after `reconcile()` |
|---|---|---|---|---|
| `wake` | **nothing** | seed | seed | nothing — **unrecoverable** |
| `dispatch` | 1 open | seed | seed | open (lease re-askable) |
| `execute` | 1 open | seed | seed | open (lease re-askable) |
| **`commit`** | 1 open | **new** | seed | **`LOST` — a negative receipt** |
| `push` | 1 open | new | **new** | **`COMMIT`, repaired** |
| `outcome` | settled | new | new | already correct |

Three results worth the lane:

1. **The `commit` row is the brief's question, and it has a definite answer:
   `LOST`.** The work happened, the commit exists in a worktree that is about to
   be destroyed, and it never reached the substrate. What survives is a
   *negative receipt*. This is the row that "the commit is the only durable
   artifact" cannot express, and it is why Plane B exists.
2. **The `push` row is recoverable, and only because of the join key.** The
   commit is on the remote; only the ledger row was lost. One `git` walk finds
   it by `Dispatch-Id:`. Mutation A deletes that line from the frame and the
   suite goes red at I5a — so the join key is load-bearing, not decoration.
3. **The `wake` row has zero trace and no fix inside the cell.** It is the
   argument for *who dispatches*: the intent row must be written by the
   dispatcher, before the cell exists, or the cell's own first action is the one
   unrecoverable thing in the system.

### 3.3 The pinned liveness enabler: the receipt is a pure function of the commit

`quilt-adjudication`'s `quilt-receipt` derives every field — commit, parents,
merge flag, changed cells, dial values, timestamp — from the commit object
itself. So I deleted one and regenerated it from nothing but the commit:

```
DELETED .quilt/receipts/4719a8a.json  ->  dir now: []
REGENERATED from the commit alone.
RESULT: BYTE-IDENTICAL.  (pins/purity.log)
```

**This converts the substrate's worst bug class from a loss into a repair.**
The brief asked *how do you know a receipt that was never written still exists?*
It does not need to exist — a receipt is **derivable state**, and a witness you
can regenerate is a witness you can audit. The same is true of the contest
record (`src/contest.js`, invariant C2): both are pure functions of commits,
order-independent, no wall clock, no model output.

Note what this is *not*. It is not a claim that the witness log is tamper-proof
— `quilt-in-git` documents plainly that fnv1a-64 "is a checksum, not
cryptography." It is a claim about **reconstructibility**, which is a different
and much stronger guarantee than append-only.

### 3.4 I built the bug this lane is about, and pinned it

The first `reconcile()` scanned `git rev-list --all` — which includes the local
worktree — and recorded `COMMIT` for any commit carrying `Dispatch-Id:`. So for
the `commit` crash row it recorded a **successful delivery of a commit that was
never pushed.** Measured: remote main `c6b7195`, ledger `COMMIT @ 0bdb34c`,
`git cat-file -e 0bdb34c` in a **cold clone of the remote → does not exist.**

The reconciler was not verifying delivery. It was asking the agent whether it
had done the work, and the agent said yes. **A hole in a hash chain is visible;
a valid ledger with a false entry is strictly worse than an absence, because at
least absence is honest.** It is the fleet's standing disease one level up: a
chain that agrees with itself, a receipt that re-hashes the system's own output.

Fixed by requiring evidence from a witness the reconciler does not control:
`git ls-remote`, then a direct `git fetch <remote> <sha>` probe, and `LOST`
otherwise. `pins/bug-false-repair.log` keeps the whole thing, and **mutant B
re-introduces the original bug and is killed by I11b/I11c.** The mutant is the
receipt; the test is the claim.

### 3.5 The disagreement protocol — and the panel trap as a function

Item 3 of the brief is where this lane is worth the most, and it is wired to
`quilt-adjudication` rather than reimplemented: the dialect is its
winner/loser/reason/`to_accept_the_loser` shape, which is already published and
11/11 pinned.

> **The lattice does not adjudicate. It records.**

- **C1** — a contest is declared when two cells commit different values for the
  same `(alias, dial)` on divergent tips. A fact about the substrate; no model,
  no judge. Ancestor/descendant tips are explicitly *not* a contest, and that is
  asserted as a **control that cannot pass** (C1c).
- **C2** — the record is a pure function of the two commits, order-independent
  (C2c passes both argument orders to the same `sig`).
- **C3** — **more cells do not resolve a contest.** `resolveWithPanel()` returns
  `resolved: false` for every input, and that is the design working, not a stub.
  It records the tally, the majority it would have leaned on, and the **margin** —
  and pins that the margin grows **1 → 6** while the conclusion does not move
  (`tests/contest.mjs` C3d).

**That test is the n_eff argument, executed rather than cited.** It is the
first time in this fleet I have seen the correlated-ensemble result *run as
code in the system being designed*, with a value on the output, rather than
quoted in a README. Anyone extending the lattice will try to break C3 with a
third opinion. The test is there to stop them, and it will tell them why.

### 3.6 Open question 1, argued

**The best case for D1/R2**, since I was asked to argue the orchestrator out of
git-native and deserves the honest version of the other side: at 477 repos,
*"which dispatches are unsettled?"* is a query, git cannot answer it, and
discovering open leases means walking 477 repos' refs — O(477) network ops —
where D1 answers in one indexed query. That is real, and it is why CF was on
the table.

**It still loses, in two steps.**

*Step 1 — the query is a fold over facts git already has.* "Which dispatches
are open?" is not new information; it is derivable from commits carrying
`Dispatch-Id:` that lack an outcome. The fold gets cheap without moving
anything: a remote-reachability walk over **one hub repo** answers it in a
single fetch. That walk is not a sketch — `reconcile()` is exactly it, and it
runs against real bare remotes in I6.

*Step 2 — the decisive one: per-repo-native git cannot express a cross-cell fact
at all.* Two cells that disagree are a fact about the **pair**. There is no
object in repo A, and none in repo B, that says "A and B disagree." The contest
record has to live somewhere, and that somewhere is a third repository. **The
hub is not a performance optimisation; it is forced by the only thing the lattice
is actually for.**

> **Content is per-repo-native (git). Cross-cell facts go in a hub repo (also
> git). Cloudflare primitives are the discovery index only — a cache that is
> allowed to be wrong and is never the record.**

The test of whether a component is infrastructure or decoration: **delete it and
see if reconciliation still works.** Delete D1, R2 and Queues and the lattice
still reconciles, because reconciliation is a git walk. Delete the Durable
Object and you lose only the lease table, which `reconcile()` rebuilds.

The DO earns its place on the axis the brief named, and it is the right one: a
branch name is a natural key and the contention is per-branch, so the
serializable unit is the branch — and `quilt-in-git` already measured what
happens when a multi-writer substrate is pretended to be single-writer (its
tracked `watch.log` conflicts on the second branch; that is why the journal is
now untracked derived state).

### 3.7 The frame — objection 3, answered

> *"without dropping a single frame of execution logic" — what is a frame?*

**A frame is a pre-registered claim plus a post-registered relation, and
nothing else.** Not a log, not a narrative, not the diff:

```
quilt-cell(shared): set dial 1 to 0.9

Dispatch-Id: d-0-256ae609
Cell-Intent: set dial 1 to 0.9
Cell-Postcondition: dial:shared:1 == 0.9
```

Two properties make it a frame rather than a comment:

1. **The intent is written before the diff exists.** This is the direct answer
   to the failure the brief names — *"the branch name was typed in the first
   ninety seconds and nothing marked when it stopped being true."* You cannot
   mark drift on a claim that was never bound to a check. A branch name is free
   text; a postcondition is an expression.
2. **The postcondition is re-read from the committed tree and recorded as
   `postcondition_holds: true|false`.** It is a claim that can come back false.
   In I8 the work writes `0.5` while the intent claims `0.9`, and the receipt
   says so. **A frame whose postcondition cannot come back false is a comment
   with a header** — and mutant E (make it always hold) is killed by I8a.

This is `GIFT-ORACLE.md` applied to the exact place the vision is vaguest: when
you cannot know the right output, check that a relationship holds. The diff is
the last 1% of the work; the postcondition is the part that survives the
worker, and it is a *relation*, so it is checkable by a machine that never met
the agent.

### 3.8 Objection 4, confirmed and sharpened: the 64-Bit Quilt Word has no type

`plato-tile-encoder/src/lib.rs`, cold clone, `pins/quilt-word.log`. The brief
says the comments say `tags(24)` while the code writes `20`. Confirmed, and
three things are worse than that:

```
const BINARY_SIZE: usize = 384;
/// Layout: id(64)+question(128)+answer(128)+domain(32)+tags(24)+confidence(4)+ghost(4)+use_count(4) = 384
pub fn encode_binary(...) -> [u8; BINARY_SIZE] {
    // tags: comma-separated, 20 bytes          <-- 10 lines below the doc
    write_str(&mut buf, &mut offset, &tags_str, 20);
```

1. **The doc's own layout does not sum to its own total.** 64+128+128+32+**24**+4+4+4 = **388**, not 384. With 20 it is exactly 384. So the code is right, the specification is wrong, and the spec contradicts itself *inside one function*. **Follow the authoritative spec and the offsets run to 388 in a 384-byte buffer** — the spec, if obeyed, breaks the type.
2. **`write_str` truncates silently**: `min(s, max)`, no error, no flag. `tags` is a lossy field that drops data without saying so.
3. **The doctest cannot fail.** `assert_eq!(bytes.len(), 384)` on a value typed `[u8; BINARY_SIZE]` where `BINARY_SIZE = 384`. It is 384 for any input under any layout, including a wrong one. **This is the `6.8×` constant's exact shape: a check that passes at any value whatsoever.**

So: a type whose spec cannot add up its own fields cannot arbitrate a field
width. **The 64-Bit Quilt Word should be declared UNSPECIFIED until it carries
a stated invariant *and* a relation that catches a wrong field width** — which
is the two-sided artifact `GIFT-ORACLE.md` describes and the thing
`types-REGISTRY.md`'s 48-invariant programme exists to produce. The lattice can
ship without it: the commit is already the durable artifact, and the word is an
encoding question, not a liveness question.

---

## 4. Corrections to the brief

Three, per ORIENTATION's "if you find an error here, fix it and say so":

1. **"The receipt is not guaranteed to land"** — true, and worse than stated: a
   receipt that *doesn't* land is a **recomputable** condition, not a loss
   (`pins/purity.log`). The substrate's real problem is not receipt loss, it is
   that `quilt-in-git`'s **merge** commits record nothing
   (`diff-tree` without `-m`) — which the entry already fixes. Those are
   different bugs and the second is much cheaper than the framing suggests.
2. **"`plato-tile-encoder` — comments say `tags(24)` while the code writes
   `20`"** — correct, but the sharper statement is that the comment is
   *arithmetically impossible* (§3.8), and the repo's own doctest is a
   cannot-fail check. The disagreement is not a typo; it is an unarbitrated
   field width with a green test over it.
3. **"Workers as ephemeral execution armor"** — the framing implies the Worker
   is the thing at risk. It isn't. The Worker is the *cheapest* part; Plane A is
   durable because it was pushed, and Plane B is durable because it was flushed
   first. The measured `wake` row shows the actual risk is a **zero-trace
   dispatch**, which is a property of *ordering*, not of ephemerality.

---

## 5. What is NOT established

- **Nothing has run on a Cloudflare edge.** No `CLOUDFLARE_TOKEN` in the R&D
  sandbox (`env` has no `*TOKEN*`/`*KEY*` variable) and `wrangler@4.146.0
  whoami` → *"You are not authenticated."* `src/worker.js` and
  `src/ledger-do.js` are **DEPLOY-PENDING and have never executed.** They are
  thin, and `src/cell.js` — the module they import — is heavily exercised, but
  the Durable Object's real semantics (input-gate serialization, `storage.put`
  durability) are **unverified**, and I will not claim otherwise.
- **The repo is not published.** `SuperInstance/lattice-cell` returns 404 and
  the sandbox's GitHub credential returns **401 Bad credentials** on both the
  API and git. Anonymous `git clone` works, so this is a *write* failure, not a
  network one. Name confirmed free (404) before creating anything. The exact
  commands are in the README; the first thing a lane with a working token
  should do is push, then `wrangler deploy`.
- **The 6-asset inventory was independently re-verified for 1 of 6.**
  `quilt-in-git` only: cold-cloned, and its `.quilt/hooks/post-commit` read —
  which is where the `git notes --ref=quilt/receipts` + `refs/quilt/dials`
  implementation of open question 1 comes from (§3.6). The other **five** rows —
  `frozen-clock-lab`'s FNV-1a-64 chain, `doubt-ledger`, the
  `quilt-tools#32/#33` fixture, the `fleet-resolver` Worker, and the wardroom
  harvest protocol — are **taken from the README and NOT re-verified by this
  lane.** Separately, and outside that inventory, I cold-cloned and audited
  `plato-tile-encoder` (objection 4) and `quilt-adjudication` (the protocol
  layer, whose hooks and receipt generator I read and whose receipt purity I
  pinned).
  The `fleet-resolver` Worker was **unreachable from this sandbox** (curl exit 6,
  DNS), so its liveness is `UNVERIFIABLE`, not false.
- **The 477-repo scale claim is unmeasured.** The crash matrix runs on a
  two-repo fixture. §3.6's argument for the hub is an *argument*; its cost at
  477 is a prediction.

---

## 6. What I learned that changes what someone else should do

**1. A crash matrix is not a test suite. The rows you can see but cannot assert are the holes — and the mutation score is the only thing that tells you which they are.**
My first mutation run came back **4/6**, and the two survivors were `reconcile`
trusting the local object store, and the dispatch row written *after* execute.
Both were the two load-bearing properties of the design. **Both were already
visible in `harness/crash-matrix.sh` as rows nobody had promoted to assertions.**
The harness had known for an hour; the suite did not. Do not report a crash
matrix as verification. Report the mutation score, and treat every survivor as
a missing assertion rather than as a low-priority bug.

**2. "Non-zero exit counts as a kill" manufactured a perfect score.** My mutation
runner treated any non-zero exit as a kill. Then the suite crashed on a missing
`readFileSync` import — and **all six mutants scored KILLED, 100%.** I had
built, in the verifier for my own verifier, exactly the control that cannot fail
that `selectlib` already paid for. **A kill requires a named FAIL line; a crash
is a broken harness, and a broken harness must make the score untrustworthy
rather than perfect.** If your mutation tool reports a suspiciously round number,
instrument the instrument before you believe it.

**3. Ask the system about itself and it will agree with itself.** The single
worst bug in this lane was my own reconciler certifying an unpushed commit,
because it asked the local object store whether delivery had happened. This is
the fleet's `6.8×`, its CRDT canary, and the `quilt-jepa` reseal-forgery
instance — the same disease, three times, at three altitudes: *a hash chain
proves order and integrity; only re-execution against a witness the system does
not control proves the claim.* The cheapest available witness in a git-based
system is **a cold clone**, and it is one command. **Put the cold clone in the
test, not in the design document.**

**4. Derivable state changes the failure class from loss to repair, and that is
worth more than another append-only guarantee.** Pinning that the quilt receipt
is a pure function of its commit took ten minutes and it reframes the entire
liveness question: the answer to "how do you know a receipt that was never
written exists" is *it doesn't need to*. When designing any witness log, ask
first whether the witness is **recomputable from the substrate** — if it is,
you have bought repair, and every "durability" feature you were about to build
is optional.

**5. A panel is a bad judge and a fine quorum — and the difference is measurable
in twenty lines.** `resolveWithPanel()` returning `resolved: false` for every
input, with the margin on the output, is the first artifact in this fleet that
*runs* the n_eff finding instead of citing it. It cost less than the argument
did. **When a design rests on correlated members, write the function that refuses
to use them, and pin its refusal with a number.**

**6. Under a multi-writer substrate, silence is the only failure you cannot
detect by looking at the data.** Every safety property in this system is
checkable from what exists. The one that is not — "did a cell that should have
run, run?" — is a liveness property, needs a fairness argument, and is the only
reason a second durable plane is justified. **If you are designing a system
whose artifacts are all positive, you have designed a system that cannot tell you
it is broken.**
