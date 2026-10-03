#!/usr/bin/env bash
# Sourced by guard suites that keep an EXEMPT associative array: appends to problems one entry
# per key whose reason is blank, ending in the optional suffix $1.
# Usage: source "$HERE/lib/exemption-reasons.sh"; probe_every_exemption_carries_a_reason [suffix]

probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing${1:+: $1}")
  done
  return 0
}
