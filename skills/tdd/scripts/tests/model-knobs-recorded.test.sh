#!/usr/bin/env bash
# Unit tests for the two root documents' record of the per-role model tunables — which
# variable a leaf reads, and why the developer's and the verifier's are two knobs.
#
# Contract under test:
#   SKILL.md's `supervise.sh` bullet lists all three tunables — `VERI_MODEL`,
#   `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER` — beside the tunables it already lists;
#   and CLAUDE.md names all three and says why the developer's and the verifier's are
#   separate knobs: the verdict distribution on one side, revise cycles on the other.
#   Each fact is matched by a regex, not a fixed string.
#
# Run: skills/tdd/scripts/tests/model-knobs-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"
source "$HERE/lib/claude-md-records.sh"

MODEL_ANY='veri_model([^_a-z]|$)'
MODEL_DEV='veri_model_developer'
MODEL_VER='veri_model_verifier'

passage_text="" passage_from=""

need_supervise_bullet() {
  passage_from="$skill_md's supervise.sh bullet"
  passage_text="$(bullet '^[-*] .*supervise\.sh')"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$skill_md has no top-level 'supervise.sh' bullet to read, so the tunables an operator looks up beside VERI_TIMEOUT could not be found")
  return 1
}

names_all_three() {
  local what="$1"
  says "$what — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER" \
    "$MODEL_ANY" "$MODEL_DEV" "$MODEL_VER"
}

probe_skill_bullet_lists_the_tunables() {
  need_supervise_bullet || return

  names_all_three "lists the three model tunables beside the ones it already lists"
}

probe_claude_md_names_them_and_why() {
  need_claude_md_records || return

  names_all_three "names the three model tunables"

  says "why the developer's and the verifier's models are separate knobs — the two roles named, that the knobs are not one, and how each one's regression shows up: a changed verdict distribution against more revise cycles" \
    'developer' \
    'verifier' \
    'separate|two knobs|one knob|independent|its own|their own|never merged' \
    'verdict' \
    'revise'
}

name="$skill_md's supervise.sh bullet and $claude_md name VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, and $claude_md says why developer and verifier are separate knobs"
problems=()

probe_skill_bullet_lists_the_tunables
probe_claude_md_names_them_and_why

report "$name"

helpers_rel="skills/tdd/scripts/tests/record-helpers.sh"
helpers_path="$ROOT/$helpers_rel"

need_helpers_file() {
  [[ -f "$helpers_path" ]] && return 0
  problems+=("$helpers_rel does not exist, so there is no shared $1 to source")
  return 1
}

same_as_copies() {
  [[ "$3" == "$4" ]] && return 0
  problems+=("sourcing $helpers_rel and calling $1 printed:" "$3" "where $2 print:" "$4")
}

probe_shared_report_and_plain() {
  if [[ "$helpers_rel" == *.test.sh ]]; then
    problems+=("$helpers_rel is named *.test.sh, so make test would run it as a suite")
    return
  fi
  need_helpers_file "report or plain" || return

  local got expected
  got="$(
    unset -f report plain
    unset pass fail
    # shellcheck source=/dev/null
    source "$helpers_path"
    printf 'plain: %s\n' "$(printf '**Never** `VERI_MODEL` Merged\n' | plain)"
    problems=()
    report "a clean case"
    printf 'after clean: %s passed, %s failed\n' "$pass" "$fail"
    problems=("first problem" "second problem")
    report "a broken case"
    printf 'after broken: %s passed, %s failed\n' "$pass" "$fail"
  )"
  expected="plain: never veri_model merged
after clean: 1 passed, 0 failed
FAIL - a broken case
    first problem
    second problem
after broken: 1 passed, 1 failed"

  same_as_copies "plain and report" "the *-recorded.test.sh suites' own copies" "$got" "$expected"
}

name="$helpers_rel, not named *.test.sh, when sourced defines report and plain with the same behaviour as the *-recorded.test.sh suites' copies"
problems=()

probe_shared_report_and_plain

report "$name"

