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
#   build-develop-prompt.sh revise <phase> <issue-spec-file> <step-text> <test-cmd> <reason-file>
#
# Prints the assembled prompt on stdout (feed it to supervise.sh). Exit 2 on an unknown
# phase or a missing template/spec file — never a partial prompt.
set -euo pipefail

# bash 5.2 added the `patsub_replacement` option and turned it ON by default: inside
# ${var//pattern/replacement}, an unescaped & in the *replacement* now expands to the text
# the pattern just matched, the way sed's & does. A step reading "Frob & Nitz" would then
# reach the leaf as "Frob {{STEP}} Nitz" — silently, with no error anywhere. Turning the
# option off restores the older meaning the substitutions below are written for: the
# replacement is literal text, so every value is carried through verbatim. This has to be
# a runtime guard rather than a fixed assumption because the same scripts run on macOS's
# bash 3.2, where `patsub_replacement` does not exist and `shopt -u` on an unknown option
# fails; there is nothing to disable there, so discarding that failure makes the line a
# no-op on 3.2 while it does the real work on 5.2+.
shopt -u patsub_replacement 2>/dev/null || true

phase="${1:?usage: build-develop-prompt.sh red|green|refactor|revise <issue-spec-file> <step-text> <test-cmd> ...}"

# The phase is checked here, before any other positional is read, because the two questions
# are answered with different exit codes and the first one asked wins. A `${N:?}` expansion
# aborts the shell with status 1, so validating the arguments of a phase that does not exist
# would answer "an argument is missing" (exit 1) to a caller whose real mistake was the
# phase itself — and a bad phase is a bad-arguments case, which is exit 2 suite-wide.
case "$phase" in
  red | green | refactor | revise) ;;
  *) echo "build-develop-prompt: unknown phase '$phase' (want red|green|refactor|revise)" >&2; exit 2 ;;
esac

# `revise` names the phase it is redoing *before* the three arguments every phase shares,
# so its spec/step/test-cmd each sit one position later than everyone else's. Take that
# extra argument off the front; past this point the positions line up again.
revised_phase=""
if [[ "$phase" == "revise" ]]; then
  revised_phase="${2:?missing <phase> being revised}"
  shift
fi

spec_file="${2:?missing <issue-spec-file>}"
step="${3:?missing <step-text>}"
test_cmd="${4:?missing <test-cmd>}"

# Each phase takes its own extra positionals past the three every phase shares, and below
# each branch names only those. Everything else stays empty, and an empty variable's
# placeholder expands to nothing — which is why red, the phase that writes the test and so
# has nothing yet to name, needs no branch body at all.
test_path="" target="" touched="" reason_file=""
case "$phase" in
  red) ;;
  green)
    test_path="${5:?missing <test-path>}"
    target="${6:?missing <target-test>}"
    ;;
  refactor)
    touched="${5:?missing <touched-files>}"
    ;;
  revise)
    reason_file="${5:?missing <reason-file>}"
    ;;
esac

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/develop-$phase.md"
shared_file="$HERE/prompts/_develop-shared.md"
for f in "$tpl_file" "$shared_file" "$spec_file" "$reason_file"; do
  [[ -n "$f" ]] || continue  # only revise has a reason file; every other phase leaves it empty
  [[ -r "$f" ]] || { echo "build-develop-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"
reason=""
if [[ -n "$reason_file" ]]; then reason="$(cat "$reason_file")"; fi

# Literal substitution via bash parameter expansion — no sed, and with the
# patsub_replacement guard above holding, so &, \, / and {} in the spec or the step text
# are carried through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{STEP\}\}/$step}"
out="${out//\{\{TEST_CMD\}\}/$test_cmd}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{TOUCHED_FILES\}\}/$touched}"
out="${out//\{\{REVISE_PHASE\}\}/$revised_phase}"
out="${out//\{\{REJECTION_REASON\}\}/$reason}"

printf '%s\n' "$out"
