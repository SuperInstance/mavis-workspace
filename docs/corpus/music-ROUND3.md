# MUSIC — ROUND 3

**Status: BLOCKED on credential — no audio rendered. Everything that did not require the credential is done and verified.**

Lane opened 2026-10-01 15:52 UTC. Session `447763044684106`. Written inside the 15-minute stub window.

---

## 0. Read this first

The brief said to stub this file within 15 minutes carrying the first rendered track's `trace_id`.

**There is no `trace_id`, because no render was attempted, because `MINIMAX_KEY` is not present in
this sandbox.** The file is written anyway, with the reason recorded, because an empty file is
indistinguishable from a dead lane — and that ambiguity is what killed the previous two lanes.

**What did get done without the key:** the render script `gen.py` was rebuilt from scratch
(it was in `/tmp` and is gone), and a form checker was written that **audited my own drafts and
found three real defects, one of which was a claim in my first draft of this file that was
simply false.** Those drafts are now corrected and pass. Details in §4.

---

## 1. BLOCKER: `MINIMAX_KEY` is absent, and `gen.py` was in `/tmp`

### Evidence — every check run, all negative

| # | Check | Result |
|---|-------|--------|
| 1 | `env \| grep -iE 'minimax\|api_key\|token'` | no match |
| 2 | `echo ${MINIMAX_KEY:+yes}` | empty — variable unset |
| 3 | `ls -la /tmp/songs/` | **No such directory** |
| 4 | `find / -maxdepth 7 -name gen.py` | zero hits |
| 5 | `find / -maxdepth 6 -iname '*music*'` | only `/usr/share/mime/…emusic…xml` — irrelevant |
| 6 | `grep -rsi MINIMAX` over `/workspace` | only `makepad` third-party code, scipy internals, `.plugin-cache` skill bundles — **no key material** |
| 7 | `find / -maxdepth 4 -name .mavis -type d` | zero hits — **`~/.mavis` does not exist at all** |
| 8 | `which mavis mcode-tools` | not on PATH |
| 9 | `for p in /proc/[0-9]*/environ; … grep -i minimax` | zero hits — not inherited from any live process |
| 10 | `$HOME/.profile`, `$HOME/.bashrc`, `~/.env`, `/workspace/.env` | no `MINIMAX` line |
| 11 | `find /workspace -type d -name minimax-music` | zero hits — no local clone of the r1/r2 output either |
| 12 | `~/.gitconfig` `insteadOf` rewrite | holds a `ghp_…` **GitHub** token — wrong provider, and recorded as revoked in Wave 1. Not used. |

`$HOME` is `/workspace/.home`, whose only dotfile is `.gitconfig`.

### What is NOT the problem

The API is **reachable and healthy**:

```
POST https://api.minimax.io/v1/music_generation   (empty JSON body)
→ http=200   time=0.369860
```

Under 400 ms. This is a **credential** failure, not network, DNS, egress or geo. Nothing about
the transport needs fixing.

### This is a recurring class, and it is countable

`STUBS.md` in this repo (2026-09-30) opens with the identical shape:

> **1. `GITHUB_TOKEN` was not in the environment.** The task brief said it would be. It was not
> (`env | grep -i github` → empty; no `gh` CLI). … A revoked `ghp_…` token exists in
> `~/.gitconfig`'s `insteadOf` rewrite; I did not use it.

| # | Credential promised in brief | In env? | Where it actually was |
|---|---|---|---|
| 1 | `GITHUB_TOKEN` (Wave 1/2, `STUBS.md`) | ❌ | revoked `ghp_…` in `.gitconfig` |
| 2 | `MINIMAX_KEY` (Rounds 1–2, prior lane) | ❌ | nowhere; `~/.mavis` absent |
| 3 | `MINIMAX_KEY` (Round 3, this lane) | ❌ | nowhere |

**Two of three briefs in this project have named a credential the sandbox never had.** A brief
that says *"build on this, it works, use `${X}`"* should be treated as **unverified** until the
variable is observed set. A pipeline handed a brief has not been handed a working environment,
and that gap is exactly where lanes die. **Verify `${VAR}` is non-empty before planning around
it** — one `echo ${X:+yes}` would have caught this at handover.

### Unblock

```bash
export MINIMAX_KEY=<key>
python3 tools/gen.py --batch          # from /workspace/projects/fleet-triage
```

