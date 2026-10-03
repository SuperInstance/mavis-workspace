# quilt-jev-WEB — the builder lane, browser-native

**Status: built and run.** `quilt-jev-web/` under this directory. 25/25 executable
invariants pass, a real Chromium renders it, zero console errors.
`node serve.mjs` → <http://127.0.0.1:8171/>.

---

## 0. The thing you have to know first

**`SuperInstance/achimala/jev-paint` does not exist in this sandbox.** I searched
the NAS for `renderer.mjs`, `paint-worker.mjs`, `jev.mjs`, `art.mjs`, and for
`achimala` and `jev-paint` as directories. Nothing. The four files you named are
not on this machine, so I could not read a line of the thing you called the
highest-craft code in this account, and I could not fork it.

What *is* here is the author's other repo, `SuperInstance/jev-quilt` (810 blobs,
Python). It has `cell.py`, `q16.py`, `fold.py`, `typesafe_client.py`,
`engine.py` — but **no renderer, no entropy, no relief, no margin.** I grepped
the whole tree: the only "margin" hits are `sheet.margin` in a demo domain
string. So relief-by-entropy is not in the code I can read either; I took your
description of it as the spec and built the projection you asked for.

**What is vendored vs what is mine, stated plainly:**

| file | status |
|---|---|
| `src/tensor.mjs` | **derived from** `jev_quilt/cell.py` + `q16.py` (Law 1 integer identity, Law 5 viability, "floats are display projections only"). The distribution-holding cell is mine — the source's `Cell` holds a *decision payload*. |
| `src/jev.mjs` | **derived from** `jev_quilt/typesafe_client.py`, wire shape cross-checked against `JEV-CONTRACT.md`. The four-way failure taxonomy is mine. |
| `src/render.mjs` | **entirely mine.** Nothing to fork. |
| `src/raster.mjs` | mine. |
| `src/app.mjs`, `index.html` | mine. |
| `src/synth.mjs` | mine. |

A from-scratch renderer that is worse would be a regression wearing a rewrite's
clothes. I cannot prove mine is better than the one I never saw. I can prove it
reads the field, which the negative control below establishes, and I can tell
you exactly which decisions I made so you can compare them yourself.

---

## 1. The four invariants, and they are executable

`node verify.mjs` — **25/25 PASS**. Same file the browser imports, so there is
one implementation of each invariant, not two.

```
PASS  I2 tensor round-trips byte for byte   (77591 == 77591)
PASS  I1/I2 invariants pass on the fixture
PASS  same tensor renders to IDENTICAL pixels twice   (930d230b == 930d230b)
PASS  a SHUFFLED tensor renders VISIBLY differently   (930d230b != e0e6f201)
PASS  changing the projection changes the pixels      (930d230b != e2485963)
PASS  changing the grid size (a fold) changes the image(930d230b != b49a7814)
PASS  a fold is a NEW TENSOR ADDRESS, and says so     (2504bb9d -> 1b5cc073)
PASS  I3 all four projections read ONE tensor (one sha, four views)
PASS  VOID cells are counted separately from zeros    (void=3)
PASS  the surface has cells of every state            (contested=15 overclaim=5 void=3)
PASS  a 6x4/4x2/1x1 fold CONCATENATES history         (99 -> 99)
PASS  a fold MERGES rank, so one patch can be a 3-deep stack (max rank 14)
PASS  the fold does not lose contested cells; it MOVES them  (17 == 17)
PASS  a tensor of UNIFORM ZEROS does not look like the fixture
PASS  transport and schema failure are four distinct typed values
```

**1. No cell ever stores a scalar alone.** `cell()` throws on a map with <2
labels, on a missing `confidence`, on a distribution that does not sum to 1. The
invariant checker goes further: it *recomputes* entropy, margin, p(argmax) and
argmax from the stored map and fails if they disagree by more than 1e-9. A cell
holding four scalars that look like they came from a map is caught.

**2. The tensor round-trips byte for byte.** `serialize()` sorts keys and pins
every float to 9dp, so `grid → file → grid` is identity at the byte level, not
the "approximately equal" level. 77 591 bytes, stable.

**3. Every rendering is labelled by which projection it is.** Four projections,
one tensor address, printed in the header of every screenshot:

