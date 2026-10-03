#!/usr/bin/env bash
# Unit tests for scripts/parse-verdict.sh — the pure transform that extracts a blind
# verifier leaf's structured verdict (PASS | REJECT + reason) from its raw output.
# Zero-dependency plain-shell asserts, same idiom as tick-criterion.test.sh.
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

check "pass with reason" 0 'I ran the test and it failed as expected.
VERDICT: PASS
REASON: The test fails because slugify is undefined, which is the missing behavior.' \
'The test fails because slugify is undefined, which is the missing behavior.'

check "reject with reason" 1 'VERDICT: REJECT
REASON: The test asserts on an internal helper, not observable behavior.' \
'The test asserts on an internal helper, not observable behavior.'

check "malformed no verdict" 2 'I could not make up my mind about this test.' ''

nv_err="$(mktemp)"
nv_out="$(printf '%s' 'I could not make up my mind about this test.' | "$PARSE" 2>"$nv_err")" && nv_code=0 || nv_code=$?
nv_stderr="$(cat "$nv_err")"
rm -f "$nv_err"
if [[ "$nv_code" == 2 && -z "$nv_out" && "$nv_stderr" == 'parse-verdict: no VERDICT: line found' ]]; then
  ok
else
  no "no verdict line exits 2, empty stdout, the no-verdict diagnostic on stderr (got exit $nv_code, stdout '$nv_out', stderr '$nv_stderr')"
fi

sl_work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$sl_work/linked-skill"
mkdir -p "$sl_work/elsewhere"
sl_input='VERDICT: REJECT
REASON: The test asserts a constant and never calls slugify().'
sl_in_place="$(printf '%s' "$sl_input" | "$PARSE" 2>"$sl_work/in-place.err")" && sl_in_place_code=0 || sl_in_place_code=$?
sl_linked="$(cd "$sl_work/elsewhere" && printf '%s' "$sl_input" | "$sl_work/linked-skill/scripts/parse-verdict.sh" 2>"$sl_work/linked.err")" && sl_linked_code=0 || sl_linked_code=$?
sl_in_place_err="$(cat "$sl_work/in-place.err")"
sl_linked_err="$(cat "$sl_work/linked.err")"
if [[ "$sl_linked" == "$sl_in_place" && "$sl_linked_err" == "$sl_in_place_err" && "$sl_linked_code" == "$sl_in_place_code" \
      && "$sl_in_place_code" == 1 && "$sl_in_place" == 'The test asserts a constant and never calls slugify().' ]]; then
  ok
else
  no "parse-verdict.sh run through a symlink to the skill directory and from another working directory prints the same reason, stderr and exit code as when run in place"
  diff <(printf '%s\nstderr: %s\nexit %s\n' "$sl_in_place" "$sl_in_place_err" "$sl_in_place_code") \
       <(printf '%s\nstderr: %s\nexit %s\n' "$sl_linked" "$sl_linked_err" "$sl_linked_code") | sed 's/^/    /'
fi

finish
