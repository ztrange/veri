#!/usr/bin/env bash
# lib/verify-options.sh — sourced, not run: defines `verify_takes_a_value`.
#
# verify_takes_a_value <word> — returns 0 if <word> is an option verify.sh reads a value
# after, 1 otherwise, an empty word included.
verify_takes_a_value() {
  case "${1:-}" in
    --step|--fast-cmd) return 0 ;;
    *) return 1 ;;
  esac
}
