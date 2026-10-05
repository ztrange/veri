#!/usr/bin/env bash
# Unit tests for the suites under skills/tdd/scripts/tests/ — none of them may force a read or
# write failure through permission bits, which uid 0 ignores.
#
# Contract under test:
#   No suite under skills/tdd/scripts/tests/ takes read or write permission away from a path
#   with chmod, outside a comment. An offender is reported as `<suite>:<line>`, unless EXEMPT lists its
#   `<suite>:<line text>` with a reason; an entry carrying no reason fails the run.
#
# Run: skills/tdd/scripts/tests/no-permission-bits.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

SUBJECT='skills/tdd/scripts/tests'

CHMOD_WORD='(^|[^[:alnum:]_.-])chmod'
REVOKING_MODE='([0145][0-7][0-7]|[ugoa]*-[rwx]*[rw][rwx]*|[ugoa]*=[rx]*)'
CHMOD_FLAGS='([[:space:]]+-[RHLPfhv]+)*'
SHELL_CHMOD="$CHMOD_WORD$CHMOD_FLAGS[[:space:]]+$REVOKING_MODE([[:space:]]|$)"
PY_REVOKING_MODE='[[:space:]]*(0|0o([0-7]{1,2}|[0-7]?[0-5][0-7]{2}))[[:space:]]*\)'
PATH_CHMOD="\\.chmod\\($PY_REVOKING_MODE|(^|[^[:alnum:]_])os\\.chmod\\([^,]+,$PY_REVOKING_MODE"
PERMISSION_BIT_CHMOD="$SHELL_CHMOD|$PATH_CHMOD"
SYSTEM_PATH="(^|[[:space:](=,])[\"']?/(\\.tdd|root|proc)([/\"'[:space:]:)]|\$)"

declare -A EXEMPT=(
  ["skills/tdd/scripts/tests/no-permission-bits.test.sh:PLANT_SYSTEM_PATH='    assert (code, out, err.startswith(\"mkdir: /"".tdd: \")) == (1, \"\", True)'"]="the system-path plant this guard is proven against, text written into a scratch fixture, never run"
  ['skills/tdd/scripts/tests/no-permission-bits.test.sh:name="a planted pytest line relying on /'.tdd' being unwritable to force a mkdir failure turns the guard red, naming <suite>:<line> (#860)"']="a case name quoting the path it plants, never a path the suite touches"
)


source "$HERE/lib/harness.sh"
source "$HERE/lib/exemption-reasons.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

split_site() {
  local rest
  site_file="${1%%:*}"
  rest="${1#*:}"
  site_line="${rest%%:*}"
  site_text="${rest#*:}"
}

chmod_lines() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ "$site_text" =~ ^[[:space:]]*# ]] && continue
    printf '%s\n' "$hit"
  done < <(cd "$ROOT" && grep -rInE -- "$PERMISSION_BIT_CHMOD" "$SUBJECT")
  return 0
}

report_sites() {
  local why="$1" site
  while IFS= read -r site; do
    split_site "$site"
    [[ -n "${EXEMPT[$site_file:$site_text]:-}" ]] && continue
    problems+=("$site_file:$site_line $why, so the failure never happens where veri runs as root: $(flat "$site_text")")
  done
  return 0
}

probe_no_suite_revokes_permission_bits() {
  report_sites "forces a read or write failure through permission bits, which uid 0 ignores" < <(chmod_lines)
}

probe_no_suite_relies_on_a_system_path() {
  report_sites "relies on a system path being unwritable or unreadable, which uid 0 can write and read" < <(cd "$ROOT" && grep -rInE -- "$SYSTEM_PATH" "$SUBJECT")
}

probe_the_guard() {
  probe_every_exemption_carries_a_reason
  probe_no_suite_revokes_permission_bits
  probe_no_suite_relies_on_a_system_path
}

name="no suite under skills/tdd/scripts/tests/ forces a read or write failure through permission bits (#846)"
problems=()

probe_the_guard

report "$name"

PLANT_REL='skills/tdd/scripts/tests/planted.test.sh'

problem_naming() {
  local text="$1" problem
  for problem in ${problems+"${problems[@]}"}; do
    [[ "$problem" == *"$text"* ]] && { printf named; return; }
  done
  printf 'not named'
}

planted_line() {
  local line
  line="$(grep -nxF -- "$2" "$ROOT/$1")"
  printf '%s' "${line%%:*}"
}

