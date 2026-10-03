# res-CLUSTER — Lane 3: how many real things are in a set?

**Date:** 2026-10-02T19:0xZ · **Lane:** 3 of 4 · **Pushes:** none.
**Every number below was executed on this box.** Scripts: `/tmp/l3/`. Where a claim
could not be reproduced, it is marked as such rather than quietly dropped.

---

# VERDICT

**The fleet's code contains ~180 real things — 177 unfiltered, 192 once the known
`recovered-copy-*` pollution is dropped — not 248, not 280, and certainly not 590.
The number is robust; the reasoning that produced the competing numbers tonight is
not.**

More important than the count: **of the 33 multi-member similarity clusters, 29 are
byte-identical copies and 4 are genuinely independent.** Similarity is not the thing
that is wrong in this fleet — **provenance** is. And the one cluster family everyone
was arguing about, the 8 CRDT ports, **does not exist on this disk.**

The single most consequential finding is not a count. It is that **the embedding
never had to be trusted**, because git hashes settle the question the embedding was
being asked to answer, and they disagree with the embedding's picture of *why*.

---

# 1. What `tasnif` actually is, and whether it runs here

Read from source, not README.

**It is a four-stage image pipeline with a pluggable embedder seam:**

```
images → Embedder (PIL.Image → (N,dim) float32) → PCA → KMeans → export/
```

- `src/tasnif/embeddings/base.py` — the entire contract is a `Protocol` with three
  members: `dim`, `device`, `embed(images) -> np.ndarray`. That is the whole
  architecture in one file.
- `src/tasnif/core.py` — the facade. `fit` / `predict` / `fit_predict` / `transform`,
  sklearn-shaped.
- `src/tasnif/clustering.py` — `KMeans(n_init="auto", random_state=42)`, optional
  silhouette (correctly documented as O(N²)).
- `src/tasnif/reduction.py` — PCA, **with `n_components` clamped to
  `min(n_samples, n_features, n_components)` and the clamp logged.** That clamp is
  the single best-engineered line in the repo and it is the thing worth stealing.
- `src/tasnif/embeddings/factory.py` — `register_embedder(name, factory)`; custom
  backends take precedence over built-ins.

**Does it run here? Measured, not assumed. Yes — partially, and usefully.**

```
$ python3 -m pytest tests -q
4 failed, 32 passed, 1 skipped in 1.88s
FAILED tests/test_export.py::test_export_with_grids   - ModuleNotFoundError: matplotlib
FAILED tests/test_visualization.py::test_make_cluster_grid_*  (x3)
```

All 4 failures are a missing plotting dependency. **Not one is a logic failure.**
The reason the suite runs at all without `torch` installed is the design:
`tests/conftest.py:51` defines a `DummyEmbedder` with the same three members as the
`Protocol`, and the tests pass it in. **The vision stack is optional by construction;
the pipeline is not.** That is the correct factoring and it is why this experiment
was possible on 1 CPU / 2 GB RAM / no GPU.

**What cannot run:** the real backbones. `torch>=2.1, torchvision, timm` are hard
dependencies of the default `"timm"` path (`pyproject.toml`), `resnet50` weights are
a separate download, and this box has 1 core, 2 GB RAM and no GPU. I did not attempt
the install to completion and I am not claiming it succeeds.

**And the decisive point: it would not have helped anyway.** `tasnif` clusters
**images**. This fleet's corpus is source code and markdown. `discover_images()` finds
nothing. I ran the pipeline's own logic with a different `Embedder` behind the same
`Protocol` — which is precisely what the seam is for.

## 1b. `cobanov/unlabeled-image-autoencoder` — 7 files, and it does not run either

Four Python files, no README (there is a lowercase `readme.md`). It is a
**MNIST convolutional autoencoder**: `model.py:Autoencoder` (4→8→16 conv encoder,
symmetric decoder), `trainer.py` (10 epochs, Adam 1e-4, MSE), `embedder.py`,
`tsne-calculations.py`.

- **`embedder.py:11` loads `models/model_9.pth`. That file is not in the repo.** The
  repo cannot run as shipped — the checkpoint was never committed.
