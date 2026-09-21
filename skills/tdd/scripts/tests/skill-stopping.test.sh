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

# stopping_section — the `## Stopping` section's lines, up to the next `## ` heading, with
# emphasis and code markup (`*`, backticks) dropped and case folded, so `**reset**` and
# `git reset --hard HEAD` read the same to every probe. Line order is kept, because whether
# the wait comes before the reset is half of what this case asks.
stopping_section() {
  awk '/^## / { inside = (tolower($0) ~ /^## stopping([[:space:]]|$)/); next } inside' "$skill_path" \
    | tr -d '*`' | tr '[:upper:]' '[:lower:]'
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

# require <pattern> <problem> — record <problem> unless the section matches <pattern>; and
# refuse <pattern> <problem> — record <problem> when it does. Every probe below but the two
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
  refuse 'classify-bail\.sh|event\.sh bail' \
    "the Stopping section bails on the rejected push; a stop is not a bail"
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
