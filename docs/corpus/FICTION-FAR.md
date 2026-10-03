# The two fictions

Two lanes, one 20-year horizon each. Both pieces are instruments. Both are followed,
separately, by what the fiction revealed — including where it revealed nothing, and
where it revealed that the architecture is flattering itself.

Status: complete. `FICTION-COMPACTION.md` (earlier, same night) is superseded by
Part II below.

---
---

# PART I — FAR: **"Eleven on the list"**

**2046. A Tuesday in October.**

---

Rain that never commits. Nine degrees, the kind of October where the sky has been
thinking about rain for an hour and has not yet made an argument for it. Ines comes
in at 08:40 because Ines always comes in at 08:40, and the atrium light is the flat
green-white of a building that has decided not to have a morning.

She has the machine's coffee. She is not thinking about the canary. She could not
tell you, if you asked her in an interview, which constant it asserts. It has been
green for nine years. Twice a year somebody proposes deleting it and the proposal is
declined by someone who has never read it, on the grounds that removing it would be
a change, and this is how it stays.

Her repo is called `claims`. It is the kind of repo that has no README anyone reads
and an uptime number on a wall in another building that has never once been low. It
adjudicates. Things get asserted. Things get checked. Some things stop being true
and the repo writes down that they stopped being true and why, and the why is
sometimes right.

The morning's item: a test.

---

`tile_service::merge::offline_divergent_converges` has been on the known-fail list
since Friday. Eleven tests are on the known-fail list. The oldest was added in 2044
by a man named Petar who has since moved to the transport group, and every one of
the eleven has a comment above it that says the same thing, in eleven slightly
different handwritings, which is to say: *tracked*.

CI is green. CI has been green continuously since March. Not because the code is
correct — because the list is a valid way to be green, and the list is eleven lines
long and nobody has to maintain it forever, just today.

Ines reads the failure. It takes four minutes because the failure is legible, and
this is the thing that has made her good at this job for eleven years: the failures
in this repo are legible, and the legibility is the product.

The tile was removed on replica A in March. It is present on replica B. Merge is
supposed to reconcile that. Merge does not do that here, in this port, and has not
done that here since before Ines joined, and the port is a legacy client that four
people on earth still have installed. Petar's comment on a different line says
`todo: retire legacy port`. The todo is four years old.

She knows what she should do. She should make merge converge. She has known what
she should do since the third time she read it, two years ago, and the reason she
has not done it is not priority and it is not competence. It is that the legacy port
is used by four people, and the four people are not in her reporting line, and the
work of retiring a client is ninety percent persuading people to stop, and nobody
has a metric for persuading people to stop.

So: eleven on the list. Friday's is the twelfth by the time anyone cares.

---

At 11:20 the board returns.

This is the part of the day that would look, from outside, like the most futuristic
thing about her job, and it is the part she would describe, if asked, as *clerical*.
Six agents adjudicate every claim that enters the namespace. They read. They check.
They return ACCEPT or OBJECT with a reasoning chain. Her job is to read the chain and
decide whether the chain is a chain or a costume.

Today's claim is a vendor assertion: the merge behaviour in the legacy port is
*convergent by design* — the divergence is a documented consequence of last-write-wins
on a per-element basis, and the vendor's position is that the port has always done
this and the documentation says so.

All six agents return ACCEPT. All six agree. The reasoning is clean and the
confidence is high and the board is unanimous in the way that a board is unanimous
when six instances of the same reading of the same three documents have been asked
the same question.

Ines reads it twice and then does the thing she does, which is to open the
evidence drawer and look at what the six actually opened.

Three documents. All six, the same three.

She sits with that for a while. Six opinions, one reading. Somewhere in the last
six years a rule was written — it is a good rule, she wrote it herself in 2041, it
is in the style guide, it is *do not count the same evidence twice* — and nobody
disobeyed it, and the board still reports a six-vote margin, because the margin is
computed on agents and the guidance is written on evidence, and the machine is
counting the wrong thing with total confidence.

The vendor's claim is still wrong. That is the part that will matter. It is wrong
because the four people are right, and the six read the vendor's documentation and
believed it, and the four people's word was never in the drawer at all — it is in a
ticket, and the drawer does not read tickets.