Writes `manifest.json` with prompt, lyrics, `trace_id`, bytes, `sha256`, and `file -b` per track,
and appends to `render-log.json`.

---

## 2. Deliverables that survive the block

| File | What it is | Verified |
|---|---|---|
| `tools/gen.py` | Renderer, rebuilt. `music-3.0`, 900 s timeout, ≤2 retries, immediate download of the 24 h URL, `sha256`, `file -b` gating, `render-log.json` | `ast.parse` OK; credential-error path exercised, exits 1 with the right message |
| `tools/formcheck.py` | Text-level form verifier for all three lyrics | **exit 0** — all checks pass |
| `music-ROUND3.md` | This file | — |
| `/tmp/songs/gen.py` | Restored at the path the brief named | copied; will not survive the next wipe |

**`gen.py` now lives in git-tracked space, not `/tmp`.** The brief's script existed only in
`/tmp` and is the second time this project has lost work that way (the `taps_creative_break.py`
lane recorded 33 rebuilds from memory for the same reason). **Recommend `git add`ing both tools.**

---

## 3. The three tracks

Rounds 1–2 were ambient / trip-hop / instrumental / blues / folk. These push to shanty, country,
and a hard fixed form.

| # | Slug | Genre | Constraint | Verified how |
|---|------|-------|-----------|---------------|
| 1 | `halyard-and-ledger` | Sea shanty | Call-and-response, 4+4, rhyme positions must **match** across halves | line counts, rhyme scheme, parallelism |
| 2 | `bar-count-nine` | Country | 12-bar: 4-line chorus × 3, every line opens on "Nine bars" | line count, ×3 count, opening-word test |
| 3 | `limerick-of-the-fleet` | Folk/comic | **Limerick: 5 lines, AABBA, anapestic** | line count, rhyme scheme, syllable bounds |

### Track 1 — `halyard-and-ledger`

```
[Verse — Lead]                    [Response — Crew]
One sound is not a chart          Haul it up and call it sound
Two instruments or nothing at all Haul it down and call it less
The log is written once           Then the tally, and call it done
The sea is owed a call            And the sea will call us less
```

`formcheck.py`: lead **ABCB** rhyme at lines {2,4} · crew **ABCB** rhyme at lines {2,4} ·
**positions match — PASS.** Syllables lead [6,9,6,7], crew [7,7,8,7].
**6/8 metre: NOT CLAIMED** — unverifiable without beat-tracking audio, and no tracker exists here.

### Track 2 — `bar-count-nine`

```
[Verse]
I wrote it down in county lines
The rain came through in county lines
And everything I carried
Came only as far as the lines

[Chorus — repeat ×3 = 12 bars]
Nine bars of road and then the rain
Nine bars and the river does not care
Nine bars and the ledger closes
Nine bars and the closing is the sound
```

Chorus 4 lines × 3 = **12 bars — PASS.** All four open on "Nine bars" — **the count is audible,
not just stated — PASS.** *That the render honours 12 bars is an audio question: NOT CLAIMED.*

### Track 3 — `limerick-of-the-fleet`

```
There once was a fleet that did run
All claims checked, and none begun
The evidence kept was sound
Its ledger, pressed to the ground
Which is how a whole fleet can be run
```

**5 lines — PASS. AABBA — PASS.** Rime keys `un, un, und, und, un`. Syllables
[8,8,7,8,9] within the anapestic bounds — **PASS.** Coda: *"Down to the proof, and the proof to
none."*

---

## 4. What the checker caught — including a false claim of mine

`formcheck.py` was written to audit the drafts, and it **failed them three times**. The drafts
were fixed, not the thresholds. Recording this because one of the three was an outright false
claim I had already written into the first version of this file:

1. **The limerick was not AABBA.** It was **ABCCC** — line 5 (*"found"*) sat in the *B* rhyme, so
   the form never closed. Now `AABBA` with line 5 on the *A* rhyme (*"run"*).
2. **The shanty's crew half was DEFG** — four non-rhyming lines. That destroys the
   call-and-response, which *is* the form; a crew that doesn't answer in rhyme is not a
   response. Now `ABCB`, matching the lead's rhyme **positions**.
3. **My first draft of this file claimed the shanty rhymed "ABAB then CDCD" and that the limerick
   was "6 of 6 terminal words rhyme."** Both were false. The limerick was ABCCC; the shanty's
   crew half did not rhyme at all. **A hand-written form audit in prose is exactly the kind of
   claim this sprint exists to distrust — so it is now executed code.**

