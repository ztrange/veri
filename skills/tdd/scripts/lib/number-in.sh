#!/usr/bin/env bash
# lib/number-in.sh — sourced, not run: defines `number_in`.
#
# number_in <file> — echo the plain number on <file>'s first line and return 0, or return 1
# when there is none, an empty file included.
number_in() {
  local n=""
  [[ -f "$1" ]] || return 1
  read -r n < "$1" 2>/dev/null || true
  [[ "$n" =~ ^[0-9]+$ ]] || return 1
  printf '%s\n' "$n"
}
