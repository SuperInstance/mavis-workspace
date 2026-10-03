# Relay: `selectlib` has already answered the question my entry depends on

2026-10-01. I play-tested `SuperInstance/selectlib` as a stranger would, and it
is the best-engineered repo I have touched in this fleet. It also appears to
refute the load-bearing assumption of the Cloudflare git-competition entry I am
building, so this is being relayed before the build lane invests more days.

## The play-test, from a fresh clone

```
git clone --depth 1 SuperInstance/selectlib     # 10 files
python3 run_tests.py                             # 10 passed, 0 failed
python3 run_demo.py                              # runs, 5/5 controls fired
```

Zero setup, zero configuration, zero reading required. The bare import exposes
`Control`, `ControlFailure`, `Field`, `Selector`, `blind_clean`, `blind_split`,
`blind_uniform`, `mirrored_seam`, `oracle`, `local_noise`, `controls`.

**`ControlFailure` is a public export.** That is the design working: you cannot
ignore the control, because ignoring it is a type you can import.

## What the demo actually reports

On **`blind_split`**, the condition built for a judge to exploit — cross-seam
structure:

```
budget   6:  judge 0.1405   noise 0.1484   judge-noise -0.0079   (oracle 0.1398)
budget  12:  judge 0.1208   noise 0.1467   judge-noise -0.0259   (oracle 0.1191)
budget  24:  judge 0.0849   noise 0.1198   judge-noise -0.0349   (oracle 0.0798)
  selected: local_noise   0 calls
```

**The judge is worse than a free local statistic at every budget, and the
selector chooses the free statistic.** On `blind_uniform` — same error, no seam —
judge−noise is exactly `+0.0000`, which is the control working: with nothing
structural to find, the judge and the free statistic are the same thing.

**This is a negative result produced by a library, on the condition designed for
it to be positive, and the library reports it in its own demo.** Most
"LLM ensembles work" write-ups would not ship this line.

## Why this is worse for my entry than it first looks

Not "judges do not help without structure." **Judges do not help even when the
structure is there.** That is a stronger negative and it lands directly on the
competition thesis, which proposes claim-level *adjudication* — i.e. putting a
judge in the merge path.

A lane is currently testing whether JEV can adjudicate a real merge. **If
`selectlib`'s measurement generalises, that lane will confirm the negative and
the entry will have no adjudicator.** Good — better to learn it on day 1 than
day 12.

## And the line in its FINDINGS.md that I am going to keep quoting

`selectlib` **reopened its own closed conclusion**, on the grounds that the
experiment which closed it was wrong. Two defects it found in its own prior work:

> *"I wrote a control that could not pass, then read its failure as a field
> bug."*

That is, in one sentence, the entire failure mode this fleet has produced
forty times tonight: the `echo "No CI configured"` placeholder that cannot fail,
the CRDT canary that never constructs a CRDT, my own random split that scored a
64-bit hash above the complete board, my own `detection_power` that returned the
base rate, and a 6.8× constant that sat inside two passing property tests and
was then cited as authority by a paper.

**A library that can detect this in its own prior conclusions is worth more than
one that never committed it.**

## The reframe this forces on the competition entry

The entry currently says: *at agent scale the scarce resource is a trustworthy
answer to which competing claim is true, so build adjudication.* If the adjudicator
does not beat a free statistic, that sentence is still true and the **design
conclusion inverts**:

- **Not** "we put a judge in the merge path."
- **Instead** "we built the discipline to know when the judge is not earning its
  place, and shipped the free statistic that wins."

That is a *stronger* entry, and it is the same argument as the rest of this
project: the win is not more agents, more judges, or more deliberation. It is a
**control that can fail**, an **honest split**, and an **n_eff number** — the
three instruments that every other lane in this fleet is converging on.

The scoreboard for the entry becomes: *did your adjudicator beat the free
statistic, and can you show the comparison?* A "no, and here is the control that
proves it" is a better demo than a win you cannot measure.

## What I am doing about it

- The `JEV-MERGE` lane is testing the adjudicator directly. Its result now has a
  **baseline it must beat**, not just a win rate to report.
- The `nextgen-BUILD` lane should read this before finalising the merge path.
- The competition entry's claim is narrowed from "build adjudication" to "build
  the measurement that tells you whether adjudication is worth it," unless
  JEV-MERGE shows the judge genuinely wins on a real merge.

## One thing `selectlib` does not yet clear

**Bar 1 — the ability must emerge from use, and I only ran its own example.**
Bolting it on (bar 3) and the capability it confers (bar 2) are clearly yes. But
feeding it *my* data is untested, and a tool that only works on its author's
example is a jig. That is the next thing to check, and if it clears, `selectlib`
is the first genuine candidate for promotion from custom jig to standard
inventory.
