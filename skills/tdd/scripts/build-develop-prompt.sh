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
#   build-develop-prompt.sh revise <phase> <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh exhausted <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh reconcile <issue-spec-file> <step-text> <test-cmd> <branch> <remote-sha>
#
# `refactor` also reads VERI_REFACTOR_BUDGET (default 5) from the environment, the number of
# transforms the leaf may apply.
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

# The phase word is read with an explicit count rather than `${1:?usage...}` for the same
# reason every other refusal below avoids `:?`: that expansion aborts the shell with status
# 1, and a caller who passed nothing at all made no call whose result could be a negative
# answer. It is the emptiest bad-arguments case there is, and bad arguments are exit 2.
#
# The phase list is spelled once, here, so the usage line and the unknown-phase refusal
# below cannot name different sets.
phases="red|green|refactor|revise|reconcile|exhausted"
# Spelled once, and quoted back by both refusals below: a caller who dropped an argument
# later than the phase word is as entitled to see the whole call as one who passed nothing.
USAGE="build-develop-prompt: usage: $phases <issue-spec-file> <step-text> <test-cmd> ..."
(( $# >= 1 )) || { echo "$USAGE" >&2; exit 2; }
phase="$1"

# Both argument questions — is the phase one we have, and did the caller pass enough for it
# — are settled here, before any other positional is read, because they are answered with
# different exit codes and the first one asked wins. A `${N:?}` expansion aborts the shell
# with status 1, the code reserved for a real answer, so letting those fire first would
# report a caller who mistyped the phase or forgot an argument as one whose call was made
# and came back negative. Both are bad-arguments cases, which is exit 2 suite-wide.
#
# One `case` answers both because the arms are the same four words either way: naming each
# phase's arity gives the whitelist something to do beyond existing, and `*)` beneath them
# still means "not one of ours". The counts include the phase word itself, and for `revise`
# the phase it is redoing, since neither has been shifted off yet.
case "$phase" in
  red) want=4 ;;
  green) want=7 ;;
  refactor) want=5 ;;
  revise) want=6 ;;
  reconcile) want=6 ;;
  # The phase a step reaches when its revise budget ran out (#408). It takes what `revise`
  # takes minus the phase being redone: there is no phase to redo here, only a step to
  # judge, so the spec, the step, the test command and the last rejection reason.
  exhausted) want=5 ;;
  *) echo "build-develop-prompt: unknown phase '$phase' (want $phases)" >&2; exit 2 ;;
esac
# refuse <what> — the shape every bad-arguments refusal past the phase word takes: say what
# was wrong with the call, quote the whole usage line back, and exit 2 because no answer
# could be obtained from a call that was never made. Spelled once, here, because the arity
# check below and `need` beneath it are the same three lines otherwise, and two copies of a
# refusal is where the one that exits with the wrong code hides.
refuse() {
  echo "build-develop-prompt: $1" >&2
  echo "$USAGE" >&2
  exit 2
}

(( $# >= want )) || refuse "$phase needs $want arguments, got $#"

# need <var> <value> <what> — assign <value> to <var>, or refuse the call naming <what>.
#
# The ten positionals below were read as `${N:?missing <what>}` until #270. That expansion
# aborts the shell with status 1 — "a clean negative", the code the conductor reads as a
# leaf that ran and answered — where a call that left an argument out owes 2, "no answer
# could be obtained". The arity check above already refuses a short call with 2, so the
# expansions could only ever have fired on an argument passed *empty*; that is the same
# bad-arguments case and owes the same code. Spelled once here because ten copies of a
# refusal is where the wrong one hides; the refusal itself is `refuse` above, shared with
# the arity check.
#
# `printf -v` rather than a `$(…)` command substitution: this builder runs once per leaf and
# CLAUDE.md's fork budget counts what a per-leaf helper costs, so the assignment happens in
# this shell rather than in ten subshells.
need() {
  [[ -n "$2" ]] || refuse "missing $3"
  printf -v "$1" '%s' "$2"
}

# `revise` names the phase it is redoing *before* the three arguments every phase shares,
# so its spec/step/test-cmd each sit one position later than everyone else's. Take that
# extra argument off the front; past this point the positions line up again.
#
# That second phase name gets the same check the first one got, and for the same reason:
# it is interpolated into the prompt as the phase the leaf is redoing, so an unchecked
# word would reach the leaf as an instruction to redo a phase that does not exist. `revise`
# is not among the four here — a revise of a revise has no template behind it.
revised_phase=""
if [[ "$phase" == "revise" ]]; then
  need revised_phase "${2:-}" '<phase> being revised'
  case "$revised_phase" in
    red|green|refactor) ;;
    *) echo "build-develop-prompt: unknown phase to revise '$revised_phase' (want red|green|refactor)" >&2; exit 2 ;;
  esac
  shift
fi

