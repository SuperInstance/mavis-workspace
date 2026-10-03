# res-OPT — Does an existing system already provide the swappable-chooser seam?

**Lane 2 of 4 · optimization cluster · 2026-10-02**
Repos: `stanfordnlp/dspy` @ `ba3f9198` (v3.4.0) · `harbor-framework/harbor` @ `dbd6dd04` (v0.23.0) ·
`yibie/awesome-autoresearch` @ `8c3f24f8`. All three cloned, none pushed to.

---

## 0. Hardware honesty, up front

**No GPU was used and no GPU was needed. Nothing in this report required one, and I am not
describing any CPU result as a GPU one.** Every number below was produced on CPU, in-process,
against the cloned source, with a **scripted fake backend** (`dspy.utils.DummyLM`) that returns
canned JSON. There is **no network call and no API key** in any experiment. The one thing I could
not do is call a real LLM or the real TypeSafe endpoint, so every claim about *what a live model
would return* is out of scope — I only claim what the **code does with what it is given**, which
is the question you asked.

DSPy's own decision test suite runs clean here: `189 passed in 16.07s`
(`tests/adapters/test_decision_types.py`, `tests/predict/test_predict_decisions.py`,
`tests/teleprompt/reanchor/`). The mechanism below is tested, not vaporware.

---

## 1. The headline, before the detail

Three answers, all measured:

1. **DSPy's chooser cannot generate. It selects from a closed, declared, finite label set, and the
   closure is enforced at the decode boundary with a `raise`.** A backend that invents a third
   option is rejected: `ValueError: Invalid Choice answer for 'c'.` This converges with what a
   sibling lane should be finding from the diffusion side.
2. **DSPy has no way to say "I decline."** `Noul` is a **boolean gate**, not an abstention. Measured:
   a maximally uninformative backend (`P(True)=0.50`) produces `value=True` with `confidence=0.0`.
   The uncertainty survives only as a number that nothing forces a caller to read. **This is a real
   limit on the most impressive thing in this list, and it is exactly your doctrine.**
3. **Harbor already ships the "app runs with no chooser" agent** — `NopAgent`, plus an `OracleAgent`
   that replays a recorded script — and already ships a **JEV judge** built on the same TypeSafe API
   your `JEV-CONTRACT.md` reverse-engineered. `r1-NOENGINE` is **not** reinventing Harbor. Details
   and the commit in §5.

**And the most valuable sentence in this report:**

> **DSPy has already solved the swappable-chooser seam and has already shipped our decision
> contract — and it fails both of our two decisive tests for a reason that is now measured, not
> guessed: the chooser slot is typed to an LM, and the app cannot run with the chooser absent.**

So: the seam is solved, the contract is solved, and **we should adopt both and keep our two tests,
because our tests are the part DSPy does not have.** Details in §7.

---

## 2. What a `Signature` actually is, read from `dspy/`

A `Signature` is a **Pydantic `BaseModel` subclass whose docstring is its instructions and whose
class body is its I/O schema** (`dspy/signatures/signature.py:39-136`, `256-271`). The metaclass:

- requires every field to be declared `InputField` or `OutputField` (`_validate_fields`, `signature.py:213-222`)
- **defaults an untyped field to `str`** (`signature.py:161-168`)
- **auto-generates the instructions from the field names** if the docstring is empty
  (`_default_instructions`, `signature.py:35-38`): *"Given the fields `a`, `b`, produce the fields `c`."*
- auto-assigns a `prefix` and a `desc` to every field (`signature.py:206-211`)

**This is the load-bearing thing for our claim, and it is stronger than I expected.** A signature is
*not* a prompt. It is a **typed, closed, validated I/O contract that the prompt is derived from** —
the prompt is a *rendering* of the schema, and `_default_instructions` proves the direction of
derivation. That is our claim ("specific is the chooser and the render") implemented as a type
system: *the schema is the state, the prompt is the render, and the render is disposable.*

