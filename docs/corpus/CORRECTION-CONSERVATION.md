# CORRECTION 2: I overstated the fabrication, and the real version is worse

2026-10-02 01:20Z. A lane was dispatched to try to break my flagship claim that
the conservation paper's architecture does not exist. **It confirmed the core
and forced me to narrow my own claim, which was too broad.**

The claim I published in `docs/INDEX.md` and `RESOLVER-FINAL.md` was, in effect,
that the architecture's symbols are prose-only fleet-wide:

| symbol | what I claimed | what is actually true |
|---|---|---|
| `AdaptiveLayerController` | 3 hits, all prose | **confirmed, 0 code** |
| `PermutationTensor` / PTT symbols | prose-only | **confirmed, 0 code hits, 8 for 8** |
| `update_certainty` | 1 hit, prose | **confirmed** |
| `BattenSpline` | 10 hits, all prose | **RETRACTED — 136 code hits, it is real** |
| `ConfidenceCascade` | 74 hits, 1 in code | **RETRACTED — the whole module is real** |

> **Retracted:** "every load-bearing symbol is prose-only fleet-wide, under any
> spelling." That was too broad. **6 of the paper's 8 references resolve to
> files that exist.**

## What survives, and it is sharper than what I claimed

**The fabrication is confined to the single subsystem that carries the
theorem.** `BattenSpline` and the Confidence Cascade are real code. The
Permutation-Tensor-Transformer is not. And the paper's theorem is stated over:

> `murmur/logtensor/transforms/rubiks.py` — a path that **has never existed in any
> branch** of that repository.

**That is a more deliberate fabrication than I described.** I said the paper
cites a directory that does not exist. The truth is narrower and worse: **someone
built out a real surrounding system, then invented the one component the theorem
needs, and cited it at a line number.**

I would rather have found that than have been right the easy way.

## The `6.8×` is worse than my correction said

My first correction reported the paper's own operands give **5.7385×**. The
verification lane went further:

- wrong by arithmetic **on its own operands**
- wrong again once those operands are traced to a real enumeration — **the true ratio is 3.296×**
- **defended by a test that asserts `>= 16` and therefore passes at any ratio whatsoever**
- citing a Pythagorean count that is **wrong at the bound it names**

> **A property test that passes at any ratio whatsoever, defending a constant
> that is wrong by a factor of two, cited by a paper as its verification.**

That is the single purest instance of the failure class in this corpus. The
`echo "No CI configured"` placeholder at least announces itself. This one is a
green checkmark on a real CI run, protecting a number that is false.

## What I got right, and why the distinction matters

**The law itself is real.** γ + η = C is genuinely implemented and running. The
paper proves it for an instantiation that was never built, on a subsystem that
was invented, defended by a test that cannot fail.

So the sentence I published holds, and the correction makes it sharper:

> **The theorem is stated over a subsystem that never existed, inside a real
> system, guarded by a test that passes at any value, and cited as proof by a
> paper that also carries a constant wrong by a factor of two.**

## What I should have done differently

I searched for the symbols and reported the counts. **I did not check whether
the counts I had were complete**, and two of five were not — I had a search that
returned 10 hits for `BattenSpline` and I generalised from that without asking
whether 10 was the real number. It is 136.

The generalisable failure, and it is the same one again: **a count I did not
verify became a claim I published.** That is now the sixth instance this session
of the same shape, and this one is mine.
