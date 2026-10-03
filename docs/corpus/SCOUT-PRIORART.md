# SCOUT — Prior Art for the F1/F2 Variance-Collapse Thesis

**Scout session:** 447560205152451 · **Date:** 2026-10-01 · **Lane:** wide internet + fleet
**Target:** `/workspace/projects/fleet-triage/docs/F1-F2-DIFFUSION.md` (read, not modified)
**Status:** nothing pushed.

---

## 0. VERIFICATION INFRASTRUCTURE — read this before you trust any citation, mine included

### 0.1 The four sentences that matter most in this report

1. **`export.arxiv.org` API is DEAD from this sandbox, and it fails in the most dangerous possible way.** It returns **HTTP 200 with a completely empty body** for *every* query — including `id_list=1706.03762` (Attention Is All You Need), which certainly exists. An agent that queries the API, gets an empty `<entry>` list, and concludes "no record" will **falsely declare every paper fabricated.** I hit this and had to control-test it before trusting it. **Always resolve citations via `https://arxiv.org/abs/<id>`, not the API.**

2. **arXiv here is authentic. The 26xx.\* range is real.** I resolved 14 distinct 26xx IDs through `arxiv.org/abs/`. Twelve return real papers with plausible 2026 titles. The 404/200 pattern tracks real sequence-number occupancy exactly (`2513.99999`→404, `2601.30000`→404, `2609.20000/24000/26000`→200). **An index is not manufacturing 26xx citations.**

3. **Two circulating 26xx IDs are fabricated:** `2610.00001` and `2609.50000`, both 404. Both are round numbers, and both are *impossible on their face* — October 2026 has no submissions yet (today is 2026-10-01), and no month reaches sequence 50000. **The tell is the round number, not the prefix.** This is exactly the fabrication signature to police for.

4. **I shipped a bad citation and caught it.** I asserted from memory that the Fruit Fly Optimization Algorithm original was `10.1016/j.engappai.2012.07.005`. Crossref says that DOI is *"Hidden Markov model-based classification of heart valve disease with PCA for dimension reduction"* (Saraçoğlu, Eng. Appl. AI 25:1523–1528). **I was wrong.** See §5.3 — the Mirjalili 2013 FFOA paper is marked UNVERIFIED and must not be cited until someone resolves its DOI.

### 0.2 The 26xx audit, spot-checked against how the fleet actually uses them

| ID | Fleet claims it is… | Real title (fetched from `arxiv.org/abs/`) | Verdict |
|---|---|---|---|
| `2605.08442` (32 uses) | memory-poisoning / persistent-memory-attack defense in the witness-log | *Injection-Execution Dissociation: A Mechanistic Evaluation of Persistent Memory Attacks and Defenses in Stateful LLM Agents* | **HONEST** |
| `2607.22000` (14 uses) | "Music-JEPA (Wang, Fang, LeCun) — action-conditioned world model for music" | *Music-JEPA: Learning a World Model of Sound from Action* | **HONEST** |
| `2608.05248` (12 uses) | WorldClaw (per its own README badge) | *WorldClaw: Agentic 3D Open-World Generation at Scale* | **HONEST** |
| `2607.14537` (10) | MIDI-RAE-JEPA | *MIDI-RAE-JEPA: Hierarchical Representation Learning and Generation for Symbolic Music* | **HONEST** |
| `2607.21653` (9) | agentic RL training framework | *Molt: A Scalable PyTorch-Native Training Framework for Agentic Reinforcement Learning* | **HONEST** |
| `2606.10968` (6) | trust-region RL | *Beyond Uniform Token-Level Trust Region in LLM Reinforcement Learning* | **HONEST** |
| `2610.00001` (2) | — | **404** | **FABRICATED** |
| `2609.50000` (2) | — | **404** | **FABRICATED** |

**Conclusion for the fleet: the citation culture is sound.** The only bad IDs are the two round-number placeholders. No manufacturing.

---

## 1. Direction 1 — F1 uniformity in population / quantitative genetics

### 1.1 The F1 uniform state is a *named law*, and its limits are already published
**Levites, "Limitation of F1 hybrids uniformity law", Nature Precedings, 2011.** DOI `10.1038/npre.2011.6734.1` · 0 citations. — **VERIFIED** (Crossref: title, author, journal, date all match).

