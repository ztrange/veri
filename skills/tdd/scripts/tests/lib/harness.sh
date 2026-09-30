#!/usr/bin/env bash
# Sourced by suites: counters, the ok/no/report/expect_eq helpers and the count line.
# Usage: source "$HERE/lib/harness.sh"; ...; finish
# finish exits non-zero (returns 1) when any assertion failed.

pass="${pass:-0}"
fail="${fail:-0}"
problems=()

ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    ok
  else
    no "$1"
    printf '    %s\n' "${problems[@]}"
  fi
}

expect_eq() {
  if [[ "$2" == "$3" ]]; then
    ok
  else
    no "$1"
    printf '    expected: %s\n    actual:   %s\n' "$2" "$3"
  fi
}

finish() {
  echo "----"
  echo "$pass passed, $fail failed"
  [[ "$fail" -eq 0 ]]
}

_harness_scratch="$(mktemp 2>/dev/null)"
_harness_exits=()

_harness_exit() {
  local cmd dir
  for cmd in ${_harness_exits+"${_harness_exits[@]}"}; do
    eval "$cmd" || true
  done
  [[ -n "$_harness_scratch" ]] || return 0
  while read -r dir; do
    rm -rf "$dir"
  done < "$_harness_scratch"
  rm -f "$_harness_scratch"
}
trap _harness_exit EXIT

scratch_dir() {
  local dir
  dir="$(mktemp -d)"
  echo "$dir" >> "$_harness_scratch"
  echo "$dir"
}

on_exit() { _harness_exits+=("$*"); }

new_repo() {
  git init -q "$@" || return
  git -C "${!#}" config user.name "Test"
  git -C "${!#}" config user.email "test@example.com"
}

claude_stub() {
  printf '#!/bin/sh\n%s\n' "$2" > "$1/claude"
  chmod +x "$1/claude"
}
