#!/usr/bin/env bash
# structural-predicate.sh <record> — read a predicate leaf's report on stdin and write its
# `PREDICATE:` command to <record>.
#
# Exit codes: 0 the command was written; 2 bad arguments.
#
# Usage:   structural-predicate.sh .tdd/issue-<n>-predicate < <leaf-report>
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="usage: structural-predicate.sh <record>"
require_args 1 "$@"
record="$1"

predicate=""
while IFS= read -r line; do
  case "$line" in
    PREDICATE:*) predicate="${line#PREDICATE:}"; predicate="${predicate# }" ;;
  esac
done

printf '%s\n' "$predicate" > "$record"
