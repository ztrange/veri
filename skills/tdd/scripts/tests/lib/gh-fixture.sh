#!/usr/bin/env bash
# Sourced by suites: register_pr, which adds a PR to a VERI_GH_JSON fixture's prs.json.
# Usage: source "$HERE/lib/gh-fixture.sh"; register_pr <fixture-dir> <number> <true|false>
# The third argument is the PR's isDraft value. Returns 0.

register_pr() {
  local dir="$1" n="$2" draft="$3" snap
  printf '{"body": "Closes #%s", "state": "OPEN", "isDraft": %s, "url": "https://example.test/pull/%s"}\n' \
    "$n" "$draft" "$n" >> "$dir/prs.lines"
  while :; do
    snap="$(cat "$dir/prs.lines")"
    if declare -F register_pr_between_read_and_write > /dev/null; then
      register_pr_between_read_and_write
    fi
    printf '[%s]\n' "$(printf '%s\n' "$snap" | paste -sd, -)" > "$dir/prs.json.tmp.$$"
    mv "$dir/prs.json.tmp.$$" "$dir/prs.json"
    [[ "$(cat "$dir/prs.lines")" == "$snap" ]] && return 0
  done
}
