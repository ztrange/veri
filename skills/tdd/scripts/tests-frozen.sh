#!/usr/bin/env bash
# tests-frozen.sh — record a step's test files, then check that none of them has changed.
#
# usage: tests-frozen.sh record <record-file> <test-file>...
#        tests-frozen.sh check <record-file>
#
# Exit: 0 recorded, or every recorded file is byte-identical (nothing on stdout),
#       1 with one path per line on stdout for each recorded file edited or deleted,
#       2 bad arguments or an unreadable record/file.
set -uo pipefail

usage="usage: tests-frozen.sh record <record-file> <test-file>... | check <record-file>"
mode="${1:-}"
rec="${2:-}"
if [[ -z "$rec" ]]; then
  echo "$usage" >&2
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
    report="$(shasum -a 256 -c "$rec" 2> /dev/null)"; sum_code=$?
    changed="$(printf '%s\n' "$report" | sed -n 's/: FAILED.*$//p')"
    if [[ -n "$changed" ]]; then
      echo "$changed"
      exit 1
    fi
    [[ "$sum_code" -eq 0 ]] || exit 2
    ;;
  *)
    echo "$usage" >&2
    exit 2
    ;;
esac
