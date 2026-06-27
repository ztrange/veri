#!/usr/bin/env bash
# Tests for scripts/run-leaf.sh — the leaf invocation, driven against a stub `claude` on
# PATH (no real subprocess, no model call). run-leaf builds and execs the `claude -p` call
# for one leaf and streams its output to stdout; it does NOT own a progress log — since #4
# the supervisor (supervise.sh) is the single launch choke point and owns `.tdd/<name>.log`.
#
# The stub `claude` records its argv to $ARGV_OUT, prints $FAKE_OUT_TEXT, exits $FAKE_CODE.
#
# Run: scripts/tests/run-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF="$HERE/../run-leaf.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work"' EXIT
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit "${FAKE_CODE:-0}"
STUB
chmod +x "$stubdir/claude"

run() {  # run <prompt-file> <fake-out-text> <fake-code> [extra args...]
  local pf="$1" text="$2" fcode="$3"; shift 3
  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$work/argv" \
      FAKE_OUT_TEXT="$text" FAKE_CODE="$fcode" \
      "$LEAF" "$pf" "$@" )
}

printf 'Verify the test for issue 3.' > "$work/prompt.txt"

# 1. streams the leaf's stdout to the caller (the supervisor captures it)
out="$(run "$work/prompt.txt" 'hello from leaf
VERDICT: PASS' 0)"
[[ "$out" == *'VERDICT: PASS'* ]] && ok || no "returns leaf stdout"

# 2. feeds the prompt-file contents to claude via -p
grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && ok || no "passes prompt via -p"

# 3. propagates the leaf's non-zero exit status
run "$work/prompt.txt" 'VERDICT: REJECT' 1 >/dev/null; code=$?
[[ "$code" == 1 ]] && ok || no "propagates leaf exit status (got $code)"

# 4. passes extra args through to the leaf (e.g. a tool allowlist)
run "$work/prompt.txt" 'ok' 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

# 5. prompt-file of "-" reads the prompt from stdin
out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

# 6. it does NOT create a progress log itself — that is the supervisor's job now
run "$work/prompt.txt" 'ok' 0 >/dev/null
[[ ! -e "$work/.tdd" ]] && ok || no "does not own a .tdd log"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
