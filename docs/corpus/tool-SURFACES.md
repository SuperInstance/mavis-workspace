# tool-SURFACES — every external interface this project depends on, probed live

**Last full probe: 2026-10-02T17:08:07Z.** Machine-readable twin: [`surfaces.json`](surfaces.json).
Checker: [`tools/surfacecheck.py`](tools/surfacecheck.py) — stdlib only, in the shape of `fleetset/fleetlint`.

> A recorded interface is a claim about a moment, and the moment expires.
> Three expired in one session on 2026-10-02. This file is the part that gets re-probed.

---

## Why

| interface | how it failed | cost |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | docs named it; the real variable is `CLOUDFLARE_TOKEN` | 3 lanes died guessing |
| JEV `POST /v1/systemone` | sent `model:"jev-1.13.0"` — the **response** id; request wants `jev-latest` | ~1 h blaming a "rotted contract" |
| `typescript.ai` | **parked GoDaddy page** named as a tool to "use massively" | caught at the door |

The failure is identical in all three: **a record that was true once and was never re-checked.**

## How to read a row

| verdict | meaning |
|---|---|
| `PASS` | probed live today; contract-shaped evidence returned |
| `FAIL_PARKED` | the domain is **for sale**. It is not a tool. |
| `FAIL_JSSHELL` | `200 OK` but the body is a redirect stub — **not** a working service |
| `FAIL_LOGINWALL` | public resource demanding a login |
| `FAIL_CONTRACT` | host is alive, **the path is gone** or the contract changed |
| `UNVERIFIABLE_AUTH` | endpoint proven **ALIVE**, contract unconfirmable — no credential here |
| `UNVERIFIABLE_EGRESS` | cannot reach it from this box. **Not a pass.** |

**`UNVERIFIABLE` is never counted as `PASS`.** It is printed, dated, and left visible.

---

## 1. Verified today — 6

Probed live 2026-10-02, all returning substantive content.

| interface | endpoint | auth | env var (name only) | evidence |
|---|---|---|---|---|
| `github-api` | `https://api.github.com` | bearer | `NPM_TOKEN`, `GITHUB_TOKEN` | 200, 2262 B JSON |
| `purplepincher-root` | `https://purplepincher.org` | none | — | 200, 33 379 B |
| `cocapn` | `https://cocapn.ai` | none | — | 200, 22 574 B |
| `superinstance-ai` | `https://superinstance.ai` | none | — | 200, 1 644 B, real nav |
| `discord-polln-invite` | `https://discord.gg/polln` | none | — | 200 → `discord.com/invite/polln` |
| `yaml-spec` | `https://eemeli.org/yaml/` | none | — | 200, 217 225 B |

`superinstance.ai` is only 1.6 KB and is **not** a shell: it is hand-written HTML with
substantive nav links. Compared against `typescript.ai`, whose 114-byte 200 *is* a shell.
**Size alone does not decide it — the JS-redirect probe does.**

## 2. Failed — 2

### `typescript-ai` — `FAIL_PARKED` (this is the negative control)

```
GET https://typescript.ai            -> 200, 114 bytes
   <script>window.onload=function(){window.location.href="/lander"}</script>
GET https://typescript.ai/lander     -> 200 (urllib follows the 307)
   final: https://forsale.godaddy.com/forsale/typescript.ai
          ?utm_source=TDFS_DASLNC&utm_medium=parkedpages&...
```

> **This is the trap that nearly fooled me too.** The root returns **HTTP 200**.
> A status-code checker passes it. `curl -L` does *not* even follow it, because the
> redirect is **JavaScript**, not a `Location:` header. The parking is one hop down.

### `purplepincher-connect` — `FAIL_CONTRACT` (a *different* failure)

`https://purplepincher.org/connect` → `404 Not found` (9 bytes) — while the **host root
is 200 and healthy**. Named in ~50 documents. This is a third distinct state: not parked,
not unreachable, not a shell. **The host is fine; the recorded path is a lie.**

## 3. Unverified — 18 (NOT "working")

**12 env vars + 6 endpoints.** Zero credentials exist in this environment (28 vars total,
none matching), so no authenticated contract can be confirmed here.

| interface | endpoint | status | the evidence that it is *alive* |
|---|---|---|---|
| `jev-systemone` | `api.typesafe.ai/v1/systemone` | 403 | `{"detail":{"error_type":"authentication_error",...}}` |
| `deepseek-chat` | `api.deepseek.com/chat/completions` | 401 | `Authentication Fails (governor)` |
| `groq-chat` | `api.groq.com/openai/v1/chat/completions` | 401 | `{"error":{"code":"invalid_api_key",...}}` — OpenAI-shaped |
| `siliconflow-chat` | `api.siliconflow.com/v1/chat/completions` | 401 | `{"code":30014,"message":"Token is invalid."}` |
| `deepinfra-chat` | `api.deepinfra.com/v1/openai/chat/completions` | 401 | `{"error":{"code":"invalid_api_key",...}}` |
| `cloudflare-token-verify` | `api.cloudflare.com/client/v4/user/tokens/verify` | 400 | `{"success":false,"errors":[{"code":1001,"message":"Missing \"Authorization\" header"}]}` |

