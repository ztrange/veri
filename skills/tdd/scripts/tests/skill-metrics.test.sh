#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics
# report. Like skill-draft-pr.test.sh and skill-commit.test.sh this suite belongs to no
# single script: its subject is the procedure document, read as text, the way the session
# that follows it reads it. Picked up by `make test`'s glob by existing.
# Zero-dependency plain-shell asserts, same idiom as skill-draft-pr.test.sh.
#
# Why this exists (issue #108): `metrics.sh` renders the report, and metrics.test.sh pins
# what it renders — but nothing launches the conductor, so the report reaches a human only
# because this document says to go and get it. A run that never calls the script leaves the
# figures computable and uncomputed, which is indistinguishable, from the issue thread, from
# not having them at all.
#
# The subject is both of the run's two endings, because the report's whole value is at the
# ending that went badly: a document that delivered metrics only on the PR path would drop
# them exactly where waste is the figure someone wants. So the criterion is read at the
# Draft PR step AND in the Bailing section, and each contributes its own problem line.
#
# Contract under test (one criterion, one case):
#   SKILL.md's `### 4. Draft PR` step runs, in this order (since #236, and since #195 opening
#   no PR of its own), `gh api …/pulls?head=` for the URL of the PR the plan commit already opened,
#   `event.sh done pr=<pr-url>`, `metrics.sh`, a `metrics:` commit of
#   `.tdd/issue-<n>-metrics.md`, `push-branch.sh`, and `gh api -X PATCH`, which carries the
#   `### 📊 Metrics` block into the PR body; the same block goes into the final `✅ Done`
#   comment; SKILL.md's `## Bailing` section commits
#   the same file on the pushed branch and puts the block on the `⛔ Bailed` comment.
#
# Run: scripts/tests/skill-metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

section_records() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path" | records_of
}

first_record_line() {
  local records="$1" n line
  shift
  n=0
  while IFS= read -r line; do
    n=$((n + 1))
    local s ok=1
    for s in "$@"; do
      [[ "$line" == *"$s"* ]] || { ok=0; break; }
    done
    [[ "$ok" -eq 0 ]] || { echo "$n"; return 0; }
  done <<< "$records"
  return 1
}

record_at() { sed -n "${2}p" <<< "$1"; }

name="$skill_md commits the metrics report and posts its 📊 block, on the PR path and on the bail path"
problems=()

pr_records="$(section_records '### 4. Draft PR' '^## |^### ')"
if [[ -z "$pr_records" ]]; then
  problems+=("$skill_md has no ### 4. Draft PR section to read — whether the run delivers its metrics could not be checked")
else
  first_record_line "$pr_records" 'metrics.sh' >/dev/null ||
    problems+=("$skill_md's Draft PR step never runs metrics.sh, so the run's figures stay computable and uncomputed")

  first_record_line "$pr_records" 'metrics:' 'metrics.md' >/dev/null ||
    problems+=("$skill_md's Draft PR step has no instruction committing .tdd/issue-<n>-metrics.md in a metrics: commit, so the report is never beside the ledger it describes")

  first_record_line "$pr_records" 'gh api -x patch' >/dev/null ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit, so the run ends with no PR carrying the metrics it committed")

  first_record_line "$pr_records" '✅ done' '📊 metrics' >/dev/null ||
    problems+=("$skill_md's final ✅ Done comment does not carry the ### 📊 Metrics block, so the issue thread ends without the run's figures")
fi

bail_records="$(section_records '## Bailing' '^## ')"
if [[ -z "$bail_records" ]]; then
  problems+=("$skill_md has no ## Bailing section to read — whether a bailed run delivers its metrics could not be checked")
else
  first_record_line "$bail_records" 'metrics.md' 'commit' >/dev/null ||
    problems+=("$skill_md's Bailing section never commits .tdd/issue-<n>-metrics.md on the pushed branch, so the run whose waste the report measures is the one that leaves no report")
  first_record_line "$bail_records" '⛔ bailed' '📊 metrics' >/dev/null ||
    problems+=("$skill_md's ⛔ Bailed comment does not carry the ### 📊 Metrics block, so the ending that most needs the figures posts none")
fi
report "$name"

name="$skill_md's Draft PR step writes the run's done mark, carrying the PR URL, before rendering the metrics report it commits"
problems=()

render_line="$(first_record_line "$pr_records" 'metrics.sh' '> .tdd/issue-<n>-metrics.md')" ||
  problems+=("$skill_md's Draft PR step never renders metrics.sh into .tdd/issue-<n>-metrics.md, so there is no committed report to order against the done mark")
done_line="$(first_record_line "$pr_records" 'event.sh done' 'pr=')" ||
  problems+=("$skill_md's Draft PR step never writes event.sh done pr=<pr-url>, so the report can never name the landed PR")
if [[ -n "${render_line:-}" && -n "${done_line:-}" && "$render_line" -lt "$done_line" ]]; then
  problems+=("$skill_md renders the committed metrics report BEFORE event.sh done, so its Outcome reads unknown instead of naming the landed PR: $(printf '%.120s' "$(record_at "$pr_records" "$render_line")")")