- **"Unlabeled" is a misnomer.** `trainer.py:8` uses `datasets.MNIST`, which returns
  `(image, label)`; the labels are simply discarded by the autoencoder loss. It is
  supervised data with the supervision thrown away.
- It is the *ancestor idea* — autoencoder latent as embedding — implemented strictly
  worse than `tasnif`, on a dataset that already has labels, with a missing artifact.

**Verdict: nothing to take.** If you want an autoencoder-latent embedder, `tasnif`'s
`Embedder` Protocol is the interface and this repo is not an implementation of it.

---

# 2. The experiment

## 2.1 Parameters — all four, stated before any cluster was inspected

| | |
|---|---|
| **Corpus A (code)** | 248 documents, one per code-bearing repo, from `/workspace/projects/fleet-triage/repos` (280 clones, 248 with source) |
| **Corpus B (prose)** | 125 documents, one per `.md` in `fleet-triage` (1,845 KB) |
| **Model (final)** | code-identifier TF-IDF (`min_df=2`, sublinear, 6,306 features) → **TruncatedSVD k=128** = LSA → L2-normalise |
| **Model (rejected)** | `all-MiniLM-L6-v2` ONNX, 384-d, mean-pool, 512 tokens — §3 |
| **Distance** | **cosine** (= dot product on normalised vectors) |
| **Linkage** | single-linkage connected components; average-linkage reported alongside as a robustness check |
| **Document construction** | per repo: up to 12 files, ≤4 KB each, ≤48 KB total, largest first, comments and string literals stripped, identifiers case-folded, numeric literals → `NUM` |

## 2.2 The threshold, and why I am not giving you one

I refused to pick a threshold by looking at clusters. Instead I calibrated against an
anchor that **shares no machinery with the embedding**: **SHA-256 byte identity of the
embedded text.** The corpus contains **38 byte-identical document pairs** that the
embedding does not know about. Sweeping τ and measuring precision/recall against those
38 is answer-independent.

**The calibration failed in an informative way.** F1 rises *monotonically to the top of
the sweep in both models* — it never peaks. Byte-identity is a floor, not a threshold:
any τ below 1.0 accumulates false positives against a target that is only 38 pairs out
of 30,676. **So the number of clusters is a function of τ and I report the function.**

| τ | 0.50 | 0.60 | 0.70 | 0.80 | 0.90 | 0.95 | 0.97 | **0.99** |
|---|---|---|---|---|---|---|---|---|
| clusters (of 248) | 4 | 44 | 141 | 182 | 201 | 203 | 203 | **206** |

## 2.3 The two instruments agree, which is the actual validation

The decisive check: run a **second method that never touches the embedding** — build a
graph over repos joined when they share **≥1 byte-identical source file** (git blob
hash, path-independent) — and collapse connected components.

```
248 code-bearing repos
 all 41 byte-sharing components      -> 71 repos collapse -> 177 distinct code bodies
 minus the 13 recovered-copy-* pairs -> 56 repos collapse -> 192 distinct code bodies
```

**Two numbers, and the difference is a stated exclusion, not a rounding.**

- **177** is the raw count of distinct code bodies on disk. The 13 `recovered-copy-*`
  repos *are* byte-identical checkouts (identical `HEAD^{tree}`), so collapsing them is
  correct and 177 is the honest unfiltered figure.
- **192** is the same graph with the known recovery pollution removed — i.e. what the
  fleet would count once `recovered-copy-*` is filtered, which is what `cluster.py`
  already does.

**177–192 by bytes. 183–206 by embedding across the whole τ range.** A method that uses
no embedding and a method that uses only an embedding land on the same interval. That
agreement is worth more than either number alone, and it is the reason I am willing to
state the range at all.

---

# 3. The negative that shaped the method: MiniLM cannot read code

The account reached for a modern pretrained embedder. I tried it first, properly.

| | mean pairwise cos | best F1 vs byte-identity | precision at best |
|---|---|---|---|
| `all-MiniLM-L6-v2` (natural language) | **0.309** | 0.784 @ τ=0.95 | 0.644 |
| LSA-128 over code tokens | **0.158** | **0.826** @ τ=0.99 | **0.704** |

