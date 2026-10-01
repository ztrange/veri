#!/usr/bin/env bash
# refactor-overflow.sh — file the structural candidates a closing pass could not reach.
#
# Usage:
#   refactor-overflow.sh <n> <owed-file> <reached>
#
# Prints the new issue's URL. Exit: 0 on success.
set -euo pipefail

n="$1" owed="$2" reached="$3"

HERE="$(cd "$(dirname "$0")" && pwd)"

unreached="$("$HERE/refactor-owed.sh" list "$owed" | tail -n "+$((reached + 1))")"

title="Refactor owed by #$n"
text="$(printf 'Structural candidates #%s'"'"'s closing pass could not reach:\n\n' "$n"
        sed 's/^/- /' <<<"$unreached")"
url="$(gh api "repos/{owner}/{repo}/issues" -f "title=$title" -f "body=$text" -q .html_url)"
echo "$url"
