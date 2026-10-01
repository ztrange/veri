#!/usr/bin/env bash
# unreachable.sh — the scripts under skills/tdd/scripts/ that no declared entry point reaches.
# Entry points: SKILL.md, the Makefile, the git hooks under docs/hooks/.
#
# Usage:   unreachable.sh <repo-root>     # one unreachable script per line on stdout;
#                                         # one reached only from tests/ as `test-only: <name>`;
#                                         # a VERI_* knob or script SKILL.md or CLAUDE.md
#                                         # promises and nothing reads as `promised-unread: <name>`
#
# Exit:    0  the list was printed, possibly empty
#          2  no <repo-root>
set -euo pipefail

[[ -n "${1:-}" ]] || { echo "usage: unreachable.sh <repo-root>" >&2; exit 2; }
root="$1"
scripts="$root/skills/tdd/scripts"

names=() libs=() docs=()
shopt -s nullglob
for f in "$scripts"/*.sh "$scripts"/lib/*.sh "$root"/skills/tdd/*.md; do
  case "$f" in
    "$scripts"/lib/*) libs+=( "lib/${f##*/}" ) ;;
    *.md)             docs+=( "${f##*/}" ) ;;
    *)                names+=( "${f##*/}" ) ;;
  esac
done
shopt -u nullglob
nodes=( "${names[@]}" "${libs[@]}" "${docs[@]}" )

path_of() {
  case "$1" in
    *.md)  printf '%s\n' "$root/skills/tdd/$1" ;;
    *)     printf '%s\n' "$scripts/$1" ;;
  esac
}

escape_dots() {
  printf -v escaped '%s' "${1//./\\.}"
}

whole_name() {
  local escaped
  escape_dots "$1"
  printf -v whole '%s' "(^|[^[:alnum:]_.-])${escaped}(\$|[^[:alnum:]_-])"
}

mentions() {
  local file="$1" name whole built escaped pattern patterns=()
  while IFS= read -r built; do
    escape_dots "$built"
    patterns+=( "$(printf '%s' "$escaped" | sed -E 's/\$\{?[[:alnum:]_]+\}?/[[:alnum:]_-]+/g')" )
  done < <(grep -oE '[[:alnum:]_.-]*(\$\{?[[:alnum:]_]+\}?[[:alnum:]_.-]*)+\.(sh|md)' "$file")
  for name in "${nodes[@]}"; do
    whole_name "$name"
    if grep -qE "$whole" "$file"; then printf '%s\n' "$name"; continue; fi
    for pattern in "${patterns[@]}"; do
      if [[ "$name" =~ ^${pattern}$ ]]; then printf '%s\n' "$name"; break; fi
    done
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

for entry in "$root/skills/tdd/SKILL.md" "$root/Makefile" "$root"/docs/hooks/*; do
  if [[ -f "$entry" ]]; then reach_from "$entry"; fi
done
while (( ${#queue[@]} > 0 )); do
  current="${queue[0]}"
  queue=( "${queue[@]:1}" )
  reach_from "$(path_of "$current")"
done

for name in "${names[@]}"; do
  [[ -n "${reached[$name]:-}" ]] && continue
  whole_name "$name"
  if [[ -d "$scripts/tests" ]] && grep -rqE "$whole" "$scripts/tests"; then
    printf 'test-only: %s\n' "$name"
  else
    printf '%s\n' "$name"
  fi
done

promises=()
for doc in "$root/skills/tdd/SKILL.md" "$root/CLAUDE.md"; do
  if [[ -f "$doc" ]]; then promises+=( "$doc" ); fi
done
if (( ${#promises[@]} > 0 )); then
  readers=( "${names[@]/#/$scripts/}" "${libs[@]/#/$scripts/}" )
  while IFS= read -r knob; do
    if ! grep -qwF "$knob" "${readers[@]}"; then printf 'promised-unread: %s\n' "$knob"; fi
  done < <(grep -ohE 'VERI_[A-Z0-9_]+' "${promises[@]}" | sort -u)
  while IFS= read -r name; do
    if [[ ! -e "$scripts/$name" ]]; then printf 'promised-unread: %s\n' "$name"; fi
  done < <(grep -ohE '(^|[^[:alnum:]_.${}-])[[:alnum:]_-]+\.sh' "${promises[@]}" | sed -E 's/^[^[:alnum:]_-]//' | sort -u)
fi
