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

name="$claude_md's '$section_name' section documents the unit-tier migration pattern, naming lib/github.sh as what still follows it and push-branch.sh as having left it for the Python convention"
problems=()

if read_section; then
  says "the migration pattern — a main guard, a unit suite that sources the script, dependencies mocked as same-named shell functions, the CLI contract unchanged" \
    'bash_source|main guard' \
    'sources?|sourcing' \
    'mock' \
    'shell functions?|same-named' \
    'cli contract|byte-identical' \
    'unchanged|unmodified|byte-identical'
  says "that lib/github.sh, sourced by tests/unit/github.test.sh with gh mocked as a shell function, still follows that pattern" \
    'lib/github\.sh' \
    'tests/unit/github\.test\.sh' \
    '(^|[^a-z])gh([^a-z]|$)' \
    'mock' \
    'shell function'
  says "that push-branch.sh left that pattern for the Python convention status.sh is the worked example of" \
    'push-branch\.sh' \
    'left|leaves|moved|ported' \
    'python' \
    'status\.sh' \
    'worked example'
  if grep -E 'push-branch\.sh is (its|the) worked example' <<< "$passage_text" > /dev/null; then
    problems+=("$claude_md's '$section_name' section still names push-branch.sh the worked example of the unit-tier pattern")
  fi
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

name="$claude_md's '$section_name' section records the shim convention for a ported script and that its tests live in tests/py/test_<module>.py"
problems=()

if read_section; then
  says "the shim convention — a ported script's .sh entry point is a /bin/sh shim over its veri/ module, its Bash holding no Python source" \
    'port' \
    '\.sh' \
    '/bin/sh' \
    'shim' \
    'veri/' \
    'module' \
    'no python source|never (contains|holds) python source|holds no python'
  says "that a ported script's tests live in tests/py/test_<module>.py" \
    'port' \
    'tests/py/test_<module>\.py'
fi

report "$name"

name="$claude_md's '$section_name' section says which python3 call the fast tier's guard lets through — one whose first argument is a module file under skills/tdd/scripts/veri/"
problems=()

if read_section; then
  says "in the admission-bar passage that shims git, gh, curl and python3, that the python3 call let through is one whose first argument is a module file under skills/tdd/scripts/veri/, a ported script's shim hand-off" \
    'make unit' \
    'shims git, gh, curl and python3' \
    'first argument' \
    'module' \
    'skills/tdd/scripts/veri/' \
    'shim'
fi

report "$name"

finish
