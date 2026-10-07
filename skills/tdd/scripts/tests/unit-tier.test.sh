#!/usr/bin/env bash
# Unit tests for the `unit` target in this repository's Makefile — the fast tier. Its
# subject is which suites a make target runs, read off `make -n`.
#
# Contract under test:
#   1. `make -n unit` names only suites matching skills/tdd/scripts/tests/unit/*.test.sh —
#      and every one of them on disk, so an empty roster over a populated directory is a
#      failure rather than a vacuous pass.
#   2. `make -n test` names the suites of both directories — the flat one and unit/ — and
#      none of them twice.
#   3. `make unit` guards a suite the way `make test` does: a suite that never prints its
#      `<n> passed, <m> failed` count line fails the run, named, and so does one that calls gh,
#      caught by the OFFLINE_BIN shim's reach log and named with what it tried.
#
# Run: skills/tdd/scripts/tests/unit-tier.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

UNIT_DIR='skills/tdd/scripts/tests/unit'


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

run_make_in() {
  local dir="$1"
  shift
  out="$(make --no-print-directory -C "$dir" "$@" 2>&1 < /dev/null)" && code=0 || code=$?
}

run_make() { run_make_in "$ROOT" "$@"; }

USAGE_COUNTS='(^|[^a-z0-9])git [0-9]+, python3 [0-9]+, server [0-9]+, sleep [0-9]+'

