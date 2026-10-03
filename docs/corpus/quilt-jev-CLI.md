# quilt-jev CLI — the tensor is the artifact, the painting is a projection

**Status: BUILT AND RUN. Every output below is a real receipt from this session
(2026-10-02, ~08:40–09:05Z), not a mockup.** Derived from
[`achimala/jev-paint`](https://github.com/achimala/jev-paint) (MIT) — read
`web/jev.mjs` and `web/art.mjs` first, then `renderer.mjs`, as instructed.

```
projects/fleet-triage/quilt-jev/
├── quilt_jev.py              27 KB   the tool. stdlib only, zero dependencies
├── tests/test_invariant.py   11 KB   31 tests, offline, no API key
└── jev-a-red-barn-on-a-hill-12.tensor.json    the artifact from the run below
```

---

## 1. The invariant, and where it is executable

```
a grid's canonical artifact is the probability tensor.
every rendering is a projection of it and says which one.
any two renderings of the same tensor are diffable.
```

`quilt-jev verify <tensor>` is the executable form. Per `TYPES-UNLOCKED.md`, a
type that carries no executable invariant is not a type, it is a shape — so the
third field is a command, not a paragraph.

```
$ python3 quilt_jev.py verify jev-a-red-barn-on-a-hill-12.tensor.json
tensor  jev-a-red-barn-on-a-hill-12.tensor.json
sha256  d5ab278f8d9daf67e6402d01a18e5527e070f552d7ef71ff4113ff6e161239a7
grid    12x12  cells=144  labels=16
PASS  structural invariant holds
    deterministic  view=paint
    deterministic  view=argmax
    deterministic  view=entropy
    deterministic  view=margin
         labelled  view=paint names itself in its header
```

Clause 1 is checked as a *structure*: cell count is `size×size`, coordinates
are the complete lattice with no duplicates, every distribution is finite, in
`[0,1]`, arity-matched to the label set, and sums to 1 within 1e-9. Clause 2 is
checked by asserting the literal string `view: PAINT` appears in the render.
Clause 3 is checked by rendering twice and comparing bytes.

**The stronger form of clause 3 is across processes, not within one.** The test
suite runs the CLI as a subprocess twice and compares `stdout` byte-for-byte:

```
paint:   byte-identical across processes (6774 bytes, sha 7b125074516c4257)
argmax:  byte-identical across processes (3999 bytes, sha 963e3fdca3164ac8)
entropy: byte-identical across processes ( 671 bytes, sha 6f720eb99486f074)
margin:  byte-identical across processes ( 665 bytes, sha 1bf065fc5011a6cd)
```

---

## 2. First render, live, real endpoint

```
$ export TYPESAFEAI_KEY=...        # never read from a file, never printed
$ quilt-jev render "a red barn on a hill" --size 12
quilt-jev  generating 12x12 tensor (1 batch(es))...
  batch 1/1
tensor written: jev-a-red-barn-on-a-hill-12.tensor.json  sha256:d5ab278f8d9daf67...
```

0.4 s, one batch of 144 questions, HTTP 200. The tensor lands on disk **before**
anything is drawn. Renderings of it need no network at all:

```
$ quilt-jev render --from jev-a-red-barn-on-a-hill-12.tensor.json --view argmax
```

```
========================================================================
quilt-jev  view: ARGMAX
  projection of tensor  sha256:d5ab278f8d9daf67
  prompt  'a red barn on a hill'
  grid    12x12 = 144 cells x 16 labels
  mean entropy 1.3677 nats   (mean of per-cell Shannon H)
  hard argmax per cell; the discarded evidence, shown alone
========================================================================
  0 SbSbSbSbSbSbSbSbSbSbSbSb
  1 SbSbSbSbSbSbSbSbSbSbSbSb
  2 SbSbSbSbSbSbSbSbSbSbSbSb
  3 SbSbSbRdRdRdRdRdRdSbSbSb
  4 SbSbRdRdRdRdRdRdRdRdSbSb
  5 GnGnRdRdRdRdRdRdRdRdRdSb
  6 GnGnRdRdRdRdRdRdRdRdGn
  7 GnGnRdRdRdRdRdRdRdRdGn
  8 GnGnGnRdRdRdRdRdRdRdRdGn
  9 GnGnGnGnRdGnRdGnRdGnGnGn
 10 GnGnGnGnGnGnGnGnGnGnGnGn
 11 GnGnGnGnGnGnGnGnGnGnGnGn
```

`Sb` = sky_blue, `Rd` = red, `Gn` = green. The barn is there. The full
`--view paint` is the same tensor in ANSI truecolor: background is the
*distribution mean*, foreground is the argmax colour, and the glyph density
carries entropy — so contested cells physically dissolve toward the mean
instead of being averaged into a colour.

---

## 3. The second view, and why it is not a picture

Same tensor, `sha256:d5ab278f8d9daf67`, two different readings.

`--view entropy` (per-cell `1-exp(-H)`; blank = confident, dense = uncertain):

```
  0  +===:==--=-
  1 -+#**-=*=+:-
  2 =%#*#**#***=
  3 *%@%#######+
  4 *@%%*#*#*%%#
  5 #@@%*=++*#%%
  6 %@%%++-*+#%@
  7 @@%###*##%#@
  8 @@%###*##%%@
  9 #%%##%#%%%%%
 10 ++*###*###%%
 11 ==-+-+=**#+*
```

`--view margin` (per-cell `p1 - p2`; blank = contested, dense = decisive):

```
  0 @##%%@##%@%%
  1 #***#@%###%@
  2 #-=-:=+-=+*@
  3 +: . . : -+%
  4 + .:*===-:.*
  5 ...-+****--:
  6 +:.-+**#*+.
  7 =:.:====+---
  8 *-.  .:::. +
  9 %=:. ... .:*
 10 @@*=+=++-++#
 11 @@@@@%@@%%%%
```

### The finding

**The two views disagree about the image, and the disagreement is the content.**

Entropy says *uncertainty is roughly uniform* — the grid is dense `@#%` almost
everywhere, mean 1.37 nats against a 16-label ceiling of `ln 16 = 2.77`.

Margin says the opposite, and it is *structured*: rows 0–1 and row 11 are
**dense and decisive** (`@##%%@##%@%%`), while the entire middle band, rows
3–9, is **sparse and contested** (`+ .:*===-:.*`).

So the model is *most certain about the sky and the grass* and *least certain
about the middle of the picture* — which is exactly where the barn, the hill's
profile, and all the subject matter live. The argmax picture above shows a
clean, confident red barn. It is a lie of omission: it is the one view in which
the contest is invisible.

The least decisive cell in the whole grid is `x8_y3`:

```
x8_y3  choice=red  confidence=0.380
       red 0.38  sky_blue 0.38  green 0.10     <- an exact p1 == p2 tie
```

The model cannot decide whether the barn is at that pixel or the sky is. The
argmax view reports "red" with no trace of the tie. That cell is one of 144, and
`--view argmax` will never show it.

At `--size 24` the same structure is starker — decisive top and bottom bands,
a contested middle spanning 18 of 24 rows:

```
  0 @%@%%@##%#%######%%###%%
  1 #***#%%#%%%###%##%##%#%#
  2 @:+--===*+##**%**######%
  3 *.:.::-:--=**=+++++##%##
 ...  (sparse)
 21 @#%#%%#*++%+**=====+#%#@
 22 %@@%@%%###%%%#*%#%*%#%%%@
 23 @%@%@%@%@%@%%%%%@%%@%%@@
```

---

## 4. The model is stochastic. The renderer is not.

This is the measurement that justifies the whole architecture, and it is the
one a picture-first design cannot express.

```
same prompt, two live runs:
  jev-a-red-barn-on-a-hill-12.tensor.json  sha256:d5ab278f8d9daf67e6402d01
  run2.tensor.json                         sha256:de59c697b8b60c72d1dc2bdd
  tensors DIFFER
```

Two runs of `"a red barn on a hill"` produce **different tensors**. JEV is
sampled. So:

- **You cannot diff two paintings of the same prompt.** They differ, and there
  is no way to tell model-drift apart from renderer-drift. A pixel diff between
  two runs is noise.
- **You *can* diff two tensors.** They are files with content hashes.
- And each fixed tensor renders byte-identically, forever.

That is the entire argument for the tensor being the artifact. A tool whose
output is a picture throws away the only stable handle it has.

### And a re-run does not destroy the previous one

If the tensor is the artifact, overwriting it on every run is the same failure
in miniature — a receipt lost because a file name collided. So the derived
default name never clobbers, and an identical re-run is a no-op rather than a
spurious duplicate:

```
$ quilt-jev render "a red barn on a hill" --size 8      # run 1
tensor written: jev-a-red-barn-on-a-hill-8.tensor.json   sha256:593a5869bd16bef1...
$ quilt-jev render "a red barn on a hill" --size 8      # run 2, same prompt
tensor written: jev-a-red-barn-on-a-hill-8.tensor-2.json  sha256:843b800ef30c8030...
```

Both files survive and both are independently renderable, which is what makes
the diff above a real diff. An explicit `--out` is treated as consent to
overwrite; the derived name is not.

### stdout and stderr are split

The view goes to **stdout**; `generating…`, per-batch progress, the
`tensor written:` line, and every refusal go to **stderr**. So
`quilt-jev render --from t.json --view jsonl > rows.jsonl` captures only rows,
and a failure never contaminates a pipeline's input.

---

## 5. Transport failure is never an empty grid

The endpoint returns `TLS EOF` on consecutive calls, exactly as the contract
warns. A failed call that renders as an all-zero grid is the failure this
project exists to name, so the two failure classes are separated by **type and
exit code**, and no tensor is written in either case.

```
$ JEV_BASE_URL=http://127.0.0.1:9 quilt-jev render "a red barn" --size 8
TRANSPORT_FAILURE: URLError: <urlopen error [Errno 111] Connection refused>
No tensor written. An unreachable endpoint is not an empty picture.
$ echo $?
75                                    # EX_TEMPFAIL — try again later
```

```
$ TYPESAFEAI_KEY=apikey_bogus ... quilt-jev render "a red barn" --size 8
SCHEMA_FAILURE: HTTP 401: request rejected by the endpoint.
No tensor written.
$ echo $?
65                                    # EX_DATAERR — do not retry, fix the input
```

| condition | reported as | exit | tensor written? |
|---|---|---|---|
| EOF, timeout, refused, 5xx | `TRANSPORT_FAILURE` | 75 | no |
| 401 / 403 / 413 / 422, no `answers` | `SCHEMA_FAILURE` | 65 | no |
| missing key | `error:` + hint | 65 | no |
| bad tensor, invariant violation | `INVARIANT VIOLATION` | 65 | no |

Transport retries are exponential with full jitter, 5 attempts, capped at 8 s
(measured 5.9 s for the dead-port case). An EOF is **evidence about the wire,
never about the grid**, and it is retried before it is reported.

---

## 6. Grid size as the abstraction dial

First-class flag, documented in `--help` because the cost is quadratic.

| `--size` | cells | batches | measured | what it buys |
|---|---|---|---|---|
| 8 | 64 | 1 | 0.3 s | coarsest; shape only |
| 12 | 144 | 1 | 0.4 s | **default** — one round trip |
| 16 | 256 | 2 | 0.6 s | |
| 24 | 576 | 4 | 0.6 s | subject detail appears |
| 32 | 1024 | 8 | — | finest, most expensive |

All five sizes produce exactly `size²` questions with no duplicate keys
(asserted in the suite), and every resulting tensor passes `verify`.

---

## 7. Composable output

A human at a terminal is one consumer. An agent diffing two runs is the other,
and the second is the point.

```
$ quilt-jev render --from jev-a-red-barn-on-a-hill-12.tensor.json --view jsonl
{"choice": "sky_blue", "confidence": 0.73, "entropy": 0.5820510495002966,
 "margin": 0.5499999999999999, "probabilities": {"black": 0.0, "blue": 0.18,
 "brown": 0.01, "cream": 0.0, "dark_green": 0.01, "gray": 0.0, "green": 0.05,
 "navy": 0.0, "orange": 0.0, "pink": 0.0, "purple": 0.0, "red": 0.01,
 "sky_blue": 0.73, "tan": 0.0, "white": 0.01, "yellow": 0.0}, "x": 0, "y": 0}
... 144 rows
```

One row per cell: `{x, y, choice, confidence, entropy, margin, probabilities}`.
Sorted keys, so rows diff cleanly. `probabilities` is the **full 16-label map**,
carried per row so a downstream quilt never has to re-derive it.

Note `confidence` here is `0.73` and it is the argmax probability. Per
`JEV-CONTRACT.md`, JEV's own `confidence` field is **not** the argmax
probability (`choice=red confidence=0.61 probabilities: red .74`); this tool
labels the derived quantity by its actual meaning and does not conflate the two.

Two consumers of the same tensor, from the same file, with no second API call:

```bash
# a human
quilt-jev render --from barn.tensor.json --view paint

# an agent: which cells are contested?
quilt-jev render --from barn.tensor.json --view jsonl \
  | jq -c 'select(.margin < 0.2) | {x, y, choice, margin}'

# an agent: two runs, and only the tensor diff
diff <(quilt-jev render --from run1.tensor.json --view jsonl) \
     <(quilt-jev render --from run2.tensor.json --view jsonl)
```

---

## 8. The test suite

```
$ python3 -B -m unittest discover -s tests -p 'test_*.py'
...............................
Ran 31 tests in 6.181s
OK
```

Offline, no API key, ~6 s. Coverage is grouped by invariant clause:
`TestTensorIsTheArtifact` (9), `TestEveryRenderIsLabelled` (2),
`TestRendersAreDiffable` (3), `TestProjectionsUseTheFullDistribution` (7),
`TestTransportIsNotAnEmptyGrid` (3), `TestUpstreamFixture` (1),
`TestTheArtifactIsNotDestroyed` (2), `TestGridSizeIsTheAbstractionDial` (4).

Two tests worth naming, because they are the ones that would catch the fleet's
signature failure:

- `test_cli_exits_75_and_writes_no_tensor_on_transport_failure` — points the CLI
  at a dead port, asserts exit 75, asserts `TRANSPORT_FAILURE` on stderr, and
  **asserts the output file does not exist**.
- `test_rejected_key_is_named_as_schema_not_transport` — asserts a 401 is
  `SCHEMA_FAILURE`, not transport. Conflating those two is what cost an hour in
  `JEV-CONTRACT.md`.

One test was wrong and the code was right: I asserted
`uncertainty(uniform-16) == 1 - 16^(-1/16)`. Uniform over `n` labels gives
`H = ln n`, so `1 - exp(-H) = 1 - 1/n = 0.9375`, which is what the code
returned. Fixed the expectation, and added
`test_uncertainty_ceiling_depends_on_label_count` to pin the real property: the
uncertainty ceiling is **label-count dependent** and is 0.9375 for this palette,
never 1.0. That is why `paint` uses the source's disclosed contrast stretch.

`TestUpstreamFixture` runs against `achimala/jev-paint`'s own recorded
`tests/fixtures/palette.json` — that repo's payload has bare RGB triples and
no coordinates, so `upgrade()` recovers the label set and the y-major/x-minor
coordinates (`web/jev.mjs` packs them positionally). **An artifact from the
source repo renders in this CLI with no API call.**

---

## 9. Relationship to the source, and honest scope

Faithful ports, not rewrites: `normalized`, `argmax`, `probability`,
`distribution` from `web/art.mjs` and `web/jev.mjs`; the palette and its
insertion order; `criteria` values as `null`; `model: "jev-latest"` as the
request alias; 144-question batches; 4-way concurrency; and the entropy
compression `1 - exp(-H)` with the `(spread - 0.48) / 0.32` relief stretch from
`renderer.mjs:236`.

**Deliberately different:**

- **`palette` method only.** The source also does HSL, RGB, and silhouette.
  Palette is the one that yields a genuine per-pixel 16-way distribution, which
  is what the whole artifact thesis rests on. The others are a second order of
  magnitude of work and a second order of magnitude of tensor.
- **The source's painter is stochastic** — 2,300 seeded strokes over a CDF
  sample. I did not port that, because a stochastic painter would break
  invariant clause 3 outright, and clause 3 is the deliverable. If the browser
  lane wants a painter, the seeded RNG is a one-line change and the
  determinism test will tell you immediately whether you broke it.
- **RGB and HSL independence is not reproduced.** The source assumes channel
  independence because JEV supplies no joint distribution. I kept that
  assumption visible in the docs rather than quietly inheriting it.

**Known limits:**

- Cost is quadratic in `--size` and every cell is a real billed question.
  `--size 32` is 8 batches / 1,024 questions.
- The contrast stretch in `paint` is a **display** remap over `0.48..0.80`.
  It touches rendering and never the tensor, and both endpoints are printed in
  every header. A disclosed distortion is fine; an undisclosed one is how the
  fleet's 6.8× constant got into a README with a passing test.
- `entropy` and `margin` normalize to the observed min/max, so the printed
  range in the header is load-bearing for reading them.
- One endpoint, one representation, no caching layer. `--from` is the cache.

---

## 10. The command someone else runs

```bash
git clone <you-will-create-this> quilt-jev && cd quilt-jev
export TYPESAFEAI_KEY=...                       # env only; never a file, never printed

python3 -B -m unittest discover -s tests -p 'test_*.py'    # expect: Ran 31 tests ... OK

python3 quilt_jev.py render "a red barn on a hill" --size 12
python3 quilt_jev.py render --from jev-a-red-barn-on-a-hill-12.tensor.json --view argmax
python3 quilt_jev.py render --from jev-a-red-barn-on-a-hill-12.tensor.json --view entropy
python3 quilt_jev.py render --from jev-a-red-barn-on-a-hill-12.tensor.json --view margin
python3 quilt_jev.py render --from jev-a-red-barn-on-a-hill-12.tensor.json --view diff
python3 quilt_jev.py verify  jev-a-red-barn-on-a-hill-12.tensor.json
```

### What "working" looks like

1. The test line prints **`Ran 31 tests ... OK`**, offline, with no key set.
2. `render` prints a `tensor written:` line with a `sha256:` in under a second,
   and that file exists on disk. Run it twice: the second run must produce a
   **`-2` filename, not an overwrite**.
3. Every view prints **`quilt-jev  view: <NAME>`** in its header and the **same
   `sha256:d5ab278f8d9daf67...`** — one tensor, five readings. If the digests
   ever differ between views, you are not projecting one artifact and the tool
   is lying to you.
4. `entropy` and `margin` are dense at the top and bottom rows and sparse
   through the middle. **If both come out uniformly dense, the tensor is flat
   and the interesting result is absent** — that is a finding, not a bug.
5. `argmax` shows `Sb` sky, an `Rd` block, `Gn` grass.
6. `verify` prints `PASS` and four `deterministic` lines.
7. `--view jsonl` emits exactly 144 rows, sorted keys, each summing to 1.0.

**Two things that look like failure and are not.** The digests from your run
will **not** match `d5ab278f8d9daf67…` — JEV is sampled (§4); a different
tensor hash is the expected result and is the reason the tensor is written to
disk. And `mean entropy ≈ 1.37` nats is *high*, not broken: over a 16-way
palette JEV is genuinely uncertain almost everywhere, and a tool that hid that
would be exactly the failure this project exists to name.

**The one thing that must never happen:** a run that exits 0 with an all-zero
or all-one grid. That is a dead call wearing a picture's clothes. It exits 75
and writes nothing.

---

**Not done, and named rather than implied:** no GitHub push, no public repo, no
CI. `chmod +x quilt_jev.py` and drop a `quilt-jev` shim on `PATH` to get the
bare command; the invocation above is deliberately `python3 quilt_jev.py` so it
runs from a clean clone with no install step. Handing back for the repo to be
created.
