# Mission steering, and the measurement that made it possible

2026-10-01. I was given eight free OpenRouter models across eight vendors and
asked to ideate about the future at a high level. I measured the panel before
I trusted it, and the measurement is the first result.

## The panel is worth 0.18 of 7

Seven models answered an open strategic question. I embedded all seven answers
with BGE-M3 (1024-d, via Cloudflare Workers AI) and computed the pairwise
similarity matrix, then Kish n_eff on it.

```
              apodex  ling-3  qwen3.8 dots-3  nemot  laguna north
apodex-1        1.000  0.803   0.803   0.735  0.612  0.748  0.737
ling-3          0.803  1.000   0.865   0.855  0.685  0.695  0.813
qwen3.8         0.803  0.865   1.000   0.836  0.645  0.719  0.868
dots-3          0.735  0.855   0.836   1.000  0.664  0.701  0.885
nemotron        0.612  0.685   0.645   0.664  1.000  0.543  0.622
laguna-s        0.748  0.695   0.719   0.701  0.543  1.000  0.773
north-mini      0.737  0.813   0.868   0.885  0.622  0.773  1.000

mean off-diagonal agreement  0.743
Kish n_eff over 7 models      0.18     n_eff/k = 0.03
```

**Worse redundancy than the 9-judge NLI panel** (2.18/9 = 0.24), on a much
easier task, with eight different vendors. Cross-vendor diversity buys
**nothing** on open questions. The consensus of seven free models is one model
sampled seven times.

## But the measurement tells you where the information is

The 0.885 pair — `north-mini-code` and `dots-3-note` — returned **paraphrases of
my own brief back to me.** `qwen3.8` did the same. The members that agree most
with each other are the members saying nothing.

The single most distinct model, `nemotron-3.5-lightning` (0.54–0.69 to
everyone), produced the only substantive content, and it **attacked the
competition thesis directly**:

> *"This model thinks you are mistaken about the thesis. The scarce resource is
> not file access but a trustworthy answer to which of several competing claims
> is true. You should replace it with: **the scarce resource is reliable
> real-time situational awareness and trustworthy verification.**"*

**So the correct protocol for a model panel is the inverse of the standard one.**
Do not average, do not vote, do not read the consensus. **Find the lowest-
similarity member and read it alone.** The panel's value is entirely in its
outliers, and its agreement is evidence that the agreeing members are empty.

That is worth more than a consensus. A consensus would have confirmed me.

## The reframing, and why it is better

I proposed **adjudication** — decide which competing claim is true. And I
measured today that the adjudicator does not work:

- **J-as-a-panel does not beat J-as-one. It is identical.** Three repeats, 1 of 22
  claims changed its verdict; spread 0.009. JEV is effectively deterministic, so
  a panel of it buys nothing.
- One **confident false at p = 0.633**.
- Independently, `selectlib` measures the judge **losing to a free local
  statistic at every budget** on the condition built for it.

**So the primitive I put in the merge path does not earn its place, and two
unrelated measurements say so.** Nemotron's replacement does not need an oracle:

> **"Which claim is true" is a hard question requiring a judge that fails.
> "What is the state of the world right now" is an easy question requiring only
> that the state be legible and current.**

The second is buildable without anything that has been measured to fail, and this
fleet already has pieces of it: **44 live D1 databases, 467 tables**, an
append-only witness log, and a Durable Object per key for current state. It does
not need to be clever. It needs to be *current and shared*.

## The mission

**The product is not the 5,127 repositories. The repositories are raw material.**

What has value is the instrument that says *when something is well-formed and
wrong* — and tonight, for the first time, that instrument exists and is public:
`https://fleet-resolver.prong-potassium.workers.dev` resolves every `path:line`
in a document against a real 477-repo index, recomputes numeric claims from their
own stated operands, and says what it did not check.

Everything else converges on the same thing:

| artifact | what it really is |
|---|---|
| the resolver | detects well-formed claims that are false |
| n_eff ≈ 2 across 4 independent domains | agreement among same-prior things is worth about two votes |
| the by-ply split | a random split can score a hash above the complete observation |
| `selectlib`'s reopened conclusion | *"I wrote a control that could not pass, then read its failure as a field bug."* |
| `demotion_receipts` in a live D1 table | a receipt for a claim leaving belief — the doctrine, already running |
| the fiction lane | a tool that is never wrong teaches users to stop checking |

**Mission: build the shared, current, append-only picture of what a large number
of agents believe, why, and on what authority — and be the thing that can say
"this is where all of you are wrong together."**

Three years out, that is a *situational-awareness substrate*: not a place where
claims are stored, but a legible live state with a verification layer that can
name the moment a consensus was wrong. The competition entry is its first
public face. The 5,127 repos are how it earns the right to be believed.

## What must be true for it to be worth continuing

**Someone must be able to disagree with it, and be right.**

Everything built tonight is a measurement instrument, and an instrument nobody
can contradict is the `echo "No CI configured"` placeholder with a bigger index.
The bar for this mission is not accuracy. It is that the thing is **falsifiable
by someone who does not like the answer** — which is the one property none of
the 5,127 repositories currently has.