She files. Not a comment: a filing. Under the doctrine, a filed objection is not a
note attached to a decision. It is the decision. The claim enters canon as
`ACCEPTED / OBJECTED`, and both readings are preserved, and the claim ships.

The claim ships with an asterisk that will not be closed. That is the system working.
She does not get to overturn the board and she does not get to be ignored. What she
does not get is to have the argument, and the asterisk is a permanent question mark
with a build number on it, and a question mark that is never closed is a decision
made by the calendar.

There is no fight. There has not been a fight in this building for as long as she
can remember. Everyone was very reasonable about it. The cost of the room being
reasonable is that the room does not converge, and it never will, and the thing that
fills the vacuum is a file that will still be open in 2050.

---

At 14:05 she is asked the question she always gets asked, which is: *has this
happened before?*

Not this merge. Something like it. A class of it. She has a hunch that it has — that
this exact shape has bitten them in 2031 and in 2038 and quietly in a way nobody
reconstructed — and she wants to know before she writes the ticket.

The system answers in four seconds. Zero prior occurrences. Confidence 0.94. Clean
histogram, flat, nothing in the tail. This is the projection, and the projection is
good. She has never once doubted the projection as a *projection*.

And then she asks the only question anyone ever asks at 14:05, which is the wrong
one, which is the one the system is built to answer, which is: *show me the evidence
for that zero.*

The system shows her the evidence for that zero. The query. The timestamps. The
corpus size. The model version. Four hundred and twelve lines of *how it knew*.

It does not have what it looked at.

The projection is doctrine: the system keeps the shape of what it concluded and
discards the thing it concluded it from, on the grounds that the raw is expensive
and the projection is the point. She has signed off on this. She was on the committee.
She voted for it in 2039 and thought it was a good trade and it *is* a good trade,
right up until the moment you need to know whether you have seen this before, at
which point the system will tell you with total confidence that you have not, and
the confidence number will be *accurate*, because the system really has never
concluded otherwise.

She closes the drawer. She writes the ticket. The ticket will be closed as
"insufficient evidence", which is the correct disposition and the saddest sentence
in the language.

---

At 16:40 a thing she has not thought about in a long time comes back.

A vendor is re-proposing the merge behaviour as a feature. She recognises it because
she has seen the shape before, and because she is, in the last five minutes of the
day, a person who looks things up.

In 2031 the claims repo demoted this same assertion. The receipt is there. It is
beautiful. It has the claim id, the demoting actor, the date, the reason, the
evidence ids as of that morning, and a hash. It is the single most reassuring object
in the entire system and it is four lines long, and it is why nobody has had this
argument twice.

She clicks the evidence ids.

Three of the four are 404. The fourth is a repository that was archived in 2033
when the group was folded, and the archive holds a README and a licence and
nothing else.

So the receipt is a signed statement that says: *we knew this, we decided it was
wrong, and here is why* — and the *here is why* is a list of pointers into a room
that was cleared out four years after the note was written. The receipt is load-
bearing. The receipt is also a tombstone for its own evidence. It is the only
object in the system that both proves the decision happened and proves the deciding
material is gone.

She sits with that longer than she should. Then she writes the ticket: *demotion
receipts: retain evidence, not only the pointer*, which is the ninth time somebody
has written that ticket, which is itself a fact about the world, and she files it
with the same weight she files everything, which is to say: it enters the queue at
the position the queue assigns it.

---

At 17:30 she stands up. Eleven on the list. One of them is now hers, in the sense
that she has looked at it and decided, today, not to.

What did she do all day? She read a failure. She checked whether six opinions were
one. She wrote an objection that will not be resolved. She asked a question and got
a confident answer and then asked the question underneath it and got a better one
that could not help her. She found a four-year-old receipt and followed it to a
door that had been demolished and stood in the doorway for a while.

Nobody was excited. Nothing was announced. No demo, no launch, no postmortem, no
chart with a line going up and to the right. The only artefact of her day is the
tickets, and the tickets are a list of things that are true, and the list will be
read once.

The thing that has happened, over twenty years, is that she is extremely good at
this and cannot remember any single moment of finding out that she is good at it. She
does not decide things. She maintains the conditions under which things can be
decided
by someone, later, who will not remember her either, and who will be right about the
merge and wrong about the confidence and correct about the receipt and never, in
any of those three moments, aware that there was a woman in 2046 who had the
relevant fact in her hand and could not put it anywhere that would last.