plant_named() {
  problem_naming "$1:$(planted_line "$1" "$2") forces a read or write failure through permission bits"
}

plant() {
  local rel="$1"
  shift
  ROOT="$(scratch_dir)"
  mkdir -p "$ROOT/${rel%/*}"
  printf '%s\n' "$@" > "$ROOT/$rel"
  problems=()
}

plant_and_probe() {
  plant "$@"
  probe_no_suite_revokes_permission_bits
}

mode_plant() { printf 'chmod %s "$%s"' "$1" "$2"; }

mode_plants() {
  local var="$1" mode
  shift
  for mode; do
    printf '%s\n' "$(mode_plant "$mode" "$var")"
  done
}

modes_named() {
  local var="$1" mode named=""
  shift
  for mode; do
    named+="$mode $(plant_named "$PLANT_REL" "$(mode_plant "$mode" "$var")");"
  done
  printf '%s' "$named"
}

PLANT_CHMOD_000="chmod $(printf '%03d' 0) \"\$ledger\""

probe_a_planted_chmod_000() {
  local ROOT
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "$PLANT_CHMOD_000"
  planted_chmod_000_named="$(plant_named "$PLANT_REL" "$PLANT_CHMOD_000")"
  problems=()
}

name="a planted suite line starting with a chmod to mode zero, then a path, turns the guard red, naming <suite>:<line> (#846)"
planted_chmod_000_named=""

probe_a_planted_chmod_000

expect_eq "$name" "named" "$planted_chmod_000_named"

PLANT_REVOKING_MODES=(a-r u-w -w)

probe_planted_revoking_modes() {
  local ROOT plants
  mapfile -t plants < <(mode_plants ledger "${PLANT_REVOKING_MODES[@]}")
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "${plants[@]}"
  planted_revoking_modes_named="$(modes_named ledger "${PLANT_REVOKING_MODES[@]}")"
  problems=()
}

name="planted suite lines running a chmod to a-r, u-w and -w, then a path, each turn the guard red, naming its own <suite>:<line> (#846)"
planted_revoking_modes_named=""

probe_planted_revoking_modes

expect_eq "$name" "a-r named;u-w named;-w named;" "$planted_revoking_modes_named"

PLANT_SEPARATORS=(';' '&&' '||' '|' '(' '{' 'then' 'do')
PLANT_SEPARATOR_LINES=(
  "true; $PLANT_CHMOD_000"
  "true && $PLANT_CHMOD_000"
  "false || $PLANT_CHMOD_000"
  "true | $PLANT_CHMOD_000"
  "($PLANT_CHMOD_000)"
  "{ $PLANT_CHMOD_000; }"
  "if true; then $PLANT_CHMOD_000; fi"
  "for f in x; do $PLANT_CHMOD_000; done"
)

probe_planted_chmods_after_a_separator() {
  local ROOT i
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "${PLANT_SEPARATOR_LINES[@]}"
  planted_separators_named=""
  for i in "${!PLANT_SEPARATORS[@]}"; do
    planted_separators_named+="${PLANT_SEPARATORS[$i]} $(plant_named "$PLANT_REL" "${PLANT_SEPARATOR_LINES[$i]}");"
  done
  problems=()
}

name="a planted chmod to mode zero after ;, &&, ||, |, (, {, then or do on the same line turns the guard red, naming its <suite>:<line> (#846)"
planted_separators_named=""

probe_planted_chmods_after_a_separator

expect_eq "$name" "; named;&& named;|| named;| named;( named;{ named;then named;do named;" "$planted_separators_named"

PLANT_CHMOD_FLAGGED="chmod -R $(printf '%03d' 0) \"\$dir\""

probe_a_planted_chmod_with_a_flag() {
  local ROOT
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'dir="$(mktemp)"' "$PLANT_CHMOD_FLAGGED"
  planted_chmod_flagged_named="$(plant_named "$PLANT_REL" "$PLANT_CHMOD_FLAGGED")"
  problems=()
}

name="a planted chmod -R to mode zero, an option flag before its mode, turns the guard red, naming <suite>:<line> (#846)"
planted_chmod_flagged_named=""

probe_a_planted_chmod_with_a_flag

expect_eq "$name" "named" "$planted_chmod_flagged_named"

PLANT_PY_REL='skills/tdd/scripts/tests/py/test_planted.py'
PLANT_PY_CHMOD="    ledger.chmod(0o$(printf '%03d' 0))"

