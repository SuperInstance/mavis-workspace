# SYN-CLAIMSTATE — transplant: D1 schemas vs. repo migrations, resolver on the corpus

**Lane B (synergy). Started 2026-10-01 20:33 UTC. Stub written at ~10 min as instructed.**

**Bottom line up front:** the D1 half is blocked on an absent credential and I will not
pretend otherwise. The resolver half produced a **negative result that inverts the brief's
framing**, and the repo-side census — fully doable offline — produced the strongest single
finding in this report. Read-only throughout. No pushes.

---

## 0. Two results that invert the brief

### 0.1 The resolver fails its own named ground-truth case

The brief said: *"Verify it on a known case first — the `6.8×` claim in `eisenstein`, where the
document states `59,841 / 10,428` and that arithmetic gives 5.7385. If the resolver gets that
wrong, report the tool broken rather than reporting its output."*

It gets it wrong. `SuperInstance/eisenstein` README, verbatim:

> "Eisenstein triples are ~6.8× denser than Pythagorean triples — **59,841 versus 10,428** at the same bound"

```
59841 / 10428 = 5.73849252013809
```

`resolver.extract_numeric_claims()` over the real README: **0 findings.**

**And it fails in the opposite direction from Lane 1's four bugs.** Those manufacture findings.
This one *suppresses* them. Verified by direct experiment:

| input form | `OPERANDS` match | RATIO_MISMATCH |
|---|---|---|
| `` 6.8x denser (59,841 vs 10,428) `` | yes | **1** — checker works |
| `` 6.8x denser — 59,841 versus 10,428 — `` *(the real text)* | **no** | **0** — silent |

`resolver.py:1004`:
```python
OPERANDS = re.compile(rf"\(\s*({NUM})\s*(?:vs\.?|versus|to)\s*({NUM})\s*\)", re.I)
```
The operand extractor is **format-locked to literal parentheses**. The real document uses an
em-dash. The check never fires. A tool that certifies this README as numerically sound has
certified a document containing a false constant — and, per §0.2, two passing tests.

**This is a fifth bug and the most dangerous one for this corpus:** the other four are
confident-and-wrong; this one is confident-and-silent. A tool that is silent is never
adversarial, but it also means the corpus has *no* numeric coverage at all from this instrument.

### 0.2 The false constant is load-bearing in a test that cannot fail

`6.8×` appears in **4 files** of `eisenstein`: `README.md`, `CONTRIBUTING.md:68`,
`src/lib.rs:32`, `tests/algebraic_properties.rs:636,688`. The property test that appears to
verify it, `eisenstein_triple_density_advantage`:

```rust
// Eisenstein triples are ~6.8× denser than Pythagorean triples.
// At c ≤ 50, Pythagorean triples: 16 primitive.
let triples = EisensteinTriple::all_with_max_norm(50);
assert!(
    triples.len() >= 16,          // <-- asserts parity with the baseline
    "Should find at least 16 Eisenstein triples with c ≤ 50, found {}", triples.len()
);
```

The comment states the comparison is 6.8×. The assertion checks `>= 16`, where the comment's own
baseline **is 16**. **A 1.0× result passes this test.** It is a test that cannot fail on the
claim it appears to certify, and it hardcodes the false constant's baseline as its oracle. The
comment even concedes the point: *"exact number depends on search"*.

So the chain the brief describes — README, CONTRIBUTING, `src/lib.rs`, two passing property
tests, and a paper citing it as verification — is real, and the last link is a test that
certifies parity while claiming 6.8×.

---

## 1. The blocker, stated precisely

**No Cloudflare credential is present in this session.** Not invalid — **absent**.

| Checked | Result |
|---|---|
| process env (29 vars) | zero CF-related |
| `/proc/1/environ` (pod env) | zero CF-related |
| `ENVD_DIR=/mnt/envd` | ships `agent-helper`/`envd` binaries only, no secrets |
| `$XDG_CONFIG_HOME/.wrangler/` | 400+ log files, no persisted OAuth material |
| `/workspace/.wrangler/` | account cache only, no token |

**Network is not the problem.** An unauthenticated request to the exact endpoint in the brief:
```
POST .../accounts/049ff5e8.../d1/database  -> HTTP 401
{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}
```
`10000 Authentication error` is precisely what a missing bearer produces. The account ID in the
brief matches the one wrangler has cached. A prior agent recorded the identical blocker at 18:57
in `cf-D1.md`; I confirmed rather than re-derived it, and spent the remaining time on the work
that does not need the token.

### Empty and inaccessible are different findings

**All 44 databases are `INACCESSIBLE`. Not one is known to be `EMPTY`.** No database in this
account has been read by any agent. The prior repo-side census that *names* databases is a
**claim, not an observation** — and §3 shows that claim set has a hole in it.

