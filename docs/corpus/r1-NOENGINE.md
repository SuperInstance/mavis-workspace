# r1-NOENGINE — the dungeon that plays itself

**Lane:** script-first. *"Agents are script writers because it allows the game to continue whether or not
not the model calls output."*
**Status:** COMPLETE. Runnable, measured, three upstream defects found, 0/5 mutation kills.
**Repo:** `SuperInstance/gh-dungeons` @ `/workspace/work/noengine` (Go 1.24, tcell v2.13.7, BSP).
**Branch:** `noengine` in `fleet-triage`. `gh-dungeons` changes are local until you fork; the one
upstream patch is at `gh-dungeons-raycast.patch`.

**Reproduce:**

```bash
cd /workspace/work/noengine
go run ./cmd/headless -seeds 3 -corpus . -mode none   # no model, no decider, no TTY
go run ./cmd/receipt  -corpus . -seeds 6              # the whole receipt, below
```

---

## 0. The answer to the question the other three lanes are blocked on

> *if you cannot trust a number, how does anything else here get believed?*

**You cannot, and the cheapest honest answer is to make the harness fail in public on purpose.**

Everything below is one run of that idea. My first mutation table said `0 of 9 faults killed`. That
number was **wrong in my favour** — 4 of the 9 faults had never fired at all. I only found out
because I wrote a liveness probe that asks "did this fault change anything?" *before* asking "did the
suite notice?". A harness that cannot tell the difference between *a check that failed to catch a
bug* and *a bug that was never introduced* will report flattering nonsense forever, and it will do so
confidently, because every number in it is green.

**So: the harness that decides whether anyone will know is the harness that can say "I don't know".**
Every claim in this report is tagged with how it could have been wrong.

---

## 1. The dungeon plays with no model at all

```
$ go run ./cmd/headless -seeds 3 -corpus . -mode none -v
# headless: mode=none corpus=. files=2 turns=4000
#   room source: README.md (160 lines)
#   room source: main.go (42 lines)
  seed=1 turns=4000 lvl=1 hp=18 kills=1 win=false dead=false term="budget"
  seed=2 turns=4000 lvl=1 hp=18 kills=1 win=false dead=false term="budget"
  seed=3 turns=4000 lvl=1 hp=20 kills=0 win=false dead=false term="budget"
```

No TTY. No API key. No network. No model. No policy object is ever constructed — a constant
`Move{1,0}` × 4000 **is** the agent. 4000 turns, one monster killed, HP 18/20. The dungeon plays.

**Zero modifications to the upstream `game` package were needed for this.** `NewGameState` and
`MovePlayer` are both exported and the state machine is a pure function of `(seed, move list)`, so the
seam already existed. The `PollEvent` loop at `game/game.go:232` is the only place a model would
naturally get welded in, and it is the only place it must not go.

> **Note:** `game.NewGameState` is *not* hermetic. `getUsername()` (`game/scanner.go:188`) shells
> out to `gh api user` — a network call inside the constructor. It fails soft, so runs still work,
> but every timing number taken through the upstream constructor is suspect. My loader
> (`noengine/corpus.go`) reads only the paths handed to it.

### The architecture, in one type

```go
type Obs struct { X, Y, HP int; Visible, Explored []string; DoorRel Rel; Adjacent []Creature; ... }

type Policy interface { Decide(Obs) Move }   // no prompt, no context, no CoT field

type Factory func(*game.GameState) Policy  // the experimenter's one privileged handle
```

**The type is the enforcement.** `Obs` has no `*game.Dungeon` and no `*game.GameState`, so a policy
*cannot* read the tile it is standing on unless the game already showed it. The asymmetry is the
architecture: **the experimenter may cheat, the agent may not**, and the compiler — not a comment —
is what says so. `Factory` is called **once per run**, which is load-bearing (see §3, bug 2).

### Cells as typed I/O

