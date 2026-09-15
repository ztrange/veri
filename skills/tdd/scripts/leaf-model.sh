#!/usr/bin/env bash
# leaf-model.sh — say which model one leaf runs on, so a run can price the two leaf roles
# separately (issue #171). Today no leaf chooses: `run-leaf.sh` passes no `--model`, so
# developer and verifier alike run on whatever the operator's `~/.claude/settings.json`
# says, and an experiment that moves one role to a cheaper model cannot be set up at all.
#
# One resolver beside leaf-timeout.sh and refactor-budget.sh, for the same reason: the
# choice is made once, from the environment, and printed — so the caller that builds the
# `claude` command line holds no policy, only the answer.
#
# Usage:   leaf-model.sh <leaf-name>
#          VERI_MODEL=<x> leaf-model.sh <leaf-name>
#
# `VERI_MODEL` is the run-wide knob: it applies to every leaf, so a developer name and a
# verifier name answer the same. Unset or empty prints NOTHING and still exits 0 — nothing,
# not a default. The caller turns a non-empty answer into `--model <value>` and omits the
# flag entirely on an empty one, so any word printed here for a run that chose no model
# would put a flag on a command line that must stay byte-identical to today's.
#
# The value is printed verbatim: aliases (`sonnet`, `opus`, `opus[1m]`) and full ids
# (`claude-sonnet-5`) are the `claude` CLI's vocabulary, not veri's, so this script neither
# maps nor validates them against a list it would have to keep in step with the CLI.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
# The name is taken, and required, before anything is printed: every caller has one to give,
# and the per-role variables that read it are the next cut's. Taking it now is what keeps
# that cut a change to this script's body rather than to every call site's argv.
name="${1:?usage: leaf-model.sh <leaf-name>}"

model="${VERI_MODEL:-}"

# The empty case exits without printing rather than echoing an empty line, so "no model
# chosen" is the absence of output. A caller reading this in a command substitution gets
# the same empty string either way, but one that pipes or tees it sees the difference.
if [[ -n "$model" ]]; then
  echo "$model"
fi
