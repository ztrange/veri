#!/usr/bin/env bash
# Unit tests for the four documentation targets in this repository's Makefile — what they do
# when the shell that invoked them is one of veri's own.
#
# Contract under test:
#   With VERI_TEST_CMD set to a development command (`make test`), each of `make docs`,
#   `make docs-test`, `make docs-check` and `make docs-fresh` exits 2, runs none of the
#   things it would otherwise run, and says on stderr why it refused.
#
#   With VERI_TEST_CMD unset, or set to a documentation target, those same four targets run
#   as they would without the guard.
#
# Run: skills/tdd/scripts/tests/docs-targets-refuse.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

WORK="$(scratch_dir)"

MAKEFILE="$ROOT/Makefile"
LOG="$WORK/ran.log"

GENERATED_DIR='docs'

TARGETS=(docs docs-test docs-check docs-fresh)

DEV_CMD='make test'

DOCS_CMD='make docs-test'

TRIPWIRE_VAR='VERI_TRIPWIRE_LOG'
GUARD_VAR='VERI_TEST_CMD'

flat() { printf '%s' "$1" | tr '\n' '/'; }

target_list() {
  local last=$(( ${#TARGETS[@]} - 1 )) joined
  joined="$(printf '%s, ' "${TARGETS[@]:0:$last}")"
  printf '%s and %s' "${joined%, }" "${TARGETS[$last]}"
}

python_tripwire() {
  cat > "$1" <<PY
import os
with open(os.environ["$TRIPWIRE_VAR"], "a") as log:
    log.write("$2\n")
PY
}

shell_tripwire() {
  cat > "$1" <<SH
#!/usr/bin/env bash
set -uo pipefail
printf '$2\n' >> "\$$TRIPWIRE_VAR"
echo "1 passed, 0 failed"
SH
  chmod +x "$1"
}

TREE=""

tree_with_tripwires() {
  TREE="$WORK/tree"
  mkdir -p "$TREE/$GENERATED_DIR/tests"
  cp "$MAKEFILE" "$TREE/Makefile"

  python_tripwire "$TREE/$GENERATED_DIR/build-walkthrough.py" "built the page"
  python_tripwire "$TREE/$GENERATED_DIR/check-walkthrough.py" "checked the page is fresh"
  shell_tripwire "$TREE/$GENERATED_DIR/tests/tripwire.test.sh" "ran a documentation suite"
}

run_code=0
run_out=""
run_err=""

run_target() {
  local target="$1" err="$WORK/err"
  shift
  : > "$LOG"
  run_out="$(env "$TRIPWIRE_VAR=$LOG" "$@" make -C "$TREE" "$target" 2>"$err")" &&
    run_code=0 || run_code=$?
  run_err="$(cat "$err")"
}

run_streams() { printf 'stdout: %s, stderr: %s' "$(flat "$run_out")" "$(flat "$run_err")"; }

probe_runner_is_this_repositorys() {
  cmp -s "$MAKEFILE" "$TREE/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says what its documentation targets do")
}

probe_tripwires_fire_when_the_variable_is_unset() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$target" env -u "$GUARD_VAR"
    [[ "$run_code" == 0 ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' over the scratch tree exited $run_code, so a refusal below is not distinguishable from a tree that cannot run: $(run_streams)")
    [[ -s "$LOG" ]] ||
      problems+=("the premise broke: with $GUARD_VAR unset, 'make $target' reached none of the stand-ins, so an empty log after a refusal says nothing")
  done
}

probe_targets_refuse() {
  local target
  for target in "${TARGETS[@]}"; do
    run_target "$target" env "$GUARD_VAR=$DEV_CMD"

    [[ "$run_code" == 2 ]] ||
      problems+=("want 'make $target' to exit 2 under $GUARD_VAR='$DEV_CMD'; got $run_code, $(run_streams)")
    [[ ! -s "$LOG" ]] ||
      problems+=("'make $target' ran something under $GUARD_VAR='$DEV_CMD' — a development run must not pay for a page build: $(flat "$(cat "$LOG")")")
    grep -q "$GUARD_VAR" <<<"$run_err" ||
      problems+=("nothing on stderr from 'make $target' named $GUARD_VAR, so its refusal does not say why: $(flat "$run_err")")
  done
}

name="with $GUARD_VAR='$DEV_CMD', make $(target_list) each exit 2 without running anything and say why on stderr"
problems=()

tree_with_tripwires
probe_runner_is_this_repositorys
probe_tripwires_fire_when_the_variable_is_unset
probe_targets_refuse

report "$name"

probe_targets_run() {
  local situation="$1" target
  shift
  for target in "${TARGETS[@]}"; do
    run_target "$target" "$@"

    [[ "$run_code" == 0 ]] ||
      problems+=("want 'make $target' to run as before with $situation; got exit $run_code, $(run_streams)")
    [[ -s "$LOG" ]] ||
      problems+=("'make $target' with $situation reached none of the stand-ins, so it did not run as before: the guard fired outside a development run")
  done
}

name="with $GUARD_VAR unset, or set to '$DOCS_CMD', make $(target_list) each run as before"
problems=()

tree_with_tripwires
probe_runner_is_this_repositorys
probe_targets_run "$GUARD_VAR unset" env -u "$GUARD_VAR"
probe_targets_run "$GUARD_VAR='$DOCS_CMD'" env "$GUARD_VAR=$DOCS_CMD"

report "$name"

finish
