#!/usr/bin/env bash
# leaf-role.sh — turn a leaf's NAME into the role its events are logged under (ADR-0014:
# observability is a per-run event log written by the scripts, not a service).
#
# The mapping itself lives in lib/leaf-role.sh's `leaf_role`, sourced below: every in-process
# writer (supervise.sh, verify.sh, harvest-usage.sh, leaf-model.sh) sources that file directly
# and calls the function, so a leaf launch pays no subprocess for it. This script is the thin
# CLI left over that contract — its own suite (leaf-role.test.sh) still exercises it as a real
# executable, to hold the CLI's exit code and stream contract to the letter.
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
# The three name shapes the run launches are `develop-<phase>` (SKILL.md:415, 469 and 511),
# `revise-<phase>-<k>` (SKILL.md:643) and `verify-<phase>`. `develop` and `revise` are both the
# developer, since a revise leaf is a fresh developer answering the verifier's objection, not a
# third role — which is the one thing about these shapes the notation cannot show, so it is said
# here and the rest is said at the two cuts that perform it (lib/leaf-role.sh).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/leaf-role.sh"

# hazard: `${1:?}` aborts with status 1, not the 2 bad arguments owe.
[[ -n "${1:-}" ]] || { echo "usage: leaf-role.sh <leaf-name>" >&2; exit 2; }
name="$1"

leaf_role "$name"