probe_shared_records_bullet_says() {
  need_helpers_file "records, bullet or says" || return

  local got expected
  got="$(
    unset -f report plain records bullet says
    unset pass fail
    # shellcheck source=/dev/null
    source "$helpers_path"
    printf 'records: [%s]\n' "$(printf -- '- One\n  cont\n\npara line1\nline2\n* **Two** `x`\n' | records)"
    skill_path=/dev/stdin
    printf 'bullet: [%s]\n' "$(bullet 'alpha' <<< $'# Head\n- alpha **One**\n  still alpha\n- beta')"
    passage_text="$(printf 'first line has foo\nsecond has foo and bar\n')"
    passage_from="doc.md"
    problems=()
    says "foo and bar" 'foo' 'bar'
    printf 'says found: %s, %s problems\n' "$?" "${#problems[@]}"
    says "baz" 'baz'
    printf 'says missing: %s\n' "${problems[@]}"
  )"
  expected="records: [- one   cont
para line1 line2
 two x]
bullet: [- alpha one   still alpha ]
says found: 0, 0 problems
says missing: doc.md does not say baz"

  same_as_copies "records, bullet and says" "the selection-order-recorded suite's and this suite's own copies" \
    "$got" "$expected"
}

name="$helpers_rel, when sourced, also defines records, bullet and says with the same behaviour as the selection-order-recorded and model-knobs-recorded suites' copies"
problems=()

probe_shared_records_bullet_says

report "$name"


defines_function() {
  [[ "$1" =~ (^|$'\n')[[:space:]]*(function[[:space:]]+)?$2[[:space:]]*\(\) ]]
}

probe_suite_uses_shared_helpers() {
  local suite_rel="skills/tdd/scripts/tests/$1.test.sh" text fn
  shift
  if ! text="$(cat "$ROOT/$suite_rel" 2>/dev/null)"; then
    problems+=("$suite_rel could not be read")
    return
  fi
  [[ "$text" =~ (^|$'\n')(source|\.)[[:space:]][^$'\n']*record-helpers\.sh ]] ||
    problems+=("$suite_rel does not source record-helpers.sh at its top level")
  for fn in "$@"; do
    defines_function "$text" "$fn" &&
      problems+=("$suite_rel still defines its own $fn")
  done
}

name="the selection-order-recorded and model-knobs-recorded suites source $helpers_rel and define no report, plain, records, bullet or says of their own"
problems=()

for stem in selection-order-recorded model-knobs-recorded; do
  probe_suite_uses_shared_helpers "$stem" report plain records bullet says
done

report "$name"


probe_suite_keeps_own_says() {
  local suite_rel="skills/tdd/scripts/tests/$1.test.sh" text
  text="$(cat "$ROOT/$suite_rel" 2>/dev/null)" || return
  defines_function "$text" says ||
    problems+=("$suite_rel no longer defines its own says")
}

name="the lane-rule-recorded and unit-tier-recorded suites source $helpers_rel and define no report or plain of their own, while each keeps its own says"
problems=()

for stem in lane-rule-recorded unit-tier-recorded; do
  probe_suite_uses_shared_helpers "$stem" report plain
  probe_suite_keeps_own_says "$stem"
done

report "$name"

probe_shared_helpers_from_elsewhere() {
  need_helpers_file "report, plain, records, bullet or says" || return

  local missing
  missing="$(
    unset -f report plain records bullet says
    cd / || exit
    # shellcheck source=/dev/null
    source "$helpers_path" > /dev/null 2>&1
    for fn in report plain records bullet says; do
      declare -F "$fn" > /dev/null || printf '%s\n' "$fn"
    done
  )"
  local fn
  while IFS= read -r fn; do
    [[ -n "$fn" ]] && problems+=("sourcing $helpers_rel from / did not define $fn")
  done <<< "$missing"
}

name="$helpers_rel sourced from a working directory other than the repo root defines report, plain, records, bullet and says"
problems=()

probe_shared_helpers_from_elsewhere

report "$name"


