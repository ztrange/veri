#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a suite from waiting out push-branch.sh's default
# backoff on wall time — skills/tdd/scripts/tests/no-unbacked-pushes.test.sh.
#
# Contract under test:
#   Over a tests directory holding one suite that invokes push-branch.sh without
#   VERI_PUSH_BACKOFF in its environment and one that sets it on the same invocation,
#   no-unbacked-pushes.test.sh fails, names the first as `<suite>:<line>` at the offending
#   line, and says nothing about the second; its header says it dies under C7.
#
# Run: skills/tdd/scripts/tests/push-backoff-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-unbacked-pushes.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

TESTS_DIR='skills/tdd/scripts/tests'

OFFENDER='pushes-unbacked.test.sh'
INNOCENT='pushes-backed.test.sh'

MARK='the-push'


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

write_plant() {
  local path="$1" env="$2"
  {
    echo '#!/usr/bin/env bash'
    echo 'set -uo pipefail'
    echo 'HERE="$(cd "$(dirname "$0")" && pwd)"'
    echo 'PUSH="$HERE/../push-branch.sh"'
    echo "${env}\"\$PUSH\" >/dev/null 2>&1  # $MARK"
    echo 'echo "----"'
    echo 'echo "1 passed, 0 failed"'
  } > "$path"
  chmod 755 "$path"
}

plant() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to plant this case's suites in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR/lib"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"
  cp "$GUARD_PATH" "$guard_copy"
  cp "$HERE"/lib/*.sh "$tree/$TESTS_DIR/lib/"
  write_plant "$tree/$TESTS_DIR/$OFFENDER" ''
  write_plant "$tree/$TESTS_DIR/$INNOCENT" 'VERI_PUSH_BACKOFF=0 '
  offender_line="$(grep -n "$MARK" "$tree/$TESTS_DIR/$OFFENDER" | cut -d: -f1)"
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing outside hermetic-suites.test.sh checks that a suite invoking push-branch.sh sets VERI_PUSH_BACKOFF")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_header_names_c7() {
  local header
  header="$(awk 'NR > 1 && !/^#/ { exit } NR > 1 { print }' "$GUARD_PATH")"
  grep -F 'C7' <<< "$header" > /dev/null ||
    problems+=("$GUARD's header does not say it dies under C7; it reads: $(flat "$header")")
}

name="no-unbacked-pushes.test.sh names a suite that invokes push-branch.sh without VERI_PUSH_BACKOFF as <suite>:<line>, leaves one that sets it alone, and its header says it dies under C7"
problems=()

if probe_guard_is_there && plant; then
  probe_header_names_c7
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over $OFFENDER, which invokes push-branch.sh without VERI_PUSH_BACKOFF; it exited 0 and said: $(flat "$guard_out")")
  grep -F -- "$OFFENDER:$offender_line" <<< "$guard_out" > /dev/null ||
    problems+=("no line of the guard's output names $OFFENDER:$offender_line, where the unbacked push is; it said: $(flat "$guard_out")")
  ! grep -F -- "$INNOCENT" <<< "$guard_out" > /dev/null ||
    problems+=("the guard named $INNOCENT, which sets VERI_PUSH_BACKOFF on its push: $(flat "$guard_out")")
fi

report "$name"

finish
