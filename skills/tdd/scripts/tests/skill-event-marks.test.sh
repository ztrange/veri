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
# The event name is bounded on the right so a mark cannot answer for one whose name it is a
# prefix of — `event.sh bailed` is not `event.sh bail`, and the hyphen is excluded for the
# same reason `done` must not be satisfied by `step-done`.
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
    [[ "$line" =~ event\.sh[[:space:]]+"$event"([^a-z0-9-]|$) ]] && return 0
  done <<< "$records"
  if [[ -z "$anchored" ]]; then
    problems+=("$skill_md no longer $what — where \`event.sh $event\` belongs could not be read")
  else
    problems+=("$skill_md $what but calls no \`event.sh $event\` beside it: $(printf '%.130s' "$anchored")")
  fi
}

# 1. The whole of this step's criterion, as one case: seven marks, each beside the comment
#    it mirrors. They are one case because they are one wiring — an event log missing any
#    one of them cannot answer when a step started, why a run stopped, or what it cost —
#    and because the fix to any of them is one edit to one document.
name="$skill_md prescribes an event.sh call for each of the conductor's seven marks, beside the issue comment it mirrors"
problems=()
records="$(instructions)"
if [[ -z "$records" ]]; then
  # Fail closed: no records means the document was renamed or emptied and not one mark
  # below was tested, which must not read as seven passes.
  problems+=("$skill_md has no instructions to read — no mark could be checked")
else
  mark step-start 'takes the next unchecked step with next-unchecked.sh' \
    'next-unchecked\.sh'
  mark step-done 'posts the `### ✅ Step done` comment' \
    'step done' 'comment'
  mark pin 'posts the `### 📌 Already satisfied` comment' \
    'already satisfied' 'comment'
  mark revise 'posts the `### ♻️ Revise <phase> — attempt <k>` comment' \
    'revise <phase>' 'attempt' 'comment'
  mark bail 'posts the `### ⛔ Bailed — <phase>` comment' \
    'bailed' 'comment'
  mark done 'posts the final `### ✅ Done — <pr-url>` comment' \
    'pr-url' 'comment'
  mark resume 'posts the `### ▶️ Resuming` comment' \
    'resuming' 'comment'
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
