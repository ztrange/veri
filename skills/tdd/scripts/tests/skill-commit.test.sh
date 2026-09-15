#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor about the commit of the
# skill a run is executing. Like skill-timeout.test.sh and skill-test-command.test.sh this
# suite belongs to no single script: its subject is the procedure document, read as text,
# the way the session that follows it reads it. Picked up by `make test`'s glob by existing.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Why this exists (issue #165): why a run needs the skill's commit recorded at all is
# event.sh's header, the one place this cycle states it, and why the plan comment is where
# a human needs it is the step under test itself. What is this suite's to say is that the
# instruction is prose and so can only be pinned as prose: `supervise.sh` records the sha
# per launch, but nothing launches the conductor — the comment it posts exists only because
# SKILL.md tells it to, so a document that stops saying so is the whole of the regression.
#
# Contract under test (this step only):
#   SKILL.md's plan-comment step says that comment names the skill commit the run started
#   on, beside the test command and the timeout it already states.
#
# Run: scripts/tests/skill-commit.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document under test, twice: the path as it is quoted in every failure message, and
# the same path resolved for the probes to read. Both spellings come from one constant, so
# a message can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# section <heading> — the line range of the first heading that STARTS WITH the literal
# <heading>, up to the line before the next heading of any level, into `sec_start` and
# `sec_end`. Returns non-zero when no such heading exists, so a renamed section is reported
# rather than silently probed as an empty range — the fail-closed half that keeps "the
# section is gone" from reading as "the section says nothing wrong". A literal prefix
# rather than a regex because every heading here carries trailing prose after an em dash,
# so the prefix is what identifies it and is quotable in the message about not finding it.
sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  local next
  next="$(tail -n "+$((sec_start + 1))" "$md" | grep -nE '^#' | head -1 | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    sec_end=$((sec_start + next - 1))
  else
    sec_end=$(($(wc -l < "$md")))
  fi
  return 0
}

# need_section <heading> <consequence> — select the section under <heading>, or push one
# problem naming it and return non-zero. One constant for both the pattern searched for and
# the message about not finding it, so a message can never name a heading nothing looked for.
need_section() {
  section "$1" && return 0
  problems+=("$skill_md has no '$1' section — $2")
  return 1
}

# items — the current section's numbered list items, one per line and lowercased: a `N. `
# in column one plus the indented lines continuing it, up to the next such line or a blank
# one. Joining an item onto one line is what lets the claim ask whether ONE instruction
# carries the fact, rather than two sentences elsewhere in the section that happen to share
# a word. Case is folded last, because the sentences are the writer's.
items() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
    rec != "" { rec = rec " " $0 }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

# 1. The criterion, as one case: the comment a human reads before the first leaf names the
#    version of the skill the run started on. The plan comment is the anchor because it is
#    the one the conductor posts at scoping time and the one that already carries the run's
#    other two facts — the test command and the timeout; a sha recorded only in the event
#    log is not on the thread, which is where the narration it has to be read against is.
#
#    Both halves are asked of the same joined item, and each regex accepts any wording that
#    carries the fact: what is pinned is that the document says it, not how it is phrased.
name="$skill_md's plan comment names the skill commit the run started on"
problems=()

if need_section '### 2. Scope & plan' 'what the plan comment states could not be read'; then
  plan_item="$(items | grep -E 'plan.*comment')"
  if [[ -z "$plan_item" ]]; then
    problems+=("$skill_md's 'Scope & plan' section has no numbered item posting the plan comment — what that comment states could not be read")
  else
    for re in 'skill' 'commit'; do
      grep -qE "$re" <<< "$plan_item" ||
        problems+=("$skill_md's plan-comment item never says '$re', so the comment does not name the skill commit the run started on and the thread cannot say which version produced it: $(printf '%.120s' "$plan_item")")
    done
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
