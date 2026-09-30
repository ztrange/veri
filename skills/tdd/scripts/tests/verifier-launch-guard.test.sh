#!/usr/bin/env bash
# Unit test for the guard that keeps a verifier launch out of the shape that stalled #297 —
# case 5 of skills/tdd/scripts/tests/skill-leaf-launch.test.sh, which reads SKILL.md's
# fenced launch lines and refuses one that reaches `verify.sh` without naming
# `supervise.sh`. Like docs-read-guard.test.sh, prose-drift-red.test.sh and
# hermetic-suites.test.sh this suite has no script as its subject: its subject is what
# another suite reports about the document it is run against. Zero-dependency plain-shell
# asserts, same idiom as docs-read-guard.test.sh.
#
# Why this exists (issue #415): SKILL.md:17 states that every leaf — developer or verifier —
# is launched through the supervisor, and SKILL.md:322 launched the verifier through
# `detach-leaf.sh` alone for months. Nothing gave that verifier a heartbeat or a timeout, so
# when it died before writing `.tdd/verdict-<phase>.exit` the conductor waited on a file
# nothing would ever write — twice on #297, deterministically, with the thread sitting dead
# until a human looked. The launch lines are fixed now, and a fix to prose is exactly the
# kind that comes back: the next incident-driven edit to a launch, or the next author
# spelling one out from the shape above it, puts the bypass back as one plausible line.
#
# The guard is what stops that, and a guard that has never been watched to fail is not
# tested: every verifier launch in the document carries the supervisor today, so case 5
# passes over this tree whether it still checks anything or not. Deleting its `problems+=`
# line, or narrowing the lines it reads, would leave `make test` green and the invariant
# unguarded. So the contradiction is planted instead, and the guard is asked about the
# planted document.
#
# Contract under test:
#   Over a copy of this tree whose one `verdict-red` launch line has had the supervisor and
#   its leaf name cut out of it — the #297 shape, `detach-leaf.sh` straight to the verdict
#   launcher that execs `verify.sh` — skill-leaf-launch.test.sh fails, and the line it names is
#   that launch: SKILL.md with the planted line's number, saying `supervise.sh` is what is
#   missing. Over the same tree with the document unplanted it passes.
#
# Both halves are the case, and the green half is not decoration: red over a tree is worth
# nothing unless the same guard is green over the same tree before the plant. A guard broken
# so that it fails on everything would satisfy the red half alone.
#
# Naming the line, rather than merely failing, is the criterion too — and naming ONLY that
# line. A guard that listed every launch line in the document would fail over the plant and
# send the next author to nine addresses, eight of which are correct.
#
# The plant carries the document and the guard and nothing else, because those are the only
# two files the guard resolves against its own repo root. In particular the generated tree
# is not copied, and no line below names a path in it, which is what no-docs-reads.test.sh
# asks of every suite in this directory.
#
# Case 2 below is the same seam one incident later, and lives here rather than in a suite of
# its own because its subject is the same one: what skill-leaf-launch.test.sh reports about a
# documented launch line planted wrong. There the plant is the #297 bypass; there it is the
# #431 one — the step's title back in single quotes, which an apostrophe in the planning
# leaf's own English closes early. Its own header, beside it, says the rest.
#
# Run: skills/tdd/scripts/tests/verifier-launch-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
ROOT="$(cd "$HERE/../../../.." && pwd)"

GUARD='skills/tdd/scripts/tests/skill-leaf-launch.test.sh'
GUARD_PATH="$ROOT/$GUARD"

SKILL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL"

FRAGMENT='$S/supervise.sh verdict-red '

MISSING='supervise.sh'

VERIFIER='run-verdict.sh'

scratch="$(scratch_dir)"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

failures_in() {
  local line
  line="$(grep -E '^[0-9]+ passed, [0-9]+ failed$' <<< "$1" | tail -1)"
  [[ -n "$line" ]] || { printf '%s' '<none>'; return; }
  line="${line#*, }"
  printf '%s' "${line% failed}"
}

