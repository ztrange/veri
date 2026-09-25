#!/usr/bin/env bash
# Unit tests for the sequence a stopped run runs — like skill-push-reconcile.test.sh this
# suite belongs to no single script: its subject is skills/tdd/SKILL.md, read as text, the
# way the session that follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-push-reconcile.test.sh.
#
# Why this exists (issue #388): #386 gives the conductor a way to learn that a stop was
# requested; this section is what it runs once it has. The first thing it owes is the edge
# #170 settled — a live leaf owns the working tree, so nothing may be reset under one. A
# stop that resets first races the leaf it is stopping: the leaf writes a file the reset has
# already walked past, and the tree the run resumes from is neither the leaf's nor the
# conductor's. So the leaves are settled before the tree is touched at all, and the only
# reach for the tree is `git reset --hard HEAD` — `git checkout` restores a path from an
# arbitrary tree, which is not what dropping a half-done step means.
#
# Contract under test (this step only):
#   1. SKILL.md has a `## Stopping` section; it waits with `wait-leaf.sh <name>` on every
#      `.tdd/<name>.pid` still running `supervise.sh <name> ` and does so BEFORE it reaches
#      for the tree, and the only reach it names is `git reset --hard HEAD`, never
#      `git checkout`.
#   2. That section refuses the tree when an interrupted rebase or merge is present —
#      `rebase-merge`, `rebase-apply` or `MERGE_HEAD` — recording `at=unsettled` instead of
#      resetting, and it checks for that before it reaches the reset.
#   3. That section runs `push-branch.sh` and answers its exit 1 — the remote rejected a
#      non-fast-forward — by recording `push=rejected` with the sha its stderr names. It
#      launches no reconcile leaf (a stop launches no leaves at all) and does not bail: a
#      rejected push leaves the run paused and resumable, not ended.
#
# And where the run looks for a request (issue #389): the only irreversible spend a run makes
# is a leaf launch, so the first checkpoint sits in front of every one, spelled once in
# *Launching a leaf* — `stop-requested.sh` runs before the launch; exit 3 launches as normal,
# `at-ledger` launches the leaf anyway (every leaf between two ledger commits is on the way to
# the next one), and `at-leaf` and `now` launch nothing and go to *Stopping*.
#
# Run: scripts/tests/skill-stopping.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the sequence is missing rather than just that some is.
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

# plain — stdin with emphasis and code markup (`*`, backticks) dropped and case folded, so
# `**reset**` and `git reset --hard HEAD` read the same to every probe. Every slice of
# SKILL.md this suite reads passes through it, so no two slices are read by different rules.
plain() {
  tr -d '*`' | tr '[:upper:]' '[:lower:]'
}

# stopping_section — the `## Stopping` section's lines, up to the next `## ` heading, read
# plain. Line order is kept, because whether the wait comes before the reset is half of what
# this case asks.
stopping_section() {
  awk '/^## / { inside = (tolower($0) ~ /^## stopping([[:space:]]|$)/); next } inside' "$skill_path" \
    | plain
}

# load_section — put the `## Stopping` section in `section` for a case's probes to read, or
# record the fail-closed problem and return 1 when the document has no such section: no probe
# below can say anything about a section that is not there.
load_section() {
  section="$(stopping_section)"
  [[ -n "$section" ]] && return 0
  problems+=("$skill_md has no ## Stopping section — nothing could be checked")
  return 1
}

# require <pattern> <problem> — record <problem> unless the text in `section` matches
# <pattern>; and refuse <pattern> <problem> — record <problem> when it does. Every probe below but the two
# ordering ones is one of these two shapes, so what they share — which text is read, how it
# is matched, where a problem lands — is written once here rather than eleven times, and a
# case reads as the list of claims it makes.
require() {
  grep -qE -- "$1" <<<"$section" || problems+=("$2")
}
refuse() {
  grep -qE -- "$1" <<<"$section" && problems+=("$2")
  return 0
}

