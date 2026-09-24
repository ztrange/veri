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
#   no PR of its own), `gh pr view` for the URL of the PR the plan commit already opened,
#   `event.sh done pr=<pr-url>`, `metrics.sh`, a `metrics:` commit of
#   `.tdd/issue-<n>-metrics.md`, `push-branch.sh`, and `gh pr edit`, which carries the
#   `### 📊 Metrics` block into the PR body; the same block goes into the final `✅ Done`
#   comment; SKILL.md's `## Bailing` section commits
#   the same file on the pushed branch and puts the block on the `⛔ Bailed` comment.
#
# Run: scripts/tests/skill-metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document twice, the way skill-draft-pr.test.sh names its two: the path as every
# problem message spells it, and the same path resolved for the probes to open. One constant
# for each, so a message can never name a file the probes did not read.
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

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

# records_of — the lines on stdin as records: the document's numbered steps, bullets and
# paragraphs, one per line and lowercased. A record runs from a `N. ` or a `- ` (indented or
# not) in column one, or from the first line after a blank, up to the next such line or the
# next blank; a fenced command block inside an item is part of that item's record, which is
# what lets a probe ask whether the instruction that opens the PR is the one carrying the
# command. Runs of whitespace collapse to one space, so a wrapped sentence reads as one, and
# case is folded last because the sentences are the writer's.
records_of() {
  awk '
    function flush() { if (rec != "") { gsub(/[[:space:]]+/, " ", rec); print rec } rec = "" }
    /^[0-9]+\. / || /^[[:space:]]*- / { flush(); rec = $0; next }
    /^[[:space:]]*$/ { flush(); next }
    rec == "" { rec = $0; next }
    { rec = rec " " $0 }
    END { flush() }' | tr '[:upper:]' '[:lower:]'
}

# section_records <heading prefix> <closer regex> — the records of the section whose heading
# STARTS WITH <heading prefix>, where a line matching <closer regex> is what ends one. Every
# read here is scoped to a section, because this document commits and comments on several
# paths: an unscoped read would answer the bail half with the PR half's instruction, and pass
# a document that delivered the report at only one of the run's two endings. Which headings
# close a section is the caller's, since the levels differ. A prefix rather than the whole
# heading because a heading may carry trailing prose after an em dash.
section_records() {
  awk -v h="$1" -v closers="$2" \
    '$0 ~ closers { inside = (index($0, h) == 1); next } inside' "$skill_path" | records_of
}

# first_record_line <records> <fixed string>… — the 1-based line number of the first record
# containing EVERY fixed string, or nothing. The line number is what makes "before the PR"
# askable: the records come out in document order, so comparing two of these compares two
# instructions' positions in the step.
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

# record_at <records> <n> — the nth record, for quoting in a problem message.
record_at() { sed -n "${2}p" <<< "$1"; }

# The criterion, as one case: the report is computed, committed and posted at whichever of
# the run's two endings it reaches. Each half is probed against its own section and each
# probe contributes its own problem line, so the output says which instruction is missing
# rather than only that something is.
name="$skill_md commits the metrics report and posts its 📊 block, on the PR path and on the bail path"
problems=()

# --- The PR path: `### 4. Draft PR`, which a heading of either level ends. -----------------
pr_records="$(section_records '### 4. Draft PR' '^## |^### ')"
if [[ -z "$pr_records" ]]; then
  problems+=("$skill_md has no ### 4. Draft PR section to read — whether the run delivers its metrics could not be checked")
