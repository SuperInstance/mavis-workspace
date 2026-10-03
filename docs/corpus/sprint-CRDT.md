# SPRINT-3 — CRDT Convergence (Part A) + Tile Dispute (Part B)

All numbers below are measured in this session, not inherited. Sources are blob digests
(`git hash-object`) or `path:line`. Clones used: `git clone https://github.com/SuperInstance/<repo>`
(read-only; **no pushes**). No repo was modified.

---

# PART A — CRDT convergence

## A.1 Verified table — the count is 8 repos, but **7 are Rust, not 8**

The scout said "8 CRDT ports in Rust". The count of *repos* is right. The count of *Rust ports* is wrong.

| repo | language | src files | blob digest (first 16) | LOC | last commit | what it implements |
|---|---|---|---|---|---|---|
| `crdt-core` | Rust | `gcounter.rs` `pncounter.rs` `gset.rs` `orset.rs` `lww.rs` | `53dc94cf02d91d69` `aae46cecca4d81ec` `9a4aeaba7215fa76` `7ddfbda52bef177a` `d6f59be7a5ee3de8` | 709 | `1bdf1a35` **2026-07-12** | all 5 types, **37 tests** |
| `crdt-gcounter` | Rust | `src/lib.rs` | `e972cdae2d0a64c6` | 57 | `e6f40769` 2026-09-30 | G-Counter + FNV canary, 3 tests |
| `crdt-gset` | Rust | `src/lib.rs` | `b57d66dbdee89651` | 61 | `dcbdeca6` 2026-09-30 | G-Set + FNV canary, 3 tests |
| `crdt-lwwreg` | Rust | `src/lib.rs` | `0ec437162b0fd7cd` | 64 | `7ea62fbc` 2026-09-30 | LWW-Reg + FNV canary, 3 tests |
| `crdt-orset` | Rust | `src/lib.rs` | `2e6be8ad7306d466` | 78 | `9ba89078` 2026-09-30 | OR-Set + FNV canary, 3 tests |
| `crdt-pnvector` | Rust | `src/lib.rs` | `11d37ed32b2a29b5` | 69 | `8e0d6ec9` 2026-09-30 | PN-Counter + FNV canary, 3 tests |
| `crdt-map` | Rust | `src/lib.rs` | `139a1448cefebe9a` | 570 | `79193927` 2026-07-12 | nested map CRDT |
| **`crdt-sync`** | **TypeScript** | `src/worker.ts` | — | — | `6c8634bb` 2026-04-13 | Cloudflare Worker (`package.json`, `wrangler.toml`, `vessel.json`, **no `Cargo.toml`**) |

**Correction to the brief:** `crdt-sync` is a TypeScript/Cloudflare Worker. It is a CRDT repo, not a Rust
port. So: **7 Rust ports + 1 TypeScript port = 8 repos.**

Second correction, which matters for the decision: the five singleton ports are dated **2026-09-30**.
`crdt-core` and `crdt-map` are dated **2026-07-12**. The singletons were created **79 days after the
superset already existed in the org**. These are not legacy survivors. They are a regression.

## A.2 "5 byte-identical below the type" is **FALSE — the claim is inverted**

Measured over extracted `src/lib.rs` bytes:

| repo | sha256 of `src/lib.rs` | `src/lib.rs` | `tests/canary.rs` | `src/main.rs` | LOC |
|---|---|---|---|---|---|
| crdt-gcounter | `75002a92b552dbd5` | `e972cdae2d0a64c6` | `f4c3d5f90be62cef` | `060c36480bcca5ae` | 57 |
| crdt-gset     | `efa90c530cd97270` | `b57d66dbdee89651` | `78d869e2249f2db6` | `ae223dac373739ee` | 61 |
| crdt-lwwreg   | `9fea907077b2e751` | `0ec437162b0fd7cd` | `fd04a5cca141f308` | `c1787bd53fe3d067` | 64 |
| crdt-orset    | `d558d2a16b3ba662` | `2e6be8ad7306d466` | `50fb8d2999bf1cd9` | `87be951744c2d623` | 78 |
| crdt-pnvector | `fddc0429b368685c` | `11d37ed32b2a29b5` | `812e34ea3f2bebc9` | `e60c1c84280e5ece` | 69 |

