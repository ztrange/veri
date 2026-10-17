#!/usr/bin/env bash
# Tests for scripts/build-verify-prompt.sh — assembles a BLIND verifier leaf's prompt
# from on-disk artifacts only: the issue's behavior spec and the test's path. It has no
# parameter for the developer leaf's rationale, so rationale structurally cannot enter
# the verifier's context (ADR-0003). This is the seam that makes blindness enforceable
# rather than left to the conductor's discretion.
#
# Run: scripts/tests/build-verify-prompt.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BUILD="$HERE/../build-verify-prompt.sh"
source "$HERE/lib/harness.sh"
source "$HERE/lib/probe-order.sh"

work="$(scratch_dir)"

cat > "$work/spec.md" <<'SPEC'
slugify("Hello & World/Foo") must return "hello-world-foo" — see {ref}\n done.
SPEC
testpath="tests/test_slugify.py"
fast_for() { fast=(); [[ "$1" == green || "$1" == refactor ]] && fast=( --fast-cmd 'make unit' ); }

red="$("$BUILD" red "$work/spec.md" "$testpath" test_slugify_lowercases)"

prompt_has() {  # prompt_has <prompt> <grep argument…> — the match itself, folded to one line
  local prompt="$1"; shift
  grep -q "$@" <<<"$(tr '\n' ' ' <<<"$prompt")"
}

# hazard: BSD grep refuses a bounded repetition over 255 and exits non-zero, which reads as a miss.
prompt_says() {  # prompt_says <prompt> <complaint> <grep argument…>
  local prompt="$1" complaint="$2"; shift 2
  prompt_has "$prompt" "$@" || problems="$problems; $complaint"
}

prompt_lacks() {  # prompt_lacks <prompt> <complaint> <grep argument…> — prompt_says inverted
  local prompt="$1" complaint="$2"; shift 2
  ! prompt_has "$prompt" "$@" || problems="$problems; $complaint"
  return 0
}

problems=""
cat > "$work/ledger.md" <<'LEDGER'
# Plan for #426

- [ ] A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧
LEDGER
plan="$("$BUILD" plan "$work/spec.md" "$work/ledger.md")"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$plan" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$plan" == *'A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧'* ]] \
  && ok || no "verify-plan carries the issue spec and the ledger named as its third argument (exit $code)"

name="verify-plan tells the verifier to REJECT a plan whose step drops a constraint the issue attaches to the cases it covers: case size, no production change, an end-to-end path through real processes (#1467)"
flat="$(printf '%s' "$plan" | tr -s '[:space:]' ' ')"
problems=""
[[ "$flat" == *"REJECT a plan whose step drops a constraint the issue attaches to"* ]] || problems="$problems; never says to REJECT a step that drops a constraint the issue attaches to its cases"
[[ "$flat" == *"case size"* ]] || problems="$problems; never names the case size as a constraint"
[[ "$flat" == *"no production change"* ]] || problems="$problems; never names \"no production change\" as a constraint"
[[ "$flat" == *"end-to-end path through real processes"* ]] || problems="$problems; never names the end-to-end path through real processes as a constraint"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

name="verify-plan tells the verifier to REJECT a plan that plans a test-only change, one satisfiable only by editing a test, as a Red/Green step (#1467)"
problems=""
[[ "$flat" == *"REJECT a plan that plans a test-only change"* ]] || problems="$problems; never says to REJECT a plan that plans a test-only change"
[[ "$flat" == *"only by editing a test"* ]] || problems="$problems; never names a change satisfiable only by editing a test"
[[ "$flat" == *"as a Red/Green step"* ]] || problems="$problems; never says the rejected shape is a Red/Green step"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

name="verify-plan tells the verifier to REJECT a plan whose step can only be observed once a later step is built, such as an input-ignored step before the step that reads it, naming both steps (#1550)"
problems=""
[[ "$flat" == *"REJECT a plan in which a step's behaviour can only be observed once a later step is built"* ]] || problems="$problems; never says to REJECT a step whose behaviour can only be observed once a later step is built"
[[ "$flat" == *"ignored, guarded or without effect"* ]] || problems="$problems; never names an input that is ignored, guarded or without effect"
[[ "$flat" == *"even when X is left in"* ]] || problems="$problems; never quotes the \"even when X is left in\" shape"
[[ "$flat" == *"before the step that makes the code read that input"* ]] || problems="$problems; never says the step sits before the step that makes the code read the input"
[[ "$flat" == *"REASON: line names both steps, the early step and the later step it waits on"* ]] || problems="$problems; never says its REASON: line names both steps, the early one and the later one it waits on"
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

