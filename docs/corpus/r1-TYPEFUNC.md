# r1-TYPEFUNC — the dungeon as a state function

**Lane:** Casey's lunch-theory claim, built as code and measured.
**Repo:** `SuperInstance/gh-dungeons` @ `/workspace/work/gh-dungeons` (Go 1.24, tcell, BSP).
**New code:** `statefunc/` (7 files) + `cmd/statefunc/`. Nothing upstream was modified.
**Branch:** `naming-door` in `fleet-triage` (this file only). The `gh-dungeons` changes are a local
working tree pending a fork — `${GITHUB_TOKEN}` is read-only, so I have not pushed.

```
go build -o /tmp/statefunc ./cmd/statefunc
/tmp/statefunc -seed 9 -turns 600 -budget 600 -code-dir . -justify rare  -model none -debug 14
/tmp/statefunc -seed 9 -turns 600 -budget 600 -code-dir . -justify always -model heuristic
```

---

## 1. HEADLINE — the prediction is wrong, and it is wrong by a lot

> *"My prediction is **no, and worse** — but I have never measured it and I want to be wrong."*

**You were wrong. Forcing justification improved play, on every seed it won, and it won 10 of 12.**

12 seeds, identical dungeons, 600 turns, turn budget 600, one variable changed (`-justify`):

| arm | justified | mean level | mean kills | mean HP left | mean turns | stuck (max) |
|---|---|---|---|---|---|---|
| **`rare`** (default: system-one, model absent) | **2.2 %** | 2.08 | 4.08 | 4.0 | 245.6 | 3.3 |
| **`always`** (justification forced at every fork) | **99.3 %** | **3.75** | **12.75** | 0.0 | 288.6 | 45.3 |

- **head to head (level, then kills): `always` wins 10, `rare` wins 0, tie 2.**
- level alone: `always` better on 8 seeds, worse on **0**, tied 4.
- kills: **+212 %**. level: **+80 %**.
- Both arms die on every seed. The justified arm does not play *safer* — it plays *harder*, and dies
  1.7 floors further along. `rare` is not cautious, it is **stuck**: 3.3 turns is its worst stall,
  against 45.3 for `always`, and 9 of 12 `rare` runs end in a stall it never recovers from.

**The one number the lane was asked for: of 2 947 decisions taken by the default agent, 64 were
justified — 2.2 % — and every single one of those 64 was forced.** They are the turns where the
pruner pruned the *entire* action space and something had to be named. Not one decision in 2 947 was
chosen with a reason. That is the brief's claim, measured: **the reason is never spelled out because
there was no decision to justify.**

---

## 2. How many decisions are justified, and what a deliberating agent would have done

`options_after` counts surviving options. `opportunities` counts turns where the pruner removed an
option a deliberator would have preferred.

| | value |
|---|---|
| pre-prune option set | **9.04** mean (8 headings + wait, +1 per adjacent monster / potion underfoot / companion in range) |
| surviving after pruning | **4.02** mean (rare), **4.14** (always) |
| turns where the pruner forced a single option | **34** across 12 seeds |
| turns where the pruner emptied the set | **64** — all of the justified ones |
| **counterfactual: a deliberating agent would have chosen differently** | **2 828 / 2 892 = 97.8 %** |

**The gap nobody in this fleet has measured, and it is enormous: on 97.8 % of turns with a live
alternative, the system-one agent did something a deliberator would not have done.** And that gap
*helps it*, because the deliberator is optimising a different thing. The interesting number is not
the disagreement rate — it is that maximum disagreement and maximum score came from the same arm.

### Option count over a run

Surviving options per turn, 12 equal buckets, mean over 12 seeds:

```
rare    6.18  4.09  4.55  2.27  2.00  3.73  3.55  4.45  4.18  7.27  3.00  3.36
always  4.82  5.73  4.18  3.00  3.64  4.27  3.82  4.82  5.64  4.09  4.18  4.55
```

Seed 11, turn by turn — the narrowing is visible and it is state-driven, not scripted:

```
rare    7  5 10  5 10  5 10  5 10  7  6  3  2  2  2  2  2  2  2  2  2  2  2  2  2  2  2  4  6  6  6 ...
always  7  5 10  7  4  3  3  3  3  3  3  3  3  3  3  3  3  3  3  3  5  7  7  7  5  5  5  5  4  3 ...
```

Prune reasons, share of all prunes:

```
rare    distance 54%   impossible 41%   budget 3%   threat 0%
always  impossible 60% distance 28%   party 7%     threat 1%   budget 0%
```

`rare` leans on the distance pruner and never once on threat. `always` prunes the same walls more
(often because it stands in corridors) and is the only arm where the **party** pruner ever fires.

---

## 3. What happened when I forced justification on

Three things, in order of how much they taught me.

