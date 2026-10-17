#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md drives the refactor-pending mark, and for the
# account of it in this repository's CLAUDE.md and CONTEXT.md, read as text.
#
# Contract under test — the mark's writer, then its reader, one case each:
#   1. SKILL.md's Green PASS ticks with `tick-ledger.sh --refactor-pending`; the pin path's
#      tick carries no such flag; and the instruction that ends a step's cycle runs
#      `clear-refactor-pending.sh`, commits the cleared ledger, and only then mirrors the
#      step as done.
#   2. SKILL.md's Resume asks `next-pending-refactor.sh` before `next-unchecked.sh`, and the
#      branch it takes on a pending step resets what the killed leaf left uncommitted,
#      re-enters that step's refactor loop with the files of its green commit (the last
#      commit that changed the ledger) and the count of `refactor:` commits since it, then
#      runs verify-refactor — with the draft PR behind both scripts exiting 3.
#   3. SKILL.md's Draft PR step itself refuses to open the PR while
#      `git status --porcelain` is non-empty or `next-pending-refactor.sh` still finds a
#      pending step.
#   4. SKILL.md's script reference list has an entry for each of the three, saying what it
#      prints (or, for the two that edit the ledger, the mark they write and strip) and
#      which exit codes it can answer with.
#   5. CLAUDE.md's ledger invariant and CONTEXT.md's **Ledger** entry each say that a ticked
#      step also carries the mark until its verify-refactor passes.
#   6. SKILL.md's Resume branch for a pending step resets what the killed leaf left
#      uncommitted and relaunches the refactor leaf with `VERI_REFACTOR_BUDGET` reduced by
#      the `refactor:` commits that step already has.
#   7. SKILL.md passes the step's green commit sha to `verify.sh refactor` at both call
#      sites: the cycle loop's `<green-sha>` and Resume's `$green`.
#   8. SKILL.md's Resume resets the worktree BEFORE it asks `next-pending-refactor.sh`.
#   9. SKILL.md's Resume captures `git status --porcelain` BEFORE that reset and says the
#      `### ▶️ Resuming` comment names the paths it discarded.
#  10. SKILL.md's Draft PR step's refusal names a remedy that applies with a dirty tree, no
#      step pending and none unchecked, and says the run reaches the PR after it.
#  11. SKILL.md's Resume says a leaf killed in Red or Green leaves the same stray work a
#      killed refactor leaf does.
#  12. SKILL.md's Resume sub-step 2 uses the `$stray` preflight step 3 captured and never
#      runs `stray="$(git status --porcelain)"` again after that reset.
#
# Run: scripts/tests/skill-refactor-pending.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
context_md="CONTEXT.md"
context_path="$ROOT/$context_md"

mark='⟂ refactor pending'

verify_refactor='(verify|run-verdict)\.sh (--step ("[^"]*"|[^ ]+) )?(--fast-cmd [^ ]+ )?refactor'

reset_command='git (reset|checkout|restore|clean)'

dirty_tree='git status --porcelain'


source "$HERE/lib/harness.sh"
source "$HERE/lib/first-record.sh"
source "$HERE/lib/plain.sh"

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

instructions() {
  records_of < "$skill_path"
}

claude_records() {
  records_of < "$claude_path"
}
context_records() {
  records_of < "$context_path"
}

section_of() {
  awk -v heading="$1" -v closers="$2" \
    '$0 ~ closers { inside = ($0 == heading); next } inside' "$skill_path" | records_of
}

resume_instructions() {
  section_of '## Resume' '^## '
}

draft_pr_instructions() {
  section_of '### 4. Draft PR' '^## |^### '
}

scripts_instructions() {
  section_of '## The scripts (this skill'\''s `scripts/` directory)' '^## '
}

records_from() {
  records="$("$1")"
  [[ -n "$records" ]] && return 0
  problems+=("$2")
  return 1
}

records_text=""
text_from() {
  records_from "$1" "$2" || return 1
  records_text="$(printf '%s' "$records" | tr '\n' ' ')"
}

ordinal() {
  local n=0 line
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$line" =~ $1 ]]; then printf '%s\n' "$n"; return 0; fi
  done <<< "$records"
  printf '0\n'
}

precedes() {
  local first second
  first="$(ordinal "$1")"
  second="$(ordinal "$2")"
  if [[ "$first" -eq 0 ]]; then
    problems+=("$3")
  elif [[ "$second" -eq 0 ]]; then
    problems+=("$4")
  elif [[ "$first" -gt "$second" ]]; then
    problems+=("$5")
  fi
}

first_instruction() {
  local args=() re
  for re in "$@"; do
    args+=(-E "$re")
  done
  instruction="$(first_record "$records" "${args[@]}")"
  [[ -n "$instruction" ]]
}

instruction=""
reads() {
  local what="$1"
  shift
  first_instruction "$@" && return 0
  problems+=("$skill_md has no instruction that $what — what that branch prescribes could not be read")
  return 1
}

record_name=""
record_of() {
  local where="$1" what="$2"
  shift 2
  record_name="$where's $what"
  first_instruction "$@" && return 0
  problems+=("$where has no $what — what it records about a ticked step could not be read")
  return 1
}

says() {
  [[ "$instruction" =~ $1 ]] || problems+=("$2")
}
denies() {
  if [[ "$instruction" =~ $1 ]]; then problems+=("$2"); fi
}

entry_script=""
reads_entry() {
  local escaped="${1//./\\.}"
  entry_script="$1"
  reads "documents $1 in the script reference list" "^- .\\\$s/$escaped"
}

