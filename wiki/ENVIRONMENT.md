# The environment, and the traps that cost the most time

Verified 2026-10-02. **Every item here was found the expensive way.**

## The workspace lies about being writable

`/workspace` is NFS. It has been **100% full (`EDQUOT`, -122)** for long
stretches, and in that state:

> **A shell redirect "succeeds" with exit 0 and produces a 0-byte file.**

- Always `stat -c %s` after writing there. **Never trust the exit code.**
- `mkdir` succeeds (metadata only), which makes it look writable.
- All write patterns fail identically at close: redirect, `dd`, agent `write`,
  `tar | tar`.
- The agent `write` tool **rejects `/tmp`**, so use a bash heredoc.
- **Staging in `/tmp` is fast but `/tmp` gets wiped mid-operation** — I lost
  three clones in one session. Staging is for speed, **the remote is the record.**

## Build tooling inherits the quota even when the project does not

`npm install` died with `Error: Unknown system error -122` while `/tmp` had 28G
free, because `npm config get cache` → `/workspace/.home/.npm`.

> **On this box, any tool writing to a default cache/home path silently inherits
> the NAS quota. `df -h` on the working directory proves nothing.**

```bash
export npm_config_cache=/tmp/npmcache
# headless Chromium needs ALL of these or it crashpads on the quota:
HOME=/tmp XDG_CACHE_HOME=/tmp XDG_CONFIG_HOME=/tmp XDG_DATA_HOME=/tmp TMPDIR=/tmp
```

## What is present, and what is not

> **Verified 2026-10-02. Re-verify before trusting this table** — it was wrong
> within hours, and an index that lists strengths *and* weaknesses is still wrong
> if the weakness list is stale.

| have | do not have |
|---|---|
| `dotnet 9.0.316` | `mono`, `msbuild`, `csc` |
| **`gcc` / `cc` 12.2.0** | `clang`, `tcc` |
| `python3`, `git`, `curl` | `cargo` / `rustc` — Rust findings are artifact-verified, not execution-verified |
| `GITHUB_TOKEN`, `TYPESAFEAI_KEY` | a working GPU (`requestAdapter()` → null) |
| network | `mcode-tools` (`invalid signature`), ElevenLabs (zero credits) |

## API traps

- **GitHub API `size` is wrong in BOTH directions** — 4× under-report and 2000×
  over-report. Rank on `git/trees?recursive=1` tree bytes, vendor-filtered.
- **`sort=full_name&direction=asc` is NOT monotonic.** Assert
  `unique_by(.full_name) == rows_returned`, not order.
- **`raw.githubusercontent.com` lags a successful push.** Verify with `ls-remote`
  or the git-tree API.
- A 503 or TLS EOF from TypeSafe is **transport failure, not schema evidence.**
- **Push support can hard-block on secrets.** Describe token shapes; don't paste.

## The one I got wrong, and the reason this warning is at the top

**I wrote "no C toolchain" into this file without checking, and `gcc 12.2.0` was
in the sandbox the whole time.** It built the connect4 solver, passed its
selftest, and walked 6,711,208 states proving its TT key injective with 0
collisions — all of it blocked behind a note I wrote from memory instead of from
`command -v`.

The deeper version of the same error is the rule I put in the README and then
broke:

> **Never write a count into a narrative before counting it.**

A capability list is a narrative about the environment. It needs the same
discipline as a number: **run the command, then write the line.**

## The one that nearly destroyed the night's work

**`git add -A` and `rm -rf` both time out on NFS mid-operation and report
success.** A `git add` that "succeeded" committed one file against a message
claiming 441. A background `rm` reported `succeeded` with half the tree intact.

> **Count on disk, after the operation, every time.**
