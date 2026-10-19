#!/usr/bin/env bash
# Unit tests for scripts/harvest-usage.sh — the harvester that turns a leaf's closing usage
# record into one event-log line.
#
# Contract under test:
#   harvest-usage.sh <leaf-name>  → reads `.tdd/<leaf-name>.log` relative to the directory
#                                   it is run in, and exits 0.
#   the event log                 → gains exactly one `usage` line, carrying the eight
#                                   numbers of the closing `result` record.
#   a log with no such record     → nothing is appended and the harvester says so on stderr,
#                                   naming itself and the leaf.
#
# Run: scripts/tests/harvest-usage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

source "$HERE/lib/harness.sh"

finish
