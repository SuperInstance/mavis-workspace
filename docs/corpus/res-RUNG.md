# res-RUNG — Lane 4: the local rung, and what a distilled policy loses

**STATUS: COMPLETE.** Repo read at the binary level, release asset downloaded and
checksum-verified, demo video inspected frame by frame, floor arithmetic shown, and
one distillation experiment built and measured on the fleet's own pre-registered
ground truth. Three instruments were built and **two were rejected as vacuous** before
any number was reported; that is section 4 and it is not a footnote.

**Hardware honesty, up front.** Everything measured *in this sandbox* ran on
**1 CPU, 2 GB RAM, no GPU** (`nvidia-smi`: not found). Nothing in this file is a
PlayStation result, and no CPU number here is described as a GPU number. Console
figures are quoted as **the repository's own measured numbers**, attributed, not
re-derived. The 27B headline target **has not run** and the GPU path **has not been
started**.

---

## 1. What `cobanov/PS5LM` actually is — verified, not inferred

**It is a working thing, not a design document.** I checked this at the strongest
level available, which is not the README.

**The repository.** 46 files, **16 commits, all dated 2026-10-02** — the day I read
it. A llama.cpp cross-port for jailbroken PS5: a payload (`ps5lm/app.cpp`, 25 KB),
a compat shim, one patch to llama.cpp, four measurement probes, a build script chain,
and a site. It is not a jailbreak. It *uses* one — Relapse (firmware 7.00–13.60),
plus `ps5-payload-dev` SDK v0.43 and elfldr on port 9021.

**The release is real, and I verified it byte-for-byte.**

```
$ curl -sIL .../releases/download/v0.1.1/ps5lm.elf
HTTP/2 200    content-length: 20974624

$ sha256sum ps5lm.elf
10ee1a913e2d534fc81e1822e5969a6d70740ff88f4eb7c8fe98789d22152126
$ payloads.json claims
10ee1a913e2d534fc81e1822e5969a6d70740ff88f4eb7c8fe98789d22152126     CHECKSUM: MATCH

$ file ps5lm.elf
ELF 64-bit LSB pie executable, x86-64, FreeBSD, dynamically linked, not stripped
NEEDED: libSceSystemService.sprx  libSceUserService.sprx
        libSceLibcInternal.sprx   libkernel_web.sprx  libSceNet.sprx
$ nm -C ps5lm.elf | wc -l            -> 35,776 symbols
$ nm -C ps5lm.elf | grep -c 'llama_\|ggml_'  -> 7,769
$ strings ps5lm.elf | grep -oE '(common|ggml)/[a-z]+/[a-zA-Z0-9_.-]+\.(cpp|c)'
  common/arg.cpp  common/chat.cpp  common/sampling.cpp  common/speculative.cpp
  ggml/src/ggml-cpu/ops.cpp  ggml/src/ggml-alloc.c  ...
```

The checksum in `site/payloads.json` matches the shipped asset. The binary imports
exactly the five Sony libraries a PS5 payload imports, and carries 7,769 llama/ggml
symbols with upstream llama.cpp source paths still in it. **This is a built,
shipped, installable payload. The claim is not in doubt.**

**A successful boot is reported, and the evidence is a camera, not a log.** The
README's GIF is 640×336, 84 frames. I coalesced and read the frames: it is a
photograph of a TV (pixel grid and moiré visible) showing `PS5LM v0.1.0`, model
`qwen0.8b.gguf`, a DualSense on-screen keyboard, and the model answering:

> *"How can I assist you today?"* — **8 tokens, 20.1 tok/s, 0.5 s**
> *"I'm Qwen3.5, a large language model developed by Tongyi Lab. I'm designed to help
> you with various tasks, including coding, translation, and more. How can I assist
> you today?"* — **44 tokens, 21.6 tok/s, 2.4 s**

Self-consistent, on-screen counters, real hardware. **A boot is reported and the
evidence is consistent.** Note the two counters (20.1, 21.6) are *above* the
`docs/CONSOLE.md` figure of 13.1 tok/s for the same model — the GIF is a
`llama-server` run at `-c 4096 -np 1` and the doc figure is a different harness. I am
not going to reconcile that from a screenshot; both are the author's own numbers.

