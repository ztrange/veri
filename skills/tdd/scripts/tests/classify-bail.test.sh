#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
#
# Contract under test:
#   classify-bail.sh killed-stuck         → first stdout line `system`,  exit 0
#   classify-bail.sh <unrecognised>       → error on stderr, exit non-zero
#
# Run: scripts/tests/classify-bail.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../classify-bail.sh"
source "$HERE/lib/harness.sh"

finish
