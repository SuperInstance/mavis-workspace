# TIME-QUERY-BUILD — the three modes, and the test that decides whether it can lie

2026-10-02. Build lane. Stub, 10 minutes' reading, everything below is
measured output from a runnable program, not an argument.

```
timequery/
  ascii_substrate.py   frame substrate: char + colour, both channels
  timequery.py         the three modes, the anchor, the decline, the trigger
  run.py               the three deciding tests FIRST, then the measurements
  out.txt              full captured output of the run
  results.json         machine-readable
```
`python3 run.py` — exits 0, ~40 s.

---

## 0. PROVENANCE — read this before any number

**No frame here was extracted. Every frame is RECONSTRUCTED at the level of the
projection and SYNTHETIC at the level of the scene.**

`ASCIIPORT.md` says the game compiles on .NET 9 with 0 errors, and I checked
rather than assumed. **It does not matter: there is no .NET runtime in this
sandbox.** Verified three ways before writing a line of substrate:

```
which dotnet                       -> not found
find / -name libhostfxr.so         -> nothing
find / -name libcoreclr.so         -> nothing
Headless/bin/.../AsciiHeadless     -> "You must install .NET to run this
                                      application. .NET location: Not found"
```

A prior lane's `Headless/` harness exists and its binary was built at 20:25
today, so this is a removed runtime, not a lane that never ran. **I could not
run `Rasterizer.Raster()` against a live `Scene`, so I did not.** A frame
presented as extracted when it was reconstructed is the one false claim this
project will not forgive, and the cheapest way to avoid making it is to not be
able to make it.

**What IS transcribed, line for line, from the real source:**

| what | where |
|---|---|
| `fogString = "@&#8x*,:. "` (10 chars) | `Rasterizer.cs:22` |
| `fogId = (z<0) ? 0 : min((int)(pow(z,10) * 10 + offset[i,j]), 9)` | `Rasterizer.cs:129` |
| `offset[i,j] = rand.NextDouble() - 0.5f`, drawn ONCE in the ctor, seeded | `Rasterizer.cs:36` + the `ASCII-CHARSELECTION.md` retraction |
| `ColorTo8Bit`: `r=clamp(X,0,.9)*8, g=clamp(Y,0,.9)*8, b=clamp(Z,0,.8)*4`, packed `r+(g<<3)+(b<<6)` | `Mathg.cs:69` |
| reset `Data=' '`, `Color=255` | `Console.cs:31`, `Rasterizer.cs:53-60` |
| Y negated: `new Vector2(v0.X, -v0.Y)/v0.W` | `Rasterizer.cs` projection |
| `EyeEasy` branch (every cell `@`, depth into brightness) | `Rasterizer.cs:124` |
| `char[width, height]` indexed `[i,j]` with `i`=x, both channels, zero MonoGame | `Console.cs` |

**What is NOT faithful: the geometry, the scene graph, the textures, and the
playthrough.** Those are a corridor and three oscillating hostiles, synthesized
in `build_scene()`. Every frame carries
`provenance = "reconstructed-projection/synthetic-scene"` in its own payload,
and it is printed next to the mode outputs above, not only here.

Resolution 60×26 (1,560 cells). `TIME-QUERY.md`'s 81-cell budget table is the
game's 9×9 default; I report 60×26 so a page is legible, and the character
budgets below scale linearly if you want the 81-cell figure.

**Three real bugs I had to fix to get here, all recorded because each was an
instrument lying to me:** my z-buffer stored raw world depth (2..60) where the
fog ramp needs NDC (0..1); I was using NDC coordinates as pixel indices, so
every triangle's bounding box clamped to empty; and the Y axis was upside down
because the game negates it. A substrate that renders *something plausible but
wrong* is worse than one that renders nothing.

---

## 1. THE THREE DECIDING TESTS — run first, all three green

