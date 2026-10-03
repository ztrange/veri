#!/usr/bin/env bash
# Sourced by suites: frontmatter_name prints the name: the frontmatter opening <file>'s first line
# declares, or nothing.
# Usage: source "$HERE/lib/frontmatter-name.sh"; frontmatter_name <file>

frontmatter_name() {
  awk 'NR == 1 && $0 == "---" { inside = 1; next }
       inside && $0 == "---" { exit }
       inside && sub(/^name:[[:space:]]*/, "") { print; exit }' "$1"
}
