# lau-git-render — REBUILD (BUILDER lane, 2026-10-02)

**Verdict up front:** it **builds**, it **runs**, and the terminal output is
**readable — but only once you hand it data. It reads nothing.** It ships no
binary. The thing that was never switched on is a **crate with no way to be
switched on.**

The honest answer to question 5 is *both*: it does not need rebuilding, and it
needs ~200 lines of glue to be the front door. Details below.

---

## 1. Does it build? — YES. Cleanly.

Clean clone, `cargo 1.99.0` / `rustc 1.99.0`, no `--locked`, no network tricks.

```
$ git clone https://github.com/SuperInstance/lau-git-render.git
$ cd lau-git-render && cargo build

   Compiling proc-macro2 v1.0.106
   Compiling unicode-ident v1.0.24
   Compiling quote v1.0.45
   Compiling serde_core v1.0.228
   Compiling zmij v1.0.21
   Compiling syn v2.0.117
   Compiling serde v1.0.228
   Compiling serde_json v1.0.150
   Compiling serde_derive v1.0.228
   Compiling memchr v2.8.1
   Compiling itoa v1.0.18
   Compiling lau-git-render v0.1.0 (/tmp/lau/lau-git-render)
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 17.40s

real 0m17.434s    BUILD_EXIT=0
```

**Zero warnings.** 12 crates, 2 direct dependencies (`serde`, `serde_json`).
Nothing exotic. This is not a project that rotted — it is a project that was
finished and shelved in working order.

### Tests

```
$ cargo test
...
test result: ok. 96 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
             finished in 0.01s
TEST_EXIT=0

   Doc-tests lau_git_render
running 0 tests
```

**96/96 green.** Zero doc-tests (no doc examples in the crate — the README's
example is not compiled, so it cannot rot, but also cannot be checked).

**Unverified:** the CI workflow also runs `cargo clippy -- -D warnings`. Clippy
is not installed in this sandbox (`rustup component add clippy` would be needed).
I did **not** verify that leg and am not claiming it.

---

## 2. THE FINDING — it reads nothing, and it has no way to be run

Three separate defects, all confirmed by execution, not by reading.

### 2a. `from_repo` is a stub that ignores its own argument

`src/lib.rs:126-129`, verbatim:

```rust
/// Create a snapshot from a repo path (placeholder — real impl reads git).
pub fn from_repo(_repo_path: &str) -> Result<Self, RenderError> {
    // In a real implementation, this would read git refs, parse state files, etc.
    // For now returns a stub that demonstrates the shape.
```

Note the `_` on `_repo_path`. The argument is **unused**. It cannot be
misinterpreted. I rendered three different paths and hashed the output:

```
fleet-triage : 3d95b4898eed3778
nonexistent  : 3d95b4898eed3778
lau-git-render: 3d95b4898eed3778
all three identical: true
```

`/workspace/projects/fleet-triage` (103 markdown files, 2.8 GB, 4 commits) and
`/tmp/this-path-does-not-exist-9f3a` produce **byte-identical** output. The
README's headline claim — *"it already reads a repository and renders it"* — is
**false**. It returns a fixed empty state and renders that.

The 96 green tests do not catch this because **all three tests that call
`from_repo` pass a nonexistent path**:

```
src/lib.rs:1634  RepoSnapshot::from_repo("/tmp/nonexistent")
src/lib.rs:1641  RenderContext::from_repo("/tmp/nonexistent")
src/lib.rs:2439  RepoSnapshot::from_repo("/tmp/nope")
```

`test_repo_snapshot_from_repo` is a test that asserts the stub is a stub. The
suite is green *because* it never touches a real repository. This is the exact
failure mode you have been measuring all day, wearing a different hat: the test
suite exercises the *shape* of the function and never its *content*.

### 2b. There is no binary. There is no CLI. `cargo run` cannot run it.

```
$ cargo install --path .
error: there is nothing to install in `lau-git-render v0.1.0`,
       because it has no binaries
```

The entire repository is `src/lib.rs`. No `main.rs`, no `src/bin/`, no
`examples/`, no `[[bin]]`. It is a library. **Nobody can run this tool.** To
produce the output in this document I had to write ~40 lines of driver myself.

And here is the sentence that matters, given that the repo's own journal says
*"Next duty: Awaiting instructions"*:

**A crate with no binary has no surface on which to receive an instruction.**
It is not that the dispatch failed to arrive. It is that there was no door for
the dispatch to knock on. The journal entry is not an excuse — it is a
*symptom with a cause*.

### 2c. The terminal box is misaligned, and ANSI is unconditional

The one screen a human would look at is hardcoded to 44 columns, and two of its
own lines don't fill it:

```
len= 44  '╔══════════════════════════════════════════╗'
len= 43  '║ branch:  zero-shot-arrival-log          ║'
len= 43  '║ mode:    idle ║'          <-- 17 chars, box collapses
len= 34  '║ rooms: 5  ensigns: 3  tiles: 5139 ║'  <-- 34 chars
len= 34  '║ correlations: 2  provenance: 4 ║'
len= 44  '╚══════════════════════════════════════════╝'
```

`{:<30}` padding is applied per-field against a fixed border, with no shared
width constant. Cosmetically it is the *whole* product — this is the renderer
whose entire job is looking correct on a screen.

Also: `TerminalRenderer` emits ANSI colour codes unconditionally, with no TTY
check. Redirect to a file or pipe to `grep` and you get escape soup (visible in
the paste below). Small, but it is the difference between a demo and a tool.

---

## 3. What the terminal output ACTUALLY looked like

**Against a real repository, as shipped (the README's exact code, verbatim):**

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

**Is the output unreadable? Yes — and this is the most valuable sentence in the
document.** It renders an empty box for a repository containing 103 documents.
It is not garbled; it is *absent*. It looks exactly like success. There is no
error, no warning, no non-zero exit, no indication that the 2.8 GB of
`fleet-triage` was never opened. **A silent wrong answer on the arrival screen
is worse than a crash**, because a crash gets debugged and this gets believed.

**Fed a real snapshot by hand, the renderer is genuinely good.** Same binary,
same code path, real data:

```
╔══════════════════════════════════════════╗
║         REPO SNAPSHOT — TERMINAL        ║
╠══════════════════════════════════════════╣
║ branch:  zero-shot-arrival-log          ║
║ commit:  487fe3f8d6d30bc1d969a7f848618b ║
║ mode:    idle ║
║ time:    1759000000                     ║
╠══════════════════════════════════════════╣
║ rooms: 5  ensigns: 3  tiles: 5139 ║
║ correlations: 2  provenance: 4 ║
╚══════════════════════════════════════════╝

╔══════════════════════════════════════╗
║          ROOM LAYOUT GRID           ║
╠══════════════════════════════════════╣
║ ESC[32m┌─quilt           ─┐ESC[0m ║
║ ESC[32m│ gravity:    0.95  │ESC[0m ║
║ ESC[32m│ alert: green      │ESC[0m ║
║ ESC[32m│ tiles: 1          │ESC[0m ║
║ ESC[32m└──────────────────┘ESC[0m ║
║ ESC[33m┌─triage          ─┐ESC[0m ║
║ ESC[33m│ gravity:    0.80  │ESC[0m ║
║ ESC[33m│ alert: yellow     │ESC[0m ║
║ ESC[33m│ tiles: 103        │ESC[0m ║
║ ESC[33m│  ↳ scout (scout)ESC[0m ║
║ ESC[33m└──────────────────┘ESC[0m ║
...
─── CORRELATIONS ───
  quilt ─── (0.70)── papers linear
  render ─── (0.50)── triage linear
```

(Real output has literal `\x1b[32m` etc. — pasted here as `ESC[…]` for
readability, and that substitution is itself the point about ANSI.)

The projection doctrine is **real and it is good**. One canonical state, many
labelled views. Colour-by-alert, nested ensigns, correlation lines. This is the
graceful-fail ladder from a boat — a watch, a phone, another agent, a screen
reader — and it works.

**The renderer is not the missing thing. The reader is.**

---

## 4. Rendering the account, as it should have happened in June

Same crate, same binary, one `RepoSnapshot` about `SuperInstance`, four
projections. Numbers are measured, not invented.

### TERMINAL — what an agent sees on arrival
*(shown in full in §3; rooms = quilt, triage, constraint-core, papers, render;
ensigns = builder, player, scout; correlations = quilt↔papers, render↔triage)*

### A2A — the structured form another agent should consume

```json
{
  "protocol": "a2a/v1",
  "sender": "hermes-construct/default",
  "type": "RepoStatus",
  "timestamp": 1759000000,
  "snapshot": {
    "branch": "zero-shot-arrival-log",
    "commit_sha": "487fe3f8d6d30bc1d969a7f848618b0fa1c1afd9",
    "identity": "SuperInstance / Casey Digennaro",
    "state": "idle",
    "rooms": [
      { "id": "quilt",            "gravity": 0.95, "alert": "green",  "tile_count": 1 },
      { "id": "triage",           "gravity": 0.8,  "alert": "yellow", "tile_count": 103 },
      { "id": "constraint-core",  "gravity": 0.7,  "alert": "red",    "tile_count": 139068 },
      { "id": "papers",           "gravity": 0.5,  "alert": "red",    "tile_count": 30921 },
      { "id": "render",           "gravity": 0.4,  "alert": "yellow", "tile_count": 1 }
    ],
    "tiles": {
      "total": 5139, "active": 0,
      "by_type": {
        "public_repos": 5139,
        "findings_zero_decisions": 4789,
        "issues_zero_readers": 5471,
        "unrendered_tools": 1
      }
    },
    "conservation": { "budget": 5139.0, "spent": 4789.0, "remaining": 350.0 }
  }
}
```

**The finding survives the projection.** `tiles.active: 0` next to
`findings_zero_decisions: 4789`. The renderer doesn't editorialize — it just
puts the two numbers in the same object and lets them sit next to each other.
That is the correct behaviour for a machine-readable surface.

### VOICE — the plainest text, the one that cannot fail to render

> Repository SuperInstance / Casey Digennaro is in idle mode on branch
> zero-shot-arrival-log. There are 5 rooms. The quilt room is nominal with a
> creative gravity of 0.95 and 1 tiles. The triage room is at yellow alert with
> a creative gravity of 0.80 and 103 tiles. The constraint-core room is at red
> alert with a creative gravity of 0.70 and 139068 tiles. The papers room is at
> red alert with a balanced gravity of 0.50 and 30921 tiles. The render room is
> at yellow alert with a balanced gravity of 0.40 and 1 tiles. 3 ensigns are
> active. Ensign builder running general is on-watch in the render room. Ensign
> player running general is cold-adopting in the render room. Ensign scout
> running scout is idle in the triage room. There is a linear correlation
> between quilt and papers with strength 0.70. There is a linear correlation
> between render and triage with strength 0.50. Conservation budget: 350
> remaining out of 5139.

**This is the strongest output in the crate** and it is the one nobody will
see, because it is the hardest to route anywhere. Note the two things it gets
wrong: `"1 tiles"` (no pluralization) and `"139068 tiles"` (I fed KB into a
tile field — the schema has no unit discipline, so a *caller* created that
lie, not the renderer). Both are one-line fixes. Neither is worth a rewrite.

### DASHBOARD — room cards and gauges, for a human

```json
{
  "layout": "grid",
  "timestamp": 1759000000,
  "widgets": [
    { "type": "room",  "id": "quilt",           "gravity": 0.95, "alert": "green",  "tiles": 1 },
    { "type": "room",  "id": "triage",          "gravity": 0.8,  "alert": "yellow", "tiles": 103 },
    { "type": "room",  "id": "constraint-core", "gravity": 0.7,  "alert": "red",    "tiles": 139068 },
    { "type": "room",  "id": "papers",          "gravity": 0.5,  "alert": "red",    "tiles": 30921 },
    { "type": "room",  "id": "render",          "gravity": 0.4,  "alert": "yellow", "tiles": 1 },
    { "type": "ensign","id": "builder", "model": "general", "room": "render", "status": "on-watch" },
    { "type": "ensign","id": "player",  "model": "general", "room": "render", "status": "cold-adopting" },
    { "type": "ensign","id": "scout",   "model": "scout",   "room": "triage", "status": "idle" },
    { "type": "gauge",  "id": "conservation", "value": 350.0, "max": 5139.0 },
    { "type": "linear", "from": "quilt",  "to": "papers", "strength": 0.7 },
    { "type": "linear", "from": "render", "to": "triage", "strength": 0.5 }
  ]
}
```

Clean, consumable, no code changes needed. This one is done.

---

## 5. Front door — proposed README text. **NOT PUBLISHED.**

Per instruction: proposed only. `SuperInstance/SuperInstance` is 54,451 KB,
7 stars, `description: NONE`, 5,139 public repos, and a 25,827-byte HTML
`<div>`-laden README. It is the front door and it is closed.

A rendered terminal view, as the tool would emit it if `from_repo` were true:

```
╔══════════════════════════════════════════════════════════╗
║  SuperInstance — Casey Digennaro                        ║
║  5,139 public repos · 79 followers · since 2024-12-29    ║
╠══════════════════════════════════════════════════════════╣
║  WHAT THIS IS                                            ║
║  A spreadsheet that thinks. The unit is a cell; sheets    ║
║  compose into programs; agents are cells.                 ║
║                                                          ║
║  IF YOU ARRIVE COLD —                                   ║
║    quilt              the grid is the runtime            ║
║    quilt-adjudication the merge that cannot commit       ║
║                      silently                           ║
║    AGENTS.md          90 seconds, read before anything   ║
║                                                          ║
║  ⚠ 4,789 findings · 0 decisions                          ║
║  ⚠ 5,471 issues · 0 readers                              ║
║                                                          ║
║  I came to software from commercial fishing.             ║
║  On a boat, nobody stops operations to deliver a         ║
║  training course. New crew watch, help, learn by         ║
║  participating.                                          ║
╚══════════════════════════════════════════════════════════╝
```

Deliberate properties: the arrival route is in the first screen, not in a
`<div>`; the two zeroes are on the front page instead of in a report; the
fishing paragraph stays, because it is the actual thesis; a stranger can act
without reading 25 KB.

---

## 6. What is missing for it to be the account's front door

Ordered by cost. Total honest estimate: **one small PR, plus a dispatch.**

1. **A binary.** `src/main.rs`, ~40 lines: `lau <format> [repo]`. Without it
   there is nothing to run, schedule, or dispatch. *This is the whole reason
   it sat asleep for seven weeks.* — **1 hour**
2. **Make `from_repo` read the repo.** `git rev-parse HEAD`, `git branch
   --show-current`, `git log -1 --format=%ct`, count `*.md`, parse
   `AGENT.md` for identity, read `memory/JOURNAL.md` for the duty line. ~150
   lines. Then **delete or rewrite the three tests that pass
   `/tmp/nonexistent`**, and add one that asserts a real repo yields a
   non-empty snapshot. — **half a day**
3. **Make a bad path fail loudly.** `from_repo` must `Err` on a path that is
   not a git repo. Silently returning an empty snapshot on the *arrival
   screen* is the single worst defect here. — **15 min, and non-negotiable**
4. **One width constant + TTY detection** for the box. — **1 hour**
5. **Doc tests for the README example**, so the headline claim is compiled.
   — **20 min**
6. **A dispatch that actually lands.** A tool with a binary, on a schedule, is
   a thing that runs. A tool without one is a thing that is finished.

**And the thing that is not a code problem:** the account has 5,139 repos and a
front door with no description. Rendering the account onto that README is
worth more than any of the above. The renderer is ready for that today. It has
been ready since May. It is not the bottleneck.

---

## 7. Honest answer to "does it need rebuilding, or switching on?"

**It does not need rebuilding. The 2,477 lines are good.** Eight renderers off
one canonical state is the projection doctrine, implemented seven weeks before
it was written down, and the Voice and Dashboard outputs are genuinely
publishable-grade. A rewrite would be the expensive, wrong answer.

**It needs switching on, and "on" is 200 lines of glue, not a rewrite.** The
crate was finished correctly and then left in a form where nothing could
address it. That is not a failure of engineering. It is a failure of
dispatch — the exact finding this project has been measuring all day, arrived
at from the other direction and confirmed by running the thing instead of
trusting the description.

**It did not fail. It was never switchable.**

---

*Build: `cargo build` 17.40s, exit 0, zero warnings. Tests: 96/96 pass, exit 0.
Clippy leg of CI: **not verified** — component unavailable. No push to
`lau-git-render` was made or attempted; `GITHUB_TOKEN` is unset in this
sandbox, so no fork was created either. All work was local to a clean clone in
`/tmp`. 2,477-line `src/lib.rs`, 2 direct dependencies, 12 crates total.*
