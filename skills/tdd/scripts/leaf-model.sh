#!/usr/bin/env bash
# leaf-model.sh — say which model one leaf runs on, so a run can price the two leaf roles
# separately. Today no leaf chooses: `run-leaf.sh` passes no `--model`, so
# developer and verifier alike run on whatever the operator's `~/.claude/settings.json`
# says, and an experiment that moves one role to a cheaper model cannot be set up at all.
#
# The resolution itself lives in lib/leaf-model.sh's `leaf_model`, sourced below: supervise.sh
# and verify.sh source that file directly and call the function, so a leaf launch pays no
# subprocess for it. This script is the thin CLI left over that contract — its own suite
# (leaf-model.test.sh) still exercises it as a real executable, to hold the CLI's exit code
# and stream contract to the letter, and the preflight steps SKILL.md documents still call it
# by that name.
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
source "$HERE/lib/leaf-model.sh"

# hazard: `${1:?}` aborts with status 1, not the 2 bad arguments owe.
[[ -n "${1:-}" ]] || { echo "usage: leaf-model.sh <leaf-name>" >&2; exit 2; }
name="$1"

leaf_model "$name"
