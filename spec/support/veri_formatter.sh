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
  # calls it: a failed expectation, a fatal error, a warning, a skip, a pending, an
  # unexpectedly-fixed example. Collapsing them is right here and nowhere else — the count
  # line answers "is this suite green", and veri's own suites have no vocabulary for a skip.
  # The detail stays visible in the lines above, printed by the formatters required at the top.
  #
  # warned_count is in this sum for a reason worth keeping. An example whose subject exits
  # non-zero with no `The status` check is WARNED, not failed: ShellSpec exits 1 for it
  # (--warning-as-failure is on by default) but counts it in neither failed_count nor
  # error_count. Leaving it out made a run that ShellSpec itself called red print
  # `2 passed, 0 failed` — a count line that disagrees with the exit code beside it. The
  # Makefile checks both and would still have failed the suite, so nothing would have got
  # through; but a count line that lies is the exact failure #157 added it to catch, and a
  # guard that only works because a second guard covers it is not a guard. Found by planting
  # the case, not by reading the formatter.
  # warned_count counts only when ShellSpec itself treats a warning as a failure, which is a
  # CLI flag (--{no-}warning-as-failure, default on). The count line's job is to agree with the
  # exit code sitting next to it, and that exit code follows the flag: hard-coding either
  # answer makes the line lie in one of the two configurations, which is the failure #157
  # added it to catch.
  _warned=0
  [ "${SHELLSPEC_WARNING_AS_FAILURE:-}" ] && _warned=${warned_count:-0}
  _failed=$(( ${failed_count:-0} + ${error_count:-0} + _warned + ${skipped_count:-0} \
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
