# RERENDER-BUILD — re-render one scene many ways and measure what survives

2026-10-02. Built against `RERENDER.md` (read first — it is the acceptance test).
Source: `github.com/wonrzrzeczny/Asciipocalypse` @ HEAD, in `port/Asciipocalypse/`.

**Provenance of every number below: `extracted`.** Not synthesised, not reconstructed.
`Rasterizer.Raster()` on a live `Scene`, headless, in-process, with the scene graph
read out beside it. The game compiles; I did not have to simulate anything.

---

## 0. The one thing that had to be fixed before anything meant anything

`RERENDER.md` names one blocker: `Rasterizer.cs:26` is `new Random()`.
**That was real and it was not the only one. The brief's blocker was the small one.**

The prior lane had already seeded the dither (`Rasterizer.RandomSeed`) and the
generator (`SceneGenerator.RandomSeed`). With `--seed 4242` I still got a
**different level every run**. `n_objects` across five arms of the *same* seed:

```
46   49   46   56   43
```

Three unseeded `Random()` sites remained, and two of them are in the scene, not the picture:

| site | what it drew | consequence |
|---|---|---|
| `Scenes/SceneGenUtils.cs:151` | **level topology** — `GenerateCorridorLayout` drew its own `new Random()` | a different maze per process |
| `GameComponents/Enemies/IceMonster.cs:42` | **aim jitter** (`delta`), not just audio pitch | the scene drifted between frames of a "fixed" run |
| `GameComponents/Enemies/Spooper.cs:76` | audio volume only | harmless, left alone |

**This is the finding I would have shipped past.** The brief said re-render does not
work until the seed is fixed, and that was true — but the seed that mattered was not
the dither's. Seeding the dither and finding the frame stable would have produced a
**beautiful, reproducible, completely invalid experiment**: five renderings of five
different dungeons, scored against five different sets of ground truth, reporting a
clean invariance number that meant nothing.

> **A frame-level digest proves the renderer is deterministic. It does not prove the
> world is.** The digest that matters is the scene graph's, and it is a different digest.

Fixed by passing the generator's already-seeded `Random` into
`GenerateCorridorLayout`, and seeding `IceMonster` from `SceneGenerator.RandomSeed`.

**Rewind now works, verified by bit-comparison across two independent processes:**

```
$ dotnet AsciiHeadless.dll --w 81 --h 45 --frames 40 --seed 4242 --rseed 777 --out a   # x2
733b291aaac8faba01117b9ebd63615a  a/frames.bin
733b291aaac8faba01117b9ebd63615a  b/frames.bin
1f51f0c465900f5216c671147f683d6c  a/ground.json
1f51f0c465900f5216c671147f683d6c  b/ground.json
```

### 0.1 One more fix, and it was mine

`OwnerId(null)` returned `0`, and the first real object was also assigned `0` — so
**every empty cell inherited the first object's label.** Owner ids now start at 1,
with 0 reserved for "no owner".

---

## 1. The gate: is the scene actually held fixed?

This is the whole experiment. If the scene moves when the projection moves, nothing
below means anything, and it is not detectable by looking at the numbers.

Fingerprint = `(n_objects, n_zones, sorted (type, position) for every game object, camera pose)`,
per frame, resolution-independent — the scene graph, never the frame.

| scene | L81_hard | M162_hard | H324_hard | L81_easy | H324_easy |
|---|---|---|---|---|---|
| 4242 | SAME | SAME | SAME | SAME | SAME |
| 777 | SAME | SAME | SAME | SAME | SAME |
| 31337 | SAME | SAME | SAME | SAME | SAME |

**GATE PASSED.** Same scene graph, 5 projections, 3 scenes, 40 frames each.
Only `--w/--h/--eyeeasy` vary. All arms 16:9 so the projection matrix is unchanged and
only the sampling grid moves.

---

## 2. The learner

Deliberately cheap, per the brief — the point is the delta, not the ceiling.

- **Task:** per-cell classification of the scene-graph owner, merged by type.
  Declared *before* scoring: `none`, `zone:bricks02`, `zone:bricks01`, `obj:BasicMonster`, `obj:Collectible`.
- **Learner:** 1-NN over the projected cell `(glyph, colour)`, exact-key lookup.
- **Split:** over **frames** — even frames train, odd frames test. A test cell came from
  a frame the learner never saw.
- **Seeds:** `game_seed ∈ {4242, 777, 31337}`, `raster_dither_seed = 777` in every arm.
  Every frame in this report came from dither seed 777; every scene from its named game seed.

**The class mix is degenerate and this caps everything below:**

```
zone:bricks02  82.3%
zone:bricks01  17.7%
obj:BasicMonster  0.0%
obj:Collectible   0.0%
                -------
majority-class floor 0.8229
```

> **99.99% of the frame is wall texture.** This is a *texture identification* task, not
> a world-model task. Read every number below as an upper bound on what the frame
> carries about the world, and the ceiling is set by a wall. See §7.

---

## 3. The same learner's score under each projection

