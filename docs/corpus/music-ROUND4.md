# MUSIC — ROUND 4

**Rendered 0 tracks. `trace_id`: none. The credential is absent — for the third time on
`MINIMAX_KEY`, and the first time on `CLOUDFLARE_API_TOKEN`.**

Lane opened 2026-10-01 20:19 UTC. Session `447827919847642`. Stub written inside the 10-minute
window carrying an honest status instead of a `trace_id`.

**What the lane did produce, and it is the part that did not need a key:** three lyrics whose
forms are **counted, not asserted** (`form-report-r4.txt`, exit 0), and **one claim taken to an
instrument and partly refuted** (§4). The refutation is the interesting result.

---

## 1. BLOCKER — both credentials absent. Verified, not assumed.

```
$ echo ${MINIMAX_KEY:+yes}          -> (empty)
$ echo ${CLOUDFLARE_API_TOKEN:+yes}  -> (empty)
```

Live probes, both actually run:

| endpoint | result | reading |
|---|---|---|
| `POST api.minimax.io/v1/music_generation` | `http=200` `{"base_resp":{"status_code":1004,"status_msg":"login fail: Please carry the API secret key in the 'Authorization' field"}}` | transport healthy, **auth** absent |
| `POST api.cloudflare.com/client/v4/accounts/…/ai/run/@cf/deepgram/aura-2-en` | `http=401` `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}` | same |

`env` has no `MINIMAX*` / `CLOUDFLARE*` / `CF_*` variable. `/run/secrets` does not exist. No
`.env` anywhere. 23 workspace files *mention* `MINIMAX_KEY`; all are code or prose, none carry a
value. `~/.gitconfig`'s `insteadOf` holds a revoked `ghp_…` **GitHub** token — wrong provider,
not used.

### The fourth brief to name a credential the sandbox never had

| # | brief | present? | claimed as |
|---|---|---|---|
| 1 | `GITHUB_TOKEN` (Wave 1/2, `STUBS.md`) | ❌ | in the environment |
| 2 | `MINIMAX_KEY` (Rounds 1–2) | ❌ | "verified working" |
| 3 | `MINIMAX_KEY` (Round 3) | ❌ | "verified working" |
| 4 | `MINIMAX_KEY` **+** `CLOUDFLARE_API_TOKEN` (Round 4) | ❌ ❌ | **"Verified working — do not rediscover"** |

Round 4 raised the claim from *used previously* to **verified working** and added a second
credential. Both absent. **A brief that asserts verification is not a receipt.** One command at
handover settles it, and that is the first thing to do, not the ninth minute of the lane.

**Also blocked, contrary to the brief's "the voice lane is now open":** Workers AI needs
`CLOUDFLARE_API_TOKEN`. The voice lane is shut by the *same* gap. The four existing spoken songs
remain at `/workspace/cftts/songs/`; nothing new was spoken.

**Unblock:** `export MINIMAX_KEY=… CLOUDFLARE_API_TOKEN=…` then `python3 tools/gen-r4.py --batch`.
Nothing downstream needs an edit.

---

## 2. The three tracks

| # | slug | shelf | constraint | counted by |
|---|---|---|---|---|
| 1 | `halyard-and-ledger` | `01-shanty` | call-and-response, AABB per half, house style | response-line count + **rhyme verified phonetically** |
| 2 | `nine-bars-to-town` | `02-country` | 12-bar: chorus ×3, every line opens "Nine bars" | section count, line count, opening-word test |
| 3 | `one-hundredth-of-the-value` | standalone | **exactly 8 syllables per line, no exceptions** | per-line syllable count; **miss list reported** |

House style matched from `slow-lander/songs/01-shanty/lyrics.md`: `[VERSE N]`, `[CHORUS]`,
`[OUTRO]`, all-caps tags, lead-then-crew.

### The measurement, as run — `form-report-r4.txt`, **exit 0**

```
T1  lead lines 6 | RESPONSE (crew) lines 7 | crew sections 4 | rhyme misses 0   -> PASS
      all/call  sound/ground  down/found  show/know  claim/game  chart/starts
T2  chorus sections 3 | chorus lines 12 | [4,4,4] | opening-word misses 0     -> PASS
T3  lines 16 | total syllables 128 | mean 8.000 | lines not at 8: 0           -> PASS
```

