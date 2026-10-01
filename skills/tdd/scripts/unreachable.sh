#!/usr/bin/env bash
# unreachable.sh — the scripts under skills/tdd/scripts/ that no declared entry point reaches.
# Entry point: SKILL.md.
#
# Usage:   unreachable.sh <repo-root>     # one unreachable script per line on stdout
#
# Exit:    0  the list was printed, possibly empty
set -euo pipefail

root="$1"
scripts="$root/skills/tdd/scripts"

names=()
for f in "$scripts"/*.sh; do
  names+=( "${f##*/}" )
done

mentions() {
  local file="$1" name
  for name in "${names[@]}"; do
    if grep -qE "(^|[^[:alnum:]_.-])${name//./\\.}(\$|[^[:alnum:]_-])" "$file"; then
      printf '%s\n' "$name"
    fi
  done
}

declare -A reached=()
queue=()
reach_from() {
  local name
  while IFS= read -r name; do
    [[ -n "${reached[$name]:-}" ]] && continue
    reached[$name]=1
    queue+=( "$name" )
  done < <(mentions "$1")
}

reach_from "$root/skills/tdd/SKILL.md"
while (( ${#queue[@]} > 0 )); do
  current="${queue[0]}"
  queue=( "${queue[@]:1}" )
  reach_from "$scripts/$current"
done

for name in "${names[@]}"; do
  [[ -n "${reached[$name]:-}" ]] || printf '%s\n' "$name"
done
