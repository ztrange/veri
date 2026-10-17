#!/usr/bin/env bash
# Unit tests for scripts/parse-verdict.sh — the pure transform that extracts a blind
# verifier leaf's structured verdict (PASS | REJECT + reason) from its raw output.
# Zero-dependency plain-shell asserts, same idiom as the other suites here.
#
# Contract under test:
#   stdin  = a verifier leaf's full raw output (free-form reasoning + a verdict block)
#   stdout = the reason text (the human-facing justification), trimmed
#   exit   = 0 PASS · 1 REJECT · 2 malformed/no verdict (stdout empty, message on stderr)
# The LAST `VERDICT:` line wins, so the word may appear earlier in the leaf's reasoning.
#
# Run: scripts/tests/parse-verdict.test.sh   (exits non-zero if any case fails)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARSE="$HERE/../parse-verdict.sh"
source "$HERE/lib/harness.sh"

check() {
  local name="$1" exp_code="$2" input="$3" exp_out="$4"
  local out code
  out="$(printf '%s' "$input" | "$PARSE")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp_out" ]]; then
    ok
  else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

finish
