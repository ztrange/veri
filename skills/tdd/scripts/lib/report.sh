#!/usr/bin/env bash
# lib/report.sh — sourced, not run: defines `report_read`.
#
# report_read [--optional-space] [--terminated-only] <key> <var> [<key> <var> …] — read a
# leaf's report on stdin and, for every line `<key>: <value>`, assign <value> to the
# variable <var> names. The last occurrence of a key wins; a variable whose key never
# appears is left as the caller set it, unset included.
#   --optional-space   also accept `<key>:<value>`, with no space after the colon
#   --terminated-only  leave a last line with no trailing newline unread
# Returns 2 on an unknown option.
report_read() {
  local _rr_line _rr_i _rr_prefix _rr_value _rr_sep=": " _rr_partial=1
  while [[ "${1-}" == --* ]]; do
    case "$1" in
      --optional-space) _rr_sep=":" ;;
      --terminated-only) _rr_partial=0 ;;
      *) return 2 ;;
    esac
    shift
  done
  while IFS= read -r _rr_line || { (( _rr_partial )) && [[ -n "$_rr_line" ]]; }; do
    for ((_rr_i = 1; _rr_i < $#; _rr_i += 2)); do
      _rr_prefix="${!_rr_i}$_rr_sep"
      if [[ "$_rr_line" == "$_rr_prefix"* ]]; then
        _rr_value="${_rr_line#"$_rr_prefix"}"
        if [[ "$_rr_sep" == ":" ]]; then
          _rr_value="${_rr_value# }"
        fi
        _rr_i=$((_rr_i + 1))
        printf -v "${!_rr_i}" '%s' "$_rr_value"
        break
      fi
    done
  done
}
