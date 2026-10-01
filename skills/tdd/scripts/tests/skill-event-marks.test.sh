#!/usr/bin/env bash
# Unit tests for the conductor's own marks in the run's event log, as skills/tdd/SKILL.md
# prescribes them, read as text.
#
# Contract under test:
#   For each of the conductor's seven marks — step-start, step-done, pin, revise, bail,
#   done, resume — SKILL.md prescribes an `event.sh <mark>` call in the same instruction
#   as the issue comment that mark mirrors. `step-start` has no comment of its own (a step
#   begins where `next-unchecked.sh` hands one over), so its anchor is that command.
#
# Run: scripts/tests/skill-event-marks.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"


source "$HERE/lib/harness.sh"

instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

calls_event() {
  [[ "$1" =~ event\.sh[[:space:]]+"$2"([^a-z0-9-]|$) ]]
}

at_over_budget() {
  [[ "$1" =~ event\.sh\ "$2".*[[:space:]]at=over-budget([[:space:]]|$) ]]
}

cost_check_at() {
  grep -m1 -nE "^#### The step's cost check" "$ROOT/$skill_md" | cut -d: -f1
}

exit_bullet_after() {
  awk -v from="$1" -v n="$2" 'NR > from && index($0, "- **exit " n " ") == 1 { print NR; exit }' "$ROOT/$skill_md"
}

cost_bullet_at() {
  local section_at
  section_at="$(cost_check_at)"
  [[ -z "$section_at" ]] || exit_bullet_after "$section_at" "$1"
}

cost_branch() {
  local from to=""
  from="$(cost_bullet_at "$1")"
  [[ -z "$from" ]] || to="$(exit_bullet_after "$from" "$2")"
  [[ -z "$to" ]] || echo "$from $to"
}

insertion_re='\$s/add-ledger-step\.sh'

have_records() {
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no instructions to read — $1 could not be checked")
  return 1
}

mark() {
  local event="$1" what="$2" line re anchored=""
  shift 2
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    [[ -n "$anchored" ]] || anchored="$line"
    calls_event "$line" "$event" && { marked="$line"; return 0; }
  done <<< "$records"
  if [[ -z "$anchored" ]]; then
    problems+=("$skill_md no longer $what — where \`event.sh $event\` belongs could not be read")
  else
    problems+=("$skill_md $what but calls no \`event.sh $event\` beside it: $(printf '%.130s' "$anchored")")
  fi
}

comment_mark() {
  local event="$1" heading="$2"
  shift 2
  mark "$event" "posts the \`$heading\` comment" "$@" 'comment'
}

refactor_mark() {
  mark refactor 'posts the `### 🛠️ Refactor` comment' '### [^ ]+ refactor( |`|$)' 'post' 'rev-list --count'
}

