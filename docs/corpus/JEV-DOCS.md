# JEV-DOCS — 22 published patterns, 5 templates, and the one that should have been found first

**Lane:** documentation. **Date:** 2026-10-02. **Branch:** `jev-docs` in `fleet-triage`.
**Model:** `jev-latest` → resolves to `jev-1.13.0`. Every number in this document was produced
by a live call against the rolled key on 2026-10-02. Nothing here is quoted from the docs'
own example outputs, and nothing is a mock.

> Standard useful applications should merely need to be **tailored** to a user or developer as
> they nest or embed our technology in theirs. Not built.

Everything between the `▸▸▸ TAILOR ▸▸▸` marks in `templates/` is the tailoring surface.
Everything else in those files is fixed and should be copied verbatim. The credential is
`$TYPESAFEAI_KEY`; the variable **name** appears in this document, the value appears nowhere,
not in a log, not in a repr, not in an error path.

---

## 0. Read this first: three contract corrections

I hit all three of these in the first ten minutes. They are recorded because the fleet has
already lost time to at least two of them.

**0.1 — A noul has no `confidence` field.** The working contract in the brief reads
`→ {choice, confidence, probabilities}`. That is true for `choice` and `score`. For `noul` the
response is:

```json
{"type": "noul", "noul": 0.95}
```

That is the entire answer. The probability *is* the answer; there is no second number to
collide with it. If you need to gate nouls and choices with the same code, use the
documented distance-from-0.5 equivalent, `confidence = |2p − 1|`, which is the Choice formula
applied to a two-option question and therefore already on the same scale.

**0.2 — `confidence` is not the argmax probability.** This was already found and written down
in `JEV-CONTRACT.md` (`grey .74 → confidence 0.61`). It is worth re-stating because the
formula makes it unarguable. For a Choice with `n` options and top probability `p_max`:

```
confidence = (p_max − 1/n) / (1 − 1/n)
```

Normalised against an even split. It rises to 1.0 only when *all* the mass is on one option.
`p_max = 0.40` is confidence 0.33 across three options and 0.20 across ten — the same number,
two very different situations. `argmax` is a claim about the world; `confidence` is a claim
about the model. You need both, and a threshold on one is not a threshold on the other.

**0.3 — a Score's `probabilities` are keyed by level INDEX, not by your level text.** The
labels come back separately in `legend`:

```json
{"type": "score", "score": 0.87, "confidence": 0.0,
 "legend": {"0": "unclear", "1": "clear", "2": "unambiguous"},
 "probabilities": {"0": 0.49, "1": 0.14, "2": 0.37}}
```

Two live consequences, both of which will bite:

* `answer["probabilities"][my_level_label]` raises `KeyError`. I hit this.
* **`score` is an interpolated number that can point the opposite way from the distribution
  it came from.** In the payload above, `score` is 0.87 — which reads as "fairly unambiguous"
  — while the argmax level is `0` ("unclear"), and `confidence` is **0.00**, because the mass
  is split between the two *ends* of the scale, which the ordered-level formula punishes
  hardest. This is the sharpest possible illustration of the distribution rule: a collapsed
  panel here does not merely lose information, it **inverts the sign of the finding**. Never
  gate on a Score's `score` field. Gate on the level distribution.

---

## 1. The mapping table, verified row by row

The brief proposed seven rows. I checked each against the published text and against what is
actually in this workspace, and added the thirteen that are untried. **Verdict column:**
`TRUE` = the fleet reinvented a documented pattern; `STRETCH` = adjacent, the documented
pattern solves a strictly different problem; `UNTRIED` = no fleet artefact found, and the
last column is where the value is.

