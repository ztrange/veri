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

test_path='tests/zorblat/test_frob & nitz.sh'
target='qwixtle seeds a newline-terminated block'

touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'

scripts_dir="$(cd "$HERE/.." && pwd)"
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

name="build-develop-prompt.sh given a directory as the issue-spec file for a red call exits 2 with nothing on stdout and a non-empty stderr"
mkdir -p "$work/spec-dir"
dir_err="$work/spec-dir.err"
dir_out="$("$BUILD" red "$work/spec-dir" "$step_text" "$test_cmd" 2>"$dir_err")"; code=$?
diag=""; [[ -s "$dir_err" ]] && diag=diagnostic
expect_eq "$name" "2::diagnostic" "$code:${dir_out:+prompt}:$diag"

name="develop-refactor's sub-step 1 tells the leaf to report a structural transform it does not apply on a CANDIDATES: structural line and one outside the issue's bounds on a CANDIDATES: out-of-scope line"
refactor_out="$(VERI_REFACTOR_BUDGET=5 "$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"
sub_step_1="$(awk '/^1\. Triage/ { inside = 1 } inside && /^2\. / { exit } inside' <<<"$refactor_out" | tr '\n' ' ')"
problems=""
[[ -n "$sub_step_1" ]] || problems="$problems; no sub-step 1 found"
[[ "$sub_step_1" == *'`CANDIDATES: structural`'* ]] || problems="$problems; sub-step 1 names no CANDIDATES: structural line"
[[ "$sub_step_1" == *'`CANDIDATES: out-of-scope`'* ]] || problems="$problems; sub-step 1 names no CANDIDATES: out-of-scope line"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

name="develop-replaces (#1625) names every case in the missing-cases file, points at the report file and asks for a REPLACES: line each, and a missing report or cases file exits 2 with no stdout"
printf '%s\n' 'wrote the replacements' > "$work/red-report.txt"
printf '%s\n' 'zibble case alpha' 'zibble case beta' > "$work/missing-cases.txt"
rep_out="$("$BUILD" replaces-report "$work/spec.md" "$step_text" "$test_cmd" "$work/red-report.txt" "$work/missing-cases.txt" 2>/dev/null)"; rep_code=$?
nr_out="$("$BUILD" replaces-report "$work/spec.md" "$step_text" "$test_cmd" "$work/no-such-report.txt" "$work/missing-cases.txt" 2>/dev/null)"; nr_code=$?
nm_out="$("$BUILD" replaces-report "$work/spec.md" "$step_text" "$test_cmd" "$work/red-report.txt" "$work/no-such-cases.txt" 2>/dev/null)"; nm_code=$?
problems=""
[[ "$rep_code" -eq 0 ]] || problems="$problems; exit $rep_code, not 0"
[[ "$rep_out" == *'zibble case alpha'* && "$rep_out" == *'zibble case beta'* ]] || problems="$problems; a missing case is not named"
[[ "$rep_out" == *"$work/red-report.txt"* ]] || problems="$problems; the report file is not named"
[[ "$rep_out" == *'REPLACES: <case> => <test id>'* ]] || problems="$problems; no REPLACES: line format asked for"
[[ "$nr_code" -eq 2 && -z "$nr_out" ]] || problems="$problems; missing report: exit $nr_code, stdout '${nr_out:+prompt}'"
[[ "$nm_code" -eq 2 && -z "$nm_out" ]] || problems="$problems; missing cases file: exit $nm_code, stdout '${nm_out:+prompt}'"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

finish
