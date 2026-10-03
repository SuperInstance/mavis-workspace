# r1 — SYNCOPATION: the deliberately-blind system-two

**Lane:** Casey's most original idea, made runnable in `gh-dungeons`.
**Status:** COMPLETE. Runnable, measured, and the answer is **no**.
**Branch:** `r1-syncopation` in `fleet-triage`. Code in `r1-syncopation/`.
**Question:** *does deliberate blindness, correctly implemented, produce better play than a designer that can see everything?*

## The answer, in one line

**No — and the way it fails is more useful than a yes would have been.** As specified, a
syncopated designer does not choose badly. It chooses **blindly**: across 4 seeds and 20
demotions it demoted a policy it had **literally never observed, 20 times out of 20**, and
cut down the actually-best policy **17 times out of 20 (85%)**. The control, given the same
interval one generation earlier, made 0 errors — not through skill, but because by
construction it was shown the truth.

The architecture degenerates into a **carousel**: the real dungeon runs a brand-new,
never-evaluated policy 100% of the time, while the two shadow worlds accumulate evidence
about policies that are already dead. The lag, which is supposed to be the engine, is what
makes the degeneration *inevitable*.

---

## 1. Cadence: **30 seconds**, 600 turns, and why that number is a trap

Casey's brief says 30s. I kept it. The world ticks at 20 Hz, so one cadence is **600
turns** — the smallest interval at which a policy's character separates from its noise.

Then I measured whether 600 turns is enough to *do* anything:

```
$ syncopate fog -seed 7            # fog-limited reachability, no designer, instant
  policy          600     1200     2400     4800   (floors / moves / explored% / HP)
  seeker        0/ 600/ 34%/17    0/1200/ 34%/17    0/2400/ 34%/17    0/4800/ 34%/17
  berserker     0/ 600/ 25%/20    0/1200/ 25%/20    0/2400/ 25%/20    0/4800/ 25%/20
  warden        0/ 600/  6%/19    0/1200/  6%/19    0/2400/  6%/19    0/4800/  6%/19

$ syncopate reach -seed 7 -ticks 600   # deliberately OMNISCIENT BFS agent
  floor 1: BFS distance from spawn to door = 88 tiles
  omniscient BFS policy, 600 ticks: levels descended 1, kills 3, HP 16
```

**A cheating agent that knows exactly where the door is descends exactly one floor in 600
turns. Fog-limited policies descend zero, at any cadence I could afford to run.**

So Casey's 30-second cadence is **longer than `gh-dungeons`' own time-to-objective.** An
A/B at 30s is not measuring play quality, because no good policy exists to select for. This
is a finding about the *pairing* of the design with the environment, not about blindness.
Every 30s run I did returned `levels=0 kills=0 deaths=0` in both arms.

**I am not reporting a winner from those runs, and neither should anyone else.**

### Open problem, precisely located

Exploration freezes at 34%/25%/6% and never grows past ~600 turns regardless of horizon. I
fixed three separate bugs in the frontier explorer to get from 6% to 34%, each of which
printed a perfectly plausible "0 floors" table while measuring nothing:

1. a reciprocal-distance gradient of magnitude ~1e-5 next to a 0.4 `Explore` term — the
   frontier was numerical noise and the policy ignored it;
2. `distOf` returned the **length of the step**, not the reduction in distance-to-target,
   so it was never 0 for any of the eight directions — *a gradient that mathematically
   could not fire*;
3. a greedy Manhattan step toward the target, which oscillates forever the moment the
   target is around a corner — the BFS already knew the route and I wasn't reading it.

After those, exploration improves and then still stalls. **The frontier explorer does not
yet solve `gh-dungeons`.** Until it does, no score in this lane measures play quality, and
the honest move is to say so rather than ship a number that means nothing.

---

## 2. What is actually enforced, and how you can check

The blindness is a **capability**, not a promise. `Designer.Decide` takes exactly two things:

```go
func (d *Designer) Decide(alive []policy.Gene, belief []PolicyReport, gen int) Plan
```

Genes are eight floats. Reports are finished numbers. There is no `World`, no `Slot`, no
callback, and the designer runs in a **different goroutine** from the worlds.

