#!/usr/bin/env bash
# build-verify-prompt.sh — assemble a BLIND verifier leaf's prompt for one cycle phase.
#
# The verifier is blind by construction (ADR-0003): this builder's only inputs are the
# issue's behavior spec and the test under review. It has NO parameter for the developer
# leaf's rationale, so the author's reasoning physically cannot reach the verifier — the
# blindness guarantee is structural, not a matter of the conductor remembering to omit it.
#
# Usage:
#   build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]
#     phase = red | green | refactor | pin
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase or a missing template/spec file.
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

phase="${1:?usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]}"
spec_file="${2:?missing <issue-spec-file>}"
test_path="${3:?missing <test-path>}"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor|pin) ;;
  *) echo "build-verify-prompt: unknown phase '$phase' (want red|green|refactor|pin)" >&2; exit 2 ;;
esac

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/verify-$phase.md"
shared_file="$HERE/prompts/_shared.md"
for f in "$tpl_file" "$shared_file" "$spec_file"; do
  [[ -r "$f" ]] || { echo "build-verify-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"

# Literal substitution via bash parameter expansion — no sed, and with the
# patsub_replacement guard above holding, so &, \, / and {} in the spec are carried
# through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"

printf '%s\n' "$out"
