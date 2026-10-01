#!/usr/bin/env bash
# Tests for scripts/comment-class.sh — prints every `#` line of the shell files it is given
# as `<file>:<line>:<class>`, class 1 a comment in code, 2 a `#` line in a heredoc written
# to a file, 3 one in any other heredoc.
#
# Admitted to the fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/comment-class.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS="$HERE/../.."
CLASSIFY="$SCRIPTS/comment-class.sh"
source "$HERE/../lib/harness.sh"

work="$(scratch_dir)"

verdict() {
  if [[ -z "$problems" ]]; then
    ok
  else
    no "$1"
    printf '%s' "$problems"
  fi
}

classify() {
  out="$("$CLASSIFY" "$@" 2>"$work/stderr")" && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    problems+="    want exit 0, got $code; stderr: $(cat "$work/stderr")"$'\n'
  fi
}

want_empty_sweepable() {
  classify --sweepable "$@"
  if [[ -n "$out" ]]; then
    problems+="    want an empty sweepable report, got:"$'\n'"$out"$'\n'
  fi
}

sweep_verdict() {
  local name="$1"; shift
  problems=""
  want_empty_sweepable "$@"
  verdict "$name"
}

want_line() {
  if ! grep -E "^$1(:|$)" <<< "$out" > /dev/null; then
    problems+="    want a line matching '$1', got:"$'\n'"$out"$'\n'
  fi
}

want_no_line() {
  if grep -E "^$1(:|$)" <<< "$out" > /dev/null; then
    problems+="    want no line matching '$1', got:"$'\n'"$out"$'\n'
  fi
}

problems=""
f="$work/plain.sh"
printf '%s\n' 'echo one' '# a comment in code' 'echo two' > "$f"
classify "$f"
want_line "$f:2:1"
verdict "a comment in code outside any heredoc is reported as class 1 with its file and line"

problems=""
f="$work/mixed.sh"
printf '%s\n' 'echo one' '# a comment in code' 'cat << EOF' '# a line in a heredoc' 'EOF' '# a comment after the heredoc' > "$f"
classify "$f"
want_line "$f:2:1"
want_line "$f:4:[23]"
want_line "$f:6:1"
verdict "a # line inside a heredoc is counted apart from a comment in the same file, never as class 1"

problems=""
f="$work/open.sh"
g="$work/after.sh"
printf '%s\n' 'cat <<EOF' '# a line in a heredoc' > "$f"
printf '%s\n' '# a comment in code' > "$g"
classify "$f" "$g"
want_line "$g:1:1"
verdict "a heredoc left open at the end of one file does not carry into the next"

problems=""
f="$work/delims.sh"
printf '%s\n' "cat <<'EOF'" '# in a single-quoted heredoc' 'EOF' 'cat <<"EOF"' '# in a double-quoted heredoc' 'EOF' \
  'cat <<-EOF' '# in a dash heredoc' $'\tEOF' 'cat <<< word' '# a comment after a here-string' > "$f"
classify "$f"
want_line "$f:2:[23]"
want_line "$f:5:[23]"
want_line "$f:8:[23]"
want_line "$f:11:1"
verdict "a # line in a quoted or <<- heredoc is never class 1, and a here-string opens no heredoc"

problems=""
f="$work/targets.sh"
printf '%s\n' 'cat > "$dir/fixture.txt" <<EOF' '# written to a file' 'EOF' 'claude -p <<EOF' '# sent to a model' 'EOF' \
  'prompt="$(cat <<EOF' '# held in a variable' 'EOF' ')"' 'cat <<EOF' '# printed to stdout' 'EOF' \
  'cat >&2 <<EOF' '# printed to stderr' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
want_line "$f:5:3"
want_line "$f:8:3"
want_line "$f:12:3"
want_line "$f:15:3"
verdict "a # line in a heredoc redirected to a file is class 2, and one sent to a model, a variable, stdout or stderr is class 3"

problems=""
f="$work/fd-redirect.sh"
printf '%s\n' 'claude -p 2>/dev/null <<EOF' '# sent to a model with stderr discarded' 'EOF' > "$f"
classify "$f"
want_line "$f:2:3"
verdict "a heredoc sent to a command whose opener redirects only stderr to a file is class 3, not class 2"

problems=""
f="$work/piped-tee.sh"
printf '%s\n' 'cat <<EOF | tee "$dir/fixture.txt"' '# written to a file through tee' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
verdict "a # line in a heredoc piped to tee writing a file is class 2"