else
  # The script by name: rendering the report by hand out of the event log would be a second
  # implementation of metrics.sh, and the one in scripts/ is the tested one.
  first_record_line "$pr_records" 'metrics.sh' >/dev/null ||
    problems+=("$skill_md's Draft PR step never runs metrics.sh, so the run's figures stay computable and uncomputed")

  # The commit, as the acceptance criterion spells it: one `metrics:` commit of the file
  # beside the ledger. Both strings of one record, because a commit verb in one instruction
  # and a filename in another is not an instruction to commit that file.
  first_record_line "$pr_records" 'metrics:' 'metrics.md' >/dev/null ||
    problems+=("$skill_md's Draft PR step has no instruction committing .tdd/issue-<n>-metrics.md in a metrics: commit, so the report is never beside the ledger it describes")

  # The PR itself, by its command: since #195 the PR is opened at the plan commit, so what
  # this step owes is the edit that puts the figures on it — without a `gh pr edit` the run
  # ends with a PR carrying none of the metrics it committed. Order is not asked here — a
  # record holds the whole sub-step, so the commit and the edit land in the same one (#267);
  # the fenced-line cases below read SKILL.md's command block directly, where the order is
  # expressible.
  first_record_line "$pr_records" 'gh pr edit' >/dev/null ||
    problems+=("$skill_md's Draft PR step never runs gh pr edit, so the run ends with no PR carrying the metrics it committed")

  # The block where a human reads a finished run: the closing comment. Asked of the record
  # carrying that comment's own command, so a mention of the block anywhere else in the step
  # cannot answer for it. The PR body's copy is not asked here — a record holds the whole
  # sub-step, so a block reaching the PR by a later gh pr edit would answer for the create
  # (#267); the fenced-line cases below read SKILL.md's command block directly instead.
  first_record_line "$pr_records" '✅ done' '📊 metrics' >/dev/null ||
    problems+=("$skill_md's final ✅ Done comment does not carry the ### 📊 Metrics block, so the issue thread ends without the run's figures")
fi

# --- The bail path: `## Bailing`, which any `##` heading ends. -----------------------------
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

# The criterion of issue #236, as one case: the Draft PR step closes the run's log with its
# `done` mark — the one carrying the opened PR's URL — BEFORE it renders the report it
# commits. metrics.sh reads that mark for both the Outcome line and the issue wall, so a
# report rendered while the log holds no ending says `unknown` for both, as #228's committed
# report and PR #234's body did. Asked of document order, the same way the commit-before-PR
# half above is: the records come out in the order the conductor follows them. Both records
# must exist first, so a step that dropped either fails closed rather than reading as ordered.
name="$skill_md's Draft PR step writes the run's done mark, carrying the PR URL, before rendering the metrics report it commits"
problems=()

# pr_records is the first case's read of the same section, reused rather than read again.
render_line="$(first_record_line "$pr_records" 'metrics.sh' '> .tdd/issue-<n>-metrics.md')" ||
  problems+=("$skill_md's Draft PR step never renders metrics.sh into .tdd/issue-<n>-metrics.md, so there is no committed report to order against the done mark")
done_line="$(first_record_line "$pr_records" 'event.sh done' 'pr=')" ||
  problems+=("$skill_md's Draft PR step never writes event.sh done pr=<pr-url>, so the report can never name the landed PR")
if [[ -n "${render_line:-}" && -n "${done_line:-}" && "$render_line" -lt "$done_line" ]]; then
  problems+=("$skill_md renders the committed metrics report BEFORE event.sh done, so its Outcome reads unknown instead of naming the landed PR: $(printf '%.120s' "$(record_at "$pr_records" "$render_line")")")
fi
report "$name"

# The third criterion of issue #236: the report a human reads — pasted into the PR body and
# into the closing `✅ Done` comment — is the one rendered AFTER `done` was written, taken
# from the committed file rather than from an earlier render. The step's command block is a
# single record, so record numbers cannot order its lines; this case orders by character
# offset in the section's records joined in document order instead. Every anchor must exist
# first, so a step that dropped one fails closed rather than reading as ordered.
name="$skill_md pastes into the PR body and the ✅ Done comment the committed report rendered after event.sh done"
problems=()

# offset_of <text> <fixed string> — the 0-based character offset of the first occurrence, or
# nothing (exit 1) when the string is absent.
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

# The PR body: the first `--body` that carries the committed file's contents, inside a
# `gh pr` command, after the render.
body_at="$(offset_of "$pr_text" 'contents of .tdd/issue-<n>-metrics.md')" ||
  problems+=("$skill_md's Draft PR step never puts the contents of .tdd/issue-<n>-metrics.md into the PR body")
if [[ -n "${body_at:-}" ]]; then
  body_cmd="${pr_text:0:$body_at}"
  body_cmd="gh pr ${body_cmd##*gh pr }"
  [[ "$body_cmd" == *"--body"* ]] ||
    problems+=("$skill_md mentions the contents of .tdd/issue-<n>-metrics.md outside a gh pr --body, so the PR body never gets the committed report")
  if [[ -n "${render_at:-}" && "$body_at" -lt "$render_at" ]]; then
    problems+=("$skill_md pastes the report into the PR body at offset $body_at, BEFORE it is rendered after done at offset $render_at: $(printf '%.120s' "$body_cmd")")
  fi
fi

# The closing comment: the `✅ Done` record carrying the 📊 block, after the render, and
# pasted from the committed file.
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