What a `Signature` does **not** do at runtime: it does not validate the model's answer against the
schema directly. The adapter (`dspy/adapters/*`) formats the prompt, the backend answers in text,
and the adapter **parses** the text into the schema. Parse failure is an `AdapterParseError`. The
type is enforced at the boundary, after the fact, not during generation.

---

## 3. What `Compile` mutates — and which of those is "a chooser"

`Teleprompter.compile(student, *, trainset, teacher=None, valset=None) -> Module`
(`dspy/teleprompt/teleprompt.py:61-75`). What each optimizer actually changes, from the code:

| Optimizer | mutates | file |
|---|---|---|
| `BootstrapFewShot` | **`predictor.demos`** (few-shot examples) | `bootstrap.py:259-273` |
| `COPRO` | **`signature.instructions`** (LLM-proposed rewrites) | `copro_optimizer.py:211-217, 261-267` |
| `ReAnchor` | **`predict.fields`** — the numeric decision parameters | `reanchor/calibrate.py` |
| `BootstrapFinetune`, `BetterTogether` | **model weights** | `bootstrap_finetune.py`, `bettertogether.py` |

Two facts that decide the question:

- **The program structure is NOT mutated.** `BootstrapFewShot` *asserts* it is fixed:
  `assert name1 == name2, "Student and teacher must have the same program structure."` and the same
  signatures (`bootstrap.py:119-133`). The architecture is the invariant; the prompt is the variable.
- **The chooser itself — the model — is not mutated by most optimizers.** It is a *slot*
  (`predict.lm` / `dspy.settings.lm`), set separately from compilation.

**So "which of these is a chooser in our sense?"** None of them, exactly — and that is the
correction. In DSPy the chooser is **not an artifact the optimizer produces**. It is the
**`BaseLM` occupying a slot**, and the optimizer produces the *instructions and demonstrations
around* it. Our seam is the same seam; DSPy just puts the optimizer's output on the app side of it
rather than the chooser side.

---

## 4. The two decisive questions

### 4a. Enumeration — the chooser **cannot** generate

DSPy 3.4.0 ships a first-class decision layer, exported publicly as
`dspy.experimental.{Noul, Score, Choice, TypeSafe, ReAnchor}`
(`dspy/experimental/__init__.py`). `Choice` is the chooser type and it is **closed by construction**:

```python
Color = Choice[("red", "warm"), ("green", "cool")]     # closed at declaration
```

Measured, three ways:

| experiment | result |
|---|---|
| backend returns a legal closed distribution | **accepted** — `value='north' probabilities={'north':0.9,'south':0.1} confidence=0.8` |
| **backend invents a third option** (`purple`) | **`ValueError: Invalid Choice answer for 'c'.`** |
| **add an option via `fields`/criteria** | **`ValueError: ... must match the declared decision type and options.`** |
| add an option via `weights` | **`ValueError: Choice weights ... must map known string labels`** |

The enforcement is in `DecisionState._decode` (`decision_state.py:198-201`):
`if set(probabilities) != set(options) or sum(probabilities.values()) <= 0: raise ValueError(...)`.
`Choice` is a **closed world with a hard type gate**, and the gate is on the *answer*, not just the
request.

**The escape hatch, and why it is not one.** You *can* declare `answer: str` — an open,
generative output. But then there is no distribution, no `confidence`, no threshold, and
`ReAnchor` cannot fit anything to it. **Generative and probabilistic are mutually exclusive in
DSPy's type system.** That is the answer, and it should match whatever the diffusion lane finds.

**Where the closure is looser than it looks (be precise here):** the `Choice` *type* itself sets no
cap on option count. The caps are on the **SystemOne wire**: `MAX_CHOICE_KEYS = 255`,
`MAX_ORDERED_LEVELS = 10` (`dspy/_vendor/lm15/judgments.py:27-28`), enforced in the provider at
`_vendor/lm15/providers/typesafe.py:145-153`. So a *generative* backend can be handed more than 255
declared options; a *SystemOne* backend cannot.

