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
#          VERI_MODEL_DEVELOPER=<x> leaf-model.sh <leaf-name>
#          VERI_MODEL_VERIFIER=<x> leaf-model.sh <leaf-name>
#
# `VERI_MODEL` is the run-wide knob: it applies to every leaf. `VERI_MODEL_DEVELOPER` and
# `VERI_MODEL_VERIFIER` each apply to one role's leaves only, and beat the run-wide knob
# there — which is the whole point of three variables rather than one: the two roles fail
# differently when priced down, so moving the verifier to a cheaper model must not be the
# same decision as moving the developer. All three unset or empty prints NOTHING and still
# exits 0 — nothing, not a default. The caller turns a non-empty answer into
# `--model <value>` and omits the flag entirely on an empty one, so any word printed here
# for a run that chose no model would put a flag on a command line that must stay
# byte-identical to today's.
#
# The value is printed verbatim: aliases (`sonnet`, `opus`, `opus[1m]`) and full ids
# (`claude-sonnet-5`) are the `claude` CLI's vocabulary, not veri's, so this script neither
# maps nor validates them against a list it would have to keep in step with the CLI.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
name="${1:?usage: leaf-model.sh <leaf-name>}"

# The role comes from leaf-role.sh, the one place a leaf NAME is turned into the half of the
# pipeline it belongs to (leaf-role.sh:18-22: `revise-*` is a developer too). Asking it, rather
# than matching `develop-*|revise-*|verify-*` here, is what stops two scripts disagreeing about
# what `revise-green-2` is — and it is also why the variable names end in the actor word: the
# suffix IS leaf-role.sh's answer, uppercased, so the name→role mapping is spelled once.
#
# Its output is the `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…` line event.sh's callers
# word-split into an environment; only the actor is wanted here, so it is read out of the
# line rather than evaluated — this script chooses a variable to read, and must not be able to
# set one. `tr` rather than `${var^^}`, which bash 3.2 does not have.
role_line="$("$HERE/leaf-role.sh" "$name")"
actor="${role_line#VERI_ACTOR=}"
actor="${actor%% *}"
role_var="VERI_MODEL_$(printf '%s' "$actor" | tr '[:lower:]' '[:upper:]')"

# `${!role_var:-}` reads the variable whose NAME is in role_var. The role's own value is
# taken first and the run-wide one is the fallback, so precedence is the order of this one
# expansion: an empty or unset role variable falls through to `VERI_MODEL`, which is what
# makes "set VERI_MODEL, override one role" the shape the issue asks for.
model="${!role_var:-${VERI_MODEL:-}}"

# Whitespace in the value is the one thing this script can refuse without asking a network
# what a model id is: `claude --model "sonnet 5"` is a SINGLE argument, and no alias or id is
# spelled with a space in it, so the value cannot be a model whatever the CLI's vocabulary
# grows to hold. Refused here rather than at launch because preflight runs this script once
# per role before any branch or leaf, so the run stops at the typo instead of paying a whole
# leaf to discover it. The test is the resolved value, not each variable, since the refusal is
# of what reached the command line — a role variable's whitespace is the same wrong argv as
# VERI_MODEL's. Only whitespace: `opus[1m]` is what the development machine actually runs on,
# so a guard written as "plain alphanumeric only" would take the brackets with the spaces and
# break every leaf.
#
# Exit 2 — no answer could be obtained, the plumbing speaking rather than a clean negative —
# with the diagnostic on stderr and stdout left empty, the same shape leaf-role.sh refuses in:
# supervise.sh reads this in a command substitution, so a refused value half-printed on stdout
# would reach `--model` anyway, which is the failure the refusal exists to stop.
if [[ "$model" =~ [[:space:]] ]]; then
  echo "leaf-model: model '$model' contains whitespace (a model id or alias is one word)" >&2
  exit 2
fi

# The empty case exits without printing rather than echoing an empty line, so "no model
# chosen" is the absence of output. A caller reading this in a command substitution gets
# the same empty string either way, but one that pipes or tees it sees the difference.
if [[ -n "$model" ]]; then
  echo "$model"
fi