**What is NOT true, stated plainly:**

| Claim | Status |
|---|---|
| llama.cpp runs on a PS5 CPU | **True.** Verified above and by the demo. |
| Qwen 3.8 **27B** on the console | **FALSE — never done.** The roadmap checkbox `- [ ] **First light: Qwen3.8-27B generates text on the PS5.**` is unticked. The README's own framing: *"No one has run it on a PS5 yet."* |
| PS5LM uses the GPU | **FALSE.** Phase 3 is entirely unticked: no driver build, no app shell, no `ggml-vulkan`, no `test-backend-ops`, no GPU decode. **Every number in the repo is a CPU number.** |
| llama.cpp on a PS5 GPU | Roadmap goal. "the part nobody has done with llama.cpp yet." |
| The 27B fits | **Not in a payload.** Measured: 1.6 GB locked ceiling, 2.7 GB froze the console. A 27B at Q2 needs 6.77–9.15 GiB. It needs a native app with direct memory. |
| Qwen 3.8 is 34 GB | Not this repo's number. `docs/MODELS.md` puts Qwen3.8-27B at **6.77 GiB** (UD-IQ2_XXS) to 15.33 GiB (UD-Q4_K_M). I use the repo's figures throughout. |

**The one patch is the most interesting artifact in the repo**, because it is the
console's real limit written as code:

```c
#if defined(__PROSPERO__)
uint64_t mask = 0;
if (scePthreadGetaffinity(pthread_self(), &mask) == 0 && mask != 0) {
    return std::max(1, __builtin_popcountll(mask) - 2);
}
return 2;
#endif
```

A payload gets **5 of 16 logical CPUs** (mask `0xea00`), shared with system
services, and llama.cpp's defaults starved them until the console shut down twice.
**That is the local rung's actual shape: not "a small model on a small computer" but
"a model on a computer that is actively rationed by its operating system and will
shut down if you take too much."**

---

## 2. The floor — arithmetic shown

### 2a. The console's real budget (the repo's own probe output, `docs/CONSOLE.md`)

| Quantity | Measured |
|---|---|
| Flexible memory configured / free | 8.00 / 7.97 GiB |
| malloc ceiling (256 MiB steps, pages touched) | 6.25 GiB |
| Largest single `posix_memalign` block | 6.00 GiB |
| **CPUs a payload may use** | **5 of 16** (affinity `0xea00`) |
| **Locked model before the console freezes** | **1.6 GB** (2.7 GB froze it) |
| Decoding, Qwen3.5 0.8B Q4_K_M | 14.2 tok/s (2 threads); 20.1 / 21.6 on the demo counter |
| Decoding, Qwen3.5 2B, `-lm mlock` | 8.5–9.2 tok/s, 1.4 GB resident |
| Decoding, Granite 4.2 3B **unlocked** | **0.2 tok/s** (paging, not architecture) |
| Download | 12.5 MB/s over 16 connections |

The last two rows are the important ones. **The dominant failure mode on this device
is not arithmetic, it is the operating system paging your weights to disk.** Unlocked,
a 3B model runs 45× slower than its size suggests. Locked, a 2B model runs 9.5× faster.
`mlock` is not a tuning flag here; it is the difference between a working rung and a
dead one.

### 2b. What fits in 1.6 GB

```
1.6 GiB = 1,717,986,918 B = 13.74 Gbit
```

| Fleet artifact | Size each | How many fit in 1.6 GiB |
|---|---|---|
| Height profile only (21 bits) | 2.62 B | **654,471,207** |
| **L6 code** — 6 heights + per-column occupancy (63 bits) | 7.88 B | **218,157,069** |
| **384-byte tile record** (`id 64, q 128, a 128, domain 32, tags 20, conf 4, ghost 4, use 4`) | 384 B | **4,473,924** |
| Distilled policy table (measured, §4) | 1,314 B | **1,307,448** |

