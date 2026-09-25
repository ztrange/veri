#!/usr/bin/env bash
# Unit tests for CLAUDE.md's record of the fast test tier — which directory it is, and what
# a suite has to be to live there. Like model-knobs-recorded.test.sh this suite's subject is
# a document rather than a script: what an agent adding a suite is told before it picks a
# directory. Zero-dependency plain-shell asserts, same idiom as model-knobs-recorded.test.sh.
#
# Why this exists (issue #336): `make unit` runs only the suites under
# skills/tdd/scripts/tests/unit/, and its recipe shims git, gh, curl and python3 so a suite
# that calls one fails there. That guard catches a suite already in the directory; it says
# nothing to the agent deciding whether a new suite belongs in it. The admission bar lives
# in the Makefile's shims and in the moved suites' headers, and neither is where an agent
# looks — CLAUDE.md's "Testing idiom" section is, and it is where every other rule about
# where a suite goes (docs/tests/, the count line) is already written down.
#
# Contract under test:
#   CLAUDE.md's "Testing idiom" section names skills/tdd/scripts/tests/unit/ as the fast
#   tier, and states the admission bar in one passage: about 100 ms per case, and no git,
#   network, servers, real waits or nested suites.
#
# Facts are asked as the regexes any wording carrying them would match, never as fixed
# strings — the protocol model-knobs-recorded.test.sh and lane-rule-recorded.test.sh use.
#
# Not asked here: that CLAUDE.md's suite count moved when this suite landed.
# claude-md-counts.test.sh holds every count in that document to the files on disk.
#
# Run: skills/tdd/scripts/tests/unit-tier-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
section_name="Testing idiom"

pass=0 fail=0

# report, plain and records: the helpers the *-recorded.test.sh suites share (issue #225).
# This suite's `says` asks a different question and stays below, defined after the source.
# shellcheck source=record-helpers.sh
source "$HERE/record-helpers.sh"

# section_records — the "Testing idiom" section of CLAUDE.md, from its `## ` heading to the
# next one, split into records by the shared `records`. A fact is asked of one record so two
# sentences sections apart that share a word do not read as a statement. Read by section
# rather than whole-file: the step asks that the rule sit where the other rules about where
# a suite goes are written.
section_records() {
  awk -v want="## $section_name" '
    $0 == want { inside = 1; next }
    inside && /^## / { exit }
    inside' "$claude_path" | records
}

passage_text=""

# read_section — load the section's records into `passage_text` for `says` to search, or
# append the problem that there is no section to read and return 1. Every case starts here.
read_section() {
  passage_text="$(section_records)"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md has no '## $section_name' section to read")
  return 1
}

# says <fact> <regex>... — some ONE record of the section has to match every <regex>, or
# one problem naming the fact is appended.
says() {
  local fact="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$passage_text"
  problems+=("$claude_md's '$section_name' section does not say $fact")
}

# 1. One criterion, one case: the fast tier is named where an agent choosing a directory
#    reads, together with the bar a suite has to clear to be put there.
name="$claude_md's '$section_name' section names skills/tdd/scripts/tests/unit/ as the fast tier and states its admission bar"
problems=()

if read_section; then
  says "that skills/tdd/scripts/tests/unit/ is the fast tier" \
    'skills/tdd/scripts/tests/unit/?' \
    'fast'
  says "the admission bar — about 100 ms per case, and no git, network, servers, real waits or nested suites" \
    '100 ?ms ?(/|per|a|each) ?case' \
    'git' \
    'network' \
    'server' \
    'real waits?|sleep' \
    'nested'
fi

report "$name"

# 2. One criterion, one case: the migration pattern a script follows into the unit tier is
#    written where the tier is, with push-branch.sh named as the worked example (#339). The
#    four parts are asked of ONE record, so a later migration reads the whole recipe in one
#    place: the main guard, the unit suite sourcing the script, its dependencies mocked as
#    same-named shell functions, and the CLI contract left unchanged.
name="$claude_md's '$section_name' section documents the unit-tier migration pattern, naming push-branch.sh as the worked example"
problems=()

if read_section; then
  says "the migration pattern — a main guard, a unit suite that sources the script, dependencies mocked as same-named shell functions, the CLI contract unchanged — naming push-branch.sh as the worked example" \
    'push-branch\.sh' \
    'worked example' \
    'bash_source|main guard' \
    'sources?|sourcing' \
    'mock' \
    'shell functions?|same-named' \
    'cli contract|byte-identical' \
    'unchanged|unmodified|byte-identical'
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
