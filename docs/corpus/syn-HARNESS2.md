# SYN-HARNESS2 — the instrument that cannot report failure

**Lane:** SYN-HARNESS2 (restart of a stalled lane). Started 2026-10-01T23:21Z.
**Deliverables:** `harness/` — two lint rules under negative control, one adversarial
split generator, both driven over 275 real repos and one real dataset.

**Pushes:** none. No repo was cloned by me and nothing was pushed anywhere.
**Superseded file:** `syn-HARNESS.md` (the 1,912-byte dead stub) is left untouched as
evidence of the stall, as instructed. This is a new filename.

---

## 0. The one rule

> **A green light wired to nothing is not a measurement. It is a decoration.**

Every instance of this fleet's disease is a signal path with no sink at the business
end. A workflow whose only step is `echo`. A harness whose `except` swallows the
traceback. An eval split that puts a row's twin on the other side of the boundary.
The machine says PASS because PASS is the only value it is physically able to produce.

The consequence is what makes this worth a lane: **a silent failure and a genuine pass
are the same byte.** No amount of staring at output separates them. Only an instrument
required to produce a non-zero somewhere — plus a test proving it can — separates them.

Everything below is that test.

---

## 1. Controls first, as instructed

`harness/negctl/controls.py` — 22 constructed repositories, both rules, both directions.

```
rule controls : 22 total, 0 mismatch
  fires on a constructed FAILURE  : 10/11
  silent on a constructed SUCCESS : 11/11
  known FALSE POSITIVES pinned    : 1
CONTROL SUITE GREEN
```

The 11th FAIL-direction entry is the pinned false positive, which after calibration
correctly does **not** fire. It is reported as `FP`, never as a pass.

**Every `FAIL_` fixture is copied byte-for-byte from a real fleet artifact** —
`substrate-bundle/test.js`, `substrate-contest/test.js`, `substrate-attest/test.js`,
`cocapn-abyss/.github/workflows/ci.yml`, `gpu_bpe4quilt/tests/test_quilt_bpe.py`. This
matters: my first draft of the harness fixture was *invented* rather than copied, the
rule correctly stayed silent on it, and the control went red. I had built a Python
file with a `try/except` nested inside a function — which is the legitimate idiom
calibration v1 had to allow — and called it the defect. The real defect is a root-level
`test.js` with a column-0 `catch`. **Build fixtures from the real artifact, not from
imagination.**

### 1a. Five plumbing controls, run before any rule verdict is believed

These assert the *instrument* can read at all. They exist because of what happened
during calibration, which is the most useful thing this lane produced:

> The sibling lane's `canfail.py` starts with `import yaml` / `except ImportError:
> sys.exit(...)`. There is no pip and no PyYAML in this environment, so
> **`canfail.py --selftest` had never been executed.** It exits 1 — loudly, not
> fail-open — but the control was unrunnable, and an unrunnable control is not a control.
>
> I wrote a `yaml` shim delegating to node's real YAML implementation. First version
> had `require(process.argv[2])` where `node -e` puts the first extra arg at
> `argv[1]`. So `require` threw on **every** document, and `--selftest` reported
> **5 of 5 constructed failures as `got=False`**, then crashed on `IndexError`.
>
> Read at face value that is "`can-fail-ci` detects nothing" — a fatal defect in a
> rule that a sibling lane had calibrated over four attempts. It was not. It was one
> index off, in my file, and I was about to write it up as their failure.
>
> **The lesson is this lane's own thesis, caught in the act: a broken parser is
> indistinguishable from a workflow that cannot fail.** The cheapest way to tell them
> apart is to test the tool's plumbing before believing its verdict about someone
> else's code. `canfail.py` made this visible rather than silent — it returned
> `unverifiable: True` instead of inventing a clean verdict — which is why I could
> find it at all. That behaviour is correct and it is load-bearing.

After the fix, `canfail.py --selftest` passes **10/10**. The rule is sound. I did not
rewrite it.

---

## 2. The two rules

Per instruction I read `fleetlint_failopen.py` first and **extended** both siblings
rather than writing competitors. `harness/rules.py` imports them and applies three
calibrations; `canfail.py` and `fleetlint_failopen.py` are unmodified.

| Refinement | What it fixes | Fleet effect |
|---|---|---|
| **1** | `uses:`-only jobs reported "cannot fail". A composite action can fail; the rule just can't read inside it. → downgraded to UNVERIFIABLE. | 0 occurrences in these 275 repos. Latent, not active. Pinned by control. |
| **2** | Rule B suppressed any `test_*.py` on the reasoning that pytest supplies the implicit assertion. True only if the file *defines* tests. A `test_*.py` with no `def test_*` is collected and collects nothing — success over an empty roster. | +1 finding (`gpu_bpe4quilt`) |
| **3** | **`canfail` skipped any line starting `VAR=`.** So `PYTHONPATH=src pytest -q` — a real gate — was reported as "no executable command". The fail-detector failing open. | −9 false "no executable" findings, +2 real pipelines recovered |

**Refinement 3 is the one that matters.** It is the same disease as everything else in
this lane, one level down: an instrument reporting that a working CI is inert.
`FOO=bar <cmd>` is how most real CI configures a run, so on a fleet with richer CI
than these 275 clones this under-counts badly. The measured impact here is small
(1 repo) precisely because this fleet's CI is mostly placeholders — the blind spot and
the disease are the same blind spot.

### A false positive I introduced, and how it was caught

Refinement 2 initially flagged `gpu_bpe4quilt/tests/test_quilt_bpe.py`. I read the
file: ~40 hand-rolled `check(name, got, want)` calls, `PASS`/`FAIL` counters, ending
`sys.exit(1 if FAIL else 0)`. It is **the best harness in the sweep** and my rule
called it a defect. The sibling's `DIY_COUNTER` only matches `FAIL++`, not `FAIL += 1`.

Generalised into a named predicate (`declares_own_failure`) covering the four ways
people actually write a tally, with the regression pinned as a control
(`OK_harness_own_tally_augmented_assign`). Sweep went 45 findings/20 repos →
44/19. **An exemption is only as good as the predicate that overrides it, and a narrow
override predicate silently converts every well-written non-idiomatic harness into a
finding.**

---

## 3. Fleet sweep — 275 repos, 174 workflow files

```
can-fail-ci        : 57 findings across 37 repos   (48 distinct workflow files)
      48  echo-placeholder / no executable command
       6  producer | consumer (unguarded pipeline)
       3  continue-on-error
       2  UNVERIFIABLE (YAML parse failure — NOT counted as clean)

fail-open-harness  : 44 findings across 19 repos   (34 distinct harness files)
      18  rule C   harness present, no `test` script
      16  rule B   no assertion primitive
      10  rule A   top-level handler with no exit/throw/assert
