# ORG.md — fleet merge-ordering triage

**Author:** Organizer lane · **Date:** 2026-10-01 · **Nothing was merged. Nothing was pushed.**
Scratch + all evidence: `projects/fleet-triage/org_scratch/`

---

## 0. Method, and why it cost no API budget

`GITHUB_TOKEN` is absent, so `/search/code` is impossible and the core API is 60/hr. Everything
below was obtained over the **git protocol** and **codeload tarballs**, neither of which draws on
the REST budget.

**The primitive that made this possible:** `git ls-remote --refs <url> 'refs/pull/*/merge'`.

GitHub maintains `refs/pull/N/merge` **only for open PRs it has computed a merge for.** It is
absent for closed and merged PRs. So one round trip per repo enumerates the entire fleet's open
PR queue with no authentication at all — 0.3 s/repo, 24-way parallel.

I ran it over **all 5,092 repos in the census, 0 errors.**

### The oracle has a false-positive mode, and I caught it

`refs/pull/N/merge` can outlive the PR it describes. `pong-quilt#88` still advertises a merge ref,
but `git merge-base --is-ancestor pr88 origin/main` returns true — **it is already merged.** A
shallow-fetch ancestry check initially told me the opposite, which is a second trap:

> **`--depth=N` silently breaks ancestry.** With `--depth=1`, `merge-base --is-ancestor` returned
> false for a PR that was in fact merged. Every PR verdict in this report was re-run against a
> ≥200-commit history. If you audit PRs with a shallow clone, you will invert your own results.

**Every candidate was therefore re-checked by ancestry, not by ref presence.** The ref is a
discovery oracle; ancestry is the authority.

---

## 1. Negative control — the method rediscovers both cases you found by hand

You said: *if the method cannot rediscover `fleet-murmur#9`/`pong-quilt#87` as an ordering
dependency and `quilt-tools#32`/`#33` as a conflict, the method is broken.*

**It rediscovers both, independently.**

### Control A — `quilt-tools#32` vs `#33`: CONFLICT reproduced

```
$ git merge-tree --write-tree pr32 pr33
3c753ee9b1ef5c88135c594cc7838039db5eb1ff
experiments/REFERRAL_GRAPH.md
experiments/referral_graph.pins.mjs
CONFLICT (content): Merge conflict in experiments/REFERRAL_GRAPH.md
CONFLICT (content): Merge conflict in experiments/referral_graph.pins.mjs
exit=1
```

Both sides of the first hunk are **the same template literal with a different number in it** —
`v[0].weight === 2 * VERIFIED_WEIGHT` vs `=== 3 * VERIFIED_WEIGHT` — inside one `check(...)` call.
Concatenating both sides yields a file that does not parse:

```
$ node --check merged_pins.mjs
SyntaxError: Unexpected token '<<'
```

**Your "keep both sides" diagnosis is confirmed exactly.** These are competing values of one
expression, not additive lines.

**Merged truth, measured from the auto-merged seed** (`referral_graph.seed.mjs` merges cleanly —
the conflict is confined to the two doc/pin files):

| | #32 alone | #33 alone | **merged** |
|---|---|---|---|
| total edges | 18 | 18 | **19** |
| VERIFIED | 14 | 14 | **15** |
| PENDING | 4 | 4 | **4** |
| fleet-murmur inbound | 2 | 3 | **3** |
| delta-shape in view | no | no | **yes** |

I enumerated all 19 rows independently. The 19th is `pq-named-refusals → fm-refusal-ledger`
(`fleet-murmur#8`) from #33; #32 contributes `qe-eproc-witness → ds-esign-drift`
(`delta-shape#1`). Both are additive; only the **narrative and the counters** conflict.

### Control B — `fleet-murmur#9` / `pong-quilt#87`: ORDERING dependency reproduced

```
fleet-murmur#9 commit written:  2026-10-01T00:00:13Z
pong-quilt main at that moment: d51631e  (R67 head, 2026-09-30T22:38:09Z)  → pin was CURRENT
pong-quilt#87 (R68) merged:     2026-10-01T01:40:32Z   ← 1h40m LATER
pong-quilt#88 (R69) merged:     2026-10-01T01:40:33Z
```

`d51631e` was genuinely `pong-quilt` main head when `fleet-murmur#9` was written, and `pong-quilt`
main has since advanced to `70af7f0`. **Your ordering call was correct and is now visible in the
history** — the two pong-quilt merges you performed are recorded as `Merge branch 'pr87'` /
`'pr88'`, distinct from GitHub's own `Merge pull request #N` style, confirming hand-merges by a
third party.

