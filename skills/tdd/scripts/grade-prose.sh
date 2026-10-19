#!/usr/bin/env bash
# grade-prose.sh — grade one prose unit against its requirements list.
#
# Usage:   grade-prose.sh <requirements-file> <unit>
# Exit:    2 bad arguments, or a grader.conf model naming no version
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

if (( $# != 2 )); then
  echo "usage: grade-prose.sh <requirements-file> <unit>" >&2
  exit 2
fi
reqs="$1" unit="$2"

claims="$("$HERE/requirements.sh" claims "$reqs" "$unit")" || exit 2
file="$(dirname "$reqs")/${unit%%#*}"
if [[ "$unit" == *'#'* ]]; then
  text="$(awk -v want="${unit#*#}" '
    match($0, /^#+/) {
      level = RLENGTH; title = substr($0, level + 1); sub(/^[ \t]+/, "", title)
      if (on && level <= lvl) exit
      if (!on && title == want) { on = 1; lvl = level }
    }
    on' "$file")" || exit 2
else
  text="$(cat "$file")" || exit 2
fi

prompt="Grade the unit below against each requirement.

Requirements (ID<TAB>Requirement):
$claims

Unit text:
$text

Analyse freely first. Then end your reply with this block, one line per requirement in list order:
BEGIN GRADES
<ID>: PASS|FAIL — <reason>
VERDICT: PASS or VERDICT: REJECT
END GRADES
The VERDICT line goes inside the block, before END GRADES; write nothing after END GRADES."

model="$(awk '/^[[:space:]]*(#|$)/ { next } !found { v = $0; sub(/^[^=]*=/, "", v); gsub(/^[[:space:]"]+|[[:space:]"]+$/, "", v); found = 1 } END { print v }' "$HERE/../grader.conf")"
if [[ "$model" != *[0-9]* ]]; then
  echo "grade-prose.sh: grader.conf model '$model' names no version" >&2
  exit 2
fi

reply="$("$HERE/supervise.sh" grade-prose "${CLAUDE_BIN:-claude}" -p --model "$model" <<< "$prompt")" || exit $?
if ! grep -E '^BEGIN GRADES' <<< "$reply" > /dev/null; then
  echo "grade-prose.sh: reply has no BEGIN GRADES block" >&2
  exit 2
fi
if awk '/^END GRADES/ { after = 0; seen = 1; next } seen && /[^[:space:]]/ { after = 1 } END { exit !after }' <<< "$reply"; then
  echo "grade-prose.sh: text after END GRADES" >&2
  exit 2
fi
block="$(awk '/^BEGIN GRADES/ { buf = ""; on = 1; next } /^END GRADES/ { on = 0; next } on { buf = buf $0 "\n" } END { printf "%s", buf }' <<< "$reply")"
want_ids="$(cut -f1 <<< "$claims")"
got_ids="$(grep -E '^[^:]+: (PASS|FAIL)' <<< "$block" | grep -v '^VERDICT:' | cut -d: -f1)"
for id in $want_ids; do
  if ! grep -Fx -- "$id" <<< "$got_ids" > /dev/null; then
    echo "grade-prose.sh: GRADES block is missing $id" >&2
    exit 2
  fi
done
for id in $got_ids; do
  if ! grep -Fx -- "$id" <<< "$want_ids" > /dev/null; then
    echo "grade-prose.sh: GRADES block has extra $id" >&2
    exit 2
  fi
done
if [[ "$want_ids" != "$got_ids" ]]; then
  echo "grade-prose.sh: GRADES block IDs are out of order" >&2
  exit 2
fi
fails="$(awk '/^BEGIN GRADES/ { buf = ""; on = 1; next } /^END GRADES/ { on = 0; next } on { buf = buf $0 "\n" } END { printf "%s", buf }' <<< "$reply" | grep -E '^[^:]+: FAIL')"
if [[ -n "$fails" ]]; then
  echo "$fails"
  exit 1
fi
