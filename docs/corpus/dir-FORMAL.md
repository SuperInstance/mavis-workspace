# dir-FORMAL — language, runtimes, formal methods

**2026-10-02. Research lane. Findings + executed receipts.**
**Not a design document.** Where something is unverified, it says so.

---

## 0. Correction to my own stub, first

My 10-minute stub said the brief was wrong: *"TC1's Design section does list `tags(20)`."* **I was
wrong and the brief was right.** I had found the wrong paper. `TC1-tile-codec-384.md` is an
*experiment pre-registration* and does list tags. The paper the brief means is the formalisation,
`06-Tile-Algebra-Formalization.md`, and `papers-WHITEPAPERS.md:390` records, from a prior lane:

> **"the paper has no `tags` field at all. There is nothing in the formalisation to check either
> number against."**

So the three-way split is real: **the formal paper has no `tags` field; the crate has `tags`; the
crate's two doc comments say `tags(24)` and sum to 388 while the code writes 20 and sums to 384.**
The brief's "comments contradict each other" and "paper has no tags" are both correct and refer to
different documents. Nothing in the repo can arbitrate, because the only normative document is
silent on the question.

---

## 1. What I actually ran (receipts, not readings)

The previous lane (`docs/PLATO-LINEAGE.md` §7) wrote: *"I did not run the Rust tests — no `cargo`
in this sandbox."* I installed a toolchain and closed that gap. **Everything numeric below is
executed.**

| | |
|---|---|
| toolchain | `rustc 1.99.0` / `cargo 1.99.0`, installed this session |
| `SuperInstance/plato-tile-encoder` | confirmed **200** before citing; cloned `--depth 50` → `de8e780` |
| `SuperInstance/constraint-theory-core` | confirmed exists; cloned `--depth 1` → `df9ce63` |
| `cargo test --lib` (encoder) | **16 passed, 0 failed** |
| `cargo test` (full, incl. doctests) | **FAILED**, exit 101 |
| GitHub Actions on `de8e780` | **1 run total, conclusion `failure`, 2026-05-08T04:30:22Z** |
| `cargo test --lib` (constraint-theory-core) | **136 passed, 0 failed, 1 ignored** |
| mutation control (+1 byte) | **`error[E0080]: evaluation panicked: Tile must be 384 bytes`** |

### 1a. The crate's own CI is red, has been since 2026-05-08, and is red on the commit that added it

The last commit in the repo is `de8e780 "Add CI/CD workflow"`. The workflow runs
`cargo test --verbose`, which runs **doctests**. The doctest at `src/lib.rs:6` does not compile:

```
error[E0425]: cannot find function `decode_json` in this scope
 --> src/lib.rs:9:12
```

The doctest block at the top of `lib.rs` calls bare `encode_json` / `decode_json` / `encode_base64`
with no `use super::*;`. The API summary at the top of the file has **never compiled.** GitHub
Actions says `failure`. **Nobody looked, for five months.**

This is not the "23 workflows that cannot fail" from `TYPES-UNLOCKED.md`. It is the opposite
disease and it is worse, because it is reusable as a control: **this workflow can fail, it did
fail, and the failure was inert.** A gate that fires into a void is a receipt, not a gate.

---

## 2. The thing that is already in the fleet, and it works

`constraint-theory-core/src/tile.rs:223-226`:

```rust
const _: () = assert!(mem::size_of::<Tile>() == 384, "Tile must be 384 bytes");
const _: () = assert!(mem::size_of::<Origin>() == 64, "Origin must be 64 bytes");
const _: () = assert!(mem::size_of::<ConstraintBlock>() == 192, ...);
```

**I verified the control can fail.** Adding one `u8` field to `Tile` (size-only mutation, no type
error) produces:

```
error[E0080]: evaluation panicked: Tile must be 384 bytes
    --> src/tile.rs:224:15
```

