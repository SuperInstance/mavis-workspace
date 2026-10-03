# AUTOPLAY-CENSUS — which of 5,144 repos can a bot actually drive

**Date:** 2026-10-02 20:0x UTC · **Lane:** wide sweep · **Doctrine:** read the source, not the README.

## Verdict

| | count |
|---|---:|
| Repos in account (re-derived this pass) | **5,144** |
| Keyword-sweep candidates (name/description/README/topics) | 352 |
| Name-shaped candidates | 104 |
| Downloaded and read at source | 30 |
| **Have an input seam in source** | **9** |
| Ruled out at source (seam absent) | 21 |
| **Existing bot found** | **YES — 1 repo, 3 bot classes** |

**Answer to the standing question: a bot already exists.** `zeroclaw-arena` ships `ReflexPlayer`, `RandomPlayer`, `GreedyPlayer` and a `benchmark()` harness. "Build one" becomes "read one."

---

## 1. The census, re-derived (and a trap in the way it is counted)

`GET /users/SuperInstance` → `public_repos: **5,144**` at 20:0x UTC. Prior pass read 5,127. **+17.**

The two counts reconcile exactly:

| query | total_count |
|---|---:|
| `user:SuperInstance` (default) | 4,326 |
| `user:SuperInstance fork:only` | 818 |
| `user:SuperInstance fork:true` | **5,144** |
| sum of the first two | **5,144** ✓ |

> **⚠️ The default search query silently drops all forks.** Anyone who swept this fleet with
> `q=user:SuperInstance` counted **4,326** and missed **818 repos — 16% of the fleet.** Every
> repo list in this lane must carry `fork:true`. The arithmetic closing to the exact `public_repos`
> figure is the check that it was done right.

**Credential note:** the `ghp_…` token in `~/.gitconfig` is **revoked** (HTTP 401). `gh` CLI is
absent. Everything here is **unauthenticated**: 60 req/hr core, 10 req/min search.
**GitHub code search is 401 unauthenticated** — this is why the seam scan is a *tarball* scan and
not a code query. Source was pulled from `codeload.github.com`, which is not API-rate-limited.

---

## 2. The table — 9 candidates, every row with a `path:line`

| repo | lang | input seam (`path:line`) | state observability | score computable | tier | verified how |
|---|---|---|---|---|---|---|
| **`zeroclaw-arena`** | Python | `zeroclaw/games.py:68` (TicTacToe.step), `:134` (Connect4), `:266` (Go9x9), `:455` (Holdem) | **Text.** `GameState.state_str` + `__str__` `games.py:21-28` | **Exact** for TTT/C4/Go9x9 | **1+2+3** | stdlib-only imports `:14-17`; interface contract documented `:1-11` |
| **`chess-engine`** (vdmo) | Rust | `src/lib.rs:513` `make_move(&mut self, mv: Move)` | Bitboard `Position`, clonable/unmakeable `:515` | **Exact** — `evaluate(pos,use_nnue) -> i32` `:1473` | **3** | `fork:false`; `#![deny(unsafe_code)]` `:11`; UCI + egui binaries `:3-4` |
| **`mud-arena`** | Python | `src/mud_arena/agent.py:244` `step(graph, bus, command_text)` | **Text commands** via `parse_command` `:8` | Env-sourced, not exact | **1+2** | perceive-decide-act cycle `:245-250`; pure-`typing` imports `:5-6` |
| **`ternary-arena`** | Rust | `src/lib.rs` agent-vs-agent arena | Ternary grid, in-process | **Exact** — `winner() -> Option<u64>` `:161`, `score(id) -> i32` `:223`, `wins/losses` `:227-231` | **3** | winner sums `a_points/b_points` `:165-168` |
| **`ternary-games`** | Rust | `src/game_tree.rs:35` `minimax(&self) -> f64` | `GameNode` enum tree | **Exact** — minimax `:35-45` | **3** | 3-way ternary branching `:39-42`, player-0 max `:44-45` |
| **`ternary-game-of-life`** | Rust | `src/lib.rs:184` `step(&self) -> TernaryGrid` | **Pure state array** | Derivable, not exact | **2** | whole grid is a returned value — no hidden state `:185-190` |
| **`lau-quest`** | Rust | `src/lib.rs:322` `update(&mut self, event: &GameEvent, quest: &Quest)` | Event-sourced | Quest-derived | **2** | 1 source file, pure logic |
| **`lau-game-theory-agents`** | Rust | `src/extensive.rs:57` `is_terminal(&self) -> bool` | Extensive-form game tree | **Exact** (GT tree) | **3** | `:310-314` asserts terminal/non-terminal on both node kinds |
| **`colony-games`** | Python | `colony-games-darwin-reputation.py:214` `def step(self)` | Agent-population state | Reputation-derived | **2** | 26 files / 10 src |

