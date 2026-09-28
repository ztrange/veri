#!/usr/bin/env bash
# detect-test-command.sh — print the one command that runs the full suite of a repo.
#
# Prints the command on stdout and exits 0; prints nothing and exits 3 when it cannot
# decide, which is the conductor's cue to ask the human.
#
# Precedence is first-match-wins: the issue's `Test command:` line, then the tier markers in
# the repo's CLAUDE.md, then .veri/test-command, then inference from the repo's files.
#
# Usage:   detect-test-command.sh [--tier fast|all] [--issue <body-file>] [repo-root]
#          (repo-root defaults to the current directory)
set -euo pipefail

tier=""
if [ "${1:-}" = "--tier" ]; then
  tier="${2:-}"
  shift 2
fi

issue=""
if [ "${1:-}" = "--issue" ]; then
  issue="${2:-}"
  shift 2
fi

root="${1:-.}"

answer() { printf '%s\n' "$1"; exit 0; }

marker='Test command:'

# hazard: a `case` that matches nothing returns 0, so both answers are returned explicitly.
holds_marker() {
  case "$1" in
    *"$marker"*) return 0 ;;
    *) return 1 ;;
  esac
}

quoted() {
  local ticks="${1//[!\`]/}"
  [ $(( ${#ticks} % 2 )) -eq 1 ]
}

ltrim() { printf '%s' "${1#"${1%%[![:space:]]*}"}"; }

unwrapped() {
  case "$1" in
    '`'*)
      local s="${1#\`}"
      printf '%s\n' "${s%%\`*}"
      ;;
    *) printf '%s\n' "$1" ;;
  esac
}

answer_from() {
  local rest="$1" seen="" cmd
  while holds_marker "$rest"; do
    seen="$seen${rest%%"$marker"*}"
    rest="${rest#*"$marker"}"
    if quoted "$seen"; then
      continue
    fi
    cmd="$(unwrapped "$(ltrim "$rest")")"
    if [ -z "$cmd" ]; then
      continue
    fi
    answer "$cmd"
  done
}

# hazard: `|| [ -n "$line" ]` keeps a last line that has no trailing newline.
answer_from_file() {
  local line
  while IFS= read -r line || [ -n "$line" ]; do
    answer_from "$line"
  done < "$1"
}

if [ "$tier" != fast ] && [ -n "$issue" ] && [ -f "$issue" ]; then
  answer_from_file "$issue"
fi

if [ -n "$tier" ] && [ -f "$root/CLAUDE.md" ]; then
  marker="veri: $tier tests:"
  answer_from_file "$root/CLAUDE.md"
fi

override="$root/.veri/test-command"
if [ -f "$override" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    if [ -n "$line" ]; then
      answer "$line"
    fi
  done < "$override"
fi

pkg="$root/package.json"
if [ -f "$pkg" ] && tr -d '[:space:]' < "$pkg" | grep -q '"scripts":{[^}]*"test":'; then
  if [ -f "$root/pnpm-lock.yaml" ]; then
    answer 'pnpm test'
  elif [ -f "$root/yarn.lock" ]; then
    answer 'yarn test'
  else
    answer 'npm test'
  fi
fi

mk="$root/Makefile"
if [ -f "$mk" ] && grep -qE '^test[[:space:]]*:' "$mk"; then
  answer 'make test'
fi

declares() { [ -f "$1" ] && grep -qE "$2" "$1"; }

if [ -f "$root/pytest.ini" ] \
  || declares "$root/pyproject.toml" '^\[tool\.pytest' \
  || declares "$root/setup.cfg" '^\[tool:pytest\]'; then
  answer 'pytest -q'
fi

if [ -f "$root/go.mod" ]; then
  answer 'go test ./...'
fi

if [ -f "$root/Cargo.toml" ]; then
  answer 'cargo test'
fi

# hazard: an unmatched glob stays its literal text, which `[ -f ]` then rejects.
for f in "$root"/tests/test_*.py; do
  if [ -f "$f" ]; then
    answer 'python3 -m unittest discover -q'
  fi
done

exit 3
