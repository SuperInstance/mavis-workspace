# Pixels → JEV → LLM → bot → slow coder → strategy index

2026-10-02. Casey's architecture, and the two failure modes that would sink it.
Written before a lane builds anything, because both failure modes are ones this
account has already paid for.

---

## The architecture, as stated

```
pixels on a screen
  ↓
JEV iterating rapidly              fast loop, many calls
  ↓
an LLM analysing the JEV iterations   reads the fast loop, interprets it
  ↓
an algorithmic auto-playing bot       the player; script-driven
  ↓
a larger, slower iterating coder     rewrites the bot's scripts
  ↓
A/B the scripts, keep the better one
  put the worse one away WITH SPECIFIC COMMENTS
  ↓
a build index of what the comments on older
strategy iterations were doing
```

> **"This makes the theory of mind have history — not just telemetry."**

**That last line is the whole idea, and it is exactly right.** Telemetry says
what happened. A theory of mind says **what was believed, why, and what was
rejected.** Every system in this account that has telemetry and no history is
unable to answer the only interesting question: *why does it do that?*

## It is four known patterns stacked, and that is a strength

| the architecture | the pattern, already measured |
|---|---|
| the slow coder designing while the bot plays | **`r1-SYNCOPATION`** — system-two is a move behind by construction |
| A/B the scripts, keep the better, archive the other | **the competition entry's refusal** — both losing claims kept verbatim, with source line and author |
| the fast JEV loop and the slow interpreting LLM | **the graceful-fall ladder** — JEV tunes, something fast samples, a local policy holds |
| the index of what the comments were doing | **the witness log**, the pattern with four known failure modes |

**The bot keeps playing when the model is slow or absent** is `r1-NOENGINE`,
and the archived-strategy-with-comments is the *thing the entry already does*
at the merge level, promoted to the strategy level.

So this is not a new idea. It is the existing stack, composed. Good.

---

## FAILURE MODE 1 — an unbound index is just more sediment

**The index of strategy comments is a witness log, and `durable-LOGIC` found the
four ways witness logs fail in this account:**

1. **Never constructs the thing.** A canary that hashes a constant.
2. **Compares a constant to a constant.** Cannot fail by construction.
3. **Truncated at the head instead of anchored.** Order and integrity without
   the claim.
4. **Never re-run.** A check that *could* fail but was not run again.

**A strategy index is a hash chain over "what was rejected and why."** And an
index of comments that are **not bound to the specific script version they
critique** is exactly the failure we already have: `fleet-triage` is 264 files of
excellent, unbound commentary and it composes with nothing.

**The requirement, and it is not optional:**

> **Every archived script carries its own comments, and every comment names the
> script version and the specific line or behaviour it is about.**

A comment that could be attached to any revision is not a witness, it is an
opinion. **If you cannot say which line it refers to, it does not go in the
index.**

And it should be **chained and anchored**, not appended — because the fourth
failure mode is the one that keeps repeating, and a strategy index that nobody
re-reads is a strategy index that is silently wrong.

## FAILURE MODE 2 — the A/B is measured over a window nobody watched

This is the sharp one, and it is the syncopation design's risk turned against
it.

**The slow coder picks the winner from a short observed window. The loser kept
playing the whole time, unseen.** So the comparison is between *the loser as
observed early* and *the loser as it actually behaved*, and the code is being
selected on a window that does not contain the evidence that would decide it.

> **A policy chosen for what it did while you were looking is not the policy you
> will get.**

This is the fifth instance of the same broken metric I have now hit:
`detection_power` scoring a perfect instrument 0.242 · `selectlib` printing a
ranking from `seeds=(0,)` · a Connect-4 policy metric returning 0/12 for a
policy measured at 0.9871 · a claim-classifier returning "zero standing" because
a string prefix did not match · **and now a strategy A/B whose denominator is
the observed window and whose numerator is the full game.**

**The fix is the same rule the other four taught:**

> **A/B over a fixed budget of *observed* play, and the tail is recorded, not
> discarded.** "The better script" has to be a claim about a window somebody
> watched.

The tail record is also the most valuable thing the system produces. **It is
where a system surprises you**, and it is precisely what a theory of mind
without history throws away.

---

## The part that is genuinely new, and worth getting right

**The fast loop cannot comment on itself.** JEV iterating on pixels is fast and
blind to its own trajectory. The slow LLM is the only thing that can read the
sequence and say *the third iteration stopped trying to identify the door and
started trying to avoid it.*

**That is the division of labour, and it is worth more than it looks:**

- the fast loop is a **sensor** and it must not be asked to be a witness
- the slow interpreter is the **witness** and it must not be asked to be fast
- the bot is the **actor** and it must not be asked to explain itself
- the index is the **memory** and it must be append-only, chained, and re-read

**One component per role, and no component asked to do two things.** That is the
same lesson as the 21 game demos — *deterministic code enumerates, something
chooses* — and as `lau-git-render` — *one `RenderContext`, eight renderers.*

## What I would want measured

1. **Does the slow coder actually improve play, or does it churn?** With the A/B
   fixed as above. If the honest answer is "it makes things worse and the fast
   loop was fine," that is the most valuable result in the round.
2. **How often does the archived strategy's comment predict the NEXT failure?**
   If the comments are only describing the past, the index is a diary. If they
   anticipate, it is a theory of mind.
3. **What does the fast loop do when the slow one is not looking?** A
   system-two gap is a feature *once* and a hazard *twice*.

## The one sentence to design against

> **Telemetry records what happened. A theory of mind records what was believed,
> what was rejected, and how far down the fallback chain the answer still
> holds.** The architecture in this document is only worth building if the index
> is the second kind.
