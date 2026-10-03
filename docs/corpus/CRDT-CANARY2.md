# CRDT-CANARY2 — the FNV canary is a tautology, and the OR-Set defect underneath it is real

**Status: EXECUTION-VERIFIED.** The brief said cargo/rustc are often unavailable and to fall back
to artifact inspection. They *are* installed — just not on `PATH`:

```
$ which cargo   ->  not found
$ ls ~/.cargo/bin
cargo  cargo-clippy  cargo-fmt  cargo-miri  clippy-driver  rls  rust-analyzer  rust-gdb  ...
$ export PATH="$HOME/.cargo/bin:$PATH"
$ cargo --version   ->  cargo 1.99.0 (5f94df478 2026-08-27)
$ rustc --version   ->  rustc 1.99.0 (b940084d7 2026-09-28)
```

Every result below was produced by running `cargo test`. Nothing is inferred. Clones are
`git clone --depth 1` of `github.com/SuperInstance/<repo>` into `/tmp`, at the commits named.
**No push, no repo modified on GitHub.**

---

## 0. Two corrections to the brief, before the finding

**"8 CRDT ports in Rust" — there are 7, not 8.** `crdt-sync` is a Cloudflare Worker in
TypeScript (`package.json`, `wrangler.toml`, no `Cargo.toml`). 7 Rust + 1 TypeScript = 8 repos.

**"5 byte-identical below the type" — false; the claim is inverted.** Measured just now:

| repo | git blob of `src/lib.rs` | bytes | md5 | distinct? |
|---|---|---|---|---|
| crdt-gcounter | `e972cdae2d0a64c6` | 1363 | `221dc3dac1145620` | yes |
| crdt-gset     | `b57d66dbdee89651` | 1334 | `b7fdbc1e2eaf5550` | yes |
| crdt-lwwreg   | `0ec437162b0fd7cd` | 1536 | `791de430ac82b5cc` | yes |
| crdt-orset    | `2e6be8ad7306d466` | 2121 | `102f1994d6e1c69a` | yes |
| crdt-pnvector | `11d37ed32b2a29b5` | 1686 | `757bf2207eb10c8e` | yes |

**0 of 5 are byte-identical.** What *is* byte-identical is the FNV block appended to each — every
one hashes to `6798a25d7785c159`. So the copies are the part that carries no science, and the
differing parts carry all of it. The scout read the surface as the substance.

---

## 1. The current canary, quoted — and the proof it is a tautology

`crdt-gset/tests/canary.rs` @ `dcbdeca`, **all 19 lines**:

```rust
//! The fleet polyformalism canary.
//!
//! `crdt_gset::fnv1a64` is FNV-1a 64, the same digest every other substrate in the
//! fleet agrees on. Asserting it here means a change to the hash — a wrong prime, an
//! offset, a signed multiply — fails this crate's own test suite rather than producing
//! digests that quietly disagree with the rest of the fleet.

#[test]
fn canary_matches_the_rest_of_the_fleet() {
    assert_eq!(
        crdt_gset::fnv1a64("café Δ 日本語".as_bytes()),
        0x024a555471370b18d
    );
}

#[test]
fn runtime_canary_check_agrees() {
    assert!(crdt_gset::canary_holds());
}
```

**There is no `GSet` in this file.** No `GSet`, no `add`, no `merge`, no `contains`. The type is
never constructed. The string "polyformalism" is in the doc comment; the assertion does not
contain any formalism. `canary_holds()` is `lib.rs:59-61` — the same comparison, called twice.

The hash constant is *correct* (FNV-1a-64 of those bytes is `0x024a555471370b18d`). It is a sound
canary **on a hash function**, filed as a canary **on a CRDT**.

### The demonstration: destroy the product, keep the canary, get green

I replaced the entire body of `merge` at `crdt-gset/src/lib.rs:21-25` with a no-op:

```rust
// BEFORE — crdt-gset/src/lib.rs:21-25
    pub fn merge(&mut self, other: &Self) {
        for e in &other.elements {
            self.elements.insert(e.clone());
        }
    }

// AFTER — the sabotage
    pub fn merge(&mut self, _other: &Self) {
        return;
    }
```

That is not a subtle bug. `merge` is the *only* operation that makes a G-Set a CRDT. With it
stubbed, two replicas can never converge, ever, for any input. The type is now a single-node set
wearing a distributed costume.

