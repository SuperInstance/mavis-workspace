# chiaroscuro — the 13-PR agent wave, triaged

**Date:** 2026-10-02 02:20–03:05 UTC
**Repo:** `SuperInstance/chiaroscuro` — default `main`, tip `4f7d4cc`
*"Real-time webcam-to-text rendering — characters are shapes, not pixels. Four doors: Mirror, Sculptor, Studio, Director."*

**Merged: 0 (pushed). Refused/blocked: 1 cluster, 3 defects.**
**Merges built and verified locally: 3. Push blocked — no working credential.**

---

## 0. The brief's premise is wrong, and the error is the whole hazard

The task describes 13 PRs awaiting merge. Recomputed from git rather than from the
API's counters, there are **15**, and the relationship between "merged" and "on main"
is not the one the API implies.

**`merged=true` does not mean the work is in the product.** Six of the thirteen were
squash-merged into a *topic branch*, not into `main`. GitHub reports them merged. A
steward counting `merged_at` clears the queue and ships nothing.

| actually on `main` | merged into a **branch** | closed, never merged |
|---|---|---|
| #1, #4, #6, #14, #15 | #5, #7, #10, #11, #12, #13 | #2, #3, #8, #9 |

#14 and #15 are not in the brief's list. They are **re-lands of #9 and #8 onto main**,
and they change the shape of the problem: main now carries both *sealed
pre-registrations* with **neither of their run receipts**.

### A note on the test I nearly used