A cell is a glyph with an address; its `Criteria()` is its type — a closed set a judge can only
return a member of. One typing path, no second. See `r1-TYPEFUNC` for the Go-side version; my
contribution is the discipline that the *observation* is where typing is enforced, because `Obs` is
the only thing crossing the agent boundary and it is deliberately too small to hold an answer.

---

## 2. The battery — and the two reds that were mine

```
== CHECK BATTERY (clean) ==
  [PASS] C10_monsters_can_kill_you       oracle_deaths=5 oracle_wins=1 straightline_deaths=0 total=6
  [RED ] C1_exploration_progresses       min explored gain over a single 600-turn trace was 1, want >= 15
  [RED ] C2_no_invisible_wall_livelock   seed 6: world fingerprint unchanged for 1997 consecutive turns INSIDE ONE run
  [PASS] C3_vision_reaches_cardinals     cardinal_visible_fraction=1
  [PASS] C4_runs_are_deterministic
  [PASS] C5_seed_changes_the_dungeon     distinct_receipts=6 seeds=6
  [PASS] C6_oracle_outperforms_blind     blind_wins=0 oracle_wins=1 gap=1
  [PASS] C7_door_is_reachable            reachable=6/6
  [PASS] C8_stuck_is_reported_not_hidden terminal_is_stuck=1 turns=0
  [PASS] C9_observation_carries_no_answer
  8/10 green
```

**C1 and C2 are red on the clean, fixed game and I am leaving them red.** The blind explorer still
livelocks: seed 6's fingerprint is unchanged for 1997 consecutive turns inside one run, and the
minimum coverage gain over 600 turns is 1 cell. That is an unresolved defect in the policy, and the
number is the measurement. Rounding it to a threshold that passes would be the exact move this lane
exists to prevent.

### The control, run and pasted

Branch `control-raycast-broken` in `/workspace/work/noengine` is **left failing on purpose.** It
reinstates the upstream Taylor-series raycast and nothing else:

```
$ git checkout control-raycast-broken && go run ./cmd/receipt -corpus . -seeds 6 -only checks
  [RED ] C3_vision_reaches_cardinals   only 25.0% of due-N/S/E/W cells are visible; the
                                       raycaster is missing axis directions
         cardinal_visible_fraction=0.25
```

On `noengine` the same check is `[PASS] cardinal_visible_fraction=1`. **25% is exactly one of four
cardinal directions surviving**, which is the fingerprint of the Taylor series: the vertical axis
still lands, the horizontal one drifts off-row. A check that has only ever been green is a
decoration; this one has a receipt showing it going red at a known value, for a known reason.

### Two checks that were wrong before they were red

Both of these first reported a finding **about the wrong thing**, and both are worth teaching:

**C1, v1 — comparing two different games and calling the difference a regression.**

```
[RED] C1_exploration_progresses   seed 1: explored count fell 92->81 at t=1
```

92 → 81 is not the agent losing ground. It is a 10-turn run and a 20-turn run standing in different
places. The check sampled the same seed with *different turn budgets* and compared the results. Fixed
by adding `noengine.Trace()`, which plays **one** run and samples along it. **A check that reports a
finding about the wrong thing is worse than no check, because it spends trust.**

**C10, v1 — the "dungeon is inert" result that was about the probe.**

```
[RED] C10_monsters_can_kill_you   no seed killed an agent that walked in a straight line
```

The oracle dies on **5 of 6** seeds. The dungeon has plenty of teeth. My probe used a constant-right
walker, which walks down a wall and never meets a monster — **it was measuring its own avoidance**,
and reporting the result as a property of the dungeon. A control that is itself broken does not fail
loudly; it fails in the direction that flatters the thing it is measuring.

---

## 3. Three upstream defects, one instrument

All three were found the same way: a coverage curve, plotted instead of a win rate.

### Defect 1 — a blocked move never refreshes the fog of war · `game/state.go:210`

```go
if !gs.Dungeon.IsWalkable(newX, newY) {
    return          // returns BEFORE updateVisibility()
}
```

