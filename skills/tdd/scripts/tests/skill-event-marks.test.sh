#!/usr/bin/env bash
# Unit tests for the conductor's own marks in the run's event log — like
# skill-timeout.test.sh and skill-test-command.test.sh this suite belongs to no single
# script: its subject is skills/tdd/SKILL.md, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-timeout.test.sh.
#
# Why this exists (issue #107): `event.sh` writes a line, but a writer nobody calls logs
# nothing. supervise.sh and verify.sh call it from inside a script, so their events are
# complete by construction; the conductor is prose, so its marks exist only where this
# document tells the session to write them. And they have to be told at the point the
# document already tells it to post the matching issue comment — one instruction, two
# mirrors of the same moment — because a mark prescribed anywhere else drifts away from
# the comment the first time either is reworded, and the log then disagrees with the
# thread about what the run did.
#
# Contract under test (this step only):
#   For each of the conductor's seven marks — step-start, step-done, pin, revise, bail,
#   done, resume — SKILL.md prescribes an `event.sh <mark>` call in the same instruction
#   as the issue comment that mark mirrors. `step-start` has no comment of its own (a step
#   begins where `next-unchecked.sh` hands one over), so its anchor is that command.
#
# Run: scripts/tests/skill-event-marks.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which mark is missing rather than just that some mark is.
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

# instructions — the document's numbered steps, bullets and paragraphs, one per line and
# lowercased. A record runs from a `N. ` or a `- ` (indented or not) in column one, or from
# the first line after a blank, up to the next such line or the next blank. Joining it onto
# one line is what lets each mark below ask whether ONE instruction carries both halves —
# the comment and the event — rather than two sentences in different sections that happen
# to share a word, which is exactly the drift this criterion is about.
#
# Runs of whitespace collapse to one space as the record is closed: a sentence wrapped
# across two lines keeps the second line's indentation otherwise, so `### ✅ Step\n
# done` would fold to `step      done` and no readable regex would match it. Case is
# folded away last, because the sentences are the writer's.
instructions() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' "$ROOT/$skill_md" | tr '[:upper:]' '[:lower:]'
}

# calls_event <instruction> <event> — does this instruction prescribe `event.sh <event>`?
#
# The event name is bounded on the right so a mark cannot answer for one whose name it is a
# prefix of — `event.sh bailed` is not `event.sh bail`, and the hyphen is excluded for the
# same reason `done` must not be satisfied by `step-done`. Every case that reads a call out of
# the document asks through here, so that boundary is one decision rather than one per case.
calls_event() {
  [[ "$1" =~ event\.sh[[:space:]]+"$2"([^a-z0-9-]|$) ]]
}

# insertion_re — how this document spells a call to `add-ledger-step.sh`, as a regex over a
# lowercased record: the call, not a mention. Every script the document orders run is written
# `$S/<script>`, and preflight names `add-ledger-step.sh` bare while reading its budget, so the
# `$S/` prefix is what tells the two apart. Three cases below ask it of a record, so the
# spelling is one decision rather than three.
insertion_re='\$s/add-ledger-step\.sh'

# have_records <what> — the guard every case that reads the document opens with. Fail closed:
# no records means SKILL.md was renamed or emptied and not one probe below ran, which must not
# read as a pass. Returns non-zero with the problem already filed, naming <what> went unchecked,
# so the case's body is skipped.
have_records() {
  [[ -n "$records" ]] && return 0
  problems+=("$skill_md has no instructions to read — $1 could not be checked")
  return 1
}

# mark <event> <what the instruction prescribes> <anchor-regex>… — assert that a single
# instruction of the global `records` matches every <anchor-regex> AND prescribes
# `event.sh <event>`, in two stages, because the two failures have different fixes.
#
# No instruction matches the anchors at all: the comment this mark mirrors has been
# reworded or moved, so where the call belongs could not be read. That is reported rather
# than passed over — fail closed, or a renamed section reads as a mark nobody has to write.
#
# Anchors match but none of them carries the call: that is the criterion failing, and the
# message quotes the instruction so the fix is an edit to a line already in front of you.
#
# On a pass, the global `marked` holds the instruction that carried the call, so a case
# asking more of the call than its name reads it from there rather than re-matching anchors.
mark() {
  local event="$1" what="$2" line re anchored=""
  shift 2
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    # The first anchored instruction, kept for the message; the loop goes on because a
    # later one may be the instruction that carries the call.
    [[ -n "$anchored" ]] || anchored="$line"
    calls_event "$line" "$event" && { marked="$line"; return 0; }
  done <<< "$records"
  if [[ -z "$anchored" ]]; then
    problems+=("$skill_md no longer $what — where \`event.sh $event\` belongs could not be read")
  else
    problems+=("$skill_md $what but calls no \`event.sh $event\` beside it: $(printf '%.130s' "$anchored")")
  fi
}

