#!/usr/bin/env bash
# Tests for scripts/build-develop-prompt.sh — what the assembled developer prompt carries.
#
# Contract under test, red phase:
#   build-develop-prompt.sh red <spec-file> <step-text> <test-cmd>
#   exits 0 and prints a prompt carrying the spec, the step criterion and the test command
#   verbatim, the `AGAINST_UNMODIFIED` report line, the `UNTESTABLE` outcome and the rules a
#   valid test holds to — behaviour over mechanism, lightweight, self-contained.
#
# Contract under test, green phase:
#   build-develop-prompt.sh green <spec-file> <step-text> <test-cmd> <test-path> <target> <fast-cmd>
#   exits 0 and prints a prompt naming the test's path and case name, and forbidding any edit
#   to it.
#
# Contract under test, refactor phase:
#   build-develop-prompt.sh refactor <spec-file> <step-text> <test-cmd> <touched-files>
#   exits 0 and prints a prompt naming the files this cycle touched, the rule against
#   generality no test demands, and the `RESULT:` / `CANDIDATES:` / `NEW_STEP:` footer.
#
# Contract under test, the reader of that footer:
#   SKILL.md's `#### Refactor loop` section tells the two stop conditions apart and, when the
#   budget ended the loop, says how many candidates were left and lists them.
#
# Contract under test, revise phase:
#   build-develop-prompt.sh revise <phase> <spec-file> <step-text> <test-cmd> <reason-file>
#   exits 0 and prints a prompt carrying the verifier's rejection reason verbatim, and
#   offering `IMPOSSIBLE`.
#
# Contract under test, refusals:
#   an unknown phase, a missing positional, or a missing template, spec or reason file, exits
#   2 with a diagnostic and prints no prompt.
#
# Run: scripts/tests/build-develop-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-develop-prompt.sh"
source "$HERE/lib/harness.sh"
source "$HERE/lib/probe-order.sh"

work="$(scratch_dir)"

cat > "$work/spec.md" <<'SPEC'
zorblat("Frob & Nitz/Quux") must return "frob-nitz-quux" — see {ref}\n done.
SPEC
step_text='QWIXTLE: a seed ending in a newline gains the block and reports added'
test_cmd='make test ZORBLAT=1 -- --only "frob & nitz/quux"'

red="$("$BUILD" red "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$red" == *'zorblat("Frob & Nitz/Quux")'* ]] \
  && [[ "$red" == *"$step_text"* ]] \
  && [[ "$red" == *"$test_cmd"* ]] \
  && [[ "$red" == *'AGAINST_UNMODIFIED'* ]] \
  && ok || no "develop-red carries spec + step + test command verbatim and the AGAINST_UNMODIFIED report line (exit $code)"

test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'

touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'

reason_text='REJECT: the case asserts on zorblat()'"'"'s log line, not its return value — & {tricky}\chars.'
printf '%s\n' "$reason_text" > "$work/reason.md"

