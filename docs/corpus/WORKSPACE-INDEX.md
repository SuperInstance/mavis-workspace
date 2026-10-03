# WORKSPACE INDEX — what was here, what it means, and where the full text lives now

2026-10-02. Written **before** the second pruning pass, as instructed.
**If a summary below points at a path that no longer exists, the full text is in
GitHub and the `where` column says exactly which repo and path.**

---

## Read this first: the deletion policy that was applied

Nothing was deleted until it was shown to be either **rebuildable by
reconstruction** or **byte-identical to something already on GitHub**. Four
classes were removed in the first pass:

| class | example | why it was safe |
|---|---|---|
| **toolchain download** | `go/`, `go125/`, `go126/`, `explore/espressif/` | 680 MB + 13,327 files of SDK. `go install` / `git clone` reproduces it. **Zero information content.** |
| **clean clone** | `explore/{autoclaw,ax-quilt,forgemaster}/` | verified `0 unpushed commits, 0 dirty files`, remote confirmed pointing at `github.com/SuperInstance/*` before removal |
| **regenerable cache** | `__pycache__/`, `.resolver-state/clones/` | bytecode and scratch clones |
| **attachments after push** | `/workspace/attachments/*.md` | 42 files, verified byte-non-zero, committed to `fleet-triage` before any copy was dropped |

**The rule that governed every delete: `git status` clean AND `git log @{u}..HEAD`
empty AND the remote URL confirmed — or the content is a re-download.**

> **A credential note that must not be lost: the three clones' `origin` URLs
> contained a GitHub PAT inline** (`https://<token>@github.com/...`).
> That is a live-secret-in-plaintext pattern. **It was never committed to any
> repo and never appears in any file in this repository.** If those repos are
> still reachable from a machine, rotate the token.

---

## The corpus: 147 reports, all in `SuperInstance/fleet-triage`

**This is the primary knowledge artifact of the whole project and it is fully on
GitHub.** Local mirror: `/workspace/projects/fleet-triage/`. **Every `.md` is
committed; `docs/` holds a second copy of each.**

**Verification: `git ls-remote` local vs remote SHA matched on every push. The
`raw.githubusercontent.com` route is not trusted for verification — it lags — and
the git-tree API is used instead.**

### How to find things in it — the eight clusters

**1. THE PROJECTION DOCTRINE — "what survives is bounded by what the observation carried"**
The single most-reused idea in the corpus. Every observation is a projection;
downstream cleverness cannot recover what the looking never carried.

| file | what it settles |
|---|---|
| `PROBE-RESULTS.md` | the ladder, corrected. L0 lossless **0.8831**, L1 colour-collapsed **0.8947**, L3 coarse 0.6839, **L4 hash64 0.5103**, L5 stone-count 0.5000. Plus the runnable probe in `probe/` |
| `RERENDER.md` | the re-projection invariance test — train on one projection, test on another. **The delta measures what was learned** |
| `ASCII-CHARSELECTION.md` | the `Rasterizer.cs` character channel, **including a retraction** |
| `PROBE-RESULTS.md` §"CORRECTION 2" | ground truth confounded with the projection — the label leaked the answer |

> **The most important single number in the corpus: an L4 irreversible projection
> scored 0.5103 against L0 lossless at 0.8831. A diff is L4. That is why the
> time-query interface needs a reference frame and not just diffs.**

**2. THE INSTRUMENT-HONESTY CLUSTER — "a check that cannot fail is worse than none"**
The dominant failure mode, found seven times, five of them mine.

- `GATE.md` — four rules encoding the four discriminators; its own report admits
  3 contaminated `ok`s in its own output and 272 `.ts` files uncovered
- `PREDICTIONS.md` — **a ledger scoring me.** 14 load-bearing claims: 5 kept,
  5 false (4 mine), 1 half-false, 1 unresolved, 1 predicted-then-refuted by
  reading the source
- `TIME-QUERY.md` — the empty-diff / stale-anchor / moved-scene acceptance trio
- `durable-LOGIC.md` — the canary invariant; **3 of 4 routes keep a record of the
  check going red, and the ones that keep only a green badge are exactly the ones
  that survive `got = expected`**

