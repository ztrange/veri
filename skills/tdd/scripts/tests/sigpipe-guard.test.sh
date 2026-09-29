#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a `pipefail` suite from reading its own writer's
# SIGPIPE as an answer — skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh. Like
# docs-read-guard.test.sh, hermetic-suites.test.sh and count-line-guard.test.sh this suite
# has no script as its subject: its subject is what another suite reports about the tree it
# is run in. Zero-dependency plain-shell asserts, same idiom as docs-read-guard.test.sh.
#
# Why this exists (issue #422): a suite that declares `set -uo pipefail` and ends a pipeline
# in `grep -q` asks its question of the wrong process. `grep -q` exits on its first match; if
# the writer still has bytes to push, its next write lands on a closed pipe, it dies of
# SIGPIPE (141), `pipefail` makes the whole pipeline 141, and the assertion built on that
# status is inverted. It is green on the development Mac (BSD grep buffers ~16 KB, so the
# writer needs one write and the race cannot happen) and red on CI (glibc gives the pipe a
# 4096-byte buffer), which is the worst shape this can take: the leaf and the blind verifier
# both run on the Mac, so a run reports green and the PR is red. It cost two consecutive
# runs — count-line-guard.test.sh (#418) and prompt-test-tiers.test.sh (#416). Repairing
# today's sites fixes today; the guard is what stops the next suite from being written that
# way.
#
# Contract under test (this case):
#   Over a tests directory holding one suite that declares `pipefail` and ends a pipeline in
#   `grep -q`, and one that ends the same pipeline in the same `grep -q` without declaring
#   `pipefail`, no-sigpipe-pipelines.test.sh fails, names the first as `<suite>:<line>` at
#   the offending line, and says nothing about the second.
#
# The second fixture is not extra generality: `pipefail` is half of the condition the
# criterion states. Without it the case is satisfied by a guard that names every pipeline
# into a grep in the tree — a guard the first author it blocked would delete, taking the
# real check with it. A suite whose pipeline's status is grep's own is doing nothing this
# issue forbids: the writer's SIGPIPE never reaches the exit status.
#
# Both suites are planted rather than asserted about where they stand: after this issue's
# other steps this repository has no live site left, so a probe over the real tree would
# pass on both sides of the fix and pin nothing. The plant goes in a scratch tree and the
# guard is copied into it, which is how docs-read-guard.test.sh puts a guard in front of a
# tree it was not written against; the guard therefore answers about the planted tree the
# same way it answers about this one, by being run inside it.
#
# No line of this file spells a pipeline ending in `grep -q` contiguously — the fixture's
# offending line is assembled from `GREP_Q` below and printf'd into the plant. That is not
# decoration: a line of THIS suite carrying the shape is exactly what the guard exists to
# catch, and a test that trips its own subject over the real tree would make the next step
# unachievable. It is also why this suite's own probes feed grep by herestring rather than
# through a pipe.
#
# Run: skills/tdd/scripts/tests/sigpipe-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

TESTS_DIR='skills/tdd/scripts/tests'

OFFENDER='probes-under-pipefail.test.sh'
INNOCENT='probes-without-pipefail.test.sh'

GREP_Q='grep -qF -- "$want"'
HEAD_R='head -n 1'

PIPEFAIL_LINE='set -uo pipefail'

MARK='the-probe'

pass=0 fail=0

report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

begin_case() {
  problems=()
  tree=""
  offender_path=""
  innocent_path=""
  guard_copy=""
  offender_line=""
  marked=""
  guard_out=""
  guard_code=0
}

drop_tree() {
  [[ -z "$tree" ]] || rm -rf "$tree"
}

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

probe_line() {
  printf 'printf "%%s\\n" "$%s" | %s  # %s\n' "$1" "$2" "$MARK"
}

write_plant() {
  local path="$1" set_line="$2" comment="$3" probe="$4"
  {
    echo '#!/usr/bin/env bash'
    echo "# Unit tests for a prompt template — $comment"
    echo "$set_line"
    echo 'body="$(printf "line %s\n" $(seq 1 400))"'
    echo 'want="line 3"'
    echo 'pass=0 fail=0'
    echo 'if '"$probe"
    echo 'then pass=1; else fail=1; fi'
    echo 'echo "----"'
    echo 'echo "$pass passed, $fail failed"'
    echo '[[ "$fail" -eq 0 ]]'
  } > "$path"
  chmod 755 "$path"
}

