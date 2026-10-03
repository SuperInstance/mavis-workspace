# Asking for time: 30fps, 3fps, or a reference and the diffs

2026-10-02. Casey: an LLM can ask for 30 fps and get 300 pages over 10 seconds, or
3 fps and get 30 frames over 10 seconds, **or just the diffs and a reference page
with triggers based on assumptions of need.**

**The first two are a rate control. The third is the architecture.**

---

## The budget is real and it is measured in cells, not frames

Asciipocalypse's frame is `Width × Height` cells. At the default resolution that
is **81 cells**, so:

| request | 10 seconds | characters |
|---|---|---|
| 30 fps | 300 pages | ~24,300 |
| 3 fps | 30 pages | ~2,430 |
| reference + diffs + triggers | **1 + k** | ~81 + change |

**Full rate is affordable.** 24,300 characters in 10 seconds is nothing for a
text model. So the diff interface **is not about fitting the budget.**

> **It is about attention. Full rate is affordable and useless, because 300 pages
> of a mostly-static ASCII screen is 300 pages in which the answer to "what
> changed" is a visual diff the model has to perform itself, badly, over a window
> it did not choose.**

**That is the real cost, and it is the cost this project has measured six times
already: the expensive impressive thing is decoration and the load-bearing thing
is cheap.** A 3 fps sample is affordable and *still* wrong, because it can alias —
miss a whole excursion between samples. **A diff is neither cheap nor expensive.
It is correct.**

---

## The diff is an irreversible projection, and I have already measured what that costs

`Rasterizer.cs:129` gives the character channel; the projection ladder measured
what irreversibility does to recoverable value:

| projection | median |
|---|---|
| L0 lossless | 0.8831 |
| L1 colour-collapsed | 0.8947 |
| L3 coarse | 0.6839 |
| **L4 hash64** | **0.5103** |
| L5 stone count | 0.5000 |

> **A diff is L4.** It throws away the state and keeps the change. **A system that
> only ever sees diffs cannot answer "what does the screen look like now" — and
> that is not a flaw, it is the definition of an L4 observation.**

**So the design is not "diff instead of frames." It is "diff *plus* a reference",
and the reference exists precisely because the diff alone is L4.** That is
Casey's third option and it is the correct one, and the reason is a number I
measured hours before he said it.

**The testable consequence, and it is a boundary rather than a slogan:**

> **Diff+reference should be excellent at change detection and *deficient at
> absolute state*.** Not uniformly worse — **worse in one specific, predictable
> way.** Any interface that reports diffs and cannot report absolute state is
> telling you something true about itself.

---

## The triggers are the load-bearing part, and they are the fragile one

*"Triggers based on assumptions of need"* is the part that makes this an
interface rather than a compression scheme.

**A diff without a valid anchor is noise** — and the anchor is a projection, and
a projection with the wrong ordinal is a liar. This project already has both
rules:

> *Zero-copy is valuable; **zero-copy does not filter stale data**.*
> *A projector with a wrong ordinal is a liar.*

**So: if the reference frame is stale, every diff is confidently wrong.** And the
model asking for diffs cannot tell, because the diffs *look* like diffs.

> **The trigger must therefore carry its own freshness claim, and a stale
> reference has to be able to return "I don't know" rather than a clean-looking
> diff against the wrong anchor.**

**This is the abstention doctrine applied to observation instead of to answers.**
`abstain-gate` and `selectlib`'s `ControlFailure` are both about declining to
answer. **The same operation is needed here for declining to observe.**

---

## What this does to the JEV's role — and it is a reframe

The architecture so far has the JEV choosing **actions**: enumerated moves, scored,
picked. This interface implies a *different* job that may be the more important
one:

> **The fast loop's job is not primarily to choose what to DO. It is to choose
> what to LOOK AT.**

**Asciipocalypse has 81 cells and 30 frames a second. The scarce resource is not
compute — full rate fits. The scarce resource is attention, and the model asking
for time has to say what it wants watched before it knows what it needs to see.**

**So the trigger is the model's hypothesis, and the system's job is to return
evidence *against* it as readily as for it.** A JEV that only ever confirms what
was asked for is a confirmation engine with an API.

**And this is where `n_eff ≈ 2` bites again.** Every lane tonight added an LLM
pass over the same evidence. The trigger mechanism is where that would concentrate
— many lanes asking for time, all answered by one observation path. **The
observation layer is the shared correlated resource, and it will bottleneck
exactly the way the judge panel does.**

---

## The three modes, stated as contracts

| mode | returns | fails when |
|---|---|---|
| **30 fps** | 300 pages, everything | the model cannot find the change in 24,300 characters, and did not choose the window |
| **3 fps** | 30 pages, sampled | **it aliases** — an excursion entirely between samples is invisible and unrecoverable |
| **ref + diffs + triggers** | 1 anchor, k diffs, and *whether the assumption held* | **the anchor is stale, and it cannot tell** |

**The second mode's failure is the one nobody warns you about**, because sampling
feels like it is throwing information away when in fact it is throwing away a
*specific and unmeasured* class of it: anything faster than the sample rate.

> **Asciipocalypse's per-cell depth ramp is a function of `z`, and `z` changes as
> the player moves. A 3 fps sample of a fast turn is a stroboscope.** The
> information lost is not uniform — it is exactly the fastest-moving content, which
> is exactly what you sampled to find.

---

## The one sentence to build against

> **A model asking for time is making a prediction about what it will need, and
> the system's obligation is to return evidence that the prediction was wrong as
> readily as evidence that it was right.** An interface that can only confirm is a
> cache with a query language.

**And the test that decides it, which I would run first:** hold the scene still,
request diffs with a correct anchor, and get **empty diffs**. **Then move the
scene slightly and request diffs against the same anchor.** The first must be
empty and the second must not — **and an interface that returns a plausible diff
in both cases is a green badge, which is the sixth instrument tonight and I intend
to keep count.**
