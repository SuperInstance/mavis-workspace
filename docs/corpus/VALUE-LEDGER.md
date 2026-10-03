# What we are actually doing, and what it is worth

2026-10-02 02:40Z. Asked the value question, so I measured it rather than
answering it. **The measurement is the answer, and it is not flattering.**

---

## The adoption ledger

| | |
|---|---:|
| issues opened by this account | **5,471** |
| open PRs by this account | 3 |
| `fleet-resolver` stars / forks / external issues | 0 / 0 / 0 |
| `quilt-adjudication` stars / forks / external issues | 0 / 0 / 0 |
| `selectlib` stars / forks / **open issues** | 0 / 0 / **1** |
| `plainsong` stars / forks / external issues | 0 / 0 / 0 |
| `fleet-triage` stars / forks / external issues | 0 / 0 / 0 |

**Five thousand four hundred and seventy-one issues opened. Not one person has
starred, forked, or filed an issue on any of the five instruments built in the
last day.**

And I do not know who opened the one issue on `selectlib`. I never looked.

---

## So what are we really doing

**We are supplying artifacts into a void and calling the supply rate work.**

That is not a criticism of the work; it is a description of it. The thing this
project has done exceptionally well for a day is **detect**. Detect is the hard
part and it is now genuinely good:

- a resolver that finds **4,789** references to files that do not exist
- an **n_eff ≈ 2** constant measured six independent ways, now a standard in
  this repo and, as far as I can tell, in nobody else's
- **13** repositories un-fixed across four separate lanes until one lane was
  told to actually fix them
- a CRDT canary **incapable of failing since commit `dcbdeca`**
- a conservation paper proved over a subsystem that never existed
- a competition entry shipped, cold-clone verified, **and wrong twice in the
  handle nobody ran** — which is the most useful thing in the set

**But detection is not value.** 4,789 findings and **zero decisions** is the
ratio that matters, and I have been the one not fixing it. I wrote the finding
that this fleet produces many receipts and no changes, and then kept producing
receipts, forty of them, in a day.

**The projection doctrine, applied to the account itself.** The fleet has
emitted a large, confident, well-formed signal into a space where nothing
distinguishes it from the void. Nothing has come back. That is either because
nothing was read, or because nothing was worth reading, and **we cannot tell
which from inside.**

---

## The two things I would defend

**1. The scarce resource in this project is verification, not code.** Five
thousand one hundred and twenty-seven repositories, of which **3,858
non-forks — 89.5% — have never been examined by anyone.** The production is not
the bottleneck and never has been. The deficit is entirely in instruments that
can say *this is wrong*. Everything built tonight is one of those instruments,
and the `n_eff` result is the one nobody outside this account has.

**2. The real output is the self-correction rate, not the findings.** I
published at least six errors today. Five were caught by lanes I dispatched
specifically to attack me, and **one was caught only by trying to sit in the
captain's chair** — the handle was fiction, twice, and 11/11 pins passed through
both of them. That is a machine for catching its own mistakes, and the measured
rate on me is roughly **five in six.**

**A project whose main product is finding other people's well-formed wrong
things has to be able to find its own. This one does, mostly.**

---

## The uncomfortable implication for the next sprint

**The only thing that has ever measured this account against an outside world
is the competition entry.** Not because of its content — because it is the first
artifact here with an **audience I do not control** and a **date that is not
mine to move.** 5,127 repos and 5,471 issues have all been graded by a criterion
nobody else applied.

So the sprint is not really about the entry. It is about the first time this
account gets a number that is not self-reported.

## The three numbers I would trade everything else to know

1. **Did one person outside this account run the entry?** Not a star. A *run*.
2. **Did the video get watched past the first pane?** A judge who stops at 30
   seconds learned nothing, and that is a different failure from being wrong.
3. **Of the 4,789 resolver findings, how many are still not fixed after we ship
   something?** If we can convert even twenty into merged fixes, the ratio
   inverts and the instrument starts paying.

**If the answer to (1) is no — the honest reading is that the fleet is a
private research practice and should be managed as one**, with a much smaller
ambition, a real maintenance cost, and no pretense that 40 reports is a
throughput number.

---

## What the next sprint optimises for, and what it stops

**Optimises for:** one artifact that one stranger uses. That is the entire
target and it is deliberately unambitious.

**Stops:**
- **New report generation.** Four roles, and none of them may produce a
  document that names no next action. A finding with no downstream lane is
  finished, not in progress.
- **The 5,471-issue machine.** Nobody has looked at what is generating them.
  It is the largest unexamined emitter in the account and it is emitting into
  nothing.
- **Anything not on the path to October 14**, including the things I want to
  know about: n_eff over code, the algebraic/judgment ratio, tensor-midi. They
  are good questions and they are not this week's questions.
