#!/usr/bin/env bash
# Unit test for the tests-frozen record and check in skills/tdd/SKILL.md, read as text.
#
# Contract under test:
#   SKILL.md's Red section runs `tests-frozen.sh record` once verify-red PASSes; it runs
#   `tests-frozen.sh check` before every verify-green — in Green between the develop-green wait
#   and the verify-green launch, and in *Revising on a REJECT* between the revise-green wait and
#   its re-verify; on check exit 1 it writes a reason naming the file to
#   .tdd/verify-green.reason, treats the attempt as a REJECT that spends REVISE_BUDGET and
#   launches no verifier; on exit 0 the verifier is launched as before; on exit 2 it bails. Every
#   record and check names the step's record by `tests-frozen.sh path` over the step text, and a
#   ⟦replaces-case⟧ step records at its verify-pin PASS, while a ⟦suite-repair⟧ or ⟦ci-repair⟧ step
#   is never frozen. Only sentences naming tests-frozen count,
#   so text the sections already held cannot satisfy a case; the outcome sentences are pinned
#   verbatim, because a keyword check stays green over a sentence that says the opposite.
#
# Run: scripts/tests/skill-tests-frozen.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"

record_arg='--step "$($S/next-unchecked.sh < .tdd/issue-<n>.md)"'
key_sentence='With `--step "<step text>"` in place of a record file, the record file is the one `$S/tests-frozen.sh path "<step text>"` prints, `.tdd/tests-frozen-<k>.record` with `<k>` the first 16 hex digits of the step text'"'"'s SHA-256: a step text is often longer than a filename may be and may hold a `/`, so the text itself is never the filename.'
repair_sentence='A step marked `⟦suite-repair⟧` or `⟦ci-repair⟧` is never frozen: for it `record --step` writes nothing and `check --step` exits 0, because its fix is often an edit to the very test file the full run or CI left red.'
ci_sentence='A `⟦ci-repair⟧` step therefore records nothing before its green, and its green may edit the test the CI job failed.'
exit2_sentence='On tests-frozen exit 2 the check could not answer, so **bail** as a system failure, never a REJECT, and launch no verifier.'
wrong_test_sentence='A revise of green whose leaf reports `WRONG_TEST: <why>` is exempt from the `SUITE:` line and reaches the same outcome a develop-green `WRONG_TEST:` stop does: it keeps its main outcome, a verify-green REJECT, never a `report-missing` bail.'
pin_record_sentence='A `⟦replaces-case⟧` step skips verify-red, so on that verify-pin PASS first run `$S/tests-frozen.sh record '"$record_arg"' <test-path>` to record its replacement cases before the deletion green checks them; tests-frozen exit 2 is a bail.'

numbered_section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside { printf "%d\t%s\n", NR, $0 }' \
    "$skill_path"
}

joined_section() {
  numbered_section "$1" | cut -f 2- | sed 's/^[[:space:]]*//' | tr '\n' ' '
}

lines_matching() {
  numbered_section "$1" | P="$2" awk -F '\t' '$2 ~ ENVIRON["P"] { print $1 }'
}

any_between() {
  local n
  for n in $1; do
    ((n > $2 && n < $3)) && return 0
  done
  return 1
}

frozen_sentences() {
  numbered_section "$1" | cut -f 2- |
    awk '/^[[:space:]]*```/ { fence = !fence; next } !fence' |
    plain --join | sed 's/\. /.\n/g' | grep -F 'tests-frozen' || true
}

check_handling() {
  local where="$1" sentences="$2"
  grep -qE 'exit 1|exits 1' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen branches on check exit 1")
  grep -qF 'verify-green.reason' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen writes the changed file to .tdd/verify-green.reason")
  grep -qE 'nam(e|es|ing) the (changed |test )?file' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen says the reason names the file")
  grep -qF 'revise_budget' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen says a changed test spends REVISE_BUDGET")
  grep -qE 'no verifier|not launch|without launching' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen says no verifier is launched for that attempt")
  grep -qE 'exit 0|exits 0' <<<"$sentences" ||
    problems+=("$where: no sentence naming tests-frozen says check exit 0 launches the verifier as before")
}

name="#1586: $skill_md's Red section runs tests-frozen.sh record after verify-red's verdict"
problems=()
red_wait="$(lines_matching '#### Red' 'wait-leaf\.sh verdict-red' | sed -n 1p)"
red_record="$(lines_matching '#### Red' 'tests-frozen\.sh record')"
if [[ -z "$red_record" ]]; then
  problems+=("$skill_md's Red section never runs tests-frozen.sh record, so nothing holds the red test as it stood when verify-red passed")
elif ! any_between "$red_record" "${red_wait:-0}" 999999; then
  problems+=("$skill_md's Red section runs tests-frozen.sh record only before verify-red's verdict (wait-leaf.sh verdict-red at line ${red_wait:-?}), not once it PASSes")
