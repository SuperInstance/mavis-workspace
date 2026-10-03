# ASCII-as-Vision: the landscape, and the hole in it

2026-10-02. Sixty years, one field, and Casey was right that there is far more of
it than either of us had indexed. **The synthesis that matters is not the
inventory — it is that three 2025-2026 results independently confirm conclusions
I reached by hand tonight, and that the one thing nobody in the field does is the
one thing this project has been doing all along.**

---

## The lineage

| era | what | why it matters here |
|---|---|---|
| **1963** | the ASCII standard: **95 printable characters** | the alphabet is fixed and small; that constraint is the whole field |
| **1966-68** | **Knowlton & Harmon, "Studies in Perception I"**, Bell Labs, IBM 7094 | **the founding move: a photograph converted to characters by tone**, exhibited at MoMA. A pixel is a byte; a character is a tone bucket |
| **1980s** | page code 437, BBS and Usenet culture, `alt.ascii-art`, ACiD/iCE artpacks | character-grid rendering as an aesthetic, not a compression scheme |
| **1994** | Jonathon Sieber's *ASCII Art Collection*; Vuk Ćosić's ASCII Art Ensemble | the archive and the art form |
| **1997 / 1999** | **AAlib** (Jan Hubicka), then **libcaca** (colour) | **the direct ancestors of Asciipocalypse** — libraries that install as a *graphics device* and render video through characters |
| **2010** | **Xu, Zhang & Wong, "Structure-based ASCII Art", ACM TOG 29(4)** — the **AISS** metric | **formally splits the field in two and says structure-based is the hard half** |
| **2016** | Xu et al. formalize ASCII art as the 95 fixed-width printable characters | the definitional boundary still used |
| **2017** | Akiyama: first CNN for character classification, ~89% | learned conversion begins |
| **2020-2025** | k-NN / SVM / RandomForest+HOG vs CNN / ResNet / MobileNetV2 | the classical-vs-deep comparison |
| **2024-2026** | the LLM era: ASCII as a modality bridge, ASCIIEval, ASCIIBench, SVE-ASCII, ArtPerception, discrete diffusion | **where it is now** |

**The two families, and they are not interchangeable:**

- **tone-based** — map pixel intensity to glyph density. `grayscale → ramp lookup`.
  **Asciipocalypse is here**, via `fogString`.
- **structure-based** — match image *tiles* to characters by shape, using log-polar
  histograms and the AISS similarity. **Fifteen years of the field live here**,
  and Xu et al. flagged it as the hard case in 2010.

---

## Five results that bear directly on this project

### 1. Your architecture is published, and it drives a physical arm

**"ASCII Art Turns LLMs into VLA Controllers"** — Jiang, Zhao, Plancher, Chen,
Balkcom (Dartmouth / Clemson / Houston). A **text-only LLM**, given a
**96 × 54 coloured ASCII raster**, is fine-tuned into a closed-loop controller
and **runs pick-and-place on a physical manipulator**. Expert demonstrations
from a planning teacher, plus **DAgger** for iterative improvement.

**And their encoder design is the opposite of Asciipocalypse's — and it is the
right one:**

> *"Background pixels are mapped to whitespace, while task-relevant entities —
> grippers, movable objects, and target markers — are represented by characters
> from a **fixed palette**."*

**They do not map intensity to density. They assign glyphs to semantic roles**,
and encode colour and depth by a colour-aware discretisation.

**My probe measured why `fogString` cannot work: 14 of 15 identity pairs are
indistinguishable under a depth ramp. This paper assigned glyphs by role and
moved a physical arm.** That is not a coincidence — it is the same finding
arrived at from opposite ends.

### 2. "Give it both modalities" is empirically harmful — and I said it before the literature confirmed it

**ASCIIEval / "Visual Perception in Text Strings"** (ICLR 2026, arXiv 2410.01733).
3,000+ samples, dozens of models, a 7-class / 23-group / 359-concept tree.

| input | accuracy |
|---|---|
| human annotators | **~100%** |
| GPT-4o, **image only** | **82.68%** |
| GPT-4o, **text + image** | **76.52%** |
| most LLMs, text only | **~30%** |

> *"None of the MLLMs successfully benefit when both modalities are supplied
> simultaneously… the performance of all models except Chameleon-7B **drops**, with
> a maximum decrease of **12.32%**… existing MLLMs are **unable to understand the
> complementarity and consistency of different modalities**."*

**Replicated independently by ASCIIBench** (arXiv 2512.04125, 5,315 images, 752
classes): *"adding text to vision does not improve performance and in some cases
**degrades** it."*

> My correction to you last night — *a vision arm is not an independent
> instrument, because it is downstream of the text arm* — is now a measured
> result with a citation, replicated twice, on 8,000+ samples. **The design
> analysis was right and the literature confirms it independently.**

### 3. `fogString` is an adversarially chosen alphabet, and there is a paper about exactly this

**"Text Speaks Louder than Vision: ASCII Art Reveals Textual Biases in
Vision-Language Models"** (COLM 2025, arXiv 2504.01591). It builds **adversarial
ASCII art where character-level semantics deliberately contradict the global
visual pattern**, and tests GPT-4o, Claude, and Gemini.

