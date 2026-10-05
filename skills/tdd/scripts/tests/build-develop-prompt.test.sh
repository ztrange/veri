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
cp "$(dirname "$BUILD")"/lib/*.sh "$work/no-prompts/lib/"

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

name="called with no arguments, build-develop-prompt.sh exits 2 with a usage line on stderr naming it"
usage_err="$work/no-args-usage.err"
"$BUILD" > /dev/null 2>"$usage_err"; code=$?
usage_line="$(grep -iE 'usage' "$usage_err" | grep -F 'build-develop-prompt.sh')" || true
expect_eq "$name" '2:named' "$code:${usage_line:+named}"

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
prompt_lacks "$refactor" "still names verify-refactor as where the full suite runs" \
  -iE -e 'verify-refactor[^.]{0,60}(full|whole|entire) suite|(full|whole|entire) suite[^.]{0,60}verify-refactor'
prompt_says "$refactor" "does not name the PR's one full run as where the full suite runs" \
  -iE -e '(full|whole|entire) +suite +runs +once +per +PR'
prompt_says "$refactor" "does not state that a break outside the affected set surfaces at that run's repair step instead" \
  -iE -e 'outside +the affected set +surfaces[^.]{0,80}repair step'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor says to run the suites covering the touched files rather than the full suite, names the PR's one full run as where the full suite runs and states the affected-set trade-off (${problems#; })"

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

forbids_index_restore() {  # forbids_index_restore <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "develop-$label never forbids git checkout -- <file>" \
    -iE -e "(never|do not|don't|not)[^.]{0,120}git checkout -- <file>"
  prompt_says "$prompt" "develop-$label never forbids git restore" \
    -iE -e "(never|do not|don't|not)[^.]{0,160}git restore"
  prompt_says "$prompt" "develop-$label never ties the rule to undoing a probe" \
    -iE -e "(undo|restor)[^.]{0,60}(probe|mutat)"
  prompt_says "$prompt" "develop-$label never names cp <file> <file>.orig" -F -e 'cp <file> <file>.orig'
  prompt_says "$prompt" "develop-$label never names mv <file>.orig <file>" -F -e 'mv <file>.orig <file>'
}

every_phase forbids_index_restore \
  "#619 _develop-shared.md forbids git checkout -- <file> and git restore for undoing a probe and names cp <file> <file>.orig / mv <file>.orig <file> instead"

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
offers_class CANDIDATES test-only
says_both_ways "$refactor" "does not define test-only as a transform changing only files under a tests/ directory" \
  160 'test-only' 'only (files|paths) under an? `?tests/'
says_both_ways "$refactor" "does not say a test-only candidate is never reported on a CANDIDATES: structural line" \
  160 'test-only' '(never|not)( on| as)? an? `?CANDIDATES: structural'
[[ -z "$problems" ]] \
  && ok || no "develop-refactor reports a candidate whose transform changes only files under a tests/ directory on a CANDIDATES: test-only line, never a CANDIDATES: structural one (${problems#; })"

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

replaces_step='⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to tests/py/test_zorblat.py ⟦criterion 1⟧'
licence='(may|permitted|allowed|licen[cs]ed?)[^.]{0,60}delet|delet[^.]{0,60}(permitted|allowed|licen[cs]ed)'
replaces_green="$("$BUILD" green "$work/spec.md" "$replaces_step" "$test_cmd" 'tests/py/test_zorblat.py' 'test_zorblat_frobs_a_nitz' "make unit" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$replaces_green" "never permits deleting the case the step names" -iE -e "$licence"
prompt_lacks "$green" "an unmarked step's prompt permits deleting a case too" -iE -e "$licence"
says_both_ways "$replaces_green" "no longer forbids modifying or deleting any other case" \
  60 '(never|not|forbid|forbidden|must not|rejected)' '(any|every) other (bash )?case'
[[ -z "$problems" ]] \
  && ok || no "develop-green for a ⟦replaces-case⟧ step permits deleting the one bash case the step names and still forbids modifying or deleting any other case (${problems#; })"

repair_step='fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz; skills/tdd/scripts/tests/quux.test.sh — FAIL - quux & {nitz} round-trips ⟦suite-repair⟧'
repair_green="$("$BUILD" green "$work/spec.md" "$repair_step" "make test" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' "make unit" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
for named in 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' \
             'skills/tdd/scripts/tests/quux.test.sh' 'quux & {nitz} round-trips'; do
  [[ "$repair_green" == *"$named"* ]] || problems="$problems; does not name '$named'"
done
says_both_ways "$repair_green" "never tells the leaf to make every listed suite green" \
  60 '(every|each|all)( of the)? (listed|red|named) suites?' 'green'
[[ -z "$problems" ]] \
  && ok || no "#690 develop-green for a ⟦suite-repair⟧ step listing two red suites names both suites and both failing cases and tells the leaf to make every listed suite green (${problems#; })"

repair_revise="$("$BUILD" revise green "$work/spec.md" "$repair_step" "make test" "$work/reason.md" 2>/dev/null)"; code=$?
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
for named in 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' \
             'skills/tdd/scripts/tests/quux.test.sh' 'quux & {nitz} round-trips'; do
  [[ "$repair_revise" == *"$named"* ]] || problems="$problems; does not name '$named'"
done
says_both_ways "$repair_revise" "never tells the revise leaf to make every listed suite green" \
  60 '(every|each|all)( of the)? (listed|red|named) suites?' 'green'
[[ -z "$problems" ]] \
  && ok || no "#690 develop-revise redoing green for a ⟦suite-repair⟧ step listing two red suites names both suites and both failing cases and tells the leaf to make every listed suite green, as develop-green does (${problems#; })"

single_repair_step='fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz ⟦suite-repair⟧'
single_green="$("$BUILD" green "$work/spec.md" "$single_repair_step" "make test" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' "make unit" 2>/dev/null)"; dev_code=$?
single_verify="$("$HERE/../build-verify-prompt.sh" --step "$single_repair_step" --fast-cmd 'make unit' green "$work/spec.md" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' 2>/dev/null)"; verify_code=$?
problems=""
[[ "$dev_code" -eq 0 ]] || problems="$problems; develop-green exited $dev_code, want 0"
[[ "$verify_code" -eq 0 ]] || problems="$problems; verify-green exited $verify_code, want 0"
for named in 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz'; do
  [[ "$single_green" == *"$named"* ]] || problems="$problems; develop-green does not name '$named'"
  [[ "$single_verify" == *"$named"* ]] || problems="$problems; verify-green does not name '$named'"
done
[[ -z "$problems" ]] \
  && ok || no "#690 a ⟦suite-repair⟧ step naming one red suite builds develop-green and verify-green prompts that name that one suite and its failing case (${problems#; })"

unmodified="$(scratch_dir)"
cp -R "$HERE/../build-develop-prompt.sh" "$HERE/../build-verify-prompt.sh" "$HERE/../lib" "$HERE/../prompts" "$unmodified/"
rm "$unmodified/prompts/_develop-green-suite-repair.md" "$unmodified/prompts/_verify-green-suite-repair.md"
for tpl in "$unmodified"/prompts/*.md; do
  body="$(cat "$tpl"; printf x)"; body="${body%x}"
  printf '%s' "${body//\{\{SUITE_REPAIR\}\}/}" > "$tpl"
done
scripts_dir="$(cd "$HERE/.." && pwd)"
plain_args=(green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target")
problems=""
built="$("$BUILD" "${plain_args[@]}" "make unit" 2>&1; echo "exit $?")"
want="$("$unmodified/build-develop-prompt.sh" "${plain_args[@]}" "make unit" 2>&1; echo "exit $?")"; want="${want//"$unmodified"/$scripts_dir}"
[[ "$built" == "$want" ]] || problems="$problems; develop-green differs from the builder without suite repair: $(diff <(printf '%s\n' "$want") <(printf '%s\n' "$built") | sed -n 1,5p)"
verify_args=(--step "$step_text" --fast-cmd 'make unit' green "$work/spec.md" "$test_path" "$target")
built="$("$HERE/../build-verify-prompt.sh" "${verify_args[@]}" 2>&1; echo "exit $?")"
want="$("$unmodified/build-verify-prompt.sh" "${verify_args[@]}" 2>&1; echo "exit $?")"; want="${want//"$unmodified"/$scripts_dir}"
[[ "$built" == "$want" ]] || problems="$problems; verify-green differs from the builder without suite repair: $(diff <(printf '%s\n' "$want") <(printf '%s\n' "$built") | sed -n 1,5p)"
[[ -z "$problems" ]] \
  && ok || no "#690 develop-green and verify-green prompts for a step without ⟦suite-repair⟧ are byte-identical to the builders' without suite repair (${problems#; })"

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
renders_as red            '1253458810 10263'       red "$work/spec.md" "$step_text" "$test_cmd"
renders_as green          '2615734855 7168'     green "$work/spec.md" "$step_text" "$test_cmd" "$test_path" "$target" "make unit"
renders_as refactor       '1398370756 9452'  refactor "$work/spec.md" "$step_text" "$test_cmd" "$touched"
renders_as 'revise red'   '788521639 7651'    revise red "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise green' '2849870849 7653'  revise green "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as 'revise refactor' '1919967131 7656' revise refactor "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as exhausted      '124126523 3995'       exhausted "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md"
renders_as reconcile      '3578743599 5598'       reconcile "$work/spec.md" "$step_text" "$test_cmd" "$rc_branch" "$rc_sha"
[[ -z "$problems" ]] \
  && ok || no "every phase other than over-budget renders byte-identically to before #450 (${problems#; })"

problems=""
unmarked_step='tests/zorblat.test.sh: "zorblat frobs a nitz" replaces-case moves to tests/py ⟦added⟧ ⟦criterion 2⟧'
renders_as 'green, unmarked step' '2880759674 7206' green "$work/spec.md" "$unmarked_step" "$test_cmd" "$test_path" "$target" "make unit"
[[ -z "$problems" ]] \
  && ok || no "develop-green for a step not carrying ⟦replaces-case⟧ renders byte-identically to before #671 (${problems#; })"

problems=""
replaces_revise="$("$BUILD" revise green "$work/spec.md" "$replaces_step" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$replaces_revise" "never permits deleting the case the step names" -iE -e "$licence"
says_both_ways "$replaces_revise" "no longer forbids modifying or deleting any other case" \
  60 '(never|not|forbid|forbidden|must not|rejected)' '(any|every) other (bash )?case'
renders_as 'revise green, unmarked step' '4146217642 7691' revise green "$work/spec.md" "$unmarked_step" "$test_cmd" "$work/reason.md"
[[ -z "$problems" ]] \
  && ok || no "develop-revise redoing green for a ⟦replaces-case⟧ step permits deleting the one bash case the step names and still forbids modifying or deleting any other case, and for an unmarked step renders byte-identically to before #671 (${problems#; })"

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

problems=""
probe_order develop-cover "$(cat "$HERE/../prompts/develop-cover.md")" 'break its behaviour' 'run the suites'
[[ -z "$problems" ]] && ok \
  || no "#619 develop-cover restores a probe with cp <file> <file>.orig before the mutation and mv <file>.orig <file> after the run under mutation (${problems#; })"

problems=""
grep -E '^COVERED:.*unreachable' <<<"${rk_out[cover]}" > /dev/null \
  || problems="$problems; the COVERED: report line does not offer unreachable"
says_both_ways "${rk_out[cover]}" "never limits unreachable to a step that only deletes code" \
  120 'unreachable' 'only delet'
says_both_ways "${rk_out[cover]}" "never says the deleted code is code no caller reaches" \
  60 'no caller' 'reach'
says_both_ways "${rk_out[cover]}" "never says the PROOF: names every caller" \
  120 'PROOF:' 'every caller'
prompt_says "${rk_out[cover]}" "never names no caller existing as a reason" -iE -e 'none exists'
prompt_says "${rk_out[cover]}" "never names every caller passing a no-op as a reason" \
  -iE -e 'every caller passes a no-op'
prompt_says "${rk_out[cover]}" "never names a value never read as a reason" -iE -e 'never read'
[[ -z "$problems" ]] && ok \
  || no "#679 develop-cover allows COVERED: unreachable only for a step that only deletes code no caller reaches, with a PROOF: naming every caller and why none reaches it — none exists, every caller passes a no-op, the value is never read (${problems#; })"

problems=""
grep -E '^COVERED:.*type-only' <<<"${rk_out[cover]}" > /dev/null \
  || problems="$problems; the COVERED: report line does not offer type-only"
says_both_ways "${rk_out[cover]}" "never limits type-only to a step that changes only types" \
  120 'type-only' 'changes only types'
says_both_ways "${rk_out[cover]}" "never says the type-only PROOF: is the type-check command" \
  120 'PROOF:' 'type-check command'
prompt_says "${rk_out[cover]}" "never says the type check must have run green" \
  -iE -e 'type-check command[^.]{0,60}(ran|run) green'
prompt_says "${rk_out[cover]}" "never names npx tsc --noEmit as an example" -F -e 'npx tsc --noEmit'
prompt_says "${rk_out[cover]}" "never names mypy as an example" -F -e 'mypy'
[[ -z "$problems" ]] && ok \
  || no "#679 develop-cover allows COVERED: type-only only for a step that changes only types, with a PROOF: that is the type-check command the leaf ran green — npx tsc --noEmit, mypy (${problems#; })"

problems=""
says_both_ways "${rk_out[cover]}" "never names a step that moves or reshapes runtime code" \
  40 'reshap' 'runtime code'
says_both_ways "${rk_out[cover]}" "never says such a step is never unreachable or type-only" \
  80 'runtime code' 'never `?unreachable`? or `?type-only'
prompt_says "${rk_out[cover]}" "never names reachable code no test watches" \
  -iE -e '(^|[^a-z])reachable code[^.]{0,40}no test watches'
prompt_says "${rk_out[cover]}" "never says reachable code no test watches is COVERED: no" \
  -iE -e 'no test watches[^.]{0,60}COVERED: no'
grep -E '^PROOF:' <<<"${rk_out[cover]}" > /dev/null \
  || problems="$problems; the report block carries no PROOF: line"
[[ -z "$problems" ]] && ok \
  || no "#679 develop-cover says a step that moves or reshapes runtime code is never unreachable or type-only, that reachable code no test watches is COVERED: no, and its report block carries a PROOF: line (${problems#; })"

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

problems=""
predicate="$("$BUILD" predicate "$work/spec.md" "$candidate" "$test_cmd" "$issue_touched" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exit $code"
[[ "$predicate" == *"$candidate"* ]] || problems="$problems; does not carry the candidate verbatim"
[[ "$predicate" == *"$issue_touched"* ]] || problems="$problems; does not name the issue's touched files"
[[ "$predicate" == *"$test_cmd"* ]] || problems="$problems; does not carry the test command"
says_both_ways "$predicate" "does not ask for one shell predicate" \
  40 '(one|a single)' '(shell )?predicate'
says_both_ways "$predicate" "does not say the predicate fails on the current tree" \
  60 '(fail|false|non-?zero)' '(current|unmodified|before)'
says_both_ways "$predicate" "does not say the predicate succeeds once the candidate is applied" \
  80 '(succeed|true|exit(s)? 0)' '(applied|after)'
[[ "$predicate" == *'PREDICATE: <command>'* ]] || problems="$problems; no 'PREDICATE: <command>' report line"
[[ "$predicate" == *'PREDICATE: NONE — <why>'* ]] || problems="$problems; no 'PREDICATE: NONE — <why>' report line"
refusal_bad=""
refuses "predicate missing issue-touched files" "$BUILD" predicate "$work/spec.md" "$candidate" "$test_cmd"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "#691 develop-predicate asks for one shell predicate for a structural candidate, false on the current tree and true once it is applied, reported as PREDICATE: <command> or PREDICATE: NONE — <why>, and refuses a missing argument with exit 2 and no stdout (${problems#; })"

problems=""
rk_step='grep -q "zorblat_parse" scripts/lib/zorblat-parser.sh'
printf '%s\n' "$rk_step" > "$work/rk-predicate.md"
rk_base=0123abcdef
rk_dev="$("$BUILD" transform "$work/spec.md" "$rk_step" "$test_cmd" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; develop transform exited $code, want 0"
rk_ver="$("$HERE/../build-verify-prompt.sh" --step "$rk_step" transform "$work/spec.md" "$work/rk-predicate.md" "$rk_base" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; verify transform exited $code, want 0"
[[ "$rk_dev" == *"$rk_step"* ]] || problems="$problems; develop transform prompt lacks the step text"
[[ "$rk_ver" == *"$rk_step"* ]] || problems="$problems; verify transform prompt lacks the step text"
[[ "$rk_ver" == *"$work/rk-predicate.md"* ]] || problems="$problems; verify transform prompt does not name the step's predicate record"
for rk_label in develop verify; do
  rk_prompt="$rk_dev"; [[ "$rk_label" == verify ]] && rk_prompt="$rk_ver"
  prompt_lacks "$rk_prompt" "$rk_label transform prompt names structural-predicate.sh" -F -e 'structural-predicate'
  prompt_lacks "$rk_prompt" "$rk_label transform prompt names a predicate leaf" -iE -e 'predicate leaf'
  prompt_lacks "$rk_prompt" "$rk_label transform prompt offers PREDICATE: NONE" -F -e 'PREDICATE: NONE'
  prompt_lacks "$rk_prompt" "$rk_label transform prompt speaks of the structural pass" -iE -e 'structural[* ]+pass'
done
[[ -z "$problems" ]] \
  && ok || no "#691 a refactor-kind step's transform prompts, develop and verify, build from the step text and its own predicate record with no predicate leaf or structural-predicate.sh involved (${problems#; })"

problems=""
dd_step='the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧'
dd="$("$BUILD" diff "$work/spec.md" "$dd_step" "$test_cmd" "make unit" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; diff exited $code, want 0"
[[ "$dd" == *"$dd_step"* ]] || problems="$problems; diff prompt lacks the step text"
[[ "$dd" == *'zorblat("Frob & Nitz/Quux")'* ]] || problems="$problems; diff prompt lacks the spec"
[[ "$dd" != "$red" ]] || problems="$problems; diff prompt is red's"
says_both_ways "$dd" "diff prompt never says to make the change the criterion names" 80 'make' 'change'
says_both_ways "$dd" "diff prompt never says to commit the change" 120 'change' 'commit'
says_both_ways "$dd" "diff prompt never says to make no commit when the criterion is that something stays unchanged" \
  160 '(no|not|never)[^.]{0,20}commit' 'unchanged'
prompt_says "$dd" "diff prompt never says to add no test" \
  -iE -e '(add|write)[^.]{0,20}(no|not a single) (new )?(test|case)|(do not|don.t|never) (add|write)[^.]{0,20}(test|case)'
refusal_bad=""
refuses "diff missing test-cmd" "$BUILD" diff "$work/spec.md" "$dd_step"
[[ -z "$refusal_bad" ]] || problems="$problems${refusal_bad}"
[[ -z "$problems" ]] \
  && ok || no "develop-diff tells the leaf to make the change the step's criterion names and commit it, to make no commit when the criterion is that something stays unchanged, and to add no test; a missing argument exits 2 with nothing on stdout (${problems#; })"

bogus_revise_err="$work/bogus-revise.err"
bogus_revise_out="$("$BUILD" revise bogus "$work/spec.md" "$step_text" "$test_cmd" "$work/reason.md" 2>"$bogus_revise_err")"; code=$?
[[ "$code" -eq 2 ]] \
  && [[ -z "$bogus_revise_out" ]] \
  && grep -F 'red|green|refactor|diff' "$bogus_revise_err" > /dev/null \
  && ok || no "#880 a revise of an unknown phase exits 2 with no prompt and names diff among the accepted revise phases red|green|refactor|diff (exit $code, stderr: $(cat "$bogus_revise_err"))"

revise_diff_err="$work/revise-diff.err"
revise_diff="$("$BUILD" revise diff "$work/spec.md" "$dd_step" "$test_cmd" "$work/reason.md" 2>"$revise_diff_err")"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$revise_diff" == *"$dd_step"* ]] \
  && [[ "$revise_diff" == *"$reason_text"* ]] \
  && ok || no "#880 a revise of a diff-checked step exits 0 and prints a prompt carrying the step text and the verifier's rejection reason (exit $code, stderr: $(cat "$revise_diff_err"))"

problems=""
prompt_lacks "$revise_diff" "asks the leaf to rewrite a test" -iE -e 'rewritten test|rewrite (a|the) test'
prompt_lacks "$revise_diff" "asks for an AGAINST_UNMODIFIED: report line" -F -e 'AGAINST_UNMODIFIED:'
prompt_lacks "$revise_diff" "asks for a PREDICTED_FAILURE: report line" -F -e 'PREDICTED_FAILURE:'
[[ -z "$problems" ]] \
  && ok || no "#880 a revise of a diff-checked step does not ask the leaf to write or rewrite a test, since a diff-checked step adds none (${problems#; })"

name="#703 a {{INCLUDE:<file>}} token is replaced by that partial under prompts/, trailing newlines stripped, before the other placeholders, so one inside the partial is filled"
included="$(scratch_dir)"
cp -R "$HERE/../build-develop-prompt.sh" "$HERE/../lib" "$HERE/../prompts" "$included/"
printf 'before {{INCLUDE:_probe-partial.md}} after\n' > "$included/prompts/develop-red.md"
printf 'partial runs {{TEST_CMD}}\n\n\n' > "$included/prompts/_probe-partial.md"
rendered="$("$included/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd" 2>&1)"; code=$?
expect_eq "$name" "0:before partial runs $test_cmd after" "$code:$rendered"

name="#703 a {{INCLUDE:<file>}} token inside an included partial is itself resolved, recursively"
nested="$(scratch_dir)"
cp -R "$HERE/../build-develop-prompt.sh" "$HERE/../lib" "$HERE/../prompts" "$nested/"
printf 'before {{INCLUDE:_probe-outer.md}} after\n' > "$nested/prompts/develop-red.md"
printf 'outer {{INCLUDE:_probe-inner.md}} end\n' > "$nested/prompts/_probe-outer.md"
printf 'inner runs {{TEST_CMD}}\n' > "$nested/prompts/_probe-inner.md"
rendered="$("$nested/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd" 2>&1)"; code=$?
expect_eq "$name" "0:before outer inner runs $test_cmd end after" "$code:$rendered"

name="#703 a {{INCLUDE:<file>}} naming a partial that does not exist exits 2 with that partial's path on stderr and nothing on stdout"
dangling="$(scratch_dir)"
cp -R "$HERE/../build-develop-prompt.sh" "$HERE/../lib" "$HERE/../prompts" "$dangling/"
printf 'before {{INCLUDE:_probe-absent.md}} after\n' > "$dangling/prompts/develop-red.md"
rendered="$("$dangling/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd" 2>"$dangling/err")"; code=$?
named=""; grep -F "$dangling/prompts/_probe-absent.md" "$dangling/err" > /dev/null && named=named
expect_eq "$name" "2:named:" "$code:$named:$rendered"

name="#703 a partial that includes itself through another partial exits 2 naming that partial on stderr, with nothing on stdout, rather than looping"
cycle="$(scratch_dir)"
cp -R "$HERE/../build-develop-prompt.sh" "$HERE/../lib" "$HERE/../prompts" "$cycle/"
printf 'before {{INCLUDE:_probe-cycle-a.md}} after\n' > "$cycle/prompts/develop-red.md"
printf 'a {{INCLUDE:_probe-cycle-b.md}}\n' > "$cycle/prompts/_probe-cycle-a.md"
printf 'b {{INCLUDE:_probe-cycle-a.md}}\n' > "$cycle/prompts/_probe-cycle-b.md"
# hazard: a looping builder never returns; the CPU-time limit ends it instead of the suite.
rendered="$(ulimit -t 2; "$cycle/build-develop-prompt.sh" red "$work/spec.md" "$step_text" "$test_cmd" 2>"$cycle/err")"; code=$?
named=""; grep -F "_probe-cycle-a.md" "$cycle/err" > /dev/null && named=named
expect_eq "$name" "2:named:" "$code:$named:$rendered"

name="#935 the transform prompt tells the leaf to give its commit a subject ending in (#<issue>), the convention develop-refactor states"
tf="$("$BUILD" transform "$work/spec.md" "$step_text" "$test_cmd" 2>/dev/null)"; code=$?
suffix=""; grep -F '(#<issue>)' <<<"$tf" | grep -iF 'commit' > /dev/null && suffix=stated
expect_eq "$name" "0:stated" "$code:$suffix"

name="#935 the structural prompt tells the leaf to give its commit a subject ending in (#<issue>), the convention develop-refactor states"
st="$("$BUILD" structural "$work/spec.md" "a candidate" "$test_cmd" "a.sh b.sh" 2>/dev/null)"; code=$?
suffix=""; grep -F '(#<issue>)' <<<"$st" | grep -iF 'commit' > /dev/null && suffix=stated
expect_eq "$name" "0:stated" "$code:$suffix"

name="#935 the diff prompt tells the leaf to give its commit a subject ending in (#<issue>), the convention develop-refactor states"
df="$("$BUILD" diff "$work/spec.md" "$step_text" "$test_cmd" "make unit" 2>/dev/null)"; code=$?
suffix=""; grep -F '(#<issue>)' <<<"$df" | grep -iF 'commit' > /dev/null && suffix=stated
expect_eq "$name" "0:stated" "$code:$suffix"

name="#935 the revise-diff prompt tells the leaf to give its commit a subject ending in (#<issue>), the convention develop-refactor states"
rd="$("$BUILD" revise diff "$work/spec.md" "$dd_step" "$test_cmd" "$work/reason.md" 2>/dev/null)"; code=$?
suffix=""; grep -F '(#<issue>)' <<<"$rd" | grep -iF 'commit' > /dev/null && suffix=stated
expect_eq "$name" "0:stated" "$code:$suffix"

name="#974 the diff prompt tells the leaf to run the given fast command through timed-test-run.sh fast and then the affected suites, and to finish only with both green"
dd_fast='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
ddf="$("$BUILD" diff "$work/spec.md" "$dd_step" "$test_cmd" "$dd_fast" 2>/dev/null)"; code=$?
timed="$(cd "$HERE/.." && pwd)/timed-test-run.sh"
fast_line="$timed fast '' $dd_fast"
fast="" order="" both=""
[[ "$ddf" == *"$fast_line"* ]] && fast=fast
[[ "$ddf" == *"$fast_line"*"$timed affected "* ]] && order=affected-after
grep -iE 'both( runs)?( are| stay)? green' <<<"$ddf" > /dev/null && both=both-green
expect_eq "$name" "0:fast:affected-after:both-green" "$code:$fast:$order:$both"

name="#974 build-develop-prompt.sh diff with the fast command left out exits 2 with a diagnostic on stderr and nothing on stdout"
nofast_err="$work/diff-no-fast.err"
nofast="$("$BUILD" diff "$work/spec.md" "$dd_step" "$test_cmd" 2>"$nofast_err")"; code=$?
diag=""; [[ -s "$nofast_err" ]] && diag=diagnostic
expect_eq "$name" "2::diagnostic" "$code:${nofast:+prompt}:$diag"

finish
