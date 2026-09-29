#!/usr/bin/env bash
# Unit tests for what the `test` recipe says over a tree whose scripts have grown past the
# prose that lists them — like hermetic-suites.test.sh, count-line-guard.test.sh and
# no-docs-reads.test.sh this suite has no script as its subject: its subject is the verdict
# the development lane's own runner reaches over a tree. Zero-dependency plain-shell
# asserts, same idiom as no-docs-reads.test.sh.
#
# Why this exists (issue #143): every commit to a script under skills/tdd/scripts/ leaves
# the generated page behind the code, because that page quotes each script verbatim and
# states its length in the listing's own header. While solvable-issues.test.sh case 13 read
# that number and compared it to the script's own length, a one-line edit to
# solvable-issues.sh turned `make test` red until somebody ran `make docs` and committed the
# result — and `make test` is the target preflight reads its baseline off, that every Green
# leaf runs and that both blind verifiers run, three times per step. So a development commit
# owed a page rebuild to keep a development run alive, which is the coupling ADR 0016 rules
# out: a page behind the code is what docs-owed.sh reports and what `make docs-fresh` catches
# at a docs merge, not something the development lane gets to fail on.
#
# no-docs-reads.test.sh says that statically — no suite `make test` runs so much as names a
# path in the generated tree — and this is the same rule observed rather than read: a script
# is grown, nothing is rebuilt, and the runner is asked for its verdict.
#
# Contract under test:
#   Over a tree with one script one line longer than the suite that owns it expects, `make
#   test` runs that suite, that suite passes, and the runner says `all suites green`.
#
# The roster is narrowed to that one suite through the recipe's own TESTS variable, for two
# reasons that both have to hold.
#
#   Scope. The tree is partial, and deliberately so: the whole roster run over a copy of this
#   repository was measured at 98 s and came back SUITES FAILED, seven cases across five
#   suites — count-line-guard, skill-identity, skill-refactor-pending, skill-suite-runs and
#   workflow-timeouts — every one of them reading something a partial copy does not carry:
#   CLAUDE.md, .github/workflows/, or the git index its tracked-file sweeps ask. None of that
#   is the criterion, and a case that had to copy a whole repository including its worktrees
#   to avoid it would be pinning the copy rather than the rule.
#
#   Cost. This case runs inside `make test` itself, and `make test` runs three times per
#   step — once for develop-green and once for each blind verifier. What used to pay for that
#   scope was a real 30-case suite (solvable-issues.test.sh) chosen because it is the actual
#   historical regression #143 names — but the property under test does not care WHICH script
#   grew or WHICH suite owns it, only that the runner does not fail a development commit for
#   a page it never reads: that is a fact about `make test`'s own recipe and no-docs-reads.sh's
#   discipline, not about solvable-issues.sh. So the witness is a fixture script and a
#   two-line suite invented for this case alone (fixture-prose-lag.sh /
#   fixture-prose-lag.test.sh), not a copy of the repository's own 145-file skills/ tree: no
#   `cp -R`, and the nested `make test` run pays for one trivial assertion instead of
#   solvable-issues.test.sh's thirty.
#
# What no static check can establish is that the runner comes back green over a tree in that
# state, and one suite is enough to observe it — its own subject no longer needs to be real
# production code, since the criterion is about the runner's recipe, not about any script's
# behaviour.
#
# The plant is an appended comment, at the END of the fixture script: the scenario is a
# script one line longer than whatever last described it, and a line added at the end cannot
# disturb the code any assertion reads. probe_plant_is_real asserts the fixture script really
# did grow against the pristine copy this case wrote first, so a plant that landed nowhere
# would not leave this case passing over an ordinary tree.
#
# No line of code below spells the generated tree's name: this case no longer copies or
# touches it at all, which is the strongest form of what no-docs-reads.test.sh asks of a
# suite in this directory.
#
# Run: skills/tdd/scripts/tests/prose-lag-green.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

SCRIPT='skills/tdd/scripts/fixture-prose-lag.sh'
SCRIPT_NAME="${SCRIPT##*/}"
SUITE='skills/tdd/scripts/tests/fixture-prose-lag.test.sh'
SUITE_NAME="${SUITE##*/}"

GREEN_LINE='all suites green'

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

flat() { printf '%s' "$1" | tr '\n' '/'; }

why() { flat "$( { grep -E '^FAIL - ' <<< "$1"; tail -5 <<< "$1"; } )"; }

lines_of() { awk 'END {print NR}' "$1"; }

tree_grown_past_its_prose() {
  local planted="$WORK/tree"
  mkdir -p "$planted/$(dirname "$SCRIPT")" "$planted/$(dirname "$SUITE")"
  cp "$ROOT/Makefile" "$planted/"

  {
    printf '#!/usr/bin/env bash\n'
    printf '# A fixture script prose-lag-green.test.sh grows to observe make test'"'"'s verdict\n'
    printf '# over a tree whose prose has fallen behind its code (#143). Not shipped.\n'
    printf 'echo ok\n'
  } > "$WORK/pristine"
  cp "$WORK/pristine" "$planted/$SCRIPT"
  chmod 755 "$planted/$SCRIPT"

  {
    printf '#!/usr/bin/env bash\n'
    printf '# Fixture suite for prose-lag-green.test.sh: %s still prints "ok".\n' "$SCRIPT_NAME"
    printf 'set -uo pipefail\n'
    printf 'here="$(cd "$(dirname "$0")" && pwd)"\n'
    printf 'pass=0 fail=0\n'
    printf 'out="$("$here/../%s" 2>/dev/null)"\n' "$SCRIPT_NAME"
    printf '[[ "$out" == ok ]] && pass=$((pass + 1)) || { fail=$((fail + 1)); echo "FAIL - %s still prints ok"; }\n' "$SCRIPT_NAME"
    printf 'echo "----"\n'
    printf 'echo "$pass passed, $fail failed"\n'
    printf '[[ "$fail" -eq 0 ]]\n'
  } > "$planted/$SUITE"
  chmod 755 "$planted/$SUITE"

  printf '\n# a line this script grew after the prose that lists it was written\n' >> "$planted/$SCRIPT"
  printf '%s' "$planted"
}

probe_plant_is_real() {
  local grown here
  grown="$(lines_of "$1/$SCRIPT")"
  here="$(lines_of "$WORK/pristine")"
  [[ "$grown" -gt "$here" ]] ||
    problems+=("the case is vacuous: $SCRIPT is $grown lines in the planted tree against $here in the pristine fixture, so nothing in the fixture was left describing a file that has moved on")
}

name="\`make test\` is green over a tree whose $SCRIPT_NAME has grown past the prose listing it, with nothing rebuilt in between"
problems=()

planted="$(tree_grown_past_its_prose)"
probe_plant_is_real "$planted"

out="$(make -C "$planted" test TESTS="$SUITE" 2>&1)" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from the runner over a tree whose $SCRIPT has grown without a rebuild — a development commit must not owe one to keep the baseline green; got $code: $(why "$out")")
grep -Fqx "$GREEN_LINE" <<< "$out" ||
  problems+=("want the runner's own '$GREEN_LINE' over that tree; got: $(why "$out")")
grep -Fqx "== $SUITE_NAME" <<< "$out" ||
  problems+=("want the runner to have announced '== $SUITE_NAME' — an empty roster prints a green verdict over nothing run; got: $(flat "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
