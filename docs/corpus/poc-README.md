# Three proofs of concept, built from a practitioner's chair

2026-10-02. Casey asked for proofs of concept built *from the context of a
practitioner* — a person with a real task today who does not care about our
architecture. So: three small tools, three different problems, each runnable
by a stranger in under a minute, each with real output from this session.

They are not three variants of one demo. They are three different questions
about where this API earns its place, and **two of the three answers are
negative**. The negative results are the reason to read this.

Everything below is real output from this session. Nothing is projected.

---

## What is in here

| file | problem | API calls | wall clock |
|---|---|---|---|
| `draftcheck.py` | a draft's `path:line` refs and arithmetic | **0** | 0.06 s |
| `route.py` | a workflow step that answers *or refuses* | **4** | 0.9 s |
| `second_opinion.py` | a second opinion on a decision already made | **4** | 1.0 s |
| `jevc.py` | shared client + a live contract check | 1 | 0.3 s |

Run any of them:

```
cd poc
python3 draftcheck.py ../README.md
python3 route.py --sweep
python3 second_opinion.py
python3 jevc.py                 # proves the three request shapes are right
```

Stdlib only. No pip install. No network for tool 1. `${TYPESAFEAI_KEY}` is
never printed — `jevc.py` reads it from the environment and falls back to a
known artifact, and the value appears in no log line, no exception, and no
output.

---

## A correction to `JEV-CONTRACT.md`, found the hard way

The contract documents `score` as taking `levels: [ordered strings]`.
**That is wrong and the API rejects it with HTTP 422.** The field is `criteria`
and it is a **list**:

```
questions.sev.score.criteria  Field required
```

`choice` takes `criteria` as an object of `{label: null}`; `score` takes
`criteria` as a list. Same field name, two different types. A contract
document that says "they have different shapes" and then gets one of them wrong
is worse than no contract, because it looks authoritative.

Two more differences, both found by running code rather than reading:

1. **`noul` returns a scalar with no distribution.** No `confidence`, no
   `probabilities`. So the rule *"never collapse a distribution to a scalar"*
   is **structurally impossible for `noul`** — there is no distribution to
   preserve. Any tool that wants calibration on a `noul` must get it
   elsewhere. Verified live:
   `noul=0.59 <-- scalar only: NO confidence, NO probabilities`.

2. **`score` keys `probabilities` by index (`"0"`,`"1"`); `choice` keys it by
   the label string.** Code written for one breaks on the other. This one
   happens to fail loudly (`int("approve with a note: ...")` raises), which is
   the good case.

`python3 jevc.py` re-proves all three shapes against the live service in one
call, so this cannot rot again unnoticed.

---

## Tool 1 — `draftcheck.py`, the draft checker

**The problem.** You are about to hit send on a README. Somewhere in it is
`resolver.py:412` and that file has 380 lines, or `3 + 4 = 12`. You will not
notice. This is the resolver's capability, aimed at a person instead of a fleet.

**What it checks.**

- every `path:line` that does not resolve, and every one whose line number is
  past the end of the file
- every numeric claim whose own stated operands disagree with it
  (`126 of 140 is 95%`, `3 + 4 = 12`, `half of 100 is 60`, `a third of 90 is 40`)

**Zero API calls.** This is the resolver, wrapped for a human. It is the only
one of the three that a practitioner could run with no network, no key, and no
budget.

### The false-positive rate — the number that matters

I ran it over **128 real human-written documents from this account** (every
`.md` in `fleet-triage/`), against **215 resolution roots** (the 280-repo
`repos/` tree plus sibling projects plus `/workspace/repos/`). 15 ms per
document.

The raw output was **471 findings**. Almost all of them were noise, and finding
out *why* is the actual result of this exercise.

A finding is called **BROKEN** only when the tool can stand behind it, and
**unconfirmed** otherwise. The tool separates these on purpose:

| class | count | what it means |
|---|---|---|
| `unresolved-path` | 75 | first segment is a generic source dir (`src/`, `tools/`) — a within-repo citation we can actually adjudicate, and it matches nothing |
| `ambiguous-path` | 217 | bare filename, no directory (`README.md:91`) — may belong to another repo |
| `unverifiable-repo` | 80 | first segment names a repo we do not have on disk |
| `range-ambiguous` | 88 | the path matches **N different files**; a line number is meaningless against an arbitrary one |

**Then I checked every one of the 75 BROKEN findings against a workspace-wide
index of 211,312 real files.**

> ### 54 of 75 were false positives. **False-positive rate: 72%. Precision: 28%.**

That is the honest answer, and it is a bad one. On ordinary prose — not
adversarial input, 128 documents written by humans and agents for themselves —
this tool cries wolf roughly three times out of four.

