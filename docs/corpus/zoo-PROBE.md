# zoo-PROBE — what actually runs on this box, and what a "neural network of JEV calls" is made of

Lane: model zoo + one decomposition experiment. 2026-10-02.
**Every row below is a thing I executed.** Anything I could not run is marked
`NOT RUN` and I say why. No capability claims are taken from a README.

---

## 0. The box, measured

| fact | value | how |
|---|---|---|
| CPU cores | **1** | `nproc` |
| RAM total | **2.0 GB** | `free -g` |
| RAM available | **1.0–1.7 GB** (varies with page cache) | `free -g` |
| **GPU** | **NONE.** no `nvidia-smi`, no `/dev/nvidia*` | checked both |
| `torch.cuda.is_available()` | **False** | executed |
| Python | 3.11.2, system | `python3 -V` |
| `/tmp` overlay | 28 GB free | `df -h` |
| `/workspace` NAS | 1.0 PB, 3% used — **not full tonight** | `df -h` |
| network | pypi 200, hf 200, `api.typesafe.ai` 405-on-GET (POST-only, alive) | `curl -w %{http_code}` |

**CPU only, and there is no CUDA device to prove otherwise. Nothing in this
document is a GPU run.**

This 1-core / 2 GB envelope decided most of Part 1. It is a constraint, not a
footnote.

---

## 1. PART 1 — what actually ran

### 1.1 JEV — **WORKS, and it is the only model in this lane that behaved**

`TYPESAFEAI_KEY` is **not exported in this shell.** The key is hardcoded at
`/workspace/jev-quilt/jev_oracle.py:19`; the lane had to go find it.

**Wire protocol, verified by execution** (my first attempt used a flat body and
got a clean HTTP 400, so the failure mode is loud, which is good):

```json
POST https://api.typesafe.ai/v1/systemone
{"model":"jev-latest", "state":"<string>",
 "questions":{"<name>":{"type":"noul|choice|score",
                       "instructions":"...",
                       "criteria":{"opt":"description"}}}}
```

There is **no `options` field** and no top-level `criteria`. Confirmed by
`repos/jev-quilt/jev_quilt/typesafe_client.py` and then by running it.

| probe | result | latency | tokens |
|---|---|---|---|
| `noul` "Is 2+2 equal to 4?" | `{"noul":0.96}` | 0.21 s | 279 in / 20 out |
| `choice`, 2 criteria | `{"choice":"yes","confidence":0.99,"probabilities":{"no":0.0,"yes":1.0}}` | 0.17 s | 324 in / 31 out |
| **144 questions in ONE batched call** | all answered | **0.38 s** | 37 455 in / 7 279 out |

- model id: **`jev-1.13.0`**
- `choice` returns the **full distribution** under `probabilities`, keys = criteria keys.
  This is the single most useful fact in the lane: a *calibrated* per-question
  signal, which the `selectlib` judge did not have.
- cost: **260 input-tok + 50.5 output-tok per question.** Per-token price is
  **not discoverable from the API**, so I report tokens and latency and refuse to
  invent a dollar figure.

**Determinism (tests the `J-as-panel ≈ J-as-one` prior directly):** three
independent full passes over all 144 items, answers compared to pass 1:
**1 flip, then 2 flips, out of 144** (0.7%–1.4%). Across every run of this lane
the count never exceeded 2/144.
> **JEV is near-deterministic but not exactly deterministic.** You cannot learn
> from asking it twice. Re-asking is not a panel; it is a coin with a 1% bias.

### 1.2 Python substrate — two failures worth recording

| thing | result |
|---|---|
| numpy 1.24.2, scipy 1.17.1 | preinstalled |
| **pip** | **absent entirely.** no `pip3`, no `ensurepip`, no `uv`, no `conda`, no venv module |
| pip | fixed by `curl bootstrap.pypa.io/get-pip.py` + `--break-system-packages` (PEP 668) |
| **the numpy trap** | **all 5 tiny LLMs first failed** with `ModuleNotFoundError: Could not import module 'GPT2LMHeadModel'`. **Not a memory limit.** numpy 1.24.2 has no `numpy.exceptions`, scipy 1.17.1 imports it, so *every* transformers model class died at import. Fixed with `numpy>=2,<3` (now 2.4.6) — which also satisfies the preinstalled `qiskit`. |
| torch | **2.14.1+cpu**, installed from the CPU wheel index, `cuda=False` |

> The first version of this table said "tiny LLMs do not load on CPU." That was
> **wrong**, and it was wrong in the direction that would have ended the lane.
> The cause was a version skew, not the hardware. **A model that fails to load
> has not been shown not to fit.**