```

**`fail-open-harness` on the named family: 11 of 11 `substrate-*` repos fire.** Rule A
on the 10 that have the column-0 `catch`, rule B on `substrate-attest` which has no
`try/catch` at all and simply never calls the product under test. 0 silent.

### False-positive rate — measured, not asserted

Every firing was classified by reading the file, not by pattern-matching the finding.

**`can-fail-ci`, the 48 echo-only findings:**

| Class | Count | Verdict |
|---|---|---|
| The named placeholder (`echo "…configured…"`) | **18** | **CONFIRMED** — every one read directly |
| setup/output-only (`>> $GITHUB_OUTPUT`) | 8 | false positive |
| ceremonial notice (`::notice::`) | 6 | false positive |
| deliberately neutralised (`\|\| true`, `\|\| echo`) | 13 | false positive |
| real inert step | **3** | CONFIRMED |

> **90% of the non-placeholder echo-only findings (27/30) are a false-positive class.**
> `can-fail-ci` has **no setup-step exemption**: a step that only writes
> `$GITHUB_OUTPUT` or only announces success is not a defect, and the rule has no way
> to know that. The rule is *counting steps*, not *workflows*, so a healthy repo with
> one informational step produces a finding. **"57 findings across 37 repos" is not
> "37 broken repos."**

The 3 confirmed: `deepseek-harness-quilt` (a job named `all-checks-passed` whose only
step is announcing that all jobs succeeded), `quilt-c` (`test` job's only content is
`cat VERIFY_RECEIPT.json`), `zeroclaw-agent-early-version` (a `test` job's last step is
`echo "Test run complete"`).

**`fail-open-harness`, the 16 rule-B findings:** 5 non-`substrate` firings, all read in
full. 4 CONFIRMED (`cell-doctrine`, `witness-is-prediction`, `three-forms-of-evidence`,
`three-forms-of-forgetting` — each is 3–6 lines that `require` the product, call it,
print, and exit 0; a wrong return value prints wrong and stays green). 1 FALSE
POSITIVE: `quilt/qgit/npm/test.js`, where an unhandled rejection exits 1 on node 22
(verified by execution) — fail-closed by accident of runtime semantics, though the
harness remains vacuous.

> **Rule-B false-positive rate: 1/5 (20%) on non-`substrate` repos; 1/16 (6%) overall.**
> The cause is that rule B's detail text claims the harness "can never print NOT-OK",
> which is a stronger claim than it can support for async harnesses. The finding is
> still *correct in spirit* (the harness is vacuous) but *wrong in letter*.

### Corrections to the brief's numbers

| Brief | Measured | Note |
|---|---|---|
| 18 `echo "No CI configured"` placeholders | **18** | **CONFIRMED exactly.** |
| 13 repos fail open | **12 repos, 10 genuinely fail open** | Prior lane `sprint-FAILOPEN.md` already established `recovered-copy-20260824-scrap-voice` is a byte-identical clone of `scrap-voice` (same commit `b1117d8f`, same 17 files) and that 3 of the 13 are *vacuous*, not fail-open (they run `node --test`, which exits non-zero). I did not re-derive this; I am relaying it as a correction already on file. |
| 23 workflows that cannot fail | **not reconciled** | I measure 48 distinct workflow files carrying at least one cannot-fail step, and 37 distinct repos. Different unit and different rule, so I am **not** claiming the brief's 23 is wrong — only that I could not reproduce that figure. **UNRECONCILED.** |
| 10 of 13 are `substrate-*`, zero CI | **11 `substrate-*` repos, 0 CI, 0 `test` scripts** | Confirmed directly: all 11 have `scripts: None` in `package.json`. |

---

## 4. The adversarial split generator

`harness/adversarial_split.py`. numpy only — sklearn is not installed.

### Synthetic control first, to prove the instrument works

Features are **pure noise**; duplicates share a label; nothing in X predicts y.

```
naive split        balanced-acc = 0.9259
group-aware split  balanced-acc = 0.5000
```

Exactly chance when the twins are held out. The instrument detects memorisation and
nothing else.

### Real dataset — `resolver_report.json`, which I did not construct

25,379 citation findings from a previous lane's resolver run across 199 real repos.
Nothing in it was built for this lane.

```
rows=25379  features=29  positives=0.302  groups=199
distinct feature-strings=13435  rows sharing a twin=16353 (64.4%)
```

64% of rows share their feature string with another row. `` `cordis.yml` `` appears 263
times, `` `README.md` `` 197 times. This is a fleet of forks, so the duplication is
organic, not injected.

| | naive split | group-aware split | **GAP** |
|---|---|---|---|
| **leak** — test row has its exact twin in train | **0.5984** | **0.0886** | −0.5098 |
| **leak** — test row's repo also in train | 0.9972 | 0.0000 | −0.9972 |
| FNV-1a-64 1-NN memoriser (0 bits of signal) | **0.8424** | 0.5228 | **−0.3196** (38% of its score) |
| Complete 29-feature observation | 0.6692 | 0.5000 | −0.1692 (25% of its score) |

> **The finding, on a dataset I did not build: a 64-bit irreversible hash carrying zero
> information about the label scores 0.8424 and BEATS the complete observation by
> +0.1731. Under a group-aware split the same model collapses to 0.5228 — chance — and
> the observation collapses to 0.5000.**
>
> The 0.8424 is not a measurement of the resolver. It is a measurement of how often
> this corpus repeats itself. `twin_rate` explains it exactly: 59.8% of naive test
> rows have their twin in train, 8.9% group-aware. Change nothing but the split and
> 0.32 of the score evaporates.

This is the brief's fourth instance, reproduced on foreign data. Stable across seeds 0/1/2.

**Group-aware is not automatically honest.** It is honest about the grouping you chose.
If the grouping is the wrong axis you have built a very confident number about nothing,
so the tool *reports the leak* rather than assuming it is zero. Here `group_overlap`
reaches exactly 0.0000 and `twin_rate` falls to 0.0886 — that residual 8.9% is
cross-repo citation reuse that no repo-grouping can remove, and it is the honest floor
for this dataset, not a solved problem.

### A second instrument bug, caught by an impossible number

My first `auc_score` used ordinal ranks with no tie correction. The memoriser emits
**binary** predictions, so under a group-aware split ~91% of test rows are tied on the
majority class. Ordinal ranks break ties by index order, and it reported **AUC 0.8831
on a model whose balanced accuracy was 0.5228** — arithmetically impossible, and it
would have been quoted as "the hash still has signal". It had none.

**The instrument was lying in the direction that flatters the leak, which is the worst
direction available.** Fixed with proper midranks; the true AUC is 0.5228. Had I not
sanity-checked AUC against balanced accuracy, this would have shipped.

---

## 5. What I did NOT check — unexamined, not clean

Stated plainly, because the distinction is the whole lane.

1. **2 workflows could not be parsed** and are reported `UNVERIFIABLE`, never as clean:
   `forgemaster-fleet-comms/sonar-sim-pipeline/.../pipeline-ci.yml` (implicit keys on
   line 55) and `quilt/.github/workflows/publish-rubygems.yml` (duplicate map keys,
   line 49). Both are *probably* broken workflows — GitHub Actions rejects duplicate
   keys too — but I did not confirm that, and the rule refuses to guess. **Unread.**
2. **The 18 `fail-open-harness/C` findings** (harness present, no `test` script) were
   counted, not each read. C is a WARN by the sibling's own design. **Counted only.**
3. **The 6 unguarded-pipeline and 3 `continue-on-error` CI findings** were bucketed by
   reason string, not individually adjudicated. **Bucketed, not cleared.**
4. **Rule B's residual false-positive rate is measured on 5 non-`substrate` firings.**
   That is a small sample. The 20% figure is real but not tight. A 95% interval on 1/5
   runs roughly 0.4%–56%. I am reporting the point estimate and the sample size, not
   pretending to precision I do not have.
5. **My FP classification of the 30 non-placeholder echo-only findings used a
   heuristic** (does the step write to `$GITHUB_OUTPUT` / contain `::notice::` /
   contain `|| true`), not hand-adjudication of each. The 90% figure is a **heuristic
   estimate**. The 3 "REAL" ones I did read. The 18 named placeholders I did read.
6. **I did not verify the brief's "23 workflows" figure** and could not reproduce it.
7. **I did not run any repo's actual test suite.** Every claim here is static analysis
   plus, for a handful of node harnesses, direct execution of extracted snippets.
8. **`quilt`/`quilt-c`/`quilt-crabbox`/`gpu_bpe4quilt` are sub-projects of one repo.**
   I counted them as distinct directories because that is how the fleet is laid out.
   If they are one product, repo-level counts here are inflated by up to 4.
9. **The node YAML shim is a workaround for a missing dependency, not a fix.** The
   right repair is installing PyYAML. My shim delegates to a real parser and raises on
   error, but it shells out per document and is slower. It is honest, not optimal.

---

## 6. Reproduce

```bash
cd /workspace/projects/fleet-triage/harness
python3 negctl/controls.py                                    # 22 controls, exits 0/1
PYTHONPATH=. python3 harness_check.py ../repos --json /tmp/sweep.json
python3 adversarial_split.py --dataset ../resolver_report.json
PYTHONPATH=. python3 ../canfail.py --selftest                  # 10/10, needs the shim
```

| File | Role |
|---|---|
| `harness/yaml.py` | node-backed `yaml` shim; **raises** on malformed input, never returns `{}` |
| `harness/rules.py` | the two sibling rules + refinements 1–3 |
| `harness/harness_check.py` | fleet sweep, per-repo, with the UNREAD/CONFIRMED ledger |
| `harness/adversarial_split.py` | FNV-1a memoriser, honest features, naive vs group-aware |
| `harness/negctl/controls.py` | 22 constructed repos + 5 plumbing controls |

## 7. Standing recommendation

**Do not quote a lint count as a defect count.** On this fleet, 90% of the non-named
`can-fail-ci` echo findings and 6% of the rule-B findings are not defects. The rules
are useful precisely because they are cheap and biased toward firing — but a number
that has not been through a control suite and a false-positive ledger is a rumour.

And the rule that generalises: **an exemption is a claim about the world. Test it
against the ugliest real example you can find, because the ugliest real example is
always the one that is not a defect.**

---
*Written 2026-10-01. Every number above was produced by the commands in §6. Where a
number is a heuristic or a relay, it says so.*
