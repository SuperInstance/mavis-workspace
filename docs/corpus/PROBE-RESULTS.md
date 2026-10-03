# Reprojection probe: a runnable instrument and three corrections

2026-10-02. `probe/reproject_probe.py`, `probe/run_probe.py`, `probe/perturb.py`,
`probe/depthmatch.py`. **The instrument can fail, which took two rebuilds to
achieve, and both rebuilds are recorded below because both were my error.**

---

## The result

**Six objects. All at the same depth. Six distinct identities.**

```
 gid  n   distinct CHARS   distinct COLOURS
   0   4       2                 1
   1   4       2                 1
   2   4       2                 1
   3   4       2                 1
   4   4       1                 1
   5   4       1                 1

identity pairs sharing at least one character : 14/15
character channel distinguishes identities     : 1/15 pairs
glyph histogram across the scene: {'&': 13, '#': 11}
```

> **Twenty-four cells. Six objects. Two characters.** The character channel
> collapses six identities into two symbols, and **14 of 15 identity pairs are
> indistinguishable to it.**

**This needs no learner and no statistics. It is a property of the projection,
measured.** `console.Data[i,j] = fogString[min(z^10 * 10 + offset[i,j], 9)]` has
no term that can distinguish two things at the same depth, and the measurement
confirms the code.

**Meanwhile the colour arm is stable across re-projections:**

| | score |
|---|---|
| colour, in-sample, EyeEasy OFF 24×9 | **0.638** |
| colour, same scene, EyeEasy **ON** | **0.552** |
| colour, same scene, 36×13 | **0.639** |

**Re-resolution costs 0.001. Re-projection costs 0.086.** A learner keyed on colour
survives changing the window; a learner keyed on characters has nothing to
transfer.

---

## CORRECTION 1 — the first version could not fail

First run, the controls scored **0.060 / 0.088 / 0.069** against real arms at
**0.088 / 0.093**. **The controls matched the real arms. The instrument was
worthless and I nearly reported the numbers.**

Two causes, both mine:
- **the scene never reached the informative band** — every object sat below
  `z = 0.79`, so every cell was `@` and there was nothing to learn
- **1-NN over exact row matches is not a learner**, it is a lookup table

**Rebuilt with a scene spanning `z ∈ [0.795, 0.956]` — inside the band where
`fogId` actually varies — and a majority-vote cell learner.** Controls then
scored **0.000 / 0.103 / 0.466** against real arms at **0.638 / 0.639**, which
is a real gap.

**That is the seventh green badge of the night and I built it myself with my own
hands, which is the strongest possible argument for making the control a
mandatory field rather than a habit.**

## CORRECTION 2 — my ground truth was confounded with the projection

The character arm scored **0.621** when I predicted ~0. The reason:

```python
for _ in range(10):  tris.append(quad(rnd.uniform(0.05,0.70), ..., gid)); gid += 1
for k in range(8):   tris.append(quad_at(0.795+k*0.023, ..., gid)); gid += 1
```

**I assigned `gid` in depth order, so identity was a function of depth — and depth
is exactly what the character encodes.** The label leaked the answer.

> **The ground truth was not independent of the projection being tested. That is
> the same class of error as comparing an absolute quantity to a ratio without
> normalising: a measurement that inherits structure from the thing it measures.**

Fixed by shuffling the `gid ↔ quad` assignment with a second RNG, so identity
carries no depth signal.

## WHAT THE CONFOUND REVEALED — the real finding underneath

**After decorrelating, the character arm STILL scored 0.621.** That is not a bug
in the fix; it is the most interesting result in the round:

> **The dither `offset[i,j]` is drawn once per cell and never redrawn, so it is a
> stable per-cell FINGERPRINT. In a static scene the character channel is a weak
> hash of screen position — and position alone is enough to memorise a frame.**

Confirmed directly: of 6 distinct characters among labelled cells, **4 map to
exactly one identity each.**

**So character-based learning does not learn what things are. It learns where
they are — and on a static scene, where-they-are is sufficient to score well.**

> **This is the strongest argument yet for the rewind test. A character-reading
> agent can look excellent on a still frame and be worthless the instant anything
> moves, and no static benchmark can tell the difference.** The perturbation run
> shows the mechanism: nudging 3 of 18 quads changed only **4 of 216 character
> cells**, and the character arm's score barely moved — because it was reading a
> position hash, not an object.

**Colour does not have this failure mode**, because colour carries identity
rather than position, and 0.638 held to 0.639 across a resolution change.

---

## What this establishes, and what it does not

**Establishes:**
- the character channel carries **depth and no identity**, measured without a
  learner
- the dither makes it a **stable positional hash**, so static-scene character
  accuracy is memorisation
- colour carries identity and **survives re-projection and re-resolution**

**Does NOT establish:** anything about the real game. **This is a faithful
reimplementation of `Rasterizer.cs:129` over a synthetic scene, not frames from
the running game.** Run against the real rasterizer before any of it is claimed
about Asciipocalypse — the port in `ASCIIPORT.md` makes that possible and it is
the next step.

**And the unrun control:** a scene where two objects share a depth *and* a colour
but differ in geometry. The character channel would also collapse those, and
**whether the true renderer does is unknown** because I have not run it.

📄 Runnable, in `probe/`. `python3 probe/depthmatch.py` reproduces the headline in
under a second with no dependencies and no network.
