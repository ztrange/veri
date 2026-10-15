#!/usr/bin/env bash
# tests-frozen.sh — record a step's test files, then check that none of them has changed.
#
# usage: tests-frozen.sh record <record-file> <test-file>...
#        tests-frozen.sh check <record-file>
#
# Exit: 0 recorded, or every recorded file is byte-identical (nothing on stdout),
#       2 bad arguments or an unreadable record/file.
set -uo pipefail

mode="${1:-}"
rec="${2:-}"
if [[ -z "$rec" ]]; then
  echo "usage: tests-frozen.sh record <record-file> <test-file>... | check <record-file>" >&2
  exit 2
fi

case "$mode" in
  record)
    shift 2
    if [[ $# -eq 0 ]]; then
      echo "tests-frozen.sh: record needs at least one test file" >&2
      exit 2
    fi
    shasum -a 256 -- "$@" > "$rec" || exit 2
    ;;
  check)
    shasum -a 256 -c "$rec" > /dev/null 2>&1 || exit 1
    ;;
  *)
    echo "usage: tests-frozen.sh record <record-file> <test-file>... | check <record-file>" >&2
    exit 2
    ;;
esac
