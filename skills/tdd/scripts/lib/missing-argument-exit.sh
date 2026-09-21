# lib/missing-argument-exit.sh — sourced, not run: defines `missing_argument_offender`, the
# one place a call that left out a required argument is judged against the contract
# CLAUDE.md's "Exit codes are the API" fixes — exit 2, "no answer could be obtained", with a
# usage line on stderr — never exit 1, "a clean negative", which the conductor branches on as
# a methodology failure (issue #270).
#
# The check lives here rather than inside the cross-suite guard that runs it over every
# script, so that it can itself be tested: every script in that guard's roster answers with 2
# today, so a case asserting over the real tree would pass whether the check works or not.
# tests/unit/missing-argument-guard.test.sh plants an offender in a scratch directory and
# asks this function about it instead.
#
# missing_argument_offender <scripts-dir> <script> [args …] — runs <scripts-dir>/<script>
# with <args> (stdin from /dev/null, so a script that reads stdin past its guard does not
# swallow the caller's own input, and stdout discarded). Returns 0 when the call refused as
# the contract says; otherwise prints one offender line on stdout, naming the call and what
# it came back with, and returns 1.
#
# `return`, never `exit`: this runs in the caller's shell once sourced, so an `exit` here
# would tear down the suite that is collecting offenders rather than hand it the one it just
# found — the same rule lib/leaf-role.sh's header states at greater length.
missing_argument_offender() {
  local dir="$1" script="$2"; shift 2
  local code=0 err shown="$script${*:+ $*}"
  err="$("$dir/$script" "$@" 2>&1 >/dev/null </dev/null)" || code=$?
  if [[ "$code" != 2 ]]; then
    echo "$shown: want exit 2, got $code"
    return 1
  fi
  if [[ "$err" != *usage* ]]; then
    echo "$shown: exit 2 but no usage line on stderr: ${err:-<nothing on stderr>}"
    return 1
  fi
}

# bare_expansion_offenders <dir> — the other half of the same contract, read off the source
# instead of off a call. `${N:?…}` aborts the shell with status 1, so a script that guards a
# required argument that way answers a missing argument with "a clean negative" however
# carefully its usage text is worded. Calling it cannot always catch that: the expansion may
# sit on a position no roster call reaches — a `${4:?…}` in a script whose first three
# arguments are checked properly — and a script added tomorrow is in no roster at all.
#
# Prints one offender line per guarded position found under <dir>, naming the script, the
# line and the position it guards, and returns 1 when it found any. `return`, never `exit`,
# for the reason the header above gives.
#
# A line whose first non-blank character is `#` is skipped: this contract is argued in prose
# at the head of eight scripts, and every one of those paragraphs quotes the `${N:?…}` shape
# it is telling the reader not to use. Reporting those would make the guard red for saying
# why it exists. The rule is deliberately the whole line and not the tail of one, so a
# `${N:?…}` in a trailing comment beside real code is still reported: distinguishing a `#`
# that opens a comment from one inside a string is a job for a shell parser, and the failure
# this guard is worth having is the one that over-reports a line a human then reads.
bare_expansion_offenders() {
  local dir="$1" found=0 file lineno text n
  for file in "$dir"/*.sh; do
    [[ -e "$file" ]] || continue
    while IFS=: read -r lineno text; do
      [[ "${text#"${text%%[![:space:]]*}"}" == '#'* ]] && continue
      [[ "$text" =~ \$\{([0-9]+):\? ]] || continue
      n="${BASH_REMATCH[1]}"
      echo "${file##*/}:$lineno: guards \$$n with a bare \${N:?…} expansion, which exits 1, not 2"
      found=1
    done < <(grep -nE '\$\{[0-9]+:\?' "$file")
  done
  (( found == 0 )) || return 1
}
