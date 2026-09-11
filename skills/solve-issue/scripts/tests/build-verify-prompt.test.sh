#!/usr/bin/env bash
# Tests for scripts/build-verify-prompt.sh — assembles a BLIND verifier leaf's prompt
# from on-disk artifacts only: the issue's behavior spec and the test's path. It has no
# parameter for the developer leaf's rationale, so rationale structurally cannot enter
# the verifier's context (ADR-0003). This is the seam that makes blindness enforceable
# rather than left to the conductor's discretion.
#
# Run: scripts/tests/build-verify-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-verify-prompt.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# A spec with characters that would break naive sed substitution (&, \, /, {}).
cat > "$work/spec.md" <<'SPEC'
slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\n done.
SPEC
testpath="tests/test_slugify.py"

red="$("$BUILD" red "$work/spec.md" "$testpath" test_slugify_lowercases)"

# 1. the issue spec is carried verbatim into the prompt (literal substitution)
[[ "$red" == *'slugify("Hello & World/Foo")'* ]] && ok || no "carries issue spec verbatim"

# 2. the test path is named so the blind verifier can read and run it itself
[[ "$red" == *"$testpath"* ]] && ok || no "names the test path"

# 3. blindness is stated explicitly: the verifier is told it has only test + spec, not
#    the author's reasoning
grep -qiE 'have not (been told|received).*(reason|rationale)|never.*(reason|rationale)' \
  <<<"$red" && ok || no "states the blindness contract"

# 4. the verdict-format contract parse-verdict.sh depends on is present
grep -q 'VERDICT:' <<<"$red" && grep -qi 'PASS' <<<"$red" && grep -qi 'REJECT' <<<"$red" \
  && ok || no "instructs the VERDICT: PASS|REJECT format"

# 5. verify-red audits right-reason failure AND test quality (trivial/coupled/complex)
grep -qi 'right reason' <<<"$red" && grep -qiE 'trivial|coupled|complex' <<<"$red" \
  && ok || no "verify-red audits right-reason + quality"

# 6. verify-green checks the FULL SUITE, not just the target test
green="$("$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases)"
grep -qi 'full' <<<"$green" && grep -qi 'suite' <<<"$green" \
  && ok || no "verify-green checks the full suite"

# 7. verify-refactor judges up-to-standard (conventions/typing/robustness) + still green
refactor="$("$BUILD" refactor "$work/spec.md" "$testpath")"
grep -qiE 'standard|convention|typing|robust' <<<"$refactor" \
  && grep -qi 'green' <<<"$refactor" && ok || no "verify-refactor judges standard + green"

# 8. an unknown phase is rejected (exit non-zero), not silently rendered
"$BUILD" bogus "$work/spec.md" "$testpath" >/dev/null 2>&1; code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (got $code)"

# 9. verify-pin: for a criterion the code already satisfies there is nothing to make fail,
#    so the blind verifier judges the test as a regression pin instead — same two inputs
#    (spec + test path), and the three checks that a passing test is worth committing:
#    it passes now, it fails under a mutation that removes the behavior, it is
#    behavior-level rather than trivial.
pin="$("$BUILD" pin "$work/spec.md" "$testpath" test_slugify_lowercases)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$pin" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$pin" == *"$testpath"* ]] \
  && grep -qiE 'pass(es)? (now|today|already|against|on the (current|unmodified))' <<<"$pin" \
  && grep -qi 'mutation' <<<"$pin" \
  && grep -qiE 'behaviou?r-level|trivial' <<<"$pin" \
  && ok || no "verify-pin carries spec + test path and the three pin checks (exit $code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
