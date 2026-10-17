#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor to do with the run's metrics
# report, at both of the run's endings, read as text.
#
# Contract under test:
#   SKILL.md's `### 4. Draft PR` step runs, in this order, `gh api …/pulls?head=` for the URL
#   of the PR the plan commit already opened, `event.sh done pr=<pr-url>`, `metrics.sh`, a
#   `metrics:` commit of `.tdd/issue-<n>-metrics.md`, `push-branch.sh`, and `gh api -X PATCH`,
#   which carries the `### 📊 Metrics` block into the PR body; the same block goes into the
#   final `✅ Done` comment; SKILL.md's `## Bailing` section commits the same file on the
#   pushed branch and puts the block on the `⛔ Bailed` comment.
#
# Run: scripts/tests/skill-metrics.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/fenced-lines.sh"

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

pr_records="$(section_records '### 4. Draft PR' '^## |^### ')"
bail_records="$(section_records '## Bailing' '^## ')"

offset_of() {
  [[ "$1" == *"$2"* ]] || return 1
  local before="${1%%"$2"*}"
  echo "${#before}"
}

first_fenced_line() {
  local n rest
  while IFS=$'\t' read -r n rest; do
    [[ "$rest" == *"$1"* ]] && { echo "$n"; return 0; }
  done <<< "$(fenced_lines "$skill_path" '' '### 4. Draft PR')"
  return 1
}

pr_read='pulls?head='
pr_edit='gh api -X PATCH'

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

name="#566: $skill_md's Draft PR step makes the metrics: commit only on a metrics.sh exit of 0, and otherwise puts the failed render and its exit code in the PR body"
problems=()

