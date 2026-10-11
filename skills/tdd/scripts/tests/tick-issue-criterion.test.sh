#!/usr/bin/env bash
# Tests for scripts/tick-issue-criterion.sh — the thin gh wrapper — driven against a
# stub `gh` on PATH.
#
# Contract under test:
#   tick-issue-criterion.sh runs with GH_REPO unset without crashing on an empty
#   repo-args array under `set -u`.
#
# Run: scripts/tests/tick-issue-criterion.test.sh
set -uo pipefail
unset VERI_GH_DRIVER

HERE="$(cd "$(dirname "$0")" && pwd)"
WRAP="$HERE/../tick-issue-criterion.sh"
source "$HERE/lib/harness.sh"

finish