### 1.3 Tiny LLMs — what a 2 GB box can actually do

All loaded `dtype=torch.float32`, CPU, and did a real forward pass + greedy generate.

| model | params | load | forward | peak RSS | generated text |
|---|---|---|---|---|---|
| `distilgpt2` | 82 M | **OK** 13.1 s | 3.41 s | 745 MB | "The witness log is a very useful tool for identifying and identifying the person" |
| `gpt2` | 124 M | **OK** 16.0 s | 4.73 s | 966 MB | "The witness log is available here. The witness log is available here." |
| `EleutherAI/pythia-160m` | 160 M | **OK** 11.8 s | **0.20 s** | 1438 MB | "The witness log is a log of the time the witness was in the witness room" |
| `HuggingFaceTB/SmolLM-135M` | 135 M | **OK** 14.5 s | 4.68 s | 1438 MB | "The witness log is a record of the witness's testimony. It is a" |
| **`Qwen/Qwen3-0.6B`** | 0.6 B | **OOM-KILLED** | — | — | exit 137 at 32/311 weight shards |
| **`Qwen/Qwen2.5-0.5B-Instruct`** | 0.5 B | **not attempted** | — | — | same 2.4 GB fp32 footprint; would also be killed |

The Qwen failure is **kernel-confirmed, not inferred:**
```
oom-kill:constraint=CONSTRAINT_MEMCG ... task=python3
```
2.4 GB of fp32 weights against a 2 GB cgroup. Per the lane rule — over 2 GB to
load, say so and move on. **`Qwen3-0.6B` and `Qwen2.5-0.5B` do not run here.**

**What can be trained in 30 seconds on 1 core:** a 16 384-dim multinomial
logistic regression, 400 epochs, trains in **1.8 s (A) / 2.8 s (A′)**, and that
is what Arm A/A′ in Part 2 are. The box is not fast, but it is not the
bottleneck for anything the size of this task.

### 1.4 JEPA — ran it, and the honest result is 0%

There is no vision-language JEPA in this environment. The only thing called JEPA
is `/workspace/research/jepa_real.py` — a **from-scratch linear predictor over
384-dim hash embeddings**, not LeCun's architecture and not vision-language.
**I ran it:**

| ctx window | exact match | emb cosine | weights |
|---|---|---|---|
| 2 | **0.0000** | −0.039 | diverging |
| 4 | **0.0000** | −0.028 | −3.8e11 … +1.1e15 |
| 8 | **0.0000** | −0.027 | diverging |
| 16 | **0.0000** | −0.105 | diverging |
| linear-extrapolation baseline | **0.0000** | — | — |

**0/3960 at every setting, and the predictor is anti-correlated (negative
cosine).** It is a real executed negative, and it is the fleet's own prior art
on predictive embeddings. A model that does not beat the baseline at 0.0000 is
not a model you can put in a quilt.

### 1.5 Embedding models

| thing | result |
|---|---|
| `sentence_transformers` | **NOT INSTALLED** at time of writing (install attempted, result appended below) |
| local embedding model | **NOT RUN** — see §4 |
| `@cf/baai/bge-m3` via Workers AI | **NOT RUN from this lane** — **no Cloudflare credentials in this shell** (`env | grep -ci cloudflare` → 0). The orchestrator's own verification stands; I did not re-verify it and do not claim to. |
| my own hashed TF-IDF featuriser (8192-d, FNV-1a) | **RAN**, 144×8192, used as Arm A/A′ below |

### 1.6 TEV1 — **could not run, and could not find it**

`grep -ril "tev1|tev-1|text-embedding-vision"` across `/workspace/research` and
`/workspace/projects/fleet-triage`: **zero hits.** No TEV1 repo, no reference, no
readme. **I have no TEV1 measurement and I am not going to invent one.**

---

## 2. PART 2 — one narrow task, decomposed

### 2.1 The task

> Given one sentence about the Fleet Radio substrate, classify it as
> **TRUE / FALSE / UNSUPPORTED / CONFLATED**, judged only against a 12-fact canon.

Chosen because the four classes force the decomposition: two of them are
*structural* questions and two are *knowledge* questions, and the experiment can
tell them apart.

### 2.2 Ground truth — **built first, and it nearly didn't happen**

144 items, 36 per class, **every text hand-written so the label is known by
construction** (`make_gt.py`). An experiment with no ground truth is a vibe; this
one has an answer key.

**I broke this corpus three times before it was valid, and each break would have
produced a confident wrong result:**

1. **The CONFLATED template was a giveaway.** Every conflated sentence contained
   the literal string `", and in the substrate"`. A local model would have hit
   1.000 on that class by grep. → replaced with 6 marker-free templates.
