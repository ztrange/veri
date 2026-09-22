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
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The document under test, twice: the path as it is quoted in every failure message, and
# the same path resolved for the probes to read. Both spellings come from one constant, so
# a message can never name a file the probes did not open.
skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

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

# section <heading> — the line range of the first heading that STARTS WITH the literal
# <heading>, up to the line before the next heading of any level, into `sec_start` and
# `sec_end`. Returns non-zero when no such heading exists, so a renamed section is reported
# rather than silently probed as an empty range — the fail-closed half that keeps "the
# section is gone" from reading as "the section says nothing wrong". A literal prefix
# rather than a regex because every heading here carries trailing prose after an em dash,
# so the prefix is what identifies it and is quotable in the message about not finding it.
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

# need_section <heading> <consequence> — select the section under <heading>, or push one
# problem naming it and return non-zero. One constant for both the pattern searched for and
# the message about not finding it, so a message can never name a heading nothing looked for.
# On success it also leaves the heading, stripped of its `#`s, in `sec_name`, which is how a
# claim below names the section it failed in: the same rule one step further on, since a
# claim that spelled the heading itself could name a section nothing had selected.
sec_name=""
need_section() {
  section "$1" || { problems+=("$skill_md has no '$1' section — $2"); return 1; }
  sec_name="${1##*# }"
  return 0
}

# items — the current section's numbered list items, one per line and lowercased: a `N. `
# in column one plus the indented lines continuing it, up to the next such line or a blank
# one. Joining an item onto one line is what lets the claim ask whether ONE instruction
# carries the fact, rather than two sentences elsewhere in the section that happen to share
# a word. Case is folded last, because the sentences are the writer's.
items() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
    rec != "" { rec = rec " " $0 }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

# 1. The criterion, as one case: the comment a human reads before the first leaf names the
#    version of the skill the run started on. The plan comment is the anchor because it is
#    the one the conductor posts at scoping time and the one that already carries the run's
#    other two facts — the test command and the timeout; a sha recorded only in the event
#    log is not on the thread, which is where the narration it has to be read against is.
#
#    Both halves are asked of the same joined item, and each regex accepts any wording that
#    carries the fact: what is pinned is that the document says it, not how it is phrased.
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

# paragraphs — the current section's PROSE, one paragraph per line and lowercased: runs of
# non-blank lines that are neither a heading nor part of a list item, joined. The list is
# cut out on purpose. The `$S/event.sh` bullet already names the event log, describing what
# that script appends; the claim below is about what the document tells a reader about the
# directory `$S` points at, which is prose or it is nowhere — so a bullet must not be able
# to answer for it. `in_item` is what carries a bullet's indented continuation lines, since
# those are not blank and would otherwise read as prose.
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

# claim <what one paragraph must say> <regex>… — assert that a single line of the global
# `paras` matches every <regex>, recording a problem naming <what> otherwise. All of a
# claim's regexes are asked of ONE paragraph because a pair split across two is not a
# statement: the fact only reaches the reader if the sentence that raises the risk is the
# one that says where the answer is recorded. `continue 2` takes the next paragraph, so a
# paragraph matching some but not all of a pair is simply not the one.
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

# need_scripts_prose — select '## The scripts' and load its prose into `paras`, or push one
# problem and return non-zero: the section is missing, or it has no prose paragraph to ask.
# Cases 2 and 4 both ask what that prose says about the directory `$S` points at.
need_scripts_prose() {
  need_section '## The scripts' 'what the document says about the directory $S points at could not be read' ||
    return 1
  paras="$(paragraphs)"
  [[ -n "$paras" ]] && return 0
  problems+=("$skill_md's 'The scripts' section has no prose paragraphs — what it says about \$S could not be read")
  return 1
}

# 2. What the document tells the conductor about the ground it is standing on. `$S` is the
#    installed skill, which here is a symlink into a clone that `main` moves under it, so a
#    run can execute one commit's scripts under another commit's prose. Nothing in the
#    procedure prevents that — this cycle's decision was to record the version rather than
#    pin it — so the document must say both halves: that the ground moves, and where a
#    reader goes to find out whether it moved under their run. A session told only the
#    first has been warned of a hazard it cannot check.
name="$skill_md says what a change to the skill means for a running conductor, and that the event log records each leaf's commit"
problems=()

if need_scripts_prose; then
  claim 'says the installed skill can change under a running conductor' \
    'chang|move|update' 'conductor|mid-run|running|under a run'
  claim 'names the event log as what records which commit each leaf used' \
    'event log|events\.jsonl' 'commit'
fi
report "$name"

# 3. The skill snapshot itself (issue #253): run-conductor.sh pins the skill a run executes
#    to the commit recorded in `.tdd/issue-<n>-skill-commit`, and taking a newer skill is
#    the explicit act `VERI_NEW_SKILL=1`. A mechanism that refuses a launch is one an
#    operator has to be able to look up, so SKILL.md documents it and CLAUDE.md — the first
#    thing an agent reads — points at it. Asked of each whole document, backticks and emphasis
#    dropped and case folded: where in the file the terms sit, and how they are phrased, is
#    the writer's; that all three are there is the claim. The file name is accepted with any
#    placeholder for the issue number, since `<n>` and `N` are both spellings of the same path.
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

# 4. Case 2's paragraph, reconciled with case 3's mechanism (issue #265): once #253 made
#    run-conductor.sh pin every launch to a recorded commit, "Nothing here pins it" in the
#    `$S` paragraph became false, and a conductor reading the two sections was told both.
#    So the stale sentence must be gone from the section's prose, and a paragraph that talks
#    about `$S` must name what does pin it — the exported `VERI_SKILL_COMMIT` and the
#    `.tdd/issue-<n>-skill-commit` record — in the same statement as the word "pin". Asked of
#    one paragraph for the reason `claim` gives; the file name takes any issue placeholder.
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
