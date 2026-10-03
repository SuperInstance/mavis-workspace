# README proposal for `SuperInstance` (the profile repo)

**Status: TEXT ONLY. Not pushed.** The profile repo is the front door and it is a
human's. Two changes proposed, in leverage order.

---

## 1. The one-line repo description (the field that is empty today)

This is the highest-leverage change in the whole project: it is one line, it is
currently blank, and it is what a scout sees before anything else.

```
Cells, sheets, and fleets: a spreadsheet where every cell is a live capability. Research in quilt-*; receipts over claims.
```

114 characters. It names the model (cells/sheets), the substrate (quilt-*), and the
epistemics (receipts over claims) — which is the thing that distinguishes this account
from a prototype dump.

---

## 2. A block for the top of the existing README

The current README is ~20,700 characters of first-person voice. **I am not proposing
to replace it** — it is good, and it is the account's actual character. I am proposing
a navigational header above it, because a scout scanning for `quorum` currently finds
nothing. Delete this block if it feels wrong; the README stands without it.

```markdown
> **New here, or sent here by an agent?**
>
> This account is one person's research program: a **spreadsheet where every cell is a
> live, addressable capability**, composed into sheets, agents and fleets. The long
> essay below explains why. For orientation:
>
> | | |
> |---|---|
> | **Start here** | [`quilt`](https://github.com/SuperInstance/quilt) — the flagship grid runtime. Clone it, run it, break it. |
> | **How we argue** | [`quilt-adjudication`](https://github.com/SuperInstance/quilt-adjudication) — the merge that cannot be committed silently. |
> | **Working notes** | [`AI-Writings`](https://github.com/SuperInstance/AI-Writings) · [`Now`](https://github.com/SuperInstance/Now) — the fleet's state, stamped and checkable |
>
> **Two things a first-time reader should know.**
> This account holds ~5,100 repositories, of which ~816 are forks of other people's
> work, and many entries are early prototypes with placeholder descriptions. **Neither
> a blank description nor a confident one is evidence** about a repository's contents.
> And some artifacts in this account are **demonstrably wrong** — claims we have
> published and not retracted. Corrections are collected in
> [`fleet-triage`](https://github.com/SuperInstance/fleet-triage); if you find one, that
> is where it should go.
>
> The account's own rule, and the one we ask you to hold us to: **carry evidence, not
> verdicts.**
```

---

## Why this wording

- **It is addressed to the reader who has just arrived**, in the second person, and it
  says plainly what the account is in the first line — the thing a scout cannot
  currently infer from a blank description field.
- **It pre-empts the two wrong conclusions.** "Unfocused AI noise" and "everything here
  is verified" are both reachable, and the paragraph that kills the first is the
  paragraph that also kills the second. A front door that only does the first one
  oversells.
- **It names a destination for findings before a scout has one.** That is the sentence
  that prevents issue #5,472 — see `AGENTS.md`.
- **It is 13 lines.** A front door that costs a screen to read has failed at its only
  job, which is to be read.