cat > "$work/rationale-ledger.md" <<'LEDGER'
# Plan for #439

- [ ] LEDGER-BODY-MARKER a plan step no cycle verifier may be shown ⟦criterion 1⟧
LEDGER
leak_step='RATIONALE-LEAK the developer chose a launcher script because bash -c broke the quoting'
problems=""
plan_only="$("$BUILD" --step "$leak_step" plan "$work/spec.md" "$work/rationale-ledger.md" test_rationale_leak)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; the plan call exited $code"
[[ "$plan_only" == *'slugify("Hello & World/Foo")'* ]] || problems="$problems; the plan prompt drops the issue spec"
[[ "$plan_only" == *'LEDGER-BODY-MARKER'* ]] || problems="$problems; the plan prompt drops the ledger"
[[ "$plan_only" != *'RATIONALE-LEAK'* ]] || problems="$problems; the plan prompt carries the --step text"
[[ "$plan_only" != *'test_rationale_leak'* ]] || problems="$problems; the plan prompt carries the fourth positional"
for phase in red green refactor pin; do
  fast_for "$phase"
  slot=test_slugify_lowercases
  [[ "$phase" == refactor ]] && slot=0123abc  # refactor's fourth slot takes a base sha only (#151)
  cycle="$("$BUILD" "${fast[@]}" "$phase" "$work/spec.md" "$work/rationale-ledger.md" "$slot")"
  [[ "$cycle" == *"$work/rationale-ledger.md"* ]] || problems="$problems; verify-$phase drops the path it was given"
  [[ "$cycle" != *'LEDGER-BODY-MARKER'* ]] || problems="$problems; verify-$phase carries the ledger's text"
done
[[ -z "$problems" ]] && ok || no "verify-plan carries only the issue spec and the ledger, and no cycle phase's prompt carries a ledger (${problems#; })"

cp "$work/spec.md" "$work/bug-spec.md"
cat >> "$work/bug-spec.md" <<'SPEC'

## Bug

### What happened

slugify returned "HELLO_WORLD" on the ampersanded seed.

### Expected

slugify returns "hello-world-foo".

### Steps to reproduce

Call slugify("Hello & World/Foo").

### Environment

veri on bash 5.2, macOS 15.
SPEC

problems=""
bug_red="$("$BUILD" red "$work/bug-spec.md" "$testpath" test_slugify_lowercases 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with a bug spec and red's own four positionals exited $code, want 0"
[[ "$bug_red" == *'slugify returned "HELLO_WORLD" on the ampersanded seed.'* ]] \
  || problems="$problems; does not carry the bug report from the spec"
observed_matches_reported='(match|matches|matching|same as)[^.]{0,80}what happened|what happened[^.]{0,80}(match|matches|matching|same as)'
prompt_says "$bug_red" "never requires the failure it observes to match What happened" \
  -iE -e "$observed_matches_reported"
prompt_lacks "$red" "a spec with no Bug section still requires the failure to match What happened" \
  -iE -e "$observed_matches_reported"
[[ -z "$problems" ]] \
  && ok || no "verify-red requires a bug's observed failure to match What happened, and requires nothing of the kind for a spec with no Bug section (${problems#; })"

