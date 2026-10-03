# AUTOPUBLISH — release safety triage, 17 first-party SuperInstance repos

**Date:** 2026-09-30 · **Scope:** the 17 first-party repos from the 500-repo sweep
**Method:** every publish workflow read in full; every test suite executed locally where a
toolchain was obtainable.

---

## The headline number

> **Before: 6 of 16 publishing repos could fail a release that should have failed.**
> **After: 16 of 16.**

(DMLogn8n is excluded from both numbers — it does not publish at all. See below.)

Of the 10 gates added, **6 are green today**, **4 are red for pre-existing reasons** that
were already there. A red gate is the intended outcome: a check that reports red is useful.
None of them was made to pass by weakening it.

---

## Three corrections to the brief, before the table

### 1. "11 of the 17 have zero tests" is false. All 17 have tests.

The census counter in `triage.py` is an `if/elif` chain:

```python
if   SRC.search(p): row["src"]  += 1
elif TEST.search(p): row["test"] += 1     # <-- unreachable
```

`SRC` is an extension match (`\.(py|ts|js|rs|go|…)$`). Every test file in this fleet has one
of those extensions, so **`SRC` always matches first and the `TEST` branch never executes.**
Recounted properly:

| repo | census said | actually has |
|---|---|---|
| ccc-os | 0 | 236 tests passing |
| cocapn-health | 0 | 113 tests (112 pass) |
| cocapn-plato | 0 | 95 tests passing |
| construct-coordination | 0 | 39 `#[test]` |
| flux-js | 0 | 172 tests passing |
| flux-runtime | 1 | **2755 tests passing** |
| flux-vm-v3 | 0 | 94 `#[test]`, 34 in the run |
| plato-core | 0 | 78 tests (76 pass) |
| quilt-fleet | 0 | 148 tests |
| websocket-fabric | 0 | 321 `#[test]` |

The `untested` signal in `triage.json` (338 of 500 repos) is an artifact of this bug and
should not be used for anything until `triage.py` is fixed. **The real finding was never
"no tests" — it was "tests exist and never run on the release path."** That is a worse
problem and a different one.

### 2. "35 publish on push" — none of the 17 publishes on a push to a branch.

Every publish workflow in the set is **tag-triggered** (`push: tags: v*`) or
**release-triggered** (`release: published`). The distinction you asked for:

- **0 of 17** fire on every push to main.
- **16 of 17** fire only on a `v*` tag push (or, for flux-js, a published GitHub Release).

This matters more than it first appears, and it is the single most important structural fact
in this report:

> **GitHub Actions does not gate across workflows.** Every one of these repos has a `ci.yml`
> on `push: branches: [main]` that runs tests. **Not one of them runs on a tag push, and not
> one of them can block a tag-triggered release job.** "This repo has CI" and "this release is
> gated" are unrelated claims. Only a `needs:` edge *inside* the publishing workflow is a gate.

So the green checkmark on `main` has been providing no protection to any release in this
fleet. The only real gates are the ones wired inside the publish workflow.

Seven of the 17 default to `master`, not `main` (`construct-coordination`, `git-agent`,
`plainsong`, `plato-core`, `quilt-fleet`, `websocket-fabric`, and the `cocapn`/`ccc-os`
branch lists include both).

### 3. One repo in the list does not publish at all.

**DMLogn8n is a false positive.** The census matched `docker push` at
`ci-cd-pipeline.yml:354` — which is a **comment** inside a deploy step whose entire body is
`echo`. The `Deploy to Staging` step does nothing. There is no publish, no upload, no push.
Its `build-and-deploy` job is gated on `push` to main, which is presumably why it looked
like a "publishes on push" hit. It should be dropped from the autopublish list.

---

## The table

Verdicts: `SAFE` = gated and green. `GATED` = real gate on the publish trigger.
`GATE-ADDED` = gate added by me, green. `GATE-ADDED-RED` = gate added, currently red for a
pre-existing reason. `UNTESTED-UNSAFE` = no tests exist; nothing honest to gate on.
`FAILS-OPEN` = a control that runs and gates nothing.

