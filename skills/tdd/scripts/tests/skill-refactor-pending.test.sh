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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
# The document twice, the way skill-suite-runs.test.sh names its two: the path as every
# problem message spells it, and the same path resolved for the readers below to open. One
# constant for each, so a message can never name a file the readers did not read — and so
# the resolving happens once rather than at each reader, which is the same reason
# `records_of` and `section_of` are each spelled once.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
# The repository's own two documents, each named the same way and for the same reason. They
# are where an agent finds out what the ledger is (CONTEXT.md's glossary) and what may never
# be broken about it (CLAUDE.md's invariants), which is why the mark has to be in them and
# why a message about one must never spell the other's path.
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
context_md="CONTEXT.md"
context_path="$ROOT/$context_md"

# The mark itself, spelled once. Four probes ask for this exact string, and they span three
# documents: two in case 4 — SKILL.md's reference-list entry for the flag that writes it, and
# the entry for the script that strips it — and one in case 5, asked in turn of CLAUDE.md's
# invariant and CONTEXT.md's glossary entry. That they all ask for the *same* string is the
# claim, not an incidental repetition: the fact any one of them fails with is that the
# procedure and the account of it can be reworded apart without either noticing, and
# independent literals here would let this suite drift exactly that way itself.
mark='⟂ refactor pending'

# The call case 7 is about, spelled once for the same reason: `verify.sh refactor`, with the
# optional `--step '<STEP>'` flag the conductor now types between the script and its phase
# (#223). Three probes ask for that shape — the read that finds the cycle loop's call, and
# the two that ask what each call site hands it — and a third independent spelling would let
# one of them go on matching a call SKILL.md no longer makes.
#
# Either script's name opens it, because since #426 the cycle loop's launch reaches the verify
# verb by exec'ing it through `run-verdict.sh` — the launcher takes verify.sh's own arguments
# in verify.sh's own order — while Resume's prose still names `verify.sh` itself. The sha is
# what this case is about, and it sits in the same slot behind either name.
verify_refactor='(verify|run-verdict)\.sh (--step [^ ]+ )?(--fast-cmd [^ ]+ )?refactor'

# The command family that counts as "the worktree was reset", spelled once for the same
# reason. Two probes ask for it of two different slices — case 6's, of the instruction that
# relaunches the refactor leaf, and case 8's, of everything Resume says before it asks
# `next-pending-refactor.sh` — and which command discards the work is not either criterion's
# claim; that something does, at that point, is. Independent spellings would let one probe go
# on accepting a form the other had stopped accepting, and a probe that no longer matches the
# document fails loudly only when it is the one asked.
#
# `says_reset_reenter_verify` keeps its own, deliberately: it additionally accepts `git
# stash`, which is a different claim about what the document may prescribe, not a drifted
# copy of this one.
reset_command='git (reset|checkout|restore|clean)'

# The question "is the tree dirty?", spelled once for the same reason the two constants above
# are. Three probes ask for this exact command across two sections: case 3's, of the Draft PR
# step that refuses to open a PR while it answers non-empty, and case 9's two, of the Resume
# that captures its answer before throwing the tree away. The command is the same question in
# both, and a document that started asking it another way has to fail every probe at once —
# independent literals would let one of them go on matching a check SKILL.md no longer makes.
dirty_tree='git status --porcelain'

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which end of the mark's lifetime broke rather than just that it did.
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

# records_of — the lines on stdin as records: the document's numbered steps, bullets and
# paragraphs, one per line and lowercased. A record runs from a `N. ` or a `- ` (indented or
# not) in column one, or from the first line after a blank, up to the next such line or the
# next blank; a fenced command block inside a bullet is part of that bullet's record, which
# is what lets a probe ask whether the branch that says "PASS" is the one that runs the
# command.
#
# Runs of whitespace collapse to one space as the record is closed, so a sentence wrapped
# across two lines still reads as one. Case is folded away last, because the sentences are
# the writer's.
#
# Every reader below ends in it — `instructions`, the two that read this repository's own
# documents, and the `section_of` slice the three scoped readers share — the way
# skill-suite-runs.test.sh's two readers both end in `plain`, so "what a record is" is spelled
# once. A second spelling would not fail — it would quietly answer a probe with records built
# by a grammar the other readers have since outgrown.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

# instructions — the whole document as records.
instructions() {
  records_of < "$skill_path"
}

# claude_records / context_records — the repository's own two documents as records, whole.
# Unscoped, unlike the three SKILL.md readers below: the case that reads them finds its record
# by what the record says — the invariant that calls the ledger the source of truth, the
# glossary entry headed `**Ledger**:` — and no other record in either file carries those
# anchors, so there is no second branch an unscoped read could answer with.
claude_records() {
  records_of < "$claude_path"
}
context_records() {
  records_of < "$context_path"
}