fi
report "$name"

name="#1586: $skill_md's Green section runs tests-frozen.sh check after develop-green and before verify-green, rejecting on exit 1 with the file named, spending REVISE_BUDGET and launching no verifier"
problems=()
green_wait="$(lines_matching '#### Green' 'wait-leaf\.sh develop-green' | sed -n 1p)"
green_verify="$(lines_matching '#### Green' 'supervise\.sh verdict-green' | sed -n 1p)"
green_check="$(lines_matching '#### Green' 'tests-frozen\.sh check')"
if [[ -z "$green_check" ]]; then
  problems+=("$skill_md's Green section never runs tests-frozen.sh check, so a green that edits the frozen test reaches verify-green unchallenged")
elif ! any_between "$green_check" "${green_wait:-0}" "${green_verify:-0}"; then
  problems+=("$skill_md's Green section runs tests-frozen.sh check, but not between the develop-green wait (line ${green_wait:-?}) and the verify-green launch (line ${green_verify:-?})")
fi
check_handling "$skill_md's Green section" "$(frozen_sentences '#### Green')"
report "$name"

name="#1586: $skill_md's Revising on a REJECT runs tests-frozen.sh check after a revise-green and before its re-verify, rejecting on exit 1 with the file named, spending REVISE_BUDGET and launching no verifier"
problems=()
revise_heading='## Revising on a REJECT'
revise_wait="$(lines_matching "$revise_heading" 'wait-leaf\.sh revise-<phase>-<k>' | sed -n 1p)"
revise_verify="$(lines_matching "$revise_heading" 'supervise\.sh verdict-<phase>' | sed -n 1p)"
revise_check="$(lines_matching "$revise_heading" 'tests-frozen\.sh check')"
revise_sentences="$(frozen_sentences "$revise_heading")"
if [[ -z "$revise_check" ]]; then
  problems+=("$skill_md's Revising on a REJECT never runs tests-frozen.sh check, so a revise-green that edits the frozen test reaches verify-green unchallenged")
elif ! any_between "$revise_check" "${revise_wait:-0}" "${revise_verify:-0}"; then
  problems+=("$skill_md's Revising on a REJECT runs tests-frozen.sh check, but not between the revise leaf's wait (line ${revise_wait:-?}) and its re-verify launch (line ${revise_verify:-?})")
fi
grep -qF 'green' <<<"$revise_sentences" ||
  problems+=("$skill_md's Revising on a REJECT: no sentence naming tests-frozen scopes the check to a revise of green")
check_handling "$skill_md's Revising on a REJECT" "$revise_sentences"
report "$name"