Quantised features (`glyph/2`, 4-level colour bucket). **All five, median and spread, no max.**

| projection | cells | EyeEasy | self-score |
|---|---|---|---|
| L81_hard | 81×45 = 3 645 | off | 0.9875 |
| M162_hard | 162×90 = 14 580 | off | 0.9868 |
| H324_hard | 324×180 = 58 320 | off | 0.9860 |
| L81_easy | 81×45 | **on** | 0.8391 |
| H324_easy | 324×180 | **on** | 0.8281 |

```
median 0.9126    spread 0.1594    (floor 0.8229)
```

### The two axes, separated — this is the number that matters

| axis | levels | scores | median | **spread** |
|---|---|---|---|---|
| **resolution** | 81 / 162 / 324 | 0.9875 0.9868 0.9860 | 0.9868 | **0.0014** |
| **projection** | EyeEasy off / on | 0.9875 0.8391 | — | **0.1484** |

> **The resolution axis bought 0.0014. The one-flag projection axis bought 0.1484 —
> a hundred times more.** A 16× change in cell count moved the score by less than the
> noise floor of the learner.

**Cross-projection transfer:**

| train → test | quant | colour-only | char-only |
|---|---|---|---|
| 81 → 324 (resolution) | **0.9838** | 0.9624 | 0.8229 |
| hard → EyeEasy, same res | **0.0000** | **0.7509** | 0.0000 |
| EyeEasy 81 → 324 | 0.8229 | 0.8275 | 0.8229 |

### The falsification result

| feature space | diagonal (train==test) | off-diagonal | collapse |
|---|---|---|---|
| quant | median **0.9860** | median **0.0000** | **+0.9860** |
| colour only | median 0.9625 | median 0.8278 | +0.1347 |
| char only | median 0.8281 | median 0.0000 | +0.8281 |

> **A learner that fits its training projection at 0.986 and scores 0.000 on the
> EyeEasy projection of the identical scene, at the identical seed, having never
> seen a different world.** The character channel is discarded, depth is folded into
> brightness, and the learned representation does not exist in the new one.

**The 0.0000 needs one caveat and it matters.** With quantised features the EyeEasy
cell key-space is *disjoint* from the hard one — `unseen% = 100.00` — because EyeEasy
multiplies colour by `d(z)`. So 0.0000 is partly a lookup miss, not purely a
representation failure. **The honest version of that cell is the colour-only column:
0.9780 → 0.7509, a real 0.227 drop with only 9.8% unseen keys.** I report both; the
second is the one I would defend.

---

## 4. Spread within a scene versus across scenes

The brief asked for exactly this, and the answer inverts the expectation.

| scene | L81_hard | M162_hard | H324_hard | L81_easy | H324_easy |
|---|---|---|---|---|---|
| 4242 | 0.9878 | 0.9871 | 0.9864 | 0.8392 | 0.8284 |
| 777 | 0.9868 | 0.9862 | 0.9854 | 0.8388 | 0.8276 |
| 31337 | 0.9877 | 0.9870 | 0.9863 | 0.8392 | 0.8282 |

```
sd WITHIN a scene, across the 5 projections : 0.0751
sd ACROSS the 3 scenes (scene means)        : 0.0004
within / between                             = 211
```

**I expected within << between and got the reverse — and the reverse is worse.**

Three independently generated dungeons score **identically to the fourth decimal
place.** The between-scene variance is 0.0004: these three scenes are not three
measurements of anything. And the within-scene variance of 0.0751 is **almost
entirely the EyeEasy flag** (0.1484 of it); the three resolutions contribute 0.0014.

> **The brief's suspicion was right about the resolutions and I have to extend it to
> the scenes. Five projections of one scene are five views of one instant — measured,
> 0.0014. And three different dungeons are also ~one measurement — measured, 0.0004.**
> **On this metric, n_eff ≈ 1 in both directions.** Do not quote 15 cells as 15 samples.

---

## 5. The control arm

Per-frame random permutation of cell order: features shuffled within each frame, labels
left in place. Same learner, same split, 27 pairs, hard arms (the easy arms contribute
100%-unseen zeros that hide the comparison).

| arm | median | range | sd |
|---|---|---|---|
| **real** | **0.9856** | 0.9822 – 0.9878 | 0.0015 |
| **control (shuffled)** | **0.7121** | 0.6994 – 0.7306 | 0.0091 |

```
gap +0.2735, with non-overlapping ranges.  majority-class floor 0.8229.
```

> **The control separates cleanly. The test can fail, so its failure elsewhere means
> something.** Note the control scores *below* the majority floor: the learner is
> confidently wrong under permutation, not defaulting to a constant. That is the
> stronger form of this control — it is not a lazy predictor being lucky.

---

## 6. Channel structure — this settles a live prediction

`ASCII-CHARSELECTION.md` §1 claims the glyph is a pure function of `z` and carries no
identity. `ASCIIPOCALYPSE.md` / `PREDICTIONS.md` carries a live prediction that the
char arm and colour arm would be *nearly equally informative* here, extrapolated from
the projection ladder's L1 colour-collapse result.