fi
report "$name"

name="$skill_md pastes into the PR body and the ✅ Done comment the committed report rendered after event.sh done"
problems=()

offset_of() {
  [[ "$1" == *"$2"* ]] || return 1
  local before="${1%%"$2"*}"
  echo "${#before}"
}

pr_text="$pr_records"
done_at="$(offset_of "$pr_text" 'event.sh done pr=')" ||
  problems+=("$skill_md's Draft PR step never writes event.sh done pr=<pr-url>, so no report can be rendered after it")
render_at="$(offset_of "$pr_text" 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')" ||
  problems+=("$skill_md's Draft PR step never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md, so there is no committed report to paste")
if [[ -n "${done_at:-}" && -n "${render_at:-}" && "$render_at" -lt "$done_at" ]]; then
  problems+=("$skill_md renders the report at offset $render_at, BEFORE event.sh done at offset $done_at, so every pasted copy reads unknown")
fi

body_at="$(offset_of "$pr_text" 'contents of .tdd/issue-<n>-metrics.md')" ||
  problems+=("$skill_md's Draft PR step never puts the contents of .tdd/issue-<n>-metrics.md into the PR body")
if [[ -n "${body_at:-}" ]]; then
  body_cmd="${pr_text:0:$body_at}"
  body_cmd="gh api ${body_cmd##*gh api }"
  [[ "$body_cmd" == *"-f body="* ]] ||
    problems+=("$skill_md mentions the contents of .tdd/issue-<n>-metrics.md outside a gh api -f body=, so the PR body never gets the committed report")
  if [[ -n "${render_at:-}" && "$body_at" -lt "$render_at" ]]; then
    problems+=("$skill_md pastes the report into the PR body at offset $body_at, BEFORE it is rendered after done at offset $render_at: $(printf '%.120s' "$body_cmd")")
  fi
fi

done_comment_line="$(first_record_line "$pr_records" '✅ done' '📊 metrics')" ||
  problems+=("$skill_md's Draft PR step has no ✅ Done comment carrying the 📊 Metrics block")
if [[ -n "${done_comment_line:-}" ]]; then
  done_comment="$(record_at "$pr_records" "$done_comment_line")"
  comment_at="$(offset_of "$pr_text" "$done_comment")"
  if [[ -n "${render_at:-}" && -n "${comment_at:-}" && "$comment_at" -lt "$render_at" ]]; then
    problems+=("$skill_md posts the ✅ Done comment's report at offset $comment_at, BEFORE it is rendered after done at offset $render_at")
  fi
  [[ "$done_comment" == *"issue-<n>-metrics.md"* || "$done_comment" == *"file just committed"* ]] ||
    problems+=("$skill_md's ✅ Done comment does not paste the report from the committed file, so it may differ from what the branch carries: $(printf '%.120s' "$done_comment")")
fi
report "$name"

name="$skill_md's Draft PR command block reads the open PR's URL before the metrics: commit, ordered line by line"
problems=()

