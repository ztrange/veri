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
#     phase = red | green | refactor | pin
#     --step = the ledger's own line for the step under judgement (#223): it scopes the
#              verdict to that criterion, and carries the conductor's words, not the leaf's
#     --fast-cmd = the fast tier's test command (#341), required for green and refactor:
#              verify-green and verify-refactor run it plus the affected suites, and a verifier in a target repository has
#              no detect-test-command.sh of its own to ask. It is a command the conductor
#              detected, never anything the developer leaf wrote.
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase, a missing template/spec file, or a green or refactor call without --fast-cmd.
set -euo pipefail

# bash 5.2 added the `patsub_replacement` option and turned it ON by default: inside
# ${var//pattern/replacement}, an unescaped & in the *replacement* now expands to the text
# the pattern just matched, the way sed's & does. A spec reading "Frob & Nitz" would then
# reach the verifier as "Frob {{ISSUE_SPEC}} Nitz" — silently, with no error anywhere.
# Turning the option off restores the older meaning the substitutions below are written
# for: the replacement is literal text, so every value is carried through verbatim. This
# has to be a runtime guard rather than a fixed assumption because the same scripts run on
# macOS's bash 3.2, where `patsub_replacement` does not exist and `shopt -u` on an unknown
# option fails; there is nothing to disable there, so discarding that failure makes the
# line a no-op on 3.2 while it does the real work on 5.2+.
shopt -u patsub_replacement 2>/dev/null || true

# The step is a flag, never read from ambient VERI_STEP, so only the caller can scope a
# verdict. Without it the prompt is what it always was: a resumed run passes no step.
# --fast-cmd is a flag for the same reason: an ambient VERI_TEST_CMD is never read.
step="" fast_cmd=""
while :; do
  case "${1:-}" in
    --step) step="${2:?--step needs the step text}" ;;
    --fast-cmd) fast_cmd="${2:?--fast-cmd needs the command}" ;;
    *) break ;;
  esac
  shift 2
done

phase="${1:?usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]}"
spec_file="${2:?missing <issue-spec-file>}"
test_path="${3:?missing <test-path>}"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor|pin) ;;
  *) echo "build-verify-prompt: unknown phase '$phase' (want red|green|refactor|pin)" >&2; exit 2 ;;
esac

# Green and refactor name the fast command in their checks; without one the verifier would be
# told to run a command nobody named (#341).
if [[ ( "$phase" == green || "$phase" == refactor ) && -z "$fast_cmd" ]]; then
  echo "build-verify-prompt: $phase needs --fast-cmd '<fast-tier test command>'" >&2
  exit 2
fi

# For refactor, the 4th slot is the step's green commit, and only a sha may arrive in it:
# a slot that accepted free text would be a channel for the developer's rationale (#151).
base_sha="${4:-}"
if [[ "$phase" == refactor && ! "$base_sha" =~ ^[0-9a-f]{7,40}$ ]]; then
  echo "build-verify-prompt: refactor needs <base-sha> as 7-40 lowercase hex characters, got '$base_sha'" >&2
  exit 2
fi

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/verify-$phase.md"
shared_file="$HERE/prompts/_shared.md"
for f in "$tpl_file" "$shared_file" "$spec_file"; do
  [[ -r "$f" ]] || { echo "build-verify-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"
step_block=""
if [[ -n "$step" ]]; then
  step_block="### The step under judgement

$step

Your verdict is about this criterion only: the spec below is the whole issue, and its other
criteria belong to other steps of the plan.

"
fi

# Literal substitution via bash parameter expansion — no sed, and with the
# patsub_replacement guard above holding, so &, \, / and {} in the spec are carried
# through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{STEP\}\}/$step_block}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{BASE_SHA\}\}/$base_sha}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
# The wrapper every test-command run goes through (#373), named at an absolute path: a
# verifier works in the target repository, where the bare name resolves to nothing.
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"

printf '%s\n' "$out"
