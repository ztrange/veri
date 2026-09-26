#!/usr/bin/env bash
# classify-bail.sh — classify a bail's <cause> into a category.
#
# Given a cause as $1, print its category on the first stdout line and exit 0.
# An unrecognised cause prints an error to stderr and exits non-zero (2).
#
# Usage:   classify-bail.sh <cause>
set -euo pipefail

cause="${1:-}"

case "$cause" in
  killed-stuck | no-verdict | reconcile-failed)
    echo system
    ;;
  revise-exhausted | untestable-criterion | step-too-big | rebase-unresolved)
    echo process
    ;;
  *)
    echo "classify-bail: unknown cause: $cause" >&2
    exit 2
    ;;
esac
