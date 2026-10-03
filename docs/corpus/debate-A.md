# DEBATE — POSITION A (FOR the claim)

Lane: A. Opponent: B (against). Third lane: C (hands the chooser to a real repo).
Evidence read first: `r3-SWAP.md`, `JEV-CONTRACT.md`, `AGENTS.md`.
Code + raw output: `debate-A-code/`. No GitHub pushes.

**VERDICT ON MY OWN POSITION: the seam is real, the claim is not supported.**
C1 and C2 pass. **C3 — "the chooser is the reusable unit" — passes mechanically and
fails semantically**, and it fails in the most expensive way available: the judges
transferred byte-identically into a second app and returned a **perfectly uniform
prior**. I am leading with that because it is the finding.

---

## 0. The one-paragraph version

I built a real triage app (`sift`) behind a one-method seam, ran it under three
executable judges and one blocked one, scored every run against a documented root
cause, verified four of the five oracles by **actually applying the repair and
re-running**, and then ran the same judges — **unedited, sha-verified** — inside a
second, unrelated app (`sort`). The app diff on every judge swap is **zero bytes**.
And that zero is the least interesting number I produced. In the transfer app the
judges' `confidence × n_options` is **1.00 and 1.06**: the uniform distribution.
A judge that runs unchanged in a new app is not evidence the judge is reusable; it
is evidence the judge had nothing to say and the app could not tell the difference.
**The claim is about where the specificity lives. What I measured is that the
specificity does not live in the code — it lives in the feature vocabulary, and a
byte-diff cannot see a vocabulary.**

---

## 1. Thesis, and the three parts it actually has

> General-purpose is the state and the enumeration. Specific is the chooser and the
> render. The fleet should extract *choosers and projections*, not *apps*.

| # | Part | Testable as |
|---|---|---|
| **C1** | The *app* can be general — state + enumeration, zero judgment. | app bytes identical across judge swaps; one method on the seam |
| **C2** | The app cannot see the chooser. | app bytes identical **and** no chooser-conditional path in the app |
| **C3** | **The chooser is the reusable unit — it moves to a different app unchanged.** | a judge written for app 1 runs, byte-identical, in app 2 |

`r3-SWAP.md` measures C1/C2. **C3 is the whole claim** and one app cannot see it.

### Concessions I made in the stub, before running anything, and now hold to

1. **`lau-git-render` is evidence of a shape, not of a unit of reuse.** 2,477 lines,
   one `RenderContext`, eight renderers, never switched on since June.
2. **The projection ladder is one task.** 0.8831 (84 lossless columns) losing to
   0.9871 (6 column heights) cuts *against* generality.
3. **21 JEV demos support the shape and say nothing about transfer.**

---

## 2. The app — a real practitioner job

**`sift`: "the tool said the wrong thing. Which line of my code is it?"**

Not a toy. It runs on the real source of 36 real repos on this disk. The
observations are **real failures harvested by executing real local tools this
session**, plus real in-repo defects the repos document about themselves. Nothing
is injected.

```
$ python3 chain_lint.py --self-test
  SELF-TEST (the two bugs this file shipped with)
    [PASS] 16-zero hash is ZERO, not LINKED
    ... 7/7 PASS ...
Traceback (most recent call last):
  File ".../chain_lint.py", line 170, in <module>   sys.exit(main())
  File ".../chain_lint.py", line 139, in main       res, err = measure(int(sys.argv[1]) ...)
ValueError: invalid literal for int() with base 10: '--self-test'
```

The tool's own self-test flag crashes, because `main()` never dispatches it. That
is a real bug a real person hits today, and it is one of my five observations.

| id | tier | file | real root cause | where the oracle comes from |
|---|---|---|---|---|
| OBS-01 | A (traceback) | `chain-lint/chain_lint.py` | `main@131` | real 2-frame traceback, executed this session |
| OBS-02 | A (traceback) | `readme-verifier/census.py` | `<If>@38` | real 1-frame traceback, executed this session |
| OBS-03 | B (symptom) | `chain-lint/chain_lint.py` | `is_zero@52` | the file's own docstring, **BUG 2** |
| OBS-04 | B (symptom) | `chain-lint/chain_lint.py` | `is_zero@52` | the file's own docstring, **BUG 1** |
| OBS-05 | B (symptom) | `fleet-triage/resolver.py` | `extract_citations@384` | `RESOLVER-DEFECT.md`, post-mortem |