# section_of <heading> <closers-re> — the records of one section of the document: the lines
# after the one that is exactly <heading>, up to the next line matching <closers-re>, which
# is what says which headings end it. Both scoped readers below are this same slice, so it
# is spelled once here and only the two arguments differ — the same reason `records_of`
# above is one function rather than one per reader.
section_of() {
  awk -v heading="$1" -v closers="$2" \
    '$0 ~ closers { inside = ($0 == heading); next } inside' "$skill_path" | records_of
}

# resume_instructions — the records of the `## Resume` section. Scoped because the document
# asks `next-unchecked.sh` twice — once at the top of the cycle loop, once on the resume path
# — and it is only the second that this issue is about, so an unscoped read would answer with
# the wrong branch and, worse, let a Resume that says nothing at all pass on the cycle loop's
# wording. `### ` sub-headings survive the slice: the closers want "## " with the space.
resume_instructions() {
  section_of '## Resume' '^## '
}

# draft_pr_instructions — the records of the `### 4. Draft PR` section, which a heading of
# either level ends. Scoped for the same reason `resume_instructions` is — the document
# pushes a branch and names the PR on more than one path (Bailing pushes too; Resume points
# at this step) — and this criterion is about the step that does the pushing, not about the
# prose elsewhere that sends a run to it.
draft_pr_instructions() {
  section_of '### 4. Draft PR' '^## |^### '
}

# scripts_instructions — the records of the `## The scripts (this skill's `scripts/`
# directory)` section: the reference list, one bullet per script, that a session reads a
# script's contract out of before it calls it. Scoped for the same reason the two readers
# above are, and more sharply: every one of these scripts is *named* again further down, at
# the point the procedure runs it, and a call site is not documentation — it says what to
# run, never what comes back. An unscoped read would answer this criterion with those call
# sites and pass a reference list that never gained an entry at all.
scripts_instructions() {
  section_of '## The scripts (this skill'\''s `scripts/` directory)' '^## '
}

# records_from <reader> <nothing-to-read fact> — what one of the readers above yields, into
# the global `records`, and a zero return; or, when it yields nothing at all, one problem
# naming <fact> and a non-zero return, so the case that follows is skipped rather than run
# against an empty document.
#
# Fail closed, for the reason `reads` below does: an empty slice means the heading was
# renamed or its section emptied, and then not one probe of that case was tested — which must
# not read as a pass. All three cases open with it, so that rule is spelled once here instead
# of as three guards that could each drift from the others.
records_from() {
  records="$("$1")"
  [[ -n "$records" ]] && return 0
  problems+=("$2")
  return 1
}

# text_from <reader> <nothing-to-read fact> — `records_from`, and then the records it yielded
# as ONE string in the global `records_text`. The two cases that read order as *text* order —
# the reset before the ask, and the capture before the reset — each need exactly this pair, and
# each fails closed the same way when the section is unreadable, so the pair is spelled once
# here rather than once per case. Two copies would be free to flatten differently, and a probe
# reading a differently flattened section answers a subtly different question of the same
# document.
records_text=""
text_from() {
  records_from "$1" "$2" || return 1
  records_text="$(printf '%s' "$records" | tr '\n' ' ')"
}

# ordinal <regex> — the 1-based position, within the global `records`, of the first
# instruction matching <regex>, or 0 when none does. Position is what turns two independent
# "is it there?" probes into the one question a criterion about order asks: which of the two
# the document does first.
ordinal() {
  local n=0 line
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$line" =~ $1 ]]; then printf '%s\n' "$n"; return 0; fi
  done <<< "$records"
  printf '0\n'
}

# precedes <first-re> <second-re> <no-first> <no-second> <out-of-order> — one problem when the
# global `records` do not do <first-re> before <second-re>, phrased as whichever of the three
# things went wrong: the first instruction is gone, the second is, or they have swapped.
#
# Two of the criteria below are this same claim — Resume asks `next-pending-refactor.sh`
# before `next-unchecked.sh`, and the Draft PR step checks the tree before it pushes — and
# both fail those same three ways, so the branching is spelled once here and only the three
# sentences differ at the call.
#
# The two absences are reported before the order is, and as their own problems, because a
# missing instruction has ordinal 0: compared as a position it reads as "comes first", which
# would let a document that dropped the check altogether pass the ordering probe.
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

# first_record <anchor-regex>… — the search both readers below are: the first record of the
# global `records` matching every <anchor-regex>, into the global `instruction` and a zero
# return; a non-zero return and `instruction` untouched when none does. It appends no problem,
# because which sentence a miss is worth is the one thing its two callers do not share.
#
# Spelled once here for the same reason `records_of` is: "which record answers this probe" is a
# grammar, and two copies of it are free to drift — a `continue 2` that turned into a `break`
# in one of them would quietly answer with a record that matched only the first anchor.
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

