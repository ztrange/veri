#!/usr/bin/env bash
# ledger-steps.sh — print lib/ledger.sh's `ledger_steps` records for the ledger on stdin.
#
# Usage:   ledger-steps.sh < .tdd/issue-<n>.md
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/ledger.sh"
ledger_steps
