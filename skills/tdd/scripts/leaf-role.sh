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
# `revise-<phase>-<k>` and `verify-<phase>`. `develop` and `revise` are both the developer,
# since a revise leaf is a fresh developer answering the verifier's objection, not a third
# role — which is the one thing about these shapes the notation cannot show, so it is said
# here and the rest is said at the two cuts that perform it.
set -euo pipefail

# `${1:?msg}` expands $1, but aborts the shell with msg on stderr if it is unset or empty.
name="${1:?usage: leaf-role.sh <leaf-name>}"

# refuse <reason> — the one way this script says no, and the three things every refusal owes
# whatever made a name unreadable. Exit 2 — no answer could be obtained, the plumbing speaking
# rather than a clean negative — with the diagnostic on stderr and stdout left empty, because
# the caller consumes this as `env $(leaf-role.sh "$name") …` and would word-split a half-role
# printed there into its environment, logging it as if the name had said it. The script's own
# name and the list of shapes are spelled here rather than at each refusal: two arms that came
# to disagree about which shapes are legal would tell one reader's run a different story.
refuse() {
  echo "leaf-role: $1 (want develop-*|revise-*|verify-*)" >&2
  exit 2
}

# The name splits at its first `-` into the two halves the role is read out of, and each cut is
# made where its result is meaningful: this one just above the arm that reads it, the phase's
# below the guard that establishes there is a phase to read at all. Each half is named for what
# it holds rather than for where in the string it sat. `%%-*` strips the longest trailing match
# of `-*`, leaving the leading word, which is the actor's.
actor_word="${name%%-*}"

# An unknown leading word is refused rather than guessed at, since either guess is a silent
# wrong answer in a log whose purpose is telling the pipeline's two halves apart: an actor
# defaulted to `developer` files the leaf's events under a role it never had, and an actor left
# empty writes `"actor": ""` for a leaf that had one.
case "$actor_word" in
  develop|revise) actor=developer ;;
  verify)         actor=verifier  ;;
  *) refuse "unknown leaf name '$name'" ;;
esac

# A name with no `-` at all carries no phase, and is refused for the same reason the unknown
# word above is: the answer would be invented rather than read. The invention is in the two
# expansions themselves — both return the WHOLE string when there is nothing to strip, so
# `develop` would be read as actor `developer` and phase `develop`, a phase no run has, printed
# with exit 0 as if the name had said it.
if [[ "$name" != *-* ]]; then
  refuse "leaf name '$name' says no phase"
fi

# The other half, cut only now that the guard above has established the name has one: `#*-`
# strips the shortest leading match, leaving the phase and, when the name carries one, the
# attempt — `red`, `green-2`, `refactor`.
phase_attempt="${name#*-}"

# A trailing `-<digits>` is the attempt the name carries, and what precedes it is the phase; a
# name without one is attempt 1. Not the empty string: event.sh writes every context key
# whether or not it is known (event.sh:22-25), so an absent attempt would be logged as
# `"attempt": ""` on the first launch of every step rather than as the 1 it is.
#
# One regex states the whole split and both halves are read out of its captures — `(.*)` is
# greedy, so on `green-2` it takes `green` and leaves the digits to `([0-9]+)`. Deriving the
# phase separately, by stripping the suffix off `$phase_attempt` again, would be a second
# spelling of the same cut that has to agree with the first; two captures of one match cannot
# disagree.
if [[ "$phase_attempt" =~ ^(.*)-([0-9]+)$ ]]; then
  phase="${BASH_REMATCH[1]}"
  attempt="${BASH_REMATCH[2]}"
else
  phase="$phase_attempt"
  attempt=1
fi

echo "VERI_ACTOR=$actor VERI_PHASE=$phase VERI_ATTEMPT=$attempt"
