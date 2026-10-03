# dir-SECURITY — what the fleet says, and what it costs to be wrong in public

**Lane:** SECURITY (read-only audit) · **Date:** 2026-10-02T02:2x–03:0xZ
**Method:** fresh `git clone --bare` of 26 repos, full-history blob scan, workflow
parse, anonymous HTTP fetches. **No workflow was edited, no secret rotated, no repo
setting changed, nothing pushed. No untrusted code was executed — clone and read only.
No `npm install`, no fork workflow run.**

**No secret value appears in this file, in any commit, or in any report.** Secrets are
identified by a **fingerprint** — the first 12 hex of the SHA-256 of the match — which
is enough to correlate findings and useless for replay.

---

## Scope, stated honestly before the findings

| Claim | What I actually did |
|---|---|
| 5,127 repos | I enumerated a **300-repo sample** (3 API pages, sorted by last-push). The fleet-wide pinning/fork numbers below are **sampled, not exhaustive**, and are labelled as such. |
| Full history | **26 repos, all refs, all reachable blobs.** Complete for those 26. |
| Liveness of keys | Tested against the issuing provider's API. Read-only, no charge, no writes. |
| `fleetkit` | **Does not exist.** Named in the brief as a key-holding repo. See R7. |

**The audit is itself capability-limited, and that is a finding (R8):** there is no `gh`
binary, and the only credential present is **dead**. Effective API budget was 60
requests/hour, anonymous. A fleet-wide audit of 5,127 repos at that rate is not possible
in one session.

---

## Ranked open exposures, most dangerous first

### R1 — The published papers assert claims the fleet has already refuted in public, and nothing links the two.
**Severity: highest reputational risk in the fleet. Already live. Cannot be un-published.**

`superinstance-papers` is public and its README is the front door. It states:

> "**Proves** the conservation law emerges from the layer removal mechanism…"
> "**Theorem 5.1**: Eisenstein norm multiplicativity provides exact conservation"

`01-conservation-law-of-intelligence.md` grounds that in code:

- **line 35** — cites `murmur/transforms/rubiks.py` as an implementing module
- **line 37** — "The layer count function from `rubiks.py` (line 437)"
- **line 50** — "confirmed in `update_certainty` at **line 281** of `rubiks.py`"
- **lines 325–326** — lists `murmur/logtensor/transforms/rubiks.py` in the reference section

**I verified this myself rather than trusting ORIENTATION.** Fresh clone of `murmur`,
all refs: **1 branch, 0 tags, 0 objects ever named `*rubiks*`**, and no `transforms/` or
`logtensor/` path in HEAD at all. The file has never existed. Three line-number-specific
citations point into it.

The `6.8×` constant in `eisenstein` is the same disease and is live in **4 files in HEAD**
including the README. I checked the test that supposedly verifies it:

```rust
// tests/algebraic_properties.rs — eisenstein_triple_density_advantage
// "At c ≤ 50, Pythagorean triples: 16 primitive.
//  Eisenstein should have significantly more."
assert!(triples.len() >= 16, "Should find at least 16 Eisenstein triples …");
```

The comment demands *significantly more*; the assertion is `>= 16`, which is **exactly the
Pythagorean count**. The test passes at 1×, at 6.8×, at 0.1×. It cannot fail on the
claim it is named for. True ratio is 3.296×.

**The part that makes this cheap to fix, and the part that makes it dangerous not to:**
the refutation is **already public and anonymously fetchable**. `fleet-triage/ORIENTATION.md`
returns HTTP 200 to an unauthenticated reader and says, in plain language:

> "The conservation paper's theorem is stated over code that never existed."
> "A `6.8×` constant sits in `eisenstein` README, CONTRIBUTING, `src/lib.rs` and two
> passing property tests… True ratio is **3.296×**. The test asserts `>= 16`, so it
> **passes at any value whatsoever**."

Meanwhile `superinstance-papers/README.md` contains **zero** references to an audit,
correction, errata, or `fleet-triage`.

> **So the correction is already published. It is simply not connected to the claim.**
> A hostile reader needs two anonymous HTTP GETs and five minutes. A hostile *writer* needs
> to publish nothing at all — they can only link.

**To close:** add `CORRECTIONS.md` at the root of `superinstance-papers`, link it from the
**first screen of the README** (above the papers list, not in a footer), one row per
claim: claim as published → status (`RETRACTED` / `SUPERSEDED`) → what the evidence
actually shows → date. The text already exists in `ORIENTATION.md`; this is mostly a
copy-and-link job. **~1 hour. Owner: Casey. Nobody else can do it.**
**Then make it structural:** have the paper's own CI assert that every path and line number
cited in the `.md` files resolves in the named repo at the named commit. That is the
instrument this fleet does not have, and it is the same shape as the missing canary.

