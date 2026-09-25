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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two documents. Each twice — the path as a failure message spells it, and the same
# path resolved for the probes to read — so a message can never name a file the probes did
# not open. The pairing claude-md-counts.test.sh and skill-leaf-launch.test.sh both use.
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report, plain, records, bullet and says: the helpers the *-recorded.test.sh suites
# share (issue #225). `bullet` reads "$skill_path"; `says` reads the passage_ globals.
# shellcheck source=record-helpers.sh
source "$HERE/record-helpers.sh"

# The three variables, as the regexes that tell them apart. The bare `VERI_MODEL` is
# bounded on the right, because `veri_model_developer` contains it: without the bound a
# document that named only the two role variables would read as one that named all three.
MODEL_ANY='veri_model([^_a-z]|$)'
MODEL_DEV='veri_model_developer'
MODEL_VER='veri_model_verifier'

# passage_text / passage_from — the passage a probe last read and the label a failure names
# it by, filled by the two readers below and read by `names_all_three` and `says`. Globals
# because bash has no way to hand back a string; the `passage_` prefix is what marks the
# pair as one thing written by a reader and read by a claim, the convention
# lane-rule-recorded.test.sh's `section_` pair follows.
passage_text="" passage_from=""

# need_supervise_bullet — SKILL.md's `supervise.sh` bullet into those globals, or one
# problem naming it and a non-zero return. The reader and the fail-closed check are one
# step, and the label and the problem are derived here rather than passed in, so no caller
# can report a bullet under a name the probe did not read — the shape
# lane-rule-recorded.test.sh's `need_section` has, for the same reason.
#
# Fail closed: an empty string matches no regex, so every fact asked of a bullet that is
# not there would be reported missing — true, but it names three edits when the repair is
# that one bullet moved.
need_supervise_bullet() {
  passage_from="$skill_md's supervise.sh bullet"
  passage_text="$(bullet '^[-*] .*supervise\.sh')"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$skill_md has no top-level 'supervise.sh' bullet to read, so the tunables an operator looks up beside VERI_TIMEOUT could not be found")
  return 1
}

# need_claude_md_records — all of CLAUDE.md's records into the same globals, for the claims
# that are about what a document says rather than about where it says it. CLAUDE.md is read
# whole on purpose: the step asks that the document name the variables and give the reason,
# not that either sit under a heading this suite picked.
need_claude_md_records() {
  passage_from="$claude_md"
  passage_text="$(records < "$claude_path")"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md could not be read, so nothing could be asked of what it records")
  return 1
}

# names_all_three <what> — the three variables in one record of the passage last read.
# Written once because both documents owe it and a copy that drifted would leave one of
# them held to a shorter list than the other.
names_all_three() {
  local what="$1"
  says "$what — it names no single passage carrying VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER" \
    "$MODEL_ANY" "$MODEL_DEV" "$MODEL_VER"
}

# probe_skill_bullet_lists_the_tunables — the launcher's bullet is where every leaf tunable
# is listed, and a fourth axis that is not in that list is one an operator has no way to
# find: `VERI_HEARTBEAT`, `VERI_TIMEOUT` and `VERI_STUCK_RETRIES` are all read off it.
probe_skill_bullet_lists_the_tunables() {
  need_supervise_bullet || return

  names_all_three "lists the three model tunables beside the ones it already lists"
}

# probe_claude_md_names_them_and_why — the document an agent reads first, and the two facts
# it owes: the names, and the reason the developer's and the verifier's are two knobs. The
# reason is asked in the terms the failure takes — a changed verdict distribution on one
# side, more revise cycles on the other — because that is what makes the sentence load-
# bearing rather than a restatement that there happen to be two variables.
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

# 1. One criterion, one case: the tunables are documented where they are looked up, with
#    the reason that keeps them apart. One case rather than three, because a reader given
#    two of the three names, or the three names without the reason, has been handed the
#    same unusable record — and the problem lines say which sentence is missing from which
#    document.
name="$skill_md's supervise.sh bullet and $claude_md name VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, and $claude_md says why developer and verifier are separate knobs"
problems=()

probe_skill_bullet_lists_the_tunables
probe_claude_md_names_them_and_why

report "$name"