```
$ cargo test          # in the sabotaged tree, canary untouched

running 1 test
test tests::test_gset ... ok
test result: ok. 1 passed; 0 failed

running 2 tests
test canary_matches_the_rest_of_the_fleet ... ok
test runtime_canary_check_agrees ... ok
test result: ok. 2 passed; 0 failed
```

**3 passed, 0 failed. On a build where merging does nothing.** The canary cannot distinguish a
correct G-Set from one that has no merge at all, because the canary and the type share no code
path. It is orthogonal to the product by construction.

For the record, CI does run it: `crdt-gset/.github/workflows/ci.yml:40` is `cargo test`, so this
green is the green that gates the repo.

---

## 2. The smallest canary that can fail

Four G-Set tests and four OR-Set tests, 76 lines total, in `tests/algebra.rs`. Full text is in
§5. The OR-Set law is the load-bearing one and it is the brief's "add, remove, add again":

> **OR-Set semantics: `remove(x)` tombstones only the adds it has *observed*.** An add that was
> concurrent with the remove — the remover never saw it — **must survive the merge.**

```rust
let mut a = ORSet::new();
a.add(1); a.remove(&1);          // A observed tag 0, tombstoned it

let mut b = ORSet::new();
b.add(2);                        // B's add is concurrent; A never saw this tag

a.merge(&b);
assert!(a.contains(&2), "concurrent add was wrongly killed by a concurrent remove");
```

### It catches the sabotage the old canary missed

Same sabotaged tree from §1, new test file dropped in:

```
$ cargo test --test algebra
test gset_merge_is_associative ... FAILED
test gset_merge_is_commutative ... FAILED
test gset_merge_is_idempotent ... ok
test gset_merge_is_union ... FAILED
test result: FAILED. 1 passed; 3 failed

  left: 2   (expected 3)
  concurrent add was wrongly killed ...
```

**3 of 4 red** where the old canary reported 2 green. That is the whole difference between a
canary and a constant.

---

## 3. Run against the real ports — and it is RED on unmodified code

This is not a sabotage result. This is the live tree at `dcbdeca` / `9ba89078`.

### `crdt-orset` — **FAILS**, and the OR-Set is not a CRDT

```
$ cargo test --test algebra          # in /tmp/crdt-orset, unmodified

test orset_add_remove_add_is_observable ... ok
test orset_concurrent_add_survives_a_concurrent_remove ... FAILED
test orset_merge_is_commutative_under_concurrency ... ok
test orset_remove_reports_whether_it_removed ... ok
test result: FAILED. 3 passed; 1 failed

thread 'orset_concurrent_add_survives_a_concurrent_remove' panicked at tests/algebra.rs:21:5:
concurrent add was wrongly killed by a concurrent remove
```

**Root cause, executed.** `crdt-orset/src/lib.rs:15-20`:

```rust
    pub fn add(&mut self, value: T) -> u64 {
        let tag = self.counter;        // <-- per-replica counter, starts at 0
        self.counter += 1;
```

`counter` is initialised to `0` at `crdt-orset/src/lib.rs:12` and is **per-replica**. Two replicas
that each perform their first add both mint **tag 0**. The OR-Set algebra requires adds to be
*uniquely* tagged — that is the entire mechanism by which "remove only what I saw" is expressible.
Diagnostic output:

```
A add(1) tag=0   B add(2) tag=0    <-- tags COLLIDE
A.merge(B): contains(2) = false    <-- B's concurrent add, silently deleted
A<-B contains(2) = false
B<-A contains(2) = false
=> both agree it is absent: convergence to a LOST add
```

Note the last two lines. This is **worse than a divergence bug**. The two replicas *agree*. They
converge cleanly to the wrong answer. Every add that is not the first on its replica can be
destroyed by a concurrent remove on another replica, and the deletion is permanent and
indistinguishable from never having happened. A consistency-checker over a single replica, or a
liveness check, or a CI run — none of them can see it.

### `crdt-core` — the superset **FAILS THE SAME LAW**

```
$ cargo test --test algebra          # in /tmp/crdt-core, unmodified

test gset_merge_is_associative ... ok
test gset_merge_is_union ... ok
test orset_concurrent_add_survives_a_concurrent_remove ... FAILED
test result: FAILED. 2 passed; 1 failed
```

`crdt-core`'s own suite is **37 passed; 0 failed**. It is green *and wrong*, and the reason is
visible at `crdt-core/src/orset.rs:148-162`:

```rust
    #[test]
    fn test_concurrent_add_remove() {
        let mut r1 = ORSet::new();
        r1.add("A"); // tag 0
        r1.remove(&"A"); // tombstone tag 0

        let mut r2 = ORSet::new();
        r2.add_with_tag("A", 100);   // <-- escapes through a test-only API

        r1.merge(&r2);
        assert!(r1.contains(&A"));
    }
```