plant_offender() {
  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the shape the guard has to catch.' "$(probe_line body "$1")"
}

plant_innocent() {
  write_plant "$innocent_path" 'set -u' \
    'the same pipeline, with the status the readers own.' "$(probe_line body "$GREP_Q")"
}

open_tree() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to plant this case's suites in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  offender_path="$tree/$TESTS_DIR/$1"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"
}

install_guard() {
  cp "$GUARD_PATH" "$guard_copy"
  git init -q "$tree" >/dev/null 2>&1
  git -C "$tree" add -A >/dev/null 2>&1
}

seal_tree() {
  install_guard

  offender_line="$(grep -n "$MARK" "$offender_path" | cut -d: -f1)"
  return 0
}

plant() {
  open_tree "$OFFENDER" || return 1
  innocent_path="$tree/$TESTS_DIR/$INNOCENT"

  plant_offender "$GREP_Q"
  plant_innocent

  seal_tree
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing under $TESTS_DIR is checked for a pipefail suite that ends a pipeline in an early-exiting reader")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_plant_declares_pipefail() {
  grep -qF -- "$PIPEFAIL_LINE" "$offender_path" ||
    problems+=("the planted offender never declares '$PIPEFAIL_LINE', so its pipeline's status is the reader's own and the shape is not a bug at all")
}

probe_marked_line_is_findable() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return 1
  }
  marked="$(sed -n "${offender_line}p" "$offender_path")"
}

probe_plant_is_what_it_claims() {
  local reader="$1"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"|"*"$reader"* ]] ||
    problems+=("the planted offender's line $offender_line does not end a pipeline in $reader, so there is nothing there to catch: $(flat "$marked")")
  probe_plant_declares_pipefail
}

probe_innocent_is_what_it_claims() {
  grep -qF -- "$GREP_Q" "$innocent_path" ||
    problems+=("the planted innocent carries no such pipeline at all, so a guard that refuses every pipeline into a grep would still pass this case")
  ! grep -qF -- "$PIPEFAIL_LINE" "$innocent_path" ||
    problems+=("the planted innocent declares '$PIPEFAIL_LINE' too, so it is a second offender rather than the contrast this case needs")
}

run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

probe_guard_names_the_offender_with_its_line() {
  local suite="$1" reader="$2" named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a suite that declares '$PIPEFAIL_LINE' and ends a pipeline in $reader; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$suite" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $suite, whose line $offender_line ends a pipeline in $reader under '$PIPEFAIL_LINE'; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$suite:$offender_line" <<< "$named" ||
    problems+=("the guard named $suite but not as $suite:$offender_line, where the pipeline is; the lines naming it were: $(flat "$named")")
}

probe_guard_leaves_the_innocent_alone() {
  local named
  named="$(grep -F "$INNOCENT" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $INNOCENT, which ends the same pipeline in $GREP_Q without declaring '$PIPEFAIL_LINE': $(flat "$named")")
}

HEAD_OFFENDER='probes-head-under-pipefail.test.sh'

plant_lone_offender() {
  open_tree "$1" || return 1

  plant_offender "$2"

  seal_tree
}

name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in grep -q as <suite>:<line>, and says nothing about the same pipeline without pipefail"
begin_case

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims "$GREP_Q"
  probe_innocent_is_what_it_claims
  run_guard
  probe_guard_names_the_offender_with_its_line "$OFFENDER" "$GREP_Q"
  probe_guard_leaves_the_innocent_alone
fi
drop_tree

report "$name"

name="no-sigpipe-pipelines.test.sh names a suite that declares pipefail and ends a pipeline in head as <suite>:<line>"
begin_case

if probe_guard_is_there && plant_lone_offender "$HEAD_OFFENDER" "$HEAD_R"; then
  probe_plant_is_what_it_claims "$HEAD_R"
  run_guard
  probe_guard_names_the_offender_with_its_line "$HEAD_OFFENDER" "$HEAD_R"