fenced_lines() {
  awk '/^## |^### / { inside = (index($0, "### 4. Draft PR") == 1); fence = 0; next }
    !inside { next }
    /^[[:space:]]*```/ { fence = !fence; next }
    fence { print NR " " $0 }' "$skill_path"
}

first_fenced_line() {
  local n rest
  while IFS=' ' read -r n rest; do
    [[ "$rest" == *"$1"* ]] && { echo "$n"; return 0; }
  done <<< "$(fenced_lines)"
  return 1
}

pr_read='pulls?head='
pr_edit='gh api -X PATCH'

block_pr_line="$(first_fenced_line "$pr_read")" ||
  problems+=("$skill_md's Draft PR command block never runs gh api …/pulls?head= to read the open PR's URL")
block_commit_line="$(first_fenced_line 'git commit -m "metrics:')" ||
  problems+=("$skill_md's Draft PR command block never runs git commit -m \"metrics: …\"")
if [[ -n "${block_pr_line:-}" && -n "${block_commit_line:-}" && "$block_commit_line" -lt "$block_pr_line" ]]; then
  problems+=("$skill_md commits the metrics report at SKILL.md:$block_commit_line, BEFORE gh api …/pulls?head= at SKILL.md:$block_pr_line, so the report is rendered and committed with no PR URL for the done mark to name")
fi
report "$name"

name="$skill_md's Draft PR command block runs gh pr edit after the metrics: commit and push-branch.sh, ordered line by line"
problems=()

block_edit_line="$(first_fenced_line "$pr_edit")" ||
  problems+=("$skill_md's Draft PR command block never runs gh pr edit, so the PR body never gets the 📊 block")
block_commit_line="$(first_fenced_line 'git commit -m "metrics:')" ||
  problems+=("$skill_md's Draft PR command block never runs git commit -m \"metrics: …\"")
block_push_line="$(first_fenced_line 'push-branch.sh')" ||
  problems+=("$skill_md's Draft PR command block never runs push-branch.sh")
if [[ -n "${block_edit_line:-}" && -n "${block_commit_line:-}" && "$block_edit_line" -lt "$block_commit_line" ]]; then
  problems+=("$skill_md runs gh pr edit at SKILL.md:$block_edit_line, BEFORE the metrics: commit at SKILL.md:$block_commit_line, so the PR body quotes a report the branch does not carry")
fi
if [[ -n "${block_edit_line:-}" && -n "${block_push_line:-}" && "$block_edit_line" -lt "$block_push_line" ]]; then
  problems+=("$skill_md runs gh pr edit at SKILL.md:$block_edit_line, BEFORE push-branch.sh at SKILL.md:$block_push_line, so the PR body quotes a report the pushed branch does not carry")
fi
report "$name"

name="$skill_md's Draft PR command block runs gh api …/pulls?head=, event.sh done, metrics.sh, the metrics: commit, push-branch.sh and gh api -X PATCH in that order"
problems=()

prev_anchor="" prev_line=""
for anchor in "$pr_read" 'event.sh done pr=' 'metrics.sh <n>' 'git commit -m "metrics:' 'push-branch.sh' "$pr_edit"; do
  if ! line="$(first_fenced_line "$anchor")"; then
    problems+=("$skill_md's Draft PR command block never runs $anchor")
    prev_anchor="" prev_line=""
    continue
  fi
  if [[ -n "$prev_line" && "$line" -le "$prev_line" ]]; then
    problems+=("$skill_md runs $anchor at SKILL.md:$line, not after $prev_anchor at SKILL.md:$prev_line")
  fi
  prev_anchor="$anchor" prev_line="$line"
done
report "$name"

name="$skill_md's Draft PR gh pr edit command puts the committed 📊 metrics report in the PR body"
problems=()

if ! edit_line="$(first_fenced_line "$pr_edit")"; then
  problems+=("$skill_md's Draft PR command block never runs gh pr edit, so no command puts the 📊 block in the PR body")
else
  edit_cmd="$(sed -n "${edit_line}p" "$skill_path")"
  [[ "$edit_cmd" == *"-f body="*".tdd/issue-<n>-metrics.md"* ]] ||
    problems+=("$skill_md's gh pr edit at SKILL.md:$edit_line does not put the contents of .tdd/issue-<n>-metrics.md in its -f body=, so the PR body never gets the 📊 block: $(printf '%.120s' "$edit_cmd")")
fi
report "$name"

name="skill-metrics.test.sh's header comment states the Draft PR order gh api …/pulls?head=, event.sh done, metrics.sh, the metrics: commit, push-branch.sh, gh api -X PATCH"
problems=()

suite_md="skills/tdd/scripts/tests/skill-metrics.test.sh"
contract="$(awk '/^# Contract under test/ { on = 1 } on && !/^#/ { exit } on && /^#[[:space:]]*$/ { exit }
  on { sub(/^#[[:space:]]*/, ""); printf "%s ", $0 }' "$ROOT/$suite_md")"
if [[ -z "$contract" ]]; then
  problems+=("$suite_md has no Contract under test paragraph in its header to read")
else
  prev_anchor="" prev_at=""
  for anchor in "$pr_read" 'event.sh done' 'metrics.sh' 'metrics:' 'push-branch.sh' "$pr_edit"; do
    if ! at="$(offset_of "$contract" "$anchor")"; then
      problems+=("$suite_md's Contract under test never names $anchor")
      continue
    fi
    if [[ -n "$prev_at" && "$at" -le "$prev_at" ]]; then
      problems+=("$suite_md's Contract under test names $anchor at offset $at, not after $prev_anchor at offset $prev_at")
    fi
    prev_anchor="$anchor" prev_at="$at"
  done
fi
report "$name"

suite_src="$(cat "$ROOT/$suite_md")"

name="skill-metrics.test.sh carries no record-level commit-before-PR comparison, which records_of's folding makes dead"
problems=()

dead_compare='commit_line" '"-gt"' "$pr_line'
dead_comment='lands '"BEFORE"' the PR is opened'
[[ "$suite_src" != *"$dead_compare"* ]] ||
  problems+=("$suite_md compares the metrics commit's record number against gh pr create's with a greater-than, but section_records folds both into the same record, so the check cannot fail and reports coverage the suite does not have")
[[ "$suite_src" != *"$dead_comment"* ]] ||
  problems+=("$suite_md still carries the comment claiming a record-level probe catches a metrics commit made after the PR is opened, which the folding makes impossible")
report "$name"

name="skill-metrics.test.sh carries no record-level gh pr create + 📊 metrics presence probe, which records_of's folding makes dead"
problems=()

probe_call='first_record_line "$pr_records" '
create_arg="'gh pr create'"
block_arg="'📊 metrics'"
[[ "$suite_src" != *"$probe_call$create_arg $block_arg"* ]] ||
  problems+=("$suite_md still asks whether the record holding gh pr create also holds the 📊 metrics block, but section_records folds the whole Draft PR sub-step into one record, so a block carried by a later gh pr edit answers for the create and the probe cannot fail")
report "$name"

finish
