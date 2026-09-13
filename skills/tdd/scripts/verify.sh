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
#     phase = red | green | refactor | pin
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

# The `verdict` mark (issue #107, ADR-0014). This script is the only place that holds the
# phase and the verdict at once: supervise.sh watched a leaf called `verify-<phase>` succeed
# and knows nothing about what it decided, and parse-verdict.sh read a verdict out of text
# without ever learning which phase the text was about.
#
# The word is derived from $vcode rather than from the reason, because $vcode is what this
# script already turned the leaf's output into — one derivation, not two that must agree.
# `*` covers 2 and nothing else can reach here: parse-verdict.sh exits 0, 1 or 2 only.
case "$vcode" in
  0) word=PASS ;;
  1) word=REJECT ;;
  *) word=malformed ;;
esac

# The mark's other payload value, named beside $word above so the call below reads as the two
# things the event carries rather than as one name and one expression. `%%$'\n'*` strips the
# longest trailing match of newline-and-anything, leaving the first line — the whole of what the
# log takes. A model's justification runs to paragraphs and the log is one line per event; the
# full reason is already mirrored to the issue thread by the conductor, which is where a human
# reads it. A malformed verdict has no reason at all (parse-verdict.sh prints nothing), so this
# is the empty string it actually has.
reason_line="${reason%%$'\n'*}"

# The context comes from leaf-role.sh, the same derivation supervise.sh marks under
# (supervise.sh:141-157), so both halves of one verification file under the same actor and
# phase; a refusal leaves $role empty and nothing is logged, rather than a line whose actor
# was invented.
role="$("$HERE/leaf-role.sh" "verify-$phase")" || role=""
if [[ -n "$role" ]]; then
  # shellcheck disable=SC2086  -- intentional word-split of leaf-role.sh's assignments
  env $role "$HERE/event.sh" verdict verdict="$word" reason="$reason_line"
fi

printf '%s\n' "$reason"
exit "$vcode"