---

## 2. Read-only enforcement: verified, not assumed

`cf_d1_readonly.py` (prior agent) enforces read-only **in code**, as the brief requires. I ran
its selftest rather than reading the code and believing it:

```
Gate 1 — SQL assertion
  ALLOW  'SELECT 1'                        ALLOW  '  select name from sqlite_master'
  ALLOW  "-- a comment\nPRAGMA ..."        ALLOW  '/* c */ WITH x AS (SELECT 1) SELECT * FROM x'
  BLOCK  'DROP TABLE t'                    BLOCK  'DELETE FROM t'
  BLOCK  'INSERT INTO t VALUES(1)'         BLOCK  'UPDATE t SET a=1'
  BLOCK  'CREATE TABLE x(a)'               BLOCK  "ATTACH DATABASE 'x' AS y"
  BLOCK  'PRAGMA writable_schema=ON'       BLOCK  'VACUUM'
  BLOCK  '--x\nDROP TABLE t'               BLOCK  ''
Gate 2 — verb/endpoint
  BLOCK POST inventory (write sql)         BLOCK POST /execute
  ALLOW POST /query (allowed)
selftest OK
```

14 adversarial strings, all correctly gated — including the comment-smuggling case
`--x\nDROP TABLE t` and `PRAGMA writable_schema=ON`, which is the classic D1 write primitive.
There is no code path to `/execute` or any migration endpoint. Given that a migration on a live
edge database is irreversible, this is the one property in this lane that must not be
improvised, and it holds.

**Credentials:** `${CLOUDFLARE_TOKEN}` — **absent**; `${GITHUB_TOKEN}` — **absent**. Reported
by location and type only. No value was read, logged, or written. GitHub public reads succeeded
unauthenticated (repo metadata + `raw.githubusercontent.com`), which is why §0 and §3 were
possible at all.

---

## 3. The repo-side claim set (the half that needs no credential)

`d1_claim_baseline.py` → `d1_claim_baseline.json`. Reads `.sql` + wrangler configs only.

**15 repos · 84 tables · 501 declared columns · 1 `ALTER TABLE`**

| repo | database_name | resolvable id | migration files | tables | cols |
|---|---|---|---|---|---|
| **Tripartite1/cloud** | **superinstance** | **NO — empty** | 0 | 12 | 103 |
| fleet-static-host | quilt-fleet-db | yes | 6 | 11 | 51 |
| mist-lab | mist-lab-db | yes | 0 | 2 | 11 |
| mist-quilt | mist-quilt-db | yes | 0 | 4 | 29 |
| rc-20260824-01 | quilt-fleet-db | yes | 1 | 5 | 34 |
| scrap-quilt | scrap-quilt-db | yes | 0 | 7 | 53 |
| scrap-voice | scrap-voice-db | yes | 0 | 1 | 8 |
| + 4 `recovered-copy-*` | *(duplicates of mist-lab/quilt, scrap-quilt/voice)* | yes | — | — | — |
| axum, fleet-memory, keel-early-version | *(SQL present, **no D1 binding**)* | — | 6 | 18 | 73 |

### 3.1 The structural finding: `IF NOT EXISTS` makes drift undetectable *by construction*

**37 of 37 `CREATE TABLE` statements across every D1-claiming repo are `CREATE TABLE IF NOT
EXISTS`.** Exactly **one** `ALTER TABLE` exists in the entire fleet
(`fleet-static-host/migrations/0004`: `ALTER TABLE forest_walks ADD COLUMN session_id TEXT;`).

`IF NOT EXISTS` is a **no-op when the table already exists** — it reports success while doing
nothing. Three consequences, all structural, all provable without touching a database:

1. **A migration is inexpressible.** A migration must *alter*; `IF NOT EXISTS` never alters.
2. **Re-applying the schema to a drifted database succeeds silently.** The drift survives and
   the run reports OK. A green deploy is not evidence of a correct schema.
3. **For 5 of 6 D1 repos, the repo-side claim is unfalsifiable against a live DB.** There is no
   artifact that could ever disagree with reality, because the artifact cannot express a
   difference.

`fleet-static-host` is the sole repo with an ordered migration history (6 files) and the only
one that *can* express drift. It should be the reference pattern.

### 3.2 The claim set is inflated by duplicates

4 of 11 wrangler declarations are `recovered-copy-20260824-*` byte-duplicates of `mist-lab`,
`mist-quilt`, `scrap-quilt`, `scrap-voice`, with **identical UUIDs**. Any DB↔repo diff must
deduplicate by UUID or it will report the same database four times and inflate its apparent
contradiction count.

### 3.3 Six names in the brief are not repos