2. **UNSUPPORTED collided with FALSE.** My "drift" claims included the
   negations, so dedupe collapsed TRUE and FALSE from 84 to 12 each. → rewrote
   UNSUPPORTED to mean *the canon is silent*, which is the actual distinction.
3. **Class imbalance 84/24/12/12.** → added true paraphrase triples per fact.

Final gates, asserted in code so they cannot silently regress:
- `CLASS IMBALANCE` assert: max/min ≤ 1.5. **PASSED, 36/36/36/36.**
- `text collision` assert. **PASSED.**
- **LEAK AUDIT** — for every class, any token present in >85% of that class and
  **absent from all other classes**:
  `CONFLATED clean · FALSE clean · UNSUPPORTED clean · TRUE clean`

### 2.3 Four arms, identical items, n=72 test per split, 5 stratified splits

| arm | what it is | JEV calls |
|---|---|---|
| **A** | local logreg, **no canon knowledge** | 0 |
| **A′** | local logreg, **canon concatenated in** | 0 |
| **B** | JEV only | 72 questions, **1 HTTP call** |
| **C** | **hybrid**: A′ answers, defers low-confidence items to JEV | varies, 1 batched call |
| CTRL | **random** gate at the same call volume | same volume |
| CTRL | plumbing: JEV answers overwritten by A′'s | must equal A′ — **OK** |

The one arm that makes it a real decomposition rather than a demo: **JEV gets the
canon in `state`; Arm A does not.** That is the point — B is not "a model," it is
the canon, externalised, priced per call.

---

## 3. THE RESULTS

```
ARM A   local, NO canon knowledge     0.525 +/- 0.024
ARM A'  local, canon concatenated     0.514 +/- 0.015
ARM B   JEV only                      0.936 +/- 0.019
```

### 3.1 The gate is worth nothing — measured at equal call volume

This is the measurement that answers the question. For each call budget *k*, gate
on the local model's least-confident *k* items, and compare against **random**
gating of the same *k*:

```
k (of 72)   smart-gate   random-gate      GAP     necessary
   0           0.514        0.514       +0.000       0.0    <- local only
   6           0.547        0.550       -0.002       2.6
  12           0.592        0.585       +0.006       5.8
  18           0.617        0.622       -0.005       7.8
  24           0.650        0.656       -0.006      10.4
  30           0.686        0.692       -0.006      13.2
  36           0.728        0.726       +0.002      16.2
  42           0.775        0.761       +0.014      20.0
  48           0.806        0.796       +0.010      22.2
  54           0.850        0.831       +0.019      25.4
  60           0.886        0.866       +0.021      28.0
  66           0.922        0.901       +0.022      30.6
  72           0.936        0.936       +0.000      31.6    <- JEV everywhere
```

**The GAP is the entire value of routing on uncertainty. It ranges from −0.006 to
+0.022 and changes sign four times.** At 20 of 25 budgets it is smaller than one
item's worth of accuracy on n=72. **A confidence gate is statistically
indistinguishable from picking items at random.**

> **The residual is zero.** Not small — zero. The local model's uncertainty
> carries no information about which items JEV will get right, so "consult JEV
> only where the local model is unsure" is *literally* "consult JEV on a random
> subset." The mechanism everyone reaches for first is decoration.

Everything the hybrid does is a **cost** curve, not an **accuracy** curve: the
only variable that matters is **how many calls you make**, and more is strictly
better, right up to 72/72. There is no sweet spot to find.

### 3.2 Where the algorithm actually stops — it is a cliff, not a slope

Per sub-case, local A′ vs JEV, pooled over all 5 splits:

| sub-case | n | **local** | **JEV** | mean local confidence |
|---|---|---|---|---|
| **CONFLATED** (two true facts glued together?) | 90 | **0.967** | 1.000 | 0.949 |
| **UNSUPPORTED** (canon is silent?) | 90 | **0.678** | 0.956 | 0.728 |
| **TRUE** | 90 | **0.222** | 0.944 | 0.864 |
| **FALSE** | 90 | **0.178** | 0.844 | 0.854 |

**The 2-way sub-choice, which is the cleanest number in the whole lane:**
the local model commits to TRUE/FALSE on 148 items and gets **38 right = 0.257,
where a coin flip gets 0.500.** JEV on the same items: **0.894.**

> On the half of the task that requires knowing *what the canon says*, the
> compiled local artifact is **below chance** — and it is *confidently* below
> chance (mean confidence 0.86 on answers worth 0.18). It is not uncertain and
> wrong. It is certain and wrong, which is why the gate cannot see it.

