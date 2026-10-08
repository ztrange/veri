#!/bin/sh
# run-conductor.sh — build and run one CONDUCTOR as a `claude -p` subprocess: a shim over veri/run_conductor.py.
#
# The conductor-level counterpart of run-leaf.sh. A conductor typed as `/tdd <n>` into an
# interactive session IS an interactive chat session, and pays for a harness surface it
# never touches: the skills roster, the full tool schemas, the interactive system prompt —
# ~25,000 tokens on every request, re-sent and re-billed each turn. Everything
# a conductor does is Bash, Read, Write, Edit and `gh`; it invokes no skill, because it is
# the skill. Running it in print mode buys that surface back.
#
# usage: run-conductor.sh <issue>
# Exit:    2 a refusal (bash or Python below its floor, no argument, a failed fetch, an
#          unresolvable pin); otherwise the conductor's own status, whatever it is.
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
# name gone from the child's. The `VERI_*` tunables are left alone, because a conductor
# launched in print mode must resolve VERI_MODEL_VERIFIER, REVISE_BUDGET, VERI_STUCK_RETRIES
# and the rest exactly as one started from a chat session does. VERI_NEW_SKILL is the one
# exception: it is not a tunable but this launch's instruction to re-pin, spent by the pin
# decision before any conductor exists. Handed on, it would reach every process the
# conductor spawns, a leaf's `make test` among them.
#
# The procedure goes in on STDIN, not as the argument to `-p`. SKILL.md's first line is the
# YAML frontmatter fence `---`, and the CLI parses a leading-dash argument as an option, so
# passing it by argv died on `unknown option '---` before any conductor existed.
# Nothing parses options on stdin, so the fence — and any future first line — arrives intact.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
exec python3 "$(dirname "$0")/veri/run_conductor.py" "$@"