| channel | self-score (hard) | vs floor 0.8229 |
|---|---|---|
| **colour only** | **0.9780** | +0.155 |
| char only | 0.8281 | **+0.005 — at chance** |

> **The char arm is at the majority-class floor. The prediction is refuted, and
> `ASCII-CHARSELECTION.md` §1 is confirmed by measurement rather than by reading.**
> `console.Data[i,j] = fogString[fogId]` reads `z` and `offset` and nothing else, and
> here is the number: a learner given the entire character channel learns nothing about
> what is in the world.
>
> The ladder's L1 result (colour-collapse retained ~99% of recoverable value) was a
> fact about a task whose channels agreed. It does not transfer. Same error as
> `BattenSpline` prose-only, and the correction in `ASCII-CHARSELECTION.md` was right
> to call it a correction to the doctrine rather than to the prediction.

---

## 7. What would make this wrong, and what it is actually worth

**The binding limitation, stated plainly: this is a wall-detection task.**
`BasicMonster` and `Collectible` are 0.0% of cells. The camera is a scripted walk that
never gets near anything alive — I tried `--observe 1 --dist 25`, which put 42 owners
in the table, and the monsters were still 0.1% and below. The score is 0.986 on
"which brick texture", against a floor of 0.823. **The dynamic part of the world is
absent from the measurement.**

So: the invariance machinery is real and the collapse is real, but
**"the learner collapsed under re-projection" here means "the learner learned to read
brick texture and the new window does not contain brick texture."** That is a true
statement and a much smaller one than "it learned the renderer."

**To get the experiment the design actually wants, in order:**

1. **Put something alive in the frame.** A camera that holds a monster at a known
   distance. `PlaceObserver` already searches for a position where the *z-buffer*
   confirms the monster won a cell — the machinery exists and the placement is just
   not aggressive enough. This is the single highest-value change.
2. **Stop merging the monster classes away.** With monsters at 0.0% the coarse label
   map is doing the work of a 2-class texture problem.
3. **A real learner, not 1-NN.** The brief permits a cheap learner and the collapse is
   unambiguous, but a decision tree would tell us whether the collapse is the
   representation or the lookup. The `colour`-only arm at 0.7509 is the honest
   cross-projection number and a tree might move it.
4. **More scenes is nearly worthless here** (between-scene sd 0.0004) until the class
   mix is fixed. More *projections* is also nearly worthless on the resolution axis
   (0.0014). **The only axis that moved anything was the one flag.**

**One methodological note for whoever runs this next.** I read the owner label from
bytes 5–6 of the cell record. The layout is `char | color8 | float z | owner | tex | hud`,
so the float occupies 2–5 and the owner is 6–7. My first full run produced seven owner
ids spaced exactly 256 apart and a class mix that was pure noise. It produced
plausible-looking numbers the whole way down.
**The check that caught it was printing the raw id distribution against
`meta.json["owner_table"]` and noticing the ids exceeded the table length** — not any
accuracy figure, all of which looked fine. This is the sixth instrument-shaped mistake
in this account and it is the cheapest one yet to make: *every field a claim depends
on, read its offset out of the writer, not out of the format you remember.*

---

## 8. The instrument, if anyone wants the data

```
Headless/Program.cs              frame extractor: 1 record per cell, stride 11
ASCII_FPS/Scenes/SceneGenUtils.cs  seeded corridor layout   [RERENDER FIX]
ASCII_FPS/GameComponents/Enemies/IceMonster.cs  seeded aim jitter [RERENDER FIX]
analysis/rerender_invariance.py  the gate, the matrix, the control
analysis/rerender_invariance.json  every number above
```

Reproduce: `dotnet AsciiHeadless.dll --w 324 --h 180 --frames 40 --seed 4242 --rseed 777
--eyeeasy 0 --out out/`, then `python3 analysis/rerender_invariance.py out/`.

> **The general layer really is `scene → triangles → z-buffer → cells`, and the specific
> layer really is replaceable, because the general layer emits text.** That part of
> `RERENDER.md` checked out. The scene graph and its projection came out of the same
> process, in the same call, every frame — and once the *level* is seeded too, they
> are byte-identical across renders. **That is the part nobody else in this account
> has, and it cost three one-line RNG fixes.**

---

## The three sentences

1. **Same learner, five projections, median 0.9126, spread 0.1594** — and the spread
   is 0.0014 on resolution and 0.1484 on the one flag. A 16× change in window moved
   nothing; changing the projection destroyed the representation.
2. **Within-scene sd 0.0751 versus across-scene sd 0.0004** — n_eff ≈ 1 in *both*
   directions. The three dungeons are one measurement, and three of the five
   projections are one view.
3. **Control 0.7121 versus real 0.9856, non-overlapping** — the test can fail, so the
   collapse means something. But the class mix is 99.99% wall, so what collapsed was
   a texture reader, and that is the caveat to read first.