# reads <what it is> <anchor-regex>… — `first_record`, for SKILL.md: the instruction it finds,
# or one problem naming <what it is> and a non-zero return. Reads as the sentence it fails
# with: `reads 'ticks the ledger'` asks for the instruction *that* ticks the ledger, and
# `says`/`denies` then probe what this left behind.
#
# Fail closed: a branch that has been reworded away is reported as unreadable rather than
# probed as an empty string, which would let "the instruction is gone" pass as "the
# instruction is right".
instruction=""
reads() {
  local what="$1"
  shift
  first_record "$@" && return 0
  problems+=("$skill_md has no instruction that $what — what that branch prescribes could not be read")
  return 1
}

# record_of <document> <what it is> <anchor-regex>… — `reads`, for the repository's own two
# documents: the same `first_record` search, but a problem naming <document> and <what it is>,
# and a non-zero return so the probes that follow are skipped rather than run against a stale
# read.
#
# A second wrapper rather than a flag on `reads`, because the sentence is the whole difference:
# SKILL.md prescribes, so a record missing from it is a branch that no longer says what to do,
# whereas these two describe, and a record missing from them is a fact this repository no
# longer writes down. Naming the document is also the point — there are two of them here, and a
# message that spelled SKILL.md's path would send the fix to a third file that is already
# right.
#
# Fail closed for the same reason `reads` does: a renamed heading or a deleted entry has to
# read as unreadable, not as an empty string that every probe then passes on.
#
# The document and the thing it owes are left composed in `$record_name`, beside the
# `$instruction` the read landed in, so `says_pending_until_verified` below can name what it is
# probing without being handed that name a second time — the shape `reads_entry` and
# `entry_says` already have, where the reader leaves what it read and the probes ask about it.
# Spelled at the call instead, the name would be a second literal beside the one the miss above
# reports under, free to drift into probing one record under another's name.
record_name=""
record_of() {
  local where="$1" what="$2"
  shift 2
  record_name="$where's $what"
  first_record "$@" && return 0
  problems+=("$where has no $what — what it records about a ticked step could not be read")
  return 1
}

# says <regex> <fact> / denies <regex> <fact> — one thing the `$instruction` just read must
# carry, or must not, written as the regex of any wording that would carry it; `fact` names
# it once when the probe is wrong.
says() {
  [[ "$instruction" =~ $1 ]] || problems+=("$2")
}
denies() {
  if [[ "$instruction" =~ $1 ]]; then problems+=("$2"); fi
}

# reads_entry <script> — the reference-list entry *for* <script>, into `$instruction`: the
# record that opens `- \`$S/<script>`, rather than any record that merely mentions it. That is
# the same distinction `scripts_instructions` draws against the call sites, one level down —
# within the list itself, a passing mention inside a neighbouring entry would otherwise be
# read as the entry, and a script that never gained one would pass on someone else's bullet.
#
# All three entries of the case below are read this way, and all three would fail that way
# without it, so the anchor is spelled once here and only the script's name differs at the
# three calls. The name's dots are escaped on the way in, so the regex a call implies matches
# the script it named and not every name of the same shape.
#
# The name is also left in `$entry_script`, beside the `$instruction` the read landed in, so
# `entry_says` below can name the entry it is probing without being handed that name a second
# time — the shape `reads` and `says` already have, where the reader leaves what it read and
# the probes ask about it. Handing it over twice would not fail; it would let a probe report
# its problem under the name of an entry it never read.
entry_script=""
reads_entry() {
  local escaped="${1//./\\.}"
  entry_script="$1"
  reads "documents $1 in the script reference list" "^- .\\\$s/$escaped"
}

# entry_says <regex> <fact> — `says`, for the entry `reads_entry` last read: one problem
# naming the document and that entry's script, then <fact>, which is written as the sentence
# that follows the name ("never names exit 3, so …").
#
# Every probe of case 4 is this shape — eight of them, all reporting against whichever entry
# the reader landed in — so "which entry this is about" is spelled once here and each call
# carries only the thing that entry owes. Spelled at the call instead, the script's name
# would be a second literal beside the one `reads_entry` matched on, free to drift into
# naming an entry the probe never read.
entry_says() {
  says "$1" "$skill_md's entry for $entry_script $2"
}

