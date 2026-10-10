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
