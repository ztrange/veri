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
#   build-develop-prompt.sh green    <issue-spec-file> <step-text> <test-cmd> <test-path> <target>
#   build-develop-prompt.sh refactor <issue-spec-file> <step-text> <test-cmd> <touched-files>
#
# Prints the assembled prompt on stdout (feed it to supervise.sh). Exit 2 on an unknown
# phase or a missing template/spec file — never a partial prompt.
set -euo pipefail

phase="${1:?usage: build-develop-prompt.sh red|green|refactor <issue-spec-file> <step-text> <test-cmd> ...}"
spec_file="${2:?missing <issue-spec-file>}"
step="${3:?missing <step-text>}"
test_cmd="${4:?missing <test-cmd>}"

# Each phase takes its own extra positionals past the three every phase shares. Red has
# none — it is the phase that writes the test, so there is nothing yet to name. Variables
# a phase does not take stay empty, and their placeholders expand to nothing.
case "$phase" in
  red) test_path="" target="" touched="" ;;
  green)
    test_path="${5:?missing <test-path>}"
    target="${6:?missing <target-test>}"
    touched=""
    ;;
  refactor)
    test_path="" target=""
    touched="${5:?missing <touched-files>}"
    ;;
  *) echo "build-develop-prompt: unknown phase '$phase' (want red|green|refactor)" >&2; exit 2 ;;
esac

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/develop-$phase.md"
shared_file="$HERE/prompts/_develop-shared.md"
for f in "$tpl_file" "$shared_file" "$spec_file"; do
  [[ -r "$f" ]] || { echo "build-develop-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"

# Literal substitution via bash parameter expansion — no sed, so &, \, / and {} in the
# spec or the step text are carried through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{STEP\}\}/$step}"
out="${out//\{\{TEST_CMD\}\}/$test_cmd}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{TOUCHED_FILES\}\}/$touched}"

printf '%s\n' "$out"