> **The cross-cutting number: `n_eff ≈ 2`, measured six independent ways.**

**3. THE ASCII / ASCIAPOCALYPSE CLUSTER — the substrate**
A 2020 DOS-Games-Jam MonoGame FPS rendered as ASCII. **Compiles on .NET 9 with
0 errors; no source file was edited.** Five of 68 files touch a graphics device;
`Console.cs` is 55 lines of pure C# with zero MonoGame references.

- `ASCIIPORT.md` — the four-line port, the two failures on the way (MGCB exits
  150; `MonoGame.Framework.Pipeline` does not exist as a 3.8 package)
- `ASCII-CHARSELECTION.md` — **`Data[i,j] = fogString[fogId]` is a function of `z`
  and carries no identity; `Color[i,j]` is the texture sample and carries all
  of it.** Plus a **retraction of my own churn finding** (the dither is written
  once in the constructor, never redrawn)
- `ASCIIPOCALYPSE.md` — the cell record `(char, R3, G3, B2, x, y)` = 16 bytes,
  the PLATO shape, already native. Plus the correction that **a vision arm is not
  an independent instrument**
- `ASCII-CELLS.md`, `PROJECTION-LOSS.md`, `AUTOPLAY-CENSUS.md` — lane outputs
- `ASCII-VISION-LANDSCAPE.md` — the 60-year field survey (see below)
- `BOTS-RESEARCH.md` — **"NLE is the right technique with its most important
  input deleted... every benchmark that produced a result is top-down 2D, where a
  glyph _is_ an identity"**
- `TIME-QUERY.md`, `RERENDER.md`, `PIXELS-ARCHITECTURE.md` — the observation
  interface and the autoplayer architecture

**4. THE ASCII-AS-VISION LITERATURE — 60 years, surveyed**
`ASCII-VISION-LANDSCAPE.md` + **`research/seed-documents/` (42 files, 385 KB)**
from Casey's other agent.

- Lineage: ASCII 1963 → **Knowlton & Harmon 1966-68** (a photograph by tone,
  shown at MoMA) → BBS/cp437 → **AAlib 1997 / libcaca 1999** (install as a
  *graphics device* — the direct ancestors of Asciipocalypse) → **Xu/Zhang/Wong
  2010 ACM TOG** (the tone/structure split) → CNN era → LLM era
- **"ASCII Art Turns LLMs into VLA Controllers"** — a text-only LLM on a 96×54
  **coloured** ASCII raster runs pick-and-place on a **physical arm**. Their
  encoder assigns glyphs to **semantic roles**, not to density
- **ASCIIEval (ICLR 2026): GPT-4o image-only 82.68% → text+image 76.52%, a
  12.32% DROP.** Giving a model both modalities is *harmful*
- **"Text Speaks Louder than Vision" (COLM 2025):** a measured **text-priority
  bias** — models read characters as text, worse as semantics get richer
- **ASCIIBench: CLIP cosine similarity is at chance on ASCII.** Never score
  ASCII with a general-purpose visual encoder
- **SSVR (2026) independently named "state-representation mismatch"** as the
  obstacle in VLA planning, caused by "lossy textual compression" — that is this
  project's own doctrine, in the VLA literature

**5. THE SEAM / ARCHITECTURE CLUSTER**
- `r3-SWAP.md` — **the seam holds for ENUMERATED apps and leaks for composed
  ones, and the discriminator is one line of static analysis**: if the
  enumeration takes anything the app did not derive from its own state, the app
  is composed and will need a chooser to exist
- `durable-LOGIC.md`, `synergy-MAP.md` — the reusable abstraction is
  **state + enumeration**; the chooser and render are swappable
- `res-RUNG.md` — **"A PS5 is not the cheapest place to run a model. It is the
  cheapest place to run a *policy*, and the fleet already owns one, and it is
  1.3 KB, and it already works."**
- `GATE.md` — the checker for the above

**6. THE FLEET-CENSUS CLUSTER**
- `HOLLOW.md` (62 repos classified), `STUBS.md` (low-blob disposition)
- `GROUP-DYNAMICS.md`, `PR-QUEUE-2026-10-01.md`
- `INDEX.md` / `ORIENTATION.md` / `DOCTRINE.md` / `EXPERIMENTS.md` / `BOARD.md` /
  `ROLES.md` / `SPRINTS.md` — the docs layer, ~3.3–4.0 MB