make_plant_tree() {
  tree="$scratch/$1"
  mkdir -p "$tree/${SKILL%/*}" "$tree/${GUARD%/*}" || {
    problems+=("could not make a scratch tree to plant the document in, so the criterion went unasked")
    return 1
  }
  guard_copy="$tree/$GUARD"
  cp "$GUARD_PATH" "$guard_copy"
  mkdir -p "${guard_copy%/*}/lib" && cp "$HERE/lib/harness.sh" "${guard_copy%/*}/lib/"
}

plant() {
  make_plant_tree tree || return 1

  planted_skill="$scratch/planted-SKILL.md"
  FRAG="$FRAGMENT" awk '
    !cut && (i = index($0, ENVIRON["FRAG"])) > 0 {
      $0 = substr($0, 1, i - 1) substr($0, i + length(ENVIRON["FRAG"]))
      cut = 1
    }
    { print }
  ' "$SKILL_PATH" > "$planted_skill"

  planted_line="$(head -1 < <(grep -nF "$FRAGMENT" "$SKILL_PATH") | cut -d: -f1)"
  return 0
}

probe_guard_is_there() {
  [[ -f "$GUARD_PATH" ]] || {
    problems+=("there is no guard suite at $GUARD, so no launch line in $SKILL is checked for reaching $VERIFIER without $MISSING")
    return 1
  }
  [[ -x "$GUARD_PATH" ]] || {
    problems+=("$GUARD is not executable, so \`make test\`'s runner cannot run it")
    return 1
  }
}

probe_plant_is_what_it_claims() {
  [[ "$planted_line" =~ ^[0-9]+$ ]] || {
    problems+=("no line of $SKILL carries '$FRAGMENT' (found '$planted_line'), so there is no supervised verifier launch to cut it out of and the criterion cannot be asked")
    return
  }
  local before after
  probe_one_carrier "$FRAGMENT"
  before="$(sed -n "${planted_line}p" "$SKILL_PATH")"
  after="$(sed -n "${planted_line}p" "$planted_skill")"
  [[ "$before" == *"$VERIFIER"* && "$before" == *"$MISSING"* ]] ||
    problems+=("$SKILL:$planted_line is not a supervised verifier launch to begin with, so cutting the supervisor out of it contradicts nothing: $(flat "$before")")
  [[ "$after" == *"$VERIFIER"* ]] ||
    problems+=("the planted $SKILL:$planted_line no longer reaches $VERIFIER, so the guard has no verifier launch there to judge: $(flat "$after")")
  [[ "$after" != *"$MISSING"* ]] ||
    problems+=("the planted $SKILL:$planted_line still names $MISSING, so nothing was planted: $(flat "$after")")
  probe_one_line_rewritten "$planted_skill" launch
}

run_guard_over() {
  cp "$1" "$tree/$SKILL"
  guard_out="$("$guard_copy" 2>&1)" && guard_code=0 || guard_code=$?
}

probe_one_carrier() {
  local carriers
  carriers="$(grep -cF "$1" "$SKILL_PATH")"
  [[ "$carriers" == 1 ]] ||
    problems+=("$SKILL carries '$1' on $carriers lines, want exactly 1 — with more than one the plant's address is a guess")
}

probe_one_line_rewritten() {
  local changed
  changed="$(diff "$SKILL_PATH" "$1" | grep -c '^[<>]')"
  [[ "$changed" == 2 ]] ||
    problems+=("the plant rewrote $changed lines of $SKILL, want exactly one line rewritten (2 diff lines) — a red over a document changed twice is not about the $2")
}

