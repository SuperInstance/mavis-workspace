# CF-EMBED — the 401 test: your 400s are proof you HAD auth, not proof the shape was wrong

**Status: BLOCKED ON CREDENTIAL — 0 embedding calls made. But the blocker is now diagnosed, and
the diagnosis contradicts the relaunch brief in the one way that matters.**

Started 2026-10-01 20:18 UTC (relaunch). Prior stub from 18:57 UTC preserved in git history.
Sister lanes: `cf-D1.md`, `cf-TTS.md` — both started 18:57 UTC, both reached the same null result.

---

## 0. The short version

The brief says: *"The token is fine and it is in your environment as `CLOUDFLARE_TOKEN`. Your
400s were request-shape errors, not auth."*

**Half of that is right, and the right half falsifies the other half.**

I ran the decisive experiment: the same endpoint, the same model, the same valid body shape —
with **no `Authorization` header at all**, and then with **a syntactically valid but garbage
Bearer token**.

```
POST /accounts/049ff5e84ecf636b53b162cbb580aae6/ai/run/@cf/baai/bge-small-en-v1.5
body: {"text": ["connect four minimax probe"]}          <- the brief's shape, verbatim

T1: no Authorization header   -> 401  {"success":false,"errors":[{"code":10000,
                                        "message":"Authentication error"}]}
T2: garbage 40-char Bearer    -> 401  (byte-identical response)
T3: DNS api.cloudflare.com    -> 104.19.192.29, HTTPS reachable, real CF error served
```

**Cloudflare returns 401 for every auth failure, and never 400.**

Therefore: **your 400s could not have been auth failures.** A missing or wrong token cannot
produce a 400 — it produces a 401. Your session authenticated successfully and then failed schema
validation, which is exactly what you said. The shape advice in the brief is correct and I have
used it.

But the same fact runs the other way, and this is the part that changes the job:

> **You got 400s. I get 401s. The difference is not the request shape — it is that your session
> has the credential and mine does not.** The variable is not shared between us.

This is a session-propagation defect, not a request-shape defect. The fix is to re-inject
`CLOUDFLARE_TOKEN` into this agent's environment; nothing in the request needs to change.

---

## 1. The credential is absent here, verified at the pod level

Not "I looked in the wrong place" — I went to the root of the environment.

| Probe | Result |
|---|---|
| `os.environ["CLOUDFLARE_TOKEN"]` | **`KeyError`** — unset |
| `CLOUDFLARE_API_TOKEN` / `CF_API_TOKEN` | unset |
| `env` — all 28 names printed | no Cloudflare var under any spelling |
| **`/proc/1/environ` — the pod's own env, the source of truth** | 28 names, same set, **no CF var** |
| Every `/proc/[0-9]*/environ` (all live PIDs) | zero matches for `cloudflare` / `^CF_` / `token` / `secret` |
| `/etc/profile.d/` | **empty** — no `acs_env.sh` or equivalent injector |
| `/workspace/.wrangler/` | `cache/pages.json`, `cache/wrangler-account.json` — account id, **no token** |
| `*.env`, `.env*`, `.dev.vars`, `wrangler.toml` (fs-wide) | none |
| `grep -rl CLOUDFLARE_TOKEN` over `/workspace` | only **consumers** (`radio_night.py`, `generate_*.sh`, `plan.yaml`) — all read `$CLOUDFLARE_TOKEN`, none define it |
| `deploy_secrets.log` (NAS) | 0 Cloudflare mentions |
| filesystem sweep for `*token*`/`*secret*`/`*cred*` | nothing carrying a CF credential |

`/workspace/.wrangler/cache/wrangler-account.json` confirms the account id and that wrangler was
authenticated **2026-09-16 → 09-22** — so this box *did* hold a CF credential once. It does not now.

**Three independent lanes** (`cf-D1.md`, `cf-TTS.md`, this one), three separate sweeps, three
identical null results. This is not a search failure.

---

## 2. Ground truth: NOT wiped — and my rebuild does not reproduce your 25,939

The brief warned `/tmp/c4/verified_subset.txt` might be gone. `/tmp` is indeed empty.

**But the source is alive on NAS**, which `find` recovered:

```
/run/csi/mount-root/nas/eab0d61a99b6696edb3d2aff87b585e8/projects/connect4/c4_ground_truth.txt
  1,536,260 bytes · 54,166 rows · format: `mask pos value`
  (also at .../SuperInstance/connect4/ and .../prod/connect4/ and .../c4gt/)
```

So the prerequisite is **not** the risk. I rebuilt the subset anyway to de-risk the moment a token
lands. **My reconstruction keeps 1,733 rows, not 25,939** — reporting that rather than quietly
tuning until the number matched:

```
raw 54166 | pos bits >=42: 34986 | pos not subset: 0 | gravity/val-mismatch: 12458 | KEPT 1733
ply histogram: {1: 7, 2: 172, 3: 1554}
```

Two ways I over-filtered, both my error, both diagnosable once a token exists:

1. I applied the `>=42` test to **both** `mask` and `pos` (34,986 rows dropped, 64.6%). Your
   stated figure is 44.1%, which is the `pos ⊄ mask` condition — a *different* filter. I conflated them.
2. I required the immediate-win check to confirm a win whenever `value==1`, dropping 12,458 rows
   where a *reachable-but-unforced* win was misread. Too strict.

Ply histogram `{1:7, 2:172, 3:1554}` is the tell: **it contains no ply 4, 5 or 6 rows at all**,
so it cannot support the by-ply split that is the whole point of rule 1. My subset is unusable for
the experiment and should not be used. The original builder script is the missing piece — the raw
file is fine.

---

## 3. What is ready the moment a token appears

The experiment's *shape* is settled; only the credential blocks it. Recorded so the relaunch is
mechanical:

- **Endpoint** `POST /accounts/049ff5e84ecf636b53b162cbb580aae6/ai/run/{model}`
- **Model ids**, verbatim from the brief: `@cf/baai/bge-m3`, `@cf/baai/bge-small-en-v1.5`,
  `@cf/baai/bge-base-en-v1.5`, `@cf/baai/bge-large-en-v1.5`, `@cf/qwen/qwen3-embedding-0.6b`,
  `@cf/google/embeddinggemma-300m`, `@cf/pfnet/plamo-embedding-1b`
- **Transport** `run()` returning **bytes** (embeddings are float arrays, not JSON-serialisable
  as a dict) — the brief's version is correct and is what I ran
- **Debugging loop** on 400: the body names the missing required property. Do not guess names.
- **Rule 1** train plies 1–4, test plies 5–6. On a random split FNV-1a scored **0.9586** and beat
  the complete board — that is the trap.
- **Rule 2** shuffled-label control, same features, same model, **must land ~0.50**. If not, leakage.

The scientific question — *is 0.9314 a ceiling or a weak learner?* and *is 0.9202 colour-irrelevant
or saturated?* — **remains unanswered.** I have no pretrained-model numbers and will not
manufacture any.

---

## 4. Budget

| Item | Value |
|---|---|
| Successful Workers AI calls | **0** |
| Tokens consumed | **0** |
| Cost incurred | **$0.00** |
| Free tier spent | **$0.00 — none available to this session** |

Four unauthenticated probes were made (T1–T3 above) to diagnose the blocker. 401s are not billed.
The "spend the free tier" instruction cannot be honoured: the free tier is reachable only with the
credential this session does not have. I am reporting $0.00 again rather than dressing it up.

**No GitHub pushes made.**

---

## 5. The ask

One line, and the lane runs:

```bash
export CLOUDFLARE_TOKEN=<the same token whose 400s you are debugging>
```

It does not need to be in *my* shell — it needs to be in **this pod's** environment, alongside
`/proc/1`. A token injected into one agent's shell is not inherited by a sibling's sandbox, which
is the whole reason three lanes have now independently reported a null result.

Verify with the one-liner that needs no request shape at all:

```bash
python3 -c "import os;print('SET' if os.environ.get('CLOUDFLARE_TOKEN') else 'ABSENT')"
```

**`SET` → I run the by-ply split, the shuffled-label control, and the 0.9314 / 0.9202 comparison
against all seven embedding models, and report the exact model id behind every number.**
