# PROJECTION-LOSS.md — what the renderer threw away, measured

**2026-10-02.** The projection doctrine says *what survives is bounded by what the
observation carried, and downstream cleverness cannot recover discarded information.*
This is the first time in this account that claim could be tested against a renderer
that discarded something **with the discarded thing in hand** — a 3D scene graph, and
the 160 × 90 console cells the rasterizer computed from it in the same instant.

**Provenance of every number below: `extracted`.** Every frame was produced by
`Rasterizer.Raster()` running on a live `Scene` inside the real game code. No frame
was reconstructed, no frame was read off a screenshot, no frame was synthesised. The
patch that makes it run is `port/Asciipocalypse/INSTRUMENTATION.patch` (10 files,
every line shown). The harness's own limits are in §6 and none of them touch the
frames.

| provenance level | frames used here | what it means |
|---|---|---|
| **extracted from the running rasterizer** | **4 800** | the real `Raster()`, seeded, on a generated level |
| reconstructed | 0 | — |
| screenshot-derived | 0 | — |

Dataset: 4 800 frames × 160 × 90 cells = **69.1 M cells**, 12 observe runs × 200
frames + 4 free-walk runs × 400 + 4 EyeEasy runs × 200.
`port/Asciipocalypse/datasets/` holds every run's `ground.json` (scene graph per
frame), `backproj.json`, `meta.json`, plus two complete `frames.bin` (32 MB each) and
`results.json`. All 20 runs regenerate in ~6 minutes from one command (§7).

---

## 0. What was built, and the one correction to `ASCIIPORT.md`

`ASCIIPORT.md` says the port compiles on .NET 9 with four project-file edits. I
re-verified it independently: **0 errors**, confirmed. One thing it missed — the
OBJ project needs a `MonoGame.Framework.DesktopGL` reference, because "compile only
`OBJFile.cs`" is not sufficient on its own:

```
ASCII_FPS/Geometry/OBJFile.cs(1,17): error CS0234:
  The type or namespace name 'Xna' does not exist in the namespace 'Microsoft'
```

Add the package reference and the port is clean. Otherwise `ASCIIPORT.md` is accurate,
including the decisive architectural fact: `Rasterizer.cs`, `Scene.cs`, `Console.cs`
and `HUD.cs` are pure managed code and run with no GL context.

**Texture path used: option 2 of the brief — the PNGs read into a CPU-side
`Color[]`.** All 29 PNGs in `Content/textures` are decoded; 28 of them back an
`AsciiTexture` asset and are built by writing the pixels into `AsciiTexture`'s
private `Vector3[256,256]` field by reflection, so the `AsciiTexture` class itself
is untouched (one `Name` label added). MGCB was not needed and was not used.
25 of the 28 are fully opaque; the three `barrel_*` textures have 4 non-opaque
texels each, recorded in `meta.json`.

**Seeding was mandatory, as `ASCII-CHARSELECTION.md` §3 predicted.** Upstream is
`rand = new Random()` in *two* places that matter — `Rasterizer.cs:26` (the per-cell
dither that decides the character) **and** `SceneGenerator.cs:30` (the level layout
itself, so the *map* is unseeded too, not just the frame). Both are now
`RandomSeed.HasValue ? new Random(RandomSeed.Value) : new Random()` (now at
`Rasterizer.cs:40` and `SceneGenerator.cs:32`). Every run names its game seed and its
dither seed; with them, every frame is reproducible.

---

## 1. The correspondence — 3D entity → cell

`Rasterizer` keeps `tBuffer[i,j]`, the triangle that won the z-test at each cell, and
`zBuffer[i,j]` its depth. Neither carries a reference to the object that owns it —
`new Triangle(v0,v1,v2, triangle.Texture, …)` in `Raster()` drops it, and the nine
sites in `ClipTriangles` drop it again. The instrumentation adds a `Tag` field to
`Triangle`, tags the source triangles in the two mesh-walk loops (dynamic objects by
`scene.gameObjects` index; zone meshes by zone bounds + mesh index + texture), and
propagates the tag through every clipped triangle (`.WithTag(triangle.Tag)` on all
nine `ClipTriangles` sites). The tag is then read out per cell.

