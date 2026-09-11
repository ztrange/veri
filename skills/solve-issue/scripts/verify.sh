#!/usr/bin/env bash
# verify.sh — run one blind verification of a cycle phase and return its verdict.
#
# This is the single "verify" verb the conductor calls. It composes the three tested
# units so verification is never improvised (and so the developer's rationale can never
# leak in):
#
#   build-verify-prompt.sh   blind prompt from ONLY the issue spec + test path
#     → run-leaf.sh          launch a claude -p verifier leaf (forensic log in .tdd/)
#       → parse-verdict.sh   extract PASS|REJECT + reason from the leaf's output
#
# Usage:
#   verify.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]
#     phase = red | green | refactor
#
# stdout: the verifier's reason (mirror it to the issue thread).
# exit:   0 PASS · 1 REJECT · 2 malformed verdict or build error.
#
# `claude -p` exits 0 whatever the verdict, so the verdict is taken from PARSING the
# leaf's output, not from the leaf's process status. The verifier leaf is denied Write/
# Edit so it can read the repo and run the test command but cannot fix the code it judges
# — override the leaf's flags with VERIFY_LEAF_ARGS if your environment needs different
# permissions. CLAUDE_BIN (read by run-leaf.sh) overrides the binary for tests.
set -euo pipefail

phase="${1:?usage: verify.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]}"
spec_file="${2:?missing <issue-spec-file>}"
test_path="${3:?missing <test-path>}"
target="${4:-}"

HERE="$(cd "$(dirname "$0")" && pwd)"

# Default verifier sandbox: may read the repo and run tests, but never modify the tree.
# Space-separated tool lists per `claude --help`.
default_leaf_args=(--permission-mode bypassPermissions \
                   --disallowedTools Write Edit MultiEdit NotebookEdit)
if [[ -n "${VERIFY_LEAF_ARGS:-}" ]]; then
  # shellcheck disable=SC2206  -- intentional word-split of caller-supplied flags
  leaf_args=( ${VERIFY_LEAF_ARGS} )
else
  leaf_args=( "${default_leaf_args[@]}" )
fi

# Build the blind prompt (exits 2 on unknown phase / unreadable files — propagated).
prompt="$("$HERE/build-verify-prompt.sh" "$phase" "$spec_file" "$test_path" "$target")"

# Launch the verifier leaf THROUGH THE SUPERVISOR (no leaf is launched directly, #4).
# supervise.sh owns the .tdd/verify-<phase>.log progress log and returns the captured
# output; a hung/runaway verifier is killed and reported killed-stuck (exit 2).
mkdir -p .tdd
promptfile=".tdd/verify-$phase.prompt"
printf '%s' "$prompt" > "$promptfile"

set +e
out="$("$HERE/supervise.sh" "verify-$phase" "$HERE/run-leaf.sh" "$promptfile" "${leaf_args[@]}")"
scode=$?
set -e

# A killed-stuck verifier yields no verdict — surface it as malformed (the conductor
# stops, just as it would on an unparseable verdict).
if [[ "$scode" -eq 2 ]]; then
  echo "verifier leaf killed-stuck — no verdict rendered (see .tdd/verify-$phase.log)"
  exit 2
fi

# The verdict is the parse result of the captured output, not the leaf's process status.
set +e
reason="$(printf '%s' "$out" | "$HERE/parse-verdict.sh")"
vcode=$?
set -e

printf '%s\n' "$reason"
exit "$vcode"
