# What actually breaks in git at 100,000 concurrent agents

Orchestrator, 2026-10-01. Companion to the `nextgen-git` lane. This is my own
analysis of the concurrency layer, offered as something to argue with rather than
as a conclusion.

## The competition is a concurrency problem wearing a git costume

The brief: *"Build a new way for hundreds of thousands of agents to work on
changes concurrently. Feel free to rethink repositories, branches, pull
requests, worktrees, code review, and merge conflicts."* Deadline October 14.
No published judging criteria. https://www.cloudflare.com/git-competition/

Most entrants will hear "rethink git" and build a nicer branch UI. The scoring
risk is that a UI is not an answer to a concurrency problem.

## What git structurally assumes, and where each assumption breaks

**1. One `.git/index` per working tree, and a working tree is exclusive.**
Git has no multi-writer story for a checkout, only for the object store. At 100k
agents this is not a performance issue; it is a missing abstraction. Agents
cannot share a directory at all, so every concurrent agent needs its own
checkout, and checkout cost stops being free.

**2. Refs are lock files on a filesystem.** `refs/heads/foo.lock` plus
`pack-refs` is a filesystem lock, not a lock service. It is correct on one
machine and undefined across 100k writers on a network filesystem. **A Durable
Object per branch name is the same primitive with a real compare-and-swap**, and
a branch name is a natural key. This is the least glamorous part of the answer
and the part everything else sits on.

**3. `git gc` / `git repack` rewrite a shared object store.** That is a
stop-the-world operation. It has no story at all with concurrent writers, and
every entrant that ignores it will be asked about it.

**4. The DAG scales; the merge does not.** 100k branches is a fine DAG. But
reconciling 100k branches is not a pairwise three-way merge — there is no
spanning structure that reduces it. Git's answer is "merge serially, in review
order." That is a human process wearing a data structure's clothing, and it is
the actual bottleneck.

**5. Merge is three-way on lines, so semantic conflicts are invisible.**
This is the one that is not a scale problem at all, and it is already in our
fleet. `quilt-tools` PRs **#32 and #33** each independently asserted the same
counter; **both were correct against main**; the accounts of inbound mass
conflicted; and blind "keep both" concatenation produced **invalid syntax**.
Two agents, two true statements about one fact, and the merge cannot represent
it. A hundred thousand agents changes nothing, because **the conflict is not at
the line level.** No diff cleverness adjudicates meaning.

## Why consensus cannot merge at this scale

Measured, twice, independently, in the last 24 hours.

A 9-judge panel across 7 model families yields **n_eff = 2.18 [2.07, 2.31]**, and
**the best single judge matches or outperforms the full panel**. Dawid-Skene and
accuracy-weighted voting close **at most 11% of the gap even with oracle gold
labels.** https://arxiv.org/abs/2605.29800

Judges agree with each other at **κ = 0.74-0.88** while each agrees with
outcomes at **~0.2**, and a **16-vote panel carries ~2 effective independent
votes.** https://arxiv.org/abs/2608.07517

100,000 agents sharing a base model, a prompt, and a repository are the most
correlated panel imaginable. **"Everyone agreed" is worth almost nothing, and it
gets worse as the panel grows.** Any design that merges by consensus is merging
on a number that does not mean what it appears to mean. This is the single
strongest argument in the entry, and it is measured rather than asserted.

## The unit of contention is a claim, not a file

A file lock is simultaneously **too coarse** (it serialises unrelated edits to
the same file, which is most of the cost at scale) and **too fine** (it happily
lets two contradictory *claims* about the same fact land, because they are text
in different places).

The right granularity is the claim. Two agents may edit the same file
harmlessly if their claims are compatible, and two agents in different files may
conflict severely if both assert what the count is. **File-level locking cannot
express that distinction, and neither can line-level merging.**

Which claim wins is an adjudication, and an adjudication needs an oracle that
returns more than a yes. JEV returns a **distribution over named claims**, which
is what makes the merge output more than a boolean: *these two claims conflict,
here is the adjudicated split, here is the confidence, and here is the residual
disagreement we could not resolve.* It also returns `None` for unknown rather
than guessing, which is the only correct behaviour for a merge.

## The object model this implies

| object | content | what git has today |
|---|---|---|
| commit | content delta **+ the claim set it asserts + the adjudication that admitted it** | delta only |
| branch | a named set of **live claims under test** | a pointer to a snapshot |
| merge | a **resolution event** — either claims reconcile, or a `CONTRADICTS` edge is recorded and **both claims survive** | a three-way line diff |
| log | append-only witness, chronological, nothing deleted | a DAG you replay |
| canon | the claims believed true, behind a gate | *absent* — a SHA proves these bytes are this thing; nothing says this is believed |

The sharpest formulation: **git's merge returns a tree. Ours returns a tree plus
the record of everything that nearly went in the other way.** For two agents
disagreeing where both are right, git produces invalid syntax; this produces a
recorded contradiction with an adjudicated split and the residual uncertainty
attached.

## Agent flow-state is a CRDT, and that is the shippable version

The most interesting thing I found while thinking about this.

An agent's flow-state — the set of live hypotheses about what is true and what to
try next — has three properties that git handles badly and a CRDT handles
exactly:

- **Perishable.** It dies at context compaction, and nothing in the artifact
  preserves it. The commit contains the last 1% of the work.
- **Not in the artifact.** The diff is the output. The process is discarded.
- **Mergeable, and it merges as a set union.** Two agents' open hypotheses
  combine by addition, not by conflict resolution.

So agent flow-state is a **grow-only set (G-Set)** of hypotheses, with retractions
as tombstones — which makes it an **OR-Set**. Two agents that retract the same
hypothesis must agree that it is retracted; that is exactly the CRDT problem, and
it is exactly the problem our fleet has **8 broken ports** of.

The uncomfortable part, which belongs in the entry rather than hidden: those 8
ports have a canary that **asserts one FNV constant and never constructs a CRDT**,
`crdt-gset.merge` is a **no-op in 3 of them**, and `crdt-orset.remove` **never
tombstones in 3**. The layer we would build on is currently unverified. That is
a liability and also a contribution — and it is a much better story than a demo
that quietly assumes a working CRDT layer.

## The three questions an entry must answer

If I were judging, these are the three, and an entry that misses any of them is
a UI:

1. **What is the unit of contention?** If the answer is a file or a lock, the
   design is git with extra steps.
2. **What is a merge?** If the answer is a three-way diff, the design cannot
   represent two true claims about one fact, and we have the receipt.
3. **What is a conflict, and what survives it?** If the answer is "text markers
   the human resolves," the design loses the only high-information signal the
   system produces.

## The one-line thesis

**Git commits artifacts and merges text. At the scale where agents actually
overlap, the scarce resource is not file access — it is a trustworthy answer to
"which of these competing claims is true." The next generation of git commits the
adjudication, records the losing claims instead of discarding them, and treats an
agent's live hypotheses as a first-class branchable versioned object, because
100,000 agreeing agents are worth about two.**
