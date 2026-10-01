#!/usr/bin/env bash
# Unit test for CLAUDE.md as a record of its own rules.
#
# Contract under test:
#   Every rule in the roster below is carried by SOME ONE record of CLAUDE.md — one
#   paragraph, one bullet or one table row — stated in full or in one sentence with a
#   pointer to where its reasoning now lives.
#
# Run: skills/tdd/scripts/tests/claude-md-rules-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"

source "$HERE/lib/harness.sh"

run_case() {
  local name="$1" probe="$2"
  problems=()
  "$probe"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    ok
  else
    no "$name"
    printf '    %s\n' "${problems[@]}"
  fi
}

plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

RECORD_SPLIT='/^([-*] |\| )/ { if (rec != "") print rec; rec = $0; next }
              /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
              rec == "" { rec = $0; next }
              { rec = rec " " $0 }
              END { if (rec != "") print rec }'

records() {
  awk "$RECORD_SPLIT" "$claude_path" | plain
}

section_records() {
  awk -v heading="$1" '$0 == heading { f = 1; next } f && /^## / { exit } f' "$claude_path" |
    awk "$RECORD_SPLIT" | plain
}

ALL_RECORDS="$(records)"

one_record_matches() {
  local text="$1" line
  shift
  while IFS= read -r line; do
    all_regexes_match "$line" "$@" && return 0
  done <<< "$text"
  return 1
}

all_regexes_match() {
  local line="$1" re
  shift
  for re in "$@"; do
    [[ "$line" =~ $re ]] || return 1
  done
  return 0
}

no_records() {
  [[ -z "${1// /}" ]] || return 1
  problems+=("$2")
}

records_carry() {
  local text="$1" problem="$2"
  shift 2
  one_record_matches "$text" "$@" && return
  problems+=("$problem")
}

record_carries() {
  records_carry "$ALL_RECORDS" "$@"
}

ROSTER=$(cat <<'ROWS'
make test is the baseline, and a red one stops a run before it starts;make test;baseline|stay green;refuse|refus
make docs publishes the page by hand only, never on a merge;make docs;by hand|disabled;publish|deploy
make install-hooks installs the tag hook once per clone and refuses to clobber a foreign one;install-hooks;reference-transaction;refus|clobber
make merge-gates runs before a merge and which gates a change owes, including what is exempt;merge-gates;before merging|merging any pr;nothing for;skills/;adr;makefile
docs-check is not part of make test, nor in CI, so documentation lag never blocks a run;docs-check;not.*part of;block|never
CONTEXT.md is where the glossary lives;context.md;glossar|terms
walkthrough.html is generated and never hand-edited;walkthrough;generat;never edit|by hand
the page build fails on a bad reference but only reports a line no commentary claims;fail;chunk|commentary;owed
exit code 1 is a clean negative — a real answer;clean negative|1 ;reject|leaf ran and failed
exit code 2 is no answer obtained;no answer;killed-stuck|unparseable|bad argument
exit code 3 is nothing to do, and not an error;nothing to do;not an error
1 and 2 are never collapsed — a process failure is not a system failure;never collapse|not collapse;process;system
a version is an annotated tag whose message is the capability, and nothing else keeps it;annotated;capability;changelog|version file
git tag is sorted with -v:refname, never plain sort;sort=-v:refname;lexical|v0.9
a backfilled tag needs GIT_COMMITTER_DATE;git_committer_date;backfill|retro
a regen commit built at the tag is not the fixpoint — build, commit, rebuild, amend;amend;unreleased;docs-check|fixpoint
every leaf is launched through supervise.sh and nothing bypasses it;supervise.sh;never|only|bypass
the verifier is blind by construction — the prompt builder takes no rationale;blind;build-verify-prompt.sh;rationale|leak
the committed ledger is the source of truth, and the refactor-pending mark is what a resumed run reads;ledger;source of truth;refactor pending
the three budgets are three axes and are never merged;veri_stuck_retries;revise_budget;veri_refactor_budget;never merged|one knob
the git questions a walkthrough build asks are a pinned budget;once per script;budget|pins;git
a tag changes the page without a commit, and the hook only notices;tag;hook;notice|never rebuild
a test injects rather than waiting on a real model or a real clock, which is why every tunable has a default;claude_bin;veri_heartbeat;:-default
a guard never watched to fail is not tested;guard|failure path;not tested|watched;break
ROWS
)

