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

name="the Stopping section waits with wait-leaf.sh on every .tdd/<name>.pid still running supervise.sh <name> before it touches the tree, and reaches only for git reset --hard HEAD, never git checkout"
problems=()
if load_section 'Stopping'; then
  wait_at="$(first_line_matching 'wait-leaf\.sh')"
  [[ -n "$wait_at" ]] \
    || problems+=("the Stopping section never calls wait-leaf.sh")
  require '\.tdd/<name>\.pid' \
    "the Stopping section never names .tdd/<name>.pid — it says nothing about which leaves are still running"
  require 'supervise\.sh <name> ' \
    "the Stopping section never names 'supervise.sh <name> ' — a pid file alone does not say the process is still that leaf's supervisor"

  reset_at="$(reset_line)"
  if [[ -z "$reset_at" ]]; then
    problems+=("the Stopping section never drops the tree with git reset --hard HEAD")
  elif after "$wait_at" "$reset_at"; then
    problems+=("the Stopping section reaches for the tree (line $reset_at) before it waits on the leaves (line $wait_at)")
  fi

  refuse 'git checkout' \
    "the Stopping section reaches for git checkout; dropping a half-done step is git reset --hard HEAD"
fi
report "$name"

name="the Stopping section resets nothing and records at=unsettled when rebase-merge, rebase-apply or MERGE_HEAD is present in the worktree"
problems=()
if load_section 'Stopping'; then
  for state in 'rebase-merge' 'rebase-apply' 'merge_head'; do
    require "$state" \
      "the Stopping section never names $state — an interrupted rebase or merge it cannot see is one it would reset away"
  done

  require 'at=unsettled' \
    "the Stopping section never records at=unsettled — the mark would claim a boundary the tree never reached"

  guard_at="$(first_line_matching 'rebase-merge')"
  reset_at="$(reset_line)"
  if after "$guard_at" "$reset_at"; then
    problems+=("the Stopping section drops the tree (line $reset_at) before it checks for an interrupted rebase or merge (line $guard_at) — the reset it must refuse has already run")
  fi
fi
report "$name"

name="the Stopping section runs push-branch.sh and records push=rejected with the sha its stderr names on exit 1, launching no reconcile leaf and bailing not at all"
problems=()
if load_section 'Stopping'; then
  require 'push-branch\.sh' \
    "the Stopping section never runs push-branch.sh — a stopped run would leave its commits only in the worktree"
  require 'exit 1' \
    "the Stopping section says nothing about push-branch.sh exit 1 — the rejected push it must record is the one case it has to answer for"
  require 'push=rejected' \
    "the Stopping section never records push=rejected — the comment would claim a push that the remote refused"
  require 'stderr' \
    "the Stopping section never names push-branch.sh's stderr, which is where the remote's sha is printed"
  require 'sha' \
    "the Stopping section never names the sha the rejected push is recorded with — without it a resume cannot tell whose commits the remote holds"

  refuse 'detach-leaf\.sh|build-develop-prompt\.sh reconcile|develop-reconcile' \
    "the Stopping section launches the reconcile leaf; a stop launches no leaves"
  refuse 'event\.sh bail' \
    "the Stopping section bails on the rejected push; a stop is not a bail"
fi
report "$name"

name="the Stopping section writes exactly one event.sh stop mode=<mode> at=<at> mark, with at one of unplanned, planned, green, step-done or unsettled, and names classify-bail.sh nowhere"
problems=()
if load_section 'Stopping'; then
  marks="$(grep -cE 'event\.sh stop' <<<"$section" || true)"
  if [[ "$marks" -eq 0 ]]; then
    problems+=("the Stopping section never writes an event.sh stop mark — nothing in the run log would say the run paused")
  elif [[ "$marks" -ne 1 ]]; then
    problems+=("the Stopping section writes $marks event.sh stop marks; a stop is one boundary, so it is one mark")
  fi

  require 'event\.sh stop mode=<mode> at=<at>' \
    "the Stopping section never spells the mark event.sh stop mode=<mode> at=<at> — a mark missing either key says which run paused but not where"

  for at in 'unplanned' 'planned' 'green' 'step-done' 'unsettled'; do
    require "at=$at" \
      "the Stopping section never names at=$at — a boundary it cannot spell is one the mark would record as some other one"
  done

  refuse 'classify-bail\.sh' \
    "the Stopping section calls classify-bail.sh; a stop has no cause, so there is no system/process classification to make"
fi
report "$name"

name="the Stopping section renders metrics.sh <n> into a ### ⏹️ Stopped — <mode> comment and commits no metrics file"
problems=()
if load_section 'Stopping'; then
  require 'metrics\.sh <n>' \
    "the Stopping section never renders metrics.sh <n> — the pause would post no record of what the run spent"
  require '### ⏹️ stopped — <mode>' \
    "the Stopping section never posts a '### ⏹️ Stopped — <mode>' comment — nothing on the issue would say the run paused rather than bailed"

  refuse 'git (add|commit)' \
    "the Stopping section stages or commits — a metrics commit marks an ending, and a stop is not one"
fi
report "$name"

name="the Stopping section ends the run with stop-requested.sh --clear, opening no PR, removing no worktree and deleting no .tdd/conductor.pid"
problems=()
if load_section 'Stopping'; then
  clear_at="$(first_line_matching 'stop-requested\.sh --clear')"
  report_at="$(first_line_matching 'metrics\.sh <n>')"
  if [[ -z "$clear_at" ]]; then
    problems+=("the Stopping section never runs stop-requested.sh --clear — the request would outlive the stop it asked for and pause the resumed run at its first checkpoint")
  elif after "$report_at" "$clear_at"; then
    problems+=("the Stopping section clears the stop request (line $clear_at) before it reports the pause (line $report_at) — the clear is what ends the run")
  fi

  refuse 'gh pr (create|ready)' \
    "the Stopping section opens or readies a PR; a stop pauses the run, it does not finish it"
  refuse 'git worktree remove' \
    "the Stopping section removes the worktree the resume has to run in"
  refuse 'rm .*conductor\.pid' \
    "the Stopping section deletes .tdd/conductor.pid; the conductor exiting is what frees the issue"
