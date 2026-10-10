#!/usr/bin/env bash
# Tests for scripts/verify.sh — the single "verify" verb the conductor calls, chaining
# build-verify-prompt.sh → run-leaf.sh → parse-verdict.sh. Driven against a stub claude
# (via CLAUDE_BIN) that prints a canned verdict and records its argv.
#
# Contract under test:
#   verify.sh's exit status comes from parsing the leaf's output, not from the leaf's
#   process status, which `claude -p` leaves at 0 whatever the verdict.
#
# Run: scripts/tests/verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VERIFY="$HERE/../verify.sh"
source "$HERE/lib/harness.sh"

stubdir="$(scratch_dir)"
work="$(scratch_dir)"

export VERI_POLL=0.02
export VERI_KILL_POLL=0.01
export TEST_CLOCK="$stubdir/clock"
clockbin="$stubdir/clockbin"; mkdir -p "$clockbin"
realdate="$(command -v date)"
realstat="$(command -v stat)"
cat > "$clockbin/date" <<D
#!/bin/sh
if [ "\$*" = "+%s" ]; then
  offset="\$(tail -n 1 "\$TEST_CLOCK" 2>/dev/null | cut -d' ' -f2)"
  printf '%s\n' "\$(( \$("$realdate" +%s) + \${offset:-0} ))"
else
  exec "$realdate" "\$@"
fi
D
cat > "$clockbin/stat" <<D
#!/bin/sh
if [ "\$#" -eq 3 ]; then
  if [ "\$1 \$2" = "-c %Y" ] || [ "\$1 \$2" = "-f %m" ]; then
    exec python3 -c '
import os, sys
try:
    m = os.stat(sys.argv[1]).st_mtime
except OSError:
    sys.exit(1)
offset = 0
try:
    for line in open(sys.argv[2]):
        at, value = line.split()
        if float(at) <= m:
            offset = int(value)
except OSError:
    pass
print(int(m) + offset)' "\$3" "\$TEST_CLOCK"
  fi
fi
exec "$realstat" "\$@"
D
cat > "$clockbin/clock-jump" <<'C'
#!/bin/sh
exec python3 -c '
import sys, time
offset = 0
try:
    offset = int(open(sys.argv[2]).read().split()[-1])
except (OSError, IndexError):
    pass
with open(sys.argv[2], "a") as f:
    f.write("%r %d\n" % (time.time(), offset + int(sys.argv[1])))' "$1" "$TEST_CLOCK"
C
chmod +x "$clockbin/date" "$clockbin/stat" "$clockbin/clock-jump"
export PATH="$clockbin:$PATH"
claude_stub "$stubdir" "$(cat <<'STUB'
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 0
STUB
)"

printf 'slugify must lowercase the title and join words with hyphens.' > "$work/spec.md"

verify_in() {
  local slot4=test_lowercases; [[ "$2" == refactor ]] && slot4=0123abc  # refactor's is a base sha (#151)
  local flag_args=(); [[ -n "${5:-}" ]] && flag_args=( --step "$5" )
  [[ "$2" == green || "$2" == refactor ]] && flag_args+=( --fast-cmd "make unit" )  # both require it (#341)
  ( cd "$1" && env CLAUDE_BIN="${4:-$stubdir/claude}" ARGV_OUT="$1/argv" FAKE_OUT_TEXT="$3" \
      "$VERIFY" "${flag_args[@]+"${flag_args[@]}"}" "$2" "$work/spec.md" tests/test_slugify.py "$slot4" )
}

cat > "$stubdir/claude-hang" <<'STUB'
#!/bin/sh
echo "thinking..."; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60
STUB
chmod +x "$stubdir/claude-hang"


verdict_work="$work/verdict"

verdict_run() {
  local dir="$verdict_work/$1"
  mkdir -p "$dir"
  verify_in "$dir" "$2" "$3" >/dev/null 2>&1
}

