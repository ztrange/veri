#!/usr/bin/env bash
# Unit tests for scripts/extract-result.sh — pull the final assistant text out of a
# `claude -p --output-format stream-json` event stream. The stream is JSONL; the last
# `{"type":"result", ..., "result":"<text>"}` event carries the clean final answer (the
# same text claude prints in plain mode), which is what parse-verdict.sh needs to read.
#
# Run: scripts/tests/extract-result.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
EXTRACT="$HERE/../extract-result.sh"
source "$HERE/lib/harness.sh"
check() {  # check <name> <input> <expected-stdout>
  local name="$1" input="$2" exp="$3" out
  out="$(printf '%s' "$input" | "$EXTRACT")"
  if [[ "$out" == "$exp" ]]; then ok; else
    no "$name"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

finish
