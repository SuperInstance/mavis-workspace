# The game as an instrument: re-render, rewind, and test what a learner actually learned

2026-10-02. Casey: frame rate and resolution change dynamically over frames, and
**scenes can be rewound and played many times in many resolutions and renderings
to get a deeper understanding of the mechanics in the game-reality.**

**The deepest thing in that sentence is "in many renderings." Everything else
follows from it.**

---

## One scene, many projections — and the game already has the switch

The engine can render the same scene five ways: five resolutions, two frame
rates, and **two projections, one flag apart.**

```csharp
// Rasterizer.cs:124
if (EyeEasy) {
    console.Data[i,j]  = '@';                              // character channel DISCARDED
    console.Color[i,j] = ColorTo8Bit(sample * d);           // depth folded into brightness
} else {
    int fogId = min(z^10 * 10 + offset[i,j], 9);
    console.Data[i,j]  = fogString[fogId];                  // character = depth ramp
    console.Color[i,j] = ColorTo8Bit(sample);               // colour = identity
}
```

> **The same scene, the same texture, the same instant, two projections — and the
> game ships the switch behind a flag.** So the re-rendering axis is not
> hypothetical. It is two lines that already exist in a jam game nobody has looked
> at since 2020.

**And the game compiles on .NET 9 with 0 errors, 5 of 68 files touching a graphics
device, and `Console.cs` being 55 lines of pure C# with zero MonoGame references**
— so this is a data engine that can be driven headless today.

---

## The test this enables, and it is the real point

**Train on one projection. Evaluate on another. The accuracy delta is a direct
measurement of what was learned.**

| train on | test on | if the delta is large |
|---|---|---|
| 81 cells | 324 cells | **the model learned the resolution** |
| `EyeEasy` off | `EyeEasy` on | **the model learned the character ramp** |
| 30 fps | 3 fps | **the model learned the sampling, not the dynamics** |

> **A world model that survives re-projection learned the game. A world model that
> collapses under it learned the renderer.**

**This is the cheapest available falsification test for a learned model in a
projected world, and I do not believe anyone in this account has ever run it** —
including on the projection ladder, where every level was trained and tested on
the *same* split of the *same* representation, so nothing there could have
detected a representation-specific learner.

**It is the difference between "scores 0.88" and "scores 0.88 on a world that
still exists when you change the window."**

---

## Rewind is what makes it an experiment instead of a demo

**Without rewind, five renderings give you five samples. With rewind, they give
you five measurements of the same instant.**

**The scene graph is the ground truth and the renderer is the variable.** Hold the
scene, vary the projection, and the only thing changing is what the observer can
see. **That is a controlled experiment, and it requires nothing more exotic than
being able to re-run a frame — which brings the prerequisite:**

> **The game is not deterministic. `Rasterizer.cs:26` is `new Random()` — unseeded —
> and it draws a fixed per-cell dither pattern once per process.** So two runs of
> "the same" frame produce different character buffers.

**So rewind does not work until the seed is fixed.** That is a one-line change
(`new Random(seed)`, seed exposed), and it is the same requirement as the
Connect-4 ground-truth pattern: **a digest and a seed are what turn a demo into a
measurement.** Nothing in the rewind idea is available until it lands.

---

## "Reworking the data for the next game" — the engine is the general part

If the same renderer can produce training data for a different game, then the
**renderer is the general-purpose layer and the game is the specific one.** That is
the split Casey has been theorising about, found in a stranger's jam game:

- **general** — scene → triangles → z-buffer → character/colour buffer
- **specific** — which meshes, which rules, what "winning" means

**And the specific layer is cheap to replace because the general layer emits
text.** 81 cells of `char` + 8-bit colour is a training sample, and a *labelled*
one, because the scene graph that produced it is right there in the same process.

> **Nothing else in this account can generate ground-truth-labelled data. The
> projection ladder needed hand-labelling. The JEV experiments needed a real
> decision. This emits the truth and the projection of it together, every frame,
> by construction — and the projection is the thing the whole project is about.**

---

## What I am suspicious of, in advance

**More renderings is not more evidence if the renderings are correlated.** Five
resolutions of one scene are five views of one instant. **That is `n_eff ≈ 2`
wearing a lab coat** — a re-rendering axis that looks like breadth and is actually
depth. **The measurement to report is the variance across projections of the SAME
scene, compared against the variance across scenes.** If the first is much
smaller, the re-rendering axis bought less than it looks like it did, and the
number should say so.

**And the tempting mistake: reporting the best rendering.** Five projections, pick
the one with the best score, publish that. **That is exactly the max-over-four-
learners artifact that killed the original projection ladder at n_eff 1.48.**
**Report all five. Median and spread, never the best.**

---

## The one sentence to build against

> **The same scene, re-rendered, is the only experiment available that can
> distinguish a model that learned the game from a model that learned the
> renderer — and distinguishing those is the difference between a world model and
> a very good texture recogniser.**

📄 Written before the lane builds, so the acceptance test is on the record.
