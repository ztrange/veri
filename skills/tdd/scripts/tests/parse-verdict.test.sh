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
pass=0 fail=0

# check <name> <expected-exit> <input> <expected-stdout>
check() {
  local name="$1" exp_code="$2" input="$3" exp_out="$4"
  local out code
  out="$(printf '%s' "$input" | "$PARSE")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp_out" ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

# 1. PASS verdict → exit 0, stdout is the reason
check "pass with reason" 0 'I ran the test and it failed as expected.
VERDICT: PASS
REASON: The test fails because slugify is undefined, which is the missing behavior.' \
'The test fails because slugify is undefined, which is the missing behavior.'

# 2. REJECT verdict → exit 1, stdout is the reason
check "reject with reason" 1 'VERDICT: REJECT
REASON: The test asserts on an internal helper, not observable behavior.' \
'The test asserts on an internal helper, not observable behavior.'

# 3. no verdict at all → exit 2, empty stdout
check "malformed no verdict" 2 'I could not make up my mind about this test.' ''

# 4. the LAST verdict line wins (the word appears earlier in the reasoning)
check "last verdict wins" 1 'My first instinct was VERDICT: PASS but on reflection:
VERDICT: REJECT
REASON: The failure is an ImportError from a typo, not the missing behavior.' \
'The failure is an ImportError from a typo, not the missing behavior.'

# 5. lowercase / mixed-case verdict and label are normalised
check "case insensitive" 0 'verdict: pass
reason: Genuine pass — target test and full suite are green.' \
'Genuine pass — target test and full suite are green.'

# 6. leading whitespace on the verdict line is tolerated
check "indented verdict line" 0 '   VERDICT: PASS
   REASON: All good.' \
'All good.'

# 7. multi-line reason is preserved (everything after the VERDICT line, label stripped)
check "multiline reason" 1 'VERDICT: REJECT
REASON: Two problems:
- the test is over-coupled to the implementation
- it is also far too complex for one criterion' \
'Two problems:
- the test is over-coupled to the implementation
- it is also far too complex for one criterion'

# 8. reason carried on the VERDICT line itself (no separate REASON: label)
check "reason inline after verdict" 1 'VERDICT: REJECT — the test never actually runs the code under test' \
'the test never actually runs the code under test'

# 9. an unrecognised verdict word is malformed, not a silent pass
check "unknown verdict word" 2 'VERDICT: MAYBE
REASON: unsure' ''

# 10. a verdict block wrapped in a ``` code fence (leaves often do this) must not leak
#     the closing fence into the reason. Regression from the live verify-red demo.
check "fenced verdict block" 1 'I ran the test myself.
```
VERDICT: REJECT
REASON: The test asserts a constant and never calls slugify().
```' \
'The test asserts a constant and never calls slugify().'

# 11. a tilde fence and a language-tagged fence are stripped the same way
check "multiline reason then fence" 1 'VERDICT: REJECT
REASON: Two problems:
- vacuous assertion
- no call to the function
```' \
'Two problems:
- vacuous assertion
- no call to the function'

# 12. a verifier that proposes work reports it as NEW_STEP: lines before the final
#     VERDICT:/REASON: pair (#362). Those lines are addressed to the conductor, not to
#     the reason the human reads: the same output without them must parse identically,
#     same exit code and same reason text.
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
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - new_step lines before the verdict pair change nothing (want exit $ns_code_plain, got $ns_code_proposing)"
  diff <(printf '%s\n' "$ns_out_plain") <(printf '%s\n' "$ns_out_proposing") | sed 's/^/    /'
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