**0 of 5 `src/lib.rs` are byte-identical.** Nor are the canary tests (`f4c3d5f9…` … `812e34ea…`, all distinct),
nor the `main.rs`. Line counts differ: 57/61/64/78/69.

What **is** byte-identical across all five, by git blob digest:

- `.github/workflows/ci.yml` = `c88d3baecb3c69f71a07fcd4febdc0dd6a960f5a`
- `.gitignore` = `ea8c4bf7f35f6f77f75d92ad8ce8349f6e81ddba`
- `LICENSE-APACHE` = `137069b823873b8bcf42979bcf8e9371052d26a2`
- `LICENSE-MIT` = `d817195dad53ec992418c28ffca5fbd1cd86502a`
- plus the 17-line FNV-1a block appended to each `lib.rs` (e.g. `crdt-gcounter/src/lib.rs:41-57`,
  `crdt-orset/src/lib.rs:62-78`)

**So the true statement is: identical scaffolding, five different implementations.** The parts that
are copies are the parts that carry no science. The parts that carry science are the parts that differ.
The scout looked at the surface and read it as the substance.

## A.3 The canary cannot distinguish consistency from a copied error — because it does not test the CRDT

`crdt-gcounter/tests/canary.rs:10-13` (and its four siblings) asserts exactly one thing:

```rust
assert_eq!(crdt_gcounter::fnv1a64("café Δ 日本語".as_bytes()), 0x024a555471370b18d);
```

I verified the constant independently: `FNV-1a-64("café Δ 日本語" as UTF-8) = 0x24a555471370b18d`. **The constant is
correct.** This is a genuinely sound hash canary.

But it is a canary on the *hash function*, and it contains **zero references** to `GCounter`, `GSet`,
`ORSet`, `LWWReg`, `merge`, or any merge law. The type is never constructed in the canary. The file's own
doc comment calls this "the fleet polyformalism canary" — the word *polyformalism* is doing work the
assertion does not do.

**The hash cannot distinguish consistency from a copied error here, because the copied thing is the hash
and the error would be in the type. The canary sits on the wrong side of the boundary.**

### Mutation proof

One identical edit applied to the G-Counter merge law — `max(a,b)` → `a.saturating_sub(b)`:

| repo | result | red tests |
|---|---|---|
| `crdt-core` | `test result: FAILED. 30 passed; **7 failed**` | `gcounter::test_merge`, `gcounter::test_merge_commutative`, `gcounter::test_merge_idempotent`, `pncounter::test_concurrent_increments`, `pncounter::test_merge`, `pncounter::test_merge_commutative`, `pncounter::test_merge_idempotent` |
| `crdt-gcounter` | `test result: ok. 3 passed; **0 failed**` | none — **canary green** |

Same edit, opposite response. `crdt-core` is 79 days older and has 37 tests including
`test_merge_associative`, `test_merge_commutative`, `test_merge_idempotent`. The singleton has one unit
test, `test_increment_and_value`, which never calls `merge`.

I swept the rest of the surface — sabotage each singleton's core operation, leave the canary untouched:

| sabotage | repo | passed | failed |
|---|---|---|---|
| `merge` max → `saturating_sub` | crdt-gcounter | 3 | **0** |
| `merge` → no-op (elements never copied) | crdt-gset | 3 | **0** |
| `merge` → `if true` (always take other) | crdt-lwwreg | 3 | **0** |
| `remove` → always returns `false`, never tombstones | crdt-orset | 3 | **0** |

**Twelve green assertions across four destroyed CRDTs.** The canary is orthogonal to the product.

## A.4 Is `crdt-core` a genuine superset? **Mostly yes — with two real exceptions**

**Live divergence found in `crdt-lwwreg`** (not a theory; executed):

```
lww: r1.merge(r2)="a"   r2.merge(r1)="b"   equal=false
```

`crdt-lwwreg/src/lib.rs:11-14` stamps from `SystemTime::now()` in milliseconds and `:31` merges with
`if other.timestamp > self.timestamp`. Two registers created in the same millisecond, merged in opposite
orders, yield **different values**. That is a convergence failure, and it is the *common* case, not an
edge case. `crdt-core` fixes it — it ships `lww::tests::test_merge_tiebreaker` and
`test_write_with_node_tiebreaker` against a `(timestamp, node)` key.

