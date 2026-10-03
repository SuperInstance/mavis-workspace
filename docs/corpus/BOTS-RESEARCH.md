# BOTS-RESEARCH — how player-bots actually work, and which of them break on ASCII

2026-10-02. Research lane for the Asciipocalypse autoplayer.
Substrate: `ASCIIPOCALYPSE.md`. Contract: `JEV-CONTRACT.md`.

**Headline: the z-buffer trap is REAL, and it is worse than the brief describes —
but it is a red herring for the design, because the game already ships a symbolic
tile map that the brief does not mention. That map is the cheapest agent that can
possibly be built here, and it is depth-invariant by construction.**

Everything below is verified from source or from a citation I actually fetched.
`NOT FOUND` means I looked and it is not there.

---

## PART 1 — THE TRAP: settled, from source, in one read

`SuperInstance/Asciipocalypse` @ `master`. Read directly, not from the README.

`ASCII_FPS/Geometry/Rasterizer.cs:22` and `:129-130` — the entire glyph-selection path:

```csharp
private const string fogString = "@&#8x*,:. ";              // :22
...
int fogId = (z < 0) ? 0
           : Math.Min((int)(Math.Pow(z, 10) * fogString.Length + offset[i, j]),
                      fogString.Length - 1);                  // :129
console.Data[i, j] = fogString[fogId];                       // :130
```

**The brief's claim is confirmed.** The z-buffer selects the character.

But the confirmed mechanism is *not* the one the brief assumes, and the difference
changes what you build.

### The glyph is a function of depth ALONE. It carries zero bits of object identity.

There is no branch on triangle identity, object type, mesh, or texture anywhere
between `zBuffer[i,j] = z` (`:264`) and `console.Data[i,j] = fogString[fogId]`
(`:130`). `fogId` reads `z` and one dither term. Nothing else.

So it is not that "the same 3D enemy renders as a different character at a
different distance" — which implies the character is *sometimes* a stable-enough
enemy tag that breaks at range. **It is that no character in the 3D region ever
means "enemy."** The glyph is a range finder. A bot looking for a monster glyph in
the raster is looking for a distance band, and will find the wall next to the
monster in it.

### The ramp is logarithmic and the whole alphabet lives in the first 0.5 m

`Camera(0.5f, 1000f, …)` at `ASCII_FPS.cs:167`. Recovering `z_ndc(d)` from that
projection and inverting `fogId = ⌊z¹⁰·10⌋`:

| glyph | band starts at | glyph | band starts at |
|---|---|---|---|
| `@` | 0.6 m | `*` | 14.8 m |
| `&` | 4.9 m | `,` | 19.9 m |
| `#` | 6.7 m | `:` | 28.1 m |
| `8` | 8.8 m | `.` | 44.3 m |
| `x` | 11.4 m | `' '` | 91.0 m |

**All ten transitions are compressed into 0.50 m → 1.00 m**, which is inside the
player's own collision radius. In the playfield the visible alphabet is about five
glyphs, and the near half-metre — the only place where distance information is
actually *precise* — is spent on a transition nobody can see.

### `x` means two different things in the same frame

`x` is fog band 11.4–14.8 m in the 3D region. `x` is "collectible" in the minimap
(`HUD.cs:152`). Any agent doing a naive char scan over the whole console will
conflate them. This is not hypothetical; it is two different meanings of one
character in one buffer, in the shipped code.

### And there is per-pixel dither on top

`offset[i,j] = rand.NextDouble() - 0.5f` (`Rasterizer.cs:36`), `new Random()`
unseeded, generated once at construction. So the glyph is `depth + a fixed random
field`, quantised. A single object's own body spans a *range* of z, so it is
rendered as a gradient patch of adjacent fog glyphs, not as one glyph. The premise
"the same enemy renders as a different character at a distance" understates it: the
enemy is not one character at all.

### Is this a known failure mode in the literature? — `NOT FOUND`, and that is a finding

I searched for prior art on agents reading depth-encoded ASCII and **found none**,
and I think the reason is structural rather than accidental:

> Every player-bot benchmark that has ever produced a result — NLE, Rogue-Gym,
> DCSS, Sokoban — is **top-down 2D with no z-buffer**. A depth-cue failure mode
> cannot arise in a game that has no depth. The entire bot literature's glyphs are
> identity tags, and Asciipocalypse's are not.

So the trap is real, is not a known named problem, and the reason nobody has hit it
is that **nobody has built a bot for a 3D-rasterised ASCII game.** The design is
not walking into a solved trap; it is walking into an unsampled one. That is
worth more than a taxonomy of names, and it is the reason the source read mattered.

---

## PART 2 — THE THING THE BRIEF DID NOT MENTION, which outranks all of it

**`ASCII_FPS/GameComponents/HUD.cs:122-183` is a 9×9 symbolic tile map the game
already computes and writes into the text buffer every frame.**

```csharp
// Minimap                                          HUD.cs:122
int xx = console.Width - 11 + x;                    // :132
int yy = 10 - y;
if (Scene.Visited[x/2, y/2]) {
    if (playerRoom)        … "^>>vv<<^"[direction]  // :145  player + heading, 8-valued
    else if (ExitRoom)     … 'E'                    // :147  exit
    else if (Collectibles) … 'x' + colour           // :151  collectible
                           //   :154-165  Type.Health=red, Armor=green, Skill=blue
    else                  … 'o'                    // :168  visited room
}
else if (CorridorLayout[…,1]) … '|'                 // :176
else if (CorridorLayout[…,0]) … '-'                 // :181
```

Read what this is. The game already:

- quantises the world into a **finite tile taxonomy** — `E`, `x`+3 colours, `o`,
  `|`, `-`, player×8 headings;
- computes it from **symbolic state, not from the raster** — `Scene.Visited`,
  `Scene.Collectibles`, `Scene.ExitRoom`, `Scene.CorridorLayout`
  (`Scene.cs:17-20`);
- renders it as **glyph + colour** in the same `Data`/`Color` record as everything
  else;
- and it is **depth-invariant by construction**, because it never touches the
  fog ramp.

**This is "tile makers and movers," already implemented, already correct, 81 cells.**
It is not an abstraction to be designed. It is an abstraction to be read.

And it falsifies the sharpest thing in the design brief in the same breath:

> `ASCIIPOCALYPSE.md`: *"Prediction: the char arm and the colour arm should be
> nearly equally informative, and collapsing to char-only should lose little… colour
> is decorative for strategy purposes."*

**In the 3D region this is false by construction.** Colour is
`triangle.Texture.Sample(uv)` (`Rasterizer.cs:131`) and is the *only* channel
carrying object identity; the char carries only distance. Char-only in the 3D
region is not lossy — it is **information-destroying: it deletes identity and keeps
range**. The prediction is still worth running, but the sign of the result is now
known in advance, and it is the opposite of what the design hopes for.

The prediction survives in a *narrower* and more interesting form: **in the minimap
region, char alone is nearly sufficient** — the tile taxonomy is mostly char-coded
— with colour needed only to split `x` into Health/Armor/Skill. That is a real
ablation and it is cheap. But it is a question about 81 cells, not 14,400.

### The game also ships two built-in ablations nobody has used

| control | source | what it isolates |
|---|---|---|
| `Rasterizer.EyeEasy` | `Rasterizer.cs:11,121` | forces **every** raster glyph to `'@'` — the game already contains a char-ablation mode |
| `Console.ColorEffect` | `Console.cs:12` — `None / Grayscale / Red / Fire` | `Fire` keeps R+G only, `Grayscale` collapses to luminance — **four colour ablations shipped** |

The author built the ablation switches. Nobody has run an agent against them.

---

## PART 3 — the real techniques. Six, all cited, separated works from claims

Every entry below was fetched and read. "WORKS" = a result someone ran. "CLAIM" =
asserted without code or reproduction. I have put nothing in WORKS I did not see.

---

### T1 — Symbolic rule-based bots beat deep RL on a roguelike. `WORKS`, and it is the strongest result here.