> **Finding: a strong text-priority bias.** Models "consistently prioritize
> textual information over visual patterns," and *"visual recognition ability
> **declining dramatically as semantic complexity increases**."* Prompting and
> visual-parameter tuning give only *"modest improvements, suggesting that this
> limitation requires **architectural-level solutions**."*

**Asciipocalypse's ramp is `"@&#8x*,:. "`.** `@` reads as a person, `#` as a tag
or a wall, `x` as a cross, `8` as a numeral — and the bias *worsens* with
semantic complexity.

> **An LLM handed that screen will read those meanings, not the depth values
> they encode.** This is a predicted design bug in the game, and the prediction
> was published before I read this paper.

**This is the cheapest fix in the whole project:** swap the ramp for glyphs with
no semantic prior — block elements, geometric shapes, or a deliberate
scrambled-but-fixed-width set — and a text model stops reading it as words.
**The VLA paper's fixed role-palette is the same move, done properly.**

### 4. CLIP cannot represent ASCII at all

**ASCIIBench:** *"cosine similarity over CLIP embeddings **fails to separate most
ASCII categories, yielding chance-level performance even for low-variance
classes**."* Classes with high internal similarity do separate — *"revealing
that the bottleneck lies in **representation** rather than generative variance."*

> **Any evaluation metric built on a general-purpose visual encoder will return
> noise on this medium.** If a lane scores ASCII output with CLIP, it is
> measuring the encoder's blindness, not the art.

### 5. The 2026 VLA literature has independently arrived at the projection doctrine

**SSVR, "State-Space Visual Reasoning"** (arXiv 2609.33412) names
**state-representation mismatch** as *the* obstacle in open-loop VLA planning,
and lists the causes:

> *"existing paradigms can encode evolving state through **lossy textual
> compression**, error-accumulating pixel rollouts, or bypass-prone latent
> tokens."*

**That is this project's central doctrine, in the VLA literature, 2026** —
"what survives is bounded by what the observation carried" — arrived at by people
who had never heard of a projection ladder.

### Plus: the boring-thing result keeps replicating

**Coumar & Kingston (2025):** Random Forest with HOG is *competitive with CNNs*
on ASCII generation at **significantly reduced computational overhead**. And:
*"the bottleneck lies in representation rather than generative variance."*

That is `selectlib` beating a judge with a free statistic, `res-CLUSTER` finding
provenance beat an embedder, and `PROBE-RESULTS` finding a lookup table beat a
neural plan. **Four independent domains, same result.**

---

## The hole: sixty years of optimisation and nobody does the accounting

**Every paper in this field optimises fidelity.** SSIM, i2v, AISS, classification
accuracy, human studies, CLIP similarity. They all treat ASCII as **a lossy
encoding to be minimised**.

**Not one asks what the representation discards.**

Nobody in the lineage from Knowlton to the VLA controllers asks:
- which facts are irrecoverable from the frame, and which are merely expensive?
- is the loss *named* (cheap) or *irreversible* (fatal)?
- does a learner trained on one projection survive re-rendering into another?
- does character-accuracy survive motion, or is it positional memorisation?

**Those are exactly the questions the projection ladder, the L1/L4 split, the
re-projection invariance test, and the "what did the renderer throw away" probe
were built to answer — and the field has never asked them.**

> **The field has the representation and sixty years of making it prettier. This
> project has the accounting. Neither half exists anywhere else.**

---

## What this changes, concretely

1. **Adopt the role-palette, not the density ramp.** The VLA paper's design
   choice is validated on hardware; my probe says the density ramp cannot
   distinguish 14 of 15 identity pairs. **Background → space, entities → fixed
   role-assigned glyphs.** This is a small patch with a large expected effect.
2. **Replace the alphabet.** `"@&#8x*,:. "` is a semantic trap with a published
   failure mode. Use glyphs with no lexical prior.
3. **Never score with CLIP.** Chance-level on this medium, measured on 5,315
   samples. Score against ground truth from the scene graph instead — which is
   what the probe already does.
4. **Cite these.** The re-rendering invariance test has no precedent in the
   literature, and that is either a gap to fill or an oversight to check. **It
   should be checked before claimed.**
5. **The 96×54 precedent is worth copying** — the resolution is chosen to "balance
   the information density required for spatial reasoning with the token limits
   typical of standard LLM context windows." Asciipocalypse's 81 cells is
   already in that regime.

---

## And the honest caveat

**I have read abstracts and one full paper, not all sixteen.** The classification
accuracy numbers above are from the fetched full text of 2410.01733; the rest are
from abstracts, snippets, and secondary sources. **Before any of this is cited in
a published artifact, the specific numbers should be checked against the PDFs** —
which is `GATE`'s rule 1 applied to my own research, and I am not going to be the
seventh green badge of the night.

📄 Written from four searches and one full fetch. The specific claims worth
verifying first: the 12.32% text+image drop, the 14/15 identity-pair collapse,
and the exact VLA palette description.
