# GH-DUNGEONS as a learning environment — the seeds, preserved

2026-10-02. Casey's brief, captured intact before the team interprets it, because
interpretation is where good briefs go to die. `SuperInstance/gh-dungeons` is the
testbed. The goal is a way to **ML the quilt systems**, and the team is to
compete on designs.

---

## 1. The ontology, in one sentence

> **An array of characters is simply a quilt with every cell getting its own
> character, and the code is the relational understanding of what's happening.**

The glyph array is the cell graph. **The code is not the program — it is the
relations between cells.** `gh-dungeons` already renders characters into a
terminal; a cell *is* a character with an address, and an edge is an adjacency
that means something.

## 2. Cells as typed I/O

> **JEV can treat various cells as the various type-safe inputs and outputs.**

Each cell is a JEV subject. **A cell's `criteria` is its type.** A tile saying
`corridor` has criteria `{corridor, wall, door, item, monster, player}` and a
judge can only return one of those. A cell saying `what is behind this door` has
criteria `{lock, trap, creature, empty, illusory}` and the state narrows it.
**Type safety is a closed option set, and JEV's `choice` already is one.**

## 3. Two speeds, and the fine-tuning split

> **How MothQuantum can quickly find the stochastic answer once JEV has
> fine-tuned the weights of the quilt's player-logic.**

JEV is slow, structured, and expensive. MothQuantum is fast and stochastic.
**JEV tunes; Moth samples.** The question every design must answer: *what is
JEV tuning, and how does that tuning reach the sampler without becoming the
sampler?*

## 4. The graceful-fall rung

> **Once the ML is good enough through heavier machinery, something like
> `SuperInstance/MicroMoth-quilt` can be an engine for driving the ML without
> true mothquantum API calls.**

Same shape as the boat: cloud intelligence, a Jetson with logs, a Pi with
voice, an ESP32 with dead-band gates. **At dungeon scale: MothQuantum, then a
local JEV-derivative, then a MicroMoth policy with no API at all.**

## 5. THE SYNCOPATION — the most original idea here, and it must not be lost

> **System-two cells pulse slower, but they are higher-level designers of flow
> that create alternate logic which A/B tests while they think of their next
> iterative improvement.**
>
> **This creates a cultivating Fibonacci-like environment where the system-two is
> a move behind in its thinking.** So while it's iterating and thinking about the
> last, say, 30 seconds of gameplay and the previous strategy it had scripted, and
> thinks about a better new strategy to A/B test, **the game is still going on.**
>
> **When the new one is toggled on, the older two are still there**, and the
> agent then digests the previous two and picks the better one while all three
> are playing.
>
> **So when it flips his new one on and decides which old one to flip off, he's
> actually behind — and the one it chose to flip off had 30 seconds of gameplay it
> didn't see until turning it off and his experiment on.**
>
> **This creates syncopation in the relationship, energizing the creativity
> through asymmetric understanding.**

**Why this is not a bug and is the engine:**

The lag is not delay. **The lag is how the designer acquires data it could not
have had.** Every system-two agent is *behind by construction*, and being behind
means the policy it just turned off has been playing, unobserved, for exactly as
long as the designer spent thinking. That unobserved interval is the evaluation
set, and **no synchronous design can have it.**

**Three policies live at once.** The game runs on the current one. Two more are
running, unseen. The designer chooses which to demote **without having seen what
the demoted one did in the interval.** This is a deliberate, controlled blindness
that generates asymmetric understanding.

**Design consequence: do not fix the lag.** Any implementation that lets the
system-two observe its own policies in real time has removed the only novel
thing about this.

## 6. Agents are script writers

> **Agents are script writers because it allows the game to continue whether or
> not the model calls output.**

The model is **optional to the loop.** A dungeon that freezes because a model is
slow, or refused, or rate-limited has thrown away the property that makes it
worth building. The script plays; the model edits the script.

## 7. The lunch theory of mind — the sharpest framing in the brief

> **I might not know where I'm going to eat or what I'll order when I get there,
> but my decisions procedurally iterate from my state.**
>
> **The options for where to eat go down as I leave my work's building** and get
> stopped several times to chat on the way to the car, **because my limited time
> starts to mean I can't go to restaurants that take as long to order.**
>
> **Or in one of those conversations, I might fish for a companion to go to lunch
> with, changing where I go and the UX of the lunch break more broadly.**
>
> **Or I might start driving out of the parking lot and decide at the moment of
> the fork in the road between going home to make a sandwich or going to my
> typical place — and the reason is never spelled out in my head, because I was
> listening to the radio about something different, and I let my system-one
> thinking just drive to the path of least resistance instead of creating for
> myself a chain of thought to prove to myself one way or another to drive.**

**What this specifies, precisely:**

- **A decision is a function of state, not a deliberation.** Nobody reasons it
  out. The option set is pruned by state, continuously.
- **Options narrow with time.** Every minute spent talking removes restaurants
  with long waits. **The action space is time-indexed.**
- **Fishing for a companion changes the destination and the whole UX**, not just
  a detail of it. **The state includes other agents, and it changes what you are
  optimising.**
- **At the fork, system-one takes the path of least resistance and the reason is
  never articulated.** Most decisions are not justified because they are not
  deliberated. **A model that emits a chain of thought for every move is not
  modelling this agent; it is doing something the agent does not do.**

**And the reverse, which is the design brief:**

> **So a dungeon agent should be a state-function, and the *interesting*
> question is not why it chose, but which of its own decisions it never
> justified — and whether the second system noticed.**

## 8. What each design must produce

Round 1 of many. Every lane builds a **runnable thing in `gh-dungeons`**, not a
memo, and the team **competes**: different architectures, same dungeon, measured
against each other on the same runs.

And at the end of every round, for each thing that worked:
**extract it into its own repo as a modular building block someone else can
build from** — because a building block that lives inside a game is not a
building block.

---

*Preserved verbatim-in-substance from Casey's brief, 2026-10-02. Interpretations
belong in the lane reports, not here.*
