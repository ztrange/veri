#!/usr/bin/env bash
# refactor-overflow.sh — file the structural candidates a closing pass could not reach.
#
# Usage:
#   refactor-overflow.sh <n> <owed-file> <reached>
#
# Prints the new issue's URL.
#
# Exit: 0 filed; 2 a missing or non-numeric argument; 3 nothing left unreached, nothing filed.
set -euo pipefail

n="${1:-}" owed="${2:-}" reached="${3:-}"

if [[ ! "$n" =~ ^[0-9]+$ || -z "$owed" || ! "$reached" =~ ^[0-9]+$ ]]; then
  echo "refactor-overflow: usage: refactor-overflow.sh <n> <owed-file> <reached>" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"

unreached="$("$HERE/refactor-owed.sh" list "$owed" | tail -n "+$((reached + 1))")"
[[ -n "$unreached" ]] || exit 3

title="Refactor owed by #$n"
text="$(printf 'Structural candidates #%s'"'"'s closing pass could not reach:\n\n' "$n"
        sed 's/^/- /' <<<"$unreached")"
url="$(gh api "repos/{owner}/{repo}/issues" -f "title=$title" -f "body=$text" -q .html_url)"
echo "$url"
