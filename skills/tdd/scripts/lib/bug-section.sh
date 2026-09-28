#!/usr/bin/env bash
# lib/bug-section.sh — sourced, not run: defines `spec_has_bug_section`.
#
# spec_has_bug_section <spec-file> — returns 0 when the spec carries a `## Bug` heading, 1
# otherwise, including for an unreadable file.
spec_has_bug_section() {
  grep -qE '^## Bug[[:space:]]*$' "$1" 2>/dev/null
}