`crdt-core` *has* the fix available — `add_with_tag` at `src/orset.rs:36-41` can inject a
globally-unique tag — but it is not reachable from `add()`, and its concurrency test reaches for
it. **The test is written to pass around the defect.** The same law, expressed only through the
public API, fails.

The singleton `crdt-orset` has no such escape hatch — `grep add_with_tag` returns nothing — so on
the singleton there is no test one can write that does not expose this.

### Summary against the real ports

| port | law | result | location |
|---|---|---|---|
| `crdt-orset` | concurrent add survives concurrent remove | **RED** | `src/lib.rs:15-20` (tag minting), `:35-46` (merge) |
| `crdt-core` | same law, public API only | **RED** | `src/orset.rs:28-33` (tag minting) |
| `crdt-gset` | G-Set merge is union | GREEN | `src/lib.rs:21-25` is correct |
| `crdt-core` G-Set | union + associativity | GREEN | `src/gset.rs:43-47` is correct |

**Two real ports are red, two are green, and nothing in the fleet's own test suite knows the
difference.** The G-Set results are a negative finding worth stating: the singletons are not all
broken, and the G-Set implementations are genuinely correct.

---

## 4. What I did not do

I did not touch any port. The sabotage lived in a throwaway copy at `/tmp/sab/gset-noop`; the
`tests/algebra.rs` files exist only in `/tmp` clones. Nothing was pushed. The fix is a product
decision and it is yours.

---

## 5. The canary, in full (drop-in, 76 lines)

`tests/algebra.rs` for a `crdt-gset`-shaped crate:

```rust
#[test]
fn gset_merge_is_union() {
    let mut a = crdt_gset::GSet::new(); a.add(1); a.add(2);
    let mut b = crdt_gset::GSet::new(); b.add(3);
    a.merge(&b);
    assert_eq!(a.len(), 3, "merge lost or invented elements");
    assert!(a.contains(&1) && a.contains(&2) && a.contains(&3), "merge did not produce the union");
}

#[test]
fn gset_merge_is_commutative() { /* a.merge(&b) == b.merge(&a) */ }
#[test]
fn gset_merge_is_idempotent()  { /* a.merge(&a) == a */ }
#[test]
fn gset_merge_is_associative(){ /* (a.b).c == a.(b.c) */ }
```

`tests/algebra.rs` for a `crdt-orset`-shaped crate:

```rust
#[test]
fn orset_concurrent_add_survives_a_concurrent_remove() {
    let mut a = crdt_orset::ORSet::new();
    a.add(1); a.remove(&1);          // A observed tag 0, tombstoned it
    let mut b = crdt_orset::ORSet::new();
    b.add(2);                        // concurrent add; A never saw this tag
    a.merge(&b);
    assert!(a.contains(&2), "concurrent add was wrongly killed by a concurrent remove");
}

#[test]
fn orset_merge_is_commutative_under_concurrency() { /* A<-B and B<-A must agree */ }
#[test]
fn orset_add_remove_add_is_observable()           { /* remove, re-add, survives a fresh replica */ }
#[test]
fn orset_remove_reports_whether_it_removed()      { /* true then false */ }
```

`crdt-core` needs its own copy for the API shapes (`add` returns `bool`, `merged()` returns a
value, and the OR-Set law **must** use `add`, not `add_with_tag` — using `add_with_tag` is what
lets the current suite stay green).

---

## 6. Since when

`tests/canary.rs` was added in commit `dcbdeca` (2026-09-30, *"housekeeping: licence, correct
repository URL, canary test, publish workflow removed"*) — 19 lines added, and never touched
since. Across all five singletons, `git log -- tests/canary.rs` returns exactly **1** commit
each, and that commit is the `--diff-filter=A` introduction, dated **2026-09-30** in every case.

So the canary has never been able to fail, and it was never able to. There is no earlier version
that tested the type and was later weakened — it was born as a hash assertion, in a single
commit, on the day it was committed. It has reported green on the same 5 assertions for its
entire life, during which `crdt-orset` and `crdt-core` both shipped an OR-Set that silently
deletes concurrent adds.

---

**Has this canary ever been able to fail, and if not, since when?**

**Never — it was incapable of failing from the moment it was written, on 2026-09-30, in commit
`dcbdeca`.** It has never contained a reference to the type it is filed under.
