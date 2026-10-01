#!/usr/bin/env bash
# Unit tests for scripts/lib/exit-contract.sh — the usage-and-refuse move, sourced, not run.
# The suite sources the module in a subshell and calls its functions in-process.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   refuse [message] — prints message (if given), then the caller's $USAGE, on stderr; nothing
#   on stdout; exits 2.
#   require_args <n> "$@" — refuses with the caller's $USAGE unless the first n arguments are
#   present and non-empty; returns 0 otherwise.
#
# Run: scripts/tests/unit/exit-contract.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIB="$HERE/../../lib/exit-contract.sh"
source "$HERE/../lib/harness.sh"

CALLER_USAGE="usage: caller.sh <issue-number>"

outcome_of() {
  local dir out err code
  dir="$(scratch_dir)"
  (
    USAGE="$CALLER_USAGE"
    source "$LIB"
    "$@"
    echo "returned $?"
  ) > "$dir/out" 2> "$dir/err" && code=0 || code=$?
  out="$(cat "$dir/out")"
  err="$(cat "$dir/err")"
  printf 'exit=%s stdout=%s stderr=%s' "$code" "$out" "$err"
}

expect_eq "refuse prints its message then the caller's \$USAGE on stderr and exits 2" \
  "$(printf 'exit=2 stdout= stderr=not a number: x\n%s' "$CALLER_USAGE")" \
  "$(outcome_of refuse "not a number: x")"

expect_eq "refuse with no message prints only the caller's \$USAGE on stderr and exits 2" \
  "exit=2 stdout= stderr=$CALLER_USAGE" \
  "$(outcome_of refuse)"

expect_eq "require_args refuses with the caller's \$USAGE unless the first n arguments are present and non-empty, and returns 0 otherwise" \
  "$(printf '%s\n' \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=2 stdout= stderr=$CALLER_USAGE" \
    "exit=0 stdout=returned 0 stderr=" \
    "exit=0 stdout=returned 0 stderr=")" \
  "$(printf '%s\n' \
    "$(outcome_of require_args 2 a)" \
    "$(outcome_of require_args 2 a '')" \
    "$(outcome_of require_args 2 a b)" \
    "$(outcome_of require_args 1 a '')")"

expect_eq "to_contract prints 0, 1, 2 or 3 unchanged and prints 2 for any other code" \
  "$(for printed in 0 1 2 3 2 2 2 2; do
    printf 'exit=0 stdout=%s\nreturned 0 stderr=\n' "$printed"
  done)" \
  "$(for code in 0 1 2 3 4 127 141 255; do
    printf '%s\n' "$(outcome_of to_contract "$code")"
  done)"

exit_of_script() {
  local dir="$1" name="$2" body="$3"
  printf '#!/usr/bin/env bash\n%s\n' "$body" > "$dir/$name"
  bash "$dir/$name" > /dev/null 2>&1 && echo 0 || echo $?
}

sourcing() {
  printf "USAGE='usage: sources.sh'\nsource '%s'\n%s" "$LIB" "$1"
}

ending_with() {
  sourcing "fail_with() { return $1; }
fail_with"
}

ends_dir="$(scratch_dir)"
expect_eq "a script that sources the module and ends outside 0-3, by a set -e abort or by its last command's status, exits 2" \
  "aborts=2 last=2 in-contract=3" \
  "aborts=$(exit_of_script "$ends_dir" aborts.sh "set -e
$(ending_with 5)
echo unreachable") last=$(exit_of_script "$ends_dir" last.sh "$(ending_with 7)") in-contract=$(exit_of_script "$ends_dir" in-contract.sh "$(ending_with 3)")"

with_rc_5() {
  sourcing "rc=5
$1"
}

DECLARED="# pass-through: the caller asks for the foreign command's own status"

pass_dir="$(scratch_dir)"
expect_eq "a script that sources the module hands on a declared pass-through exit's code unmapped outside 0-3, while an undeclared exit outside 0-3 still ends as 2" \
  "declared=5 undeclared=2" \
  "declared=$(exit_of_script "$pass_dir" declared.sh "$(with_rc_5 "$DECLARED
exit \"\$rc\"")") undeclared=$(exit_of_script "$pass_dir" undeclared.sh "$(with_rc_5 "exit \"\$rc\"")")"

expect_eq "a declared pass-through exit indented inside a block hands on its code unmapped outside 0-3" \
  "indented=5" \
  "indented=$(exit_of_script "$pass_dir" indented.sh "$(with_rc_5 "if (( rc != 0 )); then
  $DECLARED
  exit \"\$rc\"
fi")")"

expect_eq "an undeclared exit outside 0-3 ends as 2 even when an identical exit line elsewhere in the script is a declared pass-through" \
  "twin=2" \
  "twin=$(exit_of_script "$pass_dir" twin.sh "$(with_rc_5 "if (( rc == 0 )); then
  $DECLARED
  exit \"\$rc\"
fi
exit \"\$rc\"")")"

expect_eq "a bare exit in a script that sources the module ends with the status of the command before it, mapped unless declared a pass-through" \
  "after-true=0 after-3=3 declared-after-5=5" \
  "after-true=$(exit_of_script "$pass_dir" bare-true.sh "$(with_rc_5 "true
exit")") after-3=$(exit_of_script "$pass_dir" bare-3.sh "$(with_rc_5 "(exit 3)
exit")") declared-after-5=$(exit_of_script "$pass_dir" bare-declared.sh "$(with_rc_5 "(exit 5)
$DECLARED
exit")")"

OWED="its sites are owed a mapping or a marker by a later step of #497"

declare -A OWED_PASS_THROUGHS=(  # [<script>]=why its pass-through sites are still allowed unmarked
  [run-leaf.sh]="$OWED"
  [run-suite.sh]="$OWED"
  [supervise.sh]="$OWED"
  [tick-issue-criterion.sh]="$OWED"
  [tick-ledger.sh]="$OWED"
  [timed-test-run.sh]="$OWED"
  [verify.sh]="$OWED"
  [wait-leaf.sh]="$OWED"
)

pass_through_offenders() {  # pass_through_offenders <script> — print <script>:<line>: <text> per unmapped, unmarked site
  local script="$1" n=0 previous="" line trimmed
  while IFS= read -r line; do
    (( ++n ))
    trimmed="${line#"${line%%[![:space:]]*}"}"
    if [[ "$trimmed" != '#'* && "$line" != *to_contract* \
      && "$line" =~ (^|[\;\&\|\(\)\{\}])[[:space:]]*exit[[:space:]]+(\"?\$[A-Za-z_{0-9]|\"?\$\?) \
      && "$previous" != "# pass-through:"* ]]; then
      printf '%s:%s: %s\n' "${script##*/}" "$n" "$trimmed"
    fi
    previous="$trimmed"
  done < "$script"
}

problems=()
for script in "$HERE"/../../*.sh; do
  [[ -n "${OWED_PASS_THROUGHS[${script##*/}]+x}" ]] && continue
  while IFS= read -r line; do
    problems+=( "$line" )
  done < <(pass_through_offenders "$script")
done
report "every exit \"\$var\" or exit \$? in a script under scripts/ maps through to_contract or carries a # pass-through: <why> marker, outside the table of sites still owed"

finish
