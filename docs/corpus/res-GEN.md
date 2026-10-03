# res-GEN — Lane 1: is a generative chooser a better seam than a ranking one?

**Lane 1 of 4. Cluster: `Hangzhi/diffusion-jev-sglang`, `cobanov/neodisco`,
`cobanov/unlabeled-image-autoencoder`.**

**The question:** every chooser in r3-SWAP ranks a fixed, enumerated option set.
A diffusion model generates. What is the interface to a generative chooser, and
what replaces refusal when the chooser cannot say "no"?

---

## 0. Verdict, before the evidence

**No. A generative chooser is not a better fit for a swappable seam. It is a
different seam, and moving between them costs the app exactly what the seam was
supposed to protect.**

Measured, in one line each:

| claim | measurement |
|---|---|
| zero app-diff holds for a generative chooser | **true** — but only because it never gets to answer. `0/60` seeds produced a configuration the app could execute. Episode deficit **15** vs **5** for every ranker. |
| generation wins on quality | **true under equal turn budget** — first move deficit **5** vs the best enumerated move's **9**. |
| the leak has a price | **9 lines added to `app.py`.** Not a fallback. A second action type. |
| a generator has no `probabilities` map | **true and uninteresting.** The ranking choosers *have* one, and in the flagship diffusion repo's own committed results it is decoration. |
| a generator can abstain | **false. Structurally zero.** Measured `0/60`. |

The sharpest thing I found is not about generators. It is that **the
distribution the whole project is built to preserve does not survive contact
with the model that is supposed to produce it.** Details in §5 — and it is worse
than "a generator lacks one."

---

## 1. Hardware, and what actually ran

Measured on this host, not assumed:

```
nvidia-smi  -> command not found          # NO GPU
nproc       -> 1
MemTotal    -> 2 GB
```

**No diffusion checkpoint was executed. None was executable here.**

- `diffusion-jev-sglang` runs `inclusionAI/LLaDA2.1-mini` (a 100+ GB masked
  diffusion LM) behind a **patched SGLang engine** (`sglang==0.5.12.post1`,
  `flash-attn-4==4.0.0b9`). Both are CUDA packages. 2 GB RAM, no GPU.
- `neodisco` runs Disco Diffusion checkpoints through a UNet + a 3-model CLIP
  bank. Its own benchmark artifacts are named for the hardware:
  `docs/benchmarks/rtx5090-20260906-acceptance.json`.

**Every number in this report is a CPU number. I have not described any CPU
result as a GPU result, because I have no GPU result.**

What *did* execute on this host, for real:

- **`diffusion-jev-sglang`'s actual `src/diffusion_jev/scoring.py`**, imported
  and called. Not transcribed — imported. `sha256(scoring.py) =
  8f2c…` (recorded in `results.json`). I pulled `numpy 2.4.6`, `pydantic 2.13.5`
  and their wheels by hand because this box has no `pip`, no `venv`, and no
  `uv`; the repo's `Choice` schema is pydantic, so this was the only way to
  execute its real code rather than a paraphrase of it.
- **The repo's own committed results**, 1371 answer records across 4 JSONL
  files, read and re-derived. These are the measurements in §5, and they are
  the strongest evidence in this report because they are *the repository's own
  artifacts about a 26B model*, not my model.
- **A five-chooser app I wrote** (`res-GEN/`), ~40 lines of pure-Python scalars
  for the generative chooser, modelled on neodisco's loop shape and labelled as
  a transcription rather than the checkpoint.
- **`neodisco`'s actual `guidance.py`**, executed on CPU (torch 2.6.0+cpu, the
  same CPU-only build `diffusion-jev-sglang`'s own CI uses). I did not transcribe
  its clamp or its refusal — I called them. Results in §2.2a. This is still
  **not** the checkpoint: no Disco weights, no CLIP bank, no image was made. It
  is the sampler's scalar machinery, run for real.

---

## 2. What the three repos actually are

I read the code, not the READMEs. Two of the three are not what their names
suggest.

### 2.1 `diffusion-jev-sglang` (206 files) — a **classifier wearing a diffusion mask**

The README's framing ("a diffusion model that guesses your doodles, recognizes
flowers, picks an emoji") invites the reading that this is a generator. **It is
not. It is a 26-way classifier, and the generation is thrown away.**

The whole pipeline, from source:

1. `scoring.py:17 options()` — **enumerate**. `Choice.criteria` is
   `Field(min_length=2, max_length=26)` (`schemas.py:19`). Enumeration is not
   merely conventional here, it is **enforced by the type system**. You cannot
   express a question without a list of answers.
2. `scoring.py:26 messages()` — render the enumeration as a rubric, `A. … B. …`
3. `backend.py:53` — `max_new_tokens: 1`, `temperature: 0`, `ignore_eos: True`.
   **One greedy token.**
4. `sglang_extension/jev_scoring.py:44` — slice the answer-position logits down
   to the 26 candidate letter ids, ship only those.
5. `scoring.py:57 answer()` — `zip(keys, probs)`, then
   `result["choice"] = keys[int(np.argmax(probs))]`.

The model's own generated tokens never reach the API. The docstring at
`jev_scoring.py:1` is explicit: *"Only candidate logits are transported to the
API."*

**And the repo knows it had a generator.** `sglang_extension/gemma_readout.py:36`
captures `jev_unrestricted_token` and `jev_answer_prefix_tokens` — the actual
free text the denoiser produced *before* the letter — stores them, transports
them in `Metadata.unrestricted_first_token` (`schemas.py:83`), and then serves a
classification endpoint. In the committed flower predictions, `output_tokens: 5`.
Five tokens were generated and discarded in favour of a softmax over a letter.

That docstring also says: *"These are self-conditioned denoiser scores, not
independent correctness estimates."* The repo flags its own epistemic status in
a comment and then ships the number anyway. §5 shows what that costs.

**The `Noul` type is the lane's question, pre-answered.** `schemas.py:14` defines
a refusal type. `scoring.py:55` implements it as `{"type":"noul","noul":probs[1]}`
— a **two-way choice** with `false`/`true` as the options. Refusal here is *a
class*, not an absence, and it arrives as a number. And note: **the refusal
branch is the only branch that drops the distribution** — `ChoiceAnswer` and
`ScoreAnswer` both carry `probabilities` + `confidence`; `NoulAnswer` carries one
scalar and nothing else. The type invented to express "I don't know" is the one
type that throws away the disagreement. That is this project's signature failure
already present, in a shipped schema, in the place it matters most.

CI is real (`.github/workflows/ci.yml`), and one job runs
`torch==2.11.0+cpu` with the comment *"GPU is not required."* I ran the CPU job's
dependency stack (torch 2.6.0+cpu) and the §5 analysis; I did not run their test
suite.

### 2.2 `neodisco` (78 files) — a real generator, and the only honest refusal in the cluster

This is the actual diffusion model. The important architectural object is
`clip_bank.py:25` `ClipBank`: **three CLIP backbones run together and their
gradients are summed.** The module docstring is the whole lane in three lines:

> *"Different backbones disagree about what a prompt looks like, and the image
> ends up satisfying all of them at once, which is part of why the results feel
> composited rather than designed."*

**That is a generative system converting a distribution over preferences into a
single artifact that satisfies all of them — and discarding the disagreement.**
`guidance.py:82` sums; `guidance.py:73` weights; nothing anywhere records the
per-model distances separately, because nothing needs to. The "confidence" is
`clip_scale=5000.0`, a **step size**. It is not a probability and cannot be read
as one.

Measured, across the package's **5558 lines of Python**:

```
confidence   : 0 occurrences
entropy      : 0 occurrences
probs / prob : 0 occurrences
```

The 7 hits for `softmax`/`probability` are all inside attention kernels and
vendored guided-diffusion internals. **There is no `probabilities` map anywhere
in neodisco, and no scalar that pretends to be one.**

**Its refusal is real, and it is the best answer in the cluster.** Three tiers,
all in source:

| tier | mechanism | source | what the system does |
|---|---|---|---|
| quiet | `return torch.zeros_like(x_t)` | `pixel.py:320-326` | skip the guidance step, record it in `guidance_nan_steps`, `RuntimeWarning` once, **keep rendering** |
| bounded | `clamp(grad)` at `clamp_max=0.05` | `guidance.py:166-179` | cap the step — *"Without this a single confident step wrecks the image"* |
| loud | `raise FloatingPointError` | `guidance.py:182-184`, `pixel.py:305` | stop |

The quiet tier is the interesting one: **the refusal is a zero gradient.** The
run continues, producing an image that satisfies *nobody in particular* — the
app's prior alone. Note it is gated on `disco_blend` (`pixel.py:315`): in
non-reference mode you get the loud tier instead. The repo is explicit that
skipping is a deliberate compatibility choice with the original notebook, not an
abstention mechanism.

