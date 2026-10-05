#!/usr/bin/env bash
# lib/report.sh — sourced, not run: defines `report_read`.
#
# report_read <key> <var> [<key> <var> …] — read a leaf's report on stdin and, for every
# line `<key>: <value>`, assign <value> to the variable <var> names. The last occurrence of
# a key wins; a variable whose key never appears is left as the caller set it.
report_read() {
  local _rr_line _rr_i _rr_prefix
  while IFS= read -r _rr_line || [[ -n "$_rr_line" ]]; do
    for ((_rr_i = 1; _rr_i < $#; _rr_i += 2)); do
      _rr_prefix="${!_rr_i}: "
      if [[ "$_rr_line" == "$_rr_prefix"* ]]; then
        _rr_i=$((_rr_i + 1))
        printf -v "${!_rr_i}" '%s' "${_rr_line#"$_rr_prefix"}"
        break
      fi
    done
  done
}