problems=""
f="$work/piped-writers.sh"
printf '%s\n' 'cat <<EOF | dd of="$dir/fixture.txt"' '# written to a file through dd' 'EOF' \
  'cat <<EOF | sponge "$dir/fixture.txt"' '# written to a file through sponge' 'EOF' > "$f"
classify "$f"
want_line "$f:2:2"
want_line "$f:5:2"
verdict "a # line in a heredoc piped to dd or sponge writing a file is class 2"

problems=""
f="$work/sweepable.sh"
printf '%s\n' '# a comment in code' 'cat > "$dir/fixture.txt" <<EOF' '# written to a file' 'EOF' \
  'claude -p <<EOF' '# sent to a model' 'EOF' > "$f"
classify --sweepable "$f"
want_line "$f:1:1"
want_line "$f:3:2"
want_no_line "$f:6"
verdict "the sweepable report lists class 1 and class 2 lines and never a class 3 line"

problems=""
f="$work/header-hazard.sh"
printf '%s\n' '#!/usr/bin/env bash' '# tool.sh — print its one argument.' '#' '# Usage: tool.sh <arg>' \
  '# Exit: 0 printed, 2 bad arguments.' 'set -uo pipefail' '' \
  '# hazard: under set -u an unset name exits with the status of the previous command' 'echo "${1:-}"' > "$f"
want_empty_sweepable "$f"
printf '%s\n' '# print the argument, or nothing' 'echo "${1:-}"' >> "$f"
classify --sweepable "$f"
if [[ "$out" != "$f:10:1" ]]; then
  problems+="    want only $f:10:1 once a code comment follows the header, got:"$'\n'"$out"$'\n'
fi
verdict "the sweepable report omits a leading contract header and a comment marked as a shell-hazard warning"

sweep_verdict "the sweepable report is empty for metrics.sh, event.sh and harvest-usage.sh" "$SCRIPTS/metrics.sh" "$SCRIPTS/event.sh" "$SCRIPTS/harvest-usage.sh"

problems=""
want_empty_sweepable "$SCRIPTS/supervise.sh" "$SCRIPTS/run-leaf.sh" "$SCRIPTS/detach-leaf.sh" \
  "$SCRIPTS/wait-leaf.sh" "$SCRIPTS/run-verdict.sh"
verdict "the sweepable report is empty for supervise.sh, run-leaf.sh, detach-leaf.sh, wait-leaf.sh and run-verdict.sh"

problems=""
want_empty_sweepable "$SCRIPTS/issue-worktree.sh" "$SCRIPTS/verify.sh" "$SCRIPTS/parse-verdict.sh" \
  "$SCRIPTS/extract-result.sh"
verdict "the sweepable report is empty for issue-worktree.sh, verify.sh, parse-verdict.sh and extract-result.sh"

problems=""
want_empty_sweepable "$SCRIPTS/detect-test-command.sh" "$SCRIPTS/solvable-issues.sh" \
  "$SCRIPTS/session-cost.sh"
verdict "the sweepable report is empty for detect-test-command.sh, solvable-issues.sh and session-cost.sh"

problems=""
want_empty_sweepable "$SCRIPTS/build-develop-prompt.sh" "$SCRIPTS/build-verify-prompt.sh" \
  "$SCRIPTS/run-conductor.sh" "$SCRIPTS/stop-run.sh" "$SCRIPTS/preserve-attempt.sh"
verdict "the sweepable report is empty for build-develop-prompt.sh, build-verify-prompt.sh, run-conductor.sh, stop-run.sh and preserve-attempt.sh"

problems=""
want_empty_sweepable "$SCRIPTS/leaf-timeout.sh" "$SCRIPTS/ensure-run-state-ignored.sh" \
  "$SCRIPTS/orchestrate.sh" "$SCRIPTS/parallel-conductors.sh" "$SCRIPTS/workqueue.sh" \
  "$SCRIPTS/push-branch.sh" "$SCRIPTS/refactor-triage.sh" "$SCRIPTS/invisible-work.sh" \
  "$SCRIPTS/over-budget.sh" "$SCRIPTS/run-suite.sh" "$SCRIPTS/leaf-model.sh" \
  "$SCRIPTS/leaf-launchable.sh"
verdict "the sweepable report is empty for leaf-timeout.sh, ensure-run-state-ignored.sh, orchestrate.sh, parallel-conductors.sh, workqueue.sh, push-branch.sh, refactor-triage.sh, invisible-work.sh, over-budget.sh, run-suite.sh, leaf-model.sh and leaf-launchable.sh"