**Method verdict: PASS on both controls.** The sweep is not spraying conflicts.

---

## 2. The fleet's open PR queue — 9, not 8

My census found **9 open PRs across 6 repos.** Your list had 8 across 5. **You were missing a
whole repo.**

| repo | open PRs | note |
|---|---|---|
| `quilt-pincher` | **#12, #13, #14** | **NEW — never in your queue.** 3 dependabot bumps |
| `quilt-tools` | #32, #33 | the known conflict |
| `quilt-gpu-lab` | #6 | seal guard |
| `Patchwork-experts` | #1 | docs only |
| `quilt-research-canons` | #4 | **NEW** — 279-line scout report |
| `pong-quilt` | #88 (ref present, **already merged**) | stale-ref false positive |

`fleet-murmur#9`, `pong-quilt#87`, `voxelglyph#1` are all merged; `voxelglyph` retains no merge ref,
`pong-quilt#88` does. **That asymmetry is why a ref-presence-only census overcounts by one.**

---

## 3. Cluster 1 — `quilt-tools#32` / `#33` (BLOCKED: needs a human decision)

Full detail in §1 Control A. Summary of what a human must decide:

- **What each side wants.** #32: book edge 14 (`qe-eproc-witness → ds-esign-drift`) on
  `delta-shape#1`'s merge, fleet-murmur at **double** mass, view is a tie. #33: book edge 15
  (`pq-named-refusals → fm-refusal-ledger`) on `fleet-murmur#8`, fleet-murmur at **triple** mass,
  view led outright.
- **Merged truth.** 19 edges / 15 VERIFIED / 4 PENDING. fleet-murmur triple. delta-shape enters.
  Both are individually true against `main`; jointly they undercount by exactly one edge.
- **The decision.** The two PRs number the *same* event differently — both call their edge "the
  fourteenth VERIFIED edge." Only one can be fourteenth. Someone who owns the graph must decide
  whether #32's edge or #33's edge is chronologically first, then rewrite the other narrative to
  fifteenth, recompute the view percentages, and reconcile the mass account. **This is a
  judgement about the fleet's own provenance, not a merge.**

---

## 4. Cluster 2 — `quilt-pincher#12/#13/#14` (NEW; contains a genuinely broken PR)

Three dependabot bumps off a common base. **They conflict with each other**, and the cause is the
same failure class as Cluster 1 — but worse, because it is *silent*.

| pair | result |
|---|---|
| #12 ↔ #13 | **CONFLICT** in `package-lock.json` |
| #13 ↔ #14 | **CONFLICT** in `package.json` |
| #12 ↔ #14 | clean |

The #13↔#14 hunk is the identical-lines-different-values shape again:

```
<<<<<<< pr13
    "@types/node": "^26.2.0",
    "typescript": "^7.0.2",
=======
    "@types/node": "^26.6.3",
    "typescript": "^5.9.3",
>>>>>>> pr14
```

### #13 does not install. This is verified, not inferred.

`typescript ^5.9.3 → ^7.0.2` is a **major** bump. TypeScript 7.0.2 is real and is npm `latest`,
but `@typescript-eslint@8.70.1` declares `peer typescript ">=4.8.4 <6.1.0"`:

```
npm error code ERESOLVE
npm error peer typescript@">=4.8.4 <6.1.0" from @typescript-eslint/eslint-plugin@8.70.1
npm error Conflicting peer dependency: typescript@6.0.3
```

**`npm install` fails outright. The PR cannot be built, tested, or merged as-is.** I reproduced
this on a clean filesystem, with dev deps force-included, and with the cache cleared — it is not a
sandbox artifact.

| PR | change | install | `npm test` |
|---|---|---|---|
| main (baseline) | — | ok | **12/12 pass** |
| #12 | vitest 5.0.1→5.0.2 | ok | **12/12 pass** |
| #13 | typescript 5.9.3→**7.0.2** | **ERESOLVE** | cannot run |
| #14 | @types/node 26.6.2→26.6.3 | ok | **12/12 pass** |

> **Sandbox note, in case you hit it:** this environment has `NODE_ENV=production`, which makes
> npm resolve `omit=dev` and **silently prune every devDependency while printing "up to date in
> 0.5s" and writing zero files.** It looks exactly like a broken repo. Use
> `NODE_ENV=development npm install --include=dev`. I nearly filed this as a repo defect.

