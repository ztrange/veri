#!/usr/bin/env bash
# run-conductor.sh — build and run one CONDUCTOR as a `claude -p` subprocess.
#
# The conductor-level counterpart of run-leaf.sh. A conductor typed as `/tdd <n>` into an
# interactive session IS an interactive chat session, and pays for a harness surface it
# never touches: the skills roster, the full tool schemas, the interactive system prompt —
# ~25,000 tokens on every request, re-sent and re-billed each turn. Everything
# a conductor does is Bash, Read, Write, Edit and `gh`; it invokes no skill, because it is
# the skill. Running it in print mode buys that surface back.
#
# Usage:   run-conductor.sh <issue>
#
# The prompt is the `/tdd` procedure itself — SKILL.md, verbatim, beside this script — with
# the issue number appended, because print mode loads no skills roster: a conductor launched
# this way cannot be handed the procedure by name, so it is handed the procedure.
#
# `--output-format stream-json --verbose`, the same pair run-leaf.sh:44 passes and for the
# same reason: print mode's default format stays SILENT until the process finishes, so a run
# that takes an hour is indistinguishable from one that died in its first minute. The flags
# turn the launch into a continuous event stream the caller can watch.
#
# `--permission-mode bypassPermissions` because print mode has nobody to approve a tool
# call: without it the `gh`, the `make` and the nested `claude` a leaf needs are all denied,
# and the conductor is a process that can read but cannot act.
#
# The child is handed the session's `VERI_*` tunables and none of its handles. A nested
# `claude` otherwise inherits the parent's messaging socket and auth token, which is a
# second session wired into the first one's IPC channel; the rest of the eight name the
# parent's session, host session, pid, entrypoint and child-session flag, all of them
# answers to "which session am I" that belong to a session this one is not. Unsetting them
# here is enough: the child inherits this script's environment, so a name gone from it is a
# name gone from the child's. The `VERI_*` tunables are left alone, because a conductor
# launched in print mode must resolve VERI_MODEL_VERIFIER, REVISE_BUDGET, VERI_STUCK_RETRIES
# and the rest exactly as one started from a chat session does. VERI_NEW_SKILL is the one
# exception: it is not a tunable but this launch's instruction to re-pin, spent by the pin
# decision below before any conductor exists. Handed on, it would reach every process the
# conductor spawns, a leaf's `make test` among them.
#
# The procedure goes in on STDIN, not as the argument to `-p`. SKILL.md's first line is the
# YAML frontmatter fence `---`, and the CLI parses a leading-dash argument as an option, so
# passing it by argv died on `unknown option '---` before any conductor existed.
# Nothing parses options on stdin, so the fence — and any future first line — arrives intact.
#
# CLAUDE_BIN overrides the `claude` binary (used by the tests to inject a stub).
set -euo pipefail

# hazard: written in bash 3.2's syntax so the refusal can speak on the bash it refuses.
bash_major="${VERI_BASH_MAJOR:-${BASH_VERSINFO[0]}}"
if ! [[ "$bash_major" =~ ^[0-9]+$ ]] || [[ "$bash_major" -lt 5 ]]; then
  echo "run-conductor: veri needs bash 5 or newer; this is bash ${VERI_BASH_MAJOR:-$BASH_VERSION} ($BASH). Install it with \`brew install bash\` (it lands ahead of /bin/bash on PATH), or your package manager on Linux." >&2
  exit 2
fi

source "$(dirname "$0")/lib/venv-python.sh"
venv_path_python_floor run-conductor || exit 2

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/exit-contract.sh"
source "$HERE/lib/session-env.sh"
USAGE="usage: run-conductor.sh <issue>"

require_args 1 "$@"
issue="$1"

