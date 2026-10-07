#!/usr/bin/env bash
# Tests for the exit code every script under scripts/ owes a caller who left out a required
# argument: 2, with a usage line on stderr. Its subject is the argument contract all scripts
# share, not one script.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   every scripts/*.sh whose usage line names a <…> outside […],
#   called with no arguments                                      → exit 2, usage on stderr
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
source "$HERE/../lib/verdict.sh"
offenders=()

refuses() {
  local line
  line="$(missing_argument_offender "$SCRIPTS" "$@")" || offenders+=( "$line" )
}

name="a script requiring a positional argument exits 2 with a usage line when called with none"
unset VERI_TIMEOUT VERI_REFACTOR_BUDGET
mapfile -t offenders < <(argument_audit "$SCRIPTS" 2>&1)
verdict "$name" "${offenders[@]}"

usage_stub() {  # usage_stub <path> <usage-line> <exit> — an executable that prints <usage-line> on stderr and exits <exit>
  printf '#!/bin/sh\necho "%s" >&2\nexit %s\n' "$2" "$3" > "$1"
  chmod +x "$1"
}

name="the missing-argument audit covers a script added to the scripts/ directory whose usage line names a required argument"
plant="$(scratch_dir)"
usage_stub "$plant/planted.sh" 'usage: planted.sh <n>' 0
expect_eq "$name" 'planted.sh: want exit 2, got 0' "$(argument_audit "$plant" 2>&1)"

name="the missing-argument audit returns 1 when a script it audits is an offender"
code=0
argument_audit "$plant" > /dev/null 2>&1 || code=$?
expect_eq "$name" 1 "$code"

name="the missing-argument audit over a directory holding no script prints nothing and returns 0"
empty="$(scratch_dir)"
code=0
out="$(argument_audit "$empty" 2>&1)" || code=$?
expect_eq "$name" '0:' "$code:$out"

name="the missing-argument audit calls only scripts whose usage line names a required argument, and wants each one's usage line to name it"
mixed="$(scratch_dir)"
usage_stub "$mixed/optional.sh" 'usage: optional.sh [<n>]' 0
usage_stub "$mixed/required.sh" 'usage: <n>' 2
expect_eq "$name" 'required.sh: usage line on stderr does not name it: usage: <n>' "$(argument_audit "$mixed" 2>&1)"

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
verdict "$name" "${offenders[@]}"

rejects() {  # rejects <script> [args …] — want exit 2 and a usage line naming <script> on stderr
  local line
  line="$(named_usage_offender "$SCRIPTS" "$@")" || offenders+=( "$line" )
}

name="a script given a bad argument value exits 2 with its own usage text on stderr"
offenders=()
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
verdict "$name" "${offenders[@]}"

name="migration slice 6 refuses an unresolvable commit or a missing file with the script's own usage text"
offenders=()
rejects refactor-owed.sh render                         # no <file>
rejects refactor-owed.sh list                           # no <file>
rejects refactor-owed.sh append                         # no <file>
verdict "$name" "${offenders[@]}"

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
  verdict "$name" "${offenders[@]}"
}

migration_slice 2 detach-command.sh detach-leaf.sh
migration_slice 3 event.sh
migration_slice 7 run-conductor.sh
migration_slice 9 supervise.sh
migration_slice 10 verify.sh wait-leaf.sh

name="no script guards a required positional argument with a bare \${N:?…} expansion"
mapfile -t offenders < <(bare_expansion_offenders "$SCRIPTS")
verdict "$name" "${offenders[@]}"

finish
