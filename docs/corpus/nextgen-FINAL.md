# nextgen-FINAL — the merge that cannot be committed silently

**STATUS: ALL THREE COMMITS DONE AND GREEN.** 11/11 pins, 59 checks, exit 0, on git 2.39.5.

| | |
|---|---|
| Working clone | `/workspace/projects/fleet-triage/quilt-in-git-adj` |
| Branch | `adjudication` |
| Substrate | `SuperInstance/quilt-in-git` @ `6a1ae48` — **forked, never pushed to** |
| Commits | `104f9e0` journal the merges · `dc547b8` the refusal · `01197a0` hash the receipt · `4239837` README |
| Runtime added | 585 lines under `.quilt/`, of which **~120 are the adjudicator** |
| Dependency list | **git and a POSIX shell. Nothing else.** |
| Demo | `./demo.sh` → exit 0, both panes behave as described |

```bash
git clone <this repo> && cd quilt-in-git
bash tests/pins_quiltgit.sh     # 11 pins, 59 checks. exit 0.
./demo.sh                        # two-pane refusal. exit 0.
```

---

## The three commits, exactly as scoped

### 1. `104f9e0` — journal the merges ✅

`.quilt/hooks/post-merge` (new) + `diff-tree -m` in `quilt-receipt`. Receipts gained
`parents` and `merge` fields. **~40 lines.** The hook is `post-commit` with one
difference and the difference is the whole commit.

**Receipt, measured:**
```
$ git diff-tree --root --no-commit-id --name-only -r HEAD -- cells/
[]                                   # 2-parent merge
$ git show --stat HEAD
 cells/auth/dials/1 | 2 +-          # the change existed
$ git diff-tree -m --root --no-commit-id --name-only -r HEAD -- cells/
cells/auth/dials/1                  # what the fix sees
```
P7 green here; **red on the untouched substrate** — `pins/failfirst-merge.log`,
`FAIL P7c merge produced NO receipt`, exit 1.

### 2. `dc547b8` — the refusal ✅ *this is the entry*

A claim is `claim: <key> = <value>  by <attribution>` in a cell body. Two claims
conflict when they share a key, differ in value, **and** come from different
attributions. On conflict: `.quilt/adjudications/<short>.json` naming the winner,
**both losing claims verbatim**, the reason, and a one-command way to take the
other number — and **exit non-zero**. Reads bodies, never dials; writes nothing
under `cells/` (P8j asserts it).

**Receipt, measured** (`./demo.sh`, real run):
```
quilt: REFUSING the merge — the result asserts one key twice with two values.
  key: inbound_edges
    19                           by quilt-tools#32 fb2e041
    21                           by quilt-tools#33 0101409
$ echo $?  ->  1
HEAD before : 4c453deb     HEAD after : 4c453deb     (HEAD did not move)
dial files changed by the refusal: 0
```

**No judge.** Every record carries `"adjudication": "mechanical"` and
`"judge": "none — no model is in this loop, by design"`. The winner is whichever
claim arrived on the side being merged — an *ordering*, not a judgment about
truth. There is no model in this repository and no call to one. The entry's
strength is that it can say when the judge is not worth running.

### 3. `01197a0` — hash the receipt ✅

`.quilt/bin/quilt-hash`, used by both `post-commit` and `post-merge`. Field 2 is
now the content hash of the receipt, **algorithm-prefixed** (`sha256:…` / `sha1:…`)
because the sha1 fallback is real. P9 recomputes the digest with coreutils rather
than with `quilt-hash` — a check, not a tautology — then mutates the receipt and
requires the hash to change.

```
tick a6e0266 sha256:a22bb4dac80d7d99e34be7ab81e40a3e47034b9631e53051ec9bef15aff024a8 a
```
**FAIL-first:** on the substrate, `FAIL P9b field 2 is still a duplicate of field 1`.

---

## Corrections to the brief

**1. The quoted hash grep is wrong.** The brief says
`grep -rniE "sha|hash|md5|digest|checksum"` returns **zero hits**. It returns
**six**: `README.md:74` (`tick <short> <receipt-hash> <cells>`), two in
`quilt-receipt`, one in the pin harness, and the committed log. The **defect is
real and worse than stated** — the README names a `receipt-hash`, the field is a
duplicate of field 1, and *no hash is computed anywhere*. The zero-hit receipt
was wrong; the conclusion stands.