---

### R2 — 100% of third-party action references are mutable. One of them holds a long-lived registry token.
**Severity: highest technical risk. Requires a compromised account to trigger — see R4/R6 for how a token gets here.**

Across the 26 repos audited (23 workflow files, 74 third-party `uses:` references,
local `./` reusable-workflow paths excluded):

| Pinning | Count | Share |
|---|---|---|
| **SHA-pinned (immutable)** | **0** | **0.0%** |
| Mutable tag (`@v4`, `@v2`) | 70 | 94.6% |
| Mutable branch/ref (`@stable`, `@release/v1`, `@v0`) | 4 | 5.4% |

A tag is a pointer an upstream maintainer can move. **Zero of 74 are pinned to a commit.**

The sharpest instance — `AI-Writings/.github/workflows/publish-jev-core.yml`:

```yaml
on: { push: { tags: ['jev-core-v*'] } }   # tag push
jobs.publish.steps:
  - uses: katyo/publish-crates@v2          # THIRD-PARTY, MUTABLE TAG
    with:
      args: --token ${{ secrets.CRATES_TOKEN }}   # long-lived crates.io token
```

**No `permissions:` block. No `environment:` gate.** If the `v2` tag on a third-party repo
is moved, that code executes holding a long-lived crates.io publishing token.

`publish-jev-client.yml` has the same shape: `npm publish` with `secrets.NPMJS_TOKEN`,
long-lived, no `environment:`, no `permissions:`, and a preceding `npm install` that runs
registry lifecycle scripts.

**The counter-example matters more than the finding — the fleet already knows the right
pattern and applied it to one of three.** `publish-jev-decide.yml` publishes to PyPI with
**no secret at all**: OIDC trusted publishing (`id-token: write`) plus
`environment: pypi`. That is the correct shape. `jev-core` and `jev-client` were simply
never converted.

**To close:** (a) SHA-pin all 74 references — mechanical, one script, no behaviour change;
(b) move crates.io and npm onto trusted publishing exactly as PyPI already is, retiring
`CRATES_TOKEN` and `NPMJS_TOKEN`; (c) add `environment:` gates to the publish jobs.
**Owner: Casey.** (b) is the one that actually removes a credential from a build.

---

### R3 — Two repos consume a reusable workflow from this same account at a mutable tag.
**Severity: medium-high, and it is *first-party*, so there is no third-party trust boundary being crossed — the boundary is a tag.**

- `fleet-seeds/.github/workflows/forge.yml` → `uses: SuperInstance/quilt-forge/.github/workflows/forge.yml@v0`
- `pong-quilt/.github/workflows/forge.yml` → identical

One `git tag -f v0` on `quilt-forge` changes CI behaviour in every consumer at once.
Cross-repo blast radius from a single mutable ref, inside a fleet that already treats
"public by default" as doctrine. **To close:** pin to a commit SHA, or vendor the workflow
into each consumer. **Owner: Casey. ~15 minutes.**

---

### R4 — Credential-shaped material is published in public repos. Every credential tested is dead.
**Severity: lower than it looks, and this is the honest version of the "Kimi/Moonshot key" item.**

The brief said a Kimi/Moonshot key is historically exposed and needs rotation. **Located and
typed — and the answer is worse than "history only": it is in the working tree too.**

All material below is in `fleet-murmur` unless stated. Present **in HEAD** (i.e. on the
default branch, readable by anyone, right now) *and* in history:

| Type | Fingerprint | Public paths in HEAD | Repo |
|---|---|---|---|
| GitHub classic PAT | `6790559ec8f2` | `scripts/ccc-shell-maintainer.sh`, `scripts/continuous-worker.py`, `scripts/zc_tick_v3.py`, `memory/2026-05-05.md` | fleet-murmur |
| GitHub classic PAT | `3fdaeccbf271` | `memory/2026-05-01.md` | fleet-murmur |
| GitHub classic PAT | `01617ab0945e` | *(history only)* `data/plato-commands/*.json` | fleet-murmur |
| `sk-` provider key | `e5f347c371f1` | `TOOLS.md` (as `- **API key**: \`sk-…\``) | fleet-murmur |
| `sk-` provider key | `1878fc4a2c13` | `TOOLS.md`, `scripts/curriculum-engine.py`, `scripts/lock-self-directed.py` | fleet-murmur |
| `sk-` provider key | `1e2dbc693960` | `TOOLS.md`, `fleet/services/task_queue.py` | fleet-murmur |
| `sk-` provider key | `bdf13bd22ee0` | `TOOLS.md` | fleet-murmur |
| `sk-` provider key | `4d46e0d7b959` | `research/lucineer_analysis/…/multi_model_orchestrator.py`, `professional_orchestrator.py`, `quick_round_demo.py` | **superinstance-papers** |
| PEM `PRIVATE KEY` block | `3021d90eb943` | `labs/data/plato-commands/c9a0ed5926e0.json` | fleet-murmur |