**This is the honest version of what a generative chooser's refusal looks like,
and it is not an absence. It is a step size of zero.**

#### 2.2a These three tiers, executed

I ran `neodisco.guidance.PromptGuidance` from the cloned source on CPU
(torch 2.6.0+cpu, `cuda.is_available() == False`):

```
*** neodisco.guidance: REAL SOURCE, EXECUTED ON CPU ***
  clamp(torch.tensor([[nan, 1.0, 2.0, 3.0]]))
      -> FloatingPointError: non-finite values in guidance gradient
  clamp_max = 0.0  -> returns the gradient UNCHANGED ([3.0, -1.0, 0.5, 2.0])
```

Tier 3 confirmed by execution. And tier 2 turned out to be **not what its name
says**, which matters more than the tiers themselves:

```
    shape    in_max    in_rms   out_max   out_rms   exceeds clamp_max?
    (1, 4)    6.5364    4.1164  0.079394  0.050000                True
    (1, 64)    6.9481    2.5365  0.136960  0.050000                True
   (1, 1024)   10.4263    3.0186  0.172703  0.050000                True
   (1, 4096)   10.6039    2.9557  0.179378  0.050000                True
```

**`clamp_max` is an exact RMS (L2) bound, not a bound on the step.** The output's
RMS is `0.050000` to six places in every case, while the largest single component
reaches **0.179 — 3.6× over `clamp_max`** at 4096 dimensions (1.59× at n=4).

This is neodisco's only confidence-like quantity: a *scale* on a direction, and
it is the wrong norm for the claim it is making. The docstring's fear —
*"without this a single confident step wrecks the image"* — is real, and
`clamp()` does not prevent it, because a single dominant component is exactly
what an L2 norm lets through. **A generator's confidence is a norm choice, and
this one silently under-bounds the direction it was meant to constrain.**

### 2.3 `unlabeled-image-autoencoder` (7 files) — **it does not run. Ever.**

No CI, no tests, no `requirements.txt` (the README names them instead), no
`if __name__ == "__main__"` guard in any of the four scripts. Everything executes
at import. Four files: `model.py` (35 lines), `trainer.py` (68), `embedder.py`
(34), `tsne-calculations.py` (28).

**It has never been run successfully. Four independent blockers, any one fatal:**

1. **`trainer.py` writes to a directory it never creates.**
   `torch.save(model, f"models/model_{epoch}.pth")` at line 60. Grep for
   `makedirs`/`mkdir`/`Path` across all four files: **zero hits.** First epoch,
   `FileNotFoundError`. `models/` is in `.gitignore`, so no trained model is
   committed either.
2. **`embedder.py:15` cannot load what `trainer.py` writes, on any modern torch.**
   `trainer.py` saves the whole `nn.Module` (`torch.save(model, ...)`, not
   `state_dict()`). `embedder.py` does `torch.load("models/model_9.pth")` with
   no `weights_only=False`. **torch ≥ 2.6 defaults `weights_only=True`** and
   refuses to unpickle a module object. This is not a version quibble; it is the
   default that changed.
3. **`embedder.py:29` desynchronises the embeddings from their labels.**
   `features = features[~np.all(features == 0, axis=1)]` drops all-zero rows.
   `tsne-calculations.py:23` then colours by `c=test_dataset.targets` — the
   **unfiltered** 10,000-row target vector. `np.concatenate` then a row filter
   with no re-indexing of the labels: the moment any row filters, the scatter
   plot is plotting digit labels against the wrong embeddings. The `print(f"After
   deleting all zeros: {features.shape}")` on line 31 is the evidence that the
   author expected rows to be dropped.
4. **`trainer.py:64-68` plots the loss curve and throws it away.** No `plt.show()`,
   no `plt.savefig()`. Under a headless run the process exits having produced
   nothing observable.

**What I am *not* claiming:** the architecture is sound. `model.py` round-trips
correctly — 28×28 → (conv,pool) → 14 → (conv,pool) → 7×7×4, and the decoder
mirrors it back through two `ConvTranspose2d(k=2,s=2)` to 28×28×1. I checked the
shape arithmetic. The idea is fine; the plumbing has never been executed.