probe_suite_resolves_helpers_from_itself() {
  local suite_rel="skills/tdd/scripts/tests/$1.test.sh" text var
  if ! text="$(cat "$ROOT/$suite_rel" 2>/dev/null)"; then
    problems+=("$suite_rel could not be read")
    return
  fi
  if [[ "$text" =~ (^|$'\n')(source|\.)[[:space:]]+\"?\$\{?([A-Za-z_][A-Za-z_0-9]*)\}?/record-helpers\.sh ]]; then
    var="${BASH_REMATCH[3]}"
    [[ "$text" =~ (^|$'\n')$var=[^$'\n']*(\$0|BASH_SOURCE) ]] ||
      problems+=("$suite_rel sources record-helpers.sh under \$$var, which is not assigned from the suite's own path")
  else
    problems+=("$suite_rel does not source record-helpers.sh by a path under a variable holding its own directory")
  fi
  [[ "$text" =~ (^|$'\n')finish($'\n'|$) ]] ||
    problems+=("$suite_rel does not end in the harness's finish, which prints its count line")
}

name="the selection-order-recorded, lane-rule-recorded, unit-tier-recorded and model-knobs-recorded suites each resolve $helpers_rel from their own location and each end in the harness's finish"
problems=()

for stem in selection-order-recorded lane-rule-recorded unit-tier-recorded model-knobs-recorded; do
  probe_suite_resolves_helpers_from_itself "$stem"
done

report "$name"

probe_shared_helpers_plain_shell() {
  need_helpers_file "report, plain, records, bullet or says" || return

  local got expected
  local -a defines=(_harness_exit argcap_python3_stub bullet claude_stub expect_eq finish new_repo no ok
    on_exit plain records report says scratch_dir)
  got="$(
    unset -f "${defines[@]}"
    before="$(declare -F | sed 's/^declare -f //')"
    pass=3 fail=5
    out="$(
      PATH="/nonexistent-$$"
      source "$helpers_path" 2>&1
      printf 'status %s\n' "$?"
    )"
    # shellcheck source=/dev/null
    PATH="/nonexistent-$$" source "$helpers_path" > /dev/null 2>&1
    printf 'sourcing printed: [%s]\n' "$out"
    printf 'counters: %s passed, %s failed\n' "$pass" "$fail"
    printf 'new functions: [%s]\n' "$(declare -F | sed 's/^declare -f //' | grep -vxF "$before" | tr '\n' ' ')"
  )"
  expected="sourcing printed: [status 0]
counters: 3 passed, 5 failed
new functions: [${defines[*]} ]"
  same_as_copies "nothing but its definitions" "a plain-shell helper file with no dependency" "$got" "$expected"

  local stem suite_rel text line
  for stem in selection-order-recorded lane-rule-recorded unit-tier-recorded model-knobs-recorded; do
    suite_rel="skills/tdd/scripts/tests/$stem.test.sh"
    if ! text="$(cat "$ROOT/$suite_rel" 2>/dev/null)"; then
      problems+=("$suite_rel could not be read")
      continue
    fi
    [[ "$text" =~ (^|$'\n')source\ \"\$HERE/lib/harness.sh\"($'\n'|$) ]] ||
      problems+=("$suite_rel does not source the harness for its counters at top level")
    while IFS= read -r line; do
      [[ "$line" =~ ^(source|\.)[[:space:]] ]] || continue
      [[ "$line" =~ ^(source|\.)[[:space:]]+\"?\$\{?(HERE|ROOT)\}?/ ]] ||
        problems+=("$suite_rel sources a path outside its own \$HERE or \$ROOT: $line")
    done <<< "$text"
  done
}

name="$helpers_rel keeps the plain-shell idiom — sourcing it with no PATH prints nothing, leaves the suite's pass/fail counters alone and defines the harness's functions and its own four helpers — and the four suites each source lib/harness.sh and source nothing outside the repo"
problems=()

probe_shared_helpers_plain_shell

report "$name"

case_name_running() {
  local suite_rel="skills/tdd/scripts/tests/model-knobs-recorded.test.sh" line last=""
  case_name=""
  while IFS= read -r line; do
    [[ "$line" =~ ^name=\"(.*)\"$ ]] && last="${BASH_REMATCH[1]}"
    [[ "$line" =~ ^[[:space:]]*${1}([[:space:]]|$) ]] && case_name="$last"
  done < "$ROOT/$suite_rel"
  [[ -n "$case_name" ]] && return
  problems+=("$suite_rel has no case that runs $1")
  return 1
}

probe_finish_case_name() {
  local case_name
  case_name_running probe_suite_resolves_helpers_from_itself || return
  [[ "$case_name" =~ end[s]?\ in\ the\ harness\'s\ finish ]] ||
    problems+=("the case checking for a bare finish line is not named for each suite ending in the harness's finish: $case_name")
  [[ "$case_name" =~ own\ count\ line ]] &&
    problems+=("the case checking for a bare finish line still claims each suite prints its own count line: $case_name")
}

name="#595: the case that checks each suite ends in a bare finish line is named for ending in the harness's finish, not for printing its own count line"
problems=()

probe_finish_case_name

report "$name"

probe_harness_case_name() {
  local suite_rel="skills/tdd/scripts/tests/model-knobs-recorded.test.sh" line fn="" harness_fn="" case_name=""
  local -a names=()
  local needle="does not source"
  needle+=" the harness"
  while IFS= read -r line; do
    [[ "$line" =~ ^([a-z_]+)\(\)\ \{$ ]] && fn="${BASH_REMATCH[1]}"
    [[ "$line" == *"$needle"* && -n "$fn" ]] && harness_fn="$fn"
  done < "$ROOT/$suite_rel"
  if [[ -z "$harness_fn" ]]; then
    problems+=("$suite_rel has no probe that checks each suite sources lib/harness.sh")
    return
  fi
  while IFS= read -r line; do
    [[ "$line" =~ ^name=\"(.*)\"$ ]] && names+=("${BASH_REMATCH[1]}")
  done < "$ROOT/$suite_rel"
  case_name_running "$harness_fn" || return
  [[ "$case_name" =~ source[s]?\ (\$HERE/)?lib/harness\.sh ]] ||
    problems+=("the case checking each suite sources lib/harness.sh is not named for that: $case_name")
  local n
  for n in "${names[@]}"; do
    [[ "$n" == *"keep their own counters"* ]] &&
      problems+=("a case name still claims the four suites keep their own counters: $n")
  done
}

name="#595: the case that checks each suite sources lib/harness.sh is named for that, and no case name says the -recorded suites have counters of their own"
problems=()

probe_harness_case_name

report "$name"

probe_plain_shell_probe_unsourced() {
  local defined case_name
  defined="$(env -i bash --noprofile --norc -c '
    before="$(declare -F)"
    source "$1" > /dev/null 2>&1
    declare -F | grep -vxF "$before" | sed "s/^declare -f //"
  ' _ "$helpers_path")"
  if [[ -z "$defined" ]]; then
    problems+=("sourcing $helpers_rel in a fresh shell defined no functions")
    return
  fi
  local -a left=() names=()
  mapfile -t names <<< "$defined"
  mapfile -t left < <(
    problems=()
    unset -f "${names[@]}" && probe_shared_helpers_plain_shell
    [[ "${#problems[@]}" -eq 0 ]] || printf '%s\n' "${problems[@]}"
  )
  [[ "${#left[@]}" -eq 0 ]] ||
    problems+=("the plain-shell probe fails in a shell that has not sourced lib/harness.sh:" "${left[@]}")
  case_name_running probe_shared_helpers_plain_shell || return
  [[ "$case_name" == *"defines only the five helpers"* ]] &&
    problems+=("the plain-shell probe's case still claims $helpers_rel defines only the five helpers: $case_name")
}

name="#595: the plain-shell probe holds in a shell that has not sourced lib/harness.sh, and its case name no longer claims $helpers_rel defines only the five helpers"
problems=()

probe_plain_shell_probe_unsourced

report "$name"

name="#1037: bullet given '^[-*] run\\.sh' starts at '- run.sh', not at '- runXsh'"
fixture="$(scratch_dir)"
printf -- '- runXsh wrong\n- run.sh right\n- end\n' > "$fixture/SKILL.md"
expect_eq "$name" '- run.sh right ' "$(skill_path="$fixture/SKILL.md" bullet '^[-*] run\.sh')"

finish