probe_a_planted_pytest_chmod_000() {
  local ROOT
  plant_and_probe "$PLANT_PY_REL" 'def test_unreadable_ledger(tmp_path):' '    ledger = tmp_path / "issue-9.md"' "$PLANT_PY_CHMOD"
  planted_pytest_chmod_named="$(plant_named "$PLANT_PY_REL" "$PLANT_PY_CHMOD")"
  problems=()
}

name="a planted pytest suite that chmods a path to mode 000 turns the guard red, naming <suite>:<line> (#846)"
planted_pytest_chmod_named=""

probe_a_planted_pytest_chmod_000

expect_eq "$name" "named" "$planted_pytest_chmod_named"

PLANT_PY_SUITE=('import os' 'def test_unreadable_ledger(tmp_path):' '    ledger = tmp_path / "issue-9.md"')

PLANT_PY_REVOKING_MODES=(0 0o000 0o400 0o444 0o200)

py_mode_plant() {
  case "$1" in
    path) printf '    ledger.chmod(%s)' "$2" ;;
    os) printf '    os.chmod(ledger, %s)' "$2" ;;
  esac
}

probe_planted_pytest_revoking_modes() {
  local ROOT form mode i labels=() plants=()
  for form in path os; do
    for mode in "${PLANT_PY_REVOKING_MODES[@]}"; do
      labels+=("$form $mode")
      plants+=("$(py_mode_plant "$form" "$mode")")
    done
  done
  plant_and_probe "$PLANT_PY_REL" "${PLANT_PY_SUITE[@]}" "${plants[@]}"
  planted_pytest_revoking_modes_named=""
  for i in "${!plants[@]}"; do
    planted_pytest_revoking_modes_named+="${labels[$i]} $(plant_named "$PLANT_PY_REL" "${plants[$i]}");"
  done
  problems=()
}

name="planted pytest lines taking the owner's read or write away by Path.chmod or os.chmod, mode 0, 0o000, 0o400, 0o444 or 0o200, each turn the guard red, naming its own <suite>:<line> (#897)"
planted_pytest_revoking_modes_named=""

probe_planted_pytest_revoking_modes

expect_eq "$name" "path 0 named;path 0o000 named;path 0o400 named;path 0o444 named;path 0o200 named;os 0 named;os 0o000 named;os 0o400 named;os 0o444 named;os 0o200 named;" "$planted_pytest_revoking_modes_named"

PLANT_PY_MODE_SHAPES=(
  "    ledger.chmod(0o$(printf '%o' 7))"
  "    ledger.chmod(0o$(printf '%o' 768))"
  "    os.chmod(ledger, 0o$(printf '%o' 292) )"
  "    xos.chmod(ledger, $(printf '%d' 0))"
)

probe_planted_pytest_mode_shapes() {
  local ROOT plant
  plant_and_probe "$PLANT_PY_REL" "${PLANT_PY_SUITE[@]}" "${PLANT_PY_MODE_SHAPES[@]}"
  planted_pytest_mode_shapes_named=""
  for plant in "${PLANT_PY_MODE_SHAPES[@]}"; do
    planted_pytest_mode_shapes_named+="${plant#    } $(plant_named "$PLANT_PY_REL" "$plant");"
  done
  problems=()
}

name="a planted pytest chmod to a one-digit octal mode, to an owner-revoking mode behind a special-bit digit, or with a space before its ), turns the guard red, and a call to a function merely ending in os.chmod does not (#897)"
planted_pytest_mode_shapes_named=""

probe_planted_pytest_mode_shapes

expect_eq "$name" "${PLANT_PY_MODE_SHAPES[0]#    } named;${PLANT_PY_MODE_SHAPES[1]#    } named;${PLANT_PY_MODE_SHAPES[2]#    } named;${PLANT_PY_MODE_SHAPES[3]#    } not named;" "$planted_pytest_mode_shapes_named"

PLANT_CHMOD_READ_ONLY_DIR="chmod $(printf '%o' 365) \"\$dir\""

probe_a_planted_read_only_dir() {
  local ROOT
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'dir="$PWD/ledgers"' 'mkdir "$dir"' "$PLANT_CHMOD_READ_ONLY_DIR" 'touch "$dir/ledger"'
  planted_read_only_dir_named="$(plant_named "$PLANT_REL" "$PLANT_CHMOD_READ_ONLY_DIR")"
  problems=()
}