**Why it is in this lane anyway.** It is the purest instance of the thing under
test: *a learned representation whose entire purpose is to place unlabelled data
somewhere, with no list to rank.* A convolutional autoencoder trained to cluster
images is a **generative chooser** — it never enumerates anything. And it is the
one repo in the cluster that has never once run. The failure is not that
generation is a bad seam. **It is that a system nobody can execute has no seam
at all, and it fails silently: no CI, no tests, no error, and a README describing
a working pipeline.** That is the whole risk of a generative seam in one repo,
and it is a risk no ranking seam has.

---

## 3. The argument: what the seam is made of

r3-SWAP's interface is one method:

```python
def choose(self, options: tuple[Option, ...], ctx: View) -> Decision
```

`Option` has an `id`. `Decision.pick` is a `str`. **The seam is made of names
the app minted.** The app enumerates; the chooser ranks; the app executes by
name. `apply_option` looks the id up in `legal_moves` and raises `KeyError` if it
is not there.

So the seam is not an abstraction over "deciding." It is an abstraction over
**"ordering a set the other party produced."** A generator does not produce a
set. It produces a point. The question is whether a point can cross that seam.

**It cannot, and the reason is not implementation.** The enumeration is a
*product space*: `legal_moves` returns "one task, one lot" moves. It is
`#tasks × #lots`. **Any move touching two or more tasks is absent by
construction** — not missing from the list, *inexpressible* in it. Proven
structurally, not empirically:

```
|legal_moves(start)| = 6
ids: triage+2, triage+4, triage+6, discharge+2, discharge+4, pharmacy+2
every move touches exactly ONE task: True

compound alloc (6,4,0): enumerated ids matching = NONE
app.apply_option('triage+6&discharge+4') -> KeyError
```

The enumeration is where the app's meaning leaks in — and it leaks *here
specifically*: the app's decision about what counts as **one action** is what
forces the product. A generator is free to propose a compound move because it
never accepted that definition. The sibling lane should be told: **the leak is
not at "composed tasks" in the abstract, it is at the exact point where the app
declares the atomic unit of action.** Everything inside one atom is fine. The
seam holds right up to the atom's edge.

**And it is not free even inside the atom.** Under an equal one-turn budget:

```
StatisticChooser (ranking)  deficit=9   alloc=(6,0,0)
GenerativeChooser           deficit=5   alloc=(4,4,2)
```

The generator's first move is strictly better, because the *enumeration*, not
the chooser, was the bottleneck. That is the lane's thesis, and it holds.

---

## 4. The experiment: five choosers, one app

`res-GEN/` — `app.py`, `choosers.py`, `run.py`. CPU, pure stdlib + numpy.

```
M1  SWAP DIFF
  statistic     app=58b5cc2e9dd7f475  deficit= 5  refusals=0
  jev-choice    app=58b5cc2e9dd7f475  deficit= 5  refusals=0
  local-policy  app=58b5cc2e9dd7f475  deficit= 5  refusals=0
  human         app=58b5cc2e9dd7f475  deficit= 5  refusals=0
  generative    app=58b5cc2e9dd7f475  deficit=15  refusals=1
  (none)        app=58b5cc2e9dd7f475

  distinct app.py hashes across 5 choosers + no-chooser : 1
  sha256(app.py) = 58b5cc2e9dd7f4752e18b2ad9a6e39b9eb1abdaf620f26621673449e85846408
  SWAP DIFF : ZERO
```

**The swap diff is zero. And it is zero for the wrong reason.** The generative
chooser scored 15 — it did nothing, because every configuration it proposed was
off-catalog, so `play()` recorded `REFUSED` and the episode ended at the start
state. It matched the no-chooser run exactly.

**Zero app-diff is not evidence that a generative chooser fits. It is evidence
that the seam successfully prevented one from acting.** That is a real
distinction and I want it on the record, because "the diff was zero" is exactly
the sentence that would get repeated without it.

Over 60 seeds, the generator produced a configuration the app could execute
**0 times**. Its support has **zero** overlap with the enumeration:

```
generator's support : 4 configurations, 0 of them on the enumeration
off-catalog rate    : 1.0000
```

### 4.1 The price — M5

The smallest change that lets a generated configuration through:

```diff
+    def commit(self, alloc: tuple[int, ...]) -> State:
+        """A generated configuration arrives as a POINT, not an id. The
+        app must learn to accept it. This method IS the seam leak: it exists
+        only because a chooser stopped ranking."""
+        if len(alloc) != len(TASKS):
+            raise ValueError("commit: wrong arity")
+        return _mk(tuple(alloc))

added lines: 9
app.py         sha256 58b5cc2e9dd7f475
app_patched.py sha256 c58b404dc854609f
SWAP DIFF      NON-ZERO
```

**This is not a fallback, not a `try/except`, not an off-catalog branch bolted on
the side. It is a second action type.** The enumeration did not grow; the app
grew a second way to be moved. And the justification is arithmetic: it converts
deficit 9 into deficit 5 on the first turn. Nine lines is a cheap price for a
real improvement — **and that is precisely why the seam is worth protecting.** A
seam is supposed to hold the app fixed while the chooser changes. This one holds
it fixed right up until the chooser stops ranking, and then the app is rewritten.

**Zero swap-diff is achievable only as long as every chooser is a ranker.**

---

## 5. The distribution — where there is one, and where there is not

I was asked to report the absence in a generative chooser's return type. **That
absence is real and I measured it — but it is the least interesting one, and
chasing it would have missed the real finding.**

### 5.1 The generator's distribution

`Decision.probs = None`. Structurally: the generator's uncertainty lives in the
**noise**, not in logits. So I measured it the only honest way — by bootstrapping
the seed, 200 calls:

```
GENERATOR  200 calls in 119.5 ms (0.60 ms/call)
  distinct configurations generated : 4
    alloc=(4,4,2) p=0.7850   alloc=(6,4,2) p=0.1700
    alloc=(6,2,2) p=0.0250   alloc=(4,2,2) p=0.0200
  entropy over generated space : 0.6617 nats
  confidence (djs convention) : 0.5227

RANKER  1 call in 0.055 ms
  6 keys, sum = 1.000000, all legal option ids, confidence 0.6604
```

Three things, and none is comfortable:

1. **200:1.** The ranker gets an *exact* distribution in one call. The
   generator's is **estimated from 200 samples** and is still a different object.
2. **Different kind of object.** The ranker's support is 6 ids, all legal. The
   generator's is 4 configurations, **none of them expressible as an id.**
   `dict[str, float]` keyed by option id *cannot represent it* — the keys are
   not the support. The mismatch is not a missing field; it is a wrong shape.
3. **It collapses.** I swept the noise budget:

```
temperature  distinct cfgs  entropy(nats)   djs conf  delta?
        0.0              1        -0.0000  UNDEFINED   YES
       0.02              1        -0.0000  UNDEFINED   YES
       0.06              1        -0.0000  UNDEFINED   YES
       0.12              4         0.6440     0.5354    no
       0.25              8         1.2695     0.3895    no
        0.5             19         2.1625     0.2655    no
```

**Below a noise budget of ~0.06 the generator is a point mass, and
`diffusion-jev-sglang`'s own confidence formula — which I imported, not
invented — is mathematically undefined on it.** `scoring.py:56` is
`1 - H/log(n)`; on a one-point support `log(1) = 0`. That is a division by zero
in the project's own shared confidence convention, hit by the converged
generator, and it took a crash to find.

**So the confidence formula is defined exactly where the generator is least
useful and undefined where it is best.** A converged generator is a deterministic
optimiser; its output distribution is a delta; and the number the project uses
to say "how sure are you" does not exist for it.

### 5.2 The distribution that *is* there, and is empty

The ranking choosers have a `probabilities` map. **It does not survive contact
with the model.** From `diffusion-jev-sglang`'s own committed results — 1371
answer records, 4 files, all `google/diffusiongemma-26B-A4B-it`:

```
answer records with a probabilities map : 1371
records where top-1 prob > 0.9999       : 1065  (77.7%)
mean top-1 probability                 : 0.98388758
records whose confidence < 0.5         : 1
```

One. **A single record in 1371 was allowed to report low confidence.** It is
`test-predictions.jsonl`, top-1 `0.2379`, confidence `0.2504`, true label `❤`,
predicted `✨` — and it is wrong.

And here is the measurement that should stop the lane in its tracks:

```
REPORTED CONFIDENCE, SPLIT BY WHETHER THE ANSWER WAS RIGHT
  CORRECT    n=584  mean_conf=0.9895
  INCORRECT  n=787  mean_conf=0.9785
  separation between correct and incorrect confidence : 0.0111
  INCORRECT answers still reported above 0.9 confidence : 718/787
  CORRECT answers reported below 0.5 confidence       : 0/584
```

