#!/usr/bin/env bash
# leaf-launchable.sh — preflight's check that a leaf can actually be LAUNCHED (issue #187).
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
set -uo pipefail

# The probe: the cheapest launch of the leaf binary there is. `--version` starts the same
# process a leaf does, so a guard that refuses at startup — which is the whole class of fault
# this script exists for — fires here too, and it costs no model call, no network round trip
# and no tokens on a check every run makes. `CLAUDE_BIN` is the injection seam run-leaf.sh
# already reads (run-leaf.sh:56), so a test can swap the binary the same way every other
# suite does.
#
# stdout is discarded rather than shown: what the probe prints when it SUCCEEDS is a version
# string nobody asked for, and this script's stdout is reserved for saying nothing.
leaf_bin="${CLAUDE_BIN:-claude}"
probe_err="$(mktemp)"
trap 'rm -f "$probe_err"' EXIT
"$leaf_bin" --version >/dev/null 2>"$probe_err" && exit 0

# The refusal quotes what the binary SAID rather than naming a cause of its own. A fixed
# message here would report the fault veri guessed at; the binary's own words report the one
# it hit, which is what keeps this a check about the capability when the next guard arrives
# under a different name.
{
  echo "leaf-launchable: the leaf binary ($leaf_bin) could not be launched, so every leaf of this run would die at launch. It said:"
  sed 's/^/    /' "$probe_err"
  echo "Run the conductor from a plain shell instead — the supported invocation is:"
  echo '    claude -p "/tdd <issue-number>"'
  echo "veri does not work around this itself: a guard of this kind names a risk the binary is refusing to take, and taking it silently on the operator's behalf would put that risk on them without their knowledge."
} >&2
exit 2