# 2. The docs-record suites' shared helpers (issue #225): one file under this directory,
#    named outside make test's `*.test.sh` glob so it is sourced and never run as a suite,
#    that defines `report` and `plain` behaving the way every *-recorded.test.sh suite's own
#    copy does. Asked of fixed inputs and outputs rather than of this suite's copy, so the
#    case still means something once that copy is gone. Run in a subshell with the local
#    definitions unset first, so a pass is the shared file's answer and never this suite's,
#    and so its counters and `problems` never touch this suite's own.
helpers_rel="skills/tdd/scripts/tests/record-helpers.sh"
helpers_path="$ROOT/$helpers_rel"

# need_helpers_file <helpers> — the shared file is there to source, or one problem naming
# the helpers a probe went looking for in it and a non-zero return.
need_helpers_file() {
  [[ -f "$helpers_path" ]] && return 0
  problems+=("$helpers_rel does not exist, so there is no shared $1 to source")
  return 1
}

# same_as_copies <helpers> <copies> <got> <expected> — what calling the shared <helpers>
# printed is what <copies> print, or one problem quoting both.
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

# 3. The same shared file also defines `records`, `bullet` and `says` (issue #225), the
#    three helpers this suite and selection-order-recorded.test.sh carry identical copies
#    of. Asked the same way as case 2: fixed inputs and the outputs those copies give, in a
#    subshell with every local definition unset first. `bullet` reads the file named by
#    `skill_path` and `says` reads `passage_text` / `passage_from`, the globals a sourcing
#    suite sets, so the probe sets them to fixtures — `skill_path` is /dev/stdin, fed by a
#    here-string, so no scratch file is left behind (a process substitution is closed
#    before `bullet` reads it).
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

# 4. The two suites that carried identical copies of all five helpers now read them from
#    the shared file (issue #225): each sources record-helpers.sh at its top level and
#    defines no `report`, `plain`, `records`, `bullet` or `says` of its own, so a fix to the
#    shared file is the fix every one of them runs. Asked of each suite's source as text,
#    the way a reader checks it: a top-level `source` or `.` line naming the file, and no
#    line opening a function by one of the five names. The subshell sources in cases 2 and 3
#    are indented and name `$helpers_path`, so they answer neither question.

# probe_suite_uses_shared_helpers <stem> <helper>... — one problem when the suite
# <stem>.test.sh does not source the shared file at its top level, and one per <helper> it
# still defines itself.
# Given the stem, not the file name: a sibling suite's name written out in full outside a
# comment is what no-nested-suites.test.sh reads as launching it, and this only reads it.
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
    [[ "$text" =~ (^|$'\n')[[:space:]]*(function[[:space:]]+)?$fn[[:space:]]*\(\) ]] &&
      problems+=("$suite_rel still defines its own $fn")
  done
}

name="the selection-order-recorded and model-knobs-recorded suites source $helpers_rel and define no report, plain, records, bullet or says of their own"
problems=()

for stem in selection-order-recorded model-knobs-recorded; do
  probe_suite_uses_shared_helpers "$stem" report plain records bullet says
done

report "$name"

# 5. The two suites whose `says` reads a section rather than records carry only `report` and
#    `plain` as the shared copy (issue #225): each sources record-helpers.sh at its top level
#    and defines no `report` or `plain` of its own, but still defines its own `says` — sourced
#    first, a local definition is the one the suite runs, so its different question survives.
#    Asked of the source as text, as case 4 asks it.

# probe_suite_keeps_own_says <stem> — one problem when the suite <stem>.test.sh no longer
# opens a `says` function of its own.
probe_suite_keeps_own_says() {
  local suite_rel="skills/tdd/scripts/tests/$1.test.sh" text
  text="$(cat "$ROOT/$suite_rel" 2>/dev/null)" || return
  [[ "$text" =~ (^|$'\n')[[:space:]]*(function[[:space:]]+)?says[[:space:]]*\(\) ]] ||
    problems+=("$suite_rel no longer defines its own says")
}

name="the lane-rule-recorded and unit-tier-recorded suites source $helpers_rel and define no report or plain of their own, while each keeps its own says"
problems=()

for stem in lane-rule-recorded unit-tier-recorded; do
  probe_suite_uses_shared_helpers "$stem" report plain
  probe_suite_keeps_own_says "$stem"
done

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