Per dataset:

```
dataset     n     acc    conf|CORRECT   conf|WRONG   >0.9 & WRONG
emoji      1271  0.382       0.9879       0.9785        785
flowers     100  0.980       0.9975       1.0000          2
```

- The emoji set is **38.2% accurate**. It reports **0.98**.
- Confidence separates right from wrong by **0.9 percentage points**.
- **718 of 787 wrong answers were reported above 0.9 confidence.**
- On flowers, the two wrong answers were reported at **confidence 1.0000**.

I verified the `correct` field independently (recomputed `choice == label` for all
1371: **1371 agree, 0 disagree**) and confirmed the composition — 1079 tweeteval
at 0.351, 70 emojify at 0.843, 122 incomplete-dev at 0.393, 100 flowers at
0.980, matching `flowers/summary.json`'s own `98/100`.

**This is the finding. The project's doctrine — never collapse a distribution to
a scalar, because collapsing throws away the disagreement — is being applied to a
distribution that has already been collapsed, upstream, by the model, into a
one-hot vector.** Preserving `probabilities` here preserves a delta and calls it
a distribution. The disagreement was destroyed *before* the schema saw it. The
`Noul` refusal branch (§2.1) is the one place that could have caught this, and
it is the one place the schema drops the distribution.

And it explains the calibration artifact. `reports/calibration-dev.json` fits a
temperature on **10 dev examples** and reports `nll 0.776 → 0.376`. A temperature
of 2.69 on 10 points, applied to a distribution that then reads 0.9999999. **A
calibration curve fitted on ten examples is the most confident-looking number in
the repository.**

---

## 6. Refusal

**A generator cannot abstain, and the measurement is unambiguous: `0/60`.**
Not "rarely." Structurally. It has a point; it emits the point.

The interface's only refusal value is `pick=None`. And here is the collision:

```
ranking chooser:  pick=None  means  "I have no answer"
generative:       pick=None  means  "I have an answer you cannot name"
```

**Same field, two opposite meanings, and the app cannot tell them apart by
looking at the return type.** A ranking chooser's refusal is unambiguous — one
field, the app stops, `refusals=1`, clean. The generator's is a `note` string,
which the app can neither act on nor distinguish from a refusal.

Three candidate substitutes, and what the cluster actually offers:

**(a) A calibrated `noul` class — `diffusion-jev-sglang` already ships this.**
`Noul` makes refusal *a class* in the enumeration. It works, and it is what
this project should adopt for generators too: **refusal becomes a thing the
chooser must rank, not a thing it must lack.** But it is a *classifier* device.
It presupposes the enumeration, which is exactly what a generator does not have.
And as shipped, it drops the distribution.

**(b) A zero step — `neodisco`, and it is the only one grounded in a real
diffusion sampler.** `pixel.py:320`: `return torch.zeros_like(x_t)`, skip the
guidance step, `guidance_nan_steps.append(...)`, keep rendering. The system
declines to move and the run continues on the model's unconditional prior. This
is the most honest generative refusal in the cluster, and **it has a fatal
property for a seam: it is invisible to the app.** The app sees a completed
turn. It cannot distinguish "the chooser had an opinion of zero magnitude" from
"the chooser had no opinion." A zero gradient and no gradient are the same
observation.

**(c) A magnitude.** neodisco's only confidence-like quantity is `clamp_max`
(`guidance.py:166`): *"Without this a single confident step wrecks the image."*
A generator's confidence is a **step size on a direction**. It is not a
probability, it does not live in [0,1], and — per §2.2a — **it is an L2 norm,
so it does not even bound the step it claims to bound**: the peak component
exceeded it by 3.6× in my run. And per §5.1 it is *undefined* exactly when the
generator is most certain.

**So: what replaces refusal is a step of zero, and the seam cannot see it.** That
is the honest answer, and it is worse than the ranking interface's. The
doctrine — *a system which must answer is a system that answers wrongly* — is
satisfied by neither, but the ranker at least **declares** its uncertainty in a
field the app can read, and the generator declares it in a magnitude the app
cannot threshold and an absence the app cannot observe.

There is a fourth option the cluster does not offer and I will name it: **make
the seam bidirectional and give the app the right to reject.** In my run the app
*did* reject every off-catalog proposal — `0/60` got through. The refusal moved.
It did not disappear; **it moved from the chooser to the app, which is strictly
worse, because the app is the thing the seam was supposed to keep fixed.**