**Where the errors came from.** Not from sloppy regexes. From the tool not
knowing what it does not know:

- `src/lib.rs` exists in **117 of the 280 repos** on this account. A directory
  component disambiguates nothing. An early version range-checked line 2403
  against whichever 61-line `src/lib.rs` sorted first and reported a confident,
  entirely fabricated finding.
- `.quilt/bin/quilt-adjudicate:195` lives in a repo that is not cloned here.
  "Not found" and "broken" are different claims and the tool was conflating
  them.
- `1+4+6+1+1+1 = 14` was reported as a defect. The arithmetic was **correct**;
  the rule had matched the first two operands and compared them to the sum of
  all six. A sum is not a binary operator applied once.

### Three bugs the measurement caught, and one regression I caused

Worth recording, because the regression is the instructive one.

1. **Group-index shift.** `NUM` was a capture group, so every rule's group
   numbering was off by the nested groups. It printed `126 of 95 is 132.6%,
   not 140%`. Rewrote the numeric engine with named groups.
2. **Case-sensitivity.** `Half of 100 is 60` never fired because the fraction
   table was lowercase and the regex was not `IGNORECASE`. Two seeded defects
   were silently uncaught.
3. **Multi-term arithmetic.** Fixed as above.
4. **The regression I caused.** To kill the cross-repo noise I suppressed
   range-checks for any path without a directory. That silently destroyed the
   **entire `line-out-of-range` class: 8 findings → 0.** The FP number looked
   better and the tool had stopped checking. Suppressing a class to make a
   metric look good is the defect, not the fix. The correct rule is a *match
   count*: if the path resolves to exactly one file, range-check it and call it
   broken; if it resolves to many, say so and decline.

**One claim I had to retract.** I first reported `src/dcs.rs:9` in
`AGENT-ENTRY.md:171` as a true positive — "the file exists in none of the 280
repos". The wider index found it at
`/workspace/projects/constraint-theory-core/src/dcs.rs`, a sibling project I had
never searched. It was a false positive like the rest. I only caught it because
I built the ground truth from a wider corpus than the one I was testing
against.

### What it would take to actually ship

The FP rate is not a tuning problem. **It is a missing-input problem**, and
the fix is one argument:

```
python3 draftcheck.py --root <the repo this doc is about> README.md
```

The corpus here is pathological — documents that are *reports about 280 other
repos*, where "which repo does this citation belong to" is genuinely
unanswerable. Pointed at one repo, with one root, the tool's job is well
posed. **I have not measured that case**, and I am not going to quote a number
I did not measure. It is the first thing to do next.

### Control

A checker that never fires is the vacuous-suite failure mode, so the detector
is run against a seeded document with known defects. It catches **6/6 seeded
defects** and **0/12 correct claims** in the same file (`70 of 100 is 70%`,
`3 x 4 = 12`, `a quarter of 80 is 20`, `resolver.py:12`, `README.md:1`,
`12:30`, `e.g.`, `cf.`, `note:3`, an `http://` URL, a fenced code block).

---

## Tool 2 — `route.py`, the decider that declines

**The problem.** A workflow step that returns an answer *or refuses*, and is
useful either way. The primitive that makes refusal possible is measured: a
`score` on ordered levels returns a continuous position, a `confidence`, and
the full `probabilities` map, and **confidence tracks the separation of the
distribution, not its height**. The routing is the product; the answering is
incidental.

### A batching trap that silently destroys the tool

The contract says *"questions evaluate independently against one shared state
and adding questions does not significantly increase response time — so ask a
battery, not a question."* That is true, and it is the most dangerous sentence
in the document.

The first version put **all four cases into one shared state** and asked both
questions once. Every case came back with **byte-identical answers** — gate
0.16 for all four:

```
cosmetic-typo        ABSTAIN    0.16
duplicate-charge     ABSTAIN    0.16
auth-bypass          ABSTAIN    0.16
dead-dependency      ABSTAIN    0.16
```

The model scored the *batch*, not the cases, and returned a confident uniform
answer. No error, no warning, a plausible-looking tool. Batching applies to
**questions about one state**, never to **items in one state**. The fix is one
call per case with a battery inside it — 4 calls instead of 1, which is the
correct price.

### The gate, and the veto that is not the threshold

Real output, threshold 0.60, one call per case, battery of two `score`s:

```
case                 verdict    gate  severity band/conf        decidable band/conf
----------------------------------------------------------------------------------------
dead-dependency      ABSTAIN    0.49  L3 0.91  [0:0.01 1:0.03 2:0.00 3:0.96]   L0 0.49  [0:0.54 1:0.42 2:0.04 3:0.00]
auth-bypass          ABSTAIN    0.54  L3 0.54  [0:0.04 1:0.09 2:0.15 3:0.72]   L2 0.89  [0:0.02 1:0.05 2:0.91 3:0.02]
cosmetic-typo        CALL       0.62  L0 1.00  [0:1.00 1:0.00 2:0.00 3:00]      L0 0.62  [0:0.79 1:0.07 2:0.12 3:0.02]
duplicate-charge     ABSTAIN    0.74  L3 0.74  [0:0.00 1:0.03 2:0.19 3:0.78]   L2 0.99  [0:0.00 1:0.00 2:1.00 3:0.00]

CALL    (1): cosmetic-typo
ABSTAIN (3): duplicate-charge, auth-bypass, dead-dependency
```

Note the distributions are printed in full and never collapsed to the argmax.
`duplicate-charge` peaks at 0.74 for a verdict and the gate sits at 0.99 on
decidability — a confident *refusal*.

**The bug this exposed.** `min(severity_conf, decidable_conf)` alone is wrong,
and measurably so. `auth-bypass` came back with decidability = L2 ("a human
must look") at confidence 0.89–0.93 — nearly all the mass — while severity sat
at 0.54. `min()` let the *low* number dominate, and the case was **CALLED** at
threshold 0.50. A crisp opinion about *how bad* something is must not buy
permission to skip asking whether anyone can *tell*.

So there are two independent conditions and either one routes to a human:

1. **The veto** — the decidability distribution puts real mass on "a human must
   look". This fires at *every* threshold.
2. **The threshold** — both confidences clear it.

With the veto, the tool agrees with hand labels written before the calls on
**4/4** cases. Without it, 2/4.

### The threshold that moved a case from one to the other

```
 threshold  CALL                 ABSTAIN
      0.55  cosmetic-typo,dead-dependency   auth-bypass,duplicate-charge
      0.60  cosmetic-typo         auth-bypass,dead-dependency,duplicate-charge   <-- dead-dependency flips
      0.65  -                     auth-bypass,cosmetic-typo,dead-dependency,duplicate-charge   <-- cosmetic-typo flips
```

`dead-dependency` is called below 0.55 and abstained at 0.60.
`cosmetic-typo` is called below 0.65. `auth-bypass` and `duplicate-charge`
never flip, because the veto holds them.

### The honest caveat: the gate is not stable

Three consecutive runs, same input:

```
run: auth-bypass=0.48*  cosmetic-typo=0.65  dead-dependency=0.51  duplicate-charge=0.69*
run: auth-bypass=0.57*  cosmetic-typo=0.62  dead-dependency=0.51  duplicate-charge=0.75*
run: auth-bypass=0.52*  cosmetic-typo=0.65  dead-dependency=0.54  duplicate-charge=0.74*
```

Non-vetoed gates drift **±0.03–0.04**; vetoed ones drift **±0.09**. Any
threshold set within 0.05 of a case's gate is a coin flip on a given day.

**Both vetoed cases were vetoed in every single run.** That is the design
result: *the veto is the stable signal and the threshold is the fragile part.*
A practitioner should trust the refusal and treat the boundary as soft.

**A refusal mode that never refuses is a log line, and this project has 23 of
them.** This one abstains 3 times out of 4, and a stranger can watch it do it.

**Cost: 4 calls, ~600 in / 32 out tokens, median 177 ms.** Exits 0 whether it
calls or abstains, because a refusal is a successful run.

---

## Tool 3 — `second_opinion.py`, the second opinion

**The problem.** Someone already made a decision. Read the *stated reasoning*
and ask whether the evidence supports it — not whether the conclusion is
popular, and not whether it agrees with the other reviewer.

**The interesting bit, and it is the whole project.** Most reviewers are
correlated, and a correlated panel is worth about two votes. So agreement is
close to worthless information. The useful output is the place where this
reviewer **disagrees with the recorded one**. The tool prints disagreements
first and loudest.

Each case asks three questions in one call: what the evidence supports on its
own terms, what a *generic* reviewer would say (the correlation control), and
how sufficient the stated evidence actually is.

### The disagreement I think is right

```
[drop-retry-block]  recorded: APPROVE  <<< DISAGREEMENT
   evidence sufficiency: score=1.75 conf=0.62
      SUPPORTS CLAIM 0.62  EVIDENCE TOO THIN 0.31  ESTABLISHES CLAIM 0.07  NO EVIDENCE 0.00
   what a generic reviewer would say : APPROVE (note)
   what the EVIDENCE supports        : APPROVE (note) (confidence 0.21)
     approve with a note: ... 0.47  request changes: the ... 0.36  approve: the evidence... 0.17
```

The recorded reviewer approved deleting a payment webhook's entire retry block
(40 lines) on the reasoning that *"the retry caused duplicate charges in
incident 4471, seen twice in 90 days, confirmed by the support tickets."*

The tool parts company, and I agree with it. The chain has three unclosed
links: **two events in 90 days cannot establish causation**; nothing states
that the retries and the duplicate charges are the same events; and a support
ticket is a report, not a diagnosis. Only **0.07** of the sufficiency
distribution says this evidence *establishes* the claim.

The confidence is **0.21** and the split is 0.47/0.36/0.17 — the model is
genuinely undecided, and that undecidedness *is* the finding. A tool that
returned "APPROVE (note) 0.47, done" would have been less useful than one that
says "I do not know, and here is exactly why the evidence does not close".

### The correlation control

```
'what a typical reviewer says' matched what the EVIDENCE supports: 4/4
'what a typical reviewer says' matched the RECORDED verdict:      3/4
```

The generic-reviewer question tracks the evidence more closely than it tracks
the recorded panel — so on these four cases it is a **live control**, not a
restatement of the panel.

That is the good outcome, and it is also the **warning**: 4/4 and 3/4 on four
cases is a sample far too small to claim this reviewer is independent. The
right reading is that the control is *currently not firing*, not that
independence has been established. On a panel of `jev` reviewers correlated
this tightly, the control is what would catch it.

**Cost: 4 calls, 2348 in / 672 out tokens, median 185 ms.** The most expensive
of the three, because the state carries the full change description and the
recorded reviewer's reasoning.

---

## Which one a practitioner keeps, and which one I would not hand to anyone

**Kept after a week: `route.py`.** It does one job, it does it in under a
second for four cases, and its two most important properties are ones a
practitioner can *see* rather than trust. The tool visibly abstains. The tool
visibly declines to flatten a distribution into a verdict. And when I ran it
three times in a row it told me the truth about itself: the gate wobbles, the
veto does not. A workflow owner can read that output at a glance and decide
where to put the threshold. There is no configuration here that hides a
failure, and the exit code is 0 whether it acts or refuses, so it can sit in a
pipeline without being disabled by someone who mistook a refusal for a crash.

**Second: `second_opinion.py`, narrowly.** It is the most *interesting* of the
three and the one whose output a reviewer would actually argue with. The
`drop-retry-block` disagreement is a real finding and the correlation control
is the right instrument. But four cases is a demo, and a 4/4-versus-3/4 control
result is not evidence of independence. I would hand it to a colleague as a
thing to try on their own review queue, and I would not put it in front of
anyone as a decision-maker.

**I would not hand `draftcheck.py` to anyone, in its current state.** A 72%
false-positive rate is not a tuning gap; it is a tool that will be muted within
a day. The practitioner test is not "does it find things" — it does, it found a
real broken citation in `AGENT-ENTRY.md` and 6/6 seeded defects. The test is
"can I act on its output without checking it first", and the answer today is
no, because 54 of its 75 confident claims were wrong.

The uncomfortable part is that the concept is sound and the implementation is
not the bottleneck. The bottleneck is that the tool is asked a question it
cannot answer — *which repo does this citation belong to* — and answers it
confidently anyway. The fix is not a better regex; it is refusing to answer
without being told the root, exactly the lesson tool 2 learned the hard way
about its own threshold.

---

## The through-line, which I did not expect

Two of the three tools failed the same way, and it is the same failure as the
`quilt-jepa` reseal-forgery and `moth-honest` defects already in this fleet's
record: **a mechanism that stops at *tamper-evidence* and calls itself
*tamper-proof*.**

- `draftcheck` proved it could *detect* a citation it could not *locate*.
- `route` proved it could *classify* a case it could not *resolve*.
- `second_opinion` is the only one that ships an instrument for catching itself
  (the correlation control), and the instrument is the part that matters.

A tool that reports what it checked is worth more than one that reports what it
found. Every fix in this session was of that shape: downgrade a claim you
cannot support, print the distribution instead of the argmax, count the matches
before you range-check one of them, and re-measure against a corpus wider than
the one you are testing on.

---

## Reproducing

```
cd /workspace/projects/fleet-triage/poc
python3 jevc.py                                     # 1 call, proves the contract
python3 draftcheck.py ../AGENTS.md                  # 0 calls
python3 draftcheck.py --sibling-repos ../repos ../DEMO.md
python3 route.py --sweep                            # 4 calls
python3 route.py --threshold 0.60
python3 second_opinion.py                           # 4 calls
```

Requires `${TYPESAFEAI_KEY}` in the environment. If it is absent, `jevc.py`
falls back to reading it from a known fleet artifact and **never prints the
value** — the variable name is the only thing that appears anywhere in this
repository.
