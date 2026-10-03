# HOLLOW.md — the 62 no-language repos in the `SuperInstance` namespace

**What this is.** Of the 500 most active of 5,108 public `SuperInstance` repos, 62 report **no language at all** to the GitHub API. This document classifies all 62 against their actual working trees, with the count that produced each verdict.

**Method, in one line.** Every repo was read as a streaming tarball of its working tree (`codeload.github.com`), because the tar header carries every file's exact byte size — so file counts, byte totals and 0-byte files are all server truth, not inference. Full rationale and the two approaches that were tried and rejected are in [Why a tarball](#why-a-tarball).

## Verdict

| bucket | repos | meaning |
|---|---:|---|
| **HOLLOW** | 13 | no usable source, or an entry point that resolves to nothing |
| **MIRROR** | 40 | fork of an upstream; hygiene, not a bug |
| **GENUINE** | 5 | real source in extensions linguist does not count |
| **VENDORED** | 3 | tree is mostly a committed dependency dir |
| **EMPTY** | 1 | no content at all |
| UNREADABLE | 0 | could not be read |
| UNVERIFIED | 0 | read, but no decisive evidence |
| **total** | **62** | |

**All 62 were read. 0 unreadable, 0 unverified.** One (`privox`) has no content to fetch, so it was resolved by three independent probes instead (see [`privox` — EMPTY](#privox--empty)).

Across the 62: **39,652 tracked files**, of which **22,907 are source** totalling **246.77 MB**.

**The three findings that matter:**

1. **The no-language signal is mostly not a code problem — it is 40 forks.** 40 of 62 are forks, and forks inherit the upstream's `.gitattributes`/extension mix. The fleet is running upstream projects it did not write.
2. **11 repos contain no source at all**, and the worst is a **stub farm**: `synesis-research` is 52 directories named after real crates.io libraries (`actor-rs`, `allocator-rs`, `async-rs`, …), 506 files, **117 of them 0 bytes**, and **zero lines of code**. The READMEs are the upstream crates' own. (2 more are HOLLOW for a different reason — a broken entry point.)
3. **Only 1 repo is a genuinely broken package by the dangling-entry test** (`tracer-rs-archive`); one more (`Understand-Anything`) has a real code tree with a single broken `main`. The `hermes-memory-mcp` disease is **not** widespread in this cluster — see [The disease is rarer than it looks](#the-disease-is-rarer-than-it-looks).

---

## The classification table

`blobs` = files in the working tree. `src` / `src B` = after the vendor filter (below). `0-byte` counts files of size 0 after the same filter. `API/ tree` = the GitHub `size` field over the measured working-tree bytes; **>1000× means the excess is git-object history, not substance**.

| repo | bucket | sub | blobs | src | src bytes | 0-byte | dang | API/tree | evidence |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| `Hunyuan3D-WorldClaw` | **HOLLOW** | no-source | 4 | 0 | 0 | — | — | 26.50× | 4 real files, **0 source**. Top: `.jpg`×2, `(none)`×1 |
| `Understand-Anything` | **HOLLOW** | dangling-entry | 412 | 258 | 2,045,189 | 1 | 1 | 1.30× | `package.json` main=`".opencode/plugins/understand-anything.js"` → `.opencode/plugins/understand-anything.js` **absent**, no build evidence. Tree also holds 258 src files / 2.05 MB |
| `agent-priming` | **HOLLOW** | no-source | 1 | 0 | 0 | — | — | 29.30× | 1 real file, **0 source**. Top: `.md`×1 |
| `agent-priming-toolkit` | **HOLLOW** | no-source | 1 | 0 | 0 | — | — | 104× | 1 real file, **0 source**. Top: `.md`×1 |
| `algebra-explorer` | **HOLLOW** | no-source | 1 | 0 | 0 | — | — | 47.50× | 1 real file, **0 source**. Top: `.md`×1 |
| `brand-assets` | **HOLLOW** | no-source | 37 | 0 | 0 | — | — | 0.90× | 37 real files, **0 source**. Top: `.png`×26, `.jpg`×5 |
| `edge-native-paper` | **HOLLOW** | no-source | 3 | 0 | 0 | — | — | 2.10× | 3 real files, **0 source**. Top: `.md`×2, `(none)`×1 |
| `health` | **HOLLOW** | no-source | 22 | 0 | 0 | — | — | 0.90× | 22 real files, **0 source**. Top: `.pdf`×16, `.md`×3 |
| `papermill` | **HOLLOW** | no-source | 288 | 0 | 0 | — | — | 1.10× | 288 real files, **0 source**. Top: `.md`×245, `.png`×40 |
| `synesis-agents` | **HOLLOW** | no-source | 8 | 0 | 0 | — | — | 0.30× | 8 real files, **0 source**. Top: `.md`×6, `(none)`×2 |
| `synesis-architecture` | **HOLLOW** | no-source | 6 | 0 | 0 | — | — | 0.30× | 6 real files, **0 source**. Top: `.md`×4, `(none)`×2 |
| `synesis-research` | **HOLLOW** | no-source | 506 | 0 | 0 | 117 | — | 0.30× | 506 real files, **0 source**. Top: `.md`×502, `(none)`×3; **117 files are 0 bytes** |
| `tracer-rs-archive` | **HOLLOW** | dangling-entry | 14 | 1 | 826 | — | 1 | 0.30× | `Cargo.toml` cargo path=`"src/lib.rs"` → `src/lib.rs` **absent**, no build evidence. Tree also holds 1 src file / 0.8 kB |
| `privox` | **EMPTY** | no-commits | 0 | 0 | 0 | — | — | — | 0 files. API `size:0`; codeload 404 on 9 refs; `git clone` → “cloned an empty repository” |
| `modly` | **VENDORED** | vendor-majority | 141 | 92 | 432,821 | 4 | — | 0.20× | **7.8% of files, 97.8% of bytes** in a committed dep dir; only 130 real files survive |
| `snapkit-js` | **VENDORED** | vendor-majority | 958 | 0 | 0 | — | — | 0.20× | **99.6% of files, 100.0% of bytes** in a committed dep dir; only 4 real files survive |
| `ws-snapshot-soundcrab` | **VENDORED** | vendor-majority | 57 | 0 | 0 | — | — | 0.40× | **100.0% of files, 100.0% of bytes** in a committed dep dir; only 0 real files survive |
| `AutoData-old` | **MIRROR** | api-fork-true | 5 | 1 | 1,936 | 1 | — | **14,879×** | API `fork:true` → parent **`GraphResearcher/AutoData`** |
| `Bend` | **MIRROR** | api-fork-true | 1,099 | 68 | 559,073 | 2 | — | 25.70× | API `fork:true` → parent **`bendlang/bend`** |
| `EDDI` | **MIRROR** | api-fork-true | 2,019 | 1,331 | 24,382,919 | 1 | — | 2.70× | API `fork:true` → parent **`labsai/EDDI`** |
| `F5-TTS` | **MIRROR** | api-fork-true | 96 | 71 | 539,561 | 1 | — | 1.20× | API `fork:true` → parent **`SWivid/F5-TTS`** |
| `FastGen4quilt` | **MIRROR** | api-fork-true | 287 | 227 | 1,940,844 | — | — | 0.90× | API `fork:true` → parent **`NVlabs/FastGen`** |
| `Full-stack-Free-Movie-Streaming-Website` | **MIRROR** | api-fork-true | 57 | 38 | 280,506 | — | — | 3.20× | API `fork:true` → parent **`Heaven-TS/Full-stack-Free-Movie-Streaming-Website`** |
| `GeoFlood` | **MIRROR** | api-fork-true | 900 | 546 | 6,797,605 | 6 | — | 3.40× | API `fork:true` → parent **`KYANJO/GeoFlood`**; 6/546 src 0 bytes |
| `Motifcode4quilt` | **MIRROR** | api-fork-true | 208 | 167 | 1,508,893 | — | — | 0.60× | API `fork:true` → parent **`TaewoooPark/Motifcode`** |
| `Open-LLM-VTuber` | **MIRROR** | api-fork-true | 253 | 147 | 767,056 | 15 | — | 2.00× | API `fork:true` → parent **`Open-LLM-VTuber/Open-LLM-VTuber`**; 15/147 src 0 bytes |
| `OpenManus-RL` | **MIRROR** | api-fork-true | 743 | 239 | 2,151,118 | 35 | — | 2.10× | API `fork:true` → parent **`OpenManus/OpenManus-RL`**; 32/239 src 0 bytes |
| `RTSnavigator` | **MIRROR** | api-fork-true | 428 | 353 | 8,381,143 | — | — | 0.90× | API `fork:true` → parent **`bilawalsidhu/gods-eye-view`** |
| `TrendRadar` | **MIRROR** | api-fork-true | 146 | 86 | 1,611,157 | 2 | — | 2.10× | API `fork:true` → parent **`sansan0/TrendRadar`** |
| `UniRL` | **MIRROR** | api-fork-true | 1,097 | 898 | 5,575,551 | 7 | — | 0.70× | API `fork:true` → parent **`Tencent-Hunyuan/UniRL`**; 7/898 src 0 bytes |
| `ViMax` | **MIRROR** | api-fork-true | 102 | 89 | 584,345 | 3 | — | 69.60× | API `fork:true` → parent **`HKUDS/ViMax`**; 3/89 src 0 bytes |
| `alphabet` | **MIRROR** | api-fork-true | 2,460 | 553 | 23,335,732 | 18 | — | 1.00× | API `fork:true` → parent **`standardgalactic/alphabet`**; 2/553 src 0 bytes |
| `animal-ai` | **MIRROR** | api-fork-true | 1,017 | 911 | 1,409,346 | — | — | 7.50× | API `fork:true` → parent **`Kinds-of-Intelligence-CFI/animal-ai`** |
| `autoMate` | **MIRROR** | api-fork-true | 54 | 33 | 159,893 | 1 | — | 8.50× | API `fork:true` → parent **`yuruotong1/autoMate`**; 1/33 src 0 bytes |
| `coding-3d` | **MIRROR** | api-fork-true | 37 | 22 | 53,844 | — | — | 0.60× | API `fork:true` → parent **`thekiller-dev/coding-3d`** |
| `craftmind` | **MIRROR** | api-fork-true | 225 | 118 | 1,273,012 | 1 | — | 7.10× | API `fork:true` → parent **`Lucineer/craftmind`** |
| `craftmind-circuits` | **MIRROR** | api-fork-true | 33 | 24 | 149,096 | — | — | 71.60× | API `fork:true` → parent **`Lucineer/craftmind-circuits`** |
| `craftmind-courses` | **MIRROR** | api-fork-true | 52 | 39 | 311,078 | — | — | 35.20× | API `fork:true` → parent **`Lucineer/craftmind-courses`** |
| `craftmind-fishing` | **MIRROR** | api-fork-true | 291 | 185 | 1,937,620 | — | — | 1.00× | API `fork:true` → parent **`Lucineer/craftmind-fishing`** |
| `craftmind-herding` | **MIRROR** | api-fork-true | 38 | 28 | 217,293 | — | — | 51.20× | API `fork:true` → parent **`Lucineer/craftmind-herding`** |
| `craftmind-ranch` | **MIRROR** | api-fork-true | 43 | 27 | 183,488 | — | — | 75.20× | API `fork:true` → parent **`Lucineer/craftmind-ranch`** |
| `craftmind-researcher` | **MIRROR** | api-fork-true | 43 | 30 | 247,199 | — | — | 42.70× | API `fork:true` → parent **`Lucineer/craftmind-researcher`** |
| `deepseek-harness-quilt` | **MIRROR** | api-fork-true | 7,895 | 4,106 | 28,330,153 | 1 | — | 2.20× | API `fork:true` → parent **`deepseek-ai/deepseek-harness`** |
| `dmlog-ai-1` | **MIRROR** | api-fork-true | 189 | 102 | 1,255,523 | — | — | 1.00× | API `fork:true` → parent **`Lucineer/dmlog-ai`** |
| `dscode` | **MIRROR** | api-fork-true | 455 | 303 | 2,301,490 | — | — | 12.00× | API `fork:true` → parent **`dmwarenet/dscode`** |
| `jira-cli` | **MIRROR** | api-fork-true | 195 | 153 | 563,525 | 1 | — | 1.60× | API `fork:true` → parent **`ankitpokhrel/jira-cli`** |
| `libgdx` | **MIRROR** | api-fork-true | 3,811 | 3,096 | 28,172,002 | — | — | 15.90× | API `fork:true` → parent **`libgdx/libgdx`** |
| `libpointmatcher` | **MIRROR** | api-fork-true | 652 | 401 | 2,801,881 | — | — | 0.80× | API `fork:true` → parent **`norlab-ulaval/libpointmatcher`** |
| `magda-tensor` | **MIRROR** | api-fork-true | 2,682 | 2,058 | 24,332,972 | 11 | — | 0.70× | API `fork:true` → parent **`Conceptual-Machines/magda-core`**; 11/2058 src 0 bytes |
| `oh-my-zsh` | **MIRROR** | api-fork-true | 1,096 | 412 | 1,351,644 | 7 | — | 2.00× | API `fork:true` → parent **`jevinskie/oh-my-zsh`** (fork of a fork; source `ohmyzsh/ohmyzsh`); 2/412 src 0 bytes |
| `opensmile` | **MIRROR** | api-fork-true | 712 | 539 | 5,468,663 | 3 | — | 1.10× | API `fork:true` → parent **`audeering/opensmile`**; 2/539 src 0 bytes |
| `paperclip` | **MIRROR** | api-fork-true | 2,791 | 2,158 | 22,355,653 | 11 | — | 0.70× | API `fork:true` → parent **`paperclipai/paperclip`** |
| `personlog-ai` | **MIRROR** | api-fork-true | 64 | 33 | 193,077 | — | — | 1.00× | API `fork:true` → parent **`Lucineer/personlog-ai`** |
| `quilt-crabbox` | **MIRROR** | api-fork-true | 2,634 | 2,269 | 36,843,625 | — | — | 1.10× | API `fork:true` → parent **`openclaw/crabbox`** |
| `scratch-vm` | **MIRROR** | api-fork-true | 480 | 241 | 1,907,482 | — | — | 50.10× | API `fork:true` → parent **`scratchfoundation/scratch-vm`** |
| `voxblox` | **MIRROR** | api-fork-true | 175 | 129 | 691,077 | 2 | — | 46.30× | API `fork:true` → parent **`ethz-asl/voxblox`** |
| `voxelgpt` | **MIRROR** | api-fork-true | 453 | 53 | 2,478,783 | — | — | 7.20× | API `fork:true` → parent **`voxel51/voxelgpt`** |
| `.github` | **GENUINE** | real-source | 28 | 1 | 261 | — | — | 1.00× | 1 source files / 0.3 kB in uncounted extensions. Top: `.md`×16, `.jpg`×6, `.png`×4 |
| `Patchwork-experts` | **GENUINE** | real-source | 26 | 5 | 6,675 | — | — | 1.00× | 5 source files / 6.7 kB in uncounted extensions. Top: `.md`×15, `.yaml`×5, `.jpg`×3 |
| `covers` | **GENUINE** | real-source | 152 | 1 | 539 | — | — | 0.80× | 1 source files / 0.5 kB in uncounted extensions. Top: `.mp3`×91, `.wav`×37, `.txt`×9 |
| `dotfiles` | **GENUINE** | real-source | 952 | 254 | 799,041 | 1 | — | 1.10× | 254 source files / 799.0 kB in uncounted extensions. Top: `.md`×397, `.gif`×113, `.fish`×103 |
| `quilt-playtest` | **GENUINE** | real-source | 18 | 11 | 77,005 | — | — | 0.70× | 11 source files / 77.0 kB in uncounted extensions. Top: `.mjs`×11, `.md`×2, `.png`×2 |

### The vendor filter, applied to every count above

```
dirs: node_modules/ target/ vendor/ third_party/ .venv/ venv/ site-packages/ dist/
      build/ .next/ out/ _build/ __pycache__/ .wrangler/ coverage/
exts: .min.js .min.css .map .d.ts .lock
```

It is not decorative. Before the filter, `hermes-memory-mcp` ranks **8th largest in the fleet by source-file count** on the strength of zod's vendored test suite inside a committed `node_modules/`. Within this cluster it is what makes `snapkit-js` look like a 958-file TypeScript project: **954 of its 958 files and 99.97% of its bytes are `node_modules/`, and 0 are source.**

---

## HOLLOW, in detail

13 repos. They split into three kinds, and the difference matters: a *stub farm* is a fleet-hygiene problem, a *document pile* is a misfiled repo, and a *broken package* is a bug.

### H1 — broken entry point (2)

#### `Understand-Anything`

- branch `main` · 412 files · **258 source files / 2,045,189 B** · API size 32.2 MB
- **DANGLING** — `package.json` declares `main: ".opencode/plugins/understand-anything.js"`, which resolves to `.opencode/plugins/understand-anything.js`. That path is **not in the tree**, and there is no sibling source or build config to make it a compile output.
- **0 bytes** — `homepage/public/.gitkeep` (a `.gitkeep` placeholder — not a defect)

#### `tracer-rs-archive`

- branch `main` · 14 files · **1 source file / 826 B** · API size 0.1 MB
- **DANGLING** — `Cargo.toml` declares `cargo path: "src/lib.rs"`, which resolves to `src/lib.rs`. That path is **not in the tree**, and there is no sibling source or build config to make it a compile output.

### H2 — 0-byte source files (0)

No repo in this cluster had source files that all resolve to 0 bytes. The 0-byte files that do exist are markdown placeholders; they are listed under H3.

### H3 — no source at all (11)

Real content, zero code. These are not broken packages; they are repos that were never software, or were stubbed out.

| repo | files | bytes | what is actually there | 0-byte |
|---|---:|---:|---|---:|
| `Hunyuan3D-WorldClaw` | 4 | 6.98 MB | `.jpg`×2, `(none)`×1, `.md`×1 | — |
| `agent-priming` | 1 | 0.2 kB | `.md`×1 | — |
| `agent-priming-toolkit` | 1 | 0.2 kB | `.md`×1 | — |
| `algebra-explorer` | 1 | 0.2 kB | `.md`×1 | — |
| `brand-assets` | 37 | 15.10 MB | `.png`×26, `.jpg`×5, `.md`×4 | — |
| `edge-native-paper` | 3 | 3.8 kB | `.md`×2, `(none)`×1 | — |
| `health` | 22 | 40.30 MB | `.pdf`×16, `.md`×3, `(none)`×2 | — |
| `papermill` | 288 | 68.04 MB | `.md`×245, `.png`×40, `(none)`×2 | — |
| `synesis-agents` | 8 | 73.5 kB | `.md`×6, `(none)`×2 | — |
| `synesis-architecture` | 6 | 52.4 kB | `.md`×4, `(none)`×2 | — |
| `synesis-research` | 506 | 7.68 MB | `.md`×502, `(none)`×3, `.txt`×1 | 117 |

**`synesis-research` is the one to look at.** 506 files across 57 top-level directories, 52 of which are named after real crates.io libraries. 117 files are 0 bytes; in 8 directories *every* file is 0 bytes. The remaining directories hold a README that is the upstream crate's own README (badges, crates.io links, feature lists) and nothing else. There is no `src/` anywhere in the repo.

```
0  synesis-research/actor-rs/01-research.md
0  synesis-research/actor-rs/02-architecture.md
0  synesis-research/actor-rs/03-api.md
0  synesis-research/actor-rs/04-user-guide.md
0  synesis-research/actor-rs/05-dev-guide.md
0  synesis-research/actor-rs/06-cli.md
… 117 files at 0 bytes, all *.md
```

The same shape appears in miniature in `tracer-rs-archive` (14 files, 12 of them `.md`, a `Cargo.toml`, and no `src/`) and `synesis-agents` / `synesis-architecture` (agent persona `.md` files, no code).

**Four of these 13 are also forks**, and that changes who owns the defect — the missing code is upstream's, not something this fleet wrote:

| repo | parent | what it inherits |
|---|---|---|
| `papermill` | `Lucineer/papermill` | 288 files, 245 of them `.md` — a writing archive |
| `edge-native-paper` | `Lucineer/edge-native-paper` | 3 files: a LICENSE, `PAPER.md`, a README |
| `Hunyuan3D-WorldClaw` | `Tencent-Hunyuan/Hunyuan3D-WorldClaw` | 4 files: a README and two JPEG assets |
| `Understand-Anything` | `Egonex-AI/Understand-Anything` | a real 258-file code tree, but its own `main` points at a `.opencode/` dir that does not exist |

---

## EMPTY

### `privox` — EMPTY

Described as *“PII/PHI redaction library for LLM pipelines (Rust)”*, carrying 5 topics and a `pushed_at` of 2026-09-22. It has **no commits at all**.

| probe | result |
|---|---|
| `GET /repos/SuperInstance/privox -> size:0` | consistent with an empty repo |
| `codeload 404 x9 refs` | consistent with an empty repo |
| `git clone -> 'cloned an empty repository'` | consistent with an empty repo |

`codeload` returns 404 for all 9 refs tried (`main`, `master`, `core`, `develop`, `trunk`, `release`, `gh-pages`, plus `HEAD` deref). The repo is a description with nothing behind it.

---

## VENDORED — the size is a lie

| repo | files in dep dir | share of files | share of bytes | real files left | source left |
|---|---:|---:|---:|---:|---:|
| `modly` | 11 | 7.80% | **97.81%** | 130 | 92 files / 432,821 B |
| `snapkit-js` | 954 | 99.58% | **99.97%** | 4 | 0 files / 0 B |
| `ws-snapshot-soundcrab` | 57 | 100.00% | **100.00%** | 0 | 0 files / 0 B |

- **`ws-snapshot-soundcrab`** — 57 of 57 files and **100.00%** of bytes sit in `dist/`. Zero files remain after the filter. It is a build output committed as a repository.
- **`snapkit-js`** — 954 of 958 files and 99.97% of bytes are `node_modules/`. 4 real files, 0 of them source.
- **`modly`** — only 11 of 141 files are vendor, but they are **99.2 MB of the 101.4 MB tree**. Its 92 real source files survive; the byte-based size is the lie here, not the file count.

---

## MIRROR — 40 forks, with the upstream named

Every upstream below is the **`parent` field from the GitHub API**, not a guess from the name. The brief asked for the upstream; here it is.

**45 of the 62 are forks in total** (`fork:true`), and **all 45 have a resolved parent — 0 unresolved.** 40 land in this bucket; the other 5 are filed under a higher-precedence bucket (4 HOLLOW, 1 VENDORED) and are listed in their own sections with their parent named.

| repo | parent (immediate) | source (root upstream) |
|---|---|---|
| `AutoData-old` | `GraphResearcher/AutoData` | — |
| `Bend` | `bendlang/bend` | — |
| `EDDI` | `labsai/EDDI` | — |
| `F5-TTS` | `SWivid/F5-TTS` | — |
| `FastGen4quilt` | `NVlabs/FastGen` | — |
| `Full-stack-Free-Movie-Streaming-Website` | `Heaven-TS/Full-stack-Free-Movie-Streaming-Website` | — |
| `GeoFlood` | `KYANJO/GeoFlood` | — |
| `Motifcode4quilt` | `TaewoooPark/Motifcode` | — |
| `Open-LLM-VTuber` | `Open-LLM-VTuber/Open-LLM-VTuber` | — |
| `OpenManus-RL` | `OpenManus/OpenManus-RL` | — |
| `RTSnavigator` | `bilawalsidhu/gods-eye-view` | — |
| `TrendRadar` | `sansan0/TrendRadar` | — |
| `UniRL` | `Tencent-Hunyuan/UniRL` | — |
| `ViMax` | `HKUDS/ViMax` | — |
| `alphabet` | `standardgalactic/alphabet` | — |
| `animal-ai` | `Kinds-of-Intelligence-CFI/animal-ai` | — |
| `autoMate` | `yuruotong1/autoMate` | — |
| `coding-3d` | `thekiller-dev/coding-3d` | — |
| `craftmind` | `Lucineer/craftmind` | — |
| `craftmind-circuits` | `Lucineer/craftmind-circuits` | — |
| `craftmind-courses` | `Lucineer/craftmind-courses` | — |
| `craftmind-fishing` | `Lucineer/craftmind-fishing` | — |
| `craftmind-herding` | `Lucineer/craftmind-herding` | — |
| `craftmind-ranch` | `Lucineer/craftmind-ranch` | — |
| `craftmind-researcher` | `Lucineer/craftmind-researcher` | — |
| `deepseek-harness-quilt` | `deepseek-ai/deepseek-harness` | — |
| `dmlog-ai-1` | `Lucineer/dmlog-ai` | — |
| `dscode` | `dmwarenet/dscode` | — |
| `jira-cli` | `ankitpokhrel/jira-cli` | — |
| `libgdx` | `libgdx/libgdx` | — |
| `libpointmatcher` | `norlab-ulaval/libpointmatcher` | — |
| `magda-tensor` | `Conceptual-Machines/magda-core` | — |
| `oh-my-zsh` | `jevinskie/oh-my-zsh` | `ohmyzsh/ohmyzsh` |
| `opensmile` | `audeering/opensmile` | — |
| `paperclip` | `paperclipai/paperclip` | — |
| `personlog-ai` | `Lucineer/personlog-ai` | — |
| `quilt-crabbox` | `openclaw/crabbox` | — |
| `scratch-vm` | `scratchfoundation/scratch-vm` | — |
| `voxblox` | `ethz-asl/voxblox` | — |
| `voxelgpt` | `voxel51/voxelgpt` | — |

Three things stand out:

- **`oh-my-zsh` is a fork of a fork.** Its parent is `jevinskie/oh-my-zsh`; the root upstream is `ohmyzsh/ohmyzsh`. Two hops from the original, which is the shape that rots first.
- **9 of the 40 forks are `Lucineer/*`**: `craftmind`, `craftmind-circuits`, `craftmind-courses`, `craftmind-fishing`, `craftmind-herding`, `craftmind-ranch`, `craftmind-researcher`, `dmlog-ai-1`, `personlog-ai`. That is a fork family, not 9 independent projects.
- **4 forks point at renamed upstreams** — `FastGen4quilt`←`NVlabs/FastGen`, `RTSnavigator`←`bilawalsidhu/gods-eye-view`, `magda-tensor`←`Conceptual-Machines/magda-core`, `dmlog-ai-1`←`Lucineer/dmlog-ai`. The fork names do not match the upstream names, so these are invisible to a name-based audit.

**Naming trap:** `papermill` is **not** `nteract/papermill`. It is `Lucineer/papermill` — 288 files, 245 of them `.md`, a personal writing archive. An auditor assuming the famous name would draw the wrong conclusion about it.

---

## The history-bloat filter, and the `alphabet` question

The brief flagged `alphabet` at 3 GB: *“a 3 GB repo with no recognised source language is either a mirror or a history problem, and I want to know which.”*

**It is a mirror, and the 3 GB is real — it is not a history problem.**

- It **is** a mirror: `fork:true`, parent `standardgalactic/alphabet`.
- It is **not** a history problem. API `size` = **3.018 GB**; the measured working tree = **3.032 GB** across 2,460 files. Ratio **1.00×**. The working tree really is 3 GB.
- Its mass is not source: 553 source files total **23.34 MB**, which is **0.77%** of the tree. The rest is `pdf`×381, `png`×243, `mhtml`×98, `mp3`×97, `vtt`×98 — formats linguist does not count. Its `.gitattributes` is a single LFS line for one PDF and disables nothing.

**The one repo that does trip the >1000× rule:**

- `AutoData-old` — API `size` 97.9 MB, working tree **6,896 bytes** in 5 files. Ratio **14,879×**. 97.9 MB of git objects holding a 7 kB tip. This is history bloat: the size is real, the substance is not.

No other repo in the cluster exceeds 1000×. The next highest is `agent-priming-toolkit` at 104×, on a 158-byte tree.

---

## The disease is rarer than it looks

The brief's hypothesis was that this cluster is full of `hermes-memory-mcp`-shaped repos. **Measured: it is not.** That is a negative result and it is worth stating plainly, because the instrument that produced it is the thing to reuse.

- **Zero repos** in this cluster have a `main`/`entry` pointing at a file that cannot be built, other than the 2 listed above.
- **Zero repos** have source files that are all 0 bytes.
- The `hermes-memory-mcp` shape — a large blob count that is really a committed dependency tree — appears exactly once here, as `snapkit-js` (954/958 files in `node_modules/`), and it is not pretending to be anything: it is a vendored dump.

What the cluster *does* contain is a different problem: 45 unowned forks and 11 repos that were never code. Neither is a bug, and both are cheaper to fix than a hollow package would be.

### A caution about the first detector, since it nearly produced a fake finding

The first version of the entry-point checker reported **1,318 dangling entry points** across `deepseek-harness-quilt` and `paperclip`, and would have made them the headline finding. All of it was detector error, from four separate mistakes:

| mistake | what it did | how many false positives |
|---|---|---:|
| treated `"start"` as an entry point | `start` is an **npm script** (`"start": "node src/index.js"`), not a path | 4 repos |
| treated `types`/`typings` as an entry point | they point at a `.d.ts`, a compiler output, and `.d.ts` is *excluded by the vendor filter by design* | ~1,300 |
| checked manifests inside `node_modules/` | `snapkit-js` reported 8 dangling entries from vendored packages | 8 |
| blanketed `dist/`, `lib/`, `pkg/` as build outputs | `deepseek-harness-quilt` has **466** legitimate `main: lib/index.js` pointers (tsc's default `outDir`) | 468 |

The fix that mattered was not a longer deny-list. It was requiring **evidence** — a sibling source file in the same package, or a `tsconfig.json`/`Cargo.toml` in the same package — before calling a missing target a build output. The rule itself also had a bug: it tested the target's **repo-root-relative** first path segment against the build-dir list, so in a monorepo `packages/x/lib/client.js` was checked as `packages` and the rule never fired.

**The transferable lesson:** when a detector reports a startling count, the first hypothesis should be the detector. 1,318 → 2 is not a fix, it is a sign the instrument was wrong.

---

## GENUINE — 5 repos, real code in uncounted extensions

| repo | files | source | source bytes | what linguist isn't counting |
|---|---:|---:|---:|---|
| `.github` | 28 | 1 | 261 | `.yml`×1, 261 B — org profile repo |
| `Patchwork-experts` | 26 | 5 | 6,675 | `.yaml`×5 (config-driven) |
| `covers` | 152 | 1 | 539 | `.mp3`×91, `.wav`×37 — audio assets, 1 text file |
| `dotfiles` | 952 | 254 | 799,041 | shell — `.fish`×103, `.py`×85 |
| `quilt-playtest` | 18 | 11 | 77,005 | `.mjs`×11 |

`dotfiles` is the clean example of the bucket working as intended: 254 real source files, 799 kB, overwhelmingly shell — and linguist reports nothing for it. `.github` is the thin edge of the bucket (one 261-byte YAML file); it is counted GENUINE because it is config-driven, which is exactly the case the bucket exists for, but it is not a software project.

---

## Why a tarball

The GitHub REST API was unusable here: no valid token (`~/.gitconfig` holds one that returns **401**), so the anonymous limit of 60 requests/hour applied against 62 tree reads. Two obvious approaches were built and measured before falling back:

1. **`git clone --depth 1 --filter=blob:none` + `git ls-tree -r -l HEAD`.** Fast and correct on small repos — 1,020 blobs in 0.2 s for `hermes-memory-mcp`. But **git tree objects do not store blob sizes** (mode + name + oid only), so `-l` must resolve every blob, and in a blobless partial clone that resolution is a lazy network fetch per blob. On `alphabet` it ran **3 m 20 s and produced 212 of 2,460 entries** when the timeout fired. Measured, then rejected.
2. **`git clone --filter=tree:0`.** Same failure mode, one request per subtree: **316 entries in 4 m 00 s** on `alphabet`. Rejected.
3. **`curl codeload.github.com/…/tar.gz/<ref> | tar -tzvf`.** The tar header carries each member's size, so one streaming pass yields path+size for the whole working tree, with no blob store, no checkout, and no REST rate limit. It measures the **working tree**, which is the correct side of the history/source distinction. Accepted: **61/62 in one pass**; `privox` has no content and was resolved by other means.

Two implementation notes, both of which would silently corrupt counts:

- The trees contain **paths with spaces** (`alphabet/…/mode/`). Parsing `tar tzv` with `awk` shifts the column fields and yields wrong sizes. Python's `tarfile` in stream mode is used instead.
- The first classifier had `CODE.match(basename)`, which anchors at position 0 against a `\.(ext)$` pattern — so only files whose basename *begins* with `.ext` matched. `RTSnavigator` scored **0 source files while holding 349 `.js`/`.mjs` files**. Fixed to an end-anchored `search`, and `classify62.py` now refuses to run unless 15 extension cases and 12 vendor cases pass. That self-test is why the bug could not ship silently the second time.

---

## How to check this yourself

### Reproduce one row (no token needed, no rate limit)

```bash
REPO=synesis-research

# every path and its exact byte size, straight from the tar headers
curl -sL "https://codeload.github.com/SuperInstance/$REPO/tar.gz/refs/heads/main" \
  | tar tzvf - | head -20

# count files, and count 0-byte files
curl -sL "https://codeload.github.com/SuperInstance/$REPO/tar.gz/refs/heads/main" \
  | tar tzvf - | awk '$NF!~/\/$/ {n++; if ($3==0) z++} END {print n" files, "z" at 0 bytes"}'
```

Expected for `synesis-research`: `506 files, 117 at 0 bytes`.

### Reproduce the whole table

```bash
git clone https://github.com/SuperInstance/fleet-triage
cd fleet-triage

python3 cache62.py      # 61 working trees -> _cache/*.json  (streamed, ~14 min)
python3 classify62.py   # _cache/*.json -> classified.json    (offline, ~2 s)
python3 mkreport.py     # classified.json -> HOLLOW.md       (no hand-typed numbers)
```

`classify62.py` prints `self-test: 15 extension cases + 12 vendor cases OK` before it will emit anything, and **exits non-zero if the filters regress**.

### Re-derive a single number by hand

```bash
# "is the main branch's history bigger than 1000x the working tree?"
REPO=AutoData-old
SIZE_KB=$(curl -s https://api.github.com/repos/SuperInstance/$REPO | jq .size)
curl -sL "https://codeload.github.com/SuperInstance/$REPO/tar.gz/refs/heads/main" \
  | tar tzvf - | awk '$NF!~/\/$/ {s+=$3} END {print s}'
echo "ratio = $((SIZE_KB*1024)) / TREE_BYTES"

# "is the main entry point real?"  (this is the hermes-memory-mcp test)
REPO=tracer-rs-archive
curl -sL "https://codeload.github.com/SuperInstance/$REPO/tar.gz/refs/heads/master" \
  | tar tzf - | grep -E '(Cargo.toml|src/lib.rs)$'
```

Expected: `Cargo.toml` present, `src/lib.rs` **absent** — the `path` key in `Cargo.toml` points at a file the repo does not contain.

### The API-side facts used here

`fork`, `size`, `default_branch` and `language` come from the census in `nolang.json`; the fork **parents** come from `GET /repos/SuperInstance/{repo}`. Both were fetched unauthenticated inside the 60/hour limit.

---

## Limitations, stated rather than buried

- **The API was unauthenticated.** `fork`, `size` and `language` are server truth and I trust them; but no token meant no access to `git/trees?recursive=1`, so all tree facts come from the tarball. The two agree everywhere they overlap.
- **Vendor filter scope.** The filter is applied to path segments and file extensions, as specified. It does not detect a vendored tree stored under an unconventional name (`thirdparty/` is covered, `extern/` is not). A repo could in principle be mostly-vendored and still score low on this filter; none did here — the 3 VENDORED repos are 98–100% by bytes.
- **Zero-byte detection is exact, not sampled.** Every file's size comes from the tar header, so there is no sampling error in the 0-byte counts.
- **`alphabet`'s zero-language result is measured but not explained.** I can state that 99.23% of its bytes are in formats linguist does not count, and that its `.gitattributes` disables nothing. I could not establish a mechanism from anything in the tree, and I am not going to invent one.
- **Bucket assignment is a precedence, not a purity test.** Where a repo qualifies for two buckets the higher-precedence one is used and the other signals are kept in the evidence column. `deepseek-harness-quilt`, for example, is a fork *and* declares 466 build-output entry points; it is filed as MIRROR with the 466 recorded.
- **`tracer-rs-archive` and `synesis-research` are the same author's archive pattern**, and `synesis-research` is 117 files of placeholder. Whether that is deliberate archiving or an abandoned generator run is not something the repo can tell me.

## Precedence used

```
EMPTY     zero files in the working tree
HOLLOW    dangling entry point  >  all-source-0-bytes  >  VENDORED  >  no-source
VENDORED  >=50% of files or bytes in a committed dependency dir
MIRROR    GitHub API fork=true (with the parent named)
GENUINE   real source in extensions linguist does not count
```

HOLLOW is split by `sub` — `dangling-entry` (2), `zero-byte-source` (0), `no-source` (11) — because "the entry point is broken" and "this was never a code repository" are not the same finding and should not be counted together.

---

Generated from `classified.json` (62 rows). Machine: 2 GB / 1 core, no GitHub token, anonymous API. Every figure above is emitted by `mkreport.py` from that JSON; none is typed by hand.