sweep_verdict "the sweepable report is empty for every scripts/*.sh, the classifier itself included" "$SCRIPTS"/*.sh

sweep_verdict "the sweepable report is empty for every shell file under scripts/lib/" "$SCRIPTS"/lib/*.sh

problems=""
files=("$SCRIPTS"/*.sh "$SCRIPTS"/lib/*.sh)
classify "${files[@]}"
cited="$(awk -F: 'NR == FNR { if ($NF == 1) want[$1 ":" $2] = 1; next }
  (FILENAME ":" FNR) in want && /#[0-9]/ { print FILENAME ":" FNR ": " $0 }' \
  - "${files[@]}" <<< "$out")"
if [[ -n "$cited" ]]; then
  problems+="    want no comment line citing an issue number, got:"$'\n'"$cited"$'\n'
fi
verdict "no comment line in scripts/*.sh or scripts/lib/*.sh, the contract header included, cites an issue number"

problems=""
TESTS="$SCRIPTS/tests"
files=("$TESTS"/*.sh "$TESTS"/unit/*.sh "$TESTS"/fixtures/*/*.sh "$TESTS/unit-guard/git" "$TESTS/offline/gh")
classify "${files[@]}"
got="$(awk -F: -v tests="$TESTS/" 'NR == FNR { if ($NF == 3) want[$1 ":" $2] = 1; next }
  (FILENAME ":" FNR) in want { f = FILENAME; sub("^" tests, "", f); sub(/\.test\.sh$/, "", f); print f ":" $0 }' \
  - "${files[@]}" <<< "$out")"
IFS= read -r -d '' expected <<'EOF' || true
build-develop-prompt:## Bug
build-develop-prompt:### What happened
build-develop-prompt:### Expected
build-develop-prompt:### Steps to reproduce
build-develop-prompt:### Environment
build-verify-prompt:# Plan for #426
build-verify-prompt:# Plan for #439
build-verify-prompt:## Bug
build-verify-prompt:### What happened
build-verify-prompt:### Expected
build-verify-prompt:### Steps to reproduce
build-verify-prompt:### Environment
capture-spec:## What happened
capture-spec:## Expected
capture-spec:## Steps to reproduce
capture-spec:## Environment
capture-spec:## Acceptance criteria
capture-spec:## What to build
capture-spec:## Acceptance criteria
dashboard:# Plan for #$2 — $3
dashboard:## What to build
dashboard:# Plan for #51 — lamps hum
dashboard:# Plan for #22 — lamps glow
dashboard:# Plan for #31 — lamps glow
dashboard:# a stale committed report for #31 that metrics.sh would never print
dashboard:# Plan for #32 — lamps dim
dashboard:# What solving #32 cost — the committed report, verbatim
dashboard:# Plan for #33 — lamps flicker
dashboard:# What solving #33 cost — the committed report of a bailed run, verbatim
dashboard:# Plan for #34 — lamps gutter
dashboard:# Plan for #7 — lamps glow
dashboard:# Plan for #$mown_other — an earlier run's committed plan
dashboard:# Plan for #51 — lamps flicker
dashboard:# Plan for #52 — lamps dim
dashboard:# Plan for #7 — lamps glow
dashboard:# Plan for #3 — an earlier run's committed plan
dashboard:# Plan for #54 — lamps buzz
dashboard:# Plan for #59 — lamps flare
dashboard:# Plan for #61 — lamps flicker
dashboard:# Plan for #63 — lamps dim
dashboard:# Plan for #65 — lamps hum
dashboard:# Plan for #55 — lamps dim
dashboard:# Plan for #77 — a kettle boils
invisible-work:#!/bin/sh
orchestrate:# A stopped conductor must be stopped by a signal, not by its writes failing, so this stub
orchestrate:# IGNORES SIGPIPE — the state CI's Linux was observed in, where a write to the closed stream
orchestrate:# came back as plain \`echo: I/O error\` and the conductor ran on. On this Mac SIGPIPE is fatal
orchestrate:# and would end the stub whatever orchestrate.sh did, so without this line the cases below
orchestrate:# cannot go red here at all, and the regression they exist for is only visible on CI. This is
orchestrate:# a stub imitating a platform, not a suite repairing its own pipeline (#422).
parallel-conductors:#!/bin/sh
run-verdict:#!/bin/sh
run-verdict:# Stub verifier: record the argv handed to it, one argument per line, and answer like a
run-verdict:# verifier that passed — what this case reads is the record, not the verdict.
run-verdict:#!/bin/sh
run-verdict:# Stub verifier: copy the phase's reason file, as it stands now, into the record this case
run-verdict:# reads — an unreadable or absent file records as nothing, which is the same answer as a
run-verdict:# cleared one and the answer this case wants.
skill-refactor-pending:## The scripts (this skill's `scripts/` directory)
skill-refactor-pending:## The scripts (this skill's `scripts/` directory)
solvable-issues:#!/bin/sh
status:# Plan for #7 — widgets spin when clicked
status:# Plan for #8 — gears turn
status:# Plan for #9 — cogs mesh
status:# Plan for #7 — widgets spin when clicked
status:# Plan for #3 — gears turn
status:# Plan for #5 — lamps glow
status:# Plan for #3 — gears turn
status:# Plan for #5 — lamps glow
unit/emitted-text:## What to build
unit/emitted-text:## Acceptance criteria
unit/emitted-text:## Bug
unit/emitted-text:## Acceptance criteria
unit/emitted-text:## Refactor
unit/emitted-text:# Plan for #1 — fixed
EOF
expected="${expected%$'\n'}"
if [[ "$got" != "$expected" ]]; then
  problems+="    want the 75 class 3 lines unchanged (< want, > got):"$'\n'
  problems+="$(diff <(printf '%s\n' "$expected") <(printf '%s\n' "$got"))"$'\n'
