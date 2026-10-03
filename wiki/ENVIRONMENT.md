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

| have | do not have |
|---|---|
| `dotnet 9.0.316` | `mono`, `msbuild`, `csc` |
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

## The one that nearly destroyed the night's work

**`git add -A` and `rm -rf` both time out on NFS mid-operation and report
success.** A `git add` that "succeeded" committed one file against a message
claiming 441. A background `rm` reported `succeeded` with half the tree intact.

> **Count on disk, after the operation, every time.**