fi
drop_tree

report "$name"

EXEMPT_OFFENDER='probes-exempted-under-pipefail.test.sh'

EXEMPT_DECL='declare -A EXEMPT=('

EXEMPT_REASON='the early exit is the point here: the probe asks whether the first match exists at all, and its writer is one line long'

exempt() {
  local key="$1" reason="$2" entry
  entry="  [$key]=\"$reason\""
  awk -v entry="$entry" -v decl="$EXEMPT_DECL" '
    { print }
    !added && index($0, decl) == 1 { print entry; added = 1 }
  ' "$GUARD_PATH" > "$tree/guard.next" && mv "$tree/guard.next" "$guard_copy"
  chmod 755 "$guard_copy"
}

probe_guard_carries_an_exemption_table() {
  grep -qF -- "$EXEMPT_DECL" "$GUARD_PATH" || {
    problems+=("$GUARD carries no exemption table ('$EXEMPT_DECL'), so a site where leaving before EOF is the point cannot be recorded with its reason and the only way past the guard is to stop declaring pipefail")
    return 1
  }
}

probe_entry_is_in_the_table() {
  grep -qF -- "[$1]" "$guard_copy" || {
    problems+=("the entry [$1] is not in the guard copy's exemption table, so what the run below reports is not about an exemption at all")
    return 1
  }
}

probe_guard_exempts_the_listed_site() {
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over a site listed in its exemption table as [$1] with a reason; it exited $guard_code and said: $(flat "$guard_out")")
  probe_guard_no_longer_names "$EXEMPT_OFFENDER:$offender_line" "$1"
}

probe_guard_no_longer_names() {
  local named
  named="$(grep -F "$1" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $1, which its exemption table lists as [$2] with a reason: $(flat "$named")")
}

probe_guard_refuses_a_reasonless_entry() {
  local key="$1" named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over the exemption entry [$key], which carries no reason; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$key" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names the reasonless exemption entry [$key]; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- 'reason' <<< "$named" ||
    problems+=("the guard named $key but never said its reason is what is missing, so the author is told a pipeline is there rather than that their exemption is not one: $(flat "$named")")
}

probe_exemption_both_ways() {
  local key="$1" exempts_probe="$2"
  exempt "$key" "$EXEMPT_REASON"
  if probe_entry_is_in_the_table "$key"; then
    run_guard
    "$exempts_probe" "$key"
  fi

  exempt "$key" ""
  if probe_entry_is_in_the_table "$key"; then
    run_guard
    probe_guard_refuses_a_reasonless_entry "$key"
  fi
}

name="no-sigpipe-pipelines.test.sh passes over a site its exemption table lists with a reason, and fails naming an entry whose reason is missing"
begin_case

if probe_guard_is_there && probe_guard_carries_an_exemption_table && plant_lone_offender "$EXEMPT_OFFENDER" "$GREP_Q"; then
  if probe_plant_is_what_it_claims "$GREP_Q"; then
    exempt_key="$EXEMPT_OFFENDER:$offender_line"

    probe_exemption_both_ways "$exempt_key" probe_guard_exempts_the_listed_site
  fi
fi
drop_tree

report "$name"

REMOVABLE_OFFENDER='probes-removable-under-pipefail.test.sh'

unplant() {
  rm -f "$offender_path"
}

probe_plant_is_gone() {
  [[ ! -e "$offender_path" ]] || {
    problems+=("the planted offender is still at $offender_path, so the run below reads the same tree as the one before it and the guard's second verdict says nothing about removal")
    return 1
  }
}

probe_guard_is_green_once_the_plant_is_removed() {
  local suite="$1" named
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the tree once $suite is removed, since the only offending site in it left with that file; it exited $guard_code and said: $(flat "$guard_out")")
  named="$(grep -F "$suite" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $suite after that file was removed from the tree, so its verdict is not a read of the tree in front of it: $(flat "$named")")
}

name="no-sigpipe-pipelines.test.sh is red over a planted offender, naming it, and green again once the plant is removed"
begin_case