fi
verdict "the text of every class 3 line in the suites is unchanged, in its file and in its order"

problems=""
f="$work/quoted.sh"
printf '%s\n' "x='first" '# inside a single-quoted string' "last'" 'y="first' '# inside a double-quoted string' \
  'last"' '# a comment in code' > "$f"
classify "$f"
want_no_line "$f:(2|5)"
want_line "$f:7:1"
verdict "a # line inside a multi-line single- or double-quoted string is not reported as a comment"

problems=""
f="$work/quote-edges.sh"
printf '%s\n' 'a="say \"hi' '# inside, after an escaped quote' 'bye"' "b=1 # it's a trailing comment" \
  '# a comment after a trailing one' "echo c#'" '# inside, after a # inside a word' "'" > "$f"
classify "$f"
want_no_line "$f:(2|7)"
want_line "$f:5:1"
verdict "an escaped quote, a trailing comment and a # inside a word neither open nor close a quoted string"

problems=""
f="$work/stub-writer.sh"
printf '%s\n' "cat > stub <<'EOF'" '#!/bin/sh' 'echo hi' '# a comment later in the body' '#!/bin/sh later in the body' 'EOF' > "$f"
classify --sweepable "$f"
want_no_line "$f:2"
want_line "$f:4:2"
want_line "$f:5:2"
verdict "the sweepable report omits the #! line that opens a heredoc's body, and no later #! line"

problems=""
f="$work/md-writer.sh"
printf '%s\n' 'cat > "$dir/CLAUDE.md" <<EOF' '# a markdown heading' 'EOF' > "$f"
g="$work/md-tee.sh"
printf '%s\n' 'cat <<EOF | tee -a "$dir/SPEC.md"' '# a markdown heading' 'EOF' > "$g"
classify "$f" "$g"
want_line "$f:2:3"
want_line "$g:2:3"
verdict "a # line inside a heredoc written to a .md file is class 3"

problems=""
f="$work/md-dd.sh"
printf '%s\n' 'cat <<EOF | dd of="$dir/CLAUDE.md"' '# a markdown heading' 'EOF' > "$f"
g="$work/md-sponge.sh"
printf '%s\n' 'cat <<EOF | sponge "$dir/SPEC.md"' '# a markdown heading' 'EOF' > "$g"
classify "$f" "$g"
want_line "$f:2:3"
want_line "$g:2:3"
verdict "a # line inside a heredoc piped to dd of= or sponge writing a .md file is class 3"

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with a or b" "$SCRIPTS"/tests/[ab]*.sh

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with c or d" "$SCRIPTS"/tests/[cd]*.sh

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with e through j" "$SCRIPTS"/tests/[e-j]*.sh

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with k through m" "$SCRIPTS"/tests/[k-m]*.sh

problems=""
f="$work/md-var.sh"
printf '%s\n' 'f="$dir/x.md"; cat > "$f" <<'"'EOF'" '# a markdown heading' 'EOF' > "$f"
classify "$f"
want_line "$f:2:3"
verdict "a # line inside a heredoc written to a variable assigned a .md path is class 3"

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with n through r" "$SCRIPTS"/tests/[n-r]*.sh

sweep_verdict "the sweepable report is empty for the supervisor's two suites, tests/supervise*.test.sh" "$SCRIPTS"/tests/supervise*.test.sh

files=()
for f in "$SCRIPTS"/tests/s*.sh; do
  case "${f##*/}" in skill-*|supervise*) ;; *) files+=("$f") ;; esac
done
sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with s, other than the skill-* and supervise* files" "${files[@]}"