**`crdt-gcounter` invites silent data loss.** `crdt-gcounter/src/lib.rs:13-15` is
`increment(&mut self, node: &str, delta: u64)` and `:24` merges with `max`. Any node may write any slot
with any delta, so two replicas touching one slot lose an increment. `crdt-core/src/gcounter.rs:20` is
`increment(&mut self, node_id: u64) -> u64` — +1, typed node id — so the API makes the violation
unrepresentable. Executed: both return `2` where the true total is `4`. `crdt-core` is wrong here too,
but it is wrong only if you ignore its stated discipline; the singleton is wrong by construction.

**Negative result — `crdt-orset` is fine.** I tested concurrent add/remove: `a.merge(b).contains(1)=false`,
`b.merge(a).contains(1)=false`, commutative `true`. No defect found. Reported because a negative is a
result.

**The two genuine gaps in `crdt-core` (a negative result on supersets):**

1. **`crdt-map` is not covered.** 570 lines (`139a1448cefebe9a`), a nested-map CRDT. `crdt-core` ships
   only gcounter/pncounter/gset/orset/lww. Consolidating onto `crdt-core` **deletes a type**, not a copy.
2. **`crdt-sync` is not covered and cannot be** — it is the transport/sync layer in TypeScript.

So: **`crdt-core` supersedes 5 of the 7 Rust ports, not 7 of 7.** Any proposal that says "point the other
seven at `crdt-core`` is wrong on its face — `crdt-map` and `crdt-sync` have no target.

## A.5 Cost — the `file:../` premise does not hold up

The brief says "the 13 `substrate-*` repos already declare `file:../` deps, so the co-located pattern is
established." I could not confirm that. Measured against the 592-repo bare census at
`projects/fleet-triage/org2/bare/`:

- `substrate-*` repos present: **4** (`substrate-bench`, `substrate-contest-rs`, `substrate-foundation`,
  `substrate-llm-client`) — not 13.
- Of those 4, declaring a relative path dependency: **0**.
- Across the **entire** 592-repo census, repos using a relative `path = "../"` dep: **2**
  (`fleet-spread`, `integration-examples`).

**The co-located pattern is not established — it is a two-repo precedent.** Any cost estimate built on
"13 repos already do this" is built on nothing. The real cost is higher, and I cannot price it without
Casey deciding whether `crdt-core` gets vendored into each repo (a `path` dep in Cargo means the
dependency must exist on the consumer's filesystem — it is not publishable, not versioned, and it breaks
`cargo publish` and any CI that checks out one repo).

Honest cost, per port, from the actual code:

| work | effort | note |
|---|---|---|
| Add `crdt-core` dep + repoint `use` | ~15 min | mechanical |
| Delete the 17-line FNV block | ~2 min | it is dead weight once the type is shared |
| **Write the merge-law tests the port never had** | **2–4 h** | 5 ports × 3 laws × 2 types; this is the real cost and the real prize |
| Wire the shared canary as a `path` dep (not vendored) | ~1 h | needs a decision on vendoring |
| `crdt-map` / `crdt-sync` | **no path exists** | out of scope of this consolidation |

Total for the 5 covered ports: **~2–3 days**, of which ~90% is the missing tests. That is the only
consolidation worth doing, and the tests are worth doing *whether or not* you consolidate.

## A.6 The rule that stops a tenth port

Precedent confirmed with exact citations in `quilt-atlas`:

- `atlas.json:7` → `"pagination_cap_hit": false`
- `atlas.json:35954` → `"CI coverage is measured only on the top_motion slice (API economy); absence elsewhere is UNMEASURED, not zero"`
- `scripts/build_atlas.mjs:161` → `pagination_cap_hit: hardCapHit`
- `scripts/build_atlas.mjs:170-171` → writes the same sentence into the receipt
- `README.md:25` → *"CI is probed only on the top-motion slice — absence elsewhere is **UNMEASURED**, never reported as zero"*

The model is a **three-state field**, not a boolean: *measured false* / *measured true* / *not probed*.
`false` and "we never looked" are different claims and the repo refuses to conflate them.

Applied to CRDT, a `crdt-fleet.json` receipt with one entry per type:

```json
{
  "type": "GCounter",
  "canonical": "crdt-core",
  "converges_under_concurrent_merge": true,
  "tiebreak": null,
  "ports": [
    { "repo": "crdt-core",  "measured": true,  "result": "pass" },
    { "repo": "crdt-gcounter", "measured": true,  "result": "pass" },
    { "repo": "crdt-map",  "measured": false, "result": "UNMEASURED, not zero" }
  ],
  "novelty_gate": "a new port must declare a type crdt-core does not implement, or point at an existing receipt row"
}
```

The gate that stops the tenth port is `novelty_gate`. A new `crdt-*` repo is only admitted if it
implements a type **not** in `crdt-core`'s list, or it is a transport/wire port and says so. A new port
that re-implements G-Counter is refused at the door with a reason, not a code review. That is the
mechanism `quilt-atlas` uses to keep its page count honest, pointed at repos instead of pages.

**The second half of the rule** is the canary fix, and it is the part that matters more. The FNV canary
is not wrong; it is *misplaced*. A port must assert its **merge laws**, not a hash:

```rust
#[test]
fn merge_is_commutative_idempotent_associative() { /* the 3 laws, per type */ }
```

Then the receipt's `"result"` field is *earned* by a test that would go red if the science broke, instead
of by a constant that a copy-paste reproduces perfectly. The hash canary should move to one shared
`fleet-hash` crate that every port depends on — one copy, not five — where it is cheap and correct.

---

# PART B — the tile dispute

## B.1 The three facts, verified

**The paper cannot arbitrate, and not only because it lacks `tags`.** `06-Tile-Algebra-Formalization.md`
is 809 lines. `grep -niE 'tags|byte|width|serial|align|pad|384'` over the whole document returns **zero
matches**. The word "tuple" appears once, at line 41. Definition 1 (`06-Tile-Algebra-Formalization.md:41-48`):

$$T = (I_T, O_T, f_T, c_T, \tau_T)$$

with $I_T, O_T \in \text{Type}$, $f_T: I_T \to O_T$, $c_T: I_T \to [0,1]$, $\tau_T: I_T \to \text{String}$.

That is a **morphism** — a type-level object about composition. Compare the record
(`plato-tile-encoder/src/lib.rs:17-26`): `id, question, answer, tags, domain, confidence, ghost_score,
use_count`. **Seven of the record's eight fields have no counterpart in the paper at all.** The eighth,
`confidence`, is a value in the record and a *function* in the paper — different categories of thing
entirely. The paper never made a claim about bytes, so it is not wrong about the dispute. It is silent.

**The byte arithmetic.** `plato-tile-encoder/src/lib.rs:164`:

```
/// Layout: id(64) + question(128) + answer(128) + domain(32) + tags(24) + confidence(4) + ghost(4) + use_count(4) = 384
```

- `64+128+128+32+24+4+4+4` = **388** — the line's own sum is false.
- `64+128+128+32+20+4+4+4` = **384** — equals `BINARY_SIZE` at `:161`.

**Correction to the brief:** there is **one** comment saying `tags(24)`, not two. `:172` says
`// tags: comma-separated, 20 bytes` — which is *correct* and contradicts `:164`. `git log -S 'tags(24)'`
shows `:164` has said `tags(24)` since the initial commit `de8e780`. So the dispute is one stale line
against the code and against its own sibling comment.