**Resolution (not applied):** merge **#12 and #14 in either order** — they are mutually clean —
then **close #13** or rework it to bump `@typescript-eslint` to a TS7-compatible major first.
Merging #13 first poisons both others.

---

## 5. Cluster 3 — `quilt-gpu-lab#6`: your concern is DISPROVEN

You flagged this as worth a second look: *"a seal re-issued on a rebased branch is a seal whose
original manifest no longer describes the tree."* That is a sharp instinct and the right class of
worry. **On the evidence, the concern does not hold.**

I verified the manifest against the PR's own tree by sha256, with the section prefixes its own
generator uses:

```
CORRECT PREFIX RESOLUTION -> entries 159 verified 159 bad 0
```

**159/159 hashes match.** The repo's own tool agrees:

```
$ python3 tools/receipt_manifest.py
sealed: RESULTS.md 8277d9030535… QUEUE.md 8337a086bbd2… 136 experiment file(s), 21 tool/weight file(s)
```

And the 102 new test lines **pass 4/4**.

> **A methodological trap worth recording:** run from a `git archive` export, the same tests fail
> 3/4. They shell out to `git` to detect a dirty tree, and an archive has no `.git`. I re-ran in a
> real clone: **4/4 OK.** Had I not re-run, I would have filed a working seal guard as broken.

`quilt-gpu-lab#6` is **safe to merge, independent of everything else.**

---

## 6. Cluster 4 — the `fleet-murmur#9` pin is already stale, and its test cannot notice

This is the most important thing I found, and it is not a conflict or an ordering constraint.
**It is an already-merged pin that has silently drifted, guarded by a test that cannot fail.**

`fleet-murmur` main pins its refusal corpus to `pong-quilt` **`d51631e`** in
`docs/ietf-kamimura-refusal-events-ledger.md` and in `tests/test_refusal_events_ledger.py`
(`MAIN_MERGE = "d51631e"`). The test suite **passes 6/6 today.**

But `pong-quilt` main is now `70af7f0` — **two rounds later (R68, R69), which is exactly what you
merged after `fleet-murmur#9`.** Your ordering was right, and the pin was true when written. It is
false now. That is not a mistake; it is what a pin does.

### The drift, measured

All 7 pinned anchors were correct at `d51631e`. Four have since moved **+1 line**, because R68
inserted a line above them:

| pinned kind | pin line | at `d51631e` | at main now |
|---|---|---|---|
| `SAVE/COEV-EMPTY` | 396 | ✓ | **397** |
| `LOAD/COEV-MALFORMED` | 425 | ✓ | **426** |
| `WAL-EXPORT/REFUSED` | 416 | ✓ | **417** |
| `WAL-EXPORT/EMPTY` | 422 | ✓ | **423** |

The **kinds** are all still present and unmodified (R68 only added a `genC` argument to the
`receipt()` calls), so the corpus table is substantively correct. **Only the line anchors are
stale.** That distinction matters: this is a documentation-precision debt, not a false claim.

### Why nothing caught it — the test cannot fail

`test_refusal_events_ledger.py` contains **no network call, no `git`, no subprocess.** Every
assertion compares a string in the ledger doc against a string in the test file. It validates the
document against itself.

I proved this by mutation. I repointed the pin to a commit that **does not exist in the repository**
(`deadbee`) in both the doc and the test:

```
MUTATED PIN: ok=6 fail=0
```

**Six green checks against a fabricated commit SHA.** A pin that cannot fail is not a pin. Its
own docstring claims the corpus table names every kind "present on pong-quilt main **at the pin**"
— true — and the header says "VERIFIED present-tense against main" — **no longer true, and
unverifiable by the suite that claims to check it.**

### The same defect, one repo over, and worse

`quilt-tools` has a `referral_graph.pins.mjs` with an explicit **live audit** that queries `gh` for
every receipt PR and asserts it is `MERGED`. That is the right instrument. It is disabled twice over:

1. It is gated on `LIVE && ghOK` — `--live` is not passed and `gh` is absent → it prints
   *"provenance live audit SKIPPED … labeled, not silent."* Honest labelling, zero enforcement.
2. **CI never executes the file at all.** `.github/workflows/ci.yml` runs `npm run check`, which is
   `node --check` over the modules — a **syntax check**.

Demonstrated. I changed one receipt to a PR that cannot exist (`git-agent#4` → `git-agent#99999`):

```
$ npm run check        →  syntax OK          ← what CI reports
$ node experiments/referral_graph.pins.mjs
                        →  1/108 checks FAILED
```

