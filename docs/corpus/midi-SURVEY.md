# MIDI SURVEY — 91 `fleet-midi-*` repos, and the symbolic-substrate question

**Lane:** SCOUT — MIDI as more than music, and tensor-music.
**Date:** 2026-10-02. **All claims below are measurements, not README claims.** Where something
could not be measured it says `UNVERIFIABLE`.

---

## 0. Scope, method, and three corrections to the brief

**Method.** `SuperInstance` is a *user* account (Casey Digennaro, 5,129 public repos), not an org,
so `api.github.com/orgs/...` 404s. The GitHub API allows 60 unauthenticated requests/hour, which
cannot census 132 repos. The account's HTML repository search (`?tab=repositories&q=`) is not rate
limited and filters by substring, so the census was run through that, then **every repo was
`git clone --depth 1`'d** and read from disk. 91/91 clones succeeded in 45 s. Nothing below is
inferred from a description field.

### Correction 1 — the population is **91**, not 132

`q=fleet-midi`, paginated to exhaustion, returns **91** repos. Pages 6–8 are empty (217 KB
no-results shells, identical to each other — a real signal of exhaustion, not a parse failure).

### Correction 2 — "three numbers for one population" is itself a finding

| source | number | what it is |
|---|---|---|
| the brief | 132 | a hypothesis |
| `q=fleet-midi` census | **91** | the prefix, exhaustively paged |
| `flux-tensor-midi/README.md` | **180** | *"the MIDI fleet (180 repos)"* |

Three numbers, one population, no two agree, and all three are stated in the confident present
tense. **A repo count in this fleet is a claim, not a measurement.** This is the lane's signature
disease applied to the lane's own brief.

### Correction 3 — the wider surface is 225, and the good work is not named `fleet-midi-*`

Sweeping `q=midi|music|audio|synth|tonal|note` returns **225** music-adjacent repos, 134 of them
outside the prefix. The two that matter — `plainsong` and `flux-tensor-midi` — are both in that 134.
**Searching for a family by its name finds its least interesting members.**

---

## 1. FINDING: the 91 repos are one repo, instantiated 91 times

Totals across the 91: **1,326 files, of which 338 are markdown and 174 are code.** Mean 5.9 code
files/repo; median 1.

**Structure after normalization.** Every repo's code was hashed after replacing the agent name,
the port, and all integers with placeholders. Result: **73 distinct code-file contents covering the
79 repos that have any code at all.** The largest groups are one file shared *verbatim* by:

- **14 repos** share one `process.go` (batch, foxdot, generator, graph, juice, …)
- **13 repos** share one `process.js` (bridge, conductor, harmonizer, looper, mapper, …)
- **8 repos** share one `lib/rust/src/lib.rs` (collab, cycle, feed, live, pedagogy, quantum, …)
- **5 repos** share one Python body (bass, chord, melody, scale, voicing — the *pitch* agents)

Three classes, and they are not close:

| class | n | what is actually there |
|---|---|---|
| **no code at all** | **12** | 3 `.md` + `LICENSE` + `.gitignore`. `arpggiator`, `articulation`, `delay`, `gliss`, `inversion`, `mode`, `quantizer`, `remapper`, `reverb`, `router`, `substitution`, `tremolo`. **README-only repos with no engine.** |
| **the template** | **74** | 1–7 code files, all copies of the shared scaffold |
| **real MIDI I/O** | **3** | `sonicpi` (velocity→amp, **verified running**), `text2midi` (uses `mido`), `tokenizer` (`note_on` vocabulary) |
| **real code** | **2** | `fleet-midi-pulse` (1,773 LoC Rust), `fleet-midi-harmonizer` (8 modules) |

`fleet-midi-harmonizer` and `fleet-midi-pulse` are the only two whose source is unique anywhere in
the family. Both are genuine — real musical semantics (BPM/tick/swing/fermata tempo maps;
`no_crossing` counterpoint constraints), and both have **real tests: 85 and 73.**

**Five repos in this family do real music work: `pulse`, `harmonizer`, `sonicpi`, `text2midi`,
`tokenizer`.** Four of those five have CI. The CI base rate is 7/91 = 7.7%. With n = 5 this is an
association, not a cause, and I am not claiming one — but it is not a coincidence that looks like
one, and it is the most actionable pattern in the census: **the only repos that do the work are
the ones somebody wired to a build.**

*(Self-correction, recorded because it nearly went out as a finding: I first wrote "0 of 174
implement a MIDI operation" from a grep over 16 `engine.py` files, then generalised it to the
whole family. It was false. `fleet-midi-sonicpi` was running the whole time and returns
`amp: 0.01` for velocity 1 and `amp: 1.00` for velocity 127. The narrow claim — that the
`engine.py` template never touches a MIDI byte — is verified and survives. The broad claim does
not, and is retracted here rather than quietly dropped.)*

---

## 2. FINDING: the velocity service is a constant function

`fleet-midi-velocity` — *"`fleet-midi-velocity` — HTTP server on :2171"* — has exactly one
function capable of doing musical work:

```python
def _analyze(self, data):
    """Override in subclass for per-agent analysis."""
    return {"status": "ok", "agent": AGENT, "ternary_vector": [0,0,0],
            "ternary_invariant": 0, "closed_gesture": True}
```

