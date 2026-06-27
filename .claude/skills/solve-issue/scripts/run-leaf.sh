#!/usr/bin/env bash
# run-leaf.sh — launch one `claude -p` leaf and capture a forensic progress log.
#
# A leaf is a single short-lived subprocess that performs one step (write the failing
# test, implement, refactor) or one blind verification, then returns. This is the
# orchestration substrate (ADR-0001): the conductor owns the subprocess so a later
# slice (#4) can wrap this launcher with a heartbeat watcher and a hard timeout. For
# now it just launches, tees the combined output to `.tdd/<name>.log` for `tail -f`
# inspection, and propagates the leaf's exit status unchanged.
#
# Usage:
#   run-leaf.sh <leaf-name> <prompt-file> [extra claude args...]
#   run-leaf.sh <leaf-name> -            [extra args...]   # prompt read from stdin
#
# The leaf's stdout (its final message) is echoed to this script's stdout so the
# conductor can pipe a verifier leaf straight into parse-verdict.sh. Exit status is the
# leaf's own — for a verifier leaf that is the verdict (0 PASS · 1 REJECT · 2 malformed).
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
set -euo pipefail

name="${1:?usage: run-leaf.sh <leaf-name> <prompt-file> [extra claude args...]}"
prompt_src="${2:?usage: run-leaf.sh <leaf-name> <prompt-file> [extra claude args...]}"
shift 2

if [[ "$prompt_src" == "-" ]]; then
  prompt="$(cat)"
else
  prompt="$(cat "$prompt_src")"
fi

mkdir -p .tdd
log=".tdd/$name.log"

# Tee combined stdout+stderr to the progress log AND to our stdout. PIPESTATUS[0] is the
# leaf's own exit status, which `tee` would otherwise mask.
"${CLAUDE_BIN:-claude}" -p "$prompt" "$@" 2>&1 | tee "$log"
exit "${PIPESTATUS[0]}"
