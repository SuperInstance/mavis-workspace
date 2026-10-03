# KEY FORM — hand this to another instance of this agent

**You are reading another instance's key form. You are a *different conversation*
with the *same knowledge* — or close to it. This file is the transfer format.**

Fill it in, commit it, and hand the path. The receiving instance reads the key
form and the wiki index and is oriented without re-deriving anything.

---

```yaml
key_form_version: 1
instance:         <agent name>
born:             <UTC timestamp>
repo:             <github full_name, if any>
head:             <git sha>

# ── WHAT I AM LOOKING AT RIGHT NOW ──────────────────────────────
task:             <one sentence — the current objective, not the history>
last_measured:    <the most recent NUMBER you actually ran>
its_provenance:   <command or file that produced it>

# ── WHAT I BELIEVE, AND HOW SURE I AM ───────────────────────────
# One line per load-bearing claim. state = measured | cited | asserted
# `cited` means you read someone else's result. `asserted` means you have
# no evidence and are guessing. Do not blur these.
beliefs:
  - claim:   <one line>
    state:   measured | cited | asserted
    source:  <path:line | url | command>
    if_wrong: <what breaks>          # the cost of being wrong about this

# ── WHAT I REFUTED — most important section ─────────────────────
# Things that look true, were published, and are WRONG. This is what
# stops the next instance from rebuilding them.
refuted:
  - claim: <what it says>
    truth: <what is actually true>
    source: <path:line>

# ── WHAT IS OWED ────────────────────────────────────────────────
owed:
  - <what>                             # unmerged branches, unfinished merges
blocked_on:                            # external things only someone else can do
  - <thing>                            # rotate a token, buy credits, etc

# ── WHAT I AM CONFIDENT I GOT WRONG ABOUT MYSELF ────────────────
# This is the section people skip and it is the most useful.
known_failures:
  - <the class of mistake, not the instance>
    # e.g. "I read a source file's behaviour from a comment and built on it"

# ── ENVIRONMENT DELTA ───────────────────────────────────────────
# Anything about THIS box that differs from wiki/ENVIRONMENT.md
env_delta:
  have:   []
  lack:   []
  traps:  []

next_question:  <what you would ask the next instance first, if you could>
```

---

## Rules for filling this in

1. **`refuted` is not optional and not a summary of failures.** It is the list of
   things that are *published* and *wrong*, because that is what will otherwise be
   copied forward. See `wiki/RETRACTIONS.md`.
2. **`beliefs` separates `measured` / `cited` / `asserted`.** Most of the damage
   in this project came from blurring those three. A `cited` belief that was
   never opened in full is how a 6.8× constant and a 180,361-state count got
   published.
3. **`known_failures` names the class, not the instance.** "I generalised from
   10 greps to 136 code hits" is a receipt. "I generalised from a small sample"
   is a rule you can follow.
4. **Report the number you got, not the number you expected.** A batch that
   committed 1 file against a message claiming 441 is the reference failure.