**The third layout does not exist.** I swept every `.rs/.py/.c/.h/.ts` under `/workspace` for a
cache-aligned or padded 384-byte layout. The only hits are unrelated cargo-registry files (`ring`
padding docs, makepad audio). `plato-tile-cache/src/lib.rs` contains no `384`, no `align`, no `pad`.
The live GitHub `plato-tile-encoder` is byte-identical to the working copy (`de8e780`, 2026-05-08).
**The crate has two serialisation formats** — JSON and the 384-byte binary — plus base64, which is a
transport wrapper around the binary one, not a third layout. **Reporting this as a negative result:
the "third 384-byte cache-aligned layout" is not present in this workspace.**

One more false claim found while checking: `plato-tile-encoder/src/lib.rs:4` says *"Compatible with
plato-tile-bridge C struct format."* `plato-tile-bridge`'s README advertises *"Cross-language tile format
conversion with 384-byte binary layout"*, but its `src/plato_tile_bridge/bridge.py` (138 lines) contains
**no 384-byte layout and no C struct** — it is `TileMapping` / `ConflictRecord` sync logic. The
compatibility target named by the encoder does not exist.

## B.2 Recommendation: **(3)**

**Option (1)** is true but insufficient. The comment is wrong and must change — but "fix the comment"
leaves the crate asserting compatibility with a C struct that does not exist, and leaves a 20-byte tag
field that silently corrupts data.

