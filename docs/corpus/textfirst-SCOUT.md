# SCOUT LANE — the text-first generator pattern, and whether "reverse-actualization" is a mechanism or a story

2026-10-02. Primary sources, all fetched and read. Every URL below was hit in this
session; where a fetch failed I say `UNVERIFIABLE` rather than guessing.

**n_eff and the oracle problem are taken as established** (ORIENTATION §"n_eff ≈ 2"),
not re-derived. I did not re-measure anything.

---

## 0. The two headline findings, before the detail

1. **The three rows in the table are not the same architecture. Row 3 is a
   counterexample, not an instance.** And the counterexample is already in your
   table, miscounted. Two of three rows are real instances of the pattern; the
   MiniMax lane violates the pattern's load-bearing condition. See §1.3.

2. **The crux question has a published answer, and the answer is "one opinion
   seven times."** A 2026 paper measures the nine-judge panel, uses the Kish
   effective sample size, and states — as a robustness check, not a finding — that
   the deficit **survives prompt variation**. Prompt phrasing is not a source of
   independence. And you can measure this **without knowing the answer**, from the
   pairwise agreement matrix alone. See §2.1.

---

## 1. Part A — the text-first pattern

### 1.1 The fourth case that confirms it, and it is three months old

**Qwen-Music**, https://arxiv.org/abs/2607.11699 — and it is the strongest
instance in the table because **it names the components**, which makes the
architecture explicit rather than inferred:

> Qwen-Music comprises three components: **Qwen-Music-Tokenizer**,
> **Qwen-Music-LLM**, and **Qwen-Music-Render**. The tokenizer compresses audio
> into a 25 Hz single-codebook stream of Music Semantic Tokens... The LLM
> performs autoregressive modeling with a **melody-token-based chain-of-thought
> (Melody-CoT)** mechanism that **plans melodies before full-song generation**...
> **The renderer** enriches discrete semantic tokens with acoustic details to
> produce high-fidelity stereo waveforms.

Tokenizer / LLM / **Render**, as three named, separately-replaceable parts. The
symbolic layer (Melody-CoT) is **in the generative path**, not beside it. And
consequence #1 is already load-bearing inside the paper's own metric choice:
their fidelity claim is "reference-melody preservation," a *score-space* claim,
not a *spectrogram* claim.

**StepAudio 3 Music**, https://arxiv.org/abs/2609.16034, is the same architecture
with the notation spelled out:

> a Mixture-of-Experts autoregressive model uses **ABC notation** to produce an
> intermediate arrangement plan (**ABC-CoT**) before predicting music tokens

The score is literal text. The renderer is a VAE decoder. **This is plainsong's
architecture, in production, at a frontier lab, in 2026.** Nobody had to write it
down because the industry has already converged on it.

### 1.2 A fifth case, fifty years older and purer than all of them: chess

Chess is the cleanest instance of the pattern and I do not think it has been
counted. The game is a list of moves in PGN; the board is a renderer; **a game is
adjudicable from the PGN and is not adjudicable from a video of the board.**
That is consequence #1 in its sharpest possible form — a judge operating on the
symbolic layer is not a convenience, it is the *only* layer at which the question
is well-posed.

The generative step is literally a language model over a text serialization:
**The Chess Transformer** (Fraser et al., AAAI 2021),
https://arxiv.org/abs/2008.04057 — GPT-2 fine-tuned on **2.8 million chess games
in Portable Game Notation**, generating plausible openings. And the durable
artifact is the PGN, exactly as claimed: nobody archives the video.

Swappable renderer without retraining: a PGN renders in xboard, in a web board,
in a GIF, in a board-notebook notation. Fifty years, no retraining.

**Chiaroscuro, plainsong, and the chess PGN are the same object.** PGN is to
chess what LilyPond ABC is to music: *a lossless-enough text serialization whose
value is that it is adjudicable.*

### 1.3 The row that breaks it — and it is the MiniMax lane, in your own table

