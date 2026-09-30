#!/usr/bin/env bash
# Unit tests for the guard suite that keeps a file under skills/ from killing a background
# process by job spec — skills/tdd/scripts/tests/no-job-spec-kills.test.sh. Like
# sigpipe-guard.test.sh and docs-read-guard.test.sh this suite has no script as its subject:
# its subject is what another suite reports about the tree it is run in. Zero-dependency
# plain-shell asserts, same idiom as sigpipe-guard.test.sh.
#
# Why this exists (issue #424): a job spec names a job in one shell's own job table, and
# that table dies with the shell. A background process killed that way survives whenever the
# shell that started it went first — the child is reparented to PID 1 and nothing is left
# that knows its identity. On 2026-09-22 that left ten orphaned busy-loops on this machine,
# ~988% of CPU for twelve hours, computing nothing and quietly distorting every timing this
# repository measures. The two halves already landed — lib/background.sh kills the pid it
# recorded, and a shell that exits with a survivor says so — repair today's sites; the guard
# is what stops the next one being written, and this suite is what says the guard works.
#
# Contract under test (this step):
#   Over a tree holding one file under skills/ that kills a background process by job spec
#   and one that kills the pid it recorded, no-job-spec-kills.test.sh fails, names the first
#   as `<file>:<line>` at the offending line, and says nothing about the second — and its
#   exemption table honours an entry that carries a reason while failing, naming the entry,
#   over one whose reason is missing.
#
# The second file is not extra generality: killing a background process is not the offence,
# killing it by a name that dies with the shell is. A guard that named every `kill` in the
# tree would be deleted by the first author it blocked, taking the real check with it — and
# lib/background.sh, the fix this issue already shipped, would be its first victim.
#
# Both files are planted rather than asserted about where they stand: after this issue's
# earlier steps the repository has no live site left, so a probe over the real tree would
# pass on both sides of the fix and pin nothing. The plant goes in a scratch tree and the
# guard is copied into it, which is how sigpipe-guard.test.sh puts a guard in front of a
# tree it was not written against; the guard answers about the planted tree the way it
# answers about this one, by being run inside it.
#
# No line of this file spells `kill` followed by a job spec contiguously — the fixture's
# offending line is assembled from KILL and JOB_SPEC below and printf'd into the plant, and
# the prose says "a job spec" where it would otherwise write one out. That is not decoration:
# this suite is itself a file under skills/, so a line here carrying the shape is exactly
# what the guard exists to catch, and a test that trips its own subject would make the next
# step unachievable.
#
# Run: skills/tdd/scripts/tests/job-spec-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/no-job-spec-kills.test.sh'
GUARD_PATH="$ROOT/$GUARD"
GUARD_NAME="$(basename "$GUARD")"

SCRIPTS_DIR='skills/tdd/scripts'
TESTS_DIR='skills/tdd/scripts/tests'

OFFENDER_REL="$SCRIPTS_DIR/probe-load.sh"
INNOCENT_REL="$SCRIPTS_DIR/probe-load-by-pid.sh"
OFFENDER_NAME="$(basename "$OFFENDER_REL")"
INNOCENT_NAME="$(basename "$INNOCENT_REL")"

KILL='kill'
JOB_SPEC='%1'
RECORDED_PID='"$victim"'

MARK='job-spec-probe'
SAFE_MARK='recorded-pid-probe'

EXEMPT_DECL='declare -A EXEMPT=('

EXEMPT_REASON='the job spec is the point here: the line is quoted prose inside a heredoc, not a kill this shell ever runs'


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

write_plant() {
  local path="$1" arg="$2" mark="$3" comment="$4"
  {
    echo '#!/usr/bin/env bash'
    echo "# A load generator for a measurement — $comment"
    echo 'set -uo pipefail'
    echo 'sleep 30 &'
    echo 'victim=$!'
    printf '%s %s 2>/dev/null  # %s\n' "$KILL" "$arg" "$mark"
  } > "$path"
  chmod 755 "$path"
}