# first_line_matching <pattern> — the 1-based number of the section's first line matching
# <pattern>, or empty when none does. Ordering is asked of these numbers rather than of a
# single joined blob, so "before" means what a reader means by it.
first_line_matching() {
  grep -nE -m1 -- "$1" <<<"$section" | cut -d: -f1
}

# reset_line — the 1-based number of the line where the section reaches for the tree, empty
# when it never does. Both cases ask their ordering question against this one line, so the
# pattern that finds it is written once: a copy that drifted would leave one of them measuring
# "before" against a line the other does not call the reset.
reset_line() {
  first_line_matching 'git reset --hard head'
}

# after <line> <other> — true when both are real line numbers and <line> falls after
# <other>. Both cases ask their ordering question through this one predicate, for the same
# reason reset_line is written once: a second spelling of the comparison is where "before
# the reset" comes to mean two things in one suite, and an empty line number — a probe
# above has already said what is missing — is never an ordering answer.
after() {
  [[ -n "$1" && -n "$2" && "$1" -gt "$2" ]]
}

# ---------------------------------------------------------------------------
name="the Stopping section waits with wait-leaf.sh on every .tdd/<name>.pid still running supervise.sh <name> before it touches the tree, and reaches only for git reset --hard HEAD, never git checkout"
problems=()
if load_section; then
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

# ---------------------------------------------------------------------------
name="the Stopping section resets nothing and records at=unsettled when rebase-merge, rebase-apply or MERGE_HEAD is present in the worktree"
problems=()
if load_section; then
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

# ---------------------------------------------------------------------------
name="the Stopping section runs push-branch.sh and records push=rejected with the sha its stderr names on exit 1, launching no reconcile leaf and bailing not at all"
problems=()
if load_section; then
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

# ---------------------------------------------------------------------------
name="the Stopping section writes exactly one event.sh stop mode=<mode> at=<at> mark, with at one of unplanned, planned, green, step-done or unsettled, and names classify-bail.sh nowhere"
problems=()
if load_section; then
  # grep -c answers 1 when it matches nothing, and this suite runs under `set -o pipefail`,
  # so the count is taken with `|| true`: "no mark at all" is a problem to report, not a
  # reason for the case to die before it reports it.
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

# ---------------------------------------------------------------------------
name="the Stopping section renders metrics.sh <n> into a ### ⏹️ Stopped — <mode> comment and commits no metrics file"
problems=()
if load_section; then
  require 'metrics\.sh <n>' \
    "the Stopping section never renders metrics.sh <n> — the pause would post no record of what the run spent"
  require '### ⏹️ stopped — <mode>' \
    "the Stopping section never posts a '### ⏹️ Stopped — <mode>' comment — nothing on the issue would say the run paused rather than bailed"

  # A metrics commit marks an ending; a stopped run will be resumed, so the section stages
  # and commits nothing at all — the one reach for the tree it has is the reset above.
  refuse 'git (add|commit)' \
    "the Stopping section stages or commits — a metrics commit marks an ending, and a stop is not one"
fi
report "$name"

# ---------------------------------------------------------------------------
name="the Stopping section ends the run with stop-requested.sh --clear, opening no PR, removing no worktree and deleting no .tdd/conductor.pid"
problems=()
if load_section; then
  clear_at="$(first_line_matching 'stop-requested\.sh --clear')"
  report_at="$(first_line_matching 'metrics\.sh <n>')"
  if [[ -z "$clear_at" ]]; then
    problems+=("the Stopping section never runs stop-requested.sh --clear — the request would outlive the stop it asked for and pause the resumed run at its first checkpoint")
  elif after "$report_at" "$clear_at"; then
    problems+=("the Stopping section clears the stop request (line $clear_at) before it reports the pause (line $report_at) — the clear is what ends the run")
  fi

  # A stopped run will be resumed: the PR, the worktree and the conductor's pid file are
  # what the resume picks up, and liveness — the conductor exiting — is what frees the issue.
  refuse 'gh pr (create|ready)' \
    "the Stopping section opens or readies a PR; a stop pauses the run, it does not finish it"
  refuse 'git worktree remove' \
    "the Stopping section removes the worktree the resume has to run in"
  refuse 'rm .*conductor\.pid' \
    "the Stopping section deletes .tdd/conductor.pid; the conductor exiting is what frees the issue"