```
$ syncopate selftest
  PASS  PolicyReport holds no *game.GameState          only value fields
  PASS  Designer.Episode takes no *World               receives []PolicyReport and a *Clock
  PASS  a report does not track a world after closing  score 95.4 before 500 more ticks, 95.4 after
  PASS  blind arm is EXACTLY one interval behind       acted on N-1 while N had just closed
  PASS  oracle arm reads the closing interval          its decisions use interval N, not N-1

RESULT: blindness is enforced structurally, not by convention.
```

Check 3 is the one that would catch a real leak: build a report, run the world 500 more
ticks, confirm the report's score does not move. A field that lazily resolved, or a pointer
aliased into the world, would fail it.

**My first design did leak, and the selftest is why I know.** The designer loop originally
received `[]*Slot`, and `Slot` contains a `*World`. Separate goroutine or not, that was a
live handle. I rewrote the boundary to pass genes. *If your blindness test only checks that
the designer "didn't look," it will pass this.*

---

## 3. The A/B: one line, and it is all that differs

Same seed, same cadence, same genes, same mutation operator, same scoring function, same
20 Hz world. The **only** difference is one delivery:

```go
fresh := reports
if arm == ArmSyncopated {
    fresh, pending = pending, reports   // the report you slept through arrives NEXT wake
}
```

The oracle is deliberately **not** a synchronous designer. It does not watch the world while
it thinks and it does not change when the world happens to run. Holding the cadence fixed
and moving only the delivery is the only way the comparison means anything; a true
cadence-zero arm is a *different* experiment, reported separately in §5.

### Environment validity gate, run first

```
$ syncopate probe -n 6
  seed 1000 IDENTICAL ... seed 1035 IDENTICAL
  VERDICT: gh-dungeons is seed-stable across 6 seeds x 200 ticks.
```

This gate earned its place immediately: the first version compared *rendered frames*, which
carry the policy name, and reported "DIVERGED at tick 0" for all six seeds. That would have
been a fabricated invalidation of a perfectly good environment, and it would have looked
exactly as convincing as a real one.

---

## 4. THE DELIVERABLE: the unobserved window

Seed 7, cadence 5s, 5 toggles. **Left: the syncopated arm. Right: the oracle.**

| # | demoted | interval | what the designer **SAW** | chosen by | stale by | what **ACTUALLY** happened | cost |
|---|---|---|---|---|---|---|---|
| 1 | `seeker` **(active)** | t=0–5s | **`NOTHING (never observed)`** | system-two[syncopated] | — | `lv+0 dmg=1 seen=636 hp=19 score=155.0` | **+155.0** |
| 2 | `g01` **(active)** | t=5–10s | **`NOTHING (never observed)`** | system-two[syncopated] | — | `lv+0 dmg=5 seen=407 hp=15 score=81.8` | **+81.8** |
| 3 | `g02` **(active)** | t=10–15s | **`NOTHING (never observed)`** | system-two[syncopated] | — | `lv+0 dmg=3 seen=413 hp=17 score=91.2` | **+91.2** |
| 4 | `g03` **(active)** | t=15–20s | **`NOTHING (never observed)`** | system-two[syncopated] | — | `lv+0 dmg=1 seen=316 hp=20 score=75.0` | **+75.0** |
| 5 | `g04` **(active)** | t=20–25s | **`NOTHING (never observed)`** | system-two[syncopated] | — | `lv+0 dmg=0 seen=414 hp=20 score=103.5` | **+103.5** |

| # | demoted | interval | what the designer **SAW** | chosen by | stale by | what **ACTUALLY** happened | cost |
|---|---|---|---|---|---|---|---|
| 1 | `warden` | t=0–5s | `dmg=0 seen=246 hp=20 score=61.5` | system-two[oracle] | 0 | **identical** | +0.0 |
| 2 | `seeker` | t=5–10s | `dmg=0 seen=1 hp=19 score=0.2` | system-two[oracle] | 0 | **identical** | +0.0 |
| 3 | `g01` | t=10–15s | `dmg=2 seen=209 hp=13 score=44.2` | system-two[oracle] | 0 | **identical** | +0.0 |
| 4 | `berserker` | t=15–20s | `dmg=0 seen=5 hp=17 score=1.2` | system-two[oracle] | 0 | **identical** | +0.0 |
| 5 | `g02` | t=20–25s | `dmg=0 seen=26 hp=17 score=6.5` | system-two[oracle] | 0 | **identical** | +0.0 |

