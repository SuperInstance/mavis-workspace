# PLAYTEST-OUTSIDER

**Lane:** play-test the fleet as a stranger. No fleet context, no READMEs until after first
invocation, no pushes to repos I did not clone.

**What I was handed:** an empty workspace, `${GITHUB_TOKEN}` **empty** (`len=0`), no `gh`,
no proxy. `git node python3 curl jq gcc` present. Egress works — TLS 1.3 to github.com
completes. Everything below happened in `/tmp/outsider`.

**Time-to-first-result** is counted as: commands a stranger must type, from empty directory
to a real result on real data. READMEs unread until the last section.

---

## 0. The finding that reframes the table

**Three of the four tools the brief nominates do not exist in public form.** I enumerated
the owner's 599 public repos and probed the API directly.

| guess | `GET /repos/SuperInstance/<name>` |
|---|---|
| `fleet-resolver`, `fnindex`, `quilt-fleet-resolver`, `quilt-resolver`, `claim-resolver` | **404** |
| `fleetlint`, `fleet-lint` | **404** |
| `lane-checker`, `lane-check`, `readme-verifier` | **404** |

Keyword search of the full public list (`lint|verif|lane|resolv|claim|select|connect|minmax|index|solve`)
returns exactly six names, of which two are the tools I could clone:

```
connect4   eigenvalue-solver   fleet-connections   profile-lane   qthe-verify   selectlib
```

And the headline endpoint:

```
$ getent hosts fleet-resolver.prong-potassium.workers.dev   ->  NXDOMAIN
$ getent hosts workers.dev                                  ->  resolves (104.18.x.x)
$ getent hosts cloudflare.com                               ->  resolves
$ curl -X POST https://fleet-resolver.prong-potassium.workers.dev -d '{...}'
HTTP=000  t=0.010s
```

Egress is open, DNS is open, the wildcard zone is up, **the route does not exist.** The
no-backticks control returns the identical `HTTP=000`, so I cannot even confirm the
backtick bug the brief describes — a silent zero and a dead host are indistinguishable from
outside. That is the finding: **the fleet's favourite tool has no liveness signal a stranger
can read.** An agent told to "use the resolver" has no way to tell working from dead, and
the honest move is to silently produce nothing. If a lane is fixing the backtick bug, it
should first check the route exists, because right now there is nothing to fix.

---

## 1. The table

| repo | time-to-first-result | my data or only its own? | 1 | 2 | 3 | the sentence a stranger needs |
|---|---|---|---|---|---|---|
| **selectlib** | **3 steps, 0 deps, 41 s** — `git clone`; `import selectlib`; `harness.run(...)`. No README needed. | **MY data.** My own `Field` from `classified.json`, my own `Selector`, zero edits to the library. Ran first try. | **YES** — see §2 | **PARTIAL** | **YES** (best in fleet) | *"If you have a coarse 2-D grid where the exact right value is known everywhere, and you need to prove that re-measuring k cells actually helps, `selectlib.harness.run()` will refuse to return a number until five controls have fired."* |
| **connect4 / `ctool.c`** | **4 steps, 1 dep (cc)** — clone; `gcc -O2`; `./ctool`; read manifest | **ONLY ITS OWN.** No entry point takes a position. The only argument is a ply limit. | no | **YES** (the only clean yes I found) | **NO** | *"If you need Connect-4 positions labelled with exact forced-win/draw values, `gcc -O2 -o ctool ctool.c && ./ctool` writes 54,166 fully-solved positions in under a second — but it will only ever export its own corpus, so to ask it about your own position you must write your own `main()` around its `solve()`."* |
| **connect4 / `c4.py`** | never — OOM-killed | — | no | — | **NO** | Do not use. See §4. |
| **connect4 / `truth.py`** | never — `TypeError` | — | no | — | **NO** | Do not use. See §4. |
| **connect4 4×4 claim** | unreachable without a 3-line C patch | — | no | — | **NO** | Digests `3,338 / 0xcdc9636c704a7ba2` **do not reproduce.** See §3. |
| **fleet-resolver** | **never** — NXDOMAIN | — | ? | ? | **NO** | *"It is not there."* |
| **lane checker** | not obtainable — 404, no public source | — | ? | ? | **?** | Cannot be evaluated. |
| **fleetlint** | not obtainable — 404, no public source | — | ? | ? | **?** | Cannot be evaluated. |
| **pie-minimax** | cloned, **not played** — out of lane time | — | ? | ? | ? | Not evaluated. Stated as untested, not as failed. |