**2. The fixture's invalid-syntax state is already resolved upstream.** The PR
steward's recount: `quilt-tools#32` and `#33` are **both merged** (20:08, 20:29),
`#34` branched on top of the result, and `git diff origin/main...origin/pr/32`
is **empty**. The invalid-syntax hazard "no longer exists" — it was real when the
mechanical merge was refused, and the fix happened in the order the semantics
required. So the demo is a **faithful reconstruction of the conflict shape, not a
live replay**, and the demo script says so in its header. Both PRs' counters are
real (`19` / `21` edges, from the steward's table).

---

## Two things I found by building rather than reading

**1. One refusal door is not enough — a real hole in the scoped design.** git runs
`pre-merge-commit` on the clean `git merge` path but **does not run it** when a
conflict is resolved by hand and concluded with `git commit`. Measured: with only
`pre-merge-commit` installed, that merge commit **was created and the hook never
ran**. That is the common path and the path the fixture takes. `pre-commit` runs
there, so the check is enforced from both doors. **P8m pins the `git commit` path
specifically.** Had I built only the scoped `post-merge` hook, the entry would
have been decorative on the most common merge.

**2. A fourth substrate defect, found only by trying to merge.** The generated
journal (`watch.log`, `receipts/`) was **tracked**, and hooks rewrite it on every
commit — so the moment a second branch exists, every merge text-conflicts on the
journal before reaching the cells:
```
Auto-merging .quilt/watch.log
CONFLICT (content): Merge conflict in .quilt/watch.log
```
A journal that conflicts on contact cannot survive contact with a second writer.
`quilt-init` now writes `.quilt/.gitignore`; the journal is untracked. **This is
the one change that alters a substrate property, and it is what made merging
possible at all.** It is flagged as such in the README.

## Two fail-open defects in my own harness, found by the work

1. **A missing pin reported PASS.** `"pin_p8"` on a shell with no such function
   prints "command not found", records nothing, and the verdict defaults to PASS.
   My first P11 draft did exactly this and reported P8/P9 green on a substrate
   that has neither. A listed-but-undefined pin is now a hard FAIL.
2. **The substrate's own verdict matcher breaks at ten pins.**
   `case "$FAILS" in *" $p"*)` matches `" P1"` **inside `" P10"`**, so a P10
   failure flips P1 to FAIL. Latent at six pins, live at ten. `verdict_of` now
   requires a letter or dash after the pin id, never a digit. **P11 pins that**,
   including the exact ` P10` / ` P10a` / ` P1` cases.

Also: P8's first draft went green **for the wrong reason** — `git checkout main`
failed on the dirty tracked journal, the script carried on, and `checkout -b pr33`
silently branched off the wrong parent. `on()` now dies loudly on a failed
checkout, and **P8b2 asserts the refusal is the *cause*** of the failed merge, so
the pin cannot go green because the tree happened to be dirty.

---

## The suite is not vacuous — including my own code

| mutation | result |
|---|---|
| substrate `val = v*w` → `val = v*w*0` (the scout's) | **CAUGHT** — `FAIL P3b`, exit 1 |
| `quilt-adjudicate`: conflict detection → `if (0)` | **CAUGHT** — `FAIL P8b`, exit 1 |
| `quilt-hash`: digest → constant zeros | **CAUGHT** — `FAIL P9e` + `FAIL P9f`, exit 1 |

The second and third matter more than the first: they are mutations of code I
wrote today, and they prove P8 and P9 constrain semantics rather than presence.

## Receipts summary

- [x] substrate pins re-run on git 2.39.5 — **6/6 pins, 23 checks, exit 0**
- [x] defect 1 (invisible merges) — reproduced, with the empty-vs-`2 +-` receipt
- [x] defect 2 (fake hash) — reproduced; **the quoted grep is wrong, the defect is worse**
- [x] defect 3 (no contradiction vocabulary) — 0 hits for `claim|contradict|assert|disagree|conflict`; a CONFLICT repro left `watch.log` unchanged
- [x] commit 1 — P7 green, red on substrate
- [x] commit 2 — P8 + P8m green, red on substrate, demo exit 0
- [x] commit 3 — P9 green, red on substrate
- [x] substrate pins still green after all three — **11/11 pins, 59 checks, exit 0**
- [x] fresh-clone verification — clone → pins → demo, all exit 0

## Hard constraints held

- **Forked; never pushed to `quilt-in-git`.** No write of any kind to upstream.
- **Runnable by a stranger with git and a shell.** No Node, no Cloudflare, no
  account, no network, no API key, no install step.
- **No judge, no model, no `CONTROL`-mode button, no "agent-blind, not
  node-blind" gate.** The advisory lane's claims are **not** implemented here and
  **no README line claims them.** I did not add a twelfth unbacked artifact.
- **No Cloudflare Durable Object.** The offer was open ("if you want one") and I
  declined it: a DO per branch would add an account, a deploy step, and a network
  dependency to an entry whose entire claim is that it is a *local, mechanical*
  refusal with nothing to authenticate against. If you want a hosted
  adjudication viewer, that is a separate artifact and I will not smuggle it in
  here.
- **Every README claim points at a line of code or a committed log.**

## Open item for you

I have not pushed anywhere. **Send me the entry repo URL** and I will open the
branch. I will not push to `quilt-in-git` under any circumstances.

The demo script is written and passing. The argument about it — whether the
right-hand pane should be the refusal *record* rather than the refusal *message*,
and whether `demo.sh` should drive both panes in one process or be split for
side-by-side terminals — is the next thing worth having.