# says_exit_codes — the two codes a reference-list entry for either of the mark's two new
# scripts must name: 0, the answer, and 3, the *nothing to do* code this repository reserves
# for it. Both scripts answer with the same pair and both fail the same way without it — the
# conductor branches on the code, so a code nobody wrote down is a branch the session invents
# — which is why the pair is spelled once here and the two calls are identical. Asked of the
# entry `reads_entry` last read, like every other probe in this suite. `exits?` rather than
# `exit`, because the list writes it both ways.
says_exit_codes() {
  entry_says 'exits? 0' \
    "never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty"
  entry_says 'exits? 3' \
    "never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken"
}

# says_pending_until_verified — the two things each of the two repository documents owes about
# a ticked step: the mark it wears, spelled, and the verification that is the only thing that
# takes the mark off again. Both records owe the same pair and both mislead the same way
# without it, so the pair is spelled once here and the two calls are identical. Asked of the
# `$instruction` `record_of` last read and reported under the `$record_name` it left, the way
# every other probe in this suite is asked of what its reader left.
says_pending_until_verified() {
  says "$mark" \
    "$record_name never spells the \`$mark\` mark, so this repository's own account of the ledger still says a tick means the step is finished, and the next agent to read it takes the mark back out as noise"
  says 'verify-refactor' \
    "$record_name records the mark without naming verify-refactor, so nothing says what clears it and a ticked step's mark reads as something the ledger wears for ever"
}

# miss <fact> — one problem of the ordered probe below: <fact>, then the instruction it was
# read from, clipped, so the fix is an edit to a line already in front of you. Every miss
# quotes it, which is why the quoting lives here rather than at each of the three.
miss() {
  problems+=("$1: $(printf '%.130s' "$instruction")")
}

# says_clear_commit_mirror — the three things the `$instruction` just read must prescribe,
# and the order they must come in: clear the mark, commit the cleared ledger, and only then
# mirror the step to the issue. The order is the whole claim here, which is why this is not
# three `says` calls: each probe reads only what the one before it left — `rest` — and the
# first miss returns, because "and after that?" has no answer once the order is already
# broken.
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
  # Past the commit: what is left is what the document does once the cleared ledger is safe
  # on disk, and the mirror has to be in there rather than before it.
  rest="${rest#*commit}"
  [[ "$rest" =~ tick-issue-criterion\.sh ]] ||
    miss "$skill_md mirrors the step to the issue before the cleared ledger is committed, so a run killed in that window has an issue saying done over a ledger still saying pending"
}

# says_reset_reenter_verify — the four things the `$instruction` just read must prescribe for
# a step that comes back pending: throw away what the killed leaf left on disk, re-enter the
# refactor loop with its two inputs (the files of the step's green commit, and how many
# transforms already landed), and verify-refactor after it. `$anchor` is what the order is
# read against — the reset has to come before it and the verification after it — so its
# absence returns rather than probing two halves of a string that has no middle.
#
# It is spelled once, and used three times: to establish it is there, and to cut the
# instruction either side of it. A second spelling that drifted from the first would not
# fail — a `%%`/`#` whose pattern misses yields the whole string — it would silently make
# both halves the whole instruction, and the two ordered probes would then pass on any
# wording that merely mentions a reset and a verification anywhere.
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

# says_reset_and_reduced_budget — the three things the `$instruction` just read must prescribe
# for the leaf a resume relaunches: throw away the uncommitted work first, then launch with
# `VERI_REFACTOR_BUDGET`, and with that number REDUCED by the transforms the interrupted run
# already committed.
#
# The budget is the half that changed. While a leaf ran per transform, the count went to
# `refactor-budget.sh <count>` and the loop simply stopped early. One leaf per step is asked
# for a number up front and applies transforms until it is spent, so a resume that relaunches
# it on the ambient `VERI_REFACTOR_BUDGET` hands it the whole budget a second time and the
# step pays twice over for its tidying — which is the cost axis this issue exists to bound.
#
# The reset is probed here too, and deliberately: the reduced budget is an instruction about
# what to relaunch with, and it is only safe to relaunch anything once the half-applied
# transform on disk is gone. The two are the one sentence this criterion is.
#
# Each probe accepts any wording that carries its fact. The reduction's alternation covers the
# prose forms and the arithmetic one, but never a bare `--count` flag: computing the count is
# what the document already does, and a probe answered by that would pass a resume that reads
# the number and then hands the leaf the full budget anyway.
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

# reads_dirty_tree_gate — the Draft PR step's one record that asks `git status --porcelain`,
# into `$instruction`, or one problem and a non-zero return the way `reads` itself does. Cases
# 3 and 10 are the two halves of that one record — what it refuses, and what it offers the run
# instead — so which record answers them is the one thing they must not be free to spell
# apart. Two `reads` calls would still find the same sub-step today and stop doing so the day
# the section grows a second that asks the same question, and the two halves would then be
# asserted of two different records with nothing saying so.

reads_dirty_tree_gate() {
  reads 'asks git status --porcelain before the PR is opened' "$dirty_tree"
}