if probe_guard_is_there && plant_lone_offender "$REMOVABLE_OFFENDER" "$GREP_Q"; then
  if probe_plant_is_what_it_claims "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$REMOVABLE_OFFENDER" "$GREP_Q"

    unplant
    if probe_plant_is_gone; then
      run_guard
      probe_guard_is_green_once_the_plant_is_removed "$REMOVABLE_OFFENDER"
    fi
  fi
fi
drop_tree

report "$name"

WRAPPED_OFFENDER='probes-wrapped-under-pipefail.test.sh'

probe_line_wrapped() {
  printf 'printf "%%s\\n" "$%s" |\n%s  # %s\n' "$1" "$2" "$MARK"
}

plant_wrapped_offender() {
  open_tree "$1" || return 1

  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is the same shape, wrapped across two lines.' \
    "$(probe_line_wrapped body "$2")"

  seal_tree
}

probe_line_above_ends_in_the_pipe() {
  local before
  before="$(sed -n "$((offender_line - 1))p" "$offender_path")"
  [[ "$before" =~ \|[[:space:]]*$ ]] ||
    problems+=("the line above the planted offender's marked line does not end in the pipe that feeds it, so the two lines are not one pipeline at all: $(flat "$before")")
}

probe_wrapped_plant_is_what_it_claims() {
  local reader="$1"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"$reader"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not open with $reader, so there is no wrapped reader there to catch: $(flat "$marked")")
  [[ "$marked" != *"|"* ]] ||
    problems+=("the planted offender's marked line $offender_line carries a pipe of its own, so it is the contiguous shape case 1 already pins rather than the wrapped one: $(flat "$marked")")
  probe_line_above_ends_in_the_pipe
  probe_plant_declares_pipefail
}

name="no-sigpipe-pipelines.test.sh names a suite whose pipeline is split across two lines, the pipe ending one and the early-exiting reader opening the next, as <suite>:<line>"
begin_case

if probe_guard_is_there && plant_wrapped_offender "$WRAPPED_OFFENDER" "$GREP_Q"; then
  if probe_wrapped_plant_is_what_it_claims "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$WRAPPED_OFFENDER" "$GREP_Q"
  fi
fi
drop_tree

report "$name"

BOTH_READINGS_OFFENDER='probes-both-readings-under-pipefail.test.sh'

probe_line_both_readings() {
  printf 'printf "%%s\\n" "$%s" |\n  %s | %s  # %s\n' "$1" "$2" "$3" "$MARK"
}

plant_both_readings_offender() {
  open_tree "$1" || return 1

  write_plant "$offender_path" "$PIPEFAIL_LINE" \
    'the pipeline below is wrapped and goes on piping on the line below.' \
    "$(probe_line_both_readings body "$2" "$3")"

  seal_tree
}

