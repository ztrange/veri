#!/usr/bin/env bash
# Tests for the exit code every script under scripts/ owes a caller who left out a required
# argument: 2, with a usage line on stderr. Its subject is the argument contract all scripts
# share, not one script.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   every script in the first roster, called with no arguments    → exit 2, usage on stderr
#   every script in the second roster, called without one later
#   positional argument                                           → exit 2, usage on stderr
#   every script in the third roster, given a bad argument value  → exit 2, its own usage on stderr
#   no script's source guards a positional with `${N:?…}`, which exits 1
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
  unreachable.sh
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

rejects() {  # rejects <script> [args …] — want exit 2 and a usage line naming <script> on stderr
  local line
  line="$(named_usage_offender "$SCRIPTS" "$@")" || offenders+=( "$line" )
}

name="a script given a bad argument value exits 2 with its own usage text on stderr"
offenders=()
unset VERI_TIMEOUT VERI_REFACTOR_BUDGET
rejects build-verify-prompt.sh bogus spec test-path     # unknown phase
rejects build-develop-prompt.sh bogus spec step cmd     # unknown phase
rejects build-develop-prompt.sh revise bogus spec step cmd reason  # unknown phase to revise
rejects build-verify-prompt.sh green spec test-path     # green without --fast-cmd
rejects build-verify-prompt.sh --fast-cmd x refactor spec test-path nothex  # malformed <base-sha>
rejects build-verify-prompt.sh rebase spec nothex nothex  # malformed <onto-sha>
rejects affected-suites.sh no-range                     # not a <base>..<head> range
rejects classify-bail.sh bogus                          # unknown cause
rejects leaf-timeout.sh ten                             # malformed number
rejects push-branch.sh --bogus                          # not --force-with-lease=<branch>:<sha>
rejects refactor-budget.sh ten                          # malformed number
rejects step-cost.sh --bogus                            # unknown flag
rejects stop-requested.sh --bogus                       # unknown flag
rejects stop-run.sh --mode bogus 1                      # unknown mode
rejects stop-run.sh ten                                 # malformed number
rejects workqueue.sh bogus                              # unknown subcommand
verdict "$name"

migrated() {  # migrated <script> … — want each to source lib/exit-contract.sh with no hand-built usage-and-exit
  local script lineno text
  for script in "$@"; do
    grep -E '^[[:space:]]*(source|\.)[[:space:]].*lib/exit-contract\.sh' "$SCRIPTS/$script" > /dev/null \
      || offenders+=( "$script: does not source lib/exit-contract.sh" )
    while IFS=: read -r lineno text; do
      [[ "${text#"${text%%[![:space:]]*}"}" == '#'* ]] && continue
      offenders+=( "$script:$lineno: hand-built usage-and-exit: ${text#"${text%%[![:space:]]*}"}" )
    done < <(grep -niE '((usage:|\$\{?usage([^[:alnum:]_]|$)|^[[:space:]]*usage[[:space:]]).*>&2|^[[:space:]]*refuse[[:space:]]*\(\))' "$SCRIPTS/$script")
  done
}

migration_slice() {  # migration_slice <n> <script> … — the slice's case, over migrated
  local n="$1"
  shift
  name="migration slice $n sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left"
  offenders=()
  migrated "$@"
  verdict "$name"
}

migration_slice 1 add-ledger-step.sh affected-suites.sh build-develop-prompt.sh build-verify-prompt.sh \
  capture-spec.sh classify-bail.sh clear-refactor-pending.sh
migration_slice 2 comment-class.sh cover-outcome.sh coverage-blocker.sh criterion-finished.sh \
  dashboard.sh detach-command.sh detach-leaf.sh
migration_slice 3 detect-test-command.sh ensure-run-state-ignored.sh event.sh exhausted-outcome.sh \
  extract-result.sh harvest-usage.sh invisible-work.sh
migration_slice 4 issue-worktree.sh leaf-launchable.sh leaf-model.sh leaf-role.sh leaf-timeout.sh \
  ledger-steps.sh metrics.sh
migration_slice 5 next-pending-refactor.sh next-unchecked.sh orchestrate.sh over-budget.sh \
  parallel-conductors.sh parse-verdict.sh preserve-attempt.sh
migration_slice 6 profile.sh push-branch.sh rebase-onto-default.sh red-divergence.sh \
  refactor-budget.sh refactor-owed.sh refactor-touched.sh

name="no script guards a required positional argument with a bare \${N:?…} expansion"
mapfile -t offenders < <(bare_expansion_offenders "$SCRIPTS")
verdict "$name"

finish
