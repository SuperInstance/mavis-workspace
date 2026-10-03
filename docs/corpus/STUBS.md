# Fleet triage — the ten "empty" repos

**Task:** Wave 2. Read every file in ten low-blob-count `SuperInstance` repos, determine what each
actually is, and find out whether anything depends on it.
**Date:** 2026-09-30 23:36–00:20 UTC
**Doctrine:** read-and-report. Nothing was deleted, archived, created, or pushed.

---

## ⚠️ Two things to read before the table

**1. `GITHUB_TOKEN` was not in the environment.** The task brief said it would be. It was not
(`env | grep -i github` → empty; no `gh` CLI). Everything below was gathered **unauthenticated**,
against a 60 req/hr core limit and a 10 req/min search limit. A revoked `ghp_…` token exists in
`~/.gitconfig`'s `insteadOf` rewrite; I did not use it, and Wave 1's `fetch_readmes.py` records
that credential as revoked.

**2. GitHub code search is unavailable unauthenticated.** `GET /search/code` returns
**HTTP 401 "Requires authentication"**. So **I could not search the fleet's source code** for
references. Every "no references" cell below means *no references in the corpora I could actually
read* — not "nothing references it anywhere". This is the distinction the task rules demand, and
it is why the reference column is qualified rather than binary.

### Reference-search coverage (state this next to any zero)

| Corpus | Coverage | How searched |
|---|---|---|
| `fleet_meta.json` (names + descriptions + topics) | **5,092 / 5,108 = 100%** of live fleet | full scan |
| `readmes/` README bodies | **4,835 files** | full-text grep |
| `/workspace/repos` full clones | **177 repos** | full-text grep |
| Org issue/PR titles+bodies | all repos | `search/issues` API |
| **Source code across the fleet** | **0%** | ❌ **HTTP 401 — not done** |

> The README corpus grew from 1,018 → 4,835 files *during this session* (a background fetch was
> still landing). I re-measured before trusting any zero, and every grep below ran against 4,835.

---

## The table