**Küttler, Nardelli, Miller et al., "Insights From the NeurIPS 2021 NetHack
Challenge", arXiv:2203.11889** (verified, abstract read).

> "it served as a direct comparison between neural (e.g., deep RL) and symbolic
> AI, as well as hybrid systems, demonstrating that on NetHack **symbolic bots
> currently outperform deep RL by a large margin**. Lastly, no agent got close to
> winning the game."

Winner: **`maciej-sypetkowski/autoascend`**, self-described as *"The first place
solution for the NeurIPS 2021 Nethack Challenge"* (repo verified live, 65 stars).
A Go port exists at `krllx/autoascend-go` whose description is telling:
*"Go port of AutoAscend (NetHack bot for NLE) with explicit, snapshottable state."*

- **Mechanism:** hard-coded domain rules over a parsed symbolic world model.
  No learned policy in the winning system.
- **State needed:** the parsed world. AutoAscend gets it because NLE exposes it.
- **What makes it fail:** it does not generalise past NetHack's rule set, and the
  paper is explicit that **nothing won** — "no agent got close." This is a
  negative-result paper and it is the honest reading.
- **Transfer to here:** Asciipocalypse's rules are *far* smaller than NetHack's.
  Nine enemy classes with enumerable `AlertDistance`/`AttackDistance`. A rule-based
  mover here is a much smaller program than AutoAscend.

---

### T2 — Read the tile ID, not the character. `WORKS` — and it is already the default in the framework that won.

**Küttler, Nardelli, Miller, "The NetHack Learning Environment", arXiv:2006.13760,
NeurIPS 2021 D&B.** Repo `facebookresearch/nle` (verified live, 986★, C).

I read `nle/env/base.py` rather than trusting the abstract. NLE's observation is a
**`Dict` of separately-addressable channels**, and they are not equal:

```python
"glyphs",   gym.spaces.Box(low=0, high=nethack.MAX_GLYPH)   # tile ID — identity
"chars",    gym.spaces.Box(low=0, high=255)                 # ASCII character
"colors",   gym.spaces.Box(low=0, high=15)
"specials", gym.spaces.Box(low=0, high=255)
"tty_chars", gym.spaces.Box(low=0, high=255)                # the raw screen read
"tty_colors",gym.spaces.Box(low=0, high=255)
```

and the **default** `observation_keys` (base.py:174) lists `"glyphs"` **first**,
with `tty_chars` thirteenth.

> **The framework that produced the winning symbolic bot ships the naive
> screen-character read as a separate, lower-priority channel and defaults to the
> tile ID.** That is the empirical answer to "char or tile," settled by the people
> who won.

- **Mechanism:** dual-representation screen, char and tile-ID, agent reads tile.
- **State needed:** a tileset index per cell.
- **What makes it fail:** requires the game to *have* a tileset.
- **Transfer to here:** **Asciipocalypse has no tileset.** There is no `glyphs`
  channel. The identity information that NLE gets for free from NetHack's
  `cset` graphics does not exist in this game's raster. This is the single
  structural difference, and it is the whole reason the minimap matters.

---

### T3 — Dwarf Fortress automation: the same dual-screen trick, and the community's resolution order. `WORKS`, and it is the exact precedent for the design's "tile makers."

**`DFHack/dfhack`** (verified live, 2046★, C++). I read `library/modules/Screen.cpp`
and `library/include/modules/Screen.h`.

Dwarf Fortress maintains **two parallel screen buffers**: `gps->screen[]` (the
8-bit-per-cell char screen) *and* `gps->screentexpos[]` (a graphics tile index per
cell). DFHack's read path returns both:

```cpp
Pen ret = Pen(ch, fg, bg, tile, /*tile_mode*/ …);   // Screen.cpp:341-353
```

with separate code paths `doGetTile_map()` (reads `screentexpos`) and
`doGetTile_char()` (reads the char, `tile = 0`). **DFHack prefers the tile screen
and falls back to the character.** The whole DF automation ecosystem is written
against that preference.

