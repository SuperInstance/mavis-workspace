# Three collisions

Each piece takes a measured result and a piece of doctrine and puts them against each other.
The pieces are meant to disagree with something. Where a number appears, it is one I ran
tonight or one already in the repo; the checkable ones are marked.

Not pushed. Nothing outside this file was touched.

---

## 1 — Zero

4×4 four-in-a-row. Complete tree, 3,338 positions, longest game nine plies, every ply from
ten on empty. Value: `0`.

I asserted `+1` into the known-answer check before establishing it. My solver said `−1`. Both
were wrong. A retrograde table over all 161,029 reachable states and a plain max-min with no
negation both say `0`, and they agree with each other on every random legal position you
throw at them. `python3 verify_maxmin.py` in `projects/ga4444` still says `0`. I ran it while
writing this.

The oracle is heard, not consulted. I did the other thing. A known-answer check is a
consultation: you type in the note you expect the fork to sing, and when it sings something
else you assume you have turned it wrong. I was one edit from assuming that, permanently. The
only reason `0` survived is that the second instrument was too weak to be flattered — the two
wrong answers cancelled instead of one being edited into agreement with the other. That is not
validation. That is luck wearing a citation.

So the check should not be "the answer is X." It should be "here is the denominator." The
retrograde table has one: 161,029 states enumerated, empty board reads `0`, and the first move
cannot change it, because all four one-ply positions read `0` too. My assertion had no
denominator. A negative result with a count is a fence. A negative result without one is a
mood.

Then the datum nobody wants. On a board where the game is a draw, **the break never happens.**
Nobody loses. Where the boat broke is where the fish are, and there is no boat; the honest
reading is not to invent one. What the dataset holds is a complete negative — 3,338 positions
in which nothing occurs, and not even a good opening exists. Every signal the triage runs
flags a *missing* thing: hollow, stub, no licence, failopen. A file that is entirely intact and
whose every line says `0` scores healthy on all of them. **The census cannot see a null.**

---

## 2 — Additivity

A linear 9×9 map reaches 0.7148 where a depth-16 tree reaches 0.7879; on the
single-optimal subset, 0.5708 against 0.6793 — the 0.840 everybody quotes. So 0.1807 against a
0.1431 floor was never "neural nets are bad at minimax." It was "a linear map is bad at
minimax," a statement about arithmetic.

A 9×9 map is a sum of independent per-cell votes over 81 numbers. It can hold a value at a
cell. It cannot hold one that is not at a cell — and "two of my lines are one stone from
completing" is a count, and a count has no location. **The tree's edge is not a scar. It is a
scratch pad.** Its nodes name facts that correspond to nothing on the board, and a tree can
name one only because a node is not a place.

Split the 2,423 positions by COMPOSEDness — two or more of your own threats. The tree closes
55.5% of the headroom on SIMPLE and 56.7% on COMPOSED: no penalty. The linear map closes
39.7%, then 22.6%, losing about 43% of what it had. The penalty is a property of the plus
sign. Minimax is not beyond these models; it is beyond *this representation*, and the
difference is one scratch pad and no extra parameters.

That puts grown-versus-designed in a bad spot. The 617-parameter layer is the designed
object; the tree has a hand-chosen depth. "Grown" is the industry's word for more parameters,
and that is what a shape someone picked gives you. The grown thing reached 0.907 of the
ceiling; the designed thing scores 1.0 by construction — evidence of nothing except that it
can express the answer.

The ties die of the same reduction. 1,177 of 2,423 positions have more than one optimal
move; 456 have three, 116 five, one all nine. A tree hands you the set for free: a
probability over branches. A linear map hands you nine numbers and someone argmaxes before
anyone scores it. The old metric showed this by accident: scoring against `min(optimal_set)`
gave a *random* floor of 0.6927. A coin scoring 69% is not a weak baseline; it is a broken
instrument flattering itself.

Both failures are one reduction: a single value per place, selected by argmax. A cell is a
scar, not a parameter — fine. A position with nine correct answers is not that kind of cell.

---

## 3 — It still says it *(check this one)*

180,361 on a board with 19,683 states. I would like to report it fixed; it is not, and not
being fixed is worse than the bug.

```
cd projects/pie-minimax
python3 -c "from minmax import enumerate_reachable as e; p=e(); print(len(p), len({b for b,_ in p}))"
# 180361 2423
```

`minmax.py:101` returns 180,361 rows for 2,423 boards. It counts move *paths*, not
positions; the dedup is one file away, at `ceiling2.py:36`. Careful callers are right;
importers are wrong. Worse, `CEILING.md:14` — *"The real figures, from
`minmax.enumerate_reachable()`"* — is the document reporting the bug, citing the function
that still has it. Trust the citation, run the command, get the old error with a footnote.

The sentence is the bug. "180,361 reachable our-turn states" appears at
`pie-minimax/README.md:29` as a true fact and at `docs/LANES.md:198` as the false number being
corrected. Byte-identical. Nothing says which survived contact with a board. The witness log
is meant to be a prediction, not an archive — but that separates future from past. Tonight's
axis was **asserted against checked**. The log has no column for it.

`enumerate_reachable` carries a confession about an earlier version of itself: one that
played only our side and *"returned exactly one state — the empty board — while reporting no
error."* A note about an instrument that cannot overcount, attached to one that overcounts by
4.6×. Both true, same file.

`repos/ladder/ascii_3d_engine.py` has the same defect in three lines: `z_buffer` appears
three times in 183 — allocated 65, read 76, written 77, all inside the vertex loop, and
nothing outside reads it. It is not a depth sorter; it is a tie-break for two vertices in
one cell that presents as the first. In `projects/connect4` a control read a closed file and
printed `OK (0 rows)`; a `src_bytes` denominator that is zero for sourceless repos flagged
106, and `recheck.log` keeps 36. **A thing that runs, is believed, and gates nothing.** The
control that catches all of them is the one nobody writes: not "does this pass" but "what is
the denominator, and who read the rows I skipped."

The count is one line — return the dict, not the list. Not my file; I left it. The family
fix is not a line: a fence only works if someone leans on it, and 3⁹ = 19,683 was checkable
in your head and stopped nothing.
