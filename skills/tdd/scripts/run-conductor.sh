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
# The child is handed the session's `VERI_*` tunables and none of its handles. A nested
# `claude` otherwise inherits the parent's messaging socket and auth token, which is a
# second session wired into the first one's IPC channel; the rest of the eight name the
# parent's session, host session, pid, entrypoint and child-session flag, all of them
# answers to "which session am I" that belong to a session this one is not. Unsetting them
# here is enough: the child inherits this script's environment, so a name gone from it is a
# name gone from the child's. Nothing `VERI_*` is touched, because a conductor launched in
# print mode must resolve VERI_MODEL_VERIFIER, REVISE_BUDGET, VERI_STUCK_RETRIES and the
# rest exactly as one started from a chat session does.
#
# The procedure goes in on STDIN, not as the argument to `-p`. SKILL.md's first line is the
# YAML frontmatter fence `---`, and the CLI parses a leading-dash argument as an option, so
# passing it by argv died on `unknown option '---` before any conductor existed (issue #221).
# Nothing parses options on stdin, so the fence — and any future first line — arrives intact.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

issue="${1:?usage: run-conductor.sh <issue>}"

# The run pins its skill (issue #237): the commit the skill directory is checked out at is
# materialised with `git archive` into a directory of the run's own, and that snapshot — not
# the clone, which a `git pull` in another thread can move mid-run — is the base directory the
# conductor is handed, in the harness's own words, which is where SKILL.md reads `S` from —
# after the procedure, never before it, whose first line must stay the frontmatter fence.
# The snapshot is of the commit, not of the working tree, so an uncommitted edit in the clone
# is not in it. A skill that is not in a git clone runs from where it is, as before.
base="$(cd "$HERE/.." && pwd)"
if commit="$(git -C "$base" rev-parse HEAD 2>/dev/null)"; then
  snapshot="$(mktemp -d)"
  git -C "$base" archive "$commit" . | tar -x -C "$snapshot"
  base="$snapshot"
fi

skill_file="$base/SKILL.md"
[[ -r "$skill_file" ]] || { echo "run-conductor: cannot read '$skill_file'" >&2; exit 2; }

prompt="$(cat "$skill_file")

Base directory for this skill: $base

Solve issue #$issue by the procedure above."

unset CLAUDECODE \
      CLAUDE_CODE_SESSION_ID \
      CLAUDE_CODE_HOST_SESSION_ID \
      CLAUDE_CODE_MESSAGING_SOCKET \
      CLAUDE_CODE_MESSAGING_TOKEN \
      CLAUDE_PID \
      CLAUDE_CODE_CHILD_SESSION \
      CLAUDE_CODE_ENTRYPOINT

printf '%s\n' "$prompt" | "${CLAUDE_BIN:-claude}" -p \
  --output-format stream-json --verbose \
  --permission-mode bypassPermissions
