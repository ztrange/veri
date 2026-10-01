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
green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$green" == *"$test_path"* ]] \
  && [[ "$green" == *"$target"* ]] \
  && grep -qiE "(do not|don't|never) (modify|change|edit|touch|weaken).{0,40}test|test.{0,40}(must not|may not) be (modified|changed|edited|touched)" <<<"$green" \
  && ok || no "develop-green names the test path + target test and forbids modifying the test (exit $code)"

touched='scripts/zorblat.sh, tests/zorblat/test_frob & nitz.sh'
refactor="$("$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$refactor" == *"$touched"* ]] \
  && grep -qiE '(no|not|never|without)[^.]{0,80}(generality|generali[sz]ation|abstraction)' <<<"$refactor" \
  && grep -q 'RESULT:' <<<"$refactor" \
  && ok || no "develop-refactor carries the touched-files list + the no-untested-generality rule and the RESULT: footer (exit $code)"

reason_text='REJECT: the case asserts on zorblat()'"'"'s log line, not its return value — & {tricky}\chars.'
printf '%s\n' "$reason_text" > "$work/reason.md"
revise="$("$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$revise" == *"$reason_text"* ]] \
  && [[ "$revise" == *'IMPOSSIBLE'* ]] \
  && ok || no "develop-revise carries the rejection reason verbatim and the IMPOSSIBLE outcome (exit $code)"

mkdir -p "$work/no-prompts/lib"
cp "$BUILD" "$work/no-prompts/build-develop-prompt.sh"
cp "$(dirname "$BUILD")/lib/exit-contract.sh" "$work/no-prompts/lib/exit-contract.sh"

refusal_bad=""
refuses() {  # <label> <script> <args...> — records why, if this was not a clean refusal
  local label="$1" bin="$2"; shift 2
  local out code err="$work/err.txt"
  out="$("$bin" "$@" 2>"$err")"; code=$?
  [[ "$code" -eq 2 ]] || refusal_bad="$refusal_bad; $label exited $code, want 2"
  [[ -z "$out" ]] || refusal_bad="$refusal_bad; $label printed a prompt"
  [[ -s "$err" ]] || refusal_bad="$refusal_bad; $label gave no diagnostic"
}

refuses "unknown phase"           "$BUILD" bogus "$work/spec.md" "$step_text" "$test_cmd"
refuses "missing spec"            "$BUILD" red "$work/absent.md" "$step_text" "$test_cmd"
refuses "missing reason"          "$BUILD" revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/absent.md"
refuses "missing template"        "$work/no-prompts/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd"
refuses "unknown phase to revise" "$BUILD" revise bogus "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
refuses "missing positionals"     "$BUILD" red "$work/spec.md"

[[ -z "$refusal_bad" ]] \
  && ok || no "an unknown phase, a missing positional or a missing template/spec/reason file exits 2 with a diagnostic and prints no prompt (${refusal_bad#; })"

bare_err="$work/bare-unknown-phase.err"
bare_out="$("$BUILD" bogus 2>"$bare_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$bare_out" ]] \
  && grep -q 'bogus' "$bare_err" \
  && ok || no "an unknown phase with no further arguments exits 2, names the phase on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$bare_err"))"

none_err="$work/no-args.err"
none_out="$("$BUILD" 2>"$none_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$none_out" ]] \
  && [[ -s "$none_err" ]] \
  && ok || no "no arguments at all exits 2 with a usage diagnostic on stderr and prints no prompt (exit $code, stderr: $(tr '\n' ' ' < "$none_err"))"

problems=""
grep -qE '^CANDIDATES:' <<<"$refactor" || problems="$problems; no CANDIDATES: report line"
grep -qiE 'one[^.]{0,20}per line' <<<"$refactor" || problems="$problems; does not ask for one candidate per line"
grep -qiE '^CANDIDATES:.*none' <<<"$refactor" || problems="$problems; the CANDIDATES: line does not offer none"
[[ -z "$problems" ]] \
  && ok || no "develop-refactor requires a CANDIDATES: report line — the candidates still seen, one per line, or none (${problems#; })"

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

every_phase() {  # every_phase <name of a check function taking <phase label> <prompt>> <headline>
  local check="$1" headline="$2" problems=""
  "$check" red "$red"; "$check" green "$green"; "$check" refactor "$refactor"; "$check" revise "$revise"
  [[ -z "$problems" ]] && ok || no "$headline (${problems#; })"
}

says_both_ways() {  # says_both_ways <prompt> <complaint> <gap> <pattern> <pattern>
  local prompt="$1" complaint="$2" gap="$3" a="$4" b="$5"
  prompt_says "$prompt" "$complaint" -iE -e "$a[^.]{0,$gap}$b|$b[^.]{0,$gap}$a"
}

problems=""
prompt_says "$red" "never says to run the suite that holds the new case" \
  -iE -e 'suite (that |which )?(holds|contains|holding|containing)[^.]{0,40}case'
prompt_says "$red" "never says NOT to run the full suite" \
  -iE -e "(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite"
prompt_says "$red" "no fallback for a repository that cannot run one suite" \
  -iE -e '(cannot|can.t|no way to|unable to|has no way)[^.]{0,60}(suite|file)'
prompt_says "$red" "does not ask the leaf to say so in its report" \
  -iE -e '(say|says|saying|state|states|note|report) (so|it|this|that)[^.]{0,30}report'
[[ -z "$problems" ]] \
  && ok || no "develop-red says to run the suite holding the new case, not the full suite, falling back to the test command and saying so in the report (${problems#; })"

problems=""
prompt_says "$green" "never says to iterate on the suite that holds the target case" \
  -iE -e 'iterat[^.]{0,60}suite|suite[^.]{0,60}iterat'
prompt_says "$green" "never says the full suite is run exactly once" \
  -iE -e '(full|whole|entire) suite[^.]{0,40}once|once[^.]{0,40}(full|whole|entire) suite'
prompt_says "$green" "does not put that one run immediately before the SUITE: report line" \
  -iE -e 'before[^.]{0,60}SUITE:'
[[ -z "$problems" ]] \
  && ok || no "develop-green says to iterate on the target case's suite and run the full suite exactly once, immediately before the SUITE: report line (${problems#; })"

problems=""
prompt_says "$refactor" "never says to run the suites covering the touched files" \
  -iE -e 'suites?[^.]{0,40}cover|cover[^.]{0,40}suites?'
prompt_says "$refactor" "never says NOT to run the full suite" \
  -iE -e "(not|rather than|instead of|no need to|never|don't|do not)[^.]{0,40}(full|whole|entire) suite"
prompt_says "$refactor" "does not name verify-refactor as where the full suite runs" \
  -iE -e 'verify-refactor[^.]{0,60}(full|whole|entire) suite|(full|whole|entire) suite[^.]{0,60}verify-refactor'
prompt_says "$refactor" "does not state that a break in an untouched suite surfaces there instead" \
  -iE -e '(untouched|nobody touched|no one touched|nothing touched)[^.]{0,80}(surface|shows up|appears|caught)|(surface|shows up|appears|caught)[^.]{0,80}(untouched|nobody touched|no one touched)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor says to run the suites covering the touched files rather than the full suite, names verify-refactor as where the full suite runs and states the untouched-suite trade-off (${problems#; })"

demands_foreground() {  # demands_foreground <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never says to run test commands in the foreground" \
    -i -e 'foreground'
  prompt_says "$prompt" "develop-$label never says to report only after the test command has exited" \
    -iE -e '(only after|not until|never before)[^.]{0,60}(exit|exits|exited|finish)'
}

every_phase demands_foreground \
  "every built developer prompt says to run test commands in the foreground and report only after they exit"

forbids_ending_mid_run() {  # forbids_ending_mid_run <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids ending the turn mid-run" \
    -iE -e 'end(ing)?[^[:alnum:]]+(your|the|its)[^[:alnum:]]+turn'
}

every_phase forbids_ending_mid_run \
  "every built developer prompt forbids ending the turn while a suite run is still going"

forbids_stash() {  # forbids_stash <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids git stash" \
    -iE -e "(never|do not|don't|no)[^.]{0,60}stash"
  prompt_says "$prompt" "develop-$label names no shared-ref-free way to see the committed version" \
    -E -e 'git show HEAD:|git worktree add'
}

every_phase forbids_stash \
  "every built developer prompt forbids git stash and names a safe alternative"

defines_class() {  # defines_class <class word> <alternation of that class's effects>
  local class="$1" effects="$2"
  says_both_ways "$refactor" "does not define $class by what the transform changes" \
    160 "$class" "($effects)"
}

problems=""
defines_class structural 'duplication|extract|inline|dead code|rename|scope'
defines_class cosmetic 'reword|re-word|re-cite|recite|reflow|re-flow|re-comment'
prompt_says "$refactor" "does not say cosmetic leaves duplication, identifiers and structure alone" \
  -iE -e ' (without|not|never|leaves) [^.]{0,30}(duplication|identifier|structure)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor defines structural and cosmetic candidates by what the transform changes (${problems#; })"

problems=""
prompt_says "$refactor" "does not say only a structural transform may be applied" \
  -iE -e 'only[^.]{0,60}structural|structural[^.]{0,60}only'
prompt_says "$refactor" "does not say to report nothing left to tidy when only cosmetic candidates remain" \
  -iE -e 'nothing left to tidy[^.]{0,120}cosmetic|cosmetic[^.]{0,120}nothing left to tidy'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies only a structural transform and reports nothing left to tidy when only cosmetic candidates remain (${problems#; })"

offers_class() {  # offers_class <report token> <class word>
  local token="$1" class="$2"
  grep -qE "^$token:.*$class[^|]{0,40}\|" <<<"$refactor" \
    || problems="$problems; the $token: line does not offer $class as the class"
}

problems=""
offers_class CANDIDATES structural
offers_class CANDIDATES cosmetic
[[ -z "$problems" ]] \
  && ok || no "develop-refactor requires every CANDIDATES: line to carry its class, separated from the transform (${problems#; })"

problems=""
says_both_ways "$refactor" "does not say the structural candidates are applied up to the budget it is given" \
  80 'budget' 'structural'
says_both_ways "$refactor" "does not tell the leaf to commit its transforms itself as refactor:" \
  80 'commit' 'refactor:'
says_both_ways "$refactor" "does not say one refactor: commit per transform" \
  60 '(each|every|own|per)' 'refactor:'
says_both_ways "$refactor" "does not say the touched suites run after each transform" \
  80 'suites?' 'after each'
says_both_ways "$refactor" "does not say a transform that turns them red is reverted" \
  80 'revert' 'red'
says_both_ways "$refactor" "does not ask the report to name every transform it applied" \
  80 'applied' '(transforms|one per|each|every)'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies the structural candidates up to its budget, one refactor: commit per transform, runs the touched suites after each reverting one that turns them red, and reports what it applied (${problems#; })"

problems=""
budgeted="$(VERI_REFACTOR_BUDGET=37 "$BUILD" refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
says_both_ways "$budgeted" "the prompt never names 37 as the budget" \
  80 'budget' '37'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor carries VERI_REFACTOR_BUDGET into the prompt as the number of transforms the leaf may apply (${problems#; })"

asks_for() {  # asks_for <prompt> <report label> <footer token, colon included>
  local prompt="$1" label="$2" token="$3"
  prompt_says "$prompt" "the $label report never asks for $token" -F -e "$token"
}

offers_verdict() {  # offers_verdict <prompt> <report label> <verdict word>
  local prompt="$1" label="$2" verdict="$3"
  prompt_says "$prompt" "the $label report never offers $verdict on the PREDICTION: line" \
    -E -e "PREDICTION:[^.]{0,20}$verdict"
}

predicts_before_running() {  # predicts_before_running <prompt> <complaint>
  local prompt="$1" complaint="$2"
  says_both_ways "$prompt" "$complaint" 60 'predict' 'before (you|issuing|any command)'
}

problems=""
predicts_before_running "$red" "does not require the prediction to be stated before the run"
asks_for "$red" red 'PREDICTED_FAILURE:'
offers_verdict "$red" red MATCHED
offers_verdict "$red" red DIVERGED
asks_for "$red" red 'PREDICTION_NOTE:'
[[ -z "$problems" ]] \
  && ok || no "develop-red requires the predicted failure before the run and carries PREDICTED_FAILURE:, PREDICTION: MATCHED | DIVERGED and PREDICTION_NOTE: in its report footer (${problems#; })"

pin_path_says() {  # pin_path_says <complaint> <what to find beside the break>
  local complaint="$1" pattern="$2"
  says_both_ways "$red" "$complaint" 80 'break' "$pattern"
}

problems=""
pin_path_says "the pin path never asks what the temporary break should print" 'predict'
pin_path_says "does not say what the break printed is checked against that prediction" \
  '(check|compar|match)'
prompt_says "$red" "does not put that check before the restore" \
  -iE -e 'before[^.]{0,40}restor|restor[^.]{0,40}(only after|not until)'
[[ -z "$problems" ]] \
  && ok || no "develop-red's pin path predicts what the temporary break should print and checks it before restoring (${problems#; })"

problems=""
says_both_ways "$revise" "never says a rewritten test owes a new prediction" \
  80 '(rewrit|rewrote|new test)' 'predict'
predicts_before_running "$revise" "does not require that prediction before the re-run"
[[ -z "$problems" ]] \
  && ok || no "develop-revise asks for a new prediction for the rewritten test, before the re-run (${problems#; })"

rc_branch='tdd/232-zorblat-frob'
rc_sha='3f9a1c0b7e2d4a6f8c1b3e5d7f9a0c2e4b6d8f01'
problems=""
reconcile="$("$BUILD" reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$reconcile" == *"$rc_sha"* ]] || problems="$problems; no remote sha"
[[ "$reconcile" == *"$rc_branch"* ]] || problems="$problems; no branch"
[[ "$reconcile" == *"--force-with-lease=$rc_branch:$rc_sha"* ]] \
  || problems="$problems; no literal --force-with-lease=<branch>:<sha>"
rc_tpl="$HERE/../prompts/develop-reconcile.md"
if [[ ! -r "$rc_tpl" ]]; then
  problems="$problems; no template prompts/develop-reconcile.md"
elif grep -Eq -e '--force($|[^-]|-($|[^w]))' "$rc_tpl" \
  || grep -vq -e '^--force-with-lease=' < <(grep -o -e '--force-with-lease[^[:space:]`]*' "$rc_tpl"); then
  problems="$problems; template offers a --force that is not a pinned --force-with-lease="
fi
refusal_bad=""
refuses "reconcile missing remote sha" "$BUILD" reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-reconcile carries the remote sha, the branch and a pinned --force-with-lease=<branch>:<sha>, offers no bare --force, and refuses a missing argument with exit 2 (${problems#; })"

forbids_global_config() {  # forbids_global_config <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids changing global or user-level configuration" \
    -iE -e "(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config"
  prompt_says "$prompt" "develop-$label never names environment variables as the way to simulate a condition" \
    -iE -e 'environment variables?'
  prompt_says "$prompt" "develop-$label never names throwaway directories as the way to simulate a condition" \
    -iE -e '(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)'
}

every_phase forbids_global_config \
  "every built developer prompt forbids changing global or user-level configuration and names environment variables and throwaway directories instead"

problems=""
prompt_says "$red" "never forbids pinning a process count, a fork count or a timing" \
  -iE -e '(process|fork)[^.]{0,20}count|timing'
prompt_says "$red" "never points a process/fork count or a timing at make profile instead" \
  -iE -e 'make profile'
prompt_says "$red" "never carves out a call count the criterion itself names, pinned with an in-process spy" \
  -iE -e 'in-process spy'
prompt_says "$red" "never says a PATH shim counting real processes is what the spy replaces" \
  -iE -e 'PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)'
prompt_says "$red" "never gives the UNTESTABLE outcome as the report line for a criterion that cannot be pinned" \
  -iE -e 'UNTESTABLE'
[[ -z "$problems" ]] \
  && ok || no "develop-red states behaviour-over-mechanism (with the in-process-spy carve-out), points cost at make profile, and offers UNTESTABLE for a criterion no lightweight test can pin (${problems#; })"

fast_cmd='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
problems=""
fast_green="$("$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "$fast_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with <fast-cmd> exited $code, want 0"
[[ "$fast_green" == *"$fast_cmd"* ]] || problems="$problems; the prompt does not carry <fast-cmd> verbatim"
refusal_bad=""
refuses "missing <fast-cmd>" "$BUILD" green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-green takes <fast-cmd> as a seventh positional, carries it verbatim, and refuses a call without it with exit 2 (${problems#; })"

problems=""
says_both_ways "$red" "never says the predicted missing-name error names the missing name on the PREDICTED_FAILURE: line" \
  60 'PREDICTED_FAILURE' '(missing|absent) name'
[[ -z "$problems" ]] \
  && ok || no "develop-red says a predicted missing-name error names the missing name in PREDICTED_FAILURE: (${problems#; })"

problems=""
asks_for "$revise" revise 'PREDICTED_FAILURE:'
offers_verdict "$revise" revise MATCHED
offers_verdict "$revise" revise DIVERGED
[[ -z "$problems" ]] \
  && ok || no "develop-revise ends with PREDICTED_FAILURE: and PREDICTION: MATCHED | DIVERGED report lines (${problems#; })"

problems=""
says_both_ways "$refactor" "never says a transform may touch a file outside the touched-files list to remove duplication" \
  60 'outside' 'duplication'
says_both_ways "$refactor" "never says removing that duplication is the only reason to leave the list" \
  60 'outside' 'only'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor permits a transform outside the touched-files list only when it removes duplication with code this cycle wrote (${problems#; })"

problems=""
says_both_ways "$refactor" "never says the suites run after a transform cover a file it touched outside the list" \
  80 'outside' 'suites?'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor tells the leaf to run the suites covering every file a transform touched, the out-of-list file included (${problems#; })"

problems=""
grep -qE '^SPLIT:' <<<"$green" || problems="$problems; no SPLIT: report line"
prompt_says "$green" "never bounds the split at one to three criteria" \
  -iE -e 'one to three|1 to 3|(at most|no more than) three'
says_both_ways "$green" "never says a leaf that splits changes no production code" \
  80 'SPLIT' '(no|any|without changing) production code'
[[ -z "$problems" ]] \
  && ok || no "develop-green offers one to three SPLIT: lines instead of an implementation, changing no production code (${problems#; })"

revise_green="$("$BUILD" revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
grep -qE '^SPLIT:' <<<"$revise_green" || problems="$problems; no SPLIT: report line"
prompt_says "$revise_green" "never bounds the split at one to three criteria" \
  -iE -e 'one to three|1 to 3|(at most|no more than) three'
says_both_ways "$revise_green" "never says a leaf that splits changes no production code" \
  80 'SPLIT' '(no|any|without changing) production code'
[[ -z "$problems" ]] \
  && ok || no "develop-revise redoing green offers the same one to three SPLIT: lines, changing no production code (${problems#; })"

exhausted="$("$BUILD" exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$exhausted" == *"$step_text"* ]] || problems="$problems; does not carry the step"
[[ "$exhausted" == *"$reason_text"* ]] || problems="$problems; does not carry the rejection reason verbatim"
[[ "$exhausted" == *'zorblat("Frob & Nitz/Quux")'* ]] || problems="$problems; does not carry the issue spec"
refusal_bad=""
refuses "exhausted missing reason" "$BUILD" exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/absent.md"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-exhausted carries the step, the verifier's last rejection reason and the issue spec, and refuses a missing reason file with exit 2 (${problems#; })"

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

problems=""
names_with_number='(name|naming)[^.]{0,60}#<n>|#<n>[^.]{0,60}(name|naming)'
prompt_says "$bug_red" "never says to name the case so it carries #<n>" -iE -e "$names_with_number"
prompt_lacks "$red" "a spec with no Bug section is still told to name the case after the issue" -iE -e "$names_with_number"
[[ -z "$problems" ]] \
  && ok || no "develop-red tells a bug's leaf to name the case so it carries the issue's number in the project's own idiom, and tells a leaf with no Bug section nothing of it (${problems#; })"

names_class() {  # names_class <class word> <what it names> <alternation matching that>
  local class="$1" names="$2" pattern="$3"
  says_both_ways "$refactor" "does not say $class names $names" \
    120 "$class" "$pattern"
}

problems=""
grep -qE '^FLAGS:' <<<"$refactor" || problems="$problems; no FLAGS: report line"
grep -qE '^FLAGS:.*none' <<<"$refactor" || problems="$problems; the FLAGS: line does not offer none"
grep -qE '^NEW_STEP:' <<<"$refactor" && problems="$problems; the report still carries a NEW_STEP: line"
offers_class FLAGS overfit
offers_class FLAGS uncovered-spec
offers_class FLAGS beyond-spec
names_class overfit 'code that passes the test without implementing the behaviour' \
  '(without|rather than|instead of) implementing'
names_class uncovered-spec 'a behaviour the spec requires' \
  '(spec (requires|asks)|required by the spec)'
names_class beyond-spec 'something the spec does not ask for' \
  "(does not|doesn.t|never) (ask|require)"
[[ -z "$problems" ]] \
  && ok || no "develop-refactor reports overfit code on FLAGS: lines carrying the overfit, uncovered-spec and beyond-spec classes or none, in place of NEW_STEP:, and defines what each class names (${problems#; })"

over_budget="$("$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 2.50 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$over_budget" == *"$step_text"* ]] || problems="$problems; does not carry the step"
[[ "$over_budget" == *'3.47'* ]] || problems="$problems; does not carry the spent figure"
[[ "$over_budget" == *'2.50'* ]] || problems="$problems; does not carry the budget figure"
[[ "$over_budget" == *'zorblat("Frob & Nitz/Quux")'* ]] || problems="$problems; does not carry the issue spec"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget carries the step, the spent figure, the budget figure and the issue spec (${problems#; })"

problems=""
grep -qE '^SPLIT:' <<<"$over_budget" || problems="$problems; no SPLIT: report line"
grep -qE '^NEEDS_USER:' <<<"$over_budget" || problems="$problems; no NEEDS_USER: report line"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget asks for SPLIT: lines or a NEEDS_USER: answer, the two shapes exhausted-outcome.sh reads (${problems#; })"

over_budget_flat="$(tr -s '[:space:]' ' ' <<<"$over_budget")"
problems=""
grep -iE 'not a verdict' <<<"$over_budget_flat" > /dev/null || problems="$problems; does not say a crossing is not a verdict"
grep -iE 'one behaviour[^.]*simply expensive' <<<"$over_budget_flat" > /dev/null || problems="$problems; does not offer \"one behaviour, simply expensive\" as an answer"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget says a crossing is not a verdict and that one behaviour, simply expensive, is an available answer (${problems#; })"

over_budget_report="${over_budget_flat#*'### Report'}"
problems=""
[[ "$over_budget_report" != "$over_budget_flat" ]] || problems="$problems; no ### Report section"
grep -iE 'simply expensive[^.]*(no|neither)[^.]*SPLIT:[^.]*NEEDS_USER:' <<<"$over_budget_report" > /dev/null \
  || problems="$problems; the report section has no shape for the one-behaviour, simply-expensive answer that says to print no SPLIT: and no NEEDS_USER: line"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget gives the \"neither — one behaviour, simply expensive\" answer its own report shape, printing no SPLIT: and no NEEDS_USER: line (${problems#; })"

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

refusal_bad=""
refuses "over-budget with no arguments"    "$BUILD" over-budget
refuses "over-budget with one argument"    "$BUILD" over-budget "$work/spec.md"
refuses "over-budget with two arguments"   "$BUILD" over-budget "$work/spec.md" "$step_text"
refuses "over-budget with three arguments" "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd"
refuses "over-budget with four arguments"  "$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47
[[ -z "$refusal_bad" ]] \
  && ok || no "develop-over-budget with fewer than five arguments after the phase exits 2, with a diagnostic and no prompt (${refusal_bad#; })"

over_budget_extra="$("$BUILD" over-budget "$work/spec.md" "$step_text" "$test_cmd" 3.47 2.50 "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; with a reason file appended, exited $code, want 0"
[[ "$over_budget_extra" == "$over_budget" ]] || problems="$problems; a reason file appended past <budget> changed the prompt"
[[ "$over_budget_extra" != *"$reason_text"* ]] || problems="$problems; carries the rejection reason handed to it"
grep -iE 'rejection reason' <<<"$over_budget_flat" > /dev/null && problems="$problems; names a rejection reason"
grep -E 'REJECT|VERDICT' <<<"$over_budget" > /dev/null && problems="$problems; names a verdict"
[[ -z "$problems" ]] \
  && ok || no "develop-over-budget names no rejection reason and no verdict, and takes no parameter that could carry one (${problems#; })"

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
renders_as red            '2493217892 9982'       red "$work/spec.md" "$step_text" "$test_cmd"
renders_as green          '1771614540 6887'     green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit"
renders_as refactor       '2694733224 8933'  refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched"
renders_as 'revise red'   '1295566063 7099'    revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise green' '2934549822 7101'  revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise refactor' '1582308635 7104' revise refactor "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as exhausted      '3417210291 3714'       exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as reconcile      '3527139660 5317'       reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha"
[[ -z "$problems" ]] \
  && ok || no "every phase other than over-budget renders byte-identically to before #450 (${problems#; })"

rb_onto='7c1e9a3f5b2d4e6a8c0f1b3d5e7a9c2e4f6b8d0a'
rb_pre='e2b4d6f8a0c1e3b5d7f9a1c3e5b7d9f0a2c4e6b8'
rb_files=$'skills/tdd/SKILL.md\nscripts/zorblat frob & nitz.sh'
problems=""
rebase="$("$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto" "$rb_pre" "$rb_files" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
[[ "$rebase" == *"$rb_onto"* ]] || problems="$problems; no onto sha"
[[ "$rebase" == *"$rb_pre"* ]] || problems="$problems; no pre-rebase sha"
while IFS= read -r rb_file; do
  [[ "$rebase" == *"$rb_file"* ]] || problems="$problems; no conflicting file '$rb_file'"
done <<< "$rb_files"
[[ "$rebase" == *"$test_cmd"* ]] || problems="$problems; no test command"
[[ "$rebase" == *"git rebase $rb_onto"* ]] || problems="$problems; no literal 'git rebase <onto-sha>'"
[[ "$rebase" == *ledger* && "$rebase" == *'[x]'* && "$rebase" == *'⟂ refactor pending'* ]] \
  || problems="$problems; does not tell the leaf to leave the ledger's [x] ticks and ⟂ refactor pending marks untouched"
rb_last="$(printf '%s\n' "$rebase" | sed '/^[[:space:]]*$/d' | tail -n 1)"
[[ "$rb_last" == 'REBASE: RESOLVED | FAILED'* ]] \
  || problems="$problems; last line is '$rb_last', want 'REBASE: RESOLVED | FAILED …'"
refusal_bad=""
refuses "rebase missing conflicting files" "$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto" "$rb_pre"
refuses "rebase missing pre-rebase sha" "$BUILD" rebase "$work/spec.md" "$step_text" "$test_cmd" "$rb_onto"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-rebase names the onto sha, the pre-rebase sha, every conflicting file and the test command, resolves by git rebase <onto-sha>, leaves the ledger's ticks and marks untouched, ends with REBASE: RESOLVED | FAILED, and refuses a missing argument with exit 2 and no stdout (${problems#; })"

problems=""
rk_red="$("$BUILD" red "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"
declare -A rk_out=()
for rk_phase in cover transform; do
  rk_out[$rk_phase]="$("$BUILD" "$rk_phase" "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || problems="$problems; $rk_phase exited $code, want 0"
  [[ -n "${rk_out[$rk_phase]}" ]] || problems="$problems; $rk_phase printed no prompt"
  [[ "${rk_out[$rk_phase]}" == *"$step_text"* ]] || problems="$problems; $rk_phase prompt lacks the step text"
  [[ "${rk_out[$rk_phase]}" != "$rk_red" ]] || problems="$problems; $rk_phase prompt is red's"
done
[[ -z "${rk_out[cover]}" || "${rk_out[cover]}" != "${rk_out[transform]}" ]] \
  || problems="$problems; cover and transform printed the same prompt"
refusal_bad=""
refuses "unknown phase beside cover/transform" "$BUILD" covers "$work/spec.md" "$step_text" "$test_cmd"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "cover and transform each print their own prompt carrying the step, and an unknown phase is still refused with exit 2 and no stdout (${problems#; })"

states_comment_rule() {  # states_comment_rule <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never names the contract header as an allowed comment" \
    -iE -e 'contract header'
  prompt_says "$prompt" "develop-$label never names the usage line and exit-code table" \
    -iE -e 'usage line[^.]{0,40}exit[- ]code table'
  prompt_says "$prompt" "develop-$label never allows a warning where the shell itself is the hazard" \
    -iE -e 'warning[^.]{0,60}shell itself is the hazard'
  prompt_says "$prompt" "develop-$label never requires a comment to be succinct" \
    -iE -e 'succinct'
  prompt_says "$prompt" "develop-$label never forbids rationale comments" \
    -iE -e 'no rationale'
  prompt_says "$prompt" "develop-$label never forbids issue archaeology" \
    -iE -e 'no issue archaeology'
  prompt_says "$prompt" "develop-$label never forbids restating the next line" \
    -iE -e 'no restatement of the next line'
}

every_phase states_comment_rule \
  "every built developer prompt states the comment rule: contract header or shell-hazard warning, succinct, nothing else"

states_rationale_home() {  # states_rationale_home <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never sends rationale to a test first" \
    -iE -e 'rationale[^.]{0,80}test first'
  prompt_says "$prompt" "develop-$label never sends rationale to an ADR second" \
    -iE -e 'ADR second'
  prompt_says "$prompt" "develop-$label never says rationale goes nowhere third" \
    -iE -e 'nowhere third'
}

every_phase states_rationale_home \
  "every built developer prompt states where rationale goes instead of a comment: a test first, an ADR second, nowhere third"

problems=""
says_both_ways "$refactor" "does not say to apply only duplication removal" \
  30 'only' 'duplication removal'
prompt_says "$refactor" "does not bound the duplication to code this cycle wrote" \
  -iE -e 'duplication[^.]{0,80}(this|the) cycle wrote'
prompt_says "$refactor" "does not say to apply no other structural transform" \
  -iE -e '(no|never|not)[^.]{0,30}other structural transform'
prompt_says "$refactor" "does not name extracting a module as withheld" \
  -iE -e 'extract(ing)? a module'
prompt_says "$refactor" "does not name moving behaviour as withheld" \
  -iE -e 'mov(e|ing) behaviou?r'
prompt_says "$refactor" "does not name renaming across files as withheld" \
  -iE -e 'renam(e|ing)[^.]{0,20}across files'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor applies only duplication removal against code this cycle wrote and no other structural transform: extract a module, move behaviour, rename across files (${problems#; })"

problems=""
says_both_ways "$refactor" "does not tell the leaf to report every other structural candidate on a CANDIDATES: structural line" \
  120 'every other structural candidate' 'CANDIDATES: structural'
says_both_ways "$refactor" "does not say to report it rather than apply it" \
  120 'structural candidate' '(rather than|instead of) apply(ing)?'
printf 'RESULT: nothing left to tidy\nCANDIDATES: structural | extract the zorblat parser into its own module\nFLAGS: none\n' \
  | "$HERE/../refactor-owed.sh" append "$work/owed.md" "$step_text" 2>/dev/null
step_at="$(grep -nxF "### $step_text" "$work/owed.md" 2>/dev/null | cut -d: -f1)"
candidate_at="$(grep -nxF -- '- extract the zorblat parser into its own module' "$work/owed.md" 2>/dev/null | cut -d: -f1)"
[[ -n "$step_at" && -n "$candidate_at" && "$step_at" -lt "$candidate_at" ]] \
  || problems="$problems; refactor-owed.sh append does not record the CANDIDATES: structural line under the step's name"
[[ -z "$problems" ]] \
  && ok || no "develop-refactor reports every other structural candidate as a CANDIDATES: structural line rather than apply it, and refactor-owed.sh append records it under the step's name (${problems#; })"

candidate='extract the zorblat parser into its own module & {rename} it'
issue_touched='scripts/zorblat.sh, scripts/lib/frob & nitz.sh'
structural="$("$BUILD" structural "$work/spec.md" "$candidate" "$test_cmd" "$issue_touched" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exit $code"
[[ "$structural" == *"$candidate"* ]] || problems="$problems; does not carry the candidate verbatim"
[[ "$structural" == *"$issue_touched"* ]] || problems="$problems; does not name the issue's touched files"
says_both_ways "$structural" "does not name the touched files as its bounds" \
  80 '(bound|limit|confine|only)' '(touched|files)'
says_both_ways "$structural" "does not say to commit the one transform as its own refactor: commit" \
  80 'commit' 'refactor:'
says_both_ways "$structural" "does not say to touch no test file" \
  40 '(no|never|not|must not)' 'test file'
[[ -z "$problems" ]] \
  && ok || no "develop-structural builds a transform prompt for one structural candidate, bounded to the issue's touched files, committed as its own refactor: commit, touching no test file (${problems#; })"

finish