# 1. One criterion — the mark is written at exactly one tick, withheld at the other, and
#    cleared where the step ends — and so one case. The three probes are one wiring: a mark
#    written and never cleared stalls every resumed run in a refactor loop, and a mark
#    cleared but never written leaves resume blind again, so the fix to any of them is one
#    edit to one document.
name="$skill_md ticks green with --refactor-pending, pins without it, and clears the mark before mirroring the step done"
problems=()
if records_from instructions \
    "$skill_md has no instructions to read — the mark's lifetime could not be checked"; then
  # Green's PASS — the only tick that writes the mark, because it is the only one a
  # refactor loop follows.
  if reads 'ticks the ledger and commits the code with a `feat:` commit' \
      'tick-ledger\.sh' 'feat:'; then
    says 'tick-ledger\.sh[[:space:]]+--refactor-pending' \
      "$skill_md's green PASS still ticks with plain \`tick-ledger.sh\`, so the step is recorded as done the moment it is green and a run interrupted in its refactor loop resumes with nothing left to do"
  fi

  # The pin path — a step with no production code has no refactor loop, so a mark written
  # here would never be cleared.
  if reads 'ticks the ledger and commits the pin with a `test: pin` commit' \
      'tick-ledger\.sh' 'test: pin'; then
    denies '--refactor-pending' \
      "$skill_md's pin path ticks with --refactor-pending, but a pinned step runs no refactor loop, so the mark it writes can never be cleared and resume would re-enter a loop that step never had"
  fi

  # verify-refactor's PASS — the only place the mark is cleared, and the clearing has to
  # land in a commit before the step is mirrored as done.
  if reads 'ends the cycle by posting the `### ✅ step done` comment' 'step done'; then
    says_clear_commit_mirror
  fi
fi
report "$name"

# 2. One criterion — the mark's reader. Resume is the whole reason the mark is written, so
#    asking for it is only half the fix: the order of the two asks decides whether a pending
#    step is picked up at all, and what the pending branch prescribes decides whether the
#    step is actually finished or merely re-entered. Both are one case, because a Resume that
#    asks `next-pending-refactor.sh` and then does the wrong thing with the answer leaves the
#    run exactly where #116 found it — a PR opened over an unverified refactor.
name="$skill_md's Resume asks next-pending-refactor.sh before next-unchecked.sh, re-enters the pending step's refactor loop, and reaches the draft PR only when both exit 3"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what a resumed run does could not be checked"; then
  # The order of the two asks. A resume that asks for an unchecked step first starts the
  # next step's red phase with the previous step's refactor still unverified — which is the
  # bug, one step later.
  precedes 'next-pending-refactor\.sh' 'next-unchecked\.sh' \
    "$skill_md's Resume never asks next-pending-refactor.sh, so a run interrupted inside a step's refactor loop reads that step's tick as done and walks straight to the PR" \
    "$skill_md's Resume no longer asks next-unchecked.sh, so a resumed run has no next step to continue from" \
    "$skill_md's Resume asks next-unchecked.sh before next-pending-refactor.sh, so it opens the next step's red phase while the previous step's refactor is still unverified"

  # The pending branch — what the resumed conductor does with a step that comes back green
  # but not tidied.
  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says_reset_reenter_verify
  fi

  # The exit — the draft PR is where the interrupted run wrongly went, so it must now be
  # behind both scripts having nothing left to hand over.
  if reads 'sends a resumed run to the draft pr' 'draft pr'; then
    says 'next-pending-refactor\.sh' \
      "$skill_md sends a resumed run to the draft PR on next-unchecked.sh alone, so a ledger whose every step is ticked still reaches the PR with the last step's refactor unverified"
    says 'next-unchecked\.sh' \
      "$skill_md sends a resumed run to the draft PR without next-unchecked.sh having exited 3, so a run with steps still to do can reach the PR"
  fi
fi
report "$name"