The whole F1-hybrid-seed industry is built on the F1 being uniform; a 2024 instantiation is McDonald, *"F1 Hybrid Seed Can Enhance Cannabis Crop Uniformity and Yield"*, HortScience, DOI `10.21273/hortsci18197-24` — **VERIFIED** (OpenAlex).

> **Leaves your claim alone, and legitimises its premise.** You are not proposing something exotic; you are importing a load-bearing 1911-vintage law and pointing out that nobody in the FL literature has noticed what it implies.

### 1.2 What breaks the collapse? **Dominance and epistasis do not — the standard account says they are small.**
**Hill, Sorando & Weir (2010), "Data and Theory Point to Mainly Additive Genetic Variance for Complex Traits", *PLoS Genetics* 6(5):e1000008.** DOI `10.1371/journal.pgen.1000008` · **1,134 citations** · **VERIFIED, full abstract quoted from the OpenAlex inverted index:**

> *"…we evaluate the evidence from empirical studies of genetic variance components and find that additive variance typically accounts for over half, and often close to 100%, of the total genetic variance… interactions at the level of genes are not likely to generate much interaction at the level of variance."*

> ### 🔴 **"The collapse is prevented by dominance and everyone knew that" is FALSE. The opposite is the finding.**
> Under the empirically dominant additive model, **F1 *is* uniform.** Your dominance/epistasis worry is the *weak* path. This is the strongest single result in the report: it moves you from "conceivably right" to "right about the physically common case."

### 1.3 The halving is a 50-year-old named result — **the Bulmer effect**
**Bulmer (1971), "The Effect of Selection on Genetic Variability", *The American Naturalist* 85(403).** DOI `10.1086/282718` · **771 citations** — **METADATA VERIFIED** (Crossref). **⚠️ TEXT UNVERIFIED** — `journals.uchicago.edu` returned **HTTP 403 (Cloudflare)**; I could not open the paper.

Quoted instead from an open-access secondary source I *did* open — *PLoS Genetics* (2026), PMC12991805, DOI `10.1371/journal.pgen.1012035`:

> *"stabilizing selection rapidly generates negative correlations — linkage disequilibria (LD) — between alleles with the same directional effect on the trait [7] (**this has come to be known as the 'Bulmer effect'**)."*

and the load-bearing nuance:

> *"…allowing the rarer allele at each locus to be maintained at a higher mutation–selection balance in expectation, thus **indirectly increasing** … the variance contributed by polymorphism at individual loci (the 'genic variance')."*

> **Weakens the novelty of the arithmetic, sharpens the mechanism.** A one-generation halving under averaging/selection is textbook. **But note the nuance that protects you: the Bulmer effect does not *destroy* variance — it *redistributes* it from genic variance into LD (gametic-phase) variance.** Your information-destruction framing survives this; the genetics version is a *transfer to covariances*, not a loss. If you want a real adversary, this is it.

### 1.4 The specific arithmetic `Var_n = Var_0 · 2^(−n)` **under crossing** is yours
The Bulmer halving is under **truncation selection**, not under **crossing two maximally-distant lines**. I found no source stating the geometric collapse for the cross itself.

> **Supports the claim.** The F1-collapse-then-segregate *structure* is textbook; the `2^(−n)` derivation for the deterministic mixture, and the deterministic-vs-stochastic operator distinction, are not.

### 1.5 Direction-1 verdict
**Supports, with one carve-out.** The F1 state is real and standard; the additive-dominance literature confirms it is approximately uniform in practice; the halving is known under selection; the *crossing* derivation and the *operator-kind* claim are unclaimed.

---

## 2. Direction 2 — Variance collapse in federated / distributed learning  ⭐ HIGHEST VALUE

### 2.1 🔴 **"Here is the paper that names your phenomenon, in your literature, with your word."**
**Tian, Al-Ars, Kitsak & Hofstee (2024), "Vanishing Variance Problem in Fully Decentralized Neural-Network Systems", arXiv:2404.04616** (6 Apr 2024). — **VERIFIED, full abstract quoted from `arxiv.org/abs/2404.04616`:**

> *"Both methodologies involve a critical step: computing a representation of received ML models and integrating this representation into the existing model. Conventionally, this representation is derived by **averaging** the received models, exemplified by the FedAVG algorithm. Our findings suggest that this averaging approach inherently introduces a potential delay in model convergence. **We identify the underlying cause and refer to it as the 'vanishing variance' problem, where averaging across uncorrelated ML models undermines the optimal variance established by the Xavier weight initialization.**"*