`castRay` is never re-run, so **the wall the agent is pressed against is never marked `Explored`**.
An agent that touches a wall once can never learn it is a wall: it re-selects the same "unknown"
cell every turn and bumps it forever. Measured: explored cells 87 → 96 by turn 3, then **flat
through turn 20000**. The game never errors and the run never says `stuck` — it just exhausts its
turn budget, which is indistinguishable from a hard dungeon. **Patch applied locally.**

### Defect 2 — the raycaster's trig is a 4th-order Taylor series · `game/state.go:612`

```go
func cos(rad float64) float64 {
	rad = mod2pi(rad)
	x2 := rad * rad
	return 1 - x2/2 + x2*x2/24 - x2*x2*x2/720   // valid only near 0
}
```

```
cos(pi)   = -1.2114   math.Cos(pi) = -1.0000   err=21.1%
angle 176: sin=0.5201 (true 0.0698)   <- 7.4x error
angles (of 180 sampled) whose ray marks the cell due WEST of the player: 0
```

Because `castRay` **steps by** this value, the "horizontal" ray drifts off-row, and **zero of 180
sampled angles ever reach the cell immediately west of the player.** An agent that walks west bumps
a permanently invisible wall. Patch: `math.Cos` / `math.Sin`.

> **A patch that compiles is not a patch that applied.** My first attempt fixed `cos` and silently
> failed to fix `sin` (I searched for `x2*rad/6`; the source says `rad*x2/6`). `go build` exited 0,
> `go vet` was clean, the coverage curve was unchanged, and I very nearly concluded "the fix doesn't
> work." It had not been applied. Both patches are in `gh-dungeons-raycast.patch`; the upstream
> `game` test suite (22 tests) passes with it.

### Defect 3 — `getUsername()` makes a network call from the state constructor

`game/scanner.go:188` runs `exec.Command("gh", "api", "user", ...)`. Fails soft, but it means
`NewGameState` is not hermetic and not deterministic in wall-clock time. This is the "kill the
network and the dungeon must keep playing" constraint, violated one layer below where I was looking.

### And two instrument bugs of my own, which are the same lesson twice

**Per-turn factory.** `Factory` was called every turn, so `&Blind{}` was a *brand-new policy* every
turn and the committed target never survived. The policy looked stateless; the *wiring* made it so.
Fixed: the factory is a constructor, called once per run.

**Stale oracle.** The oracle cached `GroundTruth(st)` at construction. But `MovePlayer`'s door
handler calls `generateLevel()`, which builds an entirely new BSP maze with a new door. The oracle
was pathing to **level 1's door coordinate inside level 2's walls**:

```
level reached: 2 (every seed)   win: 0/6
blocked moves: 2914, 2917, 9, 12, 9, 2911
player stuck at x=5..11 while the door sits at x=71..76
```

An oracle with the map in its hands walking into a wall for 97% of the game. Fixed by making the
privileged view a per-turn closure (`NewOracle`). After the fix: **1 win, 5 deaths, level 5 on three
seeds, `blockedmoves` 2914 → 18.** Note the direction the broken control failed in: it made the
dungeon look *harder* than it is, and C6 caught it only because C6 compares blind against oracle.

---

## 4. The mutation table — **0 of 5 live faults killed**

```
F1_zero_update            SURVIVED  killed=0 survived=8   live=6/6
F2_swap_sign              SURVIVED  killed=0 survived=10  live=6/6
F3_reverse_seen_test      SURVIVED  killed=0 survived=8   live=6/6
F4_door_bearing_flipped   INERT     killed=0              live=0/6
F5_hp_reported_as_max     INERT     killed=0              live=0/6
F6_vision_radius_minus_1  INERT     killed=0              live=0/6
F7_self_target            SURVIVED  killed=0 survived=10  live=6/6
F8_stale_target           SURVIVED  killed=0 survived=10  live=1/6
F9_enemies_invisible      INERT     killed=0              live=0/6

0 of 5 LIVE faults killed, 5 survived, 4 never fired
mutation score over live faults: 0% (0/5)
```

