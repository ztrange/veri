#!/bin/sh
# build-verify-prompt.sh — assemble a BLIND verifier leaf's prompt for one cycle phase: a shim over veri/build_verify_prompt.py.
#
# The verifier is blind by construction (ADR-0003): none of this builder's inputs can carry
# the developer leaf's rationale, and none may be added that could, so the author's reasoning physically cannot reach the verifier — the
# blindness guarantee is structural, not a matter of the conductor remembering to omit it.
#
# usage: build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>|--frozen-edit <sha>] [--branch-base <sha>] [--step-green <sha>] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#        build-verify-prompt.sh [--step '<STEP>'] --branch-base <sha> pin <issue-spec-file> <test-id>...
#        build-verify-prompt.sh --fast-cmd '<CMD>' --branch-base <sha> branch <issue-spec-file>
# Usage:
#   build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] [--supersede-base <sha>|--frozen-edit <sha>] [--branch-base <sha>] [--step-green <sha>] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#   build-verify-prompt.sh [--step '<STEP>'] --branch-base <sha> pin <issue-spec-file> <test-id>...   (1-5 ids)
#   build-verify-prompt.sh rebase <issue-spec-file> <onto-sha> <pre-rebase-sha>
#   build-verify-prompt.sh --fast-cmd '<CMD>' --branch-base <sha> branch <issue-spec-file>
#   build-verify-prompt.sh --step '<STEP>' --fast-cmd '<CMD>' --branch-base <sha> diff <issue-spec-file> <step-base-sha>
#     phase = red | green | refactor | pin | plan | rebase | transform | diff | branch
#              for plan the third positional names the proposed ledger, not a test;
#              for transform it names the step's predicate record, and the fourth is the
#              step's base sha
#     --step = the ledger's own line for the step under judgement: it scopes the
#              verdict to that criterion, and carries the conductor's words, not the leaf's
#     --step-green = required for refactor, refused for any other phase: the step's green
#              tick, whose files bound the refactor; 7-40 lowercase hex, exit 2 otherwise (#4544)
#     --frozen-edit = diff only, and never with --supersede-base: the commit `tests-frozen.sh snapshot
#              --step` printed, so the verifier judges `git diff <sha>~1 <sha>` against what verify-red
#              judged (_verify-diff-frozen.md); 7-40 lowercase hex, exit 2 otherwise (#4730)
#     --fast-cmd = the fast tier's test command, required for green, refactor and diff:
#              verify-green and verify-refactor run it plus the test files covering the files the step changed, and a verifier in a target repository has
#              no detect-test-command.sh of its own to ask. It is a command the conductor
#              detected, never anything the developer leaf wrote.
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase, a missing template/spec file, a green, refactor or diff call without --fast-cmd, or a
# refactor call without --step-green.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(cd "$(dirname "$0")" && pwd)/veri/build_verify_prompt.py" "$@"
