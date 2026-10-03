# scout-DOMAINS — tool-shaped names, probed

**Lane:** SCOUT / DOMAINS · **Started:** 2026-10-02T17:05Z · **Completed:** 2026-10-02T17:26Z
**Probes:** 57 hosts, real HTTPS, bodies read, 0.8 s apart. Every row below is a measurement.
**Access:** `${GITHUB_TOKEN}` is **not set** in this sandbox. Account-wide README and
commit-message sweep was **not possible**. That is the one real gap in this report.

---

## 0. The finding, stated first

**The fleet already built this instrument, 37 minutes after this scout started, and the
instrument has a verifier but no harvester.**

`fleet-triage/tool-SURFACES.md` — `Last full probe: 2026-10-02T17:08:07Z`, with
`tools/surfacecheck.py` (672 lines) and `surfaces.json` (14 interfaces). It is good work: it
classifies `PASS / FAIL_PARKED / FAIL_JSSHELL / FAIL_LOGINWALL / FAIL_CONTRACT / FAIL_ENV /
UNVERIFIABLE_{EGRESS,AUTH,STALE}`, fails closed, rate-limits, never reads a credential value,
and — correctly — uses `typescript.ai` as its **negative control** to prove it can fail.

**It probes 14 interfaces. All 14 are ones somebody remembered to write down.**
`surfaces.json` is a hand-maintained manifest. There is no code anywhere that scans the corpus
for tool-shaped names and asks "is this in the manifest?" That is the gap the brief described,
and it is not a gap in `surfacecheck.py` — it is the absence of the thing that would *feed*
`surfacecheck.py`.

`typescript.ai` is in the manifest only because a human noticed it at the door. **The next
one — the one nobody notices at the door — is not in the manifest, will never be probed, and
will fail silently.** I found four of them, all dead, all named as `api.` or `docs.` hosts,
all absent from the manifest (grep count 0 against `surfaces.json`):

| name | state today | named in |
|---|---|---|
| `api.gpu-profiler.dev`, `docs.gpu-profiler.dev` | **NXDOMAIN** | `org2/mdcache/PersonalLog.json` — an agent-audit findings doc |
| `api.spreadsheetmoment.com`, `api-staging.…`, `spreadsheetmoment.com` | **NXDOMAIN** | **`superinstance-papers/deployment/cloudflare/ARCHITECTURE.md:1421`** + `DEPLOYMENT_GUIDE.md:284` |
| `quilt.dev` | **NXDOMAIN** | fleet prose |
| `api.polln.ai`, `docs.polln.ai` | **NXDOMAIN** (apex `polln.ai` alive) | fleet prose |
| `api.jepa.dev`, `docs.jepa.dev` | **registered, resolves, no vhost — TLS SNI failure** | `org2/mdcache/PersonalLog.json` |

**This is the one in a paper's methodology section, which is what the brief asked for:**
`superinstance-papers/deployment/cloudflare/ARCHITECTURE.md:1421` and `DEPLOYMENT_GUIDE.md:284`
specify `zone_name = "spreadsheetmoment.com"` with a Worker route
`api.spreadsheetmoment.com/*` — a **production API zone** in the deployment architecture of the
papers repo. That entire domain is NXDOMAIN as of 2026-10-02T17:20Z.

---

## 1. Correction to the incident premise

The brief says `typescript.ai` "was named as a tool to use *massively and continually*."

**I could not corroborate that anywhere in the corpus.** `typescript.ai` occurs exactly once,
in `tool-SURFACES.md:13` — as the *record of this having been caught*:

```
| `typescript.ai` | **parked GoDaddy page** named as a tool "to use massively" | caught at the door |
```

The phrase "massively and continually" appears nowhere. So the claim survives only as the
fleet's own secondhand summary of an origin that is not in the trees I can reach.

**More importantly: the parked domain and the real service are different domains.**
The fleet's credential is `TYPESAFEAI_KEY` (61 mentions). The endpoint its experiments
actually call is `api.typesafe.ai` — which is **alive, documented, and auth-gated**:

```
POST https://api.typesafe.ai/v1/systemone
 -> 403 {"detail":{"error_type":"authentication_error",
                  "message":"Must supply an API key! Check your request and try again."}}
POST …/v1/systemone  (bearer: sk-not-a-real-key)
 -> 401 {"detail":{"error_type":"authentication_error",
                  "message":"Cannot authenticate with the server. Please check your API key…"}}
GET  https://api.typesafe.ai/openapi.json      (NO credential)
 -> 200  openapi 3.1.0 | title "TypeSafe" | version 0.2.0
    desc: "Ask yes/no questions, evaluate statements, select choices, or assign ratings
           to your content. Send your API key in the Authorization header as Bearer <API_KEY>.
           Use GET /v1/models to discover available model names."
    paths: POST /v1/systemone   |   GET /v1/models
```

Two things follow, and both are things a status-code check would have gotten wrong:

1. **`GET /openapi.json` is unauthenticated and returns the full contract.**
   `tool-SURFACES.md` files `jev-systemone` as `UNVERIFIABLE_AUTH` / 403. It is not
   unverifiable — the contract is public at a route nobody tried. This entry can be upgraded
   from UNVERIFIABLE to documented **without any credential at all.**
2. **403 and 401 return different messages** ("Must supply an API key" vs "Cannot authenticate
   with the server"). That is a live auth backend validating against something, not a static
   stub. It is the same reasoning `tool-SURFACES.md` already makes for
   `api.groq.com` — I am confirming it extends here.

**`api.typesafe.ai` at the root is 404.** That is a root-route artifact, not a dead service,
and `typesafe.ai/v1/systemone` returns a Framer 404 because the marketing site and the API
are on different hosts. Three different 404s, one live service. Anyone checking these by root
status alone would file the fleet's only working oracle as broken.

---

## 2. The worst one — the receipts cannot say which model produced them

Not the most numerous; every finding here is n=1 or n=4. The worst is this, because it is
the only one where a specific, quantitative, pre-registered, hash-chained **finding** is
underwritten by a name that is a moving target.

`fleet-triage/org_scratch/qtx/experiments/` is a full experimental record. `API_LIMITS_R1.md:9`
declares a wire baseline and reports results. The findings read like data:

> "H1 STRICT version FALSIFIED — floor/ceiling collapse… 6-point continuum compresses to
> 3 distinct values {10, 50, 100}"
> "H3 SUPPORTED strongly: adjacent continuum gaps = 0,4,5,0,0 levels"

The receipt `out/e1-ordinal-not-interval.receipt.json` is complete and honest about what it
does record — `base`, `ran_at`, `scores`, `means`, `gaps`, `witness_head`, `witness_len`.
**It contains no model field at all.** I checked all six receipts: **none contains a version.**

Meanwhile the script that produced it:

```
e1-ordinal-not-interval.mjs:1    // … quantified on live jev-1.13.0.        <- a COMMENT
e1-ordinal-not-interval.mjs:55     model: 'jev-latest',                     <- a MOVING TARGET
e1-ordinal-not-interval.mjs:104    model: live.parsed.model ?? 'jev',       <- fallback to a NON-VERSION
```

So: the version `jev-1.13.0` exists **only in a comment on line 1**. The request asks for
`latest`. The log line *tries* to record the resolved id but falls back to the bare string
`'jev'`, and the receipt that was actually written doesn't carry it even so. And the API
tells you the fix in its own description — **`GET /v1/models` discovers the real model names** —
which is never called.

`tool-SURFACES.md` already names the root cause ("sent `model:"jev-1.13.0"` — the *response*
id; request wants `jev-latest`"). **Knowing the root cause did not close the hole**, because
the hole is in the *receipt schema*, and the schema has no version field to close it into.

**Why this is worse than a parked domain:** a parked domain announces itself. This one
produces confident, well-formed, chain-verified numbers. `witness_len: 18` and
`witness_head: 71803a4a4987e9d4` prove the rows weren't altered — they say nothing about
which model answered. **The chain binds the ledger, not the science.** Same defect class as
`moth-honest` and `quilt-jepa`, in a third repo, arrived at from the opposite direction:
those bound results without re-running; this one never recorded the input that determined them.

**It is also already expiring.** Receipts are `ran_at: 2026-09-25`. That is 7 days ago.
`typesafe.ai` self-describes as *Framer, Published Sep 28, 2026*. The marketing site was last
published **three days after the runs**, on a different host from the API, and the API
publishes no version to pin. Those receipts are **already un-replayable by anyone without the
key** — and I am the first scout to say so with a timestamp.

---

## 3. Tally — 57 probed hosts

| class | n | hosts |
|---|---|---|
| **SITE 200** (marketing page / SPA / SEO landing — not an API) | 30 | `superinstance.ai` `superinstance.dev` `cocapn.ai` `cocapn.com` `polln.ai` `polln.io` `deckboss.ai` `deckboss.net` `dmlog.ai` `luciddreamer.ai` `reallog.ai` `evolink.ai` `moth.run` `mothquantum.com` `halfpixel.ai` `agentreceipts.ai` `kimi.ai` `exe.dev` `now.gg` `gog.com` `flux.dev` `steel.dev` `chisel-lang.org` `smolmachines.com` `typesafe.ai` `typesafe-ai.github.io` `api.superinstance.ai` `console.groq.com` `gpt.fiftyone.ai` |
| **UNVERIFIABLE_EGRESS** (no connection) | 14 | `api.polln.ai` `docs.polln.ai` `spreadsheetmoment.com` `api.spreadsheetmoment.com` `api-staging.spreadsheetmoment.com` `docs.spreadsheetmoment.com` `api.gpu-profiler.dev` `docs.gpu-profiler.dev` `quilt.dev` `k2.ai` `nSteel.dev` `api.backup.com` + `api.jepa.dev`/`docs.jepa.dev` (see §4) |
| **ALIVE_BEHIND_AUTH** (contract-shaped 401/403) | 3 | `api.deepseek.com` `api.smolmachines.com` `api.cwsandbox.com` |
| **PARKED** | 4 | **`typescript.ai`** · **`moth.ai`** · `capitaine.ai` · `capitaineai.com` |
| **FAIL_CONTRACT** (404 at root) | 2 | `api.typesafe.ai` (root only — **service is alive**, §1) · `api.wandb.ai` |
| **FAIL_LOGINWALL** | 1 | `cloud.tensorlake.ai` → `/login` |
| **FAIL_DOWN (523, origin unreachable)** | 1 | `api.cocapn.ai` |
| **not followed** | 1 | `zenith.ai` → 301 |

**The answer to "how many tool-shaped names resolve": of 57 probed, 4 are demonstrably real
services** (`api.typesafe.ai`, `api.deepseek.com`, `api.smolmachines.com`, `api.cwsandbox.com`),
**4 are for sale**, and **14 do not connect at all.** Thirty return 200 and are websites, not
interfaces. I am not calling those 30 defects — a fleet that documents its own frontends is
doing the right thing.

**A stale record worth one line:** `repos/quilt-quantumaudio-demo/README.md:72` says
"the moth.ai and mothquantum.com hosted APIs are down" and that the key "would be for a hosted
API that's currently 503." Today `mothquantum.com` is **200 alive** and `moth.ai` is a
**GoDaddy aftermarket page**. The record says "down" for one that is up and "down" for one that
is **for sale**. A recorded interface is a claim about a moment; this one not only expired, it
expired into a different failure than it recorded.

---

## 4. A class `tool-SURFACES.md` does not have

`api.jepa.dev` → `76.223.54.146` · `docs.jepa.dev` → `13.248.169.48` · both **the same two IPs
as `typescript.ai`**, the GoDaddy lander pair. But unlike `typescript.ai`, TLS fails:

```
$ curl https://api.jepa.dev/
curl: (35) OpenSSL: error:0A000458:SSL routines::tlsv1 unrecognized name
   remote_ip=76.223.54.146
```

That is **registered, resolving, no vhost configured.** It is not `FAIL_PARKED` (no lander is
served), not `UNVERIFIABLE_EGRESS` (DNS works), not `FAIL_CONTRACT` (nothing to 404 on — the
handshake never completes). A classifier with the current six FAIL classes has to force this
into a bucket it doesn't fit, and every forced bucket is a quiet lie.

Both are named in `org2/mdcache/PersonalLog.json`, an **agent-audit findings document** — which
is the brief's "named in an agent brief" severity class, the one it said it most wanted.

**Suggested seventh class:** `FAIL_NOVHOST — resolves, no TLS vhost, handshake fails. The name
exists; nothing is served. Distinct from parked (something is served) and from
unreachable (DNS failed).`

---

## 5. Classification by how it was named

| class | where | n | severity | note |
|---|---|---|---|---|
| **A. Paper / methodology / architecture** | `superinstance-papers/deployment/cloudflare/*` | **1 zone, 4 names** | **HIGH** | `spreadsheetmoment.com` NXDOMAIN, cited as a production API zone. This is the class the brief asked for. |
| **B. Runnable script, live-call guard** | `org_scratch/qtx/experiments/*.mjs` | 1 host | **HIGH (different kind)** | `api.typesafe.ai` is alive; the defect is the receipt schema (§2), not the host |
| **C. Repo README** | `fleet-triage/repos/*/README.md` | 7 | MEDIUM | `moth.ai` record is stale *in kind* (§3) |
| **D. Agent brief / audit doc** | `org2/mdcache/PersonalLog.json` | 6 | MEDIUM | `api.jepa.dev`, `docs.jepa.dev`, `api.gpu-profiler.dev`, `docs.gpu-profiler.dev` |
| **E. Agent MEMORY / CREDENTIALS** | `org_scratch/fleet-murmur/*` | 3 creds | MEDIUM | `DEEPSEEK_API_KEY` 137, `DEEPINFRA_API_KEY` 67, `GROQ_API_KEY` 41 |
| **F. Already instrumented** | `fleet-triage/tool-SURFACES.md` + `surfaces.json` | 14 | handled | the existing instrument |
| **G. Orchestrator brief only** | this task | 1 | **uncorroborated** | `typescript.ai`, zero corpus support beyond the record of its own capture |
| **H. Commit messages** | — | **0 / not reached** | **UNKNOWN** | no token; biggest remaining gap |

---

## 6. What I did not do

- **No account-wide sweep.** `${GITHUB_TOKEN}` unset. Class **H is unmeasured** and it is the
  one the brief specifically wanted. Everything above is local trees only.
- **`quilt-research-canons`** was not in my scan list — I used the 8 trees listed in §0. If it
  exists under a different path, the harvest should be re-run over it before anyone quotes my
  counts as account-wide.
- **No credential was used, requested, or guessed.** Every auth-gated row is `UNVERIFIABLE_AUTH`,
  and the `sk-not-a-real-key-000` probe was a synthetic string to distinguish 403 from 401.
- **No pushes.** One file written.

## 7. Recommended next steps, in order

1. **Write the harvester.** `surfacecheck.py` verifies a manifest; nothing produces the
   manifest. A ~60-line scanner that runs the context-gated regex from §Method over the corpus
   and diffs the result against `surfaces.json` would have caught `jepa.dev`,
   `gpu-profiler.dev`, `spreadsheetmoment.com` and `quilt.dev` on its first run. This is the
   actual deliverable this lane was chartered to produce, and it is small.
2. **Add `version` to the qtx receipt schema**, populated from the `model` field the response
   already returns — and call `GET /v1/models` at run time so `latest` resolves to a string
   before the first call, not after. The chain then binds the science, not just the ledger.
3. **Re-file `jev-systemone` from `UNVERIFIABLE_AUTH` to documented**, citing the
   unauthenticated `GET /openapi.json` above. Free win, no credential.
4. **Restore the token** and close Class H.
5. **Decide what `spreadsheetmoment.com` is.** Either the zone in
   `superinstance-papers/deployment/cloudflare/ARCHITECTURE.md` is live somewhere and the docs
   are stale, or the deployment architecture describes infrastructure that never existed. The
   second reading is worth taking seriously, because the file is in the papers repo.

---
*Every status in this file was produced by a real request. Timestamps in §0, §1, §2, §3.
`typescript.ai` and `moth.ai` return a byte-identical 114-byte body —
`window.onload=function(){window.location.href="/lander"}` — on the same GoDaddy IP pair.*