# 3. One criterion — the gate on the way out, and so one case. Resume's last sub-step already
#    says a resumed run reaches the PR only when both scripts exit 3, but that is prose on one
#    path *into* this step; the cycle loop walks into it too, and what #116 actually found was
#    a worktree carrying a killed leaf's uncommitted transform. So the refusal has to live
#    where the handover is: the Draft PR step asks both questions itself — is the tree clean,
#    is any step still only green — and stops before `gh pr create` if either says otherwise.
#    The anchor is that command rather than `git push` since #191: the branch reaches the
#    remote after every green commit, so what this step still decides is whether a human is
#    asked to look at it.
name="$skill_md's Draft PR step refuses to open the PR while git status --porcelain is non-empty or next-pending-refactor.sh finds a pending step"
problems=()
if records_from draft_pr_instructions \
    "$skill_md has no ### 4. Draft PR section to read — what guards the PR could not be checked"; then
  # The gate comes before the PR is opened, or it is not a gate: a check made once a human
  # has been asked to look cannot refuse anything.
  precedes "$dirty_tree" 'gh pr create' \
    "$skill_md's Draft PR step never checks git status --porcelain, so the transform a killed refactor leaf left uncommitted reaches the PR with no verifier having seen it" \
    "$skill_md's Draft PR step no longer opens the PR, so there is nothing for the check to guard" \
    "$skill_md's Draft PR step checks the tree only after gh pr create, so the dirty worktree is already up for review by the time anything notices"

  # What that gate asks, and what it does with the answer. Both conditions belong to the one
  # instruction: a run stopped here is stopped for the same reason either way — the PR would
  # otherwise carry work no verifier has passed.
  if reads_dirty_tree_gate; then
    says 'next-pending-refactor\.sh' \
      "$skill_md's Draft PR step checks only that the tree is clean, so a ledger whose last step is committed but still marked refactor-pending opens a PR with that step's refactor never verified"
    says 'refuse|do not open|does not open|stop|bail|must not|never' \
      "$skill_md's Draft PR step names the checks but never says they can stop it, so a non-empty status or a pending step is read as information and the PR is opened anyway"
  fi
fi
report "$name"

# 4. One criterion — the three scripts the mark's lifetime runs through are documented where
#    a session goes to look a script up, and so one case. Cases 1–3 pin the *call sites*:
#    which branch runs which script. A call site says what to run and never what comes back,
#    and all three of these are branched on — `next-pending-refactor.sh` exiting 3 is what
#    sends a resumed run to the PR, `clear-refactor-pending.sh` exiting 3 says the step it
#    was told to clear is not in the ledger, `tick-ledger.sh` exiting 3 says the green commit
#    ticked nothing. So an entry that omits a code is worse than a missing entry: a missing
#    one is noticed, whereas a half-written one has the session invent a meaning for the code
#    it meets. One case, because the three entries are one list and any fix to them is one
#    edit to it.
name="$skill_md's script reference list documents tick-ledger.sh --refactor-pending, next-pending-refactor.sh and clear-refactor-pending.sh, each with what it prints and its exit codes"
problems=()
if records_from scripts_instructions \
    "$skill_md has no ## The scripts section to read — what the reference list documents could not be checked"; then
  # tick-ledger.sh — the writer. Its entry already documents the plain tick, so what the flag
  # owes the list is the second thing that one write does: the flag's own name, the mark it
  # appends (spelled, because that literal is what the reader matches on), and the code a
  # ledger with no matching step answers with either way.
  if reads_entry tick-ledger.sh; then
    entry_says '--refactor-pending' \
      "never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick"
    entry_says "$mark" \
      "never spells the mark the flag appends, so nothing connects that write to the \`$mark\` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing"
    entry_says 'exits? 3' \
      "never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick"
  fi

  # next-pending-refactor.sh — the reader, and the only one of the three whose answer is on
  # stdout, so its entry owes what that answer is as well as the two codes.
  if reads_entry next-pending-refactor.sh; then
    entry_says 'prints?[^.]*step' \
      "never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on"
    says_exit_codes
  fi

  # clear-refactor-pending.sh — the eraser. Nothing on stdout, so what its entry owes instead
  # is which mark it takes off, and that it does so in the ledger itself.
  if reads_entry clear-refactor-pending.sh; then
    entry_says "$mark" \
      "never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark"
    entry_says 'strip|remove|drop|clear|delete' \
      "never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name"
    says_exit_codes
  fi
fi
report "$name"

# 5. One criterion — the two documents that explain this repository to whoever touches it next
#    record the mark too — and so one case. Cases 1–4 pin the procedure; this one pins the
#    account of it. As they stand, CLAUDE.md's invariant says a ticked step is done ("ticked
#    atomically with each step's green commit", full stop) and CONTEXT.md defines the ledger as
#    the source of truth for which steps are done: read together they assert exactly the thing
#    #116 found to be false — that a tick means tidied. Prose that contradicts the procedure is
#    worse than prose that says nothing, because it is the account a human trusts, and an agent
#    who re-derives the old rule from it deletes the mark as a stray character. One case,
#    because it is one fact owed by two records and any fix to it is one edit to each.
name="$claude_md's ledger invariant and $context_md's Ledger entry say a ticked step carries the refactor-pending mark until its verify-refactor passes"
problems=()
if records_from claude_records \
    "$claude_md has no records to read — what this repository calls unbreakable about the ledger could not be checked"; then
  # The invariant, found by the claim it makes rather than by the heading it sits under: it is
  # the one record that calls the committed ledger the source of truth.
  if record_of "$claude_md" 'ledger invariant' 'committed ledger' 'source of truth'; then
    says_pending_until_verified
  fi
