#!/usr/bin/env bash
# Tests for scripts/run-leaf.sh — the leaf launcher, driven against a stub `claude` on
# PATH (no real subprocess, no model call). It is the substrate seam the supervisor
# slice (#4) will later wrap with heartbeat + timeout; here it must just launch a leaf,
# tee its output to a forensic progress log, and propagate the leaf's exit status.
#
# The stub `claude` records its argv to $ARGV_OUT, prints $FAKE_OUT, exits $FAKE_CODE.
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
      "$LEAF" sample "$pf" "$@" )
}

# A prompt file the launcher will feed to the leaf.
printf 'Verify the test for issue 3.' > "$work/prompt.txt"

# 1. returns the leaf's stdout to the caller
out="$(run "$work/prompt.txt" 'hello from leaf
VERDICT: PASS' 0)"
[[ "$out" == *'VERDICT: PASS'* ]] && ok || no "returns leaf stdout"

# 2. writes a forensic progress log at .tdd/<name>.log holding the leaf output
[[ -f "$work/.tdd/sample.log" ]] && grep -q 'hello from leaf' "$work/.tdd/sample.log" \
  && ok || no "writes .tdd/<name>.log"

# 3. feeds the prompt-file contents to claude via -p
grep -q -- '-p' "$work/argv" && grep -q 'Verify the test for issue 3.' "$work/argv" \
  && ok || no "passes prompt via -p"

# 4. propagates the leaf's non-zero exit status (a REJECT verdict exits 1, etc.)
run "$work/prompt.txt" 'VERDICT: REJECT' 1 >/dev/null; code=$?
[[ "$code" == 1 ]] && ok || no "propagates leaf exit status (got $code)"

# 5. passes extra args through to the leaf (e.g. a tool allowlist)
run "$work/prompt.txt" 'ok' 0 --allowed-tools 'Read,Bash' >/dev/null
grep -q -- '--allowed-tools' "$work/argv" && grep -q 'Read,Bash' "$work/argv" \
  && ok || no "passes extra args through"

# 6. prompt-file of "-" reads the prompt from stdin
out="$(printf 'piped prompt body' | run - 'VERDICT: PASS' 0)"
grep -q 'piped prompt body' "$work/argv" && ok || no "reads prompt from stdin on -"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
