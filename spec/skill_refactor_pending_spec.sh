#shellcheck shell=bash
# A ShellSpec port of skills/tdd/scripts/tests/skill-refactor-pending.test.sh, written for
# the spike that asks whether veri's hand-rolled suites should move to ShellSpec. It is
# evidence, not an adoption: the original stays where it is and stays authoritative.
#
# The subject is unchanged — SKILL.md, CLAUDE.md and CONTEXT.md read as text, seven criteria
# about the `⟂ refactor pending` mark's lifetime (#116). Read the original's header for what
# each criterion claims and why; it is not restated here, because a second copy of that
# reasoning is exactly the drift the original's own comments keep warning about.
#
# What had to diverge, and why — the point of the port:
#
# 1. **Every assertion is inlined at its call site.** ShellSpec's translator refuses `The`
#    and `Assert` anywhere but directly inside an Example: `Syntax error: The cannot be
#    defined outside of Example`. The original factors a claim made in two places into one
#    function on purpose — `precedes` (:230), `says_exit_codes` (:364) and
#    `says_pending_until_verified` (:377) each exist so that two call sites cannot be
#    reworded apart — and none of the three can survive as a function here. Their sentences
#    are duplicated below, in the two places each, and the duplication is free to drift the
#    way those comments say it is. Only the *readers* (`records_of`, `section_of`,
#    `first_record`, `reads`, `record_of`, `reads_entry`, `ordinal`) port unchanged, because
#    a reader contains no expectation.
#
# 2. **`Assert <fn> <args…>` over `The value … should …`.** ShellSpec 0.28.1 ships no regex
#    matcher — `match pattern` is a glob (vendor/shellspec/lib/core/matchers/match.sh) — and
#    `satisfy` reports a fixed sentence of its own. Every probe in the original is a bash
#    ERE plus the paragraph that says what a miss costs, so the port keeps the original's
#    `says`/`denies` predicates verbatim and hands the paragraph to `Assert` as a trailing
#    argument it never reads: `Assert` echoes its whole argument list into the failure, which
#    is the only way found to get the sentence in front of whoever broke it.
#
# 3. **`$instruction` and `$records` stay global**, read by the predicates rather than passed.
#    That is the original's shape (:314), and it is also what keeps a failure line readable:
#    `Assert` prints its arguments, so a record passed by value would put the whole matched
#    paragraph in front of the sentence explaining it.
#
# 4. **`entry_says` (:353) becomes a literal at each of its eight calls**, for reason 1. The
#    entry's name is still spelled once — `reads_entry` leaves it in `$entry_script` and the
#    interpolation below reads it — so the one drift that helper existed to stop (a probe
#    reporting under the name of an entry it never read) is still stopped.
#
# 5. **`miss` (:387) clipped the quoted record to 130 characters.** `Assert` prints what it
#    is given and nothing else, so the clip is gone; a failure here quotes the regex and the
#    sentence, never the record.
#
# 6. **`VERI_SPEC_DOC_ROOT` is spike scaffolding, not part of the contract.** The original
#    resolves the three documents from `$0`'s own directory and can only ever read the real
#    ones. ShellSpec gives the spec `$SHELLSPEC_PROJECT_ROOT` instead, and the override exists
#    so the spike could point the readers at a scratch copy and plant a bug in it — which is
#    the only way to show a ported probe still asserts. Nothing else sets it.
#
# Run: vendor/shellspec/shellspec --shell bash spec/skill_refactor_pending_spec.sh

# shellcheck disable=SC2154
ROOT="${VERI_SPEC_DOC_ROOT:-${SHELLSPEC_PROJECT_ROOT:-$PWD}}"

# The three documents, each named twice for the reason the original gives at :57 — the path
# as a message spells it, and the same path resolved for the readers to open.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
context_md="CONTEXT.md"
context_path="$ROOT/$context_md"

# The mark itself and the `verify.sh refactor` call shape, each spelled once, for the reasons
# at :73 and :84 of the original.
mark='⟂ refactor pending'
verify_refactor='verify\.sh (--step [^ ]+ )?(--fast-cmd [^ ]+ )?refactor'

