#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md has the conductor run its own long commands: the
# preflight baseline and the full-suite gate go through detach-command.sh, never a bare
# `make test` or detect-test-command.sh --tier command the conductor might background.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Contract under test:
#   Every procedure line that runs `make test`, or names detect-test-command.sh --tier
#   fast|all's command, also names detach-command.sh; one that does not is reported as
#   SKILL.md:<line>.
#
# Run: scripts/tests/skill-detach-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

source "$HERE/lib/harness.sh"

undetached() {
  awk '
    /detect-test-command\.sh --tier (fast|all)/ || (/[Rr]un/ && /make test/) {
      if ($0 !~ /detach-command\.sh/) print "SKILL.md:" NR ": " $0
    }' "$1"
}

name="#601 $skill_md runs make test and the detected test command only through detach-command.sh"
problems=()

planted="$(scratch_dir)/SKILL.md"
printf '%s\n' 'Run `make test` once.' 'Run it through `detach-command.sh start full make test`.' > "$planted"
expect_eq "$name (scanner flags a planted offender, not a detached line)" \
  'SKILL.md:1: Run `make test` once.' "$(undetached "$planted")"

while IFS= read -r line; do
  problems+=("$line")
done < <(undetached "$md")
report "$name"

no_background_rule() {
  awk '/[Nn]o step/ && /background/ && /end(s)? (its|the|their)? ?turn/ { found = 1 }
       END { if (!found) print "SKILL.md: no line says that no step backgrounds a command and ends its turn" }' "$1"
}

name="#601 $skill_md says no step backgrounds a command and ends its turn"
problems=()

planted="$(scratch_dir)/SKILL.md"
printf '%s\n' 'Never launch a leaf in a background Bash call and then wait for its notification.' > "$planted"
expect_eq "$name (scanner flags a leaf-only rule)" \
  'SKILL.md: no line says that no step backgrounds a command and ends its turn' "$(no_background_rule "$planted")"

while IFS= read -r line; do
  problems+=("$line")
done < <(no_background_rule "$md")
report "$name"

finish
