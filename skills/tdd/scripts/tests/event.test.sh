#!/usr/bin/env bash
# Unit tests for scripts/event.sh — the one-line writer every conductor mark goes through.
#
# Contract under test:
#   event.sh <event> [key=value …]  → appends one line to `.tdd/events.jsonl`, relative to
#                                     the directory it is run in, and exits 0.
#   that line                       → parses as JSON, and carries `ts`, `issue`, `actor`,
#                                     `phase`, `step`, `event` and `attempt`, plus one key
#                                     per `key=value` argument given.
#   `ts`                            → seconds since the epoch.
#   the run context arrives in the environment as `VERI_ISSUE`, `VERI_ACTOR`, `VERI_PHASE`,
#   `VERI_STEP` and `VERI_ATTEMPT`.
#
# Run: scripts/tests/event.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EVENT="$HERE/../event.sh"

source "$HERE/lib/harness.sh"

want_parses() {
  python3 -c '
import sys, json
line = open(sys.argv[1]).read().splitlines()[0]
obj = json.loads(line)
if not isinstance(obj, dict):
    raise SystemExit("not a JSON object")
' "$1" 2>/dev/null && return 0
  problems+=("want the line to parse as a JSON object, got: $(printf '%q' "$(head -1 "$1")")")
  return 1
}

jget() {
  python3 -c '
import sys, json
obj = json.loads(open(sys.argv[1]).read().splitlines()[0])
key = sys.argv[2]
print(obj[key] if key in obj else "<<missing>>")
' "$1" "$2" 2>/dev/null
}

jevents() {
  python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        print("<<unparseable>>")
        continue
    print(obj.get("event", "<<missing>>") if isinstance(obj, dict) else "<<unparseable>>")
' "$1" 2>/dev/null
}

finish