### The part that matters: the checker found four real defects, in my own draft

| defect | verdict on it |
|---|---|
| `chart` / `call` did **not** rhyme (`/ɑːrt/` vs `/kɔːl/`) | **real lyric defect** — rewrote line 2 to `…or it never even starts` |
| T2 had **2** choruses, not 3 | **real lyric defect** — added a third |
| T3 outro line was **7** syllables | **real lyric defect** — `Now drop the colour, keep the game` |
| `down`/`found` and `claim`/`game` flagged as non-rhyming | **checker defect, not a lyric defect** — they rhyme. The phonetics did not handle vowel digraphs (`ow`/`ou`, `ai`) or magic E, so it reported true rhymes as misses |

That last one is the dangerous kind of error. A checker that cries wolf on real rhymes trains you
to ignore it, and then it is decoration. Fixing it was more work than fixing the lyrics, and it
was the more valuable half: **the instrument is now trustworthy enough to convict my own draft**,
which is the only reason its PASS is worth anything.

Had I asserted the forms instead of counting them, all four would have shipped. That is the round
in one line.

---

## 3. Lyrics

**T1 — `halyard-and-ledger`** (sea shanty, call-and-response)

```
[VERSE 1 — LEAD]
One sound is not a chart, and one sound is not a chart at all,
Two instruments or nothing, that's the whole of what we call.
[VERSE 1 — CREW]
So haul the single reading up, let the taut wire be the sound,
And when the second joins the line, both ends are on the ground.

[VERSE 2 — LEAD]
What survives is bounded by what the looking carried down,
Nothing downstream recovers what the looking never found.
[VERSE 2 — CREW]
So hold the ledger open, boys, and let the columns show,
The cell that kept the colour keeps the row that we must know.

[CHORUS — LEAD]
Hey, the trace is not the claim, the trace is not the claim!
Hey, the seal is on the file, it never touched the game!
[CHORUS — CREW]
One sound is not a chart, boys — one sound is not a chart,
Two instruments or nothing, or it never even starts.

[OUTRO — CREW]
Haul it up and call it sound. Haul it down and call it ground.
```

**T2 — `nine-bars-to-town`** (country, 12-bar) — 3 verses + 3 choruses + outro; every chorus line
opens `Nine bars`. Full text in `tools/gen-r4.py`.

**T3 — `one-hundredth-of-the-value`** (hard form, **exactly 8 syllables per line**)

```
[VERSE 1]
The colour is what you can see
The value is what you can read
Just one part in ninety is gone
The colour is one bit, so cheap

[VERSE 2]
A hash is a perfect disguise
Sixty-four bits of even soup
The hash keeps no shape of the board
Sixty-four bits of noise, that's all

[VERSE 3]
Nothing made later brings it back
Nowhere down the line can it mend
It kept the shape, it lost the paint
Now drop the colour, keep the game

[OUTRO]
One part in ninety for the eye
The colour is what you can see
The value is what you can read
Now drop the colour, keep the game
```

---

## 4. THE CLAIM — and where the measurement refutes it

The orchestrator's finding, to be sung and then checked:

> discarding colour entirely costs **1.1%** of exact minimax value; a **64-bit irreversible
> hash costs everything**.

I built the instrument and ran it: `tools/claim-c4.py`, full enumeration of every reachable
position on a small board, exact negamax, solver gated on known-answer checks. Logs:
`music-r4/claim-c4-5x3.log`, `music-r4/claim-c4-4x4.log`. **Two independent boards.**

### Solver gate first — a control that cannot fail is not a control

```
[ok] 3-in-centre, side 0 to move -> +1   (got +1)
[ok] 3-in-centre, side 1 to move -> -1   (got -1)
[ok] empty board solved            (got -1)
```

### ARM A — colour ablation at rate p, retention of exact value

| p | 5×3 (171,242 pos.) | 4×4 (187,927 pos.) |
|---|---|---|
| 0.00 | 100.000% | 100.000% |
| 0.01 – 0.05 | **100.000%** | **100.000%** |
| 0.10 | 94.051% | 93.223% |
| 0.25 | 78.344% | 79.025% |
| 0.50 | 60.208% | 63.960% |
| **1.00** | **51.293%** | **57.263%** |

### ARM B — FNV-1a 64 hash, same memorisation decoder