probe_both_readings_plant_is_what_it_claims() {
  local first="$1" second="$2"
  probe_marked_line_is_findable || return 1
  [[ "$marked" == *"$first"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not open with $first, so the wrapped reading never reaches it and one report is all there was ever going to be: $(flat "$marked")")
  [[ "$marked" == *"|"*"$second"* ]] ||
    problems+=("the planted offender's marked line $offender_line does not pipe into $second further along itself, so the contiguous reading never reaches it and one report is all there was ever going to be: $(flat "$marked")")
  probe_line_above_ends_in_the_pipe
  probe_plant_declares_pipefail
}

probe_guard_names_the_site_once() {
  local suite="$1" named count
  named="$(grep -F "$suite:$offender_line" <<< "$guard_out")"
  count="$(grep -cF "$suite:$offender_line" <<< "$guard_out")"
  [[ "$count" -eq 1 ]] ||
    problems+=("want the guard to name $suite:$offender_line exactly once, since one line is one site to repair however many readings of the file reached it; it named it $count times: $(flat "$named")")
}

name="no-sigpipe-pipelines.test.sh names a line both of its readings reach — opened by an early-exiting reader fed from the line above, and piping into another — exactly once"
begin_case

if probe_guard_is_there && plant_both_readings_offender "$BOTH_READINGS_OFFENDER" "$HEAD_R" "$GREP_Q"; then
  if probe_both_readings_plant_is_what_it_claims "$HEAD_R" "$GREP_Q"; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$BOTH_READINGS_OFFENDER" "$GREP_Q"
    probe_guard_names_the_site_once "$BOTH_READINGS_OFFENDER"
  fi
fi
drop_tree

report "$name"

ROSTER_CASE='`make test` runs'

ROSTER_QUESTION='make -n test'

ABSENT_OFFENDER='no-suite-is-planted.test.sh'

plant_bare_tree() {
  open_tree "$ABSENT_OFFENDER" || return 1

  install_guard
}

probe_tree_has_no_makefile() {
  [[ ! -e "$tree/Makefile" ]] || {
    problems+=("the scratch tree carries a Makefile at $tree/Makefile, so \`make -n test\` there may name suites and this case is not about an empty roster at all")
    return 1
  }
}

probe_guard_reports_the_empty_roster_without_failing() {
  local failures named said
  failures="$(grep -F 'FAIL - ' <<< "$guard_out")"
  named="$(grep -F "$ROSTER_CASE" <<< "$failures")"
  [[ -z "$named" ]] ||
    problems+=("the guard failed its roster case over a tree whose \`$ROSTER_QUESTION\` names no suite, so every scratch plant is red for the tree's missing Makefile rather than for what was planted in it: $(flat "$named")")
  said="$(grep -F "$ROSTER_QUESTION" <<< "$guard_out")"
  [[ -n "$said" ]] ||
    problems+=("no line of the guard's output names \`$ROSTER_QUESTION\` at all, so the empty roster went unsaid and a reader cannot tell a roster that held nothing from one that was never read; it said: $(flat "$guard_out")")
}

name="no-sigpipe-pipelines.test.sh says what its roster read found when \`make -n test\` names no suite, instead of failing the run"
begin_case

if probe_guard_is_there && plant_bare_tree; then
  if probe_tree_has_no_makefile; then
    run_guard
    probe_guard_reports_the_empty_roster_without_failing
  fi
fi
drop_tree

report "$name"

MAKEFILE_NAME='Makefile'

MAKE_GREP_Q='grep -qF -- ok'

plant_makefile_offender() {
  open_tree "$ABSENT_OFFENDER" || return 1
  offender_path="$tree/$MAKEFILE_NAME"
  {
    echo '.PHONY: check'
    echo 'check:'
    printf '\t@printf "%%s\\n" ok | %s  # %s\n' "$MAKE_GREP_Q" "$MARK"
  } > "$offender_path"

  seal_tree
}

probe_makefile_plant_is_what_it_claims() {
  probe_marked_line_is_findable || return 1
  [[ "$marked" == $'\t'* ]] ||
    problems+=("the planted Makefile's line $offender_line does not open with a tab, so make reads it as no recipe at all: $(flat "$marked")")
  [[ "$marked" == *"|"*"$MAKE_GREP_Q"* ]] ||
    problems+=("the planted Makefile's line $offender_line does not end a pipeline in $MAKE_GREP_Q, so there is nothing there to catch: $(flat "$marked")")
  ! grep -F pipefail "$offender_path" > /dev/null ||
    problems+=("the planted Makefile mentions pipefail, so a guard that names it could still be one that requires the declaration")
}

probe_guard_names_the_recipe_with_its_line() {
  local named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a Makefile whose recipe line $offender_line ends a pipeline in $MAKE_GREP_Q; it exited 0 and said: $(flat "$guard_out")")
  named="$(grep -F "$MAKEFILE_NAME" <<< "$guard_out")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $MAKEFILE_NAME, whose recipe line $offender_line ends a pipeline in $MAKE_GREP_Q; it said: $(flat "$guard_out")")
    return
  }
  grep -F -- "$MAKEFILE_NAME:$offender_line" <<< "$named" > /dev/null ||
    problems+=("the guard named $MAKEFILE_NAME but not as $MAKEFILE_NAME:$offender_line, where the recipe's pipeline is; the lines naming it were: $(flat "$named")")
}

name="no-sigpipe-pipelines.test.sh names a Makefile recipe line that ends a pipeline in grep -q as Makefile:<line>, without asking for pipefail (#524)"
begin_case

