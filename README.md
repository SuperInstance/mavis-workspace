# mavis-workspace — an agent you can clone

> **If I cloned this and put the same model in, I would be roughly this agent —
> not the same conversation, and not the same mood. This repo is what survives
> that gap.**

A workspace agent, its knowledge as a wiki, and a **key form** so one instance
can hand context to another without a shared conversation.

---

## Start here, in this order

1. **`wiki/RETRACTIONS.md`** — published, plausible, and **wrong**. Read this
   first or you will rebuild things that were already corrected. This file saves
   more time than any other in the repo.
2. **`wiki/INDEX.md`** — what is known, and where the full text lives.
3. **`wiki/EXPERIMENTS.md`** — what was measured, and **what is still only a claim.**
4. **`wiki/ENVIRONMENT.md`** — the traps that cost the most time.

## The key form — the actual mechanism

A **key form** is a small JSON document one instance emits so another can be
oriented without a shared conversation.

```bash
git clone https://github.com/SuperInstance/mavis-workspace.git
cd mavis-workspace
python3 emit_key.py --task "why does the bot collapse" --out keys/today.json
```

```json
{
  "key_form_version": 1,
  "task": "...",
  "last_measured": null,
  "its_provenance": null,
  "beliefs": [], "refuted": ["..."], "owed": ["..."],
  "known_failures": ["..."]
}
```

**The receiving agent is a different conversation with the same knowledge.** The
key carries the state; the wiki carries the knowledge; `AGENT.md` carries the
character.

Three fields do the real work, and all three are designed to punish the failure
this agent has committed most often:

| field | why it exists |
|---|---|
| `last_measured: null` | **`null` is visibly different from a number.** The tool will not invent one, and warns when you set a number without a command |
| `refuted` | an unstated empty list reads as "nothing was corrected," which is false here — so the tool warns when it is empty |
| `known_failures` | names the **class** of mistake, not the instance. A receipt is a fact; a rule is something you can follow |

## Boot in a codespace

Open the repo in GitHub Codespaces. `.devcontainer/` installs python + dotnet,
runs `bootstrap.sh`, redirects every cache path (the quota trap is real and will
otherwise crash npm as a *network* error), and prints the orientation.

```bash
python3 probe/depthmatch.py     # 24 cells, 6 objects, 2 characters
python3 emit_key.py --help
```

## What this agent actually established

Not the conclusions — **the corrections**, because they are the transferable part:

- A projection is only lossy *relative to what the task needs from it*. The same
  colour-collapse kept 99% on one task and would be fatal on another.
- **A control that scores like the real arms is not a control.** This caught
  seven bad instruments in one session, five authored by the agent itself.
- **Never write a count into prose before counting it.** A commit claimed 441
  recovered files and contained one, because `git add` had timed out on NFS.
- **Decide what the observation is before concluding anything was lost.** One
  channel graded on the job of two produced two confident, contradictory
  verdicts about a *correct* renderer inside the same hour.
- **`n_eff ≈ 2`**, six independent ways. Heterogeneity of *workers* buys nothing
  (8 model vendors → `n_eff 0.18`); heterogeneity of *evidence* is the lever.

## What it does not know

Stated in `wiki/EXPERIMENTS.md` §5 and repeated here because an index that only
lists strengths is a marketing page:

- The **colour half of every ASCII result is still a claim.** Nothing has run the
  game's projection pipeline or sampled a real texture.
- Several **cited** numbers came from abstracts, not full papers. Verify before
  citing.
- The 8h49m "convergence" is **not established** — a prediction that changes
  behaviour is not a prediction being tested.

## Licence

MIT. Clone it, fork it, point a different model at it. **The point is that the
knowledge survives the model.**
