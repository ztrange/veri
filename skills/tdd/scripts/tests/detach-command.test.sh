#!/usr/bin/env bash
# Tests for scripts/detach-command.sh — the conductor's detach-then-wait helper for a long
# command such as the baseline or full-suite `make test`.
#
# Run: scripts/tests/detach-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/lib/harness.sh"

finish
