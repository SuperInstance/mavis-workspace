# DIGEST-CONFLICTS — where the 41 seed documents contradict work already done

**Lane:** digest · **Written:** 2026-10-02 · **Status:** stub, first three conflicts real, rest flagged.

---

## 0. Corpus receipt — READ THIS FIRST, it changes the denominators

The brief says *"41 files, 385 KB, at `research/seed-documents/*.md`"*. **That path does not
exist and that count is wrong.** What is on disk:

| claim | actual | evidence |
|---|---|---|
| `research/seed-documents/` | **does not exist** | `research/` exists but holds `PARALLELISM.md`, `demo.py`, `evid.py`, `seamclaim.py`, `seams/` — a different lane |
| 41 documents | **12** | `/workspace/attachments/{hash}/pasted-text.txt`, mtime 21:07–21:31 |
| 385 KB | **96,571 bytes (94 KB)** | `wc -c` over the 12 |

**The seed set is not in `fleet-triage` at all — it is in `/workspace/attachments/<hash>/`.**
All six hashes the brief cites are present and legible, so the three named conflicts are
verifiable. Everything below is cited against the 12 files that actually exist. **29 documents
are unaccounted for**; if they land later they will not have been triaged here.

One systematic paste defect, so nothing is mistaken for a design defect later:
**run-on lines where a newline was lost inside a C block** —
`1b4ea6c10e1b809b:46` (`#define LUT_SIZE 2048extern const…`),
`8c06f5beb07cb550:24`, `3b99cfac641bf5cc:11,12,18`, `6e697bad9a48db06:20`.
The headers **do not compile as pasted**. That is a paste artifact, not a finding.

---

## 1. The table

| # | Seed claim (path:line) | What this project believes (path:line) | Verdict |
|---|---|---|---|
| 1 | Tone ramp `.:-=+*#%@`, 4-bit `T` (`bea1cc1dd6d7586b:10`) | That exact ramp class is a published failure mode: *"text-priority bias"*, degrades **as character semantics get richer* (`ASCII-VISION-LANDSCAPE.md:87,94`); project's own `fogString="@&#8x*,:. "` is *"a predicted design bug"* (`ASCII-VISION-LANDSCAPE.md:105`) | **CONFLICT** — §2 |
| 2 | *"character chatter, the chaotic, seizure-inducing flashing…"* + temporal sub-pixel AA as cure (`bb5123b9b86d4a21:13,16`) | churn **retracted** — dither is a fixed spatial pattern, written once (`ASCII-CHARSELECTION.md:150,165`; `Rasterizer.cs:53`) | **AGREE after reconciliation** — §3. The most useful item in the seed set. |
| 2b | retraction cites `Rasterizer.cs:36` and `:129` (`ASCII-CHARSELECTION.md:152,161`) | actual writes/reads are **`Rasterizer.cs:53` and `:154`** | **CONFLICT** — §3.2. The project's own law, broken by its own receipt. |
| 3 | sandbox forks state, replays history, integer loss, commit-or-reject (`8c06f5beb07cb550:2`) | "A/B the scripts, keep the better, archive the other" (`PIXELS-ARCHITECTURE.md:22,41`); *"A/B over a fixed budget of observed play, and the tail is recorded, not discarded"* (`PIXELS-ARCHITECTURE.md:104`) | **COLLAPSE (architectural) + CONFLICT (as written)** — §4. Three asks, one mechanism — and the mechanism is dead on arrival. |
| 4 | ring buffer of 128 frames, contiguous byte pool (`bea1cc1dd6d7586b:43`; `8c06f5beb07cb550:39-44`) | tail kept as 192 frames on disk, 49 MB, fits in memory (`ASCII-CELLS.md:391`) | **NOVEL** — in-memory rewind for the *controller*, not the learner — §5 |
| 5 | integer-only Q12.4, no trig/div/float (`1b4ea6c10e1b809b:1,7,12`) | determinism is doctrine, but the shipped renderer is **float** (`Rasterizer.cs:154`, `Math.Pow(z,10)`) and the 16-byte record stores `z_ndc` as `float32` verbatim (`ASCII-CELLS.md:157`) | **CONFLICT (scope)** — §6. Satisfies the doctrine; contradicts the artifact. |
| 6 | `80 × 24` text canvas (`1b4ea6c10e1b809b:8`) | `96 × 54` for the VLA line (`ASCII-VISION-LANDSCAPE.md:42`) | **NOT THE SAME REGIME** — §6. Different reason entirely. |
| 7 | 4-byte packed cell: 8-bit Braille + 3-bit glyph + 4-bit tone (`bea1cc1dd6d7586b:5,8-10`) | 16-byte cell `(glyph, rgb8, x, y, fog_id, flags, z_ndc, distance)` (`ASCII-CELLS.md:151,163`) | **NOT A CONFLICT — the brief merged two questions** — §7. And `Console.cs` is not the 16-byte record. |
| 8 | SAEs show literal *"cross-modal features"* for concepts in text-geometry layouts (`7cfaab7aedec7d0a:7`) | `n_eff≈2` is a *reporting* defect: *"n_eff computed over outputs measures agreement, not independence"* (`EXPERIMENTS.md:164`) | **NOVEL** — §8. The seed supplies the *mechanism* the project only has as a statistic. |
| 9 | headless machine stream + independent human projection over the same cells (`bea1cc1dd6d7586b:57-66`; `36e85610879d6fd5:46-50`) | label deliberately kept **out** of the observation record, in a parallel file (`ASCII-CELLS.md:171-173`); machine/human split (`bb5123b9b86d4a21:39-43`) | **AGREE** — a 4th collapse, unnamed. |
| 10 | FNV-1a **32** to *"prove execution invariance across any CPU or compiler"* (`3b99cfac641bf5cc:2,21-28`) | FNV-1a **64** throughout (`CONFORM/c4bit.py:243`; `CLOSE-LOOP.md:109`) | **CONFLICT** — §6 |
| 11 | Sobel + Bresenham edge glyphs `─ │ ╱ ╲`, Braille `U+2800–U+28FF` (`36e85610879d6fd5:9,13`; `6e697bad9a48db06:2,51-57`) | the character channel carries **depth and only depth**, no identity (`ASCII-CHARSELECTION.md:178`) | **AGREE** — structurally neutral alphabets are exactly what the project needs |