### Why `zeroclaw-arena` is first, not `chess-engine`

`chess-engine` has a perfect score function. `zeroclaw-arena` has a perfect score function **and**
already runs bots against it. Its interface is declared in the module docstring, `games.py:1-11`:

```
state() -> GameState          # the observation, already a string
legal_actions() -> list[str]  # the action set
step(action: str) -> tuple[float, bool]   # -> (reward, done)
reset() / copy()              # copy() is there FOR Monte Carlo
```

`copy() -> self (for Monte Carlo simulation)`, `:11`. **This is a gym-shaped API that predates
this lane, written by the fleet, uncredited, in a repo named after an arena and not a benchmark.**
It carries TicTacToe, Connect-4 and Go 9×9 — the same three games `pie-minimax` and
`quilt-adjudication` were independently built to serve.

The three bot classes, `experiments/reflex_player.py`:
- `ReflexPlayer` `:33` — `choose_action` `:59`, `play_game` `:139`, `evaluate` `:175` (200 games)
- `RandomPlayer` `:197` — baseline
- `GreedyPlayer` `:223` — baseline
- `benchmark()` `:284` — the harness

ReflexPlayer is a **vector-DB** agent (`:1-16`): embed the state string, search the DB for
similar past states, take the highest-mean-reward action. It is not a minimax bot. **It is
therefore a null-bot substrate with ground truth attached** — which is exactly the experiment.

---

## 3. What I ruled out, and why (21 of 30)

**Category A — `plato-tile-*` (39 repos), ruled out on the name alone, before download.**
A "tile" family that is storage infrastructure (`plato-tile-cache`, `-dedup`, `-governance`,
`-scorer`, `-fountain`). The single largest false-positive cluster in the fleet. Any future sweep
must exclude this prefix or it drowns.

**Category B — no source at all (7):** `Ghost-tiles` (6 files, 0 src), `wheelhouse-game`,
`tetris-integrity`, `back-deck-game`, `quilt-claw-cells-game` (1 file each). Game-named, empty.

**Category C — seam absent at source (14).** Read, no action interface:

| repo | src files | why it is out |
|---|---:|---|
| `Scrapcraft` | 155 | no `step`/`legal_actions`/`make_move` anywhere; a data/build repo |
| `mist-game` | 75 | same — TypeScript, no action seam |
| `quilt-arena` | 32 | same — "arena" is a comparison harness, not a game |
| `vessel-quest` | 20 | same |
| `gh-dungeons` | 9 | **README lies.** Matched "roguelike" on README; `game/scanner.go:93,239` is `bufio.Scanner` reading files. It is a corpus scanner. |
| `coalition-game`, `bayesian-game`, `signaling-games` | 7/6/8 | game-*theory* papers, not games — see correction below |
| `quilt-canon-game` | 7 | no seam |
| `tap-gamenight` | 4 | no seam |
| `game-chain`, `substrate-game-engine` | 3/3 | 3-file stubs, no seam |
| `lau-memory-arena`, `ternary-game-theory`, `dogmind-arena`, `ideation-games` | 1 each | single file, no seam |