name="a planted suite that makes a directory read-only, chmod to r-x for all, to force a write into it to fail turns the guard red, naming <suite>:<line> (#846)"
planted_read_only_dir_named=""

probe_a_planted_read_only_dir

expect_eq "$name" "named" "$planted_read_only_dir_named"

PLANT_READ_ONLY_DIR_MODES=(a-w 500 u=rx)

probe_planted_read_only_dir_modes() {
  local ROOT plants
  mapfile -t plants < <(mode_plants dir "${PLANT_READ_ONLY_DIR_MODES[@]}")
  plant_and_probe "$PLANT_REL" '#!/usr/bin/env bash' 'dir="$PWD/ledgers"' 'mkdir "$dir"' "${plants[@]}" 'touch "$dir/ledger"'
  planted_read_only_dir_modes_named="$(modes_named dir "${PLANT_READ_ONLY_DIR_MODES[@]}")"
  problems=()
}

name="planted suite lines making a directory read-only by chmod a-w, 500 and u=rx, not only 555, each turn the guard red, naming its own <suite>:<line> (#846)"
planted_read_only_dir_modes_named=""

probe_planted_read_only_dir_modes

expect_eq "$name" "a-w named;500 named;u=rx named;" "$planted_read_only_dir_modes_named"

PLANT_EXEMPTED="$PLANT_CHMOD_000  # exempted"
PLANT_UNREASONED="$PLANT_CHMOD_000  # unreasoned"

probe_an_exemption_table() {
  local ROOT unreasoned_key="$PLANT_REL:$PLANT_UNREASONED"
  local -A EXEMPT=(
    ["$PLANT_REL:$PLANT_EXEMPTED"]="a planted line whose chmod is the text under test, never run"
    ["$unreasoned_key"]=""
  )
  plant "$PLANT_REL" '#!/usr/bin/env bash' 'ledger="$(mktemp)"' "$PLANT_EXEMPTED" "$PLANT_UNREASONED"
  probe_the_guard
  exemption_table_named="exempted $(plant_named "$PLANT_REL" "$PLANT_EXEMPTED");unreasoned $(problem_naming "[$unreasoned_key] carries no reason");"
  problems=()
}

name="a line the exemption table lists with a reason is not reported, and an entry carrying no reason turns the guard red, naming the entry (#846)"
exemption_table_named=""

probe_an_exemption_table

expect_eq "$name" "exempted not named;unreasoned named;" "$exemption_table_named"

PLANT_SUITE=('#!/usr/bin/env bash' 'ledger="$(mktemp)"' 'printf x > "$ledger"')

guard_state() {
  if [[ "${#problems[@]}" -eq 0 ]]; then printf green; else printf red; fi
}

probe_a_plant_then_its_removal() {
  local ROOT
  plant "$PLANT_REL" "${PLANT_SUITE[@]}" "$PLANT_CHMOD_000"
  probe_the_guard
  plant_then_removal="planted $(guard_state) $(plant_named "$PLANT_REL" "$PLANT_CHMOD_000");"
  printf '%s\n' "${PLANT_SUITE[@]}" > "$ROOT/$PLANT_REL"
  problems=()
  probe_the_guard
  plant_then_removal+="removed $(guard_state);"
  problems=()
}

name="planting a permission-bit chmod into a suite turns the guard red naming the planted <suite>:<line>, and removing the plant turns it green again (#846)"
plant_then_removal=""

probe_a_plant_then_its_removal

expect_eq "$name" "planted red named;removed green;" "$plant_then_removal"

PLANT_SYSTEM_PATH='    assert (code, out, err.startswith("mkdir: /.tdd: ")) == (1, "", True)'

probe_a_planted_system_path() {
  local ROOT
  plant "$PLANT_PY_REL" 'def test_assign_fails_outside_a_repository(monkeypatch):' '    monkeypatch.chdir("/")' '    code, out, err = run(["assign", "beta", "7"])' "$PLANT_SYSTEM_PATH"
  probe_the_guard
  planted_system_path_named="$(problem_naming "$PLANT_PY_REL:$(planted_line "$PLANT_PY_REL" "$PLANT_SYSTEM_PATH") ")"
  problems=()
}

name="a planted pytest line relying on /.tdd being unwritable to force a mkdir failure turns the guard red, naming <suite>:<line> (#860)"
planted_system_path_named=""

probe_a_planted_system_path

expect_eq "$name" "named" "$planted_system_path_named"

finish
