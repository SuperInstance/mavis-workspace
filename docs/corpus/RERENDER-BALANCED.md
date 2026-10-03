# RERENDER-BALANCED — was the collapse a projection, or just class imbalance?

2026-10-02. Follows `RERENDER-BUILD.md`, which reported **0.9856** and whose own caveat
("99.99% wall, so what collapsed was a texture reader") is the finding.
**The caveat was right and the number was a frequency artifact.** Rebuilt to find out.

---

## 0. The answer first

> **The collapse is a projection effect. It is not a frequency effect. And the original
> 0.9856 was almost entirely frequency.**

Two things had to be separated, and both separated cleanly:

| claim | verdict | evidence |
|---|---|---|
| Does the collapse shrink as the class mix balances? | **No — it is flat** | prior 0.167 → 0.80 moves the projection collapse by 0.012 (0.2246 → 0.2127) |
| Was the original 0.9856 measuring representation? | **No** | same instrument, balanced task: in-projection is **0.546**, not 0.986 |

**The 0.9856 was a frequency result wearing an invariance costume.** Holding the learner,
the instrument, the rasterizer and the scene-graph ground truth fixed and changing only
the class prior moves the score by 0.44. That is the size of the artifact.

---

## 1. The instrument was degenerate in three separate ways, and I only found them by building the fix

Rebuilding this properly surfaced bugs that the first run's numbers could not have.

**1.1 The learner was a memoriser, not a learner.** The first run used 1-NN over exact
`(glyph, colour)` keys. Each texture class spans a *cloud* of colours; 1-NN memorises the
handful it saw and is wrong on the rest, so its accuracy was just the class prior. At
prior 0.99 it scored 0.9280 ≈ the prior. Replaced with a **nearest class centroid** in
`(r, g, b, glyph)` — it reads the cloud, so in-projection accuracy measures whether
identity is recoverable *at all*, independently of frequency.

**1.2 The control was not a control.** I shuffled the *index list* within each frame.
That moves features and labels together and changes nothing — the control scored 0.8474
against a real arm of 0.8251, i.e. the control beat the experiment. The correct control
shuffles the labels independently. Same family as the broken control in the first report,
one level up: **a control that shares the transformation under test is not a control.**

**1.3 The class prior has to be an input, not a property of the render.** The first
design varied the *scene* to change the mix. Instead the same pixels are resampled to an
exact prior, with the **dataset size held constant**, and the **test set always balanced**.
A balanced test set is what makes chance = 1/6: if the test set carried the same skew, a
classifier that always predicts the majority class would score the prior and look like a
real learner. That bug made the first control read 0.8765 at prior 0.95.

> **Three of these are "I modelled a more impressive thing than the code does."** That is
> now the single most productive error class in this account and it is worth naming as
> such: every one of them produced *more dramatic* numbers than the truth, and not one
> produced a less dramatic one.

---

## 2. The balanced scene

Built **inside the game's own scene graph** and rendered by the game's own
`Rasterizer.Raster()`. Nothing is faked: the meshes are real `Triangle` lists, the
textures are the game's own `AsciiTexture` objects read from the real PNGs, and the
z-buffering, depth ramp and colour quantisation are the game's. What changed is *which
meshes are in the scene* — the specific layer, with the general layer untouched.

```
Headless/ProbeScene.cs   six unit quads, MATCHED depth 60, MATCHED size 14,
                         arranged in a 2x3 grid, camera drifting slightly per frame
                         so the even/odd frame split is a real generalisation test
```

Identities, all at the same distance from the camera, so the only thing distinguishing
them is what the colour channel carries: `monster`, `poison_monster`, `spinny_boi`,
`ice_monster`, `shotgun_dude`, `ice_shotgun_dude`.

**Chance = 1/6 = 0.1667. Oracle nearest-centroid ceiling (colour only, fitted on the same
data) = 0.5362.** The task is solvable; the learner reaches 0.546.

### 2.1 One thing I had to remove, and it is a real finding about the substrate

The first balanced attempt used `barrel_red`, `barrel_green`, `barrel_blue`, `monster`,
`spinny_boi`, `poison_monster`. **Oracle ceiling: 0.2869 against a chance of 0.1667** —
a task with almost no recoverable identity. The cause:

```
identity            colour8 mean (r,g,b)   fraction non-zero
barrel_red          (0.03, 0.03, 0.02)     0.8%
barrel_green        (0.05, 0.07, 0.02)     1.7%
barrel_blue         (0.12, 0.12, 0.08)     2.9%
monster             (3.21, 0.14, 0.00)    95.4%
spinny_boi          (1.71, 0.95, 0.00)    91.2%
poison_monster      (2.47, 0.24, 0.00)    93.3%
```

**All three barrel textures render ~99% black in the headless path.** I checked the
obvious explanations and they are all excluded:

- **not alpha** — all six PNGs are RGBA and **100% opaque** (`a > 128` on every sampled pixel)
- **not the PNGs** — decoded independently: `barrel_red` is (0.401, 0.226, 0.225)
- **not the loader's unpacking** — `HeadlessAssets.LoadPng` reads `R/G/B` into
  `Vector3`, and the three bright textures come through correctly by the same code path

**I have not root-caused it, and I am not going to guess.** It is a headless-path
artifact affecting three specific textures, and it is a finding in its own right:
**in this game the colour channel is not reliably populated for every object type, so a
learner keyed on colour is blind to some of the world in a way that has nothing to do with
the learner.** The barrels are excluded from the balanced task and this is why.

---

## 3. The confound sweep

Train on one projection, test on another. **The test set is always balanced**, so chance
is 1/6 regardless of the training prior. All six priors, all three seeds, no max anywhere.

### A. Resolution axis (81 → 324), same projection family

| train prior | in-projection | re-projected | **collapse** | control (shuffled) |
|---|---|---|---|---|
| 0.167 | 0.5460 | 0.5067 | **+0.0393** | 0.1594 |
| 0.25 | 0.5465 | 0.5052 | +0.0413 | 0.1593 |
| 0.35 | 0.5449 | 0.4978 | +0.0471 | 0.1566 |
| 0.50 | 0.5454 | 0.5063 | +0.0391 | 0.1569 |
| 0.65 | 0.5444 | 0.5033 | +0.0411 | 0.1573 |
| 0.80 | 0.5193 | 0.4921 | +0.0272 | 0.1577 |

### B. Projection axis (`EyeEasy` off → on), same resolution

| train prior | in-projection | re-projected | **collapse** | control (colour randomised) |
|---|---|---|---|---|
| 0.167 | 0.5460 | 0.3214 | **+0.2246** | 0.0979 |
| 0.25 | 0.5465 | 0.3215 | +0.2249 | 0.1000 |
| 0.35 | 0.5449 | 0.3220 | +0.2230 | 0.0997 |
| 0.50 | 0.5454 | 0.3223 | +0.2231 | 0.0984 |
| 0.65 | 0.5444 | 0.3220 | +0.2224 | 0.0990 |
| 0.80 | 0.5193 | 0.3066 | +0.2127 | 0.1004 |

### Both controls are clean

| control | median | chance | reading |
|---|---|---|---|
| shuffled labels | 0.1575 | 0.1667 | **at chance** |
| colour randomised | 0.0994 | 0.1667 | **below chance** — confidently wrong |

> The colour-randomised control scoring *below* chance is the strong form: the learner is
> not defaulting to a constant, it is actively misclassifying. **The test can fail.**

---

## 4. The verdict

**The collapse is flat in the class prior. It is a projection effect.**

| axis | collapse at prior 0.167 | at prior 0.80 | ratio | corr(prior, collapse) |
|---|---|---|---|---|
| resolution 81→324 | +0.0393 | +0.0272 | 1.44 | −0.636 |
| **projection hard→EyeEasy** | **+0.2246** | **+0.2127** | **1.06** | −0.819 |

A frequency story predicts the collapse tracks the prior. It does not: a 4.8× change in
the training prior moves the projection collapse by 6%. **The projection effect is real
and is not an artifact of the class distribution.**

**But it is 4× smaller than the one I reported.** That is the correction:

| | `RERENDER-BUILD.md` (imbalanced) | here (balanced) |
|---|---|---|
| in-projection | 0.9860 | **0.5460** |
| resolution collapse | 0.0014 | +0.0393 |
| projection collapse | 0.9860 (confounded) | **+0.2246** |
| chance | 0.8229 (majority class) | 0.1667 (uniform) |

