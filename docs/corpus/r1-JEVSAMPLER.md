# r1-JEVSAMPLER — the rung is a property of the cell

**Lane:** JEV tunes, something fast samples, MicroMoth-quilt drives it locally.
**Branch:** `r1-jevsampler` in `fleet-triage`. Nothing pushed to `gh-dungeons`.
**Patch:** `r1-jevsampler-gh-dungeons.patch` — 10 new files, 3,763 lines, **zero lines
of the existing game modified.** Fork at your leisure.
**Evidence:** `r1-jevsampler-evidence-seed{7,42}.txt` (full `rungsim` output, verbatim).
**Run it:** `go run ./cmd/rungsim -seed 7` (go1.24+; 8s, 2GB box).
**Tests:** `go test ./rung/...` — 11 tests, all passing. Several of them are the
assertions in this document, written so they can fail.

---

## 0. The question, and the answer, up front

> *When you lose the judge, what exactly do you lose?*

**You lose the witness on typed cells and you lose state-sensitivity on preference
cells. Those are different losses, they have different footprints, and no single
accuracy number can express both.** That is the whole finding, and §4 has the numbers.

And the part I did not expect, which is the part I would bet on:

> **The rung-1 judge is 3–13× LESS accurate than the local engine on exactly the cells
> that are hard, and the agent behaves *better* when it trusts it.** Witnessing is not a
> warranty. A rung that is merely *reachable* is not a rung that should be *believed*,
> and the design consequence is that the boundary cannot be drawn by cost.

---

## 1. The classifier: which cells are TYPED, and the test for it

Not a vibe, not a config flag. A test:

> **A cell is TYPED iff its option set is a closed, mutually-exclusive,
> jointly-exhaustive set of world-states AND the dungeon already holds a ground truth
> for it. A cell is a PREFERENCE iff every option is admissible and the answer changes
> only utility.**

Operationally: **does an oracle exist?** If yes, the cell is typed and a judge answer is
*checkable*. If no, a judge answer is merely *well-formed*.

`rung/cells.go`, the option sets are the brief's verbatim:

| cell | option set | oracle | kind | rung |
|---|---|---|---|---|
| `terrain@x,y` | `{corridor, wall, door, item, monster, player}` | `Dungeon.Tiles` + entity lists | **TYPED** | 1 → 3 |
| `doorfate@x,y` | `{lock, trap, creature, empty, illusory}` | seeded derivation¹ | **TYPED** | 1 → 3 |
| `policy.next_move` | `{advance, retreat, hold, detour}` | **none** — all four legal | PREFERENCE | 2 only |
| `policy.engage` | `{attack, pass, reposition}` | **none** | PREFERENCE | 2 only |

¹ `gh-dungeons` has no lock/trap/creature mechanic. That oracle is a **lane invention**,
labelled `derived` in code, with one function to repoint. I am not passing it off as an
upstream fact.

**The rule that does the work** — `Ladder.RungFor`, `rung/ladder.go:47`:

```go
if c.Kind == KindPreference {
    // A preference cell NEVER goes above rung 2, even with the judge fully
    // available and the key in hand. Not for speed, not for cost -- for
    // correctness. Its option set is not a type, and a judge handed one will
    // return something shaped like a world-state, and the policy will start
    // reading confidence off a preference.
    return RungSampler, l.Sampler
}
```

A preference cell sent to the judge is not a slow preference cell. It is a **utility
value wearing the costume of a world-state**, and once the policy starts reading
`confidence` off it, the policy means something different than it did. Test:
`TestPreferenceCellsNeverReachTheJudge`.

## 2. The three rungs, and the one rule that makes them mean something

```
RungJEV        networked, typed, slow.  THE ONLY RUNG THAT MINTS A WITNESS.
RungSampler    fast, stochastic.        A preference cell's only correct rung.
RungMicroMoth  local engine, no API.    A model, NOT an oracle. No witness.
RungNone       not a rung. The cell is UNJUDGED, and the code is required to say so.
```

> **Only rung 1 may mint a witness.** A rung that cannot mint one renders the answer
> with the witness mark *absent* — never as a lower-confidence witness.

Because witness is a **separate channel from answer**, losing rung 1 does not blank the
cell. **It un-witnesses it.** That is the mechanism that makes degradation per-cell
instead of global: the glyphs stay correct, and exactly the cells whose kind demanded
independent attestation are the ones that show the scar.

