# R2 — PAYOFF: what JEV gets you that a local model does not

Status: STUB (written 2026-10-02 ~17:20Z, before measurement).
Lane: EXPERIMENTER. Question: is "a network of JEV calls is a neural network whose
neurons are judgments" a capability or a rename?

## HYPOTHESIS (falsifiable, stated before data)

**H1 (sarcastic reading, the orchestrator's prior):** JEV's distribution is
(a) reducible to a scalar in nearly all cases — argmax and confidence are
coupled, and the whole map is dominated by the argmax — and (b) loses to a free
lexical/statistical read of the same input on every task where a correct answer
exists in this account's own documents. Therefore "neurons are judgments" is a
rename: a network of deterministic units is a decision procedure.

**H2 (the live rival — achimala/jev-paint):** the value is NOT judging, it is
the SHAPE. `probabilities` carries information a scalar loses, and the only
system in this account that exploits it uses per-pixel entropy as a *physical
dial* rather than a score. So the capability is: JEV supplies a cheap,
input-conditional CONTINUOUS dial over a discrete question, usable as a control
signal. A local model produces a label; JEV may produce a graded position.

**H3 (the one I am most likely to miss):** there exists at least one task where
JEV wins a free statistic, and it is a task where the answer is NOT in the
documents — i.e. out-of-corpus generalisation under a fixed small state budget,
where the free statistic has nothing to retrieve and JEV has priors.

## THE CONTROL THAT FALSIFIES EACH

- **F1 kills H1's distribution claim.** Ten prompts x N phrasings x N state
  wordings x N option orderings. If argmax flips < K and the map's rank-2 mass
  stays below threshold, the distribution is a costume. Concretely: measure
  |probabilities| ordering agreement with `choice` across ALL rephrasings, and
  measure confidence-vs-argmax-prob coupling. Pre-registered kill: if entropy
  is a deterministic function of argmax probability, H1 stands.
- **F2 kills H2.** Take a fixed corpus question set where ground truth is
  checkable in code. Score JEV (choice + argmax-prob, best-case read) against
  the free statistic on the SAME inputs. If JEV does not win at least one
  prompt at n=10, H2's "capability" is reclassified as "presentation".
- **F3 kills H3.** Out-of-corpus probes with no lexical overlap with the
  documents. Free statistic has nothing to retrieve; if JEV still loses there,
  H3 is dead and the honest answer is "not much".
- **F4 is the negative control.** A confident, well-formatted, WRONG judge must
  make the harness REFUSE, not score. The previous lane's metric could not
  return non-zero; mine must be forced to a non-zero exit by a wrong-but-
  confident answer. If the harness passes a rigged judge, every number above is void.

## METHOD COMMITMENTS (held regardless of outcome)

1. Counts, not percentages, at n=10. Paired: same 10 prompts for JEV and baseline.
2. `UNVERIFIABLE` for transport failure. A 503/EOF/timeout is retried, then
   recorded as UNVERIFIABLE — never as a wrong answer. Counts are over VERIFIED only.
3. Every number reproducible by a named command.
4. No credential is ever printed. Only `${TYPESAFEAI_KEY}`.
5. No GitHub pushes.
6. Prompt bank: 10 prompts about THIS fleet, each with an answer checkable in
   code. No uncheckable prompt enters the bank.
7. Shuffle control on every choice question, per JEV-CONTRACT.md: the
   `probabilities` map is the object of study and option order is a confound.

## STATUS
- [x] stub written
- [ ] live 200 on the recovered contract
- [ ] 10-prompt bank built + ground truth computed in code
- [ ] free-statistic baseline
- [ ] distribution characterisation (F1)
- [ ] negative control (F4)
- [ ] out-of-corpus probe (F3)
- [ ] verdict

Note: /workspace is NAS-backed. All scratch work in /tmp, and every file written
to /workspace is `stat`-verified for non-zero size (exit codes lie on this mount).