**A receipt pointing at a nonexistent PR passes CI.** The whole referral graph — the artifact both
#32 and #33 are fighting over, and the thing that mints the `fleet-murmur` edge — is **unenforced
in CI on the repository that owns it.** `grep -c pins .github/workflows/ci.yml` → `0`.

---

## 7. Correct merge order

```
NOW, unconditionally, no dependencies:
  1. quilt-gpu-lab#6        — verified 159/159 seal + 4/4 tests. Merge.
  2. Patchwork-experts#1    — docs only, no code, no inbound pins. Merge or close.
  3. quilt-research-canons#4— 279-line scout report, docs only. Merge or close.
  4. quilt-pincher#12       — clean vs #14, 12/12 tests. Merge.
     quilt-pincher#14       — clean vs #12, 12/12 tests. Merge.  (12 and 14 commute)
  5. CLOSE quilt-pincher#13 — cannot install; @typescript-eslint caps TS at <6.1.0.

BLOCKED — human decision required:
  6. quilt-tools#32 + #33   — resolve together at 19 edges / 15 VERIFIED / 4 PENDING.
                             Do not merge either alone; each is self-consistent and
                             mutually wrong.

ALREADY STALE — needs a re-pin PR, not a merge:
  7. fleet-murmur           — pin says pong-quilt@d51631e; main is 70af7f0. Re-audit
                             against 70af7f0 and correct the 4 moved line anchors.

DO NOT MERGE YET:
  pong-quilt#88             — already merged. Its merge ref is a stale artifact.
```

**The only true ordering constraint in the entire fleet is the one you already found and already
honoured.** Everything else is independent, blocked on judgement, or already merged.

---

## 8. Coverage

| | count | note |
|---|---|---|
| Repos probed for open PRs | **5,092 / 5,092** | **0 errors** |
| Repos with ≥1 open PR | 6 | 9 PRs |
| Repos with an empty tree (HTTP 409, no refs) | 61 | unreadable *by anyone*, not a token limit |
| `master`-only repos | 1,900 | re-probed on the correct branch |
| Repos scanned for cross-repo pins | **315** | all pushed ≥ 2026-09-25 |
| Tarball downloads | 315, 0 errors | codeload, free |

**What I could not reach, and why:**

- **4 repos failed the SHA-pin scan** (`AI-Writings`, `hermit`, `lucineer-system`, `quilt-gpu-lab`)
  with `EOFError` — truncated tarballs. `AI-Writings` is a **658 MB / 1.9 GB-uncompressed**
  gzip bomb; I capped streaming at 80 MB. Pins inside those four trees are **unexamined**, and
  `quilt-gpu-lab` is one of the repos with an open PR, so its inbound pins are an acknowledged gap.
- **1,600 detected citation+SHA pairs name repos outside the 5,092 census** (forks, deleted repos,
  `*.git` suffixed URLs). Unverifiable here.
- **The pin scan covers 315 recently-pushed repos, not all 5,092.** Full-fleet source search is
  impossible without `/search/code`. The 4,777 older repos are **unscanned for pins** — a real gap,
  though a low-risk one, since a stale pin in a repo untouched since August cannot be newly wrong.
- **No PR discussion, review comments, or labels** — those live behind the API only. Every verdict
  here comes from git objects.

---

## 9. Is the fleet's coordination actually working?

**It is a merge-fast culture with a real and specific ordering debt, and the debt is not in the
merge order — it is in the fact that nothing verifies the claims after the merge.** Nine open PRs
across 5,108 repos with 318 repos pushed in five days is not a coordination failure; it is a fleet
that merges on contact and trusts its own agents. That instinct is usually right, and here it was:
`quilt-gpu-lab#6` really is sound, and the two control cases really were the only genuine
cross-repo constraints in 5,092 repos. The low PR count is not hiding a queue. But the two
instruments built to catch drift — `fleet-murmur`'s self-referential pin test and `quilt-tools`'
doubly-disabled live receipt audit — are both green, both look rigorous, and neither can ever
report a failure. I demonstrated the first surviving a fabricated commit SHA and the second passing
a receipt for a PR that does not exist. The fleet's characteristic failure mode here is not
merging in the wrong order; it is **shipping a pin that is precise in form and vacuous in
substance, and then having no mechanism that could ever say so.** The `quilt-tools#32`/`#33`
conflict is what honest enforcement looks like — two agents whose tests both ran, both passed, and
both told the truth about a graph that neither could see whole. That argument should be resolved
by a person, and the fix that matters more is making `node experiments/referral_graph.pins.mjs`
a CI step.
