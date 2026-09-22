#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor about the run's test
# command. Like skill-identity.test.sh and hermetic-suites.test.sh this suite belongs to
# no single script: its subject is the procedure document those scripts are called from,
# read as text, exactly the way skill-identity.test.sh reads the same file for the skill's
# name.
# Zero-dependency plain-shell asserts, same idiom as skill-identity.test.sh.
#
# Why this exists (issue #120): detect-test-command.sh now takes `--issue <body-file>` and
# answers the issue's own `Test command:` line ahead of `.veri/test-command` and every
# inference — but a flag no instruction ever passes changes nothing about a run. There is
# no script that calls the conductor; the conductor is prose, so the wiring can only be
# pinned as prose. On #71 the gap cost a docs issue two suites on every check: the prompt
# said `make test` while the issue's notes said `make docs-test`, and every leaf ran both.
#
# Contract under test:
#   Preflight reads the issue body and hands it to detect-test-command.sh as `--issue`,
#   in that order, so the issue's own command is in hand before the baseline run.
#   The section that defines <test-cmd> for every leaf detects it the same way, so the
#   command the leaves get is the command the issue named.
#   The plan comment states the test command the run will use, so a wrong one is visible
#   before the first leaf.
#
# Run: scripts/tests/skill-test-command.test.sh
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

# section <heading> — select the lines under the first heading that STARTS WITH the literal
# <heading>, up to the line before the next heading of any level, into the globals
# `sec_start` and `sec_end`. Returns non-zero when no such heading exists, so a renamed
# section is reported rather than silently probed as an empty range — the fail-closed half
# that keeps "the section is gone" from reading as "the section says nothing wrong".
#
# A literal prefix rather than a regex: every heading here carries trailing prose after an
# em dash or an arrow, so the prefix is what identifies it, and a literal is what lets
# `need_section` below quote the same string it searched for.
#
# The section is a LINE RANGE rather than the text itself because one claim below is about
# order: the issue body has to be read before the command is detected, and line numbers are
# what make "before" answerable.
sec_start=0 sec_end=0
section() {
  sec_start="$(awk -v h="$1" 'index($0, h) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  # The next heading, counted from the line after this one so the section's own heading
  # cannot close it; none means the section runs to the end of the file.
  local next
  next="$(head -1 < <(tail -n "+$((sec_start + 1))" "$md" | grep -nE '^#') | cut -d: -f1)"
  if [[ -n "$next" ]]; then
    sec_end=$((sec_start + next - 1))
  else
    sec_end=$(($(wc -l < "$md")))
  fi
  return 0
}

# need_section <heading> <consequence> — select the section under <heading> (see `section`),
# or push one problem naming it and return non-zero. Each of the three cases below opens the
# same way, and each used to spell its heading twice: once as the pattern to search for and
# once inside the message about not finding it. One constant for both, the same trick
# `skill_md`/`md` plays above, is what stops a message from naming a heading the probe never
# looked for.
need_section() {
  section "$1" && return 0
  problems+=("$skill_md has no '$1' section — $2")
  return 1
}

# at <regex> — the line number of the first line of the current section matching <regex>,
# empty when none does. Every probe below asks the same question of a different pattern,
# and two of them then compare the answers.
at() {
  awk -v s="$sec_start" -v e="$sec_end" -v re="$1" \
    'NR >= s && NR <= e && $0 ~ re { print NR; exit }' "$md"
}

# line_at <n> — the text of line <n>, for a message that has to quote the offending line.
line_at() { sed -n "${1}p" "$md"; }

# items — the current section's numbered list items, one per line and lowercased: a `N. `
# in column one plus the indented lines continuing it, up to the next such line or a blank
# one. Joining an item onto one line is what lets a claim ask whether ONE instruction says
# both halves, rather than two sentences elsewhere in the section that happen to share a
# word. Case is folded last, because the sentences are the writer's.
items() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
    rec != "" { rec = rec " " $0 }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

