#!/bin/sh
# leaf-launchable.sh — preflight's check that a leaf can actually be LAUNCHED: a shim over veri/leaf_launchable.py.
#
# It sits beside the `claude auth status` check SKILL.md preflight 0.2 already makes, and is
# there for the same reason that one gives: every leaf is a `claude -p` subprocess, so a fault
# that makes the binary refuse to start kills each of them at launch — `supervise.sh` exit 1
# before any work — which is neither a verdict nor a hang and therefore has no bail
# classification. A conductor cannot tell it from a leaf that failed on its own merits, so it
# has to be caught before a cycle starts. What a run pays for missing it is not one leaf but
# the whole prologue: the baseline suite, a worktree, the spec, and a `### ▶️ Resuming`
# comment posted to the issue thread for a run that cannot take a single step.
#
# The question is asked of the CAPABILITY, not of one variable's name: the script launches the
# binary and reads what happened. `CLAUDECODE` set by an interactive session was the known
# cause on 2026-09-14 and as of 2026-09-15 the binary no longer refuses on it — so a check
# spelled as "is CLAUDECODE set" would today refuse a working configuration, and would still
# miss the next guard of the same kind. Launching is the only question that survives both.
#
# Usage:   leaf-launchable.sh
# Exit 2, with a diagnostic on stderr, when the probe launch failed — "no answer could be
# obtained", the plumbing speaking, not a clean negative a caller could act on. Nothing is
# printed on stdout, so a conductor reading this in a command substitution captures nothing.
exec python3 "$(dirname "$0")/veri/leaf_launchable.py" "$@"
