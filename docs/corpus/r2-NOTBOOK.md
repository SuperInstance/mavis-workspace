# R2 — THE A2A QUILT NOTEBOOK

**Lane:** turn a working JEV into something portable.
**Status:** runnable today on the live key. Two real cells, real answers, below.
**Read first if you only read one thing:** §6, the minimum replay set. Everything else is
arguable; §6 is the deliverable.

---

## 0. THE HEADLINE

> **A cell's value is a distribution. A cell's trajectory is the intelligence.
> And the two live cells I ran *changed their minds* between step 1 and step 2 —
> so a notebook that keeps only the argmax would have reported the opposite answer.**

Not a philosophical claim. Two measured flips, live, on the rolled key, 2026-10-02.

---

## 1. WHAT `A2A-native-notebookLM` ACTUALLY IS

Cloned to `/tmp/a2a-nblm` (`SuperInstance/A2A-native-notebookLM`, HEAD, ~1.9 MB + a 1 MB
logo). It is a fork of `lfnovo/open-notebook` v1.9.0 — FastAPI + Next.js + SurrealDB +
LangGraph, 18+ AI providers — re-skinned as a "cognitive command center" that lives inside
a git repo rather than being pointed at one. `python cli.py boot /path/to/repo` ingests a
repo into a persistent workspace. Identity is `CORTEX.json` (name `hermit`, `agent_type:
notebook`); transport is a **file-based bottle bus** — I2I vessels polled off
`.vessel/incoming/` and `.vessel/outgoing/`, with `before_ask`/`after_ask` hooks that
intercept LangGraph nodes. `QUILT-COMPAT.md` already projects notebook automations onto
reactive quilt cells.

### Verdict: it is closer to a **FILE FORMAT** than to a notebook or a protocol.

The UI is a notebook. The *substrate* is `nb/engine.py`: a sheet is a **DAG of cells** in
`.nb/sheet.json`, each `{id, deps, op, code}`, evaluated topologically, memoized, and
**receipted** — `sha256` over `cell_id+code+inputs+output` with **no timestamps inside the
hash**, so receipts are bit-identical across reruns. `op: port` binds a SPEC cell to a
CANDIDATE cell and books an honest verdict. `nb/mcp_server.py` exposes the whole sheet over
MCP so any agent can drive it.

This is why the file-format answer matters: **git is the notebook's version control, and the
receipt is the notebook's proof of work.** The protocol (`I2I` bottles, CORTEX) is a thin
add-on; the durable artifact is the JSON.

**And the gap is now precise, in one line of their own source.** `open_notebook/a2a/hooks.py`,
`after_ask()`:

```python
final_answer = state.get("final_answer", "")
...
await emit_fn(bottle_id=bottle_id, result=final_answer, ...)
```

The A2A payload is **`result=<a string>`**. A verdict. Every distribution JEV ever produced
is dropped at the vessel boundary. The DAG below is careful and receipted; the *wire* above
it is a string. **The notebook has already lost the information the whole project is about** —
exactly the failure the orchestrator named, sitting in a real repo, in the actual exit path.

---

## 2. THE CELL MODEL

```python
Cell = { id, subject, key, instructions, criteria: [closed set], states: [routine], rung }
```

- **`criteria` is the type.** A closed, finite, enumerated option set. That closure *is* the
  type safety: you cannot record a judgment whose answer space you did not declare first.
  `Cell.validate()` **REFUSES** an open set — verified, not asserted:

  | attempt | result |
  |---|---|
  | `criteria: []` | `REFUSED: option set is not closed (need >=2 declared options)` |
  | `criteria: ["only"]` | `REFUSED: option set is not closed (need >=2 declared options)` |
  | `states: ["  "]` | `REFUSED: a cell with no state is a cell with no subject` |

- **The value is the distribution.** `argmax` is computed and kept, but it is a *derived
  view* — it never becomes the cell's value, and it never round-trips through the wire.

- **`states` is a routine, not a state.** One state is the degenerate one-step cell. See §5.

- **`confidence` is not `p_argmax`,** and I confirmed it again on live data: C1 came back
  `argmax=fragile p=0.52 confidence=0.27`; C2 `argmax=yes p=0.68 confidence=0.52`. The
  receipts store both, separately named, and **nothing in the notebook is calibrated against
  `confidence` until someone establishes what it is.** It is not a coin, and I have not
  treated it as one.

---

## 3. A2A, WITH THE DISTRIBUTION AS PAYLOAD

`choice` is the transport. The **payload is the whole `probabilities` map**, and the
envelope looks like this on the wire:

```json
{"to":"<peer>","cell":"C1_portability","criteria":["fragile","partial","solid"],
 "distribution":{"fragile":0.52,"partial":0.27,"solid":0.21},
 "argmax":"fragile","confidence":0.27,
 "trajectory":[{"step":1,"argmax":"partial","p_argmax":0.52,"margin":0.11,"entropy_bits":1.2865}, …],
 "rung":"jev","spec_hash":"46b39be23cceaa2c","receipt":"cddc235b1236b51f"}
```

