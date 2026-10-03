#!/usr/bin/env bash
# Unit tests for the files under skills/ — none of them may end a background process by a
# job spec.
#
# Contract under test:
#   No file under skills/ ends a background process by a job spec, outside a comment.
#   An offender is reported as `<file>:<line>`. A site is exempted only by name in the
#   table below with a reason; an entry carrying no reason fails the run.
#   A kill by a recorded pid is not reported.
#
# Run: skills/tdd/scripts/tests/no-job-spec-kills.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SUBJECT='skills'

KILL_WORD='(^|[^[:alnum:]_.-])kill'
JOB_ARGS='([[:space:]]+[^%[:space:]]+)*[[:space:]]+'
JOB_SPEC='%[0-9]'
JOB_SPEC_KILL="$KILL_WORD$JOB_ARGS$JOB_SPEC"

declare -A EXEMPT=(
  [$'skills/tdd/scripts/tests/skill-leaf-env.test.sh:LITERAL_STEP=\'A title naming `kill \x251`, the "blind" verifier, $HOME and the shell s own job spec\'']="a step title's text, single-quoted, that every launch line's leaf must receive as VERI_STEP byte for byte (#608): the job spec is the character under test, and no case runs it; a launch line that ran it would do so in a bash -c with no job table, where it reaches no process at all"
  [$'skills/tdd/scripts/tests/skill-leaf-env.test.sh:EXPANDING_STEP=\'A title naming `kill \x251`, the "blind" verifier and $HOME reaches the leaf as written\'']="a step title's text, single-quoted, that the case hands a launch line as data (#437): the backticks around it are the character under test, and a fixed launch never runs it; an unfixed one runs it in a bash -c with no job table, where it reaches no process at all"
)


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

split_site() {
  local rest
  site_file="${1%%:*}"
  rest="${1#*:}"
  site_line="${rest%%:*}"
  site_text="${rest#*:}"
}

kill_lines() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ "$site_text" =~ ^[[:space:]]*# ]] && continue
    printf '%s\n' "$hit"
  done < <(cd "$ROOT" && grep -rInE -- "$JOB_SPEC_KILL" "$SUBJECT")
  return 0
}

sites() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ -n "${EXEMPT[$site_file:$site_text]:-}" ]] && continue
    printf '%s\n' "$hit"
  done < <(kill_lines)
  return 0
}

probe_no_file_kills_by_job_spec() {
  local site
  while IFS= read -r site; do
    split_site "$site"
    problems+=("$site_file:$site_line ends a background process by a job spec, which names it only in the job table of the shell that started it: once that shell is gone the kill reaches nobody and the process is left running, reparented to PID 1. Kill the pid it recorded instead — see skills/tdd/scripts/lib/background.sh: $(flat "$site_text")")
  done < <(sites)
  return 0
}

probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing: an entry is an exemption only when it says why a name that dies with the shell is the right one at that site")
  done
  return 0
}

name="no file under skills/ ends a background process by a job spec"
problems=()

probe_every_exemption_carries_a_reason
probe_no_file_kills_by_job_spec

report "$name"

probe_every_exemption_still_names_its_site() {
  local hit key
  local -A matched=()
  while IFS= read -r hit; do
    split_site "$hit"
    matched[$site_file:$site_text]+="${matched[$site_file:$site_text]:+, }$site_file:$site_line"
  done < <(kill_lines)
  for key in "${!EXEMPT[@]}"; do
    if [[ "${matched[$key]:-}" == *,* ]]; then
      problems+=("the exemption entry [$key] matches more than one line of its file, so one reason would excuse a second site nobody wrote it for: ${matched[$key]}")
      continue
    fi
    [[ -n "${matched[$key]:-}" ]] && continue
    [[ -e "$ROOT/${key%%:*}" ]] || continue
    problems+=("the exemption entry [$key] names a line that no longer ends a background process by a job spec, so it excuses nothing there: the site it was written for has moved, and its key must follow it")
  done
  return 0
}

name="every exemption names a line under skills/ that ends a background process by a job spec"
problems=()

probe_every_exemption_still_names_its_site

report "$name"

FIXTURE_REL='skills/tdd/scripts/fixture-step.sh'
FIXTURE_TEXT=$'STEP=\'A title naming `kill \x251` as written\''
FIXTURE_KEY="$FIXTURE_REL:$FIXTURE_TEXT"
FIXTURE_REASON="a fixture's step title, quoted, never run"

