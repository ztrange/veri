#!/usr/bin/env bash
# grade-prose.sh — grade one prose unit against its requirements list.
#
# Usage:   grade-prose.sh <requirements-file> <unit>
# Exit:    2 bad arguments
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
$text"

"${CLAUDE_BIN:-claude}" -p <<< "$prompt"