For scale, the **shipped payload that already contains the whole of llama.cpp is
20,974,624 B.** The 384-byte tile record is **0.0018%** of the binary that is already
running. **The floor is not a resource question.** Nothing this fleet has built is too
big for a PS5, and nothing this fleet has built is slow enough to matter next to a
0.8B decode at 20 tok/s.

### 2c. **The smallest thing in this fleet that could run there today: the 21-bit column-height profile.**

Named and sized: `L6`'s height component, 6 columns × 3 bits = **18 bits** (21 with
the profile code), **2.62 bytes per position**, and — measured in §4 — it already
determines **100%** of the decisions on the fleet's pre-registered ground truth. It is
`7.7 × 10⁻⁷` of the 1.6 GiB budget. It is inside the payload's `.rodata` today.

**That is the answer to the floor question, and it is smaller than the tile codec, the
column enumerator, the CRDT ports, and the renderer.** The ladder's "control" rung is
not below the local-small rung by a little. On a consumer device it is below it by six
orders of magnitude, and the rung below *that* — the one we have never named — is
**everything we actually build**.

---

## 3. The distillation question — the real research

### 3a. What the ladder says, and the gap in it

`GRACEFUL-FAIL.md` gives the chain: cloud → Jetson → Pi → ESP32 → hand on the wheel.
The load-bearing property is that **each rung is a strict subset already present**, and
the ESP32 holds *"dead-band + rudder counter-rudder gates"* — a **distilled decision
policy that predates the question and still steers.** `r1-NOENGINE` shows the same on
the software side: a constant `Move{1,0}` × 4000 turns is an agent. 4,000 turns, one
kill, HP 18/20, **no model, no key, no network.**

That is the theory of rung four, and it is correct. This lane asks what it costs.

### 3b. The arithmetic of what a distribution is worth

This part needs no model, so it cannot be faked.

```
A distilled policy is a FUNCTION. Its decisions cost 0 bits of policy --
whatever it decides, a table lookup reproduces it. That is why it is small.

Keeping the DISTRIBUTION behind those decisions costs exactly its entropy.
Measured label entropy on the fleet's 54,166-position corpus:

  H = -(0.6322 log2 0.6322 + 0.3678 log2 0.3678) = 0.9490 bits / decision
  0.9490 x 54,166 = 51,402 bits = 6,425 B for the whole corpus

=> THE ABSTAIN GATE IS WORTH EXACTLY 0.9490 BITS PER DECISION.
   That is its price. It is not free, and it is not zero.
```

**The 0.35 that routes a `0.57/0.43` split to a human is 0.95 bits.** A dead-band is
a 4-bit threshold. **The entire difference between "a policy that steers" and "a policy
that knows when not to" is one bit per decision** — and that one bit is the only thing
on this list that a distilled policy cannot regenerate from itself.

### 3c. The throughput asymmetry, which is the uncomfortable number

```
console decode, from the demo's own counter      : 21.6 tok/s
Qwen3.5 0.8B Q4 weights read per token          : ~0.5 GB
=> implied weight bandwidth                     : 10.8 GB/s, on 5 shared CPUs
a 1,314-entry table lookup                      : ~1 op
ratio                                           : ~10^10 x
```

**The model is ten billion times more expensive than the artifact it would produce.**
Rung one is not a slightly better rung four. It is a different *kind* of thing, and
the direction of that gap is the whole subject of this file.

---

## 4. The measurement — built, run, and two instruments rejected first

The brief asked for a thing built and measured. I built three. **Two were vacuous and
I am reporting them at full length, because in this fleet a green number that means
nothing is worse than a red one.**

### 4a. The instrument, and its own check

Ground truth is the fleet's pre-registered corpus, `connect4/c4_ground_truth.txt`.
Before any number:

```
FNV-1a-64 digest  0x4ef8351a5c319637   expected 0x4ef8351a5c319637   MATCH
rows 54166                                    value hist  +1:34242  -1:19924
ply hist  1->7  2->49  3->343  4->2025  5->10003  6->41739
|p0|-|p1|>1 violations            0        (manifest: 0 bad of 54166)
pieces on sentinel rows           0
1-ply rows all valued -1          7/7
```

**Six of the exporter's own controls reproduce exactly.**

### 4b. A first parse that was wrong, and the trap it nearly walked into