**The one genuinely swappable thing:** the *labels are fixed but their descriptions are not.*
`predict.set_criteria("urgent", {"true": {"definition": ..., "examples": [...]}, ...})` rewrites what
each element means at runtime, and the criteria must still key-match the declared type. So the
enumeration is fixed and the *semantics* are free. That is a sharper version of our claim than the
one I set out to test.

### 4b. Refusal — **DSPy has a gate, not an abstention**

`Noul` is a boolean with a probability (`Noul[(True,"blocked"),(False,"usable")]`). Its `value` field
is `bool`, strict (`types/decision.py:51`). Measured with a maximally uninformative backend:

```
P(True) = 0.5  ->  value = True   type = bool   confidence = 0.0
outcomes possible from Noul: True / False.  No third 'abstain' value exists in the schema.
```

**DSPy always answers.** At the exact decision boundary it answers `True` (`probability >= threshold`,
`decision_state.py:180-185`) and the only protest is `confidence = 0.0`, which the type system
requires nobody to read. There is no `None`, no sentinel, no third branch.

The thing that makes this a *limit* rather than a *feature* is a grep, not an argument: searching
all of `dspy/` for `abstain|refuse|decline|cannot answer` returns **hits only inside the vendored
`lm15` HTTP layer** (API-adaptation policy, auth errors). **Zero hits in DSPy's decision or
predict layer.** The refusal vocabulary exists in the transport and nowhere in the semantics.

Two further limits, both measured:

- **`Choice.confidence` is unvalidated pass-through.** Feeding a **flat 0.50/0.50 distribution** and
  varying only the chooser's stated confidence:

  | stated confidence | reported `move.confidence` | reported `move.value` |
  |---|---|---|
  | 0.05 | 0.05 | (tie → declaration order) |
  | 0.5 | 0.5 | — |
  | **0.99** | **0.99** | — |

  A coin-flip reports 0.99 confidence and DSPy passes it through. Only the *range* `[0,1]` is checked
  (a stated `5.0` is rejected by pydantic: `Input should be less than or equal to 1`). **Nothing
  correlates the confidence to the distribution.** The code is candid about this in
  `Noul`'s docstring: confidence is *"a distance from the decision boundary, **not a calibrated
  probability**"* (`types/decision.py:46-48`).
- **`Noul.confidence`, by contrast, is derived and well-defined:**
  `abs(p - threshold) / max(threshold, 1 - threshold)`, which is `0.0` exactly at `p == threshold`.
  So the *gate's* confidence is honest and the *chooser's* confidence is not. That asymmetry is the
  actionable finding: **if you want a trustworthy confidence number, take it from a `Noul` gate, not
  from a `Choice`.**

Our `abstain-gate` is not redundant with `Noul` — it is `Noul` **plus** the one thing `Noul` lacks:
a path that does not produce a value at all.

---

## 5. Harbor — and no, `r1-NOENGINE` is not reinventing it

**Harbor does not reinvent the environment/rollout harness, because it *is* one**, and it has
already built the two things `r1-NOENGINE` built:

- **`NopAgent`** (`src/harbor/agents/nop.py`) — `setup()` and `run()` are both `pass`. A legal agent
  that does nothing. Registered as `AgentName.NOP` and wired in the factory
  (`src/harbor/agents/factory.py:41`).
- **`OracleAgent`** (`src/harbor/agents/oracle.py`) — replays the task's own recorded solution steps.
  A scripted, non-model chooser.

And it **tests the thing**:

```python
# tests/integration/test_hello_user_e2e.py:26-31
pytest.param(AgentName.ORACLE.value, 1.0, id="oracle"),
pytest.param(AgentName.NOP.value,  0.0, id="nop"),
```

The environment boots, the **verifier still runs**, and the nop agent is scored `0.0`. That is
**r3-SWAP's decisive test #2 — "the app must still run with no chooser at all" — already
implemented upstream, with an expected value pinned.** This is the single most reusable thing I
found today.