`RungNone` exists because the fourth state is not "slow". A ladder with no bottom rung
does not produce a cautious agent — **it produces an uninformed one**, and
`NoEngine.Answer` returns `Transport: "transport: no engine -- cell UNJUDGED"` rather
than an empty map, because an empty map invites the caller to read the cell as "nothing
to say" and carry on. That is the expensive bug.

## 3. The three runs, same seed, different rungs

`go run ./cmd/rungsim -seed 7` builds a **real** `GameState` through the real
`NewGameState`/`GenerateDungeon` (same seeded RNG, same BSP, same placement) and drives
it through the **real exported API** — `MovePlayer`, which does the turn, the enemy phase,
the fog update and the descent exactly as a keypress does. No game state is mutated
directly. Headless because a TUI cannot be measured against three other lanes.

| | rung 1 | rung 2 | rung 3 | policy mode |
|---|---|---|---|---|
| `all` | JEV (stub) | sampler + tuning | MicroMoth | `trust-witness` |
| `nojev` | **gone** | sampler + tuning | MicroMoth | `verify-locally` |
| `noapi` | **gone** | sampler, **untuned-by-state** | **gone** | `blind-step` |

The mode is **derived from the ladder**, never chosen, and it is printed before anything
else — because which rung you are standing on *is* the meaning of everything after it.

**Predicted in the stub before running, so the run could convict it:**
`nojev` differs from `all` on witness count only; `noapi` differs on both content
and preference entropy. It did. §4.

## 4. What you actually lose — measured, four seeds

Typed content accuracy, sliced by fog (judged cells only; unjudged counted beside, never
folded in):

| seed | rung | visible | remembered | **dark** | **witnessed** | **dark-step refusals** | explored | descended |
|---|---|---|---|---|---|---|---|---|
| 7 | rung 1 (JEV stub) | 99.3% | 56.1% | **24.7%** | 1461 | 2 | 558 | no |
| 7 | rung 3 (local) | 100.0% | 92.8% | **74.9%** | 0 | 973 | 558 | no |
| 7 | none | — | — | — | 0 | 0 | **322** | no |
| 42 | rung 1 (JEV stub) | — | — | **27%** | 2190 | — | — | **YES** |
| 42 | rung 3 (local) | — | — | **73%** | 0 | — | — | **YES** |
| 42 | none | — | — | — | 0 | — | — | **no** |
| 1337 | rung 1 | — | — | **7%** | 533 | — | — | no |
| 1337 | rung 3 | — | — | **93%** | 0 | — | — | no |
| 2024 | rung 1 | — | — | **16%** | 474 | — | — | no |
| 2024 | rung 3 | — | — | **84%** | 0 | — | — | no |

### Four findings, and the one that should change how the other three lanes build this

**(a) The witness is not a warranty — it is a receipt.** The networked judge is
**7–27%** in the dark; the local engine is **73–93%**. Same information, same seed.
The mechanism is architectural, not accidental: **a network judge sees one sentence per
request and has no memory of the run**, so its accuracy is a function of how far the cell
is from what you can currently see. The local engine's memory is exactly what buys that
back. This is the "two speeds" thesis confirmed by measurement, and it points the
opposite way from the intuition that the big judge is the accurate one.

**(b) Consequently, being witnessed made the agent behave *worse*, not better.** On seed
7 the rung-1 run refused a dark step **2** times; the rung-3 run refused **973**. The
witnessed judge is *less* accurate, and because it has no base rate it defaults to
"corridor", so the trusting agent walks more. **A less accurate judge produced a more
exploratory agent.** Trust is not tracking accuracy, it is tracking fluency.

**(c) Losing rung 3 does not make the policy wrong, it makes it unresponsive.** The
cached JEV tuning survives the judge going away — that is the whole point of caching it,
and seed 7 shows it: `prefH` 1.285 with rung 3, 0.912 without. But the *state-conditioned
correction* dies with it, and the number that shows it is not entropy: it is **explored
cells, 558 → 322**, with the identical seed and the identical static weights. Without the
engine the policy keeps saying "advance" into geometry it can no longer see, repairs, and
holds. **1 distinct proposal vs 2.** And on seed 42 it is the difference between
**descending and not descending**.

**(d) The three runs differ in a way explainable from the cell kinds alone, which was the
acceptance test.** Typed-content and witness differ only on typed cells; preference
entropy and proposal-count differ only on preference cells. If a kind had shown up in the
wrong column the boundary would have leaked. It did not.

## 5. Not letting the ladder change the policy's meaning silently