**OpenAlex `cited_by_count` = 0.** It is an arXiv preprint, two years old, with zero citations in OpenAlex's index.

> **This is the most important finding in the report, and it cuts both ways.**
> - **WEAKENS:** the *observation* is not new. It is named — **"vanishing variance"** — in the federated/gossip literature, and the words "averaging across uncorrelated models" are almost verbatim your `Var((p+q)/2)` argument.
> - **STRENGTHENS, sharply, on everything that matters:** Tian et al. frame it as an **optimisation** defect (it breaks Xavier-init variance → delays convergence) and fix it by **rescaling the average back up** — re-injecting variance *deterministically, by a factor*. You frame it as **information destruction** and propose re-injecting variance *structurally, by switching the operator from deterministic averaging to stochastic recombination, held at σ²/2k*. **Same phenomenon, different physics, different fix, and a zero-citation preprint nobody built on.**

### 2.2 The canonical treatment frames heterogeneity as **convergence speed**, never as information loss
**SCAFFOLD — Karimireddy et al., arXiv:1910.06378** · **709 citations** — **VERIFIED, quoted:**

> *"We obtain tight convergence rates for FedAvg and prove that it suffers from `client-drift' when the data is heterogeneous (non-iid), resulting in **unstable and slow convergence**. As a solution, we propose a new algorithm (SCAFFOLD) which uses **control variates (variance reduction)** to correct for the `client-drift'…"*

(FedAvg itself — McMahan et al., arXiv:1602.05629, **5,115 citations** — **VERIFIED**.)

I ran eight targeted searches across arXiv (abstract + title fields) and OpenAlex. **Every single paper frames non-IID heterogeneity as slow convergence, client drift, or statistical inefficiency. Not one frames it as loss of private information.**

> **Supports the gap, strongly.** SCAFFOLD even reaches for the word "variance" and means *gradient* variance. The concept-space your thesis occupies is empty.

### 2.3 The mean-field machinery has **not** been applied to this question
OpenAlex `title.search:"mean field federated learning"` → **15 works total.** The largest, Mehrjou et al., *"Federated Learning as a Mean-Field Game"* (arXiv:2107.03770, DOI `10.48550/arxiv.2107.03770`), has **1 citation** — and it is game-theoretic control, not variance theory.

> **Supports the gap.** The exact analytical tool your equation needs has a populated FL subfield that has never once asked your question. This is the cheapest possible opening.

### 2.4 🔴 The statistical claim needs one repair before you publish it
My own derivation, offered as a correction — **flagged UNVERIFIED against a primary source**:
> The sample mean is a **sufficient statistic for the common location θ\*** — Fisher information satisfies `I(θ*; ȳ) = I(θ*; x)` — but is **ancillary for the deviations e_i**.

Consequence: **averaging destroys *zero* information about θ\*, and *all* information about the e_i.**

> **Weakens the rhetorical force, hard.** "Two federations with different private knowledge produce bit-identical averages" is, as stated, very close to tautological — it is just saying a function isn't injective. It becomes a real result only when you name the parameter class: *the mean is sufficient for the consensus and ancillary for the private parts, so a federation that keeps only the consensus has formally conditioned away exactly the quantity that made its members distinct.* **Make that move explicitly or a reviewer will dismiss §4 of your document as trivial.**

### 2.5 No paper uses **F1/F2 genetic language** for federated learning
Searched arXiv (title + abstract) and OpenAlex for FL × crossover / recombination / genetic-algorithm. The only substantial hit is Zhu et al. (2019), *"Multi-Objective Evolutionary Federated Learning"*, **IEEE TNNLS**, DOI `10.1109/tnnls.2019.2919699`, **312 citations** — **VERIFIED**, abstract read. It applies evolutionary multi-objective search to **network architecture**, not to preserving participant diversity. It is a different use of the same word.

> **Supports the gap.** The genetic vocabulary is genuinely unused in FL. This is the cheapest possible novelty claim you can make, and it is true.

### 2.6 Direction-2 verdict
**Your phenomenon is named and published. Your framing, your operator distinction, and your fix are not.** The gap is not "nobody noticed" — it is "one zero-citation preprint noticed the symptom and prescribed a rescaling factor, and the field moved on."

---

