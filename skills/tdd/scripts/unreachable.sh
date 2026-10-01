#!/usr/bin/env bash
# unreachable.sh — the scripts under skills/tdd/scripts/ that no declared entry point reaches.
# Entry points: SKILL.md, the Makefile, the git hooks under docs/hooks/.
#
# Usage:   unreachable.sh <repo-root>     # one unreachable script per line on stdout
#
# Exit:    0  the list was printed, possibly empty
#          2  no <repo-root>
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: unreachable.sh <repo-root>" >&2; exit 2; }
root="$1"
scripts="$root/skills/tdd/scripts"

names=()
for f in "$scripts"/*.sh; do
  names+=( "${f##*/}" )
done
nodes=( "${names[@]}" )
for f in "$scripts"/lib/*.sh; do
  if [[ -e "$f" ]]; then nodes+=( "lib/${f##*/}" ); fi
done
for f in "$root"/skills/tdd/*.md; do
  nodes+=( "${f##*/}" )
done

path_of() {
  case "$1" in
    *.md)  printf '%s\n' "$root/skills/tdd/$1" ;;
    *)     printf '%s\n' "$scripts/$1" ;;
  esac
}

mentions() {
  local file="$1" name
  for name in "${nodes[@]}"; do
    if grep -qE "(^|[^[:alnum:]_.-])${name//./\\.}(\$|[^[:alnum:]_-])" "$file"; then
      printf '%s\n' "$name"
    fi
  done
  local built pattern
  while IFS= read -r built; do
    pattern="$(printf '%s' "$built" | sed -E 's/\./\\./g; s/\$\{?[[:alnum:]_]+\}?/[[:alnum:]_-]+/g')"
    for name in "${nodes[@]}"; do
      if [[ "$name" =~ ^${pattern}$ ]]; then printf '%s\n' "$name"; fi
    done
  done < <(grep -oE '[[:alnum:]_.-]*(\$\{?[[:alnum:]_]+\}?[[:alnum:]_.-]*)+\.(sh|md)' "$file")
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

for entry in "$root/skills/tdd/SKILL.md" "$root/Makefile" "$root"/docs/hooks/*; do
  if [[ -f "$entry" ]]; then reach_from "$entry"; fi
done
while (( ${#queue[@]} > 0 )); do
  current="${queue[0]}"
  queue=( "${queue[@]:1}" )
  reach_from "$(path_of "$current")"
done

for name in "${names[@]}"; do
  [[ -n "${reached[$name]:-}" ]] || printf '%s\n' "$name"
done
