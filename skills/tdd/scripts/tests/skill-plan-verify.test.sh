#!/usr/bin/env bash
# Unit test for where the conductor verifies the plan — like skill-verify-step.test.sh and
# skill-refactor-pending.test.sh this suite belongs to no single script: its subject is the
# procedure, read as text, the way the session that follows it reads it. Zero-dependency
# plain-shell asserts, same idiom, picked up by `make test`'s glob by existing.
#
# Why this exists (issue #439): the plan is the one artifact of a run nothing verifies, and
# `criterion-finished.sh` ticks the issue's criterion from the ledger's own paraphrase of
# it. #426 shipped with two mechanism steps standing in for criterion 1, every phase PASSed,
# and the criterion was ticked by bookkeeping. The `plan` phase now exists in
# `build-verify-prompt.sh` and in `prompts/verify-plan.md`, but a verifier the conductor
# never launches verifies nothing — and *where* it is launched is the whole of the
# criterion: after the ledger is committed (there is no plan to read before that) and before
# the first step (a plan caught wrong after step 3 has already been paid for).
#
# Contract under test — two cases, one per criterion:
#   1. SKILL.md launches the `plan` verdict between the instruction that commits the ledger
#      and the heading that opens the cycle loop, and the prose in that same span says a
#      REJECT rewrites the plan and re-verifies it, rather than ending the run.
#   2. The same span sends the third outcome — exit 2, no verdict rendered at all — down the
#      **system** failure bail, rather than letting it read as a PASS.
#
# Run: skills/tdd/scripts/tests/skill-plan-verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice: the path as every failure message spells it, and the same path
# resolved for the readers to open, so a message can never name a file the probes did not
# read.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# The three anchors, each an ERE written without a single backslash: `line_of` hands these to
# `awk -v`, which processes escape sequences in the value it is given, so `\.` would reach
# the matcher as a bare `.` — a metacharacter, quietly matching more than it was meant to.
# `[.]` is the same character class with nothing for -v to eat.
#
# The two that bracket the span are the run's own landmarks rather than headings: the ledger
# is committed by one named command, and the cycle loop opens with one numbered heading.
commit_re='git commit -m "plan: scope'
loop_re='^### 3[.] The cycle loop'
# A verdict launch for the `plan` phase, in either spelling the document uses to reach the
# verify verb — `run-verdict.sh`, the launcher the cycle loop execs since #426, or
# `verify.sh` itself, which the prose still names directly. The phase is a bare word after
# the script and whatever flags the call carries.
plan_launch_re='(run-verdict|verify)[.]sh.* plan '
# The outcome that carries no verdict, named by the code every script in this suite's subject
# speaks: exit 2 is "no answer could be obtained" — killed stuck, or output with no parseable
# `VERDICT:` line. The parentheses are classes for the same reason the dots above are.
exit2_re='[(]exit 2[)]'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the criterion is missing rather than just that one is.
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