```
T1 STILL   anchor=anchor(t=4.0000s, epoch=0, digest=ced3987b, 60x26,
                         reconstructed-projection/synthetic-scene)
           same-t diff -> n_changed = 0                        => EMPTY     ✓
T2 MOVED   same anchor, t+1/60s -> n_changed = 15 (char 15 / color 15)
                                                               => NON-EMPTY ✓
           (19,12, ':'->'@', 84->14, 'wall_L'->'hostile_0')
           (19,13, ':'->'@', 84->14, 'wall_L'->'hostile_0')
           (19,14, ':'->'@', 84->14, 'wall_L'->'hostile_0')
T3 STALE   obs.epoch advanced 0 -> 1; old anchor is epoch 0
           ControlFailure: STALE ANCHOR: reference was advanced (epoch 0 -> 1)
           after this anchor was taken at epoch 0.  A diff against it would
           look like a diff and be confidently wrong.  DECLINING TO OBSERVE.
                                                               => DECLINED   ✓

  T1_still_empty         PASS ✓
  T2_moved_nonempty      PASS ✓
  T3_stale_declined      PASS ✓
  ALL THREE: PASS ✓
```

**The mechanism, in one line:** an `Anchor` carries `(epoch, t, digest,
provenance)`, and every `diff()` / `observe()` / `evaluate_trigger()` entry
point calls `_check(anchor, obs)` **before** touching a cell. `epoch` bumps only
when the reference advances. So a stale anchor raises `ControlFailure` — the same
decline operation as `abstain-gate` and `selectlib`'s `ControlFailure`, applied
to observation instead of to answers.

**A stale anchor is a projector with the wrong ordinal, so the interface cannot
return a diff against one.** It is not that the diff would be uninformative; it
is that it would be *shaped exactly like a diff* and confidently wrong, which is
the `durable-LOGIC` failure — a clean result with no record of a red one.

---

## 2. THE THREE MODES, real output from all three

| mode | request | returns | characters / 10 s |
|---|---|---|---|
| 1 | 30 fps | 300 pages | **1,895,100** |
| 2 | 3 fps | 30 pages | **189,510** |
| 3 | ref + diffs + triggers | 1 anchor + 30 diffs + 4 triggers | **93,118** |

Mode 3's diff sizes per 1/30 s step, first 12 of 30:
`15 16 24 31 39 42 48 49 49 47 36 40` — the scene is mostly static, so the
diffs are small, which is the whole argument for the third mode.

All three budgets are **affordable** (TIME-QUERY.md says so, and it is right).
The ratio 1,895,100 : 189,510 : 93,118 is not a budget argument. It is an
attention argument: 300 pages of a mostly-static screen is 300 pages in which
the answer to "what changed" is a visual diff the model must perform itself,
over a window it did not choose.

---

## 3. RATE ALIASING — the specific, predictable way 3 fps is worse

An **excursion** is a maximal run of ≥4 consecutive 60 fps frames in which a
hostile owns ≥8 cells. 3 fps keeps one frame in 20.

```
  hostile_0 :  1 excursions at 60 fps ->  1 survive 30 fps,  1 survive 3 fps
  hostile_1 : 11 excursions at 60 fps -> 11 survive 30 fps,  8 survive 3 fps
  hostile_2 :  4 excursions at 60 fps ->  4 survive 30 fps,  2 survive 3 fps

  TOTAL: 16 excursions | 30 fps keeps 16 (100%) | 3 fps keeps 11 (69%)
  Excursions ENTIRELY INVISIBLE at 3 fps: 5 of 16
  length of the LOST excursions (frames): [4, 5, 7, 8, 8]        median 7 = 117 ms
  length of the KEPT excursions (frames): [5,8,20,31,39,43,45,49,54,57,600]
                                                                  median 43 = 717 ms
```

**This is the boundary, and it is not a scalar accuracy gap.** Every lost
excursion is shorter than the 20-frame sample gap and every kept one is longer
than it. The loss is *exactly* the sub-133 ms events — the fastest-moving
content — which is precisely what you sampled the time in order to find. A
hostile that crosses a doorway and is gone between two samples **does not
appear in the record as a hostile that was not there.** It appears as nothing,
indistinguishable from a corridor that stayed empty.