Recall was 1.000 at *every* threshold for both — the encoder never once missed a true
duplicate. But at τ=0.50 MiniLM flags **2,838 pairs of which 2,800 are false**. Mean
cosine 0.309 means **every Python file looks like every other Python file** to a model
trained on English prose.

**This is a general finding, not a local one: a general-purpose sentence encoder is
not a code-similarity instrument, and using one silently turns "these repos are the
same" into "these repos are all made of code."** The prior `cluster.py` in this repo
clustered on *description text*, which has the same failure one level up.

## 3.1 Threshold sensitivity — the answer to "if the number is sensitive, report the sensitivity"

| τ | clusters | multi-member | **COPY** | PART-COPY | **INDEPENDENT** |
|---|---|---|---|---|---|
| 0.90 | 183 | 38 | **29** | 2 | 7 |
| 0.95 | 189 | 36 | **28** | 2 | 6 |
| 0.97 | 196 | 37 | **30** | 1 | 6 |
| 0.99 | 206 | 33 | **29** | 0 | 4 |

**The cluster count swings 183→206 — a 12% spread, threshold-dependent, not a
measurement. The COPY count does not move: 29, 28, 30, 29.** The decision is
threshold-invariant; the count is not. Report the range, act on the invariant.

---

# 4. The clusters, named, and what each one is

At τ=0.99, the 33 multi-member clusters. Named by the tokens that actually drive the
similarity, not by the directory.

### Class COPY — every pair shares a byte-identical file (29 clusters)

| shared shape | n | members |
|---|---|---|
| **MIDI event codec, Rust** (`u8/i8/wrapping_sub/base`) | 4 | `fleet-midi-{collab,cycle,feed,live}` |
| **MIDI decode/encode/filter/blend** (`func/last/append/base/process`) | 4 | `fleet-midi-{blend,decode,encode,filter}` |
| **MIDI generative engine, Python** (`func/last/append/stats/sum`) | 3 | `fleet-midi-{mapper,pattern,script}` |
| **MIDI drone/genetic/grammar/swarm** (`println/int/func/last`) | 4 | `fleet-midi-{drone,genetic,grammar,swarm}` |
| **Canon loader + `__main__` + `canary.py`** | 6 | `quilt-canon-{book,feed,game,keywords,mcp,witness}` |
| **Substrate JS test harness** (`test.js`) | 6 | `substrate-{bundle,delegate,membership,merger,traverse,withdraw}` |
| **Dojo agents** | 4 | `dojo-{alchemist,builder,scout,scribe}` |
| **Same repo, two names** | 5 pairs | `lau-error-correcting-codes`=`ecc-rs`, `lau-dynamical-systems`=`dynamical-systems`, `lau-ergodic-theory`=`ergodic-theory`, `lau-logic-foundations`=`logic-foundations`, `lau-renormalization`=`renormalization` |
| **Rename-duplicate suffix** | 3 pairs | `quilt-jev-toolkit{,-push}`, `quilt-quantumaudio-demo{,-push}`, `peanut-gallery{,-npm}` |
| **Topic rename** | 4 pairs | `Tripartite1`=`synesis`, `knowledge-graph`=`si-knowledge-base`, `polychora`=`polychora-temporal`, `flux-reasoner`=`flux-reasoner-engine` |
| **Recovery copies** | 13 pairs | `recovered-copy-20260824-*` — **byte-identical whole checkout, identical tree hash** |

### Class INDEPENDENT — no shared blob between any pair (4 clusters)

| shared shape | n | members |
|---|---|---|
| Static marketing pages | 3 | `dmlog-ai-pages`, `personallog-ai-pages`, `playerlog-ai-pages` |
| Chat UI pages | 2 | `cocapn-com-pages`, `deckboss-net-pages` |
| Landing page | 2 | `superinstance-ai`, `recovered-copy-…-superinstance-ai` |
| **CRDT ports** | 2 | `substrate-revoke`, `substrate-withdraw` |

## 4.1 THE ANSWER TO "insurance or one bug copied N times"

**It is overwhelmingly one bug copied N times, and the byte hash says so without
interpretation.**

