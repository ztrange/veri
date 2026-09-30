#!/usr/bin/env bash
# Unit tests for how the conductor drives the refactor-pending mark — like
# skill-event-marks.test.sh and skill-suite-runs.test.sh this suite belongs to no single
# script: its subject is prose, read as text, the way the session that follows it reads it.
# skills/tdd/SKILL.md for the procedure itself, and — the way skill-suite-runs.test.sh reads
# SKILL.md and CLAUDE.md together — this repository's own CLAUDE.md and CONTEXT.md for the
# account of that procedure the next agent is handed before touching any of it.
# Zero-dependency plain-shell asserts, same idiom as skill-event-marks.test.sh.
#
# Why this exists (issue #116): `tick-ledger.sh --refactor-pending`,
# `next-pending-refactor.sh` and `clear-refactor-pending.sh` now exist, but a mark nobody
# writes and nobody clears records nothing. The conductor is prose, so the mark's whole
# lifetime lives in this document: Green's PASS is the only place it is ever written, the
# pin path is the one tick that must NOT write it (a pinned step has no refactor loop to
# wait for, so a mark there would leave the step pending for ever), and verify-refactor's
# PASS is the only place it is ever cleared. Get any one of the three wrong and the ledger
# stops answering the question the mark exists for — "is this ticked step tidied, or only
# green?" — which is the question a resumed conductor asks.
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
#   4. SKILL.md's script reference list — the section a session reads a script's contract
#      out of before it calls it — has an entry for each of the three, saying what it
#      prints (or, for the two that edit the ledger, the mark they write and strip) and
#      which exit codes it can answer with.
#   5. CLAUDE.md's ledger invariant and CONTEXT.md's **Ledger** entry each say that a ticked
#      step also carries the mark until its verify-refactor passes, rather than that the tick
#      alone means the step is done.
#   6. SKILL.md's Resume branch for a pending step resets what the killed leaf left
#      uncommitted and relaunches the refactor leaf with `VERI_REFACTOR_BUDGET` reduced by
#      the `refactor:` commits that step already has.
#   7. SKILL.md passes the step's green commit sha to `verify.sh refactor` at both call
#      sites: the cycle loop's `<green-sha>` and Resume's `$green`.
#   8. SKILL.md's Resume resets the worktree BEFORE it asks `next-pending-refactor.sh`, so a
#      resume that finds no step carrying the mark still discards what a killed leaf left
#      uncommitted (issue #194).
#   9. SKILL.md's Resume captures `git status --porcelain` BEFORE that reset and says the
#      `### ▶️ Resuming` comment names the paths it discarded, so the work a killed leaf left
#      is thrown away loudly rather than silently (issue #194).
#  10. SKILL.md's Draft PR step's refusal names a remedy that applies with a dirty tree, no
#      step pending and none unchecked, and says the run reaches the PR after it, so the
#      combination case 3's gate refuses has a way out rather than a loop (issue #194).
#  11. SKILL.md's Resume says a leaf killed in Red or Green leaves the same stray work a
#      killed refactor leaf does, so the reset cases 8 and 9 pin reads as prescribed rather
#      than as an unexplained extra command (issue #194).
#
# Each half is asked of ONE instruction, the way skill-event-marks.test.sh asks for a mark
# beside the comment it mirrors: the clear and the commit that carries it belong in the
# same instruction as the mirror they precede, because a clear prescribed in some other
# section drifts away from the branch it belongs to the first time either is reworded — and
# a ledger whose mark is cleared on a different path than the one that ends the step is
# exactly the divergence this issue is about.
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

pass=0 fail=0

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

first_record() {
  local line re
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    instruction="$line"
    return 0
  done <<< "$records"
  return 1
}

instruction=""
reads() {
  local what="$1"
  shift
  first_record "$@" && return 0
  problems+=("$skill_md has no instruction that $what — what that branch prescribes could not be read")
  return 1
}