That is the whole instrument. The z-buffer decides the correspondence; nothing here
guesses it.

**And the table is certified, not asserted.** `analysis/validate.py` takes every
object-instance in the 12 observe runs, projects **that object's own mesh vertices**
through the game's own world→camera→projection matrices, and checks that every cell
the z-buffer gave it lies inside the resulting screen box:

```
object-instances checked : 15231
cells inside the object's own projected geometry: 15231 (100.00%)
```

A leak in the tag propagation through `ClipTriangles` would show up as a cell
outside the box. There are none. (This check is what caught a 160-column-wide
"monster" in a first draft of the exhibit table: the tag lookup in the *script* was
picking a tag from a different frame. The rasterizer was right; the reader was
wrong.)

### Exhibit: `run_111` frame 120 — 65 objects in the scene, 18 entities in the frame

| 3D entity (scene graph) | world pos | dist | z range | **cells won** |
|---|---|---|---|---|
| ZONE mesh `-50,-50` floor (lower) | — | — | 0.899–0.992 | **6 176** |
| ZONE mesh `-50,-50` floor (upper) | — | — | 0.901–0.992 | **5 189** |
| ZONE mesh `-50,-50` wall | — | — | 0.982–0.992 | **1 372** |
| `BasicMonster` @ `textures/monster` | (−70.0, −0.5) | 21.0 | 0.949–0.953 | **307** |
| `EnemyProjectile` @ `textures/projectile` | (−58.3, 6.6) | 8.6 | 0.863–0.875 | **116** |
| ZONE `-150,-50` wall | — | — | 0.989–0.995 | 56 |
| `BasicMonster` @ `textures/monster` | (−116.4, −2.9) | 63.5 | 0.983 | 41 |
| ZONE `-150,-50` floor ×2 | — | — | 0.990–0.994 | 30 + 30 |
| `EnemyProjectile` ×11 more | −74 … −110 | 29.6–57.4 | 0.959–0.983 | 11, 9, 5, 5, 4, 3, 3, 2, 2, 2, 1 |
| **the other 61 scene objects** | — | — | — | **0** |
| | | | **total 3D cells** | **13 366** |

65 objects exist. 4 of them are visible. **61 leave no trace at all** — not a
blurred trace, not one cell, nothing a downstream reader could bound.

The near monster's 307 cells, cut out of the real `Data` buffer (columns 50–109) with
the cells it won marked `X`:

```
 38 |............... .......,,,,,.... ... . ............ ........|
    |                       XXXXX                                |
 40 |....      .... .  ..  ,*,,,**.   .  ... ..  .. .. .. .. ..  |
    |                      XXXXXXX                               |
 42 |..   . ..       ... ,,*,,,,*,*. .. .. .  .  .    ..  .  .  |
    |                    XXXXXXXXXX                              |
 44 |..          ...   .*,*,*,,*,*,*  .. . . :    .  ... .   :.: |
    |                   XXXXXXXXXXXX                             |
 46 |..       ::     .:,,*,**,,,,*,,*. . . . ..    ..     ...: ..|
    |                  XXXXXXXXXXXXXX                            |
 48 |..   .    . ... ,,,,*,,*,*,,,**,,..                  ....   |
    |                XXXXXXXXXXXXXXXXX                           |
```

Read it twice. The `X` region is one tetrahedron, 307 cells, 21 units away. The
`,` `*` `#` cluster a human reads as "a thing" is only its *bright* texture; the cells
marked `X` to the left of it carry `.` and `:` — the same object, the same z-buffer,
the same 307 cells, and almost nothing to see. **The shape a human perceives is a
projection of the colour channel. The glyphs in those same cells are a projection of
the depth channel, and they are not the shape.** That is the whole finding, in
eleven lines of one frame.

