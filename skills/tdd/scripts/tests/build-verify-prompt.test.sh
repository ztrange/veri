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

[[ "$red" == *"$testpath"* ]] && ok || no "names the test path"

grep -qiE 'have not (been told|received).*(reason|rationale)|never.*(reason|rationale)' \
  <<<"$red" && ok || no "states the blindness contract"

grep -q 'VERDICT:' <<<"$red" && grep -qi 'PASS' <<<"$red" && grep -qi 'REJECT' <<<"$red" \
  && ok || no "instructs the VERDICT: PASS|REJECT format"

grep -qi 'right reason' <<<"$red" && grep -qiE 'trivial|coupled|complex' <<<"$red" \
  && ok || no "verify-red audits right-reason + quality"

green="$("$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
grep -qi 'full' <<<"$green" && grep -qi 'suite' <<<"$green" \
  && ok || no "verify-green checks the full suite"

refactor="$("$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" 0123abc)"  # refactor's 4th slot is a base sha (#151)
grep -qiE 'standard|convention|typing|robust' <<<"$refactor" \
  && grep -qi 'green' <<<"$refactor" && ok || no "verify-refactor judges standard + green"

"$BUILD" bogus "$work/spec.md" "$testpath" >/dev/null 2>&1; code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (got $code)"

pin="$("$BUILD" pin "$work/spec.md" "$testpath" test_slugify_lowercases)"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$pin" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$pin" == *"$testpath"* ]] \
  && grep -qiE 'pass(es)? (now|today|already|against|on the (current|unmodified))' <<<"$pin" \
  && grep -qi 'mutation' <<<"$pin" \
  && grep -qiE 'behaviou?r-level|trivial' <<<"$pin" \
  && ok || no "verify-pin carries spec + test path and the three pin checks (exit $code)"

full_suite='full[^[:alnum:]]*test[^[:alnum:]]*suite'
grep -qiE "$full_suite" <<<"$green" \
  && ok || no "verify-green still requires the full test suite"

smuggled='ran only tests/test_slugify.py, the suite I touched, because the rest is slow'
extra="$("$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases "$smuggled" 2>/dev/null)"; code=$?
[[ "$code" -eq 2 && -z "$extra" ]] \
  && ok || no "a green call with an extra positional argument beyond the target test id exits 2 with nothing on stdout (exit $code, ${#extra} bytes on stdout)"

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

every_phase() {  # every_phase <name of a check function taking <phase label> <prompt>> <headline>
  local check="$1" headline="$2" problems=""
  "$check" red "$red"; "$check" green "$green"; "$check" refactor "$refactor"; "$check" pin "$pin"
  [[ -z "$problems" ]] && ok || no "$headline (${problems#; })"
}

demands_foreground() {  # demands_foreground <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never says to run test commands in the foreground" \
    -i -e 'foreground'
  prompt_says "$prompt" "verify-$label never forbids ending the turn mid-run" \
    -iE -e 'end(ing)?[^[:alnum:]]+(your|the|its)[^[:alnum:]]+turn'
}

every_phase demands_foreground "every phase's prompt carries the foreground rule"

forbids_stash() {  # forbids_stash <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never forbids git stash" \
    -iE -e "(never|do not|don't|no)[^.]{0,60}stash"
  prompt_says "$prompt" "verify-$label names no shared-ref-free way to see the committed version" \
    -E -e 'git show HEAD:|git worktree add'
}

every_phase forbids_stash "every phase's prompt forbids git stash and names a safe alternative"

base="$(env -u VERI_TEST_CMD "$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
ambient="$(VERI_TEST_CMD='pytest -k leaked_channel' "$BUILD" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases)"
[[ "$ambient" == "$base" ]] && ok || no "VERI_TEST_CMD in the environment reaches nothing (arguments unchanged)"

prediction='the second assert fires: want "hello-world-foo", got "Hello & World/Foo"'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  smuggled_prompt="$(VERI_PREDICTED_FAILURE="$prediction" \
    "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4" "$prediction")"
  [[ "$smuggled_prompt" == *"$prediction"* ]] \
    && problems="$problems; verify-$phase carries the prediction text"
  grep -qiE 'PREDICTED_FAILURE|PREDICTION' <<<"$smuggled_prompt" \
    && problems="$problems; verify-$phase asks for a prediction"
done
[[ -z "$problems" ]] && ok || no "no verifier prompt carries the prediction (${problems#; })"

base_sha='3f9a1c07e2b4'
with_base="$("$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$base_sha")"; code=$?
[[ "$code" -eq 0 ]] && [[ "$with_base" == *"$base_sha"* ]] \
  && ok || no "verify-refactor carries the base sha from its 4th argument into the prompt (exit $code)"

problems=""
probe_base() {  # probe_base <label> [<base-sha>]
  local label="$1"; shift
  local err="$work/base-sha.err" rc
  "$BUILD" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$@" >/dev/null 2>"$err"; rc=$?
  if [[ "$rc" -ne 2 || ! -s "$err" ]]; then
    problems="$problems; $label: exit $rc, stderr $([[ -s "$err" ]] && echo present || echo empty)"
  fi
}
probe_base missing
probe_base short abc123
probe_base uppercase 3F9A1C07E2B4
probe_base with-text '3f9a1c07e2b4 because it tidies'
probe_base too-long 3f9a1c07e2b43f9a1c07e2b43f9a1c07e2b43f9a1
[[ -z "$problems" ]] && ok \
  || no "verify-refactor refuses a missing or malformed base sha with exit 2 and a stderr diagnostic (${problems#; })"

problems=""
prompt_says "$with_base" "never names git diff $base_sha..HEAD" -F -e "git diff $base_sha..HEAD"
prompt_says "$with_base" "never forbids reading the range's commit messages" \
  -iE -e "(never|not|don't|no)[^.]{0,80}commit messages"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reviews git diff <base-sha>..HEAD and not the range's commit messages (${problems#; })"

problems=""
prompt_says "$with_base" "never makes a removed or weakened test assertion a REJECT" \
  -iE -e "(removed|weakened)[^.]{0,80}assertion[^.]{0,120}REJECT|REJECT[^.]{0,120}(removed|weakened)[^.]{0,80}assertion"
prompt_says "$with_base" "never has the REJECT name the assertion" \
  -iE -e "REJECT[^.]{0,120}nam(e|es|ing)[^.]{0,40}assertion"
prompt_says "$with_base" "never names cosmetic-only hunks in REASON:" \
  -iE -e "cosmetic[^.]{0,160}REASON:"
prompt_says "$with_base" "never says a cosmetic-only hunk is not a REJECT by itself" \
  -iE -e "cosmetic[^.]{0,200}(not|never|no)[^.]{0,60}REJECT"