It **never reads `data`.** It returns a constant. And it is the *same constant* — byte-identical
after normalizing the agent name — in **all 16 repos that carry this template.**

Run it. These are real requests to a real server on a real port:

```
### fleet-midi-VELOCITY  (README: "Velocity curves — how hard do you hit?")
velocity 1      -> {"status":"ok","agent":"fleet-midi-velocity","ternary_vector":[0,0,0],"ternary_invariant":0,"closed_gesture":true}
velocity 127    -> {"status":"ok","agent":"fleet-midi-velocity","ternary_vector":[0,0,0],"ternary_invariant":0,"closed_gesture":true}
C4 v1, E4 v40, G4 v80, A4 v127 -> ... identical ...
{"banana": true}-> ... identical ...
{}              -> ... identical ...
```

`p1 == p50 == p99 == mean`. Per ORIENTATION's own rule — *"never report `p99 == p50 == mean` as a
distribution; a zero-variance 'distribution' is a constant; check for that first"* — **this is not
a velocity analyzer. It is a constant wearing the costume of one.** `ternary_vector: [0,0,0]` is
the README's own encoding for *"neutral, neutral, neutral"* on all three axes, for every input
that has ever existed.

`grep` confirms the scope precisely: across the **16** `engine.py` files that carry this
template, **zero** contain `127`, `note_on`, `0x90`, `mido`, or any MIDI library. Every one of the
16 named "dial" services — `velocity`, `dynamics`, `articulation`, `expression`, `pan`,
`modulation`, `tempo`, `groove`, `register`, `scale`, `chord`, `melody`, `bass`, `voicing`, `cc`,
`fx` — is in that set. **Not one of them has ever heard a MIDI byte.** (`note_on` appears in 2
repos outside the template and `mido` in 1; see §1. The template is the whole of the "dial"
family, and the dial family is the whole of the claim.)

**And the README contradicts the code.** 16 READMEs document the response as
`"closed_gesture": false`; all 16 return `True`. The one value a consumer could check against
documented behaviour is a value the server cannot emit.

> **This is the fleet's signature disease in its purest form, and nobody had to be careless.**
> The response is well-formed JSON. It has a valid `status`, three valid integers, a valid
> boolean. Every schema check passes. Every linter passes. Nothing is wrong in any way a machine
> can detect. The artifact is *checkable* and *wrong*, and the check is the only thing standing
> between you and the truth.

### The 172 "tests"

`#[test]` grep finds 172 across the family — **a count that is itself misleading.** 170 of them are
one golden-value test replicated from the shared Rust template:

```rust
assert_eq!(process(&v, 60), vec![60,64,64,60,64,64,60,64,68]);
```

A hardcoded expected vector. It detects *change*; it cannot detect *wrong*. And a test that pins
the output of a function that returns a constant is a control that cannot fail. The real 158
(pulse 85 + harmonizer 73) are the only tests in the family that assert a *property*.

*(Correction to my own work: my first census regex reported "0 tests, 91/91" because it looked for
a `tests/` directory. Rust `#[test]` is inline in `src/`. The regex was wrong, not the repos.
Recorded because it is the same trap that produced the false "quilt-llvm has zero tests" report.)*

---

## 3. The documentation/code seam

All 12 no-code repos have a README describing an engine. `fleet-midi-quantizer` — 5 files, zero
code — documents *"MIDI quantization from ternary timing."* There is no quantizer. The README is
not a lie; it is a description of a thing that was never built, written in the present tense.

**7 of 91 have CI** (`generator`, `harmonizer`, `musiclang`, `pulse`, `text2midi`,
`tidalcycles`, `tokenizer`). For 89 of 91, CI would have nothing to run.

---

## 4. `plainsong`: it runs, and it is the only real thing in this family

**It compiles.** The README's own four-bar example, first try, no install, no dependencies:

```
$ python3 -m plainsong compile four.song -o four.mid
Test Four Bars  --  C, 100 bpm, 4/4
1 sections, dialect: absolute
32 notes across chords (12), melody (12), bass (8)
length 9.6s
midi  four.mid

real 0m0.413s
```

0.41 s, exit 0, and the output re-parses as a **valid SMF format-1 file, 4 tracks, 480 ppq, 32
note-on events** (verified with an independent parser I wrote and then had to fix, because my
first version was wrong — see below). The README's claim of zero dependencies holds; `import
plainsong` works from a bare source tree.

**Is the notation parsed, or pattern-matched?** Parsed. `plainsong/notation/parser.py` is 976
lines over a 20,475-line package, with an explicit two-dialect grammar (`absolute`: labelled rows +
scientific pitch; `relative`: unlabelled pipe tables + roman numerals / scale degrees against a
key), a real IR (`ir.py`, 504 lines), and a separate arranger (`arrange.py`, 1,003 lines). 34 test
files, real CI, a golden corpus, and an `AGENTS.md` that opens by warning agents about mistakes
they have already made. **This is the fleet's best-engineered repository and it is not close.**

### But the artifact is not gated on the diagnosis

The parser's docstring states the policy plainly: *"Anything ambiguous becomes a diagnostic rather
than an exception, so a file always compiles to *something*."* I expected to find a silent path.
**The honest finding is more interesting: the diagnostics are excellent, and they still don't stop
the artifact.**

```
bad1 — melody row reads  H9 Q#7 Zx4
  warn  bad1.song:4: warning: melody row: nothing understood H9, Q#7, Zx4; silence there instead
      hint: chords look like Am, F#m7, Bb; pitches carry an octave, as in A4 or c3
  exit 0   →  bad1.mid  VALID SMF, 21 note-on events

