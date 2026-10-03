# WITNESS BRANCHES — dead ends kept on purpose

2026-10-02. **No PRs were opened for any of these and none should be.**
A witness branch is not a proposal. It is a record that a route was taken, why it
stopped, and what inside it is still worth having.

**Read this before rebuilding something that already exists.** Several of these
contain working code that was set aside for scope, not correctness — and the
scope reason usually does not transfer.

---

## The two reasons a route closes

**1. WE MOVED ON.** The project changed direction and this work no longer has a
caller. **No finding against the code.** It may be completely sound.

**2. IT WAS OVER-ENGINEERED FOR THE TOOL'S ACTUAL FUNCTION.** This is the one that
gets misread, so it is stated explicitly in the branch message every time:

> **The engineering was not wrong. It was correct engineering built for a use case
> beyond what the tool actually does.**

`rune-quilt` is the clean example: a per-cell C verification kernel, sound,
working — built for a general polyformalism primitive when the job was to answer
one question about one set of ports. **Strictly more work for no additional
answer.**

**A dead end for one project is often a finished tool for another.** That is the
third reason these branches exist rather than being deleted.

---

## The register

| repo | witness branch | why it closed | salvageable |
|---|---|---|---|
| `SuperInstance/rune-quilt` | `witness/2026-10-02-route-closed-overengineering` | **over-engineered.** per-cell C kernel + A2A worker patch, built for a general verification primitive instead of the one question the tool answers | `cmd/polyformal-verify/kernel_demo.c` — a per-cell intersection kernel with no dependency on rune-quilt's data model. Fits the substrate-walker and canary paths |
| `SuperInstance/quilt-mermaid` | `witness/2026-10-02-untracked-renderer` | **moved on.** project went to cell-graph/openers rather than a standalone diagram renderer | `quilt_mermaid.py` — a working cell-graph renderer. The shortest path to a picture if any surface ever needs one |
| `SuperInstance/Spreadsheet-ai` | `witness/2026-10-02-route-closed` | **moved on.** spreadsheet control-matrix, superseded by the packed-cell work | the packed-cell idea is now live elsewhere |
| `SuperInstance/quilt-conversation` | `witness/2026-10-02-route-closed` | **moved on.** A2A notebook/workspace concept, predates the Living Repository Lattice framing | the A2A workspace idea is not dead, only renamed |
| `SuperInstance/twist-engine` | `witness/2026-10-02-route-closed` | **moved on.** CLI prototype folded into other tooling | — |
| `SuperInstance/jev-quilt` | `witness/2026-10-02-route-closed` | **STALE, NOT DEAD — see the caveat** | the probe is still the JEV instrument |

**The last four carry empty commits by design.** They had no outstanding diff, so
the commit is a *position marker*: without it, a repo that was deliberately set
aside is indistinguishable from one that was forgotten. **That distinction is the
entire value of the branch.**

---

## CAVEAT — `jev-quilt` is stale, not dead

**Do not treat that branch as an abandonment.** `jev-quilt` holds the continuous
JEV probe, which is still a live instrument and has been pushed to across dozens
of sandbox wipes. It was marked only because its last commit predates this
session's work. **Check `main` before concluding anything.**

The same applies to the others: **a witness branch marks where a route paused,
not where it died.** If the route resumes, delete the branch — it has done its
job.

---

## The pattern, for the next archive

1. `git checkout -b witness/YYYY-MM-DD-<short-reason>`
2. Commit **the actual diff** if there is one, or `--allow-empty` if there is not
3. The message must answer four questions: **what was tried · why it stopped ·
   what was not wrong with it · where it might still belong**
4. Push to `refs/heads/witness/...` — **no PR, no merge request, no issue**
5. Verify with `git ls-remote` that the branch and its SHA are on the remote
6. Only then may the local copy be deleted

**Step 5 is the one that matters.** Everything else in this project that went
wrong went wrong by trusting a report instead of reading the remote — and
`quilt-mermaid`'s renderer sat untracked and invisible until this pass, which is
why it got its own branch name rather than the shared marker.