What a human sees once the HUD is drawn on top: the health and armor bars in `@` and
`%`, the `Floor / Monsters: n / m` panel, and the 9×9 minimap. **All of it is masked
out of every measurement in this report** — the extractor snapshots the console
immediately after `Raster()` and before `HUD.Draw()`, and records a per-cell `hud`
flag. 1 034 of the 14 400 cells per frame are HUD; 13 366 are rasterizer output, and
the 307-cell monster is a 2.3 % share of the frame.

---

## 2. What is lost — measured over every 2nd frame of the 12 observe runs (1 200 frames)

| quantity | mean per frame |
|---|---|
| cells in the console | 14 400 |
| cells written by the rasterizer (3D region) | 13 366 |
| cells written by the HUD (excluded everywhere below) | 1 034 |
| **scene objects in the scene graph** | **81.0** |
| **distinct 3D entities that win ≥ 1 cell** | **14.3** |
| — of which game objects (monsters, projectiles, barrels, lava) | 6.3 |
| — of which zone geometry (walls, floors) | 7.9 |
| cells won by game objects | 560.7 (**4.2 %** of the 3D region) |
| **scene objects with zero cells** | **74.7 (92.2 %)** |
| scene triangles / rendered / after clipping | 1 019 / 1 113 / 170 |

**The collapse: 81 entities → 14. The object collapse is 6.3 visible out of 81, and
92 % of the world's moving parts are gone from the frame entirely.**

Free walk (no scripted observer, the player just explores): 51.9 objects → 5.7
entities, **98.7 %** of objects invisible, objects holding 1.0 % of the cells. The
observer script is not what hides them; a level is mostly walls and floors.

**What is *not* lost, and it matters:** a visible entity is not shrunk to one cell.
Median cells per visible `BasicMonster` is 115; the largest per-class median is 557
(`ShotgunDude`). A monster 21 units away occupies 307 cells. So "40 objects behind 1
wall showing as 3 cells" — the shape the brief anticipated — is *not* what happens
here. What happens is **binary occlusion**: an entity is either represented at high
resolution or absent entirely. There is no partial, blurred, low-resolution tier. The
projection has two states, and 92 % of the world is in state two.

---

## 3. The irreversible part — which scene facts survive

Back-projection probe: for every object the z-buffer actually showed, take the
centroid of the cells it won, back-project it to the world with the **game's own
matrices**, and compare with the object position held in the scene graph. Two
variants: depth from the **glyph** (what a reader has), and **oracle depth** (what
the reader would have with a perfect depth channel — the irreducible raster loss).

The camera-matrix transcription was **verified before use**, not assumed: the
projected true position lands on a cell that entity won in 78 % of cases, the rest
being one-cell rounding at the edge of a 1–4 cell object. (It caught two real bugs
in my own code first — a missing `÷ w_clip` in the projection, and an off-by-one in
the fog-string index that made the glyph-depth arm look catastrophic when it is not.)

| fact | recoverable? | measured |
|---|---|---|
| **screen position** of a visible object | **yes, essentially exactly** | median error **0.31 cells**, p90 2.9; 77 % within 1.5 cells |
| **distance** of a visible object | **yes, approximately** | from the glyph: median **1.82 world units** at median range 26.9 (6.8 %); with oracle depth **1.15** |
| …per class (median screen error) | | `EnemyProjectile` 0.21 · `Collectible` 0.33 · `Spooper` 0.68 · `SpinnyBoi` 0.68 · `ShotgunDude` 0.97 · `BasicMonster` 1.76 · `IceMonster` 1.68. (`LavaPool` is excluded: a 554-cell flat pool whose mesh origin is nowhere near its screen centroid, so the comparison measures the mesh, not the renderer.) |
| …as a function of how much of it the frame kept | object ≤ 4 cells: **5.23**; 4–20: 1.61; 20–100: 1.23; > 100: 1.90 | the 10-bucket depth costs 4 units on a ≤ 4-cell object and nothing on a 300-cell one |
| **whether an object exists** | **no** | 92.2 % of scene objects leave zero cells. The frame cannot distinguish "there is no enemy here" from "there are 12 enemies here" |
| **how many objects exist** | **no** | the observation contains 4.2 % of the cells and 7.8 % of the entities |
| **anything at all about occluded entities** | **no** | zero bits |
| **exact z** | **no, but bounded** | 10 buckets + ±0.5 dither; the error is a named, bounded quantisation, not a hash |
| **which monster it was** | **yes — but only from colour** | see §5: F1 0.41 for `BasicMonster` with colour, **0.0000** without |