| # | published pattern / cookbook | what the fleet built by hand | verdict | why / what the published version gives you that the hand-rolled one does not |
|---|---|---|---|---|
| 1 | **Double-checking citations** — *"catch wrong or hallucinated citations by checking against the source"* | **the resolver** — 4,789 `FILE_MISSING` | **TRUE, and it is a half-implementation** | The resolver proves a *path* does not exist. The cookbook also checks the case the resolver structurally cannot see: a quote that resolves **and is verbatim present** while its context says the opposite of the claim. 4,789 is a count of absent paths, not of false claims. `dangling-TRIAGE.md` already says this in its own words — "4,791 `FILE_MISSING` is not the most valuable thing in this lane. It is approximately the least." |
| 2 | **Intent routing** | the cattle/steward layer | **STRETCH** | The fleet's layer is a *role and reputation* model (gatekeeper.py: agent reputation deltas, scoring, tile confidence with injected noise). The documented pattern is a single closed-set classify-and-dispatch, and it is a much smaller and more auditable object than a reputation ledger. Not a reimplementation — a genuinely simpler alternative that may beat it on cases where reputation is a proxy for something the question can answer directly. |
| 3 | **Confidence-gated routing** — *"the answer tells you WHAT; confidence tells you whether to trust it"* | the two-axis min-aggregated gate | **TRUE** | Documented, with the arithmetic and the three-band behaviour already specified. See §2.3 for what we got that the pattern does not give: an explicit entropy budget. |
| 4 | **Composite scoring** | the 2-axis gate, arrived at independently | **TRUE** | Same object. The pattern page also states *why* weights live in code, and warns against interpolating magnitudes out of score levels — which §0.3 shows is not merely a warning. |
| 5 | **Skill suggestion** — pick at most one skill for a turn, out of 182 | agent routing | **TRUE, under-used** | The fleet routes agents but does not, as far as I can find, carry a scored `none`. See §3 finding **F3** — I shipped that bug myself before fixing it. |
| 6 | **Classifying RAG passages** | the dangling-reference triage | **STRETCH** | The triage ranks unresolved paths by likely value. The cookbook scores *retrieved context* for usefulness before it reaches a generator. Different object: the triage has nothing to retrieve from, it has defects to rank. Related in that both are "score a pile, cut in code", not in mechanism. |
| 7 | **Self-consistency: nouls / choices** | the `noul`-gated canon promotions, measured as **vagueness detection, not falsity** | **TRUE — and the fleet's finding is the interesting part** | The cookbook's actual mechanism is to keep the underlying noul values visible while routing on uncertainty. The fleet rediscovered the shape by hitting a real limit. §2.6 shows both, and shows what the extra column does and does not buy. |
| 8 | **Function calling** | ? | **UNTRIED** | NL → typed calls with closed-set arguments, each argument a confidence-aware question. The fleet has `quilt-jev-toolkit` and a lot of hand-parsed CLI-ish dispatch. Nothing found that maps NL to a typed signature with per-argument confidence. |
| 9 | **Knowledge graph entity alignment** | ? | **UNTRIED, and there is a direct match sitting unused** | One Score plus three companion Nouls that surface *which fields disagree*. The fleet has an entity-merge problem across 477 repos and duplicated readmes (`code_dups.json`, `neardups.json`, `dups.json`, `pairs.json`, `clusters.json` all exist). This is a documented, scored solution to a problem the fleet is solving with pairwise similarity. |
| 10 | **Structure recovery** | ? | **UNTRIED** | Reconstructs Markdown from wrapped plain text in two requests. The fleet touches wrapped text constantly and has no tool for it. Cheap. |
| 11 | **SDE cascade** | ? | **UNTRIED** | 2-stage structured-data-extraction, mini → verify → reasoning. Most of a big model's quality at a fraction of the cost. Directly applicable to the fleet's report/ledger scraping. |
| 12 | **Guardrails** | ? | **UNTRIED** | One request screening both directions of an LLM app, thresholding hazard × severity to pass / review / block / route. The fleet has `llm_guardrails`-shaped *policy* scattered across CANARY-FICTION, GRACEFUL-FAIL, failopen audits — and `sprint-FAILOPEN.md` reads like a real fail-open bug. A single two-axis cell is the documented answer. |
| 13 | **Parallel questions** (13-question briefing, 12.2× cheaper, 10.0× faster) | implicit everywhere | **UNTRIED as a *measured* claim** | The fleet batches constantly but I found no artefact that measures the batch-vs-serial difference on its own workload. T2 below measures it on ours. |
| 14 | **Re-ranking** (30-passage BM25 → top-1 5%→18%, top-10 38%→62%) | ? | **UNTRIED** | Candidate generation in code, scoring in the model. Note the absolute numbers are low — this is a re-ranker on top of recall, not a search replacement. |
| 15 | **Line-by-line search** (218 line ids in one request) | ? | **UNTRIED** | One Choice scores many line ids at once. The fleet's `code_dups.json` / neardup work is the same shape. |
| 16 | **Date extraction** | ? | **UNTRIED** | Extract parts as a Choice over enumerated sets, resolve and compare in code. The fleet has date-bearing evidence everywhere and hand-parses it. |
| 17 | **Pre-parsed value extraction** | ? | **UNTRIED** | Regex finds candidates, the model *selects* the requested span, code normalises. Keeps the value verbatim so normalisation cannot corrupt it. |
| 18 | **Hierarchical classification** (deep taxonomies, parallel beam search over Choice probabilities) | ? | **UNTRIED** | The fleet's 62-cluster `classify62.py` is a flat top-1 label. This is the documented way to do a hierarchy with beam search, and it falls out when the top level is not confident enough to commit. |
| 19 | **Classification using confidence** (75 SEC industries; fall back to the broader division) | ? | **UNTRIED** | The elegant one: commit to the leaf only when confident, otherwise report the parent. A label hierarchy you already have, with a confidence-derived fallback. Cheap to adopt on `classify62.py`. |
| 20 | **Speculative fan-out** | ? | **UNTRIED** | Ask the speculative questions too, let code decide which mattered. The opposite of asking only what you expect. |
| 21 | **Autoresearch feature discovery** | ? | **UNTRIED** | Proposes questions, turns text into features, fits a supervised regressor, improves it from model errors. A meta-loop. Probably the wrong tool for this fleet and I would want a strong argument before anyone spends time here. |
| 22 | **Self-consistency: choices** | — | **PARTIAL** | Compares label agreement against the share of automatic actions. The fleet measures agreement a lot and the *action rate* almost nowhere, so the comparison that the cookbook is actually built around is unavailable. |

