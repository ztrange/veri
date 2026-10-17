#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md answers a rejected push, read as text.
#
# Contract under test:
#   1. At both `push-branch.sh` call sites — Green's tick commit and verify-refactor's clear
#      commit — exit 1 sends the run to the reconcile leaf and exit 2 bails; the reconcile
#      instructions launch `develop-reconcile` through `supervise.sh`, re-run
#      `push-branch.sh`, check the ledger's ticks and `⟂ refactor pending` marks, and bail
#      with `reconcile-failed` otherwise; "exits 0 either way" is gone.
#
# Run: scripts/tests/skill-push-reconcile.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"


finish