fi
if records_from context_records \
    "$context_md has no records to read — what this repository means by \"ledger\" could not be checked"; then
  # The glossary entry, found by its own heading line, which opens the record: a bare `ledger`
  # anchor would match the entries around it that use the word in passing.
  if record_of "$context_md" 'Ledger glossary entry' '^\*\*ledger\*\*:'; then
    says_pending_until_verified
  fi
fi
report "$name"

# 6. One criterion — what a resume hands the leaf it relaunches — and so one case. Case 2
#    pins that the pending step is picked up, reset and re-entered at all; this one pins the
#    number the relaunch carries. They are separate criteria because the budget only became a
#    number the leaf is handed when one leaf started applying the whole step's transforms
#    (#150): before that the conductor asked `refactor-budget.sh <count>` before each leaf
#    and simply stopped the loop early, so a resume needed only to pass the count along. Now
#    a resume that relaunches on the ambient VERI_REFACTOR_BUDGET gives an interrupted step
#    the full budget a second time — the transforms it already committed cost nothing against
#    it — and the one thing the cost axis is there to bound goes unbounded exactly on the
#    path where a step has already spent some of it.
name="$skill_md's Resume resets the uncommitted work and relaunches the refactor leaf with VERI_REFACTOR_BUDGET reduced by the step's existing refactor: commits"
problems=()
if records_from resume_instructions \
    "$skill_md has no ## Resume section to read — what budget a relaunched refactor leaf is given could not be checked"; then
  if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
    says_reset_and_reduced_budget
  fi
fi
report "$name"

# 7. One criterion — the base sha verify-refactor is handed, at both places the conductor runs
#    it — and so one case. `verify.sh refactor` now takes the step's green commit as its 4th
#    argument (#151) and exits 2 without one, so a call site that omits it is not a weaker
#    check but no verdict at all. There are two: the cycle loop's, which names it
#    `<green-sha>`, and Resume sub-step 2's, which has already bound that same commit to
#    `$green`. Both are one wiring, so both are one case.
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

# 8. One criterion — the reset is unconditional — and so one case. Case 2 pins the reset that
#    happens *inside* the pending branch, which is the only path that has one: a resume whose
#    `next-pending-refactor.sh` exits 3 walks to sub-step 3 over whatever a leaf killed in Red
#    or Green left on disk, and nothing throws it away. That is the same stray work by the
#    same kill mode — a usage limit takes the conductor and every leaf together, at whatever
#    point the run had reached — so the reset belongs before the ask rather than under one of
#    its two answers (issue #194).
#
#    Read as text order over the whole section rather than as record positions, because the
#    fix may leave the reset in sub-step 2 ahead of the ask or lift it into a sub-step of its
#    own, and both are the same instruction: whatever a session reads before it runs the ask
#    is what it does first. `ordinal`/`precedes` cannot answer that — both strings sit in one
#    record today, which ties their positions and would pass the document exactly as it is.
name="$skill_md's Resume resets the worktree before it asks next-pending-refactor.sh, so a resume with no step carrying the mark still discards the stray work"
problems=()
# `text_from` opens this case as `records_from` opens the others, so the fail-closed rule — an
# empty slice means the heading moved, and then no probe below ran at all — stays spelled in the
# one place, rather than as a guard here that could drift from it. What this case needs that
# those do not is the section's records as ONE string: text order is what it reads, and the
# reset it reads for is `$reset_command`, the family case 6 asks of its own slice.
if text_from resume_instructions \
  "$skill_md has no ## Resume section to read — whether the reset comes before the ask could not be checked"; then
  if [[ ! "$records_text" =~ next-pending-refactor\.sh ]]; then
    problems+=("$skill_md's Resume never asks next-pending-refactor.sh, so there is no ask for the reset to come before — case 2 says what that ask is for")
  else
    # Everything the section says before the first mention of the ask. A reset in there runs
    # on both of the ask's answers; a reset only after it runs on one.
    before_ask="${records_text%%next-pending-refactor.sh*}"
    [[ "$before_ask" =~ $reset_command ]] ||
      problems+=("$skill_md's Resume resets the worktree only after asking next-pending-refactor.sh, so a resume where that ask exits 3 continues on top of what a leaf killed in Red or Green left uncommitted, and the Draft PR step then refuses a tree nothing will ever clean")
  fi
fi
report "$name"

