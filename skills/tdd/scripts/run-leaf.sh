#!/usr/bin/env bash
# run-leaf.sh — build and exec one `claude -p` leaf, streaming its output to stdout.
#
# A leaf is a single short-lived subprocess that performs one step (write the failing
# test, implement, refactor) or one blind verification, then returns. run-leaf is the
# inner invocation; it is NOT launched directly — the supervisor (supervise.sh) is the
# single launch choke point (ADR-0002) and owns the `.tdd/<name>.log` progress log by
# capturing this script's stdout/stderr.
#
# Leaves run in `--output-format stream-json` so the leaf emits events *continuously* as
# it works: that streamed output is what gives the supervisor a real heartbeat (text mode
# stays silent until the very end, so a working leaf is indistinguishable from a hung one).
# The raw stream is emitted to stdout (captured as the progress log), then the clean final
# result text is appended via extract-result.sh so parse-verdict.sh reads a parseable
# verdict at the tail.
#
# Usage:
#   run-leaf.sh <prompt-file> [claude args...]
#   run-leaf.sh -             [claude args...]   # prompt read from stdin
#
# Exit status is the leaf's own — forwarded by supervise.sh.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
#
# A leaf gets its OWN global git config. `GIT_CONFIG_GLOBAL` names the single
# file git reads and writes for `--global`, so pointing it at a per-leaf file makes a
# leaf's `git config --global` land there and die with the leaf. It is not a refusal: the
# leaf writes and reads its own keys back normally, which is what a leaf legitimately
# configuring git for itself needs. Without it, a leaf that sets a key behind a `trap`
# that never fires — killed, timed out, backgrounded — leaves the change in the operator's
# own `~/.gitconfig` for every other run on the machine, which is how a stray
# `http.proxy http://127.0.0.1:1` broke every push and every conductor launch on
# 2026-09-17.
#
# VERI_LEAF_MODEL is the model this leaf runs on, resolved by leaf-model.sh and exported by
# supervise.sh — the one choke point that knows the leaf's name, and so its role.
# It is read here rather than resolved here because the run's `launch` event must
# report the very value the command line was built from, not a second reading of the
# environment. Unset or empty means no `--model` flag at all, and the command line is then
# byte-identical to the one this script built before the variable existed.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

[[ -n "${1:-}" ]] || { echo "usage: run-leaf.sh <prompt-file|-> [claude args...]" >&2; exit 2; }
prompt_src="$1"
shift

if [[ "$prompt_src" == "-" ]]; then
  prompt="$(cat)"
else
  prompt="$(cat "$prompt_src")"
fi

stream_tmp="$(mktemp)"
leaf_gitconfig="$(mktemp)"
trap 'rm -f "$stream_tmp" "$leaf_gitconfig"' EXIT
if [[ -f "$HOME/.gitconfig" ]]; then
  cp "$HOME/.gitconfig" "$leaf_gitconfig"
fi
export GIT_CONFIG_GLOBAL="$leaf_gitconfig"

# hazard: set -e with pipefail would abort before PIPESTATUS is read.
set +e
model_args=()
[[ -n "${VERI_LEAF_MODEL:-}" ]] && model_args=(--model "$VERI_LEAF_MODEL")
"${CLAUDE_BIN:-claude}" -p "$prompt" --output-format stream-json --verbose \
  "${model_args[@]+"${model_args[@]}"}" "$@" | tee "$stream_tmp"
rc="${PIPESTATUS[0]}"
set -e

printf '\n'
"$HERE/extract-result.sh" < "$stream_tmp"

exit "$rc"
