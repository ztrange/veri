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