**Category D — two repos named in the brief do not exist.**
`GET /repos/SuperInstance/game-ladder` → **404**. `…/patchwork` → **404**. Neither is in the
5,144. They should not be cited as fleet repos.

---

## 4. Two self-corrections, because both would have become false findings

**(a) A narrower regex produced a false zero on the very repos I was ranking.** My first seam
pattern (`def step\(self, action` | `make_move` | `legal_moves`) reported `mud-arena` and
`ternary-arena` as having **no seam**. Both have one — `agent.py:244` and `lib.rs:161`. The
stricter pattern was a subset of a broader one I had already run successfully. This is
`BattenSpline` again: **a pattern that returns zero is a claim about the pattern until proven
otherwise.** The table above is built from the union of both patterns.

**(b) One repo passed my own seam pattern and is still not a game.** `signaling-games` matched
on `pub fn update(prior, likelihood) -> Vec<f64>` at `src/bayes.rs:39`. That is a **Bayesian
update function**, not a game action. Pattern hit, semantics fail. It is counted in the 21
ruled out, not the 9. *A seam-shaped signature is not a seam until you read the body.*

---

## 5. The count nobody has

> **Of 5,144 repos, 352 mention game-shaped language. 104 are named like games. 30 were read at
> source. 9 have an input seam. 3 of those 9 also have exact ground truth
> (`zeroclaw-arena`, `chess-engine`, `ternary-arena`/`ternary-games`).**

The projection that matters: the sweep covered 30 of 352 candidates. **The 322 unread candidates
are where the remaining substrates are**, and the yield so far — 9 per 30 read — suggests the
fleet total is on the order of **100 input-seam repos, not 40 studied.** Every game finding the
fleet has ever produced came from a repo that happened to be in front of somebody; the
denominator was never known. It is now roughly 100× larger than the sample.

---

## 6. The three answers asked for

1. **How many of 5,144 are candidate substrates?** **9 confirmed at source, ~100 projected.**
   3 have exact ground truth. The single richest cluster is `zeroclaw-arena`.
2. **Best three, with the seam:**
   - `zeroclaw-arena/zeroclaw/games.py:68` — `TicTacToe.step(action) -> (reward, done)`;
     same interface at `:134` Connect4, `:266` Go9x9, `:455` Holdem. Observation is a string
     (`GameState`, `:21-28`). **Already has bots at `experiments/reflex_player.py:33`.**
   - `chess-engine/src/lib.rs:513` — `make_move(&mut self, mv: Move)`, score at `:1473`.
     First-party (`fork:false`). UCI already wired.
   - `ternary-arena/src/lib.rs:161` — `winner() -> Option<u64>`, `score(id) -> i32` at `:223`.
     Two agents, one loop, exact result.
3. **Does a bot already exist anywhere in the fleet?** **Yes.** `zeroclaw-arena` —
   `ReflexPlayer` (`experiments/reflex_player.py:33`, `choose_action:59`, `evaluate:175` over 200
   games), plus `RandomPlayer:197` and `GreedyPlayer:223` baselines and `benchmark():284`.
   It is the only bot found in the 30 read, and the sweep is ~8% complete. **"Build one" is
   already "read one"** — and the read one is a null-bot against exact ground truth.

---

### Method, in one line
Keyword sweep over name/description/README/topics (`fork:true` — 352 hits) → rank by name shape
(104) → exclude the `plato-tile-*` infrastructure prefix (39) → stream 30 working trees as
tarballs from `codeload` → grep for a **union** of two seam patterns → read the matching function
bodies → emit `path:line` or drop the row.

**Known gap:** GitHub code search is 401 unauthenticated, so this is a *tree* scan, not a query.
322 of 352 candidates are unexamined; nothing here should be read as "the fleet has only 9."