## 3. Direction 3 — Stochasticity that is not noise

### 3.1 🔴 **σ²/2k is mutation–selection balance, and the constant is literally 2μ/S**
**de Vladar & Barton (2014), "Stability and response of polygenic traits to stabilizing selection and mutation", *Genetics* 204(2), June 2014.** DOI `10.1534/genetics.113.159111` · 83 citations · arXiv:1404.1017 — **VERIFIED, quoted from the arXiv abstract:**

> *"the genetic variance that is maintained by **mutation-selection balance** is $2\mu/S$ per locus, where $\mu$ is the mutation rate and $S$ the strength of stabilizing selection."*

and the threshold:

> *"…a sharp transition: alleles with effects smaller than a threshold value of $2\sqrt{\mu/S}$ remain polymorphic, whereas those with larger effects are fixed."*

Substitute **σ² ↔ 2μ** and **k ↔ S** and your stationary-variance equation **is** the standard mutation–selection equilibrium.

> **Weakens the novelty of the knob, hard — and this is the second of the four high-value sentences:**
> **"The equilibrium variance σ²/2k is a 50-year-old textbook result under the name mutation–selection balance, and the factor of 2 is the same factor of 2."**
> The knob is real, the closed form is right, and it is standard. **What is unclaimed is the transfer** — reinterpreting it as a *federated design parameter* chosen by an operator rather than a population-genetic constant fixed by mutation biology.

### 3.2 The structure is live and being extended
**Jain & Stephan (2015), "Response of Polygenic Traits Under Stabilizing Selection and Mutation When Loci Have Unequal Effects", *G3* 5(6).** DOI `10.1534/g3.115.017970` · 45 citations — **VERIFIED** (Crossref). **Leaves the claim alone** but confirms the equilibrium-variance-vs-selection-strength framing is an active research line, so your `σ²/2k` will be recognised instantly by the right reader.

### 3.3 The variance is redistributed, not destroyed — even here
Same Bulmer-effect mechanism as §1.3. **Weakens the "destruction" reading in the genetic framing specifically**; the σξ term in *your* system is external noise, so your own framing is unaffected. Worth stating explicitly so the two literatures do not get conflated.

### 3.4 "Genetic algorithms run for maintained diversity" — the F2 reading — is thinly served
The nearest substantial work is the evolutionary-FL line (§2.5, Zhu et al.) and the Fruit Fly Optimization Algorithm (§5.1). **Neither treats the population as a diversity-maintaining object with an equilibrium variance.** → **Supports the gap.**

### 3.5 Adjacent only
**Ragsdale (2025), "Mean fitness is maximized in small populations under stabilizing selection on highly polygenic traits", bioRxiv** DOI `10.1101/2025.11.17.688329`, 0 citations — **VERIFIED** (metadata). **Leaves the claim alone**; not about variance equilibrium.

### 3.6 Direction-3 verdict
**Weakens the novelty of the equation, supports the novelty of the transplant.** Say "mutation–selection balance" in your document and cite de Vladar & Barton — it converts a possible reviewer objection ("this is just an OU process") into a demonstrated command of the literature.

---

## 4. Direction 4 — Discontinuous / quantum updates vs. the averaging attractor

### 4.1 🔴 **The direction is empty as a literature — and the claim is decidable by a theorem you can state tonight.**
**No paper found that shows a discontinuous operator lacks the averaging fixed point.** I searched arXiv (title + abstract) for quantum annealing × spectral gap (8 results — all about gap-closing and scheduling, none about fixed points), projected/projection dynamics, discontinuous maps, and contraction vs. isometry framing. **All returned nothing on the fixed-point question.**

**But the answer is one line of functional analysis, and it is favourable to you:**
> Averaging is a **projection**: idempotent, non-expansive, norm-decreasing. A **unitary is an isometry**: `‖Uψ‖ = ‖ψ‖` exactly. **Therefore no unitary evolution can reduce L2 norm, and so cannot produce a variance collapse of the F1 kind.** The F1 collapse is a theorem about *contractions*; unitaries are not contractions.

> ### This is the third high-value sentence: **your load-bearing falsification test has a positive answer available analytically, before you spend a GPU-hour on it.**
> Your §7 "The last row is the load-bearing one and it is cheap to test" — the test is cheaper than a GPU-hour. It is a proof. **Do the experiment anyway** (a real measurement is still worth more than the argument), but you now know which way it will fall and you can pre-register the reason.

