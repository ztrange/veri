#!/usr/bin/env bash
# run-conductor.sh — build and run one CONDUCTOR as a `claude -p` subprocess.
#
# The conductor-level counterpart of run-leaf.sh. A conductor typed as `/tdd <n>` into an
# interactive session IS an interactive chat session, and pays for a harness surface it
# never touches: the skills roster, the full tool schemas, the interactive system prompt —
# ~25,000 tokens on every request, re-sent and re-billed each turn (issue #207). Everything
# a conductor does is Bash, Read, Write, Edit and `gh`; it invokes no skill, because it is
# the skill. Running it in print mode buys that surface back.
#
# Usage:   run-conductor.sh <issue>
#
# The prompt is the `/tdd` procedure itself — SKILL.md, verbatim, beside this script — with
# the issue number appended, because print mode loads no skills roster: a conductor launched
# this way cannot be handed the procedure by name, so it is handed the procedure.
#
# `--output-format stream-json --verbose`, the same pair run-leaf.sh:44 passes and for the
# same reason: print mode's default format stays SILENT until the process finishes, so a run
# that takes an hour is indistinguishable from one that died in its first minute. The flags
# turn the launch into a continuous event stream the caller can watch.
#
# `--permission-mode bypassPermissions` because print mode has nobody to approve a tool
# call: without it the `gh`, the `make` and the nested `claude` a leaf needs are all denied,
# and the conductor is a process that can read but cannot act.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

issue="${1:?usage: run-conductor.sh <issue>}"

skill_file="$HERE/../SKILL.md"
[[ -r "$skill_file" ]] || { echo "run-conductor: cannot read '$skill_file'" >&2; exit 2; }

prompt="$(cat "$skill_file")

Solve issue #$issue by the procedure above."

"${CLAUDE_BIN:-claude}" -p "$prompt" \
  --output-format stream-json --verbose \
  --permission-mode bypassPermissions
