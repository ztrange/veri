#!/bin/sh
# parallel-conductors.sh — rung 3 of the scope ladder: run several issue-conductors at once
# over the solvable set, from the target repo's primary checkout.
#
# VERI_PARALLEL is how many conductors run at once, default 1. N conductors are N concurrent
# `claude -p` sessions, billed as such, so a value that is not a whole number >= 1 — zero, a
# word, set-but-empty — is a misconfigured run, not a decision: a diagnostic on stderr and
# exit 2 before anything is launched, never a guess at how much to spend.
#
# Usage:   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
exec python3 "$(dirname "$0")/veri/parallel_conductors.py" "$@"
