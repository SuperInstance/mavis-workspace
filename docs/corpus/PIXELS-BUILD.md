# PIXELS-BUILD — the seed set contains the mechanism, and the mechanism is 11 frames wide

2026-10-02. Runnable in `research/pixels-build/`. **The collapse is real and it is
not the collapse you were told about.** The shape is right, three of the four asks
land on it, and the fourth — the one the collapse is being claimed *for* — is the
one the code gets backwards.

---

## 1. The collapse, stated precisely

`8c06f5beb07cb550` is a static ring of frames, a fork, a replay, an integer loss,
and a commit-or-reject. That is genuinely one mechanism and not four asks. But:

| the ask | does it land on the ring? |
|---|---|
| A/B the scripts, keep the better | **yes** — that is `evaluate_differential` |
| rewind / replay | **yes** — that is the ring |
| "the tail is recorded, not discarded" | **no** — the ring *records* 128 frames and *retains* 11 |
| syncopation: the unobserved tail is replayed before the decision | **no, and inverted** — it replays the last 11 frames eleven times |

> **The hazard the collapse is supposed to cure is the one the seed code reproduces
> exactly, and worse.** `PIXELS-ARCHITECTURE.md` FAILURE MODE 2 is "the A/B is
> measured over a window nobody watched". The seed harness decides on an 11-frame
> window while `harness->count` says 128. The 12th architecture step and the
> syncopation design are not served by this code. They are defeated by it.

So: **collapse the shape, do not adopt the code.** Everything below is what it
takes to make the shape survive contact with a compiler.

---

## 2. Where the seed set actually is

The nudge says 43 files at `research/seed-documents/` in `fleet-triage`.

- `projects/fleet-triage/research/` contains `PARALLELISM.md`, `demo.py`, `evid.py`,
  `seamclaim.py`, `seams/` and four other reports. **There is no `seed-documents/`.**
- The seed set is **`/workspace/attachments/`** — 54 directories, each one
  `pasted-text.txt`, 808 KB total.
- `WORKSPACE-INDEX.md:98` says "42 files, 385 KB" at that path. The path is wrong
  and the count is wrong. `grep -rl 8c06f5beb07cb550` finds one hit outside
  `attachments/`, and it is a digest, not the documents.

I read five in full (`8c06f5beb07cb550` the harness, `b13c47bc66efb64b` the
memory map, `3b99cfac641bf5cc` the test suite, `bb5123b9b86d4a21` the chatter
document, `edc5de6e4fe2435f` the ASCII landscape) and indexed the opening line of
all 54. **Their claim that there are no measured results in any of them is
correct, and it is the whole finding below.**

---

## 3. The 128-frame history is 11 frames wide

`SYZ_HISTORY_DEPTH 128`, `SYZ_BUFFER_SIZE 65536`, frames of `rows*cols*(1+4+1)`
bytes. At the integration call site's own `24 × 40`:

```
cells per frame            960
bytes per frame            5760
ring depth                 128
seed pool                  65536
frames the pool can hold   11
bytes actually required    737280
undersizing factor         11.25x
```

`syz_sandbox_push_frame` handles this with

```c
if (harness->pool_tail + required_space >= SYZ_BUFFER_SIZE) {
    harness->pool_tail = 0;
}
```

The ring keeps counting. The pool wraps. **Measured**, by pushing 128 frames each
carrying a unique signature and reading them back through the seed harness's own
pointer arithmetic (E2):

```
slots whose bytes are their own     11 / 128
slots holding another frame's data  117 / 128   (91.4%)
slots showing the newest frame      12 / 128
```

> **116 of the 128 frames of recorded history are never read. The 128-slot replay
> is 12 distinct frames repeated to fill the buffer, weighted ~11× against the
> near past and 0× against everything older.**

`b13c47bc66efb64b` publishes the memory map that makes this checkable in one line
and does not make it: *"Frame Index: 128 frames \* 24 bytes = 3,072B · Data Pool:
65,536 bytes"*. The seed set documents its own bug.

**The fix is not a bigger number.** In `syz_sandbox_fixed.h` the pool size is
*derived* — `SYZ_HISTORY_DEPTH * SYZ_FRAME_STRIDE` — so there is no free variable
left to mistype. The check the seed would need instead is one line, and the seed's
own constants fail it:

```
$ cc -c poolassert.c
poolassert.c:20:14: error: size of array 'pool_must_hold_the_whole_ring' is negative
```

`make check-seed-constants` treats that compiler error as the pass. **If it ever
compiles cleanly, the result is a lie.**

---

## 4. The deeper defect: the replay is not a replay

A replay is only a replay if it starts from the state that produced the targets.
`SyzHistoryFrame` records the observation and `target_actions` and **not the
engine's state**, and `sandbox_a`/`sandbox_b` are copies of the engine *now*. So
the harness re-simulates 128 frames from a state the engine was never in.

