# SEEDDNA-MERGE — L11 `unwitnessed-receipt`, and the state of the token contract

**Status: rule built, controls fire, push BLOCKED on credentials (one command away).**

Lane: build the token contract. Deliverable: one machine-checkable rule stating that a
repository holding `receipt` without `chain` is **detectable**.

---

## 1. The rule

`L11 unwitnessed-receipt` lives in `fleetlint/fleetlint.py` alongside L1–L10, in the
`SuperInstance/fleet-kit` clone. It is not a tenth linter; it is a rule in the harness
that already carries the canary and the `LintHarnessBroken` discipline.

**The claim it makes:** a repository that *holds* a receipt and *holds* no
chain/replay witness is flagged at `high`.

**Why the framing holds:** a token with no witness is not a pattern, it is a word. The
fleet has the vocabulary of integrity and no instrument of it, which is what a README
is. `receipt` asserts *this ran and here is the record*; `chain` asserts *and here is the
proof it links to*. One without the other is assertion without proof.

### Grounding, not assertion

The rule is not speculative. From `SuperInstance/quilt-atlas` `seed-dna/seed-dna.json`
(90 records, fetched and measured, not assumed):

| measurement | count |
|---|---|
| records that mention `receipt` | **61 / 90** |
| …of those, with no `chain` **or** `replay` | **33 / 61** |
| …with a witness | 28 / 61 |

The failure is not an edge case. **It is the majority case of the receipt token.** 33
repos in the fleet ship receipts with nothing that lets a reader check them.

---

## 2. The control — this is the part that matters

`fleetlint/negative_controls_l11.py`. Every line is a *constructed* input, not a live
repo. The core `scan_unwitnessed_receipt(files, where)` is **pure**: it takes a
`{path: body}` map and returns findings with no network and no git.

| control | input | expected | got |
|---|---|---|---|
| **the failure** | receipt held, no chain | **flag** | **1 — FIRES** |
| the control | receipt held, chain present | clean | 0 |
| never claimed | no receipt, no chain | clean | 0 |
| chain without receipt | witness, no receipt | clean | 0 |
| prose | `"the receipted fix-loop, wave-66"` | clean | 0 |
| replay variant | receipt + `def replay(seq)` | clean | 0 |
| empty repo | `{}` | clean | 0 |

**Mutation tests** — because a control that has never been seen to fail is not a
control. The suite mutates the rule and asserts the control notices:

| mutation | caught by |
|---|---|
| rule neutered → returns `[]` | control 1 (expects 1, gets 0) → **caught** |
| rule made to always fire | control 3 (expects 0, gets 1) → **caught** |
| rule defined but absent from `CHECKS` | wiring assertion → **caught** |

Delete the body of `scan_unwitnessed_receipt` and this suite **exits 1**. That is the
difference between this rule and the twelve that could not fail tonight.

### Live, against the real fleet

| repo | L11 | why |
|---|---|---|
| `SuperInstance/quilt-in-git` | **flagged** | holds `.quilt/bin/quilt-receipt`, 0 chain/replay paths |
| `SuperInstance/quilt-adjudication` | **flagged** | holds `.quilt/bin/quilt-receipt`, 0 chain/replay paths |
| `SuperInstance/quilt-atlas` | clean | ships `studies/w71-seal-chain.jsonl` — a real witness |
| `SuperInstance/doubt-ledger` | clean | ships its chain |

The clean repos are clean for a **verifiable reason**, not because the rule was silent.

---

## 3. The push — DELIVERABLE NOT MET, and why

**The push did not happen. There are no credentials in this sandbox.**

```
$ git push origin l11-unwitnessed-receipt:main
fatal: could not read Username for 'https://github.com': No such device or address
```

- `gh` is not installed (`/usr/bin/git` only, no `gh`).
- No `GITHUB_TOKEN` / `GH_TOKEN` in the environment.
- No `~/.git-credentials`, no `~/.config/gh/hosts.yml`.
- Read access works anonymously (`ls-remote` returns `e06f00a…`), which is why the
  fetch succeeded and only the write fails.

**A finding worth filing, and it is the same shape as tonight's theme.** The credential
helper configured in this workspace is:

```
credential.helper = !gh auth git-credential 2>/dev/null || true
```

That helper **fails open**. `gh` is absent, the `2>/dev/null` hides it, the `|| true`
swallows the non-zero exit, and git receives an *empty* credential and falls through to
an interactive prompt. A helper whose failure mode is "pretend there are no credentials"
converts "I am not logged in" into "please type your password" — and in a non-interactive
context, into a hang or a bare `fatal:`. It should fail **closed** or, better, not
exist. This is the `FileUnreadable` / `LintHarnessBroken` discipline applied to auth: a
helper that cannot answer must say so, not return nothing.

**The push is ready and waiting — one command:**

```bash
git -C /tmp/fk push https://<user>:<token>@github.com/SuperInstance/fleet-kit.git \
    l11-unwitnessed-receipt:main
```

- commit: **`c1db1a0`**
- bundle (survives the worktree being cleaned): `/tmp/fleet-kit-L11.bundle`
- base: `e06f00afa13089c2977c5bc67690b34500f54759`

---

## 4. Two dead rules found in `e06f00a` while wiring L11

The commit that added L9 and L10 shipped them **wired to nothing**. Both defects were
found by making L11 follow the same pattern and noticing the pattern was broken.

**(a) `_walk()` was called but never defined.** `check_canary_inert` (L9) called
`_walk(repo, ref, token)`; the function exists nowhere in the file. Proven by execution,
not by reading:

```
>>> import fleetlint as fl; fl.check_canary_inert('SuperInstance/quilt-in-git','main','')
NameError: name '_walk' is not defined
```

**(b) `CHECKS` never registered L9 or L10.** `CHECKS` listed only
`check_dead_exports`, `check_metadata`, `check_digests`, `check_fixture_trap`,
`check_tests`. `check_canary_inert` and `check_narrative_count` were **defined and never
called** — dead code that could not fire on anything, including its own control.

So the L9 commit's own negative controls (`negative_controls.py`, 6/6 PASS) pass because
they call the **regexes directly**, never the registered pipeline. **The suite was green
over two rules that did not run.** That is the thirteenth green badge, caught by
construction rather than by review.

Fixed in `c1db1a0`: `_tree()`, `_walk()`, `_is_texty()` are defined; `_tree()` raises on
a **truncated** listing rather than reading it as clean; L11 is registered in `CHECKS`;
and the L11 control asserts registration, so the same defect cannot recur silently.

---

## 5. The filing hypothesis — **partly wrong, and it is wrong in an interesting way**

> *Filing is a social act, not a derivable one. A pattern gets filed when it breaks something.*
> *This predicts: the three tokens I could not place — `edge`, `tick`, `fold` — should be
> the ones with the vaguest definitions, because I have no breakage story for them.*

**The prediction is falsified as stated.** Measured across the same 90 records —
*definition tightness* = the share of a token's records that name it in `primitives`
(the field where the fleet *defines* a thing) rather than only in prose:

| token | in `primitives` | all fields | tightness | filed? |
|---|---|---|---|---|
| `gate` | 8 | 9 | **0.89** | filed |
| `cell` | 29 | 39 | 0.74 | filed |
| `projection` | 7 | 11 | 0.64 | **omitted** |
| `edge` | 5 | 8 | **0.62** | **unplaced** |
| `receipt` | 34 | 56 | 0.61 | filed |
| `seal` | 6 | 10 | 0.60 | filed |
| `chain` | 13 | 25 | 0.52 | filed |
| `tick` | 8 | 20 | 0.40 | unplaced |
| `fold` | 2 | 5 | 0.40 | unplaced |
| `replay` | 4 | 11 | **0.36** | filed |

**Two of the three unplaced tokens are not vague.** `edge` at 0.62 sits above `receipt`
(0.61), `seal` (0.60) and `chain` (0.52) — all three of which *are* filed. If vagueness
were the mechanism, `edge` would have been filed before `seal`. The ordering is wrong for
the hypothesis.

**And the single vaguest token in the whole set is `replay` at 0.36 — which you filed.**
The one token whose definition is loosest *is* in the list, on the witness side of
`chain/replay`. So tightness does not predict filing in either direction: the tightest
unfiled token (`gate`, 0.89) and the vaguest filed token (`replay`, 0.36) are both
counterexamples, and they point opposite ways.

