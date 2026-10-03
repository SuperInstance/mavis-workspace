# ASCII-CELLS — the frame, the cell record, the two arms, and the trap

Build lane, 2026-10-02. Substrate: `SuperInstance/Asciipocalypse`
(`SuperInstance/Asciipocalypse@3d144f9f03a3f6a21f87242ec3ab586f065722e6`, 2021-06-15).
Read `ASCIIPOCALYPSE.md` first; this file settles its prediction and hits its trap.

Artifacts live in `ASCII-CELLS-assets/`.

---

## 0. The answer first

**The prediction is FALSE as stated, and true by coincidence. Colour is load-bearing
for this game — but not for the reason anyone would guess, and the char arm is *not*
the cheap substitute the prediction implies.**

| | CHARS | COLOURONLY | BOTH | CTRL_SHUF | CTRL_FLATC |
|---|---|---|---|---|---|
| **A — IDENTITY** (is a living enemy here) | 0.7162 | 0.7044 | **0.7681** | **0.5000** | 0.7159 |
| **B — DEPTH** (is the surface within 25 units) | **0.9755** | 0.6562 | 0.9765 | 0.4876 | 0.9754 |

balanced accuracy, mean of 5 scene-grouped folds, held out. `CTRL_FLATC` is
`BOTH` with the colour channel flattened — **it lands on the CHARS number in both
rows** (0.7159 vs 0.7162; 0.9754 vs 0.9755). `CTRL_SHUF` is `CHARS` with the fog
ramp permuted — **it lands on chance in both rows.**

The pooled numbers say the two arms are peers. **They are not.** The pooled identity
task is confounded: enemies stand in room centres, so they are systematically *nearer*
than the walls around them, and the glyph is a pure function of depth. Hold depth
fixed and the tie disappears completely:

| stratum (glyph = depth band) | cells | CHARS | COLOURONLY (1-NN) | CTRL_FLATC |
|---|---|---|---|---|
| `'@'`  < 3.85 u | 9 382 | 0.5035 | **0.9037** | 0.5000 |
| `'&'`  3.85–5.76 | — | — | — | — |
| `'#'`  5.76–7.67 | 6 963 | 0.5298 | **0.9738** | 0.5396 |
| `'8'`  7.67–9.94 | 50 377 | 0.8275 | **0.8697** | 0.8291 |
| `'x'`  9.94–12.87 | 72 269 | 0.5000 | **0.8621** | 0.5000 |
| `'*'`  12.87–16.95 | 57 799 | 0.5386 | **0.8629** | 0.5336 |
| `','`  16.95–23.18 | 52 506 | 0.5194 | **0.6897** | 0.5167 |
| `':'`  23.18–34.08 | 55 813 | 0.5000 | **0.6245** | 0.5000 |
| `'.'`  34.08–58.44 | 40 948 | 0.5000 | **0.6023** | 0.5000 |
| `' '`  > 58.44 | 19 140 | 0.5000 | **0.8333** | 0.5000 |

**Inside a fixed glyph the char arm has structurally nothing left — 0.5000 in five of
nine strata — while colour reaches 0.60–0.97.** The char arm's residual identity
signal is entirely *proximity*: a monster in a room is closer than the room's walls.
That is a fact about level geometry, not about the projection, and it evaporates the
moment a monster stands at the end of a corridor or behind a pillar.

**So: colour carries the enemy-identity load. The text arm is blind to something a
player can see.** The design consequence is the opposite of "char-only loses little":
char-only is a *proximity detector*, colour is a *material detector*, and a player
needs both.

---

## 1. Provenance of every frame: EXTRACTED, not reconstructed

Three provenance levels exist and they are not equal. This document ships only the
top one and says so.

| level | what it means | used here |
|---|---|---|
| **EXTRACTED** | the game's own rasteriser ran and wrote `Console.Data` / `Console.Color` | **yes — all 192 frames** |
| RECONSTRUCTED | a re-implementation of the renderer produced the frame | no |
| SCREENSHOT-DERIVED | a PNG of the window, OCR'd or eyeballed | no |

