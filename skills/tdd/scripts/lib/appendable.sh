#!/usr/bin/env bash
# lib/appendable.sh — sourced, not run: defines `make_appendable`.
#
# make_appendable <file> — create <file>'s directory and end <file> in a newline, so a `>>`
# onto it starts a line of its own.
#
# hazard: `$(...)` strips trailing newlines, so a file already ending in one reads back empty.
make_appendable() {
  mkdir -p "$(dirname "$1")"
  if [ -s "$1" ] && [ -n "$(tail -c 1 "$1")" ]; then
    echo "" >> "$1"
  fi
}
