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
#     phase = red | green | refactor | pin | plan | rebase | transform
#              for plan the third positional names the proposed ledger, not a test;
#              for transform it names the step's predicate record, and the fourth is the
#              step's base sha
#     --step = the ledger's own line for the step under judgement: it scopes the
#              verdict to that criterion, and carries the conductor's words, not the leaf's
#     --fast-cmd = the fast tier's test command, required for green and refactor:
#              verify-green and verify-refactor run it plus the affected suites, and a verifier in a target repository has
#              no detect-test-command.sh of its own to ask. It is a command the conductor
#              detected, never anything the developer leaf wrote.
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase, a missing template/spec file, or a green or refactor call without --fast-cmd.
set -euo pipefail

# hazard: bash 5.2's patsub_replacement makes an unescaped & in a ${var//…/…} replacement the matched text; off, every value is literal.
shopt -u patsub_replacement 2>/dev/null || true

USAGE="usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"

step="" fast_cmd=""
while :; do
  case "${1:-}" in
    --step|--fast-cmd)
      [[ -n "${2:-}" ]] || { echo "build-verify-prompt: $1 needs a value" >&2; echo "$USAGE" >&2; exit 2; }
      case "$1" in
        --step) step="$2" ;;
        *) fast_cmd="$2" ;;
      esac ;;
    *) break ;;
  esac
  shift 2
done

# hazard: `${N:?}` would abort with status 1, the code reserved for an answer.
[[ $# -ge 3 && -n "$1" && -n "$2" && -n "$3" ]] || { echo "$USAGE" >&2; exit 2; }
phase="$1"
spec_file="$2"
test_path="$3"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor|pin|plan|rebase|transform) ;;
  *) echo "build-verify-prompt: unknown phase '$phase' (want red|green|refactor|pin|plan|rebase|transform)" >&2; exit 2 ;;
esac

if [[ ( "$phase" == green || "$phase" == refactor ) && -z "$fast_cmd" ]]; then
  echo "build-verify-prompt: $phase needs --fast-cmd '<fast-tier test command>'" >&2
  exit 2
fi

need_sha() {
  [[ "$2" =~ ^[0-9a-f]{7,40}$ ]] && return 0
  echo "build-verify-prompt: $phase needs $1 as 7-40 lowercase hex characters, got '$2'" >&2
  exit 2
}

base_sha="${4:-}"
if [[ "$phase" == refactor || "$phase" == transform ]]; then
  need_sha '<base-sha>' "$base_sha"
fi

onto_sha="" pre_rebase_sha=""
if [[ "$phase" == rebase ]]; then
  onto_sha="$3" pre_rebase_sha="${4:-}"
  for sha in "$onto_sha" "$pre_rebase_sha"; do
    need_sha '<onto-sha> <pre-rebase-sha>' "$sha"
  done
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/verify-$phase.md"
shared_file="$HERE/prompts/_shared.md"
# hazard: `||` on `source`, or a missing lib file dies under set -e with 1 instead of 2.
source "$HERE/lib/bug-section.sh" \
  || { echo "build-verify-prompt: cannot read '$HERE/lib/bug-section.sh'" >&2; exit 2; }
bug_file=""
if spec_has_bug_section "$spec_file"; then
  bug_file="$HERE/prompts/_verify-red-bug.md"
fi
refactor_plan_file=""
if [[ "$phase" == plan ]] && grep -qE '^## Refactor[[:space:]]*$' "$spec_file" 2>/dev/null; then
  refactor_plan_file="$HERE/prompts/_verify-plan-refactor.md"
fi

# hazard: `cat` on an unreadable file under set -e would exit 1, the code reserved for an answer.
readable=("$tpl_file" "$shared_file" "$spec_file")
if [[ -n "$bug_file" ]]; then
  readable+=("$bug_file")
fi
if [[ -n "$refactor_plan_file" ]]; then
  readable+=("$refactor_plan_file")
fi
if [[ "$phase" == plan ]]; then
  readable+=("$test_path")
fi
for f in "${readable[@]}"; do
  [[ -r "$f" ]] || { echo "build-verify-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"
bug_reproduction=""
if [[ -n "$bug_file" ]]; then bug_reproduction="$(cat "$bug_file")"; fi
refactor_plan=""
if [[ -n "$refactor_plan_file" ]]; then refactor_plan="$(cat "$refactor_plan_file")"; fi
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
out="${out//\{\{LEDGER\}\}/$ledger}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{BASE_SHA\}\}/$base_sha}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
out="${out//\{\{ONTO_SHA\}\}/$onto_sha}"
out="${out//\{\{PRE_REBASE_SHA\}\}/$pre_rebase_sha}"
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"

printf '%s\n' "$out"