Not a warning. Not a test failure. **`rustc` refuses to emit the crate.** Zero runtime cost, zero
CI, zero agent, zero argument. This is the strongest evidence I have for `TYPES-UNLOCKED.md`, and
it is already in the fleet, applied to **one of the two** crates that need it.

**And I measured what it does not cover.** I built a probe against the real crate:

```
size_of::<Tile>() = 384   align_of::<Tile>() = 64
  offset   0  size  64  origin          offset 104  size  64  tensor_payload
  offset  64  size   8  input           offset 168  size   4  provenance_head
  offset  72  size   8  output          offset 172  size   2  self_play_gen
  offset  80  size   4  confidence      offset 176  size   4  hydraulic_flux
  offset  84  size   4  safety          offset 192  size 192  constraints
  offset  88  size   8  bytecode_ptr
  offset  96  size   8  trace
```

The doc comment above that struct says `Padding: to 384 bytes`, which reads as trailing padding.
**There is no trailing padding.** `hydraulic_flux` ends at 180; `constraints` starts at 192. The
real padding is a **14-byte internal hole** created by `align(64)` on `ConstraintBlock`. The
`const _` assert passes anyway, because it checks the **total** and the total is correct.

> **The invariant that was mechanised is the arithmetic. The invariant that was wrong is the
> attribution. Mechanising the sum did not mechanise the meaning.**

This is the whole lane, and it is a limit, not a success.

---

## 3. The 384-byte record: what a type can and cannot hold

All executed against the real crate at `de8e780`.

### 3a. The encoder is a total function whose image is not in the decoder's domain

`encode_binary` returns `[u8; 384]`. Not `Option`. Not `Result`. It **cannot report failure**, and
it can emit bytes that `decode_binary` rejects. Executed:

```
question: 133 bytes, 131 chars
encode_binary returned 384-byte array (no Option, no Result)
DECODE *** FAILED *** -- encoder returned a value the decoder rejects
```

Boundary, measured to the byte:

```
125 ASCII + EUR (3B) = 129 bytes -> decode OK
126 ASCII + EUR (3B) = 130 bytes -> decode *** FAIL ***
127 ASCII + EUR (3B) = 131 bytes -> decode *** FAIL ***
```

`write_str` truncates on a **byte** boundary; `read_str` requires valid UTF-8. Any codepoint
starting at byte offset ≥ 126 in a 128-byte field splits, and the **entire tile** is lost. Not the
field — the tile, because `read_str` returns `Option` and every `?` propagates.

**This is the same disease as the docstring, one level deeper.** The docstring lies about the
layout. The *signature* lies about totality. Neither is visible to a type checker, and no
lint rule can see either.

### 3b. The length invariant is not enforced on the decode side, at all

`decode_binary` tests `if bytes.len() < BINARY_SIZE { return None }` — a **minimum**, not an
equality. Executed:

```
decode_binary(385 bytes)  = Some(..)   LENGTH INVARIANT NOT ENFORCED
decode_binary(1024 bytes) = Some(..)   LENGTH INVARIANT NOT ENFORCED
```

640 trailing bytes silently ignored. `encode_binary` cannot produce this, but any other producer
can, and nothing rejects it.

### 3c. Invariants live on constructors, and this type has more than one constructor

`EncodedTile::new` clamps `confidence` to `[0,1]`. **Every field is `pub`.** Executed:

```
::new(conf=5.0).confidence         = 1     (clamped)
struct-literal(conf=5.0).confidence = 5     COMPILES? all fields are pub
struct-literal.ghost_score         = -99
after encode+decode: confidence=5 ghost=-99 use_count=4294967295
=> confidence in [0,1]? false   ghost_score >= 0? false
```

The `confidence ∈ [0,1]` invariant — the one the paper calls the JEV column — **is a property of
one constructor, not of the type.** `EncodedTile { confidence: 5.0, .. }` compiles, and the value
survives a full binary round-trip as `5.0`. This is why a lint rule cannot help: the invariant
already has a home, and the home has a hole next to it.