plant() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to plant this case's files in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"

  offender_path="$tree/$OFFENDER_REL"
  innocent_path="$tree/$INNOCENT_REL"
  guard_copy="$tree/$TESTS_DIR/$GUARD_NAME"

  write_plant "$offender_path" "$JOB_SPEC" "$MARK" \
    'the kill below is the shape the guard has to catch.'
  write_plant "$innocent_path" "$RECORDED_PID" "$SAFE_MARK" \
    'the same process, killed by the pid it recorded.'

  install_guard

  offender_line="$(grep -n "$MARK" "$offender_path" | cut -d: -f1)"
  return 0
}

stage_guard() {
  chmod 755 "$guard_copy"
  git -C "$tree" add -A >/dev/null 2>&1
}

install_guard() {
  cp "$GUARD_PATH" "$guard_copy"
  mkdir -p "${guard_copy%/*}/lib" && cp "$HERE/lib/harness.sh" "${guard_copy%/*}/lib/"
  new_repo "$tree" >/dev/null 2>&1
  stage_guard
}

drop_tree() {
  [[ -z "${tree:-}" ]] || rm -rf "$tree"
}

exempt() {
  local key="$1" reason="$2" entry
  entry="  [$key]=\"$reason\""
  awk -v entry="$entry" -v decl="$EXEMPT_DECL" '
    { print }
    !added && index($0, decl) == 1 { print entry; added = 1 }
  ' "$GUARD_PATH" > "$tree/guard.next" && mv "$tree/guard.next" "$guard_copy"
  stage_guard
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so nothing under skills/ is checked for a background process killed by a job spec")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_guard_carries_an_exemption_table() {
  grep -qF -- "$EXEMPT_DECL" "$GUARD_PATH" || {
    problems+=("$GUARD carries no exemption table ('$EXEMPT_DECL'), so a site where a job spec is the right name cannot be recorded with its reason and the only way past the guard is to delete it")
    return 1
  }
}

probe_plant_is_what_it_claims() {
  [[ "$offender_line" =~ ^[0-9]+$ ]] || {
    problems+=("the planted offender has no single marked line to name (found '$offender_line'), so the criterion cannot be asked")
    return 1
  }
  marked="$(sed -n "${offender_line}p" "$offender_path")"
  [[ "$marked" == *"$KILL $JOB_SPEC"* ]] ||
    problems+=("the planted offender's line $offender_line does not kill by a job spec at all, so there is nothing there to catch: $(flat "$marked")")
  grep -qF -- "$KILL $RECORDED_PID" "$innocent_path" ||
    problems+=("the planted innocent kills nothing by its recorded pid, so a guard that refused every kill in the tree would still pass this case")
}

run_guard() {
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

naming() { grep -F "$1" <<< "$guard_out"; }

probe_guard_names_the_offender_with_its_line() {
  local named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over a file under skills/ that kills a background process by a job spec; it exited 0 and said: $(flat "$guard_out")")
  named="$(naming "$OFFENDER_NAME")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names $OFFENDER_REL, whose line $offender_line kills a background process by a job spec; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- "$OFFENDER_REL:$offender_line" <<< "$named" ||
    problems+=("the guard named $OFFENDER_NAME but not as $OFFENDER_REL:$offender_line, where the kill is; the lines naming it were: $(flat "$named")")
}

probe_guard_leaves_the_innocent_alone() {
  local named
  named="$(naming "$INNOCENT_NAME")"
  [[ -z "$named" ]] ||
    problems+=("the guard named $INNOCENT_REL, which kills the same process by the pid it recorded: $(flat "$named")")
}

probe_entry_is_in_the_table() {
  grep -qF -- "[$1]" "$guard_copy" || {
    problems+=("the entry [$1] is not in the guard copy's exemption table, so what the run below reports is not about an exemption at all")
    return 1
  }
}

probe_guard_exempts_the_listed_site() {
  local named
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over a site listed in its exemption table as [$1] with a reason; it exited $guard_code and said: $(flat "$guard_out")")
  named="$(naming "$OFFENDER_REL:$offender_line")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $OFFENDER_REL:$offender_line, which its exemption table lists as [$1] with a reason: $(flat "$named")")
}

