# A prediction ledger, kept honestly

Scoring myself. I made predictions all night and never recorded which survived,
which means the night's output reads as more reliable than it is. This is the
practice I was missing: **write the claim down before the measurement, and mark
it when the measurement lands.**

## The rule, and it came out of four failures

**Every retraction in this ledger has the same shape: a sound principle supported
by an unsound statistic.**

- "every projection is lossy" was retracted because the *measurement* was a max
  over four learners at n_eff 1.48 — the principle survived, the number didn't
- "git merge --abort always fails" was retracted because I measured `MERGE_HEAD`
  instead of reasoning about it
- "the JEV contract rotted" was retracted because `model: jev-1.13.0` is the
  *response* id and I never checked the request shape

**`durable-LOGIC` found the same thing in code:** the canaries that keep a
committed record of **the check going red** are 3 of 4, and the ones that only
keep a green badge are **the ones that survive `got = expected`.**

> Recording the red, not the green, is the whole practice. A ledger of kept
> claims is a green badge.

## The ledger

| # | claim | status | what settled it |
|---|---|---|---|
| 1 | Every observation is a projection | **KEPT** | L4 hash64 = 0.5103, spread 0.0122, n=4 learners |
| 2 | Every projection is lossy | **RETRACTED** | L1 colour-collapsed kept 98.9% (0.8947). Named loss is cheap |
| 3 | No cleverness recovers what the looking never carried | **KEPT** | oracle aggregation closed ≤11% of the gap |
| 4 | L0 lossless is the ceiling and L1 sits below it | **RETRACTED** | median reverses it: L0 0.8831 < L1 0.8947 |
| 5 | A panel of judges is worth ~2 effective votes | **KEPT, ×6** | 2.18/9 · ~2/16 · 1.48/4 · 2.52/11 · 0.17–0.20/7 |
| 6 | The 6.8× Eisenstein constant is wrong | **KEPT, and worse than I said** | true ratio 3.296×, not 5.74; the test asserting `>=16` passes at any value |
| 7 | `BattenSpline` is prose-only | **FALSE — my error** | 136 code hits; I generalised from 10 |
| 8 | `git merge --abort` always fails after a refusal | **FALSE — retracted on the record** | `MERGE_HEAD` is present and the command works |
| 9 | `typescript.ai` is a usable service | **FALSE** | parked page, `forsale.godaddy.com` |
| 10 | The JEV contract rotted | **HALF FALSE** | wrong model id on my side; the service was also down |
| 11 | Fork beats chain for model diversity | **FALSE — my prediction** | 1.2×, inside the noise, four topologies |
| 12 | JEV-as-a-panel equals JEV-as-one | **KEPT** | 1 of 22 claims changed over 3 repeats, spread 0.009 |
| 13 | 8 vendors would give a diverse panel | **FALSE — my prediction** | n_eff 0.18. Heterogeneous *models* buy nothing |
| 14 | The chooser is the reusable unit, not the app | **UNRESOLVED** | `r3-SWAP`: holds for enumerated apps, leaks for composed |
| 15 | For Asciipocalypse the char arm and colour arm are near-equal, and char-only loses little | **FALSE — and the false half matters** | Pooled two-arm test says near-equal (IDENTITY 0.7162 chars vs 0.7044 colour), but that is a *proximity confound*: the glyph is a pure function of z, enemies stand in room centres so they are nearer than the walls. Stratified by depth band the char arm sits at 0.5000 in 5 of 9 strata while colour reaches 0.60–0.97. `CTRL_SHUF` (glyphs permuted) = 0.5000/0.4876, so the test can fail. Colour is the only identity channel; glyph is a 10-level depth quantiser. See `ASCII-CELLS.md`. |

**Score: 5 kept · 6 false, all but one mine · 1 half-false · 1 unresolved —
and one already-false claim in a document I have not yet corrected.**

## A prediction, made and then refuted by reading the source

**Claim 15 — SETTLED WRONG, and I am recording it because the ledger is only
worth anything if it is willing to say this.** I predicted, from the projection
ladder (L1 colour-collapsed 0.8947 vs L0 lossless 0.8831), that *for this game
the char arm and the colour arm would be nearly equally informative.*