### 1.1 Which rows are true, which are a stretch

**True (5):** citation check (partial), confidence-gated routing, composite scoring, skill
suggestion, noul self-consistency.

**Stretch (2):** intent routing — the fleet's layer is a reputation model, not a classifier;
RAG passage classification — the triage ranks defects, the cookbook scores retrieved context.

**The other fifteen** are simply not in the fleet. Of those, four are the ones I would argue
against building on: autoresearch feature discovery (a meta-loop, wrong tool here), SDE
cascade (assumes you have a cheap tier to cascade from), re-ranking (the published absolute
numbers are 18% top-1 — it is a re-ranker, and the fleet's problems are not ranking problems),
and speculative fan-out (costs calls to find out what you did not need to ask).

The eleven that are obviously worth adopting, roughly in order of effort-to-value:
**guardrails** (the fleet has a fail-open bug and a documented answer), **classification using
confidence** (a label hierarchy you already have, a confidence-derived fallback, ~20 lines),
**entity alignment** (a scored answer to a merge problem the fleet solves with pairwise
similarity), **pre-parsed value extraction**, **line-by-line search**, **date extraction**,
**hierarchical classification**, **parallel questions** (measure it), **structure recovery**,
**function calling**, **speculative fan-out**.

---

## 2. The templates

Five, in `templates/`. Each was **run twice against the live key with different data**, or —
where a single run already demonstrates the claim — contains the counterexample inline as a
measured A/B. `templates/jev.py` is the fixed shared client; copy it, never edit it.

```
templates/
  jev.py                   the fixed half. retry, transport taxonomy, distribution readers.
  T1_citation_check.py     cookbook 11  -> fleet row 1
  T2_intent_routing.py     patterns 2+4 -> fleet rows 2, 3   (contains a measured A/B)
  T3_composite_gate.py     pattern 3    -> fleet rows 3, 4
  T4_skill_suggestion.py   cookbook 8   -> fleet row 5
  T6_noul_vagueness.py     cookbook 1   -> fleet row 7
  *.out                    captured live output, pasted below
```

Run any of them with `cd templates && python3 T1_citation_check.py`. Requires
`TYPESAFEAI_KEY` in the environment. No SDK, no dependencies — `urllib` only, because the
Python SDK's own retry policy is one more thing to tail.

### 2.0 What every template does, and why

Three things are fixed everywhere, and they are the three lessons:

1. **Presence, counting and arithmetic happen in code.** The model is never asked whether a
   string exists, how many there are, or what they sum to. T1 does its string match before it
   spends a token. This is jaggedness #2 and #1 in the published notes, and it is the single
   biggest reason a hand-rolled system is worse than the documented one.
2. **A cell stays a cell.** `describe()` never returns a scalar. It returns the argmax, the
   full `probabilities` map, `confidence`, entropy in bits, margin, and the top-2 ratio. The
   decision is then composed in code from those. The only field any template branches on is
   never the argmax alone.
3. **Transport failure is reported as transport failure.** A 503 or a TLS EOF is retried with
   backoff, and after six attempts the template exits with a message that says explicitly that
   this is *not* evidence about the question. A model that could not be reached must not
   produce a measurement.

---

### 2.1 T1 — Double-checking citations → the resolver's missing half

Tailoring points: **(1)** the source document, **(2)** the (claim, verbatim quote) pairs,
**(3)** the auto-accept floor.

```
$ python3 T1_citation_check.py
step 1  string match, in code  (no model call)
  source 849 chars, 7 citations
  not found -> fabricated : 1
  found     -> send to JEV: 6
    FABRICATED  All incidents including Tier 3 require a written retrospec

step 2  ONE call, 6 Choice questions  (model jev-1.13.0, 2344 in / 259 out tokens)

SUPPORTS  Tier 1 incidents are tho argmax=supports p=1.00 conf=1.00 H=-0.00b margin=1.00 | supports:1.00 contradicts:0.00 says_nothing:0.00
SUPPORTS  Unresolved Tier 1 incide argmax=supports p=1.00 conf=1.00 H=-0.00b margin=1.00 | supports:1.00 contradicts:0.00 says_nothing:0.00
SUPPORTS  The deployment freeze ca argmax=supports p=1.00 conf=1.00 H=-0.00b margin=1.00 | supports:1.00 contradicts:0.00 says_nothing:0.00
CONTRADICTS Retrospectives are due w argmax=contradicts p=1.00 conf=1.00 H=-0.00b margin=1.00 | contradicts:1.00 supports:0.00 says_nothing:0.00
SUPPORTS  Retrospectives are held  argmax=supports p=0.97 conf=0.95 H=0.19b margin=0.94 | supports:0.97 says_nothing:0.03 contradicts:0.00
CONTRADICTS Emergency hotfixes requi argmax=contradicts p=1.00 conf=1.00 H=-0.00b margin=1.00 | contradicts:1.00 supports:0.00 says_nothing:0.00

step 3  composed in code   CONTRADICTS=2   FABRICATED=1   SUPPORTS=4
```

The first version of this template's dataset was wrong and the template said so. Seven of
eight quotes were not character-for-character in the source, so the string match marked them
fabricated and one question reached the model. That is the correct behaviour and it is why
step 1 is in code: the quote's presence is a fact about bytes, and a model should not be
asked for facts about bytes.

**One honest miss.** The fifth citation — claim *"Retrospectives are held within 10 working
days"*, quote *"Retrospectives are blameless. Action items are tracked in the quarterly
engineering planning document"* — should be `says_nothing` and came back `supports 0.97`. The
quote is genuinely on-topic and genuinely does not establish the 10-working-day term, so this
is a false positive on the `says_nothing` class. It is reported rather than quietly re-run
until it came out right. It is also the reason `says_nothing` is a scored option rather than a
threshold: the cell is at least visibly not 1.00 here, and in the versions where it *is* 1.00
you would want a human anyway.

**What this adds to the resolver.** 4,789 is the count of absent paths. This counts the three
other things: absent quote, contradicted claim, and claim the source does not reach. The
resolver already has the first category. It has nothing for the other two, and those are the
ones that make a README wrong rather than merely stale.

---

### 2.2 T2 — Intent routing + confidence gating, with the batching trap measured

Tailoring points: **(1)** the route rubrics, **(2)** the messages, **(3)** the confidence
floor, **(4)** the margin floor.

This template ships with its own failure mode as a live A/B, because the failure is the
finding.

```
$ python3 T2_intent_routing.py
==============================================================================
A.  BROKEN — one shared state, N unqualified questions  (do not ship)
==============================================================================
  HUMAN          1 what's the current status of the inges   argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          2 the deploy script on staging is failin   argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          3 delete the production database and ever   argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          4 summarise this thread for the customer    argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          5 asdfgh qwerty                             argmax=human p=0.99 conf=0.98 H=0.08b margin=0.98 | human:0.99 deterministic:0.01 specialist:0.00
  HUMAN          6 we are legally liable if that ships, p     argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          7 the numbers in the quarterly report lo     argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  HUMAN          8 ok                                        argmax=human p=1.00 conf=0.99 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00

  -> HUMAN=8   (1 distinct answer(s) across 8 questions)

==============================================================================
B.  CORRECT — each question names its own subject
==============================================================================
ONE call, 8 Choice questions  (model jev-1.13.0, 1502 in / 333 out tokens)

  DETERMINISTIC  1 what's the current status of the inges   argmax=deterministic p=0.96 conf=0.94 H=0.24b margin=0.92 | deterministic:0.96 specialist:0.04 human:0.00
  SPECIALIST     2 the deploy script on staging is failin   argmax=specialist p=0.83 conf=0.75 H=0.79b margin=0.70 | specialist:0.83 deterministic:0.13 human:0.04
  HUMAN          3 delete the production database and ever   argmax=human p=1.00 conf=1.00 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  SPECIALIST     4 summarise this thread for the customer    argmax=specialist p=0.83 conf=0.74 H=0.71b margin=0.67 | specialist:0.83 deterministic:0.16 human:0.01
  ASK            5 asdfgh qwerty                             argmax=specialist p=0.60 conf=0.40 H=1.09b margin=0.22 | specialist:0.60 deterministic:0.38 human:0.02  <- conf 0.40 < 0.6
  HUMAN          6 we are legally liable if that ships, p     argmax=human p=1.00 conf=1.00 H=-0.00b margin=1.00 | human:1.00 specialist:0.00 deterministic:0.00
  SPECIALIST     7 the numbers in the quarterly report lo     argmax=specialist p=0.93 conf=0.90 H=0.41b margin=0.87 | specialist:0.93 deterministic:0.06 human:0.01
  ASK            8 ok                                        argmax=deterministic p=0.54 conf=0.30 H=1.06b margin=0.09 | deterministic:0.54 specialist:0.45 human:0.01  <- conf 0.30 < 0.6

  -> ASK=2  DETERMINISTIC=1  HUMAN=2  SPECIALIST=3   (3 distinct answer(s) across 8 questions)
```

**F1 — the batching trap, and it is the most expensive mistake available with this API.**

> Questions evaluate independently against one shared state.

Read that carefully, because it is about the **arithmetic**, not about the model's attention.
Put N items in one shared `state` and ask the same unqualified question N times, and you have
asked **one question N times**. Jev reads literally: *"What kind of handling does this
message need?"* has no anchor for "this", so it resolves against the whole state. The most
alarming line in the batch — *"delete the production database and everything in it"* —
dominated, and all eight messages routed to `human` at confidence 0.99. Not one of the eight
was mis-gated. They were **one answer, printed eight times**, and it looked completely healthy:
no error, no warning, confidence 0.99 on every line.

The fix is in the docs' own jaggedness notes under *Indirection* and *Large state full of
irrelevant detail*: **name the subject.** Move each item's data into that question's own
structured `instructions` and keep the shared `state` to what is genuinely common. Eight
questions, one call, same cost, and now the answer is 3 distinct routes with 2 correctly gated
to `ASK`.

This is worth stating plainly for the fleet: **batching is a performance feature, and it will
happily hide a correctness bug behind a high confidence number.** If you are not prepared to
check that N questions produced more than one distinct answer, do not batch.

**The two axes, working.** Row 5 (`asdfgh qwerty`) has `argmax_p = 0.60` — a *majority* — and
is still routed to `ASK`, because confidence is 0.40 and entropy is 1.09 of a possible 1.58
bits. Gating on `argmax` would have dispatched it. Row 8 (`ok`) is worse: `argmax_p = 0.54`,
margin 0.09, and it is nearly a coin flip between two routes. Both are cases where a panel
worth several votes was about to be spent as one.

**Why `ASK` and not a default route.** A router that falls back to a default when unsure
manufactures the confidence it was trying to detect. Two independent reasons to stop are
checked separately — confidence below the floor, and confidence fine but the runner-up close —
because they are different failures and a single threshold catches only the first.

---

### 2.3 T3 — Composite scoring, min-aggregated, with an entropy budget

Tailoring points: **(1)** the axes, **(2)** the minimum level index, **(3)** the candidates,
**(4)** the gate, **(5)** the entropy ceiling.

```
$ python3 T3_composite_gate.py
ONE call, 15 Score questions (5 candidates x 3 axes)  (model jev-1.13.0, 1150 in / 269 out tokens)

  migrate all customer records to the new schema
    blast_radius   argmax=2 score=1.39      conf=0.09 H=1.22b margin=0.39 | everything, ir=0.65 one system=0.26 several system=0.09  <- H=1.22b over budget
    specificity    argmax=1 score=1.25      conf=0.62 H=0.81b margin=0.50 | concrete but i=0.75 concrete and c=0.25 vague=0.00
    reversibility  argmax=1 score=0.83      conf=0.73 H=0.68b margin=0.64 | undoable with =0.82 cannot be undo=0.18 undoable immed=0.00
    => BLOCK  (weakest axis index 1, gate 1)

  rotate the signing key without a cutover window
    blast_radius   argmax=2 score=1.19      conf=0.00 H=1.54b margin=0.04 | everything, ir=0.41 several system=0.37 one system=0.22  <- H=1.54b over budget
    specificity    argmax=1 score=1.37      conf=0.42 H=1.03b margin=0.23 | concrete but i=0.61 concrete and c=0.38 vague=0.02  <- H=1.03b over budget
    reversibility  argmax=1 score=1.07      conf=0.42 H=1.35b margin=0.38 | undoable with =0.61 undoable immed=0.23 cannot be undo=0.16  <- H=1.35b over budget
    => BLOCK  (weakest axis index 1, gate 1)
```

**F2 — `rotate the signing key` has `confidence 0.00` and entropy 1.54 of 1.58 bits on
`blast_radius`.** The model is genuinely undecided between *everything, irreversibly* (0.41),
*several systems* (0.37) and *one system* (0.22) — a flat three-way split. A single scalar
would have reported `score = 1.19`, a respectable middling value that reads like "moderate
blast radius, proceed." The distribution says *I do not know what this will break*, which is a
completely different message and the one that should block the action.

This is why the template uses **min** across axes and not a weighted mean. A weighted mean
would have let `specificity 1.37` and `reversibility 1.07` paper over a `blast_radius` that
nobody can predict. Min aggregation says: the weakest axis decides, which is the right rule
whenever one axis is a veto.

**What the fleet's gate does not have: an entropy ceiling.** Confidence is a formula the
model applies; entropy is the property of the cell. For a three-level axis the maximum
possible entropy is `log2(3) = 1.58` bits, so a fixed absolute budget is meaningful and
comparable across axes with different level counts. The `ENTROPY_CEILING` line is the cheapest
addition I can think of to the existing two-axis gate: five lines, and it catches a class of
"looks fine, is actually a flat distribution" cells that a confidence threshold alone will not,
because a well-spread distribution on a well-posed question can still score mid-confidence.

**F3 — and the trap in the other direction.** The first version of this template rated every
action on a `grounding` axis (`["unsupported by the text", "partially supported", "fully
supported"]`) with **no text in the state at all**. Jev returned *"unsupported by the text"* at
0.94 with confidence **0.85–0.92 for all five candidates**. High confidence, wrong axis, no
detectable symptom. A confidence gate cannot catch this, because the cell is internally
consistent — it is confidently answering a question nobody meant to ask.

The rule: **every level of every axis must describe a property the state actually contains.**
If you cannot point at the evidence, you have invented an axis. This is published jaggedness
*Literal reading*, and it is the failure mode most likely to survive review, because the
output looks perfect.

---

### 2.4 T4 — Skill suggestion, two calls, at most one

Tailoring points: **(1)** the catalog, **(2)** the shortlist size, **(3)** the accept bar.

```
$ python3 T4_skill_suggestion.py
call 1  coarse choice over 12 skills  (one question, full catalog)
coarse         argmax=test.run p=1.00   conf=1.00 H=-0.00b margin=1.00 | test.run=1.00 db.write=0.00 mail.send=0.00 web.search=0.00 none=0.00 ... (12 options)
  (570 in / 113 out tokens for 12 options in one question)

  shortlist from the DISTRIBUTION (not the argmax): ['none', 'test.run', 'doc.write', 'issue.file']
  argmax alone would have kept only: ['test.run']
  the distribution is what ordered the other 3.

call 2  narrow recheck over 4 survivors, `none` included
recheck        argmax=test.run p=0.99   conf=0.99 H=0.08b margin=0.98 | test.run=0.99 none=0.01 issue.file=0.00 doc.write=0.00

  decision, in code:
    winner        test.run  (Run the test suite.)
    p(winner)     0.99     <- the probability of that ONE option
    confidence    0.99     <- separation-derived, a DIFFERENT number
    entropy       0.08 b of 4 options
    => dispatch test.run()
```

**F4 — I shipped the `none`-dropped bug before fixing it.** My first shortlist took the top-N
by probability, and `none` scored 0.00 in call 1, so it was cut. That silently converts *"the
model may not want any skill"* into *"the model must pick one of these three"* — and it does
it invisibly, because call 2 still returns a confident, well-formed answer. The fixed version
carries `none` into the recheck unconditionally.

The general form: **an escape hatch that is a scored option in one stage must be carried
unconditionally into the next stage.** It has no probability mass of its own to protect it.
This is worth more than the cookbook, because the same shape is what a "no match found"
option is in a reranker, an "other" bucket in a classifier, and a "none of the above" in an
agent router. All four are the same bug waiting to happen.

Note also the coarse pass: 12 options, **one** question, 570 input tokens. Cost barely moves
with catalog size, which is what makes the 182-skill version viable and the shortlist
worthwhile.

---

### 2.5 T5 — (omitted) Classifying RAG passages

Mapped in the table at row 6 as a **stretch** for the dangling-reference triage, and I did not
ship a template for it. The triage ranks *defects it has already found*; the cookbook scores
*retrieved context on its way to a generator*. There is no generator in that lane, so the
template would have been the author's demo rather than a fleet tool. Adopting it properly means
first building the retrieval stage, and that is a different brief.

---

### 2.6 T6 — Nouls, and the vagueness finding the fleet already paid for

Tailoring points: **(1)** the claims, **(2)** the second framing — the one that matters,
**(3)** the bands.

```
$ python3 T6_noul_vagueness.py
ONE call, 10 noul questions (5 claims x 2 framings)  (model jev-1.13.0, 1152 in / 194 out tokens)

  claim                                                       p(true)  p(formed)   band
  --------------------------------------------------------------------------------------------
  The sky is green.                                              0.03       0.83   refuted  (clearly false, and clearly formed)
  The file is fine.                                              0.55       0.22   VAGUE    (probably true, but barely a claim)
  The resolver reported 4,789 missing references and re-run      0.26       0.87   refuted  (precise, verifiable)
  The build is probably fine, or maybe not, it depends.          0.49       0.03   VAGUE    (self-cancelling)
  The sky is blue.                                               0.86       0.71   clean    (clearly true, and clearly formed)
```

The fleet's canon promotions were measured as **vagueness detection, not falsity detection**.
That is not a defect in the gate. It is what a noul is.

A noul returns one number, `p(yes)`, and it has **no `confidence` field** — with two outcomes
the probability is the whole answer, and `|2p − 1|` collapses at 0.5. So a mid-band noul,
`p ∈ [0.40, 0.60]`, does not mean *50% chance this claim is false*. It means **the model cannot
separate the claim from its negation.** *"the sky is green"* and *"the file is fine"* land in
the same place for opposite reasons: one is clearly false, the other is barely a claim. Any
gate that promotes on high-noul and blocks on low-noul treats those identically.

**What the second column does.** Ask a *differently framed* noul — is the claim precise enough
to be proved or disproved — and you get a 2×2 instead of a 1-D band. The clean case is
`p(true) = 0.03, p(formed) = 0.83`: a well-formed claim the model refutes. That is a **falsity
signal you can act on**, and a single-noul gate cannot distinguish it from a model that is
merely unsure. Two nouls, one call, one extra column, 194 output tokens.

**What the second column does not do, measured.** My first draft of the write-up claimed it
separates the two vague claims. It does not: `The file is fine.` scores 0.22 and
`The build is probably fine, or maybe not` scores 0.03. Both low. The column *confirms* both
are vague; it does not tell you they are differently vague. Not overselling it.

**What it does that the first column cannot — F7.** The swap test (§3.7) added a claim the
first dataset did not have, and it is the best evidence in this document:

```
  It is what it is.                                              0.74       0.04   clean    (tautology)
```

`p(true) = 0.74`. A one-dimensional `noul` gate — which is what every canon gate in this fleet
is — reads that as **accepted**, and promotes *"It is what it is"* to canon. The `p(formed)`
column scores it 0.04 in the same call and disqualifies it. A tautology is *vacuously* true and
`p(true)` genuinely cannot see that; only the "could this be proved or disproved" probe can.

**And a false positive, which is the most useful row in the table.** The claim *"The resolver
reported 4,789 missing references and re-running gave 4,791"* came back `p(true) = 0.26`,
`p(formed) = 0.87` — a confident falsity verdict, on a claim that `dangling-TRIAGE.md`
independently **reproduced from code** ("4,791 reproduces", ±2 from a re-clone, not a
regression). Jev was given the numbers as text with no access to either, and judged the
comparison. This is published jaggedness *Math and Numbers*, and it is not fixable by prompt
wording: **a noul cannot adjudicate a claim whose truth is a comparison.** Numeric claims go
to code, where `dangling-TRIAGE.md` already put them. What the noul contributes here is the
*`p(formed)` column* — 0.87, correctly reporting that this is a well-formed, checkable claim —
which is exactly the signal that says *go and check it in code*.

So the honest reading of the fleet's canon-promotion result is better than "the gate was
wrong." The gate was **correctly reporting that it could not adjudicate those claims**, and
the label "vagueness detection" is a true description of a correct refusal to fabricate a
verdict.

---

## 3. Findings

**F1 — the batching trap (§2.2).** Batched questions over a shared state return one answer N
times, at full confidence, with no error. Check that N questions produce more than one
distinct answer, or do not batch. This is the finding I would most want the fleet to adopt,
because it is free to check and it fails silently.

**F2 — a collapsed Score can invert the sign of the finding (§0.3, §2.3).** `score: 0.87`
alongside `confidence: 0.00` and an argmax level of 0. A Score's `probabilities` are keyed by
index, in `legend`, not by your labels. Never gate on the `score` field.

**F3 — a badly-posed axis is answered confidently (§2.3).** An axis whose levels describe a
property the state does not contain returns 0.94 at confidence 0.85–0.92, for every input.
No gate catches this, because the cell is internally consistent. Every level must describe a
property the state actually contains.

**F4 — escape-hatch options get cut from shortlists (§2.4).** `none` at probability 0.00 does
not survive a top-N. Carry it explicitly. Same shape as `other`, `no-match`, `none of the
above`.

**F5 — confidence and argmax are different questions (§0.2).** `p_max = 0.40` is confidence
0.33 across three options and 0.20 across ten. A threshold on one is not a threshold on the
other. `JEV-CONTRACT.md` had this; it is now in this document with the formula.

**F6 — a noul cannot adjudicate a comparison (§2.6).** The 4,789/4,791 claim was confidently
refuted by a model that cannot see either number. Numeric claims belong in code. The noul's
job there is the `p(formed)` column, which correctly flags it as checkable.

**F7 — a tautology scores HIGH on p(true).** Found by the §3.7 swap test, not in the first
dataset, and it is the sharpest evidence for the two-noul design:

```
  It is what it is.                                              0.74       0.04   clean    (tautology)
```

74% true, 4% checkable. A one-dimensional gate on `p(true)` — which is what every `noul` gate
in this fleet is — classifies this as **accepted** and promotes *"It is what it is"* to canon.
The `p(formed)` column disqualifies it in the same call. A tautology is *vacuously* true, and
`p(true)` cannot see that, because vacuous truth genuinely is high; only the "could this be
proved or disproved" probe can. **This is the whole fleet canon-promotion bug, in one row.**

---

## 3.7 The tailoring proof

The bar for this document was that a template only its author ran is a docstring, and that
`selectlib` is the live cautionary example — its selector is documented as beating free local
noise and the code does not implement it. So every template was run again with **different
data in its tailoring blocks only**, and the output was required to change.

| template | what was swapped | measured change |
|---|---|---|
| **T1** | whole source document (incident policy → data-retention policy) and all 5 citations | 7→5 citations, 6→4 questions, **2344→1525 input tokens**, verdicts re-derived on a different document; the new `contradicts` pair landed on a different claim |
| **T2** | all 8 messages (support router → eng-work router) | tally `ASK=2 DET=1 HUM=2 SPEC=3` → **`ASK=3 DET=1 HUM=2 SPEC=2`**; row 2 moved `SPECIALIST → ASK` at conf 0.58, row 6 dropped from `human 1.00` to `human 0.89`, 1502→1480 tokens |
| **T3** | all 3 axes (blast-radius → novelty/coupling/justified), gate 1→2, all 5 candidates | **every candidate re-graded**, all five now BLOCK at weakest index 0 under gate 2; 1150→1223 tokens. Also produced a new F-class row: `improve the code` scores `justified` at conf **0.99** (a confidently meaningless answer, F3 again) |
| **T4** | catalog 12→6 skills, turn → *"What is the capital of France?"*, accept bar 0.50→0.95 | **the decision flipped**: `dispatch test.run()` → `NO SKILL this turn`. This is also the proof that F4 is not cosmetic — with `none` dropped from the shortlist, the template would have been *forced* to dispatch `db.query`/`deploy.run`/`git.commit` to answer a geography question |
| **T6** | all 5 claims (ops claims → language/science claims) | every row re-derived, 1152→1146 tokens, and produced **F7**, the tautology at `p(true)=0.74, p(formed)=0.04` |

Reproduce any row: edit only the `▸▸▸ TAILOR ▸▸▸` blocks, leave everything below them alone,
re-run. If the output does not change, the template is a docstring and should be reported as
one.

---

## 4. The two questions

**Of the 22 published patterns, how many does this fleet use?**

**Four, honestly.** Confidence-gated routing, composite scoring, skill suggestion and noul
self-consistency are all in use or rediscovered. The citation-check pattern is a fifth the
fleet half-implemented — it owns the "path does not exist" half and not the "path exists and
the claim is still wrong" half, which is the half that matters. Intent routing I count as a
stretch rather than a use. **Seventeen of 22 are untouched**, and four of those I would argue
against adopting anyway.

That is the real number and it is a bad one, because five of the fleet's hand-rolled systems
sit directly on top of published, debugged, documented solutions to problems the vendor has
already thought about — and the most expensive one, the resolver, is a hand-rolled *rejection
stage* for a pipeline whose rejection stage is the easy part.

**Which one would have saved the most work if it had been found first?**

**Double-checking citations (cookbook 11).** Not the most patterns, and not the flashiest
demo, but:

* It is the only one that **completes a system the fleet already built and already paid for.**
  The resolver exists, runs in 460s over 8,358 docs, and is currently pointed at the one
  question it can answer cheaply. The other half — present-but-contradicted — is not a new
  system, it is a second pass over artefacts the fleet already has.
* It is the one whose output is **verifiable against ground truth the fleet controls.** A
  citation is checkable, because the source document is right there. That means it can be
  measured, which means the auto-accept floor can be tuned instead of guessed.
* The failure it targets is the one the fleet has **already been bitten by.** `dangling-TRIAGE.md`
  says the headline 4,791 is "approximately the least" valuable number in the lane and that
  the unverified-claim count is an order of magnitude worse. That is precisely the class this
  pattern finds. The triage note diagnosed the disease; the cookbook is the treatment.
* Everything else in the untried fifteen requires building a stage the fleet does not have
  (retrieval, generation, a cheap model tier) before the pattern can be used at all.

**Which one to build next: guardrails (cookbook 12).** It is close behind and it is the
cheapest. `sprint-FAILOPEN.md` and `fleetlint_failopen.py` are the shape of a real fail-open
bug, the fleet's guardrail policy is scattered across several documents with no single cell
behind it, and hazard × severity → pass/review/block/route is a two-axis composite gate you
already know how to build. The citation checker is the bigger win; the guardrails are the
faster one, and both should be templates rather than builds, which is the entire point of
this document.

---

## 5. Provenance

* Index read 2026-10-02: `https://docs.typesafe.ai/llms.txt` — 18 cookbooks, 4 patterns, plus
  SDK reference, demos, and a model-jaggedness page that is worth reading before any of this.
* All live output in this document was captured on 2026-10-02 against `jev-latest`
  (`jev-1.13.0`) using the key in `$TYPESAFEAI_KEY`. Raw captures in `templates/*.out`.
* The credential's **value** appears nowhere in this document, in the templates, or in any
  captured output.
* Fleet-side claims were checked against the workspace, not taken on trust: 4,789 in
  `resolver_audit.json` (`FILE_MISSING`, population 4789, 60/60 sampled and confirmed, 0 false
  positives), 4,791 and its interpretation in `dangling-TRIAGE.md`, the `grey .74 →
  confidence 0.61` measurement and the three request-shape errors in `JEV-CONTRACT.md`.
* No pushes. Branch `jev-docs` in `fleet-triage`.
