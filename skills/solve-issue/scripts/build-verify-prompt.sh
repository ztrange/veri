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
#     phase = red | green | refactor
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase or a missing template/spec file.
set -euo pipefail

phase="${1:?usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]}"
spec_file="${2:?missing <issue-spec-file>}"
test_path="${3:?missing <test-path>}"
target="${4:-the target test}"

case "$phase" in
  red|green|refactor) ;;
  *) echo "build-verify-prompt: unknown phase '$phase' (want red|green|refactor)" >&2; exit 2 ;;
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

# Literal substitution via bash parameter expansion — no sed, so &, \, / and {} in the
# spec are carried through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"

printf '%s\n' "$out"
