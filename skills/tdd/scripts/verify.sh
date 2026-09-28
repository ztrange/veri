#!/usr/bin/env bash
# verify.sh — run one blind verification of a cycle phase and return its verdict.
#
# This is the single "verify" verb the conductor calls. It composes the three tested
# units so verification is never improvised (and so the developer's rationale can never
# leak in):
#
#   build-verify-prompt.sh   blind prompt from ONLY the issue spec + test path
#     → run-leaf.sh          launch a claude -p verifier leaf (forensic log in .tdd/)
#       → parse-verdict.sh   extract PASS|REJECT + reason from the leaf's output
#
# Usage:
#   verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#     phase = red | green | refactor | pin
#     --step = the ledger's own line for the step under judgement, passed straight
#              through to build-verify-prompt.sh
#     --fast-cmd = the fast tier's test command, required for green, passed straight
#              through to build-verify-prompt.sh
#
# stdout: the verifier's reason (mirror it to the issue thread).
# exit:   0 PASS · 1 REJECT · 2 malformed verdict or build error.
#
# One `verdict` event is appended to the run's event log, `.tdd/events.jsonl` (ADR-0014),
# carrying the phase judged, the PASS/REJECT/malformed word of the exit line above
# and the first line of the reason. A leaf name leaf-role.sh cannot read leaves no line at
# all, rather than one whose actor and phase were invented — the tolerance supervise.sh's
# own marks have.
#
# `claude -p` exits 0 whatever the verdict, so the verdict is taken from PARSING the
# leaf's output, not from the leaf's process status. The verifier leaf is denied Write/
# Edit so it can read the repo and run the test command but cannot fix the code it judges
# — override the leaf's flags with VERIFY_LEAF_ARGS if your environment needs different
# permissions. CLAUDE_BIN (read by run-leaf.sh) overrides the binary for tests.
set -euo pipefail

USAGE="usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]"

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/verify-options.sh"

flag_args=()
while verify_takes_a_value "${1:-}"; do
  [[ -n "${2:-}" ]] || { echo "verify: $1 needs a value" >&2; echo "$USAGE" >&2; exit 2; }
  flag_args+=( "$1" "$2" )
  shift 2
done