**Why a 401/403 is better evidence than a 200:** the error body is *shaped like the API's
own contract*. That proves the endpoint exists and speaks its language. `GET` on
`api.deepinfra.com` returns `404`, and on `api.groq.com` returns `404` too — but `POST`
returns a contract-shaped `401`. **A 404 from the wrong method is not a dead path.** The
checker probes with the method recorded in the manifest for exactly this reason.

**Missing env vars, named not valued** (never recorded, only reported):
`TYPESAFEAI_KEY` · `DEEPSEEK_API_KEY` · `DEEPSEEK_KEY` · `DEEPSEEK_TOKEN` · `DEEPSEEK_BASE_URL` ·
`GROQ_API_KEY` · `GROQ_KEY` · `GROQ_URL` · `NPM_TOKEN` · `GITHUB_TOKEN` ·
`CLOUDFLARE_TOKEN` · `CLOUDFLARE_ACCOUNT_ID`

## 4. The Cloudflare variable, in full

The inventory records **`CLOUDFLARE_TOKEN`**. Across the repo, `CLOUDFLARE_API_TOKEN`
appears **122 times** and is the name in the docs. That mismatch is the whole
"three lanes died" incident: the docs were not wrong about the *service*, only about
the *name of the variable pointing at it*. Note the correct name is confirmed by the
provider's own error (`Missing "Authorization" header`), not by a doc.

---

## The checker

```bash
python3 tools/surfacecheck.py                      # probe everything; exit 1 on any FAIL
python3 tools/surfacecheck.py --negative-control   # prove it can fail
python3 tools/surfacecheck.py --self-test           # 12 offline classifier tests
python3 tools/surfacecheck.py --no-network         # env checks only, no egress
python3 tools/surfacecheck.py --json               # CI-consumable
python3 tools/surfacecheck.py --require-env        # absent var = FAIL_ENV, not UNVERIFIABLE
```

**Exit `0`** = no hard failures (unverified interfaces do *not* clear it of its label).
**Exit `1`** = at least one interface no longer resolves. That is a build failure.

Design choices that matter:

- **Fails closed.** A DNS failure, a timeout, an unexpected exception — all
  `UNVERIFIABLE`. Nothing reaches `PASS` without positive evidence of content.
- **Rate-limited.** ≥1.5 s between requests to the same host; results cached on disk so
  re-runs cost nothing. It will not be the reason a provider blocks this IP.
- **No credential is ever read, printed, or stored.** Only `os.environ` membership is
  tested (`present: true/false`). Values never enter the table or the cache.
- **Parking is checked *before* the status code**, because a parked page also returns 200.
- **JS redirects are followed by hand.** `curl -L` does not follow them; neither does a
  naive linter. This is the difference between `FAIL_JSSHELL` and `FAIL_PARKED`.

### The negative control — run 2026-10-02T17:08Z

```
$ python3 tools/surfacecheck.py --negative-control
  [PARKED] NEGATIVE-CONTROL-typescript.ai
           https://typescript.ai
           HTTP 200  114B  57ms
           -> HTTP 200 JS shell -> https://typescript.ai/lander -> HTTP 200 ->
              https://forsale.godaddy.com/forsale/typescript.ai?...
              THE DOMAIN IS FOR SALE. A status-code check passed it because the
              shell answers 200.

  VERIFIED 0 | UNVERIFIED 0 | FAILED 1
  CONTROL HOLDS: the checker FAILED a parked domain (FAIL_PARKED).
```

**A linter that has never failed is a canary that cannot fail.** This one has been made to
fail, on a domain that is provably parked, and the evidence is the literal
`forsale.godaddy.com` string. Every `PASS` it prints is a `PASS` from a checker with a
demonstrated failure mode.

### Self-test — 12/12, offline

`parked · js-shell · js-shell-into-godaddy · contract-shaped 401 · contract-shaped 403 ·
405-is-alive · 404-path-gone · dns-dead · timeout-is-not-a-pass · empty-200-shell ·
real-content · login-wall`

## Today's result

```
VERIFIED     6
UNVERIFIED  18
FAILED       2
```

Six verified, eighteen honestly unlabelled, two caught. **The eighteen are the point** —
they are the ones a "just check the docs" pass would have reported as working.