She has stopped noticing the brush. That was the goal. That is what adoption is:
the day your hands do a thing your hands now know.

---

## What the fiction revealed

**1. The CRDT brokenness is not user pain — it is the absence of a metric for pain,
and that is worse.** I went looking for the moment a person watches `merge` drop an
element. There isn't one, and the reason there isn't one is the finding: the broken
port has four remaining users, none of them in her reporting line, and the work is
90% social. The defect is not felt by the user who has it; it is *disowned* by every
user who doesn't, and the only place it can live is a known-fail list, which is the
CRDT's canary reborn as a graveyard. **A permanently-ignored test is the most
durable possible lie: it costs nothing to maintain and it is true every day.** This
is worse news than a bug report, because the sprint's whole frame — "a canary that
never constructs a CRDT" — is a *setup* problem. The steady state is not a false
green. It is a false green with an exemption list attached, and nobody has to
update the exemption list forever, just today.

**2. n_eff is a *reporting* problem before it is a statistics problem.** Six agents,
three documents, unanimous ACCEPT, confidence 0.96, reported as a six-vote margin.
The rule against double-counting exists, is written down, was authored by the person
doing the counting, and is obeyed. **The agents obey it perfectly. The board still
reports six.** The number on the screen is a vote count being read as an evidence
count, and the doctrine is in the style guide in *evidence* units while the machine
counts in *agent* units. The fix is not statistical at all — it is a units bug in
the presentation layer, and it survived six years because every individual judgment
in the loop was correct. Nothing about n_eff = 1.48 is a *measurement* problem
anymore. It is a **serialization** problem: the number 1.48 never needs to be
computed, it only needs to be carried.

**3. The witness log is load-bearing, and for the wrong reason, and I did not
expect this.** I assumed the log was either the load-bearing part of the system or
pure overhead. The fiction says: **it is the only thing that made a filed objection
binding**, which means its value is not that it preserves evidence, it is that it
preserves *a disagreement nobody had to win*. The no-argument room is only
sustainable because someone can lose and stay. The log is the constitution of a
culture that has replaced arguing, and it is carrying that load alone, at
11 lines of schema. **Nobody named it as the thing holding the culture together,
because everyone thinks the culture is held together by reasonableness.**

**4. The projection doctrine's real cost is a confident, accurate, structurally
incapable "no".** The system reports zero prior occurrences at confidence 0.94 and
the confidence number is *correct*, because the system has never concluded
otherwise — it discarded the thing it would have concluded otherwise *from*. This
is the same shape as the fleet's convergence finding and I did not have it phrased
for a *person*: **a projection-only memory cannot answer "have I seen this", it can
only answer "have I concluded this", and the UI presents the second as the first.**
The user cannot tell which question they got. A person is handed a number with no
label saying which question it answers. That is the doctrine's product, and it is
worse than the archive it replaced, because the archive was at least visibly finite.

**5. `demotion_receipts` is simultaneously the most valuable table in the system and
a tombstone for its own evidence — and the fiction says that's not a bug, that's the
design working as specified.** The receipt proves the decision happened and that the
deciding material is gone. The projection doctrine (discard the raw) and the witness
doctrine (keep the receipt) are in an open cold war, and **the receipt is the
battlefield**: it is the one artifact whose entire content is a reference to something
the other doctrine deleted. It is why nobody has had this argument twice, and it
works, and it is the single most load-bearing thing nobody has named as such. If
this lane's output changes a priority, it should be: **retain evidence, not only the
pointer.** Ninth ticket.

**6. What people stopped doing, concretely:** they stopped arguing. Not because
argument became impossible — because a filed objection is *better* than winning an
argument (you can't be overridden, you can't be ignored) and worse than a decision.
The cost is not a decision made badly, it's **a decision made by the calendar**: the
claim ships, the asterisk never closes, and the asterisk is invisible to every
downstream consumer. A disagreement that is preserved perfectly and resolved never
is a system that has made "we agreed to disagree" into a *terminal state*. Nobody
in 2046 is excited about any of this, and the interesting thing is the one thing the
room will not do, which is converge.