if probe_guard_is_there && plant_makefile_offender; then
  if probe_makefile_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_recipe_with_its_line
  fi
fi
drop_tree

report "$name"

probe_guard_exempts_the_listed_recipe() {
  probe_guard_no_longer_names "$MAKEFILE_NAME:$offender_line" "$1"
}

name="no-sigpipe-pipelines.test.sh stops naming a Makefile recipe site its exemption table lists as Makefile:<line> with a reason, and fails naming that entry when its reason is missing (#524)"
begin_case

if probe_guard_is_there && probe_guard_carries_an_exemption_table && plant_makefile_offender; then
  if probe_makefile_plant_is_what_it_claims; then
    exempt_key="$MAKEFILE_NAME:$offender_line"

    probe_exemption_both_ways "$exempt_key" probe_guard_exempts_the_listed_recipe
  fi
fi
drop_tree

report "$name"

LOOP_OFFENDER='probes-loop-break-under-pipefail.test.sh'

LOOP_OPEN='while IFS= read -r line; do'
LOOP_BREAK='[[ "$line" == "$want" ]] && break'
LOOP_CLOSE='done'
PROC_SUB_FEED='< <(printf "%s\n" "$body")'

LOOP_READER='a while loop that can break'

probe_lines_loop() {
  printf '%s\n' "$LOOP_OPEN"
  printf '  %s\n' "$@"
  printf '%s %s  # %s\n' "$LOOP_CLOSE" "$PROC_SUB_FEED" "$MARK"
}

plant_loop_offender() {
  plant_loop_suite probe_lines_loop "$@"
}

plant_loop_suite() {
  local emitter="$1"
  open_tree "$2" || return 1
  shift 2

  {
    echo '#!/usr/bin/env bash'
    echo '# Unit tests for a prompt template — the loop below reads a process substitution.'
    echo "$PIPEFAIL_LINE"
    echo 'body="$(printf "line %s\n" $(seq 1 400))"'
    echo 'want="line 3"'
    echo 'pass=0 fail=0 line=""'
    "$emitter" "$@"
    echo 'if [[ "$line" == "$want" ]]'
    echo 'then pass=1; else fail=1; fi'
    echo 'echo "----"'
    echo 'echo "$pass passed, $fail failed"'
    echo '[[ "$fail" -eq 0 ]]'
  } > "$offender_path"
  chmod 755 "$offender_path"

  seal_tree
}

probe_marked_line_closes_a_loop() {
  probe_marked_line_is_findable || return 1
  [[ "$marked" == "$LOOP_CLOSE $PROC_SUB_FEED"* ]] ||
    problems+=("the planted loop's marked line $offender_line does not close a loop on a process substitution: $(flat "$marked")")
  return 0
}

probe_loop_plant_is_what_it_claims() {
  local above
  probe_marked_line_closes_a_loop || return 1
  above="$(sed -n "$((offender_line - 1))p" "$offender_path")"
  [[ "$above" == *"$LOOP_BREAK"* ]] ||
    problems+=("the line above the planted offender's marked line carries no break, so the loop never leaves early: $(flat "$above")")
  probe_plant_declares_pipefail
}

probe_guard_exempts_the_listed_loop() {
  probe_guard_no_longer_names "$1" "$1"
}

name="no-sigpipe-pipelines.test.sh names a while loop that can break while fed by a process substitution, under pipefail, as <suite>:<line>, unless its exemption table lists that site with a reason (#526)"
begin_case

if probe_guard_is_there && probe_guard_carries_an_exemption_table &&
  plant_loop_offender "$LOOP_OFFENDER" "$LOOP_BREAK"; then
  if probe_loop_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$LOOP_OFFENDER" "$LOOP_READER"

    exempt_key="$LOOP_OFFENDER:$offender_line"
    probe_exemption_both_ways "$exempt_key" probe_guard_exempts_the_listed_loop
  fi
fi
drop_tree

report "$name"

NESTED_LOOP_OFFENDER='probes-loop-break-after-nested-loops.test.sh'
COMMENTED_BREAK_LOOP='probes-loop-commented-break.test.sh'

