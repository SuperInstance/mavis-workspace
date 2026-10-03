#!/usr/bin/env python3
"""emit_key.py — produce a key form for another instance.

    python3 emit_key.py --task "..." --out keys/<name>.yaml

The point is that it CANNOT write a count it has not measured: every numeric
field is either passed in explicitly or left as null, and null is visibly
different from a number. This is the L9/L10 lesson from fleetlint applied to
the most failure-prone output format there is -- prose about yourself.
"""
import argparse, subprocess, sys, datetime, os, json, re

def safe_url(u):
    """Strip any inline credential before it reaches a committed artifact.

    PLAYTEST CAUGHT THIS.  On a devbox the remote is
    https://<TOKEN>@github.com/... and `git config remote.origin.url` copies that
    whole string into the key form, which is then committed to a PUBLIC repo.
    GitHub push protection caught it.  A tool that gathers context must never
    be the thing that leaks the credential it gathered while doing it.
    """
    return re.sub(r"://[^/@]+@", "://***@", u or "")


def sh(c, default=None):
    try: return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception: return default

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--measured", help="the most recent number you RAN, with its command")
    ap.add_argument("--refuted", action="append", default=[], help="'what it says | what is true'")
    ap.add_argument("--owed", action="append", default=[])
    ap.add_argument("--blocked", action="append", default=[])
    ap.add_argument("--failure", action="append", default=[])
    ap.add_argument("--instance", default=os.environ.get("AGENT_NAME", "mavis-workspace"))
    ap.add_argument("--out")
    a = ap.parse_args()

    repo = safe_url(sh("git config --get remote.origin.url")) or None
    head = sh("git rev-parse --short HEAD") or None
    d = {"key_form_version": 1, "instance": a.instance,
         "born": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
         "repo": repo, "head": head,
         "task": a.task,
         "last_measured": a.measured,          # null if not passed -- and null is visible
         "its_provenance": None,               # must be filled by hand if measured is set
         "beliefs": [], "refuted": a.refuted, "owed": a.owed,
         "blocked_on": a.blocked, "known_failures": a.failure,
         "env_delta": {"have": [], "lack": [], "traps": []},
         "next_question": None}
    # JSON, not YAML: a key form that needs a package to read is a key form that
    # will not transfer to whatever instance receives it. JSON is universally
    # parseable and the null-vs-number distinction is unmissable.
    warn = []
    if a.measured:
        warn.append("last_measured is set but its_provenance is null -- FILL IT IN BY HAND")
    else:
        warn.append("last_measured is null. That is honest. Leave it null rather than invent one.")
    if not a.refuted:
        warn.append("refuted is EMPTY. If nothing is refuted, say so deliberately -- an "
                    "unstated empty list reads as 'nothing was corrected', which is false here.")
    # WARNINGS GO INSIDE THE JSON.  The first version appended them as trailing
    # `// WARN:` lines, which made the file unparseable by json.load -- so the
    # receiving agent got an exception instead of the context it came for.
    # Found by the cold playtest, not by reading the code.
    d["_warnings"] = warn
    body = json.dumps(d, indent=2)
    if a.out:
        open(a.out, "w").write(body)
        print(f"  wrote {a.out}  ({len(body)} b)")
        for w in warn: print(f"  ! {w}")
    else:
        print(body)
if __name__ == "__main__":
    main()
