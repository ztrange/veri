#!/usr/bin/env bash
# Unit tests for the two root documents' record of the per-role model tunables — which
# variable a leaf reads, and why the developer's and the verifier's are two knobs and not
# one. Like lane-rule-recorded.test.sh and skill-timeout.test.sh this suite's subject is a
# document rather than a script: what an operator is told before any leaf launches.
# Zero-dependency plain-shell asserts, same idiom as lane-rule-recorded.test.sh.
#
# Why this exists (issue #171): `leaf-model.sh` resolves the model and `supervise.sh` puts
# it on the leaf's command line, so a run can already be moved onto a cheaper model — but a
# tunable nobody is told about is one nobody sets. The two places an operator looks are
# SKILL.md's `supervise.sh` bullet, which is where every other leaf tunable is listed
# (`VERI_HEARTBEAT`, `VERI_TIMEOUT`, `VERI_STUCK_RETRIES`), and CLAUDE.md, which is the
# first thing an agent reads. The `VERI_MODEL_VERIFIER` experiment that motivates the whole
# issue cannot be run by someone who cannot find the variable's name.
#
# And the *why* is not decoration. The two roles fail differently: a cheaper verifier shows
# up as a changed verdict distribution, a cheaper developer as more revise cycles and worse
# code. One knob over both would make "cheaper developer" and "weaker verifier" the same
# decision — the identical trap CLAUDE.md already records for the three budgets, whose
# entry says why they are never merged. A document that named the three variables without
# that sentence would leave the next reader free to collapse them.
#
# Contract under test:
#   SKILL.md's `supervise.sh` bullet lists all three tunables — `VERI_MODEL`,
#   `VERI_MODEL_DEVELOPER`, `VERI_MODEL_VERIFIER` — beside the tunables it already lists;
#   and CLAUDE.md names all three and says why the developer's and the verifier's are
#   separate knobs, in the terms the failure actually takes: the verdict distribution on
#   one side, revise cycles on the other.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings: what a document has to record is the claim, and how it is phrased belongs to
# whoever writes it — the protocol lane-rule-recorded.test.sh and skill-suite-runs.test.sh
# both use on these documents.
#
# Not asked here: that CLAUDE.md's script and suite counts moved when this suite landed.
# claude-md-counts.test.sh is the case that holds every count in that document to the files
# on disk, and this file arriving in the tree is what makes it answer.
#
# Run: skills/tdd/scripts/tests/model-knobs-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

source "$HERE/record-helpers.sh"

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

need_claude_md_records() {
  passage_from="$claude_md"
  passage_text="$(records < "$claude_path")"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md could not be read, so nothing could be asked of what it records")
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
    pass=0 fail=0
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
    pass=0 fail=0
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
  [[ "$text" =~ (^|$'\n')echo[[:space:]]+\"\$pass\ passed,\ \$fail\ failed\" ]] ||
    problems+=("$suite_rel prints no \$pass passed, \$fail failed count line of its own")
}

name="the selection-order-recorded, lane-rule-recorded, unit-tier-recorded and model-knobs-recorded suites each resolve $helpers_rel from their own location and each print their own count line"
problems=()

for stem in selection-order-recorded lane-rule-recorded unit-tier-recorded model-knobs-recorded; do
  probe_suite_resolves_helpers_from_itself "$stem"
done

report "$name"

probe_shared_helpers_plain_shell() {
  need_helpers_file "report, plain, records, bullet or says" || return

  local got expected
  got="$(
    unset -f report plain records bullet says
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
new functions: [bullet plain records report says ]"
  same_as_copies "nothing but its definitions" "a plain-shell helper file with no dependency" "$got" "$expected"

  local stem suite_rel text line
  for stem in selection-order-recorded lane-rule-recorded unit-tier-recorded model-knobs-recorded; do
    suite_rel="skills/tdd/scripts/tests/$stem.test.sh"
    if ! text="$(cat "$ROOT/$suite_rel" 2>/dev/null)"; then
      problems+=("$suite_rel could not be read")
      continue
    fi
    [[ "$text" =~ (^|$'\n')pass=0\ fail=0($'\n'|$) ]] ||
      problems+=("$suite_rel does not set its own pass=0 fail=0 at top level")
    while IFS= read -r line; do
      [[ "$line" =~ ^(source|\.)[[:space:]] ]] || continue
      [[ "$line" =~ ^(source|\.)[[:space:]]+\"?\$\{?(HERE|ROOT)\}?/ ]] ||
        problems+=("$suite_rel sources a path outside its own \$HERE or \$ROOT: $line")
    done <<< "$text"
  done
}

name="$helpers_rel keeps the plain-shell idiom — sourcing it with no PATH prints nothing, leaves the suite's pass/fail counters alone and defines only the five helpers — and the four suites keep their own counters and source nothing outside the repo"
problems=()

probe_shared_helpers_plain_shell

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