Your table says the MiniMax lane's generative step is **"lyrics + prompt."**
Lyrics and prompt are *natural language*, not a score. The MP3 is therefore **not a
projection of them.** The MP3 is a projection of:

```
(lyrics, prompt, model weights, random seed)
```

The score is not in that tuple. If the model generates audio tokens directly with
no symbolic intermediate — and Qwen-Music and StepAudio both *had to build* one
(Melody-CoT, ABC-CoT) precisely because the audio-token route does not have one —
then **there is no score, and the audio cannot be re-derived from anything durable
in the system.** The durable artifact is a weight file, which is the one thing the
fleet's whole doctrine is against.

**This is the correct reading and it is a real finding, not a nitpick:** the
frontier music labs converged on the text-first pattern *because the alternative
loses the artifact.* The thing that is worth building is the intermediate.

### 1.4 The load-bearing condition, stated once

The pattern is not "there is a score." It is:

> **The symbolic layer must be IN the generative path, and the render must be a
> pure function of `(score, renderer_version)`.**

Qwen-Music's render is deterministic given tokens and weights → `(score,
renderer_version)` **is** the artifact, and "the audio is a projection" is true.
chiaroscuro and plainsong pass. **The MiniMax lane fails** — its generative step
emits audio, not notation, so nothing downstream can recover a score.

Where it fails, the exported notation is a **post-hoc description**: a MIDI file
dumped beside a diffusion model's output. A judge on that notation is judging the
*describer*, not the thing that generated the audio. That is the failure mode the
doctrine has to name, and it is indistinguishable from success unless you check
which one you have.

### 1.5 The correction to point 3, which is the real content

Point 3 as stated — *"the durable artifact is the score; the audio is a
projection"* — is **half true, and the false half is the interesting half.**

Qwen-Music: "The **renderer enriches** discrete semantic tokens **with acoustic
details**." The acoustic details are *not in the tokens*. The score is a **lossy
projection of the audio**, and the audio is a function of the score **and the
renderer.** The information in the audio that is not in the score — all timbre,
all room, all articulation — is **not recoverable from the score.**

So the corrected statement is:

> **The score is the durable artifact of the generative process. The renderer
> version is the durable artifact of the acoustic process. The audio is a
> projection of the *pair*, not of the score.**

And the reason a score-domain judge is a *better* judge is precisely this: it is
a judge operating on the part of the evidence that is **causally upstream** of the
render. That is not a weaker instrument. It is the right one.

### 1.6 Empirical support for consequence #1, in the music lane specifically

**"Aligning Text-to-Music Evaluation with Human Preferences"**,
https://arxiv.org/abs/2503.16669. The state of the art in judging generated
music:

> the standard **FAD** setup is **inconsistent** on both synthetic and human
> preference data, and **nearly all existing metrics fail to effectively capture
> desiderata, and are only weakly correlated with human perception.** … average
> rank correlation **0.84** for their proposed metric vs. **0.49** for FAD, and on
> human preferences **0.62 vs. 0.14**.

**FAD correlates with human preference at ρ = 0.14.** Every audio-domain judge
the field has is close to noise. There is no score-domain judge — the field does
not have one because nobody has the durable score. **This is the strongest
possible empirical statement of consequence #1, and it is also the strongest
possible argument for building the intermediate: you cannot evaluate what you
cannot re-observe.**

### 1.7 Verdict on the pattern

- It is **real, and it is industrial, and it predates all of us** (chess, 50y;
  LilyPond, ~30y; compilers, ~60y).
- The three consequences are **real**, with the qualification in §1.5.
- It is **not** a coincidence of how these three happened to be built: the
  frontier music labs independently arrived at it, and the one lane that did not
  is the one that has no durable artifact.
- The thing that makes it load-bearing is **§1.4**, and the thing that makes it
  lossy is **§1.5**. Both are the same fact: a symbolic layer is a *bottleneck*,
  and that is why you can judge it and why you cannot reconstruct from it.

---

## 2. Part B — "reverse-actualization" as a learning method

Casey's proposal, decomposed into its four components. **It is not one idea. It is
three published ideas plus one component that is measured not to work.** The
novelty is concentrated precisely in the broken component.

### 2.1 Q1 — "crafting questions to flavor the weighting" vs. prompt variation

**The direct primary source is a paper that measures your exact panel.**

**Kohli, "Nine Judges, Two Effective Votes: Correlated Errors Undermine LLM
Evaluation Panels"**, https://arxiv.org/abs/2605.29800 (2026-05-28, 14pp, 5fig,
12tab). This is the 9-judge / 7-family / 3-NLI-dataset / 100-human-annotations
design in ORIENTATION's table, **published**. The number in your orientation doc
is now citable. The relevant sentences:

> We quantify these findings using the **Kish effective sample size (n_eff)** and
> a Condorcet null model, and show **the deficit is robust across prompt
> variants**, temperatures, chain-of-thought reasoning, and a pairwise preference
> task (RewardBench). The bottleneck is **correlated judges, not the aggregation
> algorithm**, implying that **scaling up panels cannot substitute for
> genuinely independent evaluation.**

That is the answer to Q1, stated as a robustness check by someone who had already
found the result: **prompt variants do not buy independence.** And this is the
same conclusion the fleet reached from six directions, now in the primary
literature.

**The mechanism, stated precisely, and it is 1940s statistics not an LLM fact:**

```
n_eff = k / (1 + (k-1)·ρ)          ρ = mean pairwise correlation
```

Sanity-check against the published result: k=9, n_eff=2.18 ⇒ ρ ≈ **0.39**, and
9→2.18 is 75.8% of nominal independence lost, which matches the paper's "roughly
three-quarters" exactly. The formula and the paper are internally consistent.
(ρ=0.39 is **derived by me**, not read off the paper.)

**What seven phrasings are worth:**

| ρ (phrasing correlation) | n_eff at k=7 | reading |
|---|---|---|
| 0.90 | **1.09** | one opinion seven times |
| 0.70 | 1.46 | one opinion seven times |
| 0.50 | 1.75 | one opinion, slightly better resolved |
| 0.39 | 1.99 | one opinion, matching a 9-model panel |
| 0.30 | 2.50 | real but modest gain over no panel |
| 0.20 | 3.18 | meaningful |
| 0.00 | 7.00 | seven opinions |

**Question phrasing only becomes worth anything below ρ ≈ 0.4**, and the honest
prior from the Kohli panel is that a family of LLM judges sits at ρ ≈ 0.4. So the
expected value of "seven phrasings" is **n_eff ≈ 2** — **the same place as
everything else in ORIENTATION's table.** Varying the phrasing is the seventh
thing that lands at n_eff ≈ 2.

**Sclar et al.**, https://arxiv.org/abs/2310.11324 (ICLR 2024), is the reason you
cannot skip this: meaning-preserving *format* changes move accuracy by **up to 76
points** (LLaMA-2-13B), and the effect **survives scaling, more few-shot examples,
and instruction tuning**. Their recommendation is the operational form of the
answer:

> report a **range** of performance across plausible prompt formats, instead of
> the currently-standard practice of reporting performance on a single format.

**A range, not seven votes.** That is the whole correction.

**The decisive distinction, and it is the one to keep:**

> **Reducing the variance of a mean is not the same as increasing the number of
> things measured.**

Seven correlated phrasings give you a *better-estimated single opinion*. This is
real, and it is worth having — but it is **precision**, not **information**, and
it cannot be spent on anything the single opinion could not already buy.

And this is confirmed directly, and counterintuitively. **Liu, "What Is Actually
Being Annotated? Inter-Prompt Reliability"**, https://arxiv.org/abs/2604.16413:

> We further show that **majority voting across prompts significantly improves
> reproducibility and reduces variance.**

Note what that claims: **reproducibility and variance.** Not independence, not
information, not accuracy. The paper measures prompt-variant voting as a
*variance-reduction* technique, and its own conclusion is to report
"distributional stability" — which is a range again, not a count.

### 2.2 Can you tell which without already knowing the answer? — **Yes.**

This is the cleanest result in the lane, and it is worth stating loudly because it
answers the final question directly:

**`n_eff = k/(1+(k-1)ρ)` needs only ρ. And ρ is computable from the k×k pairwise
agreement matrix with NO ground truth at all.** No labels, no human annotation, no
known correct answer. Two judges who agree 90% of the time are highly correlated
regardless of whether they are right.

This is exactly what Liu's IPR framework does — it defines **Inter-Prompt
Reliability** measured by **Pairwise Agreement Rate (PAR) and its
distribution**, "to capture both consistency and stochasticity," and it is
explicitly modelled on **Inter-Rater Reliability**, which has never needed a gold
standard to compute a kappa.

**So the measurement is:**

> Run the same judge under k phrasings over the same items. Compute the pairwise
> agreement matrix. Apply Kish. You now hold `n_eff`, and you held it **without
> knowing the answers.** k=7 phrasings of a judge that returns itself seven times
> gives n_eff ≈ 1.1 and you know it before you look at a single label.

The trap — and it is the trap this lane is most likely to fall into — is
conflating **spread** with **ρ**. A wide spread across phrasings is compatible
with both:

- a **shared systematic bias** (high ρ, everyone swings the same way) — the spread
  is a bias term, and averaging it out helps, and you have learned nothing;
- **genuine independent noise** (low ρ) — the spread is error, and averaging it
  out buys precision on a well-defined target.

**These are indistinguishable by spread alone.** They are trivially distinguishable
by the correlation structure, which requires no labels. If a lane reports "the
answers varied a lot across phrasings, so we have k measurements," it has
reported the one number that cannot distinguish signal from noise, and reported it
as if it could.

### 2.3 Q2 — what exactly is being learned? Three readings, three literatures, three different failure modes

"A vocabulary" is carrying three incompatible loads. Each has a real primary
source and each fails differently. **This is the sharpest thing in the proposal:
you cannot implement "learn a vocabulary" until you pick one, and the pick
determines the failure.**

**(a) A label set — concept bottleneck.** Koh et al., https://arxiv.org/abs/2007.04612.
Predict human-interpretable concepts, then predict the label from the concepts.
Published failure mode: **information leakage**, and it is exactly the failure you
would predict. Sun et al., https://arxiv.org/abs/2402.05945: CBMs "suffer from
information leakage, where unintended information beyond the concepts … are leaked
to the subsequent label prediction. Consequently, **distinct classes are falsely
classified via indistinguishable concepts**, undermining the interpretation and
intervention of CBMs."

> **This is the fleet's own disease in a published paper.** If the bottleneck is
> learned end-to-end, it re-encodes the label, and the decomposition is
> **decorative** — the intermediate layer looks interpretable and carries no
> information the raw input did not already have. *A well-formed, checkable,
> decorative artifact.* Read as: you get a score that diffs, and it means nothing.

**(b) Compositional features — a learned library.** **Latent Programmer** (ICML
2021), https://arxiv.org/abs/2012.00377:

> learn representations of the outputs that are **specifically meant for search**:
> rich enough to specify the desired output but **compact enough to make search
> more efficient** … a program synthesis method that first predicts a **discrete
> latent code** from input/output examples, and **then generates the program in the
> target language** … the discrete latent representation significantly improves
> synthesis accuracy.

This is the *right* reading of "learn a vocabulary," and notice its two halves:
the vocabulary is **discrete** (so the judge can address an element of it by name)
and it is **explicitly built for search** (so the search has a small space). That
is the version of the idea that works.

**(c) A weight-space direction.** **ActAdd / CAA**,
https://arxiv.org/abs/2308.10248: contrast intermediate activations on prompt
pairs to compute a steering vector, add it during the forward pass. "Lightweight:
it does not require any machine optimization and **works with a single pair of
data points**."

This is the cheapest to run and the most likely to be a mirage, because a
difference-of-means direction is a **first-order, single-axis, globally-uniform**
approximation to what is almost certainly a **nonlinear, context-conditional,
many-layered** property. The published failure rate on learned feature
interpretations is the relevant prior — **Gao et al., "Are Sparse Autoencoders
Useful?"**, https://arxiv.org/abs/2502.16681:

> although SAEs occasionally perform better than baselines on individual datasets,
> **we are unable to design ensemble methods combining SAEs with baselines that
> consistently outperform ensemble methods solely using baselines.**

A learned vocabulary that cannot beat the baseline is a **narrative about a
vocabulary**, not a vocabulary. (Note the careful negative result shape: not
"SAEs are useless," which would be an overclaim — "we could not demonstrate
downstream benefit against strong baselines.")

**On the round-trip idea (Duke→Basie→Duke):** it is a good idea and it is not
testing what you want it to test. As constructed it is an **autoencoding /
cycle-consistency** test. Its residual is `decoder loss + geometry of Duke-ness`,
and **you cannot separate them** — a large residual is consistent with "Duke-ness
is diffuse" and with "the decoder is bad," and the instrument does not distinguish
those. That is a *low-resolution* measurement, and it is worse than it looks
because the fleet already has the fact that kills it: **hash-chained receipts and
re-derivation are circular when the re-derivation uses the same components**
(ORIENTATION item 1; the `quilt-jepa` reseal-forgery result). A round trip
through your own encoder and your own decoder is a self-consistency check, not a
geometry measurement.

The published frame that *does* work is **Dai et al., "Emergent World
Representations"** (ICLR 2023 **oral**, notable-top-5%),
https://arxiv.org/abs/2210.13382:

> Although the network has **no a priori knowledge of the game or its rules**, we
> uncover evidence of an **emergent nonlinear internal representation** of the
> board state. **Interventional experiments** indicate this representation can be
> used to **control the output** of the network.

Two things to copy. The representation is **nonlinear** — which is the direct
empirical answer to "(c) is it a weight-space direction?" and it is **no**, not
reliably. And it is established by **intervention**, not by round-trip
reconstruction. Intervene on the state, see the behaviour change, and the
representation is doing causal work. **That is a better Duke test than
Duke→Basie→Duke by a wide margin, and it is already published.**

### 2.4 Q3 — is "tutored by bigger models" signal, or a laundered prior in a second voice?

**Both. And the condition is sharp, and it is checkable before you build anything.**

**The case for "it is a laundered prior":** a bigger model reviewing your
pipeline's logic and data is a **judge in the loop.** The fleet has measured, six
independent ways, that a judge panel is worth about two votes, and the published
Kohli result says the bottleneck is **correlated judges, not the aggregation
algorithm.** Self-Refine (https://arxiv.org/abs/2303.17651) is the pure form —
"the **same LLM** provides feedback for its output" — and it measures real gains
in task performance *without* claiming any independence. Swapping the self for a
bigger model moves you along the same axis the fleet has already measured to be
flat. **If the bigger model's feedback is a judgment, this is the second thing.**

**The case for "it is real signal":** there is a well-known algorithm whose entire
construction is "learn from a better process's evaluation of your outputs," and it
is not a judge. **MuZero**, https://arxiv.org/abs/1911.08265 (Nature 2020,
doi:10.1038/s41586-020-03051-4):

> a tree-based search with a learned model, achieves superhuman performance …
> **without any knowledge of their underlying dynamics.** MuZero learns a model
> that, when applied iteratively, predicts the quantities most directly relevant
> to planning: the reward, the action-selection policy, and the value function.

Search supervises the representation by trial and error, at scale, for thousands
of iterations. This is a real, published, working instance of the proposal's
shape. **But look at what supervises it: the reward, and a terminal game
outcome.** The tutor is not a bigger model *reviewing* anything. The tutor is
**the environment saying win or lose**, which is a measurement, not an opinion.

**So the rule is:**

> **A bigger model is a tutor when its output is an outcome the environment
> checked. A bigger model is a second judge when its output is an opinion about
> aesthetics, structure, or "Duke-ness" — and a second judge is worth n_eff ≈ 2,
> exactly like the first one.**

That is the whole answer, and it is testable *before* you build: **ask what the
tutor's feedback is a measurement OF.** If you cannot name a verifier, you have a
judge.

Applied to a music pipeline specifically, this is sharp and painful. For **"is
this Duke Ellington"** — is there a verifier? A recording of Ellington is
**reference data**, and a model can be scored against it (this is the
reference-based divergence metric line: FAD, and its successor at ρ=0.62 — see
§1.6). That is closer to a measurement than a judgment. But it is *closer*, not
*there*, and the FAD result at ρ=0.14 is the receipt for how far away it is. **The
honest position: in this domain the tutor is not yet a verifier, and anyone
describing it as one is describing a judge.**

Which is why §1.6's finding is the load-bearing one for the whole proposal: **if
you have the score, you can build a verifier** — deterministic, checkable, no
judge. The score does not fix the tutor problem by magic. **It makes the tutor
unnecessary for a large class of checks.** That is the real argument for the
pattern, and it is stronger than the argument I was originally asked to assess.

### 2.5 Q4 — is there a published version?

**Yes, three, and none of them is the proposal. The proposal's novel component is
its broken component.**

| Proposal clause | Published version | Status |
|---|---|---|
| decompose output into a learned symbolic vocabulary | Concept Bottleneck Models (2007.04612); Latent Programmer (2012.00377) | **real, published, works** — with a documented failure mode each |
| trial-and-error, tutored, iteratively | STaR (2203.14465); self-refinement (2303.17651); MuZero (1911.08265) | **real, published, works** |
| verifier guides the search | "Let's Verify Step by Step" (2305.20050) — process supervision beats outcome supervision on MATH, 78% | **real, published, works** |
| **craft questions to flavor the weighting** | — | **measured not to work** (§2.1) |
| **k differently-phrased questions = k views** | — | **measured not to work** (§2.1) |

**"Learning a task vs. learning a language for tasks" — yes, this is a real
distinction, and it has a name and a citation.** The name is **a learned library
of reusable abstractions over which search operates**, and the cleanest statement
is Latent Programmer's (§2.3b): the representation must be "rich enough to
specify the desired output but compact enough to make search more efficient." A
*task* is a point. A *language for tasks* is a **finite, discrete, addressable
basis plus a search procedure over it.** The distinction is real, well-motivated,
and it is exactly the difference between compressing your pipeline and making it
searchable.

**And the closest thing to "reverse-actualization of vocabulary" currently
running in production is Melody-CoT and ABC-CoT** (§1.1) — chain-of-thought in a
symbolic intermediate, before the artifact. Qwen-Music reports the gain plainly:
"**plans melodies before full-song generation**, improving musicality, structural
coherence, and reference-melody preservation." **The idea is not a metaphor. It is
a design that shipped, twice, in 2026, under a different name, and the name is
chain-of-thought in a notation.**

The one thing neither does: learn the notation. Both use a **given** notation
(ABC, melody tokens). Nobody has published a pipeline that *learns the vocabulary
and then reasons in it*, and the reason is probably the leakage result in §2.3a —
a learned intermediate that is trained end-to-end tends to re-encode the output,
and you get a vocabulary-shaped layer that carries no new structure. **The given
notation is doing the work.** That is the honest status: *the reasoning-in-symbols
half is shipped; the learn-the-symbols half is unproven and has a documented
decoy.*

### 2.6 Verdict, in one paragraph

**Not a nice metaphor, and not a mechanism as stated.** The reasoning-in-symbols
half is a real, shipped, published design. The learn-the-vocabulary half is a real
research question with a real, named literature and a documented decoy (leakage).
**The "craft questions to flavor the weighting" half is a nice metaphor, and it is
the part that is measured not to work** — it is the seventh independent route to
n_eff ≈ 2. Strip that clause and the proposal is a good plan. **Leave it in and
the pipeline has a knob that looks like it tunes and does not.**

---

## 3. What I learned that changes what someone else should do

1. **The MiniMax music lane is a counterexample, not an instance. Build the
   score first; the judge problem is downstream of not having one.** Qwen-Music and
   StepAudio both *invented a symbolic intermediate* (Melody-CoT, ABC-CoT) to get
   this. That is the strongest available evidence that the intermediate is the
   point. Everything else in the pattern is downstream of it.

2. **"The durable artifact is the score" is half wrong in an instructive way.**
   The score is lossy; the renderer carries real information the score does not.
   Write the artifact as `(score, renderer_version)`. If you write it as `score`,
   you have silently assumed the renderer is free, and it is not.

3. **Never let a lane report a spread across phrasings as if it were a count.**
   Spread and correlation are different measurements, and only one of them tells
   you whether you have k opinions. This is the specific mistake this proposal
   invites, and it is the fleet's established disease in a new costume: **a
   well-formed, checkable, wrong number.** A lane that reports "7 phrasings gave
   spread 0.31 across 22 claims" has reported the one quantity that cannot
   distinguish signal from noise.

4. **The measurement exists and it needs no oracle.** Kish `n_eff` from the
   pairwise agreement matrix, computable before you know a single label. **This
   should be a standing check on any multi-vote design in this fleet**, including
   the ones already built. The ORIENTATION number is now published and citable
   (arXiv:2605.29800), which means "a panel is worth two votes" stops being a
   local finding and becomes the field's finding.

5. **Ask what the tutor's feedback is a measurement OF, before building the
   pipeline.** Reward/terminal outcome ⇒ tutor, works, publish it. Opinion ⇒
   second judge, n_eff ≈ 2, stop. This is a two-minute check that decides the
   entire architecture.

6. **For "Duke-ness," drop the round-trip and use intervention.** Duke→Basie→Duke
   confounds geometry with decoder loss and cannot separate them. Dai et al.
   (arXiv:2210.13382) established an emergent representation by *intervening* on
   it and watching behaviour change. Same cost, and it measures the causal claim
   the round-trip only pretends to.

7. **Learn the notation from a given one, and check the round-trip residual
   against a baseline that has no vocabulary.** The Gao et al. result
   (arXiv:2502.16681) is the standing disconfirmation: a learned vocabulary that
   cannot beat a strong baseline is a narrative about a vocabulary. **Without
   that control, "reverse-actualization worked" is unfalsifiable.** And per
   ORIENTATION: *a control that cannot fail is worse than no control* — the
   baseline-less learnable-bottleneck is exactly that shape.

8. **The audio-domain judge is ρ≈0.14 with humans. That is the strongest business
   case in the lane.** Nothing in the fleet competes with it, and the fix is
   architectural (get the score) rather than a better model.

---

## UNVERIFIABLE — recorded, not guessed

- **Expert Iteration** (Anthony et al., *Policy Iteration for Exponential
  Approximation of the Value Function*, ICLR 2018) is the canonical citation for
  "a better process supervises a policy." **I could not retrieve a correct arXiv
  ID** (two guesses returned unrelated papers: kilonovae, a Bayesian
  robustness paper; and 1703.01234 is a different paper). **Not cited above.**
  MuZero is cited instead and carries the same argument with a verified DOI.
- **MiniMax's own music architecture** — I did not find a primary source for it.
  The claim in §1.3 is made from **the user's own table** (the generative step is
  "lyrics + prompt") plus the structural contrast with two competitors who *did*
  publish theirs. **I have not read MiniMax's technical report and am not
  claiming its internals.** If MiniMax also emits a symbolic intermediate, §1.3
  inverts and row 3 becomes a fourth confirming instance. **This is the single
  cheapest thing left to check and it decides whether the pattern is 3-for-3 or
  2-for-3.**

---

## The one line

**Asking the same judge seven different ways gives you one opinion seven times —
and yes, we can tell which without already knowing the answer, because Kish
`n_eff = k/(1+(k-1)ρ)` is computable from the pairwise agreement matrix alone, with
no labels at all; but the answer is already published, and it is that phrasing
variation is the seventh road to n_eff ≈ 2.**
