#!/bin/sh
# build-develop-prompt.sh — assemble a DEVELOPER leaf's prompt for one cycle phase: a shim over veri/build_develop_prompt.py.
#
# The mirror of build-verify-prompt.sh, and its opposite in emphasis: the verifier builder
# is defined by what it cannot carry (no rationale parameter, so blindness is structural),
# this one by what it must carry. Every run of a phase sends the same instructions from a
# versioned template; the conductor supplies only the variables. That is what removes the
# run-to-run variance of a prompt improvised from prose each cycle.
#
# usage: build-develop-prompt.sh <phase> <issue-spec-file> <step-text> <test-cmd> ...
# Usage:
#   build-develop-prompt.sh red      <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh green    <issue-spec-file> <step-text> <test-cmd> <test-path> <target> <fast-cmd>
#   build-develop-prompt.sh refactor <issue-spec-file> <step-text> <test-cmd> <touched-files>
#   build-develop-prompt.sh cover     <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh transform <issue-spec-file> <step-text> <test-cmd>
#   build-develop-prompt.sh diff      <issue-spec-file> <step-text> <test-cmd> <fast-cmd>
#   build-develop-prompt.sh structural <issue-spec-file> <candidate> <test-cmd> <issue-touched-files>
#   build-develop-prompt.sh predicate <issue-spec-file> <candidate> <test-cmd> <issue-touched-files>
#   build-develop-prompt.sh revise <phase> <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh revise diff <issue-spec-file> <step-text> <test-cmd> <reason-file> <fast-cmd>
#   build-develop-prompt.sh exhausted <issue-spec-file> <step-text> <test-cmd> <reason-file>
#   build-develop-prompt.sh reconcile <issue-spec-file> <step-text> <test-cmd> <branch> <remote-sha>
#   build-develop-prompt.sh over-budget <issue-spec-file> <step-text> <test-cmd> <spent> <budget>
#   build-develop-prompt.sh rebase <issue-spec-file> <step-text> <test-cmd> <onto-sha> <pre-rebase-sha> <conflicting-files>
#
# `refactor` also reads VERI_REFACTOR_BUDGET (default 5) from the environment, the number of
# transforms the leaf may apply.
#
# Prints the assembled prompt on stdout (feed it to supervise.sh). Exit 2 on an unknown
# phase or a missing template/spec file — never a partial prompt.
exec python3 "$(cd "$(dirname "$0")" && pwd)/veri/build_develop_prompt.py" "$@"