`superinstance-db`, `i2i-ledger`, `quilt-db` → **HTTP 404** on `SuperInstance`. `quilt-edge-lab`
→ 200 (cloned, real). The brief's framing of repo↔DB pairs partly does not exist: these are
database *names*, and only one has a repo.

---

## 4. The resolver on this corpus

**Corpus: 70 documents, 6 D1-claiming repos + `quilt-edge-lab`. 80 citations.**

| outcome | n | share |
|---|---:|---:|
| RESOLVES | 39 | 48.8% |
| AMBIGUOUS | 16 | 20.0% |
| FILE_MISSING | 10 | 12.5% |
| PATH_PRECISE_ONLY | 9 | 11.2% |
| SKIP / REPO_NOT_INDEXED / REPO_UNKNOWN | 6 | 7.5% |
| **LINE_OOR** | **0** | **0%** |
| **numeric findings** | **0** | — |

**Two structural facts, measured:**
- **0 of 80 citations carry a line anchor.** The ±140-char window bug (defect 1) has an *empty
  population* here — it cannot fire because no citation on this corpus has an anchor to
  misattribute.
- **0 numeric claims extracted.** §0.1's format-lock, at corpus scale.

So **two of Lane 1's four known bugs have no population on the very corpus this lane was
scoped to.** The corpus is 70 documents of mostly SQL and config.

### 4.1 How many findings are plans rather than defects

Lane 1's method: count roadmap-vs-defect. I hand-classified every `FILE_MISSING` against the
filesystem, because the obvious filename heuristic (`IDEATION|ARCH|FEASIBILITY`) is itself
unreliable — `ARSENAL.md`, `yard-band-spec-draft.md` and `WEEKEND2_MODEL_SMOKE.md` are planning
artifacts that a filename regex calls "shipped". I nearly published a 79.5% "shipped" figure off
that heuristic; it was an artifact of my own classifier.

Ground truth instead — for each dangling citation, harvest the **dotted API identifiers the
document itself documents**, and check whether they are implemented in the citing repo:

| document | cites | API ids | implemented | verdict |
|---|---|---:|---:|---|
| `scrap-quilt/README.md` | `kinematics.js` | 25 | **25** | **shipped under a stale name** |
| `mist-quilt/CONTRACT.md` | `flock.py` | 32 | **32** | **shipped under a stale name** |
| `fleet-static-host/…/VIBE-CODER-ARCH.md` | `ratelimit.ts`, `access.ts` | 5 | 2 | partly shipped |
| `scrap-quilt/docs/ARSENAL.md` | `mutate.ts`, `judge.ts`, `scope.ts` | 4 | 2 | partly shipped |
| `…/LINK-LAYER-FEASIBILITY.md` | `re_origin.ex`, `portal/disagreement.ex` | 1 | 0 | **genuinely a plan** |

**4 of 5 documents with dangling citations document APIs that are verifiably shipped.**

`kinematics.js` does not exist — and `scrap-quilt/src/` contains **no `.js` file at all**. The
`robot.*` API it describes is 100% implemented, in `sheet.ts:77`, `predict.ts:92`, `chat.ts:43`.
Same shape in `mist-quilt`: **no `.py` file exists anywhere in the repo**, and `flock.*`/`dog.*`
is 100% implemented in `chat.ts:35`, `predict.ts:29`, `sheet.ts`.

**These `FILE_MISSING` findings are technically true and substantively wrong.** They point a
reader at "dead documentation" when the documentation is alive, accurate about the system, and
wrong only about a filename's extension. That is worse than a false positive, because the
remedy it implies — go fix the docs — is the wrong remedy.

**Plans, honestly counted: 1 document of 5 (`LINK-LAYER-FEASIBILITY.md`, a feasibility study, and
its citations sit inside a fenced code sketch). The other 4 are stale-filename-over-shipped-code,
which is a defect — but a trivial, mechanical one, and not the one the tool implies.**

---

## 5. Findings, ranked

1. **`superinstance` — a `DB` binding with an empty `database_id` guarding 12 tables.** *(§6)*
2. **The resolver is silent on the one case it was built to catch** (§0.1) — fifth bug, opposite
   failure mode, and it is why the `6.8×` constant had to be found by a human reading a paper.
3. **`eisenstein_triple_density_advantage` cannot fail on the claim it certifies** (§0.2).
4. **`IF NOT EXISTS` × 37 makes drift undetectable by construction** (§3.1) — the single change
   with the best ratio of value to effort across the whole fleet.
5. **`FILE_MISSING` lacks a symbol-level fallback and therefore misdirects on stale filenames**
   (§4.1).
6. **Basename matching is 20% of this corpus's citations** (16/80 `AMBIGUOUS`) — defect 4's
   population is real and large; "basename exists in 69 repos" is the modal message.