The instrument that settles it needs no statistics: **replay the live engine
against its own recorded targets.** A harness that can see its own past
reproduces those targets exactly. Any nonzero self-loss is measurement error
before a candidate even exists. 2×2, same history, same loss function (E3):

| | no state restore | state restored |
|---|---|---|
| **seed pool (aliased)** | 21100 | 3600 |
| **sized pool** | 200 | **0** |

> **Only the correctly-sized pool *with* state restore returns 0, and 0 is the
> only value a sound harness can return.** The pool fix alone gets you to 200 out
> of a possible 12800 — a 99% error floor that is pure instrumentation, all of it
> charged to the candidate.

**And the half-fix is worse than no fix.** Holding state broken and fixing only the
buffer is the arm with the most dangerous promotions in the whole factorial (E4):

| arm | disagree | **dangerous** | accept% |
|---|---|---|---|
| seed pool, state not restored | 107/600 | 30 | 9.7% |
| seed pool, state restored | 91/600 | 32 | 13.0% |
| **sized pool, state not restored** | 126/600 | **63** | 17.5% |
| sized pool, state restored *(oracle)* | 0/600 | 0 | 17.5% |

> **"Dangerous" = the arm promoted a proposal the oracle had already rejected: a
> worse script went live.** Fixing the buffer and leaving the state broken nearly
> doubles the dangerous promotions relative to fixing neither. My reading is that
> aliasing acts as an accidental tie-breaker — it pins the two losses together and
> suppresses the accept rate from 17.5% to 9.7% — so removing it hands the harness
> a comparison it is confidently mis-reading. **That reading is a hypothesis. The
> numbers are measurements; the mechanism is not isolated.**

> **A half-fix in this system is not a partial result. It is a more confident
> wrong answer.**

---

## 5. The seed set's own verification suite is the eighth green badge

`3b99cfac641bf5cc` is the document that closes the architecture: a freestanding
test that "produces a single, deterministic Golden FNV-1a Hash to prove execution
invariance". Executed (E5):

```
frames pushed                      1
harness->count after push          1
seed guard:  if (count < 16) return 0;
differential core executed         NO
proposed_accepted                  0
enters the golden receipt as       ^ 0  (XOR with a constant zero)
pool bytes covered by the hash     0 of 65536
index slots covered by the hash    2 of 128
```

**The one push, against the suite's own `if (count < 16) return 0`, means the
differential never runs. `proposed_accepted` is unconditionally 0 and enters the
golden receipt as `XOR 0`.** The test that verifies the sandbox does not execute
the sandbox and cannot distinguish the two. It hashes 2 of 128 index records and
none of the 65,536 pool bytes — so the aliasing in §3 is outside the hash's reach
by construction.

And the receipt cannot be architecture-invariant, because it hashes a struct
containing `size_t` offsets. The seed set's own memory map calls that field
*"4B/8B depending on WASM architecture"* (E6):

```
wasm32 ABI    sizeof = 24 bytes   hash 0x19931624
host 64-bit   sizeof = 40 bytes   hash 0x403CA264
equal: NO
```

> **"MUST match this signature exactly" on every machine, over a struct the seed
> set itself documents as architecture-dependent.** The magic constant
> `0x7E3A19C4` is asserted to be reproducible and, so far as this repo goes, has
> never been produced by anything.

The 64-bit layout is the real struct; the 32-bit layout is the wasm32 ABI
reconstructed by hand, because this sandbox has no wasm toolchain. **I did not
cross-compile.**

My own instruments are held to the standard the seed set's does not meet:
`make verify` confirms `lab` and `chatter` are **bit-identical across repeat runs
and across `-O0` and `-O2`**. And the one control that matters: `lab_replay`'s
accept/reject bit agrees with the verbatim seed header on **600/600** candidates,
which is what licenses the 2×2 above to be about the seed code and not about my
reimplementation of it.

---

## 6. The churn claim holds. What is missing is a floor.

The seed asserts that `total_loss_b < total_loss_a` *"prevents macro weights from
alternating rapidly when noise boundaries are tight."* Measured (E8):

```
the known-good fix offered 20x        promotions = 1   (converges)
two candidates alternating 20x         promotions = 1   (no flip-flop)
```

**That claim is true.** Integer arithmetic plus a strict inequality makes the
sequence monotone; there is no tie to break and no oscillation to damp. I expected
to knock this down and could not, and the honest thing is to say so plainly.

What it does not have is a floor. Loss is 100 per wrong bit over 128 frames × 4
actions, so a proposal can win by one bit in 512:

```
winning margin over 600 proposals:
  <=100 (1 bit)    2   <=200    0   <=400    7   <=800    4   <=1600    8   >1600   73
  accepted 94 of 600; 2 of those rest on a SINGLE bit.
```