**⚠️ UNVERIFIED:** I am stating the contraction/isometry fact from analysis, not from a fetched citation. It is elementary and I hold it confidently, but per the citation rule it is marked as such. **Get a source before it goes in a published document.**

### 4.2 Quantum annealing is not where this lives
Eight arXiv results on annealing × spectral gap; the closest (*"Bounding first-order quantum phase transitions in adiabatic quantum computing"*, arXiv:2301.13861) is about gap scaling, not about escaping an averaging attractor. **Leaves your claim alone.**

### 4.3 The real conceptual neighbour is decoherence — and it is about *redundancy*, not *loss*
Adjacent literature, **VERIFIED** (titles via `arxiv.org/search`, abstracts not opened in full):
- **"Quantum Theory of the Classical: Quantum Jumps, Born's Rule, and Objective Classical Reality via Quantum Darwinism"** — arXiv:1807.02092
- **"Environment as a Witness: Selective Proliferation of Information and Emergence of Objectivity in a Quantum Universe"** (einselection; no arXiv ID parsed)

> **ADJACENT, NOT PRIOR ART.** Quantum Darwinism is decoherence-as-*redundancy* — how the environment proliferates copies of pointer information. Your claim is decoherence-as-*destruction* — the private phase information `e_i` that averaging conditions away. **They are opposite readings of the same physics, which makes this a much better citation than a rival: you can position your thesis as the Darwinism result inverted.** Worth an explicit paragraph.

### 4.4 Direction-4 verdict
**A well-evidenced gap.** Nothing to cite against you; a theorem to cite in your favour; one adjacent literature to position against.

---

## 5. Direction 5 — "Fruit-fly decomposition"

### 5.1 🔴 **"Fruit fly" in computing overwhelmingly means a metaheuristic**
**FFOA — the Fruit Fly Optimization Algorithm.** OpenAlex `title.search:"fruit fly optimization algorithm"` → **577 works.**

**Anchor (VERIFIED, Crossref):** Pan, Wen-Tsao (single author), *"A new Fruit Fly Optimization Algorithm: Taking the financial distress model as an example"*, **Knowledge-Based Systems 26:69–74 (Feb 2012)**, DOI `10.1016/j.knosys.2011.07.001`, **1,379 citations**. *(OpenAlex reports this same DOI as 2011 / vol. 24 — metadata conflict between the two registries; the Crossref record is authoritative for the DOI.)*

**On-theme, incidentally:** FFOA is a *population-based stochastic optimizer* whose members are moved by an attractor-search rather than averaged — the same instinct as your F2. If you want a citable algorithm that maintains a dispersed population, this is one.

### 5.2 🔴 **"Fruit fly … decomposition" as a literal phrase means a signal-processing pipeline**
The dominant real-world collocation is **FFOA + Variational Mode Decomposition (VMD)**. **VERIFIED example:** Ren, Chaofan et al. (2022), *"Coal–Rock Cutting Sound Denoising Based on Complete Ensemble Empirical Mode Decomposition with Adaptive Noise and an improved Fruit Fly Optimization Algorithm"*, **Machines**, DOI `10.3390/machines10060412` — a denoising paper. Europe PMC and S2 both return this family first for the phrase.

> ### 🔴 **Fourth high-value sentence: "the term 'fruit-fly decomposition' means FFOA-tuned Variational Mode Decomposition in the engineering literature, and it is not what you think."**
> It denotes a *signal-decomposition pipeline whose hyperparameters are tuned by a metaheuristic*. **It has nothing to do with decomposing a behaviour into contributing factors.** If the phrase reached you as a serious research programme, it was either garbled or a local coinage.

### 5.3 ⚠️ The Mirjalili 2013 FFOA paper is **UNVERIFIED** — do not cite it
I could not resolve it in Crossref by title or by author. **And the DOI I reached for from memory (`10.1016/j.engappai.2012.07.005`) is a *different paper entirely*** — Saraçoğlu, *"Hidden Markov model-based classification of heart valve disease with PCA for dimension reduction"*, Eng. Appl. AI 25:1523–1528. **Caught by checking. Would have shipped if I had not.** Use Pan (2012) as the anchor instead; it is verified and has 1,379 citations.