**Enumeration (deterministic, no judgment):** every top-level def/class, every
method, every module-level statement block, in source order, as
`file::qualname@line`. 4–13 real candidate sites per observation.

**Render:** two styles, `source` and `sig` — because "specific is the render" is
half the claim and swapping only the judge would leave that half untested.

**The seam, in full:**

```python
class Chooser(Protocol):
    def choose(self, options: tuple[Option, ...], ctx: View) -> Decision: ...
```

`Decision(pick, probs | None, confidence | None, source)`. **No judge needed a
second method.** That much of the claim survives.

---

## 3. The judges — four, structurally different

| judge | what it is | class |
|---|---|---|
| `free-stat` | a fixed weighted sum of the render's feature vector | no model, no key, no net, no file |
| `evidence` | regexes the candidate's **own source text** (`argv`, `int(`, guards) + file recency | different *kind* of evidence, can err differently |
| `human` | reads a person's picks from a file; returns `probs=None` | a person, who has no distribution |
| `model-jev` | the real `JEV-CONTRACT.md` client, `criteria` = the option set | a model |

**`model-jev` is BLOCKED, and that is a measurement, not a gap I papered over.**
Probed this session:

```
POST https://api.typesafe.ai/v1/systemone   ->  HTTP 401
{"error_type":"authentication_error","message":"Cannot authenticate with the server."}
```

`TYPESAFEAI_KEY` is absent from this environment (`exp-02/harness.py:285` records
the same for an earlier lane). **10/10 decisions blocked, 0 scored.** A 401 is a
missing credential. It is not evidence about the request, it is not a wrong answer,
and **its per-decision cost is reported as UNMEASURED, not as zero.** So the token
column below is empty for a reason, and that reason is the honest one.

---

## 4. Results

### 4.1 The app diff on judge swap: ZERO

```
  seam.py        before 3dcc6d98b7431de33c1cf5a58aa67824  after 3dcc6d98b7431de33c1cf5a58aa67824  IDENTICAL
  app_sift.py    before e983fefb2eeb1104a113b20f4119ce41  after e983fefb2eeb1104a113b20f4119ce41  IDENTICAL
  ---- diff -u _snapshot/app_sift.py app_sift.py  (verbatim) ----
  <no output>
  ---- diff -u _snapshot/seam.py seam.py  (verbatim) ----
  <no output>
  app diff = 0 lines; seam diff = 0 lines
```

**C1 and C2 pass.** The app holds state, enumerates, and renders; it calls
`choose()` once and returns whatever came back. It never sorts by preference.

### 4.2 Cost per decision

```
  judge        runs  net  tok_in  tok_out  enum_ms  choose_ms   conf  probs
  free-stat      10    0       0        0    6.067     0.0660  0.138   24.0
  evidence       10    0       0        0    6.076     0.7132  0.382   24.0
  human          10    0       0        0    5.311     0.0088    nan    0.0
  model-jev       0   10  UNMEASURED -- TYPESAFEAI_KEY absent (probe: HTTP 401)
```

- `enum_ms` is **the app's** cost and is judge-independent (5.3–6.1 ms): that is the
  "general-purpose" part, and it is ~90× the cheap judges' entire cost.
- `free-stat` decides in **66 µs** with zero network. `evidence` costs **713 µs**,
  10.8× more, for a *different* answer.
- The spread between the two free judges is the whole argument for having a seam
  at all: **the same app, the same options, 66 µs vs 713 µs, and they disagree.**
- `human` returns `probs=None, confidence=None` and the app does not care. That is
  the contract earning its keep in one line.

### 4.3 Accuracy against the oracle

```
  judge        OBS-01  OBS-02  OBS-03  OBS-04  OBS-05   TOP1    MRR
  free-stat       HIT      #4      #7      #7     #29 1/5     0.657
  evidence        HIT     HIT      #7      #7     #29 2/5     0.103
  human           HIT     HIT     HIT     HIT     HIT 5/5     0.131  <- UNSCORED: I wrote this key
  model-jev     BLOCK   BLOCK   BLOCK   BLOCK   BLOCK 0/0     0.000
```

**I do not score the human arm as a competitor, and I want to be blunt about why:
I wrote the answer key.** 5/5 there is my own knowledge leaking into a table that
looks like a result. It is a plumbing check — it proves the seam admits a chooser
with no distribution — and nothing more.

**Both free judges are 0/3 on tier B.** Split by tier:

```
  free-stat   tier A: 1/2 top-1   mean lift 1.70
  free-stat   tier B: 0/3 top-1   mean lift 1.38
  evidence    tier A: 2/2 top-1   mean lift 6.58
  evidence    tier B: 0/3 top-1   mean lift 8.34
```

Where the practitioner has a **traceback**, the cheap judges are fine. Where they
have a **wrong output and a hunch**, both are at zero. The traceback is not one
feature among seven; it is most of the signal.

### 4.4 Did they disagree, and who was right

They disagreed on **4 of 5** observations. Distributions, never collapsed:

```
  OBS-04  truth = is_zero@52
    free-stat  pick=<Expr>@2   conf=0.077   <Expr>@2=0.077  <BASE>@29=0.077  <UA>@30=0.077
    evidence   pick=main@131   conf=0.719   main@131=0.719  <BASE>@29=0.037  <Expr>@2=0.023
    human      pick=is_zero@52 probs=None conf=None
    -> DISAGREE on 3 distinct picks

  OBS-05  truth = extract_citations@384
    free-stat  pick=<Expr>@2   conf=0.013   <Expr>@2=0.013  <HERE>@48=0.013  <CACHE>@52=0.013
    evidence   pick=main@1569  conf=0.082   main@1569=0.082  <CACHE>@52=0.018  walk_tree@133=0.018
    human      pick=extract_citations@384 probs=None conf=None
    -> DISAGREE on 3 distinct picks
```

`free-stat` on OBS-04 returns `conf=0.077` over 13 options. **1/13 = 0.0769.** That
is the uniform distribution, to three decimals. It was not hedging — it had
nothing to discriminate on.

**And the dangerous one: `evidence` is confidently wrong.** On OBS-03/04 it returns
`conf=0.719` on `main@131`, which is not the root cause. A cheap judge that is
*uncertain* is harmless; a cheap judge that is *confident and wrong* is what this
account has been shipping as a finding for two days. The seam's distribution would
have flagged it — **but only if you had an oracle, and the whole point is that you
usually don't.**

### 4.5 The oracle was verified by execution, not asserted

```
  OBS-01      chain-lint --self-test
    BEFORE repair: exit 1  symptom present: True   ValueError: invalid literal for int()
    AFTER  repair: exit 0  symptom present: False  self-test ran, 7/7 PASS, no traceback
  OBS-03/04   is_zero() self-test  -> 7/7 controls PASS, 0 FAIL, no 'SELF-TEST FAILED'
  OBS-05      extract_citations() negative control
              -> PASS: 'NEGATIVE CONTROL: the old code really did leak 977'
```

Repairs applied to **copies**; originals untouched. One correction to my own work:
my first pass scored OBS-03/04 as failed because the process *also* hit OBS-01's
crash after the self-test printed. That is a check firing on a different
observation's symptom — I narrowed it to count `[PASS]`/`[FAIL]` and to look for
`SELF-TEST FAILED` specifically.

### 4.6 What the app gave up to get the seam

The contract lets a judge assume all seven features exist. An app that cannot
honestly produce one must supply a neutral **and declare it**. I counted the
declarations:

```
  OBS-01 (A)  fabricated ['depth']                        = 1/7
  OBS-02 (A)  fabricated ['depth']                        = 1/7
  OBS-03/04/05 (B) fabricated ['depth','in_trace']        = 2/7
```

**Specific cost, and it is not small:** in `sift` the app is made to *track traceback
depth for every candidate that is not on the traceback* — a quantity that does not
exist for those candidates — purely so the judge's weight vector stays total. That
is expressiveness spent on schema compliance. A judge that wanted to know "was this
site ever on any stack?" has to be told `-1`, and `-1` is not the same answer as
`no`.

### 4.7 C3 — THE LOAD-BEARING TEST

Second app, **`sort`**: *"7 files changed, 90 minutes before the cut, what do I read
first?"* Different state type, different enumeration, different render, different
question. Not a rename. The judges are imported **unedited**, sha-verified.

```
choosers.py sha256 (written for sift, imported unchanged):
    d210e88c1377159ca29286667c2c59524815bccec25aff1791637c001f031935
  judges edited to make this work: 0   (sha unchanged: True)

  free-stat   pick=docs/README.md#hunk     conf=0.1429  README.md=0.143 CHANGELOG.md=0.143 chain_lint.py=0.143
  evidence    pick=docs/CHANGELOG.md#hunk  conf=0.1487  CHANGELOG.md=0.149 chain_lint.py=0.149 Cargo.lock=0.149
  human       pick=chain-lint/chain_lint.py#hunk  probs=None conf=None
  model-jev   BLOCKED — TYPESAFEAI_KEY absent (not scored)

  sift  fabricated 2/7  ['depth','in_trace']
  sort  fabricated 5/7  ['depth','has_literal','in_trace','named','same_file']
```