**The whole product is the `SAW` column.** In the syncopated arm it is `NOTHING`, every
row, forever. The information did not exist. The demoted policies were doing real work —
exploring 316–636 tiles, taking 0–5 damage, holding HP 15–20 — and every bit of it arrived
one generation after the decision that destroyed them.

**Two honest caveats on the right-hand table, so nobody over-reads it:**

- The oracle's `+0.0` is **definitional, not a triumph.** It was handed the truth and
  demoted the worst, so "0/5 wrong" is an identity, not an achievement. The informative
  number is the left table's `NOTHING`, not the right table's zero.
- The oracle's own play got *worse* — its exploration collapsed to `seen=1`, `seen=5`,
  `seen=26`. It correctly identified the worst explorer each round and kept it.

---

## 5. Cadence = 0: what actually breaks

The cadence is a wall-clock deadline, not a loop counter, so zero does not give you an
instant designer — it gives you a designer that runs once per tick, competing with the
world for the machine.

```
  baseline (cadence 2s)  cadence=2s   wall= 8.2s  world_ticks=160  real_score=131.8
  LAG REMOVED (cadence 0) cadence=0s   wall= 0.4s  world_ticks=  4  real_score=1912.5
```

**Wall-clock time drops 20× and that is the trap.** The cadence looks like pure overhead, so
you optimise it away. But the world gets **4 ticks instead of 160** for the same four
toggles — a **40× starvation**. The designer no longer sleeps between decisions; it runs
once per tick, and the two goroutines fight.

The lag is load-bearing **twice**: informationally it is the unobserved interval this lane
exists to create, and mechanically it is the headroom that lets the game keep playing. *A
designer that never waits does not observe more; it observes a dungeon that stopped running.*

(The `real_score=1912.5` is meaningless — each interval at cadence 0 is one tick, so the
exploration *rate* is computed over a single turn. Comparing it to anything is nonsense.)

---

## 6. The run-level score contradicts the decision-level evidence. I believe the evidence, and here is why.

Across 4 seeds at cadence 5s, the **blind arm scored higher on 4 of 4** seeds:

| seed | syncopated | oracle | delta | "winner" |
|---|---|---|---|---|
| 7 | 69.3 | 52.8 | +16.5 | blindness |
| 108 | 127.3 | 52.6 | +74.7 | blindness |
| 209 | 17.5 | 15.7 | +1.8 | blindness |
| 310 | 76.8 | 45.4 | +31.5 | blindness |

**A +1886.8-point selection failure produced a better-looking run on every seed.** I do not
believe that, and the reason is worth more than the number:

- `levels=0` and `kills=0` in **all 20 runs**. Nothing was won. Nothing could be.
- With levels and kills at zero the score collapses to `25 × exploreRate − 4 × damage`.
- Exploration rate is **causally unrelated to the demotion decision** the arms differ in.

So the run score is dominated by a term that cannot see the thing being compared. **A
metric that cannot detect a 1886-point failure in the decision it is supposed to be scoring
is not a metric.** Reporting "BLINDNESS WINS" from this table would be reporting the
absence of a measurement as a result.

This is the most transferable thing I found: **before asking whether an architecture wins,
check that your score can see the decision it is scoring.** A blind designer that ruins
every decision can still post a better run, and a fleet comparing four designs on run
scores will rank them by noise.

---

## 7. Why the carousel is structural, and how to stop it

Three properties compose into a degenerate loop:

1. the new policy is **promoted unconditionally** (no evidence required to try something);
2. demotion picks the **worst-scoring** live policy;
3. an unobserved policy scores as **the worst thing imaginable** — you cannot defend what
   you have no evidence for.

The newborn was promoted *during the sleep*, so by the next wake it has **zero observations**,
so (3) makes it the worst, so (2) demotes it. Every generation. Forever. The one-cadence
delay makes the newborn unobservable *by construction*.

`-prior neutral` breaks it, and the damage halves:

| prior | mis-demotions | cost/demotion | cost total |
|---|---|---|---|
| `worst` (default) | **17/20 (85%)** | +94.3 | +1886.8 |
| `neutral` | **3/10 (30%)** | +48.5 | +484.5 |