# Issue #240: since #236 the Draft PR step's commands share one fenced block, which
# records_of folds into a single record, so the first case's record comparison can no longer
# tell the metrics commit from the command that names the PR. This case reads the step's
# fenced command lines one by one, with their line numbers in SKILL.md, and orders those
# instead: the PR's URL is read first — since #195 from the PR the plan commit opened, not
# from a create of this step's own — and the `metrics:` commit follows it. Both anchors must
# exist first, so a step that dropped either fails closed rather than reading as ordered.
name="$skill_md's Draft PR command block reads the open PR's URL before the metrics: commit, ordered line by line"
problems=()

# fenced_lines — `<line number> <line>` for every line inside a ``` fence of the Draft PR
# section, in document order; the fence markers themselves are not printed.
fenced_lines() {
  awk '/^## |^### / { inside = (index($0, "### 4. Draft PR") == 1); fence = 0; next }
    !inside { next }
    /^[[:space:]]*```/ { fence = !fence; next }
    fence { print NR " " $0 }' "$skill_path"
}

# first_fenced_line <fixed string> — the SKILL.md line number of the first fenced line
# containing the string, or nothing (exit 1).
first_fenced_line() {
  local n rest
  while IFS=' ' read -r n rest; do
    [[ "$rest" == *"$1"* ]] && { echo "$n"; return 0; }
  done <<< "$(fenced_lines)"
  return 1
}

block_pr_line="$(first_fenced_line 'gh pr view')" ||
  problems+=("$skill_md's Draft PR command block never runs gh pr view to read the open PR's URL")
block_commit_line="$(first_fenced_line 'git commit -m "metrics:')" ||
  problems+=("$skill_md's Draft PR command block never runs git commit -m \"metrics: …\"")
if [[ -n "${block_pr_line:-}" && -n "${block_commit_line:-}" && "$block_commit_line" -lt "$block_pr_line" ]]; then
  problems+=("$skill_md commits the metrics report at SKILL.md:$block_commit_line, BEFORE gh pr view at SKILL.md:$block_pr_line, so the report is rendered and committed with no PR URL for the done mark to name")
fi
report "$name"

# Issue #240, second half of the order: the 📊 block reaches the PR body through `gh pr edit`,
# and that edit must come after the `metrics:` commit AND after `push-branch.sh`, or the body
# quotes a file the pushed branch does not yet carry. Ordered by SKILL.md line number, the
# way the case above orders gh pr create against the commit. Every anchor must exist first,
# so a step that dropped one fails closed rather than reading as ordered.
name="$skill_md's Draft PR command block runs gh pr edit after the metrics: commit and push-branch.sh, ordered line by line"
problems=()

block_edit_line="$(first_fenced_line 'gh pr edit')" ||
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

# Issue #240, the whole order at once: the two cases above each pin one pair, and this one
# walks the Draft PR command block's six commands in the order SKILL.md gives them — read the
# open PR's URL, write its done mark, render, commit, push, then put the report in the body — and asks
# that each sits on a later SKILL.md line than the one before it. Every anchor must exist
# first, so a step that dropped one fails closed rather than reading as ordered.
name="$skill_md's Draft PR command block runs gh pr view, event.sh done, metrics.sh, the metrics: commit, push-branch.sh and gh pr edit in that order"
problems=()

prev_anchor="" prev_line=""
for anchor in 'gh pr view' 'event.sh done pr=' 'metrics.sh <n>' 'git commit -m "metrics:' 'push-branch.sh' 'gh pr edit'; do
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

# Issue #240, the 📊-in-PR-body probe asked of the right command: since #236 the block reaches
# the PR body through `gh pr edit`, and the first case's record probe is answered by the whole
# command block, which holds `gh pr create` and a 📊 mention in the prose above it whether or
# not the edit carries the report. This case reads the fenced `gh pr edit` line itself and
# asks that its `--body` carries the contents of the committed report — the file metrics.sh
# writes, whose first line is the `### 📊 Metrics` heading.
name="$skill_md's Draft PR gh pr edit command puts the committed 📊 metrics report in the PR body"
problems=()

if ! edit_line="$(first_fenced_line 'gh pr edit')"; then
  problems+=("$skill_md's Draft PR command block never runs gh pr edit, so no command puts the 📊 block in the PR body")
else
  edit_cmd="$(sed -n "${edit_line}p" "$skill_path")"
  [[ "$edit_cmd" == *"--body"*".tdd/issue-<n>-metrics.md"* ]] ||
    problems+=("$skill_md's gh pr edit at SKILL.md:$edit_line does not put the contents of .tdd/issue-<n>-metrics.md in its --body, so the PR body never gets the 📊 block: $(printf '%.120s' "$edit_cmd")")
fi
report "$name"

# Issue #240, the suite's own statement of the contract: the header's `Contract under test`
# paragraph is what a reader takes the cases to pin, so it must name the post-#236 Draft PR
# order rather than the commit-before-PR order #236 replaced. The paragraph is read as text,
# its comment markers stripped and its wrapped lines joined, and its commands must appear in
# the order the step runs them. A missing anchor is a problem of its own and leaves the last
# found one in place, so an old paragraph still reports what it orders wrongly.
name="skill-metrics.test.sh's header comment states the Draft PR order gh pr view, event.sh done, metrics.sh, the metrics: commit, push-branch.sh, gh pr edit"
problems=()

suite_md="skills/tdd/scripts/tests/skill-metrics.test.sh"
contract="$(awk '/^# Contract under test/ { on = 1 } on && !/^#/ { exit } on && /^#[[:space:]]*$/ { exit }
  on { sub(/^#[[:space:]]*/, ""); printf "%s ", $0 }' "$ROOT/$suite_md")"
if [[ -z "$contract" ]]; then
  problems+=("$suite_md has no Contract under test paragraph in its header to read")
else
  prev_anchor="" prev_at=""
  for anchor in 'gh pr view' 'event.sh done' 'metrics.sh' 'metrics:' 'push-branch.sh' 'gh pr edit'; do
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

# The suite's own source, read once for the two #267 cases below: both ask that a dead
# record-level check has not come back, and neither writes to the file between the reads.
suite_src="$(cat "$ROOT/$suite_md")"

# Issue #267: the record-level commit-before-PR check this suite used to carry could not
# fail. section_records folds the whole Draft PR sub-step — its prose and its fenced command
# block — into ONE record, so the metrics commit's record number and gh pr create's are the
# same number, and a greater-than between them is false whatever order the step runs. A check
# that cannot fail reports coverage the suite does not have; the fenced-line cases above pin
# that ordering for real, at the granularity where it is expressible. This case reads the
# suite's own source and asks that neither the comparison nor the comment claiming it catches
# a metrics commit made after the PR is opened has come back. Both needles are assembled from
# two pieces at runtime, so the lines writing them here can never answer for the lines they
# are looking for.
name="skill-metrics.test.sh carries no record-level commit-before-PR comparison, which records_of's folding makes dead"
problems=()

dead_compare='commit_line" '"-gt"' "$pr_line'
dead_comment='lands '"BEFORE"' the PR is opened'
[[ "$suite_src" != *"$dead_compare"* ]] ||
  problems+=("$suite_md compares the metrics commit's record number against gh pr create's with a greater-than, but section_records folds both into the same record, so the check cannot fail and reports coverage the suite does not have")
[[ "$suite_src" != *"$dead_comment"* ]] ||
  problems+=("$suite_md still carries the comment claiming a record-level probe catches a metrics commit made after the PR is opened, which the folding makes impossible")
report "$name"

# Issue #267: the second dead record-level check, for the same reason as the one above. The
# probe asked whether the record carrying `gh pr create` also carries the metrics block, and
# claimed that a create whose --body omits it fails the suite. It cannot: section_records
# folds the whole Draft PR sub-step into ONE record, so the block reaching the PR by the
# `gh pr edit` two instructions later satisfies a probe aimed at the create. Today's SKILL.md
# is exactly that shape and the suite was green. The fenced-line cases above read the command
# block directly, where that question is expressible. This case reads the suite's own source
# and asks that the probe has not come back. Its needle is assembled from three pieces at
# runtime, so the lines writing it here can never answer for the line it is looking for.
name="skill-metrics.test.sh carries no record-level gh pr create + 📊 metrics presence probe, which records_of's folding makes dead"
problems=()

probe_call='first_record_line "$pr_records" '
create_arg="'gh pr create'"
block_arg="'📊 metrics'"
[[ "$suite_src" != *"$probe_call$create_arg $block_arg"* ]] ||
  problems+=("$suite_md still asks whether the record holding gh pr create also holds the 📊 metrics block, but section_records folds the whole Draft PR sub-step into one record, so a block carried by a later gh pr edit answers for the create and the probe cannot fail")
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
