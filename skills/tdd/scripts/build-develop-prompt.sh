#!/usr/bin/env bash
# build-develop-prompt.sh — assemble a DEVELOPER leaf's prompt for one cycle phase.
#
# The mirror of build-verify-prompt.sh, and its opposite in emphasis: the verifier builder
# is defined by what it cannot carry (no rationale parameter, so blindness is structural),
# this one by what it must carry. Every run of a phase sends the same instructions from a
# versioned template; the conductor supplies only the variables. That is what removes the
# run-to-run variance of a prompt improvised from prose each cycle.
#
# Usage:
#   build-develop-prompt.sh red      <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh green    <issue-spec-file> <step-text> <test-cmd> <test-path> <target> <fast-cmd>
#   build-develop-prompt.sh refactor <issue-spec-file> <step-text> <test-cmd> <touched-files>
#   build-develop-prompt.sh cover     <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh transform <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh diff      <issue-spec-file> <step-text> <test-cmd> <fast-cmd>
#   build-develop-prompt.sh structural <issue-spec-file> <candidate> <test-cmd> <issue-touched-files>
#   build-develop-prompt.sh predicate <issue-spec-file> <candidate> <test-cmd> <issue-touched-files>
#   build-develop-prompt.sh revise <phase> <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh revise diff <issue-spec-file> <step-text> <test-cmd> <reason-file> <fast-cmd>
#   build-develop-prompt.sh exhausted <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh reconcile <issue-spec-file> <step-text> <test-cmd> <branch> <remote-sha>
#   build-develop-prompt.sh over-budget <issue-spec-file> <step-text> <test-cmd> <spent> <budget>
#   build-develop-prompt.sh rebase <issue-spec-file> <step-text> <test-cmd> <onto-sha> <pre-rebase-sha> <conflicting-files>
#
# `refactor` also reads VERI_REFACTOR_BUDGET (default 5) from the environment, the number of
# transforms the leaf may apply.
#
# Prints the assembled prompt on stdout (feed it to supervise.sh). Exit 2 on an unknown
# phase or a missing template/spec file — never a partial prompt.
set -euo pipefail

# hazard: bash 5.2's patsub_replacement makes an unescaped & in a ${var//…/…} replacement the matched text; off, every value is literal.
shopt -u patsub_replacement 2>/dev/null || true

phases="red|green|refactor|cover|transform|diff|structural|predicate|revise|reconcile|exhausted|over-budget|rebase"
revise_phases="red|green|refactor|diff"
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="build-develop-prompt.sh: usage: $phases <issue-spec-file> <step-text> <test-cmd> ..."
(( $# >= 1 )) || refuse
phase="$1"

case "$phase" in
  red) want=4 ;;
  green) want=7 ;;
  refactor) want=5 ;;
  cover|transform) want=4 ;;
  diff) want=5 ;;
  structural|predicate) want=5 ;;
  revise) want=6 ;;
  reconcile) want=6 ;;
  exhausted) want=5 ;;
  over-budget) want=6 ;;
  rebase) want=7 ;;
  *) refuse "build-develop-prompt.sh: unknown phase '$phase' (want $phases)" ;;
esac

(( $# >= want )) || refuse "build-develop-prompt: $phase needs $want arguments, got $#"

# hazard: `${N:?}` would abort with status 1, the code reserved for an answer.
need() {
  [[ -n "$2" ]] || refuse "build-develop-prompt: missing $3"
  printf -v "$1" '%s' "$2"
}

revised_phase=""
if [[ "$phase" == "revise" ]]; then
  need revised_phase "${2:-}" '<phase> being revised'
  [[ "$revised_phase" =~ ^($revise_phases)$ ]] ||
    refuse "build-develop-prompt.sh: unknown phase to revise '$revised_phase' (want $revise_phases)"
  shift
fi

need spec_file "${2:-}" '<issue-spec-file>'
need step "${3:-}" '<step-text>'
need test_cmd "${4:-}" '<test-cmd>'

test_path="" target="" fast_cmd="" touched="" reason_file="" refactor_budget="" branch="" remote_sha="" spent="" budget="" onto_sha="" pre_rebase_sha="" conflicting=""
case "$phase" in
  red|cover|transform) ;;
  diff) need fast_cmd "${5:-}" '<fast-cmd>' ;;
  green)
    need test_path "${5:-}" '<test-path>'
    need target "${6:-}" '<target-test>'
    need fast_cmd "${7:-}" '<fast-cmd>'
    ;;
  structural|predicate)
    need touched "${5:-}" '<issue-touched-files>'
    ;;
  refactor)
    need touched "${5:-}" '<touched-files>'
    refactor_budget="${VERI_REFACTOR_BUDGET:-5}"
    ;;
  revise|exhausted)
    need reason_file "${5:-}" '<reason-file>'
    [[ "$revised_phase" == diff ]] && fast_cmd="${6:-}"
    ;;
  reconcile)
    need branch "${5:-}" '<branch>'
    need remote_sha "${6:-}" '<remote-sha>'
    ;;
  rebase)
    need onto_sha "${5:-}" '<onto-sha>'
    need pre_rebase_sha "${6:-}" '<pre-rebase-sha>'
    need conflicting "${7:-}" '<conflicting-files>'
    ;;
  over-budget)
    need spent "${5:-}" '<spent>'
    need budget "${6:-}" '<budget>'
    for figure in "<spent>=$spent" "<budget>=$budget"; do
      [[ "${figure#*=}" =~ ^[0-9]+(\.[0-9]+)?$ ]] \
        || refuse "build-develop-prompt: ${figure%%=*} '${figure#*=}' is not a non-negative decimal number"
    done
    ;;