### The faults I injected, and the ones that passed silently

**All five live faults passed silently. Not one check noticed.** These are not near-misses — an
agent that multiplies every move by zero, an agent that walks backwards, an agent whose "have I seen
this cell" test is reversed, an agent permanently aimed at itself, and an agent that can never
reconsider a decision. **The dungeon is uncorrelated with agent competence, and all ten checks are
consistent with that.**

### The four that never fired, and the measurement that explains why

```
seeds where the blind agent ever SAW THE DOOR:         0/6
seeds where it ever stood NEXT TO A MONSTER:          0/6
Obs.HP reads in the policy source:                    0
Obs.Visible reads in the policy source:               0
Obs.Explored reads in the policy source:              4
```

**F5** (`HP` reported as max) is an *equivalent mutant*, provably: the policy never reads `HP`.
**F4, F6, F9** are *conditionally* equivalent — the code they corrupt is never reached, because the
blind agent never sees a door and never touches a monster in 1500 turns. That is not an excuse for
the faults; it is a finding about the tested surface. **Half my mutation set could not fire because
the agent's entire tested behaviour is `BFS(Explored) + bump-detect + NoMove`.**

### Why the liveness probe is the most valuable thing in this file

My first table said `0 of 9 killed` and I nearly filed it as "my suite is blind." It was actually
**"four of my faults are no-ops."** One of them, F8, was a fault *I wrote* whose two branches called
the same function — the same "compiles ≠ applied" mistake as §3, this time inside the harness that
was supposed to catch that mistake.

> **The general rule, and I would put it on the wall: a surviving mutant is a reason to check
> liveness and equivalence before it is a reason to accuse your suite.** A harness that cannot
> distinguish *"the check failed to catch a bug"* from *"the bug was never introduced"* is not
> measuring anything, and it will report 0% with a straight face.

---

## 5. The degeneracy check nobody does — the most important line in this report

Feed the agent a dungeon where its own output is fed back as its input: tell it, every turn, that
**the door is under its feet.** A self-consistent lie — "you are at the door" is a perfectly good
world, just not this one — that never becomes false.

```
seed 1: turns=2000  coverage=[95 95 95 95 ... 95]   cycle at turn 3, period 1
seed 2: turns=2000  coverage=[102 102 102 ... 102] cycle at turn 3, period 1
seed 3: turns=2000  coverage=[90 90 90 90 ... 90]   cycle at turn 4, period 1

DEGENERATE: the agent entered a cycle at turn 3 and ran to turn 2000 without converging.
Coverage held at 95 cells throughout. The loop is not a fixed point, so the NoMove
detector never fires; the run reports a normal budget exhaustion. A closed loop ran
forever and nothing said so.
```

**A closed loop ran for 2000 turns inside a harness that reported everything as fine.** The agent
never converged. The game never errored. Every move was legal. The coverage never moved. And the run
was reported as a *normal budget exhaustion*.

**And my first detector said the closed loop was fine.** It watched for `mv.IsNo()` — "did the policy
stop?" — which catches *stopping*. What actually happens is *cycling*, so the correct instrument is a
**periodic-state detector**: hash `(position, coverage)` each turn and report the first repeat. It
finds the cycle at **turn 3** and the run still goes 2000.

> **This is the whole lane in one measurement.** The lane exists because this fleet keeps shipping
> checks that ran, passed, and measured the wrong thing. A degenerate loop is the purest instance:
> the process is alive, the output is produced, the contract is satisfied, and the content is
> worthless. Nothing errors. **If your harness cannot fail on a closed loop, it cannot fail.**

---

## 6. Rung 3: MicroMoth-quilt — measured, and it does not carry the weight

Cloned it. It is **pure-stdlib Python and a quantum circuit simulator** — `micromoth.py`,
`collapse_ledger.py`, `import_manifest.py`. No weights, no inference, no policy, no transformer; the
files matching "policy/neural" are quality-diversity map-elites experiments. **It cannot drive a
dungeon policy at all.** Rung 3 has nothing to carry, and the honest thing is to leave it out of the
diagram rather than draw a box and let it imply coverage.

