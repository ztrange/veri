#!/usr/bin/env bash
# Unit test for the tests-frozen record and check in skills/tdd/SKILL.md, read as text.
#
# Contract under test:
#   SKILL.md's Red section runs `tests-frozen.sh record` once verify-red PASSes; it runs
#   `tests-frozen.sh check` before every verify-green — in Green between the develop-green wait
#   and the verify-green launch, and in *Revising on a REJECT* between the revise-green wait and
#   its re-verify; on check exit 1 it writes a reason naming the file to
#   .tdd/verify-green.reason, treats the attempt as a REJECT that spends REVISE_BUDGET and
#   launches no verifier; on exit 0 the verifier is launched as before. Only sentences naming
#   tests-frozen count, so text the sections already held cannot satisfy a case.
#
# Run: scripts/tests/skill-tests-frozen.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"

numbered_section() {
  awk -v h="$1" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside { printf "%d\t%s\n", NR, $0 }' \
    "$skill_path"
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

name="#1586: $skill_md's every tests-frozen.sh record and check names a record file that carries the step, so one step's check never reads another step's record"
problems=()
mapfile -t frozen_calls < <(grep -oE 'tests-frozen\.sh (record|check) [^ ]+' "$skill_path")
((${#frozen_calls[@]} > 0)) ||
  problems+=("$skill_md has no tests-frozen.sh record or check command to read")
for call in "${frozen_calls[@]}"; do
  [[ "${call##* }" == *'<step'* ]] ||
    problems+=("$skill_md runs '$call', a record path shared by every step, so a later step's check compares against the record an earlier step made")
done
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
  grep -qE 'tests-frozen\.sh record [^ ]*<step' <<<"$(numbered_section "$revise_heading" | cut -f 2-)" ||
    problems+=("$skill_md's Revising on a REJECT: tests-frozen.sh record does not name the step's own record path")
  grep -qiE 'red' <<<"$(frozen_sentences "$revise_heading" | grep -F record)" ||
    problems+=("$skill_md's Revising on a REJECT: no sentence naming tests-frozen record scopes it to a revise of red")
fi
report "$name"

name="#1586: $skill_md's Red section has a ⟦ci-repair⟧ step whose Red reports PASSES, and so skips verify-red, run tests-frozen.sh record to the step's own record before its green"
problems=()
ci_sentences="$(frozen_sentences '#### Red' | grep -F 'ci-repair' || true)"
if [[ -z "$ci_sentences" ]]; then
  problems+=("$skill_md's Red section: no sentence naming tests-frozen and ⟦ci-repair⟧, so a ci-repair step that skips verify-red reaches green with no record to check")
else
  grep -qE 'tests-frozen\.sh record [^ ]*<step' <<<"$ci_sentences" ||
    problems+=("$skill_md's Red section: the ⟦ci-repair⟧ sentence naming tests-frozen does not run record to the step's own record path")
  grep -qiE 'before (its |the )?green' <<<"$ci_sentences" ||
    problems+=("$skill_md's Red section: the ⟦ci-repair⟧ sentence naming tests-frozen does not say the record is made before green")
fi
report "$name"

finish
