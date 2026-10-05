#!/usr/bin/env bash
# build-verify-prompt.sh — assemble a BLIND verifier leaf's prompt for one cycle phase.
#
# The verifier is blind by construction (ADR-0003): this builder's only inputs are the
# issue's behavior spec and the test under review. It has NO parameter for the developer
# leaf's rationale, so the author's reasoning physically cannot reach the verifier — the
# blindness guarantee is structural, not a matter of the conductor remembering to omit it.
#
# Usage:
#   build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#   build-verify-prompt.sh rebase <issue-spec-file> <onto-sha> <pre-rebase-sha>
#   build-verify-prompt.sh --step '<STEP>' --fast-cmd '<CMD>' diff <issue-spec-file> <branch-base-sha> <step-base-sha>
#     phase = red | green | refactor | pin | plan | rebase | transform | diff
#              for plan the third positional names the proposed ledger, not a test;
#              for transform it names the step's predicate record, and the fourth is the
#              step's base sha
#     --step = the ledger's own line for the step under judgement: it scopes the
#              verdict to that criterion, and carries the conductor's words, not the leaf's
#     --fast-cmd = the fast tier's test command, required for green, refactor and diff:
#              verify-green and verify-refactor run it plus the affected suites, and a verifier in a target repository has
#              no detect-test-command.sh of its own to ask. It is a command the conductor
#              detected, never anything the developer leaf wrote.
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase, a missing template/spec file, or a green, refactor or diff call without --fast-cmd.
set -euo pipefail

# hazard: bash 5.2's patsub_replacement makes an unescaped & in a ${var//…/…} replacement the matched text; off, every value is literal.
shopt -u patsub_replacement 2>/dev/null || true

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
USAGE="usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"

step="" fast_cmd=""
while :; do
  case "${1:-}" in
    --step|--fast-cmd)
      [[ -n "${2:-}" ]] || refuse "build-verify-prompt: $1 needs a value"
      case "$1" in
        --step) step="$2" ;;
        *) fast_cmd="$2" ;;
      esac ;;
    *) break ;;
  esac
  shift 2
done

# hazard: `${N:?}` would abort with status 1, the code reserved for an answer.
require_args 3 "$@"
(( $# <= 4 )) || refuse "build-verify-prompt: too many arguments"
phase="$1"
spec_file="$2"
test_path="$3"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor|pin|plan|rebase|transform|diff) ;;
  *) refuse "build-verify-prompt: unknown phase '$phase' (want red|green|refactor|pin|plan|rebase|transform|diff)" ;;
esac

if [[ ( "$phase" == green || "$phase" == refactor || "$phase" == diff ) && -z "$fast_cmd" ]]; then
  refuse "build-verify-prompt: $phase needs --fast-cmd '<fast-tier test command>'"
fi

need_sha() {
  [[ "$2" =~ ^[0-9a-f]{7,40}$ ]] && return 0
  refuse "build-verify-prompt: $phase needs $1 as 7-40 lowercase hex characters, got '$2'"
}

base_sha="${4:-}" step_base_sha=""
if [[ "$phase" == diff ]]; then
  [[ -n "$step" ]] || refuse "build-verify-prompt: diff needs --step '<STEP>'"
  base_sha="$3" step_base_sha="${4:-}"
  need_sha '<step-base-sha>' "$step_base_sha"
fi
if [[ "$phase" == refactor || "$phase" == transform || "$phase" == diff ]]; then
  need_sha '<base-sha>' "$base_sha"
fi

onto_sha="" pre_rebase_sha=""
if [[ "$phase" == rebase ]]; then
  onto_sha="$3" pre_rebase_sha="${4:-}"
  for sha in "$onto_sha" "$pre_rebase_sha"; do
    need_sha '<onto-sha> <pre-rebase-sha>' "$sha"
  done
fi

tpl_file="$HERE/prompts/verify-$phase.md"
shared_file="$HERE/prompts/_shared.md"
# hazard: `||` on `source`, or a missing lib file dies under set -e with 1 instead of 2.
source "$HERE/lib/bug-section.sh" \
  || { echo "build-verify-prompt: cannot read '$HERE/lib/bug-section.sh'" >&2; exit 2; }
source "$HERE/lib/include.sh" \
  || { echo "build-verify-prompt: cannot read '$HERE/lib/include.sh'" >&2; exit 2; }
bug_file=""
if spec_has_bug_section "$spec_file"; then
  bug_file="$HERE/prompts/_verify-red-bug.md"
fi
refactor_plan_file=""
if [[ "$phase" == plan ]] && grep -qE '^## Refactor[[:space:]]*$' "$spec_file" 2>/dev/null; then
  refactor_plan_file="$HERE/prompts/_verify-plan-refactor.md"
fi

replaces_file=""
suite_repair_file=""
if [[ "$phase" == green ]]; then
  if [[ "$step" == *"⟦replaces-case⟧"* ]]; then
    replaces_file="$HERE/prompts/_verify-green-replaces-case.md"
  fi
  if [[ "$step" == *"⟦suite-repair⟧"* ]]; then
    suite_repair_file="$HERE/prompts/_verify-green-suite-repair.md"
  fi
fi

# hazard: `cat` on an unreadable file under set -e would exit 1, the code reserved for an answer.
readable=("$tpl_file" "$shared_file" "$spec_file")
for f in "$replaces_file" "$suite_repair_file" "$bug_file" "$refactor_plan_file"; do
  if [[ -n "$f" ]]; then readable+=("$f"); fi
done
if [[ "$phase" == plan ]]; then
  readable+=("$test_path")
fi
for f in "${readable[@]}"; do
  [[ -r "$f" ]] || { echo "build-verify-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
resolve_includes tpl "$HERE/prompts"
shared="$(cat "$shared_file")"
resolve_includes shared "$HERE/prompts"
spec="$(cat "$spec_file")"
optional() {
  local content=""
  if [[ -n "$2" ]]; then content="${3:-}$(cat "$2")"; fi
  printf -v "$1" '%s' "$content"
}
optional bug_reproduction "$bug_file"
optional refactor_plan "$refactor_plan_file"
optional replaces_case "$replaces_file" $'\n\n'
optional suite_repair "$suite_repair_file" $'\n\n'
resolve_includes replaces_case "$HERE/prompts"
resolve_includes suite_repair "$HERE/prompts"
ledger=""
if [[ "$phase" == plan ]]; then
  ledger="$(cat "$test_path")"
fi
step_block=""
if [[ -n "$step" ]]; then
  step_block="### The step under judgement

$step

Your verdict is about this criterion only: the spec below is the whole issue, and its other
criteria belong to other steps of the plan.

"
fi

out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{STEP\}\}/$step_block}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{BUG_REPRODUCTION\}\}/$bug_reproduction}"
out="${out//\{\{REFACTOR_PLAN\}\}/$refactor_plan}"
out="${out//\{\{REPLACES_CASE\}\}/$replaces_case}"
out="${out//\{\{SUITE_REPAIR\}\}/$suite_repair}"
out="${out//\{\{LEDGER\}\}/$ledger}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{BASE_SHA\}\}/$base_sha}"
out="${out//\{\{STEP_BASE_SHA\}\}/$step_base_sha}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
out="${out//\{\{ONTO_SHA\}\}/$onto_sha}"
out="${out//\{\{PRE_REBASE_SHA\}\}/$pre_rebase_sha}"
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"

printf '%s\n' "$out"
