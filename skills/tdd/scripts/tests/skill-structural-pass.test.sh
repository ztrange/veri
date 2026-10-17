#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md runs the issue's one structural pass, read as
# text.
#
# Contract under test: the Draft PR step — reached when `next-unchecked.sh` exits 3 — before
# its `gh pr ready`, lists the recorded candidates with `refactor-owed.sh list`, builds one
# `build-develop-prompt.sh structural` prompt per candidate, bounds it to
# `refactor-touched.sh --issue`, and counts it against `refactor-budget.sh --issue`.
#
# Run: scripts/tests/skill-structural-pass.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
draft_pr='### 4. Draft PR'


source "$HERE/lib/harness.sh"

require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

before_ready() {
  awk -v h="$draft_pr" \
    'index($0, h) == 1 { inside = 1; next }
     inside && (/^#/ || /gh_pr_ready/) { exit }
     inside' "$skill_path" | tr -d '*`' | tr '\n' ' '
}
section="$(before_ready)"

pass_text="${section#*one structural pass}"
squeezed="$(tr -s ' ' <<<"$pass_text")"
touches_phrase='transform-touches-tests.sh <base-sha>'
verifier_phrase='transform verifier against <base-sha>'

missing_pass() {
  [[ "$pass_text" == "$section" ]] || return 1
  problems+=("$skill_md's Draft PR step has no 'one structural pass' before gh pr ready — $1 could not be established")
}

offset() {
  local head="${2%%"$1"*}"
  if [[ "$head" == "$2" ]]; then echo -1; else echo "${#head}"; fi
}

name="#596: $skill_md's structural pass runs whenever refactor-owed.sh list prints a candidate, never skips or shortens it for cost, spends less only by a lower VERI_ISSUE_REFACTOR_BUDGET set before launch, and files candidates past the budget by refactor-overflow.sh"
problems=()

if ! missing_pass 'whether it may be skipped for cost'; then
  require 'whenever refactor-owed.sh list prints a candidate' "$squeezed" \
    "$skill_md's structural pass never says it runs whenever refactor-owed.sh list prints a candidate"
  require 'never skips or shortens it for cost' "$squeezed" \
    "$skill_md's structural pass never says the conductor never skips or shortens it for cost"
  require 'set a lower VERI_ISSUE_REFACTOR_BUDGET before launch' "$squeezed" \
    "$skill_md's structural pass never says the way to spend less is to set a lower VERI_ISSUE_REFACTOR_BUDGET before launch"
  require 'past the budget are filed by refactor-overflow.sh' "$squeezed" \
    "$skill_md's structural pass never says candidates past the budget are filed by refactor-overflow.sh"
fi

report "$name"

name="#596: $skill_md's structural pass says stopped= takes only candidates-done, budget-spent or nothing-structural, and budget-spent is marked only when refactor-budget.sh --issue exited 3, i.e. transforms equals the budget"
problems=()

if ! missing_pass 'which reasons its mark may carry'; then
  require 'stopped= takes only candidates-done, budget-spent or nothing-structural' "$squeezed" \
    "$skill_md's structural pass never says stopped= takes only candidates-done, budget-spent or nothing-structural"
  require 'budget-spent is marked only when refactor-budget.sh --issue exited 3' "$squeezed" \
    "$skill_md's structural pass never says budget-spent is marked only when refactor-budget.sh --issue exited 3"
  require 'transforms equals the budget' "$squeezed" \
    "$skill_md's structural pass never says budget-spent means transforms equals the budget"
fi

report "$name"

name="#691: $skill_md's structural pass takes each candidate's predicate from a build-develop-prompt.sh predicate leaf checked by structural-predicate.sh, whose record is the test path the transform verifier runs, and skips a candidate with no predicate for refactor-overflow.sh to file"
problems=()

if ! missing_pass 'where each candidate'"'"'s predicate comes from'; then
  require 'build-develop-prompt.sh predicate' "$squeezed" \
    "$skill_md's structural pass never builds a build-develop-prompt.sh predicate prompt, so no predicate leaf writes a candidate's predicate"
  require 'structural-predicate.sh .tdd/issue-<n>-predicate' "$squeezed" \
    "$skill_md's structural pass never checks the predicate leaf's report with structural-predicate.sh .tdd/issue-<n>-predicate"
  require 'the test path the transform verifier runs' "$squeezed" \
    "$skill_md's structural pass never says the record structural-predicate.sh writes is the test path the transform verifier runs, so the verifier is still handed the prose candidate"
  require 'with no predicate is skipped' "$squeezed" \
    "$skill_md's structural pass never says a candidate with no predicate is skipped rather than handed to a transform leaf"
  require 'refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md <taken> <skipped-file>' "$squeezed" \
    "$skill_md's structural pass never hands refactor-overflow.sh the <skipped-file>, so a candidate skipped for want of a predicate is never filed"
fi

report "$name"

name="#726: $skill_md's structural pass says a missing .tdd/issue-<n>-refactor-owed.md is the refactor-owed.sh list exit-3 case, marked stopped=nothing-structural before the PR is readied"
problems=()

if ! missing_pass 'what a missing refactor-owed file means'; then
  require 'a missing .tdd/issue-<n>-refactor-owed.md is the list exit-3 case' "$squeezed" \
    "$skill_md's structural pass never says a missing .tdd/issue-<n>-refactor-owed.md is the list exit-3 case, so a run with no owed file reads it as no pass and no mark"
  require 'marked stopped=nothing-structural before the PR is readied' "$squeezed" \
    "$skill_md's structural pass never says the missing-file case is marked stopped=nothing-structural before the PR is readied"
fi

report "$name"

name="#952: $skill_md's structural pass runs refactor-owed.sh applied on the run's owed file with the candidate and the commit after each transform verifier PASS, before the PR body is rendered"
problems=()
applied_phrase='refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md'

if ! missing_pass 'whether an applied transform is recorded'; then
  applied="$(offset "$applied_phrase" "$pass_text")"
  verifier="$(offset "$verifier_phrase" "$pass_text")"
  if [[ "$applied" -lt 0 ]]; then
    problems+=("$skill_md's structural pass never runs $applied_phrase before gh pr ready, so refactor-owed.sh render still lists a transform the pass applied as owed")
  elif [[ "$verifier" -ge "$applied" ]]; then
    problems+=("$skill_md's structural pass runs $applied_phrase at $verifier_phrase's offset $verifier or before ($applied), not after the transform verifier's PASS")
  fi
  require 'PASS' "$pass_text" \
    "$skill_md's structural pass never ties refactor-owed.sh applied to a transform verifier PASS"
fi

report "$name"

name="#980: $skill_md's structural pass stages and commits .tdd/issue-<n>-refactor-owed.md after refactor-owed.sh applied records a transform, before the PR is readied"
problems=()
stage_phrase='git add .tdd/issue-<n>-refactor-owed.md'

if ! missing_pass 'whether the applied record is committed'; then
  applied="$(offset "$applied_phrase" "$pass_text")"
  staged="$(offset "$stage_phrase" "$pass_text")"
  after_stage="${pass_text:$(( staged < 0 ? 0 : staged ))}"
  if [[ "$applied" -lt 0 || "$staged" -lt 0 ]]; then
    problems+=("$skill_md's structural pass is missing a phrase to order before gh pr ready: $applied_phrase at $applied, $stage_phrase at $staged (-1 = absent), so the applied record never rides a commit")
  elif [[ "$staged" -le "$applied" ]]; then
    problems+=("$skill_md's structural pass stages the owed file at $staged, not after $applied_phrase at $applied")
  elif [[ "$after_stage" != *'git commit'* ]]; then
    problems+=("$skill_md's structural pass stages .tdd/issue-<n>-refactor-owed.md but never runs git commit after it before gh pr ready")
  fi
fi

report "$name"

name="#992: $skill_md's structural pass hands the owed file's out-of-scope candidates to refactor-overflow.sh even when the pass skipped nothing or list exits 3, so they are still filed as Refactor owed by #<n>"
problems=()

if ! missing_pass 'whether out-of-scope candidates are filed with no candidate listed'; then
  no_candidate="${squeezed#*list exits 3}"
  no_candidate="${no_candidate%%Mark the PR ready for review*}"
  if [[ "$no_candidate" == "$squeezed" ]]; then
    problems+=("$skill_md's structural pass has no 'list exits 3' case — whether out-of-scope candidates are filed without a pass could not be established")
  else
    require 'refactor-overflow.sh' "$no_candidate" \
      "$skill_md's structural pass never runs refactor-overflow.sh when list exits 3, so an owed file holding only out-of-scope candidates files nothing"
    require 'out-of-scope' "$no_candidate" \
      "$skill_md's structural pass never names the out-of-scope candidates in its list exit-3 case, so they are not handed to refactor-overflow.sh there"
  fi
  nothing_skipped="${squeezed#*With nothing skipped}"
  nothing_skipped="${nothing_skipped%%No candidate*}"
  if [[ "$nothing_skipped" == "$squeezed" ]]; then
    problems+=("$skill_md's structural pass has no 'With nothing skipped' case — whether out-of-scope candidates are filed when the pass skipped nothing could not be established")
  else
    require 'refactor-overflow.sh' "$nothing_skipped" \
      "$skill_md's structural pass never runs refactor-overflow.sh with nothing skipped, so a pass that applies every structural candidate drops the out-of-scope ones"
    require 'out-of-scope' "$nothing_skipped" \
      "$skill_md's structural pass never names the out-of-scope candidates in its nothing-skipped case, so they are not handed to refactor-overflow.sh there"
  fi
  require 'Refactor owed by #<n>' "$squeezed" \
    "$skill_md's structural pass never says out-of-scope candidates are filed as Refactor owed by #<n>"
fi

report "$name"

name="#1058: $skill_md's structural pass records a candidate whose predicate already holds (structural-predicate.sh exit 1) as applied with refactor-owed.sh applied at the current HEAD, not in <skipped-file>; only exit 3 appends to <skipped-file>"
problems=()

if ! missing_pass 'what an already-applied candidate becomes'; then
  predicate_text="${squeezed#*structural-predicate.sh .tdd/issue-<n>-predicate}"
  predicate_bound='Once the pass ends'
  if [[ "$predicate_text" == "$squeezed" ]]; then
    problems+=("$skill_md's structural pass never runs structural-predicate.sh .tdd/issue-<n>-predicate — what its exit 1 leads to could not be established")
  elif [[ "$predicate_text" != *"$predicate_bound"* ]]; then
    problems+=("$skill_md's structural pass never says '$predicate_bound' after structural-predicate.sh .tdd/issue-<n>-predicate — where its predicate handling ends could not be established")
  else
    predicate_text="${predicate_text%%"$predicate_bound"*}"
    require 'refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md' "$predicate_text" \
      "$skill_md's structural pass never records a candidate structural-predicate.sh exits 1 for with refactor-owed.sh applied, so refactor-overflow.sh files an already-applied candidate as owed"
    require 'git rev-parse HEAD' "$predicate_text" \
      "$skill_md's structural pass never records an already-applied candidate at the current HEAD"
    require 'only exit 3' "$predicate_text" \
      "$skill_md's structural pass never says only exit 3 (PREDICATE: NONE) appends a candidate to <skipped-file>"
    if [[ "$predicate_text" == *'1 or 3 ⇒ skip'* ]]; then
      problems+=("$skill_md's structural pass still says structural-predicate.sh exit 1 or 3 ⇒ skip, so an already-applied candidate lands in <skipped-file>")
    fi
  fi
fi

report "$name"

name="#1058: $skill_md's Draft PR step re-checks every refactor-owed.sh out-of-scope candidate against the tree before refactor-overflow.sh runs: a develop-predicate leaf per candidate, and structural-predicate.sh exit 1 records it applied as out-of-scope | <candidate>"
problems=()

if ! missing_pass 'whether out-of-scope candidates are re-checked before filing'; then
  recheck_cmd='refactor-owed.sh out-of-scope .tdd/issue-<n>-refactor-owed.md'
  overflow_cmd='refactor-overflow.sh <n> .tdd/issue-<n>-refactor-owed.md'
  recheck="$(offset "$recheck_cmd" "$squeezed")"
  overflow="$(offset "$overflow_cmd" "$squeezed")"
  if [[ "$recheck" -lt 0 || "$overflow" -lt 0 ]]; then
    problems+=("$skill_md's structural pass is missing a command to order: $recheck_cmd at $recheck, $overflow_cmd at $overflow (-1 = absent), so an out-of-scope candidate a later plan step applied is filed as owed")
  elif [[ "$recheck" -gt "$overflow" ]]; then
    problems+=("$skill_md's structural pass runs $overflow_cmd at $overflow before $recheck_cmd at $recheck, so out-of-scope candidates are filed before they are re-checked")
  else
    recheck_text="${squeezed:$recheck:$((overflow - recheck))}"
    require 'develop-predicate' "$recheck_text" \
      "$skill_md never launches a develop-predicate leaf per out-of-scope candidate between $recheck_cmd and $overflow_cmd"
    require 'structural-predicate.sh' "$recheck_text" \
      "$skill_md never checks an out-of-scope candidate's predicate with structural-predicate.sh between $recheck_cmd and $overflow_cmd"
    require 'refactor-owed.sh applied .tdd/issue-<n>-refactor-owed.md' "$recheck_text" \
      "$skill_md never records an already-applied out-of-scope candidate with refactor-owed.sh applied before $overflow_cmd"
    require 'out-of-scope | <candidate>' "$recheck_text" \
      "$skill_md never records an already-applied out-of-scope candidate as 'out-of-scope | <candidate>', so refactor-overflow.sh still files it"
  fi
fi

report "$name"

finish