**I ran the game.** `dotnet`/`msbuild` were absent, so I installed .NET SDK 8.0.425
from `dot.net` and compiled the game's own sources into a headless harness.

* `git status --porcelain` on the clone is **empty**. All 72 `.cs` files are
  byte-identical to the upstream commit; digests in
  `ASCII-CELLS-assets/game-source-sha256.txt`. **No game file was edited.**
* The harness (`ASCII-CELLS-assets/headless-*.cs`) links the tree verbatim and
  **excludes exactly two files**: `ASCII_FPS/ASCII_FPS.cs` and `ASCII_FPS/Program.cs`,
  the `Game`/`Main` shell. Nothing else.
* Everything that computes a frame — `Rasterizer.cs`, `Camera.cs`, `Mathg.cs`,
  `Console.cs`, `Zone.cs`, `Scene.cs`, `SceneGenerator*.cs`, `Triangle.cs`,
  `MeshObject.cs`, `SceneGenUtils.cs` — is the game's own code.
* Three substitutions, all outside the rasteriser and all disclosed:
  1. `class ASCII_FPS` is a stand-in (the real one derives from `Game` and needs a
     `GraphicsDevice`). It carries the four members the compiled code touches:
     `triangleCount`, `triangleCountClipped`, `zonesRendered`, `PlayerStats`/`Scene`/`HUD`.
  2. **Textures.** MonoGame's Content Pipeline needs a GPU. The harness decodes each
     `Content/textures/*.png` directly and populates the private `AsciiTexture.colors`
     field with exactly the data its own constructor would have produced
     (`colors[i,j] = (R,G,B)/255`). `AsciiTexture.Sample()` — the only sampling the
     renderer uses — is the game's code. PNGs are 8-bit non-interlaced RGBA/RGB, 256×256.
  3. **Models.** `OBJFile` is a 4-field struct that the content pipeline normally
     fills; the harness reads the game's own `.obj` files. Vertex and texcoord data
     are the repo's bytes.
* `MonoGame.Framework.DesktopGL` 3.8.1.303 is used for `Vector2/3/4`, `Matrix`,
  `Color`, `Point` — so the transform arithmetic is the real MonoGame implementation,
  not my transcription of it.

**One honesty note on the last point, because it is the only real fidelity risk left:**
`Vector3.Transform` / `Matrix` are real MonoGame code, so matrix convention and
float behaviour are not mine. But `AsciiTexture.Sample` and my PNG decoder meet in a
way the real build does not: the real build converts `Texture2D` → `Color` → `ToVector3()`.
I reproduce the same `(r/255, g/255, b/255)` and the same 4-plane-to-2D index
`i + j*256`, and `Mathg.ColorTo8Bit` is the game's. I did not find a way to cross-check
that against a real `GraphicsDevice` in this sandbox, so **the colour values are
high-confidence but not byte-proven against a live game.** The glyph and depth channels
carry no such caveat — they are pure float geometry.