- **29 of 33** multi-member clusters: every pair shares a byte-identical file.
- **13** are byte-identical *whole checkouts* — same `HEAD^{tree}` hash. The
  `recovered-copy-*` family. These are not near-copies; they are the same tree.
- **The `lau-*` family: 5 of them are the same repository under a second name.**
  These are not even ports. They are the same commit wearing a different name, and
  any count that treats `lau-ergodic-theory` and `ergodic-theory` as two independent
  implementations of ergodic theory is wrong by construction.
- **0 clusters were PART-COPY-only.** Stripping comments and string literals added just
  **14** shared blobs on top of 448 exact ones (462 vs 448). **The duplication is
  byte-level, not "same code, different prose."** These are copies, not forks that
  drifted.

**The only genuine insurance in the entire corpus is `substrate-revoke` /
`substrate-withdraw`** — two CRDT ports that share no blob and nonetheless cluster
together on meaning. That is what redundancy that is worth having looks like, and
there is **one pair of it in 248 repos.**

### 4.2 The three circulating claims, checked

**"8 CRDT ports, 5 byte-identical below the type" — the premise is void.**
`org2/bare/` holds **590 repositories, and every single one is a bare repo cloned with
`partialclonefilter = tree:0`.** Not one has any file content on this disk.

```
$ git -C org2/bare/crdt-orset ls-tree -r --name-only HEAD
.github/workflows/ci.yml … src/lib.rs  src/main.rs  tests/canary.rs      (10 entries)
$ git clone --no-local org2/bare/crdt-orset co_test
remote: warning: lazy fetching disabled; some objects may not be available
fatal: could not fetch 2814e3e6… from promisor remote
   aborting due to possible repository corruption on the remote side
   → 0 files obtained
```

The five `crdt-{gcounter,gset,lwwreg,orset,pnvector}` each show **54 files / 193 KB** —
and every one of those 54 is `.git` plumbing: `HEAD`, `config`, `description`, 14
`hooks/*.sample`, `info/exclude`. `description` and `info/exclude` are byte-identical
across all five (`a0a7c3ff`, `036208b4`); `config` differs in exactly one line, the
URL. **"Byte-identical below the type" is a `git init` template, not a CRDT finding.**
There is no code there to compare. The real CRDT artifacts are the 7 files in
`crdt-canary/`, and those are **all 7 distinct** (7 different MD5s, 43–110 lines each),
each asserting its own merge law.

**"12 `substrate-*` repos that are near-copies" — understates it.** 11 exist with
content (not 12). **6 of 11 share a byte-identical `test.js`**; 4 more share a second
byte-identical file. Not near-copies. And `substrate-revoke`/`substrate-withdraw` are
the exception that proves the family is not uniformly cloned.

**"23 workflows, 18 the same echo placeholder" — does not reproduce at corpus scale.**
Measured: **209 workflow files, 126 distinct contents, 106 files in 16 shared blobs**,
largest shared blob in **46** repos (it is `axum`'s upstream `ci.yml` — a vendored
crate, not fleet work). Only **10** files have a bare `run: echo`/`true`. I am not
asserting the 23/18 figure is wrong; the original scope is not recorded anywhere I
could find, and I decline to guess at it.

---

# 5. The free-text corpus: 125 reports, and the embedding cannot answer the question

Same pipeline, MiniLM used as-is (natural language is its home turf). Anchor changed,
because there are **zero** byte-identical pairs to calibrate against: I used **5-gram
shingle Jaccard over the raw text** — an independent detector sharing no machinery with
the encoder.

```
n=125   mean shingle-Jaccard = 0.001   max = 0.900
anchor near-dup pairs (J≥0.60) = 3
τ* = 0.85, F1 = 0.500, P = 0.400, R = 0.667
120 clusters, 4 multi-member, 116 singletons
```

**Three findings, and the second is the important one.**

1. **The corpus contains almost no duplication to find.** Mean pairwise Jaccard
   **0.001** — these 125 documents are lexically nearly disjoint. Whatever the fleet
   report corpus is, it is not 125 copies of one report.