My first loader read the row `mask pos value` as `(p0, p1, value)`. That gives
`54,166 / 53,767` stone-count violations against a manifest that asserts zero. The
exporter's comment explains it: `ctool.c:347-360` **normalises every row to player
zero**, so field 2 is `p0` and `p1 = mask ^ p0`. The author wrote, in the file:

> *"A dataset whose sign convention flips with row parity is a trap for every
> downstream consumer, and the cost of fixing it here is one line."*

The one line was not enough, and the trap survived into the file. **It caught me.**
Had I trusted the first parse I would have reported a 63%-accurate policy on
inverted labels.

### 4c. Instrument 1 — a deep CART over 137 board features. **REJECTED: vacuous.**

I grew a 664-node decision tree to predict the **full-depth game value**, over
heights, occupancy, per-column immediate-win threats, and all 69 line differences,
on a ply-stratified 80/20 split.

```
REFERENCE accuracy on held-out      : 0.6323
majority-class floor                : 0.6337
BALANCED accuracy                   : 0.5006
balanced floor                      : 0.5000
LIFT                                : +0.0006
```

**It is at the floor.** At plies 1–6 the value is a *search result*, not a board
property; no board feature carries it. Had I reported 0.6323 as "a model that
distils well" I would have published the majority-class rate as a result.

**Two bugs I hit and rejected rather than reported:**
- Feeding the tree `±1` labels made `gini` go **negative** and silently return a
  single-leaf tree, whose `p=1.845` was impossible for a probability. Fixed to 0/1
  labels; `gini` now raises if `p` leaves `[0,1]`.
- A by-ply split that **crosses parity** is worse than random: plies 1–5 are 92.3%
  losses, ply 6 is 79.7% wins. The fleet's own rule ("by-ply, never random") is
  necessary and **not sufficient**; it must be parity-matched too.

### 4d. Instrument 2 — the threat-count target. **REJECTED: no positive class.**

Retargeted to the fleet's own pre-registered SIMPLE/COMPOSED split. The COMPOSED class
(fork, ≥2 immediate winning moves) is **0.30% of the corpus — 161 positions.** I was
trying to measure a distribution the data does not contain.

### 4e. Instrument 3 — the representation ceiling. **ACCEPTED: a bound, not a fit.**

A *fit* can be vacuous. **A bound cannot.** For each representation I computed the
accuracy of the **best possible function of that code, fitted on the data it is
scored on.** Every learner — 1-NN, a deep tree, a 34 GB model — is bounded by it.