### 5.4 The Drosophila-genetics meaning is real, but **"fruit-fly decomposition" is not its term**
The standard names for "decompose a phenotype into separable genetic contributions" are:
- **Generation means analysis** — the Mather/Griffiths procedure splitting a trait into additive + dominance + epistasis components. Ex. Mackay, Anstey, et al. (2024), *"Pleiotropy, epistasis and the genetic architecture of quantitative traits"*, **Nat. Rev. Genet.**, DOI `10.1038/s41576-024-00711-3`, 124 citations — **VERIFIED**.
- **Variance-component partitioning** — Vitezica et al. (2017), *"Orthogonal Estimates of Variances for Additive, Dominance, and Epistatic Effects in Populations"*, **Genetics**, DOI `10.1534/genetics.116.199406`, 207 citations — **VERIFIED**.

**Leaves the Drosophila reading alone: the work exists, the phrase is not how anyone says it.**

### 5.5 🔴 **The fleet contains nothing under this name**
`grep -rliE "fruit.?fly|fruitfly|drosophila"` across `/workspace/projects` (excluding `node_modules`): **0 files, 0 matches.** It is not a lost internal term. Combined with §5.2, the most likely reading is that the phrase is **FFOA+VMD noise that surfaced during a literature scan**, or a local coinage with no referent.

### 5.6 What "decompose a complex behaviour into separable factors and reconstruct it" is actually called
Four unrelated names, no umbrella: **generation means analysis** / **variance-component partitioning** (genetics) · **factor analysis** / **structural equation modelling** (psychology) · **main-effects-plus-interactions decomposition** (statistics) · **eigenvalue decomposition of the covariance matrix** (linear algebra — literally, decomposing the second-moment tensor). **No single name spans these, and "fruit-fly decomposition" is not it.**

> **Direction-5 verdict: the term names a body of work you do not want. Report it and move on.**

---

## 6. Ranked by what would change what you build

| # | Finding | Effect on the build |
|---|---|---|
| **1** | **Tian et al. 2024 — "vanishing variance"** (arXiv:2404.04616, 0 citations). Your phenomenon is *named and published*; the framing and the fix are not. | **Do not open your paper with "I noticed averaging destroys variance."** Open with the information-destruction framing and cite Tian as the near-miss. Also: **cite it, and state plainly why their rescaling fix is not yours.** |
| **2** | **Hill et al. 2010** — additive variance is "often close to 100%", gene-level interaction does "not generate much interaction at the level of variance." | **Delete the dominance/epistasis worry from your falsification table.** It is answered, and the answer is that the F1 state is approximately real. This is a *strengthening*, and it is free. |
| **3** | **de Vladar & Barton 2014 — 2μ/S mutation–selection balance.** | **Name your equation.** `σ²/2k` *is* mutation–selection balance. Citing it converts "this is just an OU process" into "I know it is, and here is the population-genetic name for my knob." |
| **4** | **The contraction/isometry argument** (isometries cannot reduce variance). | **Your load-bearing falsification test has an analytic answer, tonight, for free.** Write the proof *before* the experiment. |
| **5** | **Sufficiency correction**: the mean is sufficient for θ\*, ancillary for the e_i. | **Required edit to §4.** Without it, "bit-identical averages" reads as tautology. With it, it is a precise statement about conditioning away the random effects. |
| **6** | **Zero papers use F1/F2 language for FL; zero-citation preprint on the exact phenomenon.** | **Your cheapest defensible novelty claim, and it is true.** Lead the contribution section with it. |
| **7** | **Bulmer effect** — 771 citations, halving under selection, but variance is *redistributed into LD*, not destroyed. | **Cite it as an ally and pre-empt the strongest objection.** The genetics literature's own collapse is not a destruction. Distinguish your σξ (external, no information) from theirs (genetic, redistributed). |
| **8** | **"Fruit-fly decomposition" = FFOA + VMD.** Fleet has zero occurrences. | **Drop the term.** If it names a research programme you were handed, that programme does not exist under that name. |
| **9** | **`export.arxiv.org` API is silently empty; two fabricated 26xx IDs are circulating.** | **Fix your tooling before anyone else burns an hour on it.** Pollice round-number 26xx IDs. |

---

## 7. What I would change in `F1-F2-DIFFUSION.md`