name="#1586: $skill_md's every tests-frozen.sh record and check names the step's record by tests-frozen.sh path over the step text, and the Red section defines that key verbatim"
problems=()
mapfile -t frozen_lines < <(grep -nE 'tests-frozen\.sh (record|check)' "$skill_path")
((${#frozen_lines[@]} > 0)) ||
  problems+=("$skill_md has no tests-frozen.sh record or check command to read")
for line in "${frozen_lines[@]}"; do
  [[ "$line" == *"tests-frozen.sh record $record_arg"* || "$line" == *"tests-frozen.sh check $record_arg"* ]] ||
    problems+=("$skill_md:${line%%:*} runs tests-frozen.sh record or check without $record_arg as its record file")
done
grep -nF 'tests-frozen-<step>' "$skill_path" > /dev/null &&
  problems+=("$skill_md still names .tdd/tests-frozen-<step>.record, a filename built from the step text itself")
[[ "$(joined_section '#### Red')" == *"$key_sentence"* ]] ||
  problems+=("$skill_md's Red section does not define the record key verbatim: $key_sentence")
report "$name"

name="#1586: $skill_md's Revising on a REJECT runs tests-frozen.sh record to the step's own record once a revised red's re-verify PASSes"
problems=()
reverify_wait="$(lines_matching "$revise_heading" 'wait-leaf\.sh verdict-<phase>' | sed -n 1p)"
revise_record="$(lines_matching "$revise_heading" 'tests-frozen\.sh record')"
if [[ -z "$revise_record" ]]; then
  problems+=("$skill_md's Revising on a REJECT never runs tests-frozen.sh record, so a red that passes only after a revise leaves its step with no record to check green against")
else
  any_between "$revise_record" "${reverify_wait:-0}" 999999 ||
    problems+=("$skill_md's Revising on a REJECT runs tests-frozen.sh record, but not after the re-verify's wait (line ${reverify_wait:-?}), so it does not follow a PASS")
  grep -qF "tests-frozen.sh record $record_arg" <<<"$(numbered_section "$revise_heading" | cut -f 2-)" ||
    problems+=("$skill_md's Revising on a REJECT: tests-frozen.sh record does not name the step's own record path")
  grep -qiE 'red' <<<"$(frozen_sentences "$revise_heading" | grep -F record)" ||
    problems+=("$skill_md's Revising on a REJECT: no sentence naming tests-frozen record scopes it to a revise of red")
fi
report "$name"

name="#1586: $skill_md's Red section says a ⟦suite-repair⟧ or ⟦ci-repair⟧ step is never frozen, and a ⟦ci-repair⟧ step records nothing before its green, verbatim"
problems=()
red_text="$(joined_section '#### Red')"
[[ "$red_text" == *"$repair_sentence"* ]] ||
  problems+=("$skill_md's Red section does not say repair-marked steps are never frozen verbatim: $repair_sentence")
[[ "$red_text" == *"$ci_sentence"* ]] ||
  problems+=("$skill_md's Red section does not say a ⟦ci-repair⟧ step records nothing before its green verbatim: $ci_sentence")
grep -F 'ci-repair' <<<"$(frozen_sentences '#### Red')" | grep -F 'tests-frozen.sh record' > /dev/null &&
  problems+=("$skill_md's Red section still runs tests-frozen.sh record for a ⟦ci-repair⟧ step")
report "$name"

name="#1586: $skill_md's Green section and Revising on a REJECT handle tests-frozen.sh check exit 2 as a system-failure bail, never a REJECT, launching no verifier, in one verbatim sentence each"
problems=()
for where in '#### Green' "$revise_heading"; do
  [[ "$(joined_section "$where")" == *"$exit2_sentence"* ]] ||
    problems+=("$skill_md's $where does not carry the check exit 2 handling verbatim: $exit2_sentence")
done
report "$name"

name="#1586: $skill_md's Revising on a REJECT gives a revise-green WRONG_TEST: report the outcome Green gives a develop-green WRONG_TEST: stop, a verify-green REJECT and never a report-missing bail, verbatim"
problems=()
green_outcome="$(numbered_section '#### Green' | cut -f 2- | plain --join | sed 's/\. /.\n/g' | grep -F 'looks wrong' || true)"
grep -qF 'verify-green reject' <<<"$green_outcome" ||
  problems+=("$skill_md's Green section: no sentence about a green that stops because the test looks wrong names a verify-green REJECT, so there is no outcome to match")
[[ "$(joined_section "$revise_heading")" == *"$wrong_test_sentence"* ]] ||
  problems+=("$skill_md's Revising on a REJECT does not give a revise-green WRONG_TEST: report its outcome verbatim: $wrong_test_sentence")
report "$name"

name="#1586: $skill_md's Already satisfied — the pin records a ⟦replaces-case⟧ step's tests at its verify-pin PASS, before the deletion green is launched"
problems=()
pin_heading='## Already satisfied — the pin'
pin_text="$(joined_section "$pin_heading")"
if [[ "$pin_text" != *"$pin_record_sentence"* ]]; then
  problems+=("$skill_md's $pin_heading does not record a ⟦replaces-case⟧ step's tests at its verify-pin PASS verbatim: $pin_record_sentence")
else
  before_green="${pin_text%%launch a green leaf exactly as*}"
  [[ "$before_green" == *"$pin_record_sentence"* ]] ||
    problems+=("$skill_md's $pin_heading records the ⟦replaces-case⟧ step's tests only after it launches the deletion green")
fi
report "$name"

name="#1621: $skill_md's Green section routes a WRONG_TEST: report through wrong-test-route.sh: exit 0 writes no revise mark, spends no REVISE_BUDGET and launches a red-contradicted red through the supervisor, verifies it with verify-red, re-records both test paths with tests-frozen.sh record --step and retries green; exit 3 takes the revise path; exit 2 bails"
problems=()
route_text="$(joined_section '#### Green')"
route_text="${route_text#*'A green report carrying `WRONG_TEST:`'}"
route_text="${route_text%%'tests-frozen.sh check'*}"
[[ "$route_text" == *'wrong-test-route.sh'* ]] ||
  problems+=("$skill_md's Green section does not route a WRONG_TEST: report through wrong-test-route.sh")
[[ "$route_text" == *'supervise.sh'*'red-contradicted'* || "$route_text" == *'red-contradicted'*'supervise.sh'* ]] ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not launch the red-contradicted red through supervise.sh")
[[ "$route_text" == *'verify-red'* ]] ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not verify the contradicted red with verify-red")
[[ "$route_text" == *'tests-frozen.sh record --step'* ]] ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not re-record the step's frozen tests with tests-frozen.sh record --step")
grep -qiE 'no `?revise`? mark' <<<"$route_text" ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not say exit 0 writes no revise mark")
grep -qiE 'no (revise|REVISE_BUDGET)|spends? no' <<<"$route_text" ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not say exit 0 spends no REVISE_BUDGET attempt")
grep -qiE 'retr(y|ies) green' <<<"$route_text" ||
  problems+=("$skill_md's Green WRONG_TEST: routing does not retry green after the red")
report "$name"

finish