> **2 of 94 promotions rest on a single bit out of 512.** Small, real, and
> invisible to `loss_b < loss_a`, which cannot tell it from a proposal that wins
> by a thousand. `syz_sandbox_v2_evaluate` takes a margin for this reason. It is
> the smallest of the four fixes and the only one that is a policy choice rather
> than a bug.

---

## 7. The archive, and the index that is not sediment

The fourth ask — *"put the worse one away WITH SPECIFIC COMMENTS"* and *"a build
index of what the comments on older strategy iterations were doing"* — is the one
thing the seed set does not have at all. `syz_witness.h` is that index, built to
close the four failure modes `durable-LOGIC` names, each structurally rather than
by discipline (E7):

```
bound entry appended           yes
UNBOUND entry appended         REFUSED   (refused counter = 1)
chain verifies                 OK   0xBC1BC950 over 1 entries
tamper with entry 0            DETECTED
strip its line binding         DETECTED
lose the head anchor           DETECTED
(restored)                     OK
```

An entry with no script version, or no line number, or a script name that is
padding, **is refused and counted** — the log reports its own blind spot rather
than silently dropping the evidence. The head is a compile-time constant, so a
zeroed log fails verification instead of verifying vacuously.

### The primary affordance, run

E9 runs 512 live frames with a proposal every 16, one in three of which is a
known-good fix. Two independent streams, each with its own engine, its own history
and its own index; every promotion audited against the oracle computed from that
stream's own live state.

```
stream                       promotions    dangerous      index      chain
A: driven by the seed harness          3            2         32         OK
B: driven by the sized pool           2            0         32         OK
proposals offered                    32

  script=seed-v1  v1   line=7 field=5  loss 0 -> 100  KEPT
  comment: "PROMOTED band 1 action 1 better on replay"
```

> **The seed-driven stream promoted 3 scripts and 2 of them were ones the oracle
> had already rejected.** The sized, state-restored stream promoted 2 and neither
> was. Both indexes verify. This is the whole result in one table: the mechanism
> works, and the code as written promotes worse scripts two times in three.

E10 runs the fixed header itself, because it ships and unexercised code is a
liability:

```
pool bytes            746496   (derived, not typed: 128 frames x 5832 stride)
slots with live bytes 128 / 128   (seed harness: 11 / 128)
self-loss             0
null change promoted? no
```

---

## 8. Chatter: the retraction was of the mechanism, and the phenomenon is real

`bb5123b9b86d4a21` names character chatter and prescribes **temporal sub-pixel
anti-aliasing** as the cure. `ASCII-CHARSELECTION.md` retracted a churn figure
because the dither is written once in the constructor. Both can be true, and
`chatter.c` settles it by modelling `Rasterizer.cs:129` exactly:
`fogId = min((int)(pow(z,10)*10 + offset[i,j]), 9)`.

**1024 cells, a monotone z sweep, five dither policies. Only the dither differs.**

| arm | total flips | peak in one frame |
|---|---|---|
| FLAT — `offset = 0` everywhere | 9216 | **1024** |
| FIXED — drawn once *(what the game does)* | 9216 | **7** |
| REDRAW — redrawn every frame *(the retracted experiment)* | 5,698,924 | 565 |
| TEMPORAL — sine phase per cell per frame *(the prescribed cure)* | 643,192 | 86 |
| PHASED — phase walks slowly through a period | 10,766 | 7 |

Three results, in order of how much they change the picture.

> **(a) The retraction was right, and now it has a number.** REDRAW — the
> algorithm the retracted experiment simulated — carries **618× the total flips
> and 81× the peak** of the real one. That is why the figure was an artifact and
> why it was such a dramatic one. The game never does this.

> **(b) A dither is a re-phasing. It cannot change how many times `z^10·10` crosses
> an integer — only how many cells cross together.** FLAT and FIXED agree on the
> total to 0.00% and differ **146× on the peak**. FLAT is the control that scores
> badly: identical information, no spread, the entire wall flips at once. **That is
> the flicker the seed document is describing, and the game is already protected
> against it** — a fixed per-cell dither *is* a static sub-pixel phase field, and
> the cell-to-cell variation is precisely what staggers the crossings.

> **(c) The prescribed cure, applied as written, is 70× worse than what the game
> already does.** Per-frame dither variation on a quantiser this steep is not
> anti-aliasing, it is extra noise. A *correctly phased* version (PHASED) comes out
> roughly neutral — 1.17× the total, the same peak of 7. **The cure is not
> harmful if implemented carefully and it is unnecessary if implemented naively.**

And the actual source of chatter is neither of them. It is the ramp function:

| z window | flips per unit z | ratio to z=0.80 | z⁹ predicts |
|---|---|---|---|
| 0.795 – 0.805 | 14,800 | 1.00× | 1.00× |
| 0.855 – 0.865 | 26,800 | 1.81× | 1.92× |
| 0.915 – 0.925 | 49,800 | 3.36× | 3.52× |
| 0.985 – 0.995 | 92,600 | **6.26×** | **6.81×** |

> **The flip rate scales as `d/dz[z¹⁰] = 10z⁹` — 6.8× from the bottom of the
> informative band to the top, measured within 8% at the far end. Chatter is worst
> where the ramp is most compressed: the far end, the same band
> `ASCII-CHARSELECTION.md` reports as reading `@` for ~79% of cells.**

One qualification on the seed document's own words. It describes chatter as
characters that *"swap back and forth rapidly"*. With a monotone z a cell's glyph
only ever steps one way — there is no back-and-forth to damp. Back-and-forth needs
a non-monotone z, and a first-person camera has one. Measured with `z = 0.90 ±
0.010` at a 60-frame period: **79,155 flips, peak 47 in a frame, 39,600 of them
toward the camera.** That is genuine two-way flicker, produced by the same fixed
dither, and it is the phenomenon the document is right about.

> **The reconciliation: the retraction removed a number that measured the wrong
> algorithm. The phenomenon it was a number about is real, it is caused by the
> `z¹⁰` quantiser rather than by the dither, and the game already contains the
> mitigation the seed document recommends inventing.**

---

## 9. The alphabet is a separate decision, and I was wrong to link them

I expected chatter and the text-priority bias to be one decision: a density ramp
must chatter, so stop using one. **The measurement says otherwise.** `"@&#8x*,:. "`
and `".:-=+*#%@"` are both 10-glyph density ramps, and swapping one for the other
changes no flip count in any arm above. The flip count is a property of the
quantiser, not of the characters.

> **The alphabet decision and the quantiser decision are orthogonal. Fix the
> quantiser for chatter; fix the alphabet for the trap, and they do not interact.**

`ASCII-VISION-LANDSCAPE.md`'s text-priority finding stands on its own and is
untouched by any of this. `@` is still a person, `#` is still a tag, and the VLA
paper's role-palette is still the right answer for identity — for the separate
reason that a depth ramp carries no identity, which `PROBE-RESULTS.md` measured
without a learner. **Two defects, one screen, no shared fix.**

---

## 10. What this does not establish

- **A synthetic scene.** 4 actions, 128 frames, a 24×40 band world with one known
  defect. The absolute counts do not transfer. The *structure* does: pool sizing,
  the Markov precondition, the self-loss floor, and the half-fix inversion.
- **Not the real rasterizer.** `chatter.c` models `Rasterizer.cs:129`. The real
  `AsciiTexture`/texture path and the real camera motion are not in it.
- **The loss function is the seed's**, 100 per wrong bit, unweighted, no
  false-positive/false-negative asymmetry — despite the seed's own comment claiming
  it models "false positives or misses". Worth revisiting; not done here.
- **`pow()` in C, not C#'s `Math.Pow`.** Same shape, not guaranteed bit-identical.
  The z⁹ result is analytic and survives any monotone implementation.
- **The 32-bit layout in E6 is reconstructed, not cross-compiled.** No wasm
  toolchain in this sandbox.
- **I did not run the seed's `test_3d_spreadsheet.c`.** It needs
  `syz_3d_projection.h` and `syz_vector_line.h`, which are not in the seed set.
  E5 and E6 reproduce the sandbox-relevant and hash-relevant parts and say so.
- **The half-fix inversion in §4 has a hypothesis and not a mechanism.** Isolating
  it needs an arm with the pool fixed and the state perturbed deliberately.

## 11. The three-line version

1. **The collapse is real in shape and false in substance for the ask it is claimed
   for.** A static ring + fork + replay + integer loss + commit is one mechanism
   for three of the four asks. The fourth — the unobserved tail — is the one it
   gets backwards, because the 128-frame history is 11 frames wide.
2. **The seed set's verification suite is the eighth green badge**, and its golden
   receipt is architecture-dependent by construction over a field the seed set's own
   memory map documents as architecture-dependent.
3. **The chatter retraction was of the mechanism; the phenomenon is real, it is
   caused by `z¹⁰` and not by the dither, and the game already contains the
   mitigation the seed document recommends inventing.**

---

```
cd research/pixels-build
make            # two binaries, C99 + libm, no dependencies
make run        # results-lab.txt, results-chatter.txt
make verify     # bit-identical across -O0/-O2, and the seed's constants
                # are rejected at compile time
```

`syz_sandbox_seed.h` is the seed set's harness transcribed with **zero edits**. It
is the control, and every defect measured above is a property of that code as
written.