### 3d. The codec is not injective, silently

`tags` are joined with `,` and split on `,` with **no escaping**. Executed:

```
tags ["alpha,beta","gamma"] -> ["alpha", "beta", "gamma"]   (2 tags in, 3 tags out)
```

Two tags become three, silently, and the record is a tabulation whose row count changes under
round-trip. **The 16-test suite does not catch this** because `test_binary_preserves_tags` uses
`["a","b","c"]` — no comma. This is a *semantic* invariant (`tags` round-trip identity) violated
by a real input, missed by a green suite, in a crate whose own tests are otherwise decent.

### 3e. The gate is watching the wrong failure mode

TC1 pre-registered **G1**: fail if the deterministic arm fails to decode **≥ 5%** of the corpus,
and predicted *"A will … fail outright on unicode truncation."* Executed over 546 real paragraphs
from five fleet documents, using TC1's own recipe:

| file | n | undecodable | silently truncated |
|---|---:|---:|---:|
| RESULTS.md | 162 | 0 (0.00%) | 157 (96.9%) |
| HOLLOW.md | 105 | 0 (0.00%) | 56 (53.3%) |
| F1-AUDIT.md | 157 | 3 (1.91%) | 85 (54.1%) |
| papers-WHITEPAPERS.md | 96 | 1 (1.04%) | 61 (63.5%) |
| ORIENTATION.md | 26 | 0 (0.00%) | 12 (46.2%) |
| **TOTAL** | **546** | **4 (0.73%)** | **371 (67.9%)** |

**TC1's gate G1 does not fire: 0.73% < 5%.** The prediction was directionally right and
quantitatively off by ~7×.

And the reason it does not fire is the finding, not a detail: **the hard failure is rare (0.73%)
and the quiet failure is routine (67.9%) — a 93× ratio — and the gate was pre-registered against
the loud one.** Meanwhile `test_long_string_truncation` asserts the quiet failure is *correct
behaviour*:

```rust
assert_eq!(back.question, "x".repeat(128)); // truncated
```

**The suite certifies the data loss as intended.** That is the `6.8×` disease again, in a new
place: a test that cannot fail *because it asserts the defect*.

---

## 4. Is "a type with no executable invariant does not compile" implementable?

**Yes for arithmetic. No for meaning. And no for the thing that actually matters here.** Three
distinct reasons, each with executed or primary-source backing.

### Reason 1 — only the integers are checkable, and the integers are the less meaningful half

§2 above is the proof. `constraint-theory-core` has the best invariant enforcement in the fleet
and its doc comment is still wrong about where the padding is. A `const _` on the sum cannot
check the labels, because labels are prose. **Enforcing the total leaves the attribution
unverifiable by construction.** Any lane that reports "I added a const assert, layout verified"
has verified the sum and nothing else.

### Reason 2 — every system strong enough to enforce this ships a documented way to skip it