diff_step='the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧'
diff_base=0123abcdef diff_fast_cmd="make unit"
branch_base=0123abcdef step_base=4567abcdef
problems=""
diff_refused_as() {  # <label> <want stderr line> <args...> — records a diff call that is not exit 2, empty stdout, <want> first on stderr
  local label="$1" want="$2" out code err; shift 2
  out="$("$BUILD" "$@" 2>"$work/diff-refused.err")"; code=$?
  IFS= read -r err < "$work/diff-refused.err"
  [[ "$code" -eq 2 ]] || problems="$problems; $label exited $code, want 2"
  [[ -z "$out" ]] || problems="$problems; $label printed ${#out} bytes, want none"
  [[ "$err" == "$want" ]] || problems="$problems; $label's first stderr line is '$err', want '$want'"
}
hex_msg() { printf "build-verify-prompt: diff needs %s as 7-40 lowercase hex characters, got '%s'" "$1" "$2"; }
fc=( --fast-cmd "$diff_fast_cmd" )
diff_refused_as 'diff with a non-hex base' "$(hex_msg '<base-sha>' 'tidied the helper')" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" 'tidied the helper' "$diff_base"
diff_refused_as 'diff with no --step' "build-verify-prompt: diff needs --step '<STEP>'" \
  "${fc[@]}" diff "$work/spec.md" "$diff_base" "$diff_base"
diff_refused_as 'diff with no step base' "$(hex_msg '<step-base-sha>' '')" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$branch_base"
diff_refused_as 'diff with a non-hex step base' "$(hex_msg '<step-base-sha>' 'tidied the helper')" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$branch_base" 'tidied the helper'
diff_refused_as 'diff with an uppercase step base' "$(hex_msg '<step-base-sha>' 4567ABCDEF)" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$branch_base" 4567ABCDEF
diff_refused_as 'diff with a 6-character step base' "$(hex_msg '<step-base-sha>' 4567ab)" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$branch_base" 4567ab
[[ -z "$problems" ]] \
  && ok || no "#995 diff with --fast-cmd refuses a non-hex base, a missing --step and a missing, non-hex, uppercase or 6-character step base, each with exit 2, nothing on stdout and its own check's message on stderr (${problems#; })"

problems=""
diff_refused_as 'diff with an extra positional' "build-verify-prompt: too many arguments" \
  --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$diff_base" "$diff_base" extra
[[ -z "$problems" ]] \
  && ok || no "#1041 diff with --fast-cmd refuses an extra positional argument with exit 2, nothing on stdout and the extra-argument check's message on stderr (${problems#; })"

problems=""
diff_prompt="$("$BUILD" --step "$diff_step" "${fc[@]}" diff "$work/spec.md" "$branch_base" "$step_base")"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$diff_prompt" "never says the wrapper hands the exit status straight back" \
  -F -e "The wrapper hands the command's own exit status straight back, so a red run stays red."
[[ -z "$problems" ]] \
  && ok || no "a diff prompt tells the verifier the wrapper hands the test command's own exit status straight back, so a red run stays red (${problems#; })"

scripts_dir="$(cd "$HERE/.." && pwd)"

name="run through a symlink to the scripts directory from another working directory, red, green and diff calls answer as in place, but the timed-test-run.sh path names the symlink as called"
linked="$(scratch_dir)"
ln -s "$scripts_dir" "$linked/veri-scripts"
problems=""
same_through_link() {  # <label> <args...> — records a call whose answer through the link differs from in place
  local label="$1"; shift
  local want_out want_err want_code got_out got_err got_code
  want_out="$("$BUILD" "$@" 2>"$linked/want-err")"; want_code=$?
  got_out="$(cd "$linked" && ./veri-scripts/build-verify-prompt.sh "$@" 2>"$linked/got-err")"; got_code=$?
  want_err="$(cat "$linked/want-err")"; got_err="$(cat "$linked/got-err")"
  [[ "$want_out" == *"$scripts_dir/timed-test-run.sh"* ]] || problems="$problems; $label in place names no $scripts_dir/timed-test-run.sh"
  want_out="${want_out//"$scripts_dir/timed-test-run.sh"/"$linked/veri-scripts/timed-test-run.sh"}"
  [[ "$got_code" == "$want_code" ]] || problems="$problems; $label exited $got_code through the link, $want_code in place"
  [[ "$got_out" == "$want_out" ]] || problems="$problems; $label stdout differs through the link"
  [[ "$got_err" == "$want_err" ]] || problems="$problems; $label stderr differs through the link"
}
same_through_link red red "$work/spec.md" "$testpath" test_slugify_lowercases
same_through_link green --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases
same_through_link diff --step 's' --fast-cmd 'make unit' diff "$work/spec.md" 0123abc 4567def
[[ -z "$problems" ]] && ok || no "$name (${problems#; })"

finish