sweep_verdict "the sweepable report is empty for every top-level tests/*.sh whose name starts with t through z" "$SCRIPTS"/tests/[t-z]*.sh

sweep_verdict "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with a through l" "$SCRIPTS"/tests/skill-[a-l]*.test.sh

sweep_verdict "the sweepable report is empty for every tests/skill-*.test.sh whose name after skill- starts with m through z" "$SCRIPTS"/tests/skill-[m-z]*.test.sh

problems=""
f="$work/stub-writer-dash.sh"
printf '%s\n' "cat > stub <<-'EOF'" $'\t#!/bin/sh' $'\techo hi' $'\tEOF' > "$f"
classify --sweepable "$f"
want_no_line "$f:2"
verdict "the sweepable report omits a tab-indented #! line that opens a <<- heredoc's body"

problems=""
f="$work/quote-in-subst.sh"
printf '%s\n' "x=\"\$(echo 'a \"b')\"" '# a comment in code' > "$f"
classify "$f"
want_line "$f:2:1"
verdict "comment-class.sh classifies a # line after a \"\$(cmd 'a \"b')\" shape as class 1"

problems=""
f="$work/subshell-in-subst.sh"
printf '%s\n' "x=\"\$( (cd /) && echo 'a \"b')\"" '# a comment in code' > "$f"
classify "$f"
want_line "$f:2:1"
verdict "comment-class.sh classifies a # line after a \"\$( (cmd) && cmd 'a \"b')\" shape as class 1"

files=()
for f in "$SCRIPTS"/tests/unit/[c-e]*.sh; do
  [[ "${f##*/}" == comment-class.test.sh ]] || files+=("$f")
done
sweep_verdict "the sweepable report is empty for every tests/unit/*.sh whose name starts with c through e, other than comment-class.test.sh" "${files[@]}"

sweep_verdict "the sweepable report is empty for tests/unit/ledger.test.sh" "$SCRIPTS"/tests/unit/ledger.test.sh

sweep_verdict "the sweepable report is empty for every tests/unit/*.sh whose name starts with m through p" "$SCRIPTS"/tests/unit/[m-p]*.sh

sweep_verdict "the sweepable report is empty for tests/unit/red-divergence.test.sh" "$SCRIPTS"/tests/unit/red-divergence.test.sh

sweep_verdict "the sweepable report is empty for tests/unit/run-affordable.test.sh" "$SCRIPTS"/tests/unit/run-affordable.test.sh

sweep_verdict "the sweepable report is empty for tests/unit/step-budget.test.sh and tests/unit/step-cost.test.sh" "$SCRIPTS"/tests/unit/step-budget.test.sh "$SCRIPTS"/tests/unit/step-cost.test.sh

sweep_verdict "the sweepable report is empty for tests/unit/stop-requested.test.sh" "$SCRIPTS"/tests/unit/stop-requested.test.sh

sweep_verdict "the sweepable report is empty for every shell file under tests/fixtures/, and for tests/unit-guard/git and tests/offline/gh" "$SCRIPTS"/tests/fixtures/*/*.sh "$SCRIPTS"/tests/unit-guard/git "$SCRIPTS"/tests/offline/gh

sweep_verdict "the sweepable report is empty for tests/unit/comment-class.test.sh, the case labels of its own sweepable-report cases included" "$SCRIPTS"/tests/unit/comment-class.test.sh

problems=""
cited="$(awk 'FNR == 1 { header = /^#!/; next }
  header && /^#/ { if (/#[0-9]/) print FILENAME ":" FNR ": " $0; next }
  { header = 0 }' "$SCRIPTS"/tests/[a-e]*.sh)"
if [[ -n "$cited" ]]; then
  problems+="    want no header line citing an issue number, got:"$'\n'"$cited"$'\n'
fi
verdict "no line of the leading header block of a top-level tests/*.sh whose name starts with a through e cites an issue number"

problems=""
shapeless="$(awk 'FNR == 1 { header = /^#!/; para = 0; fresh = 1; next }
  header && /^#$/ { fresh = 1; next }
  header && /^#/ {
    if (fresh) { para++; if (para > 1 && !/^# Contract under test/ && !/^# Run:/ && !/^#   /) print FILENAME ":" FNR ": " $0 }
    fresh = 0; next }
  { header = 0 }' "$SCRIPTS"/tests/[a-e]*.sh)"
if [[ -n "$shapeless" ]]; then
  problems+="    want every header paragraph after the description to be a Contract under test block or the Run: line, got:"$'\n'"$shapeless"$'\n'
fi
verdict "the leading header block of a top-level tests/*.sh whose name starts with a through e holds only a description, its Contract under test block and its Run: line"

finish
