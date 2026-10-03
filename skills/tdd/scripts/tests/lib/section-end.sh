#!/usr/bin/env bash
# Sourced by suites: section_end prints the last line of the section the heading on <line> opens —
# the line before the next heading, or the file's last line.
# Usage: source "$HERE/lib/section-end.sh"; section_end <file> <line>

section_end() {
  local next
  next="$(head -1 < <(tail -n "+$(($2 + 1))" "$1" | grep -nE '^#') | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    echo $(($2 + next - 1))
  else
    echo $(($(wc -l < "$1")))
  fi
}
