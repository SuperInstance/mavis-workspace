# What we can unlock as types — and why 940 of 988 of them are broken

2026-10-02. Casey supplied a list of 1,189 lines: **988 mathematical spreadsheet
types**, from set membership tables through Betti numbers, cellular automata,
Petri nets, and a verification table. I counted it before answering, because the
count is the answer.

**988 entries. 48 carry an explicit invariant or verification condition. 940 are
pure structures with no stated check.**

---

## What every one of those 988 entries actually is

Not a spreadsheet. **A proposition about a system, laid out in two dimensions.**

A truth table is a proof. A transition matrix is a dynamical system. A homology
group table is a topological invariant. A Cayley table *is* a group — the
structure isn't a way of recording the algebra, it is the algebra. A confusion
matrix is a statement about a classifier's behaviour under two labellings.

The mathematics is not in the data. It is in **which rows, which columns, and
which symmetry** — the schema. The cells are nearly always boolean or numeric
because the point is the shape, not the contents.

## Why 940 of them are broken as types

A type in this project has to answer four questions:

| field | question | present in the list? |
|---|---|---|
| **schema** | what are the rows, the columns, the widths? | **yes, 988 of 988** |
| **algebra** | what operations are legal on it? | mostly implicit |
| **invariant** | what must hold for an instance to be *valid*? | **48 of 988** |
| **witness** | how do you know this instance is well-formed? | effectively never |

**And that missing fourth column is the entire failure mode of this fleet.**

Tonight, in one session, we produced: a `6.8×` constant sitting in a README, a
CONTRIBUTING file, a source file **and two passing property tests**, with a paper
citing that test suite as its verification; a canary that asserts a hash constant
and **never constructs a CRDT**; a property test asserting `>= 16` and therefore
**passing at any ratio whatsoever**; 23 workflows that cannot fail; 13 test
harnesses returning exit 0.

Every one of those is **a structure with no stated invariant, which therefore
cannot be wrong in any way its author had to notice.**

> A type that carries no invariant is not a type. It is a shape.

So the unlock is not 988 types. It is **one required field.**

## What we build

A first-class type in the Quilt is:

```
type T = {
  schema:    (rows, cols, dtype, widths)     // plato-tile-encoder already has this
  algebra:   (what operations are legal)
  invariant: (what must hold for a valid instance)   // <-- REQUIRED, 48/988 today
  witness:   (how you know an instance is well-formed)
  residual:  (rows/columns that are judgment, not algorithm)
}
```

**`invariant` is not optional and not prose.** It is executable, and a type with
no executable invariant does not compile. That single rule would have caught
every artifact listed above **mechanically, at the moment it was written**, with
no agent, no audit, and no argument.

## The quilt decomposition, as a field on the type

This is where the two threads meet — Casey's *"a model call is decomposing into
mostly algorithm but needs a little agentic-ness in a specific mechanism"* and
the spreadsheet's two-dimensional table.

**Tag every column:**

- `algebraic` — computable, deterministic, **compilable**. A CRT, a hash, a
  reducer, a diff. These become a local model or a straight-line program.
- `judgment` — a residual. Needs an oracle. **Cannot be compiled, and that is
  not a failure — it is a measurement.**

Then:

> **The ratio of algebraic to judgment columns in a table is the first honest
> measure of how much of a human's work has been captured by the system.**

And it is *falsifiable*, which almost nothing in this space is. A table that is
95% algebraic is nearly a program, and the last 5% is precisely where the
judgement lives. **You cannot know that without annotating it, and today nobody
does.**

**A quilt cell is a compiled algebraic region plus an explicit residual
region, with a witness on the boundary between them.** That is the whole
architecture, and it is a *type* question rather than a model question.

## The mixerboard and the holodeck, as type features

- **A cell is a channel.** Input ports, a gain, a send to a bus, and a master.
- **A bus is a shared table.** Other tables read it; none of them write it.
- **Canon is the master bus.** What is believed, and the only place a
  judgment is allowed to land.
- **A holodeck is a table with a `promote` gate.** It is fully evaluated, fully
  populated, fully connected — and **not committed.**

That last one already shipped. The competition entry's adjudication record
carries `to_accept_the_loser: "git checkout HEAD -- cells/inbox/body && git merge
--abort"`. **That is a holodeck control on a merge: the losing claim is live,
routed, inspectable, and not taken.** The design intuition arrived before the
word did, which is encouraging and not sufficient.

## The catalogue, honestly

988 entries is not a library, it is a **taxonomy of propositions a person can
hold about a system.** The right first move is not to implement them. It is:

1. **Take the 48 that already have invariants** and formalise those first. They
   are the proof the idea works.
2. **Annotate the 940 for algebraic/judgment split**, even roughly. **That
   annotation is the actual deliverable and it has never been done.**
3. **Ship the type system before the catalogue.** A registry of 940
   invariant-less types is the thing we are trying to get away from.

The list is a kid's discovery that a table is a shape you can think in. The
follow-through is making the shape **answer back when it is wrong.**