# ---------------------------------------------------------------------------
# Readers. These port unchanged: they contain no expectation, so ShellSpec has
# no opinion about them. Their doc comments live in the original at the line
# numbers named below and are not copied here.
# ---------------------------------------------------------------------------

# records_of (original :123) — stdin as the document's records, one per line, lowercased.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

instructions() { records_of < "$skill_path"; }
claude_records() { records_of < "$claude_path"; }
context_records() { records_of < "$context_path"; }

# section_of (original :155) — the records of one section, <heading> to the next <closers-re>.
section_of() {
  awk -v heading="$1" -v closers="$2" \
    '$0 ~ closers { inside = ($0 == heading); next } inside' "$skill_path" | records_of
}

resume_instructions() { section_of '## Resume' '^## '; }
draft_pr_instructions() { section_of '### 4. Draft PR' '^## |^### '; }
scripts_instructions() { section_of '## The scripts (this skill'\''s `scripts/` directory)' '^## '; }

# ordinal (original :209) — the 1-based position of the first record matching <regex>, or 0.
ordinal() {
  local n=0 line
  while IFS= read -r line; do
    n=$((n + 1))
    if [[ "$line" =~ $1 ]]; then printf '%s\n' "$n"; return 0; fi
  done <<< "$records"
  printf '0\n'
}

# first_record (original :251) — the first record matching every <anchor-regex>, into
# `$instruction`.
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

# reads / record_of / reads_entry (original :272, :302, :338) — the three searches, minus the
# `problems+=` each ended in: the sentence a miss is worth now travels to the `Assert missing`
# in the `else` branch at the call site, because ShellSpec will not let it live in here.
instruction=""
records=""
reads() { shift; first_record "$@"; }

record_name=""
record_of() {
  record_name="$1's $2"
  shift 2
  first_record "$@"
}

entry_script=""
reads_entry() {
  local escaped="${1//./\\.}"
  entry_script="$1"
  first_record "^- .\\\$s/$escaped"
}

# ---------------------------------------------------------------------------
# Predicates. `Assert <fn> <regex> <fact>` runs one of these in a subshell and
# prints its whole argument list on a miss, so <fact> — the original's problem
# sentence, unedited — is what a reader of the failure sees. The predicates
# themselves never read it.
# ---------------------------------------------------------------------------

# says / denies (original :314) — one thing the record in `$instruction` must carry, or must
# not.
says() { [[ "$instruction" =~ $1 ]]; }
denies() { ! [[ "$instruction" =~ $1 ]]; }

# matches — `says`, for a string that is not the record just read: the halves either side of
# an anchor, which `says_reset_reenter_verify` (original :427) cuts out of the instruction.
matches() { [[ "$1" =~ $2 ]]; }

# has_records — the fail-closed guard `records_from` (original :198) was: an empty slice means
# a renamed heading, and not one probe of that case was tested, which must not read as a pass.
has_records() { [[ -n "$records" ]]; }

# present / in_order — the two halves of `precedes` (original :230) that survive as
# predicates. The branching it did around them could not: see divergence 1 in the header.
present() { [[ "$1" -ne 0 ]]; }
in_order() { [[ "$1" -le "$2" ]]; }

# missing — the unconditional failure a fail-closed branch needs. The original appended a
# problem and returned; ShellSpec has no way to fail an example except an expectation, so the
# sentence is asserted against a predicate that never holds.
missing() { return 1; }

