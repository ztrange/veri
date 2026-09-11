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
out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_HEARTBEAT=1 VERI_POLL=0.2 \
          "$VERIFY" red "$work/spec.md" tests/test_slugify.py test_lowercases 2>/dev/null )"
code=$?
{ [[ "$code" == 2 ]] && [[ "$out" == *'killed-stuck'* ]]; } && ok \
  || no "hung verifier leaf → killed-stuck exit 2 (code=$code)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
