#!/usr/bin/env bash
# run-verdict.sh — launch one verification, taking the step title through argv rather than
# through a shell command string.
#
# Usage:  run-verdict.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#
# With a <phase> and a .tdd/ directory, verify.sh's stderr is appended to .tdd/verify-<phase>.stderr.
#
# The call is verify.sh's own, argument for argument, because this script stands exactly where
# verify.sh used to stand on a conductor's command line: under `supervise.sh verdict-<phase>`,
# in place of the `bash -c "…"` string SKILL.md spelled out. That string inlined the step's own
# title into a single-quoted argument inside a double-quoted one, so a title carrying an
# apostrophe — `that shell's own job spec` — closed the `'…'` early and the launch died with
#
#     bash: -c: unexpected EOF while looking for matching `''
#
# The title never becomes shell text here. It arrives as one element of this script's argv and
# is handed on as one element of verify.sh's, where an apostrophe is a character like any
# other: no second shell parses it on the way.
#
# Arguments are passed through unexamined — which phase, spec and test path are valid is
# verify.sh's judgement, spelled there once, and a copy of it here would be a second guard to
# keep in step. A call missing an argument therefore gets verify.sh's own usage line and its
# exit 2, the code CLAUDE.md reserves for "no answer could be obtained".
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -x "$HERE/verify.sh" ]]; then
  echo "run-verdict.sh: cannot start the verifier: $HERE/verify.sh is missing or not executable" >&2
  exit 2
fi

source "$HERE/lib/verify-options.sh"
args=("$@")
while verify_takes_a_value "${args[0]:-}"; do
  args=("${args[@]:2}")
done
phase="${args[0]:-}"

if [[ -n "$phase" && -f ".tdd/verify-$phase.reason" ]]; then
  : > ".tdd/verify-$phase.reason"
fi

if [[ -n "$phase" && -d .tdd ]]; then
  exec "$HERE/verify.sh" "$@" 2>> ".tdd/verify-$phase.stderr"
fi
exec "$HERE/verify.sh" "$@"