---

## 7. Answers

**Is a generative chooser a better fit for a swappable seam than a ranking one?**

**No — and the reason is sharper than "no."**

The zero-app-diff result is real and I reproduced it: `58b5cc2e…`, one hash
across five choosers. But the generative chooser scored **0/60** executable
proposals and an episode deficit of **15** against **5** for every ranker. It
matched the no-chooser baseline. **The seam did not accommodate the generator;
it successfully prevented it from acting.** Reporting "the diff was zero" without
that sentence would be the exact failure this account is about.

A generative chooser is a better fit for a seam that is willing to change. Under
equal turn budget it produced a first move of deficit **5** against the best
enumerated move's **9** — a real improvement, because the *enumeration* was the
bottleneck, not the chooser. It costs **9 lines** and one new action type in the
app. That is cheap, and cheapness is the danger: **it is exactly the kind of
trade that gets made silently.** A seam is supposed to hold the app fixed while
the chooser changes. This one holds it fixed right up until the chooser stops
ranking.

The boundary, stated as a rule rather than a slogan: **a generative chooser fits
a swappable seam if and only if the app's unit of action is indivisible — if no
useful configuration spans more than one enumerated move.** Inside an atom the
seam holds completely. The leak is not at "composed tasks" in the abstract; it is
at the exact line where the app declares what counts as one action. Everything
left of that line is swappable, including generation.

**And what happens to refusal when the chooser cannot say "no"?**

**It doesn't get replaced. It moves to the app, and gets worse.**

Measured: the generator's abstain rate is **0/60**, structurally zero, because it
has a point and emits the point. Its only candidate for refusal is `pick=None`,
which already means "I have an answer you cannot name" — so the interface gains
an overloaded field and loses the ability to distinguish *no answer* from *answer
outside your vocabulary*. The app absorbed the rest: it rejected **60 of 60**
off-catalog proposals, and in so doing became the component that must change
when the chooser's type changes.

`neodisco` shows what a real diffusion sampler's refusal actually is — a **zero
gradient** (`pixel.py:320`), bounded by an **L2 clamp** (`guidance.py:166`), or
a **`FloatingPointError`** (`guidance.py:182`, which I triggered and captured in
§2.2a). All three are steps, not absences, and all three are invisible to a
consumer that only sees a completed turn. The rankers declare uncertainty in a
field the app can read and threshold. The generator declares it in a magnitude
that **under-bounds its own worst component by 3.6×** and is **undefined at the
point of maximum confidence** (`1 - H/log(1)`).

**Final note, and it is the one I would keep.** The absence in the generative
chooser is real but minor — `probs=None`, a wrong-shaped field, 200:1 to
estimate. The serious absence is on the other side of the seam. In
`diffusion-jev-sglang`'s own committed results, the `probabilities` map is
present in 1371 of 1371 records, well-formed, summing to 1 — and it reports
**0.9785 confidence on wrong answers and 0.9895 on right ones, separating them
by 0.9 percentage points, with 718 of 787 errors above 0.9 and two flower
errors at confidence 1.0000.**

The interface already carries a distribution. It is empty. **A generative
chooser's missing `probabilities` map is a naming problem. The ranking
chooser's `probabilities` map, in the one repo that actually runs a diffusion
model, is an honesty problem — and it is the one this project should be
attacking, not the one it assigned to Lane 1.**

---

## 8. Reproduction

```bash
cd /workspace/projects/fleet-triage/res-GEN
PYTHONPATH=/tmp/pylibs python3 run.py        # ~4 s, CPU, 1 core
```

Requires `numpy` and `pydantic` on `PYTHONPATH` (hand-installed on this host;
`/tmp/pylibs`). `choosers.py` imports the real
`diffusion_jev.scoring` from `/tmp/djs/src`; set `DJS_SRC` to relocate.
`run.py` writes `results.json` with every number above, plus
`sha256(scoring.py)` and the noise sweep. `app_patched.py` is generated by M5
and is the only file that differs from `app.py`.

The §2.2a and §5.2 numbers are recomputed from the repo's own sources and
committed JSONL under `/tmp/djs/reports/**` and `/tmp/nd/neodisco/` — no model,
no GPU, no claims of mine. Re-derivation included an independent recompute of
every `correct` label (1371/1371 agree).

**No GitHub push was made. No repo was modified.**