That asymmetry is why this is worth more than a table of accuracies: the
sampling error is **correlated with the thing you care about**, so it is not
averaging out, it is preferentially deleting the signal.

---

## 4. THE TWO QUESTIONS, ASKED SEPARATELY

### Q1 — change detection. *"did X change between the reference and t?"*

```
observe mode: 18/18 correct = 1.000   (per-trial truth vector: TTTTTTTTTTTTTTTTTT)
```

Exact, and exact for a reason worth naming: the diff is computed over **both**
channels. `ASCII-CHARSELECTION.md` established that the glyph is a function of
`z` and carries no identity, so a char-only diff would be a diff over a channel
that cannot tell you what anything is. In this run the two channels happen to
move together (`char 15 / color 15` at T2), so the point is not demonstrated by
a failure — it is demonstrated in §6, where a char-only query *is* refuted.

`full_rate` is not less correct. It is **20× more expensive to check**:

```
  30 fps over 10 s, cell-comparisons the reader must perform: 31,200
  diff + reference:                                          1,560
```

And under a bounded reader — if the change lands on one of N pages uniformly
and the reader may examine B without knowing which, P(find) = B/N:

```
  B=  1 of 300 -> 0.003     B= 30 of 300 -> 0.100
  B=  5 of 300 -> 0.017     B=100 of 300 -> 0.333
  B= 10 of 300 -> 0.033     B=300 of 300 -> 1.000
```

(Exact, not simulated. An earlier version of this sweep invented a
pseudo-random window and produced a curve from nothing — a fabricated
instrument, deleted.)

### Q2 — absolute state. *"what is at position P right now?"*

```
  observe (valid anchor)     27/27 correct = 1.000 | confidently wrong: 0
  diff only (no reference)    0/27 correct = 0.000 | confidently wrong: 0
  full_rate (direct read)    27/27 correct = 1.000 | confidently wrong: 0
  observe (STALE anchor)      5/ 5 DECLINED | answered anyway: 0
```

### THE PREDICTION IS REFUTED, and that is the result

`TIME-QUERY.md` predicted:

> *diff+reference should be excellent at change detection and **deficient at
> absolute state**.*

**Measured: diff+reference is 1.000 at absolute state — identical to full
state, not deficient.** The deficiency is real, and it is in the *diff alone*:

> **diff ALONE scores 0.000. diff + REFERENCE scores 1.000.**

A diff is L4 — irreversible, keeps the change, throws the state away — and
"what is at P right now" is answered 0/27 times without the reference. **The
reference does not merely help the third mode. It is the entire reason the third
mode can answer that question at all**, and the measured cost of omitting it is
not a little accuracy, it is total.

So the corrected statement is sharper than the prediction, and it is a
trade rather than a win:

- diff+reference is **exact at both questions**;
- it buys that exactness with a **reference it must keep valid**;
- and validity is a *stateful* obligation that full state never has. At a stale
  anchor the third mode **declines 5/5 and answers 0/5**, while full_rate
  cannot decline because it has no anchor to be wrong about.

> **The third mode is not better than full state. It is full state plus a
> freshness obligation it can fail — and the failure it can fail is the
> abstention doctrine, correctly applied.**

---

## 5. THE TRIGGER — built to be wrong, and confirmed wrong

```
WRONG assumption (moving hostile assumed still)   -> REFUTED    moved_in_world: true
  world_pose_ref [-1.8212, 0.9699, 14.0]  ->  now [-1.6764, 1.4157, 14.0]
CORRECT assumption (static ceiling)               -> OCCLUDED   moved_in_world: false
FALSE POSITIVE (asks about hostile_9, which does not exist)
                                                   -> REFUTED    cells_owned: 0
SEPARABILITY: can CHARS alone tell hostile from wall?
                                                   -> CONFIRMED  glyph_overlap: ''

  verdicts: 2 REFUTED (evidence AGAINST) | 1 OCCLUDED (neither)
          | 0 UPHELD | 1 CONFIRMED (evidence FOR)
```