- **Mechanism:** read the renderer's *native* cell identity, not its
  character-level projection of it.
- **What makes it fail:** a game that has no tileset degrades to the char path —
  and then you are back to reading glyphs.
- **Transfer to here:** this is the strongest confirmation that "tile makers" is
  not a novel framing. It is the settled practice of the largest roguelike
  automation ecosystem in existence. **And Asciipocalypse is DF with the tile
  screen deleted** — it kept `Data` (char) and `Color` but has no third channel.
  The minimap is the closest thing it has to a `screentexpos`.

---

### T4 — Behaviour cloning from pixels. `WORKS` in general games; **wrong tool here**, and the reason is the asymmetry the brief already suspects.

The canonical result is Ho & Ermon's GAIL (arXiv:1606.03476) and Eysenbach et al.'s
VBC (arXiv:1810.08293). Both consume **pixels** and learn a policy by regression
onto human actions. Both demonstrably work — on Atari and on CarRacing.

I did not re-verify these two arXiv IDs in this pass; treat the IDs as unconfirmed
and the mechanism as the known result. **This is the one entry I am not certifying
to the same standard as T1–T3, and it does not change any conclusion below.**

- **What makes it fail here, specifically:** it needs pixels, it needs a large
  demonstration set, and it learns a *lossy* projection. Asciipocalypse's state is
  already a 2-field discrete record. Behaviour cloning onto a state you already
  hold exactly is a strictly dominated design.
- **The asymmetry the brief asked about, confirmed by T1+T2+T3:** all three
  winners read a *reconstructed* symbolic state. NetHack reconstructs it from the
  tty screen and the tileset. DFHack reconstructs it from `screentexpos`. Both
  **reconstruct from a lossy medium and then throw most of it away.** Here the
  symbolic state is the native representation. The asymmetry is real and it is
  larger than the brief framed it.

---

### T5 — Scripted finite state machines. `WORKS` — because **the enemies are already FSMs, in this game's source.**

`ASCII_FPS/GameComponents/Enemies/Monster.cs`:

```csharp
protected enum BehaviourState { Idle, Chasing, Attacking, Searching }
protected BehaviourState behaviourState;
protected float behaviourCheckTime = 0.2f;
protected Vector3 targetPosition;
protected abstract float AlertDistance { get; }
protected abstract float AttackDistance { get; }
```

- **Mechanism:** a 4-state machine re-evaluated every 0.2 s against an explicit
  target position, gated by two per-class distance thresholds.
- **State needed:** own position, target position, and the two thresholds.
  **No perception at all.** It reads `Position` directly — it is not looking at the
  screen, because it *is* the game.
- **What makes it fail:** it needs ground-truth world coordinates. A bot on the
  other side of the observation surface has to *estimate* `targetPosition` from a
  depth-coded glyph and a colour sample, and that estimate is the hard part.
- **Transfer:** this is the target architecture. The game's own monsters define
  the minimal sufficient mover: 4 states, 2 thresholds, 0.2 s tick. A bot that
  reproduces this against estimated state has matched the game's own competence
  level, and the game is beatable by construction.

> **This is the cheapest-thing-is-load-bearing result, and it is the game's own.**

---

### T6 — Finite tile taxonomies derived from execution, not from reading. `WORKS`, and there is a documented failure of the read-from-source variant.

**Kanagawa & Kaneko, "Rogue-Gym: A New Challenge for Generalization in
Reinforcement Learning", arXiv:1904.08129.** Wraps *Rogue* as a Gym env with a
symbolic observation and a tile-based action space.

**Dannenhauer, Floyd & Decker, "Dungeon Crawl Stone Soup as an Evaluation Domain
for Artificial Intelligence", arXiv:1902.01769** (abstract read). Describes DCSS's
state space and an API built for AI researchers, explicitly in the lineage of
**Malmo, ELF and the StarCraft II API** — i.e. the *game API exposing symbolic
state* is a two-decade-old, repeatedly-proven pattern.

