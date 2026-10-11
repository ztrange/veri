#!/usr/bin/env bash
# Tests for scripts/wait-leaf.sh — the foreground half of a detached leaf launch: it blocks
# until the completion file a detached `supervise.sh` writes appears, then exits with the
# code it holds. Driven against stub writers on a stub `date` that advances a fixed step
# per reading.
#
# Contract under test:
#   exit 0 success · 1 leaf-failure · 2 killed-stuck (whatever the supervisor recorded)
#   · 3 nothing to report yet. A completion file absent when the wait begins is polled for.
#
# Run: scripts/tests/wait-leaf.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WAIT="$HERE/../wait-leaf.sh"
source "$HERE/lib/harness.sh"

finish
