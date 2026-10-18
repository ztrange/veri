#!/usr/bin/env bash
# Tests for scripts/ledger-steps.sh — the entry point that prints lib/ledger.sh's
# `ledger_steps` records for the document on its stdin.
#
# Run: scripts/tests/ledger-steps.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
STEPS="$HERE/../ledger-steps.sh"
source "$HERE/lib/harness.sh"


finish