esac

tpl_file="$HERE/prompts/develop-$phase.md"
[[ "$revised_phase" == diff ]] && tpl_file="$HERE/prompts/develop-revise-diff.md"
shared_file="$HERE/prompts/_develop-shared.md"

# hazard: `||` on `source`, or a missing lib file dies under set -e with 1 instead of 2.
source "$HERE/lib/bug-section.sh" \
  || { echo "build-develop-prompt: cannot read '$HERE/lib/bug-section.sh'" >&2; exit 2; }
source "$HERE/lib/include.sh" \
  || { echo "build-develop-prompt: cannot read '$HERE/lib/include.sh'" >&2; exit 2; }
bug_file=""
if spec_has_bug_section "$spec_file"; then
  bug_file="$HERE/prompts/_develop-red-bug.md"
fi

green_partial() {
  local file=""
  if [[ ( "$phase" == "green" || "$revised_phase" == "green" ) && "$step" == *"$2"* ]]; then
    file="$HERE/prompts/$3"
  fi
  printf -v "$1" '%s' "$file"
}
green_partial replaces_file "⟦replaces-case⟧" _develop-green-replaces-case.md
green_partial suite_repair_file "⟦suite-repair⟧" _develop-green-suite-repair.md

for f in "$tpl_file" "$shared_file" "$spec_file" "$reason_file" "$bug_file" "$replaces_file" "$suite_repair_file"; do
  [[ -n "$f" ]] || continue
  [[ -r "$f" ]] || { echo "build-develop-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
resolve_includes tpl "$HERE/prompts" || exit 2
shared="$(cat "$shared_file")"
resolve_includes shared "$HERE/prompts" || exit 2
spec="$(cat "$spec_file")"
optional() {
  local content=""
  if [[ -n "$2" ]]; then content="${3:-}$(cat "$2")"; fi
  printf -v "$1" '%s' "$content"
}
optional reason "$reason_file"
optional replaces_case "$replaces_file" $'\n\n'
optional suite_repair "$suite_repair_file" $'\n\n'
resolve_includes replaces_case "$HERE/prompts" || exit 2
resolve_includes suite_repair "$HERE/prompts" || exit 2
optional bug_reproduction "$bug_file"

out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{BUG_REPRODUCTION\}\}/$bug_reproduction}"
out="${out//\{\{REPLACES_CASE\}\}/$replaces_case}"
out="${out//\{\{SUITE_REPAIR\}\}/$suite_repair}"
out="${out//\{\{STEP\}\}/$step}"
out="${out//\{\{TEST_CMD\}\}/$test_cmd}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"
out="${out//\{\{TOUCHED_FILES\}\}/$touched}"
out="${out//\{\{REFACTOR_BUDGET\}\}/$refactor_budget}"
out="${out//\{\{REVISE_PHASE\}\}/$revised_phase}"
out="${out//\{\{REJECTION_REASON\}\}/$reason}"
out="${out//\{\{BRANCH\}\}/$branch}"
out="${out//\{\{REMOTE_SHA\}\}/$remote_sha}"
out="${out//\{\{SPENT\}\}/$spent}"
out="${out//\{\{BUDGET\}\}/$budget}"
out="${out//\{\{ONTO_SHA\}\}/$onto_sha}"
out="${out//\{\{PRE_REBASE_SHA\}\}/$pre_rebase_sha}"
out="${out//\{\{CONFLICTING_FILES\}\}/$conflicting}"

printf '%s\n' "$out"
