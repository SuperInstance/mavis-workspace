# synergy-MAP — a capability that did not exist in either half

**Lane:** synergy. 2026-10-02. **Build:** `synergy/panel_canary.py` (215 lines),
`synergy/demo.py` (154), `synergy/mutation_test.py` (94). **Nothing pushed.**

```
cd /workspace/projects/fleet-triage/synergy
python3 demo.py           # 14/14 checks, exit 0
python3 mutation_test.py  # 6/6 mutations killed, exit 0
```

**The rule I held myself to:** every combination below answers *what capability
now exists that neither component could produce?* If the answer is "it does both
things faster," it is **composition** and it is in the wrong table.

---

# 1. THE PICK: CANARY × n_eff × TYPED CELL

> **The third thing, named: `n_witness` — the number of effective *independent*
> witnesses standing behind a green canary — plus a verdict that can `REFUSE`.**

```
n_witness = (Σ σᵢ)² / Σ σᵢ²      over the singular values of R
R = P − mean(P)                  the RESIDUAL matrix, M members × K options
```

and three verdicts, not two: `CONFIRMED` / `REFUSED-CORRELATED` / `VIOLATED`.

## 1.1 Why neither half can do it alone — one wall per half

**A canary cannot, because a canary's subject is a value.** Every canary in this
account pins a string, a hash, or a number and compares it to a literal. The
panel is not in the artifact; it is a property of the *callers*.
`CANARY-FICTION.md` is the receipt: eleven ports agreed, the build was green for
eleven months, and the pin *passed* every single day it was wrong. The canary was
not weak. It was pointed at the wrong noun, and nothing in a canary's own
construction can see a panel, because a canary has no door for a panel to come
through.

**n_eff cannot, because n_eff is arithmetic downward.** It takes many
distributions and returns one number. A canary is *comparative* — one thing vs a
pinned value. Compose them the obvious way and you get `n_eff(canary(pin))`: a
number about a constant, which is the same inert pin wearing a calculator.
The interesting structure lives in the *residuals around the consensus*, and a
pure n_eff never takes residuals, because it has no anchor to take them around.
It does not know there is a pin.

**And the gap is real, not rhetorical:** Panel A and Panel B are **both green on
the canary** — same pin, five members each, all naming the canon. In the
pre-synergy world their canary output is the *same string*, `PASS`, and the two
states are indistinguishable. The build separates them: A → `REFUSED-CORRELATED`
(n_witness 1.00), B → `CONFIRMED` (n_witness 4.00).

## 1.2 The typed cell is not decoration — it is what makes the measurement well-posed

I built this as a two-way combination and it was wrong. The **closed option set
with stable byte-exact keys is load-bearing**, and mutation M4 proves it: replace
byte-exact option identity with NFC-normalised identity and the canary
**cannot be expressed at all** — the constructor refuses to declare an option set
containing both NFC and NFD, because under NFC identity they are the same option.

That is the sharpest thing in the lane, and I only found it by running the thing:

> **I reached for NFC as the identity function out of pure habit — my own notes
> say "normalise to NFC" — and on this canary that habit IS the defect. NFC is
> precisely the normalization the canary exists to catch. Normalising option
> identity makes the canary structurally incapable of detecting the failure it
> was built to detect.**

The generalisable form, now shipped as `Canary.identity_floor()`:

> **A canary is live only if its option identity is FINER than the normalization
> the pipeline actually runs.** A canary the fleet's own normalizer can collapse
> is a dead canary that will pass forever. This canary declares `identity_floor
> = "NFC"` — it is one normalizer away from being the eleven-months-green pin.

## 1.3 Real output

