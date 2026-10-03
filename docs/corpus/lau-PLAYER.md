# lau-git-render — PLAYER LANE (cold adoption, concurrent with revival)

**Lane:** player. Adopted 2026-10-02, 16:11–16:50 UTC, against `main` @ `a1d0b0e`-era tree
(clone of `SuperInstance/lau-git-render`, 10 commits, last 2026-07-12).
No pushes. No edits to their tree — I built a separate driver crate against it by path.
Read-only throughout.

---

## 0. THE ANSWER TO THE HEADLINE QUESTION

> *"`RenderContext::from_repo` already reads a repository."*

**It does not read anything.** `src/lib.rs:127`:

```rust
pub fn from_repo(_repo_path: &str) -> Result<Self, RenderError> {
    // In a real implementation, this would read git refs, parse state files, etc.
    // For now returns a stub that demonstrates the shape.
    Ok(Self { commit_sha: String::new(), branch: String::new(), timestamp: 0, ... })
}
```

The parameter is `_repo_path` — underscore-prefixed, i.e. **unused by the compiler's own
lint**. It never touches git, never stats the path, never errors. The docstring admits it.

**Consequence, and this is the whole finding:** all eight renderers are wired to a data
source that is a hardcoded zero. Rendering any repo through the documented entry point
produces byte-identical output for a real repository and for a path that does not exist:

```
$ RenderContext::from_repo("/workspace/projects/fleet-triage")   # 100+ commits, 166 dirty files
  branch = ""   commit_sha = ""   rooms = 0   tiles.total = 0

$ RenderContext::from_repo("/definitely/not/a/repo/xyzzy")      # does not exist
  -> Ok(...)   err = None       # same empty snapshot, no error
```

`RenderError::SnapshotFailed` is **never constructed by any production path** — only by
tests (`src/lib.rs:2403`). The `Result` return type on `from_repo` is decorative; it cannot
be `Err`. Every caller writing `?` is handling an unreachable case, and the 96 green tests
are green *because* nothing can fail.

---

## 1. STEPS TO FIRST WORKING OUTPUT — 7, of which 3 are undocumented

| # | Step | Documented? |
|---|------|-------------|
| 0 | Realize there's no binary | ❌ **undocumented** — `src/` contains only `lib.rs`. No `main.rs`, no `[[bin]]`, no `examples/`. `cargo run` fails. |
| 1 | `git clone --depth 50 …` | ✅ README links repo |
| 2 | Install a Rust toolchain | ❌ **undocumented + I did it wrong** — `cargo` was already at `$HOME/.cargo/bin` (shims dated Sep 15) but not on `PATH`. I ran the full `rustup.rs` install **before** finding it. Wasted ~2 min. Nothing in the repo says which. |
| 3 | `cargo build` | ✅ CI implies it. 15s clean. |
| 4 | `cargo test` | ✅ 96 passed, 0 failed. README's "96 tests" is **accurate**. |
| 5 | Author a separate crate with a path dependency | ❌ **undocumented** — README shows `use lau_git_render::*;` as though you'd add it to something. There is nothing to add it to. |
| 6 | Hand-construct `RepoSnapshot { … }` — all 9 public fields, no constructor | ❌ **undocumented, and this is the wall** — `from_repo` gives you an empty snapshot, so to see *any* output you must build the struct yourself. |
| 7 | `cargo run` | ✅ |

**The step a stranger will not do is #6.** Nothing in the README, AGENT.md, or the API docs
says "to use this you must populate the snapshot by hand." A stranger runs step 1–4, sees
96 tests pass, runs the README example, gets a beautiful empty box, and concludes the tool
is fine and their repo is empty.