refactor_call() {
  [[ "$marked" =~ (event\.sh[[:space:]]+refactor([^a-z0-9-][^\`]*)?) ]]
  call="${BASH_REMATCH[1]}"
}

name="$skill_md prescribes an event.sh call for each of the conductor's seven marks, beside the issue comment it mirrors"
problems=()
records="$(instructions)"
if have_records 'no mark'; then
  mark step-start 'takes the next unchecked step with next-unchecked.sh' \
    'next-unchecked\.sh'
  comment_mark step-done '### ✅ Step done' 'step done'
  comment_mark pin '### 📌 Already satisfied' 'already satisfied'
  comment_mark revise '### ♻️ Revise <phase> — attempt <k>' 'revise <phase>' 'attempt'
  comment_mark bail '### ⛔ Bailed — <phase>' 'bailed'
  comment_mark done '### ✅ Done — <pr-url>' 'pr-url'
  comment_mark resume '### ▶️ Resuming' 'resuming'
fi
report "$name"

name="$skill_md writes an event.sh refactor mark carrying transforms, budget and stopped, beside the Refactor comment"
problems=()
if have_records 'the refactor mark'; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    refactor_call
    for key in transforms budget stopped; do
      [[ "$call" =~ (^|[[:space:]])"$key"= ]] ||
        problems+=("$skill_md calls \`$call\` without \`$key=\` — metrics.sh's cell stays unknown")
    done
  fi
fi
report "$name"

name="$skill_md prescribes the refactor mark's transforms as the observed git rev-list count, unclamped on an overrun"
problems=()
if have_records "the refactor mark's count"; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    before="${marked%%event.sh refactor*}"
    sentence="${before##*. }"
    [[ "$sentence" =~ observed|rev-list ]] ||
      problems+=("$skill_md introduces the refactor mark without saying its count is the observed one: $(printf '%.160s' "$sentence")")
    [[ "$sentence" =~ unclamped|never\ clamped ]] ||
      problems+=("$skill_md introduces the refactor mark without saying an overrun is recorded unclamped: $(printf '%.160s' "$sentence")")
  fi
fi
report "$name"

name="a run whose SKILL.md refactor mark is present renders real refactor and stopped cells for that step, and unknown for a step without one"
problems=()
S="$(cd "$HERE/.." && pwd)"
call="$(grep -m1 'event\.sh refactor ' "$ROOT/$skill_md" | sed 's/^[[:space:]]*//')"
if [[ -z "$call" ]]; then
  problems+=("$skill_md has no \`event.sh refactor\` call line to run — the report could not be checked")
else
  fixture="$(scratch_dir)"
  tidied="the step whose refactor mark was written"
  untidied="the step that wrote no refactor mark"
  call="${call//\$S/$S}"
  call="${call//<n>/230}"
  call="${call//<STEP>/$tidied}"
  call="${call//<count>/7}"
  call="${call//<VERI_REFACTOR_BUDGET>/5}"
  call="${call//<reason>/budget}"
  mkdir -p "$fixture/.tdd"
  printf -- '- [x] %s ⟂ refactor pending\n- [ ] %s\n' "$tidied" "$untidied" > "$fixture/.tdd/issue-230.md"
  for s in "$tidied" "$untidied"; do
    ( cd "$fixture" && VERI_ISSUE=230 VERI_ACTOR=developer VERI_STEP="$s" VERI_PHASE=refactor \
        VERI_ATTEMPT=1 "$S/event.sh" launch name=develop-refactor ) ||
      problems+=("event.sh could not write the fixture's launch line for step: $s")
  done
  ( cd "$fixture" && bash -c "$call" ) ||
    problems+=("the call $skill_md prescribes did not run: $call")
  report_out="$( cd "$fixture" && "$S/metrics.sh" 230 2>&1 )" ||
    problems+=("want metrics.sh to exit 0, it did not: $report_out")
  cell_of() {
    awk -F'|' -v step="$1" -v want="$2" '
      function trim(s) { gsub(/^[[:space:]]+|[[:space:]]+$/, "", s); return s }
      !/^\|/ { seen = 0; col = 0; next }
      !seen { seen = 1; for (i = 2; i < NF; i++) if (trim($i) == want) col = i; next }
      col && trim($2) == step { print trim($col); exit }' <<< "$report_out"
  }
  for probe in "$tidied|refactor|7/5" "$tidied|stopped|budget" \
               "$untidied|refactor|unknown" "$untidied|stopped|unknown"; do
    IFS='|' read -r s heading want <<< "$probe"
    got="$(cell_of "$s" "$heading")"
    [[ "$got" == "$want" ]] ||
      problems+=("step \"$s\": want its $heading cell to say \`$want\`, it says \`$got\`")
  done
  [[ "${#problems[@]}" -eq 0 ]] || problems+=("the report was: $(printf '%q' "$report_out")")
  rm -rf "$fixture"
fi
report "$name"

name="$skill_md names stopped=nothing-structural for refactor-triage.sh exit 3 and stopped=structural-owed for exit 0, no stopped=triage, and keeps malformed, nothing-left and budget"
problems=()
if have_records "the refactor mark's stop reasons"; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    for pair in '3|nothing-structural' '0|structural-owed'; do
      IFS='|' read -r code value <<< "$pair"
      exit_re="exit \**${code}\**"
      value_re="\`(stopped=)?${value}\`"
      [[ "$marked" =~ ${exit_re}[^\;,.\`]{0,40}${value_re} || "$marked" =~ ${value_re}[^\;,.\`]{0,40}${exit_re} ]] ||
        problems+=("$skill_md does not name \`stopped=$value\` against refactor-triage.sh exit $code")
    done
    [[ "$marked" =~ \`(stopped=)?triage\` ]] &&
      problems+=("$skill_md still offers \`stopped=triage\`, which cannot tell exit 3 from exit 0")
    for value in nothing-left budget malformed; do
      [[ "$marked" =~ \`(stopped=)?${value}\` ]] ||
        problems+=("$skill_md no longer offers \`stopped=$value\` for the refactor mark")
    done
  fi
fi
report "$name"

name="$skill_md prescribes an event.sh step-added call beside every add-ledger-step.sh insertion"
problems=()
if have_records 'the step-added mark'; then
  insertions=0
  while IFS= read -r line; do
    [[ "$line" =~ $insertion_re ]] || continue
    insertions=$((insertions + 1))
    calls_event "$line" step-added ||
      problems+=("$skill_md inserts a step with no \`event.sh step-added\` beside it: $(printf '%.130s' "$line")")
  done <<< "$records"
  [[ "$insertions" -gt 0 ]] ||
    problems+=("$skill_md prescribes no \`\$S/add-ledger-step.sh\` call — where \`event.sh step-added\` belongs could not be read")
fi
report "$name"

name="$skill_md marks the Refactor section's own plan insertion with an event.sh step-added call beside it"
problems=()
if have_records "the Refactor section's step-added mark"; then
  mark step-added "grows the plan with the \`uncovered-spec\` flags beside the refactor-pending clear" \
    "$insertion_re" 'clear-refactor-pending\.sh' 'uncovered-spec'
fi
report "$name"

name="$skill_md marks the exhausted-budget split and the needs-user park in the event log, the split told apart from a leaf-volunteered one"
problems=()
if have_records 'the exhausted-budget marks'; then
  split_rec="" park_rec="" bail_rec="" volunteered_rec=""
  while IFS= read -r line; do
    if [[ "$line" =~ exhausted-answer && "$line" =~ instead-of ]]; then split_rec="$line"
    elif [[ "$line" =~ exhausted-answer && "$line" =~ park ]]; then park_rec="$line"
    elif [[ "$line" =~ exit[[:space:]]+3 && "$line" =~ revise-exhausted ]]; then bail_rec="$line"
    elif [[ "$line" =~ $insertion_re && "$line" =~ [[:space:]]before[[:space:]] && "$line" =~ split: ]]; then volunteered_rec="$line"
    fi
  done <<< "$records"

  event_calls() { grep -oE 'event\.sh [a-z][a-z-]*( [a-z]+=[^ ]+)*' <<< "$1"; }

  mark_names() { awk '{print $2}' <<< "$1"; }

  split_calls="$(event_calls "$split_rec")"

  if [[ -z "$split_rec" ]]; then
    problems+=("$skill_md prescribes no instead-of insertion beside .tdd/exhausted-answer.txt — where the split outcome's mark belongs could not be read")
  elif [[ -z "$volunteered_rec" ]]; then
    problems+=("$skill_md prescribes no \`before\` insertion for a leaf-volunteered split — what the exhausted split must be told apart from could not be read")
  else
    distinct=""
    while IFS= read -r call; do
      [[ -n "$call" ]] || continue
      [[ "$volunteered_rec" == *"$call"* ]] || distinct="$call"
    done <<< "$split_calls"
    [[ -n "$distinct" ]] ||
      problems+=("$skill_md marks the split a run reaches at exhaustion with nothing a leaf-volunteered split does not write too, so the log cannot say which of the two grew the plan: $(printf '%.130s' "$split_rec")")
  fi

  if [[ -z "$park_rec" ]]; then
    problems+=("$skill_md prescribes no park beside .tdd/exhausted-answer.txt — where the escalated outcome's mark belongs could not be read")
  else
    park_calls="$(event_calls "$park_rec")"
    if [[ -z "$park_calls" ]]; then
      problems+=("$skill_md parks a step at exhaustion with no \`event.sh\` call beside it, so the outcome that stops a run without bailing it leaves no mark in the log")
    else
      split_names="$(mark_names "$split_calls")"
      own=""
      while IFS= read -r call; do
        grep -qxF "$(mark_names "$call")" <<< "$split_names" || own="$call"
      done <<< "$park_calls"
      [[ -n "$own" ]] ||
        problems+=("$skill_md marks the parked step only with marks the split branch writes too, so the escalated outcome is not distinguishable from the split one")
    fi
  fi

  [[ -n "$bail_rec" ]] ||
    problems+=("$skill_md no longer names the revise-exhausted cause against exhausted-outcome.sh's exit 3, so the bailed outcome's own mark could not be read")
fi
report "$name"

name="$skill_md writes one event.sh step-over-budget carrying spent= and budget= at the crossing, before the over-budget leaf is launched"
problems=()
launch_at="$(grep -m1 -nE 'detach-leaf\.sh.*develop-over-budget' "$ROOT/$skill_md" | cut -d: -f1)"
if [[ -z "$launch_at" ]]; then
  problems+=("$skill_md launches no develop-over-budget leaf through detach-leaf.sh — where the crossing's mark belongs could not be read")
else
  before_launch="$(head -n "$((launch_at - 1))" "$ROOT/$skill_md" | while IFS= read -r line; do
    calls_event "$line" step-over-budget && printf '%s\n' "$line"
  done)"
  calls=0
  [[ -z "$before_launch" ]] || calls="$(wc -l <<< "$before_launch" | tr -d ' ')"
  if [[ "$calls" -ne 1 ]]; then
    problems+=("want one \`event.sh step-over-budget\` before the develop-over-budget launch at $skill_md:$launch_at, found $calls")
  else
    for key in spent budget; do
      [[ "$before_launch" =~ event\.sh\ step-over-budget.*[[:space:]]"$key"= ]] ||
        problems+=("$skill_md's crossing mark carries no \`$key=\`: $(printf '%.130s' "$before_launch")")
    done
  fi
fi
report "$name"

name="$skill_md writes step-over-budget on every crossing, before the branch that splits, parks or carries on"
problems=()
section_at="$(cost_check_at)"
read_at="$(grep -m1 -nE 'exhausted-outcome\.sh < \.tdd/develop-over-budget\.out' "$ROOT/$skill_md" | cut -d: -f1)"
if [[ -z "$section_at" || -z "$read_at" ]]; then
  problems+=("$skill_md has no cost-check section or no exhausted-outcome.sh read of the over-budget answer — where every crossing's mark belongs could not be read")
else
  shared=0
  while IFS= read -r line; do
    [[ "$line" =~ ^[^[:space:]] ]] && calls_event "$line" step-over-budget && shared=$((shared + 1))
  done < <(sed -n "$((section_at + 1)),$((read_at - 1))p" "$ROOT/$skill_md")
  [[ "$shared" -ge 1 ]] ||
    problems+=("no top-level \`event.sh step-over-budget\` between $skill_md:$section_at and the over-budget answer's read at $skill_md:$read_at, so not every crossing — split, park or carry on — writes it")
  for outcome in 0 1 3; do
    bullet_at="$(exit_bullet_after "$section_at" "$outcome")"
    if [[ -z "$bullet_at" ]]; then
      problems+=("$skill_md's cost check has no \`- **exit $outcome\` branch — the crossing that takes it could not be read")
    elif [[ "$bullet_at" -le "$read_at" ]]; then
      problems+=("$skill_md's exit $outcome branch at line $bullet_at comes before the over-budget answer's read at line $read_at")
    fi
  done
fi
report "$name"

name="$skill_md's over-budget exit 0 branch writes step-split carrying at=over-budget, and the revise-exhausted split keeps at=exhausted"
problems=()
read -r split_at park_at <<< "$(cost_branch 0 1)"
if [[ -z "$park_at" ]]; then
  problems+=("$skill_md's cost check has no \`- **exit 0\` branch followed by an \`- **exit 1\` one — where the cost-driven split's mark belongs could not be read")
else
  over_budget=0 exhausted=0 lineno=0
  while IFS= read -r line; do
    lineno=$((lineno + 1))
    calls_event "$line" step-split || continue
    if (( lineno > split_at && lineno < park_at )); then
      at_over_budget "$line" step-split && over_budget=$((over_budget + 1))
    else
      [[ "$line" =~ event\.sh\ step-split[[:space:]]+at=exhausted([[:space:]]|$) ]] && exhausted=$((exhausted + 1))
    fi
  done < "$ROOT/$skill_md"
  [[ "$over_budget" -ge 1 ]] ||
    problems+=("no \`event.sh step-split\` carrying \`at=over-budget\` in the over-budget exit 0 branch at $skill_md:$split_at–$park_at, so a cost-driven split reads in the log as another cause's")
  [[ "$exhausted" -ge 1 ]] ||
    problems+=("no \`event.sh step-split at=exhausted\` outside the over-budget branch, so the revise-exhausted split lost the spelling #408 gave it")
fi
report "$name"

name="$skill_md's over-budget exit 1 branch writes step-escalated carrying at=over-budget"
problems=()
read -r park_at carry_at <<< "$(cost_branch 1 3)"
if [[ -z "$carry_at" ]]; then
  problems+=("$skill_md's cost check has no \`- **exit 1\` branch followed by an \`- **exit 3\` one — where the cost-driven park's mark belongs could not be read")
else
  over_budget=0
  while IFS= read -r line; do
    calls_event "$line" step-escalated &&
      at_over_budget "$line" step-escalated &&
      over_budget=$((over_budget + 1))
  done < <(sed -n "$((park_at)),$((carry_at - 1))p" "$ROOT/$skill_md")
  [[ "$over_budget" -ge 1 ]] ||
    problems+=("no \`event.sh step-escalated\` carrying \`at=over-budget\` in the over-budget exit 1 branch at $skill_md:$park_at–$carry_at, so a cost-driven park reads in the log as a verifier's")
fi
report "$name"

name="$skill_md's over-budget exit 3 branch writes no event mark beyond the crossing's step-over-budget"
problems=()
carry_at="$(cost_bullet_at 3)"
if [[ -z "$carry_at" ]]; then
  problems+=("$skill_md's cost check has no \`- **exit 3\` branch — where the carry-on writes nothing could not be read")
else
  # hazard: fed by a pipe, the writer would die of SIGPIPE when the loop breaks.
  mapfile -t -s "$((carry_at - 1))" branch < "$ROOT/$skill_md"
  lineno="$carry_at"
  for line in "${branch[@]}"; do
    (( lineno > carry_at )) && [[ "$line" =~ ^[^[:space:]] ]] && break
    [[ "$line" =~ event\.sh[[:space:]]+[a-z] ]] &&
      problems+=("the over-budget exit 3 branch writes a mark of its own at $skill_md:$lineno: $(printf '%.130s' "$line")")
    lineno=$((lineno + 1))
  done
fi
report "$name"

name="case 13 reads $skill_md's exit 3 branch without leaving a writer mid-stream, and still names a mark planted there by its line (#526)"
problems=()
scratch="$(scratch_dir)"
mkdir -p "$scratch/$(dirname "$skill_md")"
fixture="$scratch/$skill_md"
case13="$(awk '/^name=".*over-budget exit 3 branch writes no event mark/ { on = 1 } on && /^report "\$name"$/ { exit } on { print }' "${BASH_SOURCE[0]}")"
carry_at="$(cost_bullet_at 3)"
if [[ -z "$case13" ]]; then
  problems+=("case 13's code could not be cut out of this suite's source, so how it reads the branch could not be asked")
elif [[ -z "$carry_at" ]]; then
  problems+=("$skill_md's cost check has no \`- **exit 3\` branch — where to plant a mark could not be read")
else
  planted_at=$((carry_at + 1))
  planted='  run `$S/event.sh step-not-split` before carrying on.'
  {
    sed -n "1,${carry_at}p" "$ROOT/$skill_md"
    printf '%s\n' "$planted"
    sed -n "$((carry_at + 1)),\$p" "$ROOT/$skill_md"
    for _ in {1..4000}; do printf '%s\n' 'Padding past the branch, so the rest of the file outgrows any pipe buffer.'; done
  } > "$fixture"
  [[ "$(sed -n "${planted_at}p" "$fixture")" == "$planted" ]] ||
    problems+=("the fixture does not carry the planted mark at line $planted_at, so what case 13 names could not be asked")
  stderr_out="$( (
    trap '' PIPE
    ROOT="$scratch"
    problems=()
    eval "$case13"
    printf '%s\n' "${problems[@]}" > "$scratch/named"
  ) 2>&1 > /dev/null)"
  [[ -z "$stderr_out" ]] ||
    problems+=("case 13 wrote to stderr reading the exit 3 branch, so a writer outlived its reader and its error would land after the count line: $(printf '%.200s' "$stderr_out")")
  named="$(cat "$scratch/named" 2> /dev/null)"
  [[ "$named" == *"$skill_md:$planted_at"* ]] ||
    problems+=("case 13 did not name a mark planted in the exit 3 branch at $skill_md:$planted_at; it filed: ${named:-nothing}")
fi
rm -rf "$scratch"
report "$name"

name="$skill_md writes the refactor mark with pass=<k>: 1 for a step's first pass, one more each time the triangulation path resumes the refactor loop"
problems=()
if have_records "the refactor mark's pass index"; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    refactor_call
    [[ "$call" =~ (^|[[:space:]])pass= ]] ||
      problems+=("$skill_md calls \`$call\` without \`pass=\` — two passes of one step cannot be told apart")
    [[ "$marked" =~ (^|[^0-9])1([^0-9]|$)[^.\;]{0,40}first || "$marked" =~ first[^.\;]{0,60}[^0-9]1([^0-9]|$) ]] ||
      problems+=("$skill_md does not say a step's first refactor pass marks \`pass=1\`: $(printf '%.160s' "$marked")")
    [[ "$marked" =~ (one more|increments?|\+ ?1)[^.]{0,120}triangulat || "$marked" =~ triangulat[^.]{0,160}(one more|increments?|\+ ?1) ]] ||
      problems+=("$skill_md does not say the pass index counts one more each time the triangulation path resumes the refactor loop: $(printf '%.160s' "$marked")")
  fi
fi
report "$name"

finish
