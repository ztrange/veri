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
#     phase = red | green | refactor | pin | plan
#              for plan the third positional names the proposed ledger, not a test (#439)
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
#
# The call this script accepts, spelled once: both refusals below quote it back.
USAGE="usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]"

# Both flags take a value and neither may be given an empty one, so the refusal is written
# once for the pair and names whichever flag `$1` holds, the way verify.sh's own loop does —
# two spellings of it are two chances for the one a caller is shown to be the stale one. The
# inner `case` is then all that is left of what the two arms differ in: which name the value
# lands in.
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

# Every required positional is checked here, in one place, rather than each being read
# through a `${N:?…}` expansion: that expansion aborts the shell with status 1, the code
# reserved for an answer the call came back with, and a call missing an argument came back
# with none — which is exit 2 (#270). `$#` is asked first and `[[ … && … ]]` stops at the
# first false operand, so `$2` and `$3` are only read once they exist.
[[ $# -ge 3 && -n "$1" && -n "$2" && -n "$3" ]] || { echo "$USAGE" >&2; exit 2; }
phase="$1"
spec_file="$2"
test_path="$3"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor|pin|plan) ;;
  *) echo "build-verify-prompt: unknown phase '$phase' (want red|green|refactor|pin|plan)" >&2; exit 2 ;;
esac

# For plan, the third slot names the proposed ledger instead of a test under review (#439):
# the plan is this phase's subject, so its own text goes into the prompt — a verifier given
# only a path, in a target repository, would judge a file it was never handed.
ledger=""
if [[ "$phase" == plan ]]; then
  ledger="$(cat "$test_path")"
fi

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
out="${out//\{\{LEDGER\}\}/$ledger}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{BASE_SHA\}\}/$base_sha}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
# The wrapper every test-command run goes through (#373), named at an absolute path: a
# verifier works in the target repository, where the bare name resolves to nothing.
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"

printf '%s\n' "$out"
