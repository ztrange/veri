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

name="Launching a leaf asks stop-requested.sh before reading a leaf's wait-leaf.sh exit 2 as killed-stuck, and a pending now goes to Stopping instead of Bailing"
problems=()
if load_section 'Launching a leaf'; then
  section="$(joined)"
  require "$(either_order 'stop-requested\.sh' 'before[^.;]*killed-stuck')" \
    "the Launching a leaf section never asks stop-requested.sh before reading a leaf's exit 2 as killed-stuck"
  require "$(word now)[^.;]*stopping[^.;]*(instead of|rather than)[^.;]*bailing|$(word now)[^.;]*(instead of|rather than)[^.;]*bailing[^.;]*stopping" \
    "the Launching a leaf section never sends a leaf's exit 2 with a pending now to Stopping instead of Bailing"
fi
report "$name"

name="each phase's leaf-exit-2 branch (develop-red, green, refactor, revise, verify-plan) points back to Launching a leaf, where stop-requested.sh is asked before the exit 2 is read as killed-stuck"
problems=()
phase_exit2() {
  heading="$1" awk '
    /^#{2,4} / { inside = (tolower($0) ~ ENVIRON["heading"]); next }
    inside' "$skill_path" | plain | anchor="$2" awk '
    function flush() { if (hit) { print buf; done = 1 } buf = "" }
    done { next }
    /^[[:space:]]*$/ { flush(); next }
    /^[[:space:]]*(- |[0-9]+\. )/ { flush() }
    { buf = buf " " $0; if ($0 ~ ENVIRON["anchor"]) hit = 1 }
    END { if (hit && !done) print buf }' | tr -s ' '
}
while IFS='|' read -r phase heading anchor; do
  section="$(phase_exit2 "$heading" "$anchor")"
  if [[ -z "$section" ]]; then
    problems+=("the $phase branch has no exit-2 clause to read — nothing could be checked")
    continue
  fi
  require 'launching a leaf' \
    "the $phase branch reads a leaf's exit 2 without pointing back to Launching a leaf — a pending now stop there would bail"
done <<'PHASES'
verify-plan|^### 2c\. verify the plan|killed-stuck \(exit 2\)
develop-red|^#### red|exits 2 \(killed-stuck\)
green|^#### green|exit 2 → bail
refactor|^#### refactor loop|exit 2 → bail
revise|^## revising on a reject|exit 2 → bail
PHASES
report "$name"

name="Bailing keeps a bail reached first — REVISE_BUDGET exhausted, or killed-stuck with no now pending — as a bail, and its comment says a stop was pending when one was"
problems=()
if load_section 'Bailing'; then
  section="$(joined)"
  pending="$(word pending)" stop="$(word stop)"
  require 'stop-requested\.sh' \
    "the Bailing section never asks stop-requested.sh — it cannot say whether a stop was pending"
  require "$(either_order revise_budget "$stop[^.;]*$pending")" \
    "the Bailing section never says a REJECT exhausting REVISE_BUDGET with a stop pending still bails"
  require "$(either_order killed-stuck "no[^.;]*$(word now)[^.;]*$pending")" \
    "the Bailing section never says a killed-stuck leaf with no now pending still bails"
  require "$(either_order comment "$stop[^.;]*$pending")" \
    "the Bailing section's comment never says a stop was pending when one was"
fi
report "$name"

name="the Draft PR step runs to completion with a stop request pending, clears it with stop-requested.sh --clear, and its final ### ✅ Done comment says a stop arrived after the last step"
problems=()
if load_section 'Procedure'; then
  draft_pr="$(ledger_branch '^### 4\. draft pr' '^### 5\.')"
  section="$draft_pr"
  section="$(joined)"
  stop="$(word stop)"
  require 'stop-requested\.sh --clear' \
    "the Draft PR step never runs stop-requested.sh --clear — a stop arriving after the last step would outlive the run and pause the next one"
  require "$(either_order "($stop[^.;]*pending|pending[^.;]*$stop)" '(runs? to completion|not interrupted|finish(es)?)')" \
    "the Draft PR step never says it runs to completion with a stop request pending"
  section="$(awk '/^4\. post a final/ { inside = 1 } inside && /^[[:space:]]*$/ { exit } inside' <<<"$draft_pr")"
  section="$(joined)"
  require '### ✅ done' \
    "the Draft PR step has no sub-step posting the final ### ✅ Done comment to read"
  require "$stop[^.;]*arrived[^.;]*after[^.;]*last step" \
    "the final ### ✅ Done comment never says a stop arrived after the last step"
fi
report "$name"

name="the Draft PR step says both checkpoints apply to the repair step a red full run appends, like any other step"
problems=()
if load_section 'Procedure'; then
  joined_branch '^### 4\. draft pr' '^### 5\.'
  require "$(either_order 'repair step' '(both|the two) checkpoints')" \
    "the Draft PR step never says both checkpoints apply to the repair step a red full run appends — a stop requested during a repair would run on to its end"
fi
report "$name"