| | 5×3 | 4×4 |
|---|---|---|
| positions hashed | 171,242 | 187,927 |
| **64-bit collisions** | **0** | **0** |
| collision rate | 0.000000 | 0.000000 |
| decoder retention | 100.000% | 100.000% |

### What this actually says — two of the three parts move

1. **Colour loss is *graceful*, not 1.1%.** It is flat at **exactly 0.000% up to p = 0.05** on both
   boards, then bends: 5.9% at p = 0.10, 21.7% at p = 0.25, **48.7% at p = 1.00**. So the real
   finding is stronger and stranger than the lyric: **throw away *every* colour, impute all of it
   as the side to move, and you still keep ~51–57% of the exact value.** The observation is
   almost information-free and the value survives half of it. **I could not reproduce 1.1%.** The
   nearest measurements are 0.000% and 5.949%. Whatever produced 1.1% used a different board,
   decoder, or ablation — and the lyric's number is not what this instrument says.

2. **The hash loses *nothing*, and the lyric is right for the wrong reason.** FNV-1a 64 is
   **injective over 359,169 positions across two boards, zero collisions.** A 64-bit hash of a
   ~30-bit board is a *relabelling*, not a destruction. A decoder keyed on the hash recovers
   **100%**. "The hash costs everything" is true about **compute, not bits**: `map(hash → value)`
   costs exactly what `map(board → value)` costs, because the hash leaves no local structure to
   generalise from. The lyric line stands; **its stated mechanism does not.**

3. **The boundary is not entropy.** This is the finding worth keeping, and it is the project's own
   doctrine with a number on it. Colour is *one bit per cell* and costs a fraction. A 64-bit hash
   is a *lot* of bits and costs nothing in the memorised sense. **Bit count is not the currency;
   structure is.** *"What survives is bounded by what the observation carried"* is true, and the
   operative word is **carried** — not *encoded*.

**The line that is the claim, in T3 verse 1: `Just one part in ninety is gone`** — that is the
number to go and refute, and `claim-c4.py` is the thing that would.

---

## 5. Deliverables

| File | What | State |
|---|---|---|
| `music-ROUND4.md` | this file | ✅ |
| `form-report-r4.txt` | the form measurement, all three tracks | ✅ **exit 0** |
| `tools/formcheck-r4.py` | form verifier — response count, phonetic rhyme, 12-bar, syllables | ✅ runs |
| `tools/sylcount.py` | documented heuristic syllable counter | ✅ |
| `tools/claim-c4.py` | the ablation, KAT-gated, board-size selectable | ✅ runs, 2 boards |
| `music-r4/claim-c4-5x3.log` | 171,242 positions | ✅ |
| `music-r4/claim-c4-4x4.log` | 187,927 positions | ✅ |
| `tools/gen-r4.py` | renderer, `music-3.0`, 900 s timeout, ≤2 retries, immediate download, per-track save, `manifest.json` | ✅ `ast.parse`; credential path exercised, exits 1 with the right message |

**No audio. No `manifest.json`. No `trace_id`. No GitHub push.** Nothing was pushed anywhere.

The tools are in git-tracked space, not `/tmp` — this project has lost the music script to `/tmp`
twice, and a sibling lane has rebuilt the same script from memory **33 times**. **The script is
the artifact. Do not let it live in `/tmp`.** `git add tools/gen-r4.py tools/formcheck-r4.py
tools/claim-c4.py tools/sylcount.py` is the one command that makes that true.

---

## 6. Honest scorecard

- **Tracks rendered: 0/3.** Blocked on a credential, not on a bug, not on the API.
- **Forms counted: 3/3**, and counting them found **4 defects** that asserting them would have shipped.
- **Claims audited: 1**, with a KAT-gated instrument, run on two independent boards.
  **Result: 1 of 3 sub-claims moved.** 1.1% not reproduced; hash-collision sub-claim refuted;
  the structure-over-entropy reading strengthened and kept.
- **TTS: 0 new.** Blocked by the same absent `CLOUDFLARE_API_TOKEN`.
- **Follow-ups worth someone's time:** (a) export the key, or the lane is dead on arrival;
  (b) find what produced 1.1% — board size and decoder are the two free parameters, and this
  instrument can sweep both; (c) sweep p finer between 0.05 and 0.10, where the entire curve
  happens.
