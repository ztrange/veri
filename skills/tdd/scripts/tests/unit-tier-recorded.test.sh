#!/usr/bin/env bash
# Unit tests for CLAUDE.md's record of the fast test tier — which directory it is, and what
# a suite has to be to live there.
#
# Contract under test:
#   CLAUDE.md's "Testing idiom" section names skills/tdd/scripts/tests/unit/ as the fast
#   tier, and states the admission bar in one passage: about 100 ms per case, and no git,
#   network, servers, real waits or nested suites. Each fact is asked as a regex, not a
#   fixed string.
#
# Run: skills/tdd/scripts/tests/unit-tier-recorded.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"
section_name="Testing idiom"

source "$HERE/lib/harness.sh"

source "$HERE/record-helpers.sh"

section_records() {
  awk -v want="## $section_name" '
    $0 == want { inside = 1; next }
    inside && /^## / { exit }
    inside' "$claude_path" | records
}

passage_text=""

read_section() {
  passage_text="$(section_records)"
  [[ -n "${passage_text// /}" ]] && return 0
  problems+=("$claude_md has no '## $section_name' section to read")
  return 1
}

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

name="$claude_md's Commands table and '$section_name' section describe the pytest leg, its admission rule, make install-dev, VERI_VENV and the two refusals"
problems=()

if read_section; then
  says "that make unit and make test run a pytest leg over skills/tdd/scripts/tests/py/" \
    'pytest' \
    'skills/tdd/scripts/tests/py/?' \
    'make unit' \
    'make test'
  says "the pytest suites' admission rule — no process but the interpreter" \
    'pytest' \
    'no (other )?process (but|other than|except|besides) the interpreter'
  says "that make install-dev installs pytest into the one environment at VERI_VENV, default ~/.veri-tools/venv" \
    'make install-dev' \
    'veri_venv' \
    '\.veri-tools/venv'
  says "the refusal when pytest cannot be imported — exit 2, naming make install-dev" \
    'pytest' \
    'exit 2|refuse' \
    'make install-dev'
  says "the refusal below the interpreter floor — exit 2, naming Python 3.12" \
    '3\.12' \
    'floor|older' \
    'exit 2|refuse'
fi

section_name="Commands"
if read_section; then
  says "a row for make install-dev naming requirements-dev.txt and VERI_VENV" \
    'make install-dev' \
    'requirements-dev\.txt' \
    'veri_venv'
fi
section_name="Testing idiom"

report "$name"

finish