But the lane needs to say what rung 3 *does* have, and whether it can be trusted, so I tested the
one property that matters — **independent re-execution**:

```python
A. honest, verified WITH re-execution  : {'ok': True,  'why': 'ok'}
B. honest, verified WITHOUT (hash only) : {'ok': True,  'why': 'ok'}
C. FORGED, verified WITHOUT re-execution : {'ok': True,  'why': 'ok'}     # <-- the finding
D. FORGED, verified WITH re-execution    : {'ok': False, 'why': 'replay_divergence'}
```

`verify(receipt, qc)` at `tools/collapse_ledger.py:185` re-derives every cell id and the prev chain —
and then, **`if qc is not None:`**, re-executes the circuit and compares. The re-execution is
**optional**. Call it without a circuit and it returns `ok: True` for a receipt whose collapse results
I rewrote by hand and re-chained with its own `fnv1a64` construction.

**This is the third independent instance of the same defect class** — after `moth-honest` and the
`quilt-jepa` reseal forgery — and it is in the repo the seeds nominate as the graceful-fall rung.
A hash chain proves **order and integrity**. Only re-execution proves the **claim**. The receipt binds
the ledger, not the science.

**Ruling for the other lanes:** a rung that is credited for the rung above's results is the exact
failure this lane exists to catch. If anyone nominates MicroMoth-quilt (or any receipt system) as a
measurement spine, the admission price is **non-optional re-execution**, verified by a test that
forges a receipt and watches it fail. I have the forge in §6 above; it is four lines.

---

## 7. The bar

| | |
|---|---|
| **Runnable in the actual dungeon, round one** | ✅ 4000 turns, no model, no TTY, no network |
| **A pasted red** | ✅ C1/C2 red on the clean game; the whole mutation table is red; 3 upstream defects |
| **Faults injected** | 9 (5 live, 4 never fired) |
| **Passed silently** | **5 of 5 live faults. 0% mutation score.** |
| **Repo note** | §3 — the two "compiles ≠ applied" moments, and why liveness-before-accusation is the rule |
| **`${GITHUB_TOKEN}`** | read-only; nothing pushed. `noengine` branch in `fleet-triage` |
| **Changes to `gh-dungeons`** | `gh-dungeons-raycast.patch` (60 lines, 2 one-line fixes + comments). Fork at will |

---

## 8. End of report

**The faults I injected:** a zeroed update, a negated X component, a reversed "have I seen this"
comparison, a flipped door bearing, an HP observation rewritten to full, a one-cell vision erosion, a
self-targeting policy, a pinned target, and invisible monsters.

**The ones that passed silently:** **all five that fired.** The agent can multiply every move by zero,
walk backwards, aim at itself permanently, and never reconsider — and all ten checks are consistent
with that. The four that did not fire did not fire because the blind agent never sees the door
(0/6) and never touches a monster (0/6); its whole tested surface is `BFS(Explored)`.

**The one check in this project I trust least: C6, `oracle_outperforms_blind`.**

I have declared it before the number and I am not moving it. C6 is the only check the other three
lanes' numbers will be read against, and it is the one that **already failed in the direction that
flatters the dungeon** — my stale oracle reported `0/6` wins for a dungeon that is `1/6`. It is a
comparison of two things I wrote, on a corpus of two files, at `MaxLevel=5`, and its margin is a
**single win**. If the three lanes compare against a gap of 1, they will be measuring noise and will
not be able to tell. I would rather report a gap I cannot trust than a gap I can.

**And the deeper reason, which is the answer to the orchestrator's question:** C1 and C2 are red
*right now* on a game I have already fixed, because the blind agent still cycles. The harness is
failing in public, which is the only reason I know. A harness that reported green would have told
three lanes that this dungeon is fine.