**The commits you asked for** (I unshallowed the clone first; my initial `--depth 50` returned the
shallow boundary, not the truth, and would have been a false citation):

| artifact | commit | date |
|---|---|---|
| `src/harbor/agents/nop.py` added | `8196c368` "Add a CLI." | 2025-08-14 |
| `src/harbor/agents/oracle.py` added | `9b41a020` "Implement docker env." | — |
| the `nop`/`oracle` e2e test added | `51699724` "fix: oracle agent run fail in user agent mode (#1615)" | — |
| **JEV judge + rubric criteria** | **`404bae7` "feat(rewardkit): add JEV judge and rubric criteria (#3325)"** | 2026-09-21 |

**So: keep `r1-NOENGINE`.** The lane is not reinventing Harbor. The distinction that keeps it
alive: `NopAgent` **does nothing**, and `OracleAgent` **replays a recording**. Neither one is a
*closed-loop deterministic policy that plays a stateful world to termination*. That is the gap, and
`r1-NOENGINE` (a dungeon that reaches a terminal state with no model) is the only thing I saw that
fills it. The contribution is the **liveness probe** — its own finding that a harness cannot tell
"a check failed to catch a bug" from "a bug was never introduced" — and **Harbor has no
equivalent**. That is the part worth porting, not the dungeon.

### 5a. Harbor also already speaks JEV

`packages/rewardkit/src/rewardkit/judges.py:626-650` calls `typesafe_sdk` with
`typesafe_sdk.Score(instructions=..., criteria=[...levels])` and `typesafe_sdk.Noul(instructions=...)`.

**That is your `JEV-CONTRACT.md`, implemented upstream, in a different repo, by different people.**
Three-way convergence: your hand-recovered contract, DSPy's `TypeSafe` client
(`dspy/clients/typesafe.py` + `_vendor/lm15/providers/typesafe.py`, 341 lines, full wire format),
and Harbor's `rewardkit` judge.

**And DSPy is strictly better here in one measurable way.** Harbor hard-codes the decision boundary:

```python
# judges.py:650
raw = answer.noul
value = 1.0 if raw >= 0.5 else 0.0
```

DSPy makes the same number a **fitted parameter** (`Noul` threshold), tuned by `ReAnchor` against a
metric with 5-fold cross-validation (`reanchor/calibrate.py:54-57`, `FOLDS = 5` at `:56`). The one place
Harbor's judge is a hand-rolled version of a solved problem.

### 5b. The agent seam — four methods, one of which does the work

```python
class BaseAgent(ABC):                    # src/harbor/agents/base.py:29
    @abstractmethod def name() -> str
    @abstractmethod def version() -> str | None
    @abstractmethod async def setup(self, environment) -> None
    @abstractmethod async def run(self, instruction, environment, context) -> None
```

`run()` is the seam: **one behavioral method**, and it hands the agent the *environment*, so the
agent is a **policy driving a world**, not a script replaying a recording. 48 registered agents
(`src/harbor/models/agent/name.py`), 88 benchmark adapters (`adapters/`), the official
Terminal-Bench-2.0 harness. **This is your `r3-SWAP` interface with 48 production implementations
behind it, and your test #2 already green.**

One more convergence worth noting: `src/harbor/agents/dspy_rlm.py` is a **DSPy agent inside
Harbor**. The two systems are already integrated.

### 5c. `awesome-autoresearch` — an index, not a system

32 files, `README.md` generated by `scripts/build-readme.py`, 602 entries split across
`categories/`. It is a **curated link list with an explicit anti-endorsement warning** and
inclusion rules. There is no mechanism to adopt, only prior art to read. Its one relevant
contribution is the framing it defines — a **"modify → verify → keep/discard" loop** — which is
the *loop* half of our claim stated independently by a third party. Worth citing; nothing to port.

---

## 6. The composition primitive — the thing r3-SWAP actually needs

**Yes, it exists, in both repos, and it is smaller than anything we have built.**

