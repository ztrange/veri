#!/usr/bin/env bash
# demo-ledger-loop.sh — show the loop + resume primitives draining a ledger (#6).
#
# Deterministic, no model call: drives the REAL next-unchecked.sh and tick-ledger.sh over a
# committed-style ledger to show the conductor's loop — work the first unchecked step, check
# it off, repeat — and that a "stop" mid-way RESUMES from the next unchecked step because
# the ledger (re-read from disk each turn) is the source of truth.
#
# Usage:  fixtures/demo-ledger-loop.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
S="$(cd "$HERE/.." && pwd)/.claude/skills/solve-issue/scripts"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
led="$work/issue-42.md"
cat > "$led" <<'LED'
# Plan for #42 — general slugify

- [ ] slugify lowercases the text
- [ ] spaces become single hyphens
- [ ] runs of non-alphanumerics collapse to one hyphen
- [ ] leading/trailing hyphens are stripped
LED

total=$(grep -c '^- \[' "$led")
echo ">> Plan has $total steps. Looping the cycle over the ledger..."
echo

done_count=0
while step="$("$S/next-unchecked.sh" < "$led")"; do
  done_count=$((done_count + 1))
  echo "  cycle $done_count → working step: \"$step\""
  # (a real run does Red→Green→Refactor here; we just check the step off)
  "$S/tick-ledger.sh" "$led" "$step" >/dev/null
  echo "          ✓ checked off (atomic with the green commit in a real run)"

  # Simulate a STOP after the 2nd step, then RESUME by re-reading the ledger from disk.
  if [[ "$done_count" -eq 2 ]]; then
    echo
    echo "  -- simulated stop (bail / interruption) --"
    echo "  -- resuming: re-reading the ledger; next-unchecked finds where we left off --"
    next="$("$S/next-unchecked.sh" < "$led" || true)"
    echo "     resume point: \"${next:-<none>}\""
    echo
  fi
done

echo
echo "✅ next-unchecked.sh exited 3 — all $total steps checked off, no step repeated or"
echo "   skipped. In a real run this is where the conductor opens the draft PR."