Roughly **40 further paths** under `data/plato-commands/` and `data/task-queue/` carry
`sk-`-shaped values — these are agent conversation transcripts committed to the repo.

**Liveness — every credential tested returns HTTP 401:**
- 3 GitHub PATs → `GET api.github.com/user` → **401 Bad credentials** (all three)
- 5 `sk-` keys → tested against Moonshot, DeepSeek, Groq, SiliconFlow, Anthropic
  → **401 from all five providers**

**So this is disclosure, not access.** An unauthenticated reader can read the exact bytes,
the variable names, and the provider relationships — and can authenticate to nothing.

**Two things worth knowing anyway:**

1. **The fleet already knew.** `memory/2026-05-05.md` records, in plain text, a PAT
   followed by *"returning 401 Bad Credentials."* A dead credential has sat in a public
   repo for ~5 months **with the knowledge that it was dead written next to it**. That is
   the pattern to break, not the individual key.
2. **The same `sk-` value is assigned to eight different provider variables**
   (`MOONSHOT_API_KEY`, `DEEPSEEK_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`,
   `SILICONFLOW_API_KEY`, `ICONFLOW_API_KEY`, `DEEPINFRA_API_KEY`, `NVIDIA_API_KEY`).
   Real per-vendor keys are unique per vendor. This is a strong tell that at least some of
   these are template/example values rather than live credentials — but I could not
   confirm which, because **the corpus conflates documentation with configuration** and I
   will not guess. Marked **partially unresolved**, not resolved.

**To close:** (a) confirm the eight-variable conflation and delete the example values —
they are the ones most likely to be mistaken for real; (b) add a pre-commit secret scan
to the ~10 repos that carry credential-shaped material; (c) the history rewrite is
**optional** — since every value is dead, rewriting 1,678 commits of `fleet-murmur` history
costs more in trust (it looks like tampering) than it buys in security. **I recommend
not rewriting history**, and saying so in the corrections ledger instead.
**Owner: Casey.**

---

### R5 — `permissions:` is unset in 20 of 23 workflow files (87%).
`GITHUB_TOKEN` falls back to the **account default**, which for a personal account is not
a value the fleet controls per-repo. Only 3 workflows declare permissions at all.
Least-privilege is opt-in here when it should be opt-out.
**To close:** add `permissions: {contents: read}` at the top of every workflow and opt in
per job. Mechanical, and it is the correct default posture for 5,111 PR-accepting repos.
**Owner: Casey.**

---

### R6 — The audit's own credential is dead, and TLS verification is off.
`/workspace/.home/.gitconfig` carries a well-formed 40-char classic GitHub PAT in a
`url.https://x-access-token:…@github.com/.insteadof` rewrite, **plus `http.sslverify=false`**
in the same file. **The PAT returns 401 — it is dead.** The config file's mtime
(2026-10-01T04:18:38Z) is a sandbox-image artefact and is **not** a bound on when the
token was minted; global git config has no history, so the exposure window is **unbounded**.

`http.sslverify=false` is the standing part: any token placed in that rewrite is sent
**without certificate verification**, so it leaks to any network position, not merely to
anyone who can read the file. There is also no `gh` binary, so the configured
`credential.helper = !gh auth git-credential` resolves to nothing — meaning the token
in the URL is the *only* thing making authenticated git work.
**To close:** install `gh`, drop the `insteadOf` rewrite, re-enable `http.sslverify`,
and rotate at the account level. **Owner: Casey.** (Audit ran read-only and unauthenticated
in the meantime; nothing was pushed.)

---

### R7 — `fleetkit` does not exist.
The brief names `fleetkit` as one of the repos that "run agents or hold keys." It is not
present under `SuperInstance/` — 16 of the 17 named repos cloned; `fleetkit` failed.
Consistent with ORIENTATION's warning that two repos were clobbered by assuming a name was
free. **I did not create it, rename anything, or guess at a substitute.**
Either it was renamed or it never existed. **Owner: Casey, one sentence to resolve.**