**(a) It worked — and I nearly reported the opposite.** My first sweep had `always` at level 1.00 vs
`rare` at 2.08, losing 9 of 12. That was *my model being wrong*, not deliberation failing. See §5:
the escort objective was the slowest party member's distance, which no player move can change within
a turn, so the deliberator's gradient was **structurally zero** and it oscillated between two cells
for 520 turns of a 600-turn run at a 100 % justification rate. **A deliberator reasoning perfectly
about an objective nothing can move is worse than a system-one that never consulted it.** The first
result was not evidence about justification; it was evidence that I had built an objective function
with no gradient in it. Fixing it flipped the sign of the headline. Anyone reporting the first number
would have been reporting my bug as a finding about minds.

**(b) The 2.2 % is not "the agent is irrational."** It is the pruner having done the work. `rare`
reaches the companion, fishes, and drops the escort entirely on `system-one` scoring alone. The brief's
mechanism — *the options go down as you spend time, and you take what is left* — is a competent player
when the pruner is good. It just isn't a *deep* one: it stalls 3.3 turns at worst and dies on 9 of 12
seeds at level 2.

**(c) Justification is worth ~+80 % level and ~+212 % kills, and it costs the agent its stalls.**
`always` has a *worse* worst-case stall (45.3 vs 3.3) and a *higher* mean one. It is not more
careful. It is more committed, and commitment is what gets it down a floor.

**The honest caveat, stated plainly:** this is not a clean test of "justification." The two arms
differ in their *scoring function*, and the deliberator's utility carries `+40` for attacking, which
mechanically produces 12.75 kills against 4.08. So the honest claim is **"an agent that deliberates
about what it is optimising outperforms one that does not, and the gap is large"** — which is
Casey's claim, and is supported. The narrower claim "adding a justification step to an otherwise
identical agent helps" is **not** what I measured, and the 2.2 %-justified/97.8 %-disagreement pair
is the reason to measure it properly next round.

---

## 4. The two falsification tests, one passed and one failed

**PASS — the game continues without the model.** `rare_slow` (a 20 ms-per-deliberation model) is
**byte-identical to `rare_none` on 12 of 12 seeds** — identical option trajectories, identical
outcomes. `rare_none` runs with *no deliberator object at all* and is likewise identical. The loop
never waits on the model. Agents are script writers, and this is the measurement, not a claim.

**FAIL — the dungeon is still a font.** `-shuffle-glyphs` permutes which code character sits in which
cell while holding the tile graph (walkability) fixed. Result: **option-count trajectory identical
on 12 of 12 seeds**, and the glyph walk changes completely:

```
real     m g g g   i  = flag.Int64("s................................
shuffled g r e r e r r r   n t f ( " l a b e l = % s   s e e . . " l : 4 . . . . . . . . . . . . . .
positions identical: True     cell kinds identical: True
```

The cells are typed, logged, and carried in every decision record — but **no pruner reads the glyph.**
Every pruner reads distance, threat, budget, or party. So the relations between cells are not yet
load-bearing, and the ontology is currently decoration with good JSON.

**This is the single most important thing to fix in round 2, and I am naming the fix rather than
claiming the win:** one pruner that reads `Cell.Criteria()`. A corridor cell adjacent to a door cell
is a junction and a corridor cell adjacent to another corridor is not, and that distinction should
change the option set. The test harness to prove it exists and is already wired — run it with and
without `-shuffle-glyphs` and require the trajectories to differ.

---

## 5. Four livelocks, all found by reading the decision log and none by reading the code

Each one is a bug I shipped, fixed, and kept the comment for.

1. **Least resistance with no habit is a coin flip.** `resistScore` had no gradient at all, so the
   agent walked north until blocked and ping-ponged between two cells forever. Path of least
   resistance needs a destination that was never deliberated — "my usual place." Fixed with a `Habit`
   set once per floor and never re-derived.
2. **A cost term makes a multi-turn deliberative act mathematically unreachable.** With `cost*5` in
   the score, fishing floors at 10 while a neutral move scores 8. The hesitation decay (400→0 over 8
   turns) could not rescue it, because the decay bottoms out and the cost term does not. The agent
   stood next to the companion for 395 turns rather than speak. **Cost is priced by the budget
   pruner; scoring it again made the deliberative option unreachable by construction.**
3. **The party must act before the player decides.** The companion originally moved *after* the
   decision, so the escort objective could not change within the turn, every action scored flat, and
   the habit term alone chose — 600 turns of E/W ping-pong two cells from the door. Then it chased at
   the player's own speed, so the last step to the companion was permanently unreachable. Then it
   orbited the player, so the player could never land on it. Fixes: the party takes its own turn
   first; it stops when within 2; it has a terminal state when fishing has been tried and failed.