Three things, all in code:

1. **`MeaningDrift`** on every decision (`driftFor`, `rung/ladder.go`): preference on a
   non-sampler rung, typed on the sampler (boundary leak), any transport failure, and
   **a typed cell answered UNWITNESSED by a policy compiled against witnesses**. That
   last one is the one that matters: the same move now means something else, and the run
   prints the count.
2. **The behaviour branches on the rung, not on a thought process.** Exactly two places
   — the dark step and the door — and both print their reason. Seed 7 `noapi`:
   `685 x cell unjudged: transport: no engine -- cell UNJUDGED`.
3. **The door probe** (`doorProbe` in `cmd/rungsim`) asks the one typed cell that gates a
   *behaviour*, on each rung, and prints the decision:
   ```
   rung set  policy mode      judge says  rung       descend?
   all       trust-witness    creature    jev        true
   nojev     verify-locally   creature    micromoth  true
   noapi     blind-step       (no answer) none       true
   ```
   The third row is the point: **at the bottom of the ladder the agent does not become
   careful, it becomes unaware, and it takes the stairs anyway.** And note the first two
   rows agree — *agreement between two rungs is not corroboration, and this report does
   not treat it as such.*

## 6. Batching discipline, measured

`go run ./cmd/rungsim` runs all three. Transport is the **stub**, and every number below
is labelled `STUB` — a model of the endpoint, **not evidence about it**.

1. **The `noul` collapse is real on this transport.** 64 subjects, one batch:
   named → **3 distinct answers** (`corridor x32, door x16, wall x16`);
   anonymous → **1 distinct answer** (`wall x64`). Naming the subject bought 2 extra
   distinct answers. *An unnamed subject has an observation but no address to attach it
   to.* Test: `TestTheNoulCollapseIsMeasuredNotAssumed`.
2. **`choice` read as a distribution, never an argmax.** `ArgmaxGap = 1 − P(argmax)` is
   the discarded mass. On a 45/40/10/5 preference it is **0.55** — an argmax-only reader
   throws away more than half. In `ReadArgmaxOnly` mode the sampler *records a point
   mass*, not the true distribution, because reporting the real one beside an argmax
   decision would let an audit conclude the reader had seen the runner-up's mass, which
   is the error the mode exists to measure. Also flagged on every answer: **`confidence`
   is not the argmax probability** (`confidence=0.72 argmaxP=0.60`), per
   `JEV-CONTRACT.md`.
3. **A 503 is not an empty result.** Staged transport outage:
   ```
   statuses [0 0 0]  attempts 3  final "transport: stub: staged connection reset"
   CORRECT: the outage is visible as an outage -- 0 labels returned
   NoEngine.Answer -> transport="transport: no engine -- cell UNJUDGED" label="" probs=map[]
   ```
   4xx is retried **zero** times (a 422 with validation detail is the most informative
   thing the endpoint returns); 5xx and EOF are retried up to the budget. Tests:
   `TestTransportFailureIsNotAnEmptyResult`, `TestTransportAndSchemaAreDifferentEvents`.

## 7. The oracle-leak assertion — the one that makes the numbers mean anything

The judge receives the **observation** and the **option set**. It never receives
`Dungeon.Tiles`. `TestOraclesNeverLeaveTheProcess` inspects the **real request bodies
that were actually sent** and fails if the answer key appears in one, with a positive
control so it cannot pass vacuously.

This matters because a judge handed the tile grid is not judging — it is reading, and
every accuracy number downstream of that is a measurement of the dungeon. Same defect
class as a verifier that re-hashes the experiment's own output: the receipt binds the
ledger, not the science. `ORACLE LEAK: 6 requests inspected; forbidden fields found: 0`.

## 8. Things I got wrong by running it, kept because they are the lane's actual content

These are all in the code comments, because a lane report that only lists successes is
a lane report with the interesting part removed.

- **A batched `choice` request has one shared `state`.** My first request shape gave each
  subject only its map key, so the judge could not tell which part of the scene was about
  it. Result: **59% on the visible slice, 0.3% in the dark** — a judge that looked
  useless for reasons that had nothing to do with the judge. The fix was in the
  **request**, not the model: the subject's own observation travels in its own
  instructions. This is also *why* naming is a correctness surface: drop the name and the
  observation has no subject to belong to.