**DSPy — two methods on `Module` (`dspy/primitives/module.py`):**

```python
def set_lm(self, lm):                      # module.py:179  — recurse to every leaf
def map_named_predictors(self, func):      # module.py:226  — replace every Predict
```

both driven by the structural walk **`named_parameters()`** (`base_module.py:24-68`), which is the
"general-purpose is the state and the enumeration" half of the claim, already implemented as a
recursive tree walk that descends into `Module`s, `list`s, `tuple`s and `dict`s.

**Harbor — one abstract method**, `BaseAgent.run`, plus a factory keyed by name string.

### The zero-diff swap, measured

I built a fixed app file and swapped choosers under it:

```
app2.py sha256 before : 888d05d8c36135bf0969ddc87ca999fbb32491308468d3627ff6add564e2cc06
app2.py sha256 after  : 888d05d8c36135bf0969ddc87ca999fbb32491308468d3627ff6add564e2cc06
APP DIFF ON SWAP      : ZERO

chooser: free statistic (DummyLM, no net, no key, no GPU)
  move = value='north' probabilities={'north': 0.9, 'south': 0.1} conf 0.8
  can_act = value=True P(True)=0.99 conf 0.98
chooser: judgment model, 0.45/0.55 split
  move = value='south' probabilities={'north': 0.45, 'south': 0.55} conf 0.35
  can_act = value=True P(True)=0.5  conf 0.0
```

**r3-SWAP's decisive test #1 passes in DSPy today.** Two wildly different choosers, identical app
bytes. A `Choice` and a `Noul` coexist in one signature, so a program can carry a chooser *and* a
gate side by side.

**And the mechanism has one property we do not have, which I did not expect:** on the generative
path the model is asked for **evidence only**. I tried to return `value` and it was rejected:

```
Failed to parse field m: 1 validation error for ChoiceEvidence
value  Extra inputs are not permitted
```

`ChoiceEvidence` is `extra="forbid"` (`adapters/decision.py:47`) and contains only `probabilities` and `confidence`. **The
model supplies a distribution; DSPy's local decoder picks the winner, applying its own threshold,
cuts and weights** (`decision_state.py:170-215`). The chooser is therefore split into
**(a) an evidence producer, swappable and untrusted, and (b) a decision rule, local, deterministic,
inspectable and testable.** That is a better decomposition than ours and we should copy it.

### The two places DSPy fails our tests

| our test | DSPy | measured |
|---|---|---|
| **#1 app diff on chooser swap = 0** | **PASSES** | identical sha256 above |
| **#2 app runs with no chooser** | **FAILS** | `ValueError: No LM is loaded...` (`predict.py:161-166`) |
| — chooser slot accepts a plain callable | **FAILS** | `ValueError: LM must be a dspy.BaseLM or a decision-request client, not <class 'StatisticChooser'>` (`predict.py:176-177`) |

**The chooser slot is typed to an LM.** A free statistic is rejected outright at the seam. The
workaround is to wrap it — I did, and it works:

```python
class StatisticShim(BaseLM):      # isinstance(shim, dspy.BaseLM) is True
    ...
# accepted, no network, no key, no GPU
```

`dspy.BaseLM` is duck-typed enough that a deterministic statistic can occupy DSPy's chooser slot —
**but only by claiming to be a language model.** DSPy has no notion of a chooser that is not an LM,
and no notion of an app that runs with no chooser. It fails closed, loudly, on both.

---

## 7. The bottom line — what to adopt rather than build

**Does an existing system already provide the swappable-chooser seam? Yes. Twice.**

**The smallest thing we should adopt rather than build, in order:**

1. **Adopt DSPy's `Choice` / `Noul` / `Score` as our decision types, and `dspy.experimental` as the
   import path.** They are already exported, already tested (189 green), already calibrated by
   `ReAnchor`, and already cover four of our ~20 hand-rolled published patterns. Our `abstain-gate`
   and our JEV client become ~200 lines of configuration. *This is the "delete a lane" moment for
   anything we built on top of a JEV `choice` call.*
