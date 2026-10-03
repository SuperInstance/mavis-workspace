# café Δ 日本語

*They spelled it wrong on the way in. Nobody noticed for eleven months.*

---

The string is eight characters long. It is the shortest thing in the building and
it has outlasted two refactors, a language migration, and a man named Sung who
left in March.

```
café Δ 日本語
0x24a555471370b18d
```

That is the whole of it. A little accented letter, a Greek capital, three
Japanese characters, hashed once by a function invented in 1970. The number
underneath is what it must be. Sixty-four bits of insistence.

Here is why there is any insistence at all.

Eleven months ago, a well-meaning tool walked through every file in the
repository and normalised the text. This is what tools do. This is what they are
for. It found the accented letter and, being helpful, being correct, being
unable to tell the difference between *tidying* and *changing*, replaced it.

The build went green. Every port agreed. Eleven implementations of the same
idea, in a language nobody had heard of, running on hardware that could not
afford a surprise — and all eleven of them agreed, unanimously, on a string
that was no longer the string.

Because the canary did not fail. The canary *passed*.

Here is the shape of the mistake, because it is the shape of all the mistakes:
the test asked *"does the function compute a hash?"* and the function did. The
function has never once been wrong. It was handed something else and it hashed
that thing correctly, with great speed, for eleven months, and every port
agreed, and agreeing is exactly what a panel does.

The pin was never live. Somewhere back when the ports were written, a test was
added that compared a constant to a constant. It could fail if you deleted the
constant. Nothing in the universe could make it fail otherwise.

## What fixed it was not clever

It was a person — a person, later, reading a diff for no reason at all — who
typed the eight characters into a separate program and got a different number,
and then said the sentence that does the actual work:

*the pin doesn't build the thing.*

Not: *the pin is wrong.* Not: *the hash function has a bug.* The pin is
correct. The pin is a tautology wearing a warning label, and it had eleven months
of unanimous agreement behind it.

So they changed one line. The canary now constructs the thing it certifies,
feeds it the string, and reads the digest back out of the object rather than out
of a literal. It fails now. It fails *loudly*, and it fails on the first night,
because the first night is the night the accent comes back.

## The part nobody expected

The two repositories that had no canary at all were the ones that were correct.
Not by discipline. By luck. One of them had never been touched by the
normalising tool, because it lived in a directory the tool skipped, and its
author had spelled `café` with the accent out of habit rather than out of
policy, the way you spell a name you have been saying out loud your whole life.

**We built the fence and then forgot that a fence is a thing you maintain.**

There is a version of this story where the lesson is *add more tests*. There is
a version where it is *be more careful with your tools*. Both are wrong, and
both are the reason the pin was dead for eleven months while everybody agreed.

The lesson is smaller and colder than that. **A check that cannot fail is not a
weak check. It is a signal, and it is the same signal in both directions.** It
says *nothing broke* in exactly the tone it would use to say *something broke*,
and a building full of honest people will believe it, because believing a green
check is not stupidity. It is what green checks are for.

Eight characters. An accent. A Greek letter. Three Japanese characters.

Somebody spelled them right, on purpose, and that is the entire load-bearing
structure of the thing.