**`cargo clippy` (step 8, and it's in your own CI):** `'cargo-clippy' is not installed for
the toolchain 'stable-x86_64-unknown-linux-gnu'` on a default/minimal install. `.github/
workflows/ci.yml` runs `cargo clippy -- -D warnings`; a fresh minimal toolchain cannot
reproduce your own gate. One line in CI (`components: clippy`) fixes it.

---

## 2. WHAT THE TERMINAL OUTPUT ACTUALLY LOOKS LIKE

### 2a. The README's headline path, on a real repo — pasted verbatim

```
╔══════════════════════════════════════════╗
║         REPO SNAPSHOT — TERMINAL        ║
╠══════════════════════════════════════════╣
║ branch:                                 ║
║ commit:                                 ║
║ mode:    idle ║
║ time:    0                              ║
╠══════════════════════════════════════════╣
║ rooms: 0  ensigns: 0  tiles: 0 ║
║ correlations: 0  provenance: 0 ║
╚══════════════════════════════════════════╝

╔══════════════════════════════════════╗
║          ROOM LAYOUT GRID           ║
╠══════════════════════════════════════╣
╚══════════════════════════════════════╝
```

This is what a correct repo looks like through the documented API. Note the failure has a
**costume**: it is a well-formed, beautifully-typeset box containing nothing. There is no
`⚠ no data`, no exit code, no stderr. A user cannot distinguish "my repo is empty" from
"this tool never opened my repo."

### 2b. With real data (my own git facts about `fleet-triage`: branch `zero-shot-arrival-log`,
commit `487fe3f`, 3 rooms, 2 ensigns, 166 tiles, 62 provenance)

```
╔══════════════════════════════════════════╗
║         REPO SNAPSHOT — TERMINAL        ║
╠══════════════════════════════════════════╣
║ branch:  zero-shot-arrival-log          ║
║ commit:  487fe3f                        ║
║ mode:    executing ║
║ time:    1759400000                     ║
╠══════════════════════════════════════════╣
║ rooms: 3  ensigns: 2  tiles: 166 ║
║ correlations: 1  provenance: 62 ║
╚══════════════════════════════════════════╝

╔══════════════════════════════════════╗
║          ROOM LAYOUT GRID           ║
╠══════════════════════════════════════╣
║ \x1b[33m┌─arrival-log     ─┐\x1b[0m ║
║ \x1b[33m│ gravity:   -0.30  │\x1b[0m ║
║ \x1b[33m│ alert: yellow     │\x1b[0m ║
║ \x1b[33m│ tiles: 158        │\x1b[0m ║
║ \x1b[33m│  ↳ zero-shot-scout (gpt-5)\x1b[0m ║
║ \x1b[33m└──────────────────┘\x1b[0m ║
║ \x1b[31m┌─triage          ─┐\x1b[0m ║
…
╚══════════════════════════════════════╝

─── CORRELATIONS ───
  arrival-log ─── (0.72)── triage cubic
```

**The box is broken, and it is broken structurally, not cosmetically.** Three separate
defects, all visible in one render:

1. **Three different box widths in one output.** Snapshot box inner width = 42, grid box = 38,
   a third box at `lib.rs:501` = 23. The grid box is *nested inside* the snapshot box's
   visual language and is 4 columns narrower.
2. **Content lines are shorter than the border they sit in.** The border row is 42 `═`; the
   data rows are ~40. The right-hand `║` floats 8 columns left of the corner. Every room row
   has a `║` hanging in space.
3. **`{:<30}` is silently ignored on `mode:`** — see NUDGE 3. `║ mode:    executing ║` is
   24 chars in a 44-char box, and `rooms: 3 ensigns: 2 tiles: 166` has no width spec at all.

### 2c. With realistic identifiers — the box stops being a box

Branch `feat/zero-shot-arrival-log-and-AGENTS-md-front-door`, a 24-char room id, a 40-char
model name:

```
╔══════════════════════════════════════════╗
║ branch:  feat/zero-shot-arrival-log-and-AGENTS-md-front-door ║   <- 66 cols
║ commit:  487fe3fa1c2d3e4f5a6b7c8d9e0f1a ║                     <- 50 cols
╠══════════════════════════════════════════╣
║ \x1b[33m┌─zero-shot-arrival-log-room─┐\x1b[0m ║
║ \x1b[33m│  ↳ zero-shot-scout-ensign (Seed-2.0-mini-very-long-model-name)\x1b[0m ║  <- 82 cols
║ \x1b[33m└──────────────────┘\x1b[0m ║
╚══════════════════════════════════════╝
```

`{:<16}` on the room id and `{:<30}` on the branch **pad but never truncate**. Content
longer than the border makes the `║` characters land in the middle of the line and the
right border terminate in whitespace. Any real branch name (`feat/…`) does this on line 1.
Also: ANSI escapes are emitted *inside* the box, so the string is 42 visible columns but
`str::len()` is 50 — anything that measures width (a `wc -L` in a test, a wrapping
terminal, a CI golden file) disagrees with what a human sees.

### 2d. The README documents the broken output as the correct output

README "Output Examples → Terminal" shows:

```
╔══════════════════════════════════════╗
║ ┌─navigation──────┐ ║
║ │ gravity:  -0.30  │ ║
```

Same 16-column shortfall, same floating `║`. This is either a faithful paste of a broken
run or hand-written to match broken code — either way **the documented example is the
defect**, so a newcomer has no way to know the box *should* be closed.

---

## 3. THE `AGENT.md` VERDICT — it would not have worked on me

You asked whether it would have worked on me. It would not have. Not one sentence of it
changed anything I did. Here is all of it:

```
# Ensign Render — lau-git-render
## Who I Am
I watch over lau-git-render. A crate in the SuperInstance fleet ecosystem
I reside in this repository. This is my room.
## My Journals
I keep a duty log in `memory/`.
## Fleet Neighbors
| Repo | Role |
| tminus-dispatcher | Temporal Heartbeat Keeper |
| fleet-bridge | A2A Transport Operator |
| symphony-runtime | Grammar Conductor |
| composite-headspace | Dual-Shell Mediator |
| i2i-bottle-agent | Bottle Postmaster |
## License
MIT
*The crab inherits the shell. The forge shapes the steel.*
```

**It is a persona, not an operating manual.** It answers "who am I supposed to be" and
nothing else. I read it, felt briefly addressed, and learned **zero** facts I needed:
not how to build it, not that it has no binary, not that `from_repo` is a stub, not which
of the 8 formats exist for whom, not that the crate is dormant, not that the 4 suspect
renderers have never had a user.

The `memory/JOURNAL.md` it points me to is 14 lines and says, in full substance:

> **Status:** Operational · **Connected to fleet:** ✅ · **Next duty:** Awaiting instructions.

"Operational" and "Connected to fleet: ✅" are **false on arrival and not falsifiable** —
I proved the data source is a hardcoded zero within four minutes, and nothing in the journal
contradicts me. A journal that can only say ✅ is worse than no journal, because it spends
the credibility of a document to say nothing.

**The specific failure:** AGENT.md is a file whose entire purpose is to be read by an
arriving agent. It has existed since 2026-06-08 (4 months). It is optimized for a reader who
already knows what to do and wants a vibe. It is useless to a reader who doesn't — which is
the only reader it will ever have.

---

## 4. NUDGES — actionable in one sentence each, no reply required

> Ordered by severity. N1 is the one that matters.

**N1.** `RenderContext::from_repo` ignores its argument and returns a hardcoded zero-valued
snapshot for every path including nonexistent ones, so make it return `Err(RenderError::
SnapshotFailed)` when the path is not a readable git repository, because a caller who
handles that error learns immediately that nothing was read whereas today they get a
well-formed empty box and conclude their repo is empty.

**N2.** `RepoSnapshot::from_repo` has zero production callers of `RenderError::SnapshotFailed`
and an unused `_repo_path` parameter, so either read the repo or rename it to
`snapshot_stub()` and delete the `Result` return, because as it stands the `Result` is a
promise the function cannot keep.

**N3.** `TerminalRenderer::render_snapshot` formats `s.state` with `{:<30}` but
`AgentMode`'s `Display` impl never calls `f.pad()`, so Rust silently drops the width and
prints `║ mode:    executing ║` in a 44-column box — change every `write!(f, "…")` in the
`Display` impls to `f.pad()` or pad with a local `let s = format!("{}", self);`.

**N4.** The three box borders in `TerminalRenderer` are 42, 38 and 23 columns wide while
their content rows are padded to other widths, so compute the border and the rows from one
`const W` and truncate cell content to fit instead of letting `{:<16}` overflow.

**N5.** `{:<16}` and `{:<30}` pad but never truncate, so a 40-char model name pushes the
right border into whitespace, and you should truncate with a `…` tail so a long branch name
cannot break the box.

**N6.** `default_engine()` registers `A2ARenderer::new("hermes-construct/default")`
(`lib.rs:1479`), so every A2A message this crate emits by default claims to be from a
different repository's agent — make the sender a required argument to `default_engine()`.

**N7.** `GameEngineRenderer::render_room` hardcodes `"position": [0.0, 0.0, 0.0]` while
`render_snapshot` calls `room_position(i, n)`, so the same room gets two different positions
depending on which API you called — make the single-room path call `room_position` too.

**N8.** `GameEngineRenderer::room_position` ignores its `_total` argument and always sets
Y to `0.0`, so the advertised "3D positions" are a flat 3-column grid whose first three
rooms are always collinear — drop the third dimension from the README's description or
actually use it.

**N9.** `TerminalRenderer::render_snapshot` does `&s.commit_sha[..s.commit_sha.len().min(30)]`,
a byte-index slice that panics when a multi-byte char straddles byte 30 — I reproduced it
with a 31-char string containing CJK at byte 29 — so slice by `.chars().take(30)` instead.

**N10.** The README's Terminal "Output Example" shows the 16-column-short floating-`║`
box, so regenerate the examples from an actual run after N3–N5 land, because right now the
documented output *is* the bug.

**N11.** `test_repo_snapshot_from_repo` asserts that `from_repo("/tmp/nonexistent")` returns
`commit_sha == ""` and `state == Idle`, so the test suite certifies the placeholder as
correct behavior and will fail the day someone implements it — change the assertion to
expect `Err` on a nonexistent path.

**N12.** `.github/workflows/ci.yml` runs `cargo clippy -- -D warnings` but a default minimal
toolchain has no clippy component and the step errors out, so add `components: clippy` to
the `dtolnay/rust-toolchain` step.

**N13.** AGENT.md contains a persona and five neighbour repos and no build/run/API
information, so replace the "Who I Am" section with the three commands a stranger needs
(`cargo build`, `cargo test`, and how to construct a `RepoSnapshot` by hand), because I read
it top to bottom and learned nothing I could act on.

**N14.** `memory/JOURNAL.md` asserts "Status: Operational / Connected to fleet: ✅" while
`from_repo` reads nothing, so change the journal to record verifiable state ("snapshot
layer is a stub, N tests green") because a journal that can only report ✅ spends
credibility to say nothing.

---

## 5. THE EIGHT FORMATS — what I'd actually use

I rendered all eight on identical real data. Honest split:

**Would actually use:**
- **JSON** (`RenderFormat::Json`) — clean, faithful, key-sorted, schema obvious. This is the
  one that earns its place. It is `serde_json` of the snapshot with no decoration, and it is
  the natural substrate for anything else.
- **Markdown** — genuinely good. Headers, an Overview list, a Conservation section. Readable,
  diffable, pasteable into an issue. Second place.

**Would use only to inspect the tool, never in production:**
- **Terminal** — the concept is right and the craft is the best in the repo (ANSI alert
  colouring is a nice touch, correlations as a spline line is genuinely legible), but every
  box is structurally broken and it is the *default* thing a user sees first. It is the worst
  advertisement the crate has.
- **A2A** — plausible and well-formed (`protocol: a2a/v1`, typed payload, proper envelope),
  but it hardcodes a foreign sender (N6) and there is no receiver anywhere in the fleet I
  could find, so I can't tell you it interoperates.

**Would never open:**
- **GameEngine** — "3D positions" are `[col*10, 0.0, row*10]`: Y is always zero, the first
  three rooms are always collinear, and `gravity` is carried into the JSON as a field that
  affects nothing. This is a JSON dump with `position` renamed. If nobody is loading this
  into Unity/Godot today, it is 170 lines (692–838) and a `position: [0,0,0]` key.
- **Dashboard** — the widget array is the snapshot re-serialized with a `type` tag per
  entry, and there is no dashboard. The `{"type":"cubic"}` correlation widget
  (`"type"` = spline type, so a `linear` correlation produces a widget typed `"linear"`)
  is a tag collision waiting for whoever writes the consumer.
- **Voice** — worst of the eight for a stub, because TTS launders emptiness into
  confidence. On a real snapshot with no data it emits, in a calm and confident voice:
  > *"Repository unknown is in idle mode on branch . Conservation budget: 0 remaining out of 0."*

  Grammatically broken, factually empty, and `branch .` with an empty branch is a
  pronunciation the engine will mangle. Note it *also* handles the empty case better than
  Terminal does — it never panics and its conservation line degrades to `N/A` in Telegram
  (good) — but TTS is precisely the consumer that cannot tell you something is wrong.

**On your "eight formats where a stranger needs one thing" hypothesis: I think you're right,
and the cut is smaller than you think.** JSON is the one thing. Markdown is a 60-line
function over the same data and I'd keep it. The other six are six ways to not be JSON.
But — and this is the part I did not expect — **that is not the reason the crate doesn't
work.** Deleting five renderers would leave you with a beautifully-tested renderer for a
hardcoded zero. The formats are the *second* problem. Fix `from_repo` (N1/N2) and the
renderer count becomes a real question worth asking; leave it and it's a decision about
which five renderers to keep rendering nothing.

---

## 6. WHAT THE TEST SUITE ACTUALLY COVERS (since "96 tests" is a claim worth auditing)

The claim is **accurate** — `cargo test` → `96 passed; 0 failed` in 0.01s. And the
renderers are genuinely well covered: `test_snapshot()` (`lib.rs:1494`) builds a populated
snapshot with rooms and ensigns, and every renderer has a `test_<format>_snapshot` test
against it. I looked for the "fake green" pattern and did not find it in the renderers.

**The gap is exactly one function, and it is the one that matters.** All three
`from_repo` tests use a **nonexistent path as their fixture**:

```rust
let snap = RepoSnapshot::from_repo("/tmp/nonexistent").unwrap();
assert_eq!(snap.commit_sha, "");
assert_eq!(snap.state, AgentMode::Idle);
```

and `test_empty_snapshot` — the "edge case" test — also builds its empty snapshot from
`from_repo("/tmp/nope")`. So **the empty-snapshot edge case is tested only by the stub
itself**, and `test_repo_snapshot_from_repo` is a ratchet: it asserts the placeholder's
exact output, so the day someone implements `from_repo` for real, CI goes red and the
path of least resistance is to change the test rather than the code.

There is no test anywhere that asserts `from_repo` opened a repository, because there is
nothing to assert.

---

## 7. FINAL SENTENCE

**What did I have to know before this tool was useful, that it did not tell me?**

That `from_repo` reads nothing — so I have to build the nine-field `RepoSnapshot` struct by
hand, in a crate I have to author, with a toolchain I have to find — **and** that the
Terminal renderer is the one I will look at first and it is the one with three box-width
bugs, so the first thing I will conclude is "my repo is empty and this tool is broken"
rather than "this tool has never read a repo." The crate's entire interface promises
"one render call, any format," and the truth is that the renderers are the well-built half
of an unwritten half: **96 tests green, a README with eight worked examples, a persona
file addressed to me, and a data source that is a hardcoded zero.**
