#!/usr/bin/env bash
# demo-revise-recovers.sh — show the verdict-axis REVISE LOOP recovering a step (#5).
#
# A blind verifier REJECTs the first attempt; the conductor spawns a fresh developer leaf
# carrying the rejection reason and re-verifies; the second verdict is PASS — so the step
# is recovered automatically within the attempt budget, instead of stopping the run.
#
# This exercises the REAL plumbing — verify.sh → supervise.sh → run-leaf.sh →
# parse-verdict.sh — with a stub `claude` (via CLAUDE_BIN) standing in for the leaves: it
# answers as a verifier that REJECTs on its first call and PASSes on its next (toggled by a
# marker file), and as a developer otherwise. The bounded-loop control flow mirrors the
# "Revising on a REJECT" section of SKILL.md. No GitHub, no real model call.
#
# Usage:  fixtures/demo-revise-recovers.sh        (expect: recovered on attempt 1 → exit 0)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
S="$REPO/skills/solve-issue/scripts"

work="$(mktemp -d)"
state="$(mktemp -d)"
trap 'rm -rf "$work" "$state"' EXIT

# Dispatcher stub: a verifier prompt (built by build-verify-prompt.sh) contains the phrase
# "blind independent verifier". First verifier call REJECTs; later ones PASS. Anything else
# is a developer leaf.
cat > "$state/claude" <<STUB
#!/usr/bin/env bash
if [[ "\$*" == *"blind independent verifier"* ]]; then
  if [[ -e "$state/verified-once" ]]; then
    echo "VERDICT: PASS"
    echo "REASON: the revised test now pins the behavior and fails for the right reason."
  else
    : > "$state/verified-once"
    echo "VERDICT: REJECT"
    echo "REASON: the test asserts an internal helper, not observable behavior."
  fi
else
  echo "developer: rewrote the test to assert observable behavior, per the reason."
fi
exit 0
STUB
chmod +x "$state/claude"

cat > "$work/spec.md" <<'SPEC'
slugify(text) lowercases and hyphenates: slugify("Hello, World!") == "hello-world".
SPEC
testpath="tests/test_slugify.py"
mkdir -p "$work/tests"; : > "$work/$testpath"

REVISE_BUDGET=2
cd "$work"
export CLAUDE_BIN="$state/claude" VERI_HEARTBEAT=10 VERI_TIMEOUT=10 VERI_POLL=0.2

run_verify() { "$S/verify.sh" red "$work/spec.md" "$testpath" test_slug; }

echo ">> initial verify-red ..."
set +e
reason="$(run_verify)"; code=$?
set -e
echo "   verdict: $([[ $code -eq 0 ]] && echo PASS || echo REJECT) — $reason"

attempt=0
while [[ $code -eq 1 && $attempt -lt $REVISE_BUDGET ]]; do
  attempt=$((attempt + 1))
  echo ">> REJECT → revise attempt $attempt/$REVISE_BUDGET (fresh developer leaf carrying the reason)"
  # fresh developer leaf, launched through the supervisor (stub developer here)
  printf 'Address this rejection: %s' "$reason" > "$work/revise.prompt"
  "$S/supervise.sh" "revise-red-$attempt" "$S/run-leaf.sh" "$work/revise.prompt" >/dev/null 2>&1 || true
  echo ">> re-verify-red ..."
  set +e
  reason="$(run_verify)"; code=$?
  set -e
  echo "   verdict: $([[ $code -eq 0 ]] && echo PASS || echo REJECT) — $reason"
done

echo
if [[ $code -eq 0 ]]; then
  echo "✅ Recovered on attempt $attempt within budget $REVISE_BUDGET — the revise loop turned a REJECT into a PASS."
  exit 0
else
  echo "⛔ Still REJECT after $REVISE_BUDGET attempts — would bail the step (process failure)."
  exit 1
fi
