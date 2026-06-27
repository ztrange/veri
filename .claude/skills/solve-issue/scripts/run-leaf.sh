#!/usr/bin/env bash
# run-leaf.sh — build and exec one `claude -p` leaf, streaming its output to stdout.
#
# A leaf is a single short-lived subprocess that performs one step (write the failing
# test, implement, refactor) or one blind verification, then returns. run-leaf is the
# inner invocation; it is NOT launched directly — the supervisor (supervise.sh) is the
# single launch choke point (ADR-0002) and owns the `.tdd/<name>.log` progress log by
# capturing this script's stdout/stderr. run-leaf therefore just resolves the prompt and
# execs claude, leaving logging and stuck-detection to the supervisor above it.
#
# Usage:
#   run-leaf.sh <prompt-file> [claude args...]
#   run-leaf.sh -             [claude args...]   # prompt read from stdin
#
# Exit status is the leaf's own — forwarded by supervise.sh; for a verifier leaf the
# verdict itself comes from parse-verdict.sh reading the captured output.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
set -euo pipefail

prompt_src="${1:?usage: run-leaf.sh <prompt-file|-> [claude args...]}"
shift

if [[ "$prompt_src" == "-" ]]; then
  prompt="$(cat)"
else
  prompt="$(cat "$prompt_src")"
fi

exec "${CLAUDE_BIN:-claude}" -p "$prompt" "$@"
