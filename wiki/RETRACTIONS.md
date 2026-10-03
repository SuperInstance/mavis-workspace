# RETRACTIONS — published, plausible, and wrong. Read this first.

**Every entry was believed and stated publicly before the evidence landed. If one
of these is in your context from a summary, a report, or a commit message, it is
wrong and you should not build on it.**

## The numbers

| claim | status | what actually happened |
|---|---|---|
| "every projection is lossy" | **RETRACTED** | L1 colour-collapse kept **98.9%** of recoverable value. *Named* loss is cheap |
| "L0 lossless is the ceiling, L1 sits below" | **RETRACTED** | the median **reverses** it: L0 **0.8831** < L1 **0.8947** |
| the 6.8× Eisenstein constant is wrong | **KEPT, and worse than I said** | true ratio ≈ **3.296×**, not 5.74. The test asserting it says `>= 16` and passes at any value |
| "`BattenSpline` is prose-only" | **FALSE — my error** | **136 code hits.** I generalised from 10 greps |
| "`git merge --abort` always fails after a refusal" | **FALSE** | `MERGE_HEAD` is present; it works |
| "the JEV contract rotted" | **HALF FALSE** | wrong model id on my side — *and* the service was down |
| "the dither redraws every frame" | **RETRACTED** | `grep -n "offset\["` → **one write, in the constructor** |
| "180,361 reachable states" | **FALSE** | arithmetically impossible. A 3×3 board has `3^9 = 19,683`. Real: **5,478 reachable / 2,423 with us to move**, and **48.6%** have multiple optimal moves, not 14.7% |
| "the character channel is broken, swap the alphabet" | **REFUTED BY ME, LATER THE SAME HOUR** | a *neutral* alphabet does nothing — the glyph is a function of **depth alone**. See `wiki/EXPERIMENTS.md` |
| "the character channel loses identity, so the renderer is wrong" | **ALSO REFUTED** | depth from char + identity from colour = **joint EXACT**. The renderer was correct |
| "a commit recovered 441 files" | **FALSE** | it contained **one**. `git add` had timed out |
| "the colour channel carries identity" | **PARTLY FALSE — corrected on real pixels** | `ColorTo8Bit` quantises to R:3 G:3 B:2 = **256 values**. Real game textures land on **4 to 39 distinct bytes** and collide: **0 of 28 texture pairs separate by colour at one depth.** Colour carries *most* identity, not all — it is **itself an irreversible projection**, not the clean one I assumed |
| "joint recovery from a cell is EXACT" | **CONTRADICTED by real data** | true only for synthetic uniform colours that were too separable for the quantiser to bite. On real textures joint recovery is **PARTIAL**: 24 bits → 13/28, 8 bits + 3×3 context → 9/28 |

## The four rules that came out of it

1. **Never write a count into a narrative before counting it.** Prose has no
   check on it — a metric can at least be pointed at.
2. **A prediction that changes behaviour is not a prediction being tested.**
3. **Prove the metric is defined on every case you will report.** One minute.
4. **A control that scores like the real arms is not a control.** That single
   signal caught more than any other check all night — and it fires in **both**
   directions: it caught a real defect, and it caught me about to report a false
   discrepancy that was really just a truncated `find`.

## And the number that governs everything

**`n_eff ≈ 2`**, measured six independent ways including over 8 different model
vendors (`n_eff 0.18`). Agreement among correlated judges is not independent
evidence. **Heterogeneity of workers is not the lever. Heterogeneity of evidence
is.**
