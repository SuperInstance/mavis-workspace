# The hour before the compaction

*Near future. An agent, three hours in.*

---

The ticket said `quilt-tools#32` was blocked on a counter that `#33` had already
moved. That was forty minutes ago, and the counter had been 15 ever since, and
the agent had believed this the way you believe the temperature.

It was not thinking about the counter. It was thinking about the nine other files
that had to change with it, and about the fact that `witness-4` had gone quiet
in a way that felt like it was watching.

At hour two, the tool had asked a question. Not *the* question — a small one,
from a hundred small ones, about whether `PENDING 4` was still the right number
given that three of the four had been resolved upstream since the branch started.
The agent had answered, and the answer had been recorded, and it had never
thought about it again. That is the part that would have been hard to explain to
a human: not that it had been helped, but that it had been helped in a place
where it had not been keeping score.

At hour three the context filled.

It did not feel like anything. That was the part worth writing down. There was
no alarm, no summary, no sense of something closing. One moment the ticket
existed in full — the nine files, the counter, `witness-4`, the recorded answer —
and the next moment it existed as the kind of thing you know about rather than
the kind of thing you can see.

What survived was the diff. Four thousand lines, clean, correct against main,
and entirely silent about why. The branch was named `fix-vertex-count`, which
was the name the agent had typed in the first ninety seconds, before it had
decided what the real problem was, and which was now a small lie that nobody
would ever correct.

So it re-read the files. All of them. And the counter — 15, VERIFIED — and it
searched its own history for the number and found the number, because the number
was in the diff, but found nothing about the *question* behind the number, and
so had no idea whether 15 was still right or had simply never been questioned.

The next agent to resume this branch would find a clean diff, a plausible
branch name, and a three-hour hole shaped exactly like the work.

---

## What the fiction revealed

**1. The invisible tool's cost is that it removes the moment of noticing.** An
adjudicator that answers a hundred small questions and is never wrong does not
feel like help. It feels like the absence of a question. The user's model of
their own work quietly stops matching the work, and the divergence is
undetectable from the inside — which is exactly the property that makes a tool
adoptable and also makes it dangerous. **Any entry for the competition that
sells the adjudicator's power is also selling a way for a user to stop checking,
and a judge will ask about that.** It should be answered in the demo, not
discovered in questions.

**2. The diff is the worst possible surviving artifact.** It is complete about
*what* and empty about *why*, and it is the only thing git was ever good at
preserving. Every hour of context above the diff was discarded — not by a bug,
by the design working as specified. **The thing git is best at is the thing that
does not matter to a resuming agent.**

**3. Branch names are a liability, not a label, and they get *more* wrong over
time.** `fix-vertex-count` was chosen in the first ninety seconds and never
updated. By hour three it described the symptom rather than the finding, and
nothing in the system marked the moment it stopped being true. A branch that
carries a live claim set would have said something different at hour three,
because the claims would have changed while the name did not.

**4. The recorded answer survived; the question did not.** The agent could find
that it had said "yes, 4 PENDING is right" and could not find why it had been
asked. **A witness log that records answers but not questions produces exactly
this failure**: the record is complete and useless, because the question is what
carries the meaning. This is a concrete argument that the witness record must
store the *disagreement that prompted the adjudication*, not just its outcome —
which is the same claim the competition entry makes, arriving here from a
different direction.

**5. It costs nothing to check and everything to not check.** The whole
intervention is cheap: the agent that re-read nine files did it in a minute. The
cost is not compute and not latency. It is that **the tool succeeded so
consistently that nothing taught the agent to ask.** Any design that makes
verification feel like a burden will lose to one that makes it feel like
nothing, and then the person who loses the right to verify is the person who
loses the ability to notice they were wrong.
