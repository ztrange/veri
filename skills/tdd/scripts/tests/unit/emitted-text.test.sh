#!/usr/bin/env bash
# Pins the text veri emits: every script's usage output on a missing argument, and each prompt
# builder's output for fixed inputs, byte-identical by `cksum`.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/emitted-text.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$(cd "$HERE/../.." && pwd)"
pass=0 fail=0
unset "${!VERI_@}"
export LC_ALL=C

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

verdict() {
  if [[ -z "$problems" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '%s' "$problems"
  fi
}

# pin <want-cksum> <what> <script> [args …] — <what> is `usage` (exit code plus stdout and
# stderr) or `prompt` (stdout), with the scripts and scratch directories masked.
pin() {
  local want="$1" what="$2" script="$3"; shift 3
  local text code=0 got
  if [[ "$what" == usage ]]; then
    text="$("$SCRIPTS/$script" "$@" 2>&1 </dev/null)" || code=$?
    text="exit $code"$'\n'"$text"
  else
    text="$("$SCRIPTS/$script" "$@" 2>/dev/null </dev/null)" || code=$?
    text="exit $code"$'\n'"$text"
  fi
  text="${text//"$SCRIPTS"/<scripts>}"
  text="${text//"$work"/<work>}"
  got="$(printf '%s\n' "$text" | cksum)"
  got="${got//[[:space:]]/ }"
  if [[ "$got" != "$want" ]]; then
    problems+="    $script${*:+ $*}: want $want, got $got"$'\n'
  fi
}

cat > "$work/spec.md" <<'EOF'
## What to build

A fixed spec for pinning prompts, with an & and a \ in it.

## Acceptance criteria

- [ ] one criterion
EOF
cat > "$work/bug.md" <<'EOF'
## Bug

It breaks.

## Acceptance criteria

- [ ] it no longer breaks
EOF
cat > "$work/refactor.md" <<'EOF'
## Refactor

Move a function.
EOF
cat > "$work/ledger.md" <<'EOF'
# Plan for #1 — fixed

- [ ] one criterion ⟦criterion 1⟧
EOF
echo "the test pins nothing" > "$work/reason.md"

# 1. what every script prints on a missing argument, and what each prompt builder prints for
#    fixed inputs, is byte-identical to what it printed before the comment sweep.
name="usage output on a missing argument and prompt output for fixed inputs are unchanged"
problems=""
pin '1022369698 110' usage add-ledger-step.sh
pin '3115481657 48' usage affected-suites.sh
pin '1272164864 173' usage build-develop-prompt.sh
pin '217537457 94' usage build-verify-prompt.sh
pin '3916945256 64' usage clear-refactor-pending.sh
pin '3860559291 55' usage comment-class.sh
pin '3619846594 58' usage coverage-blocker.sh
pin '1651026890 60' usage criterion-finished.sh
pin '3059909970 45' usage detach-leaf.sh
pin '1642735334 47' usage event.sh
pin '1165055683 43' usage harvest-usage.sh
pin '3146090332 58' usage issue-worktree.sh
pin '620984865 40' usage leaf-model.sh
pin '1964507760 39' usage leaf-role.sh
pin '1507644654 40' usage metrics.sh
pin '3513573825 54' usage over-budget.sh
pin '3822748993 60' usage refactor-touched.sh
pin '134802541 39' usage run-conductor.sh
pin '1042169812 59' usage run-leaf.sh
pin '4252593059 50' usage supervise.sh
pin '3650033748 63' usage tick-issue-criterion.sh
pin '1820952631 74' usage tick-ledger.sh
pin '3568418922 35' usage tier-usual.sh
pin '1826447128 65' usage timed-test-run.sh
pin '2203537502 52' usage transform-touches-tests.sh
pin '3019634167 120' usage verify.sh
pin '3132011146 48' usage wait-leaf.sh
pin '1022369698 110' usage add-ledger-step.sh .tdd/issue-1.md after anchor
pin '3421904611 226' usage build-develop-prompt.sh green spec step
pin '217537457 94' usage build-verify-prompt.sh green
pin '217537457 94' usage build-verify-prompt.sh green spec
pin '2618584748 136' usage build-verify-prompt.sh --step
pin '3146090332 58' usage issue-worktree.sh 270
pin '3146090332 58' usage issue-worktree.sh --remove
pin '3513573825 54' usage over-budget.sh unit
pin '3513573825 54' usage over-budget.sh unit 10
pin '28322156 83' usage session-cost.sh --since
pin '1968660819 53' usage solvable-issues.sh --repo
pin '1825838473 75' usage supervise.sh develop-red
pin '1826447128 65' usage timed-test-run.sh all
pin '1826447128 65' usage timed-test-run.sh all ''
pin '3019634167 120' usage verify.sh green
pin '3019634167 120' usage verify.sh green spec
pin '3584306278 149' usage verify.sh --step

spec="$work/spec.md" step="the step" cmd="make test"
pin '1430760052 9932' prompt build-develop-prompt.sh red "$spec" "$step" "$cmd"
pin '4073833405 10907' prompt build-develop-prompt.sh red "$work/bug.md" "$step" "$cmd"
pin '1203928892 6783' prompt build-develop-prompt.sh green "$spec" "$step" "$cmd" t/x.test.sh "case one" "make unit"
pin '3673328186 8839' prompt build-develop-prompt.sh refactor "$spec" "$step" "$cmd" "a.sh b.sh"
pin '2836921973 4545' prompt build-develop-prompt.sh cover "$spec" "$step" "$cmd"
pin '3121106979 4287' prompt build-develop-prompt.sh transform "$spec" "$step" "$cmd"
pin '505412475 4319' prompt build-develop-prompt.sh structural "$spec" "a candidate" "$cmd" "a.sh b.sh"
pin '1053899059 6930' prompt build-develop-prompt.sh revise red "$spec" "$step" "$cmd" "$work/reason.md"
pin '3328331771 6932' prompt build-develop-prompt.sh revise green "$spec" "$step" "$cmd" "$work/reason.md"
pin '25705623 6935' prompt build-develop-prompt.sh revise refactor "$spec" "$step" "$cmd" "$work/reason.md"
pin '2802947363 3593' prompt build-develop-prompt.sh exhausted "$spec" "$step" "$cmd" "$work/reason.md"
pin '2179429738 5056' prompt build-develop-prompt.sh reconcile "$spec" "$step" "$cmd" tdd/1-x 0123456789abcdef
pin '3590900387 4365' prompt build-develop-prompt.sh over-budget "$spec" "$step" "$cmd" 12.5 10
pin '1166736421 4759' prompt build-develop-prompt.sh rebase "$spec" "$step" "$cmd" 0123456 89abcde "a.sh b.sh"
pin '3620616597 6175' prompt build-verify-prompt.sh red "$spec" t/x.test.sh "case one"
pin '3052690884 7034' prompt build-verify-prompt.sh red "$work/bug.md" t/x.test.sh "case one"
pin '122415219 6352' prompt build-verify-prompt.sh --step "$step" red "$spec" t/x.test.sh "case one"
pin '2482643720 6268' prompt build-verify-prompt.sh --fast-cmd "make unit" green "$spec" t/x.test.sh "case one"
pin '1035243659 7724' prompt build-verify-prompt.sh --fast-cmd "make unit" refactor "$spec" t/x.test.sh 0123456
pin '3465355537 6114' prompt build-verify-prompt.sh pin "$spec" t/x.test.sh "case one"
pin '1148857191 6717' prompt build-verify-prompt.sh plan "$spec" "$work/ledger.md"
pin '1703273279 7262' prompt build-verify-prompt.sh plan "$work/refactor.md" "$work/ledger.md"
pin '3733575378 4812' prompt build-verify-prompt.sh rebase "$spec" 0123456 89abcde
pin '1153397306 4495' prompt build-verify-prompt.sh transform "$spec" "$work/reason.md" 0123456
verdict "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