# comment_mark <event> <heading> <anchor-regex>… — a `mark` whose anchor is the issue
# comment it mirrors, which is every mark but `step-start`: the heading names the comment
# in the failure message, and `comment` joins the anchors so an instruction that merely
# mentions the heading in passing cannot answer for the one that posts it. Six of the seven
# go through here, so what is left spelled out at `step-start` is the one real difference —
# a step begins at a command, not at a comment.
comment_mark() {
  local event="$1" heading="$2"
  shift 2
  mark "$event" "posts the \`$heading\` comment" "$@" 'comment'
}

# refactor_mark — the `mark` every refactor case starts from: the instruction that posts the
# `### 🛠️ Refactor` comment and narrates the `git rev-list --count` figure (the plan comment
# lists that heading too, and is not where the count is known).
refactor_mark() {
  mark refactor 'posts the `### 🛠️ Refactor` comment' '### [^ ]+ refactor( |`|$)' 'post' 'rev-list --count'
}

# 1. The whole of this step's criterion, as one case: seven marks, each beside the comment
#    it mirrors. They are one case because they are one wiring — an event log missing any
#    one of them cannot answer when a step started, why a run stopped, or what it cost —
#    and because the fix to any of them is one edit to one document.
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

# 2. The refactor mark (issue #230): `metrics.sh` reads a `refactor` mark's `transforms`,
#    `budget` and `stopped` into the per-step `refactor` and `stopped` cells, and nothing
#    wrote one, so every step read `unknown`. The three values are the ones the
#    `### 🛠️ Refactor` comment already states, so the call belongs in the instruction that
#    posts it (see `refactor_mark`) — and a call carrying fewer than all three keys still
#    leaves a cell unknown.
name="$skill_md writes an event.sh refactor mark carrying transforms, budget and stopped, beside the Refactor comment"
problems=()
if have_records 'the refactor mark'; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    [[ "$marked" =~ (event\.sh[[:space:]]+refactor([^a-z0-9-][^\`]*)?) ]]
    call="${BASH_REMATCH[1]}"
    for key in transforms budget stopped; do
      [[ "$call" =~ (^|[[:space:]])"$key"= ]] ||
        problems+=("$skill_md calls \`$call\` without \`$key=\` — metrics.sh's cell stays unknown")
    done
  fi
fi
report "$name"

# 3. The refactor mark's count (issue #230): the figure is only worth logging if it is the
#    one `git rev-list --count` observed, and a count over the budget is the leaf ignoring
#    it — so an overrun clamped to the budget is exactly the event the log exists to show,
#    erased. The narration already says both about the comment; this case asks the sentence
#    that prescribes the *mark* to say them, because a mark instruction that only says
#    `transforms=<count>` leaves the session free to write the leaf's own account, or
#    `min(count, budget)`, and every cell downstream would still read as a real number.
name="$skill_md prescribes the refactor mark's transforms as the observed git rev-list count, unclamped on an overrun"
problems=()
if have_records "the refactor mark's count"; then
  refactor_mark
  if [[ "${#problems[@]}" -eq 0 ]]; then
    # The sentence that introduces the call: everything before `event.sh refactor`, from
    # the last sentence break on — the narration's own sentences do not count for the mark.
    before="${marked%%event.sh refactor*}"
    sentence="${before##*. }"
    [[ "$sentence" =~ observed|rev-list ]] ||
      problems+=("$skill_md introduces the refactor mark without saying its count is the observed one: $(printf '%.160s' "$sentence")")
    [[ "$sentence" =~ unclamped|never\ clamped ]] ||
      problems+=("$skill_md introduces the refactor mark without saying an overrun is recorded unclamped: $(printf '%.160s' "$sentence")")
  fi
fi
report "$name"

# 4. The refactor mark reaches the report (issue #230): cases 2 and 3 read the call as text,
#    and a call that reads right can still write a line `metrics.sh` does not read — a key
#    spelled differently, a quoted value — and every cell would stay `unknown` exactly as it
#    did before the mark existed. So this case runs the call SKILL.md prescribes, verbatim
#    but for its placeholders, through the real `event.sh` into a fixture log, beside a
#    second step that writes no refactor mark, and reads both rows of the real report: the
#    marked step says `7/5` (an overrun, so a clamp would show) and `budget`, the unmarked
#    one still says `unknown` in both cells rather than a borrowed or zero figure.
name="a run whose SKILL.md refactor mark is present renders real refactor and stopped cells for that step, and unknown for a step without one"
problems=()
S="$(cd "$HERE/.." && pwd)"
call="$(grep -m1 'event\.sh refactor ' "$ROOT/$skill_md" | sed 's/^[[:space:]]*//')"
if [[ -z "$call" ]]; then
  problems+=("$skill_md has no \`event.sh refactor\` call line to run — the report could not be checked")
else
  fixture="$(mktemp -d)"
  tidied="the step whose refactor mark was written"
  untidied="the step that wrote no refactor mark"
  call="${call//\$S/$S}"
  call="${call//<n>/230}"
  call="${call//<STEP>/$tidied}"
  call="${call//<count>/7}"
  call="${call//<VERI_REFACTOR_BUDGET>/5}"
  call="${call//<reason>/budget}"
  for s in "$tidied" "$untidied"; do
    ( cd "$fixture" && VERI_ISSUE=230 VERI_ACTOR=developer VERI_STEP="$s" VERI_PHASE=refactor \
        VERI_ATTEMPT=1 "$S/event.sh" launch name=develop-refactor ) ||
      problems+=("event.sh could not write the fixture's launch line for step: $s")
  done
  ( cd "$fixture" && bash -c "$call" ) ||
    problems+=("the call $skill_md prescribes did not run: $call")
  report_out="$( cd "$fixture" && "$S/metrics.sh" 230 2>&1 )" ||
    problems+=("want metrics.sh to exit 0, it did not: $report_out")
  # cell_of <step> <heading> — the cell under <heading> in the row for <step>, read from the
  # header of the table that row sits in.
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

# 5. The refactor mark's stop reason (issue #250): `refactor-triage.sh` gives two real
#    answers — exit 3, nothing structural is left and the tidying owes nothing; exit 0,
#    structural candidates remain and a follow-up owes them — and one `stopped=triage` value
#    for both leaves a log reader unable to tell them apart. So the record that prescribes
#    the mark must name `nothing-structural` against exit 3 and `structural-owed` against
#    exit 0, each within a short clause of its exit so a swapped pairing cannot pass, must no
#    longer offer `triage`, and must still offer the three reasons that did not change.
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

# 6. The plan grows mid-run (issue #360): `add-ledger-step.sh` inserts a step the scoping pass
#    never wrote, and a plan that changes without a record leaves the log unable to say which
#    steps the run chose for itself — metrics counts them, and a bail reader cannot otherwise
#    tell an original step from one a leaf asked for. The script is prose to the session like
#    every other mark here, so the event exists only where this document prescribes it: beside
#    the insertion, and beside EVERY insertion, since a second call site added later with no
#    mark of its own is exactly the drift this suite exists to catch.
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
  # Fail closed: no insertion prescribed anywhere means the loop asked nothing, which must not
  # read as a pass.
  [[ "$insertions" -gt 0 ]] ||
    problems+=("$skill_md prescribes no \`\$S/add-ledger-step.sh\` call — where \`event.sh step-added\` belongs could not be read")
fi
report "$name"

# 7. The Refactor phase's own insertion (issue #361): case 6 asks that every insertion
#    prescribed anywhere carries the mark, which a section that prescribes no insertion at all
#    satisfies vacuously. This case asks the one the Refactor phase makes — the call that grows
#    the plan with the `uncovered-spec` flags (#175) after verify-refactor's final PASS, in the same
#    breath as the refactor-pending clear — to carry it, so dropping that call or its mark from
#    the phase that grows the plan mid-run is caught where it happens.
name="$skill_md marks the Refactor section's own plan insertion with an event.sh step-added call beside it"
problems=()
if have_records "the Refactor section's step-added mark"; then
  mark step-added "grows the plan with the \`uncovered-spec\` flags beside the refactor-pending clear" \
    "$insertion_re" 'clear-refactor-pending\.sh' 'uncovered-spec'
fi
report "$name"

# 8. The three outcomes at exhaustion (issue #408): a step whose revise budget runs out no
#    longer ends one way but three — the criteria the leaf named replace it, it is parked for
#    the user, or it bails exactly as it did before — and marks that cannot be told apart
#    leave a log reader unable to say afterwards which of the three a run took. The bailed one
#    already carries its own cause token; the other two are new, and the split needs more than
#    a mark of its own: the Green section's volunteered split writes the very same call, so a
#    plan that grew at exhaustion and one that grew because a leaf asked read identically
#    unless this branch's mark carries something that one does not.
name="$skill_md marks the exhausted-budget split and the needs-user park in the event log, the split told apart from a leaf-volunteered one"
problems=()
if have_records 'the exhausted-budget marks'; then
  # The three branch records and the Green section's volunteered split, each anchored on what
  # only it says: the answer file plus its placement, the answer file plus the park, the third
  # answer's exit code beside the cause it keeps, and the `before` insertion that is the
  # leaf-volunteered split's own.
  split_rec="" park_rec="" bail_rec="" volunteered_rec=""
  while IFS= read -r line; do
    if [[ "$line" =~ exhausted-answer && "$line" =~ instead-of ]]; then split_rec="$line"
    elif [[ "$line" =~ exhausted-answer && "$line" =~ park ]]; then park_rec="$line"
    elif [[ "$line" =~ exit[[:space:]]+3 && "$line" =~ revise-exhausted ]]; then bail_rec="$line"
    elif [[ "$line" =~ $insertion_re && "$line" =~ [[:space:]]before[[:space:]] && "$line" =~ split: ]]; then volunteered_rec="$line"
    fi
  done <<< "$records"

  # event_calls <record> — every `event.sh <mark> [key=value …]` the record prescribes, one
  # per line. The call ends at the first word that is neither a mark name nor a key=value, so
  # the shell command that follows it in the same fenced block is not read as part of it.
  event_calls() { grep -oE 'event\.sh [a-z][a-z-]*( [a-z]+=[^ ]+)*' <<< "$1"; }

  # mark_names <calls> — the mark name of each of those calls, one per line: the name alone is
  # what two outcomes have to differ in for a log reader to tell them apart at a glance, its
  # keys aside.
  mark_names() { awk '{print $2}' <<< "$1"; }

  # The split branch's calls, read once: both halves below ask about them — the split's own,
  # against the volunteered split's, and the park's, against these.
  split_calls="$(event_calls "$split_rec")"

  # The split branch, and the half of this criterion nothing else pins: its mark must say
  # something the volunteered split's does not.
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

  # The needs-user branch, which writes no mark at all until this step: an escalation is the
  # one outcome that stops the run without a bail, so a log without it says only that the run
  # stopped saying nothing.
  if [[ -z "$park_rec" ]]; then
    problems+=("$skill_md prescribes no park beside .tdd/exhausted-answer.txt — where the escalated outcome's mark belongs could not be read")
  else
    park_calls="$(event_calls "$park_rec")"
    if [[ -z "$park_calls" ]]; then
      problems+=("$skill_md parks a step at exhaustion with no \`event.sh\` call beside it, so the outcome that stops a run without bailing it leaves no mark in the log")
    else
      # And a mark of its own: a park logged under the name the split writes is a third
      # outcome the log still reads as the first.
      split_names="$(mark_names "$split_calls")"
      own=""
      while IFS= read -r call; do
        grep -qxF "$(mark_names "$call")" <<< "$split_names" || own="$call"
      done <<< "$park_calls"
      [[ -n "$own" ]] ||
        problems+=("$skill_md marks the parked step only with marks the split branch writes too, so the escalated outcome is not distinguishable from the split one")
    fi
  fi

  # The third outcome, which already has its mark: the bail's cause token, kept beside the
  # answer that takes it, so all three ways out of exhaustion are named in one case.
  [[ -n "$bail_rec" ]] ||
    problems+=("$skill_md no longer names the revise-exhausted cause against exhausted-outcome.sh's exit 3, so the bailed outcome's own mark could not be read")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
