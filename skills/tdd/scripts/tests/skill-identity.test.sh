#!/usr/bin/env bash
# Unit tests for where the skill ships and what it calls itself.
#
# Contract under test:
#   skills/tdd/ is a directory, and skills/tdd/SKILL.md's frontmatter reads `name: tdd`.
#   No tracked file outside the two forwarding stubs still names the scripts directory
#   under the skill's old home.
#   Each old name still has a SKILL.md, declaring that old name and forwarding $ARGUMENTS
#   to /tdd.
#   The skill's Inputs section resolves that forwarded argument three ways — an integer is
#   the single-issue procedure, any other word is a scope, nothing at all is the scope
#   `plain` — with the loop it dispatches to reachable from that section rather than
#   resident in the document.
#   A scope's selection label is `ready-for-agent` for the scope `plain` and
#   `ready-for-agent:<scope>` for any other, with `VERI_LABEL` still overriding it, read
#   from the file the loop now lives in.
#   Only the scope branch is sent to that file — `## Inputs` is the one section of SKILL.md
#   naming it — while SKILL.md still holds Procedure and the loop delegates each issue
#   back to it.
#
# Run: scripts/tests/skill-identity.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_dir="skills/tdd"
want_name="tdd"
skill_md="$skill_dir/SKILL.md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/frontmatter-name.sh"

finish
