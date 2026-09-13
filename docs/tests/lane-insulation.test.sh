#!/usr/bin/env bash
# Unit tests for which tree the docs lane's own suites are allowed to judge — like
# suite-lanes.test.sh this suite has no script as its subject: its subject is whether a
# suite under docs/tests/ answers for a tree it built or for the tree it happens to be
# running in. Zero-dependency plain-shell asserts, same idiom as the other suites here.
#
# Why this exists (issue #137): `make docs-test` is the test command a /tdd run on a docs
# issue uses, so the conductor reads its baseline off it and refuses to start on a red one.
# A suite that judges THIS tree goes red on events belonging to the other lane — a script
# commit leaving lines no commentary chunk covers, a tag cut with no commit behind it — and
# the docs pool then cannot be drained until somebody rebuilds the page by hand. Observed
# 2026-09-13: #131 added lines inside detect-test-command.sh and docs-owed.test.sh was red
# on main until a prose PR (#142) caught up. A page behind the code is already a
# docs-owed.sh reading and docs-fresh's job at merge time; it is not the generator's
# suite's to fail on.
#
# Contract under test:
#   docs/tests/docs-owed.test.sh passes over a tree whose scripts carry lines no commentary
#   chunk covers. Its zero-debt case is a claim about a tree that suite builds, so how far
#   this repository's own prose has fallen behind its own scripts cannot decide it.
#
# The tree is copied and planted rather than asserted about where it stands, because the
# claim is about some other repository and this one owes no commentary today: a probe run
# here would pass on both sides of the fix and pin nothing. The copy is docs/, skills/ and
# the Makefile — what the suite under test reads — and not the whole tree, because in the
# primary clone .tdd/wt/ holds this repository's worktrees and a recursive copy would
# descend into them.
#
# It costs one copy of those paths, one page build over the copy and one run of the suite
# under test, ~14 s measured, nearly all of it that run — which is the observation itself.
#
# Run: docs/tests/lane-insulation.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The suite under test, and the script the case plants a coverage gap in. Named once each
# because the failure messages quote them and the probes act on them, and a case that
# planted the gap in one script while naming another in its complaint would send the reader
# to the wrong file. The bare name too: the build reports debt by basename.
SUITE='docs/tests/docs-owed.test.sh'
SCRIPT='skills/tdd/scripts/classify-bail.sh'
SCRIPT_NAME="${SCRIPT##*/}"

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

# flat <text> — one line of it, for a failure message. Newlines become slashes so a suite's
# tail that came back red is still readable inside an indented problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# 1. A script gains lines nobody has written prose for, which is what a merged development
#    PR leaves behind every time (#125: the build carries an uncovered line as debt instead
#    of refusing to emit the page, and a change under skills/ owes no rebuild). The docs
#    lane's suite for the tool that REPORTS that debt must still pass, because the debt is
#    the tool's subject and not its verdict on the repository it lives in.
#
#    The gap is planted at the end of the script: a chunk in docs/wt/commentary.py claims a
#    line range, so any line inside the file's existing length may already be claimed, while
#    the lines past its end can be claimed by nothing.
#
#    Exit code and the count line together are the claim, for the reason case 4 of
#    docs-guard-filter.test.sh spells out: a suite with zero cases run and a suite with
#    every case passing both exit 0, and only one of them is evidence.
name="docs/tests/docs-owed.test.sh passes over a tree whose scripts carry lines no commentary chunk covers"
problems=()

d="$WORK/tree"
mkdir -p "$d"
cp -R "$ROOT/docs" "$d/docs"
cp -R "$ROOT/skills" "$d/skills"
cp "$ROOT/Makefile" "$d/"
rm -rf "$d/docs/wt/__pycache__"

printf '\n# a line this tree grew after its prose was written\n# and a second one\n' >> "$d/$SCRIPT"

# The plant is only a plant if the build reads it as debt, and the build is where
# docs-owed.sh reads coverage from too — so this asks the same question the subject asks,
# of the copy, rather than re-deriving the coverage rule here. Without it a renamed script
# or a commentary chunk that grew to the end of the file would leave the case passing over
# a tree that owes nothing, which is the tree it already passes over today.
build_err="$( cd "$d" && python3 docs/build-walkthrough.py --stdout 2>&1 >/dev/null )"
grep -Fq "owed: $SCRIPT_NAME" <<< "$build_err" ||
  problems+=("the case is vacuous: appending to $SCRIPT left no coverage gap for the build to report; it said: $(flat "$build_err")")

out="$("$d/$SUITE" 2>&1)" && code=0 || code=$?
{ [[ "$code" == 0 ]] && grep -Eq '[1-9][0-9]* passed, 0 failed' <<< "$out"; } ||
  problems+=("want $SUITE green over a tree owing prose for $SCRIPT_NAME — a script commit is a development-lane event and must not turn the docs lane red; got $code: $(flat "$(tail -5 <<< "$out")")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