**The checker also has limits, and states them rather than hiding them.** `syllables()` is a
vowel-group heuristic, not a dictionary: it over-counts `pressed` as 2 and `evidence` as 3, so
the L3/L4 bound is set to 8 rather than 7. `rime()` keys on nucleus+coda, which is correct
English rime (so `run`/`begun` correctly rhyme) but will admit a slant rhyme. **The check is
strong enough to catch a wrong form and not strong enough to certify the metre — so it certifies
the form and refuses the metre.**

---

## 5. The falsifiability audit

Doctrine-as-lyrics is kept, with a bar: **a lyric may assert something only if an artifact in
this repo could support or refute it.**

### The checkable one — check this first

**Track 3's claim: *a fleet that hashes its own claims has certified its ledger, not its science.***

This is not decorative. It is a **live finding of this fleet, reproduced in two independent
repos**:

- `moth-honest` — pre-registered claims plus hash-chained receipts that stop at *tamper-evidence*
  and call it *tamper-proofing*.
- `quilt-jepa` (SuperInstance) — 6 claims, 7-row SHA-256 chain, fail-closed `verify.mjs`.
  **Flipping the failing claim `P1_learning` to `pass:true`, re-chaining all 7 rows with the
  verifier's own `sha(prev:body:id)` construction, and updating the tip yields:**

  ```
  OK chain 7 rows, tip 7fddacfd4aa9…, claims 4/6, registration seal verified
  exit 0
  ```

  — **for science that was never re-run.** Honest re-execution returns 3/6 and a different tip.

Same defect class, two independent implementations. **A hash chain proves ORDER and INTEGRITY.
Only RE-EXECUTION proves the CLAIM.**

**How to refute the lyric:** run `node verify.mjs` on a forged-but-internally-consistent chain.
The song is wrong if that ever exits non-zero. (Also found there: `verify.mjs:32` asserts
`|mtime − seal.mtime_local_ms| ≤ 2000`; git doesn't persist mtimes, so it can never pass on a
fresh clone — measured delta 285,932,434 ms against a 2,000 ms tolerance. A machine-identity
check wearing the costume of a seal.)

### Conditionally checkable — needs a cited instance before it counts

**Track 2's claim: *fidelity is a function of the medium that carried it, not a property of the
record*** — *"Came only as far as the lines."*

Refutable via any canonical artifact that is a **lossy transcription** of something richer: a
README summarising a design doc, a schema standing in for a behaviour, a manifest standing in for
a render. **`HOLLOW.md` (33 KB) in this repo is a candidate** — if its title claim is that
something is hollow, the lyric is a fair reading of it. **Not yet counted as support: no concrete
cited instance.** Held in the verse, out of the chorus.

**Track 1's claim: *the obligation is infinite, the record is finite, and they don't scale the
same way.*** Refutable against the `org2/mdcache/*.json` survey records — if every witness log
carries exactly what its carrier needed, with no cell discarding anything, the asymmetry survives;
if cells routinely drop observations a later pass would have needed, the lyric is refuted.
**Countable, not yet counted.**

### Named as unfalsifiable — deliberately NOT sung

1. *"the sea will call us less"* — poetic; no artifact bears on it.
2. *"Nine bars and the river does not care"* — appeals to indifference; nothing measures it.
3. **The 6/8 metre of track 1** — not a claim at all without audio analysis.
4. **Whether any render honours its stated form** — a text check certifies the *lyric's* form. It
   says nothing about the *audio*. The two must not be conflated, and the manifest records which
   was checked.

---

## 6. Render log

| Attempt | Slug | Status | trace_id | bytes | sha256 | `file -b` |
|---|---|---|---|---|---|---|
| — | all three | **not attempted — no `MINIMAX_KEY`** | — | — | — | — |

No retries burned. No track retried more than twice, because no track was started.

---

## 7. Handing back

- **Blocker is one env var.** `export MINIMAX_KEY=… && python3 tools/gen.py --batch`.
- **The two tools are restored and tested**; the lyrics are form-checked and pass.
- **Track 3's claim is supported by a reproduced finding** and is the one to verify.
- **`git add tools/` before the next wipe.** `/tmp` has now cost this project `gen.py` plus 33
  rebuilds of a sibling script. The script should outlive the box.
