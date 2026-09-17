#!/usr/bin/env bash
# Unit test for the ADR set under docs/adr/ and the exit-2 branch of skills/tdd/SKILL.md —
# like preamble-cost-adr.test.sh this suite has no script as its subject: it reads the
# records as text and asserts that they carry a decision. Zero-dependency plain-shell
# asserts, same idiom as that suite.
#
# Why this exists (issue #219): ADR-0011 and SKILL.md's "Malformed / killed-stuck (exit 2)"
# branch say that verify.sh exit 2 is a bail. #219 narrows that: a verifier leaf that exited
# cleanly — never killed — without a `VERDICT:` line is relaunched instead, and only an
# exhausted relaunch budget bails. A reversal that lives only in verify.sh is a decision the
# next reader re-derives from the code, and the conductor reads SKILL.md, not verify.sh, so
# both the record and the procedure have to say it.
#
# Contract under test:
#   docs/adr/0020-*.md exists and says: a clean exit (not killed) with no verdict is
#   relaunched rather than bailed; and it names ADR-0011 and SKILL.md's exit-2 branch as
#   what it narrows. And some exit-2 branch of skills/tdd/SKILL.md says the same: a verifier
#   that exited with no verdict is relaunched. Wording is the author's — each probe accepts
#   any phrasing that carries its fact.
#
# Where this suite lives (issue #143, ADR 0016): here, not under the `make test` glob, for
# the reason preamble-cost-adr.test.sh gives — its subject is a record under docs/adr/, and
# no-docs-reads.test.sh fails `make test` for a suite there that names a path in this tree.
#
# Run: docs/tests/no-verdict-relaunch-adr.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
ADR_DIR="$ROOT/docs/adr"
SKILL="$ROOT/skills/tdd/SKILL.md"
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

# probe <message> <regex>... — one fact `$lc` has to carry: every regex must match, else
# `message` is appended to `$problems` once.
probe() {
  local msg="$1"; shift
  local re
  for re in "$@"; do
    [[ "$lc" =~ $re ]] || { problems+=("$msg"); return; }
  done
}

# exit2_branches — every "(exit 2)" bullet of SKILL.md with its continuation lines, up to
# the next bullet or a blank line, lowercased. The branch is the bullet, not the file: a
# relaunch mentioned elsewhere in SKILL.md does not tell the conductor what to do on exit 2.
exit2_branches() {
  awk '
    /^[[:space:]]*- / { inb = ($0 ~ /\(exit 2\)/) }
    /^[[:space:]]*$/ { inb = 0 }
    inb { print }
  ' "$SKILL" | tr '[:upper:]' '[:lower:]'
}

# --- a clean exit with no verdict is relaunched, on the record and in the procedure ---
problems=()
adr=""
for f in "$ADR_DIR"/0020-*.md; do [[ -f "$f" ]] && adr="$f"; done
if [[ -z "$adr" ]]; then
  problems+=("no docs/adr/0020-*.md — the no-verdict relaunch is unrecorded")
else
  lc="$(tr '[:upper:]' '[:lower:]' < "$adr")"
  probe "${adr##*/} does not say a clean exit with no verdict is relaunched rather than bailed" \
    'relaunch' 'no[ -]verdict|verdict:' '(clean|not killed|never killed|exited)' 'bail'
  probe "${adr##*/} does not name ADR-0011 as what it narrows" 'adr[ -]?0011'
  probe "${adr##*/} does not name SKILL.md's exit-2 branch as what it narrows" \
    'skill\.md' 'exit[ -]?2'
fi
lc="$(exit2_branches)"
probe "no exit-2 branch of skills/tdd/SKILL.md says a clean exit with no verdict is relaunched" \
  'relaunch' 'no[ -]verdict|verdict:'
report "ADR 0020 and SKILL.md's exit-2 branch record that a clean exit with no verdict is relaunched, narrowing ADR-0011"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
