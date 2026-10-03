# Graceful fail, and the type it forces into the open

2026-10-02. From Casey, describing a boat. It is the clearest statement yet of
what a "codespace" is, and it produces a record field I have not seen anywhere.

---

## 1. The chain, and the property that makes it work

```
cloud assistant        conversationalist, all day, smart
  ↓
jetson 8GB             grep logs + past conversations, answers
                       "how many lb of each species over the last 3 trips"
                       WITH LINKS TO SOURCE — but cannot say anything
                       intelligent about the connections between them
  ↓
raspberry pi (LAN)     wake word, STT/TTS. "I, I, 10 turning degrees port."
                       can still load the latest uploaded algorithm
  ↓
esp32                  the autopilot. dead-band + rudder counter-rudder gates.
                       1990s. present, always, on the board
  ↓
hand on the wheel
  ↓
hydraulics fail        pipe-wrench on the rudderpost, decouple the rams
  ↓
rudderpost lost        drag on one side or the other
  ↓
radio                 call for the next fallback
  ↓
life-rafts, survival suits
```

**The load-bearing property is not that each rung is weaker. It is that each rung
is a strict subset that is already present.** Nothing is fetched on the way down.
The ESP32 has held its gates the whole time.

**And the fine-tune propagates down through the chain.** The algorithm improved
somewhere higher in the quilt gets *uploaded* until it reaches the ESP32, which
also still holds the old copy. That is deployment with a fallback, which is
almost nothing anyone builds.

## 2. The surprising split: citation is *not* above regulation

| | Jetson | Pi | ESP32 |
|---|---|---|---|
| can retrieve and cite source | **yes** | no | no |
| can reason about connections | no | no | no |
| can regulate the vessel | no | no | **yes** |
| can talk | yes | **yes** | no |

**A retrieval-with-citations agent is not a superset of a dead-band autopilot,
and neither is a superset of the other.** They are different rungs answering
different questions. The Pi's only job is to *transmit the ESP32's answer in
speech* — it is a voice, not a brain, and the mechanical "I, I, 10 turning
degrees port" is the honest sound of a system that is not thinking.

**That is why this is a chain and not a hierarchy.** There is no total order on
capability, so "which level is better" is not a well-formed question. It is a
lattice with several partial orders, and a given system needs a *set* of
guarantees, not a rank.

## 3. The two views, and why neither is enough

> *The spreadsheet sees the corn maze from above. The terminal gives you the UX
> of the one in the maze.*

- **Synoptic / spreadsheet view** — topology, routing, the whole system at once.
  **Lossy about meaning.** It can show you that nine agents touch the same node
  and cannot tell you what they say to it.
- **Terminal view** — granular, manual, debuggable, rewindable. **Lossy about
  topology.** It can show you every token and cannot show you the shape.

**Neither is the artifact. The alignment between them is.**

> *Their UX can be viewed like a sequencer with the relevant agents like
> instruments on a MIDI score with their token outputs like the keys they
> trigger.*

**And here is the thing I did not have: this is a visualisation of n_eff.**

A panel with `n_eff ≈ 2` is a score where eight instruments keep playing the
same note. You would *see* it — the same key struck in unison, the chord
degenerate, the melody that is really one instrument. **Correlation becomes
audible before it becomes arithmetic.**

Two agents on the same key is a collision. Two on adjacent keys is a chord. And
the `CHOPS-FORK-VS-CHAIN` result becomes a picture: seven "instruments," one
melody, and every arrangement of them sounding like the same performance.

## 4. The scaling claim, and it is the real one

> *A repo that's a good tool can be called by millions of applications, and only
> the diffs for the application, user and hardware need to be saved.*

**This inverts what a repository is.** Today a repo is a *thing being edited*.
Under this model:

- **a repo is a capability** — a function, essentially
- **the saved artifact is a call site plus its input** — `(tool_version, user,
  hardware, input)`
- **a diff is the difference between two calls, not between two files**

So the history of a repo is **the call log of a tool, not the edit log of a
file.** And it scales globally for exactly the reason the boat does: the tool is
present everywhere, the per-application/user/hardware residue is small, and the
surviving record is the residue.

**The grid structure is the point.** `application × user × hardware` is a sparse
3-dimensional index over a very large population, and git has no primitive for
it, because git's unit is a path in a tree and this unit is a *call*.

## 5. The new type — the field that was missing

I wrote a `ControlLoop` type yesterday with `tolerance_ms` and `degradation_order`.
It was incomplete, and the boat says what was missing:

```
type Call = {
  tool_version:   str
  user:           id
  hardware:       id
  input:          bytes
  output:         bytes

  authority_level: 0..N        // <-- WHICH RUNG produced this
  depends_on:       [Call]     // what it is downstream of
  if_above_falls: {            // <-- THE NEW FIELD
    level:  int
    lost:   [str]              // what stops being true when rung <level> dies
    still:  [str]              // what survives anyway
  }
}
```

**`if_above_falls` is the whole thing, and it is a degradation axis attached to
provenance.**

Today a witness log answers *"who decided this, and on what authority."* It does
not answer *"how far down the chain does this still hold."* Those are different
questions and only the second one is asked on the boat, at 3am, in a swell,
when the Jetson is gone and the Pi is gone and the ESP32 is still holding
dead-band gates from 1994.

**A record with `authority_level: 3` — computed from cloud conversation — is
worthless the moment the radio stops working, and the record should SAY that,
in the record, before it is needed.** A record with `authority_level: 6` — a
direct physical read — is worth something almost anywhere.

This is the projection doctrine with a vertical axis attached. `what survives is
bounded by what the observation carried` now has a second clause: **and by which
rung the observation came from.**

## 6. What this means for the codespace, and it is exactly the "shell of the repo"

The codespace is not an application. It is a **space**: a shell with a tool
manifest, a display, and a rewind. The tools are whatever the current role
needs, and **the role declares which rung you are currently able to operate at.**

And the two views are not preferences:

- **terminal = the granular, manual, rewindable rung** — always available,
  because it has no GPU, no 3D, no fonts, no rendering pipeline, and therefore
  cannot fail in the ways a rendered view can
- **synoptic = the topological rung** — available when something richer is
  alive
- **the sequencer = the alignment between them** — the view that makes
  correlated agents visible as the same note

**The one you cannot lose is the one with the fewest dependencies.** That is the
argument for terminal-first, and it is a safety argument, not an aesthetic one.

## 7. Open, and I am not guessing

1. **How many rungs does a general system actually need?** Nine is a boat. Is
   the number domain-specific, or is there a small universal set? I suspect the
   answer is **two or three** — retrieve-with-citation, transmit, regulate — and
   the other six are all "be physical about it."
2. **What is the minimum viable copy of an ML algorithm at rung 6?** A
   fine-tuned model will not fit an ESP32. A distilled decision *policy* might.
   **Is there a rung below "model" that still learns?** The counter-rudder gates
   are a 1990s hand-tuned policy that predates the question — and it still
   steers.
3. **Does the MIDI/sequencer view actually help, or is it a metaphor that
   flatters?** It could be a genuinely better interface for agent work, or it
   could be a nice story that nobody uses twice. **It needs a user, not an
   argument.**
