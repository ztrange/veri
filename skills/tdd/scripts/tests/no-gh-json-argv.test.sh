#!/usr/bin/env bash
# Unit tests for the scripts under skills/tdd/scripts/ — none of them may hand python3 a
# gh JSON document as an argument. The subject is the tree it is run in, as in
# no-job-spec-kills.test.sh.
#
# Contract under test:
#   A variable is a gh JSON document when the same file assigns it from `gh …`, `gh_list`,
#   `gh_json`, a `*_json` function or `cat "$VERI_GH_JSON/…"`. A python3 invocation whose
#   arguments — after a `-c '…'` program, before any redirection — name one is reported as
#   `<file>:<line>`, the line holding those arguments. A site is exempted only by an entry
#   in EXEMPT carrying its reason; an entry with no reason fails the run.
#
# Run: skills/tdd/scripts/tests/no-gh-json-argv.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SUBJECT='skills/tdd/scripts'

GH_SOURCE='^[[:space:]]*(if[[:space:]]+!?[[:space:]]*|!?[[:space:]]*|local[[:space:]]+)?([A-Za-z_][A-Za-z_0-9]*)="?\$\((gh|gh_list|gh_json|[A-Za-z_]*_json)([[:space:]]|\))'
GH_FIXTURE='^[[:space:]]*(local[[:space:]]+)?([A-Za-z_][A-Za-z_0-9]*)="?\$\(cat[[:space:]]+"?\$\{?VERI_GH_JSON'

declare -A EXEMPT=()

source "$HERE/lib/harness.sh"

gh_names() {
  local line
  while IFS= read -r line; do
    if [[ "$line" =~ $GH_SOURCE || "$line" =~ $GH_FIXTURE ]]; then
      printf '%s\n' "${BASH_REMATCH[2]}"
    fi
  done < "$1"
  return 0
}

quotes() { local s="${1//[^\']/}"; printf '%s' "${#s}"; }

python3_args() {
  local line n=0 open=0 tail
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$open" -eq 1 ]]; then
      [[ "$line" == *\'* ]] || continue
      open=0
      printf '%s\t%s\n' "$n" "${line#*\'}"
      continue
    fi
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [[ "$line" =~ (^|[^[:alnum:]_./-])python3([[:space:]]|$) ]] || continue
    tail="${line#*python3}"
    if [[ "$tail" == *"-c '"* && $(( $(quotes "$tail") % 2 )) -eq 1 ]]; then
      open=1
      continue
    fi
    printf '%s\t%s\n' "$n" "$tail"
  done < "$1"
  return 0
}

sites() {
  local file rel names name n args
  while IFS= read -r file; do
    rel="${file#"$ROOT"/}"
    names="$(gh_names "$file")"
    [[ -n "$names" ]] || continue
    while IFS=$'\t' read -r n args; do
      args="${args%%[<|>]*}"
      while IFS= read -r name; do
        if [[ "$args" =~ \$\{?$name([^A-Za-z_0-9]|$) ]]; then
          [[ -n "${EXEMPT[$rel:$n]:-}" ]] && continue
          printf '%s:%s\t%s\t%s\n' "$rel" "$n" "$name" "$args"
        fi
      done <<< "$names"
    done < <(python3_args "$file")
  done < <(find "$ROOT/$SUBJECT" -name '*.sh' -not -path '*/tests/*' | sort)
  return 0
}

probe_no_script_hands_python3_a_gh_document() {
  local site name args
  while IFS=$'\t' read -r site name args; do
    problems+=("$site hands python3 the gh JSON document in \$$name as an argument, which Linux caps at 128 KiB per argument: pass it on stdin or in a file instead:$args")
  done < <(sites)
  return 0
}

probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing")
  done
  return 0
}

name="no script under skills/tdd/scripts/ hands python3 a gh JSON document as an argument"
problems=()

probe_every_exemption_carries_a_reason
probe_no_script_hands_python3_a_gh_document

report "$name"

finish