---

## 2. CONFLICT 1 — the tone ramp. The seed is *less* bad, not good.

**Both sides walk into COLM 2504.01591. Neither side escapes it.**

Counted by what a text model actually reads (`/tmp/seedchk/ramp2.py`):

| ramp | source | strongly-meaningful | which |
|---|---|---|---|
| `@&#8x*,:. ` | project `Rasterizer.cs:22` | **6/10** | `@ # x 8 * &` |
| `.:-=+*#%@` | seed `bea1cc1dd6d7586b:10` | **6/9** | `= + * # % @` |
| `░▒▓█▁▂▃▄▅▆▇` | the project's own prescribed fix | **0/11** | — |

**Where the seed set is better, plainly:** the project's ramp contains `8` and `x` — a
**numeral** and a **variable/cross**. Those are the two glyphs in the set most likely to be
read as *values*, and this is a game where the player reads numbers. The seed's ramp drops
both. The brief's framing ("the seed walks into a measured failure mode") is correct but
incomplete: **it walks into it less deeply than we do.**

**Which side is right: neither. The project's own prescription is right and the seed set
ignores it.** `ASCII-VISION-LANDSCAPE.md:108` already says the fix is *"swap the ramp for
glyphs with no semantic prior — block elements, geometric shapes, or a deliberate
scrambled-but-fixed-width set."* The seed proposes a **conventional ASCII-art ramp**, which
is precisely the category the COLM paper attacks. It is an incremental de-risking of a
finding we already published.

**Cost to switch:** the ramp is one string literal at `Rasterizer.cs:22`, plus the `fog_id`
decode in `ASCII-CELLS.md:158` and the `.cells` fixtures. Cheap. The expensive part was
already paid — the finding is already measured.

**Also note the three-channel split is right and survives intact.** Edge (`─ │ ╱ ╲`) and
Braille (`U+2800–U+28FF`) are semantically neutral; the project's own law says a neutral
channel cannot be read as words. So: **keep three channels, replace one alphabet.**

---

## 3. CONFLICT 2 — "character chatter". The reconciliation holds. This is the headline.

### 3.1 The reconciliation

The retraction was of the **mechanism**, not the **phenomenon**. Both halves survive.

- `Rasterizer.cs:53` — `offset[i,j] = rand.NextDouble() - 0.5f` is written **once, in the
  constructor**. Never redrawn. `ASCII-CHARSELECTION.md:165` is right about this.
- `Rasterizer.cs:154` — `fogId = (int)(Math.Pow(z,10) * fogString.Length + offset[i,j])`