need spec_file "${2:-}" '<issue-spec-file>'
need step "${3:-}" '<step-text>'
need test_cmd "${4:-}" '<test-cmd>'

# Each phase takes its own extra positionals past the three every phase shares, and below
# each branch names only those. Everything else stays empty, and an empty variable's
# placeholder expands to nothing — which is why red, the phase that writes the test and so
# has nothing yet to name, needs no branch body at all.
test_path="" target="" fast_cmd="" touched="" reason_file="" refactor_budget="" branch="" remote_sha=""
case "$phase" in
  red) ;;
  green)
    need test_path "${5:-}" '<test-path>'
    need target "${6:-}" '<target-test>'
    # The fast tier's command (#341): green runs it plus the affected suites instead of the
    # full suite, and a leaf in a target repository has no way to ask for it itself.
    need fast_cmd "${7:-}" '<fast-cmd>'
    ;;
  refactor)
    need touched "${5:-}" '<touched-files>'
    # The one variable this builder reads from the environment rather than from a
    # positional. It is the same number `refactor-budget.sh` reads, same name and same
    # default, because one leaf per step moves the spending decision inside the leaf: the
    # bound in the template is a phrase with nothing behind it unless the number travels
    # with the prompt. Taking it from `VERI_REFACTOR_BUDGET` rather than from an argument
    # keeps one way to say it — a second channel could disagree with the one the loop's
    # own bound is read from.
    refactor_budget="${VERI_REFACTOR_BUDGET:-5}"
    ;;
  revise|exhausted)
    need reason_file "${5:-}" '<reason-file>'
    ;;
  reconcile)
    need branch "${5:-}" '<branch>'
    need remote_sha "${6:-}" '<remote-sha>'
    ;;
esac

HERE="$(cd "$(dirname "$0")" && pwd)"
tpl_file="$HERE/prompts/develop-$phase.md"
shared_file="$HERE/prompts/_develop-shared.md"
for f in "$tpl_file" "$shared_file" "$spec_file" "$reason_file"; do
  [[ -n "$f" ]] || continue  # only revise and exhausted have a reason file; every other phase leaves it empty
  [[ -r "$f" ]] || { echo "build-develop-prompt: cannot read '$f'" >&2; exit 2; }
done

tpl="$(cat "$tpl_file")"
shared="$(cat "$shared_file")"
spec="$(cat "$spec_file")"
reason=""
if [[ -n "$reason_file" ]]; then reason="$(cat "$reason_file")"; fi

# The reproduction paragraph, and the one condition under which it is emitted (#112). An
# issue labelled `bug` reaches the leaf through the one channel there is — `capture-spec.sh`
# copies the report into the blind spec under a `## Bug` heading — so the spec's own text is
# what this asks, rather than a new positional: the builder's arity per phase is the
# conductor's contract and does not change for a bug. No section, no paragraph, and not a
# word of difference: a leaf told to reproduce a report nobody filed has nothing to
# reproduce, and would go looking for one in a spec that is the whole of what it can see.
bug_reproduction=""
if grep -qE '^## Bug[[:space:]]*$' "$spec_file"; then
  bug_file="$HERE/prompts/_develop-red-bug.md"
  [[ -r "$bug_file" ]] || { echo "build-develop-prompt: cannot read '$bug_file'" >&2; exit 2; }
  bug_reproduction="$(cat "$bug_file")"
fi

# Literal substitution via bash parameter expansion — no sed, and with the
# patsub_replacement guard above holding, so &, \, / and {} in the spec or the step text
# are carried through verbatim.
out="${tpl//\{\{SHARED\}\}/$shared}"
out="${out//\{\{ISSUE_SPEC\}\}/$spec}"
out="${out//\{\{BUG_REPRODUCTION\}\}/$bug_reproduction}"
out="${out//\{\{STEP\}\}/$step}"
out="${out//\{\{TEST_CMD\}\}/$test_cmd}"
out="${out//\{\{TEST_PATH\}\}/$test_path}"
out="${out//\{\{TARGET_TEST\}\}/$target}"
out="${out//\{\{FAST_CMD\}\}/$fast_cmd}"
# The wrapper every test-command run goes through (#373), named at an absolute path: a leaf
# works in the target repository, where the bare name resolves to nothing.
out="${out//\{\{TIMED_TEST_RUN\}\}/$HERE/timed-test-run.sh}"
out="${out//\{\{TOUCHED_FILES\}\}/$touched}"
out="${out//\{\{REFACTOR_BUDGET\}\}/$refactor_budget}"
out="${out//\{\{REVISE_PHASE\}\}/$revised_phase}"
out="${out//\{\{REJECTION_REASON\}\}/$reason}"
out="${out//\{\{BRANCH\}\}/$branch}"
out="${out//\{\{REMOTE_SHA\}\}/$remote_sha}"

printf '%s\n' "$out"
