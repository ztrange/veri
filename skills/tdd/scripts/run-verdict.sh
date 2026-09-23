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

# `exec` rather than a call: this process has nothing left to do after the verifier's, so the
# supervisor watching it watches verify.sh directly, and the verdict's exit code is verify.sh's
# own rather than one relayed through a second shell.
exec "$HERE/verify.sh" "$@"