### Recommended fixes (described, not applied — read-only lane)

- **Resolver:** loosen `OPERANDS` to accept em-dash/en-dash/comma-delimited operands, not just
  parenthesised. One regex change, closes §0.1.
- **Resolver:** when a file is missing, fall back to a document-level dotted-identifier harvest
  against the citing repo before emitting `FILE_MISSING`; emit `STALE_FILENAME` when the
  documented API is present. Note `_symbol_check` (`resolver.py:602`) is only called on the
  found-file path (`resolver.py:777`), and `c.symbols` was empty for all 10 findings — so the
  fix is a *document-level* harvest, not a reuse of the existing symbol field.
- **Resolver:** skip fenced code blocks. The `.ex` citations come from inside a code sketch.
- **Repo:** convert `schema.sql` files to numbered migrations; `ALTER` beats `IF NOT EXISTS`.
- **`Tripartite1/cloud`:** the empty `database_id` should fail loudly at config load, not ship.

---

## 6. The one database that most contradicts its repo

**`superinstance` — declared at `repos/Tripartite1/cloud/wrangler.toml:51-54`.**

```toml
[[d1_databases]]
binding = "DB"
database_name = "superinstance"
database_id = ""          # <-- empty
```

It is the repo-side claim that most sharply contradicts any database it could attach to, and it
is the one place in the fleet where the contradiction is provable **without reading a single
database**:

- A Worker binds `DB` to a name with **no address**. The claim has no referent — it cannot be
  matched to any of the 44, and a repo↔DB diff cannot even ask the question.
- Behind that empty id sit **12 tables / 103 columns**, including `users`, `api_keys`,
  `billing_ledger`, `purchases`, `audit_log`. The most sensitive schema in the fleet is
  attached to the least specific address in the fleet.
- All 12 are `CREATE TABLE IF NOT EXISTS`, so re-applying the schema is a no-op that **reports
  success** (§3.1).
- The failure is silent in the worst direction: a deploy pipeline that "helpfully" fills the
  blank with the nearest available database turns this into a production-data incident, and
  nothing in the repo would resist it. A hard failure at config load is strictly safer.

**Caveat, stated plainly:** this is the strongest *repo-side* contradiction. I did not read a
live database and am not claiming `superinstance` exists, is empty, or holds any rows. Whether
it also contradicts a *live* schema is exactly the question the credential would answer.

---

## 7. Did the resolver earn its place on this corpus?

**No — and the reason is more useful than a yes would have been.**

- **On its own named test: no.** `eisenstein` README, 0 findings, false constant present (§0.1).
  Per the brief's own instruction, that means report the tool broken, not its output.
- **On anchor claims: no measurable population.** 0 of 80 citations carry an anchor; `LINE_OOR`
  is 0. Defect 1 cannot fire here.
- **On numerics: no population at all.** 0 claims extracted across 70 documents.
- **On paths: it fires, and it mostly misdirects.** 10 `FILE_MISSING`; 4 of 5 affected
  documents describe APIs that are verifiably shipped, so the finding is true about a filename
  and false about the system.

**What it did earn:** the outcomes are *reproducible by hand* — every hit carries the exact
bytes and the command to check, and I confirmed the read-only harness and the arithmetic by
direct execution rather than by reading code. The instrument is honest about its evidence. Its
defect is not dishonesty, it is **calibration**: it is confidently specific in a direction it
has not earned, and silent in the one direction where its evidence would have been decisive.

**A tool that flags 4,000 broken references must be assumed broken until proven otherwise — and
on this corpus it would have been.** 4,789 broken references in `superinstance-papers`, of which
the sharpest category was already shown to be an artifact of the tool itself. The 20.0%
`AMBIGUOUS` rate here (bare basenames, "exists in 69 repos") is the same disease at 1/60th the
scale: **the tool is confident and specific, and wrong, about which file a name denotes.**

**Recommended disposition: do not use its output as evidence of a defect on this corpus until
the `OPERANDS` format-lock and the symbol fallback are fixed.** The five fixes in §5 are small;
the one that matters most is the regex, because until it is fixed the instrument reports
"numerically sound" over a document containing a false constant that two passing tests certify.

---

## 8. To unblock Lane 2

`export CLOUDFLARE_TOKEN=...` (or point me at a file path) into a future session, and the rest
is mechanical: `cf_d1_readonly.py` is written, gate-tested, and read-only by construction, and
`d1_claim_baseline.json` holds the expected side of the diff — 84 tables, 501 columns, keyed to
5 resolvable UUIDs plus 1 unresolvable. First run should be `SELECT name, type, sql FROM
sqlite_master` per database, deduplicating by UUID per §3.2, and reporting
`INACCESSIBLE` separately from `EMPTY` per §1.
