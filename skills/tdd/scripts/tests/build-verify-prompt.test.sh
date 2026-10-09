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

[[ "$red" == *'slugify("Hello & World/Foo")'* ]] && ok || no "carries issue spec verbatim"

"$BUILD" bogus "$work/spec.md" "$testpath" >/dev/null 2>&1; code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (got $code)"

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

prompts="$HERE/../prompts"
problems=""
probe_order verify-green "$(cat "$prompts/verify-green.md")" 'remove the code yourself' \
  'remove the code yourself[^.]{0,40}run[^.]{0,40}suites'
[[ -z "$problems" ]] && ok \
  || no "#619 verify-green restores a probe with cp <file> <file>.orig before the mutation and mv <file>.orig <file> after the run under mutation (${problems#; })"

problems=""
probe_order verify-pin "$(cat "$prompts/verify-pin.md")" 'break it yourself' 'run the target test again'
[[ -z "$problems" ]] && ok \
  || no "#619 verify-pin restores a probe with cp <file> <file>.orig before the mutation and mv <file>.orig <file> after the run under mutation (${problems#; })"

problems=""
for label in verify-green verify-pin develop-cover; do
  prompt="$(cat "$prompts/$label.md")"
  prompt_says "$prompt" "$label never compares git diff with what it printed before the probe" \
    -iE -e "git diff[^.]{0,120}(before|earlier)[^.]{0,40}(probe|mutat)|(probe|mutat)[^.]{0,120}git diff[^.]{0,120}(before|earlier)"
  prompt_lacks "$prompt" "$label still names git checkout --" -F -e 'git checkout --'
  prompt_lacks "$prompt" "$label still names git diff --exit-code" -E -e 'git diff[[:space:]]+--exit-code'
done
[[ -z "$problems" ]] && ok \
  || no "#619 verify-green, verify-pin and develop-cover confirm the restore by comparing git diff with what it printed before the probe, and name neither git checkout -- nor git diff --exit-code (${problems#; })"

problems=""
stash_rule='**Never run `git stash`**: the stash stack is one ref, `refs/stash`, in a `.git` shared by
every worktree of this repository, so what you pop may be another agent'"'"'s work — and theirs
is then lost. To see the committed version of a file, read it with `git show HEAD:<path>`;
to compare a whole tree against it, make a throwaway checkout with
`git worktree add --detach <scratch> HEAD` and remove it afterwards.'
for shared in _shared _develop-shared; do
  [[ "$(cat "$prompts/$shared.md")" == *"$stash_rule"* ]] \
    || problems="$problems; $shared.md no longer carries the git stash rule verbatim"
done
[[ -z "$problems" ]] && ok \
  || no "#619 _shared.md and _develop-shared.md keep the git stash rule unchanged, recommending git show HEAD:<path> and git worktree add --detach <scratch> HEAD (${problems#; })"

problems=""
forbidding='Never undo a probe with[[:space:]]`git checkout -- <file>` or `git restore`'
for file in "$prompts"/*; do
  name="${file##*/}"
  text="$(cat "$file")"
  [[ "$text" == *'git stash push'* ]] && problems="$problems; $name contains git stash push"
  case "$name" in
    _shared.md|_develop-shared.md)
      [[ "$text" == *$forbidding* ]] \
        || problems="$problems; $name lacks the sentence forbidding git checkout -- <file>"
      text="${text//$forbidding/}" ;;
  esac
  [[ "$text" == *'git checkout --'* ]] \
    && problems="$problems; $name names git checkout -- outside the sentence that forbids it"
done
[[ -z "$problems" ]] && ok \
  || no "#619 no prompt contains git stash push, and git checkout -- <file> appears only in _shared.md and _develop-shared.md inside the sentence that forbids it (${problems#; })"

problems=""
numbered_item() {  # numbered_item <prompt file> <n> — the text of list item <n>., up to item <n+1>.
  awk -v n="$2" '$0 ~ "^" n "\\. " { on = 1 } $0 ~ "^" (n + 1) "\\. " { on = 0 } on' "$1"
}
for item in verify-green:4 verify-pin:2 develop-cover:4; do
  label="${item%%:*}" n="${item#*:}"
  text="$(numbered_item "$prompts/$label.md" "$n")"
  prompt_says "$text" "$label item $n never restores with mv <file>.orig <file>" -F -e 'mv <file>.orig <file>'
  case "$label" in
    develop-cover)
      prompt_says "$text" "$label item $n never requires the tree exactly as the leaf found it" \
        -iE -e 'working tree must be exactly as you found it' ;;
    *)
      prompt_says "$text" "$label item $n never requires the restore before reporting" \
        -F -e 'before you report' ;;
  esac
done
[[ -z "$problems" ]] && ok \
  || no "#619 verify-green check 4 and verify-pin check 2 restore before the verifier reports, and develop-cover step 4 leaves the working tree exactly as the leaf found it (${problems#; })"

cat > "$work/ledger.md" <<'LEDGER'
# Plan for #426

- [ ] A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧
LEDGER
plan="$("$BUILD" plan "$work/spec.md" "$work/ledger.md")"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$plan" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$plan" == *'A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧'* ]] \
  && ok || no "verify-plan carries the issue spec and the ledger named as its third argument (exit $code)"

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