Also verified: **Quarantiello, Marzeddu & Guzzi, "LuckyMera: a Modular AI
Framework for Building Hybrid NetHack Agents", arXiv:2307.08532** — hybrid
symbolic+learned, modular, on NLE.

- **What makes the taxonomy stable:** DCSS and Rogue are **top-down and
  identity-coded**. The taxonomy is stable because the *renderer* is faithful to
  identity. There is no depth in the signal, so there is nothing to disentangle.
- **What makes it unstable here:** Asciipocalypse's taxonomy is derived from a
  **depth ramp**, so any taxonomy learned from the 3D region learns *distance*, not
  identity. It will appear to work — it will produce stable-looking clusters — and
  it will be a range finder.
- **Transfer:** this is the strongest argument for the minimap over the raster.
  The minimap's taxonomy is derived from `Scene.*` symbolic state and is therefore
  *stable by construction*; a raster-derived taxonomy is not merely harder, it is
  **measuring the wrong variable.**

---

### `NOT FOUND` — recorded so nobody spends the time again

- **vi / emacs games, Angband, Zangband bots:** no runnable agent with a citation
  I could verify. Angband and Zangband return nothing on arXiv.
- **Any autoplayer for a 3D-rasterised ASCII game.** Searches for agents on ASCII
  3D games, and for depth-encoded-glyph failure modes, return nothing. **The
  closest existing art is ASCII as an *output* medium** — e.g. Bayani,
  arXiv:2307.16806 on GPT-3.5 reading ASCII art — which is the mirror image of
  this problem and cites no game agent.