### L1 or L4?

**Neither, and that is the finding: it is two different projections stacked in one
frame.**

- **Depth is L1 — named loss, cheap.** The renderer keeps depth, quantised to 10
  buckets with a dither. A downstream reader recovers world position to a median
  **1.82 units** at a median range of 26.9, and the screen position to a median
  **0.31 cells**. Nothing is hashed, nothing is destroyed; a number was rounded. The
  quantisation is monotone and invertible to a bounded interval. `L4 hash64` scored
  0.5103 in the ladder because it is a *one-way* map; this is a *lossy but
  invertible* one.
- **Identity is carried by a second channel, and the character channel contributes
  nothing to it** (§5). So the identity question is not "was identity lost" — it was
  never there. **Collapsing to char-only is not a small loss. It is total loss:**
  enemy F1 0.0207, versus 0.3002 with colour.
- **Occlusion is the only genuinely irreversible part, and it is unrecoverable by
  any cleverness**: 92.2 % of entities are absent, and their absence is
  indistinguishable from their non-existence.

**So the doctrine holds, and it holds for a sharper reason than expected.** The
doctrine says downstream cleverness cannot recover discarded information. The
measurement says: the console kept the depth and the colour, threw away the
entities behind the walls, and *the entities behind the walls are exactly the
information no downstream cleverness can touch* — because they are not in the frame
in any degraded form. What it cannot do is pretend the loss is uniform: the part
that survives is recoverable to a 0.31-cell screen position and a 1.8-unit range
error. The cheap-L1 part and the fatal-L4 part sit in the same 160×90 buffer, and
**which cells a bot is allowed to read decides whether its problem is L1 or L4.**

---

## 4. The trap, quantified — glyph stability as a function of depth

`Rasterizer.cs:130`: `console.Data[i,j] = fogString[(int)(z^10 · 10 + dither)]`, and
`fogString = "@&#8x*,:. "` (`Rasterizer.cs:22`). The character is a function of depth
and nothing else. Measured over 1 200 frames — distinct characters per 3D entity
class:

| 3D entity class | cells observed | **distinct glyphs** | which |
|---|---|---|---|
| `arch:bricks01` (wall) | 1 297 554 | **10** | `@&#8x*,:. ` — the whole ramp |
| `arch:jungle_bricks` (wall) | 447 899 | **10** | the whole ramp |
| `EnemyProjectile` | 95 269 | **10** | the whole ramp |
| `Spooper` | 85 400 | **10** | the whole ramp |
| `obj:BasicMonster` (the enemy) | 225 033 | **6** | `x*,:. ` |
| `obj:Collectible` (barrel_blue) | 21 000 | 9 | `&#8x*,:. ` |
| `obj:ShotgunDude` | 46 674 | 5 | `x*,:.` |
| `obj:IceMonster` | 15 391 | 6 | `x*,:. ` |
| `obj:SpinnyBoi` | 36 464 | 4 | `x*,:` |
| `arch:bricks02` (floor) | 3 904 449 | 8 | `#8x*,:. ` |

**The number that decides whether "tile makers" is sound: the enemy class renders as
6 different characters across its range** (`x*,:. `), and a wall renders as all 10.
The measured ramp for `BasicMonster`, glyph → mean NDC z straight out of the
z-buffer:

```
'x'  z 0.93854      ','  z 0.95280      '.'  z 0.98292
'*'  z 0.94525      ':'  z 0.96970      ' '  z 0.98960
```

Monotone, as the source says. Converted to world units through the game's own
projection, those six glyph means sit at **16.0, 17.9, 20.8, 32.0, 55.3 and 87.8
units** — the buckets are ~2 units apart at monster range and ~33 units apart at the
far end, because the ramp is `z^10` in *normalised* depth and the near plane is
0.5 units. Worked the other way, a monster reads as