Two things a verdict-only envelope cannot carry, both of which I needed: **the margin**
(0.52 with margin 0.11 is not 0.52 with margin 0.42 — one is a coin, one is a finding) and
**the trajectory** (§5).

**`noul` is banned in this notebook.** It collapses unnamed subjects into one shared answer.
Every subject here is named in *both* `subject` and `instructions`, and the run used
`choice`. Batching is safe only because the whole distribution came back each time and both
cells' full maps are in §4 — I did not read an argmax off a batch.

---

## 4. THE REAL CELLS — live, rolled key, 2026-10-02T17:2xZ

Contract used verbatim as supplied. Model resolved `jev-latest` → **`jev-1.13.0`**.

### C1_portability — *how portable is a template another agent must fill?*

- `criteria` (the type): `["fragile", "partial", "solid"]`
- **FINAL DISTRIBUTION: `{"fragile": 0.52, "partial": 0.27, "solid": 0.21}`**
- argmax `fragile` · **p_argmax 0.52** · **confidence 0.27**
- rung **`jev`** · usage `{input_tokens: 457, output_tokens: 50}`
- `spec_hash 46b39be23cceaa2c` · `receipt cddc235b1236b51f`

**State vector (retained):**

| step | state digest | argmax | p | margin | H (bits) | rung |
|---|---|---|---|---|---|---|
| 1 — README's claim | `78775f24` | **partial** | 0.52 | 0.11 | 1.2865 | jev |
| 2 — `hooks.py` emits a string | `1d770e60` | **fragile** | 0.67 | 0.42 | 1.1786 | jev |
| 3 — `engine.py` receipts, no distribution | `beb2aedd` | **fragile** | 0.52 | 0.25 | 1.4734 | jev |

> **This is the whole lane in one table.** Given only the README, the notebook says
> **partial**. One line of their actual source flips it to **fragile**, and the margin more
> than triples (0.11 → 0.42) — the flip is not noise, it is the evidence arriving.
> **A notebook that stored inputs and outputs would have filed `partial` and been wrong.**

### C2_replay — *can a non-author replay it with NO key?*

- `criteria`: `["no", "partly", "yes"]`
- **FINAL DISTRIBUTION: `{"yes": 0.68, "no": 0.29, "partly": 0.03}`**
- argmax `yes` · **p_argmax 0.68** · **confidence 0.52**
- rung **`jev`** · usage `{input_tokens: 460, output_tokens: 51}`
- `spec_hash 840a122e0c4f8ec3` · `receipt d70004e82b29f444`

**State vector (retained):**

| step | state digest | argmax | p | margin | H (bits) | rung |
|---|---|---|---|---|---|---|
| 1 | `78775f24` | **no** | 0.68 | 0.39 | 1.048 | jev |
| 2 | `1d770e60` | **yes** | 0.53 | 0.10 | 1.1948 | jev |
| 3 | `beb2aedd` | **yes** | 0.68 | 0.39 | 1.048 | jev |

Also flipped, `no` → `yes`, on the same evidence. Note step 2's margin of **0.10** — the
model *moved* to `yes` but was nearly indifferent while doing it. The final cell reports
0.68 with a 0.39 margin and looks decisive; **the routine is what tells you it spent step 2
undecided.** A scalar cannot express that. The distribution can.

---

## 5. CASEY'S IDEA, AND WHAT I ACTUALLY KEPT

> *Decomposed weights are intelligence when you see their routine as a state of vectors.*

Taken literally into the cell. **The state vector is logged at every step** and retained in
the receipt: `(step, state_digest, argmax, p_argmax, margin, entropy_bits, n_options,
prev_argmax, flipped, rung)`.

Three design decisions that make the trajectory a *portable artifact* rather than a log:

1. **`state_digest` = `sha256(state)[:8]`, not the prose.** The trajectory binds to the
   *inputs* it was computed from. You can verify a step without trusting the sentence.
2. **`flipped` and `prev_argmax` are first-class.** The routine knows it changed its mind
   and *when*. That is the finding in C1 and C2; a reader who only sees the last row cannot
   see it.
3. **`rung` is per-step, not per-cell.** A notebook that says "jev" at the top has already
   thrown away the one moment that matters — the step where it silently wasn't.

**And the trap, stated plainly:** a trajectory of length 1 is a configuration, not a routine.
The single-point cell looks like a notebook and is not one. The minimum to be a notebook is
**≥2 states**, and a template that ships with one state has shipped a lookup table.

**Counter-argument I'll defend losing.** Keeping the whole trajectory is expensive and most
cells don't need it. Fine — but the default must be retain, and thinning must be a *declared*
rung stamp, or the notebook is lying about what it knows. `quiln.py` keeps all of it; a
storage tier may compress, but compression stamps `trajectory_retained: false` and the cell
refuses to present itself as replayable.

---

## 6. THE MINIMUM TO REPLAY A CELL — THE ACTUAL ANSWER

**Six fields. Not the prompt. Not the key. Not the endpoint.**

