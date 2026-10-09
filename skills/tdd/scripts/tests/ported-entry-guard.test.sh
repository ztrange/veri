#!/usr/bin/env bash
# Unit tests for the guard suite that keeps every shimmed module's __main__ block on the shared
# entry point — skills/tdd/scripts/tests/ported-entry-point.test.sh.
#
# Contract under test:
#   Over a tree holding a shim that execs python3 on veri/<module>.py and that module ending in
#   a bare `sys.exit(main(sys.argv[1:]))`, the guard fails and names the module as
#   `<module>:<line>` at its `if __name__ == "__main__":` line; it says nothing about a shimmed
#   module whose __main__ block calls entry.run; and once the offender is removed from the same
#   tree it passes.
#
# Run: skills/tdd/scripts/tests/ported-entry-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/ported-entry-point.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

SCRIPTS_DIR='skills/tdd/scripts'
TESTS_DIR='skills/tdd/scripts/tests'

OFFENDER_SHIM_REL="$SCRIPTS_DIR/probe-bare.sh"
OFFENDER_REL="$SCRIPTS_DIR/veri/probe_bare.py"
COMPLIANT_SHIM_REL="$SCRIPTS_DIR/probe-entry.sh"
COMPLIANT_REL="$SCRIPTS_DIR/veri/probe_entry.py"
OFFENDER_NAME="$(basename "$OFFENDER_REL")"
COMPLIANT_NAME="$(basename "$COMPLIANT_REL")"

source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

write_shim() {
  local path="$1" module="$2"
  {
    echo '#!/bin/sh'
    echo "exec python3 \"\$(dirname \"\$0\")/veri/$module\" \"\$@\""
  } > "$path"
  chmod 755 "$path"
}

write_module() {
  local path="$1" tail="$2"
  {
    echo 'import sys'
    echo ''
    echo ''
    echo 'def main(argv):'
    echo '    return 0'
    echo ''
    echo ''
    echo 'if __name__ == "__main__":'
    printf '%s\n' "$tail"
  } > "$path"
}

plant() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to plant this case's files in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR/lib" "$tree/$SCRIPTS_DIR/veri"

  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

  write_shim "$tree/$OFFENDER_SHIM_REL" "$OFFENDER_NAME"
  write_module "$tree/$OFFENDER_REL" '    sys.exit(main(sys.argv[1:]))'
  write_shim "$tree/$COMPLIANT_SHIM_REL" "$COMPLIANT_NAME"
  write_module "$tree/$COMPLIANT_REL" "$(printf '    import entry\n    entry.run(main, sys.argv[1:])')"
  cp "$ROOT/$SCRIPTS_DIR/veri/entry.py" "$tree/$SCRIPTS_DIR/veri/"
  : > "$tree/$SCRIPTS_DIR/veri/__init__.py"

  cp "$GUARD_PATH" "$guard_copy" && chmod 755 "$guard_copy"
  cp "$HERE/lib/harness.sh" "$tree/$TESTS_DIR/lib/"

  main_line="$(grep -n '^if __name__ == "__main__":$' "$tree/$OFFENDER_REL" | cut -d: -f1)"
  return 0
}

drop_tree() {
  [[ -z "${tree:-}" ]] || rm -rf "$tree"
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing stops a shimmed module's __main__ block from bypassing the shared entry point again")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_plant_is_what_it_claims() {
  [[ "$main_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted $OFFENDER_REL has no single __main__ line to name ('$main_line'), so the criterion cannot be asked")
    return 1
  }
}

run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

naming() { grep -F "$1" <<< "$guard_out"; }

names_none() {
  local named
  named="$(naming "$1")"
  [[ -z "$named" ]] || problems+=("$2: $(flat "$named")")
}

probe_guard_names_the_bare_module() {
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over $OFFENDER_REL, named by $OFFENDER_SHIM_REL's exec line and ending in a bare sys.exit(main(...)); it exited 0 and said: $(flat "$guard_out")")
  [[ -n "$(naming "$OFFENDER_NAME:$main_line")" ]] ||
    problems+=("no line of the guard's output names $OFFENDER_NAME:$main_line, where its __main__ block bypasses the shared entry point; it said: $(flat "$guard_out")")
}

probe_guard_leaves_the_compliant_alone() {
  names_none "$COMPLIANT_NAME" "the guard named $COMPLIANT_REL, whose __main__ block calls entry.run"
}

remove_plant() {
  rm -f "$tree/$OFFENDER_SHIM_REL" "$tree/$OFFENDER_REL"
}

probe_guard_is_green_once_the_plant_is_removed() {
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the same tree once $OFFENDER_REL and its shim are removed; it exited $guard_code and said: $(flat "$guard_out")")
  names_none "$OFFENDER_NAME" "the guard still named $OFFENDER_NAME, whose file is no longer in the tree"
}

name="#1150: ported-entry-point.test.sh names a shimmed module whose __main__ block is a bare sys.exit(main(...)) as <module>:<line>, leaves one that calls entry.run alone, and goes green once the planted offender is removed"
problems=()

if probe_guard_is_there && plant; then
  if probe_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_bare_module
    probe_guard_leaves_the_compliant_alone
    remove_plant
    run_guard
    probe_guard_is_green_once_the_plant_is_removed
  fi
fi
drop_tree

report "$name"

finish