| # | Repo | What is actually in it | Who references it | Disposition | Evidence |
|---|---|---|---|---|---|
| 1 | **privox** | **Nothing.** Zero commits, zero refs, zero blobs. Not a stub file — an initialised repo that was never written to. | **8 repos cite it as a working Rust crate**, incl. `knowledge-vault` which *ships* `examples/with_privox.rs` calling `privox::{PatternSet, PrivacyRedactor}`. `privox` **does not exist on crates.io** (404). | 🔴 **BROKEN PROMISE** — highest priority. Empty *and* load-bearing. | `git ls-remote` → zero refs. crates.io → `crate 'privox' does not exist`. 8 READMEs cite it. 0★ 0🍴 0👁 |
| 2 | **agent-priming** | Default `main`: **175-byte README**. **`master`: 8,459 B incl. a 7,980-byte `PRIMER.md`** ("The Mechanic Doctrine"). Unrelated histories. | `agent-priming-toolkit`, `agent-priming-toolkit-pkg`, `quilt-live-canon-pypi` | 🟠 **NOT EMPTY — real content stranded on non-default `master`.** Also superseded (its own `master` README says "legacy, see toolkit") and its advertised endpoint is 404. | `main`=1 blob/175 B; `master`=2 blobs/8,459 B. `git merge-base` → **NONE (unrelated histories)**. `/api/agent-priming` → **404** |
| 3 | **agent-priming-toolkit** | Default `main`: **158-byte README**. **`master`: 11 files / 35,795 B** — `payloads/schema.json` (6,298 B), `docs/DESIGN.md`, `docs/STREAMING.md`, 3 client examples, 3 job profiles (NIL/MAK/RUN), manifest. Unrelated histories. | `agent-priming-toolkit-pkg`, `quilt-live-canon-pypi` | 🟠 **NOT EMPTY — the realest artifact of the three, hidden on `master`.** But its contract points at a **dead API**: `schema.json` has a **required `"const"` field** = `…/api/agent/schema` → **404**, as do all 4 documented layers. | `main`=1 blob/158 B; `master`=11 blobs/35,795 B. `merge-base` → NONE. `/api/agent/{manifest,tools,doctrine,context}` all **404** |
| 4 | **algebra-explorer** | Default `main`: **151-byte README**. **`master`: a working 22,730-byte single-file HTML demo** (`index.html`, 9 `onclick`/`addEventListener` handlers, full CSS). Unrelated histories. | **Nothing.** 0 in 4,835 READMEs, 177 clones, 100% of descriptions/topics, 0 issues | 🟡 **NOT EMPTY — a finished demo on the wrong branch, with zero readers.** | `main`=1 blob/151 B; `master`=1 blob/22,730 B. `merge-base` → NONE |
| 5 | **starter-shell** | 3 files / 2,411 B: README, `bin/starter-shell.js` (831 B), `package.json`. A thin npm wrapper that shells out to a Python CLI. | **Published**: `@superinstance/starter-shell@0.1.1` on npm, `starter-shell` on PyPI. Referenced by closed issue [forgemaster#5 "Publish starter-shell to npm"](https://github.com/SuperInstance/forgemaster/issues/5) | 🟡 **Real and published, but `main` is broken.** `package.json` sets `"main": "index.js"` — **`index.js` is in neither the repo nor the published tarball**, so `require()` throws. `"test": "echo …"` is a no-op. | Downloaded the real tarball: `package/{README.md,bin/starter-shell.js,package.json}` — `index.js` **absent**. 1★ |
| 6 | **edge-native-paper** | 3 files: `PAPER.md` (2,271 B), README (475 B), LICENSE. **7 commits**, plus 2 side branches whose README is *longer* (1,427 B). A fork of `Lucineer/edge-native-paper`. | [`SuperInstance/Edge-Native` PR #3](https://github.com/SuperInstance/Edge-Native/pull/3); `quilt-jev-toolkit/JEV_FLEET_GATE.md` (scored 0.08) and `FLEET_GATE_RESULTS.md`; `the-fleet` | 🟢 **NOT A STUB — a small but complete paper**, and third-party work (Cocapn/Lucineer), not fleet work. `PAPER.md` already self-flags its unverifiable claims with 🔮. | 7 commits; `fork=true`, `parent=Lucineer/edge-native-paper`; 1★; 0 open issues |
| 7 | **Hunyuan3D-WorldClaw** | **Zero-delta mirror.** 4 blobs: README + 2 JPEGs (6.98 MB). All 3 commits are upstream authors (Season-sweet Orange, Yang Li, LongHZ140516) — **no SuperInstance commit at all.** | **Nothing** found | ⚪ **MIRROR/BOOKMARK — not a stub.** 4/4 blobs **byte-identical** to `Tencent-Hunyuan/Hunyuan3D-WorldClaw`; **0 commits not in parent**. The 180,845 KB API size is inherited git history, not content. | blob-SHA comparison against parent clone: 4 identical, 0 differing. `fork=true` |
| 8 | **AutoData-old** | **Zero-delta mirror.** 5 blobs: 145-byte README, `pyproject.toml`, LICENSE, `.gitignore`, and a **0-byte** `.env.example`. All 8 commits are upstream authors. | **Nothing** found | ⚪ **MIRROR + correct archive pointer — not a stub.** README says source moved to `Tianyi-Billy-Ma/AutoData`; that repo **does have 121 blobs incl. full `autodata/agents/*.py`** → **the promise is met.** 100,203 KB is history bloat (a `benchmark.tar.gz` that upstream deleted). | 5/5 blobs byte-identical to `GraphResearcher/AutoData`; 0 extra commits. Note the fork parent is `GraphResearcher/AutoData` but the README links `Tianyi-Billy-Ma/AutoData` (same author, two accounts) |
| 9 | **si-variational-bayes** | 5 blobs / 57,771 B: **`src/lib.rs` = 39,466 B**, 16,656-byte README, `Cargo.toml`, LICENSE. A genuine Rust crate (ELBO, mean-field, Gaussian families, natural gradient, BBVI, fleet VI). | **Nothing** found | 🟢 **NOT A STUB — a real crate.** But its test claims are internally inconsistent and **unverified**: commit says "40 tests, all passing", README badge says "32+ passing". I counted **40 `#[test]` attributes** (structurally real) but **could not run them — no `cargo` in this sandbox.** | `#[test]` count = 40, `mod tests` at `src/lib.rs:719`. `cargo: command not found`. 0★ |
| 10 | **loom-caching-rollout** | 5 blobs: 336-line shell script, README, `.conf.example`, LICENSE, `.gitignore`. Bot-generated 2026-06-15. | Listed in the `education` catalog: `education/assets/repos.json` and `education/crates/index.html` | 🟠 **NOT A STUB, but its headline safety feature is a stub.** README advertises "🚨 Automatic rollback on error rate or latency thresholds"; `rollback_instance()` has the real command **commented out** and replaced with `sleep 1  # Simulate rollback delay`. (File locking *is* genuinely implemented — symlink-create + `trap release_lock EXIT`.) | `loom-caching-rollout.sh:153-159`. Commit `17019e5` "Bot-generated … [bot-generated]" |

---

## What is in each repo, file by file

Ground truth from `git clone --filter=blob:none` (zero API cost), not from the API tree endpoint.

| Repo | Default | Branches | Commits | Files on default branch |
|---|---|---|---|---|
| `privox` | — | **none** | **0** | **none — no refs exist at all** |
| `agent-priming` | `main` | `main`, `master` | 1 / 3 | `README.md` 175 B — *`master` adds* `PRIMER.md` 7,980 B |
| `agent-priming-toolkit` | `main` | `main`, `master` | 1 / 1 | `README.md` 158 B — *`master` adds* 10 files, 35,637 B |
| `algebra-explorer` | `main` | `main`, `master` | 1 / 1 | `README.md` 151 B — *`master` adds* `index.html` 22,730 B |
| `starter-shell` | `main` | `main` | 1 | `README.md` 616, `bin/starter-shell.js` 831, `package.json` 964 |
| `edge-native-paper` | `master` | +2 | 7 | `PAPER.md` 2,271, `README.md` 475, `LICENSE` 1,069 |
| `Hunyuan3D-WorldClaw` | `main` | `main` | 3 | `README.md` 1,333, 2 JPEGs (6.98 MB) |
| `AutoData-old` | `main` | `main` | 8 | `README.md` 145, `pyproject.toml` 1,936, `LICENSE` 1,078, `.gitignore` 3,737, `.env.example` **0** |
| `si-variational-bayes` | `master` | `master` | 3 | `src/lib.rs` **39,466**, `README.md` 16,656, `Cargo.toml` 535, `LICENSE`, `.gitignore` |
| `loom-caching-rollout` | `main` | `main` | 3 | `loom-caching-rollout.sh` 10,783, `README.md` 4,680, `LICENSE`, `.conf.example` 649, `.gitignore` 21 |

**Stars / forks / watchers / open issues — all ten, all fetched successfully:**

| Repo | ⭐ | 🍴 | 👁 | Open issues | Archived |
|---|---|---|---|---|---|
| `starter-shell` | 1 | 0 | 0 | 0 | no |
| `edge-native-paper` | 1 | 0 | 0 | 0 | no |
| `AutoData-old` | 1 | 0 | 0 | 0 | no |
| the other 7 | 0 | 0 | 0 | 0 | no |

**Total across all ten: 3 stars, 0 forks, 0 watchers, 0 open issues.** No repo in this set has
community activity. So the "repo with community activity and an empty tree" scenario the brief
asked me to look for **does not exist here** — but `privox` is a worse case than that scenario,
because other fleet repos *depend* on it.

---

## The methodology bug that produced this list

Three of these repos are not empty. They have **227×, 151×, and 48× more content than the default
branch shows** — sitting on a `master` branch that nothing points at:

| Repo | What a default-branch scan sees | What is actually on `master` |
|---|---|---|
| `agent-priming` | 1 blob, 175 B | 2 blobs, **8,459 B** |
| `agent-priming-toolkit` | 1 blob, 158 B | 11 blobs, **35,795 B** |
| `algebra-explorer` | 1 blob, 151 B | 1 blob, **22,730 B** (a finished demo) |

All three pairs have **unrelated histories** (`git merge-base` → no common ancestor), so this is
not a fast-forward — `main` was initialised separately and the `F156`/`F158`/`F165` feature work
was pushed to `master`. Any census that reads only the default branch will call these stubs
forever.

---

## "What this should be" seeds

**The brief asked for a seed paragraph per *genuine stub with no references and no readers*. That
set is empty — there are zero such repos among the ten.** Three looked like stubs and turned out
to be substantial work; six are real (if small) repos, published packages, or third-party forks;
one (`privox`) is empty but heavily depended upon. Manufacturing ten seeds here would be padding.

So, only the two that genuinely need a first commit:

### `privox` — the one repo that should get a first commit

The name and topics promise a Rust crate for PII/PHI redaction in LLM pipelines
(`pii-redaction`, `privacy`, `rust`, `slice-of-life`, plus `superinstance-archive` and
`synesis-archive` — someone already half-archived it in their head). Eight fleet repos cite it as
real, `knowledge-vault` ships an example that imports `PrivacyRedactor` and `PatternSet`, and
`eventstream` advertises it as the thing that makes its event publishing GDPR/HIPAA-compliant.
The smallest honest first commit is a single `src/lib.rs` defining exactly the two types the
citing docs already name — `PatternSet` with builder methods `.with_email() .with_phone()
.with_ssn() .with_address()` and `Default`, and `PrivacyRedactor::new(PatternSet)` with
`redact(&str) -> Result<String, _>` — plus a `Cargo.toml` named `privox` v0.1.0. That is the
precise surface the eight citations already assume, so nothing has to be rewritten downstream.
Then uncomment the import in `knowledge-vault/examples/with_privox.rs` and delete the placeholder
it currently falls back to. **Ship that placeholder fix even if the crate is never written** —
see the finding below; it is a live PII leak in a published example.

### The three branch-stuck repos — no new content needed

Their first commit already exists. The honest fix is to decide which branch is canonical and
merge the other (`--allow-unrelated-histories`, or repoint the default branch), then delete
nothing. `algebra-explorer` in particular needs no authoring at all: a finished 22 KB demo is
sitting one branch-pointer away from being visible, and it currently has zero readers anywhere in
the fleet.

---

## Two findings worth escalating beyond this task

**1. `knowledge-vault/examples/with_privox.rs` does not redact anything, and says it does.**
The privox import is commented out and replaced with three `String::replace()` calls whose
arguments are *regex syntax* passed to a **literal** replace. I translated the exact code to
Python and ran it: all four PII values survive — email, phone, SSN, and street address — and the
output is printed under the heading `🔒 Redacted document (placeholder)`. A reader skimming the
output sees PII passing through a privacy tool untouched. This is the `String::replace` vs
`Regex` mistake, and it is the highest-severity item I found.

**2. The `agent-priming` family documents an API that does not exist.**
`live-canon.superinstance.dev` is up (HTTP 200, serves a 10 KB landing page) and serves a
`/api/canon/*` family — but there is **no `/api/agent*` route at all**. Every endpoint named in
these READMEs returns 404, including all four layers of the toolkit and the
`https://live-canon.superinstance.dev/api/agent/schema` URL that `payloads/schema.json` declares
as a **required `"const"` field** — so no payload in the toolkit can be validated against its own
schema. Whether the API was ever deployed, was renamed, or was lost is **UNVERIFIED**; I can only
report that as of 2026-09-30 ~23:55 UTC it is not there.

---

## Counts

- **Genuine stubs (empty, no references, no readers): 0.**
- **Referenced by something: 6** — `privox` (8 READMEs + 1 shipped example file),
  `agent-priming-toolkit` (2 repos), `agent-priming` (2 repos), `starter-shell` (npm + PyPI +
  1 closed issue), `edge-native-paper` (1 PR + 2 gate docs), `loom-caching-rollout`
  (education catalog ×2).
- **Could not determine: 1 axis, affecting 4 rows** — fleet-wide **source-code** reference
  search is **UNVERIFIED** (code search HTTP 401, no token). `algebra-explorer`,
  `Hunyuan3D-WorldClaw`, `AutoData-old`, `si-variational-bayes` show **0 references in READMEs,
  descriptions, 177 clones and issues**; I cannot claim they have none in code.
- Also **UNVERIFIED**: `si-variational-bayes`'s test-passing claim (no `cargo` in this sandbox).
- **Corrections to the incoming framing:** `privox`'s "0 blobs" was a *failed tree read* in the
  Wave 1 data (`errors: ["tree unreachable"]`) — I re-verified it as genuinely empty via
  `git ls-remote`, so that one is upgraded from UNVERIFIED to verified. Conversely `Hunyuan3D-WorldClaw`
  (180 MB) and `AutoData-old` (100 MB) are large because of **inherited git history**, not content —
  both are zero-delta mirrors whose current trees are 6.98 MB and 6.9 KB.

## Reproducing this

```bash
cd /workspace/projects/fleet-triage/stubs/clone
for r in */; do r=${r%/}; echo "── $r"
  git -C $r rev-list --count HEAD
  git -C $r ls-tree -r -l HEAD
  git -C $r branch -r --format='%(refname:short)'   # non-default branches carry the real content
done
```