Describe 'the refactor-pending mark is written, withheld and cleared where the conductor says'

  # 1. One criterion — the mark is written at exactly one tick, withheld at the other, and
  #    cleared where the step ends.
  It 'ticks green with --refactor-pending, pins without it, and clears the mark before mirroring the step done'
    records="$(instructions)"
    Assert has_records \
      "$skill_md has no instructions to read — the mark's lifetime could not be checked"

    if has_records; then
      # Green's PASS — the only tick that writes the mark.
      if reads 'ticks the ledger and commits the code with a `feat:` commit' \
          'tick-ledger\.sh' 'feat:'; then
        Assert says 'tick-ledger\.sh[[:space:]]+--refactor-pending' \
          "$skill_md's green PASS still ticks with plain \`tick-ledger.sh\`, so the step is recorded as done the moment it is green and a run interrupted in its refactor loop resumes with nothing left to do"
      else
        Assert missing \
          "$skill_md has no instruction that ticks the ledger and commits the code with a \`feat:\` commit — what that branch prescribes could not be read"
      fi

      # The pin path — a mark written here could never be cleared.
      if reads 'ticks the ledger and commits the pin with a `test: pin` commit' \
          'tick-ledger\.sh' 'test: pin'; then
        Assert denies '--refactor-pending' \
          "$skill_md's pin path ticks with --refactor-pending, but a pinned step runs no refactor loop, so the mark it writes can never be cleared and resume would re-enter a loop that step never had"
      else
        Assert missing \
          "$skill_md has no instruction that ticks the ledger and commits the pin with a \`test: pin\` commit — what that branch prescribes could not be read"
      fi

      # verify-refactor's PASS — the only place the mark is cleared, and the clearing has to
      # land in a commit before the step is mirrored as done. `says_clear_commit_mirror`
      # (original :397) read each probe off what the one before it left and returned on the
      # first miss, because "and after that?" has no answer once the order is broken; the
      # early returns become nesting, which is the only shape that keeps that semantics when
      # the probes cannot be moved into a function.
      if reads 'ends the cycle by posting the `### ✅ step done` comment' 'step done'; then
        rest="$instruction"
        Assert matches "$rest" 'clear-refactor-pending\.sh' \
          "$skill_md never runs clear-refactor-pending.sh where a step's cycle completes, so the mark green wrote is never removed and every finished step reads as pending"
        if [[ "$rest" =~ clear-refactor-pending\.sh ]]; then
          rest="${rest#*clear-refactor-pending.sh}"
          Assert matches "$rest" 'git[[:space:]].*commit' \
            "$skill_md clears the mark but commits nothing after it, so the cleared ledger stays uncommitted and the next resume reads the committed one, which still says pending"
          if [[ "$rest" =~ git[[:space:]].*commit ]]; then
            rest="${rest#*commit}"
            Assert matches "$rest" 'tick-issue-criterion\.sh' \
              "$skill_md mirrors the step to the issue before the cleared ledger is committed, so a run killed in that window has an issue saying done over a ledger still saying pending"
          fi
        fi
      else
        Assert missing \
          "$skill_md has no instruction that ends the cycle by posting the \`### ✅ step done\` comment — what that branch prescribes could not be read"
      fi
    fi
  End

  # 2. One criterion — the mark's reader.
  It "Resume asks next-pending-refactor.sh before next-unchecked.sh, re-enters the pending step's refactor loop, and reaches the draft PR only when both exit 3"
    records="$(resume_instructions)"
    Assert has_records \
      "$skill_md has no ## Resume section to read — what a resumed run does could not be checked"

    if has_records; then
      # `precedes` (original :230) inlined — first call site of two. The two absences are
      # probed before the order is, and the order only when both are present, because a
      # missing instruction has ordinal 0 and reads as "comes first".
      first="$(ordinal 'next-pending-refactor\.sh')"
      second="$(ordinal 'next-unchecked\.sh')"
      Assert present "$first" \
        "$skill_md's Resume never asks next-pending-refactor.sh, so a run interrupted inside a step's refactor loop reads that step's tick as done and walks straight to the PR"
      if [[ "$first" -ne 0 ]]; then
        Assert present "$second" \
          "$skill_md's Resume no longer asks next-unchecked.sh, so a resumed run has no next step to continue from"
        if [[ "$second" -ne 0 ]]; then
          Assert in_order "$first" "$second" \
            "$skill_md's Resume asks next-unchecked.sh before next-pending-refactor.sh, so it opens the next step's red phase while the previous step's refactor is still unverified"
        fi
      fi

      # The pending branch — `says_reset_reenter_verify` (original :427) inlined. `$anchor` is
      # what the order is read against, so its absence returns rather than probing two halves
      # of a string that has no middle; it is still spelled once and used three times.
      if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
        anchor='git diff --name-only'
        Assert says "$anchor" \
          "$skill_md's Resume re-enters no refactor loop for the pending step — nothing computes the files of its green commit, so the loop has no bounds to tidy within and the step is left green but never tidied"
        if [[ "$instruction" =~ $anchor ]]; then
          before="${instruction%%$anchor*}"
          after="${instruction#*$anchor}"
          Assert matches "$before" 'git (checkout|restore|reset|stash|clean)' \
            "$skill_md's Resume re-enters the refactor loop without first resetting the worktree, so the transform the killed leaf left uncommitted is carried into the resumed step and into the PR unverified"
          Assert says 'git log.*issue-<n>\.md' \
            "$skill_md's Resume never identifies the pending step's green commit as the last commit that changed the ledger, so the files it hands the refactor loop are some other commit's and the tidy-up is aimed at the wrong code"
          Assert says 'refactor:' \
            "$skill_md's Resume hands the refactor loop no count of the \`refactor:\` commits already made for the step, so the budget restarts at 0 and an interrupted run can spend it twice over"
          Assert matches "$after" 'verify-refactor|verify\.sh refactor' \
            "$skill_md's Resume re-enters the refactor loop but never runs verify-refactor after it, which is the check the interruption skipped in the first place"
        fi
      else
        Assert missing \
          "$skill_md has no instruction that runs next-pending-refactor.sh on a resume — what that branch prescribes could not be read"
      fi

      # The exit — the draft PR behind both scripts having nothing left to hand over.
      if reads 'sends a resumed run to the draft pr' 'draft pr'; then
        Assert says 'next-pending-refactor\.sh' \
          "$skill_md sends a resumed run to the draft PR on next-unchecked.sh alone, so a ledger whose every step is ticked still reaches the PR with the last step's refactor unverified"
        Assert says 'next-unchecked\.sh' \
          "$skill_md sends a resumed run to the draft PR without next-unchecked.sh having exited 3, so a run with steps still to do can reach the PR"
      else
        Assert missing \
          "$skill_md has no instruction that sends a resumed run to the draft pr — what that branch prescribes could not be read"
      fi
    fi
  End

  # 3. One criterion — the gate on the way out.
  It 'the Draft PR step refuses to open the PR while git status --porcelain is non-empty or next-pending-refactor.sh finds a pending step'
    records="$(draft_pr_instructions)"
    Assert has_records \
      "$skill_md has no ### 4. Draft PR section to read — what guards the PR could not be checked"

    if has_records; then
      # `precedes` inlined — second call site of two. The sentences below and the branching
      # around them are a copy of the block in the example above; see divergence 1.
      first="$(ordinal 'git status --porcelain')"
      second="$(ordinal 'gh pr create')"
      Assert present "$first" \
        "$skill_md's Draft PR step never checks git status --porcelain, so the transform a killed refactor leaf left uncommitted reaches the PR with no verifier having seen it"
      if [[ "$first" -ne 0 ]]; then
        Assert present "$second" \
          "$skill_md's Draft PR step no longer opens the PR, so there is nothing for the check to guard"
        if [[ "$second" -ne 0 ]]; then
          Assert in_order "$first" "$second" \
            "$skill_md's Draft PR step checks the tree only after gh pr create, so the dirty worktree is already up for review by the time anything notices"
        fi
      fi

      if reads 'checks the worktree is clean before the PR is opened' 'git status --porcelain'; then
        Assert says 'next-pending-refactor\.sh' \
          "$skill_md's Draft PR step checks only that the tree is clean, so a ledger whose last step is committed but still marked refactor-pending opens a PR with that step's refactor never verified"
        Assert says 'refuse|do not open|does not open|stop|bail|must not|never' \
          "$skill_md's Draft PR step names the checks but never says they can stop it, so a non-empty status or a pending step is read as information and the PR is opened anyway"
      else
        Assert missing \
          "$skill_md has no instruction that checks the worktree is clean before the PR is opened — what that branch prescribes could not be read"
      fi
    fi
  End

  # 4. One criterion — the three scripts documented where a session looks a script up.
  It 'the script reference list documents tick-ledger.sh --refactor-pending, next-pending-refactor.sh and clear-refactor-pending.sh, each with what it prints and its exit codes'
    records="$(scripts_instructions)"
    Assert has_records \
      "$skill_md has no ## The scripts section to read — what the reference list documents could not be checked"

    if has_records; then
      # tick-ledger.sh — the writer.
      if reads_entry tick-ledger.sh; then
        Assert says '--refactor-pending' \
          "$skill_md's entry for $entry_script never mentions --refactor-pending, so the flag the green commit must tick with is invisible to a session that reads the list to find out how to tick"
        Assert says "$mark" \
          "$skill_md's entry for $entry_script never spells the mark the flag appends, so nothing connects that write to the \`$mark\` string next-pending-refactor.sh matches, and either side can be reworded without the other noticing"
        Assert says 'exits? 3' \
          "$skill_md's entry for $entry_script never names exit 3, so a green commit whose substring matched no unchecked step looks like it ticked, and the step is committed as green with no mark and no tick"
      else
        Assert missing \
          "$skill_md has no instruction that documents tick-ledger.sh in the script reference list — what that branch prescribes could not be read"
      fi

      # next-pending-refactor.sh — the reader, the only one that answers on stdout.
      if reads_entry next-pending-refactor.sh; then
        Assert says 'prints?[^.]*step' \
          "$skill_md's entry for $entry_script never says it prints the pending step, so a resumed conductor is not told that stdout is the step to re-enter the refactor loop on"
        # `says_exit_codes` (original :364) inlined — first call site of two.
        Assert says 'exits? 0' \
          "$skill_md's entry for $entry_script never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty"
        Assert says 'exits? 3' \
          "$skill_md's entry for $entry_script never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken"
      else
        Assert missing \
          "$skill_md has no instruction that documents next-pending-refactor.sh in the script reference list — what that branch prescribes could not be read"
      fi

      # clear-refactor-pending.sh — the eraser. Nothing on stdout.
      if reads_entry clear-refactor-pending.sh; then
        Assert says "$mark" \
          "$skill_md's entry for $entry_script never spells the mark it removes, so the list documents an eraser without saying what it erases and nothing ties it to the flag that wrote the mark"
        Assert says 'strip|remove|drop|clear|delete' \
          "$skill_md's entry for $entry_script never says it takes the mark off the step, so what the script does to the ledger is left to be guessed from its name"
        # `says_exit_codes` inlined — second call site of two, a verbatim copy of the pair
        # above. The original spells them once precisely so the two cannot drift apart.
        Assert says 'exits? 0' \
          "$skill_md's entry for $entry_script never names exit 0, so nothing says what a call that did its work answers with, and the conductor is left inferring it from whether stdout came back empty"
        Assert says 'exits? 3' \
          "$skill_md's entry for $entry_script never names exit 3, so the one code that is not an error — nothing matched, nothing pending — has no documented meaning and reads as the plumbing having broken"
      else
        Assert missing \
          "$skill_md has no instruction that documents clear-refactor-pending.sh in the script reference list — what that branch prescribes could not be read"
      fi
    fi
  End

  # 5. One criterion — the two documents that explain this repository record the mark too.
  It "CLAUDE.md's ledger invariant and CONTEXT.md's Ledger entry say a ticked step carries the refactor-pending mark until its verify-refactor passes"
    records="$(claude_records)"
    Assert has_records \
      "$claude_md has no records to read — what this repository calls unbreakable about the ledger could not be checked"

    if has_records; then
      if record_of "$claude_md" 'ledger invariant' 'committed ledger' 'source of truth'; then
        # `says_pending_until_verified` (original :377) inlined — first call site of two.
        Assert says "$mark" \
          "$record_name never spells the \`$mark\` mark, so this repository's own account of the ledger still says a tick means the step is finished, and the next agent to read it takes the mark back out as noise"
        Assert says 'verify-refactor' \
          "$record_name records the mark without naming verify-refactor, so nothing says what clears it and a ticked step's mark reads as something the ledger wears for ever"
      else
        Assert missing \
          "$claude_md has no ledger invariant — what it records about a ticked step could not be read"
      fi
    fi

    records="$(context_records)"
    Assert has_records \
      "$context_md has no records to read — what this repository means by \"ledger\" could not be checked"

    if has_records; then
      if record_of "$context_md" 'Ledger glossary entry' '^\*\*ledger\*\*:'; then
        # `says_pending_until_verified` inlined — second call site of two, a verbatim copy.
        Assert says "$mark" \
          "$record_name never spells the \`$mark\` mark, so this repository's own account of the ledger still says a tick means the step is finished, and the next agent to read it takes the mark back out as noise"
        Assert says 'verify-refactor' \
          "$record_name records the mark without naming verify-refactor, so nothing says what clears it and a ticked step's mark reads as something the ledger wears for ever"
      else
        Assert missing \
          "$context_md has no Ledger glossary entry — what it records about a ticked step could not be read"
      fi
    fi
  End

  # 6. One criterion — what a resume hands the leaf it relaunches.
  It "Resume resets the uncommitted work and relaunches the refactor leaf with VERI_REFACTOR_BUDGET reduced by the step's existing refactor: commits"
    records="$(resume_instructions)"
    Assert has_records \
      "$skill_md has no ## Resume section to read — what budget a relaunched refactor leaf is given could not be checked"

    if has_records; then
      if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
        # `says_reset_and_reduced_budget` (original :468) inlined. The reduction's alternation
        # covers the prose forms and the arithmetic one, and deliberately not a bare `--count`.
        Assert says 'git (checkout|restore|reset|clean)' \
          "$skill_md's Resume relaunches the refactor leaf without first resetting the worktree, so the transform the killed leaf left half-applied on disk is carried into the relaunched leaf and into the PR unverified"
        Assert says 'veri_refactor_budget' \
          "$skill_md's Resume never names VERI_REFACTOR_BUDGET on the pending branch, so the relaunched leaf is asked for the run's whole budget and the interrupted step pays for its tidying twice over"
        Assert says 'reduc|minus|subtract|net of|what is left|left of|remaining|\$\(\(' \
          "$skill_md's Resume never says the budget the relaunched leaf is given is reduced by the \`refactor:\` commits the step already has, so the count it computes is read and then thrown away"
      else
        Assert missing \
          "$skill_md has no instruction that runs next-pending-refactor.sh on a resume — what that branch prescribes could not be read"
      fi
    fi
  End

  # 7. One criterion — the base sha verify-refactor is handed, at both call sites.
  It "the step's green commit sha reaches verify.sh refactor in the cycle loop and in Resume's pending branch"
    records="$(instructions)"
    Assert has_records \
      "$skill_md has no instructions to read — what verify-refactor is handed could not be checked"

    if has_records; then
      if reads 'runs verify.sh refactor in the cycle loop' "$verify_refactor"; then
        Assert says "$verify_refactor [^ ]+ [^ ]+ <green-sha>" \
          "$skill_md's cycle loop runs verify.sh refactor without the step's <green-sha>, so verify-refactor has no range to diff and exits 2"
      else
        Assert missing \
          "$skill_md has no instruction that runs verify.sh refactor in the cycle loop — what that branch prescribes could not be read"
      fi
    fi

    records="$(resume_instructions)"
    Assert has_records \
      "$skill_md has no ## Resume section to read — what a resumed verify-refactor is handed could not be checked"

    if has_records; then
      if reads 'runs next-pending-refactor.sh on a resume' 'next-pending-refactor\.sh'; then
        Assert says "$verify_refactor"' [^ ]+ [^ ]+ "?\$green' \
          "$skill_md's Resume never runs verify.sh refactor with \$green, so the resumed step's verify-refactor is handed no base sha and exits 2"
      else
        Assert missing \
          "$skill_md has no instruction that runs next-pending-refactor.sh on a resume — what that branch prescribes could not be read"
      fi
    fi
  End
End
