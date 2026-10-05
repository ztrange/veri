#!/usr/bin/env bash
# lib/stop-modes.sh — sourced, not run: defines `STOP_MODES`, the modes a stop request may name,
# `stop_mode_known <mode>`, which returns 0 when `<mode>` is one of them and 1 otherwise, and
# `modes_named`, which prints them as a phrase: "at-ledger, at-leaf or now".
STOP_MODES=(at-ledger at-leaf now)

stop_mode_known() {
  local listed
  for listed in "${STOP_MODES[@]}"; do
    [[ "$1" == "$listed" ]] && return 0
  done
  return 1
}

modes_named() {
  local wanted="${STOP_MODES[*]:0:${#STOP_MODES[@]}-1}"
  printf '%s or %s' "${wanted// /, }" "${STOP_MODES[*]: -1}"
}