name="#987: preflight step 3 runs stop-requested.sh --clear beside the .tdd/conductor.pid write, so a stale request from a killed run cannot stop the run that resumes it"
problems=()
if load_section 'Procedure'; then
  joined_branch '^3\. suite is green at baseline' '^4\. '
  require '\.tdd/conductor\.pid' \
    "preflight step 3 has no .tdd/conductor.pid write to read — nothing could be checked beside it"
  require 'stop-requested\.sh --clear' \
    "preflight step 3 never runs stop-requested.sh --clear — a request a killed run left behind would stop the run that resumes it"
  require "$(either_order '(stale|killed)' '(request|stop)')" \
    "preflight step 3 never says the clear is for a stale request left by a killed run"
fi
report "$name"

name="#987: step 1.2 neither writes .tdd/conductor.pid nor runs stop-requested.sh --clear — preflight step 3 already took the lock"
problems=()
if load_section 'Procedure'; then
  joined_branch '^2\. derive the slug' '^3\. '
  [[ -n "${section// }" ]] \
    || problems+=("step 1.2 has no branch to read — nothing could be checked")
  refuse '> \.tdd/conductor\.pid' \
    "step 1.2 writes .tdd/conductor.pid again — the lock belongs to preflight step 3, and a second write here is the one #987 moved"
  refuse 'stop-requested\.sh --clear' \
    "step 1.2 runs stop-requested.sh --clear again — the stale-request clear belongs beside preflight step 3's lock"
fi
report "$name"

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

name="SCOPE-LOOP.md's Loop 4 stop conditions list an issue that ended in a stop, and say the loop then reports and stops without going back to Loop 1 or selecting another issue"
problems=()
if load_scope_stop "$scope_loop_md's Loop 4 lists no issue that ended in a stop — a stopped issue leaves the loop carrying on to the next one"; then
  require '(^|[^a-z])reports?[^.;]*stops?' \
    "the stopped-issue condition never says the loop reports and stops"
  require '(not|never)[^.;]*(go(es)? back|return)[^.;]*loop 1' \
    "the stopped-issue condition never says the loop does not go back to Loop 1"
  require "$(either_order '(not|never|no)[^.;]*(select|pick|take|start)' '(another|next|other) issue')" \
    "the stopped-issue condition never says the loop does not select another issue"
fi
report "$name"

name="SCOPE-LOOP.md says a stop, unlike a bail, has no continue-past option — no --continue-on-bail equivalent, because a stop is the operator speaking"
problems=()
if load_scope_stop; then
  require "$(either_order '(^|[^a-z])(no|not|never|nothing)[^a-z]' '(--continue-on-bail|continue[- ]past)')" \
    "the stopped-issue condition never says a stop has no --continue-on-bail equivalent"
  require '(^|[^a-z])operator' \
    "the stopped-issue condition never says a stop is the operator speaking"
fi
report "$name"

name="SCOPE-LOOP.md's Loop 5 report gives a stopped issue a stopped: <mode> per-issue line, and names the stop and the stopped issue's mode as what stopped the loop"
problems=()
loop5="$(scope_loop_section 5)"
if [[ -z "$loop5" ]]; then
  problems+=("$scope_loop_md has no ### Loop 5 section — nothing could be checked")
else
  section="$(awk '/^```/ { fence++; next } fence == 1' <<<"$loop5" | plain)"
  require 'stopped: ?<mode>' \
    "Loop 5's per-issue line has no stopped: <mode> form beside the PR url, bailed: and skipped:"
  section="$(awk '/^```/ { fence++; next } fence >= 2' <<<"$loop5" | plain)"
  section="$(joined)"
  require "$(either_order 'what stopped the loop' "$(word stop)")" \
    "Loop 5 never names the stop as what stopped the loop"
  require "$(either_order 'what stopped the loop' '(^|[^a-z])mode')" \
    "Loop 5 never names the stopped issue's mode as what stopped the loop"
fi
report "$name"

name="SCOPE-LOOP.md says re-invoking the same command after a stop resumes the stopped issue from its committed ledger and then carries on draining the scope"
problems=()
if load_scope_stop; then
  require 're-?invok(e|es|ing)[^.;]*same command' \
    "the stopped-issue condition never says to re-invoke the same command"
  require "$(either_order 'resum' 'committed ledger')" \
    "the stopped-issue condition never says the stopped issue resumes from its committed ledger"
  require 'resum[^.;]*(carr(y|ies|ying) on|continu(e|es|ing)|keep(s|ing)? going)[^.;]*(drain|scope)' \
    "the stopped-issue condition never says the resumed run then carries on draining the scope"
fi
report "$name"

name="#1174: $skill_md tells the conductor it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (pkill, killall, kill \$(pgrep …)), and that experiments carry the exp- prefix no live run uses"
problems=()
section="$(plain --join < "$skill_path" | tr -s ' ')"
require '(signal|kill)s? only (the )?processes (it|you) (started|start)' \
  "$skill_md never says the conductor signals only processes it started"
require 'pid (it|you) recorded when (it|you) started' \
  "$skill_md never says it signals by the pid it recorded when it started them"
require 'never by name or (by )?pattern' \
  "$skill_md never says it never signals by name or pattern"
require "$(word pkill)" "$skill_md never names pkill"
require "$(word killall)" "$skill_md never names killall"
require 'kill \$\(pgrep' "$skill_md never names kill \$(pgrep …)"
require "$(either_order "$(word exp-)" 'prefix')" \
  "$skill_md never says an experiment's processes and leaf names carry the exp- prefix"
require 'no live run uses' "$skill_md never says no live run uses that prefix"
report "$name"

finish