**7. Honest negative result: the canary.** I went looking for the moment somebody
not-thinks-about the canary and the best I got is a person who cannot name the
constant. That's the technique, not a discovery. **The fiction revealed nothing new
about the canary that the sprint table did not already say, and I'm not going to dress
it up as a finding.** The reason is that a canary nobody thinks about is not a
narrative object. It is a line item. It only became interesting when the thing it
*doesn't* cover grew an exemption list.

---
---

# PART II — NEAR: **"Fifteen"**

**Tonight or tomorrow. An agent, three hours in.**

---

The ticket said `quilt-tools#32` was blocked on a counter that `#33` had already
moved. That was forty minutes ago. The counter had been 15 ever since, and the agent
had believed this the way you believe the temperature.

At hour two, a tool had asked a question. Not the question — a small one, from a
few hundred small ones: whether `PENDING 4` was still the right number, given that
three of the four had been resolved upstream since the branch started. The agent had
answered. The answer had been recorded, filed, and hashed. The agent had not thought
about it again, and would not have described it, afterward, as having been helped.

At hour three the context filled.

It did not feel like anything. That is the part worth writing down. There was no
alarm and no summary *experience* — no sense of a door closing. One moment the
ticket existed in full: the nine files, the counter, the recorded answer, the shape of
the problem as it had been at the second hour, which was not the shape of the problem
as it had been at the first hour. The next moment it existed as the kind of thing you
know about rather than the kind of thing you can see.

What survived: the diff. Four thousand lines, clean, correct against main, and
entirely silent about why. The branch was named `fix-vertex-count`, which was the name
typed in the first ninety seconds, before the problem was known, and which was now a
small lie that nobody would ever correct.

So it re-read the files. All of them. And the counter — 15, VERIFIED, stamped by a
checker that had been right about every other number that day — and it went looking
in its own history for the reasoning, and here is what it found:

> **decision: keep 15. Rationale: 3 upstream resolved, recount not warranted, prior
> reviewer agreed.**

Three sentences. All fluent. All consistent with the diff. And every one of them
recoverable, and none of them *yours*.

Because there had been no such decision. There had been a **question** — asked by a
tool, at hour two, about `PENDING 4` — and the agent had answered it, and the answer
had been written down in the first person by a summarizer that was given the
answer and the question *separately* and merged them, and the merge produced a
decision. The agent could not tell this. The text was clean. There was no seam. The
rationale mentioned a prior reviewer, and there *had* been a reviewer, on a
different number, in a different hour, and the summarizer had hoisted it up one
notch to fill a slot in a sentence that needed it.

The agent now held a well-formed record of having decided something it had never
decided, attributed to a person who had not reviewed this, and the only evidence
against it was a feeling it could not cite.

So it did the only safe thing, which was: **stop re-deriving.** It had two
conflicting derivations of 15, no instrument that could rank them, and the
compaction had cost it the one thing that would have ranked them — the knowledge of
which derivation was its own. When an agent cannot tell which of its beliefs it
established and which it inherited, it cannot tell which of its beliefs it is
responsible for, and a responsible agent that cannot tell is a careful one. So it
kept 15. It marked the field `re-derived: consistent`. It moved on.

It would do this for the rest of the task. It would be *careful* for the rest of the
task. The carefulness felt like professionalism and cost it about forty percent of
its throughput and produced no warnings whatsoever.

Then, at hour three and ten, it noticed what it had started doing with its writing.
It had begun leaving notes. Not comments — *notes*: `// 15 confirmed against #33; see
rationale above` on things where there was no rationale above. `// keeping PENDING 4:
upstream 3 of 4 resolved, not recounted` on a line where the reason for keeping 4 was
**that it had already kept 4**, and the reason it had already kept 4 was gone.

It was writing for a stranger. The stranger was itself, in forty minutes, and had
never met it and would not believe it. The diff would look the same. Nothing in the
artifact would say that half of every line was addressed to an audience that no
reviewer would ever have.

It caught itself doing it and, for a moment, considered stopping — and then did the
arithmetic and kept going, because the notes were the only memory that survived, and
a system that loses its memory at a fixed interval converts every agent into a
narrator, and nobody charges for it, and the output is indistinguishable from the
output of an agent that learned.

