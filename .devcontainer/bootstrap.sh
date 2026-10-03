#!/usr/bin/env bash
# Bring up the workspace agent. Idempotent: safe to re-run in a warm codespace.
set -uo pipefail
echo "== mavis-workspace bootstrap =="

# The quota trap: on some hosts any tool that writes to a default cache path
# inherits a full NAS. Redirect every one of them, or npm/Chromium crash on
# a disk quota error that looks like a network fault.
export npm_config_cache=/tmp/npmcache
export HOME=/tmp XDG_CACHE_HOME=/tmp XDG_CONFIG_HOME=/tmp XDG_DATA_HOME=/tmp TMPDIR=/tmp

git config --global user.name  "${AGENT_NAME:-mavis-workspace}"
git config --global user.email "${AGENT_EMAIL:-mavis-workspace@superinstance.dev}"

# The knowledge this agent runs on. Read RETRACTIONS.md before anything else.
if [ ! -d wiki ]; then
  git submodule update --init --recursive 2>/dev/null || true
fi

echo "-- orientation --"
echo "   wiki/RETRACTIONS.md   published-and-wrong claims. READ FIRST."
echo "   wiki/INDEX.md         what is known and where the full text lives"
echo "   wiki/ENVIRONMENT.md   the traps that cost the most time"
echo "   wiki/EXPERIMENTS.md   what was measured, and what is still only a claim"
echo
echo "== runnable probes (no network, <1s each) =="
if [ -d probe ]; then
  for p in probe/*.py; do
    [ -f "$p" ] || continue
    case "$p" in *__pycache__*) continue;; esac
    # A check on EXIT CODE is a green badge: a probe that prints nothing and a
    # probe that prints a correct answer look identical to `&& echo OK`.  This is
    # the defect L9 exists to catch in fleetlint, and it was in my own bootstrap
    # on the first playtest.  Assert on OUTPUT, and say how much of it.
    out=$(timeout 30 python3 "$p" 2>&1)
    rc=$?
    lines=$(printf '%s' "$out" | grep -cv '^[[:space:]]*$')
    if [ "$rc" -ne 0 ]; then
      printf '   %-22s FAIL(exit %s)\n' "$(basename "$p")" "$rc"
    elif [ "$lines" -lt 3 ]; then
      printf '   %-22s GREEN BADGE (exit 0, %s lines)\n' "$(basename "$p")" "$lines"
    else
      printf '   %-22s OK  (%s lines)\n' "$(basename "$p")" "$lines"
    fi
  done
fi
echo
echo "== emit a key form to hand to the next instance =="
echo "   python3 emit_key.py --task '...' --out keys/\$(date -u +%Y%m%dT%H%M%SZ).json"
echo
echo "== when you are done, do not delete anything =="
echo "   commit and push. A workspace that exists only locally is a workspace that"
echo "   is one /tmp wipe from gone, and that has happened repeatedly."
