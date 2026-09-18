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
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the criterion broke rather than just that it did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
home="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work" "$home"' EXIT

# The stub `claude` is the leaf that misbehaves: it writes a key with
# `git config --global` and reads it straight back, reporting what it saw in the
# stream-json result event run-leaf appends via extract-result.sh. Both halves of the
# criterion are observable from outside — the file on disk, and this line of output.
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
git config --global veri.probe wrote-it 2>/dev/null || true
readback="$(git config --global --get veri.probe 2>/dev/null)" || readback="<unset>"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"result","subtype":"success","is_error":false,"result":"read-back: %s"}\n' \
  "$readback"
STUB
chmod +x "$stubdir/claude"

# The operator's global config as it stands at launch. A real one is never empty, so the
# probe is a file with content: a truncation, an appended section and a rewritten file all
# have to show up as a difference, and only a byte-for-byte comparison catches all three.
printf '[user]\n\tname = Operator\n' > "$home/.gitconfig"
cp "$home/.gitconfig" "$work/gitconfig.before"

printf 'Write the failing test for issue 276.' > "$work/prompt.txt"

# 1. Criterion 1. The leaf's `git config --global` must be private to the leaf, which is
#    two facts and not one: the operator's file is untouched, AND the leaf reads its own
#    write back. Either alone is satisfiable the wrong way — a run-leaf that pointed
#    GIT_CONFIG_GLOBAL at /dev/null or an unwritable path would leave the operator's file
#    perfect while silently breaking every leaf that legitimately configures git for
#    itself, and a leaf that read the value back proves nothing about where it landed.
#    `HOME` is the operator here: the suite must never write the machine's real
#    ~/.gitconfig, which is the very accident this issue is about, and `env -u` clears an
#    ambient GIT_CONFIG_GLOBAL so the answer is a fact about run-leaf.sh rather than about
#    the shell that ran the suite (hermetic-suites.test.sh's concern). XDG_CONFIG_HOME is
#    pointed inside the sandbox for the same reason — git falls back to it for --global
#    writes, so leaving the operator's own would aim the misbehaving leaf at it.
name="a leaf's git config --global leaves the operator's global config byte-identical and the leaf reads the value back"
problems=()
out="$( cd "$work" && env -u GIT_CONFIG_GLOBAL HOME="$home" XDG_CONFIG_HOME="$home/.config" \
    CLAUDE_BIN="$stubdir/claude" "$LEAF" "$work/prompt.txt" 2>&1 )"
cmp -s "$work/gitconfig.before" "$home/.gitconfig" ||
  problems+=("want the operator's global config byte-identical, got: $(printf '%q' "$(cat "$home/.gitconfig")")")
[[ "$out" == *'read-back: wrote-it'* ]] ||
  problems+=("want the leaf to read its own write back (read-back: wrote-it), got: $(printf '%q' "$out")")
report "$name"

# 2. Criterion 2. Private must not mean empty: the leaf's copy starts as the operator's
#    global config, so what the operator configured for git — a credential helper,
#    `url.*.insteadOf` — still works inside the leaf. A run-leaf that handed every leaf a
#    blank file would pass case 1 while breaking every authenticated push a leaf makes.
#    The probe is a key the operator's file holds and the leaf only reads, so the answer
#    is about what the copy started with, not about what the leaf wrote into it.
cat > "$stubdir/claude-reader" <<'STUB'
#!/usr/bin/env bash
seen="$(git config --global --get credential.helper 2>/dev/null)" || seen="<unset>"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '{"type":"result","subtype":"success","is_error":false,"result":"sees: %s"}\n' "$seen"
STUB
chmod +x "$stubdir/claude-reader"
printf '[user]\n\tname = Operator\n[credential]\n\thelper = veri-test-helper\n' > "$home/.gitconfig"

name="a leaf's private global git config starts as a copy of the operator's, so a key present there is visible to the leaf"
problems=()
out="$( cd "$work" && env -u GIT_CONFIG_GLOBAL HOME="$home" XDG_CONFIG_HOME="$home/.config" \
    CLAUDE_BIN="$stubdir/claude-reader" "$LEAF" "$work/prompt.txt" 2>&1 )"
[[ "$out" == *'sees: veri-test-helper'* ]] ||
  problems+=("want the leaf to see the operator's credential.helper (sees: veri-test-helper), got: $(printf '%q' "$out")")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