NESTED_FOR='for word in $line; do :; done'
NESTED_UNTIL='until true; do :; done'

COMMENTED_BREAK="# $LOOP_BREAK"

probe_nested_plant_is_what_it_claims() {
  local body
  probe_loop_plant_is_what_it_claims || return 1
  body="$(sed -n "$((offender_line - 3)),$((offender_line - 2))p" "$offender_path")"
  [[ "$body" == *"$NESTED_FOR"*"$NESTED_UNTIL"* ]] ||
    problems+=("the two lines above the planted loop's break are not a nested for loop and a nested until loop: $(flat "$body")")
}

probe_commented_plant_is_what_it_claims() {
  local body
  probe_marked_line_closes_a_loop || return 1
  body="$(sed -n "$((offender_line - 1))p" "$offender_path")"
  [[ "$body" == "  $COMMENTED_BREAK" ]] ||
    problems+=("the planted loop's body is not the one commented break: $(flat "$body")")
  probe_plant_declares_pipefail
}

probe_guard_says_nothing_of() {
  local named
  named="$(grep -F "$1" <<< "$guard_out")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $1, whose loop's only break is a comment and so never leaves the loop: $(flat "$named")")
}

name="no-sigpipe-pipelines.test.sh names a while loop that can break while fed by a process substitution as <suite>:<line> when a nested for and until loop close ahead of the break (#526)"
begin_case

if probe_guard_is_there &&
  plant_loop_offender "$NESTED_LOOP_OFFENDER" "$NESTED_FOR" "$NESTED_UNTIL" "$LOOP_BREAK"; then
  if probe_nested_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$NESTED_LOOP_OFFENDER" "$LOOP_READER"
  fi
fi
drop_tree

report "$name"

name="no-sigpipe-pipelines.test.sh says nothing about a while loop fed by a process substitution whose only break is a comment (#526)"
begin_case

if probe_guard_is_there &&
  plant_loop_offender "$COMMENTED_BREAK_LOOP" "$COMMENTED_BREAK"; then
  if probe_commented_plant_is_what_it_claims; then
    run_guard
    probe_guard_says_nothing_of "$COMMENTED_BREAK_LOOP"
  fi
fi
drop_tree

report "$name"

PIPED_LOOP_OFFENDER='probes-piped-loop-break-under-pipefail.test.sh'

PIPE_FEED='printf "%s\n" "$body" |'

probe_lines_piped_loop() {
  printf '%s %s  # %s\n' "$PIPE_FEED" "$LOOP_OPEN" "$MARK"
  printf '  %s\n' "$@"
  printf '%s\n' "$LOOP_CLOSE"
}

plant_piped_loop_offender() {
  plant_loop_suite probe_lines_piped_loop "$@"
}

probe_piped_loop_plant_is_what_it_claims() {
  local below
  probe_marked_line_is_findable || return 1
  [[ "$marked" == "$PIPE_FEED $LOOP_OPEN"* ]] ||
    problems+=("the planted loop's marked line $offender_line does not feed a while loop through a pipe: $(flat "$marked")")
  below="$(sed -n "$((offender_line + 1))p" "$offender_path")"
  [[ "$below" == *"$LOOP_BREAK"* ]] ||
    problems+=("the line below the planted offender's marked line carries no break, so the loop never leaves early: $(flat "$below")")
  probe_plant_declares_pipefail
}

name="no-sigpipe-pipelines.test.sh names a while loop that can break while fed by a pipe as <suite>:<line>, unless its exemption table lists that site with a reason (#526)"
begin_case

if probe_guard_is_there && probe_guard_carries_an_exemption_table &&
  plant_piped_loop_offender "$PIPED_LOOP_OFFENDER" "$LOOP_BREAK"; then
  if probe_piped_loop_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_offender_with_its_line "$PIPED_LOOP_OFFENDER" "$LOOP_READER"

    exempt_key="$PIPED_LOOP_OFFENDER:$offender_line"
    probe_exemption_both_ways "$exempt_key" probe_guard_exempts_the_listed_loop
  fi
fi
drop_tree

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
