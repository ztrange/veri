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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The fast tier's directory, repo-relative — what a roster line says and what the failure
# messages quote.
UNIT_DIR='skills/tdd/scripts/tests/unit'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message: newlines become slashes.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# roster <dir> <target> — the suite paths `make -n <target>` names over the Makefile in <dir>,
# one per line, duplicates kept so a case can count them — none is an empty answer, not a
# failure, hence the `|| :` on grep. When make fails, the problem line instead, and status 1.
roster() {
  local recipe code
  recipe="$(make --no-print-directory -n -C "$1" "$2" 2>&1)" && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    echo "make -n $2 exited $code: $(flat "$recipe")"
    return 1
  fi
  printf '%s\n' "$recipe" | grep -o '[^ ]*\.test\.sh' || :
}

# 1. `make -n unit` names only the fast tier's suites, and all of them.
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

# 2. `make -n test` names both directories' suites, each once. Read off a scratch copy of the
# Makefile over a fixture tree holding one suite in each directory, so the answer does not
# depend on which real suites have moved yet — with unit/ still empty in the repo, a check
# against the real tree would pass vacuously.
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

# 3. `make unit` applies `make test`'s two guards. Each fixture is handed to the real recipe as
# `make unit UNIT_TESTS=<fixture>`, the way make-test-env.test.sh hands one to `test` as
# TESTS=<fixture>: the target's SUITES reads UNIT_TESTS, so the fixture is all it runs. Neither
# fixture calls git or python3, so the case asks only the two guards and nothing the fast tier
# may add on top of them.
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

unit_out="$(make --no-print-directory -C "$ROOT" unit UNIT_TESTS="$scratch/no-count-line.test.sh" 2>&1 < /dev/null)" &&
  unit_code=0 || unit_code=$?
[[ "$unit_code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that never reached its count line; it exited 0 and said: $(flat "$unit_out")")
grep -F 'no-count-line.test.sh' <<< "$unit_out" | grep -qF 'never reached its count line' ||
  problems+=("no line of 'make unit' names no-count-line.test.sh and says it never reached its count line: $(flat "$unit_out")")

unit_out="$(make --no-print-directory -C "$ROOT" unit UNIT_TESTS="$scratch/reaches-gh.test.sh" 2>&1 < /dev/null)" &&
  unit_code=0 || unit_code=$?
[[ "$unit_code" != 0 ]] ||
  problems+=("want 'make unit' to fail a suite that ran gh; it exited 0 and said: $(flat "$unit_out")")
grep -F 'reaches-gh.test.sh: tried the network:' <<< "$unit_out" | grep -qF 'veri-unit-gh-probe' ||
  problems+=("no 'tried the network' line of 'make unit' names reaches-gh.test.sh with the gh call carrying veri-unit-gh-probe: $(flat "$unit_out")")

report "$name"

echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
