# Experiments run, and what they settled

Runnable: `probe/`. All reproduce in under a second, no network.

## 1. Does the character channel carry identity? — **NO**

Six objects, **identical depth**, six distinct identities:

```
CURRENT  depth ramp @&#8x*,:.       1/6 glyphs   15/15 pairs collide   0/6 identifiable
ARM A    neutral ramp, by depth     1/6          15/15                0/6
ARM B    role palette, by role      6/6           0/15                6/6
CONTROL  non-injective (must fail)  2/6           6/15                0/6
```

**`console.Data[i,j] = fogString[min(z^10*10 + offset[i,j], 9)]` has no term that
can see identity.** ARM A is the important row: a semantically-neutral alphabet
**does not help at all**, because the problem is not which characters you pick.

## 2. Is the renderer therefore broken? — **NO. It is correct.**

```
CURRENT (EyeEasy OFF)          depth-from-char=YES  identity-from-colour=YES  JOINT=EXACT
EyeEasy ON (char='@', x d)     depth-from-char=NO   identity-from-colour=YES  JOINT=EXACT
```

**Depth from the character, identity from the colour, both exactly recoverable
from the frame together.**

> The retraction that matters: **I graded one channel on the job of two.** "14 of
> 15 identity pairs collapse" is a true statement about a *field*, and I promoted
> it to a verdict about *the system*. **Decide what the observation is before you
> conclude anything was lost.**

## 3. Is that reimplementation faithful? — **YES, verified on the real C#**

```
REAL C# glyph occupancy: @=79.7%  &=5.5% #=3.5% 8=2.6% x=2.1% ...
my Python predicted:    @=79.13%
real offset[0,0] = -0.278256   (one draw per cell, never redrawn)
real Sample() headless: (0.25,0.5,0.75)   <- no GraphicsDevice, no Texture2D, no .xnb
```

**`Sample()` is a pure array read.** Build the `AsciiTexture` with
`GetUninitializedObject` and inject its private `colors` by reflection — that
removes the last blocker to running the actual game.

## 4. Measured numbers worth keeping

| | |
|---|---|
| Connect-4 ground truth | 54,166 positions, plies 1–6, digest `0x4ef8351a5c319637` |
| 4×4 four-in-a-row (Gale's) | **9,067,975 positions**, digest `0x32d6d9539cffc85a` ✓ recomputed |
| 4×4 value distribution | **−1: 3.38% · 0: 66.51% · +1: 30.11%** — the draw, independently |
| projection ladder | 0.8831 / 0.8947 / 0.6839 / **0.5103** / 0.5000 |
| FNV-1a 64 canary | `0x24a555471370b18d` (NFC, UTF-8 **bytes**; 3 encoding traps) |
| fleet | 5,127 repos · resolver 477 / 85,990 files · 4,789 `FILE_MISSING` |

## 5. What is still a claim, and must not be upgraded to a result

- **The colour half of every ASCII result.** Nothing has run `Raster(Scene)`, and
  no real PNG has been sampled — the texture array is still a constant.
- **ASCIIEval's 12.32% drop, the 14/15 collapse, the VLA palette** — read one
  paper in full; the rest are abstracts. **Verify before citing.**
- **The 8h49m "convergence".** A prediction that changes behaviour is not a
  prediction being tested. Their own synthesis amends it better.
