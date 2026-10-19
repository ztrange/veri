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
text="$(cat "$(dirname "$reqs")/$unit")" || exit 2

prompt="Grade the unit below against each requirement.

Requirements (ID<TAB>Requirement):
$claims

Unit text:
$text"

"${CLAUDE_BIN:-claude}" -p <<< "$prompt"