Honesty note: three of the brief's four nominated tools could not be obtained at all. I have
marked them `?` rather than `NO` on bars 1–2, because *unobtainable* is not *does not clear*.
On bar 3 they are all **NO** regardless, and that is a finding, not a gap in my work.

---

## 2. The three worth sharpening into standard form

I only have two, not three. I am not going to pad the list to match the brief.

### (1) `selectlib` — the only one that took my code unmodified

This is the surprise, and it is a good one. I wrote a `Field` from a JSON census file and a
`Selector` (robust median-residual outlier rank) I had never seen, from the dataclass
signatures in `__init__.py`, and the harness ran it first try with **no library changes**,
**no README**, **zero dependencies**, and no `requirements.txt`/`pyproject.toml`/`setup.py`
to be confused by. Its own suite is **10 passed, 0 failed**.

| budget | seed | oracle | local_noise | mine | mine < noise? |
|---:|---:|---:|---:|---:|---|
| 1 | 0/1/2 | 0.01131 | 0.01214 | 0.01214 | tie |
| 4 | 0/1/2 | 0.00931 | 0.01157 | **0.01138** | **YES** |
| 12 | 0/1/2 | 0.00624 | 0.01018 | 0.01025 | no |
| 24 | 0/1/2 | 0.00367 | 0.00735 | **0.00652** | **YES** |
| 48 | 0/1/2 | 0.00000 | 0.00000 | 0.00000 | tie |

**Bar 1 is a genuine yes, and it is not about speed.** The capability is not "compute a MAE"
— I can compute a MAE. It is: *a number that will not exist until the instrument has been
shown to work.* `harness.run()` runs the control suite **before** any measurement and lets
`ControlFailure` propagate. `Result.verdict()` exists specifically so a caller cannot report
a number from a run that never checked. Neither I nor a bare `for` loop can produce that
property. The tool and the agent are each half of it.

**Bar 2 is partial, and honestly so.** The *field* part is arithmetic. The part agents cannot
do is the **control-gated refusal plus the oracle bound** — the oracle is what makes "my
selector beat free noise" a statement instead of a coincidence, because a lucky selector and
a good selector are otherwise indistinguishable. That is a real capability gap, but it is
narrower than the brief's framing.

**Bar 3 is the best in the fleet.** Three steps, no dependencies, no account, no fleet
vocabulary. The library's vocabulary ("field", "target", "budget", "control") is generic
enough that I had to invent my own task to use it, and it did not care.

**Two defects, both in the parts that would be the standard form:**
- `Result.table()` is **misindented and drops rows.** `for c in cols:` is dedented out of
  `for r in self.rows:`, so it runs once on the last row. My 15-row result printed a header
  and **one** data row. The public display surface of the library is the one thing that
  silently discards results.
- **The central thesis is not enforced.** `selectors.py` says *"A selector that does not beat
  it is not a finding; it is arithmetic done expensively."* I ran a selector I built to be
  **worst possible** (picks the cells with the *least* error). It came back
  `controls 5/5` and a normal row. The harness gates on *instrument validity* and not at all
  on *selector quality*. The refusal exists; the decision it exists to support does not.

### (2) `ctool.c` — the only clean bar-2 yes, and only as a corpus generator

No agent can decide minimax in its head. That part of the hypothesis holds and I confirmed
it hard: **the Python in the same repo cannot do it at all** (§4). C compiles in 0.42 s and
solves 54,166 positions to full depth in under a second, with a transposition table and real
alpha-beta (`negamax(Board pos, Board mask, int alpha, int beta, ...)`), plus four
self-checks that read the export back and refuse to publish a file that fails them. That
"refuse to publish" logic is real engineering and it did its job on me (§3).

But as shipped it is a **jig**: it answers exactly one question — "regenerate my corpus" —
and it will not answer yours. The only CLI argument is a ply limit. To ask it about a
position I cared about I had to write my own `main()` around its `static int solve()`. I did
not, because `c4.py` was the advertised path and it is broken. **Bar 3 fails hardest here**:
a stranger following the Python file the repo leads with hits an OOM.

The standard form is obvious and cheap: a `solve FEN-ish-string` subcommand, a `--board WxH`
flag, and delete `c4.py` and `truth.py` rather than ship two dead siblings next to a working
C file.

### (3) — reserved