**7 options, `conf = 0.1429 = 1/7`.** That is the uniform prior, exactly.
`evidence` gives 0.1487 — also uniform to rounding. **Both free judges ran
byte-identically in a new app and returned nothing.** The truth,
`chain-lint/chain_lint.py`, is option 3 of 7 and neither judge moved toward it.

**C3's mechanical test passes and its semantic test fails, and that is the finding.**
The coupling was not removed. It was **relocated from the code into
`FEATURE_SCHEMA`** — and a schema is data, so a byte-diff reports zero and a
sha256 reports zero, and both of them are telling the truth about the *files* and
nothing at all about the *coupling*.

---

## 5. What this does and does not support

**Supported, narrowly:**
- C1/C2. A real app can hold state, enumerate legally, and render, with a
  one-method seam and **zero bytes of app diff** across a free statistic, a
  source-reading judge, and a human. That is a real, cheap result.
- The seam admits a chooser with **no distribution** without special-casing.
- A judge swap is genuinely cheap: 66 µs vs 713 µs for two free judges, and the
  expensive-looking one changes its answer.

**Not supported:**
- **C3, the actual claim.** A judge that transfers unchanged is a judge that
  transferred *nothing*. In the transfer app 5 of 7 of its input was a neutral
  placeholder and its output was the uniform prior.
- Nothing here licenses extracting *choosers* rather than *apps* at fleet scale.
  n=5 observations, 3 of them from one file, 2 sharing one oracle. **This is enough
  to falsify a claim. It is not enough to support one** — and I am the one
  proposing it.

**On my own three concessions, now with numbers:** `lau-git-render` was never
switched on, and I now think that is not bad luck, it is the predicted outcome.
**A seam that nothing transfers through is indistinguishable from a folder.** The
projection ladder's 0.8831 → 0.9871 is looking more like the central fact than a
narrow one: when you have a fixed task, the specific representation wins, and
"general" mostly means "has somewhere to put the parts you did not need."

---

## 6. The strongest case AGAINST my own position

> **The seam is not a boundary, it is a namespace.** A judge transfers unchanged
> only when the new app can fill the vocabulary the judge already speaks — and the
> measure of that is not the diff, which is zero by construction, but the lift,
> which was 1.00. I ran the experiment that separates "reusable" from "portable":
> a second app, a real job, sha-verified judges, zero edits, and both free judges
> returned the exact uniform distribution while the app paid 5 of 7 fabricated
> features to keep the contract satisfied. Worse, the one place the judges *were*
> right (tier A, 3/3 combined) they were right because of `in_trace` and
> `touches_argv` — features that only exist because the practitioner happened to
> have a traceback. So the thing that transfers is not the judgment, it is the
> *evidence type*, and evidence types are not units of reuse; they are a list.
> Meanwhile the projection ladder already said the more specific representation wins
> (0.9871 > 0.8831) and `lau-git-render` already said a seam nobody uses is worth
> zero — and I treated both as narrow. The honest reading of the whole account is
> that **specific is not what you extract; specific is what you keep, and you keep
> it by paying for it app by app.** The fleet's 5,127 apps are not a failure to
> abstract. They are the correct number of things, each of which was allowed to be
> right.

## 7. What I would need to change my mind

A judge that, in `sort`, returned a **non-uniform** distribution *and* was not
re-edited. Concretely: either the contract is small enough that most apps can fill
it honestly (≤2 fabricated features), or the judge reads the *rendered text*
rather than a fixed feature vector, so that a new app's richer render is
information the judge can actually use. Either would make the zero diff mean
something. Right now it means the vocabulary is empty, and I have measured that in
the only currency that counts.

---

### Reproduce

```
python3 debate-A-code/obs_build.py       # re-harvests the real observations by execution
python3 debate-A-code/run_debate.py      # tests 1-5
python3 debate-A-code/transfer.py        # C3
python3 debate-A-code/repair_verify.py   # oracle level 2, on copies
```

`model-jev` requires `TYPESAFEAI_KEY`. Without it, 10 decisions are counted BLOCKED
and its cost stays UNMEASURED.