prompt_says "$with_base" "never says an empty range is not a REJECT by itself" \
  -iE -e "empty (range|diff)[^.]{0,160}(not|never|no)[^.]{0,60}REJECT"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor rejects a weakened assertion by name, names cosmetic hunks without rejecting, and does not reject an empty range (${problems#; })"

step='frobnicate --dry-run prints the plan and writes nothing ⟦criterion 3⟧'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  stepped="$("$BUILD" --step "$step" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4" 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || problems="$problems; verify-$phase exits $code"
  [[ "$stepped" == *"$step"* ]] || problems="$problems; verify-$phase never shows the step"
  prompt_says "$stepped" "verify-$phase never says the verdict is about that criterion only" \
    -iE -e 'verdict[^.]{0,160}(criterion|step)[^.]{0,40}only|verdict[^.]{0,160}only[^.]{0,40}(criterion|step)'
done
[[ -z "$problems" ]] && ok \
  || no "--step shows the step in every verifier prompt and scopes the verdict to it (${problems#; })"

ambient_step='frobnicate --dry-run prints the plan and writes nothing ⟦criterion 9⟧'
problems=""
for phase in red green refactor pin; do
  slot4=test_slugify_lowercases; [[ "$phase" == refactor ]] && slot4=0123abc  # a base sha (#151)
  fast_for "$phase"
  unset_arm="$(env -u VERI_STEP "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4")"
  ambient_arm="$(VERI_STEP="$ambient_step" "$BUILD" "${fast[@]+"${fast[@]}"}" "$phase" "$work/spec.md" "$testpath" "$slot4")"
  [[ "$ambient_arm" == *"$ambient_step"* ]] \
    && problems="$problems; verify-$phase carries the ambient VERI_STEP text"
  [[ "$ambient_arm" == "$unset_arm" ]] \
    || problems="$problems; verify-$phase differs from the prompt built with VERI_STEP unset"
done
[[ -z "$problems" ]] && ok \
  || no "VERI_STEP in the environment with no --step reaches nothing (${problems#; })"

scoped_refactor="$("$BUILD" --step "$step" --fast-cmd 'make unit' refactor "$work/spec.md" "$testpath" "$base_sha")"
problems=""
prompt_says "$scoped_refactor" "never sends a shortfall against a criterion outside the step to REASON: as out of scope" \
  -iE -e "out of scope[^.]{0,200}REASON:|REASON:[^.]{0,200}out of scope"
prompt_says "$scoped_refactor" "never says an out-of-scope shortfall is not by itself a REJECT" \
  -iE -e "outside[^.]{0,240}(not|never|no)[^.]{0,80}REJECT|out of scope[^.]{0,240}(not|never|no)[^.]{0,80}REJECT"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor notes an out-of-scope shortfall in REASON: rather than rejecting for it (${problems#; })"

forbids_global_config() {  # forbids_global_config <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never forbids changing global or user-level configuration" \
    -iE -e "(never|do not|don't|not)[^.]{0,80}(global|user-level)[^.]{0,60}config"
  prompt_says "$prompt" "verify-$label never names environment variables as the way to simulate a condition" \
    -iE -e 'environment variables?'
  prompt_says "$prompt" "verify-$label never names throwaway directories as the way to simulate a condition" \
    -iE -e '(throwaway|temporary|scratch)[^.]{0,20}director(y|ies)'
}

every_phase forbids_global_config "every phase's prompt forbids changing global or user-level configuration and names environment variables and throwaway directories instead"

problems=""
mechanism_reject() {  # mechanism_reject <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label never rejects a test that pins a process/fork count or a timing" \
    -iE -e '(process|fork)[^.]{0,20}count|timing'
  prompt_says "$prompt" "verify-$label never carves out an in-process spy for a call count the criterion names" \
    -iE -e 'in-process spy'
  prompt_says "$prompt" "verify-$label never rejects a PATH shim counting real processes over a spy" \
    -iE -e 'PATH[^.]{0,60}shim|shim[^.]{0,60}(count|real process)'
  prompt_says "$prompt" "verify-$label never rejects a test that runs another suite or re-runs its own" \
    -iE -e '(runs?|running)[^.]{0,40}(another|other)[^.]{0,20}suite|re-runs?[^.]{0,30}suite'
}
mechanism_reject red "$red"
mechanism_reject pin "$pin"
[[ -z "$problems" ]] && ok \
  || no "verify-red and verify-pin reject mechanism-pinning tests (process/fork/timing, a PATH shim over an in-process spy, or running another suite) (${problems#; })"

fast_cmd='make unit ZORBLAT=fast -- --only "frob & nitz/quux"'
problems=""
fast_green="$("$BUILD" --fast-cmd "$fast_cmd" green "$work/spec.md" "$testpath" test_slugify_lowercases 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; with --fast-cmd exited $code, want 0"
[[ "$fast_green" == *"$fast_cmd"* ]] || problems="$problems; the prompt does not carry --fast-cmd's value verbatim"
"$BUILD" green "$work/spec.md" "$testpath" test_slugify_lowercases >/dev/null 2>"$work/fast-cmd.err"; code=$?
[[ "$code" -eq 2 && -s "$work/fast-cmd.err" ]] \
  || problems="$problems; without --fast-cmd: exit $code, stderr $([[ -s "$work/fast-cmd.err" ]] && echo present || echo empty), want exit 2 and a diagnostic"
[[ -z "$problems" ]] \
  && ok || no "verify-green takes --fast-cmd, carries it verbatim, and refuses a green call without it with exit 2 (${problems#; })"

problems=""
prompt_says "$red" "verify-red never says an error on exactly the name the step introduces is a valid red" \
  -iE -e "error[^.]{0,160}(exactly the name|the exact name)[^.]{0,200}(valid|legitimate) red|(valid|legitimate) red[^.]{0,200}error[^.]{0,160}(exactly the name|the exact name)"
prompt_says "$red" "verify-red never says a missing script or file is one of the names that qualify" \
  -iE -e "(missing|absent)[^.]{0,120}(script|file)[^.]{0,120}(route|field)"
[[ -z "$problems" ]] && ok \
  || no "verify-red accepts an error on exactly the name the step introduces as a valid red (${problems#; })"

problems=""
prompt_says "$red" "verify-red never says any other error before an assertion is a REJECT" \
  -iE -e "any [^.]{0,20}other[^.]{0,20} error[^.]{0,60}before[^.]{0,40}assertion[^.]{0,80}REJECT"
prompt_says "$red" "verify-red names no typo'd name among the errors it still rejects" \
  -iE -e "typo"
prompt_says "$red" "verify-red names no wrong path among the errors it still rejects" \
  -iE -e "wrong path|incorrect path|path that does not exist"
prompt_says "$red" "verify-red names no missing fixture among the errors it still rejects" \
  -iE -e "(missing|absent) fixture"
prompt_says "$red" "verify-red names no syntax error among the errors it still rejects" \
  -iE -e "syntax error"
[[ -z "$problems" ]] && ok \
  || no "verify-red still rejects any other error before an assertion: a typo'd name, a wrong path, a missing fixture, a syntax error (${problems#; })"

problems=""
one_line="$(tr '\n' ' ' <<<"$red")"
grep -qiE -e "(must|has to|should)[^.]{0,100}not error before[^.]{0,60}assertion" <<<"$one_line" \
  && problems="$problems; verify-red still forbids a failure that errors before it reaches its assertions"
grep -qiE -e "(must|has to|should)[^.]{0,100}reach(es)? its assertions" <<<"$one_line" \
  && problems="$problems; verify-red still requires the target test to reach its assertions"
[[ -z "$problems" ]] && ok \
  || no "verify-red no longer requires the target test to reach its assertions (${problems#; })"

problems=""
prompt_says "$green" "verify-green never makes production code no test requires a REJECT" \
  -iE -e "REJECT[^.]{0,200}code[^.]{0,80}no test requires|code[^.]{0,80}no test requires[^.]{0,200}REJECT"
prompt_says "$green" "verify-green never names a branch, option, flag or parameter as the code it means" \
  -iE -e "branch[^.]{0,80}option[^.]{0,80}flag[^.]{0,80}parameter"
prompt_says "$green" "verify-green never says removing it leaves every test green" \
  -iE -e "remov(e|ed|ing|al)[^.]{0,140}(leaves?|leaving)[^.]{0,60}tests? green|remov(e|ed|ing|al)[^.]{0,140}(every|all) tests? [^.]{0,40}green"
prompt_says "$green" "verify-green never has REASON: name that code" \
  -iE -e "REASON:?[^.]{0,160}nam(e|es|ing)[^.]{0,60}code|nam(e|es|ing)[^.]{0,60}code[^.]{0,160}REASON"
[[ -z "$problems" ]] && ok \
  || no "verify-green REJECTs production code no test requires and names it in REASON: (${problems#; })"

problems=""
prompt_says "$green" "verify-green never says to remove the code and run the suite" \
  -iE -e "remov(e|ing)[^.]{0,120}run[^.]{0,80}suite"
prompt_says "$green" "verify-green never says to restore the tree afterwards" \
  -iE -e "restor(e|ing)[^.]{0,80}(tree|code|file)"
prompt_says "$green" "verify-green never says the restore comes before reporting" \
  -iE -e "before[^.]{0,60}report"
[[ -z "$problems" ]] && ok \
  || no "verify-green tells the verifier to remove the code, run the suite, and restore the tree before reporting (${problems#; })"

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
prompt_says "$red" "never forbids git checkout -- <file>" \
  -iE -e "(never|do not|don't|not)[^.]{0,120}git checkout -- <file>"
prompt_says "$red" "never forbids git restore" \
  -iE -e "(never|do not|don't|not)[^.]{0,160}git restore"
prompt_says "$red" "never ties the rule to undoing a probe" \
  -iE -e "(undo|restor)[^.]{0,60}(probe|mutat)"
prompt_says "$red" "never names cp <file> <file>.orig" -F -e 'cp <file> <file>.orig'
prompt_says "$red" "never names mv <file>.orig <file>" -F -e 'mv <file>.orig <file>'
[[ -z "$problems" ]] && ok \
  || no "#619 _shared.md forbids git checkout -- <file> and git restore for undoing a probe and names cp <file> <file>.orig / mv <file>.orig <file> instead (${problems#; })"

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

problems=""
prompt_says "$with_base" "never names git diff --name-only $base_sha^ $base_sha" \
  -F -e "git diff --name-only $base_sha^ $base_sha"
prompt_says "$with_base" "never makes a changed file outside that list a REJECT" \
  -iE -e "outside[^.]{0,80}list[^.]{0,160}REJECT|REJECT[^.]{0,160}outside[^.]{0,80}list"
prompt_says "$with_base" "never spares the hunk that removes duplication with code in the list" \
  -iE -e "(unless|except)[^.]{0,160}duplication|duplication[^.]{0,160}(unless|except)"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor derives the cycle's files as git diff --name-only <base-sha>^ <base-sha> and REJECTs a changed file outside that list unless its hunk removes duplication with code in it (${problems#; })"

problems=""
prompt_says "$refactor" "verify-refactor never ties FLAGS: to an unhandled edge case the spec implies" \
  -iE -e "unhandled edge case[^.]{0,200}FLAGS|FLAGS[^.]{0,200}unhandled edge case"
prompt_says "$refactor" "verify-refactor never puts the FLAGS: line before the VERDICT: line" \
  -iE -e "FLAGS[^.]{0,120}before[^.]{0,120}VERDICT"
prompt_says "$refactor" "verify-refactor never says an unhandled edge case is not a REJECT" \
  -iE -e "(edge case|robust)[^.]{0,200}not( by itself)? a REJECT|not( by itself)? a REJECT[^.]{0,200}(edge case|robust)"
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reports an unhandled edge case the spec implies as a FLAGS: line before VERDICT: rather than a REJECT (${problems#; })"

allows_flags() {  # allows_flags <phase label> <prompt>
  local label="$1" prompt="$2"
  prompt_says "$prompt" "verify-$label's output contract never allows a FLAGS: line" \
    -iE -e "FLAGS[^.]{0,200}(may|can|allow|permit)|(may|can|allow|permit)[^.]{0,200}FLAGS"
  prompt_says "$prompt" "verify-$label never puts FLAGS: lines before the final VERDICT:/REASON: pair" \
    -iE -e "FLAGS[^.]{0,160}before[^.]{0,160}(VERDICT|(final|last)[^.]{0,40}two lines)"
}

every_phase allows_flags "every phase's prompt allows FLAGS: lines before the final VERDICT:/REASON: pair"

cat > "$work/ledger.md" <<'LEDGER'
# Plan for #426

- [ ] A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧
LEDGER
plan="$("$BUILD" plan "$work/spec.md" "$work/ledger.md")"; code=$?
[[ "$code" -eq 0 ]] \
  && [[ "$plan" == *'slugify("Hello & World/Foo")'* ]] \
  && [[ "$plan" == *'A verdict launcher script runs verify.sh with the step title as an argument ⟦criterion 1⟧'* ]] \
  && ok || no "verify-plan carries the issue spec and the ledger named as its third argument (exit $code)"


no_ledger="$("$BUILD" plan "$work/spec.md" 2>/dev/null)"; code=$?
missing_ledger="$("$BUILD" plan "$work/spec.md" "$work/absent-ledger.md" 2>/dev/null)"; missing_code=$?
[[ "$code" -eq 2 && -z "$no_ledger" ]] \
  && [[ "$missing_code" -eq 2 && -z "$missing_ledger" ]] \
  && ok || no "verify-plan refuses a call naming no ledger or an unreadable one with exit 2 and no stdout (no ledger: exit $code, ${#no_ledger} bytes; unreadable: exit $missing_code, ${#missing_ledger} bytes)"


problems=""
prompt_says "$plan" "never asks whether the steps tagged for a criterion together deliver it" \
  -iE -e 'together[^.]{0,200}deliver|deliver[^.]{0,200}together'
prompt_says "$plan" "never sets the criterion's own wording as the standard" \
  -iE -e 'as written|in its own terms|the criterion.{0,20}own (words|terms|wording)'
prompt_says "$plan" "never requires a REJECT reason to name the criterion and what no step covers" \
  -iE -e 'REJECT[^.]{0,120}(name|identif|say|state)[^.]{0,200}criterion[^.]{0,200}(no step|nothing[^.]{0,40}cover|uncovered)'
[[ -z "$problems" ]] && ok || no "verify-plan asks whether the steps tagged for a criterion together deliver it as written, and binds a REJECT reason to the criterion and the part no step covers (${problems#; })"


problems=""
prompt_says "$plan" "never directs a PASS when every criterion is delivered by the steps tagged for it" \
  -iE -e 'PASS[^.]{0,200}every criterion[^.]{0,200}(deliver|cover)|every criterion[^.]{0,200}(deliver|cover)[^.]{0,200}PASS'
[[ -z "$problems" ]] && ok || no "verify-plan directs a PASS when every criterion is delivered by the steps tagged for it (${problems#; })"


problems=""
prompt_says "$plan" "never judges a step too big for one Red → Green → Refactor cycle" \
  -iE -e '(too (big|large)|too much|does not fit|not fit)[^.]{0,150}cycle'
prompt_says "$plan" "never sends that step's name to the reason" \
  -iE -e '(name|names|say so|state)[^.]{0,100}(REASON:|reason\b)'
prompt_says "$plan" "never holds the duty whether the verdict is PASS or REJECT" \
  -iE -e '(whether|either way|regardless)[^.]{0,100}(PASS|REJECT|verdict)'
[[ -z "$problems" ]] && ok || no "verify-plan requires a step too big for one Red → Green → Refactor cycle to be named in the reason under either verdict (${problems#; })"


problems=""
gap_step='gap step|untagged|no[^.]{0,20}criterion[^.]{0,20}tag'  # the untagged step, named once for the two probes that look for it
prompt_says "$plan" "never names a step carrying no criterion tag" \
  -iE -e "$gap_step|(carries|carrying|with|without|has) no[^.]{0,40}criterion"
prompt_says "$plan" "never says such a step is not a REJECT" \
  -iE -e "($gap_step)[^.]{0,200}(not|never|no)[^.]{0,80}REJECT"
prompt_says "$plan" "never carries the by-itself qualifier on that exemption" \
  -iE -e '(by itself|on its own|alone|in itself)[^.]{0,100}REJECT|REJECT[^.]{0,100}(by itself|on its own|alone|in itself)'
[[ -z "$problems" ]] && ok || no "verify-plan states that a step carrying no criterion tag is never by itself a reason to REJECT (${problems#; })"


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


problems=""
prompt_says "$plan" "never makes a mechanism step deliver the criterion only when that mechanism is sufficient for it" \
  -iE -e 'mechanism[^.]{0,200}(sufficient|suffices|enough)|(sufficient|suffices|enough)[^.]{0,200}mechanism'
prompt_says "$plan" "never directs a REJECT when no step establishes the criterion as written" \
  -iE -e 'REJECT[^.]{0,200}(no step|nothing)[^.]{0,150}(establish|deliver)|(no step|nothing)[^.]{0,150}(establish|deliver)[^.]{0,200}REJECT'
[[ -z "$problems" ]] && ok || no "verify-plan makes a mechanism step deliver a criterion only when the mechanism is sufficient for it as written, and directs a REJECT when no step establishes the criterion (${problems#; })"

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


problems=""
prompt_says "$refactor" "no FLAGS: line" -F -e 'FLAGS:'
for class in overfit uncovered-spec beyond-spec; do
  prompt_says "$refactor" "does not name the $class class" -F -e "$class"
done
prompt_lacks "$refactor" "still asks for a NEW_STEP: line" -F -e 'NEW_STEP'
[[ -z "$problems" ]] && ok \
  || no "verify-refactor reports a finding on a FLAGS: line carrying the overfit, uncovered-spec or beyond-spec class, never on a NEW_STEP: line (${problems#; })"

problems=""
rb_onto='8d05a4410c2e' rb_pre='278252a1b9f3'
rebase_prompt="$("$BUILD" rebase "$work/spec.md" "$rb_onto" "$rb_pre" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; exit $code, want 0"
[[ "$rebase_prompt" == *'slugify("Hello & World/Foo")'* ]] || problems="$problems; spec not carried verbatim"
[[ "$rebase_prompt" == *"$rb_onto"* ]] || problems="$problems; no onto sha"
[[ "$rebase_prompt" == *"$rb_pre"* ]] || problems="$problems; no pre-rebase sha"
[[ "$rebase_prompt" != *'{{'* ]] || problems="$problems; an unfilled {{placeholder}} left in the prompt"
prompt_says "$rebase_prompt" "does not tell the verifier to run the full test command" -iE -e 'full[^.]{0,80}(test|suite)'
prompt_says "$rebase_prompt" "does not name HEAD as what is tested" -F -e 'HEAD'
prompt_says "$rebase_prompt" "does not name the default branch's changes" -iE -e 'default branch'
prompt_says "$rebase_prompt" "does not ask that both sides' changes survive" \
  -iE -e 'both[^.]{0,200}(surviv|preserv|intact|kept)|(surviv|preserv|intact|kept)[^.]{0,200}both'
probe_rebase_sha() {  # probe_rebase_sha <label> <onto-sha> <pre-rebase-sha>
  local label="$1" out rc
  out="$("$BUILD" rebase "$work/spec.md" "$2" "$3" 2>/dev/null)"; rc=$?
  [[ "$rc" -eq 2 && -z "$out" ]] || problems="$problems; $label: exit $rc, ${#out} bytes on stdout, want exit 2 and none"
}
probe_rebase_sha "short onto" abc123 "$rb_pre"
probe_rebase_sha "uppercase onto" 8D05A4410C2E "$rb_pre"
probe_rebase_sha "onto with text" "$rb_onto because it merged" "$rb_pre"
probe_rebase_sha "short pre-rebase" "$rb_onto" abc123
probe_rebase_sha "uppercase pre-rebase" "$rb_onto" 278252A1B9F3
probe_rebase_sha "pre-rebase with text" "$rb_onto" "$rb_pre because it was green"
[[ -z "$problems" ]] && ok \
  || no "verify-rebase renders from the spec and the two shas alone, tells the verifier to run the full test command on HEAD and judge that both the branch's and the default branch's changes survive, and refuses a sha that is not 7-40 lowercase hex with exit 2 and no stdout (${problems#; })"

plan_rejects_shape() {
  local marker="$1" shape="$2" ere="$3"
  prompt_says "$plan" "never names the ⟦$marker⟧ marker" -F -e "⟦$marker⟧"
  prompt_says "$plan" "never directs a REJECT for a criterion $shape" \
    -iE -e "REJECT[^.]{0,200}$ere|$ere[^.]{0,200}REJECT"
  prompt_says "$plan" "never sets a Red/Green step against the ⟦$marker⟧ line it should have been" \
    -iE -e "Red[^.]{0,40}Green[^.]{0,200}$marker|$marker[^.]{0,200}Red[^.]{0,40}Green"
}
problems=""
plan_rejects_shape full-suite "whose only observable is the test command passing" \
  '(test command|suites?)[^.]{0,120}pass'
[[ -z "$problems" ]] && ok || no "verify-plan REJECTs a plan that makes a criterion whose only observable is the test command passing a Red/Green step instead of a ⟦full-suite⟧ line (#481) (${problems#; })"

problems=""
plan_rejects_shape human-owed "whose deliverable is the record of a manual check" \
  '(manual|human)[^.]{0,120}(check|record)'
[[ -z "$problems" ]] && ok || no "verify-plan REJECTs a plan that makes a criterion whose deliverable is the record of a manual check a Red/Green step instead of a ⟦human-owed⟧ line (#481) (${problems#; })"

problems=""
deliver_verb='deliver(s|ed|ing)?[^a-z]'
for marker in full-suite human-owed; do
  prompt_says "$plan" "never counts a ⟦$marker⟧ line as delivering its criterion" \
    -iE -e "⟦$marker⟧[^.]{0,200}$deliver_verb|$deliver_verb[^.]{0,200}⟦$marker⟧"
done
[[ -z "$problems" ]] && ok || no "verify-plan counts a ⟦full-suite⟧ or ⟦human-owed⟧ line tagged ⟦criterion k⟧ as delivering criterion k, so a plan written that way passes check 1 (#481) (${problems#; })"

problems=""
plan_rejects_shape diff-checked "that is a property of the branch's own diff" 'diff[- ]property'
prompt_says "$plan" "never counts a ⟦diff-checked⟧ line as delivering its criterion" \
  -iE -e "⟦diff-checked⟧[^.]{0,200}$deliver_verb|$deliver_verb[^.]{0,200}⟦diff-checked⟧"
for read in "another suite's source text" "git history"; do
  prompt_says "$plan" "never directs a REJECT for a planned test that reads $read" \
    -iE -e "REJECT[^.]{0,200}$read|$read[^.]{0,200}REJECT"
done
[[ -z "$problems" ]] && ok || no "verify-plan names the diff-property shape, counts a ⟦diff-checked⟧ ⟦criterion k⟧ line as delivering criterion k, and REJECTs a plan that makes such a criterion a Red/Green step or plans a test reading another suite's source text or the git history (${problems#; })"

problems=""
prompt_says "$plan" "never directs a REJECT for a step introducing a branch only a later step's test requires" \
  -iE -e "REJECT[^.]{0,200}branch[^.]{0,200}later step|branch[^.]{0,200}later step[^.]{0,200}REJECT"
prompt_says "$plan" "never requires the REJECT reason to name both the introducing step and the later pinning step" \
  -iE -e "nam(e|es|ing)[^.]{0,40}both[^.]{0,200}introduc[^.]{0,200}pin|nam(e|es|ing)[^.]{0,40}both[^.]{0,200}pin[^.]{0,200}introduc"
[[ -z "$problems" ]] && ok || no "verify-plan REJECTs a plan whose step introduces a branch only a later step's test requires, naming both the introducing step and the later pinning step (${problems#; })"

problems=""
prompt_says "$plan" "never says a step bringing in code after the steps pinning its branches is not a REJECT on ordering grounds" \
  -iE -e "after[^.]{0,80}pin[^.]{0,200}not[^.]{0,40}REJECT|not[^.]{0,40}REJECT[^.]{0,200}after[^.]{0,80}pin"
prompt_says "$plan" "never says a step bringing in only the branches its own test requires is not a REJECT on ordering grounds" \
  -iE -e "only[^.]{0,40}branch[^.]{0,80}own test[^.]{0,200}not[^.]{0,40}REJECT|not[^.]{0,40}REJECT[^.]{0,200}only[^.]{0,40}branch[^.]{0,80}own test"
[[ -z "$problems" ]] && ok || no "verify-plan does not REJECT on ordering grounds a step bringing in code after the steps pinning its branches, or bringing in only the branches its own test requires (${problems#; })"

problems=""
printf '%s\n' 'grep -q "extract_helper" lib/foo.sh' > "$work/predicate.md"
tf_base=0123abcdef
tf="$("$BUILD" transform "$work/spec.md" "$work/predicate.md" "$tf_base" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; transform exited $code, want 0"
[[ "$tf" == *'slugify("Hello & World/Foo")'* ]] || problems="$problems; transform prompt lacks the spec"
[[ "$tf" == *"git diff $tf_base..HEAD"* ]] || problems="$problems; transform prompt never says git diff $tf_base..HEAD"
prompt_lacks "$tf" "transform prompt bounds the diff to a green commit" -iE -e 'green commit'
"$BUILD" transform "$work/spec.md" "$work/predicate.md" 'tidied the helper' >/dev/null 2>&1; code=$?
[[ "$code" -eq 2 ]] || problems="$problems; transform with a non-hex base exited $code, want 2"
"$BUILD" transforms "$work/spec.md" "$work/predicate.md" "$tf_base" >/dev/null 2>&1; code=$?
[[ "$code" -eq 2 ]] || problems="$problems; unknown phase 'transforms' exited $code, want 2"
[[ -z "$problems" ]] \
  && ok || no "transform takes the predicate record and a hex base sha, tells the verifier to judge git diff <base-sha>..HEAD rather than a green commit's files, and an unknown phase is still exit 2 (${problems#; })"

problems=""
diff_step='the dead counted line in the status suite is gone ⟦diff-checked⟧ ⟦criterion 5⟧'
diff_base=0123abcdef diff_fast_cmd="make unit"
dp="$("$BUILD" --step "$diff_step" --fast-cmd "$diff_fast_cmd" diff "$work/spec.md" "$diff_base" "$diff_base" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; diff exited $code, want 0"
[[ "$dp" == *"$diff_step"* ]] || problems="$problems; diff prompt lacks the step text"
[[ "$dp" == *"git diff $diff_base..HEAD"* ]] || problems="$problems; diff prompt never says git diff $diff_base..HEAD"
prompt_says "$dp" "diff prompt never says the diff alone is the evidence" -iE -e "git diff $diff_base\.\.HEAD[^.]{0,200}alone|alone[^.]{0,200}git diff $diff_base\.\.HEAD"
[[ "$dp" == *'VERDICT: PASS'* && "$dp" == *'VERDICT: REJECT'* ]] || problems="$problems; diff prompt lacks VERDICT: PASS and VERDICT: REJECT"
[[ -z "$problems" ]] \
  && ok || no "diff takes --step, the spec and a hex base sha, carries the step text and tells the verifier to judge it against git diff <base-sha>..HEAD alone, answering VERDICT: PASS or VERDICT: REJECT (${problems#; })"

problems=""
prompt_says "$dp" "diff prompt never forbids reading the range's commit messages" \
  -iE -e "(never|not|don't|no)[^.]{0,80}commit messages"
prompt_lacks "$dp" "diff prompt leaves a placeholder unfilled" -F -e '{{'
prompt_lacks "$dp" "diff prompt names a test under review" -F -e 'the target test'
dp_ambient="$(VERI_STEP='I tidied the helper because it was ugly' VERI_RATIONALE='the author meant well' \
  "$BUILD" --step "$diff_step" --fast-cmd "$diff_fast_cmd" diff "$work/spec.md" "$diff_base" "$diff_base" 2>/dev/null)"
[[ "$dp_ambient" == "$dp" ]] || problems="$problems; diff prompt changes with VERI_STEP or VERI_RATIONALE in the environment"
other_base=fedcba9876
dp_other="$("$BUILD" --step "$diff_step" --fast-cmd "$diff_fast_cmd" diff "$work/spec.md" "$other_base" "$other_base" 2>/dev/null)"
[[ "${dp_other//$other_base/$diff_base}" == "$dp" ]] || problems="$problems; diff prompt differs by more than the base sha when only the base sha changes"
[[ -z "$problems" ]] \
  && ok || no "the diff prompt tells the verifier to read git diff <base-sha>..HEAD and not the range's commit messages, and carries nothing but the spec, the step text and the base sha (${problems#; })"

prompt_has "$dp" -iE -e "REJECT[^.]{0,160}(add|adds|added)[^.]{0,40}test|(add|adds|added)[^.]{0,40}test[^.]{0,160}REJECT" \
  && ok || no "the diff prompt tells the verifier to REJECT when the step's commits add a test"

problems=""
branch_base=0123abcdef step_base=4567abcdef
ds="$("$BUILD" --step "$diff_step" --fast-cmd "$diff_fast_cmd" diff "$work/spec.md" "$branch_base" "$step_base" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; diff with a step base exited $code, want 0"
prompt_says "$ds" "never judges the criterion against git diff $branch_base..HEAD" -F -e "git diff $branch_base..HEAD"
prompt_says "$ds" "never confines the adds-a-test REJECT to git diff $step_base..HEAD" \
  -iE -e "(add|adds|added)[^.]{0,40}test[^.]{0,200}git diff $step_base\.\.HEAD|git diff $step_base\.\.HEAD[^.]{0,200}(add|adds|added)[^.]{0,40}test"
[[ -z "$problems" ]] \
  && ok || no "#875 diff takes <branch-base-sha> <step-base-sha>, judges the criterion against git diff <branch-base-sha>..HEAD and REJECTs only a test added in git diff <step-base-sha>..HEAD (${problems#; })"

problems=""
diff_fast='make unit ZORBLAT=diff -- --only "frob & nitz/quux"'
df="$("$BUILD" --step "$diff_step" --fast-cmd "$diff_fast" diff "$work/spec.md" "$branch_base" "$step_base" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; diff with --fast-cmd exited $code, want 0"
[[ "$df" == *"timed-test-run.sh fast '' $diff_fast"* ]] \
  || problems="$problems; never runs --fast-cmd's value verbatim through timed-test-run.sh fast"
after_fast="${df#*"timed-test-run.sh fast '' $diff_fast"}"
[[ "$after_fast" != "$df" && "$after_fast" == *'affected-suites.sh'* ]] \
  || problems="$problems; never runs the suites affected-suites.sh prints after the fast command"
red_word='(red|fails?|failing|not green)[^[:alnum:]]'
prompt_says "$df" "never REJECTs when the fast command or the affected suites are red" \
  -iE -e "(fast|affected)[^.]{0,200}$red_word[^.]{0,200}REJECT|REJECT[^.]{0,200}(fast|affected)[^.]{0,200}$red_word"
[[ -z "$problems" ]] \
  && ok || no "#974 diff with --fast-cmd tells the verifier to run that command, then the affected suites, and to REJECT when either is red (${problems#; })"

name="#974 diff without --fast-cmd exits 2 with a diagnostic on stderr and nothing on stdout, as green and refactor do"
out="$("$BUILD" --step "$diff_step" diff "$work/spec.md" "$branch_base" "$step_base" 2>"$work/diff-fast.err")"; code=$?
diagnosed=""; [[ -s "$work/diff-fast.err" ]] && diagnosed=diagnosed
expect_eq "$name" "2:diagnosed:0" "$code:$diagnosed:${#out}"

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

cp "$work/spec.md" "$work/refactor-spec.md"
printf '\n## Refactor\n\nRun kind: refactor. This issue changes structure, not behaviour.\n' \
  >> "$work/refactor-spec.md"
problems=""
rf_plan="$("$BUILD" plan "$work/refactor-spec.md" "$work/ledger.md" 2>/dev/null)"; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; plan with a refactor spec exited $code, want 0"
names_one_refactoring='REJECT[^.]{0,200}(one|a single|named) refactoring|(one|a single|named) refactoring[^.]{0,200}REJECT'
runnable_predicate='REJECT[^.]{0,200}(runnable|shell)[^.]{0,40}predicate|(runnable|shell)[^.]{0,40}predicate[^.]{0,200}REJECT'
prompt_says "$rf_plan" "never directs a REJECT for a step that does not name one refactoring" \
  -iE -e "$names_one_refactoring"
prompt_says "$rf_plan" "never directs a REJECT for a step whose smell is not a runnable shell predicate" \
  -iE -e "$runnable_predicate"
prompt_lacks "$plan" "a spec with no Refactor section still demands one named refactoring per step" \
  -iE -e "$names_one_refactoring"
prompt_lacks "$plan" "a spec with no Refactor section still demands a runnable shell predicate" \
  -iE -e "$runnable_predicate"
[[ -z "$problems" ]] \
  && ok || no "verify-plan, for a spec with a Refactor section, REJECTs a plan whose steps do not each name one refactoring and state its smell as a runnable shell predicate, and says neither for a spec without one (${problems#; })"

mkdir -p "$work/no-refactor-plan"
cp "$BUILD" "$work/no-refactor-plan/"
cp -R "$HERE/../prompts" "$HERE/../lib" "$work/no-refactor-plan/"
rm "$work/no-refactor-plan/prompts/_verify-plan-refactor.md"
problems=""
out="$("$work/no-refactor-plan/build-verify-prompt.sh" plan "$work/refactor-spec.md" "$work/ledger.md" 2>"$work/no-refactor-plan.err")"; code=$?
[[ "$code" -eq 2 ]] || problems="$problems; plan without the paragraph's file exited $code, want 2"
[[ -z "$out" ]] || problems="$problems; plan without the paragraph's file printed ${#out} bytes, want none"
grep -F '_verify-plan-refactor.md' "$work/no-refactor-plan.err" > /dev/null \
  || problems="$problems; stderr does not name _verify-plan-refactor.md"
"$work/no-refactor-plan/build-verify-prompt.sh" red "$work/refactor-spec.md" "$testpath" test_slugify_lowercases \
  >/dev/null 2>&1; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; red on a refactor spec without the plan paragraph's file exited $code, want 0"
[[ -z "$problems" ]] \
  && ok || no "the refactor-plan paragraph is read by the plan phase alone, and an unreadable one is exit 2 with no stdout (${problems#; })"

problems=""
prompt_says "$rf_plan" "never directs a REJECT for a step that leaves a no-op in place for a later step to delete" \
  -iE -e 'REJECT[^.]{0,200}no-op[^.]{0,200}later step|no-op[^.]{0,200}later step[^.]{0,200}REJECT'
[[ -z "$problems" ]] \
  && ok || no "#679 verify-plan, for a spec with a Refactor section, REJECTs a step that leaves a no-op in place for a later step to delete (${problems#; })"

rejects_rationale_comment() {
  local prompt="$1" phase="$2"
  problems=""
  prompt_says "$prompt" "$phase never makes a rationale comment a REJECT" \
    -iE -e "REJECT[^.]{0,200}rationale comment|rationale comment[^.]{0,200}REJECT"
  prompt_says "$prompt" "$phase never names the contract header as an allowed comment" \
    -iE -e "contract header"
  prompt_says "$prompt" "$phase never names the shell-hazard warning as an allowed comment" \
    -iE -e "shell[^.]{0,40}hazard"
  [[ -z "$problems" ]] && ok \
    || no "$phase REJECTs a rationale comment outside the two allowed classes (${problems#; })"
}
rejects_rationale_comment "$green" verify-green
rejects_rationale_comment "$refactor" verify-refactor

problems=""
not_reject='\b(not|never)\b[^.]{0,40}REJECT'
contract='contract header' hazard='shell[^.]{0,40}hazard'
for pair in "verify-green:$green" "verify-refactor:$refactor"; do
  phase="${pair%%:*}" prompt="${pair#*:}"
  prompt_says "$prompt" "$phase never says a contract header is not grounds for REJECT" \
    -iE -e "$contract[^.]{0,200}$not_reject|$not_reject[^.]{0,200}$contract"
  prompt_says "$prompt" "$phase never says a shell-hazard warning is not grounds for REJECT" \
    -iE -e "$hazard[^.]{0,200}$not_reject|$not_reject[^.]{0,200}$hazard"
done
[[ -z "$problems" ]] && ok \
  || no "a contract header or a shell-hazard warning is not grounds for REJECT (${problems#; })"

replaces_step='⟦replaces-case⟧ tests/zorblat.test.sh: "zorblat frobs a nitz" moves to tests/py/test_zorblat.py ⟦criterion 1⟧'
replaces_green="$("$BUILD" --step "$replaces_step" --fast-cmd 'make unit' green "$work/spec.md" 'tests/py/test_zorblat.py' test_zorblat_frobs_a_nitz 2>/dev/null)"; code=$?
gone='(gone|deleted|removed|no longer)'
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$replaces_green" "never makes PASS depend on a pytest case asserting the same behaviour" \
  -iE -e "PASS[^.]{0,250}pytest[^.]{0,120}same behaviou?r"
prompt_says "$replaces_green" "never makes PASS depend on the named case being gone" \
  -iE -e "PASS[^.]{0,250}named (bash )?case[^.]{0,60}$gone"
prompt_says "$replaces_green" "never REJECTs a deletion or modification of any other case" \
  -iE -e "REJECT[^.]{0,200}(delet|modif)[^.]{0,80}(any|every) other (bash )?case|(delet|modif)[^.]{0,80}(any|every) other (bash )?case[^.]{0,200}REJECT"
prompt_lacks "$green" "an unmarked step's prompt makes PASS depend on a pytest case too" \
  -iE -e "PASS[^.]{0,250}pytest"
[[ -z "$problems" ]] && ok \
  || no "verify-green for a ⟦replaces-case⟧ step PASSes only when the named case is gone and a pytest case asserting the same behaviour was added, and REJECTs a deletion or modification of any other case (${problems#; })"

repair_step='fix the full-suite failure: skills/tdd/scripts/tests/zorblat.test.sh — FAIL - zorblat frobs a nitz; skills/tdd/scripts/tests/quux.test.sh — FAIL - quux & {nitz} round-trips ⟦suite-repair⟧'
repair_green="$("$BUILD" --step "$repair_step" --fast-cmd 'make unit' green "$work/spec.md" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' 2>/dev/null)"; code=$?
every_suite='(every|each|all)( of the)? (listed|red|named) suites?'
full_cmd='full test command'
problems=""
[[ "$code" -eq 0 ]] || problems="$problems; exited $code, want 0"
prompt_says "$repair_green" "never makes PASS depend on every listed suite being green" \
  -iE -e "PASS[^.]{0,250}$every_suite[^.]{0,80}green"
prompt_says "$repair_green" "never tells the verifier to judge the listed suites by running the full test command" \
  -iE -e "run[^.]{0,120}$full_cmd|$full_cmd[^.]{0,120}(run|judge)"
prompt_says "$repair_green" "never says the fast command is not what judges the listed suites" \
  -iE -e "(not|rather than|instead of)[^.]{0,60}fast (test )?command"
prompt_lacks "$green" "an unmarked step's prompt tells the verifier to run the full test command too" \
  -iE -e "run[^.]{0,120}$full_cmd"
[[ -z "$problems" ]] && ok \
  || no "#690 verify-green for a ⟦suite-repair⟧ step listing two red suites PASSes only when every listed suite is green, judged by running the full test command rather than the fast one (${problems#; })"

mkdir -p "$work/no-replaces-case"
cp "$BUILD" "$work/no-replaces-case/"
cp -R "$HERE/../prompts" "$HERE/../lib" "$work/no-replaces-case/"
rm "$work/no-replaces-case/prompts/_verify-green-replaces-case.md"
problems=""
out="$("$work/no-replaces-case/build-verify-prompt.sh" --step "$replaces_step" --fast-cmd 'make unit' green "$work/spec.md" 'tests/py/test_zorblat.py' test_zorblat_frobs_a_nitz 2>"$work/no-replaces-case.err")"; code=$?
[[ "$code" -eq 2 ]] || problems="$problems; green for a ⟦replaces-case⟧ step without the paragraph's file exited $code, want 2"
[[ -z "$out" ]] || problems="$problems; green without the paragraph's file printed ${#out} bytes, want none"
grep -F '_verify-green-replaces-case.md' "$work/no-replaces-case.err" > /dev/null \
  || problems="$problems; stderr does not name _verify-green-replaces-case.md"
"$work/no-replaces-case/build-verify-prompt.sh" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases \
  >/dev/null 2>&1; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; green for an unmarked step without the paragraph's file exited $code, want 0"
[[ -z "$problems" ]] \
  && ok || no "the replaces-case paragraph is read for a ⟦replaces-case⟧ green step alone, and an unreadable one is exit 2 with no stdout (${problems#; })"

mkdir -p "$work/no-suite-repair"
cp "$BUILD" "$work/no-suite-repair/"
cp -R "$HERE/../prompts" "$HERE/../lib" "$work/no-suite-repair/"
rm "$work/no-suite-repair/prompts/_verify-green-suite-repair.md"
problems=""
out="$("$work/no-suite-repair/build-verify-prompt.sh" --step "$repair_step" --fast-cmd 'make unit' green "$work/spec.md" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' 2>"$work/no-suite-repair.err")"; code=$?
[[ "$code" -eq 2 ]] || problems="$problems; green for a ⟦suite-repair⟧ step without the paragraph's file exited $code, want 2"
[[ -z "$out" ]] || problems="$problems; green without the paragraph's file printed ${#out} bytes, want none"
grep -F '_verify-green-suite-repair.md' "$work/no-suite-repair.err" > /dev/null \
  || problems="$problems; stderr does not name _verify-green-suite-repair.md"
"$work/no-suite-repair/build-verify-prompt.sh" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases \
  >/dev/null 2>&1; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; green for an unmarked step without the paragraph's file exited $code, want 0"
"$work/no-suite-repair/build-verify-prompt.sh" --step "$repair_step" red "$work/spec.md" 'skills/tdd/scripts/tests/zorblat.test.sh' 'zorblat frobs a nitz' \
  >/dev/null 2>&1; code=$?
[[ "$code" -eq 0 ]] || problems="$problems; red for a ⟦suite-repair⟧ step without the paragraph's file exited $code, want 0"
[[ -z "$problems" ]] \
  && ok || no "the suite-repair paragraph is read for a ⟦suite-repair⟧ green step alone, and an unreadable one is exit 2 with no stdout (${problems#; })"

scripts_dir="$(cd "$HERE/.." && pwd)"
unmarked_step='tests/zorblat.test.sh: "zorblat frobs a nitz" replaces-case moves to tests/py ⟦added⟧ ⟦criterion 4⟧'
problems=""
green_sums_as() {  # <label> <want-cksum> <args...> — records a green prompt whose sum is not <want>
  local label="$1" want="$2"; shift 2
  local out code got
  out="$("$BUILD" "$@" --fast-cmd 'make unit' green "$work/spec.md" "$testpath" test_slugify_lowercases 2>/dev/null)"; code=$?
  [[ "$code" -eq 0 ]] || { problems="$problems; $label exited $code, want 0"; return; }
  got="$(printf '%s\n' "${out//"$scripts_dir"/@SCRIPTS@}" | cksum)"
  [[ "$got" == "$want" ]] || problems="$problems; $label renders as '$got', want '$want'"
}
green_sums_as 'green, unmarked --step' '1447155214 6914' --step "$unmarked_step"
green_sums_as 'green, no --step'       '4188760161 6638'
[[ -z "$problems" ]] \
  && ok || no "verify-green for a --step not carrying ⟦replaces-case⟧, or no --step, renders byte-identically to before #671 (${problems#; })"

name="#703 a {{INCLUDE:<file>}} token, in a template and recursively inside an included partial, is replaced by that partial under prompts/ before the other placeholders, with no new parameter"
included="$(scratch_dir)"
cp -R "$BUILD" "$HERE/../lib" "$HERE/../prompts" "$included/"
printf 'before {{INCLUDE:_probe-outer.md}} after\n' > "$included/prompts/verify-red.md"
printf 'outer {{INCLUDE:_probe-inner.md}} end\n' > "$included/prompts/_probe-outer.md"
printf 'inner judges {{TEST_PATH}}\n' > "$included/prompts/_probe-inner.md"
rendered="$("$included/build-verify-prompt.sh" red "$work/spec.md" "$testpath" test_slugify_lowercases 2>&1)"; code=$?
expect_eq "$name" "0:before outer inner judges $testpath end after" "$code:$rendered"

name="#703 a {{INCLUDE:<file>}} naming a partial that does not exist exits 2 with that partial's path on stderr and nothing on stdout"
dangling="$(scratch_dir)"
cp -R "$BUILD" "$HERE/../lib" "$HERE/../prompts" "$dangling/"
printf 'before {{INCLUDE:_probe-absent.md}} after\n' > "$dangling/prompts/verify-red.md"
rendered="$("$dangling/build-verify-prompt.sh" red "$work/spec.md" "$testpath" test_slugify_lowercases 2>"$dangling/err")"; code=$?
named=""; grep -F "$dangling/prompts/_probe-absent.md" "$dangling/err" > /dev/null && named=named
expect_eq "$name" "2:named:" "$code:$named:$rendered"

name="#703 a partial that includes itself through another partial exits 2 naming that partial on stderr, with nothing on stdout, rather than looping"
cycle="$(scratch_dir)"
cp -R "$BUILD" "$HERE/../lib" "$HERE/../prompts" "$cycle/"
printf 'before {{INCLUDE:_probe-cycle-a.md}} after\n' > "$cycle/prompts/verify-red.md"
printf 'a {{INCLUDE:_probe-cycle-b.md}}\n' > "$cycle/prompts/_probe-cycle-a.md"
printf 'b {{INCLUDE:_probe-cycle-a.md}}\n' > "$cycle/prompts/_probe-cycle-b.md"
# hazard: a looping builder never returns; the CPU-time limit ends it instead of the suite.
rendered="$(ulimit -t 2; "$cycle/build-verify-prompt.sh" red "$work/spec.md" "$testpath" test_slugify_lowercases 2>"$cycle/err")"; code=$?
named=""; grep -F "_probe-cycle-a.md" "$cycle/err" > /dev/null && named=named
expect_eq "$name" "2:named:" "$code:$named:$rendered"

finish