```
canary      : fnv1a64-cafe
option set  (7 options, residual dim 6):
   [0]* 'café Δ 日本語'      <- pin
   [1]  'café Δ 日本語'      <- NFD
   [2]  'cafe Δ 日本語'   [3]  'caféΔ日本語'
   [4]  'café Delta 日本語'  [5]  'café δ 日本語'   [6]  'cafeΔ日本語'
identity floor: NFC

PANEL A  correlated — 5 ports, identical distribution
  verdict : REFUSED-CORRELATED
  why     : n_witness=1.00 < k=3 (ceiling 4)
  residual spectrum : [] (rank 0)   ceiling=4  n_witness=1.00

PANEL B  independent — 5 members, doubt in 5 directions
  verdict : CONFIRMED
  why     : n_witness=4.00 >= k=3 (ceiling 4)
  residual spectrum : [1.000e-01 1.000e-01 1.000e-01 1.000e-01 6.939e-18]

PANEL C  correlated AND WRONG — normalising tool already ran
  verdict : VIOLATED
  why     : no member names the pinned option; hard fail, unanimity or not
```

14/14 acceptance checks, exit 0. Panels E/F/G/I (`noul`, legend merging two
levels, out-of-set option, undeclared option as the top assertion) all → `EMPTY`.

## 1.4 A note on the acceptance criterion as written

The brief asks me to show it *"correctly reporting on a constructed correlated
panel and correctly refusing on an independent one."* Read literally that demands
the tool **refuse correct, independent evidence** — which is a tool that punishes
the truth, and I did not build that. I implemented the inverse: `REFUSED` on the
correlated panel, `CONFIRMED` on the independent one, and both full outputs are
above so either reading can be checked. Flagging rather than silently choosing.

---

# 2. THE HONEST TABLE — synergy and composition, separated

## 2.1 SYNERGY (a third thing, named)

| # | combination | what exists now that did not before |
|---|---|---|
| **S1** | **CANARY × n_eff × typed cell** | **`n_witness`** — a canary result that carries its own epistemics and can decline to confirm. Undefined for a bare canary (no panel) and undefined for bare n_eff (no pin to take residuals around). Neither half contains it; M4 shows the typed cell is a *precondition*, not a passenger. |
| **S2** | **witness log × n_eff, recording the RESIDUAL not the consensus** | **A stored panel weakness.** The log can answer "how close were the keepers?" — not just "who won." Blocked on a real panel corpus; attacked in §3.2, not built. |
| **S3** | **refusal × typed cell, by EXHAUSTIVENESS not by option-set membership** | **A `verdict` that cannot be partially handled.** `ci_exit` is an exhaustive map over a 3-value sum type, so a fourth verdict is a *compile error*, not a forgotten branch. This is the buildable form of the brief's item 2 — see §3.1 for why the option-set form is not it. |

## 2.2 COMPOSITION (both halves, no third thing — do not call these synergy)

| # | combination | verdict |
|---|---|---|
| C1 | witness log × canary (record which members pinned the constant) | **Composition.** Provenance. You can already write both fields in one row. |
| C2 | typed cell × n_eff (put `levels:` in the JEV call) | **Composition.** The JEV `score` primitive already does this; `JEV-CONTRACT.md` calls it a "display convenience." |
| C3 | refusal × canary (add "the canary may be disabled") | **Composition.** A config flag is not a type. |
| C4 | n_eff × witness log (store the number next to the decision) | **Composition — and worse, misleading.** A stored scalar `n_eff` is a snapshot of an *ordering* that the log will later be read as a *measurement*. Storing the residual spectrum instead is S2; storing the number is C4. |
| C5 | any pair × a hash chain | **Composition.** The chain proves order and integrity. It says nothing about whether the claims were re-executed — the `moth-honest` / `quilt-jepa` lesson, now with a third independent instance. |

---

# 3. THE TWO OTHER COMBINATIONS I WAS ASKED TO ATTACK

## 3.1 REFUSAL × TYPED CELL — the version asked for is composition; the version that works is S3

**The ask:** add `DECLINE` to the JEV option set so abstention is a *value* rather
than an error path, so a consumer "cannot accidentally treat a refusal as a
verdict, because there is no shape in which that mistake compiles."

**Attacked, and the premise is half wrong.** If `DECLINE` is one label in the
producer's `criteria` map, then:

- the API still returns a `probabilities` dict and the consumer still receives
  **four** options to rank. It is one more value to ignore, not a type to match;
- `{"DECLINE": 0.4, "blocking": 0.35, "workaround": 0.25}` is a perfectly
  well-formed answer in which **declining is merely a third-place opinion**.
  Nothing compiles. Nothing fails. The refusal is now a *low-confidence verdict*,
  which is the exact thing we were trying to make inexpressible.

The enforceability cannot come from the producer's option set. It has to come from
the consumer's type system — and the fleet already knows this, which is why
`RELAY-SELECTLIB.md` treats `ControlFailure` being a **public export** as the load-
bearing fact: *you cannot ignore the control because ignoring it is a type you can
import.* I had the wrong half of that sentence: the export is the mechanism, and
the producer's option list is not.

**So the buildable form is S3, and I built it:** `Canary.parse` returns a
complete vector **or `None`**. There is no way to obtain a partial distribution, so
"mostly a vector with a missing option" is unrepresentable. `verdict` returns a
3-value sum type, and `ci_exit` is an exhaustive map over it — a fourth verdict is
an error, not a forgotten `else`. Declining is a value, and the value cannot be
half-consumed.

## 3.2 WITNESS LOG × n_eff — attacked, right instinct, wrong place, and I can name the blocker

**The ask is correct and I believe it.** We keep the losing claims verbatim with
source line and author, and we never record how much the *keepers* disagreed,
because we collapse first and record the collapse.

**Where I think it is mis-specified:** the thing to record is not a correlation
*statistic*, it is the **residual matrix** — or at minimum the singular-value
spectrum, because that is the quantity that is comparable across entries, whereas
"how correlated were the winners" has no stable unit and will be re-derived
differently by every future reader. S1 already produces the spectrum. The log entry
is `R`'s spectrum, not `R`'s dot product.

**The blocker, honestly:** I have no panel corpus. Every panel in this build is
constructed to make the acceptance test decidable, and storing constructed
residuals in a real log would be exactly the fiction `CANARY-FICTION.md` is about.
**This one is deferred, not delivered** — and the thing that would unblock it is a
real `probabilities` capture off the JEV endpoint, which needs
`TYPESAFEAI_KEY` (unset in this sandbox, verified, not assumed). I am not going to
claim a witness-log format I have never seen populated.

---

# 4. THE DANGEROUS CHECK — harder to get wrong, or just more possible?

Most tooling does the second. So I wrote down the one new failure mode this
combination *could* introduce, and then made it unrepresentable.

> **The failure mode I had to design against:** a panel that measures weak, and
> someone reads `REFUSED-CORRELATED` as *"canary inconclusive — proceed."* That
> would be a new way to launder a red build, i.e. strictly more surface.

**Four structural defenses, all mutation-backed:**

1. **The red path never reads `n_witness`.** `verdict()` checks
   `panel_green` **first** and returns `VIOLATED` before the statistic is ever
   computed. Correlation can only ever *downgrade evidence of a PASS*. It is
   structurally incapable of suppressing a FAIL. Panel C is the test: five ports
   **unanimously and confidently wrong**, and the verdict is `VIOLATED`, not
   `REFUSED`. *Killed by M1.*
2. **A refusal is not green.** `ci_exit` maps `CONFIRMED→0` and everything else
   to non-zero (`REFUSED→1`, `EMPTY→1`, `VIOLATED→2`). There is no wiring in
   which the scary outcome is the passing exit code. *Killed by M6.*
3. **An undeclared option cannot be the witness that greens a canary.** Panel I:
   an option outside the closed set, asserting at 0.90. Coerce it onto the pin
   and the canary passes on a string it never declared. *Killed by M5.*
4. **A noul is refused at the door.** A `noul` has no distribution; a panel of
   scalars has no agreement structure. Taking one would be collapsing a
   distribution to a scalar, which `JEV-CONTRACT.md` forbids. Refusing it is a
   refusal, not a missing feature.