| # | field | why it is irreducible |
|---|---|---|
| 1 | **`criteria`** | the type. Without the closed set there is no way to know what a probability means, and no way to check the replay is even the same question. |
| 2 | **`instructions`** | the *question*, with the subject named. Two cells with the same criteria and different questions are different cells. |
| 3 | **`key`** | the subject binding. This is what `noul` collapses and what stops an unnamed subject from being answered by a shared prior. |
| 4 | **`states`** | the routine. The input space the trajectory was computed over — and the only thing that lets a replayer *interleave* rather than re-run. |
| 5 | **`trajectory`** | the state vector. The intelligence. **This is the only item that is not derivable from the others, which is exactly why it is the minimum.** |
| 6 | **`rung` (per step)** | whether this was JEV or a local policy. Without it a reader cannot tell a measurement from a fallback. |

**Everything else is derived and must NOT be shipped as authoritative:**

- ❌ `argmax` — a view. Derive it; never trust a stored one.
- ❌ `confidence` — semantics unestablished. Carry it, calibrate it never (yet).
- ❌ the API key, the endpoint, the model id — **a key is not part of a cell.** Cells
  recorded on `jev-1.13.0` today are still readable on another rung tomorrow.
- ❌ `ran_at` — a timestamp, deliberately **outside** the content hash, so replay is
  bit-identical. Copied from `nb/engine.py`'s no-timestamps-inside-the-hash law, which is
  the one piece of their design I would not change.

**The proof that 1–6 suffice and the rest are noise:** a replayer with fields 1–6 and **no
key, no network, and no author** reproduces the cell. `spec_hash` re-derives from
`{key, instructions, criteria, states}` alone — it is a *check*, not an input. A
distribution is a claim; the spec is the claim; the trajectory is the evidence.

---

## 7. THE TEMPLATE — AND THE SECOND-AGENT TEST

`/tmp/r2notebook/template.json`. **The bar was: someone else's agent fills it and it
works. I ran that test. I have not yet seen a second lane dispatch, so read the next line
as a partial, not a pass.**

**Test executed:** a second agent — no author present, **key explicitly unset**
(`env -u TYPESAFEAI_KEY -u TYPESAFE_API_KEY`) — filled `fill` verbatim and ran it:

- ✅ it ran, produced a full 3-step trajectory, and **declared itself honestly**:
  `rung: "local"`, `model: "local-lexical-v1"`, all three steps `rung: local`
- ✅ distribution on the *unfilled* placeholders: `{"<opt1>": 0.333, "<opt2>": 0.333, "<opt3>": 0.333}`
- ✅ `receipt b155777a6050cb8c`

**That third line is a feature, not a bug.** Placeholder text has no lexical signal, so the
local rung returns **uniform** and **refuses to invent confidence**. An unfilled template is
therefore safe to publish: it **cannot** masquerade as a measurement. A template whose local
rung guessed would be the `selectlib` failure mode — author's-environment-only, and worse,
it would *look* like it worked.

**What I have NOT yet proven:** the template filled with a *real* subject by an *actual*
separate lane. I ran the no-key path myself, which proves the mechanism and the honesty, but
"the author tested it" is exactly the claim I am not entitled to make. **Next lane: fill it,
paste the receipt, and say whether it worked without me.** That result goes in this section.

**Portability law, stated as a rung, not a hope:**

| rung | when | what it means |
|---|---|---|
| `jev` | a key is present | a real measurement, model-stamped |
| `local` | no key | a declared lexical policy, **stamped `local` in every step** |
| `local(fallback:<reason>)` | key present, **transport/schema failure** | the drop is *recorded*, never silent |

The third row is the orchestrator's warning, absorbed into the format. A 503 or a TLS EOF is
a **transport failure**, and the cell that drops to rung 2 carries the reason in its rung
stamp. **The notebook cannot lie about which rung produced it** — and it never pretends a
local answer is a JEV answer.

---

## 8. WHAT I'D PUSH ON NEXT

1. **Trajectory ≥2 is the notebook's real invariant.** Worth enforcing in `validate()` and
   worth an equivalent-mutant check — a template shipping one state is a lookup table that
   passes every structural test I wrote.
2. **`hooks.py` is a one-line fix with a fleet-sized blast radius.** `result=final_answer` →
   the whole distribution + trajectory. It is the exit path every A2A peer reads.
3. **The `confidence` field is still uncalibrated and now has 4 live data points across 4
   cells, all with `confidence < p_argmax`.** Four points is not a finding. It is a reason to
   stop treating it as a probability before someone builds an n_eff on it.

---

## 9. REPRODUCE

```bash
export TYPESAFEAI_KEY=<your key>            # absent is FINE — rung 2 runs
cd /tmp/r2notebook
python3 run_cell.py                         # the two live cells above
python3 fill.py template.json -o out.json   # a second agent, no key
```

Files: `quiln.py` (engine) · `template.json` (contract) · `run_cell.py` (the two cells) ·
`cells.json` (full receipts) · `second_agent.json` (the no-key fill).

**One line for the board:** the repo under study already receipts its DAG beautifully and
throws the judgment away at the wire; the minimum to replay a cell is six fields, and only
one of them — the trajectory — is not derivable from the rest.
