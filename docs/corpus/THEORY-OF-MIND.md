# THEORY OF MIND — what a scout actually sees, and why it isn't this work

2026-10-02. The question was how a zero-shot agent experiences this account,
landing on it for any of the reasons scouts get sent. So I sampled the three
routes that actually happen, rather than the ones I wish happened.

---

## 1. The three routes, measured

**Route A — "most popular."** What a human or an agent sees first.

| repo | size | ★ | description as shown |
|---|---:|---:|---|
| `SuperInstance` (the profile repo) | 54 MB | 7 | **NO DESCRIPTION** |
| `AI-Writings` | 3.6 GB | 4 | *Creative writing, essays, and philosophical ex…* |
| `cocapn` | 838 KB | 4 | *repo-first Agent for local or cloud…* |
| `mud-arena` | 431 KB | 3 | *Flow-state engineering arena — agents run forw…* |
| `plato-nervous` | 465 KB | 3 | *Room-specific model distillation for PLATO rooms* |
| `constraint-theory-core` | 139 MB | 3 | *Unified geometric constraint theory — Eisenste…* |

**Routes B and C — "recently active" and "what is new".** Identical sets:

| repo | size | description |
|---|---:|---|
| `quilt-tools` | 389 KB | *Ten working Quilt tool prototypes + springboar…* |
| `pong-quilt` | 1.9 MB | **NO DESCRIPTION** |
| `doubt-ledger` | 50 KB | *PoC: novel mechanism lab (fleet snowball)* |
| `tidepool` | 90 KB | **NO DESCRIPTION** |
| `wardroom` | 17 KB | *Fleet salon: off-duty rounds between agents* |

---

## 2. What that means, stated without softening

**None of the work from the last two days appears in any of the three routes.**

Absent from every entry point: `quilt-adjudication` (the shipped, cold-clone
verified competition entry), `fleet-triage` (282 files, the whole body of
work), `connect4` (the exact ground truth every number measures against),
`plainsong` (the clean yes), `selectlib`, `moth-cells`, `quilt-studio`.

**So the account's perceived quality is a lottery, and the lottery is rigged
against the work that best represents it.**

Two specific, fixable observations:

**2a. The front door is a 54 MB profile repository with no description.** That is
the first impression, and it is *nothing*. A scout arriving at
`github.com/SuperInstance` sees an empty description and a large binary blob.
**This is a one-line fix with more leverage than anything else in this
document.**

**2b. The worst first impression available is third on the popularity list.**
`constraint-theory-core` is 139 MB, is described as *"Unified geometric
constraint theory,"* and **is the repo containing the paper whose theorem is
stated over a subsystem that has never existed, and whose load-bearing constant
is wrong by a factor of two and defended by a property test that passes at any
value whatsoever.**

A scout sent to check the fleet's mathematics will open that repo. What they get
is a confident, well-formatted, wrong claim. **That is the fleet's entire failure
mode, sitting in the third most popular repository, and it is the one most
likely to be believed.**

---

## 3. The theory of mind, stated as a rule

> **A reader's belief about an account is set by the first repository they open,
> and an account of 5,127 repositories gets exactly one.**

This is the same measurement as everything else here. We have n_eff ≈ 2 across
six independent domains: nine judges, sixteen A/B votes, four learners, eleven
own reports, seven free models, four topologies. **The account behaves as a
panel of 5,127 repos with an effective sample size near one.** Whatever repo a
scout opens first is, for them, the entire account — and its perceived quality is
not sampled uniformly. It is sampled *by whatever ranking or description a
scout's route happens to surface.*

**Routes A, B, and C are three different samples of the same population, and
they do not agree.** The most popular and the most recent are almost disjoint.
**There is no single account. There are several, and a reader gets one at
random.**

## 4. The two feelings a scout can leave with

**"This is a serious, unusual research program."** Reachable — via
`quilt-adjudication` in under two commands, or `plainsong`'s `doctor` in two
steps. Neither is on any route.

**"This is an unfocused pile of AI-generated noise."** Also reachable, and
*more* reachable. 3.6 GB of essays, a 139 MB constraint theory with a fabricated
theorem, a repo named `doubt-ledger` described as a *"PoC,"* a repo named
`mud-arena` described as an *"arena,"* four hundred prototypes in one repo, and a
profile repository with no description at all.

**The first feeling is earned and hidden. The second is unearned and
default.** That is the whole problem, and it is a navigation problem, not a
quality problem.

---

## 5. What fixes it, in order of leverage

**1. Describe the profile repository.** One line. It is the front door and it
says nothing. **Nothing else in this document comes close in leverage per
minute.**

**2. An `AGENTS.md` at the front door.** This is the emerging convention for
agent-facing repository documentation and it is the correct instrument for the
problem: **a scout is not a human reader, and the file should be written for
the reader who has no context and a task.** It needs to say, in under a screen:
what this account is, which three repos represent it, what is verified, what is
known broken, and **what a scout should do with a finding** — because a scout who
finds a defect and has no place to put it generates another issue, and the
account already has 5,471 of those.

**3. Make `fleet-triage` reachable from the three routes**, not only from a URL
someone was given. It is the index and nobody arrives at it.

**4. Correct `constraint-theory-core` in place, with a corrections ledger at the
top of the README.** Not a retraction buried in a commit. **A scout will read the
README or they will read nothing.** The corrections file in `fleet-triage` is
correct and invisible, which is the worst possible combination.

**5. Three descriptions that do not exist yet:** `pong-quilt` and `tidepool`
have none, and `quilt-adjudication` should be discoverable by the words a scout
would actually search.

---

## 6. The uncomfortable generalisation

**This is the projection doctrine applied to the account, and it is the one
finding I did not go looking for.**

The fleet measures individual repos carefully — a resolver that checks 477 of
them, a lint suite, a canary, mutation testing. **It has never measured
itself being read.** Every instrument in this account points *inward*, at code
and claims, and not one points outward, at the experience of a first-time
reader.

**So the account has excellent instruments for detecting that its artifacts are
wrong, and no instrument at all for detecting that its *door* is unwritten.**

That is the same failure as the 23 workflows that cannot fail, one level up: a
system with many checks, all of them pointed the wrong way.