**The honest counterweight.** This tool *does* add surface, in one specific way:
it adds a verdict a human must now read. `REFUSED-CORRELATED` is not a failure and
not a pass, and a reader who treats it as either has been made *less* safe by my
work. The defense is structural (exit codes, not prose) rather than a promise, but
it is not zero. The mitigating fact is that the alternative is a canary that
returns `PASS` for Panel A — a green that is worth one opinion and is labelled as
worth five. **A confidently wrong green is worse than a labelled refusal**, and
that is the entire trade.

**Does it make things harder to get wrong? Yes — for a specific class, and only
that class:** it makes *false-green-from-agreement* hard to get wrong. It does
nothing for missing canaries, wrong pins, unexecuted claims, or any of the other
failure modes in this account. Six ways to measure a panel worthless does not stop
anyone from measuring it six times by hand.

---

# 5. THE THREE THINGS I GOT WRONG BY RUNNING IT

Kept because each one was invisible on the page and obvious on the terminal.

1. **A silent dict collision kept the canary green on the wrong bytes.** Two
   visually identical `café` literals collided; the dict kept one key; the pin
   passed while certifying a different string. This *is* `CANARY-FICTION.md`, at
   toy scale, and I reproduced it accidentally before I understood it. It is now
   `identity_floor()` plus a closed option set, and M4 kills the regression.
2. **My ceiling bound was wrong, and the tool caught it, not the doc.** I wrote
   `n_witness ≤ min(M, K−1)`. Residual rows sum to zero *by construction*, so the
   true bound is `min(M−1, K−1)` and a 5-member panel tops out at **4**, not 5.
   The measured 4.00 was correct and my docstring was not. **The instrument being
   right while the prose is wrong is the normal case and is worth watching for.**
3. **M5 survived the first mutation run and I nearly called it a vacuous suite.**
   It was a **provably equivalent mutant**: the `seen` collision guard subsumes
   the closed-set guard, so deleting the latter changed nothing on any input I
   had written. Rather than accuse the suite I made the guard *load-bearing* with
   Panel I. **A surviving mutant is a reason to check equivalence first, and only
   then a reason to suspect the test.**

Mutation coverage, all six killed, exit 0:

| | mutation | why it must die |
|---|---|---|
| M1 | correlation launders a red into a refusal | the whole anti-laundering claim |
| M2 | `n_witness := headcount` | reduces to "5 votes", the naive canary |
| M3 | distribution collapsed to argmax | the forbidden scalar collapse |
| M4 | option identity is NFC, not byte-exact | the canary becomes inexpressible |
| M5 | closed-set check removed | Panel I goes green on an undeclared string |
| M6 | every verdict exits 0 | the tool wired so scary == green |

---

# 6. CLOSING

## The one combination that made something harder to get wrong

**CANARY × n_eff × TYPED CELL — `synergy/panel_canary.py`.**

Not because it detects more faults. Because it **removes a specific way of
producing a fault**: a green check standing on one opinion while being labelled as
five. The defenses are structural, not advisory — the red path never reads the
statistic, a refusal cannot exit 0, and an undeclared option cannot green a canary.
All three are mutation-killed.

## The three that only made more things possible

1. **`DECLINE` in the JEV option set** (refusal × typed cell, as literally
   specified). Makes abstention *representable*, not *non-ignorable* — a
   declining vote is still a low-confidence verdict, and nothing about it fails to
   compile. The enforceable version is exhaustiveness in the consumer's type
   system (S3), which is a different thing wearing its name.
2. **Storing `n_eff` next to a decision in the witness log** (C4). Adds a field.
   Worse than neutral: a stored scalar reads as a *measurement* when it is the
   output of an *ordering*, and the log will be trusted accordingly.
3. **Recording which members pinned a constant** (C1, witness log × canary).
   Provenance. Genuinely useful, zero new capability — and it is on this list
   because provenance is what gets mistaken for insight.

**And the one I could not deliver:** S2, storing residual spectra in a real witness
log. Right instinct, mis-specified location, and blocked on a panel corpus I do
not have. Deferred, not done.