fi
report "$name"

name="SKILL.md's script reference list has an entry for stop-requested.sh saying what it prints and which exit codes it answers with"
problems=()
section="$(awk '
  /^## / { in_list = ($0 ~ /^## The scripts/); in_entry = 0; next }
  !in_list { next }
  /^- `\$S\// { in_entry = ($0 ~ /^- `\$S\/stop-requested\.sh/) }
  in_entry' "$skill_path" | plain)"
if [[ -z "$section" ]]; then
  problems+=("the script reference list has no \$S/stop-requested.sh entry — the Stopping section's two calls have no contract to read")
else
  for mode in 'at-ledger' 'at-leaf' 'now'; do
    require "$mode" "the stop-requested.sh entry never names the mode $mode it can print"
  done
  one_line="$(joined)"
  exit0_sentence="$(grep -E 'exit 0([^0-9]|$)' <<<"${one_line//. /.$'\n'}")"
  section="$exit0_sentence" require 'printed on stdout' \
    "the stop-requested.sh entry's exit 0 sentence never says the mode is printed on stdout"
  require '--clear' "the stop-requested.sh entry never names --clear, the Stopping section's second call"
  for code in 0 2 3; do
    require "exits? ([0-9]+[ ,/]+(or |and )?)*$code([^0-9]|\$)" "the stop-requested.sh entry never names exit $code"
  done
fi
report "$name"

name="Launching a leaf runs stop-requested.sh before every leaf launch: exit 3 launches as normal, at-ledger launches the leaf anyway, at-leaf and now launch nothing and go to Stopping"
problems=()
if load_section 'Launching a leaf'; then
  section="$(joined)"
  require 'stop-requested\.sh' \
    "the Launching a leaf section never runs stop-requested.sh — no launch asks whether a stop was requested"
  require "$(either_order 'before[^.;]*launch' 'stop-requested\.sh')" \
    "the Launching a leaf section never says stop-requested.sh runs before a leaf is launched"
  require 'exit 3[^.;]*launch' \
    "the Launching a leaf section never says stop-requested.sh's exit 3 launches as normal"
  require 'at-ledger[^.;]*launch' \
    "the Launching a leaf section never says mode at-ledger launches the leaf anyway"
  for mode in 'at-leaf' 'now'; do
    require "$(word "$mode")[^.;]*launch(es)? nothing" \
      "the Launching a leaf section never says mode $mode launches nothing"
  done
  require 'launch(es)? nothing[^.;]*stopping' \
    "the Launching a leaf section never sends a launch-nothing mode to Stopping"
fi
report "$name"

name="the green PASS branch runs stop-requested.sh immediately after the atomic green commit's push, and any mode it prints goes to Stopping"
problems=()
if load_section 'Procedure'; then
  ledger_checkpoint "the green PASS branch" 'git commit -m "feat: <step summary>' \
    'continue to the refactor loop' 'push-branch\.sh'
fi
report "$name"

name="the refactor-pending clear's push and a pin's test: commit are each followed by stop-requested.sh, and any mode it prints goes to Stopping"
problems=()
if load_section 'Procedure'; then
  ledger_checkpoint "the refactor-pending clear" '\$s/clear-refactor-pending\.sh \.tdd/issue-<n>\.md' \
    'loop back to the top of step 3' 'push-branch\.sh'
fi
if load_section 'Already satisfied'; then
  ledger_checkpoint "the pin's test: commit" 'git commit -m "test: pin' \
    'loop back to the top of step 3' 'git commit -m "test: pin'
fi
report "$name"

require_unreadable_at_ledger() {
  require 'exit 2[^.;]*at-ledger' \
    "$1 never says stop-requested.sh's exit 2 is a stop in mode at-ledger"
  require "$(either_order 'exit 2' 'unreadable')" \
    "$1 never says to narrate that the stop request was unreadable on exit 2"
}

name="Launching a leaf treats stop-requested.sh exit 2 as a stop in mode at-ledger, narrating that the request was unreadable"
problems=()
if load_section 'Launching a leaf'; then
  section="$(joined)"
  require_unreadable_at_ledger "the Launching a leaf section"
fi
report "$name"

name="the three ledger-commit checkpoints send stop-requested.sh exit 2 to Stopping as at-ledger, narrating that the request was unreadable"
problems=()
ledger_exit2() {
  local what="$1" text
  text="$(ledger_branch "$2" "$3" | tr '\n' ' ' | tr -s ' ')"
  if [[ "$text" != *stop-requested.sh* ]]; then
    problems+=("$what has no stop-requested.sh checkpoint to read — nothing could be checked")
    return
  fi
  section="${text#*stop-requested.sh}"
  require_unreadable_at_ledger "$what"
}
if load_section 'Procedure'; then
  procedure="$section"
  ledger_exit2 "the green PASS branch" 'git commit -m "feat: <step summary>' \
    'continue to the refactor loop'
  section="$procedure"
  ledger_exit2 "the refactor-pending clear" '\$s/clear-refactor-pending\.sh \.tdd/issue-<n>\.md' \
    'loop back to the top of step 3'
fi
if load_section 'Already satisfied'; then
  ledger_exit2 "the pin's test: commit" 'git commit -m "test: pin' \
    'loop back to the top of step 3'
fi
report "$name"

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