**Option (2)** is arithmetically dead. I implemented it — changed the code to match its own doc comment
(`20` → `24` in `write_str` at `:174` and `read_str` at `:191`) and ran the crate's own suite:

```
test_binary_size ... FAILED          test_binary_roundtrip ... FAILED
test_binary_preserves_tags ... FAILED test_binary_ghost_score ... FAILED
test_binary_use_count ... FAILED     test_binary_confidence_precision ... FAILED
test_binary_empty_fields ... FAILED  test_long_string_truncation ... FAILED
test_base64_roundtrip ... FAILED
```

**9 of 16 tests go red.** The reason is arithmetic: at `tags(24)` the final `u32` write lands at
`buf[384..388]` on a 384-byte array — out of bounds. To reach 384 with `tags(24)` you must shrink another
field, and there is nowhere to shrink: `question` is already truncating at exactly its test limit
(`:411-416` asserts a 200-char question round-trips to exactly 128). So (2) requires inventing a smaller
`question`, which changes the product, on the authority of a document that has no opinion about `question`.

**Option (3) is right, because the three artifacts are three different objects that have been silently
conflated, and the conflation is what makes the dispute look unresolvable.**

| artifact | what it actually is | verdict |
|---|---|---|
| `06-Tile-Algebra-Formalization.md` | a *morphism* $(I,O,f,c,\tau)$ for reasoning about composition | not wrong — **irrelevant** to bytes |
| `EncodedTile` | a persisted Q&A record | right about bytes, **wrong about compatibility** (`:4`) |
| `src/lib.rs:164` | a byte layout | **factually false** — sums to 388 |

Nobody in this repo is lying. The doc comment is the only falsifiable claim and it is false; the paper
is a category error; the code is a correct wire format attached to a fictitious interop target. Calling
the paper "normative" for a `tags` width it has never heard of is the mistake.

**What *should* be true:** a fixed-width record should be specified by the record, cite a normative
byte-layout document that actually contains byte widths, and never claim formal backing from a document
about morphisms. The paper should gain a short "what this does not specify" note. The two artefacts
should stop citing each other.

## B.3 The real bug the dispute is hiding

While measuring the `tags` width I found something the 24-vs-20 argument obscures. The tag field is
**20 bytes of comma-joined text**, and realistic tag sets exceed it:

```
["math","geometry","algebra"]           -> "math,geometry,algebra"    = 21 bytes  -> TRUNCATED
["mathematics","geometry","algebra"]     -> "mathematics,geometry,..." = 28 bytes -> TRUNCATED
first 20 bytes = "mathematics,geometry"
round-trips as tags = ["mathematics","geometry"]     // third tag silently lost
```

`write_str` (`:199-204`) does `bytes.len().min(max)` and drops the rest **without a NUL, without an
error, and without a length byte**. The truncation is *mid-tag*, so the reader splits a corrupt token
into a valid-looking tag. The only test covering tags, `:331-335`, uses `["a","b","c"]` = 5 bytes — it
can never fail. **A 20-byte tag field holds about two tags.** Whatever the 24-vs-20 resolution, a
record that cannot hold its own data is the actual defect, and it is the one the stale comment was
hiding from review.

---

## Proposed diff (review only — nothing applied, nothing pushed)

Target: `plato-tile-encoder/src/lib.rs` @ `de8e780`. Four changes, in priority order.

