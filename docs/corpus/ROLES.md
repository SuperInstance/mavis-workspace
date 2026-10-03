# FOUR LANES, and why they are different jobs

2026-10-02. A long-running project needs roles, not a queue. These four exist
because they have **four different failure modes**, and a lane that does one
job well will do another badly.

**The rule that makes this work: a finding with no downstream lane is finished,
not in progress.** Every artifact must name its hand-off, or it is a receipt.

---

## SCOUT — look at what nobody has looked at

**Mandate.** Unaudited surface. Something exists, nobody has read it, nobody
knows whether it is real.

**Tonight's proof this role is worth having.** 132 `fleet-midi-*` repos, never
surveyed. 3,858 non-forks of which **89.5% never examined**. The highest-value
output of the entire survey was **four lines long**: `--strict` does not exist,
`-q` silences the only instrument, and total garbage exits 0 with a valid,
empty, playable MIDI. **The census was the cost of admission. The seam was the
product.**

**Kill criterion.** A census of N things with no named seam is **not done.** You
have not finished until you can say *this specific line, here, is wrong*.
If you surveyed 132 repos and found nothing, say that in one line and stop —
that is a finding, and padding it is a failure.

**Hand-off → EXPERIMENTER.** "Here is the seam, here is how to make it fail."

**Failure mode.** *A list of findings nobody acts on.* 4,789 resolver findings,
zero decisions. If your report cannot be acted on, it is a receipt.

---

## EXPERIMENTER — run it and find out

**Mandate.** Convert a claim into a number, or convert a number into a retraction.

**Tonight: four experiments, and three produced a wrong result first.**
- The projection ladder: a **max over 4 learners at n_eff 1.48**; the ordering
  **reversed** under the median.
- `detection_power`: divided by the wrong denominator, so a **perfect instrument
  scored 0.242**.
- The quilt script: used a **random split** — the exact thing I had been warning
  against in every brief — and reproduced the hash-beats-the-board failure
  inside my own experiment.
- The IT-department harness: printed a ledger with **0/10 everywhere**, which
  was my broken harness and not a result.

**Kill criterion.** **Every run must have a negative control before it has a
result.** If the control does not fail when it should, the run is `INVALID` and
you say so. A failed instrument must be loud, because a well-formed instrument
reporting success while broken is the entire subject of this project.

**The second criterion: a result that is inside the noise is not a result.**
Six datasets and one constant of ≈2 is a real finding. Six samples and a
+0.04 difference is not. Say which you have.

**Hand-off → BUILDER.** "This number, and the fix is these lines."

**Failure mode.** *Publishing a number from a broken harness.* Twice tonight the
instrument was the story and I nearly believed it.

---

## BUILDER — ship something that runs

**Mandate.** An artifact a stranger can clone and use, with instructions.

**Tonight: two ships and one lesson.**
- `quilt-adjudication`: 11/11 pins, demo green, cold-clone verified — **and its
  primary affordance was fiction.** `to_accept_the_loser` ended in
  `git merge --abort`, which *always* fails after a refusal, and named the loser
  while restoring the state the reader was already in. **Green, verified, wrong.**
- `--strict` for `plainsong`: four lines that close the fleet's most musical
  repo against producing well-formed wrong music.

**Kill criterion.** **Run the primary affordance before you ship it.** Not the
test suite. The handle. The button. The thing a person reaches for. A passing
suite on a fiction is the same defect as a passing suite on a tautology.

**Hand-off → PLAYER.** "Here, break it from outside."

**Failure mode.** *Shipping something that runs but does not work for a person.*

---

## PLAYER — use it as a stranger and report the awkwardness

**Mandate.** Adopt the thing with no fleet context and find where it stops
being usable.

**Tonight.** `PLAYTEST-OUTSIDER` found that I expected "three or four tools
clear the bar" and there is **one clean yes and one partial** — and that
`selectlib`'s *"beats free local noise"* half is **a sentence in a docstring,
not an implementation**. It also reported the live resolver as `NXDOMAIN` from
its egress while it answered from mine, and was half right.

**Kill criterion.** **Time to first working invocation, counted.** "Nine steps,
two undocumented" is a finding. Zero is a bug report. And: **does it work on
*your* data, or only its author's example?** That single test is where most
things fail and nobody notices.

**Hand-off → SCOUT.** "Here is the thing that is actually hard to use; go find
the other twenty like it."

**Failure mode.** *Playing with your own artifacts and calling it testing.* You
have the context; the value is entirely in the context you throw away.

---

## The pipeline, and the part everyone forgets

```
SCOUT ──seam, how to break it──▶ EXPERIMENTER ──number, and the lines──▶ BUILDER ──artifact, run the handle──▶ PLAYER ──awkward, adoptable──▶ SCOUT
   ▲                                                                                                                          │
   └────────────────────────────────────────────────────────────────────────────────────────── the census was the cost ─────┘
```

**A finding that stops at any stage is incomplete, not delivered.**

And the counter that keeps getting missed: **a pipeline with no player is a
report generator.** The whole fleet is 40+ reports and zero adopted changes, and
that is not an accident — it is the pipeline running with the last stage
missing.

---

## Standing rules, learned the hard way

1. **A broad brief produces nothing. A narrow one produces something.** Every
   lane that died got "investigate X" across several surfaces. Every lane that
   delivered got one file, one action, one hour.
2. **Env var names are exact.** `CLOUDFLARE_TOKEN`, not `CLOUDFLARE_API_TOKEN`.
   Three lanes died on that before I noticed.
3. **`/tmp` is wiped in this environment.** Push anything that should survive.
4. **An API contract rots inside a session.** A recorded interface is a claim
   about a moment, not a fact about a duration. JEV worked for 693 calls and
   then 400'd on the same shape.
5. **Fix it in the open.** Every correction in this repo names what was wrong,
   who was right, and what replaced it. Three of the most valuable documents
   here correct *me*.