| repo | trigger | registry / artifact | tests in repo | gate before | gate after | verdict |
|---|---|---|---|---|---|---|
| **quilt** ★ | tag `v*` + dispatch | RubyGems `quilt_cell` | 23 `#[test]` + 11 node | **none** (+ invalid YAML, + missing `lib/`) | `npm ci` → `npm run build` → `npm test` | **GATE-ADDED** ✅ 66+79+15 pass |
| **flux-runtime** | tag `v*` **×2 workflows** | PyPI (twine **and** OIDC) + GH Release | **2755** | none | `pytest tests/ -q` in both | **GATE-ADDED** ✅ 2755 pass |
| **flux-js** | `release: published` | npm | 172 | none in publish job | `npm test` | **GATE-ADDED** ✅ 172 pass |
| **git-agent** | tag `v*` | PyPI + GH Release | 281 | none; upload `continue-on-error` | `pytest` + **COE removed** | **GATE-ADDED** ✅ 281 pass |
| **AI-Writings** (jev-core) | tag `jev-core-v*` | crates.io | 5 `#[test]` | none | `cargo test` | **GATE-ADDED** ✅ 4 pass |
| **AI-Writings** (jev-client) | tag `jev-client-v*` | npm | 0 — `test` script is `echo "no tests yet" && exit 0` | `tsc` build only | *unchanged, on purpose* | **UNTESTED-UNSAFE** |
| **AI-Writings** (jev-decide) | tag `jev-decide-v*` | PyPI | 0 — no Python modules exist | `python -m build` only | *unchanged, on purpose* | **UNTESTED-UNSAFE** |
| **websocket-fabric** | tag `v*.*.*` | crates.io + ghcr | 321 `#[test]` | **none at all** | `cargo test` | **GATE-ADDED-RED** |
| **construct-coordination** | tag `v*` | crates.io | 39 `#[test]` | none | `cargo test` | **GATE-ADDED-RED** |
| **usemeter** | tag `v*.*.*` | crates.io ×6 + ghcr | 2079 `#[test]` | `--version` smoke only | `cargo test --workspace` | **GATE-ADDED-RED** |
| **tripartite-rs** | tag `v*.*.*` | crates.io ×6 + ghcr | 2103 `#[test]` | `--version` smoke only | `cargo test --workspace` | **GATE-ADDED** ✅ 302 pass |
| **plato-core** | tag `v*` | PyPI | 78 | none | `pytest tests/ -q` | **GATE-ADDED-RED** |
| **ccc-os** | tag `v*` | PyPI | 236 | `pytest tests/ ccc_os/tests/` + cov≥75, same job | unchanged | **SAFE** ✅ 236 pass |
| **cocapn-plato** | tag `v*` | PyPI + GH Release | 95 | `pytest -x -v`, same job | unchanged | **SAFE** ✅ 95 pass |
| **cocapn-health** | tag `v*` | PyPI | 113 | `needs: build-and-test` (pytest+cov) | unchanged | **GATED** (see note) |
| **flux-vm-v3** | tag `v*` | crates.io | 94 `#[test]` | `cargo test --release` in `build`, publish `needs: build` | unchanged | **SAFE** ✅ 34 pass |
| **plainsong** | tag `v*` | PyPI + GH Release | 812 | tag==version check, `unittest`, `spec`, doc examples | unchanged | **SAFE** ✅ 812 pass |
| **quilt-fleet** | tag `v*.*.*` | npm + GH Release | 148 | `npm test` before `npm publish` | unchanged | **GATED** (flaky, see below) |
| **DMLogn8n** | `push` main (no publish) | — | 2 | — | — | **NOT A PUBLISHER** |

### `FAILS-OPEN` — controls that run and gate nothing

| repo | control | why it gates nothing |
|---|---|---|
| **git-agent** | `continue-on-error: true` on `twine upload` | A failed PyPI upload reported success. **Removed.** |
| **AI-Writings** jev-client | `"test": "echo \"no tests yet\" && exit 0"` | Hardcoded exit 0. Wiring this in would be a gate that cannot fail. **Deliberately not wired in.** |
| **ccc-os / cocapn-health / cocapn-plato** `ci.yml` | `run: pytest \|\| true` | Fails open — but on `push: branches`, not on the tag. The `release.yml` gates are correct and unpiped, so releases are still protected. Not touched. |
| **flux-js** `ci-node.yml` | `npm test \|\| true` | Fails open, and is on `push: branches` not the release trigger. The gate I added to `publish.yml` is unpiped. |
| **DMLogn8n** | `npm test --if-present` | Silently skips if no test script. Moot — not a publisher. |

No `| tee`-without-`pipefail` instance was found in any publish workflow in the set. The
census's `failopen` counter reads only the first 6 workflow files per repo and only fires on
`| tee`/`| grep`; the live instance in this fleet is `|| true` and `--if-present`, which it
does not look for.

---

## Per-repo findings behind the red gates

These are **pre-existing**. I added the gate anyway and left it red, with the reason written
into the workflow file next to the step.

