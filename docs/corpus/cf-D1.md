# CF-D1 — 44 D1 databases, account `049ff5e84ecf636b53b162cbb580aae6`

**Lane 44. Status: BLOCKED ON CREDENTIAL — still 0 of 44 databases read.**
Re-verified 2026-10-01 20:20 UTC under the corrected variable name. The correction did not change
the outcome, and the reason why is the interesting part. See §0.2.

---

## 0. The blocker, restated after the re-check

### 0.1 The credential is still not in this session

The brief corrected the variable name to `CLOUDFLARE_TOKEN`. I checked that name first, then swept
for the credential everywhere the sandbox could plausibly hold one. It is not there.

| Location searched | Result |
|---|---|
| `CLOUDFLARE_TOKEN` (the name in the brief) | **unset** — `len: 0` |
| `CLOUDFLARE_API_TOKEN`, `CF_API_TOKEN` | unset |
| Full `os.environ` — **all 29 names printed** | no Cloudflare var under any spelling |
| `/proc/1/environ` (the Pod env, the sandbox's source of truth) | 29 names, same set, no CF var |
| **Every** `/proc/[0-9]*/environ`, all 5 live PIDs | zero matches for `cloudflare` / `^CF_` / `token` / `secret` / `key` except `CLOUD_RUNTIME_GIT_SHA` |
| `/etc/profile.d/acs_env.sh` — where this sandbox persists injected env vars | **does not exist**; `/etc/profile.d/` is empty |
| `ENVD_DIR` = `/mnt/envd`, `run_with_envs.sh`, `sandbox-runtime-storage` | binaries + the sync script only; no secret material |
| `/run/agent-helper`, `/run/agent-runtime`, `/run/e2b` | empty or a 5-byte sandbox marker |
| `.mavis/` (agent runtime state) | plans and memory only; no secret store, and no `mavis` binary on `PATH` |
| `*.env` / `.env*` anywhere under `/workspace` | none |
| `/workspace/.wrangler/` | `cache/pages.json`, `cache/wrangler-account.json` — **no token** |
| Files modified in the last 60 min under `/workspace` | **none** — no credential file was dropped for me |
| `git log --all -S CLOUDFLARE` in fleet-triage | zero hits; never committed, correctly |

`/workspace/.wrangler/cache/wrangler-account.json` still confirms the account ID and that wrangler
was authenticated here on 2026-09-16 → 09-22. It carries no token.

### 0.2 Why "wrong variable name" and "no token" are indistinguishable from the 400s

This is the part worth recording, because it is a trap in the diagnostic method rather than a fact
about Cloudflare.

Running the brief's snippet verbatim, with no `Authorization` header at all:

```
GET /user/tokens/verify
400 {"success":false,"errors":[{"code":1001,"message":"Missing \"Authorization\" header"}]}
```

A *missing* variable name and an *absent* credential produce **byte-identical failures**, because
`os.environ["CLOUDFLARE_TOKEN"]` on an unset name and `os.environ["CLOUDFLARE_API_TOKEN"]` on an
unset name are the same event. So the `400`s I reported are fully consistent with either hypothesis
and **cannot discriminate between them**. The orchestrator's read — "you were looking for a name
that does not exist" — is a *sufficient* explanation of the 400s, but it is not the only one, and
it was not testable from the response.

The thing that *does* discriminate is the environment dump, and it is unambiguous: 29 variables,
none of them Cloudflare's, in this process and in PID 1's. The network is fine (Cloudflare answers
in 400ms); the account ID is right; the credential is not in this session.

**I am not disputing that the variable name may have been wrong.** I am reporting that fixing the
name did not unblock the lane, because the variable is not present under any name.

**To unblock:** `export CLOUDFLARE_TOKEN=...` into this session, or write it to a file inside
`/workspace` and give me the path — `cf_d1_readonly.py --token-file PATH` takes it directly.

### 0.3 Coverage — read this before any table below

- **Databases inventoried: 0 of 44.** Not "inspected and found empty" — never reached.
- **Databases schema-inspected: 0 of 44.**
- **Empty: unknown — 0 confirmed.**
- **Inaccessible: 0 confirmed.** Nothing was refused; nothing was reachable. "Could not attempt"
  is a different bucket from "attempted and was denied", and only the first applies.
- **Repo-side D1 census: re-run, now automated** (§2). 39 declaration lines, 12 distinct names,
  13 distinct `database_id` values.
- **Live facts established from local artifacts: 1** (§4) — one database confirmed to exist and
  accept a query, with a quoted `200`.

**No claim in this document is about a live database, except the one in §4, which is quoted.**

---

## 1. What changed in this pass

I could not read the databases, so I spent the pass on the work that does not need the token, and
delivered it rather than idling:

1. **Wrote the audit harness** (`cf_d1_readonly.py`, §3) — complete, self-tested, and it enforces
   read-only in code with two independent gates.
2. **Caught a hole in my own read-only gate** via its selftest (§3.2) before it could run against
   a real account. This is the second time in this lane that a self-test earned its keep.
3. **Replaced the hand-written repo census with a machine one** (§2) — and it immediately found
   two declarations the manual pass had missed.
4. **Mined the wrangler logs for live-account evidence** (§4) — recovered one database's real UUID
   and a confirmed `200 OK`.

---

## 2. Repo-side D1 census — DONE, no API required

`cf_d1_readonly.py::repo_side_declarations()` walks `/workspace` for `wrangler.{toml,json,jsonc}`
and parses every `database_name` / `database_id` / `preview_database_id`. This replaces the grep in
the previous revision of this file, which is why the numbers moved.

```
39 declaration lines · 12 distinct database_name · 20 id lines (13 distinct values) ·
8 of 20 id lines cannot address a real database
```

| Database name | Declared `database_id` | Declaring repo | UUID is real? |
|---|---|---|---|
| `superinstance` | `""` (empty) | `Tripartite1/cloud/wrangler.toml:51` | **no** |
| `superinstance-db` | `"superinstance-db-id"` | `superinstance-papers/website/functions/wrangler.toml:28` | **no** |
| `superinstance-db` (preview) | `"superinstance-db-preview-id"` | same file, `:29` | **no** |
| `spreadsheet_moment_db` | `"your-database-id-here"` | `superinstance-papers/.../workers/wrangler.toml:25` | **no** |
| `ai-writings` | `"YOUR_D1_DATABASE_ID"` | `research/lanes/shelf/AI-Writings/site/api-worker/wrangler.toml:9` | **no** |
| `duke-lab-db` | `00000000-0000-0000-0000-000000000000` | `repos/duke-lab/worker/wrangler.toml:26` | **no — nil UUID** |
| `quilt-fleet-db` | `19d1d2f3-d6ef-48bb-9475-253f303bfb37` | `fleet-static-host`, `rc-20260824-01` | uuid-shaped |
| `mist-lab-db` | `c720fb84-09d1-4cf7-98f6-c0ed2daa7337` | `mist-lab`, `recovered-copy-20260824-mist-lab` | uuid-shaped |
| `mist-quilt-db` | `9ee7851b-4bb4-4847-b0e8-eacc0ceeaba3` | `mist-quilt`, `recovered-copy-…` | uuid-shaped |
| `scrap-quilt-db` | `0e4399b7-9acc-4a16-aa5b-dd7b6ac31e3a` | `scrap-quilt`, `recovered-copy-…` | uuid-shaped |
| `scrap-voice-db` | `601b91c0-3228-49f7-be36-26f258e9b4be` | `scrap-voice`, `recovered-copy-…` | uuid-shaped |
| `quilt-canon` | `801f84bf-9c12-4d91-8f55-873eb5d69f9f` | `research/cargo-line-tycoon/cloudflare-stack/wrangler.toml:23` | **confirmed live — §4** |
| `plainsong` | `bb0cbc42-0397-4052-9299-cd423fe7113d` | `work/autopub/plainsong/worker/wrangler.jsonc:21` | uuid-shaped |

### 2.1 Correction to the previous revision of this file

The earlier version of this document said *"three of the twelve carry a non-UUID placeholder."*
The automated census says **7 of the 20 `database_id` lines cannot address a real database, plus
1 nil UUID**:

| Non-functional ID | Lines | Where |
|---|---|---|
| `""` (empty string) | 3 | `Tripartite1/cloud/wrangler.toml:54`, `work/autopub/tripartite-rs/cloud/wrangler.toml:54`, `work/autopub/usemeter/cloud/wrangler.toml:54` |
| `"your-database-id-here"` | 1 | `superinstance-papers/spreadsheet-moment/workers/wrangler.toml:28` |
| `"superinstance-db-id"` | 1 | `superinstance-papers/website/functions/wrangler.toml:28` |
| `"superinstance-db-preview-id"` | 1 | same file, `:29` |
| `"YOUR_D1_DATABASE_ID"` | 1 | `research/lanes/shelf/AI-Writings/site/api-worker/wrangler.toml:9` |
| `00000000-0000-0000-0000-000000000000` (nil UUID) | 1 | `repos/duke-lab/worker/wrangler.toml:26` |

The earlier count of three came from reading only the `database_id` key by hand and skipping
`preview_database_id` and the three empty-string cases. **8 of 20 id lines are unusable; 12 are
UUID-shaped**, of which 1 is nil and 1 (`quilt-canon`, §4) is confirmed live.

The nil UUID deserves its own line because it is a different failure from a placeholder string.
It is well-formed: it passes any "is this a UUID?" validation, so a linter or a reviewer sees a
real ID. It is carrying the comment `# ← replace after \`wrangler d1 create\``, which means the
author knew it was unset. `wrangler d1 create` was never run for `duke-lab-db`, so **that database
has most likely never existed** — the one repo-side claim I can state as a strong hypothesis
without the API, and the harness will confirm it in one `COUNT(*)` against a 404.

### 2.2 Orphan signal — names the brief cites that no repo declares

| Named live in brief | Declared by any repo? |
|---|---|
| `superinstance-db` | yes — but with placeholder IDs, so never deployed |
| `quilt-edge-lab` | **no match** |
| `i2i-ledger` | **no match** |
| `quilt-db` | **no match** — the fleet declares `quilt-fleet-db` and `quilt-canon`; plain `quilt-db` is a distinct name |

**Still a hypothesis, not a finding.** The census covers `/workspace` but a D1 binding declared in
another file type, or in a repo not cloned here, would not appear. Only the live list settles it,
and I do not have the live list.

---

## 3. The harness — `cf_d1_readonly.py`, delivered and self-tested

Complete and ready. One command, the moment a token exists:

```bash
export CLOUDFLARE_TOKEN=...
python3 cf_d1_readonly.py            # full audit → cf_d1_audit.json
python3 cf_d1_readonly.py --dry-run  # prints the plan, makes no network call
python3 cf_d1_readonly.py --selftest # proves the read-only gates fire
```

It does exactly the order in the brief: `GET /d1/database?per_page=100` for all 44 with `uuid`,
`created_at`, `file_size`, `num_tables`, `version`; then per database
`SELECT type,name,tbl_name,sql FROM sqlite_master` (the single query that yields every table, its
verbatim DDL, and its views); then `SELECT COUNT(*)` per user table; then `PRAGMA table_info`,
`index_list`, `foreign_key_list`. Output is JSON, joinable against the §2 census to produce
`orphans_live_no_repo`, `repo_refs_missing_db`, and `repo_ids_not_in_account` in one pass.

### 3.1 Read-only is enforced in code, not by intention

Two independent gates, as the brief required — "assert that in your code rather than trusting
yourself":

1. **`assert_readonly_sql()`** — every statement must begin with `SELECT` / `PRAGMA` / `WITH` after
   leading whitespace *and comments* are stripped, so `-- x\nDROP TABLE t` cannot smuggle a write
   past a prefix check. The `PRAGMA` case carries an extra rule (§3.2).
2. **`api()`** — refuses every verb but `GET`, with a single exception: `POST` to
   `/d1/database/{uuid}/query`, and only with SQL that passed gate 1. There is no code path to
   `/execute`, to a migration endpoint, or to any write verb anywhere in the file.

The token is never logged. Runs record `sha256:<6hex>/len<n>` so two runs can be shown to have
used the same credential without disclosing it.

### 3.2 The selftest caught a real hole in my own gate

`PRAGMA` has a mutating assignment form. `PRAGMA writable_schema=ON` is a **write** that sails
straight through a naive `startswith("PRAGMA")` check — the check I wrote first. The selftest
failed on it, I tightened the gate to reject the `PRAGMA x=value` assignment form, and it now
passes. Had I shipped the harness on the strength of "I only ever write SELECTs", that hole would
have sat in a file whose entire purpose is to be the thing that cannot write.

```
$ python3 cf_d1_readonly.py --selftest
  ALLOW  'SELECT 1' / '  select name from sqlite_master' / '-- a comment\nPRAGMA table_info(t)'
  ALLOW  '/* c */ WITH x AS (SELECT 1) SELECT * FROM x'
  BLOCK  DROP TABLE / DELETE / INSERT / UPDATE / CREATE TABLE / ATTACH DATABASE
  BLOCK  'PRAGMA writable_schema=ON'   <-- the catch
  BLOCK  VACUUM / '--x\nDROP TABLE t' / ''
  Gate 2: BLOCK POST-with-write-sql, BLOCK POST /execute, ALLOW POST /query
  selftest OK
```

---

## 4. One live fact, recovered from the wrangler logs

I do not have the credential, but `/workspace/.home/.config/.wrangler/logs/` (439 files,
2026-09-16 → 2026-10-01) contains wrangler's own debug record of CF API calls. Quoted:

```
--- 2026-09-22T04:45:04.858Z log
🌀 Executing on remote database quilt-canon (801f84bf-9c12-4d91-8f55-873eb5d69f9f):

--- 2026-09-22T04:45:04.861Z debug
-- START CF API REQUEST: POST https://api.cloudflare.com/client/v4/accounts/
   049ff5e84ecf636b53b162cbb580aae6/d1/database/801f84bf-9c12-4d91-8f55-873eb5d69f9f/query

--- 2026-09-22T04:45:05.283Z debug
-- START CF API RESPONSE: OK 200
```

**Established, not inferred:** database `801f84bf-9c12-4d91-8f55-873eb5d69f9f`, named
`quilt-canon`, existed in this account on 2026-09-22 and accepted a `d1 execute --remote` query,
returning HTTP 200. That resolves the real UUID for `quilt-canon`, which the repo census had only
as a bare ID, and it is a control for the 6 uuid-shaped IDs: at least one of them is genuine.

**Scope limit, stated plainly:** the SQL text is withheld by wrangler
(`QUERY STRING: omitted; set WRANGLER_LOG_SANITIZE=false`) and the logs contain **no**
`d1 create` / `d1 delete` / `d1 list` events. So this establishes *one* database's existence, not
its schema, and not the fate of the other 43. It is a single data point, and I am not going to
inflate it into a census.

---

## 5. Orphans, both directions — current state

| Direction | Count | Detail |
|---|---|---|
| Live DB with no repo | **unknown (0 of 44 reachable)** | hypotheses: `quilt-edge-lab`, `i2i-ledger`, `quilt-db` (§2.2) |
| Repo referencing a DB that does not exist | **≥ 1, strongly indicated** | `duke-lab-db` holds a nil UUID with a "replace after `wrangler d1 create`" comment (§2.1) |
| Repo with a non-deployable binding | **8 of 20 id lines** | 7 non-UUID + 1 nil UUID (§2.1) |
| Confirmed live and queryable | **1** | `quilt-canon` — §4 |

The first row needs the inventory. The second row is a hypothesis that survives on repo evidence
alone but is not yet confirmed against the account — I will mark it confirmed or kill it the
moment the query endpoint answers.

---

## 6. Standing constraints

- **No writes, no pushes, no migrations.** Nothing in this lane will mutate a database or a repo.
- The token is treated as read-only regardless of its actual scopes. Two repos have already been
  clobbered tonight by assuming a target was free; a destructive migration on a live edge database
  is the same error with a worse blast radius. If a change looks needed, I will describe it and stop.
- No secret values are written to this file or anything derived from it. The wrangler log quotes in
  §4 contain no headers and no query text — wrangler omits both by default.

---

## 7. Interim conclusions

1. **The databases remain uninspected, and the reason is unchanged: no credential.** I have read
   zero of the 44. The account ID is confirmed, the network is confirmed, the API is confirmed to
   answer — and the bearer token is in neither this process's environment nor PID 1's.

2. **Naming one database as "the one that contradicts its repo" remains something I will not do.**
   I still have not read a single schema. The repo side supports a dozen hypotheses and the live
   side would settle them; the discipline this lane exists to enforce is refusing to promote the
   first one to a finding just because it is well-formed and checkable-looking.

3. **What I can say without the API is now more specific than it was.** One database
   (`quilt-canon`) is confirmed real from a quoted `200`. One repo binding (`duke-lab-db`) points
   at a nil UUID and has probably never been deployed. Six bindings carry IDs that cannot deploy.
   The previous revision's "three placeholders" was an undercount: a hand read of one config key
   missed `preview_database_id`, three empty-string IDs, and a nil UUID that passes UUID validation.

4. **The harness is done and tested; the remaining gap is exactly one variable.** The moment
   `CLOUDFLARE_TOKEN` exists in this session, `python3 cf_d1_readonly.py` produces the full
   inventory, per-database DDL quoted from `sqlite_master`, row counts, and the two-directional
   orphan join. No further work stands between the credential and the 44.

---

*Live inspection pending credential. Repo-side census automated. One live fact recovered from
local logs. Nothing was written to Cloudflare, to any database, or to any repository.*