2. **Cosine similarity cannot find a contradiction, and this is structural, not a
   tuning failure.** The orchestrator flagged "at least two places where two documents
   assert opposite things." Two documents that assert opposite things are, by
   definition, **maximally similar** — same vocabulary, same domain, same claim
   structure, opposite sign. They will cluster *together*, tighter than almost any
   other pair. **Asking whether a set contains contradictory ideas by clustering it is
   asking the wrong question.** Contradiction detection needs paired claim extraction
   and an entailment check, not a distance threshold. The 2 clusters with internal
   Jaccard of **0.00** and **0.01** (`BOARD`/`syn-HARNESS`, `nextgen-BUILD`/
   `nextgen-git`) are the symptom: MiniLM clustered on *register*, not content. Two
   documents sharing literally zero 5-grams landed in one cluster.

3. **Mean pairwise cosine 0.537 is a measurement of authorial voice, not of idea.**
   This corpus is one author writing in one idiom for two months. Any embedding of it
   will find the author. **The free-text question — "how many independent ideas does
   this corpus contain?" — is not answerable by this method, and I am not going to
   produce a number for it.** 125 lexically distinct documents is what I can defend.

---

# 6. `grid-table`: no. And here is the sharper reason.

A native Emacs table system. 44 files: 11 core `.el` modules, 4 format plugins
(csv/markdown/org/rst), a chart module with 9 plot types, 5 `ert-deftest` files, and a
776-line formula engine with Excel-style `SUM`/`IF`/`VLOOKUP`/`IFS` and an
`=elisp:(cell"A1")` escape hatch.

**The domain is wrong** — you are not building a table editor — and the orchestrator's
instinct was right. But the reason to reject it is better than "wrong domain," and it
is a direct lesson for this lane:

### The dependency graph that is declared and never built

```elisp
;; grid-data-model.el:15
(defconst grid-cell--dependencies 3)
;; grid-data-model.el:19
(defconst grid-cell--dependents 7) ; New slot for dependency graph
```

The slots are allocated in the constructor. **They are never written and never read
anywhere in the repository.** The only other hit for "dependency" in 44 files is a
section header:

```elisp
;;; grid-data-model.el:263
;;; Dependency Graph & Recalculation

(defun grid-model-recalculate-all (model)
  "Recalculate all formula cells in the model by simple iteration.
   This is inefficient but guaranteed to terminate. Includes a circuit breaker."
  (let* ((cells-vec (grid-data-model-cells model))
         (total-cells (length cells-vec))
         (max-iterations (* total-cells 2))) ; Circuit breaker: max iterations = 2 * total cells
    (dotimes (i total-cells) (push (aref cells-vec i) cell-list))
    …))
```

`max-iterations` is **computed and never used.** There is no iteration, no fixpoint, no
topological sort. The real entry point, `grid-table-calc-evaluate` (`grid-table-calc.el:9`),
walks cells in array order once. A formula in row 10 reading a formula in row 20 is
evaluated against a **stale value**, silently. The five test files contain **zero**
forward-reference cases — I grepped for `=[A-Z]+[0-9]+` in `test/*.el` and got nothing.

**So: a function called `recalculate-all`, under a header reading "Dependency Graph",
with a circuit breaker that never fires, guarding slots nothing populates, validated
by tests that never exercise the case the graph would exist to handle.**

That is the same defect class as the reseal-forgery finding in this fleet: **the
receipt describes the mechanism rather than constituting it.** A name in the right place
is not an implementation. `grid-table` is a working demonstration of the failure mode,
which makes it a genuinely useful thing to have read — and nothing to steal. The one
mechanically reusable line in the whole repo is `tasnif`'s PCA clamp, already noted.

---

# 7. What this method cannot do

- **Embedding similarity is not duplication.** It ranked every Python file near every
  other (§3). A model that has not seen code cannot see code.
- **A threshold chosen after seeing the answer is not a measurement.** I refused to
  pick one, calibrated against byte-hashes instead, and reported the sweep when the
  calibration came back with no interior optimum (§2.2).
- **Similarity cannot distinguish insurance from a copy.** Only provenance can, and
  provenance is not similarity. Every COPY/INDEPENDENT verdict in §4 is a git-hash
  fact, not an embedding opinion. The embedding chose *what to look at*; git decided
  *what was true*.
