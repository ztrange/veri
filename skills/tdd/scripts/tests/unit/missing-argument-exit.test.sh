#!/usr/bin/env bash
# Tests for the exit code every script under scripts/ owes a caller who left out a required
# argument: 2, with a usage line on stderr. This suite has no single script as its subject —
# its subject is the argument contract all of them share, the one CLAUDE.md's "Exit codes are
# the API" fixes: 1 is a clean negative, an answer the call came back with, and 2 is "no
# answer could be obtained", which is what a call missing an argument is. The conductor
# branches on the difference, so a leaf launched with a dropped argument must read as a
# plumbing failure, never as a methodology one (issue #270).
#
# Three cases. Two of them call, because a script has as many ways to be called wrong as it
# has required arguments: the first drops all of them at once, the second drops one at a time
# from the later positions — the ones a `${2:?…}`/`${3:?…}` expansion used to guard, which is
# where the exit 1 the issue reports actually came from. `verify.sh green <spec>` with no
# <test-path> is the reported shape, and it is in the second roster. The third reads the
# source instead, for the offender no call can reach.
#
# Both rosters are named here rather than discovered, because "requires this argument" is not
# a question a script can be asked without calling it, and calling the ones that require none
# (dashboard.sh serves a page, profile.sh runs the suite) is not something a test may do.
# Scripts whose first positional is optional (solvable-issues.sh, detect-test-command.sh,
# classify-bail.sh) are absent from the first roster; solvable-issues.sh is in the second one
# all the same, for the repository name its --repo requires.
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
# Every call below is answered before the script does any work, so none of them starts a
# process either — a script that reached for git before reading its arguments would fail here,
# named, which is the contract this suite is for.
#
# Run: scripts/tests/unit/missing-argument-exit.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/../.."
source "$HERE/../../lib/missing-argument-exit.sh"
source "$HERE/../lib/harness.sh"
offenders=()

refuses() {
  local line
  line="$(missing_argument_offender "$SCRIPTS" "$@")" || offenders+=( "$line" )
}

verdict() {
  if (( ${#offenders[@]} > 0 )); then
    no "$1"
    printf '    %s\n' "${offenders[@]}"
  else
    ok
  fi
}

name="a script requiring a positional argument exits 2 with a usage line when called with none"
roster=(
  add-ledger-step.sh
  affected-suites.sh
  build-develop-prompt.sh
  build-verify-prompt.sh
  clear-refactor-pending.sh
  comment-class.sh
  coverage-blocker.sh
  criterion-finished.sh
  detach-leaf.sh
  event.sh
  harvest-usage.sh
  issue-worktree.sh
  leaf-model.sh
  leaf-role.sh
  metrics.sh
  over-budget.sh
  refactor-touched.sh
  run-conductor.sh
  run-leaf.sh
  supervise.sh
  tick-issue-criterion.sh
  tick-ledger.sh
  tier-usual.sh
  timed-test-run.sh
  transform-touches-tests.sh
  verify.sh
  wait-leaf.sh
)
offenders=()
for script in "${roster[@]}"; do
  refuses "$script"
done
verdict "$name"

name="a script exits 2 with a usage line when a later required argument is missing"
offenders=()
refuses add-ledger-step.sh .tdd/issue-1.md after anchor   # no <text>
refuses build-develop-prompt.sh green spec step           # green needs four more
refuses build-verify-prompt.sh green                      # no <issue-spec-file>
refuses build-verify-prompt.sh green spec                 # no <test-path>
refuses build-verify-prompt.sh --step                     # no step text
refuses issue-worktree.sh 270                             # no <slug>
refuses issue-worktree.sh --remove                        # no <n>
refuses over-budget.sh unit                               # no <seconds>
refuses over-budget.sh unit 10                            # no <usual>
refuses session-cost.sh --since                           # no ISO date
refuses solvable-issues.sh --repo                         # no owner/name
refuses supervise.sh develop-red                          # no <cmd>
refuses timed-test-run.sh all                             # no <suites>, no <cmd>
refuses timed-test-run.sh all ''                          # a suite list may be empty; <cmd> may not
refuses verify.sh green                                   # no <issue-spec-file>
refuses verify.sh green spec                              # no <test-path> — the shape #270 reports
refuses verify.sh --step                                  # no step text
verdict "$name"

name="no script guards a required positional argument with a bare \${N:?…} expansion"
mapfile -t offenders < <(bare_expansion_offenders "$SCRIPTS")
verdict "$name"

finish