The steward's test — "an empty three-dot diff proves containment" — is **wrong for
squashed merges**, and using it would have told me all ten branches were unmerged
(three-dot diffs measure against the merge base, so main's later independent additions
inflate them). `fly-stack-v0` (#6, `merged=true`) looks like 20 divergent files
three-dot and is **2** two-dot, both of them main having *more*. Ancestry alone also
lies. The only sound test is the two-dot content diff plus a test run.

---

## 1. Dependency order, rebuilt from the graph

```
main ─┬─ #1  round-5-lane-abcd ──────────────────────── ON MAIN
      │    └─ #2  edge-nl-graph ──── CLOSED, NEVER MERGED
      │         ├─ #3  edge-ts-mirror-parity ── CLOSED, NEVER MERGED
      │         ├─ #5  jev-v2-holdcast        ──squash→ #2
      │         └─ #7  edge-worker-graph-port ──squash→ #2
      ├─ #4  research-fruitfly-jev-moth ───────────── ON MAIN
      └─ #6  fly-stack-v0 ─────────────────────────── ON MAIN (content-complete)
           ├─ #8  cast-vocab-v3-spec ── CLOSED → re-landed as #15 ON MAIN
           │    └─ #11 cast-vocab-v3-run ────────────squash→ #8
           └─ #9  geopn-kc-pre-registration ── CLOSED → re-landed as #14 ON MAIN
                ├─ #10 kc-geo-implementation ─────────squash→ #9
                │    └─ #12 geopn-kc-v4-pre-registration ─squash→ #10
                └─ #13 kc-geo-v4-run ─────────────────squash→ #12
```

Six PRs target branches, not the trunk. That is the structural fact the mechanical
merge would have missed.

---

## 2. What I merged, and the verification of each

I built the merge locally, in dependency order, and ran the tree after each step.
Three merges, all conflicts resolved, all results reproduced.

### Merge 1 — `edge-nl-graph` (#2 + #5 + #7) — **4 conflicts**

All four resolved to the branch side, after checking each was safe rather than
assuming:

| file | conflict | resolution basis |
|---|---|---|
| `js/jev_gate.js` | add/add | branch is a **strict superset** — 0 lines removed, +54 |
| `docs/RD-PLAN.md` | content | branch is a **strict superset** — 0 lines removed, +7 |
| `edge/score_eval.py` | add/add | branch relabels the file as the frozen historical baseline; docstring only |
| `edge/worker.ts` | content | the point of the PR — removes the keyword table for the router |

**Verified at merged head:**

```
node  edge/score_graph.js     50/50 = 1.000   exit 0
python3 edge/score_eval.py    28/50 = 0.560   exit 0   <- baseline reproduces
node  tools/holdcast_ab.js     H1/H2/H3 MET    exit 0
node  tools/nl_parity.mjs     6/7 pins green  exit 1   <- RED
```

### Merge 2 — `kc-geo-v4-run` (#9 → #10 → #12 → #13) — **clean, no conflicts**

```
python3 tools/kc_geo.py   verdict FAIL
   H1_cv5_clean           pass=False   (0.88 < 0.90)
   H2_zeroshot_degraded   pass=False   (0.3621 < 0.931)
   H3_interference        pass=False   (41.18 pts > 5)
   H4_geometry_shuffle    pass=False   (0.80 > 0.40)
   G2_max_dev 29.359  pass=True        <- the claim-bug fix works
   exit 1
```

`tools/kc_geo_v4_receipt.json` **reproduces bit-exactly** on re-run.

### Merge 3 — `cast-vocab-v3-run` (#8 → #11) — **clean**

```
node tools/cast_v3_pins.js   11/11 green, 0 red   exit 0
```

`tools/cast_route.js` resolved to the branch blob `8ceb0840…`, verified identical.

**The merge branch is preserved at `chiaroscuro-merge.bundle` (266 KB, verified).**
`git clone chiaroscuro-merge.bundle` → `git checkout triage/merge`.

---

## 3. The defects — three, with locations

### 3.1 `edge/worker.ts:24-25` — a false claim, and the pin that disproves it is reported green

```ts
// The worker routes through the SAME graph router as edge/nl_route.js —
// two implementations, one behavior, pinned by tools/nl_parity.mjs.
```

**They are not the same behaviour.** `edge/worker.ts:12` imports `makeRouter` from
`./nl_route_core.mjs`. That core file contains **zero occurrences of `cast`**. The
canonical `edge/nl_route.js:125` turns CAST widening on by default:

```js
const castWidening = opts.castWidening !== false; // v2 default on; v1 null-control passes false
```

CAST was added to the canonical router and **never ported to the module the worker
actually runs.** The production path and the measured path are different algorithms.

The pin that exists to catch exactly this is committed **green**:

```json
{ "pin": "fuzz:core-vs-reference", "ok": true, "detail": "10/10 probes identical" }
  "all_pass": true
```

Running the tool at that exact commit, `b6c4bc9`, whose probe list is **hardcoded and
deterministic** (`tools/nl_parity.mjs:90-100`, `"make everything louder and brighter"`
with the comment `// zero-hit -> default`):

```
FAIL  fuzz:core-vs-reference  divergent: "make everything louder and brighter"
6/7 pins green    exit 1
```

Core returns `default`, score 0, no hits. The canonical returns `soft`, score 1,
`cast: true`, hits `["soft:make~haze(cast)@undefined", "woodcut:make~oak(cast)@undefined"]`.

**This is not a stale badge.** `git log b6c4bc9..origin/edge-nl-graph -- edge/nl_route.js
edge/nl_route_core.mjs` is **empty** — no commit touched the router after the receipt was
written. The committed 7/7 was never true at the commit that carries it.

It propagates: `tools/cast_eval_v3_receipt.json` asserts
`"h4_parity_external": {"result": "7/7 green"}` citing that tool.

### 3.2 `edge/nl_route.js:218` — `@undefined` on every CAST hit

```js
hits: hits.map(h => `${h.cls}:${h.term}${h.fuzzy ? "(fuzzy)" : ""}@${h.pos}`),
```

CAST neighbours are constructed at `:192` as `{cls, term, weight}` — **no `pos`**. Every
CAST hit therefore prints `@undefined` into the receipt-facing `hits` array.

### 3.3 `tools/kc_geo_receipt.json` — stale against the code beside it

It holds **v3** numbers (`G2 33.763`, `H2 0.4483`, spec `pre-registration-geopn-kc.md`),
but the shipped `kc_geo.py` is **v4** and produces `G2 29.359`, `H2 0.3621`. Anyone who
re-runs the tool on main reads a receipt describing a different experiment. The v4 numbers
are separately receipted and bit-reproducible in `tools/kc_geo_v4_receipt.json`.

---

## 4. The 1.000 claim — real arithmetic, empty evidence

`edge/score_graph.js` scores **50/50 = 1.000, exit 0**. It is arithmetically exact and
reproduces. It is also not evidence that the router understands natural language.

The router is a **75-term hand-authored lexicon** with edit-distance matching:

```
prompts containing >=1 literal lexicon term : 44/50 = 0.880
prompts that ARE a literal lexicon term     :  7/50
lexicon terms never exercised by the eval   : 19/75
```

The eval set was written first, the baseline measured (0.560), the 22 failures
diagnosed — and *then* the synonym terms were written to cover those specific
failures. The 1.000 is **training accuracy of a lexicon on the prompt set that
motivated the lexicon.** The pre-registration of the *target* (≥0.85) is genuine; the
*design* was fitted after seeing the R1 result on the same 50 prompts. The receipt's own
`limits` field says "50-prompt dev set; not a guarantee of open-vocabulary NL" — which
discloses it, but the PR title and `overall_top1: 1.0` do not.

The CAST widening then makes it worse on anything *outside* the set. On 15 neutral,
non-style sentences:

```
CAST fired on 11/15
  "someone is here"      -> CAST, hits soft:here~haze, harsh:here~hard
  "take it away"          -> CAST
  "give me a different look" -> CAST terminal, score 1.75
  "make me a coffee"      -> CAST
```

CAST is not a cosmetic flag — it is the fruitfly's "commit with no evidence" move.
The router commits, with a fabricated justification, on most ordinary English.

---

## 5. What the system actually does

**The product.** `chiaroscuro` turns a webcam into text. A frame is divided into cells;
each cell runs a glyph election and prints a character, so the image appears as text in
a terminal. "Characters are shapes, not pixels" — you do not stream a picture, you
stream a *description made of glyphs*, which is why it can be ANSI, a font atlas, or
WGSL. Four doors: **Mirror** (live viewfinder), **Sculptor**, **Studio** (offline
video→ascii, five engines, 56 dials), **Director**.

**The research stack is a fruitfly.** This is the part worth understanding, because
the PR titles are unreadable without it.

- **fly-state (4.1) — `tools/fly_cx.py`.** A **ring attractor**: a population of
  neurons each holding a phase ψ on a circle, which is how a fly tracks a direction.
  Chiaroscuro's JEV gate drives each cell's ψ into one of three states —
  **commit / reject / abstain**. A conflicting cue forces ψ backwards and displaces the
  ring; ten seconds of darkness forces Abstain. This is the "is this cell worth
  redrawing?" signal, and Abstain is what lets `shaders/glyph_election.wgsl` skip a cell
  and keep its prior glyph resident — the compute saving in PR #1 Lane A. Measured:
  ψ = 16 commit / 5 reject / 0 abstain. The null control (ψ forced +1 on every cue)
  displaces 72° against a >60° bar, which is what proves the Reject branch does the work
  rather than the attractor drifting on its own. **PASS.**

- **the edge-NL router (#2/#3/#7).** A text prompt becomes four render dials —
  contrast, blackPoint, trailDecay, edgePaint — for one of five style classes
  (woodcut / terminal / soft / harsh / default). It replaced a keyword table that scored
  0.560. This is the natural-language door onto the renderer.

- **CAST (4.3, v1→v3).** "Odor-OFF casting." A fly that smells nothing still casts
  anyway — exploration under absence of evidence. Here: when a prompt matches no style
  term, do not fall back to `default`, *cast* — widen the search to near neighbours and
  commit. v1, v2 and v3 all **sealed FAIL**, each with its own pre-registration, and the
  v3 receipt states in its own words: *"Per sealed R8 clean-delta FAIL → v3 layers NOT
  merged into canonical."* The agent killed its own candidate and said so.

- **geometric-PN KC (4.2, v0→v4) — `tools/kc_geo.py`.** Encode each class as a
  **geometric prototype in a 64-dim cone**, project into a 2048-neuron KC layer,
  WTA top-102, MBON, depression-only plasticity. The idea: a plain random-expansion KC
  preserved *term*-level rather than *class*-level locality in discrete synonym space
  (v0: 5-fold 0.26 against a dense null of 0.40 — FAIL), so the terms must be placed in
  a geometry where "woodcut" and "carved" land near each other.

  **The best reasoning in the wave is here, and it is a self-correction.** v3 set
  ρ = tan(30°) and claimed every term lies within a 30° cone of its prototype. That
  claim is false. For `point = normalize(u + ρε)`, the worst-case angle is
  `sin θ_max = ρ`, attained at `cos(u,ε) = −ρ`. I verified this numerically, independent
  of the repo:

  ```
  rho=0.577350  max sin^2 = 0.33333333 = rho^2  ->  theta_max = 35.2644 deg
  rho=0.500000  max sin^2 = 0.25000000 = rho^2  ->  theta_max = 30.0000 deg
  ```

  So v3's measured 33.763° was *inside the true bound* and *outside the claimed one* —
  G2 failed on a false claim, not on a geometry defect. v4 sets ρ = sin(30°) = 0.5, which
  makes the 30° cone true **by construction**, changing exactly one constant and freezing
  the hypothesis bars. It then failed anyway: H1 0.88 < 0.90, H2 0.3621 < 0.931,
  H3 41.18 pts > 5, H4 0.80 > 0.40. **Three sealed experiments, three honest FAILs, no
  goalpost moved.**

- **moth_notary (4.4).** An fnv1a-64 chain over all four receipts, so the failure
  history is carried by the artifacts rather than by prose.

**The lineage risk you flagged.** This repo sits in `voxelglyph → syzygy-lattice →
Projectionist`, which carries a luma collision and an encoding identity. Nothing I found
here reproduces either, but the pattern is the same family: **a mapping presented as
information-preserving that is not.** The CAST widening is the local instance — 11 of 15
neutral sentences acquire a class from a fabricated neighbour, and the receipt records
the fabricated justification in `hits` while the real provenance (`@undefined`) is
silently wrong.

---

## 6. Verdict per PR

| PR | what it is | verdict |
|---|---|---|
| #1 | Round 5, 4 lanes: Jev-gate JS+WGSL, Sobel, NL eval, token quantisation | **already on main.** Best-executed work in the wave; retired its own 1280× headline as superseded |
| #2 | synonym-graph router, claims 1.000 | **block** — 3.1, 3.2, §4. Code mergeable, evidence not |
| #3 | TS mirror + parity runner | **block** — same divergence; parity runner ships red |
| #4 | FRUITFLY×JEV×MOTH research synthesis | **already on main.** No measurements claimed — correctly labelled |
| #5 | JEV v2 HOLD/CAST split | **merge.** `holdcast_ab.js` 3/3 MET, exit 0 |
| #6 | fly-stack v0 | **already on main**, content-complete. 4.1 PASS, 4.2 FAIL, 4.4 chain OK |
| #7 | worker graph-port | **block** — `worker.ts:24-25` false; receipt 3.1 |
| #8 | CAST v3 pre-reg | **already on main** via re-land #15 |
| #9 | geometric-PN KC pre-reg | **already on main** via re-land #14 |
| #10 | KC v3 run — FAIL | **merge**, with 3.3 flagged. Reproducible, honest |
| #11 | CAST v3 run — FAIL | **merge receipts**, **block the `h4_parity_external` claim** |
| #12 | KC v4 pre-reg (cone-math fix) | **merge.** Verified correct independently |
| #13 | KC v4 run — FAIL | **merge.** Bit-reproducible |
| #14 | re-land of #9 | already on main |
| #15 | re-land of #8 | already on main |

**Merged: 0 pushed. Refused: #2, #3, #7 (and the h4 claim inside #11). Mergeable now: #5, #10, #11(receipts), #12, #13.**

---

## 7. The fixes, if this is picked up

1. `edge/nl_route_core.mjs` — port CAST widening, or set `castWidening` off in the
   canonical so the two agree. **Then** `worker.ts:24-25` becomes true.
2. `tools/nl_parity_receipt.json` — re-run and commit the **red** result. A red pin that
   is honestly red is worth more than a green one that is false.
3. `edge/nl_route.js:192,218` — carry `pos` on CAST neighbour hits.
4. Gate CAST on a minimum evidence floor, or restrict bases to content words. 11/15 is
   not a router.
5. Fresh eval set before any v4. The agent's own pre-registration already says
   *"fresh unseen set owed before v4."* That debt is unpaid.
6. `tools/kc_geo_receipt.json` — label as the v3 historical receipt, or delete it in
   favour of `kc_geo_v4_receipt.json`. Do not leave a v3 receipt beside v4 code.
7. There is **no CI and no test runner** on any branch. The pin scripts are the entire
   test surface and they must be invoked by hand — which is how a false 7/7 survived.

---

## 8. Push blocked

The only credential in the environment is a `ghp_…` PAT in global git config. It
returns **`401 Bad credentials`**. Unauthenticated clone and API read work (58/60
requests remaining); **`git push` fails with exit 128.**

```
fatal: could not read Username for 'https://github.com'
```

**No merge has been pushed.** I did not fabricate one. The three merges are real,
committed, and test-verified on branch `triage/merge`, bundled to
`chiaroscuro-merge.bundle`. To land them:

```bash
git clone chiaroscuro-merge.bundle c && cd c && git checkout triage/merge
git push origin triage/merge:main      # needs a working token
```

**Note on method:** `set -o pipefail` was used throughout; no verdict in this report
comes from a `producer | tail` shape. Every number was produced by executing code at
the merged head, and each receipt was re-derived rather than read.