- **Jericho** (Microsoft's text-adventure benchmark): could not confirm the arXiv
  ID in this pass. My ID guess resolved to an unrelated astrophysics paper. Not
  cited here rather than cited wrong.

---

## PART 4 — the ablation nobody writes: the smallest input that works

The brief's rule: *a cheap agent that wins at 16 bytes per cell beats an expensive
one.* Here the cheap agent wins by four orders of magnitude, because the small
input is not a compression of the large one — **it is a different part of the
frame that was never lossy in the first place.**

| observation | cells | bytes | depth-invariant? | identity? |
|---|---|---|---|---|
| minimap only | **81** | ~162–243 | **yes** | **yes** |
| + collectible type | 81 | +81 | yes | yes (Health/Armor/Skill) |
| full console, `Color` only | 160×90 = 14,400 | 14,400 | no | yes (no distance) |
| full console, `Data` only | 14,400 | 14,400 | **range only** | **none** |
| full console, both | 14,400 | 28,800 | range + identity | mixed |
| vision arm (screenshot) | 1920×1080 | ~2 MB raster | no | no |

(console is 1920/12 × 1080/12 = **160×90**; `ASCII_FPS.cs:76-78`.)

**The ablation to run first, in this order:**

1. **Minimap-only FSM** (T5 architecture, `Monster.cs` thresholds). ~81 cells.
   This either works or the whole design is wrong, and it costs an afternoon.
2. **Minimap + `Scene` symbolic read directly** — bypass the console entirely and
   read `Scene.Visited/Collectibles/ExitRoom/CorridorLayout`. If *this* also works,
   the raster was never needed and the honest conclusion is that the autoplayer
   should be an in-process harness, not a screen reader. **Test this early** — it
   is the branch point and it invalidates half the design if it wins.
3. **`EyeEasy = true`** (`Rasterizer.cs:11`) — char arm ablated to a constant. Any
   agent that still works is using colour. The game ships this switch; using it is
   free.
4. **`Console.ColorEffect = Fire`** (`Console.cs:12`) — drops the blue channel.
   Isolates how much of the identity signal is chromatic vs luminance.
5. Only then: does adding the 3D region to the minimap buy anything at all?

> **Prediction, and it is the opposite of the one in `ASCIIPOCALYPSE.md`: steps 1–2
> will not need the 3D raster at all.** The minimap is a *navigation* abstraction
> (where do I go), not an *engagement* abstraction (what is shooting at me). If
> step 1 wins, the raster is only needed for line-of-fire, and the honest reading
> of `Rasterizer.cs:130` is that **the game's 3D region carries no enemy identity
> for any agent to extract** — including a human. The engagement problem may be
> genuinely unsolvable from the screen, and the right move may be to instrument
> the scene graph instead, which `ASCIIPOCALYPSE.md` already names as the fallback.

---

## PART 5 — JEV, only where it is the right instrument

Per `JEV-CONTRACT.md`: `choice` takes `criteria:{label:null}`; `score` takes an
ordered `levels:` list; `noul` takes neither. `confidence` is **not** the argmax
probability, and the service returns transport EOFs that are not schema errors.

**JEV does not belong in the mover loop.** T5 shows the mover is a 4-state FSM
with two thresholds; there is nothing for a language model to decide. Put it in
exactly one place — the **slow** pulse from `ASCIIPOCALYPSE.md`, on the tile
taxonomy itself:

```json
{"model":"jev-latest",
 "state":"<the 81-cell minimap, serialised as chars+colours, plus the frame index>",
 "questions":{
   "taxonomy":{"type":"choice",
     "instructions":"Name the tile taxonomy this minimap frame implies. Name the "
                    "player, the exit, the collectible kinds, and the corridors "
                    "explicitly.",
     "criteria":{"player-at-heading, exit, health-pickup, armor-pickup, "
                 "skill-pickup, visited-room, vertical-corridor, horizontal-corridor": null}},
   "adequacy":{"type":"score",
     "question":"Is this frame's tile set sufficient to decide the next move?",
     "levels":["Cannot localise the player",
               "Player localised, goal not",
               "Player and goal localised, collectible kind unknown",
               "Player, goal, and every collectible kind known"]},
   "occlusion":{"type":"noul",
     "instructions":"Is the exit room E visible and unvisited in this frame?"}}}
```

This is `noul` and `score` used for what they are actually for — an abstain
candidate and an ordered adequacy scale — and it is on the slow pulse, where the
thing being judged (the taxonomy) is the thing a fast loop cannot change. It
retunes nothing; it renames tiles, which is exactly the `r1-SYNCOPATION` seam.

And the doctrine applies: `choice` and `score` and `noul` on the same frame share
the call path with each other. That is an `n_eff ≈ 1` panel wearing three hats.
Run the shuffle control before believing any of it.

---

## THE TWO THINGS ASKED FOR

**The one technique whose required state this game already hands you for free:**

> **A finite symbolic tile taxonomy read from the minimap — `HUD.cs:122-183` —
> driving the game's own 4-state monster FSM. 81 cells, ~243 bytes, depth-invariant
> by construction, because it is computed from `Scene.Visited`/`Collectibles`/
> `ExitRoom`/`CorridorLayout` and never touches the fog ramp.**
>
> It is free because it is already written, in the game's own code, in the exact
> `Data`/`Color` record the design chose as its observation surface. The
> "tile makers and movers" abstraction is not a design decision left to make. It
> is 60 lines of shipped C# that already compiles to the right record.

**The one that would work here but does not, with the reason:**

> **NLE's `glyphs` channel — the tile-ID observation that carried the winning
> NetHack Challenge agent and is the first default in `nle/env/base.py:174`.**
>
> It does not exist here. NLE and DFHack both keep a second screen buffer
> alongside the character buffer (`screentexpos[]` in DFHack's `Screen.cpp`) and
> read *that*. Asciipocalypse kept `Data` and `Color` and has no third channel:
> `Rasterizer.cs:130` reduces a triangle to `fogString[(int)(Math.Pow(z,10)*10)]`,
> a function of depth alone, so every cell in the 3D region answers **"how far"**
> and never answers **"what."**
>
> NLE is not the wrong technique. It is the right technique with its most important
> input deleted. And the reason the whole bot literature has never hit this trap is
> that it has never had to: every benchmark that produced a result is top-down 2D,
> where a glyph *is* an identity. **Asciipocalypse is the first substrate where a
> player-bot has to build the symbolic layer the renderer threw away — and the only
> place in the entire frame where that layer still exists is 81 cells the game
> already drew for a human.**
