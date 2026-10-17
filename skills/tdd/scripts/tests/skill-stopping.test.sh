#!/usr/bin/env bash
# Unit tests for the sequence skills/tdd/SKILL.md runs when a stop is requested, read as
# text.
#
# Contract under test:
#   1. SKILL.md has a `## Stopping` section; it waits with `wait-leaf.sh <name>` on every
#      `.tdd/<name>.pid` still running `supervise.sh <name> ` and does so BEFORE it reaches
#      for the tree, and the only reach it names is `git reset --hard HEAD`, never
#      `git checkout`.
#   2. That section refuses the tree when an interrupted rebase or merge is present —
#      `rebase-merge`, `rebase-apply` or `MERGE_HEAD` — recording `at=unsettled` instead of
#      resetting, and it checks for that before it reaches the reset.
#   3. That section runs `push-branch.sh` and answers its exit 1 by recording
#      `push=rejected` with the sha its stderr names. It launches no reconcile leaf and does
#      not bail.
#   4. *Launching a leaf* runs `stop-requested.sh` before the launch; exit 3 and `at-ledger`
#      launch the leaf, and `at-leaf` and `now` launch nothing and go to *Stopping*.
#   5. SKILL.md says the conductor signals only processes it started, by the pid it recorded
#      when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`),
#      and that an experiment's processes and leaf names carry the `exp-` prefix no live run
#      uses.
#
# Run: scripts/tests/skill-stopping.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


skill_section() {
  awk -v want="$(plain <<<"$1")" '
    /^## / {
      h = tolower($0); after = substr(h, length(want) + 4, 1)
      inside = (index(h, "## " want) == 1 && (after == "" || after ~ /[[:space:]]/)); next
    }
    inside' "$skill_path" | plain
}

load_section() {
  section="$(skill_section "$1")"
  [[ -n "$section" ]] && return 0
  problems+=("$skill_md has no ## $1 section — nothing could be checked")
  return 1
}

require() {
  grep -qE -- "$1" <<<"$section" || problems+=("$2")
}
refuse() {
  grep -qE -- "$1" <<<"$section" && problems+=("$2")
  return 0
}

first_line_matching() {
  grep -nE -m1 -- "$1" <<<"$section" | cut -d: -f1
}

reset_line() {
  first_line_matching 'git reset --hard head'
}

joined() {
  tr '\n' ' ' <<<"$section" | tr -s ' '
}

word() {
  printf '(^|[^a-z-])%s([^a-z-]|$)' "$1"
}

either_order() {
  printf '%s[^.;]*%s|%s[^.;]*%s' "$1" "$2" "$2" "$1"
}

after() {
  [[ -n "$1" && -n "$2" && "$1" -gt "$2" ]]
}

ledger_branch() {
  start="$1" end="$2" awk '
    !inside && $0 ~ ENVIRON["start"] { inside = 1 }
    inside { print }
    inside && $0 ~ ENVIRON["end"] { exit }' <<<"$section"
}

joined_branch() {
  section="$(ledger_branch "$1" "$2")"
  section="$(joined)"
}

ledger_checkpoint() {
  local what="$1" anchor="$4" anchor_at stop_at
  section="$(ledger_branch "$2" "$3")"
  if [[ -z "$section" ]]; then
    problems+=("$what has no branch to read — nothing could be checked")
    return
  fi
  anchor_at="$(first_line_matching "$anchor")"
  stop_at="$(first_line_matching 'stop-requested\.sh')"
  if [[ -z "$stop_at" ]]; then
    problems+=("$what is never followed by stop-requested.sh — a stop waiting for at-ledger is not seen at that ledger commit")
  elif ! after "$stop_at" "$anchor_at"; then
    problems+=("$what runs stop-requested.sh (line $stop_at) before its ledger commit lands (line ${anchor_at:-none})")
  fi
  section="$(joined)"
  require "$(either_order '(any|every|whatever)[^.;]*mode' 'stopping')" \
    "$what never says any mode stop-requested.sh prints goes to Stopping there"
}

scope_loop_md="skills/tdd/SCOPE-LOOP.md"

scope_loop_section() {
  n="$1" awk '
    /^### / { inside = ($0 ~ ("^### Loop " ENVIRON["n"] "\\.")); next }
    inside' "$ROOT/$scope_loop_md"
}

scope_stop_unchecked="$scope_loop_md's Loop 4 lists no issue that ended in a stop — nothing could be checked"
load_scope_stop() {
  section="$(scope_loop_section 4 | plain)"
  if [[ -z "$section" ]]; then
    problems+=("$scope_loop_md has no ### Loop 4 section — nothing could be checked")
    return 1
  fi
  section="$(awk '
    /^- / { inside = ($0 ~ /^- [^.]*stop/) }
    /^[^- ]/ { inside = 0 }
    inside' <<<"$section")"
  if [[ -z "$section" ]]; then
    problems+=("${1:-$scope_stop_unchecked}")
    return 1
  fi
  section="$(joined)"
}

finish
