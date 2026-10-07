#!/bin/sh
# build-verify-prompt.sh — assemble a BLIND verifier leaf's prompt for one cycle phase: a shim over veri/build_verify_prompt.py.
#
# The verifier is blind by construction (ADR-0003): this builder's only inputs are the
# issue's behavior spec and the test under review. It has NO parameter for the developer
# leaf's rationale, so the author's reasoning physically cannot reach the verifier — the
# blindness guarantee is structural, not a matter of the conductor remembering to omit it.
#
# usage: build-verify-prompt.sh <phase> <issue-spec-file> <test-path> [<target-test-id>]
# Usage:
#   build-verify-prompt.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#   build-verify-prompt.sh rebase <issue-spec-file> <onto-sha> <pre-rebase-sha>
#   build-verify-prompt.sh --step '<STEP>' --fast-cmd '<CMD>' diff <issue-spec-file> <branch-base-sha> <step-base-sha>
#     phase = red | green | refactor | pin | plan | rebase | transform | diff
#              for plan the third positional names the proposed ledger, not a test;
#              for transform it names the step's predicate record, and the fourth is the
#              step's base sha
#     --step = the ledger's own line for the step under judgement: it scopes the
#              verdict to that criterion, and carries the conductor's words, not the leaf's
#     --fast-cmd = the fast tier's test command, required for green, refactor and diff:
#              verify-green and verify-refactor run it plus the affected suites, and a verifier in a target repository has
#              no detect-test-command.sh of its own to ask. It is a command the conductor
#              detected, never anything the developer leaf wrote.
#
# Prints the assembled prompt on stdout (feed it to run-leaf.sh). Exit 2 on an unknown
# phase, a missing template/spec file, or a green, refactor or diff call without --fast-cmd.
exec python3 "$(cd "$(dirname "$0")" && pwd)/veri/build_verify_prompt.py" "$@"
