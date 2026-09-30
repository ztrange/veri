#!/usr/bin/env bash
# Unit tests for scripts/run-leaf.sh's reach outside the repository — a leaf's
# `git config --global` must land in a per-leaf copy and never in the operator's own
# global config (issue #276).
# Zero-dependency plain-shell asserts, same idiom as run-leaf.test.sh.
#
# Why this exists: verify.sh snapshots the *repository* and refuses a verdict when the
# verifier changed it (#172), but a leaf reaches further than that. On 2026-09-17 a
# verifier leaf ran `git config --global http.proxy http://127.0.0.1:1` behind a `trap`
# that never fired, and every network git operation on the machine — every push, every
# `run-conductor.sh` launch, the operator's own clones — failed until it was found by
# chance and removed by hand.
#
# Contract under test (this step only):
#   a leaf launched through run-leaf.sh that runs `git config --global <key> <value>`
#                              → the operator's global config (HOME's .gitconfig here) is
#                                byte-identical afterwards, and the leaf still reads its
#                                own write back, so the write went somewhere private
#                                rather than being refused.
#
# Run: scripts/tests/leaf-global-git-config.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF="$HERE/../run-leaf.sh"

source "$HERE/lib/harness.sh"

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
home="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work" "$home"' EXIT

cat > "$stubdir/claude" <<'STUB'
#!/bin/sh
git config --global veri.probe wrote-it 2>/dev/null || true
readback="$(git config --global --get veri.probe 2>/dev/null)" || readback="<unset>"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"result","subtype":"success","is_error":false,"result":"read-back: %s"}\n' \
  "$readback"
STUB
chmod +x "$stubdir/claude"

printf '[user]\n\tname = Operator\n' > "$home/.gitconfig"
cp "$home/.gitconfig" "$work/gitconfig.before"

printf 'Write the failing test for issue 276.' > "$work/prompt.txt"

launch_leaf() {
  ( cd "$work" && env -u GIT_CONFIG_GLOBAL HOME="$home" XDG_CONFIG_HOME="$home/.config" \
      CLAUDE_BIN="$1" "$LEAF" "$work/prompt.txt" 2>&1 )
}

name="a leaf's git config --global leaves the operator's global config byte-identical and the leaf reads the value back"
problems=()
out="$(launch_leaf "$stubdir/claude")"
cmp -s "$work/gitconfig.before" "$home/.gitconfig" ||
  problems+=("want the operator's global config byte-identical, got: $(printf '%q' "$(cat "$home/.gitconfig")")")
[[ "$out" == *'read-back: wrote-it'* ]] ||
  problems+=("want the leaf to read its own write back (read-back: wrote-it), got: $(printf '%q' "$out")")
report "$name"

cat > "$stubdir/claude-reader" <<'STUB'
#!/bin/sh
seen="$(git config --global --get credential.helper 2>/dev/null)" || seen="<unset>"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"result","subtype":"success","is_error":false,"result":"sees: %s"}\n' "$seen"
STUB
chmod +x "$stubdir/claude-reader"
printf '[user]\n\tname = Operator\n[credential]\n\thelper = veri-test-helper\n' > "$home/.gitconfig"

name="a leaf's private global git config starts as a copy of the operator's, so a key present there is visible to the leaf"
problems=()
out="$(launch_leaf "$stubdir/claude-reader")"
[[ "$out" == *'sees: veri-test-helper'* ]] ||
  problems+=("want the leaf to see the operator's credential.helper (sees: veri-test-helper), got: $(printf '%q' "$out")")
report "$name"

finish
