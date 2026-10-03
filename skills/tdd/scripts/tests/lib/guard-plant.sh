#!/usr/bin/env bash
# Sourced by guard suites: the scratch tree a guard copy runs in, and its run over one document.
# Usage: source "$HERE/lib/guard-plant.sh" after setting $scratch, $ROOT, $GUARD, $GUARD_PATH,
#   $SKILL and, optionally, the array COMPANIONS (paths under $ROOT copied into the tree).
#   make_plant_tree <name>   sets $tree and $guard_copy; appends to $problems and returns 1 on failure
#   run_guard_over <doc>     sets $guard_code and $guard_out
#   failures_in <output>     prints the count line's failure count, or '<none>'

GUARD_PLANT_LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

failures_in() {
  local line
  line="$(grep -E '^[0-9]+ passed, [0-9]+ failed$' <<< "$1" | tail -1)"
  [[ -n "$line" ]] || { printf '%s' '<none>'; return; }
  line="${line#*, }"
  printf '%s' "${line% failed}"
}

make_plant_tree() {
  local companion
  tree="$scratch/$1"
  mkdir -p "$tree/${SKILL%/*}" "$tree/${GUARD%/*}" || {
    problems+=("could not make a scratch tree to plant the document in, so the criterion went unasked")
    return 1
  }
  guard_copy="$tree/$GUARD"
  cp "$GUARD_PATH" "$guard_copy"
  mkdir -p "${guard_copy%/*}/lib" && cp "$GUARD_PLANT_LIB/harness.sh" "${guard_copy%/*}/lib/"
  for companion in ${COMPANIONS[@]+"${COMPANIONS[@]}"}; do
    mkdir -p "$tree/${companion%/*}" && cp "$ROOT/$companion" "$tree/$companion"
  done
}

run_guard_over() {
  cp "$1" "$tree/$SKILL"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}