verdict_field_in() {
  python3 -c '
import sys, json
hits = []
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == "verdict":
        hits.append(obj)
if len(hits) != 1:
    print("<<%d verdict lines>>" % len(hits))
else:
    print(hits[0].get(sys.argv[2], "<<missing>>"))
' "$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo '<<no event log>>'
}

verdict_field() {
  verdict_field_in "$verdict_work/$1" "$2"
}

fixture_repo() {
  local dir="$1" extra
  shift
  new_repo -b main "$dir" >/dev/null 2>&1
  git -C "$dir" config user.name veri
  git -C "$dir" config user.email veri@example.test
  printf 'the developer committed this\n' > "$dir/src.txt"
  printf '.tdd/\n' > "$dir/.gitignore"
  for extra in "$@"; do printf '%s\n' "$extra" >> "$dir/.gitignore"; done
  git -C "$dir" add -A >/dev/null 2>&1
  git -C "$dir" commit -q -m "initial" >/dev/null 2>&1
}

pres_dir="$work/preserve-reject"
fixture_repo "$pres_dir" argv
printf 'the work the verifier rejected\n' > "$pres_dir/src.txt"
pres_issue=409
pres_step=4
( export VERI_ISSUE="$pres_issue" VERI_STEP="$pres_step"
  verify_in "$pres_dir" green 'VERDICT: REJECT
REASON: the helper it asserts on is still private.' >/dev/null 2>&1 )
pres_code=$?

event_issue="$(verdict_field_in "$pres_dir" issue)"
event_step="$(verdict_field_in "$pres_dir" step)"
event_phase="$(verdict_field_in "$pres_dir" phase)"
event_attempt="$(verdict_field_in "$pres_dir" attempt)"
pres_ref="refs/veri/attempts/$event_issue/$event_step/verify-$event_phase-$event_attempt"
git -C "$pres_dir" rev-parse --verify --quiet "$pres_ref^{commit}" >/dev/null 2>&1; pres_resolved=$?
pres_shown="$(git -C "$pres_dir" show "$pres_ref:src.txt" 2>&1)"
pres_copy="$(head -1 < <(ls "$pres_dir/.tdd/attempts/$event_step-verify-$event_phase-$event_attempt-"*.log 2>/dev/null))"
pres_paired="$(if [[ -n "$pres_copy" ]] && cmp -s "$pres_copy" "$pres_dir/.tdd/verify-green.log"; then echo yes; else echo no; fi)"
{ [[ "$pres_code" == 1 ]] \
  && [[ "$event_issue" == "$pres_issue" ]] && [[ "$event_step" == "$pres_step" ]] \
  && [[ "$pres_resolved" == 0 ]] \
  && [[ "$pres_shown" == "the work the verifier rejected" ]] \
  && [[ "$pres_paired" == yes ]]; } && ok \
  || no "a REJECT preserves the attempt under the ref and the copy name its own verdict event pairs with (code=$pres_code want 1; event issue=$event_issue step=$event_step phase=$event_phase attempt=$event_attempt; ref=$pres_ref resolved=$pres_resolved; git show said '$pres_shown'; log copy='${pres_copy:-<none>}' matches .tdd/verify-green.log: $pres_paired)"


nv_dir="$work/preserve-no-verdict"
fixture_repo "$nv_dir" argv
printf 'the work no verdict was rendered on\n' > "$nv_dir/src.txt"
nv_issue=409
nv_step=5
( export VERI_ISSUE="$nv_issue" VERI_STEP="$nv_step" VERI_NO_VERDICT_RETRIES=0
  verify_in "$nv_dir" green 'the leaf rambled and never rendered a verdict' >/dev/null 2>&1 )
nv_code=$?

nv_issue_seen="$(verdict_field_in "$nv_dir" issue)"
nv_step_seen="$(verdict_field_in "$nv_dir" step)"
nv_phase="$(verdict_field_in "$nv_dir" phase)"
nv_attempt="$(verdict_field_in "$nv_dir" attempt)"
nv_cause="$(verdict_field_in "$nv_dir" cause)"
nv_ref="refs/veri/attempts/$nv_issue_seen/$nv_step_seen/verify-$nv_phase-$nv_attempt"
git -C "$nv_dir" rev-parse --verify --quiet "$nv_ref^{commit}" >/dev/null 2>&1; nv_resolved=$?
nv_shown="$(git -C "$nv_dir" show "$nv_ref:src.txt" 2>&1)"
nv_copy="$nv_dir/.tdd/attempts/$nv_step_seen-verify-$nv_phase-$nv_attempt-$nv_cause.log"
nv_paired="$(if [[ -f "$nv_copy" ]] && cmp -s "$nv_copy" "$nv_dir/.tdd/verify-green.log"; then echo yes; else echo no; fi)"
{ [[ "$nv_code" == 2 ]] \
  && [[ "$nv_issue_seen" == "$nv_issue" ]] && [[ "$nv_step_seen" == "$nv_step" ]] \
  && [[ "$nv_cause" == no-verdict ]] \
  && [[ "$nv_resolved" == 0 ]] \
  && [[ "$nv_shown" == "the work no verdict was rendered on" ]] \
  && [[ "$nv_paired" == yes ]]; } && ok \
  || no "a malformed verdict with no VERDICT: line preserves the attempt under its own ref and copies (code=$nv_code want 2; event issue=$nv_issue_seen step=$nv_step_seen phase=$nv_phase attempt=$nv_attempt cause=$nv_cause want no-verdict; ref=$nv_ref resolved=$nv_resolved; git show said '$nv_shown'; log copy='$nv_copy' matches .tdd/verify-green.log: $nv_paired)"


cat > "$stubdir/claude-clean-failure" <<'STUB'
#!/bin/sh
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 1
STUB
chmod +x "$stubdir/claude-clean-failure"

preserved_trace() {
  local refs copies
  refs="$(git -C "$1" for-each-ref --format='%(refname)' 'refs/veri/attempts/' 2>/dev/null | grep -c . || true)"
  copies="$(ls -1 "$1/.tdd/attempts" 2>/dev/null | grep -c . || true)"
  echo "refs=$refs copies=$copies"
}

untroubled_verdict='VERDICT: PASS
REASON: the test pins the behaviour and the suite is green.'
quiet_issue=409
quiet_step=7

quiet_pass_dir="$work/preserve-none-pass"
fixture_repo "$quiet_pass_dir" argv
printf 'the work the verifier accepted\n' > "$quiet_pass_dir/src.txt"
( export VERI_ISSUE="$quiet_issue" VERI_STEP="$quiet_step"
  verify_in "$quiet_pass_dir" green "$untroubled_verdict" >/dev/null 2>&1 )
quiet_pass_code=$?

quiet_fail_dir="$work/preserve-none-failure"
fixture_repo "$quiet_fail_dir" argv
printf 'the work the verifier accepted\n' > "$quiet_fail_dir/src.txt"
( export VERI_ISSUE="$quiet_issue" VERI_STEP="$quiet_step"
  verify_in "$quiet_fail_dir" green "$untroubled_verdict" "$stubdir/claude-clean-failure" >/dev/null 2>&1 )
quiet_fail_code=$?

quiet_pass_trace="$(preserved_trace "$quiet_pass_dir")"
quiet_fail_trace="$(preserved_trace "$quiet_fail_dir")"
quiet_pass_word="$(verdict_field_in "$quiet_pass_dir" verdict)"
quiet_fail_word="$(verdict_field_in "$quiet_fail_dir" verdict)"
quiet_pass_issue="$(verdict_field_in "$quiet_pass_dir" issue)"
quiet_fail_issue="$(verdict_field_in "$quiet_fail_dir" issue)"
quiet_leaf_rc="$(cat "$quiet_fail_dir/.tdd/verify-green.rc" 2>/dev/null)"
{ [[ "$quiet_pass_code" == 0 ]] && [[ "$quiet_fail_code" == 0 ]] \
  && [[ "$quiet_pass_word" == PASS ]] && [[ "$quiet_fail_word" == PASS ]] \
  && [[ "$quiet_pass_issue" == "$quiet_issue" ]] && [[ "$quiet_fail_issue" == "$quiet_issue" ]] \
  && [[ "$quiet_leaf_rc" == 1 ]] \
  && [[ "$quiet_pass_trace" == "refs=0 copies=0" ]] \
  && [[ "$quiet_fail_trace" == "refs=0 copies=0" ]]; } && ok \
  || no "a PASS verdict and a leaf that exits success or clean failure write no ref and no preserved copy (pass arm: code=$quiet_pass_code want 0, verdict=$quiet_pass_word issue=$quiet_pass_issue want PASS/$quiet_issue, $quiet_pass_trace want refs=0 copies=0; clean-failure arm: code=$quiet_fail_code want 0, verdict=$quiet_fail_word issue=$quiet_fail_issue want PASS/$quiet_issue, leaf rc=${quiet_leaf_rc:-<none>} want 1, $quiet_fail_trace want refs=0 copies=0)"



supervised_verdict() {
  local dir="$1" phase="$2" text="$3"
  mkdir -p "$dir/.tdd"
  ( cd "$dir"
    env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$dir/argv" FAKE_OUT_TEXT="$text" \
      "$HERE/../supervise.sh" "verdict-$phase" bash -c "$VERIFY --step '<STEP>' $phase '$work/spec.md' tests/test_slugify.py test_lowercases > .tdd/verify-$phase.reason 2> .tdd/verify-$phase.err; echo \$? > .tdd/verdict-$phase.exit" > /dev/null 2>&1
    "$HERE/../wait-leaf.sh" "verdict-$phase" 1 )
  sv_code=$?
  sv_reason="$(cat "$dir/.tdd/verify-$phase.reason" 2>/dev/null)"
}

supervised_verdict "$work/supervised-reject" red 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.'
sup_reject_code=$sv_code sup_reject_reason="$sv_reason"
supervised_verdict "$work/supervised-malformed" red 'the leaf rambled and never rendered a verdict'
sup_malformed_code=$sv_code
{ [[ "$sup_reject_code" == 1 ]] && [[ "$sup_malformed_code" == 2 ]] \
  && [[ "$sup_reject_reason" == 'The test asserts on a private helper, not observable behavior.' ]]; } && ok \
  || no "a supervised verification hands the conductor the verdict text and verify.sh's own code (REJECT arm: wait=$sup_reject_code want 1, reason='$sup_reject_reason' want the verifier's own line; malformed arm: wait=$sup_malformed_code want 2)"

noisy_dir="$work/reason-only-verifier"
noisy_want='The test asserts on a private helper, not observable behavior.'
fixture_repo "$noisy_dir" argv
mkdir -p "$noisy_dir/.tdd"
git -C "$noisy_dir" update-ref refs/veri/attempts/625/6 HEAD
( cd "$noisy_dir"
  env VERI_ISSUE=625 VERI_STEP=6 CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$noisy_dir/argv" \
    FAKE_OUT_TEXT="VERDICT: REJECT
REASON: $noisy_want" \
    "$HERE/../supervise.sh" verdict-red "$HERE/../run-verdict.sh" --step '<STEP>' red "$work/spec.md" \
      tests/test_slugify.py test_lowercases > .tdd/verify-red.reason 2> .tdd/verify-red.err )
noisy_reason="$(cat "$noisy_dir/.tdd/verify-red.reason" 2>/dev/null)"
[[ "$noisy_reason" == "$noisy_want" ]] && ok \
  || no "#625: a REJECT's reason file carries only the verifier's reason, not stderr from preserve_attempt or anything else verify.sh runs (reason file='${noisy_reason//$'\n'/ / }')"

unpreserved_dir="$work/unpreserved-attempt"
fixture_repo "$unpreserved_dir" argv
mkdir -p "$unpreserved_dir/.tdd"
git -C "$unpreserved_dir" update-ref refs/veri/attempts/625/6 HEAD
( cd "$unpreserved_dir"
  env VERI_ISSUE=625 VERI_STEP=6 CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$unpreserved_dir/argv" \
    FAKE_OUT_TEXT='VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.' \
    "$HERE/../supervise.sh" verdict-red "$HERE/../run-verdict.sh" --step '<STEP>' red "$work/spec.md" \
      tests/test_slugify.py test_lowercases > .tdd/verify-red.reason 2> .tdd/verify-red.err )
unpreserved_seen="$(cat "$unpreserved_dir/.tdd/verify-red.stderr" "$unpreserved_dir/.tdd/events.jsonl" 2>/dev/null)"
[[ "$unpreserved_seen" == *'could not preserve the reject attempt'* ]] && ok \
  || no "#625: a REJECT whose attempt cannot be preserved says so in the verifier's stderr or the event log (verify-red.stderr + events.jsonl='${unpreserved_seen//$'\n'/ / }')"



events_of_in() {
  python3 -c '
import sys, json
count = 0
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == sys.argv[2]:
        count += 1
print(count)
' "$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo 0
}

killed_log_dir="$work/no-verdict-event-killed"
mkdir -p "$killed_log_dir"
( cd "$killed_log_dir" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_STUCK_RETRIES=0 \
    VERI_HEARTBEAT=1 "$VERIFY" red "$work/spec.md" tests/test_slugify.py test_lowercases ) \
  >/dev/null 2>&1
killed_log_code=$?

answered_log_dir="$work/no-verdict-event-answered"
mkdir -p "$answered_log_dir"
verify_in "$answered_log_dir" red 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.' >/dev/null 2>&1
answered_log_code=$?

killed_verdicts="$(events_of_in "$killed_log_dir" verdict)"
killed_exits="$(events_of_in "$killed_log_dir" exit)"
answered_verdicts="$(events_of_in "$answered_log_dir" verdict)"
{ [[ "$killed_log_code" == 2 ]] && [[ "$killed_verdicts" == 0 ]] && [[ "$killed_exits" -ge 1 ]] \
  && [[ "$answered_log_code" == 1 ]] && [[ "$answered_verdicts" == 1 ]]; } && ok \
  || no "a killed verifier leaves no verdict event while an answering one leaves its own (killed arm: code=$killed_log_code want 2, verdict lines=$killed_verdicts want 0, exit marks=$killed_exits want at least 1; answering arm: code=$answered_log_code want 1, verdict lines=$answered_verdicts want 1)"


rebase_verdict() {
  mkdir -p "$1"
  ( cd "$1" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$1/argv" FAKE_OUT_TEXT="$2" \
      "$HERE/../run-verdict.sh" rebase "$work/spec.md" 0123abc 4567def ) >/dev/null 2>&1
  rv_code=$?
  rv_name="$(python3 -c '
import sys, json
hits = []
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == "launch":
        hits.append(obj.get("name", "<<missing>>"))
print(hits[0] if len(hits) == 1 else "<<%d launch lines>>" % len(hits))
' "$1/.tdd/events.jsonl" 2>/dev/null || echo '<<no event log>>')"
}

rebase_verdict "$work/rebase-pass" 'VERDICT: PASS
REASON: The resolution keeps both sides of the contract and the suite is green.'
rb_pass_code=$rv_code rb_pass_name="$rv_name"
rebase_verdict "$work/rebase-reject" 'VERDICT: REJECT
REASON: The resolution drops the onto side of the conflicted hunk.'
rb_reject_code=$rv_code rb_reject_name="$rv_name"
rebase_verdict "$work/rebase-malformed" 'VERDICT: MAYBE
REASON: The resolution might be fine.'
rb_malformed_code=$rv_code rb_malformed_name="$rv_name"
{ [[ "$rb_pass_code" == 0 ]] && [[ "$rb_reject_code" == 1 ]] && [[ "$rb_malformed_code" == 2 ]] \
  && [[ "$rb_pass_name" == verify-rebase ]] && [[ "$rb_reject_name" == verify-rebase ]] \
  && [[ "$rb_malformed_name" == verify-rebase ]]; } && ok \
  || no "run-verdict.sh rebase returns a verify-rebase leaf's verdict, supervised under that name (PASS arm: code=$rb_pass_code want 0, leaf=$rb_pass_name; REJECT arm: code=$rb_reject_code want 1, leaf=$rb_reject_name; malformed arm: code=$rb_malformed_code want 2, leaf=$rb_malformed_name; every leaf want verify-rebase)"

diff_verdict() {  # diff_verdict <dir> <entry> <fake-out> <args…> -> sets $dv_code, $dv_prompt
  local dir="$1" entry="$2" text="$3"
  shift 3
  mkdir -p "$dir"
  ( cd "$dir" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$dir/argv" FAKE_OUT_TEXT="$text" \
      "$HERE/../$entry" "$@" ) >/dev/null 2>"$dir/err"
  dv_code=$?
  dv_prompt=no
  if grep -F 'git diff 0123abc..HEAD' "$dir/argv" >/dev/null 2>&1 \
     && grep -F 'DIFF-STEP the old cases are gone' "$dir/argv" >/dev/null 2>&1 \
     && grep -F 'slugify must lowercase' "$dir/argv" >/dev/null 2>&1; then
    dv_prompt=yes
  fi
}

diff_problems=""
for entry in verify.sh run-verdict.sh; do
  diff_verdict "$work/diff-pass-$entry" "$entry" 'VERDICT: PASS
REASON: the diff removes the cases.' --step 'DIFF-STEP the old cases are gone' --fast-cmd 'make unit' diff "$work/spec.md" 0123abc 0123abc
  [[ "$dv_code" == 0 && "$dv_prompt" == yes ]] \
    || diff_problems="$diff_problems; $entry PASS arm: code=$dv_code want 0, prompt carries spec, step and git diff 0123abc..HEAD: $dv_prompt ($(head -1 "$work/diff-pass-$entry/err"))"
  diff_verdict "$work/diff-reject-$entry" "$entry" 'VERDICT: REJECT
REASON: the diff leaves a case behind.' --step 'DIFF-STEP the old cases are gone' --fast-cmd 'make unit' diff "$work/spec.md" 0123abc 0123abc
  [[ "$dv_code" == 1 ]] \
    || diff_problems="$diff_problems; $entry REJECT arm: code=$dv_code want 1 ($(head -1 "$work/diff-reject-$entry/err"))"
done
[[ -z "$diff_problems" ]] && ok \
  || no "verify.sh and run-verdict.sh --step diff <spec> <branch-base-sha> <step-base-sha> run one blind diff verification: 0 on PASS, 1 on REJECT (${diff_problems#; })"

diff_refusal_problems=""
diff_refused_with() {  # <dir> <entry> <label> <want stderr line> <args…> — records a diff call that is not exit 2 with <want> first on stderr
  local dir="$1" entry="$2" label="$3" want="$4" err=""
  shift 4
  diff_verdict "$dir" "$entry" 'VERDICT: PASS
REASON: ok' "$@"
  IFS= read -r err < "$dir/err"
  [[ "$dv_code" == 2 ]] || diff_refusal_problems="$diff_refusal_problems; $entry $label: code=$dv_code want 2"
  [[ "$err" == "$want" ]] || diff_refusal_problems="$diff_refusal_problems; $entry $label: first stderr line '$err', want '$want'"
}
for entry in verify.sh run-verdict.sh; do
  diff_refused_with "$work/diff-fc-nostep-$entry" "$entry" 'with no --step' \
    "build-verify-prompt: diff needs --step '<STEP>'" \
    --fast-cmd 'make unit' diff "$work/spec.md" 0123abc 0123abc
  diff_refused_with "$work/diff-fc-nonhex-$entry" "$entry" 'with a non-hex base sha' \
    "build-verify-prompt: diff needs <base-sha> as 7-40 lowercase hex characters, got 'not-a-sha'" \
    --step 'DIFF-STEP the old cases are gone' --fast-cmd 'make unit' diff "$work/spec.md" not-a-sha 0123abc
done
[[ -z "$diff_refusal_problems" ]] && ok \
  || no "#995 verify.sh and run-verdict.sh diff with --fast-cmd refuse a missing --step and a non-hex base sha with exit 2 and the named check's own message on stderr (${diff_refusal_problems#; })"

diff_refusal_problems=""
for entry in verify.sh run-verdict.sh; do
  diff_refused_with "$work/diff-fc-extra-$entry" "$entry" 'with an extra argument' \
    "build-verify-prompt: too many arguments" \
    --step 'DIFF-STEP the old cases are gone' --fast-cmd 'make unit' diff "$work/spec.md" 0123abc 0123abc extra
done
[[ -z "$diff_refusal_problems" ]] && ok \
  || no "verify.sh and run-verdict.sh diff with --fast-cmd refuse an extra argument with exit 2 and the extra-argument check's own message first on stderr (${diff_refusal_problems#; })"

empty_step_problems=""
for form in empty trailing; do
  es_dir="$work/empty-step-$form"
  mkdir -p "$es_dir"
  if [[ "$form" == empty ]]; then
    es_args=( --step "" red "$work/spec.md" tests/test_slugify.py test_lowercases )
  else
    es_args=( --step )
  fi
  ( cd "$es_dir" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$es_dir/argv" FAKE_OUT_TEXT='VERDICT: PASS
REASON: ok' "$VERIFY" "${es_args[@]}" ) >/dev/null 2>"$es_dir/err"
  es_code=$?
  [[ "$es_code" == 2 ]] || empty_step_problems="$empty_step_problems; $form: code=$es_code want 2"
  grep -v '^usage:' "$es_dir/err" > "$es_dir/message"
  grep -F -- '--step' "$es_dir/message" >/dev/null || empty_step_problems="$empty_step_problems; $form: stderr names --step only in the usage line ($(head -1 "$es_dir/err"))"
  [[ ! -e "$es_dir/argv" ]] || empty_step_problems="$empty_step_problems; $form: a verifier leaf was launched"
done
[[ -z "$empty_step_problems" ]] && ok \
  || no "#753: verify.sh given --step \"\" or a trailing --step with no value exits 2, names --step on stderr and launches no verifier leaf (${empty_step_problems#; })"

linked_skill="$stubdir/linked-skill"
ln -s "$HERE/../.." "$linked_skill"
caller="$work/linked-caller"
mkdir -p "$caller"
out="$( cd "$caller" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$caller/argv" FAKE_OUT_TEXT='VERDICT: PASS
REASON: run through the link' "$linked_skill/scripts/verify.sh" red "$work/spec.md" tests/test_slugify.py test_lowercases 2>"$caller/err" )"
code=$?
linked_verdict="$(verdict_field_in "$caller" verdict)"
{ [[ "$code" == 0 ]] \
  && [[ "$out" == 'run through the link' ]] \
  && grep -F 'slugify must lowercase' "$caller/argv" >/dev/null \
  && grep -F 'slugify must lowercase' "$caller/.tdd/verify-red.prompt" >/dev/null \
  && [[ "$linked_verdict" == PASS ]]; } && ok \
  || no "verify.sh run through a symlink to the skill directory from another working directory finds its siblings and writes .tdd/ under the caller's directory (code=$code want 0; stdout='$out'; verdict event=$linked_verdict; prompt file $( [[ -e "$caller/.tdd/verify-red.prompt" ]] && echo present || echo missing ); stderr: $(head -3 "$caller/err"))"

finish