fi
report "$name"

# ---------------------------------------------------------------------------
# The Stopping section calls stop-requested.sh twice — for the mode it was entered with, and
# with --clear at its end — so the script's contract belongs where every other script's is
# read: its own entry in "The scripts" list, from its `- `$S/stop-requested.sh` bullet up to
# the next bullet or heading, read plain like the section above.
name="SKILL.md's script reference list has an entry for stop-requested.sh saying what it prints and which exit codes it answers with"
problems=()
# The entry is loaded where the section's text goes, so its probes are the same require.
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
  # The mode's channel is asked of the sentence that names exit 0, not of the whole entry:
  # the entry also says "nothing on stdout" of exit 3 and exit 2, and a probe over the
  # whole entry would still find `stdout` there after exit 0 stopped naming it. Lines are
  # joined and split at ". ", so a sentence wrapped over two lines is still one sentence.
  joined="$(tr '\n' ' ' <<<"$section" | tr -s ' ')"
  exit0_sentence="$(grep -E 'exit 0([^0-9]|$)' <<<"${joined//. /.$'\n'}")"
  section="$exit0_sentence" require 'printed on stdout' \
    "the stop-requested.sh entry's exit 0 sentence never says the mode is printed on stdout"
  require '--clear' "the stop-requested.sh entry never names --clear, the Stopping section's second call"
  for code in 0 2 3; do
    require "exits? ([0-9]+[ ,/]+(or |and )?)*$code([^0-9]|\$)" "the stop-requested.sh entry never names exit $code"
  done
fi
report "$name"

# ---------------------------------------------------------------------------
# The first checkpoint lives in *Launching a leaf*, not in this section, so the case loads
# that section where the probes read — joined onto one line, so a sentence wrapped over two
# lines is one sentence, and every pattern kept inside one clause with `[^.;]*`, so a mode
# and what it does are read from the same clause rather than from anywhere in the section.
name="Launching a leaf runs stop-requested.sh before every leaf launch: exit 3 launches as normal, at-ledger launches the leaf anyway, at-leaf and now launch nothing and go to Stopping"
problems=()
section="$(awk '/^## / { inside = (tolower($0) ~ /^## launching a leaf/); next } inside' "$skill_path" \
  | plain | tr '\n' ' ' | tr -s ' ')"
if [[ -z "$section" ]]; then
  problems+=("$skill_md has no ## Launching a leaf section — nothing could be checked")
else
  require 'stop-requested\.sh' \
    "the Launching a leaf section never runs stop-requested.sh — no launch asks whether a stop was requested"
  require 'before[^.;]*launch[^.;]*stop-requested\.sh|stop-requested\.sh[^.;]*before[^.;]*launch' \
    "the Launching a leaf section never says stop-requested.sh runs before a leaf is launched"
  require 'exit 3[^.;]*launch' \
    "the Launching a leaf section never says stop-requested.sh's exit 3 launches as normal"
  require 'at-ledger[^.;]*launch' \
    "the Launching a leaf section never says mode at-ledger launches the leaf anyway"
  for mode in 'at-leaf' 'now'; do
    require "(^|[^a-z-])$mode([^a-z-]|\$)[^.;]*launch(es)? nothing" \
      "the Launching a leaf section never says mode $mode launches nothing"
  done
  require 'launch(es)? nothing[^.;]*stopping' \
    "the Launching a leaf section never sends a launch-nothing mode to Stopping"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
