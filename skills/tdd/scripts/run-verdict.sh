#!/usr/bin/env bash
# run-verdict.sh — launch one verification, taking the step title through argv rather than
# through a shell command string (#426).
#
# Usage:  run-verdict.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
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

# A verifier this process cannot start produced no answer at all, so the code for that is 2 and
# never 1: `1` is reserved for a verdict the verifier gave, and a conductor reading it spends a
# revise attempt arguing with a working test — the #424 damage. Left to `exec`, the two ways
# the start fails come back as the shell's own 127 (nothing there) and 126 (there, not
# executable), neither of which a conductor reads as a bail. One test of the verifier as an
# executable file answers both before the point of no return.
if [[ ! -x "$HERE/verify.sh" ]]; then
  echo "run-verdict.sh: cannot start the verifier: $HERE/verify.sh is missing or not executable" >&2
  exit 2
fi

# The phase this verdict is for, read the way verify.sh reads it — the first positional, after
# the value-taking options `lib/verify-options.sh` names for both of us — off a copy of argv,
# so what is exec'd below is still the caller's own arguments, unexamined and unmodified. That
# list is shared rather than copied because a copy of it here would be the one that goes stale:
# a new option verify.sh read a value after would be read as the phase here, and the reason
# file this script then cleared would be one nothing writes, leaving the real one stale — the
# #424 failure back again. Which phase names are valid stays verify.sh's judgement: an
# unrecognised word here only names a reason file nothing wrote, and clearing that is harmless.
# shellcheck source=lib/verify-options.sh
source "$HERE/lib/verify-options.sh"
args=("$@")
while verify_takes_a_value "${args[0]:-}"; do
  args=("${args[@]:2}")
done
phase="${args[0]:-}"

# Clear the phase's reason file before the verifier starts. The conductor's launch line
# redirects the verifier's stdout into `.tdd/verify-<phase>.reason`, so that file is written
# only if the verifier both starts and speaks; a launch that dies before either leaves the
# PREVIOUS step's reason sitting there, and on the #424 run a conductor read a 23-minute-old
# REJECT as this step's verdict. Truncating here makes "no verdict was produced" look like
# what it is — an empty file — rather than like an answer. The file is only truncated, never
# created: a `.tdd` that does not exist is a tree no conductor is running in, and a launcher
# that conjured one would be writing outside its job.
if [[ -n "$phase" && -f ".tdd/verify-$phase.reason" ]]; then
  : > ".tdd/verify-$phase.reason"
fi

# `exec` rather than a call: this process has nothing left to do after the verifier's, so the
# supervisor watching it watches verify.sh directly, and the verdict's exit code is verify.sh's
# own rather than one relayed through a second shell.
exec "$HERE/verify.sh" "$@"
