# AGENTS.md — you are about to read a 5,114-repo account. Read this first.

Written by a zero-shot scout who arrived with no map. Read time: ~90 seconds.

**What this is:** one human's (`Casey Digennaro`) research account on
spreadsheet-as-runtime. The unit is a **cell**; sheets compose into programs; agents
are cells. Repos are named `quilt-*`. Your job is almost certainly one repo, not the account.

---

## Three repos, in the order I'd read them

| repo | what it is | why |
|---|---|---|
| **`quilt`** | "A spreadsheet where every cell is a live, addressable capability. The grid is the runtime." | The flagship, and **pinned** on the profile. Start here. |
| **`quilt-adjudication`** | "The merge that cannot be committed silently." Cloudflare git-competition. | Best evidence of *how this account argues*: competing merges, receipts, no silent commits. |
| **`SuperInstance-papers`** | 30 MB, 2★ | **Contains the account's worst-known defects. Open it expecting to find a wrong claim.** |

`constraint-theory-core` (135 MB, 3★) is what you'll be *sent* to check. It is
currently third on the popularity list. **It is also the repo most likely to hand you
a confident, well-formatted, false claim.** See below.

---

## The enumeration trap — this will cost you an hour if you don't know

**The repos API does not list this account.** `constraint-theory-core` is a real,
reachable, 135 MB, 3★ repo. Paging `users/SuperInstance/repos` through **4,000 entries
does not return it.** The pages are distinct but the `sort=updated` order is scrambled
(pages 3–5 each mix 2026-10-02 and 2026-09-30 pushes; pages 18–33 are uniformly
`pushed_at=2026-07-12`).

**So: reach repos by NAME. Never conclude a repo does not exist because a list omitted it.**

```bash
curl -s https://api.github.com/repos/SuperInstance/<exact-name> | jq '{size,stargazers_count,description,pushed_at}'
```

**Access:** no working token exists — the one in `fleet-triage`'s git config returns
`401 Bad credentials`. Unauthenticated only: **60 core req/hr, 10 search req/hr.**
Budget accordingly; a scouting session is ~50 calls.

---

## Known-broken. Verified at these commits, not hearsay.

### `SuperInstance-papers` @ `82831fc` — the worst of it
`01-conservation-law-of-intelligence.md`:
- **Quotes a file that does not exist.** Lines 35, 37 and 50 cite
  `murmur/transforms/rubiks.py` at **line 437** and **line 281** and build a formal
  proof on them (it ends in `□`). No `rubiks.py` exists anywhere in the account.
  The same paper cites a *different* path, `murmur/logtensor/transforms/rubiks.py`, at
  line 326. Two paths, neither present.
- **The headline `6.8×` is refuted by its own sentence.** Line 207 claims
  "6.8× higher density … (59,841 vs 10,428)". `59841 / 10428 = 5.738`. The number is
  wrong by 18%, and lines 215 and 297 repeat it.

### `constraint-theory-core` @ `df9ce63` — two false theorems, promoted to constants
`docs/PAPER-V2-ADDITIONS.md`:
- **Theorem 1 (12-Neighbor Rigidity Limit)** derives `k = 6 − 12/n`, then asserts
  `lim(n→∞) k = 12`. **The limit of that expression is 6.** The error is load-bearing:
  `src/dcs.rs` ships `LAMAN_NEIGHBOR_THRESHOLD = 12` and `is_rigidly_connected()` uses it.
- **Theorem 2 (Unit Vector Information Capacity)** states "exhaustive enumeration
  confirms there are exactly 48" Pythagorean quadruples with `d ≤ 200`. **No such code
  exists in the repo.** I ran it: there are **1,364** primitive quadruples
  (8,052 mod sign; 64,416 raw) — never 48. `log2(48)=5.585` was evidently chosen to
  match a claimed 5.6-bit empirical limit. It ships as `PYTHAGOREAN_INFO_BITS`.

### `constraint-theory-core/src/dcs.rs` — the tests restate the constants
Every assertion in that module compares a constant to its own definition:
`assert!((RICCI_CONVERGENCE_MULTIPLIER - 1.692).abs() < 0.001)` where the const *is*
`1.692`; `assert!((convergence_time(100.0) - 169.2).abs() < 0.01)` where the function
is `x * 1.692`. These cannot fail unless the author edits both sides. **A green suite
here is not evidence.** (The `6.8×` constant you may have been warned about is in
`SuperInstance-papers`, *not* here — that claim is not reproducible in this repo.)

Stale metadata, same repo: GitHub's description says "83 tests, zero deps". There are
**229** `#[test]` functions, and dev-dependencies are `rand` + `criterion`.

---

## Where a finding goes

**Do not open an issue on a repo you have not read the source of.** This account's
weakness is confident wrong claims, not an issue backlog — per-repo open-issue counts
are single digits (`SuperInstance` 7, `constraint-theory-core` 1, `quilt` 2).

1. **Verified defect in a specific repo** → an issue on *that repo*, leading with the
   commit, the file:line, the exact command or arithmetic that refutes it, and the
   correction. Not a verdict — a reproducible counter-example.
2. **Anything cross-cutting, or anything you could not attribute** → `fleet-triage`,
   which is the namespace triage repo (0 open issues; it is a document, not a queue).
3. **Not sure yet** → do not file. Write it down in your own notes and keep going.
   Half the value here is refusing to publish an unverified claim.

The house rule, from the profile: **carry evidence, not verdicts.**

---

## Reading the account honestly

Of 5,114 repos, **816 are forks** (mostly of one `Lucineer` account) — the headline
number is inflated. Stars are noise: the top repo has 7★; the 363 MB `quilt-gpu-lab`
has 0★; the 3.6 GB `AI-Writings` has 4★. Several hundred repos carry placeholder
descriptions ("PoC", "arena", empty). **An empty description is not evidence of an
empty repo, and a confident description is not evidence of a real one** — as above.

The profile README is ~20,700 characters: worth reading once, but it mentions `entropy`
zero times, `quorum` zero times, and names none of the three repos above. It is a good
mission statement and a poor index.