mkdir -p "$work/no-prompts/lib"
cp "$BUILD" "$work/no-prompts/build-develop-prompt.sh"
cp "$(dirname "$BUILD")"/lib/*.sh "$work/no-prompts/lib/"
cp -R "$(dirname "$BUILD")/veri" "$work/no-prompts/"

refusal_bad=""
refuses() {  # <label> <script> <args...> — records why, if this was not a clean refusal
  local label="$1" bin="$2"; shift 2
  local out code err="$work/err.txt"
  out="$("$bin" "$@" 2>"$err")"; code=$?
  [[ "$code" -eq 2 ]] || refusal_bad="$refusal_bad; $label exited $code, want 2"
  [[ -z "$out" ]] || refusal_bad="$refusal_bad; $label printed a prompt"
  [[ -s "$err" ]] || refusal_bad="$refusal_bad; $label gave no diagnostic"
}

bare_err="$work/bare-unknown-phase.err"
bare_out="$("$BUILD" bogus 2>"$bare_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$bare_out" ]] \
  && grep -q 'bogus' "$bare_err" \
  && ok || no "an unknown phase with no further arguments exits 2, names the phase on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$bare_err"))"

SKILL="$HERE/../../SKILL.md"
narration="$(awk '/^#### Refactor loop/ { inside = 1; next }
                  inside && /^#{1,6} / { exit }
                  inside' "$SKILL" | tr '\n' ' ')"

narrates() {  # narrates <complaint> <grep argument…>
  local complaint="$1"; shift
  grep -q "$@" <<<"$narration" || problems="$problems; $complaint"
}

problems=""
if [[ -z "$narration" ]]; then
  problems="$problems; no '#### Refactor loop' section in SKILL.md — the narration could not be read"
else
  narrates "the narration never names the nothing-left-to-tidy stop" \
    -i -e 'nothing left to tidy'
  narrates "the narration never names the budget stop" \
    -i -e 'budget'
  narrates "the narration never names the leaf's CANDIDATES: line" \
    -e 'CANDIDATES:'
  narrates "the narration does not say the comment lists those candidates" \
    -iE -e '(list|lists|listing|enumerate)[^.]{0,80}candidate|candidate[^.]{0,80}(list|lists|listing|enumerate)'
  narrates "the narration does not say how many candidates the budget left" \
    -iE -e '(how many|number of|count of|(^|[^[:alnum:]])n)[[:space:]]+(candidates?|left)'
fi
[[ -z "$problems" ]] \
  && ok || no "SKILL.md's Refactor narration tells nothing-left-to-tidy from stopped-by-budget and lists the N candidates from the leaf's CANDIDATES: lines (${problems#; })"

bullet="$(awk '/^#### Refactor loop/ { inside = 1; next }
               inside && /^#{1,6} / { exit }
               inside && /^3\. / { narration = 1 }
               inside && narration' "$SKILL" | tr '\n' ' ')"

problems=""
if [[ -z "$bullet" ]]; then
  problems="no '3.' bullet under '#### Refactor loop' — the narration bullet could not be read"
elif ! grep -q -e 'CANDIDATES:' <<<"$bullet"; then
  problems="the narration bullet never names CANDIDATES:, so only sub-step 1 does"
fi
[[ -z "$problems" ]] \
  && ok || no "SKILL.md's Refactor narration bullet names the leaf's CANDIDATES: line itself, not merely somewhere in the section ($problems)"

# hazard: BSD grep backtracks on two bounded `[^.]{0,N}` in one alternation branch and hangs; keep one per branch.
prompt_has() {  # prompt_has <prompt> <grep argument…> — the match itself, folded to one line
  local prompt="$1"; shift
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")"
}

prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  prompt_has "$prompt" "$@" || problems="$problems; $complaint"
}

prompt_lacks() {  # prompt_lacks <prompt> <complaint> <grep argument…> — prompt_says inverted
  local prompt="$1" complaint="$2"; shift 2
  ! prompt_has "$prompt" "$@" || problems="$problems; $complaint"
  return 0
}

says_both_ways() {  # says_both_ways <prompt> <complaint> <gap> <pattern> <pattern>
  local prompt="$1" complaint="$2" gap="$3" a="$4" b="$5"
  prompt_says "$prompt" "$complaint" -iE -e "$a[^.]{0,$gap}$b|$b[^.]{0,$gap}$a"
}

rc_branch='tdd/232-zorblat-frob'
rc_sha='3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01'

replaces_step='⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to tests/py/test_zorblat.py ⟦criterion 1⟧'
licence='(may|permitted|allowed|licen[cs]ed?)[^.]{0,60}delet|delet[^.]{0,60}(permitted|allowed|licen[cs]ed)'

cp "$work/spec.md" "$work/bug-spec.md"
cat >> "$work/bug-spec.md" <<'SPEC'

## Bug

### What happened

zorblat returned "FROB_NITZ" on the quuxed seed.

### Expected

zorblat returns "frob-nitz-quux".

### Steps to reproduce

Run zorblat --seed "Frob & Nitz/Quux".

### Environment

veri on bash 5.2, macOS 15.
SPEC

problems=""
bug_red="$("$BUILD" red "$work/bug-spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with a bug spec and red's own three positionals exited $code, want 0"
[[ "$bug_red" == *'zorblat returned "FROB_NITZ" on the quuxed seed.'* ]] \
  || problems="$problems; does not carry the bug report from the spec"
writes_expected='(write|derive|encode)[^.]{0,40}expected|expected[^.]{0,40}(write|derive|encode)'
driven_by_steps='(drive|driven)[^.]{0,40}steps|steps[^.]{0,40}(drive|driven)'
fails_as_reported='(fail|fails|failure)[^.]{0,60}what happened|what happened[^.]{0,60}(fail|fails|failure)'
prompt_says "$bug_red" "never says to write the test from Expected" -iE -e "$writes_expected"
prompt_says "$bug_red" "never says to drive it with Steps to reproduce" -iE -e "$driven_by_steps"
prompt_says "$bug_red" "never says the failure must be the one What happened describes" -iE -e "$fails_as_reported"
prompt_lacks "$red" "a spec with no Bug section is still told to write the test from Expected" -iE -e "$writes_expected"
prompt_lacks "$red" "a spec with no Bug section is still told to drive it with Steps to reproduce" -iE -e "$driven_by_steps"
prompt_lacks "$red" "a spec with no Bug section is still told what the failure must be" -iE -e "$fails_as_reported"
[[ -z "$problems" ]] \
  && ok || no "develop-red tells a bug's leaf to write the test from Expected, drive it with Steps to reproduce and fail as What happened describes, and tells a leaf with no Bug section none of it (${problems#; })"

refusal_bad=""
for bad in -1 3, qwixnum 1e3 .5 '3.47 because'; do
  refuses "spent '$bad'"  "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" "$bad" 2.50
  refuses "budget '$bad'" "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 "$bad"
done
refuses "spent 'qwixnum' with no template" "$work/no-prompts/build-develop-prompt.sh" \
  over-budget "$work/spec.md" "$step_text" "$test_cmd" qwixnum 2.50
grep -F 'cannot read' "$work/err.txt" > /dev/null \
  && refusal_bad="$refusal_bad; with no template, refused for an unreadable file rather than the figure"
grep -F 'qwixnum' "$work/err.txt" > /dev/null \
  || refusal_bad="$refusal_bad; with no template, the diagnostic does not name the bad figure"
[[ -z "$refusal_bad" ]] \
  && ok || no "develop-over-budget refuses a <spent> or <budget> that is not a non-negative decimal number with exit 2, a diagnostic and no prompt, before any template is read (${refusal_bad#; })"

scripts_dir="$(cd "$HERE/.." && pwd)"
problems=""
renders_as() {  # <label> <want-cksum> <args...> — records a prompt whose sum is not <want>
  local label="$1" want="$2"; shift 2
  local out code got
  out="$(VERI_REFACTOR_BUDGET=5 "$BUILD" "$@" 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || { problems="$problems; $label exited $code, want 0"; return; }
  got="$(printf '%s\n' "${out//"$scripts_dir"/@SCRIPTS@}" | cksum)"
  [[ "$got" == "$want" ]] || problems="$problems; $label renders as '$got', want '$want'"
}
renders_as red            '981610769 10392'       red "$work/spec.md" "$step_text" "$test_cmd"
renders_as green          '3453024810 7300'     green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit"
renders_as refactor       '4038231874 9685'  refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched"
renders_as 'revise red'   '2457909894 7787'    revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise green' '2359866403 7789'  revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise refactor' '3942894315 7792' revise refactor "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as exhausted      '124126523 3995'       exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as reconcile      '3578743599 5598'       reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha"
[[ -z "$problems" ]] \
  && ok || no "every phase other than over-budget renders byte-identically to before #450 (${problems#; })"

problems=""
unmarked_step='tests/zorblat.test.sh: "zorblat frobs a nitz" replaces-case moves to tests/py ⟦added⟧ ⟦criterion 2⟧'
renders_as 'green, unmarked step' '1396175610 7338' green "$work/spec.md" "$unmarked_step" "$test_cmd" "$test_path" "$target" "make unit"
[[ -z "$problems" ]] \
  && ok || no "develop-green for a step not carrying ⟦replaces-case⟧ renders byte-identically to before #671 (${problems#; })"

problems=""
replaces_revise="$("$BUILD" revise green "$work/spec.md" "$replaces_step" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$replaces_revise" "never permits deleting the case the step names" -iE -e "$licence"
says_both_ways "$replaces_revise" "no longer forbids modifying or deleting any other case" \
  60 '(never|not|forbid|forbidden|must not|rejected)' '(any|every) other (bash )?case'
renders_as 'revise green, unmarked step' '961542236 7827' revise green "$work/spec.md" "$unmarked_step" "$test_cmd" "$work/reason.md"
[[ -z "$problems" ]] \
  && ok || no "develop-revise redoing green for a ⟦replaces-case⟧ step permits deleting the one bash case the step names and still forbids modifying or deleting any other case, and for an unmarked step renders byte-identically to before #671 (${problems#; })"

problems=""
probe_order develop-cover "$(cat "$HERE/../prompts/develop-cover.md")" 'break its behaviour' 'run the suites'
[[ -z "$problems" ]] && ok \
  || no "#619 develop-cover restores a probe with cp <file> <file>.orig before the mutation and mv <file>.orig <file> after the run under mutation (${problems#; })"

problems=""
dd_step='the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧'

dd_err="$work/diff-no-test-cmd.err"
dd_out="$("$BUILD" diff "$work/spec.md" "$dd_step" '' 'make unit' 2>"$dd_err")"; code=$?
dd_first=""; IFS= read -r dd_first < "$dd_err"
[[ "$code" -eq 2 ]] \
  && [[ -z "$dd_out" ]] \
  && [[ "$dd_first" == 'build-develop-prompt: missing <test-cmd>' ]] \
  && ok || no "#995 develop-diff given every argument but an empty <test-cmd> exits 2 with no prompt and 'missing <test-cmd>' on stderr (exit $code, stderr: $(cat "$dd_err"))"

name="#974 the diff prompt tells the leaf to run the given fast command through timed-test-run.sh fast and then the affected suites, and to finish only with both green"
dd_fast='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'

name="build-develop-prompt.sh, run through a symlink to the scripts directory from another working directory, answers a red, a green and a diff call as in place, but the timed-test-run.sh path names the symlink as called"
linked="$(scratch_dir)"
ln -s "$scripts_dir" "$linked/veri-scripts"
problems=""
same_through_link() {  # <label> <args...> — records a call whose answer through the link differs from in place
  local label="$1"; shift
  local want_out want_err want_code got_out got_err got_code
  want_out="$("$BUILD" "$@" 2>"$linked/want-err")"; want_code=$?
  got_out="$(cd "$linked" && ./veri-scripts/build-develop-prompt.sh "$@" 2>"$linked/got-err")"; got_code=$?
  want_err="$(cat "$linked/want-err")"; got_err="$(cat "$linked/got-err")"
  [[ "$want_out" == *"$scripts_dir/timed-test-run.sh"* ]] || problems="$problems; $label in place names no $scripts_dir/timed-test-run.sh"
  want_out="${want_out//"$scripts_dir/timed-test-run.sh"/"$linked/veri-scripts/timed-test-run.sh"}"
  [[ "$got_code" == "$want_code" ]] || problems="$problems; $label exited $got_code through the link, $want_code in place"
  [[ "$got_out" == "$want_out" ]] || problems="$problems; $label stdout differs through the link"
  [[ "$got_err" == "$want_err" ]] || problems="$problems; $label stderr differs through the link"
}
same_through_link red   red "$work/spec.md" "$step_text" "$test_cmd"
same_through_link green green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit"
same_through_link diff  diff "$work/spec.md" "$dd_step" "$test_cmd" "$dd_fast"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

name="build-develop-prompt.sh given a directory as the issue-spec file for a red call exits 1 with nothing on stdout and a non-empty stderr"
mkdir -p "$work/spec-dir"
dir_err="$work/spec-dir.err"
dir_out="$("$BUILD" red "$work/spec-dir" "$step_text" "$test_cmd" 2>"$dir_err")"; code=$?
diag=""; [[ -s "$dir_err" ]] && diag=diagnostic
expect_eq "$name" "1::diagnostic" "$code:${dir_out:+prompt}:$diag"

finish