Dafny language reference, §8.18, fetched and read
([dafny.org/dafny/DafnyRef/DafnyRef](https://dafny.org/dafny/DafnyRef/DafnyRef), 806,586 chars
extracted):

> **"The `assume` statement lets the user specify a logical proposition that Dafny may assume to be
> true without proof. If in fact the proposition is not true this may lead to invalid
> conclusions."**

And §11.2.22 lists **`{:verify false}`** as a first-class attribute — turn off verification for a
method. And §13.7.2 is titled *"Verification debugging when verification is slow"* and its first
subsection is **`13.7.2.1. assume false;`**.

**The documented debugging workflow of the strongest available tool is: hit an invariant you cannot
prove, disable the check, keep building.** That is not a leak. It is the intended workflow, because
the alternative is a tool nothing compiles under. "Does not compile" is the state everyone designs
for and nobody ships in, because the escape hatch is load-bearing for adoption.

There is also `{:axiom}` (§11.2.4), `{:extern}` (§11.2.7), and the `{:isolate_assertions}` /
`{:vcs_max_splits}` family for scaling. **The escape hatches are not exceptions to the design. They
are the design.**

### Reason 3 — the invariants that matter here are properties of *two functions*, not of a type

The invariants that are actually violated in §3 are:

- `∀t. decode(encode(t)) = t` — round-trip identity (§3a, §3d)
- `Σ widths = 384` — layout total (§2)

The first is the one that costs the fleet real content and it **cannot live on the type at all**,
because the type `EncodedTile` is well-formed for every value of it; the defect is that
`encode`/`decode` are not mutually inverse. A dependent type, refinement type, or liquid type
checks properties of *values*. This is a property of a *pair of functions*. Dafny can prove it.
It costs, per IronFleet (§6 below), **3.6 lines of proof per line of code, 3.7 person-years for
two systems.** A property-based test finds §3a and §3d in **about ten lines** and milliseconds.

> **The rule is stated about types. The invariants that are actually being violated are about
> codecs. Codecs are functions. The type carries none of it.**

### The honest sentence, as requested

> **The enforcement is the hard part, and everyone skips it — and worse, every system strong
> enough to enforce it ships a documented, first-class, recommended way to skip it, and its own
> reference manual lists "disable this assertion" as step 1 of debugging.**

**And the most valuable output of this lane is the reason the rule is naive:**

> **"A type with no executable invariant does not compile" assumes the invariant is a property of
> the type. In every artifact in this lane it was a property of a *description* of the type, or of
> a *pair of functions*, or of *one of several constructors* — and those are exactly the three
> places a type-level rule cannot reach. A rule about types cannot fail a build over a comment, and
> this fleet's most expensive defect is a comment.**

---

## 5. The interception point — named file, named mechanism

Four candidates, in descending order of how much they actually bind.

### 5a. The merge gate — **broken, not absent.** This is the real answer.

`plato-tile-encoder/.github/workflows/ci-rust.yml` runs `cargo fmt --check`, `cargo build`,
`cargo clippy -- -D warnings`, and `cargo test --verbose`. It has run **once**, on `de8e780`, and
its conclusion is **`failure`**. The repository is public, the workflow is present, and the
doctest failure is a hard compile error.

**So the fleet does not lack an enforcement point. It has a working one that fired and was not
read.** If you add a `const _` assert to `plato-tile-encoder/src/lib.rs` tomorrow, the next push
runs the doctest that is already failing, and the commit is blocked by an *unrelated pre-existing
red*. The first mechanical prerequisite to "make violating it impossible" is **fixing the
doctest**, because you cannot distinguish your new failure from the old one.

This is a genuinely different answer from "add a compiler check," and I would not have found it
without running the suite a previous lane reported as unrunnable.

### 5b. The codec chokepoint — `write_str`, 3 lines, fixes §3a

`plato-tile-encoder/src/lib.rs`, `fn write_str` is the **single function through which all four
text fields pass**, and it is the only place the byte-truncation decision is made. Refusing to
write a partial codepoint — truncate at the last char boundary, or return `Result` — makes the
straddle **impossible** rather than flagged. The same function is the natural place to escape
`,` in `tags`, which fixes §3d.

This is the highest value-per-line in the whole report: **one function, both silent-corruption
defects, and the enforcement is structural (the bytes cannot exist) rather than advisory.**

### 5c. Compile-time layout — the mechanism already in the fleet, applied unevenly

`constraint-theory-core/src/tile.rs:223` proves the pattern works and proves the control fires.
`plato-tile-encoder/src/lib.rs` has a `BINARY_SIZE` const and **eight magic integers inline** with
no sum check. One line — `const _: () = assert!(64+128+128+32+20+4+4+4 == BINARY_SIZE);` — would
close the docstring/code divergence on the *code* side. Per §2, that still leaves the labels
unchecked, and this lane's own measurement is that the labels in the one crate which *has* the
assert are wrong.

### 5d. What I checked and rejected

- **D1/Postgres CHECK constraints** — do not apply. These records are 384-byte blobs in a
  fixed-width record, not columns; the D1 write path for `demotion_receipts` is already
  `UNVERIFIABLE` per ORIENTATION open item 2, and adding a CHECK there adds an unverifiable layer.
- **A compiler / dependent types** — the fleet's substrate is "plain text, shell, hand-rolled
  codecs" per the brief. A language change is not available at this scale, and per §6 it is the
  most expensive known answer anyway.
- **A judge panel** — excluded by ORIENTATION's n_eff ≈ 2, and irrelevant: validity of a fixed-width
  record is decidable, and paying a model to decide a decidable question is the `6.8×` mistake.

---

## 6. What has genuinely worked in industry

### Primary source I read in full: IronFleet (SOSP '15)

Hawblitzel, Howell, Kapritsos, Lorch, Parno, Roberts, Setty, Zill — Microsoft Research.
**Fetched and text-extracted this session** (474,409 bytes → 1,919 lines):
<https://www.microsoft.com/en-us/research/wp-content/uploads/2015/10/ironfleet.pdf>
(also <https://dl.acm.org/doi/10.1145/2815400.2815428>). This is a real, shipped, publicly
documented system: a verified Paxos RSM library and a sharded KV store.

**The cost, stated by the authors (§6.3):**

> "the high-level trusted specification for IronRSL is only 85 SLOC, and for IronKV it is only 34,
> making them easy to inspect for correctness. At the implementation layer, **our ratio of proof
> annotation to executable code is 3.6 to 1.** … In total, developing the IronFleet methodology and
> applying it to build and verify two real systems required **approximately 3.7 person-years**."

**The trust base, stated by the authors (§2.5 Assumptions):**

> **"A small amount of our code is assumed, rather than proven, correct. Thus, to trust the system,
> a user must read this code. Specifically, the spec for each system is trusted, as is the brief
> main-event loop described in §3.7."**

Plus, in the same section: the correctness of **Dafny, the .NET compiler and runtime, the
underlying Windows OS, and the underlying hardware.**

**So: the strongest industrial verification result in the literature ships with an
assumed-not-proven residue, a trusted-by-reading spec, a 3.6:1 proof-to-code ratio, and a 3.7
person-year price tag for two systems.** That is not a failure of IronFleet. It is the honest
price of the only approach that genuinely works, and it is the correct benchmark against which
"add an executable invariant" should be costed.

### A defect it MISSED — the trust base is the miss

IronFleet's guarantees are conditional on Dafny, the .NET toolchain, the OS, the hardware, and
"a small amount of our code" that a user must **read**. That is a defect class the method is
structurally unable to reach, and the paper is upfront about it rather than hiding it. This is
the honest "missed" account, and it is better than an anecdote because it is a *design* property
that will still be there in ten years.

### Corroborating primary signal: the tooling is dormant

`microsoft/Ironclad` via the GitHub API, read this session — **not archived**, 1 open issue,
created 2015-09-23. Commits:

```
2023-06-03  Microsoft mandatory file (#24)
2023-06-02  Add LICENSE at top level. Fixes #23
2023-03-30  Secure, deterministic hashing of public keys (#22)
2022-03-02  Use .NET 6.0
2022-03-01  IoFramework performance improvements
```

**Microsoft's flagship verified-code repository has had no substantive commit since 2023-03-30 —
roughly three and a half years — and the three commits after that are LICENSE, a .NET bump, and
a mandatory-file policy.** It is not archived, so the signal is "dormant", not "retracted". I am
not claiming abandonment; I am reporting that the industry artefact is not being advanced, which
is relevant to how much anyone should bet on this class of solution.

### UNVERIFIABLE — the Amazon TLA+ account

I could **not** retrieve the primary source. Recorded as `UNVERIFIABLE`, not false:

- `lamport.azurewebsites.net/tla/papers/amazon-tla.pdf` → **404**, body reads *"The resource you
  are looking for has been removed, had its name changed, or is temporarily unavailable."*
- `lamport.azurewebsites.net/papers/amazon-tla.pdf` → **404**
- `cacm.acm.org/research/amazon/` → **403**
- `research.microsoft.com/.../some-social-engineering-for-software-engineers` → **200 but
  JS-rendered**; no abstract or body text present in the served HTML (I extracted 0 occurrences of
  "TLA", "bug", or "lock" from the nav shell)
- `web.archive.org` → **unreachable from this sandbox** (connection failure, 0 bytes, all attempts)
- Semantic Scholar Graph API, DuckDuckGo HTML/lite, Mojeek → returned no parseable results

**I am therefore not citing the Amazon TLA+ bug story.** I know the account exists and roughly
what it says, and I have written it up in many documents myself in past sessions. That is not a
source. Anyone wanting to use the "TLA+ found a lock bug at Amazon" line should fetch the PDF from
a working network first, and should not take it from me. Per ORIENTATION: a failed fetch is
`UNVERIFIABLE`, and it stays that way.

### A defect MISSED, executed locally and in the fleet's own words

The best available "verification missed it" account in this lane is the fleet's own, and it is
stronger than any anecdote: **`plato-tile-encoder`'s 16-test suite is green, and it contains a test
that asserts the defect is correct behaviour** (`test_long_string_truncation`). The suite verifies
that 67.9% of real fleet content is silently destroyed, and reports that as a pass. This is
exactly the "`6.8×` sitting in a README and two passing property tests" disease, and it is
reproduced here in a crate nobody had flagged.

---

## 7. Direct answers to the four questions

**Q1 — What do real type systems with machine-checked invariants do that a lint cannot?**
They make the *sum* and the *size* unfalsifiable at build time. IronFleet/Dafny go further and
make protocol properties machine-checked over an implementation. For **this** record — 384 fixed
bytes, no `tags` field in the paper, self-contradicting comments — the right shape is **none of the
dependent/refinement/liquid families.** The record's problem is not that it lacks a type; it has
two, in two crates, in two incompatible layouts (`constraint-theory-core` is
`#[repr(C, align(64))]` with 11 fields; the encoder is a hand-rolled byte-offset serializer with
8). The right shape is a **`const` layout table that the code iterates**, so there is one source of
truth and the doc comment has nothing to say. That is not a type system. It is deleting a
duplication.

**Q2 — Is the rule implementable, or a slogan?** Implementable for arithmetic, already implemented
in `constraint-theory-core/src/tile.rs:223`, verified to fire. **Unimplementable for prose, which
is where both live.** The honest sentence is in §4. The rule is not a slogan; it is a rule about
the wrong object.

**Q3 — The interception point.** `plato-tile-encoder/src/lib.rs`, `fn write_str` — the single
chokepoint for all four text fields; refuse to write a partial codepoint and escape `,`, and both
silent-corruption defects become unrepresentable. Above that, `.github/workflows/ci-rust.yml`, which
is **already red** and must be fixed before any new check can be distinguished from the old
failure.

**Q4 — What has worked.** IronFleet works, at 3.6:1 proof-to-code and 3.7 person-years for two
systems, with a named assumed-not-proven trust base it publishes itself. It is the correct
reference point and it is three orders of magnitude more expensive than this fleet's problem. The
property-testing answer is right for codec semantics and I did not obtain a primary industry
defect account for it — see `UNVERIFIABLE` above; Hypothesis's own site is reachable
(<https://hypothesis.works/>, confirmed 200) and its claim is only that it reports the *simplest*
failing example, which is a debugging aid, not evidence of a production catch. I am not citing it
as one.

---

## What I learned that changes what someone else should do

**1. Stop writing the layout down. The docstring is not a documentation defect, it is a second
source of truth, and the fix is deletion, not correction.** I found the same 388-vs-384 divergence
in `plato-tile-encoder` that a prior lane found, and then measured `constraint-theory-core` — the
crate that *does* have a compile-time size assert — and found its padding description is still
wrong. Correcting the comment would have produced a correct comment that drifts again next year.
The change: make `write_str` take its width from a `const LAYOUT: [(&str, usize); 8]` that the
encoder iterates, and let the comment have no numbers in it at all. A comment with no numbers
cannot be a wrong number.

**2. Before adding any check, establish that a *known-failing* check is visible. This repo has one
and nobody read it for five months.** A red CI on the last commit, on the commit that added the CI,
with a compile error in the file's own API example. If your enforcement strategy does not include
"prove the existing gate is green before trusting it to catch your new failure," you are building
a receipt, not a gate — which is the `TYPES-UNLOCKED.md` §"23 workflows that cannot fail" failure
mode, except the gate *can* fire and the output is still discarded. **This is a one-hour check that
invalidates any enforcement claim not backed by a green baseline.**

**3. Gate on the failure you measured, not the failure you predicted.** TC1 pre-registered a ≥5%
decode-failure gate; the real rate is 0.73%, so the gate does not fire, while silent truncation
runs at 67.9% and is asserted to be *correct* by the crate's own test. Anyone writing a threshold
from intuition about the loud mode will write a gate that never fires over the quiet one. **The
actionable change is cheap: before pre-registering a threshold, measure the rate of each failure
mode on real corpus, and put the two numbers in the same sentence.**

**4. Type the codecs, not the records — and use a property test, not a proof.** Every real
invariant violated here (`decode∘encode ≠ id`, comma injection, straddle) is a property of two
functions. A `#[test]` with a handful of adversarial inputs catches all three in ~10 lines. Dafny
would catch them too, at IronFleet's 3.6:1 ratio. **The "no executable invariant does not compile"
rule, applied literally, points at a 3.7-person-year solution to a ten-line problem, and would not
have caught the two defects that are actually corrupting fleet content.** The rule is worth
keeping for *arithmetic* — where it is free and already proven in `constraint-theory-core` — and
should be explicitly scoped to arithmetic in `TYPES-UNLOCKED.md` before it gets used to justify a
type-system investment.

**5. Correct `TYPES-UNLOCKED.md` in one line.** "A type that carries no invariant is not a type.
It is a shape." → the sharper and more actionable form is: **"A type whose *descriptions* are not
generated from the type is not a type. It is a shape with a copy attached."** Every defect in this
lane is a copy that drifted from its original — the docstring, the crate comments vs the paper,
`test_long_string_truncation` asserting the truncation is fine, the 6.8× in four files. The
invariants were not missing. They were duplicated into prose, and prose is not in any type system.

---

## Provenance and honesty ledger

| claim | status |
|---|---|
| `cargo test --lib` 16/16 pass; full `cargo test` fails | **executed this session** |
| CI red on `de8e780` since 2026-05-08 | **GitHub Actions API, read this session** |
| `const _` assert fires on +1 byte | **executed this session** (`E0080`) |
| 14-byte internal hole, no trailing padding | **executed this session** (`offset_of!`) |
| 0.73% undecodable / 67.9% truncated on 546 paragraphs | **executed this session** |
| tags not injective under `,` | **executed this session** |
| `confidence` clamp bypassed by struct literal | **executed this session** |
| IronFleet costs, trust base, 3.6:1, 3.7 person-years | **primary PDF fetched + read, quoted verbatim** |
| Dafny `assume` / `{:verify false}` / `assume false;` | **DafnyRef fetched, 806,586 chars extracted, quoted verbatim** |
| Ironclad dormant since 2023-03-30 | **GitHub API, read this session** |
| Amazon TLA+ defect account | **`UNVERIFIABLE` — 6 fetch routes failed, not cited** |
| Property testing caught a production defect | **not obtained; not cited** |
| `docs/PLATO-LINEAGE.md` §7 "no cargo in this sandbox" | **now falsified — toolchain installed, tests run** |
