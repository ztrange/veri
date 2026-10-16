#!/usr/bin/env bash
# Unit test for what skills/tdd/SKILL.md tells an operator about launching the conductor,
# read as text, one paragraph or bullet at a time.
#
# Contract under test:
#   SKILL.md says, in one passage, how to run the conductor when the operator is already
#   inside a session — a plain shell, outside it, `claude -p "/tdd <n>"` — and says, in one
#   passage, that veri never unsets CLAUDECODE itself and why.
#
# Run: scripts/tests/skill-conductor-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


records() {
  awk '/^[-*] / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | plain
}

passage_text="" passage_from=""

need_skill_records() {
  passage_from="$skill_md"
  passage_text="$(records < "$skill_path")"
  [[ "$passage_text" =~ [^[:space:]] ]] && return 0
  problems+=("$skill_md could not be read, so nothing could be asked of what it tells an operator")
  return 1
}

matches_all() {
  local record="$1" re
  shift
  for re in "$@"; do
    [[ "$record" =~ $re ]] || return 1
  done
}

says() {
  local fact="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" && return 0
  done <<< "$passage_text"
  problems+=("$passage_from does not say $fact")
}

never_says() {
  local claim="$1" line
  shift
  while IFS= read -r line; do
    matches_all "$line" "$@" || continue
    problems+=("$passage_from still says $claim: \"${line:0:120}...\"")
  done <<< "$passage_text"
}


finish
