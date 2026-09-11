#!/usr/bin/env bash
# Tests for scripts/build-develop-prompt.sh — see that script's header for why the
# developer's prompt is a versioned template rather than prose improvised each cycle.
# These tests hold it to the half of that bargain a test can observe: what the assembled
# prompt must carry.
#
# Contract under test, red phase:
#   build-develop-prompt.sh red <spec-file> <step-text> <test-cmd>
#   exits 0 and prints a prompt carrying the spec, the step criterion and the test command
#   verbatim, plus the `AGAINST_UNMODIFIED` report line — the protocol token the conductor
#   greps for to route a passing red test to verify-pin (SKILL.md, Red step).
#
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target>
#   exits 0 and prints a prompt naming the test the implementation must satisfy — its path
#   and its case name — and forbidding any edit to it, the rule that keeps "make it green"
#   from degenerating into "weaken the test".
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched — the bounds of the
#   tidy-up — carrying the rule that bounds it further (no generality no test demands), and
#   requiring the `RESULT:` / `FLAGS:` footer the conductor branches on.
#
# Contract under test, revise phase:
#   build-develop-prompt.sh revise <phase> <spec-file> <step-text> <test-cmd> <reason-file>
#   exits 0 and prints a prompt carrying the verifier's rejection reason verbatim — the
#   fresh leaf never saw the rejected attempt, so the reason text is the whole of what it
#   has to address — and offering `IMPOSSIBLE`, the outcome that lets it say the step
#   cannot be met rather than fake a pass.
#
# Contract under test, refusals:
#   an unknown phase, or a missing template, spec or reason file, exits 2 with a diagnostic
#   and prints no prompt — the verifier builder's contract. Exit 2 is veri's "no answer
#   could be obtained", and a half-assembled prompt on stdout would read to the conductor
#   as a whole one.
#
# Run: scripts/tests/build-develop-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-develop-prompt.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# Distinctive strings throughout, so no assertion below can match on boilerplate prose
# that the template happens to contain. The spec also carries &, \, / and {} — the
# characters a naive sed substitution would mangle.
cat > "$work/spec.md" <<'SPEC'
zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\n done.
SPEC
step_text='QWIXTLE: a seed ending in a newline gains the block and reports added'
test_cmd='make test ZORBLAT=1 -- --only "frob & nitz/quux"'

# 1. the red prompt carries its three inputs verbatim and the AGAINST_UNMODIFIED line
red="$("$BUILD" red "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$red" == *'zorblat("Frob & Nitz/Quux")'* ]] \
  && [[ "$red" == *"$step_text"* ]] \
  && [[ "$red" == *"$test_cmd"* ]] \
  && [[ "$red" == *'AGAINST_UNMODIFIED'* ]] \
  && ok || no "develop-red carries spec + step + test command verbatim and the AGAINST_UNMODIFIED report line (exit $code)"

# 2. the green prompt names the test it must satisfy — path and case name — and forbids
#    editing it
test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'
green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$green" == *"$test_path"* ]] \
  && [[ "$green" == *"$target"* ]] \
  && grep -qiE "(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test|test.{0,40}(must not|may not) be (modified|changed|edited|touched)" <<<"$green" \
  && ok || no "develop-green names the test path + target test and forbids modifying the test (exit $code)"

# 3. the refactor prompt names the files the cycle touched, carries the rule that bounds
#    the tidy-up (no generality no test demands) and requires the RESULT:/FLAGS: footer
touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'
refactor="$("$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$refactor" == *"$touched"* ]] \
  && grep -qiE '(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)' <<<"$refactor" \
  && grep -q 'RESULT:' <<<"$refactor" \
  && grep -q 'FLAGS:' <<<"$refactor" \
  && ok || no "develop-refactor carries the touched-files list + the no-untested-generality rule and the RESULT:/FLAGS: footer (exit $code)"

# 4. the revise prompt carries the verifier's rejection reason verbatim and offers the
#    IMPOSSIBLE outcome
cat > "$work/reason.md" <<'REASON'
REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\chars.
REASON
revise="$("$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$revise" == *"REJECT: the case asserts on zorblat()'s log line, not its return value — & {tricky}\\chars."* ]] \
  && [[ "$revise" == *'IMPOSSIBLE'* ]] \
  && ok || no "develop-revise carries the rejection reason verbatim and the IMPOSSIBLE outcome (exit $code)"

# 5. every way of not having what it takes to build a prompt is refused identically:
#    exit 2, a diagnostic on stderr, nothing on stdout. The missing-template case runs a
#    copy of the script from a directory with no prompts/ beside it — the template path is
#    derived from the phase name, so an unreadable template is not otherwise reachable.
mkdir -p "$work/no-prompts"
cp "$BUILD" "$work/no-prompts/build-develop-prompt.sh"

refusal_bad=""
refuses() {  # <label> <script> <args...> — records why, if this was not a clean refusal
  local label="$1" bin="$2"; shift 2
  local out code err="$work/err.txt"
  out="$("$bin" "$@" 2>"$err")"; code=$?
  [[ "$code" -eq 2 ]] || refusal_bad="$refusal_bad; $label exited $code, want 2"
  [[ -z "$out" ]] || refusal_bad="$refusal_bad; $label printed a prompt"
  [[ -s "$err" ]] || refusal_bad="$refusal_bad; $label gave no diagnostic"
}

refuses "unknown phase"    "$BUILD" bogus "$work/spec.md" "$step_text" "$test_cmd"
refuses "missing spec"     "$BUILD" red "$work/absent.md" "$step_text" "$test_cmd"
refuses "missing reason"   "$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/absent.md"
refuses "missing template" "$work/no-prompts/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd"

[[ -z "$refusal_bad" ]] \
  && ok || no "an unknown phase or a missing template/spec/reason file exits 2 with a diagnostic and prints no prompt (${refusal_bad#; })"

# 6. that refusal does not depend on the later positionals being supplied: a bad phase on
#    its own is still a bad-arguments case, which is exit 2. The shell's own `${N:?}` abort
#    exits 1, so a missing-argument check reached first would answer the wrong question.
bare_err="$work/bare-unknown-phase.err"
bare_out="$("$BUILD" bogus 2>"$bare_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$bare_out" ]] \
  && grep -q 'bogus' "$bare_err" \
  && ok || no "an unknown phase with no further arguments exits 2, names the phase on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$bare_err"))"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