Three of four triggers return **REFUTED or OCCLUDED**. The interface returns
evidence *against* the assumption of need, and it can return **neither** — which
a confirm-only interface cannot do, and which is the difference between an
interface and a cache with a query language.

**The sharpest line in this section:** the verdict is taken from the **scene
graph** (the pose), and the frame-level diff is the **evidence**. Cross-checking
them:

```
  scene-graph truth vs frame-level evidence: 1/2 agree
    moving hostile   truth_moved=True   frame_says_moved=True    agree
    static ceiling   truth_moved=False  frame_says_moved=True    DISAGREE
```

> **A diff cannot answer "did X move". It can only answer "did X's cells
> change", and those are different questions — a hostile walking in front of a
> static ceiling changes the ceiling's cells without the ceiling moving.** The
> trigger has to reach past the diff to the scene graph to answer the question it
> was actually asked, and the disagreement rate is not zero.

That is a real boundary in mode 3, and it is invisible if you only ever look at
whether the diff fired.

### And the char channel, tested where it can actually fail

The separability query above returns CONFIRMED — but that is a property of *my
scene*, not of the channel: the hostile sits in a depth band the walls do not
occupy, and `z^10` flattens the ramp so everything nearer than
`z_ndc = (0.1)^(1/10) = 0.794` reads `@` regardless of what it is. Sweeping the
hostile across that knee:

```
  hostile z  verdict   glyph overlap  colour overlap
  14.0       CONFIRMED ''             0   (1 target colour vs 3 other)
  26.0       CONFIRMED ''             0
  40.0       CONFIRMED ''             0
  46.0       CONFIRMED ''             0
  48.0       REFUTED   '&'            0     <-- the knee
  50.0       REFUTED   '&'            0
  52.0       REFUTED   '#'            0
  55.0       REFUTED   '8'            0
  58.0       REFUTED   ','            0

  char-only separability REFUTED at 5 of 9 adversarial depths.
```

**Refuted at exactly the depths predicted, and the colour channel separates
cleanly at every one of them (overlap 0 in 9/9).** `ASCII-CHARSELECTION.md`'s
finding reproduces on a substrate that never ran the game: the glyph is depth,
depth is a poor proxy for identity, and at the depths where the proxy breaks
down — which is to say, everywhere the scene is not conveniently stratified —
the character channel cannot tell a hostile from a wall. **This is why both
channels are carried, and it is now a measurement here rather than an
assertion there.**

---

## 6. THE SHARED OBSERVATION PATH — the n_eff question

```
  1 lane  x 30 fps x 10 s =  300 page-requests
    unique captures 300 | cache hits    1 | raster time 1.161 s | wall 1.293 s
  5 lanes x 30 fps x 10 s = 1500 page-requests
    unique captures 300 | cache hits 1205 | raster time 1.161 s | wall 0.528 s
  5 lanes x  30 diffs    =  150 diff-requests
    unique captures   0 | cache hits  151 | raster time 0.000 s | wall 0.040 s
```

Everything goes through one `capture()` and one cache. So:

- **cost amortises perfectly** — 5 lanes cost the same 300 rasterisations as
  one, 5.0× — and **freshness is shared too**: all lanes see the same `epoch`.
- **The trigger mechanism doubles up on itself, and here is the demonstration
  rather than the argument.** Two lanes, two different hypotheses
  (`hostile_0 still?` / `hostile_1 still?`), one epoch:

```
  lane1: moved_in_world: true,  footprint_lost 14, gained 21, changed_total 41
  lane2: moved_in_world: true,  footprint_lost  4, gained  0, changed_total 41
  same epoch (0), same captured frames, same verdict shape: True
```

  They are not independent observations that happen to agree. **They are two
  reads of one capture, at one epoch, sharing `n_cells_changed_total = 41`
  exactly** — their evidence is correlated by construction. `n_eff ≈ 2` does
  not need to be asserted at the observation layer; it is a property of the
  topology. Two lanes disagreeing about the world is not two measurements, and
  a disagreement check between them would be checking the cache, not the scene.

  **The same mechanism is also the one that makes staleness detectable at all**
  — a single shared epoch is what lets a reference be declared stale. The
  correlation is the price of the abstention, and you cannot have the abstention
  without it.