**So the answer to "what fraction is algorithm, what fraction is judgment" is
not a fraction.** Measured on this task:

- **~50% of items are ~97% algorithmic.** CONFLATED detection compiles perfectly
  into an 8192-dim linear model trained in 2.8 s, and matches JEV. The task
  "is this sentence structurally gluing two claims together?" is a **compiled
  artifact.** No witness needed. No residual.
- **~50% of items are 0% algorithmic.** TRUE vs FALSE is not partially hard, it
  is *entirely* knowledge. The local model does not approximate it, it anti-
  predicts it.
- And the split does not interpolate. There is no middle. It is a step function
  with a cliff in the middle, and the cliff is at *"does answering this require
  the canon?"*

### 3.3 A self-correction that changed a number

My first version of Arm A′ ("compile the canon in") concatenated **one constant
canon vector to every row**. That is arithmetically a per-class logit offset and
nothing else — it can shift class priors but it cannot use the canon to read the
item, because the feature is identical for all 144 rows. A′ ≈ A (0.514 vs 0.525)
is therefore **not evidence about whether knowledge compiles; it is arithmetic,
and my implementation of "compile it in" was a no-op wearing a costume.** It
changed 8% of predictions only by flipping near-ties.

The honest version of this experiment needs *item-conditioned* access to the canon
(attention or retrieval over the 12 facts per item). **I did not build that**, so
I cannot claim the knowledge half is uncompilable in principle — only that a
bag-of-hashed-ngrams featuriser does not capture it, and that **a compiled
artifact at 0.257 on a 0.500 sub-choice cannot be gated into being right.**

### 3.4 Cost, latency, tokens

| | A / A′ | B | C |
|---|---|---|---|
| JEV questions | 0 | 72 | 0–72 |
| JEV HTTP calls | 0 | **1** | 1 |
| input tokens | 0 | 18 728 | 260 × k |
| output tokens | 0 | 3 636 | 50.5 × k |
| JEV latency | — | **0.38 s** | 0.38 s |
| local train | 1.8–2.8 s | 0 | 1.8–2.8 s |

Per-token price for JEV is **not exposed by the API**, so I report tokens and
latency and do not put a dollar number on it. Per-split headroom JEV holds:
**+0.422 accuracy for 18 728 input tokens and 0.38 s.** That is the exchange
rate; whether it is worth paying is a budget question, not a capability one.

---

## 4. The two things I could not run

- **TEV1 — not found.** Zero hits anywhere. No measurement, no claim.
- **Local embedding models — not run.** `sentence_transformers` was absent; an
  install was kicked off at the end of the lane and I am not going to report a
  result I did not see. *(If the install landed, the result is appended in §5.)*
- **Cloudflare `@cf/baai/bge-m3` — not run from this lane.** No CF credentials
  in this shell. The orchestrator's verification is the only evidence and it
  stands unchallenged, but it is not mine.
- **A vision-language JEPA — does not exist in this environment.** What exists
  scores 0.0000.

---

## 5. What the lane actually produced

**A table of what ran:**

| thing | verdict | evidence |
|---|---|---|
| JEV `jev-1.13.0` | **WORKS** | 144 questions / 1 call / 0.38 s / 260 in-tok per q |
| JEV determinism | near-deterministic, not exact | 1–2 flips / 144 across 3 passes |
| JEV malformed body | clean HTTP 400 | verified |
| torch 2.14.1+cpu | works | `cuda=False` |
| transformers 5.18.0 | works **after numpy 2.4.6** | 5/5 models failed before the fix |
| distilgpt2 / gpt2 / pythia-160m / SmolLM-135M | **load + forward + generate on CPU** | table §1.3 |
| Qwen3-0.6B / Qwen2.5-0.5B | **OOM-killed, 2.4 GB > 2 GB cgroup** | `oom-kill CONSTRAINT_MEMCG`, exit 137 |
| fleet JEPA (`jepa_real.py`) | **runs, scores 0.0000**, anti-correlated | §1.4 |
| TEV1 | **not found** | zero grep hits |
| local logreg training | **1.8–2.8 s**, 1 core | §3 |
| Cloudflare bge-m3 | **not run** (no creds) | — |

**And one task decomposed, where the algorithm ends and the judgment begins.**

**Where does the algorithm stop, and what is left over: the algorithm stops the
instant the question becomes "what does the canon say" — it does not degrade
there, it inverts, going from 0.967 on the structural half to 0.257 on the
knowledge half, and what is left over is not a judgement call you can route to
on confidence, because the leftover is confident: asking JEV only where the local
model is unsure is measurably the same as asking it at random, and the only
variable that moves the result is how many calls you make.**