probe_guard_refuses_a_reasonless_entry() {
  local key="$1" named
  [[ "$guard_code" != 0 ]] ||
    problems+=("want the guard to fail over the exemption entry [$key], which carries no reason; it exited 0 and said: $(flat "$guard_out")")
  named="$(naming "$key")"
  [[ -n "$named" ]] || {
    problems+=("no line of the guard's output names the reasonless exemption entry [$key]; it said: $(flat "$guard_out")")
    return
  }
  grep -qF -- 'reason' <<< "$named" ||
    problems+=("the guard named $key but never said its reason is what is missing, so the author is told a kill is there rather than that their exemption is not one: $(flat "$named")")
}

name="no-job-spec-kills.test.sh names a file under skills/ that kills a background process by a job spec as <file>:<line>, leaves a kill by recorded pid alone, and honours an exemption entry only when it carries a reason"
problems=()

if probe_guard_is_there && probe_guard_carries_an_exemption_table && plant; then
  if probe_plant_is_what_it_claims; then
    run_guard
    probe_guard_names_the_offender_with_its_line
    probe_guard_leaves_the_innocent_alone

    exempt_key="$OFFENDER_REL:$offender_line"

    exempt "$exempt_key" "$EXEMPT_REASON"
    if probe_entry_is_in_the_table "$exempt_key"; then
      run_guard
      probe_guard_exempts_the_listed_site "$exempt_key"
    fi

    exempt "$exempt_key" ""
    if probe_entry_is_in_the_table "$exempt_key"; then
      run_guard
      probe_guard_refuses_a_reasonless_entry "$exempt_key"
    fi
  fi
fi
drop_tree

report "$name"

remove_plant() {
  rm -f "$offender_path"
  git -C "$tree" add -A >/dev/null 2>&1
}

probe_plant_is_red_first() {
  [[ "$guard_code" != 0 ]] || {
    problems+=("want the guard to fail over the tree as planted, whose $OFFENDER_REL ends a background process by a job spec at line $offender_line; it exited 0 and said: $(flat "$guard_out")")
    return 1
  }
  [[ -n "$(naming "$OFFENDER_REL:$offender_line")" ]] || {
    problems+=("the guard failed over the tree as planted but named no site at $OFFENDER_REL:$offender_line, so its red is not this plant's and the green below would say nothing; it said: $(flat "$guard_out")")
    return 1
  }
}

probe_plant_is_gone() {
  [[ ! -e "$offender_path" ]] || {
    problems+=("$OFFENDER_REL is still in the planted tree, so the run below is not the one this case asks about")
    return 1
  }
}

probe_guard_is_green_once_the_plant_is_removed() {
  local named
  [[ "$guard_code" == 0 ]] ||
    problems+=("want the guard to pass over the same tree once the planted offender is removed; it exited $guard_code and said: $(flat "$guard_out")")
  named="$(naming "$OFFENDER_NAME")"
  [[ -z "$named" ]] ||
    problems+=("the guard still named $OFFENDER_NAME, whose file is no longer in the tree: $(flat "$named")")
}

name="no-job-spec-kills.test.sh goes red naming the planted offender and green again once that file is removed"
problems=()

if probe_guard_is_there && plant; then
  if probe_plant_is_what_it_claims; then
    run_guard
    if probe_plant_is_red_first; then
      remove_plant
      if probe_plant_is_gone; then
        run_guard
        probe_guard_is_green_once_the_plant_is_removed
      fi
    fi
  fi
fi
drop_tree

report "$name"

finish