2. **Adopt the evidence/decision split, not just the types.** Return `probabilities` + `confidence`
   only, and let a local deterministic decoder pick the winner (`DecisionState._decode`). This is
   the piece that makes a chooser swappable *and* auditable, and it is the part we have not built.
3. **Take the `Noul` threshold-as-a-fitted-parameter idea, and take it to Harbor.** Harbor's judge
   hard-codes `>= 0.5` (`rewardkit/judges.py:650`); DSPy's `ReAnchor` fits it against a metric with
   5-fold CV. That is a one-line upstream contribution and it is better than anything we would
   write.
4. **Keep both of our decisive tests, and keep them as tests against DSPy.** They are the only part
   of this we have that DSPy does not. DSPy passes #1 and **fails #2**. Any adoption must therefore
   keep a `chooser=None` run mode and a chooser slot that a plain callable can occupy — otherwise we
   are inheriting a framework that is structurally incapable of the thing we are arguing for.

**What I would not adopt:** `awesome-autoresearch` (an index). **What I would not delete:**
`r1-NOENGINE` (Harbor's `nop` does nothing and its `oracle` replays a recording; neither is a
closed-loop deterministic policy, and the liveness probe is genuinely novel).

**And the sentence you said you would act on, if DSPy had solved the seam outright:** it has, for
the swap; it has not, for the two properties that make the swap *mean* anything — the chooser must
be able to be a non-LM, and the app must survive without one. **DSPy is a three-thousand-times-larger
answer to the seam and a strictly smaller answer to the doctrine.** We should stand on its shoulder
for the types and keep our two tests as the specification it fails.

---

## 8. Files read (all under the cloned HEADs; nothing taken from a README)

**DSPy — 4,716 lines, read not skimmed:**
`dspy/signatures/signature.py` (865) · `dspy/predict/predict.py` (430) · `dspy/primitives/module.py`
(353) · `dspy/primitives/base_module.py` (289) · `dspy/adapters/types/decision.py` (246) ·
`dspy/adapters/decision_state.py` (215) · `dspy/utils/dummies.py` (206) · `dspy/teleprompt/bootstrap.py`
(272) · `dspy/teleprompt/copro_optimizer.py` (356, structure) · `dspy/teleprompt/reanchor/calibrate.py`
(354) · `dspy/teleprompt/reanchor/reanchor.py` (87) · `dspy/clients/typesafe.py` (154) ·
`dspy/adapters/decision.py` (146) · `dspy/teleprompt/teleprompt.py` (86) ·
`dspy/_vendor/lm15/judgments.py` (312) · `dspy/_vendor/lm15/providers/typesafe.py` (341, header+judgments) ·
`dspy/experimental/__init__.py` · `docs/docs/tutorials/jev_decisions/index.md` (345 — read for the
contract, and because it is titled after our project).

**Harbor:** `src/harbor/agents/base.py` · `src/harbor/agents/nop.py` · `src/harbor/agents/oracle.py` ·
`src/harbor/agents/dspy_rlm.py` · `src/harbor/agents/factory.py` · `src/harbor/models/agent/name.py` ·
`src/harbor/trial/trial.py` (imports + structure) · `tests/integration/test_hello_user_e2e.py` ·
`packages/rewardkit/src/rewardkit/judges.py` · full 1,749-commit history for the commit table.

**`awesome-autoresearch`:** `README.md`, `categories/`, `scripts/` — read, characterized, nothing adopted.

**Executed, not asserted:** `tests/adapters/test_decision_types.py`,
`tests/predict/test_predict_decisions.py`, `tests/teleprompt/reanchor/` (189 passed);
and six purpose-written probes in `/tmp/optlab/` (`probe1`–`probe7`) covering enumeration closure,
abstention, the swap diff, the `BaseLM` shim, and confidence pass-through. No network, no API key,
no GPU, no pushes.