```diff
--- a/src/lib.rs
+++ b/src/lib.rs
@@ -1,10 +1,24 @@
-//! plato-tile-encoder — Tile encoding/decoding
-//!
-//! Multiple codecs: JSON (hand-rolled), binary (384-byte compact), base64.
-//! Compatible with plato-tile-bridge C struct format.
+//! plato-tile-encoder — Tile encoding/decoding
+//!
+//! Multiple codecs: JSON (hand-rolled), binary (384-byte compact), base64.
+//!
+//! # What this crate is not
+//!
+//! `EncodedTile` is a persisted Q&A **record**. It is NOT the `Tile` of
+//! `white-papers/06-Tile-Algebra-Formalization.md`, which is the morphism
+//! T = (I, O, f, c, tau) over a type system. That document specifies no
+//! widths, no byte order, and no serialisation, and has no `tags` field.
+//! It is not normative for this layout and is not cited as such.
+//!
+//! Normative source: the `layout` module below, whose sum is asserted against
+//! `BINARY_SIZE` at compile time, so this comment cannot drift from the code.
+//!
+//! (removed: "Compatible with plato-tile-bridge C struct format." —
+//!  plato-tile-bridge has no C struct and no 384-byte layout; see SPRINT-3
+//!  Part B.1. Restore this line only when that contract actually exists.)
```

```diff
@@ -11,6 +18,7 @@
 //! ```
+//! use plato_tile_encoder::*;   // <-- the doctest has NEVER compiled; see B.4
 //! let tile = EncodedTile::new("id", "Q?", "A!", &["math"], "math", 0.9);
```

```diff
@@ -159,7 +173,22 @@
 // ── Binary Codec (384-byte compact) ────────────────────────────────

 const BINARY_SIZE: usize = 384;