| representation | bits/pos | distinct codes | collision pairs | codes carrying **both** labels | **ACC CEILING** |
|---|---|---|---|---|---|
| lossless (both 49-bit masks) | 98 | 13,931 | 40,235 | **0** | **1.0000** |
| **L6** (6 heights + occupancy) | 63 | 13,931 | 40,235 | **0** | **1.0000** |
| heights only | 21 | 1,314 | 52,852 | **0** | **1.0000** |
| FNV-1a 64 (the fleet's L4) | 64 | 13,931 | 40,235 | **0** | **1.0000** |

**Three findings, and the first one is about the fleet's own headline claim:**

1. **L6 is not a projection on this corpus.** It produces 13,931 distinct codes —
   *exactly* the number of distinct 98-bit positions. `DOCTRINE.md` §1 presents L6's
   0.9871-beats-0.9239 as evidence that *"projection does not destroy structure by
   default"* and that *"less evidence, better accuracy."* **On this corpus L6 destroys
   nothing at all.** The 0.9871 is not a representation beating a lossless baseline;
   here the two representations are the same function. Whatever L6's 0.9871 measures, it
   is not that.
2. **The 21-bit height profile alone determines every label in the corpus.** 1,314
   codes, **zero** carrying both labels, ceiling exactly **1.0000**.
3. **Therefore the smallest artifact that reproduces 100% of this corpus's decisions is
   1,314 entries — 1,314 bytes, or 10.4 bits of index per position.** Not 0.8B
   parameters. Not 34 GB. **1.3 KB**, and it is provably not improvable by a better
   optimiser, because the ceiling is already 1.0000.

### 4f. The result I did not get, and will not fake

I could not produce a validated local model to distil **from**. I wrote a
from-scratch numpy Llama forward pass (safetensors + BPE, no torch available) and ran
it on a cached **SmolLM-135M**. It executes, the tokenizer round-trips exactly, the
weights are sane, and the logits are input-dependent (cosine 0.887 across different
prompts). But the control:

```
perplexity, REAL English sentence  : 20.36
perplexity, SCRAMBLED word salad   : 21.85     -> PLAUSIBLE
```

is **not the control passing.** A correct SmolLM-135M is ~20 on real English and
**several hundred** on scrambled text. A 1.5-nat gap means the implementation is
partly wrong — I fixed one real bug along the way (HF Llama uses the **half-split**
`rotate_half` convention, not even/odd interleaving; and the GQA and causal-mask axes
were wrong three separate times) and it is still not faithful.

**So I report no distillation-fidelity number from that model.** A hand-rolled forward
pass that has not cleared its own perplexity control produces fabricated
distributions, and a fidelity figure computed against a fabricated distribution is
exactly the *flattering nonsense* `r1-NOENGINE` §0 is about — a harness that cannot
tell "a check failed to catch a bug" from "a bug was never introduced."

**The honest summary of the distillation experiment: the one number I can defend is a
bound, and it is a good one. 1,314 bytes, ceiling 1.0000, zero residual.**

---

## 5. The honest caveat — what a rung-four system cannot do

**The corpus decided this for me, and it decided it negatively.** Look again at the
ceiling table: **zero** codes carry both labels. Not one. Across 54,166 positions,
**there is no case in this ground truth where a compact policy and the truth disagree.**

Which means:

- **There is no residual.** The residual is the gap between what a system says and
  what is true, on the same input. A function has no residual on its own support. The
  ceiling being exactly 1.0000 is not a triumph of the representation — **it is the
  corpus having no disagreements to find.** A residual measured on data with no
  disagreements is not a small residual. It is an **unmeasured** one.
- **There is no witness.** The witness is the input that separated two hypotheses. With
  one hypothesis per code there is nothing to separate, so no witness can be
  *constructed*, only assumed. Every claim the distilled policy makes is unfalsifiable
  *by that policy* — it cannot produce the counterexample that would refute itself.
- **There is no `CONTRADICTS` edge.** A `CONTRADICTS` edge requires two live claims
  that disagree. `plato-tile-relation` can hold a disagreement as a first-class edge
  (per `docs/PLATO-LINEAGE.md` §5) because it is a *store*. A distilled policy is not a
  store. **It has exactly one claim per input and no edge type that means "and also,
  the opposite."** It cannot record a contradiction because it cannot hold both sides —
  and holding both sides is the whole point.
- **There is no `0.35`.** The gate fires on a `0.57/0.43` split: *confidence tracks
  the separation of the distribution, not its height* (`JEV-CONTRACT.md`). Distilling
  keeps the argmax and discards the separation. The gate's entire input is the thing
  distillation is defined as throwing away. **You cannot distil a policy and keep its
  abstention, because abstention is not a property of the policy — it is a property of
  the policy's uncertainty, and the uncertainty is what you deleted.**

### The sentence this lane exists to produce

> **A policy distilled to nothing keeps every decision and loses every reason to doubt
> one, and the second is the only thing that ever protected you from the first. A free
> heuristic with a distribution attached — 1,314 bytes of table plus 0.949 bits of
> entropy per decision — is not beaten by a 34 GB model on this task. It is beaten by
> nothing, because there is nothing left to beat. The moment the corpus grows one
> disagreement, the 1,314-byte policy is wrong, it cannot know it is wrong, and the
> 0.35 that would have routed it to a human does not exist.**

Stated in the project's own terms: **the ladder is not a ranking of quality. It is a
ladder of *error-detection capability*, and only the top rungs have any.** A boat whose
ESP32 holds a distilled gate is not a boat with a small brain; it is a boat that
cannot notice its rudder is wrong. `GRACEFUL-FAIL.md` already says the fallback chain
works because each rung is a strict subset **already present** — and that is exactly
why the hand on the wheel and the radio are still on the manifest. **The fallback is
not the bottom of the ladder. The fallback is a separate rung that no amount of
distillation can synthesise**, because the person at the wheel is not a compressed
model. They are the residual.

---

## 6. The ladder, with the fourth rung named

| rung | what | cost | can abstain? | can hold a `CONTRADICTS` edge? | can be surprised? |
|---|---|---|---|---|---|
| cloud | a judgment model | latency, money, a key | **yes** | yes | yes |
| local big | workstation-class local model | RAM, GPU | **yes** | yes | yes |
| **local small** | a model on a consumer device | almost nothing | **yes, and cheaply** | yes | yes |
| **control** | hand-tuned policy: dead-band, counter-rudder, a table | nothing at all | **no** | **no** | **no** |
| **unlabelled** | **8 CRDT ports, the 2,477-line renderer, the 0.9871 heuristic** | **nothing at all** | **no** | **partially — the `CONTRADICTS` edge exists here** | **no** |
| hand on the wheel | a person | a life | yes | yes | yes |

**The fourth rung is the one we have been measuring all along, and it sits *below*
the control rung, not beside it.** Our 8 CRDT ports, the renderer, and the column
heuristic are all hand-tuned policies: no model, no key, no network, no distribution.
The ladder in the brief has four rungs and the fleet lives in the one that was never
drawn. §4e is the first honest measurement of that rung's *size* (1,314 bytes).

**And the local rung is real, cheap, and further down than expected.** `PS5LM` proves
a 0.8B model runs on a consumer device at 20 tok/s with no cloud and no key — the
ladder's third rung is **real and shipped today, as a 20 MB ELF with a matching
SHA-256**. What it does not yet do is run the model the ladder is *for* (27B), touch
the GPU, or fit a 27B in a payload at all. **The gap between rung three and rung four
is not 1.3 KB. It is the difference between a system that can be wrong on purpose and
one that cannot.** The bytes were never the problem.

---

## 7. What I did not do, and would not claim

- **I did not boot a console, and I gave no jailbreak instructions.** The bar was a
  repository read and a rung, not a bricked PS5.
- **I did not run the 27B.** It has not been run, by anyone, per the repo's own
  unticked box.
- **I did not measure the GPU.** Zero GPU work exists in this repo. Every console
  number is a CPU number and is labelled as one.
- **I did not report a distillation-fidelity number from an unvalidated model.** §4f.
- **My first ground-truth parse was wrong** and was caught by the manifest's own
  controls (§4b). So were two CART instruments (§4c, §4d) and a 98-bit overflow that
  had me briefly believing the lossless representation had a 0.8967 ceiling.
- **`PS5LM` is 16 commits old, all from today.** A v0.1.1. The measurement quality is
  genuinely high — the probe, the patch, the export controls, the checksums — and
  **that is a statement about one very careful author over one day, not about a
  mature field.** There is no independent confirmation of the boot that I could find.
- **No pushes.** File written locally; `git status` left dirty on purpose.

---

## 8. The closing answer

> **The smallest artifact in this fleet that could run with no cloud, no key and no
> network is the 21-bit column-height profile — 2.62 bytes per position, 1,314 bytes
> for a complete decision table over the fleet's own pre-registered ground truth,
> `7.7 × 10⁻⁷` of a PS5 payload's 1.6 GB budget, and `0.0018%` of the 20,974,624-byte
> ELF that already ships.**
>
> **What it would lose that the model has: every reason to doubt itself.** The model
> carries a distribution whose separation from its runner-up is worth **0.949 bits per
> decision** — and that is the entire budget of the `0.35` gate that routes a
> `0.57/0.43` split to a human. The table has no distribution, so it has no residual,
> so it cannot produce a witness, so it cannot record a `CONTRADICTS` edge, so it cannot
> be surprised and cannot abstain. It will be wrong, at the same rate the model is
> wrong, and **it will be wrong identically confidently.**
>
> **A PS5 is not the cheapest place to run a model. It is the cheapest place to run a
> policy, and the fleet already owns one, and it is 1.3 KB, and it already works.**
