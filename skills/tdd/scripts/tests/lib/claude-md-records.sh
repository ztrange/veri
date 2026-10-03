#!/usr/bin/env bash
# Sourced by suites after record-helpers.sh: need_claude_md_records sets passage_from to
# $claude_md and passage_text to the records read from $claude_path; when those are blank it
# appends to problems and returns 1.
# Usage: source "$HERE/lib/claude-md-records.sh"; need_claude_md_records || return

need_claude_md_records() {
  passage_from="$claude_md"
  passage_text="$(records < "$claude_path")"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md could not be read, so nothing could be asked of what it records")
  return 1
}
