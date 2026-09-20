#shellcheck shell=sh disable=SC2154
#
# veri's ShellSpec formatter: everything the built-in `progress` formatter prints, except
# that the last line is the count line the Makefile's runner demands.
#
# `make test` does not trust a suite's exit code (#157): it also greps the suite's last line
# for `^[0-9]+ passed, [0-9]+ failed$`, because a suite killed partway under `set -u` exits
# with the status of the command before the one that died — routinely 0. ShellSpec's own
# summary formatter ends a run with "N examples, M failures" followed by two newlines, so a
# ShellSpec suite run under that glob fails the check twice over: wrong words, and a blank
# last line.
#
# This formatter is the cheapest fix that keeps the guard honest. It costs no process: it is
# sourced by the reporter that is already running, not wrapped around it. The alternative was
# a wrapper script per suite translating ShellSpec's summary, which adds a bash start and a
# pipeline to every suite — the cost #322/#323 spent two days removing.
#
# `summary` is deliberately NOT required: it is the formatter that would print the
# "N examples, M failures" line and the trailing blank, and its output would land after this
# one's. Everything else the progress formatter shows — the dots, failure detail, the timing
# line — is kept, so a failing run still reads the same.

require_formatters methods conclusion finished references profiler
[ "$SHELLSPEC_KCOV" ] && require_formatters kcov

create_buffers veri progress

veri_each() {
  case $field_type in (result)
    _mark=''
    case $field_tag in
      succeeded) _mark="." ;;
      warned   ) _mark="W" ;;
      skipped  ) [ "$field_temporary" ] && _mark="S" || _mark="s" ;;
      failed   ) _mark="F" ;;
      todo     ) [ "$field_temporary" ] && _mark="P" || _mark="p" ;;
      fixed    ) [ "$field_temporary" ] && _mark="=" || _mark="-" ;;
    esac
    progress '=' "${field_color}${_mark}${RESET}"
  esac
}

veri_end() {
  progress '=' "${LF}${LF}"

  # An example that did not succeed is a failure for this count's purpose, whatever ShellSpec
  # calls it: a failed expectation, a fatal error, a skip, a pending, an unexpectedly-fixed
  # example. Collapsing them is right here and nowhere else — the count line answers "is this
  # suite green", and veri's own suites have no vocabulary for a skip. The detail stays
  # visible in the lines above, printed by the formatters required at the top.
  _failed=$(( ${failed_count:-0} + ${error_count:-0} + ${skipped_count:-0} \
            + ${todo_count:-0} + ${fixed_count:-0} ))
  _passed=$(( ${example_count:-0} - _failed ))
  [ "$_passed" -lt 0 ] && _passed=0

  veri '+=' "${_passed} passed, ${_failed} failed${LF}"
}

veri_output() {
  progress '>>>'
  output "$1" methods conclusion finished references
  if [ "$SHELLSPEC_KCOV" ]; then output "$1" kcov; fi
  output "$1" profiler
  veri '>>>'
}
