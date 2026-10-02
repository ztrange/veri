#!/usr/bin/env bash
# Sourced by suites: probe_order, which checks a prompt names cp <file> <file>.orig before its
# mutation instruction and mv <file>.orig <file> after its run under mutation.
# Usage: source "$HERE/lib/probe-order.sh"; probe_order <label> <prompt> <mutation regex> <run-under-mutation regex>
# Appends each problem found to the caller's $problems. Returns 0.

offset_of() { local at; at="$(grep -obiE -e "$2" <<<"$1" | cut -d: -f1)"; printf '%s' "${at%%$'\n'*}"; }

probe_order() {
  local label="$1" line cp_at mutate_at run_at mv_at
  line="$(tr '\n' ' ' <<<"$2")"
  cp_at="$(offset_of "$line" 'cp <file> <file>\.orig')"
  mutate_at="$(offset_of "$line" "$3")"
  run_at="$(offset_of "$line" "$4")"
  mv_at="$(offset_of "$line" 'mv <file>\.orig <file>')"
  [[ -n "$cp_at" ]] || problems="$problems; $label never names cp <file> <file>.orig"
  [[ -n "$mv_at" ]] || problems="$problems; $label never names mv <file>.orig <file>"
  [[ -n "$mutate_at" ]] || problems="$problems; $label no longer gives the mutation instruction"
  [[ -n "$run_at" ]] || problems="$problems; $label no longer gives the run under mutation"
  if [[ -n "$cp_at" && -n "$mutate_at" ]] && (( cp_at > mutate_at )); then
    problems="$problems; cp <file> <file>.orig comes after the mutation instruction"
  fi
  if [[ -n "$mv_at" && -n "$run_at" ]] && (( mv_at < run_at )); then
    problems="$problems; mv <file>.orig <file> comes before the run under mutation"
  fi
  return 0
}