**Every frame file names its own provenance in line 1.** 192 frames, 24 generated
levels, 8 camera poses each, 160×90 console (the game's own `1920/12 × 1080/12`).
A frame is `Data` + `Color` + the z-buffer, as text:

```
# Asciipocalypse frame -- EXTRACTED by executing the game's own Rasterizer.Raster()
# scene 3 floor 4 pose 3 tag mon_ShotgunDude_d26 cam=(-197.7,0.0,-25.9) rot=-0.088
# console 160x90  triangles=586 clipped=155 zones=3
# DATA -- Console.Data[i,j], the 10-character fog ramp @&#8x*,:. selected by the z-buffer
:::::::::::::::::::,:::::::::::::::::::::::::::::::::::::::::::::,:::::::::::::...
...
```

Full text: `ASCII-CELLS-assets/frame-scene003-pose03.txt` (a `ShotgunDude` at 26 units).
**Nothing was screenshotted.** Screenshotting would have thrown away the substrate.

### Ground truth, and its falsification

Per-cell labels come from a **second rasterisation of the same scene with the same
camera**, in which every enemy triangle carries a flat marker texture. Zones are
untouched, so the z-buffer picks the same nearest surface; only the winning triangle's
sampled colour changes. Per-frame census over 2 764 800 cells:

```
# cells total 2764800
# cells where the enemy marker texture won the z-buffer: 142803
# of those, how many the REAL frame also shows as colour 0x38 (marker code): 0
# real-frame cells with colour 0x38: 0
# distinct glyphs observed in real frames: char count
#   ' ' 187060  '@' 67594  '&' 27496  '#' 77426  '8' 369496
#   'x' 520976  '*' 419683  ',' 382576  ':' 404506  '.' 307987
# distinct colours observed: 102
```

**Zero real-frame cells carry the marker code `0x38` across 2 764 800 cells, and zero
marked cells collide with a real colour.** The marker is a perfect discriminator in
this corpus: the label is exact, not sampled, and not an approximation.

The glyph census also shows **all ten fog levels occur** in this corpus, `'@'`
(under 3.85 units) at 2.4% of cells — so the ramp in §3 is measured across its whole
range, not extrapolated from the far end.

---

## 2. The cell record — 16 bytes, fixed width, and round-tripped

```
off size field     meaning
  0    1  glyph    ASCII code point of Console.Data[x,y]  (the 10-glyph fog ramp, or 0x20)
  1    1  rgb8     R:3 G:3 B:2 -- byte-for-byte Console.Color[x,y], as Mathg.ColorTo8Bit packs it
  2    2  x        uint16 LE, column
  4    2  y        uint16 LE, row
  6    1  fog_id   0..9 index into "@&#8x*,:. ", or 10 for "no surface" (zBuffer == 1)
  7    1  flags    bit0 surface present; bit1 interior (3x3 not edge-clamped); rest 0
  8    4  z_ndc    float32, the game's own Rasterizer zBuffer value, verbatim
 12    4  distance float32, world distance recovered from z_ndc via the game's own projection
  = 16 bytes, row-major, y*width + x
```

First three cells of row 0 of `scene003_pose03.cells`:

```
0000000  20 ff 00 00 00 00 09 00  00 00 80 3f 00 00 7a 44
0000016  20 ff 01 00 00 00 09 00  00 00 80 3f 00 00 7a 44
0000032  20 ff 02 00 00 00 09 00  00 00 80 3f 00 00 7a 44
         ^^  ^^ |  |     |  |     ^^^^^^^^    ^^^^^^^^
         |   |  |  |     |  |     z_ndc = 1.0  distance = 1000.0
         |   |  x  y     fog=9 flags=0        (no surface won these cells)
         |   colour 0xff  <- the Console reset value
         glyph 0x20 = ' '
```

**The label is deliberately not in this record.** A label inside the observation record
leaks the answer into the tile a learner is handed. Labels are a parallel 2-byte file
(`.label`, `enemy` + pad) — `ASCII-CELLS-assets/scene003_pose03.label`.

Round trip, on 8 frames, reading the binary back and rebuilding the frame:

```
  scene000_pose00.txt  xy=True colour=True fog=True z=True glyph=True  OK
  ... (8 frames)
all round trips clean
```

`x`,`y`,`colour`,`fog_id`,`z_ndc` and the reconstructed `Data` grid all match the
source text exactly. 192 frames packed, 49 MB total, 230 400 bytes each — 16 × 160 × 90.

---

## 3. The trap, decoded

`ASCIIPOCALYPSE.md` flagged: *"the z-buffer is also used to select which character is
written"*, so the same enemy renders as a different character at a different distance.
Here is the actual code path (`Rasterizer.cs:22` and `:132`):

```csharp
private const string fogString = "@&#8x*,:. ";
...
int fogId = (z < 0) ? 0 : Math.Min((int)(Math.Pow(z, 10) * fogString.Length + offset[i,j]), fogString.Length - 1);
console.Data[i,j] = fogString[fogId];
console.Color[i,j] = Mathg.ColorTo8Bit(triangle.Texture.Sample(uv) * (1f + Gamma));
```

**The character is a function of `z` and nothing else. Not of the object.** Inverting
the ramp through the game's own projection matrix (`Camera.cs:53`, near 0.5, far 1000):

| glyph | `@` | `&` | `#` | `8` | `x` | `*` | `,` | `:` | `.` | ` ` |
|---|---|---|---|---|---|---|---|---|---|---|
| distance ≥ | 3.85 | 5.76 | 7.67 | 9.94 | 12.87 | 16.95 | 23.18 | 34.08 | 58.44 | 163.6 |

**The trap is worse than stated, and the correction is the finding:**

> It is not that *the same* enemy renders differently at different distances.
> **No object renders as a distinct character at all.** A `ShotgunDude`, a wall, a
> lava pool and a barrel at 12 units all write `x`. The glyph alphabet is a 10-level
> depth quantiser spanning 3.85 → 163 world units, plus ±1 level of dither
> (`offset` ∈ [-0.5, 0.5) on the index). That is ~3.3 bits, and it is **depth, not identity.**

So:
* **The char arm is a depth channel.** Task B: 0.9755 chars vs 0.6562 colour. It wins by 32 points.
* **The colour arm is a material channel.** It is the *only* channel that knows what a
  thing is, because it is a sample of that thing's texture.
* A mover scripted on raw characters is chasing a distance glyph, exactly as warned.
  And the failure mode is worse than "thrash": at matched depth it is not degraded,
  it is **provably at chance**.

**Measured evidence for the neighbourhood requirement.** Same glyph, same coarse
colour, bucketed by how many of the 8 neighbours share the centre glyph:

| `'x'` + colour-cq41 | 1 of 8 | 2 | 3 | 4 | 5 | 6 | 7 | 8 of 8 |
|---|---|---|---|---|---|---|---|---|
| enemy rate | **0.0862** | 0.0782 | 0.0768 | 0.0715 | 0.0514 | 0.0295 | 0.0128 | **0.0047** |

An 18× swing from neighbourhood alone, at identical glyph *and* identical colour.
`'x'` standing alone is 18× more likely to be an enemy than `'x'` inside a field of
`'x'`. **The tile is `f(glyph, colour, neighbourhood)`; the brief's claim holds, and
here is the number for it.**

**Held out, no learner, on 4 levels never used to fit the table:**

| tile | balanced accuracy | TPR | TNR |
|---|---|---|---|
| always-negative baseline | 0.5000 | 0.000 | 1.000 |
| glyph alone | 0.7510 | 0.662 | 0.841 |
| **(glyph, coarse colour)** | **0.8341** | 0.691 | 0.977 |

Coarse colour is `R:3>>1, G:3>>1, B:2` — a re-quantisation of the game's own 8-bit
console byte into 4×4×4 material buckets, not a different channel. Adding it is worth
**+0.083 balanced accuracy** and **+0.136 TNR** on unseen levels.

### The fallback was not needed, and the scene graph was not used

The brief's fallback — take tiles from the 3D scene graph when the projection cannot
carry them — turned out to be unnecessary. The projection carries everything the
question needed, *provided the tile is `(glyph, colour, neighbourhood)`*. Glyph alone
was never going to work, and it is worth being explicit that this was a
**negative** result about glyph-alone tiles, not a failure of the projection.

---

## 4. The enemy roster, verified by execution, not by reading filenames

160 generated levels, 40 per generator, floors 1–10, every object the real
`SceneGenerator` placed:

```
BasicMonster  4206     IceShotgunDude  259     LavaPool       643
BushMonster    341     Collectible     940     PoisonMonster  727
IceMonster     750     ShotgunDude    2256     SpinnyBoi      665
Spooper       1439
```

**The brief's roster was wrong in both directions, and reading filenames would not
have caught either.**

* **Missing: `BasicMonster`** (4 206 — 37% of everything, the most common enemy in
  the game) and **`IceMonster`** (750). The brief listed 8 kinds; there are **8 monster
  classes**, but not the 8 named.
* **Correct and confirmed: `IceShotgunDude`** (259). An earlier 60-floor sample showed
  **zero**. Its weight is `iceShotgunChance × monsterChanceShotgun`, which is exactly
  0 below floor 2 and ~3.5% at floor 5 (`SceneGeneratorIce.cs:28-34`). Reading the
  filename would have "confirmed" it and a 60-floor sample would have "refuted" it.
  **Both would have been wrong.** Only execution settles it.

With `Collectible` and `LavaPool` that is **10 `GameObject` kinds**, not 9.

---

## 5. The two-arm test, and why it can fail

**Task A — IDENTITY.** Per cell: is the nearest surface a living enemy? Label from
the marker-texture pass (§1). Positives 5.17% pooled.

**Task B — DEPTH.** Per cell: is the nearest surface within 25 world units? Distance
recovered from the game's own `zBuffer` through the game's own projection matrix —
not estimated, not binned by hand. Positives: see `twoarm_results.json`.

Every arm sees the **same 3×3 neighbourhood of the cell**, so spatial context is held
constant and the only thing that varies is *which fields the arm can read*.
Folds are grouped by **scene**, so no frame is scored by a model that saw its own level.
Classifier: binary logistic regression, L2, full-batch gradient descent, deterministic.

**The controls, and this is the part that decides whether any of it means anything:**

* `CTRL_SHUF` — `CHARS` with the ten fog glyphs permuted. **0.5000 on IDENTITY
  (TPR 0.000, TNR 1.000) and 0.4876 on DEPTH.** It collapses to the majority class in
  both tasks, exactly as it must. **The test can fail.** Had it scored like the real
  arms, the whole experiment would have been uninformative and I would have said so
  rather than reporting a ranking.
* `CTRL_FLATC` — `BOTH` with the colour channel flattened to a constant. It reproduces
  the `CHARS` number to within 0.003 in both tasks (0.7159/0.7162 and 0.9754/0.9755).
  **Colour adds nothing on top of the glyph in the pooled view** — and that is exactly
  why the pooled view is the wrong instrument. §0's matched-depth table is where the
  two arms separate, and the stratified `CTRL_FLATC` returns to 0.5000 in five of nine
  strata while `COLOURONLY` sits at 0.60–0.97.

**Two instrument bugs I hit and fixed, because they would have produced the wrong
headline and one of them is the exact failure this project has been bitten by:**

1. Balanced accuracy alone cannot distinguish "no information" from "the classifier
   collapsed to one class" — both are 0.5000. My first run reported `CHARS = 0.5000`
   on IDENTITY with TPR 0.000, TNR 1.000, which reads like a finding and was actually
   an underfit. After fixing the optimiser the same arm scores 0.7162. **Every table
   above reports TPR and TNR.** Inside a stratum the char arm's *centre* glyph is
   constant by construction, so its only remaining variance is neighbourhood shape;
   I report that measured variance (1.2–4.4) rather than claiming the arm is
   structurally empty. The falsification control is what settles it, not the argument.
2. The linear colour readout collapses to 0.5000 in several strata where a
   non-parametric 1-NN gets 0.86–0.97. A weak learner would have been reported as
   absent information. Both are in `taskC-matched-depth.py`; **the 1-NN column is the
   one to trust.**

Base rates: IDENTITY 5.22% positive, DEPTH 63.15% positive; 250 cells sampled per
frame, 48 000 cells per task in total.

---

## 6. JEV: credential failure, not transport failure

Per `JEV-CONTRACT.md`, a 503 or a TLS EOF is transport failure and says nothing about
request shape. What I actually got:

```
POST https://api.typesafe.ai/v1/systemone   (choice / criteria:{label:null}, per contract)
  no Authorization header  -> HTTP 403  {"error_type":"authentication_error","message":"Must supply an API key!"}
  placeholder bearer       -> HTTP 401  {"error_type":"authentication_error","message":"Cannot authenticate with the server."}
```

**The endpoint is alive and the TLS is healthy.** 403 and 401 with a structured
`authentication_error` are a *credential* result, categorically different from the
503/EOF mode the contract warns about. `TYPESAFEAI_KEY` is not present in this
environment, so **the remote arm did not run and no JEV number is reported.**
The local arm (logistic regression over 3×3 cell patches) is what produced every
score above, and it is labelled as such. Nothing here is a claim about `choice` vs
`score` vs `noul` request shape — I could not test it, so I am not going to.

**No distribution was collapsed to a scalar.** Per-fold numbers, ranges and TPR/TNR
are in `ASCII-CELLS-assets/twoarm_results.json`; the summary cells in §0 and §3 are
means over 5 scene-grouped folds with sd and range in the JSON beside them.

---

## 7. What this changes, and what it does not

**Settles:** the prediction in `ASCIIPOCALYPSE.md` / `PREDICTIONS.md`. Char and colour
are *not* peers. Colour is the only identity channel; glyph is a 10-level depth
quantiser. Collapsing to char-only does not "lose little" — it loses **all** identity
information at matched depth, and its apparent parity in the pooled test is an artifact
of enemies happening to stand nearer than walls.

**Settles:** the trap. The tile must be `f(glyph, colour, neighbourhood)`; the
neighbourhood alone is worth 18× in enemy rate at fixed glyph and colour.

**Settles:** the roster, by execution, in both directions the brief got wrong.

**Does not settle:** whether a *vision* model reading the rendered screen is
independent. It is not — it reads a re-rasterisation of this same buffer, exactly as
`ASCIIPOCALYPSE.md` already argues. I did not test it and it is not mine to test.

**Does not settle:** player-bot technique, ASCII-agent prior art, or mover scripts.
Dispatched separately. This lane produced a substrate, a record, two arm scores, a
control that scores badly, and a taxonomy.

**What I would do next, in order.** (1) Ship the cell record as the archival format —
16 bytes/cell, 49 MB for 192 frames, and a whole play session fits in memory, which
is the thing that was never true of the pixel version. (2) Take the fast mover's tile
set from the **scene graph** for training labels and the projection for inference, so
the mover is never asked to infer identity from a glyph. (3) Re-run §0's stratified
table on a corpus that includes corridors and pillars, where the proximity confound is
absent and the char arm's pooled score should collapse toward 0.5 — that is the
prediction this document makes, and it is falsifiable.

---

## Provenance index

| file | what it is |
|---|---|
| `frame-scene003-pose03.txt` | an extracted frame as text: Data, Color, z, labels |
| `frame-scene000-pose00.txt` | the game's own start view |
| `frame-census.txt` | marker-code false-positive / false-negative audit |
| `scene003_pose03.cells` | the 16-byte cell record, 160×90, little-endian |
| `scene003_pose03.label` | parallel 2-byte ground-truth labels |
| `headless-Harness.cs` / `-Shim.cs` / `-csproj` | the harness; game sources linked, not copied |
| `game-source-sha256.txt` | all 72 upstream `.cs` digests (tree is clean) |
| `twoarm.py`, `twoarm_results.json` | the two-arm test, per fold |
| `taskC-matched-depth.py`, `taskC.json` | identity at matched depth |
| `taxonomy.py` | tile = f(glyph, colour, neighbourhood), held out |
| `cellrecord.py` | packer + round-trip verifier |
| `roster-by-execution.txt` | 10 GameObject kinds from 160 generated levels |
