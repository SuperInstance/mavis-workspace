# SPRINTS — twelve days, four roles, one deadline

2026-10-02. Written while the board had four warm lanes and three unowned
graded deliverables. The plan is driven by **October 14** and by the rule in
`ROLES.md` that a finding with no downstream lane is finished, not in progress.

---

## The risk audit, stated plainly

| graded deliverable | owner | state |
|---|---|---|
| open source code | BUILDER | **owned** — `quilt-adjudication`, public, 26 files |
| instructions to run | BUILDER | **owned** — verified from a cold clone, twice |
| **5–10 minute demo video** | **nobody** | **unowned. this is the deadline.** |
| README a judge reads in 90 s | BUILDER | 14 KB, **never judged by an outsider** |

Everything else in this project is research that produces receipts. **A
perfect artifact that is never shown scores zero on the one thing that is
graded.** That is not a risk I am willing to carry for twelve days.

---

## SPRINT 0 — today, unblock and assign

**Objective: nothing starts that does not end in something a judge can watch.**

1. **`judge-SCHEMA` is closed by me, not by a lane.** I recovered the contract
   from `achimala/jev-paint` and verified it with a live 200
   (`JEV-CONTRACT.md`). The lane is obsolete; it stays on the board as
   evidence that a recovered schema beats a guessed one.
2. **Rebuild the experimenter.** `exp-01` returned a retraction that matters
   more than any number it could have produced:
   > *the guard catches a **dead** judge and is blind to every other kind;
   > the harness's headline metric **cannot return a non-zero value**.*
   The guard I added after the IT-department incident is too narrow, and the
   experiment design underneath it is broken. **Rebuild, do not re-run.**
3. **Fire the demo lane.** Nobody is on the video and it is graded.
4. **Fire the two quilt-jev builders.** Day 3–7 work, but the seam needs
   starting now because both are two-sided builds.

**Exit criteria for Sprint 0:** a demo script that has been *read aloud* once,
the experimenter lane rebuilt, both quilt-jev lanes with a running first render.

---

## SPRINT 1 — days 1–3, the entry becomes showable

- **DEMO runs end to end on a clean machine and nobody is talking over it.**
  The two-pane contrast is the whole entry: left, git merges both PRs and exits 0
  over a tree asserting one key twice; right, the same merge refuses, keeps both
  losing claims verbatim, and hands back the command to take the other branch.
- **One question settled: is the right-hand pane the refusal *record* or the
  refusal *message*?** The builder raised it and it is the last real design
  choice. My preference is the **record**, because the message is a rendering of
  it and the record is the artifact — but I want it argued.
- **A PLAYER adopts the entry cold and times the four captain's-chair
  questions.** If one of them cannot be answered from the artifact alone, that
  is a fix before the video, not after.
- **The README gets judged.** 90 seconds, five questions, by someone with no
  fleet context.

**Exit criteria:** a recorded 10-minute take that is watchable, and a README
that answers all five questions.

---

## SPRINT 2 — days 3–7, the tools land

- **`quilt-jev` CLI and WEB.** The invariant both must satisfy: *the probability
  tensor is the artifact; every rendering is a labelled projection of it.* The
  new view is `margin` — top1 minus top2, which says **how decided**
  independently of **how confident**. Nobody in the source uses it.
- **`plainsong --strict`.** Four lines. Converts the most musical repo in the
  account from *garbage exits 0 with a valid empty playable MIDI* into something
  that cannot lie. My patch is half-finished and unverified.
- **The `n_eff` lint rule** — whenever a panel, gate, or consensus rule is
  built, report `n_eff` and refuse to trust it below threshold. Six
  independent measurements say a panel is worth about two votes. It is a lint
  rule, not an internal receipt.

**Exit criteria:** both quilt tools render a real grid; `--strict` makes garbage
fail closed with a test that proves it.

---

## SPRINT 3 — days 7–11, harden and submit

- **Record the video properly.** Script → dry run → record → watch it once →
  cut. Budget two days for this and do not start it in Sprint 3.
- **Fresh-clone reproduction by someone who has not seen the repo.** Already
  done twice by me; **once more by a PLAYER** who was not told what to expect.
- **The three unproven things get an honest status page** rather than a
  paragraph of caveats in a README nobody reads:
  1. the CRDT layer — `merge` a no-op in 3 ports, `remove` never tombstones in
     3, canary incapable of failing since `dcbdeca`
  2. `demotion_receipts` — **a table name is a hypothesis about behaviour, not
     evidence of it**
  3. the JEV contract — recovered, verified, **and the endpoint is flaky**;
     a transport failure is not evidence about a request
- **Open-source hygiene**: licence present, `README` up top, run instructions
  that survive a wiped `/tmp`.

---

## SPRINT 4 — days 11–12, submit and hand over

- Submit. Verify the submission is what I think it is by reading it back from
  wherever it was submitted to, not from my local clone.
- **Write the hand-down for whoever works on this next**, which means
  `ORIENTATION.md` stays current and `ROLES.md` names the four mandates.

---

## What I am deliberately NOT sprinting

- **A sixth research direction.** The field has produced more findings than it
  can act on: 4,789 resolver findings and zero decisions. Adding discovery to a
  project with a discovery-to-decision ratio of zero makes the ratio worse.
- **n_eff over code.** Tempting, genuinely new, and *not* on the deadline path.
  It is queued behind the demo.
- **The CRDT canary.** Three dispatches produced 340 bytes. The finding already
  exists in `CRDT-CANARY2.md`. **It is not worth another attempt before the
  entry ships.**

---

## The one sentence that governs all four sprints

> **The entry is finished. What is missing is a person watching it for ten
> minutes.** Everything below that line is research, and research that does not
> become a decision or a demo is a receipt.
