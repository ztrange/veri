#!/usr/bin/env bash
# Unit test for CLAUDE.md as a record of its own rules.
#
# Contract under test:
#   Every rule in the roster below is carried by SOME ONE record of CLAUDE.md — one
#   paragraph, one bullet or one table row — stated in full or in one sentence with a
#   pointer to where its reasoning now lives.
#
# Run: skills/tdd/scripts/tests/claude-md-rules-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
source "$HERE/lib/harness.sh"

finish
