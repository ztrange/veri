#!/usr/bin/env bash
# Tests for scripts/verify.sh — the single "verify" verb the conductor calls. It chains
# the three tested units: build-verify-prompt.sh (blind prompt) → run-leaf.sh (launch a
# claude -p verifier leaf) → parse-verdict.sh (extract the verdict). Driven against a
# stub claude (via CLAUDE_BIN) that prints a canned verdict and records its argv.
#
# `claude -p` always exits 0 regardless of the verdict, so verify.sh's exit status must
# come from PARSING the leaf's output, not from the leaf's process status.
#
# Run: scripts/tests/verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VERIFY="$HERE/../verify.sh"
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
exit 0
STUB
chmod +x "$stubdir/claude"

printf 'slugify must lowercase the title and join words with hyphens.' > "$work/spec.md"

verify() {  # verify <fake-out-text> <phase> -> runs in $work, sets $out/$code
  local text="$1" phase="$2"
  out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$work/argv" \
            FAKE_OUT_TEXT="$text" "$VERIFY" "$phase" "$work/spec.md" \
            tests/test_slugify.py test_lowercases )"
  code=$?
}

# 1. a PASS verdict from the leaf → verify.sh exits 0 and surfaces the reason
verify 'I ran it.
VERDICT: PASS
REASON: Target test and full suite are green.' green
{ [[ "$code" == 0 ]] && [[ "$out" == *'full suite are green'* ]]; } && ok \
  || no "PASS verdict exits 0 with reason (code=$code)"

# 2. a REJECT verdict → exit 1, reason surfaced for mirroring to the issue
verify 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.' red
{ [[ "$code" == 1 ]] && [[ "$out" == *'private helper'* ]]; } && ok \
  || no "REJECT verdict exits 1 with reason (code=$code)"

# 3. malformed leaf output (no verdict) → exit 2, so the conductor never proceeds on a
#    verification it could not read
verify 'the leaf rambled and never rendered a verdict' green
[[ "$code" == 2 ]] && ok || no "malformed leaf output exits 2 (code=$code)"

# 4. the blind prompt actually reaches the leaf: the issue spec is in the leaf's argv,
#    end-to-end through build-verify-prompt.sh
verify 'VERDICT: PASS
REASON: ok' red
grep -q 'slugify must lowercase' "$work/argv" && ok || no "spec reaches the leaf (blind prompt built + passed)"

# 5. an unknown phase fails fast (exit non-zero), surfaced from the builder
out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$work/argv" \
          FAKE_OUT_TEXT='VERDICT: PASS' "$VERIFY" bogus "$work/spec.md" t x 2>/dev/null )"
code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (code=$code)"

# 6. a hung verifier leaf is killed by the supervisor → no verdict → exit 2, so the
#    conductor never proceeds on a verification it could not obtain
cat > "$stubdir/claude-hang" <<'STUB'
#!/usr/bin/env bash
echo "thinking..."; sleep 60
STUB
chmod +x "$stubdir/claude-hang"

# hung_leaf -> sets $out / $code, stderr in $work/err (runs in $work)
# VERI_STUCK_RETRIES=0 is pinned, not inherited: both hung-leaf cases here are about a
# single attempt, so the caller's environment must not be able to add retries (each extra
# attempt waits out the heartbeat window again, changing the suite's wall time).
hung_leaf() {
  out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_STUCK_RETRIES=0 \
            VERI_HEARTBEAT=1 VERI_POLL=0.2 "$VERIFY" red "$work/spec.md" \
            tests/test_slugify.py test_lowercases 2>"$work/err" )"
  code=$?
}

hung_leaf
{ [[ "$code" == 2 ]] && [[ "$out" == *'killed-stuck'* ]]; } && ok \
  || no "hung verifier leaf → killed-stuck exit 2 (code=$code)"

# 7. the `pin` phase (the "already satisfied" outcome, #31) speaks the same three exit
#    codes as red/green/refactor — 0 PASS, 1 REJECT, 2 no verdict — so the conductor can
#    branch on a verify-pin result with exactly the code it already uses for verify-red.
verify 'VERDICT: PASS
REASON: The test passes now and fails under the mutation I applied.' pin
pin_pass_code=$code pin_pass_out="$out"
verify 'VERDICT: REJECT
REASON: The test still passes with the behavior removed.' pin
pin_reject_code=$code
verify 'the pin verifier rambled and never rendered a verdict' pin
pin_none_code=$code
{ [[ "$pin_pass_code" == 0 ]] && [[ "$pin_pass_out" == *'fails under the mutation'* ]] \
  && [[ "$pin_reject_code" == 1 ]] && [[ "$pin_none_code" == 2 ]]; } && ok \
  || no "pin phase exit codes: PASS→0 REJECT→1 no verdict→2 (got $pin_pass_code/$pin_reject_code/$pin_none_code)"

# 8. how many attempts a hung verifier leaf gets is fixed by this suite, not by the shell
#    that ran `make test`: with VERI_STUCK_RETRIES=3 exported in the environment, the
#    hung-leaf launch must still run the leaf exactly once — one killed-stuck status line
#    on stderr and no `retry N/M` line — so both the verdict and the suite's wall time are
#    the suite's own answer. The assignment prefix puts the variable in hung_leaf()'s
#    environment for this call only, so no other case sees it; its `env` list overrides it.
VERI_STUCK_RETRIES=3 hung_leaf
stuck_lines="$(grep -c 'supervise\[verify-red\]: killed-stuck' "$work/err")"
retry_lines="$(grep -c 'retry [0-9][0-9]*/[0-9][0-9]*' "$work/err")"
{ [[ "$code" == 2 ]] && [[ "$stuck_lines" -eq 1 ]] && [[ "$retry_lines" -eq 0 ]]; } && ok \
  || no "ambient VERI_STUCK_RETRIES=3 → hung verifier leaf still runs exactly once (code=$code, killed-stuck lines=$stuck_lines, retry lines=$retry_lines)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