# line_of <ere> — the 1-based number of the document's first line matching <ere>, or 0 when
# none does. Position is what a criterion about order is asking for: not whether the launch
# is written down, but whether it sits between the two landmarks.
line_of() {
  awk -v re="$1" 'n == 0 && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

# span_text <from> <to> — the lines strictly between two line numbers, lowercased and
# flattened to one line, so a sentence wrapped across two lines still reads as one.
span_text() {
  awk -v a="$1" -v b="$2" 'NR > a && NR < b' "$skill_path" |
    tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

# line_in_span <from> <to> <ere> — like `line_of`, but blind to everything outside the span:
# the document names exit 2 in a dozen other places, and only this span's answer is the
# criterion's subject.
line_in_span() {
  awk -v a="$1" -v b="$2" -v re="$3" \
    'n == 0 && NR > a && NR < b && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

# bullet_text <from> <to> <ere> — the span's first bullet matching <ere> together with the
# lines that continue it (a bullet ends at the next bullet or at a blank line), lowercased and
# flattened. The directive under test is one sentence wrapped across lines, and it is that
# bullet's own text that has to carry it: the span as a whole already says "bail" for the
# REJECT path, so a probe over the whole span would pass on the wrong bullet's words.
bullet_text() {
  awk -v a="$1" -v b="$2" -v re="$3" '
    NR <= a || NR >= b { next }
    !inb && match($0, re) { inb = 1; print; next }
    inb && ($0 ~ /^[[:space:]]*$/ || $0 ~ /^- /) { inb = 0 }
    inb { print }
  ' "$skill_path" | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

name="SKILL.md verifies the plan between the ledger commit and the first step, and a REJECT rewrites it and re-verifies"
problems=()

commit_line="$(line_of "$commit_re")"
loop_line="$(line_of "$loop_re")"

if [[ "$commit_line" -eq 0 ]]; then
  problems+=("$skill_md has no instruction committing the ledger (no line matching /$commit_re/), so there is no point in the run after which the plan exists to be read")
elif [[ "$loop_line" -eq 0 ]]; then
  problems+=("$skill_md has no cycle-loop heading (no line matching /$loop_re/), so there is no point in the run before which the plan has to have been verified")
else
  # The span both probes below judge against, named once: two spellings of it are two chances
  # for the line numbers a failure quotes to disagree with the ones the probe actually used.
  span_desc="the ledger commit (line $commit_line) and the cycle loop (line $loop_line)"
  launch_line="$(line_of "$plan_launch_re")"
  if [[ "$launch_line" -eq 0 ]]; then
    problems+=("$skill_md never launches the plan verifier: no line matching /$plan_launch_re/, so the plan phase is a prompt nothing runs")
  elif [[ "$launch_line" -le "$commit_line" || "$launch_line" -ge "$loop_line" ]]; then
    problems+=("$skill_md launches the plan verifier at line $launch_line, outside the span between $span_desc — before the commit there is no committed plan to verify, and after the loop opens the first step has already been paid for")
  fi

  span="$(span_text "$commit_line" "$loop_line")"
  for want in reject rewrit re-verif; do
    case "$span" in
      *"$want"*) ;;
      *) problems+=("$skill_md says nothing matching '$want' between $span_desc, so the span does not say that a REJECT rewrites the plan and re-verifies it rather than ending the run") ;;
    esac
  done
fi

report "$name"

# Case 2 — the same span's answer to the third exit code. A verifier leaf that was killed
# stuck, or one whose output carries no parseable `VERDICT:` line, leaves `wait-leaf.sh`
# exiting 2: no verdict was rendered at all. The two real verdicts are already written down
# above; the criterion here is that the third outcome is not quietly folded into the good one
# — a plan nobody looked at must bail the run as a **system** failure, never continue as if
# it had PASSed.
name="SKILL.md bails as a system failure when the plan verification rendered no verdict"
problems=()

if [[ "$commit_line" -eq 0 || "$loop_line" -eq 0 ]]; then
  problems+=("$skill_md is missing a landmark of the plan-verification span (ledger commit line $commit_line, cycle loop line $loop_line), so there is no span in which to read what an unobtainable verdict does")
else
  exit2_line="$(line_in_span "$commit_line" "$loop_line" "$exit2_re")"
  if [[ "$exit2_line" -eq 0 ]]; then
    problems+=("$skill_md says nothing about /$exit2_re/ between the ledger commit (line $commit_line) and the cycle loop (line $loop_line), so a plan verification that rendered no verdict has no documented outcome and reads as the PASS the conductor falls through to")
  else
    bullet="$(bullet_text "$commit_line" "$loop_line" "$exit2_re")"
    for want in bail system; do
      case "$bullet" in
        *"$want"*) ;;
        *) problems+=("$skill_md's exit-2 outcome for the plan verdict (line $exit2_line) says nothing matching '$want', so a run whose plan verifier rendered no verdict is not sent down the system-failure bail: $bullet") ;;
      esac
    done
  fi
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