Better, and still wrong 30% of the time. Three candidate fixes, none tested yet:
**(a)** never make the newborn eligible for demotion — demote among the two *previously
shadowed* policies, which is the most literal reading of "digests the previous two and
picks the better one"; **(b)** require a policy to survive one full cadence before it is
eligible; **(c)** keep the newborn pinned until it has one observation.

I lean toward **(a)**: it is what the brief actually says, and my implementation demoted
among all three live policies, which is the more aggressive reading. That may be my bug and
not the architecture's.

---

## 8. The loop survives the model, as required

There is no model. `policy.Act` is `func(View) (dx, dy int)` — a state function, no chain
of thought, because per the brief's §7 this agent does not narrate its decisions and a
model that explains every move is not modelling it. The designer is a script too
(`Designer.Decide`); wiring a model in later replaces exactly one method.

**The game keeps running when things go wrong.** The world goroutine is independent of the
designer, and a dead player does not end the run — it respawns on a derived seed and books
the death as a cost. A dungeon that stops because a model was slow has thrown away the one
property worth having. A player dying must not look like a finished experiment.

## 9. The toggle as a visible event

`-frames` renders the live dungeon with the governing policy named in the frame header, so
you watch the world's logic change under you with no input. It is legible in a log, which is
what round 1 needs.

**This is the weakest of the four requirements and I am not going to pretend otherwise.**
The real requirement is a toggle visible *in the tcell game* — walls recolouring, the
monster AI visibly changing, the player seeing the world's rules change mid-dungeon. That
needs one upstream change I am **not** proposing yet:

> `Game` needs a `Tick()` that the existing `PollEvent` loop calls on a timer, plus a
> policy hook. `game/game.go:236` blocks on `PollEvent`; there is no loop to hang a policy
> on. It is ~30 lines and it is the change I would ask the orchestrator to fork.

Round 1 did **not** require touching `gh-dungeons`: the whole simulation is drivable
headless through `NewGameState` + `MovePlayer` (`game/state.go:58,203`), which runs
gh-dungeons' own turn economy. Zero upstream changes. Please do not fork for me yet.

---

## 10. Commands

```
go run ./cmd/syncopate probe                       # seed-stability gate — RUN THIS FIRST
go run ./cmd/syncopate selftest                    # can system-two obtain a live world?
go run ./cmd/syncopate reach -ticks 600            # omniscient agent: is the door reachable?
go run ./cmd/syncopate fog                         # fog-limited: how many turns to descend?
go run ./cmd/syncopate debug -n 48                 # per-tick frontier + chosen direction
go run ./cmd/syncopate run -seed 7 -cadence 5s -toggles 5 -arm syncopated -frames
go run ./cmd/syncopate ab -seed 7 -cadence 5s -toggles 5 -seeds 4 [-prior neutral]
go run ./cmd/syncopate cadence-zero
go run ./cmd/syncopate score
```

## 11. What round 2 needs

1. **A frontier explorer that actually solves the dungeon.** Everything downstream is
   blocked on it and I have located the stall precisely enough to hand it over.
2. **Then re-run the A/B.** Until `levels > 0` somewhere, no play comparison is meaningful.
3. **Fix the eligible-set question** (§7a) — possibly my bug, possibly the architecture's.
4. **A score that can see the decision.** Weight descent; make exploration a tiebreaker.
5. **The tcell toggle**, if and when the orchestrator will fork.

---

## Final answers to the three questions asked

**Cadence I chose:** **30 seconds** — Casey's number, kept, at 20 Hz = 600 turns. Reported
rather than optimised. Then measured and found to be longer than the dungeon's own
time-to-objective, which is a finding about the pairing, not about the lag.

**Number of policies that lived:** **3 at any instant**, one born and one demoted per
generation, **8 distinct policies over a 5-toggle run** (3 seeds + 5 bred). 20 demotions
across the 4-seed sweep.

**What the demoted one did while nobody was looking:** it worked. `seeker` explored 636
tiles, took 1 damage, held 19 HP, scoring 155.0. `g01` took 5 damage and held 15 HP. Every
one of them was doing useful work in the dungeon, and **the designer that destroyed all of
them had seen `NOTHING` — not stale data, not partial data, nothing — in 20 demotions out
of 20.**

---

*Design belongs to this lane. The brief it came from is `GH-DUNGEONS-SEEDS.md` §5, preserved
and not restated, because the point of this document is to disagree with it productively.*