entry_says() {
  says "$1" "$skill_md's entry for $entry_script $2"
}

says_exit_codes() {
  entry_says 'exits? 0' \
    "never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty"
  entry_says 'exits? 3' \
    "never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken"
}

says_removal_verb() {
  local whole="$instruction"
  instruction="${whole//"$entry_script"/}"
  entry_says 'strip|remove|drop|clear|delete' \
    "never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name"
  instruction="$whole"
}

reference_list_probes() {
  if reads_entry tick-ledger.sh; then
    entry_says '--refactor-pending' \
      "never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick"
    entry_says "$mark" \
      "never spells the mark the flag appends, so nothing connects that write to the \`$mark\` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing"
    entry_says 'exits? 3' \
      "never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick"
  fi

  if reads_entry next-pending-refactor.sh; then
    entry_says 'prints?[^.]*step' \
      "never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on"
    says_exit_codes
  fi

  if reads_entry clear-refactor-pending.sh; then
    entry_says "$mark" \
      "never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark"
    says_removal_verb
    says_exit_codes
  fi
}

removal_verb_probe() {
  if reads_entry clear-refactor-pending.sh; then
    says_removal_verb
  fi
}

probes_against_planted() {
  local probes="$1" unreadable="$2"
  local planted_dir real_skill_path
  planted_dir="$(scratch_dir)"
  cat > "$planted_dir/SKILL.md"
  real_skill_path="$skill_path"
  skill_path="$planted_dir/SKILL.md"
  problems=()
  if records_from scripts_instructions "$unreadable"; then
    "$probes"
  fi
  probe_problems=("${problems[@]}")
  problems=()
  skill_path="$real_skill_path"
  rm -rf "$planted_dir"
}

says_pending_until_verified() {
  says "$mark" \
    "$record_name never spells the \`$mark\` mark, so this repository's own account of the ledger still says a tick means the step is finished, and the next agent to read it takes the mark back out as noise"
  says 'verify-refactor' \
    "$record_name records the mark without naming verify-refactor, so nothing says what clears it and a ticked step's mark reads as something the ledger wears for ever"
}

miss() {
  problems+=("$1: $(printf '%.130s' "$instruction")")
}

says_clear_commit_mirror() {
  local rest="$instruction"
  if [[ ! "$rest" =~ clear-refactor-pending\.sh ]]; then
    miss "$skill_md never runs clear-refactor-pending.sh where a step's cycle completes, so the mark green wrote is never removed and every finished step reads as pending"
    return
  fi
  rest="${rest#*clear-refactor-pending.sh}"
  if [[ ! "$rest" =~ git[[:space:]].*commit ]]; then
    miss "$skill_md clears the mark but commits nothing after it, so the cleared ledger stays uncommitted and the next resume reads the committed one, which still says pending"
    return
  fi
  rest="${rest#*commit}"
  [[ "$rest" =~ tick-issue-criterion\.sh ]] ||
    miss "$skill_md mirrors the step to the issue before the cleared ledger is committed, so a run killed in that window has an issue saying done over a ledger still saying pending"
}

says_reset_reenter_verify() {
  local before after
  local anchor='git diff --name-only'
  local reset_re='git (checkout|restore|reset|stash|clean)'
  local green_re='git log.*issue-<n>\.md'
  local verify_re='verify-refactor|verify\.sh refactor'
  if [[ ! "$instruction" =~ $anchor ]]; then
    miss "$skill_md's Resume re-enters no refactor loop for the pending step — nothing computes the files of its green commit, so the loop has no bounds to tidy within and the step is left green but never tidied"
    return
  fi
  before="${instruction%%$anchor*}"
  after="${instruction#*$anchor}"
  [[ "$before" =~ $reset_re ]] ||
    miss "$skill_md's Resume re-enters the refactor loop without first resetting the worktree, so the transform the killed leaf left uncommitted is carried into the resumed step and into the PR unverified"
  [[ "$instruction" =~ $green_re ]] ||
    miss "$skill_md's Resume never identifies the pending step's green commit as the last commit that changed the ledger, so the files it hands the refactor loop are some other commit's and the tidy-up is aimed at the wrong code"
  [[ "$instruction" =~ refactor: ]] ||
    miss "$skill_md's Resume hands the refactor loop no count of the \`refactor:\` commits already made for the step, so the budget restarts at 0 and an interrupted run can spend it twice over"
  [[ "$after" =~ $verify_re ]] ||
    miss "$skill_md's Resume re-enters the refactor loop but never runs verify-refactor after it, which is the check the interruption skipped in the first place"
}

says_reset_and_reduced_budget() {
  local reset_re="$reset_command"
  local reduced_re='reduc|minus|subtract|net of|what is left|left of|remaining|\$\(\('
  [[ "$instruction" =~ $reset_re ]] ||
    miss "$skill_md's Resume relaunches the refactor leaf without first resetting the worktree, so the transform the killed leaf left half-applied on disk is carried into the relaunched leaf and into the PR unverified"
  [[ "$instruction" =~ veri_refactor_budget ]] ||
    miss "$skill_md's Resume never names VERI_REFACTOR_BUDGET on the pending branch, so the relaunched leaf is asked for the run's whole budget and the interrupted step pays for its tidying twice over"
  [[ "$instruction" =~ $reduced_re ]] ||
    miss "$skill_md's Resume never says the budget the relaunched leaf is given is reduced by the \`refactor:\` commits the step already has, so the count it computes is read and then thrown away"
}

reads_dirty_tree_gate() {
  reads 'asks git status --porcelain before the PR is opened' "$dirty_tree"
}

finish