probe_every_rule_is_carried_by_one_record() {
  local row rule

  no_records "$ALL_RECORDS" \
    "$claude_md could not be read, so no rule could be looked for in it" && return

  while IFS= read -r row; do
    [[ -n "$row" ]] || continue
    IFS=';' read -r -a fields <<< "$row"
    rule="${fields[0]}"
    record_carries "$claude_md has no single record stating that $rule" "${fields[@]:1}"
  done <<< "$ROSTER"
}

run_case "$claude_md still states every rule it is the only record of, in full or in one sentence with a pointer" \
  probe_every_rule_is_carried_by_one_record

probe_budgets_invariant_names_the_fourth_axis() {
  record_carries \
    "$claude_md has no single record naming VERI_NO_VERDICT_RETRIES as a fourth budget axis beside VERI_STUCK_RETRIES, liveness against protocol compliance, never merged" \
    'veri_no_verdict_retries' 'veri_stuck_retries' 'four' \
    'liveness' 'protocol|contract|compliance' 'never merged|not merged|one knob'
}

run_case "$claude_md's budgets invariant names VERI_NO_VERDICT_RETRIES as a fourth axis and why it is not merged with VERI_STUCK_RETRIES" \
  probe_budgets_invariant_names_the_fourth_axis

probe_blind_invariant_names_the_base_sha() {
  record_carries \
    "$claude_md has no single record naming <base-sha> as the refactor phase parameter of build-verify-prompt.sh in the blind-verifier invariant, and why a hex sha cannot leak rationale" \
    'blind' 'build-verify-prompt\.sh' 'base.sha' 'refactor' \
    'hex|0-9a-f' 'rationale|leak'
}

run_case "$claude_md's blind-verifier invariant names the refactor base-sha parameter and why a sha cannot leak rationale" \
  probe_blind_invariant_names_the_base_sha

probe_budgets_invariant_names_the_fifth_axis() {
  record_carries \
    "$claude_md has no single record naming VERI_STEP_GROWTH as a fifth budget axis beside the other four, plan growth, never merged" \
    'veri_step_growth' 'veri_refactor_budget' 'five' \
    'plan' 'never merged|not merged|one knob'
}

run_case "$claude_md's budgets invariant names VERI_STEP_GROWTH as a fifth axis, plan growth, never merged with the other four" \
  probe_budgets_invariant_names_the_fifth_axis

IDIOM_HEADING="## Testing idiom"

probe_idiom_records_the_sigpipe_rule() {
  local idiom_records
  idiom_records="$(section_records "$IDIOM_HEADING")"

  no_records "$idiom_records" \
    "$claude_md has no '$IDIOM_HEADING' section to read, so nothing states the pipefail/SIGPIPE rule where the agent writing a suite would find it" && return

  records_carry "$idiom_records" \
    "$claude_md has no single record in its '$IDIOM_HEADING' section stating that a suite declaring pipefail never ends a pipeline in grep -q or head, that the status asserted on is then the writer's SIGPIPE, which case says so (no-sigpipe-pipelines), and what the repair is" \
    'pipefail' \
    'grep -[a-z]*q' \
    '[^a-z]head' \
    'sigpipe' \
    'no-sigpipe-pipelines' \
    '/dev/null|redirect|to eof' \
    'never|must not|does not|no suite'
}

run_case "$claude_md's testing idiom section states the pipefail/SIGPIPE rule" \
  probe_idiom_records_the_sigpipe_rule

count_matching_records() {
  local text="$1" line n=0
  shift
  while IFS= read -r line; do
    all_regexes_match "$line" "$@" && n=$((n + 1))
  done <<< "$text"
  printf '%s\n' "$n"
}

JOB_SPEC_RULE=(
  'job spec'
  'kill %'
  'pid'
  'bg_start|bg_kill|background\.sh'
  'no-job-spec-kills'
  'never|must not|not by'
)

probe_job_spec_rule_is_stated_once() {
  local found
  found="$(count_matching_records "$ALL_RECORDS" "${JOB_SPEC_RULE[@]}")"

  case "$found" in
    1) ;;
    0)
      problems+=("$claude_md has no single record stating that a background process is killed by the pid it recorded and never by a job spec, naming bg_start/bg_kill as what does it and no-job-spec-kills as the guard that fails the run on the next site") ;;
    *)
      problems+=("$claude_md states the job-spec kill rule in $found records rather than once, so the next trim can take one copy away and leave the document stating a rule it also contradicts") ;;
  esac
}

run_case "$claude_md states once that a background process is killed by its recorded pid, never by a job spec" \
  probe_job_spec_rule_is_stated_once

finish