probe_guard_is_red() {
  local what="$1" failures
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 ]] ||
    problems+=("want ${GUARD##*/} to fail over a $SKILL whose $what; it exited 0 and said: $(flat "$guard_out")")
  [[ "$failures" != 0 && "$failures" != '<none>' ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state a failure over that document; it stated '$failures': $(flat "$guard_out")")
}

probe_only_this_address() {
  local want="$SKILL:$1" addresses
  addresses="$(grep -oE "${SKILL//./\\.}:[0-9]+" <<< "$guard_out" | sort -u | tr '\n' ' ')"
  [[ "$addresses" == "$want " ]] ||
    problems+=("${GUARD##*/} named the addresses '$addresses' over that document, want only $want — the document's other documented lines are correct and a red naming them is a list rather than a fix")
}

probe_guard_is_green_unplanted() {
  local failures
  run_guard_over "$SKILL_PATH"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over $SKILL as committed — red there says nothing about the plant; it exited $guard_code and said: $(flat "$guard_out")")
  [[ "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/}'s own count line to state 0 failed over $SKILL as committed; it stated '$failures': $(flat "$guard_out")")
}

probe_guard_names_the_planted_launch() {
  local named
  run_guard_over "$planted_skill"
  probe_guard_is_red "$planted_line reaches $VERIFIER without $MISSING"
  named="$(grep -F "$SKILL:$planted_line" <<< "$guard_out")"
  if [[ -z "$named" ]]; then
    problems+=("no line of ${GUARD##*/}'s output names $SKILL:$planted_line, the launch the plant cut $MISSING out of; it said: $(flat "$guard_out")")
  else
    grep -qF "$MISSING" <<< "$named" ||
      problems+=("${GUARD##*/} named $SKILL:$planted_line without saying $MISSING is what it no longer goes through; the lines naming it were: $(flat "$named")")
  fi
  probe_only_this_address "$planted_line"
}

name="${GUARD##*/} fails over a $SKILL whose verifier launch has lost $MISSING, naming that line and nothing else, and passes over the document as committed"
problems=()
tree=""
guard_copy=""
planted_skill=""
planted_line=""
guard_out=""
guard_code=0

if probe_guard_is_there && plant; then
  probe_plant_is_what_it_claims
  probe_guard_is_green_unplanted
  probe_guard_names_the_planted_launch
fi
report "$name"


STEP_ANCHOR='$S/refactor-owed.sh append '

STEP_DOUBLE='"<STEP>"'
STEP_SINGLE="'<STEP>'"

EXEMPT_DECL='declare -A EXEMPT=('
EXEMPT_REASON='planted by verifier-launch-guard.test.sh to ask what an exemption with a reason does'

exempting() {
  local reason="$1" out="$scratch/guard-exempt-${2}.test.sh"
  grep -qF "$EXEMPT_DECL" "$GUARD_PATH" || return 1
  DECL="$EXEMPT_DECL" ENTRY="  [\"$SKILL:$step_line\"]=\"$reason\"" awk '
    { print }
    !done && index($0, ENVIRON["DECL"]) > 0 { print ENVIRON["ENTRY"]; done = 1 }
  ' "$GUARD_PATH" > "$out"
  printf '%s' "$out"
}

plant_step_title() {
  make_plant_tree step-tree || return 1

  step_line="$(head -1 < <(grep -nF "$STEP_ANCHOR" "$SKILL_PATH") | cut -d: -f1)"
  planted_step_skill="$scratch/planted-step-SKILL.md"
  LINE="$step_line" FROM="$STEP_DOUBLE" TO="$STEP_SINGLE" awk '
    NR == ENVIRON["LINE"] && (i = index($0, ENVIRON["FROM"])) > 0 {
      $0 = substr($0, 1, i - 1) ENVIRON["TO"] substr($0, i + length(ENVIRON["FROM"]))
    }
    { print }
  ' "$SKILL_PATH" > "$planted_step_skill"
  return 0
}

probe_step_plant_is_what_it_claims() {
  [[ "$step_line" =~ ^[0-9]+$ ]] || {
    problems+=("no line of $SKILL carries '$STEP_ANCHOR' (found '$step_line'), so there is no documented launch to put the title's quotes back on and the criterion cannot be asked")
    return 1
  }
  local before after
  probe_one_carrier "$STEP_ANCHOR"
  before="$(sed -n "${step_line}p" "$SKILL_PATH")"
  after="$(sed -n "${step_line}p" "$planted_step_skill")"
  [[ "$before" == *"$STEP_DOUBLE"* ]] ||
    problems+=("$SKILL:$step_line does not carry $STEP_DOUBLE to begin with, so single-quoting it contradicts nothing: $(flat "$before")")
  [[ "$after" == *"$STEP_SINGLE"* ]] ||
    problems+=("the planted $SKILL:$step_line does not carry $STEP_SINGLE, so nothing was planted: $(flat "$after")")
  probe_one_line_rewritten "$planted_step_skill" "step title"
  return 0
}

probe_step_guard_names_the_planted_line() {
  run_guard_over "$planted_step_skill"
  probe_guard_is_red "$step_line carries $STEP_SINGLE"
  probe_only_this_address "$step_line"
}

probe_exemption_with_a_reason_excuses_the_line() {
  local guard_with_reason failures
  guard_with_reason="$(exempting "$EXEMPT_REASON" reason)" || {
    problems+=("${GUARD##*/} carries no exemption table — no '$EXEMPT_DECL' line — so a documented line that has to keep $STEP_SINGLE can only be answered by deleting the check")
    return 1
  }
  cp "$guard_with_reason" "$guard_copy"
  run_guard_over "$planted_step_skill"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" == 0 && "$failures" == 0 ]] ||
    problems+=("want ${GUARD##*/} to pass over that document once its table names $SKILL:$step_line with a reason; it exited $guard_code, its count line stated '$failures' and it said: $(flat "$guard_out")")
}

probe_exemption_without_a_reason_excuses_nothing() {
  local guard_no_reason failures
  guard_no_reason="$(exempting '' noreason)" || return 1
  cp "$guard_no_reason" "$guard_copy"
  run_guard_over "$planted_step_skill"
  failures="$(failures_in "$guard_out")"
  [[ "$guard_code" != 0 && "$failures" != 0 && "$failures" != '<none>' ]] ||
    problems+=("want ${GUARD##*/} to fail over that document when its table names $SKILL:$step_line with no reason — an entry that says nothing excuses nothing; it exited $guard_code, its count line stated '$failures' and it said: $(flat "$guard_out")")
  grep -F "$SKILL:$step_line" <<< "$guard_out" > /dev/null ||
    problems+=("${GUARD##*/} failed over that document without naming $SKILL:$step_line, the line the reasonless entry did not excuse; it said: $(flat "$guard_out")")
}

reset_step_case() {
  problems=()
  tree=""
  guard_copy=""
  planted_step_skill=""
  step_line=""
  guard_out=""
  guard_code=0
}

name="${GUARD##*/} fails over a $SKILL whose launch line carries $STEP_SINGLE, naming that line and nothing else, unless its exemption table names it with a reason"
reset_step_case

if probe_guard_is_there && plant_step_title; then
  if probe_step_plant_is_what_it_claims; then
    probe_guard_is_green_unplanted
    probe_step_guard_names_the_planted_line
    if probe_exemption_with_a_reason_excuses_the_line; then
      probe_exemption_without_a_reason_excuses_nothing
    fi
  fi
fi
report "$name"

PIN_CASE='FAIL - the #431 guard still refuses a single-quoted step title'

name="${GUARD##*/}'s #431 guard pin still answers over a $SKILL whose one $STEP_DOUBLE line is planted $STEP_SINGLE and exempted with a reason (#437)"
reset_step_case

if probe_guard_is_there && plant_step_title; then
  if probe_step_plant_is_what_it_claims; then
    if guard_with_reason="$(exempting "$EXEMPT_REASON" pin)"; then
      cp "$guard_with_reason" "$guard_copy"
      run_guard_over "$planted_step_skill"
      [[ "$(failures_in "$guard_out")" != '<none>' ]] ||
        problems+=("${GUARD##*/} never reached its count line over that document, so its #431 pin went unasked: $(flat "$guard_out")")
      grep -F "$PIN_CASE" <<< "$guard_out" > /dev/null &&
        problems+=("${GUARD##*/}'s #431 pin failed over $SKILL with $SKILL:$step_line planted $STEP_SINGLE and exempted with a reason: $(flat "$guard_out")")
    else
      problems+=("${GUARD##*/} carries no exemption table — no '$EXEMPT_DECL' line — to name $SKILL:$step_line in")
    fi
  fi
fi
report "$name"

finish
