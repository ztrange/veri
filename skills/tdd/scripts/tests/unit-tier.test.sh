#!/usr/bin/env bash
# Unit tests for the `unit` target in this repository's Makefile — the fast tier. Like
# make-test-env.test.sh and count-line-guard.test.sh this suite has no script as its
# subject: its subject is which suites a make target runs. Zero-dependency plain-shell
# asserts, same idiom as the rest of this directory.
#
# Why this exists (issue #336): every suite here ran in one tier, so a one-line change to a
# script paid the whole `make test` for a check that only needed the suites asserting pure
# logic. `make unit` is the faster loop, and it is only faster if it runs the suites under
# skills/tdd/scripts/tests/unit/ and nothing from the flat directory beside it.
#
# Contract under test:
#   1. `make -n unit` names only suites matching skills/tdd/scripts/tests/unit/*.test.sh —
#      and every one of them on disk, so an empty roster over a populated directory is a
#      failure rather than a vacuous pass.
#   2. `make -n test` names the suites of both directories — the flat one and unit/ — and
#      none of them twice, so the full tier still covers what the fast tier runs.
#   3. `make unit` guards a suite the way `make test` does: a suite that never prints its
#      `<n> passed, <m> failed` count line fails the run, named, and so does one that calls gh,
#      caught by the OFFLINE_BIN shim's reach log and named with what it tried.
#
# The roster is read off `make -n`, which expands the target's list and runs nothing, the
# same idiom as no-docs-reads.test.sh's roster helper: running `make unit` to find out
# what it runs would cost the run it is asking about.
#
# Run: skills/tdd/scripts/tests/unit-tier.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

UNIT_DIR='skills/tdd/scripts/tests/unit'

pass=0 fail=0

source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

roster() {
  local recipe code
  recipe="$(make --no-print-directory -n -C "$1" "$2" 2>&1)" && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    echo "make -n $2 exited $code: $(flat "$recipe")"
    return 1
  fi
  printf '%s\n' "$recipe" | grep -o '[^ ]*\.test\.sh' || :
}

run_make() {
  out="$(make --no-print-directory -C "$ROOT" "$@" 2>&1 < /dev/null)" && code=0 || code=$?
}

name="make -n unit lists only suites matching $UNIT_DIR/*.test.sh"
problems=()

if ! listed="$(roster "$ROOT" unit)"; then
  problems+=("$listed")