4. **Arrival must not freeze you.** `RuleDistance` with slack 0 prunes *every* move at distance 0, so
   the agent was unable to act on the exact cell it had successfully reached. And a *distinguishing
   note on grid geometry*: on a 4-connected grid the distance field is 1-Lipschitz, so **a slack-1
   distance pruner can never fire on a unit step.** Slack 0 is the only value that prunes anything.

Plus one arithmetic bug the falsification arm alone could have caught: the shuffle RNG used `%` on a
shifted `int64`, which goes negative in Go and produced `j = -71`.

---

## 6. The state function, as built

```
State{turn, turnsLeft, hp, objective, party{members, escorted, spentTurns, attempts, snagged}, habit}
  → Enumerate   8 headings (each carrying the CELL it lands on) + wait + attack/drink/descend/fish/leave
  → Prune       Bundle{RulePossible, RuleBudget, RuleDistance, RuleThreat, RuleKeepParty}
  → Decide      len(live)==0 → deliberate (the only forced justification)
                len(live)==1 → execute, no reason recorded, counted as forced_by_state
                len(live)>=2 → ModeRare: LeastResistance (no reason) / ModeAlways: deliberate
  → Execute     against the real game.GameState
  → Log         {options_before, options_after, pruned[{action, reason}], objective, party,
                 justified, justification, counterfactual, counterfactual_why, disagreed, outcome}
```

- **`Cell.Criteria()` is the type** and the only typing path. A tile cell carries
  `{corridor, room, door, item, monster, player}`; a monster cell carries
  `{attack, avoid, flee, negotiate, ignore}`; a door carries `{lock, trap, creature, empty, illusion,
  descend}`. `tileCell.MarshalJSON` exists because the interface serialised to `{}` and the glyph
  quilt vanished from the only artifact anyone reads.
- **The action space is time-indexed.** `RuleBudget` is the lunch constraint literally: an option is
  removed when `cost + projected completion > turns left`. The party raises the cost of everything
  behind it, which is "the options go down as I get stopped several times."
- **The party changes the objective, not the score.** `reach_exit → accompany_companion →
  escort_companion → survive`, with a terminal `reach_exit` for "I fished, it did not take, lunch
  alone." `ActLeave` exists because otherwise the budget pruner just *freezes* the agent instead of
  making it choose; the brief's "I can't go to restaurants that take as long to order" has to be
  actionable or it is only a wall.
- **A snagged companion is a real cost.** The companion steps greedily, so it wedges in corners.
  After 5 turns of not closing the gap it is `Snagged`, the keep-together pruner goes inert, and
  abandoning the escort becomes a live question. Noticing that a commitment has stopped paying is
  the clearest thing the second system is actually for.
- **No per-move chain of thought exists in this lane.** `justification` is populated only when a
  deliberator ran, and it is empty on all 2 883 defaulted decisions. A model that emits a
  justification on every move is not modelling this agent; it is doing something the agent does not
  do, and it is a flag (`-justify=always`), not the architecture.

**Composability with the syncopation lane:** `Pruner` is a slice, the deliberator is an injected
interface, and this lane owns the *option set*, not policy selection. Nothing here assumes one
policy. `ActLeave` and the snagging counter are the closest thing to the syncopation idea in this
round — *which value you are still committed to, and when the one you flipped off stops paying* —
and they are deliberately cheap enough to hand over.

---

## 7. Round 2 — the three things that decide whether this lane is worth continuing

1. **Make the glyph load-bearing** (§4). One pruner over `Cell.Criteria()`. Without it the ontology
   is decoration and the shuffle test keeps failing.
2. **Separate "deliberating" from "optimising the right thing."** §3(c): the `+40 attack` term is
   doing part of the work. The clean experiment is one option set, one pruner, two selectors that
   differ *only* in whether a justification is computed and logged — then the justified arm can be
   made to use the *same* heuristic and the justification becomes pure overhead. **That is the run
   that actually answers Casey's question**, and it will be much less flattering.
3. **Extract it.** `statefunc` is 7 files and imports exactly one symbol from `game` (`GameState`).
   Pruner, State, OptionSet and the decision log are a building block; the brief is explicit that a
   building block living inside a game is not a building block.

---

## Artifacts

| what | where |
|---|---|
| code | `/workspace/work/gh-dungeons/statefunc/`, `/workspace/work/gh-dungeons/cmd/statefunc/` |
| per-run summaries | `/workspace/work/runs/sweep-{rare,always,slow,shuf}-s{1..12}.json` |
| per-decision logs | `/workspace/work/runs/sweep-*.jsonl` (one JSON object per decision) |
| sweep driver | `/workspace/work/sweep.sh` (`SEEDS=… TURNS=… ./sweep.sh`) |

Runs are deterministic: dungeon seed, RNG for enemy placement, and the shuffle permutation are all
derived from `-seed`, and `rare_none` reproduces byte-identically across invocations.
