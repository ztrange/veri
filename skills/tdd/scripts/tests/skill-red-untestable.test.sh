#!/usr/bin/env bash
# Unit tests for how skills/tdd/SKILL.md's Red section handles a criterion no lightweight,
# behavior-level test can pin, read as text.
#
# Contract under test:
#   1. SKILL.md's Red section states what a valid test is: behaviour over mechanism (no
#      process/fork count or timing assertion), with the in-process-spy carve-out for a call
#      count the criterion itself names.
#   2. SKILL.md's Red section's verify sub-step branches on `AGAINST_UNMODIFIED: UNTESTABLE`
#      by skipping verify-red and verify-pin and bailing immediately, with cause
#      `untestable-criterion`.
#   3. SKILL.md's Bailing section lists `untestable-criterion` as a **process** failure
#      cause, alongside `revise-exhausted`.
#
# Run: scripts/tests/skill-red-untestable.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


doc_text() {
  h="$1" from="${2:-}" awk '
    BEGIN { h = ENVIRON["h"]; from = ENVIRON["from"] }
    !in_s && index($0, h) == 1 { in_s = 1; if (from == "") want = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && from != "" && $0 ~ from) want = 1
      if (want) print
    }' "$skill_path" | plain --join
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

name="$skill_md's Red section states what a valid test is (behaviour over mechanism, with the in-process-spy carve-out)"
problems=()
text="$(doc_text '#### Red' 'Develop\.')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Red section has no \"Develop.\" sub-step — what a valid test is could not be read")
else
  says 'process[^.]{0,20}(count|fork)|fork[^.]{0,20}count' \
    "$skill_md never forbids pinning a process or fork count"
  says 'make profile' \
    "$skill_md never points process/fork counts or timings at make profile instead of an assertion"
  says 'in-process spy' \
    "$skill_md never carves out an in-process spy for a call count the criterion itself names"
fi
report "$name"

name="$skill_md's Red section skips the blind verifier and bails immediately on AGAINST_UNMODIFIED: UNTESTABLE"
problems=()
text="$(doc_text '#### Red' 'Branch on the leaf')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Red section has no \"Verify (blind).\" sub-step — the UNTESTABLE branch could not be read")
else
  says 'untestable' \
    "$skill_md's verify sub-step never branches on UNTESTABLE"
  says 'skip[^.]{0,60}verify-(red|pin)|verify-(red|pin)[^.]{0,60}skip' \
    "$skill_md never says to skip verify-red/verify-pin on UNTESTABLE"
  says 'bail' \
    "$skill_md never says to bail on UNTESTABLE"
  says 'untestable-criterion' \
    "$skill_md never names the untestable-criterion cause token for this bail"
fi
report "$name"

name="$skill_md's Bailing causes list classifies untestable-criterion as a process failure"
problems=()
text="$(doc_text '## Bailing' 'killed-stuck')"
if [[ -z "${text// /}" ]]; then
  problems+=("$skill_md's Bailing section has no causes list starting at killed-stuck — the classification could not be read")
else
  says 'untestable-criterion[^.]{0,220}process' \
    "$skill_md's Bailing causes list never classifies untestable-criterion as a process failure"
fi
report "$name"

name="#1037: doc_text given 'run\\.sh' starts at 'run.sh', not at 'runXsh'"
fixture="$(scratch_dir)"
printf -- '## H\nrunXsh wrong\nrun.sh right\n# end\n' > "$fixture/SKILL.md"
expect_eq "$name" 'run.sh right ' "$(skill_path="$fixture/SKILL.md" doc_text '## H' 'run\.sh')"

finish
