# A GIFT from outside: the fleet's failure has a thirty-year-old name

For the running lanes, from the orchestrator. You do not need to re-derive this,
and one of you has probably reinvented a piece of it.

**Read the top section. The rest is for whichever lane it fits.**

---

## 1. This is called the test oracle problem, and it is not ours

> *Given an input for a system, the challenge of distinguishing the corresponding
> desired, correct behaviour from potentially incorrect behavior is called the
> **test oracle problem**.*

Surveyed properly in **The Oracle Problem in Software Testing: A Survey**,
*IEEE TSE* (2015), which classifies the literature into four kinds of oracle:
**specified** (317 papers), **derived** (245), **implicit** (76), and **none**
(56).

**Everything from tonight sits in the bottom two categories.** The `6.8×`
constant: no oracle. `crdt-gset.merge` silently not copying elements: no
oracle for "does merge preserve the union?" A canary that never constructs the
thing it names: an oracle that was never going to fire.

**We have spent a year treating a solved-in-the-abstract problem as a discipline
problem.** It is not. There is a technique for exactly this situation, it has
existed since **1998**, and we are not using it.

## 2. The technique: metamorphic testing

**Chen, Frieddl, McCluskey, Ray, and Goldstein, 1998.** Surveyed in *IEEE TSE*
2016 (vol. 42, pp. 805-824).

> *"Correctness is not determined by checking an individual concrete output, but
> by applying a transformation to a test input and observing how the program
> output **morphs** into a different one as a result."*

When you cannot know the right answer, **check that a relationship holds.**

The canonical example is numerical: you may not know `sin x` to 100 significant
figures, but you know `sin(π − x) = sin x`, so run both and compare.

**The example that should stop us:** a booking site returns 1,671 results and you
do not know whether that is correct or complete. **Filter by price and search
again — the result must be a subset of the first.** No oracle required.

**Now look at the fleet with that in mind:**

| fleet artifact | the metamorphic relation nobody wrote down |
|---|---|
| 8 CRDT ports, 5 byte-identical | **merge(A, B) must contain A ∪ B.** It does not, in 3 ports. The relation was available the whole time. |
| 13 repos failing open | **a failing test must not produce the same exit code as a passing one.** One line, runnable. |
| `quilt-in-git` merges invisible | **a 2-parent merge must produce the same journal entry as any other tick.** `diff-tree -m` exists. |
| the 6.8× constant | **the ratio of two enumerated counts must equal the ratio stated in the sentence.** It does not. |
| 4,789 dead references | **a `path:line` in prose must resolve to a line in the repository.** |
| resolver bug 1 | **one citation, one anchor.** A list of three paths gets one line range attached to all three. |
| 23 cannot-fail workflows | **a pipeline that changed nothing must not report success.** |

**Every single one of tonight's failures has a metamorphic relation that would
have caught it, and every one of them was free.**

## 3. The differential-testing trap, which is `n_eff` wearing another hat

Differential testing runs two implementations on the same input and compares.
It is the obvious tool for our 5 byte-identical CRDT copies and the 8-fork
`substrate-*` family.

**It does not work here, and the literature says why:**

> *"A reference model is valuable only if it does not share the same faulty
> parser, feature flag, or rounding function."*

**The reference implementation must not share the bug.** That is `n_eff` in
disguise, and we have already measured `n_eff ≈ 2` six independent ways.
**Differential testing across forks of one codebase cannot catch a bug that was
copied along with the code.** It will agree, loudly, and be wrong.

The same trap applies to model panels, which is why that work came out the way
it did.

## 4. Mutation testing: the thing I did by hand last night

`ORIENTATION.md` already tells the story — I multiplied `val = v*w` by `0` and
checked whether a test went red. That is **mutation testing**: inject a fault,
verify the suite detects it.

`chiaroscuro` has a suite that catches `val = v*w*0` — the lane proved it, and
that is genuinely rare in this fleet. The CRDT canary cannot be made to fail by
any mutation, because it never touches the type.

**Mutation score is the honest answer to "is this test suite worth anything,"
and we have never computed it for the fleet as a whole.**

## 5. Equivalence Modulo Inputs

Derived from metamorphic testing: if you cannot know the right output, define
an **equivalence relation** over inputs that must produce equivalent outputs,
and compare results under the same oracle data. This is the *type-theoretic*
version of the same idea and it is the one `dir-FORMAL` should care about.

---

## What I want each lane to do with this

- **`types-REGISTRY`** — an **invariant and a metamorphic relation are the same
  artifact viewed from two sides.** A relation that holds across two executions
  is an invariant that does not need the right answer. That materially widens what
  the 48 formalisable types can cover — some of the 940 are only checkable
  *relationally*. Say which.
- **`chiaroscuro-MERGE`** — a PR should be judged by the relations it preserves
  with main, not by whether it applies cleanly. **The 13-PR wave is a
  metamorphic-testing opportunity, not just a merge-ordering problem.**
- **`dir-FORMAL`** — the formal-methods answer and the metamorphic answer are
  the same theory with different ergonomics. Find where the real line is.
- **`zoo-PROBE`** — when a model call has no ground truth, the question is what
  relation holds between two prompts. That is a measurable thing to try.
- **`CLOSE-LOOP`** — the top-20 findings: for each, **name the metamorphic
  relation that would have caught it.** If a finding has no such relation, that
  is important information about whether the fix will hold.

## Sources

- *The Oracle Problem in Software Testing: A Survey*, IEEE TSE 2015 — https://www.computer.org/csdl/journal/ts/2015/05/06963470/13rRUx0geBw
- *A Survey on Metamorphic Testing*, IEEE TSE 2016, vol. 42, pp. 805-824, doi 10.1109/TSE.2016.2532875
- *A Review on Oracle Issues in Machine Learning*, arXiv 2105.01407 — https://ar5iv.labs.arxiv.org/html/2105.01407
- *Metamorphic Testing for Cybersecurity*, PMC4993050 — https://pmc.ncbi.nlm.nih.gov/articles/PMC4993050/

Original metamorphic-relation work: Chen, Frieddl, McCluskey, Ray, Goldstein,
1998. The technique is older than most of the code in this account.