> **What survives: a representation learner, re-projected onto a different resolution,
> loses 0.039. Re-projected onto a different projection, it loses 0.225 — 5.7× more.
> The wide axis is the projection, not the window, which is the qualitative claim
> `RERENDER.md` wanted and which the first run could not distinguish from frequency.
>
> **What does not survive: the magnitude.** The first run's headline 0.9860 collapse was
> 82% class imbalance and 18% projection. I reported the sum as if it were the second term.

---

## 5. The TIME-QUERY pairing, which is the other half of the question

`TIME-QUERY-BUILD`'s stale-anchor test returned **`ControlFailure`** — the interface
declined rather than returning a confident wrong diff. The question here is whether the
*learner* can be fooled by a projection it was never trained on. On the same frames:

| reader | trained on | asked about an unfamiliar projection | behaviour |
|---|---|---|---|
| TIME-QUERY interface | — | stale anchor | **declines** (`ControlFailure`) |
| this learner | `EyeEasy` off | `EyeEasy` on | **answers at 0.3214** — 1.9× chance, 41% relative loss |

> **They disagree, and the disagreement is the result.** The interface recognises an
> unfamiliar condition and refuses. The learner does not: it keeps producing a confident
> answer, and the answer is wrong-but-not-random. **There is no abstention anywhere in the
> learned path, and the only reason this is visible at all is that a control arm was run.**
>
> A learner that scored 0.32 and *knew* it was guessing would be safer than this one. The
> `ControlFailure` primitive is the thing the learner lacks, and the gap between 0.32 and
> the 0.0994 colour-randomised control is the size of the confidence it should not have.

---

## 6. What is still unresolved

- **The black barrels.** Three textures render ~99% black headless, alpha and PNG both
  excluded, cause unknown. This is the highest-value thing to chase: it means the colour
  channel's coverage is not guaranteed across object types, and every colour-keyed claim
  in this account is downstream of that assumption.
- **Six identities, one shape.** All probes are the same unit quad, so shape carries
  nothing. Real objects differ in geometry as well as texture, and a real learner would
  have both. The projection collapse measured here is a *lower bound* on what a
  shape-aware learner would lose.
- **`Gamma = 0` throughout.** The game exposes a brightness control the sweep never varied.
- **The within/between n_eff result from the first run still stands** and was not
  re-measured here: across-scene sd 0.0004 on the maze task. A balanced task with varied
  *depths* and *layouts* would be needed to re-test it properly.
- **n = 1 scene for the balanced task.** The maze sweep used 3 seeds; this uses one,
  because the probe scene is constructed rather than generated. The prior sweep varies
  6 points and the conclusion is flat across all of them, but a second scene would make it
  a measurement rather than a sweep.

---

## 7. Reproduce

```
dotnet AsciiHeadless.dll --probe 1 --w 324 --h 180 --frames 24 --seed 4242 --rseed 777 \
    --nident 6 --depth 60 --spread 90 --size 14 --eyeeasy 0 --out bal_H324_hard
python3 analysis/balanced_invariance.py /workspace/rr
```

```
Headless/ProbeScene.cs              the balanced scene, in the game's own scene graph
analysis/balanced_invariance.py     the prior sweep, both controls, the verdict
analysis/balanced_invariance.json   every number above
```

Every frame: dither seed **777**, game seed **4242**, `Rasterizer.RandomSeed = 777`.
Provenance **`extracted`** — real `Rasterizer.Raster()` on a live `Scene`, in-process,
with the scene graph read out beside it. Nothing synthesised.

---

## The three sentences

1. **The collapse is flat in the class prior** (0.2246 → 0.2127 as the prior goes 0.167 →
   0.80), so it is a **projection effect, not a frequency effect** — but it is **+0.225**,
   not the 0.9860 I reported before. **The original number was ~82% class imbalance.**
2. **The control is clean in both forms** (shuffled 0.158, colour-randomised 0.099, chance
   0.167) and the in-projection arm reaches 0.546 against a 0.536 oracle ceiling, so the
   test can fail and the task is solvable.
3. **The learner answers an unfamiliar projection at 0.32 and never declines**, where the
   TIME-QUERY interface returned `ControlFailure` on the same kind of unfamiliarity. That
   disagreement is the result: the learned path has no abstention, and only the control
   arm made it visible.
