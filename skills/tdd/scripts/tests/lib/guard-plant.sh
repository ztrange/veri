#!/usr/bin/env bash
# Sourced by guard suites: the scratch tree a guard copy runs in, and its run over one document.
# Usage: source "$HERE/lib/guard-plant.sh" after setting $scratch, $ROOT, $GUARD, $GUARD_PATH,
#   $SKILL and, optionally, the array COMPANIONS (paths under $ROOT copied into the tree).
#   make_plant_tree <name>   sets $tree and $guard_copy; appends to $problems and returns 1 on failure
#   run_guard_over <doc>     sets $guard_code and $guard_out
#   failures_in <output>     prints the count line's failure count, or '<none>'
#   probe_guard_is_there     appends to $problems and returns 1 when $GUARD_PATH is missing or not executable
#   probe_guard_is_red <what>  appends to $problems unless the last run exited non-zero and counted a failure
#   probe_guard_is_green_unplanted  runs over $SKILL_PATH; appends to $problems unless it exited 0 and counted 0 failed

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

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing checks $SKILL")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it over $SKILL")
    return 1
  }
}

probe_guard_is_red() {
  local what="$1" failures
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 ]] ||
    problems+=("want ${GUARD##*/} to fail over a $SKILL whose $what; it exited 0 and said: ${guard_out//$'\n'/\/}")
  [[ "$failures" != 0 && "$failures" != '<none>' ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state a failure over that $SKILL; it stated '$failures': ${guard_out//$'\n'/\/}")
}

probe_guard_is_green_unplanted() {
  local failures
  run_guard_over "$SKILL_PATH"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over $SKILL as committed — red there says nothing about the plant; it exited $guard_code and said: ${guard_out//$'\n'/\/}")
  [[ "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state 0 failed over $SKILL as committed; it stated '$failures': ${guard_out//$'\n'/\/}")
}
