#!/usr/bin/env bash
# Sourced by suites: plain reads stdin and prints it with * and backticks stripped, lowercased;
# with --join it also joins its lines with spaces.
# Usage: source "$HERE/lib/plain.sh"; plain [--join] < <text>

plain() {
  if [[ "${1-}" == --join ]]; then
    tr -d '*`' | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
  else
    tr -d '*`' | tr '[:upper:]' '[:lower:]'
  fi
}
