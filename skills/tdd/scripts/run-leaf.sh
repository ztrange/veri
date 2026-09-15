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
# VERI_LEAF_MODEL is the model this leaf runs on, resolved by leaf-model.sh and exported by
# supervise.sh — the one choke point that knows the leaf's name, and so its role (issue
# #171). It is read here rather than resolved here because the run's `launch` event must
# report the very value the command line was built from, not a second reading of the
# environment. Unset or empty means no `--model` flag at all, and the command line is then
# byte-identical to the one this script built before the variable existed.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

prompt_src="${1:?usage: run-leaf.sh <prompt-file|-> [claude args...]}"
shift

if [[ "$prompt_src" == "-" ]]; then
  prompt="$(cat)"
else
  prompt="$(cat "$prompt_src")"
fi

stream_tmp="$(mktemp)"
trap 'rm -f "$stream_tmp"' EXIT

# Stream the leaf's events to stdout (the supervisor captures this — every event is a
# heartbeat) while teeing them aside for result extraction. set +e so pipefail can't abort
# before we read the leaf's real exit status from PIPESTATUS.
set +e
# `--model` only when a model was chosen: an empty array expanded through the `[@]+` guard
# (the same idiom solvable-issues.sh:54 explains) contributes NOTHING, where a quoted
# `"$model"` would pass an empty argument the CLI would have to reject.
model_args=()
[[ -n "${VERI_LEAF_MODEL:-}" ]] && model_args=(--model "$VERI_LEAF_MODEL")
"${CLAUDE_BIN:-claude}" -p "$prompt" --output-format stream-json --verbose \
  "${model_args[@]+"${model_args[@]}"}" "$@" | tee "$stream_tmp"
rc="${PIPESTATUS[0]}"
set -e

# Append the clean final result text so the captured output ends with a parseable verdict.
printf '\n'
"$HERE/extract-result.sh" < "$stream_tmp"

exit "$rc"