render_status=""
if ! render_line="$(first_fenced_line 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')"; then
  problems+=("$skill_md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
else
  render_cmd="$(sed -n "${render_line}p" "$skill_path")"
  if [[ "$render_cmd" =~ ([A-Za-z_][A-Za-z0-9_]*)=\$\? ]]; then
    render_status="${BASH_REMATCH[1]}"
  else
    problems+=("$skill_md renders metrics.sh at SKILL.md:$render_line without capturing its exit status, so nothing can keep a failed render out of the metrics: commit: $(printf '%.120s' "$render_cmd")")
  fi
fi

if ! commit_line="$(first_fenced_line 'git commit -m "metrics:')"; then
  problems+=("$skill_md's Draft PR command block never runs git commit -m \"metrics: …\"")
elif [[ -n "$render_status" ]]; then
  gated=0 open_if=0
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*if[[:space:]].*\$\{?$render_status([^A-Za-z0-9_]|$) ]] && open_if=1
    [[ "$line" =~ ^[[:space:]]*fi([[:space:];]|$) ]] && open_if=0
  done < <(sed -n "$((render_line + 1)),$((commit_line - 1))p" "$skill_path")
  commit_cmd="$(sed -n "${commit_line}p" "$skill_path")"
  [[ "$commit_cmd" =~ \$\{?$render_status([^A-Za-z0-9_]|$) ]] && gated=1
  [[ "$open_if" -eq 1 ]] && gated=1
  [[ "$gated" -eq 1 ]] ||
    problems+=("$skill_md runs the metrics: commit at SKILL.md:$commit_line whatever \$$render_status, metrics.sh's exit status, says, so a failed render's partial report is committed: $(printf '%.120s' "$commit_cmd")")
fi

if ! edit_line="$(first_fenced_line "$pr_edit")"; then
  problems+=("$skill_md's Draft PR command block never runs gh api -X PATCH, so no PR body can name a failed render")
else
  edit_cmd="$(sed -n "${edit_line}p" "$skill_path" | tr '[:upper:]' '[:lower:]')"
  [[ "$edit_cmd" == *"-f body="*"metrics.sh"*"exit"* ]] ||
    problems+=("$skill_md's gh api -X PATCH at SKILL.md:$edit_line puts no line naming a failed metrics.sh render and its exit code in the PR body, so a failed render leaves the body quoting a report that was never committed: $(printf '%.120s' "$edit_cmd")")
fi
report "$name"

name="#566: $skill_md's Draft PR step, on a non-zero metrics.sh exit, puts the failed render and its exit code in the ✅ Done comment in place of the 📊 Metrics block"
problems=()

done_status=""
if ! done_render_line="$(first_fenced_line 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')"; then
  problems+=("$skill_md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
elif [[ "$(sed -n "${done_render_line}p" "$skill_path")" =~ ([A-Za-z_][A-Za-z0-9_]*)=\$\? ]]; then
  done_status="$(tr '[:upper:]' '[:lower:]' <<< "${BASH_REMATCH[1]}")"
else
  problems+=("$skill_md renders metrics.sh at SKILL.md:$done_render_line without capturing its exit status, so no ✅ Done comment can name it")
fi

if ! done_record_line="$(first_record_line "$pr_records" '✅ done' '📊 metrics')"; then
  problems+=("$skill_md's Draft PR step has no ✅ Done comment carrying the 📊 Metrics block")
elif [[ -n "$done_status" ]]; then
  done_record="$(record_at "$pr_records" "$done_record_line")"
  [[ "$done_record" == *"metrics.sh"* && "$done_record" =~ \$\{?$done_status([^a-z0-9_]|$) ]] ||
    problems+=("$skill_md's ✅ Done comment carries no line naming a failed metrics.sh render and its exit code (\$$done_status), so a failed render leaves the comment pasting a report that was never committed: $(printf '%.160s' "$done_record")")
fi
report "$name"

name="#566: $skill_md's Bailing sub-step 4 makes the metrics: commit only on a metrics.sh exit of 0, and otherwise the ⛔ Bailed comment carries the failed render and its exit code in place of the 📊 Metrics block"
problems=()

bail_status=""
if ! bail_render_line="$(first_record_line "$bail_records" 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')"; then
  problems+=("$skill_md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
else
  bail_render="$(record_at "$bail_records" "$bail_render_line")"
  if [[ "$bail_render" =~ ([a-z_][a-z0-9_]*)=\$\? ]]; then
    bail_status="${BASH_REMATCH[1]}"
    after_capture="${bail_render#*"$bail_status"=\$\?}"
    before_commit="${after_capture%%'git commit -m "metrics:'*}"
    [[ "$after_capture" == *'git commit -m "metrics:'* && "$before_commit" =~ \$\{?\"?$bail_status([^a-z0-9_]|$) ]] ||
      problems+=("$skill_md's Bailing section makes the metrics: commit in record $bail_render_line whatever \$$bail_status, metrics.sh's exit status, says, so a failed render's partial report is committed: $(printf '%.160s' "$bail_render")")
  else
    problems+=("$skill_md renders metrics.sh in Bailing record $bail_render_line without capturing its exit status, so nothing can keep a failed render out of the metrics: commit: $(printf '%.160s' "$bail_render")")
  fi
fi

if ! bailed_line="$(first_record_line "$bail_records" '⛔ bailed' '📊 metrics')"; then
  problems+=("$skill_md's Bailing section has no ⛔ Bailed comment carrying the 📊 Metrics block")
elif [[ -n "$bail_status" ]]; then
  bailed_record="$(record_at "$bail_records" "$bailed_line")"
  [[ "$bailed_record" == *"metrics.sh"* && "$bailed_record" =~ \$\{?$bail_status([^a-z0-9_]|$) ]] ||
    problems+=("$skill_md's ⛔ Bailed comment carries no line naming a failed metrics.sh render and its exit code (\$$bail_status) in place of the 📊 Metrics block: $(printf '%.160s' "$bailed_record")")
fi
report "$name"

name="#566: $skill_md's Draft PR step, on a non-zero metrics.sh exit, neither bails nor stops: it goes on to push-branch.sh and gh api -X PATCH"
problems=()

go_status=""
if ! go_render_line="$(first_fenced_line 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')"; then
  problems+=("$skill_md's Draft PR command block never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
elif [[ "$(sed -n "${go_render_line}p" "$skill_path")" =~ ([A-Za-z_][A-Za-z0-9_]*)=\$\? ]]; then
  go_status="${BASH_REMATCH[1]}"
else
  problems+=("$skill_md renders metrics.sh at SKILL.md:$go_render_line without capturing its exit status")
fi
go_push_line="$(first_fenced_line 'push-branch.sh')" ||
  problems+=("$skill_md's Draft PR command block never runs push-branch.sh")
go_edit_line="$(first_fenced_line "$pr_edit")" ||
  problems+=("$skill_md's Draft PR command block never runs gh api -X PATCH")

if [[ -n "$go_status" && -n "${go_push_line:-}" && -n "${go_edit_line:-}" ]]; then
  gated_ifs=0
  while IFS=$'\t' read -r n text; do
    (( n > go_render_line && n <= go_edit_line )) || continue
    mentions=0
    [[ "$text" =~ \$\{?$go_status([^A-Za-z0-9_]|$) ]] && mentions=1
    if [[ "$text" =~ ^[[:space:]]*if[[:space:]] ]]; then
      [[ "$mentions" -eq 1 || "$gated_ifs" -gt 0 ]] && gated_ifs=$((gated_ifs + 1))
    elif [[ "$text" =~ ^[[:space:]]*fi([[:space:];]|$) && "$gated_ifs" -gt 0 ]]; then
      gated_ifs=$((gated_ifs - 1))
    fi
    if [[ "$mentions" -eq 1 && "$text" =~ (event\.sh[[:space:]]+bail|(^|[^A-Za-z0-9_-])(exit|return)([^A-Za-z0-9_-]|$)) ]]; then
      problems+=("$skill_md stops or bails on \$$go_status, metrics.sh's exit status, at SKILL.md:$n, so a failed render ends the Draft PR step instead of reaching its push and PR body rewrite: $(printf '%.120s' "$text")")
    fi
    if [[ "$n" -eq "$go_push_line" || "$n" -eq "$go_edit_line" ]]; then
      [[ "$gated_ifs" -eq 0 ]] ||
        problems+=("$skill_md runs SKILL.md:$n inside an if on \$$go_status, so a non-zero metrics.sh exit skips it: $(printf '%.120s' "$text")")
      [[ "$text" =~ ^[[:space:]]*(\$S/push-branch\.sh|gh[[:space:]]+api[[:space:]]+-X[[:space:]]+PATCH) ]] ||
        problems+=("$skill_md guards SKILL.md:$n behind a condition, so a non-zero metrics.sh exit may skip it: $(printf '%.120s' "$text")")
    fi
  done <<< "$(fenced_lines "$skill_path" '' '### 4. Draft PR')"
fi
report "$name"

name="#566: $skill_md's Bailing sub-step 4, on a non-zero metrics.sh exit, does not stop the bail: it goes on to sub-step 5's push and sub-step 6's ⛔ Bailed comment"
problems=()

bs_status=""
if ! bs_render_line="$(first_record_line "$bail_records" 'metrics.sh <n> > .tdd/issue-<n>-metrics.md')"; then
  problems+=("$skill_md's Bailing section never renders metrics.sh <n> > .tdd/issue-<n>-metrics.md")
else
  bs_render="$(record_at "$bail_records" "$bs_render_line")"
  if [[ "$bs_render" =~ ([a-z_][a-z0-9_]*)=\$\? ]]; then
    bs_status="${BASH_REMATCH[1]}"
    [[ "$bs_render" =~ ^4\. ]] ||
      problems+=("$skill_md renders metrics.sh in Bailing record $bs_render_line, which is not sub-step 4: $(printf '%.120s' "$bs_render")")
    after_capture="${bs_render#*"$bs_status"=\$\?}"
    [[ "$after_capture" =~ (event\.sh[[:space:]]+bail|(^|[^a-z0-9_-])(exit|return|stop|stops|skip|skips|abort|aborts)([^a-z0-9_-]|$)) ]] &&
      problems+=("$skill_md's Bailing sub-step 4 stops or skips on \$$bs_status, metrics.sh's exit status, so a failed render ends the bail before its push and comment: $(printf '%.160s' "$after_capture")")
  else
    problems+=("$skill_md renders metrics.sh in Bailing record $bs_render_line without capturing its exit status")
  fi
fi

if [[ -n "$bs_status" ]]; then
  if ! bs_push_line="$(first_record_line "$bail_records" 'git push')"; then
    problems+=("$skill_md's Bailing section never pushes the branch")
  else
    bs_push="$(record_at "$bail_records" "$bs_push_line")"
    [[ "$bs_push" =~ ^5\. && "$bs_push_line" -gt "$bs_render_line" ]] ||
      problems+=("$skill_md's Bailing push is not sub-step 5, after the metrics render in record $bs_render_line: $(printf '%.120s' "$bs_push")")
    [[ "$bs_push" =~ \$\{?$bs_status([^a-z0-9_]|$) ]] &&
      problems+=("$skill_md's Bailing sub-step 5 push is conditioned on \$$bs_status, so a non-zero metrics.sh exit may skip it: $(printf '%.160s' "$bs_push")")
  fi
  if ! bs_bailed_line="$(first_record_line "$bail_records" '⛔ bailed' '📊 metrics')"; then
    problems+=("$skill_md's Bailing section has no ⛔ Bailed comment carrying the 📊 Metrics block")
  else
    bs_bailed="$(record_at "$bail_records" "$bs_bailed_line")"
    [[ "$bs_bailed" =~ ^6\. && "$bs_bailed_line" -gt "$bs_render_line" ]] ||
      problems+=("$skill_md's ⛔ Bailed comment is not sub-step 6, after the metrics render in record $bs_render_line: $(printf '%.120s' "$bs_bailed")")
    [[ "$bs_bailed" =~ (^|[^a-z0-9_-])(stop|stops|skip|skips|omit|abort|aborts)([^a-z0-9_-]|$) ]] &&
      problems+=("$skill_md's ⛔ Bailed comment in sub-step 6 is skipped or stopped on a failed render: $(printf '%.160s' "$bs_bailed")")
  fi
fi
report "$name"

finish