# 1. The three halves of one criterion: where the issue's command is read, that it is the
#    command every leaf then gets, and that the run says out loud which one it picked.
#    They are one case because they are one wiring — a preflight that reads the body but a
#    <test-cmd> defined without it, or either without the plan comment naming the result,
#    leaves the run doing what #71 did — and because the fix to any of them is one edit to
#    one document.
name="$skill_md detects the run's test command from the issue body in preflight, gives it to every leaf, and names it in the plan comment"
problems=()

# The baseline is preflight's, and preflight is what runs before any cycle — so the issue
# body has to be read there, ahead of the detection, and not at step 1.3 where the blind
# spec is written. Both facts are asked of this one section, in its own order.
if need_section '### 0. Preflight' 'where the baseline reads its test command could not be read'; then
  detect_at="$(at 'detect-test-command\.sh')"
  body_at="$(at 'gh issue view')"
  if [[ -z "$detect_at" ]]; then
    problems+=("$skill_md preflight never names detect-test-command.sh, so the baseline runs a command from nowhere")
  else
    # The offending line, read once and named, so the test and the message it quotes are
    # provably the same string — and so this probe reads like its two siblings below
    # rather than as a `case` whose matching arm does nothing.
    detect_line="$(line_at "$detect_at")"
    [[ "$detect_line" == *--issue* ]] ||
      problems+=("$skill_md:$detect_at detects the test command without --issue, so the issue's own line cannot answer: $detect_line")
  fi
  if [[ -z "$body_at" ]]; then
    problems+=("$skill_md preflight never reads the issue body (no gh issue view), so there is no body file to pass as --issue")
  elif [[ -n "$detect_at" ]] && [[ "$body_at" -gt "$detect_at" ]]; then
    problems+=("$skill_md reads the issue body at line $body_at, after detecting the test command at line $detect_at — the baseline runs before the issue's line is known")
  fi
fi

# The section that defines <test-cmd> for the whole run. Preflight's own call is only the
# baseline; this is where the document says that one stdout is what every leaf's prompt
# carries, so a detection spelled without --issue here hands the leaves a different
# command from the one the baseline just used.
if need_section '## Detecting the test command' 'how <test-cmd> is obtained could not be read'; then
  [[ -n "$(at '--issue')" ]] ||
    problems+=("$skill_md's 'Detecting the test command' section never names --issue, so <test-cmd> — what every leaf runs — is detected without the issue's line")
fi

# And the run says which command it picked, in the comment a human reads before the first
# leaf starts. The plan comment is the anchor because that is the one the conductor posts
# at scoping time; a command named only in the ledger is not visible on the thread.
if need_section '### 2. Scope & plan' 'what the plan comment states could not be read'; then
  plan_item="$(items | grep -E 'plan.*comment')"
  if [[ -z "$plan_item" ]]; then
    problems+=("$skill_md's 'Scope & plan' section has no numbered item posting the plan comment — what that comment states could not be read")
  elif ! grep -qE 'test command' <<< "$plan_item"; then
    problems+=("$skill_md's plan-comment item never names the test command, so a wrong one is invisible until the first leaf: $(printf '%.120s' "$plan_item")")
  fi
fi
report "$name"

# 2. The baseline runs the fast tier (issue #341). Preflight's baseline is the one suite run
#    before any cycle, and it is timed; what it runs is `detect-test-command.sh --tier fast`'s
#    command, not the issue's full one — the full command runs once, at the Draft PR gate.
#    Asked of the ONE numbered item that times the baseline, so a `--tier fast` elsewhere in
#    preflight cannot stand in for the command that item actually runs.
name="$skill_md's preflight baseline runs and times detect-test-command.sh --tier fast's command"
problems=()
if need_section '### 0. Preflight' 'what the baseline runs could not be read'; then
  baseline_item="$(items | grep -E 'baseline' | grep -E 'time it')"
  if [[ -z "$baseline_item" ]]; then
    problems+=("$skill_md preflight has no numbered item that runs and times the baseline")
  elif ! grep -qE 'detect-test-command\.sh --tier fast' <<< "$baseline_item"; then
    problems+=("$skill_md's baseline item never runs detect-test-command.sh --tier fast, so the baseline times a command other than the fast tier: $(printf '%.120s' "$baseline_item")")
  fi
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