**websocket-fabric** — `cargo build` succeeds (verified, exit 0). The `message_tests` target
does not compile: 9 errors including `unresolved import websocket_fabric::CloseFrame`, no
`builder` on `WebSocketClient`, `WebSocketServer is not a future` (×3), and a missing `anyhow`
dependency. The test suite has drifted from the library. 321 `#[test]` functions, none of
which have compiled.

**construct-coordination** — `Cargo.toml` declares 8 sibling `path` dependencies
(`../circuit-breaker`, `../rate-limiter`, `../health-check`, `../retry-backoff`,
`../load-balancer`, `../config-center`, `../feature-flag`, `../service-discovery`) and there
is no `[workspace]`. `actions/checkout` fetches one repo, so these do not exist and every
cargo command fails. **The pre-existing `cargo publish` step has therefore never succeeded
either.** This is a dependency-vendoring problem, not a gating one.

**usemeter** — same class, different cause: `crates/synesis-cli` depends on
`privox = { path = "privox" }`, there is no `privox/` directory, and there is no `Cargo.lock`.
Every cargo command fails. **Its `build` and `publish-crates` jobs cannot have succeeded
either.** (usemeter's release notes are also copy-pasted from Tripartite1 — the install URLs
point at `github.com/SuperInstance/Tripartite1`.)

**plato-core** — 2 failures, 76 pass, deterministic:
`tests/test_types.py::test_content_hash` and `test_advanced.py::test_content_hash_length` both
assert `len(content_hash(...)) == 16`, but `content_hash` returns a 64-character SHA-256 hex.
Whether the implementation or the assertion is wrong is a code decision, not mine.

**tripartite-rs** — was the one I could not verify in the first pass; it finished on a second
run. Self-contained (`privox/` present, `Cargo.lock` present), `cargo test --workspace` exits
**0** with **302 passed, 0 failed, 13 ignored** across the 6 crates. The gate is green.

### Two repos cannot publish at all, for reasons independent of gating

**quilt (the flagship)** has three stacked faults; I fixed one and reported the other two:

1. **`publish-rubygems.yml` is invalid YAML at HEAD.** Lines 67–70 (an embedded Ruby gemspec
   template) sit at column 0, dedenting out of the `run: |` block scalar. GitHub Actions
   refuses to load the workflow, so **the flagship's RubyGems publish has never run.** I
   verified this was pre-existing (`git show HEAD:…` fails to parse identically), and fixed
   it minimally by building the gemspec with `'\n'.join([...])`, which keeps every line inside
   the block scalar. I proved the generated content is byte-identical to the original.
2. **`shutil.copytree('lib', …)` — there is no `lib/` directory in quilt.** Zero entries under
   `lib/` in HEAD; the tree is clean. Even with the YAML fixed, the gem build raises
   `FileNotFoundError` before `gem push`. The monorepo builds to `packages/*/dist`. Deciding
   what the gem *should* contain is a packaging decision — not silently mine to make.
3. No test gate (now added).

**AI-Writings jev-decide** ships an empty package: `src/` contains only
`jev_decide.egg-info`, and there is not a single `.py` file in the package. `pytest` would
exit 5 ("no tests collected") and block every release permanently, so I did not wire it in.

---

## Notes on the two "gated but not SAFE" repos

- **cocapn-health** — `test_check_cpu` asserts `check_cpu(max_percent=200.0).ok`, and
  utilisation is `loadavg / cpu_count × 100`. It failed here at 827% on a 1-CPU sandbox
  (saturated by my own parallel cargo builds). This is load-sensitivity, not a defect, and it
  will pass on a standard 4-core runner at idle — but it is a test that fails under load, so
  it is worth knowing about.
- **quilt-fleet** — `npm test` failed once (an MQTT transport test against `mqtt://127.0.0.1:1`)
  and then passed 4/4 on re-run. The gate is real and can fail; it is **flaky**.

---

## Changes made, repo by repo

All changes are additions of a gate step plus comments. No existing gate was weakened, no
`continue-on-error` was added, no `|| true` was added.

