#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor about the commit of the
# skill a run is executing. Like skill-timeout.test.sh and skill-test-command.test.sh this
# suite belongs to no single script: its subject is the procedure document, read as text,
# the way the session that follows it reads it. Picked up by `make test`'s glob by existing.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Why this exists (issue #165): why a run needs the skill's commit recorded at all is
# event.sh's header, the one place this cycle states it, and why the plan comment is where
# a human needs it is the step under test itself. What is this suite's to say is that the
# instruction is prose and so can only be pinned as prose: `supervise.sh` records the sha
# per launch, but nothing launches the conductor — the comment it posts exists only because
# SKILL.md tells it to, so a document that stops saying so is the whole of the regression.
#
# Contract under test (this step only):
#   SKILL.md's plan-comment step says that comment names the skill commit the run started
#   on, beside the test command and the timeout it already states.
#   SKILL.md's own account of `$S` says the directory tracks the installed skill and so can
#   change under a running conductor, and names the event log as what records which commit
#   each leaf was launched under.
#
# Run: scripts/tests/skill-commit.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"

sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  local next
  next="$(head -1 < <(tail -n "+$((sec_start + 1))" "$md" | grep -nE '^#') | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    sec_end=$((sec_start + next - 1))
  else
    sec_end=$(($(wc -l < "$md")))
  fi
  return 0
}

sec_name=""
need_section() {
  section "$1" || { problems+=("$skill_md has no '$1' section — $2"); return 1; }
  sec_name="${1##*# }"
  return 0
}

items() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
    rec != "" { rec = rec " " $0 }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

name="$skill_md's plan comment names the skill commit the run started on"
problems=()

if need_section '### 2. Scope & plan' 'what the plan comment states could not be read'; then
  plan_item="$(items | grep -E 'plan.*comment')"
  if [[ -z "$plan_item" ]]; then
    problems+=("$skill_md's 'Scope & plan' section has no numbered item posting the plan comment — what that comment states could not be read")
  else
    for re in 'skill' 'commit'; do
      grep -qE "$re" <<< "$plan_item" ||
        problems+=("$skill_md's plan-comment item never says '$re', so the comment does not name the skill commit the run started on and the thread cannot say which version produced it: $(printf '%.120s' "$plan_item")")
    done
  fi
fi
report "$name"

paragraphs() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^#/ { next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; in_item = 0; next }
    /^([0-9]+\.|[-*]) / { in_item = 1; next }
    in_item { next }
    { rec = (rec == "" ? $0 : rec " " $0) }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

claim() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$paras"
  problems+=("$skill_md's '$sec_name' prose: no paragraph $what")
}

need_scripts_prose() {
  need_section '## The scripts' 'what the document says about the directory $S points at could not be read' ||
    return 1
  paras="$(paragraphs)"
  [[ -n "$paras" ]] && return 0
  problems+=("$skill_md's 'The scripts' section has no prose paragraphs — what it says about \$S could not be read")
  return 1
}

name="$skill_md says what a change to the skill means for a running conductor, and that the event log records each leaf's commit"
problems=()

if need_scripts_prose; then
  claim 'says the installed skill can change under a running conductor' \
    'chang|move|update' 'conductor|mid-run|running|under a run'
  claim 'names the event log as what records which commit each leaf used' \
    'event log|events\.jsonl' 'commit'
fi
report "$name"

claude_md="CLAUDE.md"
name="$skill_md documents the skill snapshot, VERI_NEW_SKILL and .tdd/issue-<n>-skill-commit, and $claude_md cross-references them"
problems=()

for doc in "$skill_md" "$claude_md"; do
  text="$(tr -d '*`' < "$ROOT/$doc" | tr '[:upper:]' '[:lower:]')"
  if [[ -z "$text" ]]; then
    problems+=("$doc could not be read, so nothing could be asked of what it records")
    continue
  fi
  for term in 'skill snapshot' 'veri_new_skill' 'issue-[^[:space:]/]+-skill-commit'; do
    grep -qE "$term" <<< "$text" ||
      problems+=("$doc never mentions /$term/, so a reader cannot find the skill snapshot a launch pins or refuses on")
  done
done
report "$name"

name="$skill_md's \$S paragraph no longer says nothing pins it, and says the skill snapshot (VERI_SKILL_COMMIT, .tdd/issue-<n>-skill-commit) pins the commit a run executes under"
problems=()

if need_scripts_prose; then
  stale="$(grep -F 'nothing here pins it' <<< "$paras")"
  [[ -z "$stale" ]] ||
    problems+=("$skill_md's '$sec_name' prose still says 'nothing here pins it', contradicting the skill snapshot run-conductor.sh enforces: $(printf '%.120s' "$stale")")
  claim 'about $S says the skill snapshot (VERI_SKILL_COMMIT, .tdd/issue-<n>-skill-commit) pins the commit a run executes under' \
    '\$s' 'pin' 'veri_skill_commit' 'issue-[^[:space:]/]+-skill-commit'
fi
report "$name"

finish