`pie-minimax` is the obvious candidate (it is the *source* of the pre-registered prediction
that `connect4` is built to test, and the brief's own chain says so) but I ran out of lane
time and did not play it. **I am listing it as untested, not as clearing the bar.** Anyone
sharpening this into standard form should play that one next.

---

## 3. What I could not make reproduce, in the repo the brief trusts most

**The 7×6 digest is real. The 4×4 digest is not.**

`./ctool` default run reproduces `54166 / 0x4ef8351a5c319637` exactly, and I independently
recomputed the FNV-1a-64 over the shipped `c4_ground_truth.txt` byte-for-byte: `0x4ef8351a5c319637`.
So that number is honest.

For 4×4, `WIDTH`/`HEIGHT` are `#define`s, and `BOTTOM_BITS` is a **hardcoded 7-column
literal** `0x0002040810204081ULL /* bits 0,7,14,21,28,35,42 */`. I changed the two dimension
defines, fixed the sentinel bits to `0x8421` (bits 0,5,10,15), and fixed the one control that
hardcoded the literal 7 (`n1 == 7` → `n1 == WIDTH`). Three lines. Then:

| config | positions | digest |
|---|---:|---|
| 4×4, plies 1–6 | 1,343 | `0xe25121fa1326878b` |
| 4×4, plies 1–7 | 2,200 | `0x73ee72c56ce622f9` |
| 4×4, plies 1–8 | 2,984 | `0x01afb35f76048d9a` |
| **claimed** | **3,338** | **`0xcdc9636c704a7ba2`** |

3,338 does not appear at any ply limit I tried, and the digest does not match. Either the 4×4
figures come from a different tool, or the repo cannot produce them. **Both digests should be
treated as unverified until someone reproduces the 4×4 one.**

**And the known-answer checks are size-blind.** With the board set to 4×4 and the sentinel
bits still wrong:

```
check 1  empty board, value for P1 = -1   expected -1   OK
check 2  three in the centre, value for P1 = +1   expected +1   OK
both known-answer checks passed
...
  1-ply rows   4  (expect exactly 7)  *** FAIL ***
```

Both "known-answer checks" pass on a **wrong-sized game**. The empty board is -1 and three in
the centre is +1 in any gravity game, so neither can see a board-dimension error. The brief
cites these checks as the reason to trust the tool; the checks are insensitive to the most
basic misconfiguration the tool admits. What actually caught it was the *export* control —
a different, weaker layer. That is the same shape as a vacuous test suite: green where it is
easy, red only by accident.

**The digest is a determinism check, not a correctness check.** `./ctool 5` gives 12,427
positions and `0x1428eb1eab901a77`. So the headline digest is a function of the *default
argument*. Recomputing it proves the tool is deterministic; it cannot prove the solver is
right, because the tool hashes its own output. The real correctness evidence would be
agreement with an independent solver — which is exactly what I tried to build, and which
`c4.py` made impossible.

---

## 4. The most instructive failure: `c4.py`, the file the repo leads with

I expected the brief's list to be roughly right and the lint suite to fall over. Instead the
sharpest thing I found is a **solver that cannot solve one move of Connect 4 while shipping a
1.5 MB corpus of positions its own solver cannot produce.**

`c4.py`'s module docstring opens by explaining that five earlier versions used the standard
49-bit Pons bitboard and every one failed in a way that looked like a result, and retires to
a flat 7×6 array of tuples because *"a representation you cannot reason about is a
measurement instrument you cannot check."* That is an excellent paragraph, and then:

```
$ python3 -c "import c4; print(c4.value_for_p1(c4.new_board()))"
rc=124        # timeout at 60s

$ python3 duel.py      # my ply-9 position
Killed        rc=137   # OOM
```

By ply, on a fresh process each time:

| ply | result |
|---|---|
| 0 (empty board) | killed |
| 2 | killed |
| 3 | killed |
| 4 | `value = 1` ✅ |
| 9 (my position) | **OOM-killed** |

`MAX_PLY = 11` with a single `lru_cache` and one weak `best == 1` early-out. And:

```python
def negamax(b, turn, depth=MAX_PLY):     # three parameters. no alpha. no beta.
```

**The docstring's central claim — "The solver is negamax with alpha-beta" — is false.** There
is no alpha and no beta anywhere in the file. The C tool in the same repo *does* have them
(`ctool.c:219`). The Python transliteration dropped them, and the prose was never updated to
match, so the file advertises the one property that would have made it work.

And the generator that produced the shipped corpus:

```python
sys.path.insert(0, '/workspace/projects/connect4')     # hardcoded absolute path
...
if c4.wins(p0) or c4.wins(p1):      # TypeError: wins() missing 1 required positional argument
```

`truth.py` was never migrated off the bitboard API. It calls `c4.wins(p0)`, `c4.play(p0, c)`,
`c4.negamax(p0, p1)` against a library whose signatures are `wins(b, player)`,
`play(b, c, player)`, `negamax(b, turn, depth)`. It dies on line 64, immediately, in a fresh
clone. **So `c4_ground_truth.txt` cannot have been generated by `c4.py`, and cannot be
regenerated by it.** It is a 1.5 MB orphan of a deleted ancestor, shipped beside a solver
that cannot consume its representation — the file is Pons bitboard masks (`1 1 -1`,
`128 128 -1`) and `c4.py` is a flat tuple-of-tuples. Nothing in the repo connects them.

Worse for bar 3, and this one is subtle enough to be worth the space: because
`sys.path.insert(0, '/workspace/projects/connect4')` puts a **fleet-internal absolute path
first on the import path**, running `truth.py` from my clean clone *silently imported the
fleet's copy of `c4.py` and not mine.* I only caught it by asking `c4.__file__`. On a
stranger's machine that path does not exist and it is an `ImportError` instead. Either way
it is broken; the point is that the one diagnostic it produces depends on which account you
are.

**Why this is the most instructive failure in the whole lane.** The repo contains a
paragraph of genuinely excellent reasoning about why its own earlier representations were
untrustworthy, and it is *correct* — and then it ships a new representation whose failure
mode is precisely the one it diagnosed: a plausible number from a solver that is not
checking itself. The lesson was learned, written down, and not applied to the artifact
immediately downstream of the paragraph. **A stated principle is not a control.** The one
control that would have caught this — "the Python solver must reproduce the digest the C
solver produces" — is one line, runs in under a second, and does not exist.

---

## 5. The one thing that would have to be true for the rest to ever clear it

**Every one of these needs an input/output contract a stranger can hit in one call, where the
thing being asked is a question about the caller's own data rather than a regeneration of the
author's.**

That is the whole gap, and it is one shape repeated:

| tool | what it accepts | what it can only do |
|---|---|---|
| `ctool` | a ply limit | regenerate its own corpus |
| `c4.py` / `truth.py` | nothing | (broken) |
| resolver | a URL that does not resolve | — |
| fleetlint / lane checker | unobtainable | — |

Nothing in the public fleet takes **my** position, **my** grid, **my** prose, **my** repo, or
**my** judge pool and returns an answer keyed to it. The two that come closest — `selectlib`,
which took my `Field` and `Selector` without complaint, and `ctool`, whose `solve()` is
genuinely correct and merely unreachable — are the two with any chance.

Concretely, the single highest-leverage change is a **one-command, no-auth, take-my-input
contract** with a liveness signal:

```
$ tool --selftest            # exits 0, prints a digest, works offline
$ tool <my input>            # answer about MY data, not the author's
```

`ctool` already has half of this (`--selfcheck` inside, the known-answer banner, the
refuse-to-publish logic) and does not expose it. `selectlib` has the other half (works on any
`Field`) and does not expose *that* either — but it is the one where the two halves are
already in the same process.

The secondary thing, which cost me the whole lane on one tool: **liveness must be checkable
without the tool.** A dead worker and a working one both return `HTTP=000`-shaped nothing to
an agent that is not looking carefully. Anything a stranger is told to depend on needs a
health URL that answers even when the main route does not.

---

## 6. Corrections to the brief's hypothesis

1. **"Only three or four clear bar 2."** I found **one clean yes** (`ctool`, and only as a
   corpus generator) and **one partial** (`selectlib`). The hypothesis is directionally right
   and numerically generous.
2. **"`selectlib` chooses among judges and measures whether the choice beats free local
   noise."** The measuring half is real and is the best thing in the fleet. **The "beats free
   local noise" half is not implemented** — it is a sentence in a docstring. A worst-possible
   selector scores 5/5 controls and a normal row.
3. **"The lint suite should fail."** Untested, because `fleetlint` does not exist publicly
   under any name I guessed (6 variants, all 404). I still expect it to fail bar 2 — grepping
   is a capability I have — but that is a prediction, not a measurement, and I am flagging it
   as such rather than taking credit for a result I did not get.
4. **"The resolver is live."** It is not. `NXDOMAIN`, with the wildcard zone and general egress
   both healthy. Whatever a lane is fixing in the backtick handling, there is currently no
   route to fix.

**Not tested, stated as such:** `pie-minimax` (cloned, unplayed), the lane checker and
`fleetlint` (unobtainable), and any of the 4,042 repos that are neither public nor named here.
