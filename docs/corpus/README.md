# fleet-triage

Mechanical triage for the SuperInstance namespace (5,108 public repos), plus the
experiment queue for a GPU agent.

**Why it exists:** there are more repos than anyone can read, so the question is never
"which need help" — it is "which need help *and* can be helped mechanically." Every signal
here is cheap and mechanical so the census narrows the field before any judgement is applied.

## The signals

| signal | meaning |
|---|---|
| `hollow` | source files that are 0 bytes |
| `untested` | source files, zero test files |
| `nolicense` | no LICENSE — blocks outside contribution |
| `noverify` | no CI at all |
| `failopen` | a CI step whose test command ends in a pipe without `pipefail` — **it cannot fail** |
| `autopub` | a workflow that publishes on push |
| `vendored` | most of the tree is a committed dependency directory |
| `historybloat` | API `size` far exceeds the current tree — the excess is git history |
| `nocode` / `noreadme` | no source files / README is a stub |

**A read that fails is recorded `unreadable`, never as a clean bill of health.**

## Two bugs this tool has already had, kept here on purpose

**1. The `pipefail` check was per workflow file.** One job setting `set -o pipefail`
silently exempted every other job in the same file — *a control that runs, is satisfied,
and gates nothing.* Now checked **per step**, with a negative control: a file where one job
is guarded and one is not must flag exactly one.

**2. `historybloat` divided by `src_bytes`, which is zero for any repo with no source
files.** A ratio against a denominator that can be zero is not a measurement; it is a
construction that always produces a finding. It flagged 106 repos; **36 are real.**

Found by refusing to accept an impossible number: `covers` reported 344 MB of files inside
a 291 MB repo. It was not a GitHub quirk — the tree was complete and the true sum was
361 MB. The arithmetic caught the instrument.

## The namespace is a user account, not an organization

`/orgs/SuperInstance/repos` returns **404**. `/user/repos` returns all 5,108. Org-level
Actions policy, team-scoped secrets, and org branch-protection defaults **do not exist for
a user namespace.**

## Documents

- [`docs/GPU-EXPERIMENTS.md`](docs/GPU-EXPERIMENTS.md) — **the experiment queue for a GPU
  agent**: ten experiments, each with a pre-registered prediction and a written decision
  tree for what every possible result would mean. The decision trees are the point.
- `docs/HOLLOW.md`, `docs/AUTOPUBLISH.md`, `docs/SYNERGY.md`, `docs/STUBS.md` — wave output
  (in progress).

## Use

```
python3 triage.py              # full sweep
python3 triage.py ranked.txt   # a slice
```