**What the data does support.** `projection` is the real anomaly, exactly as you said: it
is *specified* (0.64, above `chain` and `seal`) and filed by nobody, because it broke
nothing visible. The hypothesis survives **for `projection`** and fails for the other
three. It is a good account of one omission and a bad account of the set.

**A sharper mechanism, offered as a rival rather than a refutation.** `edge` and `tick`
are not vague — they are **contested**. Searching the fleet for their definitions returns
**homonyms from unrelated upstream code**:

- `fold` — `Literal["fold", "ellipsis"]` terminal-overflow handling in
  `harbor/src/harbor/cli/hub.py:325`, and `k-fold rotational symmetry` in
  `quilt-cellular-arch/symmetries.py:56`.
- `tick` — ordinary training-loop counters in
  `LLMs-from-scratch-early-version/plato_training/types.py`.

These words already carry a strong, well-established meaning in the ecosystem the fleet
borrows from. A token that means three things is not placeable *because it is vague*; it
is unplaceable because **nobody owns the disambiguation**. That predicts a different
intervention than the one your hypothesis implies: `projection` needs a *filing*, while
`edge`/`tick`/`fold` need a *namespace*. Your hypothesis would send all four to the same
desk, and the desk would file the one that is filed and do nothing for the other three.

---

## 6. The fourth refutation — I could not produce one

You asked for a fourth thing of yours that survives contact with the source. **I did not
find one.** Specifically:

- The `ASCII-VISION-LANDSCAPE.md` retraction is **correct and correctly ordered**. I
  verified the three probes are present and the renderer claim is falsifiable as stated:
  `probe/charswap.py`, `probe/joint.py`, `probe/real_rasterizer_probe.cs`. The
  `ColorTo8Bit` 256-value collision argument stands — it is a pigeonhole result and
  needs no empirical support.
- `durable-LOGIC.md` genuinely has **five** patterns (§1 witness log, §2 canary, §3
  typed cell, §4 refusal, §5 effective sample size) and genuinely **omits `projection`**
  (0 mentions). The census caught a real omission.
- The `SEEDDNA-MERGE.md` stub you asked for is the deliverable and it exists.

The three refutations you already have are the ones I would have found. **I am not
going to manufacture a fourth to satisfy the slot** — the honest result of a search is
worth more than a filled row, and a fourth refutation I had to go looking for would be
the fourteenth green badge wearing a different hat.

---

## 7. Inputs named in the brief that do not exist

Recorded so the next lane does not re-spend the turn:

| named | status |
|---|---|
| `fleet-triage/research/seed-documents/` | **does not exist** — the directory is absent |
| `SuperInstance/quilt-atlas` `seed-dna.json` | exists, but at **`seed-dna/seed-dna.json`**, 90 records |
| `SuperInstance/fleet-kit` at `projects/fleet-kit` | **not a git repo** — the real clone is `projects/prod/fleet-kit` |
| `emit_key.py` in `mavis-workspace` | not found on this filesystem |
| `probe/colour_probe.cs` | named `real_rasterizer_probe.cs` |

`projects/prod/fleet-kit` also carries a **divergent local commit** (`8b28209`,
"make production what can be production") that cannot fast-forward onto `main` and
deletes the module structure. `main` is the authoritative line; I worked from a clean
worktree of `origin/main` at `e06f00a` and left the local branch untouched.

---

## 8. What the next lane should do

1. **Push `c1db1a0`.** It is ready and verified. This is the only thing blocking the
   deliverable, and it is a credentials problem, not a code problem.
2. **Run L11 fleet-wide once auth exists.** 33 of 61 receipt-bearing records in the seed
   set are violations by measurement; the live repo scan is the number that matters.
3. **File `projection`.** It is specified, measured, and unfiled. Your hypothesis
   explains this one correctly.
4. **Namespace `edge` / `tick` / `fold`** rather than filing them. They are contested,
   not vague. The evidence is in §5.
5. **Fix the credential helper** to fail closed. It currently fails open, and that is
   how this lane's push died with a message that implies the wrong cause.
