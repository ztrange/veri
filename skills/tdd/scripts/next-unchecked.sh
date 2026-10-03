#!/usr/bin/env bash
# next-unchecked.sh — print the first unchecked step in a ledger, for the cycle loop.
#
# Reads a ledger (checkbox markdown) on stdin and writes the description of the FIRST
# `- [ ]` step (the text after the box), then exits 0. If every step is checked — or there
# are no checkbox steps — it exits 3 with no output, which is the conductor's signal that
# the loop is complete / nothing remains to resume.
#
# The step grammar is lib/ledger.sh's `ledger_steps`, so the description printed here is a
# stable substring to hand back to tick-criterion.sh when the step is checked off.
#
# A step marked `⟦full-suite⟧` is skipped: it is covered by the run's full-suite gate,
# not by a Red/Green cycle, so it is never handed to a leaf. A step marked
# `⟦human-owed⟧` is skipped too: its deliverable is the record of a manual check, owed by
# a human, which no leaf may produce. A marker counts only where *Scope & plan*
# writes it, immediately before the closing `⟦criterion k⟧`; a step whose text quotes one
# anywhere else is an ordinary step and is printed.
#
# Usage:   next-unchecked.sh < .tdd/issue-<n>.md
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/ledger.sh"

while IFS= read -r record; do
  ledger_fields "$record"
  [[ "$state" == open && ( "$kind" == step || "$kind" == diff-checked ) ]] || continue
  printf '%s\n' "$text"
  exit 0
done < <(ledger_steps)

exit 3