fixture() {
  printf '%s\n' '#!/usr/bin/env bash' "$FIXTURE_TEXT" 'printf "%s\n" "$STEP"'
}

scratch_fixture() {
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${FIXTURE_REL%/*}"
  cat > "$ROOT/$FIXTURE_REL"
}

probe_lines_inserted_above_an_exemption() {
  local ROOT
  local -A EXEMPT=([$FIXTURE_KEY]="$FIXTURE_REASON")
  scratch_fixture < <(printf '# inserted\n# inserted\n# inserted\n'; fixture)
  probe_no_file_kills_by_job_spec
  probe_every_exemption_still_names_its_site
}

name="lines inserted above an exempted line leave both cases green"
problems=()

probe_lines_inserted_above_an_exemption

report "$name"

probe_an_edited_exempted_line() {
  local ROOT problem
  local -A EXEMPT=([$FIXTURE_KEY]="$FIXTURE_REASON")
  scratch_fixture < <(fixture | sed 's/as written/verbatim/')
  problems=()
  probe_every_exemption_still_names_its_site
  edited_entry_named="not named"
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == *"[$FIXTURE_KEY]"* ]] && edited_entry_named="named"
  done
  problems=()
}

name="editing an exempted line's text turns the stale-exemption case red, naming the entry"
edited_entry_named=""

probe_an_edited_exempted_line

expect_eq "$name" "named" "$edited_entry_named"

probe_an_unexempted_job_spec_kill() {
  local ROOT line problem
  local -A EXEMPT=([$FIXTURE_KEY]="$FIXTURE_REASON")
  scratch_fixture < <(fixture | sed 's/as written/verbatim/')
  line="$(grep -n 'verbatim' "$ROOT/$FIXTURE_REL")"
  line="${line%%:*}"
  problems=()
  probe_no_file_kills_by_job_spec
  unexempted_site_named="not named"
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == "$FIXTURE_REL:$line ends a background process by a job spec"* ]] && unexempted_site_named="named"
  done
  problems=()
}

name="a job-spec kill no exemption's text matches turns the no-job-spec-kill case red, naming <file>:<line>"
unexempted_site_named=""

probe_an_unexempted_job_spec_kill

expect_eq "$name" "named" "$unexempted_site_named"

probe_an_exemption_matching_two_lines() {
  local ROOT line lines=() problem
  local -A EXEMPT=([$FIXTURE_KEY]="$FIXTURE_REASON")
  scratch_fixture < <(fixture; printf '%s\n' "$FIXTURE_TEXT")
  while IFS= read -r line; do
    lines+=("${line%%:*}")
  done < <(grep -nF 'as written' "$ROOT/$FIXTURE_REL")
  problems=()
  probe_every_exemption_carries_a_reason
  probe_no_file_kills_by_job_spec
  probe_every_exemption_still_names_its_site
  matching_lines_expected="${lines[*]}"
  matching_lines_named=""
  for line in "${lines[@]}"; do
    for problem in ${problems+"${problems[@]}"}; do
      if [[ "$problem" == *"$FIXTURE_REL:$line" || "$problem" == *"$FIXTURE_REL:$line"[!0-9]* ]]; then
        matching_lines_named+="${matching_lines_named:+ }$line"
        break
      fi
    done
  done
  problems=()
}

name="an exemption whose text matches two lines of its file fails the run, naming each matching line"
matching_lines_expected=""
matching_lines_named=""

probe_an_exemption_matching_two_lines

expect_eq "$name" "$matching_lines_expected" "$matching_lines_named"

probe_an_exemption_with_no_reason() {
  local ROOT problem
  local -A EXEMPT=([$FIXTURE_KEY]="")
  scratch_fixture < <(fixture)
  problems=()
  probe_every_exemption_carries_a_reason
  probe_no_file_kills_by_job_spec
  reasonless_entry_named="not named"
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == "the exemption entry [$FIXTURE_KEY] carries no reason"* ]] && reasonless_entry_named="named"
  done
  problems=()
}

name="an exemption whose text key carries an empty reason fails the run, naming the entry"
reasonless_entry_named=""

probe_an_exemption_with_no_reason

expect_eq "$name" "named" "$reasonless_entry_named"

finish