base="$(cd "$HERE/.." && pwd)"
record=".tdd/issue-$issue-skill-commit"
run_wt=".tdd/wt/$issue"
head_rev=HEAD
pinned=""
refuse_unpinned() {
  echo "run-conductor: refs/remotes/origin/HEAD is not set in '$base' and $1 — refusing to run unpinned" >&2
  exit 2
}
if git -C "$base" remote get-url origin >/dev/null 2>&1; then
  fetches=1
  until fetch_err="$(git -C "$base" fetch -q origin 2>&1)"; do
    printf '%s\n' "$fetch_err" >&2
    [[ "$fetch_err" == *"cannot lock ref"* ]] && (( fetches++ < 60 )) ||
      { echo "run-conductor: fetch of origin failed in '$base' — refusing to run a skill that may be stale" >&2; exit 2; }
    sleep "${VERI_FETCH_RETRY_SLEEP:-1}"
  done
  head_rev=refs/remotes/origin/HEAD
  if ! git -C "$base" rev-parse -q --verify "$head_rev" >/dev/null; then
    default="$(git -C "$base" ls-remote --symref origin HEAD 2>/dev/null |
      awk '$1 == "ref:" { sub("^refs/heads/", "", $2); print $2 }')"
    [[ -n "$default" ]] || refuse_unpinned "origin names no default branch"
    head_rev="refs/remotes/origin/$default"
    git -C "$base" rev-parse -q --verify "$head_rev" >/dev/null ||
      refuse_unpinned "origin's default branch '$default' has no $head_rev"
  fi
fi
if commit="$(git -C "$base" rev-parse "$head_rev" 2>/dev/null)"; then
  mkdir -p .tdd
  [[ -e .tdd/.gitignore ]] || printf '%s\n' '.gitignore' 'issue-*-skill-commit' > .tdd/.gitignore
  if [[ ! -r "$record" ]]; then
    printf '%s\n' "$commit" > "$record"
  elif [[ "${VERI_NEW_SKILL:-}" == 1 ]]; then
    printf '%s\n' "$commit" > "$record"
    mkdir -p "$run_wt"
    (cd "$run_wt" && VERI_ISSUE="$issue" "$HERE/event.sh" skill-repin commit="$commit") || exit 2
  elif recorded="$(cat "$record")" &&
     git -C "$base" cat-file -e "$recorded^{commit}" 2>/dev/null; then
    commit="$recorded"
  else
    echo "run-conductor: recorded skill commit '$recorded' is not in '$base' — refusing to re-pin; set VERI_NEW_SKILL=1 to take the new skill" >&2
    exit 2
  fi
  snapshot="$(mktemp -d)"
  at_exit 'rm -rf "$snapshot"'
  git -C "$base" archive "$commit" . | tar -x -C "$snapshot"
  export VERI_SKILL_CLONE="$base" VERI_SKILL_REF="$head_rev"
  base="$snapshot"
  export VERI_SKILL_COMMIT="$commit"
  pinned="$commit"
else
  echo "run-conductor: no skill commit resolvable from '$base' — running unpinned" >&2
  export VERI_SKILL_UNPINNED=1
fi

skill_file="$base/SKILL.md"
[[ -r "$skill_file" ]] || { echo "run-conductor: cannot read '$skill_file'" >&2; exit 2; }

prompt="$(cat "$skill_file")

Base directory for this skill: $base
${pinned:+
Pinned skill commit (name it in the plan comment): $pinned
}
Solve issue #$issue by the procedure above."

strip_session_env
unset VERI_NEW_SKILL

code=0
printf '%s\n' "$prompt" | "${CLAUDE_BIN:-claude}" -p \
  --output-format stream-json --verbose \
  --permission-mode bypassPermissions || code=$?

past_preflight() {
  local top
  if top="$(git -C "$run_wt" rev-parse --show-toplevel 2>/dev/null)" &&
     [[ "$top" == "$(cd "$run_wt" && pwd -P)" ]]; then
    return 0
  fi
  [[ -n "$(git for-each-ref --format='%(refname)' "refs/heads/tdd/$issue-*" 2>/dev/null)" ]]
}
past_preflight || rm -f "$record"

# pass-through: the caller reads the conductor's own status, whatever it is.
exit "$code"