- **Rules that must not be lost:** rank by `git/trees?recursive=1` tree bytes
  **never** API `size`; the vendor-filter rule; the `recovered-copy-20260824-*`
  pollution event (31 of 59 are empty); re-derive the census every pass

**7. THE CORRECTIONS — five claims this project retracted, kept on the record**
| claim | what killed it |
|---|---|
| "every projection is lossy" | L1 colour-collapse kept **98.9%** — the principle survived, the statistic didn't |
| "L0 lossless is the ceiling" | median **reverses** it: L0 0.8831 < L1 0.8947 |
| "`BattenSpline` is prose-only" | **136 code hits.** I generalised from 10 |
| "`git merge --abort` always fails" | `MERGE_HEAD` is present; it works |
| "the dither redraws per frame" | `grep -n "offset\["` → one write, in the constructor |

> **Every one of these is worth more than an unchallenged claim would have been.
> `PREDICTIONS.md` is the ledger; a ledger that cannot say "I was wrong" is a
> green badge.**

**8. THE SHARED INSTRUMENTS — separate repos, all public**
| repo | what it is |
|---|---|
| `SuperInstance/fleet-triage` | **this corpus** — 147 reports + 42 seed documents |
| `SuperInstance/fleet-resolver` | live at `fleet-resolver.prong-potassium.workers.dev`; 477 repos / 85,990 files, 4,789 `FILE_MISSING` |
| `SuperInstance/quilt-adjudication` | the competition entry; 26 files, 11/11 pins, 59 checks, deterministic demo. **Correct loser handle: `git checkout HEAD -- <path> && git commit`** |
| `SuperInstance/fleetlint` | 8 lint rules, alphabet canary `0xe5c271ee5c13e9c7` |
| `SuperInstance/selectlib` | 10/10; `ControlFailure` is a **public export** |
| `SuperInstance/jev-quilt`, `jev-harness`, `jev-fusion` | the JEV contract and harnesses |
| `SuperInstance/Asciipocalypse` | the game; the port is mirrored at `fleet-triage/port/Asciipocalypse/` |

---

## Numbers worth being able to quote without looking

- Connect-4 ground truth: **54,166 positions, plies 1–6, digest `0x4ef8351a5c319637`**
- 4×4 four-in-a-row: **3,338 positions, complete tree, draw, digest `0xcdc9636c704a7ba2`**
- Fleet: **5,127 repos, 0 private, 16 archived, 3,858 non-forks never examined**
- Resolver: **477 repos / 85,990 files**, 21,014 citation sites, 4,789 `FILE_MISSING`
- `n_eff ≈ 2` — six independent measurements
- Projection ladder: **0.8831 / 0.8947 / 0.6839 / 0.5103 / 0.5000**
- Character-channel collapse: **14 of 15 identity pairs indistinguishable; 24 cells, 6 objects, 2 characters**
- Canaries: FNV-1a `0x24a555471370b18d` · alphabet `0xe5c271ee5c13e9c7`
- Instruments that could not fail: **7, and I am the common factor in 5**

---

## What was NOT touched, and why

`IDEATION/`, `agents/`, `papers/`, `reports/`, `repos/`, `research/`, `Spreadsheet-ai/`,
`ax-quilt/`, `c4/`, `c4gt/`, `erised*/`, `ga4444/`, `experiments/`, and the
per-project directories under `projects/`.

**These hold unique work. They get their own pass, each one verified against a
GitHub remote before anything is removed.** The instruction was *don't lose data*,
and the only defensible order is: **index → push → verify → then delete.**

## The one-line summary

> **The load-bearing element is always the boring one — the enumerator, the
> provenance, the record of the red, the metric with a denominator that exists —
> and the expensive impressive thing is decoration.** That is `n_eff ≈ 2`, it is
> `selectlib` beating a judge with a free statistic, it is the VLA paper assigning
> glyphs by role instead of density, and it is why 5,127 repos have produced
> approximately zero composition.