So the glyph index is `floor(z¹⁰ · L + u)` with a **fixed** `u ∈ [-0.5, 0.5)` per cell.
As `z` moves, `z¹⁰·L` sweeps continuously. **A cell whose `z¹⁰·L` sits within 0.5 of an
integer boundary flips glyph whenever `z` crosses it** — with a completely static dither.
Chatter does not require a per-frame redraw. It requires only that the cell is near a
quantisation boundary, which is *exactly* the near-field the retracted experiment was
looking at.

**The retraction stands as written** (`ASCII-CHARSELECTION.md:168-176`): the 92.9% figure
was wrong by construction, because the experiment modelled a redraw the code does not
perform. Nothing here resurrects it.

**The seed set names the phenomenon correctly and prescribes the correct cure**
(`bb5123b9b86d4a21:16`): *"the character is locked or subtly phased using sub-pixel dithering
masks … before hard-swapping to a denser character"* — i.e. **deliberately vary the dither
per frame so boundary crossings are spread over time instead of colliding.** That is
precisely the move the fixed-offset design cannot make, and it is right.

> **This is the most useful thing in the seed set. It converts a retracted result into a
> named, named-mechanism, already-diagnosed failure mode with a known cure — for free.**

### 3.2 But the retraction's own receipt is now wrong, and that matters here

`ASCII-CHARSELECTION.md:152` says the grep *"returns two lines: 36 and 129"*, and `:161`
quotes `// Rasterizer.cs:36`. **The actual lines in the port are `53` and `154`.**

The substance is unaffected — the grep conclusion (one write, in the constructor, never
redrawn) still holds. But the retraction is the project's most-cited methodological
correction, its entire authority is *"I grepped before I modelled"*, and the grep receipt
points at the wrong file positions. `ASCII-CHARSELECTION.md:204` states the law:
*"**`grep` for every write to every field a claim depends on, before modelling it.** That
check takes one second and it would have caught this."* The check was run; the line numbers
were then transcribed wrong. **`port/` was re-synced after the retraction was written.**

**Cost to fix:** two line numbers. Do it before anyone cites that grep.

---

## 4. COLLAPSE 3 — the sandbox is the mechanism. It is also structurally dead.

### 4.1 The collapse is real — three asks, one mechanism

| ask | seed text | project text |
|---|---|---|
| A/B and keep the better | `bea1cc1dd6d7586b:54` *"If Matrix B yields a lower error score … the pointer … is instantly swapped"* | `PIXELS-ARCHITECTURE.md:22,41` |
| rewind/replay | `8c06f5beb07cb550:2` *"replays history at hardware speed"* | `PIXELS-ARCHITECTURE.md:104` |
| tail recorded, not discarded | `bea1cc1dd6d7586b:43` *"running ring-buffer of the past 128 frames"* | `PIXELS-ARCHITECTURE.md:104,108` |

All three land in `syz_sandbox.h`, a 225-line zero-allocation C header with a 128-frame
ring and static allocation. That is a genuine collapse and nobody had named it.

### 4.2 …and the gate can never fire. Executed, not argued.

`8c06f5beb07cb550`:
- `:126` `harness->sandbox_a = *live_engine;` with `:206` `&global_production_engine`
- `:183-187` `action_mask = syz_spreadsheet_step(&global_production_engine, live_frame, …)`
- `:193` `syz_sandbox_push_frame(&global_sandbox_harness, live_frame, action_mask);`
- `:161-162` `if (bit_a != target_bit) total_loss_a += 100;` where `target_bit` comes from
  `f->target_actions` — **the mask the live engine just produced.**

**`target_actions` is Matrix A's own output, replayed back to A.** The engine is asserted
deterministic twice (`36e85610879d6fd5:33` *"Perfect Determinism"*; `bea1cc1dd6d7586b:2`).
So `bit_a == target_bit` on every replay, always: **`total_loss_a ≡ 0`.**

The gate at `:167` is `if (total_loss_b < total_loss_a)`. With `total_loss_a == 0` that
requires `total_loss_b < 0`. **`total_loss_b` is a sum of non-negative penalties and is
initialised to `0` at `:130`. It cannot be negative.**

**The hot-swap is unreachable. The VLM reweighting path is dead code.**

Executed reproduction (`/tmp/seedchk/oracle.c`, 4 actions, deterministic integer engine,
candidate weights 10× the incumbent):

```
loss_a = 0   loss_b = 0
line 167 test  (loss_b < loss_a)  = FALSE -> candidate REJECTED
line 167 requires loss_b < 0 ; best achievable loss_b is 0
```