# hazard: `$#` is tested first, so set -u never reads an absent $2 or $3.
[[ $# -ge 3 && -n "$1" && -n "$2" && -n "$3" ]] || { echo "$USAGE" >&2; exit 2; }
phase="$1"
spec_file="$2"
test_path="$3"
target="${4:-}"

source "$HERE/lib/leaf-model.sh"
source "$HERE/lib/preserve.sh"

leaf_name="verify-$phase"

default_leaf_args=(--permission-mode bypassPermissions \
                   --disallowedTools Write Edit MultiEdit NotebookEdit)
if [[ -n "${VERIFY_LEAF_ARGS:-}" ]]; then
  leaf_args=( ${VERIFY_LEAF_ARGS} )

  resolved_model="$(leaf_model "$leaf_name")" || resolved_model=""
  if [[ -n "$resolved_model" ]]; then
    for arg in "${leaf_args[@]}"; do
      if [[ "$arg" == "--model" ]]; then
        echo "verify: VERIFY_LEAF_ARGS carries its own --model and a role model variable resolved '$resolved_model' — which one the leaf would run on is flag order; unset one of them" >&2
        exit 2
      fi
    done
  fi
else
  leaf_args=( "${default_leaf_args[@]}" )
fi

prompt="$("$HERE/build-verify-prompt.sh" "${flag_args[@]+"${flag_args[@]}"}" "$phase" "$spec_file" "$test_path" "$target")"

mkdir -p .tdd
promptfile=".tdd/$leaf_name.prompt"
printf '%s' "$prompt" > "$promptfile"

in_temp_index() {  # prints the stdout of `git "$@"` run against that index, or nothing on failure
  local dir out=""
  dir="$(mktemp -d)"
  if GIT_INDEX_FILE="$dir/index" git add -A >/dev/null 2>&1; then
    out="$(GIT_INDEX_FILE="$dir/index" git "$@" 2>/dev/null)" || out=""
  fi
  rm -rf "$dir"
  printf '%s' "$out"
}

tree_snapshot() {  # prints the tree sha of the working tree, or nothing where there is no repo
  in_temp_index write-tree
}

restore_tree() {  # puts the working tree back to the tree object named by $1
  in_temp_index read-tree -u --reset "$1"
}

head_snapshot() {  # prints the sha HEAD names, or nothing where there is no repo or no commit
  # hazard: without --verify, rev-parse prints a literal `HEAD` on a repo with no commits.
  git rev-parse --verify HEAD 2>/dev/null || true
}

restore_head() {  # points HEAD back at the sha $1 names, where it moved from it and $1 is a sha
  if [[ -n "$1" && "$1" != "$2" ]]; then
    git update-ref HEAD "$1"
  fi
}

tree_before="$(tree_snapshot)"
head_before="$(head_snapshot)"

operator_gitconfig="$HOME/.gitconfig"
gitconfig_snapshot() {  # prints the checksum of the operator's global git config, or nothing if absent
  if [[ -f "$operator_gitconfig" ]]; then cksum < "$operator_gitconfig"; fi
}
gitconfig_before="$(gitconfig_snapshot)"

no_verdict_retries="${VERI_NO_VERDICT_RETRIES:-1}"
# hazard: under set -u a word inside `-lt` is read as a variable name and kills the script.
if [[ ! "$no_verdict_retries" =~ ^[0-9]+$ ]]; then
  echo "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got '$no_verdict_retries'" >&2
  exit 2
fi

role="$(leaf_role "$leaf_name")" || role=""
mark() {  # mark <event> [key=value …] -> event.sh under $role, or nothing when leaf_role refused
  if [[ -n "$role" ]]; then
    env $role "$HERE/event.sh" "$@"
  fi
}

refuse_modified() {  # refuse_modified <what> <paths> -> the refusal on stdout, then exit 2
  echo "verifier leaf modified $1 — verdict not accepted (see .tdd/$leaf_name.log); changed:"
  printf '%s\n' "$2"
  exit 2
}

parse_err="$(mktemp)"
trap 'rm -f "$parse_err"' EXIT
relaunches=0
while :; do
  cause=""
  set +e
  out="$("$HERE/supervise.sh" "$leaf_name" "$HERE/run-leaf.sh" "$promptfile" "${leaf_args[@]}")"
  scode=$?
  set -e

  if [[ "$scode" -eq 2 ]]; then
    echo "verifier leaf killed-stuck — no verdict rendered (see .tdd/$leaf_name.log)"
    exit 2
  fi

  if [[ -n "$tree_before" ]]; then
    tree_after="$(tree_snapshot)"
    head_after="$(head_snapshot)"
    changed="$(git diff-tree -r --name-only --no-commit-id "$tree_before" "$tree_after" 2>/dev/null)" || changed=""
    [[ "$head_before" == "$head_after" ]] || changed="${changed:+$changed$'\n'}HEAD"
    if [[ -n "$changed" ]]; then
      restore_tree "$tree_before"
      restore_head "$head_before" "$head_after"
      refuse_modified "the repository" "$changed"
    fi
  fi

  if [[ "$(gitconfig_snapshot)" != "$gitconfig_before" ]]; then
    refuse_modified "the operator's global git config" "$operator_gitconfig"
  fi

  set +e
  reason="$(printf '%s' "$out" | "$HERE/parse-verdict.sh" 2>"$parse_err")"
  vcode=$?
  set -e
  cat "$parse_err" >&2

  if [[ "$vcode" -eq 2 ]] && grep -q 'no VERDICT: line found' "$parse_err"; then
    cause=no-verdict
    if [[ "$relaunches" -lt "$no_verdict_retries" ]]; then
      relaunches=$(( relaunches + 1 ))
      mark relaunch cause="$cause"
      continue
    fi
  fi
  break

done

case "$vcode" in
  0) word=PASS ;;
  1) word=REJECT;    trouble=reject ;;
  *) word=malformed; trouble="${cause:-malformed}" ;;
esac

reason_line="${reason%%$'\n'*}"

mark verdict verdict="$word" reason="$reason_line" ${cause:+cause="$cause"}

if [[ "$word" != PASS ]]; then
  attempt="${role##*VERI_ATTEMPT=}"
  if [[ -n "$tree_before" && -n "$role" && -n "${VERI_ISSUE:-}" && -n "${VERI_STEP:-}" ]]; then
    preserve_attempt verify "$VERI_ISSUE" "$VERI_STEP" "$leaf_name" "$attempt" "$trouble"
  fi
fi

printf '%s\n' "$reason"
exit "$vcode"
