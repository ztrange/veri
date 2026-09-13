#!/usr/bin/env bash
# Unit tests for the line between the repository's two test targets — like
# hermetic-suites.test.sh and workflow-timeouts.test.sh this suite has no script as its
# subject: its subject is which suite each target runs. Zero-dependency plain-shell
# asserts, same idiom as the other suites under docs/tests/.
#
# Why this exists (issue #137): `make test` is what every veri leaf runs after every edit
# and what the conductor reads the baseline off, so a docs assertion inside it lets the
# docs pipeline stop development on a red the code did not cause. ADR 0016 puts the two on
# separate cadences. docs-gap-adr.test.sh — whose subject is a record under docs/adr/ —
# sat under the `make test` glob anyway, on a rationale that has stopped being true: it
# argued that `make docs-test` named its suites one recipe line each, so a suite added
# there would run only once the Makefile was edited too. That target globs now.
#
# Contract under test:
#   docs/tests/docs-gap-adr.test.sh is where the ADR suite lives: `make docs-test` runs
#   it, it passes from there, and its header no longer argues for the home it left. And no
#   suite `make test` runs declares a subject in the docs pipeline.
#
# Both rosters are read off `make -n`, which expands a target's list and runs nothing. The
# claim is which suites a target would run, and running them to find out would cost
# minutes — and for docs-test would recurse into this file.
#
# Where this suite lives is decided by its own subject: a suite about the docs lane
# running inside `make test` is the arrangement it exists to forbid. It reads two make
# expansions and one small suite, and spawns no page build, so it costs `make docs-test`
# about a second.
#
# Run: docs/tests/suite-lanes.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0

# The suite this step moves, at the path it has to end up on — named once so the roster
# probe, the run probe and the header probes all ask about the same file.
ADR_SUITE='docs/tests/docs-gap-adr.test.sh'

# What a subject line naming the docs pipeline looks like. Every suite in this repository
# declares its subject on its first comment line ("Unit tests for scripts/verify.sh — …",
# "Unit tests for the workflow files under .github/workflows/ — …"), so that one line is
# where a docs suite gives itself away: it names a path under docs/, or the page those
# paths build. Not a format anyone has to keep — a suite whose subject is a script says so
# without either word.
DOCS_SUBJECT='docs/|walkthrough'

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message. Newlines become slashes so a roster
# or a suite's tail that came back wrong is still readable inside an indented problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# roster <target> — the suite paths <target> would run, one per line. `make -n` prints the
# recipe with the wildcard already expanded and executes none of it, so this is the
# target's own list rather than a second copy of the glob written out here.
roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

# subject <path> — the first comment line after the shebang, which is where every suite in
# this tree says what it is about.
subject() { awk 'NR > 1 && /^#/ { print; exit }' "$ROOT/$1"; }

# 1. The two halves of the lane, in one case because they are one rule: the ADR suite is
#    run by the docs target and by nothing in development's. Four probes.
#
#    The roster probe alone would pass over a file that the target runs and that dies on
#    its first line, so the suite is also run from its new home: a move that leaves its
#    ROOT counting the old depth still gets picked up by the glob and still cannot find
#    the ADR set it reads. Its exit code is the claim and the count line beside it, for
#    the reason case 4 of docs-guard-filter.test.sh spells out — zero cases run and every
#    case passing both exit 0.
#
#    The header is the third probe because the rationale is what makes the placement
#    reviewable: the paragraph arguing this suite belongs under `make test`, and the run
#    line pointing at its old path, are both false where it now sits, and a false reason
#    left in place is what sends the next reader to move it back.
#
#    The last probe sweeps development's whole roster rather than only asking whether this
#    one file left it, because the rule is about the lane and not about one suite: any
#    file `make test` runs whose subject line names something under docs/ is the same
#    failure wearing a different name.
name="the ADR suite runs under 'make docs-test', and no suite 'make test' runs is about the docs pipeline"
problems=()

docs_roster="$(roster docs-test)"
test_roster="$(roster test)"

printf '%s\n' "$docs_roster" | grep -qx "$ADR_SUITE" ||
  problems+=("want $ADR_SUITE among the suites 'make docs-test' runs; it runs: $(flat "$docs_roster")")

if [[ -x "$ROOT/$ADR_SUITE" ]]; then
  adr_out="$("$ROOT/$ADR_SUITE" 2>&1)" && adr_code=0 || adr_code=$?
  { [[ "$adr_code" == 0 ]] && printf '%s\n' "$adr_out" | grep -Eq '[1-9][0-9]* passed, 0 failed'; } ||
    problems+=("want exit 0 and a green count over cases that ran from $ADR_SUITE; got $adr_code: $(flat "$(printf '%s' "$adr_out" | tail -3)")")

  header="$(awk '/^set /{ exit } { print }' "$ROOT/$ADR_SUITE")"
  [[ "$header" != *"not under docs/tests/"* ]] ||
    problems+=("the header still argues the suite lives somewhere other than docs/tests/, which is where it now is")
  [[ "$header" != *"scripts/tests/docs-gap-adr.test.sh"* ]] ||
    problems+=("the header still names scripts/tests/docs-gap-adr.test.sh, a path the suite no longer has")
  [[ "$header" == *"docs-test"* ]] ||
    problems+=("want the header to say which target runs the suite now; it does not mention docs-test")
else
  problems+=("want $ADR_SUITE to exist and be executable; it is not")
fi

while IFS= read -r suite; do
  [[ -n "$suite" ]] || continue
  subj="$(subject "$suite")"
  if printf '%s' "$subj" | grep -Eq "$DOCS_SUBJECT"; then
    problems+=("'make test' runs $suite, whose subject is the docs pipeline: $(flat "$subj")")
  fi
done <<EOF
$test_roster
EOF

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