**This is the same defect class this project already measured and named elsewhere:** the
machinery audits its own outputs. Here it is not merely uninformative, it is *constant-zero
and constant-reject*. And the doc's own defence at `:222` — *"By enforcing the strict
conditional check `total_loss_b < total_loss_a`, the engine prevents macro weights from
alternating rapidly"* — describes the **symptom** (no churn) while the **cause** is that
nothing is ever accepted.

**Which side is right:** the architecture is right and worth adopting; the loss function is
wrong. The fix is small and the project already knows what a real oracle looks like —
`ASCII-CELLS.md:171-173` keeps the label **out** of the observation precisely so it can
score against a held-out target. The sandbox has no held-out target; it scores A against A.

**Cost to fix:** the target must come from outside the engine — demonstrated action, a
teacher, or a held-out split of the replay window. That is the same "the tail is recorded"
rule applied honestly: **the tail you replay against must not be the tail you produced.**

### 4.3 Second defect in the same header

`:64-66` — on pool overflow, `harness->pool_tail = 0;`. The ring in `frames[]` is evicted
independently (`:71-75` advances `head_idx`). **Wrapping the tail to zero overwrites pool
bytes still referenced by live `frames[]` entries**, silently corrupting the replay window
that the differential is scored on. Compounding: `:90` casts `&data_pool[glyph_offset]`
(a `uint8_t[]` element) to `uint32_t*` — **unaligned**, which is undefined behaviour on the
Cortex-M class the document explicitly targets (`1b4ea6c10e1b809b:23`).

---

## 5. NOVEL — in-memory rewind for the controller

The project keeps its tail, but on **disk** and for the **learner**: 16 bytes/cell, 49 MB for
192 frames, "a whole play session fits in memory" (`ASCII-CELLS.md:391`) — a file, read
after the fact. The seed proposes the same tail as a **128-frame in-register ring that the
controller re-enters synchronously before committing a weight change**
(`bea1cc1dd6d7586b:43,51`).

Nobody has built that. **What it would take:** the cell record already exists and already
round-trips (`ASCII-CELLS.md:151,163`); the 16-byte format is fixed-width and
row-major, so a 128-frame ring at 80×24 is `128 × 1920 × 16 B = 3.9 MB` — resident, not a
file. The missing piece is only the *placement*: swap the file-backed tail for a resident
ring, and give the controller a rewind that does not touch the filesystem. **This is the
cheapest genuine capability in the whole seed set.**

---

## 6. The four checks requested

**Fixed-point Q12.4, integer-only (`1b4ea6c10e1b809b`) — does it satisfy determinism?**
**Yes, and better than what we have.** No trig, no division (`RECIP_LUT` is a precomputed
reciprocal, `:23`), Q2.14 rotations, static `SyzVec3i`/`SyzCellCoord`/`SyzCameraMatrix`.
It satisfies the doctrine in `DOCTRINE.md` better than the C# it would replace. **Three
caveats, all checked:**

1. **The prose equation is wrong, the C is right.** `:16` writes
   `X_c = ((…) + (…) + (…)) >> 14 + t_x` — as typeset that reads `>> (14 + t_x)`. The C at
   `:72` correctly applies the shift to the whole sum. *(`/tmp/seedchk/prec2.c`: gcc groups
   `A+B+C >> 14` as `(A+B+C)>>14`, so `:72-74` are fine. I checked this because I was about
   to file it as a precedence bug and it is not one.)* Fix the prose.
2. **LUT truncation.** `floor(2^20 / Z)` (`:23`) loses up to 1 LSB; relative error reaches
   ~3% at the far end of the 2048-entry range. Acceptable for a display grid, not for a
   loss function being compared across candidates.
3. **It contradicts our artifact, not our doctrine.** `Rasterizer.cs:154` is float
   (`Math.Pow(z,10)`), and `ASCII-CELLS.md:157` stores `z_ndc` as `float32` **verbatim**.
   Adopting Q12.4 means the stored cell record changes, and the measured `.cells` fixtures
   with it. That is a migration, not a swap.

**80×24 vs 96×54 — same regime?  No, and the difference is the point.**
`96 × 54` is 1.78:1 — a 16:9 camera raster, sized for a fine-tuned LLM's **context-window
budget** while still resolving a gripper and movable objects
(`ASCII-VISION-LANDSCAPE.md:42,51`). `80 × 24` is 3.33:1 — a **terminal aspect ratio**
(`1b4ea6c10e1b809b:8`), and the same document puts `cx,cy ≈ (40,12)`, i.e. a screen-centre
offset for a human watching a terminal. **Same medium, opposite constraint:** theirs is
sized by tokens, ours by columns a human can scan. Do not treat the 96×54 result as
transferring to an 80×24 grid — the token-budget argument does not apply, and the
identity-pair collapse (14 of 15) was measured on a depth ramp, so it applies *harder* at
lower resolution.