```
quilt.stitch   px e049a756  relief:margin  grain:entropy  history:YES
entropy.relief px e20b7da7  relief:entropy grain:none     history:no
margin.relief  px 11e44c82  relief:margin  grain:none     history:no
choice.flat    px 4eac7acb  relief:none    grain:none     history:no
```

**4. Grid size is a dial.** `fold()` requires an exact divisor (a fold that
could interpolate would be a new artifact wearing a fold's name). Every fold
carries `meta.foldedFrom = {12×8, 2504bb9d}` — the *source* tensor's address
travels with the fold, so the header reads `1×1 ← fold of 12×8@2504bb9d` and you
can always see whose field you are looking at.

---

## 2. Negative control, first, as demanded

```
same tensor, rendered twice      930d230b == 930d230b
shuffled tensor                   930d230b != e0e6f201
projection changed                930d230b != e2485963
fold changed                      930d230b != b49a7814
```

The hash is over **pixels**, not over the op list. Hashing ops would only prove
the instruction stream changed; hashing pixels proves something was painted.

---

## 3. Entropy drives the surface — I argue myself out of it, mostly

I kept it. It is a projection, it is the default relief of `entropy.relief`, and
it is in the tool. But it is **not** the geometry, and that is the disagreement.

Relief-by-entropy makes entropy a *summary* of the map, so the moment you draw
the cell you have thrown the map away. Then the one case you most need to see —
**a judge that is confident and wrong** — renders as *maximum relief*: a
tall, dramatic, high-contrast cell. Relief is the visual language for "this is
interesting and resolved", and high entropy is precisely the state where
nothing is resolved. The dial says the opposite of the truth.

So the division of labour is:

- **geometry = the whole probability map.** Always, every projection, never
  summarised. Band widths are the probabilities.
- **relief = margin.** `top1 − top2` is the only quantity that means "decided",
  so it is the only one allowed to make a cell loud.
- **grain = entropy.** A stipple, never a geometry. A contested cell gets
  *textured*; the bar underneath is untouched and still fully readable.
- **seam = the state entropy and margin disagree about.** Below.

**One thing I had to be talked out of by measurement.** I first made relief a
drop shadow. `margin.relief` and `entropy.relief` came out within a few pixels
of each other — at 20px cells a 1px shadow is invisible. Relief is now
**structural**: the dial sets the *bar's thickness*. Same width, same bands, same
complete map; only the height moves. Now the two views are unmistakably
different surfaces — compare the shots below, same tensor `2504bb9d`: in
`entropy.relief` the flat cells are thick; in `quilt.stitch` the flat cells are
thin and the peaked ones are thick. Neither loses the map.

**The alarm-colour discipline.** My first palette gave red to the most common
label. That is fatal to the whole design: if red is the background, the red seam
that means "contested" stops meaning anything. The label palette is now muted and
tonally close, and the alarm red is in **no** label palette. Red on this surface
can only mean danger.

---

## 4. `history` is where it becomes a quilt, and this is where I beat it

A cell judged three times is drawn as a **three-layer patch**, one sub-row per
judgment, most recent on top, each sub-row carrying that judgment's own complete
banded map. Layered on top is **the stitch**: a thread through the patch whose
kinks *are* the disagreement, coloured by the Jensen-Shannon divergence between
consecutive judgments — green where they agree, red where they argue. Boundary
*k* of row *i* joins boundary *k* of row *i+1*, because every judgment of a cell
shares the cell's label vocabulary, and where a judgment was recorded on a
different vocabulary the code takes `min` and **never invents a boundary**.

```
cell(6,1)  judges=[kestrel,marginalia,quill] rank=3 maxJSD=0.030 pairwise=[0.023 0.030]
cell(11,2) judges=[kestrel,marginalia,quill] rank=3 maxJSD=0.065 pairwise=[0.065 0.032]
cell(4,5)  judges=[kestrel,marginalia,quill] rank=3 maxJSD=0.054 pairwise=[0.054 0.033]
```

**Why this is better than a list, which is what the source has:** a list of
judgments is a *linear* artifact. Reading it costs one judgment at a time, and
comparing two of them is a memory task you have to do in your head while holding
both. The stitch makes the comparison a **shape**. You do not compute a
divergence and look it up; you see a thread that runs straight through a patch
where the panel agreed and jumps sideways where it did not. The number is still
there, in the hover readout, for the person who wants it — but the shape comes
first, and it is the shape that gets noticed at 22px.

---

## 5. The one you most wanted answered: does the grid survive being wrong?

**Yes — and here is the specific failure it survives.**

There are four different questions a cell can be answering, and they are not the
same question:

| quantity | asks |
|---|---|
| `choice` / `p(argmax)` | what did it pick, and how likely is that |
| `confidence` | what the judge says about **itself** — and per the contract this is *not* p(argmax) |
| `margin` | how *decided*, independent of how loud |
| `entropy` | how *spread out* the whole map is |

Collapsing any two of these is the bug. So `classify()` puts every cell in
exactly one of five buckets, and the surface draws each one differently:

- **settled** — low entropy, high margin. Clean ground.
- **open** — high entropy, low margin. Honestly uncertain. Fine.
- **contested** — **high entropy AND high margin.** ← this is the answer.
- **overclaim** — `confidence > p(argmax)`. The record contradicts itself.
- **void** — never judged. Not data. Not zeros.

**"High entropy with high confidence" is not one cell type, it is two, and they
look nothing alike:**

1. **contested** (high entropy, high margin): the judge is *decided* and the field
   is *contested*. Under relief-by-entropy this is the loudest cell on the
   surface. Here it is a **red seam** — a hard bar across the middle and a red
   cross through the cell — on a **thin** margin bar, over an **entropy-grain**
   texture. Loud, but the loudness now means the opposite of what it meant
   before. And it is enumerated: the sidebar lists every contested cell by
   coordinate and clicking one jumps the readout to it.
2. **overclaim** (`confidence 0.93`, `p(argmax) 0.44`): the judge claims more
   confidence in its answer than its own probability map allows. This is the
   *literal* "confidently wrong" signature and it is checkable arithmetic, not a
   vibe. It gets a yellow tick row along the cell's bottom edge. It is also
   ranked **above** contested in `classify()`, because a self-contradiction in
   the record outranks a disagreement in the field.

**Can a person see it?** In the fixture: 15 contested, 5 overclaim, 3 void, in
96 cells. Yes — the red seams are the first thing the eye lands on in the shot
below, and the void patches (hatched, colourless, no shadow, no grain) are
unmistakable next to them. The census in the sidebar is a second, independent
channel: the same five numbers, no pixels required.

---

## 6. It runs with no API key, and says so

There is no key in this environment, so the no-key path is not a fallback — it
is the path I ran. Three things, not one:

1. **A banner in alarm red** that states the distinction in a sentence, not a
   footnote: *"NO API KEY — THIS IS NOT ZEROS… 96 cells, 3 of them never
   judged."*
2. **`source: 'synthetic'`** in the tensor header, in the exported JSON, and in
   the fixture's own `note` field. The provenance is in the artifact, not in the
   UI chrome, so it survives `save tensor`.
3. **VOID is a type, not a rendering mode.** A void cell is hatched, colourless,
   has no cast shadow and no grain, is excluded from every mean, and is counted
   on its own line in the header (`93 judged / 3 void`) and its own row in the
   census. A distribution of zeros would be coloured, banded and lit. The
   verifier proves the two are not confusable by hashing both.

**The API is flaky, so failure is typed.** `FAILURE` has four members —
`TRANSPORT` (TLS EOF, 5xx, timeout, DNS) / `SCHEMA` (4xx with a validation
body) / `AUTH` / `NOKEY` — and **only `TRANSPORT` is retried**, with full-jitter
exponential backoff (250 → 4000 ms) and a kept attempt log. `JEV-CONTRACT.md`
records an hour lost to conflating these two and writing a document blaming the
contract; the type system exists so that hour is not available to spend again.
The wire shape is the source's, cross-checked against the contract's three
mistakes: `model` present and `jev-latest` (not the *response* id), `criteria`
values `null`, `type` as a union discriminator — and `confidence` is copied
through untouched, never recomputed from the map, because recomputing it is
exactly how you would erase the only field the judge says about itself.

---

## 7. The finding I did not expect: a fold destroys the thing you care about

I thought invariant 4 was a formatting concern. It is not.

```
12x8   contested 15   overclaim 5   void 3
6x4    contested  0   overclaim 21  void 0
4x2    contested  0   overclaim 8   void 0
1x1    contested  0   overclaim 1   void 0
```

Coarsening **dissolves every contested cell and manufactures overclaims.** The
mean of four decided-but-contested cells is a flatter, less decided cell, and a
flatter mean gets a `confidence` that no longer sits below its own top
probability. Zoom the grid out to see the shape of the field and you are looking
at a field where the confidently-wrong cells have all quietly become ordinary
ones. The 6×4 `overclaim` count of 21 against 5 at full resolution is not a
measurement, it is an averaging artifact — and it would have been read as data.

**The fix is to move the signal instead of dropping it.** Every coarse cell
records `block = {n, judged, spread, contestedInside, voidInside, sourceCoords}`.
The disagreement relocates from the mean into the block record, and:

- `contestedInside` is re-surfaced as red ticks on the coarse patch and rolled up
  as `swallowed: 17` in the census, which is the number you actually want at a
  coarse zoom.
- between-cell `spread` rides the grain channel, so a fold that averaged the
  disagreement away gets it back as texture.
- **VOID survives a fold** as `voidInside` — a coarse cell is never declared
  uniform just because it happens to be all zeros.

Verified: 17 contested cells at 12×8, 0 surviving as a *mean* at 4×2, **17
recovered from the block record.** The dial is honest about what it is
averaging, which is more than I expected to have to build.

---

## 8. What this can show that the original cannot — and what it cost

**Can show:**

- **contested and overclaim as first-class, countable, clickable states.** The
  distinction between *decided and contested* and *self-contradictory* exists
  nowhere in the four-field model; both fall out of it arithmetically and both
  are enumerable by coordinate.
- **disagreement as geometry.** JSD is a number in the source. Here it is a
  thread through a patch, and rank is a layer count.
- **rank visible at a glance.** How many times a cell was judged is the height
  of its stack, not a field in a record.
- **margin as a first-class dial**, with the argument for it: it is the only
  quantity that licenses "loud".
- **void as a type**, and a fold that reports what it swallowed instead of
  quietly diluting it.
- **one artifact, four labelled views**, each carrying the tensor's content
  address so you can prove two pictures are one field.

**What I gave up:**

- **A fork.** There was nothing to fork. The renderer is unreviewed by anyone who
  knows the original, and its craft bar is set by your description, not by
  comparison. This is the real cost and it is not recoverable in this sandbox.
- **d3 and the force layout.** The only browser artifact in the repo I could
  read is `docs/landing/jev-organism.html`, which is a d3 force graph of a
  loop's nodes — the wrong shape for a grid whose coordinates are identity
  (`cell.py` Law 1: identity never floats). Forces would move cells. So: zero
  dependencies, and the display list has exactly two op kinds (`clear`, `poly`).
- **A real second renderer to compare against.** The one saving grace is that
  `render()` is a pure function to a display list and there are two executors
  of it — Canvas2D in the browser and a pure-JS scanline rasteriser in
  `verify.mjs`. The PNGs in `out/` are painted by the same op list the browser
  paints, so the receipt is not a picture of something else. But both are mine.
- **A live judgment.** No key, so the fixture is hand-built. It is deterministic
  (seeded LCG, no `Math.random` in the data path) and byte-stable, and it is
  labelled `synthetic` everywhere, but **no number in these screenshots is a
  measurement.** The `Ask` path is written, typed and retrying; it is unexercised.
- **Anti-aliased edges.** Nearest-neighbour, on purpose, so a band boundary is
  exactly where the number says and resampling cannot move it.

---

## Files

```
quilt-jev-web/
  index.html          the surface
  serve.mjs           zero-dep static server (ES modules need it; file:// is blocked)
  verify.mjs          25 executable invariants + the negative control
  zoom.mjs            big-render one projection
  shot.mjs            drives real Chromium, 6 screenshots, 0 console errors
  src/tensor.mjs      the cell, the grid, fold, JSD, canonical bytes, invariants
  src/render.mjs      the four projections -> display list of polys
  src/raster.mjs      pure-JS scanline rasteriser + pixel hash   (node)
  src/png.mjs         PNG encoder via zlib + crc32                (node)
  src/jev.mjs         the client, the four failure kinds, backoff (node + browser)
  src/synth.mjs       the no-key fixture, with planted cases
  src/app.mjs         the browser executor. contains NO rendering logic
  out/*.png           9 receipts + 6 browser screenshots
```

Run it: `node verify.mjs && node serve.mjs` → <http://127.0.0.1:8171/>
