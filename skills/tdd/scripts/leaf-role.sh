#!/usr/bin/env bash
# leaf-role.sh — turn a leaf's NAME into the role its events are logged under (issue #107,
# ADR-0014: observability is a per-run event log written by the scripts, not a service).
#
# The writers only ever receive the name: `supervise.sh <name> <cmd>` takes one (supervise.sh:31)
# and the harvester is handed `.tdd/<name>.log`, while an event line's context is `actor`,
# `phase` and `attempt` (event.sh:47-53). Every writer therefore performs the same derivation,
# so it is spelled here once instead of in each of them — two writers that disagreed about what
# `revise-green-2` was would split one leaf's events across two roles in the same log.
#
# Usage:   leaf-role.sh <leaf-name>
#
# Prints the role as environment assignments, `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…`, so a
# caller writes `env $(leaf-role.sh "$name") event.sh launch …`: event.sh reads its context out
# of the environment (event.sh:17-19), and this way the VERI_* names stay spelled in one script
# rather than at every call site.
#
# The three name shapes the run launches are `develop-<phase>` (SKILL.md:643 and its siblings),
# `revise-<phase>-<k>` and `verify-<phase>`. The leading word is the actor — `develop` and
# `revise` are both the developer, since a revise leaf is a fresh developer answering the
# verifier's objection, not a third role — and the phase follows it. Only the revise name
# carries its own attempt; every other leaf is the first attempt at what it does.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
name="${1:?usage: leaf-role.sh <leaf-name>}"

# `%%-*` strips the longest trailing match of `-*`, leaving the leading word; `#*-` strips the
# shortest leading match, leaving everything after it — `red`, `green-2`, `refactor`.
lead="${name%%-*}"
rest="${name#*-}"

case "$lead" in
  develop|revise) actor=developer ;;
  verify)         actor=verifier  ;;
esac

# A trailing `-<digits>` is the attempt the name carries, and what precedes it is the phase; a
# name without one is attempt 1. Not the empty string: event.sh writes every context key
# whether or not it is known (event.sh:22-25), so an absent attempt would be logged as
# `"attempt": ""` on the first launch of every step rather than as the 1 it is.
#
# One regex states the whole split and both halves are read out of its captures — `(.*)` is
# greedy, so on `green-2` it takes `green` and leaves the digits to `([0-9]+)`. Deriving the
# phase separately, by stripping the suffix off `$rest` again, would be a second spelling of
# the same cut that has to agree with the first; two captures of one match cannot disagree.
if [[ "$rest" =~ ^(.*)-([0-9]+)$ ]]; then
  phase="${BASH_REMATCH[1]}"
  attempt="${BASH_REMATCH[2]}"
else
  phase="$rest"
  attempt=1
fi

echo "VERI_ACTOR=$actor VERI_PHASE=$phase VERI_ATTEMPT=$attempt"