else
  listed="$(sort -u <<< "$listed")"
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    [[ "$rel" =~ ^$UNIT_DIR/[^/]+\.test\.sh$ ]] ||
      problems+=("make -n unit names $rel, which is not under $UNIT_DIR/")
  done <<< "$listed"
  for f in "$ROOT/$UNIT_DIR"/*.test.sh; do
    [[ -e "$f" ]] || continue
    rel="$UNIT_DIR/$(basename "$f")"
    grep -qxF "$rel" <<< "$listed" ||
      problems+=("make -n unit does not name $rel, which is on disk under $UNIT_DIR/")
  done
fi

report "$name"

name="make -n test lists suites from both skills/tdd/scripts/tests/*.test.sh and $UNIT_DIR/*.test.sh, none twice"
problems=()

scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
mkdir -p "$scratch/$UNIT_DIR"
cp "$ROOT/Makefile" "$scratch/Makefile"
flat_suite='skills/tdd/scripts/tests/fixture-flat.test.sh'
unit_suite="$UNIT_DIR/fixture-unit.test.sh"
: > "$scratch/$flat_suite"
: > "$scratch/$unit_suite"

if ! listed="$(roster "$scratch" test)"; then
  problems+=("$listed")
else
  for rel in "$flat_suite" "$unit_suite"; do
    n="$(grep -cxF "$rel" <<< "$listed")"
    [[ "$n" -eq 1 ]] || problems+=("make -n test names $rel $n times, not once")
  done
fi

report "$name"

name="make unit applies make test's count-line check and OFFLINE_BIN reach-log guard"
problems=()

cat > "$scratch/no-count-line.test.sh" <<'SUITE'
#!/usr/bin/env bash
echo "a suite that stopped asserting"
exit 0
SUITE
cat > "$scratch/reaches-gh.test.sh" <<'SUITE'
#!/usr/bin/env bash
gh api --hostname example.invalid veri-unit-gh-probe >/dev/null 2>&1
echo "1 passed, 0 failed"
exit 0
SUITE
chmod +x "$scratch/no-count-line.test.sh" "$scratch/reaches-gh.test.sh"

run_make unit UNIT_TESTS="$scratch/no-count-line.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that never reached its count line; it exited 0 and said: $(flat "$out")")
grep -qF 'never reached its count line' < <(grep -F 'no-count-line.test.sh' <<< "$out") ||
  problems+=("no line of 'make unit' names no-count-line.test.sh and says it never reached its count line: $(flat "$out")")

run_make unit UNIT_TESTS="$scratch/reaches-gh.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran gh; it exited 0 and said: $(flat "$out")")
grep -qF 'veri-unit-gh-probe' < <(grep -F 'reaches-gh.test.sh: tried the network:' <<< "$out") ||
  problems+=("no 'tried the network' line of 'make unit' names reaches-gh.test.sh with the gh call carrying veri-unit-gh-probe: $(flat "$out")")

report "$name"

name="make unit runs each suite with LC_ALL=C and stdin from /dev/null, as make test does"
problems=()

probe="$scratch/env-probe"
cat > "$scratch/reports-env.test.sh" <<'SUITE'
#!/usr/bin/env bash
if [[ /dev/stdin -ef /dev/null ]]; then stdin=devnull; else stdin=inherited; fi
printf 'LC_ALL=%s\nstdin=%s\n' "${LC_ALL-<unset>}" "$stdin" > "$PROBE_OUT"
echo "1 passed, 0 failed"
SUITE
chmod +x "$scratch/reports-env.test.sh"

fifo="$scratch/stdin"
if mkfifo "$fifo" && exec 3<>"$fifo"; then
  out="$(env LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 PROBE_OUT="$probe" \
    make --no-print-directory -C "$ROOT" unit UNIT_TESTS="$scratch/reports-env.test.sh" 2>&1 < "$fifo")" &&
    code=0 || code=$?
  exec 3>&-
  [[ "$code" == 0 ]] ||
    problems+=("make unit over the fixture exited $code: $(flat "$out")")
  saw_locale="$(sed -n 's/^LC_ALL=//p' "$probe" 2>/dev/null)"
  saw_stdin="$(sed -n 's/^stdin=//p' "$probe" 2>/dev/null)"
  [[ "$saw_locale" == C ]] ||
    problems+=("a suite under make unit saw LC_ALL=${saw_locale:-<nothing>}, want C")
  [[ "$saw_stdin" == devnull ]] ||
    problems+=("a suite under make unit saw stdin=${saw_stdin:-<nothing>}, want devnull")
else
  problems+=("could not hold a FIFO open to hand make as stdin, so the case went unasked")
fi

report "$name"

name="make unit shims git, gh, curl and python3 to fail naming themselves; make test does not"
problems=()

cat > "$scratch/calls-real-vcs.test.sh" <<'SUITE'
#!/usr/bin/env bash
if git --version > /dev/null; then echo "1 passed, 0 failed"; exit 0; fi
echo "FAIL - the version probe"
echo "0 passed, 1 failed"
exit 1
SUITE
cat > "$scratch/mocks-vcs.test.sh" <<'SUITE'
#!/usr/bin/env bash
git() { echo "mocked"; }
if [[ "$(git --version)" == mocked ]]; then echo "1 passed, 0 failed"; exit 0; fi
echo "FAIL - the mocked probe"
echo "0 passed, 1 failed"
exit 1
SUITE
chmod +x "$scratch/calls-real-vcs.test.sh" "$scratch/mocks-vcs.test.sh"

run_make unit UNIT_TESTS="$scratch/calls-real-vcs.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran real git; it exited 0 and said: $(flat "$out")")
grep -qw git < <(grep -v '^== ' <<< "$out") ||
  problems+=("no line of 'make unit' over a suite that ran real git names git: $(flat "$out")")

run_make test TESTS="$scratch/calls-real-vcs.test.sh" UNIT_TESTS=
[[ "$code" == 0 ]] ||
  problems+=("want 'make test' to pass a suite that ran real git; it exited $code and said: $(flat "$out")")

run_make unit UNIT_TESTS="$scratch/mocks-vcs.test.sh"
[[ "$code" == 0 ]] ||
  problems+=("want 'make unit' to pass a suite that mocks git as a shell function; it exited $code and said: $(flat "$out")")

report "$name"

name="at least five existing suites move into $UNIT_DIR/, each passing and recording its git/python3/server/sleep count in its header"
problems=()

USAGE_COUNTS='(^|[^a-z0-9])git [0-9]+, python3 [0-9]+, server [0-9]+, sleep [0-9]+'

moved=0
for f in "$ROOT/$UNIT_DIR"/*.test.sh; do
  [[ -e "$f" ]] || continue
  base="$(basename "$f")"
  moved=$((moved + 1))
  [[ -e "$HERE/$base" ]] && cmp -s "$f" "$HERE/$base" &&
    problems+=("$base is under $UNIT_DIR/ and still in skills/tdd/scripts/tests/ too")
  header="$(sed -n '2,$p' "$f" | sed '/^#/!q' | grep '^#')"
  grep -Eq "$USAGE_COUNTS" <<< "$header" ||
    problems+=("$base's header comment has no 'git <n>, python3 <n>, server <n>, sleep <n>' line")
done
[[ "$moved" -ge 5 ]] ||
  problems+=("want at least 5 suites under $UNIT_DIR/, found $moved")

run_make unit
[[ "$code" == 0 ]] ||
  problems+=("want 'make unit' over the real tree to pass; it exited $code and said: $(flat "$out")")

report "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