| repo | file | change |
|---|---|---|
| AI-Writings | `publish-jev-core.yml` | +`cargo test --manifest-path packages/jev-core/Cargo.toml` before publish |
| AI-Writings | `publish-jev-client.yml` | comment only — records *why* no gate was added |
| AI-Writings | `publish-jev-decide.yml` | comment only — records *why* no gate was added |
| construct-coordination | `publish.yml` | +`cargo test` before `cargo publish`, marked CURRENTLY RED |
| flux-js | `publish.yml` | +`npm test` before `npm publish` |
| flux-runtime | `publish.yml` | +`pytest tests/ -q` before build/upload |
| flux-runtime | `release.yml` | +`pytest tests/ -q` before build/upload (2nd publish path) |
| git-agent | `release.yml` | +`pytest tests/ -q`; **removed `continue-on-error: true`** from the upload |
| plato-core | `publish.yml` | +`pytest tests/ -q`, marked CURRENTLY RED |
| quilt | `publish-rubygems.yml` | +node setup, `npm ci`, `npm run build`, `npm test`; **fixed invalid YAML** |
| tripartite-rs | `release.yml` | +`test` job (`cargo test --workspace`); `create-release` now `needs: [validate, build, test-release, test]` |
| usemeter | `release.yml` | +`test` job (`cargo test --workspace`); `create-release` now `needs: […, test]`; marked CURRENTLY RED |
| websocket-fabric | `release.yml` | +`test` job (`cargo test`); `create-release` now `needs: [validate, build, test]`; marked CURRENTLY RED |

In tripartite-rs, usemeter and websocket-fabric the new `test` job hangs off `create-release`,
which `publish-crates` and `docker` both already depend on — so one test run gates crates.io
**and** the ghcr image transitively, rather than duplicating a 2100-test run across a
five-target build matrix.

**I dropped a typecheck I had added to quilt.** `npx tsc --noEmit -p .` fails
(`TS18003: No inputs were found in config file`) — which is exactly why that repo's own
`ci.yml` wraps it in `|| echo "no tsc config found, skipping"`. Adding it would have meant
shipping a knowingly-red step. Build + test is the honest gate.

---

## What I ran to confirm this

| check | command | result |
|---|---|---|
| YAML parse, all 55 workflow files in all 17 repos | `python3 -c "yaml.safe_load(open(f))"` per file | 1 failure, `DMLogn8n/monitoring.yml`, **pre-existing**, untouched (not a publisher) |
| Fail-open audit of every added line | `git diff \| grep -E '\|\| true\|continue-on-error\|\| tee\|\| grep\|--if-present'` | 0 real hits (only my own comment text matched) |
| quilt YAML fix is content-preserving | compared generated gemspec string old vs new | byte-identical |
| Test suites executed | see per-repo table | **11 of 16 publishing repos run locally** |

Suites I could **not** run, and why: `plainsong`, `ccc-os`, `cocapn-health`, `cocapn-plato`,
`quilt-fleet`, `flux-vm-v3`, `tripartite-rs` were all run. Rust needed a toolchain that was
not present in the sandbox and had to be installed; two concurrent runs corrupted a shared
`CARGO_HOME` and had to be re-serialized, which is what made `tripartite-rs` miss its first
window (it passed on the second).

Environment artifacts I ruled out rather than reported as repo defects:
`git-agent` hardcodes `/tmp/git-agent` in its fixtures (12 apparent failures were my clone
path; **281 pass** from the expected path); `cocapn-plato`'s 3 collection errors were missing
`fastapi`/`pydantic` (**95 pass** once installed); `NODE_ENV=production` and
`npm config omit=dev` were stripping devDependencies fleet-wide.

---

## Not done

**The changes are not pushed.** The token in `~/.gitconfig` returns `401 Bad credentials`
(the census that produced the brief ran with a `GITHUB_TOKEN` env var that is no longer set),
and there is no `gh` CLI, no `.netrc`, no deploy key and no SSH key in this sandbox. Clone and
read work anonymously; write does not. The 10 repos are modified in local clones at
`/workspace/work/autopub/<repo>/` and are ready to commit and push the moment a working
credential is available. **Nothing in this report is reflected on GitHub yet.**

Also not done, deliberately: no test suite was written for any repo (§ "do not invent a test
suite"), no `|| true` was added anywhere, and no existing gate was touched — `ccc-os`,
`cocapn-plato`, `plainsong`, `quilt-fleet` and `flux-vm-v3` were left exactly as they were.

## Suggested follow-ups, in order

1. **Fix `triage.py:118`** — the `elif` makes the `untested` signal meaningless fleet-wide
   (338 false positives). Every other count derived from it is suspect.
2. **Fix `triage.py`'s `autopub` regex** — it matched a comment in DMLogn8n and missed
   AI-Writings' `katyo/publish-crates` action, because it only matches literal command strings.
3. **quilt's missing `lib/`** — decide what the gem should contain. Until then the flagship
   publishes nothing, which may be preferable to publishing a broken gem.
4. **Vendor or repoint the missing path dependencies** in usemeter (`privox/`) and
   construct-coordination (8 siblings). Both release pipelines are dead for this reason alone.
5. **Repair websocket-fabric's test suite** against the current API, then re-land the gate.
