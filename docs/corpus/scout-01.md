# SCOUT-01 — `tensor-midi`: the codec is tested, the writer is not

**Target:** `SuperInstance/tensor-midi` (600 KB, 172 files, never examined).
**Clone:** `projects/fleet-triage/repos/tensor-midi` @ `288ce64`. Read-only; repo left pristine.
**Status:** SEAM NAMED. One line. Two characters.

---

## The seam

`capture.js:472` and `capture.js:406,415` write byte 0 of an SWMIDI event as a **raw
MIDI status byte**; `src/swmidi.js:71` writes the same byte as a **4-bit event-type
enum**. Both call it "the SWMIDI-8 wire format". They are two different formats, and
the file in the repo is written by one and cannot be read by the other.

```
capture.js:406     0x90 | (track.channel & 0x0F)      <- NoteOn  => type nibble 9
capture.js:415     0x80 | (track.channel & 0x0F)      <- NoteOff => type nibble 8
src/swmidi.js:71   ((event.eventType & 0x0F) << 4) | (event.channel & 0x0F)
                                                      NoteOn=0, NoteOff=1
src/swmidi.js:99   if (eventType > 4) throw new Error(`Invalid event type: ${eventType}`)
```

The comment at `capture.js:470-471` states the spec correctly and the code below it
violates it:

```js
// status byte: type nibble in high 4, channel in low 4
// For MIDI compat: status is already the full status byte
buf[0] = status & 0xFF;          // <- and it isn't; the high nibble is 0x9/0x8
```

---

## Why it is silent

**The repo ships the artifact and a test suite that cannot see it.**

| | |
|---|---|
| `node --test tests/*.test.js game-engine/*.test.js` | **515 tests, 515 pass, 0 fail** |
| `output/relay-bridge-fix.swmidi` — 8-byte records | **32** |
| …decoded by the repo's own decoder, `src/swmidi.js` | **0** — throws `Invalid event type: 9` |
| …decoded by the repo's own Python port, `bindings/tensor_midi.py` | **0** — returns `None` ×32 |
| `.swmidi` written by the *other* writer, `src/swmidi.js` | 32/32 decode fine |

The suite is green because it round-trips `src/swmidi.js` against **itself**
(16 assertions in `tests/swmidi.test.js`, all `encodeEvent`→`decodeEvent` on the same
module). The code that actually produces the committed bytes, root `capture.js`, is
**not the module under test** — `tests/capture.test.js` imports `../src/capture.js`,
a different, 200-line file that has no `toSWMIDI` and no `toMIDI` at all.

```
$ grep '"main"' package.json          →  "main": "capture.js"      <- the untested one
$ grep "toSWMIDI" src/capture.js      →  0
server.js:45, demo.js:7               →  require('./capture.js')   <- the untested one
```

Two files named `capture.js`, one at the root and one in `src/`. 599 lines of tests
buy 100% coverage of the one nobody runs. That is not a coverage gap, it is a
**name collision wearing a coverage report as a costume**.

---

## Proof the committed file is this code's output, not a stale artifact

I re-ran `toSWMIDI()`'s algorithm over `output/relay-bridge-fix.tensor.json` and
compared against the committed bytes:

```
recomputed bytes: 256   committed bytes: 256   BYTE-IDENTICAL: true
```

## The fix is two characters, and it is decisive

On a scratch copy (`/tmp/scout01/fix`, repo untouched), `0x90`→`(0 << 4)` and
`0x80`→`(1 << 4)`, regenerated via `node demo.js`:

```
original:  FAILS -> Invalid event type: 9        0 of 32 events
2-char fix: decoded 32 of 32 events
```

Every other language port was already correct. The JS writer is the only defect.

---

## Recipe for another lane

`scout-01-seam.sh` is checked in beside this file. Three commands:

```bash
# 1. the number CI publishes
cd repos/tensor-midi && node --test tests/*.test.js game-engine/*.test.js | grep -E '^# (tests|pass|fail)'
#    → 515 / 515 / 0

# 2. read the repo's own artifact with the repo's own decoder
node --input-type=module -e "
import {decodeStream} from './src/swmidi.js'; import fs from 'fs';
try { console.log(decodeStream(new Uint8Array(fs.readFileSync('output/relay-bridge-fix.swmidi'))).length,'events'); }
catch(e){ console.log('FAILS:', e.message); }"
#    → FAILS: Invalid event type: 9

# 3. the two writers, side by side
grep -n "buf\[0\] = status" capture.js
grep -n "view.setUint8(0," src/swmidi.js
```

**Negative control (run this first, or the recipe is worthless):** point step 2 at a
file written by the *other* writer and it must pass. It does — `encodeStream` output
from `src/swmidi.js` decodes 32/32. The seam is real, not a decoder that fails on
everything.

### Generic form — this is the reusable detector

> **In any repo with two independent implementations of one wire format, each
> implementation's tests will round-trip that implementation against itself and
> report perfect coverage of a format that does not exist.**

The detector is one line of grep. Find every writer of the format, find every reader,
and check whether **any single test crosses from one to the other**:

```bash
grep -rln "encode" --include=*.js . | xargs grep -ln "decode"    # writers that also read
# then: for each file that WRITES, is its output ever fed to a file that READS?
```

`tensor-midi` has four ports (Python/C/Zig/JS) of a format whose entire purpose is
interchange with `slackwater-rust`, and **zero cross-port tests**. The Rust original
would reject these bytes exactly as JS does. The 515 green tests are a comment on the
internal consistency of each port and evidence of nothing about the wire.

---

## What I learned that changes what someone else should do

1. **515 passing tests tells you how many assertions ran. It does not tell you which
   file the user touched.** This repo's suite is 599 lines of thorough work aimed at
   `src/capture.js` while `package.json` points `main` at a *different* `capture.js`.
   Before trusting any green suite: `grep '"main"' package.json`, then read the import
   line in the largest test file. If they are different files, the suite is theatre.

2. **The artifact is the cheapest oracle in the repo, and nobody reads it.**
   `output/*.swmidi` has been committed, byte-stable, since before CI existed. One
   `decodeStream` over a checked-in artifact would have caught this. Generalise:
   *if a repo commits generated output, the decode path over that output is a free,
   permanent, zero-maintenance test.* Four repos in this fleet commit `.mid` files
   nobody has ever parsed.

3. **A fail-silent reader hides a fail-loud writer.** The Python port returns `None`
   on an invalid type nibble; JS throws. My first differential run printed
   *"python decoded 32"* and I nearly published it — I had counted list length, not
   non-`None` entries. The reader that fails silently is what makes the writer's bug
   survive contact with a second language. **Any decoder that returns a sentinel
   instead of raising is a defect generator**: it converts a loud format violation
   into a quiet wrong answer, and the wrong answer survives the port.

4. **A spec comment directly above a violated line is a receipt, not evidence.** The
   comment at `capture.js:470` describes the wire format correctly, in the right words,
   one line above code that does the opposite. Read the comment as the *intent* and the
   next line as the *implementation* and diff them. That is where the seam was, in
   nine words.

5. **Still not examined:** the rest of `tensor-midi` (analyzer, device-context, the
   12-pulse engine, the `POLYFORMALISM.md` doctrine). This lane found one seam and
   stopped, per the kill criterion. There is a second seam in the same neighbourhood:
   `src/swmidi.js:105-109` composes the tick with `|` and never applies the `>>> 0`
   that the comment on `src/swmidi.js:110` claims is there — ticks ≥ 2³¹ decode
   **negative** (0xFFFFFFFF → −1). The round-trip is byte-exact so the suite cannot
   see it, and at 96 PPQ it needs 2.7 million years of music to bite. **Filed as
   UNVERIFIED-IN-PRACTICE, not as a defect of consequence.** Named so the next lane
   does not spend an hour re-deriving it.