**4-byte packed cell vs 16-byte — and is it human or model?**
First, a correction to the brief: **the 16-byte record is not in `Console.cs`.**
`Console.cs:9-10` is `char[,] Data` and `byte[,] Color` — two separate 2-D arrays, no packed
struct. The 16-byte record is `ASCII-CELLS.md:151,163`.

They are **not competing designs — the brief merged two different records:**

| | seed 4-byte | project 16-byte |
|---|---|---|
| fields | Braille 8 · glyph 3 · tone 4 (`:5,8-10`) | glyph · rgb8 · x · y · fog_id · flags · z_ndc · distance |
| role | **input to the control matrix** (`a₀..a₃`, `bea1cc1dd6d7586b:12-16`) | **observation record for a learner** |
| consumed by | the spreadsheet loop, every frame | stored, replayed, trained on |
| derived? | packed, lossy | round-tripped, verified (`ASCII-CELLS.md:185`) |

The seed's 4 bytes are the *activation vector*; the project's 16 are the *evidence*. Both
are for a **model** — the human projection is a separate ANSI layer
(`bea1cc1dd6d7586b:66`). So the human/model question has a cleaner answer than the brief
assumed: **`ASCII-CELLS.md:171-173` is the real answer — the label is deliberately kept out
of the observation record** so it cannot leak into the tile a learner is handed. Neither
record is for a human. The 16-byte one is right for a learner, the 4-byte one is right for
a controller, and **collapsing them would destroy the label-hygiene property.**

**Sparse-autoencoder "cross-modal features" (`7cfaab7aedec7d0a:7`) and `n_eff ≈ 2` — does it
bear on it, and is it checkable here?**
**It bears on it directly, and it is the best explanatory candidate anyone has offered.**
The project treats `n_eff ≈ 1.48–2` as a **reporting** defect — *"n_eff computed over
outputs measures agreement, not independence"* (`EXPERIMENTS.md:164`) — correct, and
Kish is the right arithmetic. But the project has **no account of *why* the outputs
correlate.** The seed supplies one: if a model has literal features that fire for concepts
in *text-based geometric layouts* (`7cfaab7aedec7d0a:7`), then two agents reading the same
ASCII frame are **not independent draws**. They are projecting one frame onto a shared,
low-dimensional, pre-trained basis. The number of independent readings is bounded by the
feature count, not the agent count — which would make `n_eff ≈ 2` a **property of the
channel**, not a property of the panel.

That is testable with what is here, and it is the one NOVEL row I would act on:
**measure agreement at the feature layer, not the verdict layer.** Concretely — score
`n_eff` over *logit distributions* on an identical ASCII frame across agents, not over
binary pass/fail. If the correlation sits as high on continuous scores as on verdicts, the
channel is the bottleneck and more agents is wasted budget. If it collapses, the panel is
fine and the verdicts were the coincidence. **That is a two-run experiment and it either
vindicates `EXPERIMENTS.md:164` or indicts it.**

---

## 7. The three highest-value conflicts

1. **The sandbox gate can never fire** (`8c06f5beb07cb550:167`, target seeded from the live
   engine's own output at `:193`). Executed proof in §4.2. Highest value because the
   mechanism is the one this lane was told to believe in, and it is **dead code** — not
   merely weak. The whole async-reweighting story depends on it.
2. **The retraction's grep receipt is wrong** — `ASCII-CHARSELECTION.md:152,161` cite
   `Rasterizer.cs:36,129`; the real lines are `53,154`. Two-character fix, but it is the
   project's most-cited methodological correction and its authority is the grep.
3. **The tone ramp, where the seed is less bad and both are wrong** (§2). The project's own
   prescribed block-element ramp scores 0/11 and the seed ignores it. Cheapest real fix in
   the project, already diagnosed, already published.

## 8. The single most useful thing the seed set has that this project does not

**A named, correct mechanism for character chatter** (`bb5123b9b86d4a21:13,16`) — and with
it, the reconciliation in §3.1: the project's retracted churn experiment was measuring a
real phenomenon through a mechanism the code does not run. The seed's temporal
sub-pixel-dither cure is a deliberate per-frame variation that the current fixed-offset
design (`Rasterizer.cs:53`) cannot perform, and it is the right move.

**We retracted a number and kept a silence. The seed set gives the silence a name, a
mechanism, and a cure.** Everything else in the 12 files is either an implementation of
something already designed here, or an implementation of it with a fatal bug.
