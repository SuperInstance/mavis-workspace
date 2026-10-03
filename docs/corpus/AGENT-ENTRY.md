# AGENT-ENTRY.md — the arrival log

**Author:** a zero-shot scout, sent with no map, told to find its own way in.
**Started:** 2026-10-02 15:49Z. **Stub written:** 15:51Z (+2 min). **This file completed
after the investigation.**

A stub of this file was written at +2 minutes, *before* reading
`THEORY-OF-MIND.md`, deliberately, so the impression below is mine and not an
inheritance. Sections 1–3 are that stub, lightly corrected where verification
overturned it. Section 4 onward is the investigation.

The raw log matters more than the conclusions, so the wrong turns are kept.

---

## 0. The access problem, which gates everything

- No `GITHUB_TOKEN` in env. `gh` is not installed.
- A token **is** present in `fleet-triage`'s git config
  (`url.https://x-access-token:<...>@github.com/.insteadof git@github.com:`).
  **It is dead — `401 Bad credentials`.** Anyone who finds it will waste time.
- What works: **unauthenticated** `api.github.com`, HTML scraping, `git clone` anonymously.
- **60 core requests/hour, 10 search requests/hour.** A scouting session is ~50 calls.
  I burned ~25 paging through a listing that turned out to be worthless (§2).

---

## 1. The ordered log — what I opened, what I assumed, what was true