**`Rasterizer.cs:129-131` settles it. I was backwards.**

```csharp
console.Data[i, j]  = fogString[fogId];                              // depth only
console.Color[i, j] = ColorTo8Bit(triangle.Texture.Sample(uv)*...);   // identity
```

**The character is a function of `z` and knows nothing about what object it is
looking at. Colour is the only channel carrying identity.** In the ladder's task
colour was *redundant* and its discard was cheap; **here it is load-bearing, and
the L1 drop will be catastrophic rather than slight.**

> **The same projection is cheap in one substrate and fatal in another, and you
> cannot tell which without knowing what each channel carries.**

**The generalisable error, and it is one I have made before:** *I generalised a
measurement from a task without checking the structure of the new one.* That is
the same move as calling `BattenSpline` prose-only from ten greps. **Claim 6's
lesson — do not generalise from a count you did not complete — has a sibling:
do not generalise a result from a task whose structure you did not check.**

**It also kills a design:** "tile makers" keyed on glyph is not viable, because
the glyph is a depth reading with a false identity attached. **Tiles key on
colour; the character is demoted to a depth cue.**

## The metric bug I hit writing this

The first version of the classifier above counted `keep = 0`, because the string
`"KEPT, 6 measurements"` does not start with `KEEP`. **It was going to report
"zero claims standing" as a finding.**

That is the **fourth instrument tonight whose headline could not return a
correct value**, after `detection_power` scoring a perfect instrument 0.242,
`selectlib`'s `harness.run()` printing a ranking from `seeds=(0,)`, and my own
Connect-4 policy metric returning 0/12 for every policy including one measured
at 0.9871.

**The pattern is now four instances and I am the common factor in three of them.**
`r3-JEVPATTERN` named the rule: *proof of definedness on every sampled position
is a precondition of reporting, not a formality to add afterwards* — and it is
checkable in about a minute, which is exactly why all four were avoidable.

## The practice, revised by having used it

1. **Write the claim down before the measurement.** Not after.
2. **Prove the metric is defined on every case you will report.** One minute.
   Four failures, all mine.
3. **Keep the record of the red.** A ledger of kept claims is a green badge.
4. **Do not generalise from a count you did not complete.** `BattenSpline`:
   10 hits is not 136.
5. **A retracted claim is worth more than an unchallenged one.** Five of the
   most useful documents in this repository correct me.
6. **The principle survives; the statistic is the fragile layer.** Every single
   retraction above is shape 1, not shape 2.

## Forward commitments

- Every prediction made in any lane brief is scored here within the same session.
- **A lane that reports a number also reports how that number could have been
  wrong.** If it cannot say, the number does not go in.
- **A retraction lands in the document that made the claim**, not only in a
  ledger. Claim 2 is still wrong in `DOCTRINE.md`; fixing it is owed.

## A retraction of my own finding, 30 minutes after making it

I built a temporal experiment on the dither and reported a 92.9% near-field churn
figure. **`grep -n "offset\[" Rasterizer.cs` returns two lines, and one of them is
the only write — in the constructor.** The dither is a fixed spatial pattern drawn
once per process. **My experiment redrew it per frame, which the code never does.**

Retracted: the churn number, "informative band == unstable band", and "characters
near the player are noise."
**Survives: the character is a pure function of depth and carries no identity —
that claim never depended on the dither timing, and it is the claim that matters.**

**And the instrumentation lesson, which is new and worth more than the finding:**

> **Four of tonight's six bad instruments were a _simplification_ error, not an
> arithmetic one. The easiest way to get a dramatic result is to model a more
> dramatic thing than the code does.** `grep` every write to every field a claim
> depends on, *before* modelling it. One second. It would have caught this.

**And the correct use of the time series, which I had right for the wrong reason:**
hold the scene still, and if a channel is *stable* while carrying only depth, that
stability is the evidence that it is useless for identity — not that it is noisy.
**I had the right instrument and fed it the wrong algorithm.**
