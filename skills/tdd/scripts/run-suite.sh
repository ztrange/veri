#!/usr/bin/env bash
# run-suite.sh — run ONE suite and hold it to the same count-line contract the `test` recipe
# holds every suite to.
#
# Usage:   run-suite.sh <suite>
#
# Until this script existed, that contract lived in the Makefile and nowhere else, so it
# reached only the suites `make test`'s glob — or a `TESTS=` override — handed it. A leaf
# running one suite by itself (`bash skills/tdd/scripts/tests/<suite>.test.sh`) got no check
# at all: not the exit code, which lies — under `set -u`, which every suite
# here declares, an unbound name inside a numeric comparison kills the script, and a script
# killed that way exits with the status of the command before it, routinely 0 — and not the
# count line, which nothing read. The leaf that once ran a suite that way was the blind
# verifier, the one component whose whole purpose is to establish ground truth independently.
#
# So: a suite whose last line is not `<n> passed, <m> failed` is refused here, named, however
# it exited. The refusal is exit 1 rather than 2, matching the answer the same shape gets
# through `make test`: the suite ran, and what came back about the tree under it is that it is
# not green. What a caller must never be handed is 0.
set -uo pipefail

HERE="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="usage: run-suite.sh <suite>"
require_args 1 "$@"
suite="$1"

n="${GIT_CONFIG_COUNT:-0}"
export "GIT_CONFIG_KEY_$n=maintenance.auto" "GIT_CONFIG_VALUE_$n=false" GIT_CONFIG_COUNT=$((n + 1))

case "$suite" in
  */tests/py/test_*.py)
    source "$HERE/lib/venv-python.sh"
    py_bin="$(venv_python)"
    "$py_bin" -m pytest --version > /dev/null 2>&1 || {
      echo "run-suite.sh: pytest cannot be imported by $py_bin; run make install-dev" >&2
      exit 2
    }
    "$py_bin" -m pytest "$suite" < /dev/null
    exit "$(to_contract $?)"
    ;;
esac

guard="$HERE/lib/count-line-guard.sh"
[[ -f "$guard" ]] && source "$guard"
[[ -n "${COUNT_LINE:-}" && -n "${COUNTLESS:-}" ]] || {
  echo "run-suite.sh: could not read the count-line guard from $guard" >&2
  exit 2
}

out="$(mktemp)"
at_exit 'rm -f "$out"'
trap 'exit 143' TERM

# hazard: the pipeline's status is tee's; the suite's comes off PIPESTATUS.
"$suite" < /dev/null | tee "$out"
code=${PIPESTATUS[0]}

last_line="$(tail -n 1 "$out")"
grep -Eq "$COUNT_LINE" <<< "$last_line" || {
  name="$(basename "$suite")"
  printf "$COUNTLESS" "$name"
  if grep '[^[:space:]]' "$out" > /dev/null; then printf '%s: its last line was: %s\n' "$name" "$last_line"
  else printf '%s: its output was empty\n' "$name"; fi
  exit 1
}

# pass-through: the caller reads the suite's own status once its count line is there.
exit "$code"