# 9. One criterion — what the reset tells the thread it threw away — and so one case. Case 8
#    pins that the reset runs before the ask, on every resume; this one pins that it is not
#    silent. A killed leaf's stray work is real work — #194 records a 235-line untracked test
#    file left by a Red leaf a usage limit killed — and `git reset --hard` destroys it without
#    a word. The content is not preserved (decided 2026-09-16); naming the paths is the whole
#    requirement, and it has two halves that only work together: the capture has to happen
#    *before* the reset, because afterwards `git status --porcelain` has nothing left to
#    report, and the names it captured have to reach the `### ▶️ Resuming` comment, which is
#    the one thing a human reads about a resume. Either half alone leaves the same silence.
#
#    Read as text order over the whole section, for the reason case 8 is: the capture and the
#    reset will sit in one record — a bullet and the fenced block under it are one record here
#    — so `ordinal` cannot tell which the session runs first, while the order of the two
#    strings in what it reads is exactly that.
name="$skill_md's Resume captures the dirty paths before it resets and names them in the ### ▶️ Resuming comment"
problems=()
if text_from resume_instructions \
  "$skill_md has no ## Resume section to read — whether the reset says what it discarded could not be checked"; then
  if [[ ! "$records_text" =~ $dirty_tree ]]; then
    problems+=("$skill_md's Resume never captures git status --porcelain, so nothing knows what the reset is about to discard and a killed leaf's files vanish unnamed")
  else
    # A capture followed, later in the same text, by a reset. Greedy or not, the match exists
    # only if some capture precedes some reset — which is the whole claim.
    [[ "$records_text" =~ $dirty_tree.*$reset_command ]] ||
      problems+=("$skill_md's Resume captures git status --porcelain only after the reset, where the tree is already clean, so the comment names nothing however faithfully it reports what it captured")
  fi
  # Whichever record carries it — the sub-step that resets or the one that posts — the
  # instruction wanted is the one that says the comment carries the paths. Anchored on both
  # the comment and a path rather than on a sub-step number, because a fix is free to say it
  # in either place and both are the same instruction to the session that reads it.
  if reads 'says the ### ▶️ Resuming comment names the paths the reset discarded' \
      '▶️ resuming' '(path|file)'; then
    says '(discard|threw away|thrown away|throw away|stray|reset)' \
      "$skill_md's Resume mentions paths in the ### ▶️ Resuming comment without saying they are what the reset discarded, so the thread names files without recording that they are gone"
  fi
fi
report "$name"

# 10. One criterion — the refusal has a way out on every combination of its two answers, and
#     so one case. Case 3 pins the gate: a non-empty `git status --porcelain` or a pending step
#     stops the run before `gh pr create`. What #194 found is that the remedy the same record
#     names is conditional — "for a pending step" — and one combination falls outside it: a
#     dirty tree with nothing pending and nothing unchecked. There, Resume sub-step 2 exits 3,
#     sub-step 3 finds no step to run, and control arrives back at a gate that refuses the same
#     tree again. Neither finished nor failed, and an unattended conductor has nothing to do but
#     repeat it.
#
#     The case belongs beside case 3 rather than in skill-draft-pr.test.sh because it is the
#     same record and the same refusal: what this criterion adds is the answer that record owes
#     once it has refused, and a probe of it written against another suite's slice would drift
#     from the gate it is the other half of.
#
#     Read from the record the refusal lives in, the way case 3 reads it, and asked for the two
#     conditions in the writer's own words: the tree is dirty with no step pending, and none
#     unchecked either. `no ` with its space rather than a bare `no`, and within one sentence,
#     because the record already carries "do **not** open the PR" a few words ahead of "for a
#     pending step" — a looser probe would read that refusal as the answer to it.
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

# 11. One criterion — the section says WHY the reset is unconditional — and so one case. Cases
#     8 and 9 pin what a resume does: it resets before the ask, and it names what it threw
#     away. Neither asks the document to say what that reset is for, and a command with no
#     reason beside it is the first thing a later rewording moves back under the pending
#     branch, which is exactly the regression #194 is the record of. The reason is one fact:
#     the kill mode that leaves stray work is not particular to a refactor leaf — a usage limit
#     takes the conductor and every leaf together, so a leaf killed in Red or Green leaves the
#     same uncommitted, unverified work behind that a killed refactor leaf does.
#
#     Read from the record that says what a resumed worktree may be carrying, and probed for
#     the two halves of the claim within one sentence: both phases named in one breath, and
#     that breath tying them to the killed refactor leaf. Bounded with `[^.]` rather than asked
#     of the record as a whole, because this record also says "**green but not tidied**" and
#     "that step's green commit and its verify-refactor" further down — unbounded probes would
#     read those as the claim and pass a Resume that had dropped the sentence entirely. The
#     `[^a-z]` guards are there for the same reason at word level: `or` is a substring of
#     "refactor", "worktree" and "before", all of which this record says repeatedly, so a
#     conjunction probed as a bare substring would find one between any two of the `$green`s.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