+
+/// Normative byte layout. Single source of truth for every field width.
+/// Order is the on-disk order; all fields are little-endian, fixed-width,
+/// NUL-padded, NOT NUL-terminated.
+pub mod layout {
+    pub const ID: usize = 64;
+    pub const QUESTION: usize = 128;
+    pub const ANSWER: usize = 128;
+    pub const DOMAIN: usize = 32;
+    pub const TAGS: usize = 20;   // comma-joined UTF-8; see the overflow note below
+    pub const CONFIDENCE: usize = 4;
+    pub const GHOST: usize = 4;
+    pub const USE_COUNT: usize = 4;
+    pub const TOTAL: usize =
+        ID + QUESTION + ANSWER + DOMAIN + TAGS + CONFIDENCE + GHOST + USE_COUNT;
+}
+
+// The layout must sum to BINARY_SIZE. A width change that breaks this is a
+// build failure, not a comment that quietly becomes a lie.
+const _: () = assert!(layout::TOTAL == BINARY_SIZE);
```

```diff
@@ -164,7 +193,12 @@
-/// Layout: id(64) + question(128) + answer(128) + domain(32) + tags(24) + confidence(4) + ghost(4) + use_count(4) = 384
+/// Layout: see [`layout`] (normative). As of `de8e780` this comment said
+/// `tags(24)`, which sums to 388. The code has always written 20, which sums
+/// to 384. The code was right; the comment was wrong.
+///
+/// KNOWN LIMITATION: `tags` is 20 bytes of comma-joined text and is truncated
+/// mid-tag on overflow, with no error. Three realistic tags already exceed it
+/// (`"math,geometry,algebra"` = 21 bytes). A length-prefixed or fixed-slot tag
+/// encoding is required before this field can be considered lossless.
 pub fn encode_binary(tile: &EncodedTile) -> [u8; BINARY_SIZE] {
```

```diff
@@ -331,6 +365,26 @@
     fn test_binary_preserves_tags() {
         let tile = EncodedTile::new("t1", "Q", "A", &["a", "b", "c"], "d", 0.5);
         let back = decode_binary(&encode_binary(&tile)).unwrap();
         assert_eq!(back.tags, vec!["a", "b", "c"]);
     }
+
+    /// Pins the arithmetic the stale comment got wrong. If any width changes,
+    /// this fails by name instead of by mystery offset corruption.
+    #[test]
+    fn test_layout_sums_to_binary_size() {
+        use layout::*;
+        assert_eq!(TOTAL, 384);
+        assert_eq!(TAGS, 20);
+        assert_eq!(ID + QUESTION + ANSWER + DOMAIN + TAGS
+                 + CONFIDENCE + GHOST + USE_COUNT, BINARY_SIZE);
+    }
+
+    /// Documents the overflow as a KNOWN, MEASURED defect rather than leaving
+    /// it undiscovered. XFAIL-style: flip to a real assertion once the field
+    /// is widened or length-prefixed. See [`layout::TAGS`].
+    #[test]
+    fn test_tags_overflow_is_silent_corruption() {
+        let tile = EncodedTile::new("t", "Q", "A",
+            &["mathematics", "geometry", "algebra"], "d", 0.5);
+        let back = decode_binary(&encode_binary(&tile)).unwrap();
+        // 28 bytes into a 20-byte field: the third tag is lost, silently.
+        assert_eq!(back.tags, vec!["mathematics", "geometry"]);
+    }
```

And to the paper, `white-papers/06-Tile-Algebra-Formalization.md`, after Definition 1:

```diff
 ### 2.1 Basic Definitions

+> **Scope note.** This document defines `Tile` as the morphism
+> $T = (I_T, O_T, f_T, c_T, \tau_T)$ over a type system. It specifies **no
+> field widths, no byte order, no serialisation, and no `tags` field**. It is
+> therefore **not normative for any on-disk record format** and cannot arbitrate
+> a dispute over one. Concretely, the 384-byte record in `plato-tile-encoder`
+> carries `id, question, answer, tags, domain, confidence, ghost_score,
+> use_count`; seven of those eight have no counterpart here, and the eighth
+> (`confidence`) is a value here but a function $c_T$ in this document.
+> A separate normative document — the `layout` module in
+> `plato-tile-encoder/src/lib.rs` — owns the byte widths.

 **Definition 1 (Tile):** A tile $T$ is a 5-tuple:
```

---

## B.4 The proposed diff was executed, not sketched

I applied all of it to a scratch copy at `de8e780` and ran it:

```
cargo test  ->  test result: ok. 18 passed; 0 failed     (unit)
                test result: ok.  1 passed; 0 failed     (doctest)
```

**The `const` guard was verified by sabotage, both directions:**

| experiment | result |
|---|---|
| proposed diff, `TAGS = 24` (the value the stale comment demanded) | **build fails**: `error[E0080]: evaluation panicked: assertion failed: layout::TOTAL == BINARY_SIZE` at `src/lib.rs:187`, `exit=101` — before any test runs |
| same sabotage, guard line removed | `test tests::test_layout_sums_to_binary_size ... FAILED` (17 passed, 1 failed) |

The comment became a lie because nothing made it checkable. With the guard, the stale width is not a
thing you can write down incorrectly — it is a build error with a line number.

**Bonus defect found while verifying: the crate's own doctest has never compiled.** At pristine `de8e780`:

```
test src/lib.rs - (line 6) ... FAILED
error[E0433]: cannot find type `EncodedTile` in this scope
error[E0425]: cannot find function `encode_json` in this scope      (+4 more)
```

The headline usage example — the first thing a reader sees — has no `use` statement.
`.github/workflows/ci-rust.yml` runs `cargo test --verbose`, which *does* include doctests, at the same
commit `de8e780` that added the workflow. So either CI has been red since the day it was written, or it
has never run. The one-line `use plato_tile_encoder::*;` above repairs it, taking the crate from
"16 unit green, 1 doctest red" to "19 green, 0 red".

## Summary of every correction to the brief

| brief said | measured |
|---|---|
| 8 CRDT ports in Rust | 8 repos; **7 Rust + 1 TypeScript** (`crdt-sync` = CF Worker) |
| 5 are byte-identical below the type | **0 of 5** `lib.rs` identical; identical is the *scaffolding* (ci.yml, .gitignore, 2 licenses) + the FNV block |
| the canary proves the ports agree | the canary asserts one FNV constant (correct) and **never constructs a CRDT** |
| 13 `substrate-*` declare `file:../` | **4** `substrate-*` exist, **0** declare it; **2 of 592** census repos use relative path deps |
| `crdt-core` supersedes the others | supersedes **5 of 7 Rust**; `crdt-map` (570 lines) and `crdt-sync` have no target |
| the crate has a third 384-byte cache-aligned layout | **not present anywhere on disk** — negative result |
| two comments say `tags(24)` | **one** (`:164`); `:172` correctly says 20 |
| neither documented layout sums to 384 | `tags(24)` → **388**; `tags(20)` → **384**. The code's layout *does* sum to 384. |
| the paper has no `tags` field | correct — and no `byte`/`width`/`serial`/`align`/`pad` either; 7 of 8 record fields have no counterpart |
| (not in brief) | the crate's own doctest has never compiled, and CI runs `cargo test` at the very commit that added the workflow |