record_name=""
record_of() {
  local where="$1" what="$2"
  shift 2
  record_name="$where's $what"
  first_record "$@" && return 0
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
  planted_dir="$(mktemp -d)"
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

name="$skill_md ticks green with --refactor-pending, pins without it, and clears the mark before mirroring the step done"
problems=()
if records_from instructions \
    "$skill_md has no instructions to read — the mark's lifetime could not be checked"; then
  if reads 'ticks the ledger and commits the code with a `feat:` commit' \
      'tick-ledger\.sh' 'feat:'; then
    says 'tick-ledger\.sh[[:space:]]+--refactor-pending' \
      "$skill_md's green PASS still ticks with plain \`tick-ledger.sh\`, so the step is recorded as done the moment it is green and a run interrupted in its refactor loop resumes with nothing left to do"
  fi

  if reads 'ticks the ledger and commits the pin with a `test: pin` commit' \
      'tick-ledger\.sh' 'test: pin'; then
    denies '--refactor-pending' \
      "$skill_md's pin path ticks with --refactor-pending, but a pinned step runs no refactor loop, so the mark it writes can never be cleared and resume would re-enter a loop that step never had"
  fi

  if reads 'ends the cycle by posting the `### ✅ step done` comment' 'step done'; then
    says_clear_commit_mirror
  fi
fi
report "$name"

name="$skill_md's Resume asks next-pending-refactor.sh before next-unchecked.sh, re-enters the pending step's refactor loop, and reaches the draft PR only when both exit 3"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what a resumed run does could not be checked"; then
  precedes 'next-pending-refactor\.sh' 'next-unchecked\.sh' \
    "$skill_md's Resume never asks next-pending-refactor.sh, so a run interrupted inside a step's refactor loop reads that step's tick as done and walks straight to the PR" \
    "$skill_md's Resume no longer asks next-unchecked.sh, so a resumed run has no next step to continue from" \
    "$skill_md's Resume asks next-unchecked.sh before next-pending-refactor.sh, so it opens the next step's red phase while the previous step's refactor is still unverified"

  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says_reset_reenter_verify
  fi

  if reads 'sends a resumed run to the draft pr' 'draft pr'; then
    says 'next-pending-refactor\.sh' \
      "$skill_md sends a resumed run to the draft PR on next-unchecked.sh alone, so a ledger whose every step is ticked still reaches the PR with the last step's refactor unverified"
    says 'next-unchecked\.sh' \
      "$skill_md sends a resumed run to the draft PR without next-unchecked.sh having exited 3, so a run with steps still to do can reach the PR"
  fi
fi
report "$name"

name="$skill_md's Draft PR step refuses to open the PR while git status --porcelain is non-empty or next-pending-refactor.sh finds a pending step"
problems=()
if records_from draft_pr_instructions \
    "$skill_md has no ### 4. Draft PR section to read — what guards the PR could not be checked"; then
  precedes "$dirty_tree" 'pr-creating `gh api`' \
    "$skill_md's Draft PR step never checks git status --porcelain, so the transform a killed refactor leaf left uncommitted reaches the PR with no verifier having seen it" \
    "$skill_md's Draft PR step no longer opens the PR, so there is nothing for the check to guard" \
    "$skill_md's Draft PR step checks the tree only after the PR-creating gh api call, so the dirty worktree is already up for review by the time anything notices"

  if reads_dirty_tree_gate; then
    says 'next-pending-refactor\.sh' \
      "$skill_md's Draft PR step checks only that the tree is clean, so a ledger whose last step is committed but still marked refactor-pending opens a PR with that step's refactor never verified"
    says 'refuse|do not open|does not open|stop|bail|must not|never' \
      "$skill_md's Draft PR step names the checks but never says they can stop it, so a non-empty status or a pending step is read as information and the PR is opened anyway"
  fi
fi
report "$name"

name="$skill_md's script reference list documents tick-ledger.sh --refactor-pending, next-pending-refactor.sh and clear-refactor-pending.sh, each with what it prints and its exit codes"
problems=()
if records_from scripts_instructions \
    "$skill_md has no ## The scripts section to read — what the reference list documents could not be checked"; then
  reference_list_probes
fi
report "$name"

name="$claude_md's ledger invariant and $context_md's Ledger entry say a ticked step carries the refactor-pending mark until its verify-refactor passes"
problems=()
if records_from claude_records \
    "$claude_md has no records to read — what this repository calls unbreakable about the ledger could not be checked"; then
  if record_of "$claude_md" 'ledger invariant' 'committed ledger' 'source of truth'; then
    says_pending_until_verified
  fi
fi
if records_from context_records \
    "$context_md has no records to read — what this repository means by \"ledger\" could not be checked"; then
  if record_of "$context_md" 'Ledger glossary entry' '^\*\*ledger\*\*:'; then
    says_pending_until_verified
  fi
fi
report "$name"

name="$skill_md's Resume resets the uncommitted work and relaunches the refactor leaf with VERI_REFACTOR_BUDGET reduced by the step's existing refactor: commits"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what budget a relaunched refactor leaf is given could not be checked"; then
  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says_reset_and_reduced_budget
  fi
fi
report "$name"

name="$skill_md passes the step's green commit sha to verify.sh refactor in the cycle loop and in Resume's pending branch"
problems=()
if records_from instructions \
    "$skill_md has no instructions to read — what verify-refactor is handed could not be checked"; then
  if reads 'runs verify.sh refactor in the cycle loop' "$verify_refactor"; then
    says "$verify_refactor [^ ]+ [^ ]+ <green-sha>" \
      "$skill_md's cycle loop runs verify.sh refactor without the step's <green-sha>, so verify-refactor has no range to diff and exits 2"
  fi
fi
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what a resumed verify-refactor is handed could not be checked"; then
  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says "$verify_refactor"' [^ ]+ [^ ]+ "?\$green' \
      "$skill_md's Resume never runs verify.sh refactor with \$green, so the resumed step's verify-refactor is handed no base sha and exits 2"
  fi
fi
report "$name"

name="$skill_md's Resume resets the worktree before it asks next-pending-refactor.sh, so a resume with no step carrying the mark still discards the stray work"
problems=()
if text_from resume_instructions \
  "$skill_md has no ## Resume section to read — whether the reset comes before the ask could not be checked"; then
  if [[ ! "$records_text" =~ next-pending-refactor\.sh ]]; then
    problems+=("$skill_md's Resume never asks next-pending-refactor.sh, so there is no ask for the reset to come before — case 2 says what that ask is for")
  else
    before_ask="${records_text%%next-pending-refactor.sh*}"
    [[ "$before_ask" =~ $reset_command ]] ||
      problems+=("$skill_md's Resume resets the worktree only after asking next-pending-refactor.sh, so a resume where that ask exits 3 continues on top of what a leaf killed in Red or Green left uncommitted, and the Draft PR step then refuses a tree nothing will ever clean")
  fi
fi
report "$name"

name="$skill_md's Resume captures the dirty paths before it resets and names them in the ### ▶️ Resuming comment"
problems=()
if text_from resume_instructions \
  "$skill_md has no ## Resume section to read — whether the reset says what it discarded could not be checked"; then
  if [[ ! "$records_text" =~ $dirty_tree ]]; then
    problems+=("$skill_md's Resume never captures git status --porcelain, so nothing knows what the reset is about to discard and a killed leaf's files vanish unnamed")
  else
    [[ "$records_text" =~ $dirty_tree.*$reset_command ]] ||
      problems+=("$skill_md's Resume captures git status --porcelain only after the reset, where the tree is already clean, so the comment names nothing however faithfully it reports what it captured")
  fi
  if reads 'says the ### ▶️ Resuming comment names the paths the reset discarded' \
      '▶️ resuming' '(path|file)'; then
    says '(discard|threw away|thrown away|throw away|stray|reset)' \
      "$skill_md's Resume mentions paths in the ### ▶️ Resuming comment without saying they are what the reset discarded, so the thread names files without recording that they are gone"
  fi
fi
report "$name"

name="$skill_md's Draft PR step names a remedy for a dirty tree with no step pending and none unchecked, and reaches the PR after it"
problems=()
if records_from draft_pr_instructions \
    "$skill_md has no ### 4. Draft PR section to read — whether its refusal has a remedy could not be checked"; then
  if reads_dirty_tree_gate; then
    says '(no |nothing |none |without a )[^.]{0,40}pending' \
      "$skill_md's Draft PR step refuses a dirty tree but names a remedy only for a step that is pending, so a run whose tree is dirty with nothing pending is sent to a branch that exits 3 and arrives back at the same refusal"
    says 'unchecked' \
      "$skill_md's Draft PR step's refusal never says what happens when no step is unchecked either, which is the combination that loops: the cycle loop has nothing left to run and the gate refuses the same tree for ever"
    says '(come back|comes back|return here|returns here|open the pr|gh pr create)' \
      "$skill_md's Draft PR step's refusal names a remedy without saying the run reaches the PR after it, so a conductor that has cleaned the tree is left with no instruction saying it may now go on"
  fi
fi
report "$name"

name="$skill_md's Resume says a leaf killed in Red or Green leaves the same stray work a killed refactor leaf does"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what it says a resumed worktree may be carrying could not be checked"; then
  if reads 'says what a killed leaf leaves in a resumed worktree' 'killed' '(uncommitted|stray)'; then
    says '[^a-z](red|green)[^.]{0,30}[^a-z](or|and)[^a-z][^.]{0,30}(green|red)[^a-z]' \
      "$skill_md's Resume never names Red and Green together as phases a kill leaves stray work from, so the unconditional reset reads as being about the refactor leaf alone and the next rewording puts it back under the pending branch"
    says '[^a-z](red|green)[^.]{0,30}[^a-z](or|and)[^a-z][^.]{0,30}(green|red)[^a-z][^.]{0,80}refactor' \
      "$skill_md's Resume names Red and Green without saying their killed leaf leaves the same stray work a killed refactor one does, so nothing says the two paths are one kill mode and a reader is left thinking only the pending step's tree is dirty"
  fi
fi
report "$name"

name="case 4's removal-verb probe reports a problem naming the clear-refactor-pending.sh entry when only the filename that opens it supplies a removal verb"
probes_against_planted removal_verb_probe \
    "the planted entry's ## The scripts section could not be read, so the removal-verb probe was never asked" <<'PLANTED'
## The scripts (this skill's `scripts/` directory)

- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of
  `tick-ledger.sh --refactor-pending`: the first ticked step matching the substring no longer
  carries the ` ⟂ refactor pending` mark afterwards, once that step's refactor has been
  verified. Nothing on stdout. **Exit 0** when it did its work; **exit 3** when no ticked step
  both matched and carried the mark.
PLANTED
if [[ "${#probe_problems[@]}" -eq 0 ]]; then
  problems+=("the removal-verb probe reported nothing against an entry whose only removal verb is the \`clear-refactor-pending.sh\` filename that opens it, so the probe is satisfied by its own subject's name and stays true however the entry's prose is reworded")
elif [[ ! "${probe_problems[*]}" =~ clear-refactor-pending\.sh ]]; then
  problems+=("the removal-verb probe reported a problem that never names the clear-refactor-pending.sh entry, so a run it turns red does not say which of the list's entries to fix")
fi
report "$name"

name="$skill_md's clear-refactor-pending.sh entry names a removal verb in its own prose, so case 4's removal-verb probe reports nothing against the document as committed"
problems=()
if records_from scripts_instructions \
    "$skill_md has no ## The scripts section to read — whether the removal-verb probe stays green against it could not be checked"; then
  removal_verb_probe
fi
probe_problems=("${problems[@]}")
problems=()
if [[ "${#probe_problems[@]}" -ne 0 ]]; then
  problems+=("the removal-verb probe reported a problem against $skill_md's own entry for clear-refactor-pending.sh, whose prose does name a verb meaning to remove, so the strip that lets the probe read that prose is taking the verb with it and a true entry is turned red: ${probe_problems[*]}")
fi
report "$name"

name="case 4's other nine probes each report a problem, under the entry they were asked of, against reference-list entries that carry none of what they ask for"
probes_against_planted reference_list_probes \
    "the planted entries' ## The scripts section could not be read, so case 4's probes were never asked" <<'PLANTED'
## The scripts (this skill's `scripts/` directory)

- `$S/tick-ledger.sh .tdd/issue-<n>.md '<substring>'` — the ledger is rewritten so the first
  unchecked step matching the substring is ticked.
- `$S/next-pending-refactor.sh .tdd/issue-<n>.md` — reads the ledger and answers about the
  first ticked step whose tidying is still owed.
- `$S/clear-refactor-pending.sh .tdd/issue-<n>.md '<substring>'` — the counterpart of the
  tick above, run once that step's refactor has been verified. Nothing on stdout.
PLANTED
for want in \
  "tick-ledger.sh|never mentions --refactor-pending" \
  "tick-ledger.sh|never spells the mark the flag appends" \
  "tick-ledger.sh|never names exit 3, so a green commit" \
  "next-pending-refactor.sh|never says it prints the pending step" \
  "next-pending-refactor.sh|never names exit 0" \
  "next-pending-refactor.sh|never names exit 3, so the one code" \
  "clear-refactor-pending.sh|never spells the mark it removes" \
  "clear-refactor-pending.sh|never names exit 0" \
  "clear-refactor-pending.sh|never names exit 3, so the one code"; do
  want_entry="${want%%|*}"
  want_fact="${want#*|}"
  found=""
  for reported in "${probe_problems[@]}"; do
    if [[ "$reported" == *"entry for $want_entry"* && "$reported" == *"$want_fact"* ]]; then
      found=yes
    fi
  done
  if [[ -z "$found" ]]; then
    problems+=("no probe reported that $skill_md's entry for $want_entry \"$want_fact\", though the planted entry carries none of it — so that probe is answered by something other than the prose it asks about, the way the removal-verb one was answered by the filename, and it stays true however the entry is reworded")
  fi
done
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