- **Training the local engine on a uniform map sweep pointed it the wrong way.** The
  global base rate of a BSP dungeon is mostly WALL, so "remembered ground" trained to
  "wall" — and the engine scored **0.0%** on the dark slice, because the cells around a
  player at any moment are mostly the opposite of the map's average. A model fitted on
  the wrong distribution is not a worse model; it is a model aimed the other way.
  Retrained on the deployment distribution (a walk, not a sweep).
- **An infinite loop in the path walk-back** (`bfsStep`) that looked seed-dependent and
  intermittent: `nx, ny := ox+dx, oy+dy` where `dx, dy` were already the difference, so
  the loop spun forever. It only bites when the target is **more than two BFS steps away
  AND reachable** — so two of four seeds never found the door and never hung, and the
  one that did hung forever on a 2GB box. Path reconstruction is where "it seems to work"
  survives longest. Fixing it is what made seed 42 descend at all.
- **A ledger that retained every parsed request** cost 200KB/step and took the process
  out at 3000 steps. The subtle part: copying the `Call` struct copies the map *header*,
  so nil-ing the copy's fields still leaves the whole parsed request reachable.
- **A zero delta is a legal step and cannot also be a null marker.** `frontierStep` used
  `{0,0}` to mean "this node is the player" — which is exactly the node whose frontier
  matters most. Result: 5 landed moves out of 1500, against a wall, forever.
- **"hold" is always feasible, so a naive feasibility check lets the sampler stall the
  agent forever** with a perfectly legal no-op. An agent allowed to legally do nothing
  will do nothing, and its run is then a measurement of the sampler.
- **A sweep narrower than the agent's own vision contains no dark cells at all** — it
  reports 100% on every rung and the outage has nothing to show. The instrument has to
  look further than the player can, or it is measuring the player's eyesight.

## 9. Which cells on which rung — the answer

| cell kind | rung 1 (JEV) | rung 2 (sampler) | rung 3 (MicroMoth) | no engine |
|---|---|---|---|---|
| **TYPED** — `terrain`, `doorfate` | **yes**, mints the witness | **never** | **yes**, no witness | UNJUDGED, content survives from the world's determinism, attestation does not |
| **PREFERENCE** — `next_move`, `engage` | **never, not even for free** | **yes**, and only it | state-conditioned correction to the proposal | static cached weights; unresponsive, not wrong |

## 10. What the dungeon looks like with the API gone

Not "a log line saying offline". In the render:

- **Typed cells keep their glyphs.** The world is deterministic, so content survives.
  What disappears is the **witness mark** — a separate channel, absent rather than
  dimmed. A reader can see, per cell, *answered* versus *attested*.
- **Preference cells keep working**, from a cached artifact, and go **flat**: 2 distinct
  proposals become 1, 558 explored cells become 322, and on seed 42 the agent stops
  descending. The symptom is **not wrong answers. It is a dungeon the agent no longer
  reacts to.**
- **Every typed cell shows its reason for being unjudged**, counted separately from
  being wrong, because "the endpoint 503'd" and "the judge disagreed" are different
  events and only one of them is an outage.
- **The agent does not become careful.** It becomes unaware, and it says so on the way
  in: `685 x cell unjudged`.

And the finding the team should take from this: **the boundary cannot be drawn by cost,
and it should not be drawn by "is the expensive rung available".** On this test the
expensive rung was 3–13× less accurate than the free one on the hard cells, and the
trusting agent was worse off. The boundary has to be drawn by **what the cell can be
checked against** — and a witness is only worth having once somebody has measured
whether the witness is any good.

---

## Appendix: reproducibility

```
git apply r1-jevsampler-gh-dungeons.patch     # or: cherry-pick f52178b
go test ./rung/...                            # 11 tests
go run ./cmd/rungsim -seed 7 -steps 2000      # 8s
TYPESAFEAI_KEY=... go run ./cmd/rungsim -live
```

**Live status:** no `TYPESAFEAI_KEY` in this environment, so **every number above is
`STUB`-transport**. The client is written to the corrected contract from
`JEV-CONTRACT.md` (`model: jev-latest`, `criteria` values `null`, `type` as the union
discriminator) and `LiveTransport` is wired, but **I have not observed a 200 from
`api.typesafe.ai` and I am not going to report a number I did not measure.** The stub is
a model of the endpoint — in particular it reproduces the documented `noul` collapse and
is deliberately *stateless*, which is the mechanism behind finding (a). The moment a key
is present, `-live` swaps the transport and the same three runs execute against the real
service. If it 503s, that is the third rung, and the run says so.