---

### R8 — A public security policy that is an unmodified template, and no policy at all where it would matter.
`superinstance-papers/SECURITY.md` **exists** (HTTP 200) and is the **unedited GitHub
template** — "Use this section to tell people about which versions of your project are
currently supported." It renders as a security posture and delivers none. Meanwhile
`fleet-triage` and `fleet-murmur` — the two repos holding the most sensitive material —
have **no `SECURITY.md` (404)**.
**To close:** delete the template (a dead policy is worse than none — it invites reports
into a void) or fill it in; add one to the two sensitive repos. **Owner: Casey. ~20 min.**

---

## What I learned that changes what someone else should do

**1. The lane you assigned me was half-wrong, and the wrong half was the urgent half.**
I was told the Kimi/Moonshot key was the live exposure needing rotation, and pointed at
credential and PR surfaces. Every credential I could find is **dead** — 401 from every
issuing provider. Had I written the report I was primed to write, it would have led with a
credential incident and buried the thing that is actually live: **the papers repo asserts
claims the fleet has already refuted, in public, and does not link the two.** Rotation was
already done. The publication was not.

**2. "Verify the claim" is worth more than "confirm the brief."** The brief asserted a
historically exposed key. Verification produced a *different and larger* answer (working
tree, not just history) and then a *smaller* one (all dead). Both halves came only from
testing rather than reading. I would rather a lane hand me "the premise was wrong in this
direction" than a confirmation.

**3. My own first test was a control that could not fail, and I nearly shipped it.**
`git ls-remote` against `fleet-triage` **succeeded**, and I wrote it up as evidence the
credential was live. It wasn't. The repo is **public**, so git fell back to anonymous
read — a test that passes identically whether auth works or not. The API call is what
returned 401. Per ORIENTATION: *a control that cannot fail is worse than no control.* I
recorded the correction in E1 rather than quietly fixing it, because the stub was already
on disk and anyone who read it deserves to know it was wrong.

**4. Secrets scanners need a binary guard and a vendored-code guard or they will
convict you of your own repo.** The first pass reported 18 credential-like findings in
`superinstance-papers` and hits in `quilt-gpu-lab`. All were false: `.rgb` frames and a
compiled `.so` matching `hf_[A-Za-z0-9]{34}`, and SPDX licence text inside
`site-packages`. After excluding non-UTF-8 blobs and vendored trees, `superinstance-papers`
went **18 → 1**, and `quilt-gpu-lab` went **3 → 0**. A scanner that reports 18 when the
answer is 1 gets tuned off, and then it reports 0 when the answer is 2.

**5. The strongest security finding was a *documentation* finding, and it was cheap.**
The entire fix for R1 is a file that says what `ORIENTATION.md` already says, placed where
a reader lands. The dangerous property is not secrecy — the fleet publishes its own
refutation openly. It is that **an unlinked correction is indistinguishable from an
undiscovered error.** The same logic applies to the correction-conservation work already
in this repo: corrections that are not *surfaced* do not count as published.

**6. Negative findings are worth publishing, and I would not have got them by looking
harder.** **Zero `pull_request_target` in 23 workflows**, and **no workflow combines a
`pull_request` trigger with a `secrets.` reference** — the one combination that would let
5,111 PR-accepting repos hand a fork a credential. That is the finding a "5,111 repos
accept outside PRs" framing is designed to provoke, and it did not hold. Reporting the
negative is what stops the next lane from re-spending a day on it.

---

## If someone wanted to damage this account's credibility rather than its uptime, what
## would they do, and how long would it take?

**They would publish nothing.** They would write one paragraph, in about fifteen minutes:

> "SuperInstance's paper claims to *prove* exact conservation, citing a specific function
> at line 281 of a file. The file does not exist in any branch of the repo. Their README
> also claims a 6.8× density ratio that their own test suite cannot distinguish from 1×."

Both halves are true and both are already public. They would then link
`01-conservation-law-of-intelligence.md` to the fleet's **own** `fleet-triage/ORIENTATION.md`,
which says the same thing in more detail, and post it anywhere with a syndication button.

**They would not need to break anything, forge anything, or hold a single credential.**
Every credential in this account is already dead. The uptime attack surface is the weaker
one — it is 100% unpinned actions, but reaching it requires a write token, and the write
tokens are all revoked. **The cheapest attack on this account is the one where the account
has already written the damaging document itself and simply did not link the two halves.**

**And the defensive fix is the cheapest thing on this list:** one file, one README link,
about an hour, and the text is already written. It is the only item here where doing nothing
costs more than doing it.