unit_roster_problems() {
  local root="$1" f base flat_copy header moved=0
  for f in "$root/$UNIT_DIR"/*.test.sh; do
    [[ -e "$f" ]] || continue
    base="$(basename "$f")"
    flat_copy="$root/skills/tdd/scripts/tests/$base"
    moved=$((moved + 1))
    [[ -e "$flat_copy" ]] && cmp -s "$f" "$flat_copy" &&
      echo "$base is under $UNIT_DIR/ and still in skills/tdd/scripts/tests/ too"
    header="$(sed -n '2,$p' "$f" | sed '/^#/!q' | grep '^#')"
    grep -Eq "$USAGE_COUNTS" <<< "$header" ||
      echo "$base's header comment has no 'git <n>, python3 <n>, server <n>, sleep <n>' line"
  done
  [[ "$moved" -ge 5 ]] ||
    echo "want at least 5 suites under $UNIT_DIR/, found $moved"
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

scratch="$(scratch_dir)"
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
cat > "$scratch/calls-real-interpreter.test.sh" <<'SUITE'
#!/usr/bin/env bash
if python3 -c 'pass' > /dev/null; then echo "1 passed, 0 failed"; exit 0; fi
echo "FAIL - the interpreter probe"
echo "0 passed, 1 failed"
exit 1
SUITE
cat > "$scratch/calls-real-transfer.test.sh" <<'SUITE'
#!/usr/bin/env bash
curl --silent --max-time 2 http://example.invalid/veri-unit-curl-probe > /dev/null 2>&1
echo "1 passed, 0 failed"
exit 0
SUITE
chmod +x "$scratch/calls-real-vcs.test.sh" "$scratch/mocks-vcs.test.sh" "$scratch/calls-real-interpreter.test.sh" \
  "$scratch/calls-real-transfer.test.sh"

run_make unit UNIT_TESTS="$scratch/calls-real-vcs.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran real git; it exited 0 and said: $(flat "$out")")
grep -qw git < <(grep -v '^== ' <<< "$out") ||
  problems+=("no line of 'make unit' over a suite that ran real git names git: $(flat "$out")")

run_make unit UNIT_TESTS="$scratch/calls-real-interpreter.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran real python3; it exited 0 and said: $(flat "$out")")
grep -qw python3 < <(grep -v '^== ' <<< "$out") ||
  problems+=("no line of 'make unit' over a suite that ran real python3 names python3: $(flat "$out")")

run_make unit UNIT_TESTS="$scratch/calls-real-transfer.test.sh"
[[ "$code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran real curl; it exited 0 and said: $(flat "$out")")
grep -qw curl < <(grep -v '^== ' <<< "$out") ||
  problems+=("no line of 'make unit' over a suite that ran real curl names curl: $(flat "$out")")

run_make test TESTS="$scratch/calls-real-vcs.test.sh" UNIT_TESTS=
[[ "$code" == 0 ]] ||
  problems+=("want 'make test' to pass a suite that ran real git; it exited $code and said: $(flat "$out")")

run_make unit UNIT_TESTS="$scratch/mocks-vcs.test.sh"
[[ "$code" == 0 ]] ||
  problems+=("want 'make unit' to pass a suite that mocks git as a shell function; it exited $code and said: $(flat "$out")")

report "$name"

name="make test refuses real git in a suite under $UNIT_DIR/, naming git"
problems=()

tree="$(scratch_dir)"
mkdir -p "$tree/$UNIT_DIR" "$tree/skills/tdd/scripts/lib"
cp "$ROOT/Makefile" "$tree/Makefile"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$tree/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/tests/offline" "$ROOT/skills/tdd/scripts/tests/unit-guard" "$tree/skills/tdd/scripts/tests/"
cp "$scratch/calls-real-vcs.test.sh" "$tree/$UNIT_DIR/calls-real-vcs.test.sh"

run_make_in "$tree" test
[[ "$code" != 0 ]] ||
  problems+=("want 'make test' to fail a suite under $UNIT_DIR/ that ran real git; it exited 0 and said: $(flat "$out")")
grep -qw git < <(grep -v '^== ' <<< "$out") ||
  problems+=("no line of 'make test' over a suite under $UNIT_DIR/ that ran real git names git: $(flat "$out")")

report "$name"

name="make test passes a suite outside $UNIT_DIR/ that runs real git, after one under $UNIT_DIR/"
problems=()

mixed="$(scratch_dir)"
mkdir -p "$mixed/$UNIT_DIR" "$mixed/skills/tdd/scripts/lib"
cp "$ROOT/Makefile" "$mixed/Makefile"
cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$mixed/skills/tdd/scripts/lib/"
cp "$ROOT/skills/tdd/scripts/run-suite.sh" "$mixed/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/veri" "$mixed/skills/tdd/scripts/"
cp -R "$ROOT/skills/tdd/scripts/tests/offline" "$ROOT/skills/tdd/scripts/tests/unit-guard" "$mixed/skills/tdd/scripts/tests/"
cp "$scratch/mocks-vcs.test.sh" "$mixed/$UNIT_DIR/mocks-vcs.test.sh"
cp "$scratch/calls-real-vcs.test.sh" "$mixed/skills/tdd/scripts/tests/calls-real-vcs.test.sh"

run_make_in "$mixed" test TESTS="$UNIT_DIR/mocks-vcs.test.sh skills/tdd/scripts/tests/calls-real-vcs.test.sh"
[[ "$code" == 0 ]] ||
  problems+=("want 'make test' to pass a suite outside $UNIT_DIR/ that ran real git after one under it; it exited $code and said: $(flat "$out")")

report "$name"

name="at least five existing suites move into $UNIT_DIR/, each recording its git/python3/server/sleep count in its header"
problems=()

while IFS= read -r problem; do
  [[ -n "$problem" ]] && problems+=("$problem")
done < <(unit_roster_problems "$ROOT")

report "$name"

name="the unit roster check names a suite under $UNIT_DIR/ whose header lacks its git/python3/server/sleep line"
problems=()

fixture="$(scratch_dir)"
mkdir -p "$fixture/$UNIT_DIR"
printf '#!/usr/bin/env bash\n# A fixture suite.\n# git 0, python3 0, server 0, sleep 0\necho "1 passed, 0 failed"\n' \
  > "$fixture/$UNIT_DIR/has-header.test.sh"
printf '#!/usr/bin/env bash\n# A fixture suite with no counts.\necho "1 passed, 0 failed"\n' \
  > "$fixture/$UNIT_DIR/lacks-header.test.sh"

said="$(unit_roster_problems "$fixture" 2>&1)"
grep -F 'lacks-header.test.sh' <<< "$said" | grep -F "header comment has no 'git <n>, python3 <n>, server <n>, sleep <n>' line" > /dev/null ||
  problems+=("want the roster check over a fixture to name lacks-header.test.sh's header as lacking its counts line; it said: $(flat "$said")")
grep -F 'has-header.test.sh' <<< "$said" | grep -F 'header comment' > /dev/null &&
  problems+=("the roster check named has-header.test.sh's header, which carries its counts line: $(flat "$said")")

report "$name"

name="unit-tier.test.sh runs no nested make unit or make test over the real roster; every nested run names a fixture suite"
problems=()

lineno=0
while IFS= read -r line; do
  lineno=$((lineno + 1))
  [[ "$line" =~ ^[[:space:]]*# ]] && continue
  [[ "$line" =~ (^|[[:space:]])-n([[:space:]]|$) ]] && continue
  if [[ "$line" =~ (^|[[:space:]])run_make[[:space:]]+(unit|test)([[:space:]]|$) ]]; then
    target="${BASH_REMATCH[2]}"
  elif [[ "$line" =~ (run_make_in|-C)[[:space:]]+\"\$ROOT\"[[:space:]]+(unit|test)([[:space:]]|$) ]]; then
    target="${BASH_REMATCH[2]}"
  else
    continue
  fi
  [[ "$line" =~ (^|[[:space:]])UNIT_TESTS= ]] ||
    problems+=("line $lineno runs make $target over the real $UNIT_DIR/ roster: $line")
  [[ "$target" == unit || "$line" =~ (^|[[:space:]])TESTS= ]] ||
    problems+=("line $lineno runs make test over the real flat roster: $line")
done < "${BASH_SOURCE[0]}"

report "$name"

name="the Makefile's guard comment and CLAUDE.md's fast-tier paragraph say make test guards the suites under $UNIT_DIR/ and no other"
problems=()

says_scope() {
  local text="$1" who="$2" place="$3" s
  text="$(tr '\n' ' ' <<< "$text")"
  text="${text//. /$'.\n'}"
  while IFS= read -r s; do
    [[ "$s" == *"$who"* && "$s" == *"$place"* && "$s" =~ guard|shim|refus &&
      "$s" =~ no\ other|outside|only ]] && return 0
  done <<< "$text"
  return 1
}

guard_comment="$(awk '/^#/ { b = b substr($0, 2) " "; next } /^UNIT_GUARD_BIN :=/ { print b; exit } { b = "" }' "$ROOT/Makefile")"
fast_tier="$(awk '/^\*\*`skills\/tdd\/scripts\/tests\/unit\/` is the fast tier\*\*/ { p = 1 } p && /^$/ { exit } p' "$ROOT/CLAUDE.md")"

[[ "$guard_comment" != *"same suites unguarded"* ]] ||
  problems+=("the Makefile's comment on UNIT_GUARD_BIN still says \`test\` runs the same suites unguarded: $guard_comment")
says_scope "$guard_comment" '`test`' 'unit' ||
  problems+=("no sentence of the Makefile's comment on UNIT_GUARD_BIN says \`test\` guards the suites under $UNIT_DIR/ and no other: $guard_comment")
says_scope "$fast_tier" '`make test`' '' ||
  problems+=("no sentence of CLAUDE.md's fast-tier paragraph says \`make test\` guards the suites under $UNIT_DIR/ and no other: $(flat "$fast_tier")")

report "$name"

finish