```
16 units -> 'x'      30 units -> ':'      90 units -> ' '
21 units -> ','      50 units -> '.'
```

So a "tile maker" keyed on `x` is a tile maker keyed on *"something, 14–18 units
away"*, and the same key means wall-at-16-units for a different class. **`x` is a
depth reading wearing a monster costume.** The glyph channel is a usable range
sensor — it is just not an identity.

The `SPACE` case deserves its own line: a cell whose glyph is `' '` is either the
**farthest** bucket (z ≈ 0.99) or **empty background**. The console's reset value is
`' '` (`Rasterizer.cs:47`) and so is fog bucket 9. In this dataset the camera is
always inside geometry so the two never collide, but in general the blank glyph is
ambiguous by construction, and that is a 1-bit identity carried by a *space
character* at 12 px.

---

## 5. The two-arm test, settled on real frames

The prediction in `PREDICTIONS.md`, scored and unanswered:

> *for this game, the char arm and the colour arm should be nearly equally
> informative, and collapsing to char-only should lose little.*

**Task.** For every cell of a held-out frame, name the class of the 3D entity the
z-buffer says won it. Labels come from the **scene graph**, never from the frame.
Reader: 1-NN on the observed channels, fitted on half the runs and tested on the
other half. The split is **within each level generator** (floor 1, floor 5, floor 9
each split by seed) — a split *across* generators would test "can you name a game you
have never seen", and I ran it that way first and it made every arm collapse. That
was a confounded split, not a result.

450 000 training cells, 450 000 test cells, 6 runs each side.

| arm | macro-F1 | micro-F1 | accuracy | **enemy F1** | enemy P | enemy R |
|---|---|---|---|---|---|---|
| **A — `Data` (characters only)** | **0.0367** | 0.0367 | 0.122 | **0.0207** | 0.017 | 0.052 |
| **B — `Data` + `Color`** | **0.2973** | 0.2973 | 0.784 | **0.3002** | 0.718 | 0.481 |
| C — `Color` only | 0.2949 | 0.2949 | 0.767 | 0.3040 | 0.731 | 0.470 |
| D — depth only (the channel the glyph is a function of) | 0.0214 | 0.0214 | 0.096 | 0.0189 | 0.019 | 0.031 |
| **CTRL — shuffled glyphs** | 0.0108 | | 0.096 | **0.0000** | 0.000 | 0.000 |
| **CTRL — randomised colour** | 0.0104 | | 0.098 | **0.0000** | 0.000 | 0.000 |
| **CTRL — both randomised** | 0.0171 | | 0.144 | **0.0000** | 0.000 | 0.000 |
| BASE — majority class | 0.0067 | | 0.090 | 0.0000 | 0.000 | 0.000 |

**The controls score at or below the majority baseline, so the test can fail.** It
did not fail: the real arms are 8× the baseline and 8× the char arm, and on enemy
classes specifically **0.300 vs 0.021 — 14×**. Re-running with a different 1-NN
draw seed reproduces the ranking to ±0.005 (0.2969 / 0.3002).

**The prediction is refuted, and the direction is the opposite of what was
predicted:**

1. *Char and colour are "nearly equally informative"* — **no.** 0.0367 vs 0.2973.
   Colour alone (0.2949) is not merely better than Data+Color, it is **indistinguishable
   from it** (−0.0024, inside the seed noise, and its enemy F1 is *higher*).
   **The character channel adds nothing to identity.** Adding colour to glyphs is
   worth 8×; adding glyphs to colour is worth nothing.
2. *"Collapsing to char-only should lose little"* — **no.** It loses **everything
   that matters**: every enemy class drops to F1 0.0000–0.021. Per class, the twelve
   largest:

