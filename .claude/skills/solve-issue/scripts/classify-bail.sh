#!/usr/bin/env bash
# classify-bail.sh — classify a bail's <cause> into a category.
#
# Given a cause as $1, print its category on the first stdout line and exit 0.
#
# Usage:   classify-bail.sh <cause>
set -euo pipefail

cause="${1:-}"

case "$cause" in
  killed-stuck | no-verdict)
    echo system
    ;;
esac