1. **§7 falsification table** — strike the dominance/epistasis row. Hill et al. 2010 answers it: additivity dominates, so the uniform state is approximately real. Replace with the LD-redistribution counterweight (Bulmer).
2. **§3** — add one line: *"This stationary variance is the population-genetic mutation–selection balance; see de Vladar & Barton 2014."* Costs nothing, buys the reader's trust.
3. **§4** — restate the information claim in sufficiency language. It is the difference between a theorem and an observation.
4. **§0** — add Tian et al. 2024 as the paper that named "vanishing variance" two years ago and got zero citations. The gap is real; say so with a citation.
5. **§6, quantum discontinuity** — the analytic argument is available now. Add it as a pre-registered prediction *before* running the test.
6. **§8** — "Whether this is already named somewhere" is now answered: **yes, "vanishing variance," once, in a preprint nobody cited; and "mutation–selection balance," extensively, for the steady state.** Neither claims the F1/F2 operator distinction.

---

## Appendix — full citation ledger

| Ref | Verification | How |
|---|---|---|
| Tian et al. 2024, arXiv:2404.04616 | ✅ **VERIFIED** (full abstract) | `arxiv.org/abs/` |
| Karimireddy et al., SCAFFOLD, arXiv:1910.06378 | ✅ **VERIFIED** (abstract) | OpenAlex DOI |
| McMahan et al., FedAvg, arXiv:1602.05629 | ✅ **VERIFIED** (abstract) | OpenAlex DOI |
| Hill, Sorando & Weir 2010, `10.1371/journal.pgen.1000008` | ✅ **VERIFIED** (full abstract) | OpenAlex DOI |
| Bulmer 1971, `10.1086/282718` | ⚠️ **METADATA ONLY** — 403 Cloudflare | Crossref |
| Bulmer effect definition | ✅ **VERIFIED** (quoted) | *PLoS Genet.* `10.1371/journal.pgen.1012035`, PMC12991805 |
| Levites 2011, `10.1038/npre.2011.6734.1` | ✅ **VERIFIED** (metadata) | Crossref |
| McDonald 2024, `10.21273/hortsci18197-24` | ✅ **VERIFIED** (metadata) | OpenAlex |
| de Vladar & Barton 2014, `10.1534/genetics.113.159111` | ✅ **VERIFIED** (full abstract) | arXiv:1404.1017 + Crossref |
| Jain & Stephan 2015, `10.1534/g3.115.017970` | ✅ **VERIFIED** (metadata) | Crossref |
| Zhu et al. 2019, `10.1109/tnnls.2019.2919699` | ✅ **VERIFIED** (abstract) | OpenAlex DOI |
| Pan 2012, FFOA, `10.1016/j.knosys.2011.07.001` | ✅ **VERIFIED** (Crossref) | Crossref DOI |
| Ren et al. 2022, FFOA+VMD, `10.3390/machines10060412` | ✅ **VERIFIED** (via S2) | Semantic Scholar |
| Mackay et al. 2024, `10.1038/s41576-024-00711-3` | ✅ **VERIFIED** (metadata) | OpenAlex |
| Vitezica et al. 2017, `10.1534/genetics.116.199406` | ✅ **VERIFIED** (metadata) | OpenAlex |
| Ragsdale 2025, `10.1101/2025.11.17.688329` | ✅ **VERIFIED** (metadata) | Crossref |
| arXiv:1807.02092 (Quantum Darwinism) | ✅ **VERIFIED** (title) | `arxiv.org/search` |
| **Mirjalili et al. 2013, FFOA** | ❌ **UNVERIFIED — DO NOT CITE** | not resolvable in Crossref |
| **"Discontinuous operators lack the averaging fixed point"** | ❌ **NO SOURCE FOUND** — claim stated as my own analysis | — |
| **Sufficiency/ancillarity for θ\* vs e_i** | ⚠️ **MY OWN DERIVATION** — true but needs a stats citation | — |
| `10.1016/j.engappai.2012.07.005` | ❌ **NOT FFOA** — heart-valve HMM paper; my memory was wrong | Crossref |
| `2610.00001`, `2609.50000` | ❌ **404 — FABRICATED** | `arxiv.org/abs/` |

**Tooling left in place** (not part of the deliverable, reusable): `scouttools/ax2.py` (arXiv title/abstract search), `srch.py` (arXiv + OpenAlex), `doi.py` (exact DOI → title/abstract/citations), `title.py` (OpenAlex title search), `s2.py` (Semantic Scholar with 429 backoff).
