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
#   SKILL.md's `### 4. Draft PR` step runs `metrics.sh`, commits `.tdd/issue-<n>-metrics.md`
#   in a `metrics:` commit BEFORE `gh pr create`, and carries the `### 📊 Metrics` block into
#   both the PR body and the final `✅ Done` comment; SKILL.md's `## Bailing` section commits
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
  commit_line="$(first_record_line "$pr_records" 'metrics:' 'metrics.md')" ||
    problems+=("$skill_md's Draft PR step has no instruction committing .tdd/issue-<n>-metrics.md in a metrics: commit, so the report is never beside the ledger it describes")

  # …and it lands BEFORE the PR is opened, which is what keeps the branch the human is
  # asked to look at from being one commit short of the report its body quotes.
  pr_line="$(first_record_line "$pr_records" 'gh pr create')" ||
    problems+=("$skill_md's Draft PR step never runs gh pr create, so there is no PR for the metrics commit to precede")
  if [[ -n "${commit_line:-}" && -n "${pr_line:-}" && "$commit_line" -gt "$pr_line" ]]; then
    problems+=("$skill_md commits the metrics report AFTER gh pr create, so the PR is opened on a branch missing the file its body quotes: $(printf '%.120s' "$(record_at "$pr_records" "$commit_line")")")
  fi

  # The block, in the two places a human reads a finished run: the PR body and the final
  # comment. Each is asked of the record carrying that instruction's own command, so a
  # mention of the block anywhere in the step cannot answer for either.
  first_record_line "$pr_records" 'gh pr create' '📊 metrics' >/dev/null ||
    problems+=("$skill_md's gh pr create instruction does not put the ### 📊 Metrics block in the PR body, so a reviewer reads the PR without what the run cost")
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
