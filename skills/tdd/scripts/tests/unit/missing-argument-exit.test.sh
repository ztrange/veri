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
pass=0 fail=0
offenders=()

# refuses <script> [args …] — call it, and record an offender unless it came back with exit 2
# and said on stderr how it is called. The judging is lib/missing-argument-exit.sh's, so that
# the check this suite's whole worth rests on has a suite of its own
# (tests/unit/missing-argument-guard.test.sh): every script in the rosters below answers
# correctly today, so no case here can tell a working check from a broken one.
refuses() {
  local line
  line="$(missing_argument_offender "$SCRIPTS" "$@")" || offenders+=( "$line" )
}

# verdict <name> — one case's result: green unless `refuses` recorded an offender above, and
# the offender lines are what a failing case prints in place of a diff. Both cases below are
# judged the same way, so the block lives here once rather than once per roster.
verdict() {
  if (( ${#offenders[@]} > 0 )); then
    fail=$((fail + 1)); echo "FAIL - $1"
    printf '    %s\n' "${offenders[@]}"
  else
    pass=$((pass + 1))
  fi
}

# 1. called with no arguments at all — the emptiest bad-arguments case there is — every script
#    that requires a positional argument refuses with exit 2 and says how it is called.
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

# 2. the same contract one argument in: each call below passes everything the script needs
#    except its last required argument, so the refusal it owes is for a LATER position than
#    case 1 tests — the position a `${N:?…}` expansion used to guard, aborting the shell with
#    status 1 and telling the conductor a methodology failure. A flag's required value counts:
#    `--since` with no date named nothing, the same way a dropped positional does.
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

# 3. the same contract read off the source instead of off a call: no script under scripts/
#    still guards a required positional with a bare `${N:?…}` expansion. The two rosters
#    above cannot settle this on their own — an expansion can sit on a position no call in
#    them reaches, and a script added tomorrow is in neither — so this case asks the tree
#    rather than a list, and covers a new script by existing. What it reports is a line
#    number, because that is what a `${N:?…}` has instead of an exit code worth calling.
#
#    lib/missing-argument-exit.sh does the reading, and its own suite
#    (tests/unit/missing-argument-guard.test.sh) plants an offender to prove the scan finds
#    one: scripts/ is clean today, so a green here says nothing about whether the scan works.
name="no script guards a required positional argument with a bare \${N:?…} expansion"
mapfile -t offenders < <(bare_expansion_offenders "$SCRIPTS")
verdict "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
