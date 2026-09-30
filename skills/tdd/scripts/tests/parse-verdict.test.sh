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

check "last verdict wins" 1 'My first instinct was VERDICT: PASS but on reflection:
VERDICT: REJECT
REASON: The failure is an ImportError from a typo, not the missing behavior.' \
'The failure is an ImportError from a typo, not the missing behavior.'

check "case insensitive" 0 'verdict: pass
reason: Genuine pass — target test and full suite are green.' \
'Genuine pass — target test and full suite are green.'

check "indented verdict line" 0 '   VERDICT: PASS
   REASON: All good.' \
'All good.'

check "multiline reason" 1 'VERDICT: REJECT
REASON: Two problems:
- the test is over-coupled to the implementation
- it is also far too complex for one criterion' \
'Two problems:
- the test is over-coupled to the implementation
- it is also far too complex for one criterion'

check "reason inline after verdict" 1 'VERDICT: REJECT — the test never actually runs the code under test' \
'the test never actually runs the code under test'

check "unknown verdict word" 2 'VERDICT: MAYBE
REASON: unsure' ''

check "fenced verdict block" 1 'I ran the test myself.
```
VERDICT: REJECT
REASON: The test asserts a constant and never calls slugify().
```' \
'The test asserts a constant and never calls slugify().'

check "multiline reason then fence" 1 'VERDICT: REJECT
REASON: Two problems:
- vacuous assertion
- no call to the function
```' \
'Two problems:
- vacuous assertion
- no call to the function'

ns_plain='I read the diff against the base sha.
VERDICT: PASS
REASON: The transform is behaviour-preserving and the suite is green.'
ns_proposing='I read the diff against the base sha.
NEW_STEP: slugify returns an empty string for input that is all separators
VERDICT: PASS
REASON: The transform is behaviour-preserving and the suite is green.'
ns_out_plain="$(printf '%s' "$ns_plain" | "$PARSE")" && ns_code_plain=0 || ns_code_plain=$?
ns_out_proposing="$(printf '%s' "$ns_proposing" | "$PARSE")" && ns_code_proposing=0 || ns_code_proposing=$?
if [[ "$ns_code_proposing" == "$ns_code_plain" && "$ns_out_proposing" == "$ns_out_plain" ]]; then
  ok
else
  no "new_step lines before the verdict pair change nothing (want exit $ns_code_plain, got $ns_code_proposing)"
  diff <(printf '%s\n' "$ns_out_plain") <(printf '%s\n' "$ns_out_proposing") | sed 's/^/    /'
fi

finish