- **Byte-sharing over-detects in one direction and under-detects in the other.** It
  will call two files that share a vendored `LICENSE` a copy, and it will call two
  independently-written implementations of the same interface unrelated. I filtered
  `__init__.py`/license/hook templates by hand for that reason (a naive run scores 45
  repos as duplicates on a 2-line SPDX header alone).
- **Cluster count is threshold-dependent. Do not quote a single number.** Quote the
  183–206 range and the invariant 29.
- **All local clones are depth-1.** There is no local git history, so "written
  independently" is inferred from blob disjointness, not from commit ancestry. The
  strong version of this experiment needs real clones.
- **One corpus, one author, one moment.** §5's voice/idea collapse is a property of
  this corpus, not of embeddings in general.

---

# 8. The two answers

## How many real things are in this fleet?

| view | n | note |
|---|---|---|
| Repos on disk under `repos/` | 280 | |
| …with actual source | **248** | 32 are empty or metadata-only |
| …under `org2/bare/` | **590** | **all `tree:0`, all zero content — not countable** |
| **Real things (code)** | **177–192** | byte-collapse, raw / recovery-filtered; embedding agrees at 183–206 |
| **Real things (reports)** | **125** | mean pairwise Jaccard 0.001; no duplication found |
| Fleet census on GitHub | 5,113 | unchanged by this work; untested here |

**The honest answer is a range, and it is wide because the corpus is not what it was
assumed to be: 177–192 real code bodies, and 590 repositories that are indistinguishable
from empty.** If you had counted `org2/bare/` as 590 implementations, you would have
been wrong by 590.

**The corpus does not support the `n_eff ≈ 2` constant being tested here.** That
constant came from panels of judges, where members are *designed* to be independent and
the finding is that they aren't. Here, independence was never designed in — repos were
generated from shared scaffolds — so a small `n_eff` is a fact about the **generator**,
not about the ideas. **Comparing this number to 2 would be a category error, and I am
declining to make it.** What transfers is the *method*: fix the corpus, state the
model, calibrate against something the model cannot see, and report the sensitivity.

## Which clusters are insurance, and which are one bug copied N times?

| | count | what to do |
|---|---|---|
| **One bug copied N times** | **29 of 33** multi-member clusters | Delete or re-derive. No review value. |
| — of which byte-identical *checkouts* | 13 | `recovered-copy-*` — pure noise, already known |
| — of which the same repo under two names | 5 `lau-*` pairs | **Fix the census, not the code.** These are phantom implementations. |
| — of which scaffold clones with a real API each | 11 (`fleet-midi-*`, `substrate-*`, `quilt-canon-*`, `dojo-*`) | One implementation + N thin wrappers, or delete N−1 |
| **Genuine redundancy (insurance)** | **4 clusters, and effectively 1 useful pair** | `substrate-revoke` + `substrate-withdraw` |
| **Not measurable — no content** | 590 `org2/bare` repos | Re-clone without `--filter=tree:0` before saying anything about them |

**The second half is the one that changes what we do next, so I will be blunt:**

**The fleet does not have a redundancy problem. It has a generator problem, and the
embedding was measuring the generator.** Twenty-nine of thirty-three similarity
clusters are the *same bytes under different names*, which means the last two days of
"how many real things are there" were answered by looking at a naming axis and calling
it an implementation axis. The two things worth acting on are neither of them
clustering:

1. **`org2/bare/` is 590 empty shells.** Any count, census, or score that reads that
   directory is reading nothing. This is the largest single defect found in this lane
   and it is not a clustering finding — it is a measurement-validity finding.
2. **Similarity is the wrong first question for this fleet.** Provenance answered
   every question the embedding was recruited for, faster, exactly, and with no
   threshold to argue about. The `tasnif` pipeline is a fine pipeline, and the honest
   conclusion is that **the embedder was the optional part all along.**

---

*Reproduce: `/tmp/l3/build_corpus.py` → `embed.py` (MiniLM arm) → `lsa_run.py` (LSA arm) →
`provenance.py` → `synth.py` (TAU env) → `prose.py`. No pushes were made.*