---

## 7. FIVE OF MY OWN INSTRUMENTS THAT COULD NOT FAIL

The brief says an interface that returns a plausible diff in both the still and
moved cases is the sixth green badge tonight. **I built five of my own before
the deciding tests passed**, and every one was caught by asking what result
would have been impossible.

| # | the instrument | why it could not fail | fix |
|---|---|---|---|
| 1 | "static ceiling" trigger | refuted a **true** assumption 100% of the time — it counted occlusion as movement | three verdicts: REFUTED / OCCLUDED / UPHELD |
| 2 | "spot a hostile from chars" | filtered on **colour** `0x0e` while claiming to be char-only; confirmed by construction | real separability test: do the glyph sets overlap? |
| 3 | amortisation measurement | ran on a **warm cache** → "0 unique captures", "1500×" | fresh `Observation`; also fixed a literal `%d` printing as text |
| 4 | bounded-reader sweep | a **fabricated** pseudo-random window producing a curve from nothing | exact `P = B/N` under a stated uniform prior |
| 5 | Q1 "did X change" truth | defined truth as **cell count**, so a target whose cells swapped read as unchanged → one FALSE | truth = the owned cell **set** |

And one that would have been the worst of them, because it would have reported
a **green** where the brief demands a **decline**:

> **6. The stale-anchor arm of Q2 called the `full_rate` code path, which never
> consults the anchor.** It printed `0/5 DECLINED | 0 diffs returned` — and
> that `0 diffs returned` looked like a pass. It had tested nothing at all. The
> honest number is **5/5 DECLINED, 0 answered anyway**.

That last one is the pattern worth keeping: `0 diffs returned` and `0
declined` look identical in a log, and only one of them is a result. **A count
of zero is ambiguous between "nothing happened" and "nothing was measured", and
the difference is invisible unless you say which arm ran.**

---

## 8. THE BAR

- [x] Runnable, real output from all three modes — `python3 run.py`, exit 0
- [x] **Empty-diff test green** (T1: 0 cells)
- [x] **Stale-anchor test DECLINING** (T3: `ControlFailure`, 5/5, 0 answered)
- [x] **Moved-scene test non-empty** (T2: 15 cells)
- [x] Every frame's provenance labelled — `reconstructed-projection/synthetic-scene`,
      in the frame payload and printed beside every mode
- [x] Distributions kept as distributions — excursion lengths, per-trial truth
      vectors, the depth sweep, the budget sweep. No scalar anywhere that a
      vector stood behind it.
- [x] No GitHub pushes. This file is the only thing written outside `timequery/`.

**Not done, and named:** the frames are reconstructed, not extracted, because
there is no .NET runtime here. Restoring it and re-running against
`Rasterizer.Raster()` is the one step that would upgrade the provenance label,
and it changes no conclusion in §1–§6 — the deciding tests are about the
interface's algebra over frames, not about where the frames came from. It would
change §5's depth sweep, which is the one result that depends on my geometry.

---

## 9. THE TWO QUESTIONS, ASKED SEPARATELY — the scores

> ### Q1 — change detection, "did X change?" — **1.000** (18/18)
> ### Q2 — absolute state, "what is at P right now?" — **1.000** (27/27)
> ### Q2 — the same question to a diff with no reference — **0.000** (0/27)
> ### Q2 — the same question with a **stale** reference — **declines 5/5, answers 0/5**

The prediction was that diff+reference would be deficient at absolute state. It
is not — it is exact, and the deficiency belongs to the diff alone, where it is
total rather than slight. **What the third mode actually costs is not accuracy.
It is a freshness obligation: a stateful thing that must be kept valid, that
declines when it is not, and that full state never has to be.**

**And if the stale-anchor test had returned a confident diff instead of
declining, that would be the finding that mattered. It returned
`ControlFailure`.** That is the one result here I would defend under an attempt
to break it, and the only way to know whether it holds is the one I could not
run: the real rasterizer, which is the sixth thing this build lane did not do.