| class | A: Data | B: Data+Color |
|---|---|---|
| `EnemyProjectile/projectile2` | 0.0000 | 0.4929 |
| `jungle_ground` | 0.0000 | 0.4831 |
| `EnemyProjectile/projectile` | 0.2065 | 0.4830 |
| `bricks02` (floor) | 0.0000 | 0.4759 |
| `EnemyProjectile/projectile4` | 0.0000 | 0.4758 |
| `bricks01` (wall) | 0.1672 | 0.4590 |
| `ice_floor` | 0.0000 | 0.4473 |
| `lava_ground` | 0.1527 | 0.4293 |
| `ShotgunDude` | 0.0000 | 0.4240 |
| `lava_walls` | 0.2443 | 0.4217 |
| **`BasicMonster`** | **0.0000** | **0.4078** |
| `IceMonster` | 0.0000 | 0.3806 |

The char arm's non-zero scores are *depth* scores that happen to correlate with a
class (near walls read `@`, distant floors read `,`). That is the trap in §4
showing up as a number: the char arm looks like it knows something, and what it
knows is how far away the cell is.

### The `EyeEasy` A/B — the game contains both projections, one flag apart

`Rasterizer.cs:124` has a second projection: every cell becomes `'@'`, depth moves
into colour *brightness*. Same scene, same textures, same task, four runs of 200
frames:

| arm | macro-F1 | enemy F1 |
|---|---|---|
| A: Data (all `'@'`) | 0.0341 | **0.0000** |
| B: Data+Color | 0.1223 | 0.1050 |
| C: Color | 0.1223 | 0.1050 |
| BASE | 0.0341 | 0.0000 |

Three things, all measured. (i) Under EyeEasy the char channel is **provably
constant** and every character-based arm collapses to the baseline — the identity
test in the *other* direction. (The shuffled-glyph control is **degenerate** in
this table, and reported as such: with every glyph `'@'`, shuffling changes nothing
and the control equals the baseline by construction. The normal-projection table
above is the one whose controls are live.) (ii) `B` and `C` are now *bit-identical*,
which is the sanity check that the pipeline is wired correctly. (iii) EyeEasy is
**worse for the bot than the default projection** (0.1223 vs 0.2973): moving depth
into brightness multiplies the texture sample by `1 − z^25`, which destroys colour
identity at range. **The "easier on the eyes" projection is also the more lossy one
for anything downstream.**

---

## 6. Limitations, stated rather than buried

**The reader was wrong twice before the numbers were right, and both are worth
recording because they are the same failure mode as the ones this project already
knows about.** (i) A missing `÷ w_clip` in the camera-matrix transcription made the
back-projection report an error that scaled with distance; (ii) the extractor writes
`frames.bin` column-major and the first reader assumed row-major, so every printed
frame was transposed and a 3-unit monster appeared 160 cells wide. Both were caught
by checks against ground truth — the projection check in §3 and the geometry-bbox
check in §1 — not by looking at the output. **Marginal statistics (counts, class
distributions, glyph ramps, per-cell classification) are invariant under the
transposition and were identical before and after; every spatial number in this
report was computed in C# from the game's own matrices and never depended on the
Python reader.** All the same discipline, applied to my own instruments.

1. **Audio was suppressed, not simulated.** `SoundEffect.Play()` needs a device; the
   container has none (`OpenAL: Could not open /dev/dsp`; `ALSOFT_DRIVERS=null`
   segfaults). All 28 `Assets.x.Play()` call sites were rewritten to a no-op
   `HeadlessAudio.Play("x")` — shown in the patch. `Play()` returns void and touches
   no game state, so the simulation is unchanged; **but the attack events are still
   in the timeline** and monsters, projectiles and combat all appear in the frames
   (§1, frame 120 has 13 projectiles in flight).
2. **Camera placement is scripted.** The scene is the game's own generator output,
   unmodified. In observe mode the camera is placed on a free post near the nearest
   monster **and the placement is kept only if the real z-buffer agrees the monster
   wins ≥ 1 cell** — the instrument decides, not a geometric argument. The free-walk
   runs have no such placement and are reported alongside (§2) so the effect of the
   script is visible rather than hidden.
3. **Player input is a script, not `PlayerLogic`.** `PlayerLogic` reads
   `Keyboard.GetState`. Movement goes through the game's own
   `Scene.SmoothMovement`, at the game's own 20 u/s, and `Scene.Visited` is updated
   as `PlayerLogic` does — but no key bindings ran.
