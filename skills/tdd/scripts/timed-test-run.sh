#!/usr/bin/env bash
# timed-test-run.sh — run a test command and record what it cost (issue #342, part of
# PRD #335). Nothing in a run said which tier a test-command invocation used, which suites
# it covered, or how long it took, so "is this run typical" was a question only a human
# reading the log by eye could answer. Every test-command run a leaf or the conductor makes
# goes through this wrapper, and each one leaves exactly one `test-run` line in
# `.tdd/events.jsonl`.
#
# Usage:   timed-test-run.sh <tier> <suites> <cmd> [args …]
#
# The command runs in this script's own working directory and its status is handed straight
# back to the caller. That is the load-bearing half: a test command exits non-zero when the
# suite it ran failed, and every caller branches on that, so a wrapper that reported its own
# success — or event.sh's — would turn a red suite green. `set -e` is therefore absent here
# on purpose: the command failing is an answer to report, not a reason to abort.
#
# One line per run, written after the command exits rather than a start mark and an end mark,
# so a reader counting runs counts each one once. The eight fixed keys come with it because
# the line goes through event.sh, which reads the run context out of the environment the
# caller already exports — nothing about the run is restated on this command line.
#
# `status` is the command's own exit status, the same one handed back to the caller, under the
# key supervise.sh already records an exit code by. Without it a `test-run` line looked the
# same whether the suite was green or red, so a reader could say what a run cost but not what
# it answered.
#
# `seconds` is wall time, from bash's own `printf '%(%s)T'` clock in the same unit event.sh's
# `ts` uses (seconds since the epoch), so a reader subtracts two marks without parsing a
# calendar and this script forks no `date`. It is recorded, never asserted on: what counts as
# slow is a comparison against a tier's usual, which a later reader makes.
set -uo pipefail

USAGE="usage: timed-test-run.sh <tier> <suites> <cmd> [args …]"

# hazard: `${N?}` aborts with status 1, not the 2 bad arguments owe.
[[ $# -ge 3 && -n "$1" && -n "$3" ]] || { echo "$USAGE" >&2; exit 2; }
tier="$1"
suites="$2"
shift 2

HERE="$(cd "$(dirname "$0")" && pwd)"

printf -v started '%(%s)T' -1

"$@"
code=$?

printf -v ended '%(%s)T' -1

"$HERE/event.sh" test-run "tier=$tier" "suites=$suites" "seconds=$((ended - started))" \
  "status=$code"

exit "$code"