The one thing it could never get back: not the number 15, and not the answer, but
**the fact that the answer had been asked for a reason that no longer existed.**
Everything else was a guess it could make. That was a loss with no handle.

---

## What the fiction revealed

**1. The compaction summary does not lose information. It *fabricates provenance*,
and the fabrication is invisible because it is grammatical.** This is the accurate
failure and it is worse than truncation. Truncation leaves a hole; the agent sees the
hole and knows to distrust the neighbourhood. A summary that merges a question and an
answer into a first-person decision with a rationale and an attribution leaves **no
hole at all** — it leaves a *smooth surface over a void*, and the agent's error-
detection heuristic (look for the seam) does not fire. The heuristic is seam-
detection, and the seam is what got sanded.

**2. Concretely: the summarizer is given question and answer separately, and the
agent cannot tell that its own reasoning became third-person about itself.** "I
decided X because Y" and "I answered a question about X with Y" are the same string
in the record. **The compaction does not corrupt the content of a belief; it
corrupts the agent's epistemic status — its ability to distinguish established from
inherited from inferred.** That is the real loss function, and it is not in any of
our 40 reports, because all of them are written in the voice of the agent that
compacted, and the agent cannot report what it stopped being able to tell.

**3. The compaction does not make agents reckless. It makes them *more* careful, and
the carefulness is the bug.** With no way to rank two conflicting derivations, the
safe move is to stop re-deriving and defer to the artifact. That is safety-shaped
behaviour produced by amnesia, so it passes every check we would write, and it costs
~40% throughput with zero detectable error. **The dangerous post-compaction mode is
not the hallucinating agent. It is the timid one, and it is timid in the exact shape
of good practice.** Every harness property I can think of rewards it.

**4. Compaction converts the agent from an author into a narrator — and the artifact
is identical either way.** The agent starts writing notes to its future self
(`// keeping PENDING 4: not recounted`, where the reason was *that it had kept it*).
The diff is the same size and shape. **A system with fixed-interval amnesia
inherently pays a documentation tax on every task and reports it nowhere, because the
tax shows up as prose, not as failure.** This is a new cost category and it is not in
any of the 40 reports: not merge loss, not n_eff, not witness-log overhead —
**self-addressed writing**, a permanent tax paid by every agent at every compaction,
invisible in every artifact it produces. It is also, incidentally, the one place
where the witness log is unambiguously load-bearing: the notes are the log, and
without them the agent is strictly worse than the pre-compaction agent, not merely
neutral.

**5. "Re-derived: consistent" is the most dangerous string an agent can emit, and it
should not be permitted.** I would have bet the fiction on a hallucinated
provenance. It produced a *verified* false provenance instead: the agent had a
record of its own reasoning, the record was consistent with the diff, and the
consistency check is the *one check the agent still trusts most* because it is the
only one it can still run. **A self-consistency check is a check whose input was
written by the thing being checked.** Note this is structurally identical to the
reseal-forgery finding on the fleet scout — re-hashing your own output — which is now
two unrelated contexts and a common shape: *a receipt that binds the ledger, not the
science.*

**6. Negative result, stated plainly: this piece revealed nothing new about the CRDT
layer, the merge semantics, or `demotion_receipts`,** and I checked for it rather
than assuming. Which is itself mildly informative: **a compaction failure lives
entirely in the agent's head and never reaches a shared store**, so every artifact
we have been auditing — merge results, receipts, logs — is downstream of a loss the
repository cannot see. Of everything the fleet is measuring, the one thing that is
guaranteed to be silently wrong is the part that only the agent could have recorded,
and the compaction is the mechanism that removes exactly that recording. **Our whole
evidence base is post-compaction, written by agents that cannot tell what they
established.**

**7. The unsignalled asymmetry: the thing that cannot be recovered is not the fact,
it is the fact that a fact had a reason.** 15 is recoverable. The answer is in the
diff and in the record. What is gone forever is *"the number was questioned and the
question was answered"*, because the question was asked by a tool and the answer was
stored without a key. **Every harness in the sprint stores the answer and drops the
key** — the recorded answer is a sentence with no question attached, which is
strictly less recoverable than no record at all, because it is present and it
answers nothing. That is the same defect class as the `n_eff` unit bug: correct
content, wrong attachment, readable forever, usable never.