**1. `github.com/SuperInstance` (HTML, unauth) — 1 step.**
*Assumed:* an organisation, maybe a small one.
*True:* a **user** — "SuperInstance (Casey Digennaro)". 262 KB of HTML, which is large;
that turned out to be because the profile README is ~20,700 characters and fully
rendered. The repo grid shows **two pinned repos**: `pincher` ("Vector Database as
runtime, LLM as compiler") and `quilt` ("A spreadsheet where every cell is a live,
addressable capability. The grid is the runtime."). **The whole account has two
front doors, and neither is `quilt-adjudication`.**

**2. `api.github.com/users/SuperInstance/repos` — 2 steps.**
*Assumed:* this enumerates the account, so I could rank by size/stars and be done.
*True:* **it does not.** 100/page, sorted `updated`. I paged to 40 (4,000 entries)
without reaching an end. `constraint-theory-core` — 135 MB, 3★, the repo I was sent
to check — **is not among them**, while `GET /repos/SuperInstance/constraint-theory-core`
returns it instantly. The pages are individually distinct (38 distinct SHA-1 page
signatures across pages 3–40, no duplicates), so this is not a repetition bug: the
`sort=updated` ordering is simply **scrambled**. Pages 3, 4 and 5 each contain repos
pushed on both 2026-10-02 and 2026-09-30; pages 18–33 are uniformly
`pushed_at=2026-07-12`, a mass-creation date.
*Consequence:* **this is the single most important structural fact about the account
and it is not in `THEORY-OF-MIND.md`.** Reach repos by name. Never infer non-existence
from a list.

**3. Star ranking — 2 steps.**
*Assumed:* stars approximate importance.
*True:* noise. `SuperInstance` 7★, `AI-Writings` 4★, then a flat tail of 0–3★.
The 363 MB `quilt-gpu-lab` has 0★ and no description. `constraint-theory-core` is
**not in the top 12 by stars** — so the "third on the popularity list" in
`THEORY-OF-MIND.md` §2b is GitHub's own recommendation, not stars. I could not
reproduce that list: `cocapn`, `mud-arena` and `plato-nervous` (which it lists) do not
appear in my star-sorted top 12, and the profile's repo grid is a pinned list, not a
ranking. **Treat the exact position as unverified; the repo's rank barely matters —
it is reachable by name in one request.**

**4. Search by task terms — 2 steps.** *This is the route that works.*
`judge` → `quilt-adjudication` at **rank 1**. `merge` → same repo, rank 1. `witness` →
`quilt-ewitness` ("Anytime-valid e-process witnesses for training claims"),
`witness-validation`. `entropy` → `si-renyi-entropy` ("Rényi entropy spectrum detects
fleet monocultures"). `quorum` → `consensus-weave` ("Multi-agent consensus protocol
with quorum and veto"). All 0★, all with no path from the profile.

**5. `constraint-theory-core` — 4 steps (1 API call once I had the name).**
Verified defects in §5. Two of my three starting assumptions were wrong.

**6. `SuperInstance-papers` — 5 steps.** Found by chasing the `6.8×` claim, which
`BOARD.md` attributes to lane `papers-ROOT`. Verified defects in §5.

**7. `THEORY-OF-MIND.md` — read last**, on purpose.

---

## 2. Steps-to-reach, the measurement

| route | steps | lands on |
|---|---:|---|
| profile page | 1 | `pincher` + `quilt`. Real work, but neither is the best of it. |
| most popular / most recent | 1–2 | AI-Writings (3.6 GB essays), `quilt-gpu-lab`, `pong-quilt`, `tidepool`. **None is the work.** |
| repos API listing | ∞ | does not terminate usefully; misses the target repo entirely |
| **search `judge` / `merge`** | **1** | **`quilt-adjudication`, rank 1** |
| exact name | 1 | anything, if you already know the name |

**The good work is one search query away and zero list-routes away.** The profile
README mentions `entropy` **0** times, `quorum` **0** times, and names **none** of
`quilt-adjudication`, `quilt-ewitness`, `witness-validation`, `si-renyi-entropy`,
`consensus-weave`, `quilt-fleet-tools` or `quilt-jepa`. It is a good mission statement
and a poor index.

---

## 3. What I believed before I found it — *the number the orchestrator wanted*

Before reading the good repos, on the evidence of the profile page and the top of a
star-sorted list, my honest estimate was:

> **"A solo developer who has mass-generated several thousand near-empty prototype
> repos and is using the account as a scratchpad. The 5,114-repo headline is mostly
> forks and placeholders. There is a real spreadsheet runtime underneath, but the
> surrounding material is AI-generated noise, and the confident math in
> `constraint-theory-core` is decoration."**

I was **~half right, and wrong in the direction that matters.** Right: the placeholder
descriptions ("PoC", "arena", empty), the fork inflation, the noise-to-signal ratio.
Wrong: `quilt-adjudication` is genuinely careful work — competing merge strategies,
receipts, refusal to commit silently. It is not a scratchpad. It is a person who cannot
stop building instruments, and who is losing the ability to point at them.

**I also believed the `6.8×` warning was about `constraint-theory-core`, because I was
told it was. It is not there. It is in `SuperInstance-papers`.** I nearly wrote a
warning that a reader could not act on.

---

## 4. Corrections to the brief I was handed

Three, all verified, all of which change what the next scout should do:

1. **The `6.8×` constant is not in `constraint-theory-core`.** Zero occurrences of the
   string `6.8` anywhere in that repo at `df9ce63` (fresh anonymous clone, HEAD
   confirmed). It is in `SuperInstance-papers/01-conservation-law-of-intelligence.md`.
   `BOARD.md` agrees: the 6.8× is lane `papers-ROOT`.
2. **"defended by a test that passes at any value" is nearly right but not literal.** The
   tests in `constraint-theory-core/src/dcs.rs` assert each constant against *its own
   defining literal* — they cannot fail unless the author edits both sides. That is
   worse than "passes at any value", and easier to demonstrate.
3. **"5,471 issues that nobody read" misleads if placed in a scout's context.**
   `open_issues_count` is **per repo and single-digit**: `SuperInstance` 7,
   `constraint-theory-core` 1 (and that one is an adoption request from April about
   Python bindings), `quilt` 2, `fleet-triage` 0. Telling a scout "5,471 unread issues"
   teaches them not to file. Telling them "`constraint-theory-core` has 1 open issue and
   it is unrelated" teaches them it will be read.

---

## 5. Verified damage

All re-derivable. Commits and commands given so a reader can check rather than trust.

### `SuperInstance-papers` @ `82831fc`

- **A formal proof resting on a file that does not exist.**
  `01-conservation-law-of-intelligence.md` line 35 cites `murmur/transforms/rubiks.py`;
  line 37 quotes "the layer count function from `rubiks.py` (line 437)"; line 50 says
  certainty is "confirmed in `update_certainty` at line 281 of `rubiks.py`". The section
  closes with `□`. **`rubiks.py` exists nowhere in the account** (`find . -name rubiks.py`
  → empty; the directory `murmur/transforms/` does not exist). Line 326 of the same paper
  cites a *different* path, `murmur/logtensor/transforms/rubiks.py`, as does paper 02 at
  line 385. **Two mutually inconsistent paths, neither present.** The file lives in
  `murmur`; the paper is asserting a theorem about code it does not contain, with
  line numbers, to three significant figures of confidence.
- **The headline `6.8×` is contradicted by its own sentence.** Line 207: "6.8× higher
  density … (59,841 vs 10,428)". `59841/10428 = 5.7385`. Wrong by ~18%. Repeated at
  lines 215 and 297, and line 297 states it as a falsifiable **Prediction** of an
  experiment. `git log -S'6.8'` shows one commit, `efbc664`; it is not in `README.md`,
  `CONTRIBUTING.md` or `src/lib.rs` as `BOARD.md` records, and no Rust source references
  Eisenstein at all — so **`BOARD.md`'s version of this finding is not reproducible at
  current HEAD.** The paper's version is.

### `constraint-theory-core` @ `df9ce63`

- **Theorem 1 (12-Neighbor Rigidity Limit)** proves `k = 6 − 12/n` (step 3) and then
  asserts `lim(n→∞) k = 12` (step 4). **The limit of `6 − 12/n` is 6.** The error is
  load-bearing: `src/dcs.rs:9` ships `LAMAN_NEIGHBOR_THRESHOLD: usize = 12` and
  `is_rigidly_connected()` returns `avg_neighbors >= 12`.
- **Theorem 2 (Unit Vector Information Capacity)** states "exhaustive enumeration
  confirms there are exactly 48" Pythagorean quadruples with `d ≤ 200`, then computes
  `log2(48) = 5.585` and calls it a three-significant-figure match to a claimed 5.6-bit
  empirical limit. **No enumeration code exists in the repo.** I ran it: primitive
  `a²+b²+c²=d²`, `a<b<c`, `d ≤ 200` → **1,364** solutions. Modulo sign → 8,052.
  Counting sign and permutation separately → 64,416. **No reading gives 48.** The value
  `48 = 16 × 3` (hence the paper's tidy `log2(48) = 4 + log2(3)`) reads as
  reverse-engineered to hit the target. It ships as `PYTHAGOREAN_INFO_BITS`.
- **`src/dcs.rs` tests restate their own constants.** `assert!((RICCI_CONVERGENCE_MULTIPLIER
  - 1.692).abs() < 0.001)` where `const RICCI_CONVERGENCE_MULTIPLIER: f64 = 1.692`;
  `assert!((convergence_time(100.0) - 169.2).abs() < 0.01)` where the function is
  `avg_latency_ms * RICCI_CONVERGENCE_MULTIPLIER`. Seven tests, all of this shape.
  `test_pythagorean_bits` checks the constant against `log2(48)` and then checks it is
  within `0.1` of `5.6` — a window that admits any value in `[5.5, 5.7]`, ten times
  wider than the "3 significant figures" the module header claims.
- **Stale metadata.** GitHub description: "83 tests, zero deps". Actually **229**
  `#[test]` functions; `[dependencies]` is empty but `[dev-dependencies]` has
  `rand = "0.8"` and `criterion = "0.5"`.

---

## 6. The structural finding

> **The repos API does not index this account. The work is reachable by name and by
> search term, and unreachable by any list.**

This is the one thing I learned that `THEORY-OF-MIND.md` does not say, and it changes
the remedy. It is not primarily a *description* problem — describing three more repos
would not put `quilt-adjudication` on route A, because route A is a ranking over a
listing that is itself unreliable. It is an **index** problem.

The profile's "Reading order" section is the right instinct and the wrong instrument: it
is 20,700 characters of first-person voice, and a scout scanning it for `quorum` finds
nothing.

---

## 7. Deliverables

- `fleet-triage/AGENTS.md` — the short entry point a scout reads first.
- `fleet-triage/AGENT-ENTRY.md` — this file.
- Profile-repo `README.md` proposal — text only, not pushed. The profile repo belongs to
  a human and **I did not touch it.** See `README-PROPOSAL.md`.