bad2 — chords cover 2 bars, section runs 7
  warn  bad2.song:3: warning: [V1] chords covers 2 bar(s), the section runs 7
  exit 0   →  bad2.mid  VALID SMF, 27 note-on events

bad3 — total garbage
  warn  ×8, one per bar, "nothing understood … silence there instead"
  exit 0   →  bad3.mid  VALID SMF, 0 note-on events
```

**A total-garbage input produces a structurally valid, correctly-formatted, playable MIDI file
containing no music.** The musical content is gone; the container is perfect.

Then two things make it a trap rather than a wart:

**`-q/--quiet` erases the last channel.** Documented as *"only print what was asked for"* — which is
exactly what an automated caller wants:

```
$ plainsong compile bad3.song -o q.mid -q
$ echo $?
0
$ ls -la q.mid
-rw-r--r-- 1 root root 157 ... q.mid        # valid, empty, exit 0, zero output
```

**There is no `--strict`.** `plainsong compile … --strict` → `error: unrecognized arguments`.

So: *loud diagnosis, ungated artifact, and a quiet flag that removes the diagnosis without changing
the artifact.* Exit codes are otherwise sane — missing file 2, unknown flag 2, empty file 1
(`no sections found` is correctly fatal). **The gap is specific: structural failures are fatal,
musical failures are not fatal and cannot be made fatal.** A file with no sections dies. A file
whose every note is `Hjkl tyu` plays.

For a tool whose stated consumer is an agent, and which ships an MCP server, this is the seam
where the score stops being the evidence. *The score is the durable artifact; the MIDI is its
projection; the diagnosis is the truth. Here the projection is written to disk and the truth is
printed to a terminal that is about to be closed.*

**The fix is small and I'd build it first: `--strict` (warnings → non-zero exit) and make `-q`
suppress cosmetics, not diagnostics.** Both are one flag each. The parse-quality work is already
done; nothing consumes it.

*(Self-correction: I first reported the argparse error as `exit 0` because I piped to `tail`.
`$?` was `tail`'s. Re-measured without a pipe: it is 2. Flagged because this is the fourth time
this fleet has lost a real exit code to a pipe.)*

---

## 5. Is anyone treating MIDI as a substrate rather than a file format?

**In the 91: no.** The decomposition the brief asks about — separate services for `dynamics`,
`velocity`, `articulation` — is real as a *directory listing* and fake as a *decomposition*. All
three are the same template returning the same constant. **It is 91 ways to write the same note,
and the same note is always `[0,0,0]`.** `fleet-midi-vel` and `fleet-midi-velocity` are two repos
for one dial, both returning zero.

**Outside the 91, in this account: yes, and it is large.** `flux-tensor-midi` — *4-dimensional
tensor representation of MIDI events, 6 languages* — is **425 top-level entries, 992 Python,
427 Rust, 225 CUDA, 445 test-related files, 184 MB.** It is the tensor-music substrate the brief
is looking for, and it is not named `fleet-midi-*` and has no MIDI port. Its README is
self-aware about the count problem — it is where the "180 repos" figure comes from.

*(`counterpoint-engine` — "Species counterpoint as constraint satisfaction — SAT/UNSAT rules,
Laman rigidity, tensor-MIDI output" — is the other real one, and is the subject of a prior lane's
vacuity finding. Not re-litigated here.)*

---

## 6. Prior art — five primary sources, read

| work | what it establishes for us |
|---|---|
| **Music Transformer** (Huang, Vaswani, Uszkoreit; arXiv:1809.04281) | Symbolic, relative timing, self-reference across timescales. The symbolic-representation line is 2018-vintage and mature. |
| **MusicGen** (Copet et al.; arXiv:2306.05284) | Audio tokens, single-stage LM. "Better controls" means *text conditioning*, i.e. one dial with a text knob. |
| **Instruct-MusicGen** (arXiv:2405.18386) | Editing, not synthesis, as the primitive — add/remove/separate stems via instruction tuning. |
| **BeatEdit** (Gu, Qian, Zhou, Liu; arXiv:2607.11124) | **The key citation.** Recasts symbolic generation as explicit editing and attributes prior failure to *representation*: *"conventional event-based music encodings lack the structural properties required by explicit music editing."* Its **BEAT** encoding is beat-grid-anchored precisely so it is editable. |
| **LZMidi** (Ding, Gorle, Bhattacharya, Haste; arXiv:2503.17654) | LZ78 on MIDI, **no neural network**, competitive FAD/WD/KL, 30× faster training and 300× faster generation on CPU, with universal convergence guarantees. |
| **Disentangled Representations for Controllable Music Generation** (Ibáñez-Martínez, Nkama, Poltronieri, Serra; arXiv:2602.10058) | Probes whether "named" coordinates are actually independent. Finding: **"inconsistencies between intended and actual semantics of the embeddings… current strategies fall short of producing truly disentangled representations."** |

*(The MIDI Manufacturers Association technical summary PDF 404s — it returns an HTML error page,
74 KB, not a PDF. **UNVERIFIABLE**; I have not cited spec details from it. My own knowledge of
SMF structure is labelled as such and is not load-bearing for any claim above.)*

**Two of my six first-pass arXiv IDs were wrong** — I misremembered `2309.04380` and `1804.09361`,
which are an astrophysics paper and a graphene-composites paper. Fetched, read, discarded. Recorded
because it is exactly the failure mode this lane was told to avoid.

**BeatEdit is the prior art for the brief's central architectural claim, and it says the claim is
right for a reason the brief did not give.** It is not "symbolic is easier to inspect." It is
**"the encoding determines which operations are possible."** A beat-grid-anchored score is
editable; an event stream is not. That is a stronger and more testable version of
`text → [renderer] → domain object → [display] → output`, and it is published.

---

## 7. Casey's proposal: which is a dial, which is a curve, which is a metaphor

> *"A GAN is not a process with a conclusion but a **dial** … a structured judge gives you a
> **space** of dials where a binary discriminator gives you one axis … take a Duke state, convert
> it to Count Basie, convert it back, and look at the **residual** … the iterative cycle, read as a
> waveform rather than as points, is the real signal."*

Four claims. They are not the same kind of claim and should not be adopted as a unit.

### (a) "A GAN is a dial" — **metaphor. Do not build.**

A GAN has a conclusion: the minimax solution, and training is an optimization trajectory with a
stopping condition. A dial is a knob you set and the system obeys *now*. The generator is not
dial-like; it is a point in weight space that training moves. The proposal's own round-trip idea
depends on this being false — you cannot take "a Duke state" and "a Basie state" as coordinates of
something being dialled unless the thing is not a trajectory. **The metaphor and the measurement
contradict each other, and the measurement is the better one.**

### (b) "A structured judge gives a space of dials where a binary one gives one axis" — **true, and vacuous as stated. The premise is empirically false in the literature.**

A binary discriminator is the D=1 case of a vector-valued one. So "space of dials" reduces to "the
output has coordinates." Fine. But **coordinates are not dials.** A dial requires a map from
*knob settings* to outputs — an independently controllable actuator. A judge sits downstream and
is a function of x; nothing in it makes its coordinates independently reachable. Holding axis 2
fixed while varying axis 1 is only meaningful if the judge is locally surjective along that
direction, and that is a property you have to *establish*, not assume.

And it has been established, negatively, by people with instruments: **arXiv:2602.10058** probes
exactly this across four axes (informativeness, equivariance, invariance, disentanglement) and
finds **"inconsistencies between intended and actual semantics of the embeddings,"** concluding
current strategies "fall short of producing truly disentangled representations." **Labelling a
dimension "voicing" does not make it a voicing dial.** Do not adopt (b) without running a
disentanglement probe on your own judge first; that probe is the deliverable, and it is cheap.

### (c) The round-trip residual — **this is a real measurement. Build this first.**

Duke → Basie → Duke, keep the residual. This is genuinely good and genuinely unclaimed, and it is
cheap: no new model, no adversarial training, just a map and its inverse and a norm.

The only correction is to stop overselling what it measures. It is **not** "the geometry of
Duke-ness in weight space." It is the **singular-value spectrum of the operator** `f∘g` — how much
of the input direction survives a round trip. Read that way it is better, because it is
falsifiable: you get a *spectrum*, not a vibe. Directions with large residual are Duke-features
the representation cannot hold; directions with small residual are the ones the map has
collapsed. **That is a measurement of a representation's rank, dressed as a measurement of
style — and the dressed-up version is the one that will mislead you.** The residual is a number;
say it is a number.

### (d) Reading the training cycle as a waveform — **a diagnostic, worth one afternoon, not a program.**

GAN training oscillation is well-documented lore: D's output hovering near 0.5, mode-collapse
dynamics, periodic spikes from the discriminator overpowering the generator. Plotting the score
against iteration and calling it a waveform tells you training is oscillating — true, known, and
not a finding. **The interesting version, which nobody has done, is (c) not (d):** stream the
*round-trip residual* per iteration. That is a curve, it is not lore, and it would show whether
the representation's rank is collapsing or recovering over training. If you want one plot from
this whole proposal, it is that one, not the discriminator's.

### What I would actually build, in order

1. **The round-trip residual, with a disentanglement probe attached** (c + the (b) caveat).
   Two artifacts, one afternoon each, no training. If the probe says the coordinates are not
   independent, the residual tells you *which* ones collapse. These are the same measurement and
   they should be built together.
2. **`--strict` on plainsong**, and make `-q` cosmetic. An hour. It converts the fleet's best
   musical asset from "a thing that always succeeds" into "a thing that can say no" — and it is
   the only item on this list where the score/diagnosis seam is currently open.
3. **Not the GAN.** If the objective is distributional match on MIDI, **LZMidi matches diffusion
   models on FAD/WD/KL with a compressor, 30–300× cheaper, and a convergence guarantee.** Before
   funding an adversarial training run, establish that the discriminative signal beats a
   sequential probability assignment. It very possibly does not. That is a cheap negative and it
   should be run *first*, as a control.

### The reframe that ties it to plainsong

The brief is right that the judge should operate on the symbolic layer, and this is the most
important thing in the survey. But it is worth being precise about **what legibility buys**, because
it is easy to overclaim here.

A symbolic representation does **not** make the judge more accurate at telling Duke from Basie. A
discriminator on MIDI tokens is still a discriminator on tokens. **Legibility buys
interpretability and — decisively — intervention.** You can open a score and change one voice. You
cannot open a discriminator.

And that is precisely where a dial comes from. **A dial lives on the actuator side, not the judge
side.** A named, independently editable field in a score that a renderer consumes — voicing,
articulation, dynamics, tempo — is a real dial, because moving it changes the output and holding
the rest fixed is well-defined. A named axis of a judge's output is not, unless you have proven
the map is locally surjective. So the brief's "space of dials" intuition is right, and its
location is wrong: **it belongs to the notation, not to the judge.** The 91 repos were trying to
build it in the second place and returned `[0,0,0]`.

---

## 8. What I learned that changes what someone else should do

1. **Cloning 91 repos took 45 seconds and the GitHub API would not have done it.** The account is a
   *user*, not an org, and the 60/hr unauthenticated limit cannot census anything at fleet scale.
   `git clone --depth 1` in parallel has no rate limit, is not throttled for tens of repos, and
   gives you the actual files. **Census by clone, not by API.** A filename classifier is not a
   census, and neither is a description field.

2. **"132 repos" and "180 repos" and "91 repos" are all in this fleet's documents, all in the
   present tense, and all wrong.** Counts in this account are claims. If a number is load-bearing,
   re-measure it before building on it — including the numbers in your own brief.

3. **The highest-value audit finding available in a repo is the cheapest one: normalize the
   source and hash it.** One regex plus one SHA-256 turned "132 projects" into "one project,
   instantiated 91 times," with a per-file leaderboard. It found the duplication in seconds, no
   execution required, and it is fully reproducible. **Run this on every family before reading
   any README.**

4. **A constant function will pass every check you have.** `[0,0,0]` for velocity 1 and velocity
   127 is well-formed, schema-valid, and constant. Per ORIENTATION's own rule about zero-variance
   distributions — *check for a constant first* — the highest-value test in a service is not
   "does it return 200" but **"does it return a different answer for two inputs that must differ."**
   One POST with two adversarial payloads, run against every service, would have caught this in
   91 seconds. **That is the audit to automate fleet-wide.**

5. **A template is not a bug; a template with no test is a claim.** 89 of 91 repos here would be
   perfectly good *scaffolds* — the failure is that 77 of them have been *presented and
   documented* as engines, and the 12 no-code repos have READMEs describing machines that were
   never built. **The defect is the documentation, not the absence of code.** A scaffold honestly
   labelled as a scaffold costs nothing and is useful. A scaffold described in the present tense
   is the fleet's signature disease wearing a port number.

6. **plainsong's diagnostics are good and its artifact is ungated — and that is a one-flag fix,
   not an architecture problem.** Everything needed to gate the artifact already exists and is
   already computed. It is just never consulted for the exit code. *Before adding a new instrument
   to a codebase, check whether the instrument it already has is wired to anything.* That is a
   cheaper question than building a checker, and it was the whole finding.

7. **Legibility is not accuracy.** Reading the brief's own claim precisely: operating on the
   symbolic layer does not make a judge better at Duke-vs-Basie. It makes the output
   **intervention-ready**. Dials live on the actuator side — in the notation — not in the judge's
   output vector. Anyone building "structured judges as dials" should read arXiv:2602.10058 first
   and be prepared to find their coordinates are not independent.

8. **Run the cheap negative before the expensive build.** LZMidi matches diffusion models on
   distributional metrics using an LZ78 compressor on a CPU. If a GAN's discriminator is the
   load-bearing primitive, that is the control that has to come first.

9. **The durable artifact is the score, and this fleet already knows it — in one repo, which is
   named after neither MIDI nor music.** `flux-tensor-midi` (425 entries, 445 test-related files)
   and `plainsong` (20,475 LOC, 34 test files) are both real. Neither is a `fleet-midi-*`. **A
   census keyed on a name prefix finds the family that named itself and misses the family that
   did the work.**

---

## Appendix A — full census of the 91

`port` = the port the service claims. `code files` = .py/.js/.ts/.rs/.go/.c/.h/.mod, excluding
build artifacts. `tests` = real property assertions vs. a replicated golden-value test.
`REAL` = unique source in the family. `NO CODE` = 3 markdown files and a LICENSE, nothing else.

**Reading the "does" column: it is the README's first line, quoted, and for 89 of 91 rows it
describes a machine that does not exist.** That is the point of reproducing it here.

| # | repo | does | port | code files | CI | tests |
|---|------|------|------|-----------|----|-------|
| 1 | `fleet-midi-arp` | Arpeggiation engine — the notes cascade. | 2169 | 1 | — | 1 golden |
| 2 | `fleet-midi-arpggiator` | APeppgiator from agent state patterns | — | 0 | — | 0 |
| 3 | `fleet-midi-articulation` | Fleet MIDI service. | — | 0 | — | 0 |
| 4 | `fleet-midi-bass` | Bass line generator — the harmonic and rhythmic anchor. | 2175 | 1 | — | 1 golden |
| 5 | `fleet-midi-batch` | Batch processing engine for fleet-wide MIDI operations | — | 1 | — | 1 golden |
| 6 | `fleet-midi-blend` | **Blend MIDI from multiple agent sources.** | — | 3 | — | 1 golden |
| 7 | `fleet-midi-bridge` | Ternary vectors → MIDI pitch sequences. The same mapping i | — | 3 | — | 1 golden |
| 8 | `fleet-midi-cc` | Control Change processor — smooth those CC messages! | 2164 | 1 | — | 1 golden |
| 9 | `fleet-midi-chaos` | Chaotic attractor-based MIDI from agent state dynamics | — | 1 | — | 1 golden |
| 10 | `fleet-midi-chord` | Ternary chord quality analyzer — major, minor, or other? | 2160 | 1 | — | 1 golden |
| 11 | `fleet-midi-cluster` | Clustered note generation from tensor states | — | 2 | — | 1 golden |
| 12 | `fleet-midi-collab` | **Multi-user collaborative MIDI composition.** | — | 1 | — | 1 golden |
| 13 | `fleet-midi-composer` | **Higher-level composition engine — generates complete pie | — | 2 | — | 1 golden |
| 14 | `fleet-midi-conductor` | Baton-like orchestration from a single control point — par | — | 2 | — | 1 golden |
| 15 | `fleet-midi-cycle` | **Cyclic patterns from agent state periodicity.** | — | 1 | — | 1 golden |
| 16 | `fleet-midi-decode` | **Decompressed MIDI decoding from fleet transport.** | — | 3 | — | 1 golden |
| 17 | `fleet-midi-delay` | **Delay/echo from agent state repetition.** | — | 0 | — | 0 |
| 18 | `fleet-midi-drone` | **Drone/pedal point MIDI from agent sustain.** | — | 2 | — | 1 golden |
| 19 | `fleet-midi-dynamics` | Dynamic contour — the shape of volume over time. | 2166 | 1 | — | 1 golden |
| 20 | `fleet-midi-echo` | **Acoustic echo modeling for fleet MIDI spatialization** | — | 1 | — | 1 golden |
| 21 | `fleet-midi-effects` | MIDI effects — delay, arp, transposition, randomization | — | 3 | — | 1 golden |
| 22 | `fleet-midi-emergent` | Emergent pattern generation — music emerges from agent int | — | 1 | — | 1 golden |
| 23 | `fleet-midi-encode` | **Compressed MIDI encoding for fleet transport.** | — | 3 | — | 1 golden |
| 24 | `fleet-midi-expression` | Expression and articulation — the soul between the notes. | 2165 | 1 | — | 1 golden |
| 25 | `fleet-midi-feed` | **Feedback/FMIDI from agent state feedback loops.** | — | 1 | — | 1 golden |
| 26 | `fleet-midi-filter` | **Conditional MIDI routing and filtering.** | — | 3 | — | 1 golden |
| 27 | `fleet-midi-flux` | Flux/flow-based MIDI generation from agent entropy | — | 1 | — | 1 golden |
| 28 | `fleet-midi-foxdot` | **3007 -d '{"code":"p1 >> pads([0,4,7], dur=4)"}'** | — | 2 | — | 1 golden |
| 29 | `fleet-midi-fractal` | Fractal-based MIDI generation from recursive ternary struc | — | 1 | — | 1 golden |
| 30 | `fleet-midi-fx` | Effects routing — wet, dry, or somewhere in between. | 2172 | 1 | — | 1 golden |
| 31 | `fleet-midi-gateway` | Unified API gateway for all MIDI fleet services | — | 1 | — | 1 golden |
| 32 | `fleet-midi-generator` | ** +1 ascends, 0 repeats, -1 descends** | — | 2 | yes | 1 golden |
| 33 | `fleet-midi-genetic` | **Genetic algorithm MIDI evolution from agent fitness.** | — | 2 | — | 1 golden |
| 34 | `fleet-midi-gliss` | **Glissando/portamento from agent state slides.** | — | 0 | — | 0 |
| 35 | `fleet-midi-grammar` | **Grammar-based MIDI from L-systems.** | — | 2 | — | 1 golden |
| 36 | `fleet-midi-graph` | Graph-based MIDI routing through agent networks | — | 1 | — | 1 golden |
| 37 | `fleet-midi-groove` | Swing and groove — the feel of time. | 2170 | 1 | — | 1 golden |
| 38 | `fleet-midi-harmonizer` | **Conservation-governed MIDI harmonization. SATB voice lea | — | 13 | yes | 73 real |
| 39 | `fleet-midi-inversion` | **Chord inversion engine from agent state position** | — | 0 | — | 0 |
| 40 | `fleet-midi-juce` | **** [osc-server](https://github.com/SuperInstance/fleet-o | — | 3 | — | 1 golden |
| 41 | `fleet-midi-layer` | Layered composition from multi-agent states | — | 2 | — | 1 golden |
| 42 | `fleet-midi-live` | **Low-latency live performance MIDI engine.** | — | 1 | — | 1 golden |
| 43 | `fleet-midi-looper` | Loop-based MIDI composition engine | — | 4 | — | 1 golden |
| 44 | `fleet-midi-mapper` | **Map any data stream to MIDI parameters.** | — | 3 | — | 1 golden |
| 45 | `fleet-midi-markov` | **Feed it 8 notes. Get infinite variations. No GPU require | — | 6 | — | 1 golden |
| 46 | `fleet-midi-melody` | Melodic contour — the shape of a tune. | 2174 | 1 | — | 1 golden |
| 47 | `fleet-midi-mesh` | Mesh network topology for fleet MIDI distribution | — | 1 | — | 1 golden |
| 48 | `fleet-midi-mode` | Identifies modal centres (Ionian, Dorian, Phrygian, Lydian | — | 0 | — | 0 |
| 49 | `fleet-midi-modulation` | Modulation rate — vibrato, tremolo, and LFO speed. | 2168 | 1 | — | 1 golden |
| 50 | `fleet-midi-monitor` | Real-time visualization of fleet MIDI activity — part of t | — | 2 | — | 1 golden |
| 51 | `fleet-midi-morph` | Smooth morphing between agent state vectors as musical tra | — | 4 | — | 1 golden |
| 52 | `fleet-midi-musiclang` | **Agent tension states become chord progressions.** | — | 4 | yes | 1 golden |
| 53 | `fleet-midi-pan` | Spatial positioning — put sounds where they belong. | 2167 | 1 | — | 1 golden |
| 54 | `fleet-midi-pattern` | **Pattern language for fleet MIDI generation.** | — | 3 | — | 1 golden |
| 55 | `fleet-midi-pedagogy` | **Music theory education through fleet generation.** | — | 2 | — | 1 golden |
| 56 | `fleet-midi-phase` | **Phase-shifted MIDI from agent state offsets.** | — | 2 | — | 1 golden |
| 57 | `fleet-midi-player` | **** [jam-engine](https://github.com/SuperInstance/fleet-j | — | 1 | — | 1 golden |
| 58 | `fleet-midi-prob` | Probabilistic state transition music from agent Markov cha | — | 4 | — | 1 golden |
| 59 | `fleet-midi-pulse` | Heartbeat-driven timing layer for the [fleet-midi](https:/ | — | 10 | yes | 85 real |
| 60 | `fleet-midi-quantizer` | MIDI quantization from ternary timing — part of the SuperI | — | 0 | — | 0 |
| 61 | `fleet-midi-quantum` | **Quantum state-inspired MIDI from superposition.** | — | 2 | — | 1 golden |
| 62 | `fleet-midi-rand` | Chance/aleatoric music generation from agent randomness. | — | 4 | — | 1 golden |
| 63 | `fleet-midi-recorder` | Record and replay fleet MIDI sessions — part of the SuperI | — | 2 | — | 1 golden |
| 64 | `fleet-midi-register` | Octave register — where in the frequency spectrum? | 2173 | 1 | — | 1 golden |
| 65 | `fleet-midi-remapper` | MIDI note/CC remapping engine — part of the SuperInstance  | — | 0 | — | 0 |
| 66 | `fleet-midi-resonance` | **Resonant frequency MIDI from agent harmonics.** | — | 2 | — | 1 golden |
| 67 | `fleet-midi-reverb` | **Convolution reverb from agent decay profiles.** | — | 0 | — | 0 |
| 68 | `fleet-midi-router` | **Event-based MIDI routing between fleet agents.** | — | 0 | — | 0 |
| 69 | `fleet-midi-scale` | Scale and mode detector — what key are we in? | 2161 | 1 | — | 1 golden |
| 70 | `fleet-midi-script` | **Scripting language for fleet MIDI composition.** | — | 3 | — | 1 golden |
| 71 | `fleet-midi-sequencer` | Step sequencer from ternary state vectors | — | 4 | — | 1 golden |
| 72 | `fleet-midi-sonicpi` | **3006 -d '{"notes":[60,64,67,72],"bpm":120}'** | 3006 | 2 | — | 1 golden |
| 73 | `fleet-midi-spread` | Spread/arpeggiation of agent state vectors | — | 2 | — | 1 golden |
| 74 | `fleet-midi-stream` | Stream processing MIDI pipeline engine | — | 1 | — | 1 golden |
| 75 | `fleet-midi-studio` | Browser-based MIDI workstation chaining all fleet tools | — | 1 | — | 1 golden |
| 76 | `fleet-midi-substitution` | **Chord substitution engine from agent state tension** | — | 0 | — | 0 |
| 77 | `fleet-midi-swarm` | **Swarm intelligence MIDI from multi-agent states.** | — | 2 | — | 1 golden |
| 78 | `fleet-midi-symusic` | **** [tokenizer](https://github.com/SuperInstance/fleet-mi | — | 1 | — | 1 golden |
| 79 | `fleet-midi-synth` | **Web Audio API synthesis engine for fleet MIDI.** | — | 2 | — | 1 golden |
| 80 | `fleet-midi-tempo` | Tempo and time feel — how fast and how swung? | 2163 | 1 | — | 1 golden |
| 81 | `fleet-midi-text2midi` | **Type "jazz piano in Cmaj7" and get a real MIDI file.** | — | 3 | yes | 1 golden |
| 82 | `fleet-midi-tidalcycles` | **Ternary strategy vectors become percussive patterns.** | — | 7 | yes | 1 golden |
| 83 | `fleet-midi-tide` | Tidal harmonic generation from agent cycles | — | 1 | — | 1 golden |
| 84 | `fleet-midi-tokenizer` | ** H(header) T(tempo) K(key) S(time_sig) E(track) N(note_o | — | 4 | yes | 1 golden |
| 85 | `fleet-midi-tremolo` | **Tremolo from agent amplitude modulation.** | — | 0 | — | 0 |
| 86 | `fleet-midi-vel` | **Velocity-sensitive MIDI from agent intensity** | — | 1 | — | 1 golden |
| 87 | `fleet-midi-velocity` | Velocity curves — how hard do you hit? | 2171 | 1 | — | 1 golden |
| 88 | `fleet-midi-visualizer` | **** [hydra-connector](https://github.com/SuperInstance/fl | — | 1 | — | 1 golden |
| 89 | `fleet-midi-voicing` | Voicing analyzer — how wide are your intervals? | 2162 | 1 | — | 1 golden |
| 90 | `fleet-midi-wave` | Waveform-based MIDI from agent state oscillations | — | 1 | — | 1 golden |
| 91 | `fleet-midi-weave` | Interleaved multi-voice patterns from ternary | — | 2 | — | 1 golden |
**Summary:** 91 repos · 1,326 files · 338 markdown · 174 code files (159 after excluding build
artifacts) · **12** with no code at all · **74** instances of one template whose `_analyze` returns
one constant, none of which has ever seen a MIDI byte · **3** with real MIDI I/O (`sonicpi`
verified running, `text2midi` uses `mido`, `tokenizer` has `note_on` vocabulary) · **2** with real
code and real tests (`pulse` 85, `harmonizer` 73) · **5** repos do real music work, **4** of them
with CI against a 7.7% base rate · **7** with CI in total.

**One POST with two adversarial payloads against every service in the fleet would have separated
those 5 from the other 86 in 91 seconds.** That is the audit to automate.

---

## Appendix B — things I could not measure

- **`fleet-resolver.prong-potassium.workers.dev` is unreachable from this sandbox** — DNS does not
  resolve (`HTTP 000` on 3 attempts; `getent hosts` returns nothing). The resolver covers 477
  repos / 85,990 files and would have made this census a single query. It is listed as a live
  surface in ORIENTATION.md and is **not reachable from here**. This is `INACCESSIBLE`, not
  `EMPTY`, and it is not a claim that the resolver is down.
- **The MIDI Manufacturers Association technical summary PDF 404s** (returns a 74 KB HTML error
  page). I cite no SMF spec facts from it. My own MIDI structural knowledge is used only in §4,
  and it was checked by writing a parser — which was wrong on the first attempt and was fixed
  before any number was reported.
- **7 non-prefix MIDI repos were cloned but not audited** (`mmx-toolkit`, `spline-midi-smooth`,
  `ternary-counterpoint`, `fleet-jepa-midi`, `fleet-sheet-music`, and 2 others). GitHub began
  throttling after 91 rapid clones. `counterpoint-engine` and `flux-tensor-midi` are the two that
  mattered and both landed; the rest are **UNVERIFIABLE**, not clean.
- **`quilt-velato`, `ternary-cuda-kernels-v2`, `grand-synthesis`** appeared in name sweeps and
  were not opened. Not a negative.

---

## Final line

**Is a score a better thing to keep than a recording, and has anyone in this fleet noticed?**

**Yes, better — and yes, exactly one repo has noticed, and it is the repo this lane was sent to
audit.**

`plainsong` is the proof of concept: 20,475 lines, a real 976-line grammar, 34 test files, a
golden corpus, a CI gate on zero dependencies, and a `.song` file that is diffable, reviewable in
a pull request, and playable by a human who has never opened a terminal. It compiles in 0.41
seconds. The score is the artifact; the MIDI is one projection of it; a different renderer gives
you different audio with the score untouched. That is the whole doctrine — the waveform is the
projection, the score is the evidence — **built, running, and shipping, before anyone wrote it
down.**

What has *not* been noticed is the inverse. The 91 repos chose to keep the **projection** and
discard the score: they emit JSON on a port, hold no score, and cannot be diffed, reviewed, or
replayed into a different renderer. Their artifact is the thing that was supposed to be
derived. **The fleet did not fail to build the score. It built it in one repo, failed to build it
in 91, and pointed the other 91 at the MIDI file as if it were the source.**

The one open seam is four lines long: `--strict` does not exist, `-q` silences the only
instrument, and total garbage still exits 0 with a valid, empty, playable MIDI. **The score
exists. The evidence is computed and thrown away. The artifact is written anyway.** Close that
and the fleet finally has a repo where you cannot get well-formed wrong music — which is the only
status worth having.