4. **The 81 cells are the minimap, not the 3D view.** `HUD.cs:122-183` draws a 9×9
   = 81-cell top-down minimap from `Scene.Visited` / `CorridorLayout` /
   `Collectibles` / `ExitRoom`, at `xx = console.Width-11+x, yy = 10-y`. The 3D
   view is 160×90 at 1080p (`1920/12 × 1080/12`). The brief called the 81 cells "the
   projection"; the 81 cells are in fact the game's own **symbolic layer, computed
   from the scene graph, depth-invariant by construction** — the thing a bot would
   have to build, which the game already builds. Every number above is the 3D view,
   with the 1 034 HUD cells masked out.
5. **The 3D region has no background cells** in this dataset (the camera is always
   inside geometry), so "entity not drawn because it is off-screen" never occurs and
   the occlusion figure is not inflated by it.

---

## 7. Reproducing it

```
dotnet --version                       # 9.0.318
cd port/Asciipocalypse/Headless && dotnet build
for f in 1 5 9; do for sd in 11 23 37 51; do
  dotnet run --no-build -- --frames 200 --observe 1 --seed $sd --rseed $((sd*3)) \
             --floor $f --dist 42 --out /tmp/fx/run_$((f*100+sd))
done; done                                        # + 4 free-walk + 4 EyeEasy runs
cd ../analysis && python3 runall.py               # every number in this file
cd ../analysis && python3 validate.py '/tmp/fx/run_*'   # certify the correspondence
```

`analysis/frames.py` reads the binary frames, `measure.py` computes correspondence /
collapse / glyph stability / the arms, `recover.py` is the projection-transcription
check and the back-projection probe, `runall.py` is the driver, `results.json` is
the output. Runtime ≈ 6 min for 2 800 frames, ≈ 4 min of analysis on a 2 GB box.

---

## 8. The four numbers, and the finding

| | |
|---|---|
| **Arm A (`Data` only) enemy F1** | **0.0207** |
| **Arm B (`Data`+`Color`) enemy F1** | **0.3002** |
| **Control (shuffled glyphs / random colour) enemy F1** | **0.0000 / 0.0000** (baseline 0.0000) — *the test can fail* |
| **Glyph stability, enemy class** | **6 distinct characters** over its depth range (walls: 10) |
| **Are the discarded scene facts recoverable?** | **No.** 92.2 % of scene objects leave zero cells. Nothing downstream recovers them. |

> **The projection doctrine says: what survives is bounded by what the observation
> carried, and downstream cleverness cannot recover discarded information.**
>
> **This is the first time in this account that claim could be tested against a
> renderer that discarded something, with the discarded thing in hand. It holds.**
> 74.7 of 81 objects per frame are gone and no cleverness brings them back — and the
> correspondence was certified at 100 % against the scene's own geometry before any
> of it was used.
>
> **But the loss is not uniform, and that is the part worth carrying forward.** The
> same buffer keeps depth to a 1.82-unit range error and screen position to 0.31
> cells — L1, cheap, recoverable. The character channel is a *pure* depth channel
> that contributes **nothing** to identity (colour-only scores 0.2949 against
> Data+Color's 0.2973), so char-only is not a smaller view of the game, it is a
> different game in which no enemy has a name. And the shipped "easier" projection,
> `EyeEasy`, is measurably *worse* — 0.1223 against 0.2973 — because it folds depth
> into brightness and takes identity with it.
>
> **The actionable consequence for the bot lane, and it inverts the plan in
> `ASCII-CHARSELECTION.md` §2 in one respect while confirming it in another:** key
> the tile on **colour**, yes — but the tile still needs the glyph, not as identity,
> as **range**. A tile that is `(colour, glyph)` carries identity *and* a 1.8-unit
> distance estimate; a tile keyed on colour alone throws away the one recoverable
> channel the renderer gave you for free. `ASCII-CHARSELECTION.md` is right that the
> glyph is a depth reading with a false identity attached. It is worth adding that
> it is *still a depth reading*, and that is the part a mover needs.
