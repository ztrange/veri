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
#   verify.sh [--step '<STEP>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]
#     phase = red | green | refactor | pin
#     --step = the ledger's own line for the step under judgement (#223), passed straight
#              through to build-verify-prompt.sh
#
# stdout: the verifier's reason (mirror it to the issue thread).
# exit:   0 PASS · 1 REJECT · 2 malformed verdict or build error.
#
# One `verdict` event is appended to the run's event log, `.tdd/events.jsonl` (issue #107,
# ADR-0014), carrying the phase judged, the PASS/REJECT/malformed word of the exit line above
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

# The step is a flag and only a flag: an ambient VERI_STEP is never read here, so nothing
# but this call site can scope a verdict (#223). Without it the prompt is what it always was.
step_args=()
if [[ "${1:-}" == --step ]]; then
  step_args=( --step "${2:?--step needs the step text}" )
  shift 2
fi

phase="${1:?usage: verify.sh [--step '<STEP>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]}"
spec_file="${2:?missing <issue-spec-file>}"
test_path="${3:?missing <test-path>}"
target="${4:-}"

HERE="$(cd "$(dirname "$0")" && pwd)"

# The verifier leaf's name, spelled once. Four things below are derived from it and must agree
# — the name supervise.sh supervises under, the `.tdd/<name>.prompt` and `.tdd/<name>.log`
# paths that follow supervise.sh's convention for it, and the name leaf-role.sh reads the
# event's actor and phase out of — so a reader sees one name used four times rather than four
# expressions to check against each other.
leaf_name="verify-$phase"

# Default verifier sandbox: may read the repo and run tests, but never modify the tree.
# Space-separated tool lists per `claude --help`.
default_leaf_args=(--permission-mode bypassPermissions \
                   --disallowedTools Write Edit MultiEdit NotebookEdit)
if [[ -n "${VERIFY_LEAF_ARGS:-}" ]]; then
  # shellcheck disable=SC2206  -- intentional word-split of caller-supplied flags
  leaf_args=( ${VERIFY_LEAF_ARGS} )

  # Two things can name a model for this one leaf, and the pair is refused rather than ranked
  # (issue #171). VERI_MODEL / VERI_MODEL_VERIFIER are resolved by leaf-model.sh in supervise.sh
  # and become `--model <value>` in run-leaf.sh; the caller's own flags are passed through
  # verbatim, so a `--model` among them lands on the SAME `claude` command line. Which of the two
  # the CLI honours is flag order — a rule veri never chose and cannot see — so the run's `launch`
  # mark would record one model while the leaf ran on the other, and that field is exactly what a
  # per-model cost comparison joins on.
  #
  # The check belongs to this branch and not after the if/else: the default sandbox above
  # carries no `--model`, so a run that set no VERIFY_LEAF_ARGS has nothing to clash and must
  # not pay a leaf-model.sh process to be told so. It is also what makes the diagnostic below
  # true of what it names — the array scanned IS the caller's flags, not whatever leaf_args
  # ended up being.
  #
  # Refused before the leaf launches, because a leaf paid for is the cost the refusal exists to
  # save. Exit 2: no answer could be obtained, the plumbing speaking rather than a verdict. A
  # leaf-model.sh refusal (exit 2, whitespace) is read here as "no model chosen" and left to
  # preflight, which runs the resolver once per role before any cycle and reports its diagnostic.
  resolved_model="$("$HERE/leaf-model.sh" "$leaf_name")" || resolved_model=""
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

# Build the blind prompt (exits 2 on unknown phase / unreadable files — propagated).
prompt="$("$HERE/build-verify-prompt.sh" "${step_args[@]+"${step_args[@]}"}" "$phase" "$spec_file" "$test_path" "$target")"

# Launch the verifier leaf THROUGH THE SUPERVISOR (no leaf is launched directly, #4).
# supervise.sh owns the .tdd/verify-<phase>.log progress log and returns the captured
# output; a hung/runaway verifier is killed and reported killed-stuck (exit 2).
mkdir -p .tdd
promptfile=".tdd/$leaf_name.prompt"
printf '%s' "$prompt" > "$promptfile"

# The tree the verifier is handed, recorded before it launches (issue #172). The leaf's
# sandbox denies four editing TOOLS (`--disallowedTools` above) and says nothing about Bash,
# through which a leaf can write any file — so what a verifier did to the repo is a question
# only a before/after comparison answers. The comparison is by CONTENT, which is what makes a
# mutation the verifier reverted itself a non-event: verify-pin.md:17-22 tells it to break the
# production code, run the test and restore, and that ends where it started.
#
# Both halves of that — taking the snapshot and putting the tree back — are one git command
# run against an index holding every path the working tree currently has, untracked ones
# included, which is what this builds: `git add -A` with GIT_INDEX_FILE naming a throwaway
# file, so the real index is never touched and no ref is written (not `refs/stash`, see #169).
# What the two commands leave behind is tree and blob objects, unreachable garbage the next
# `git gc` collects. A directory `git add -A` fails in is one with no repo to guard, and the
# empty output is what says so to both callers.
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

# The same index run backwards: `read-tree -u --reset` against the snapshot makes the working
# tree that tree — rewriting what the verifier changed and DELETING what it created, because a
# path in that index and not in the tree is removed. Ignored paths are in neither, so the run's
# own state under `.tdd/` (the supervisor's log, this leaf's prompt) survives untouched.
#
# `git checkout -- <path>` and `git reset --hard` are the obvious restores and both are wrong
# here: they restore from HEAD, and verify-green and verify-red run while the developer's work
# is still uncommitted, so either would throw away the very change the step exists to produce.
# The snapshot is the tree the verifier was handed, uncommitted work and all, which is why the
# restore is against it rather than against a commit.
restore_tree() {  # puts the working tree back to the tree object named by $1
  in_temp_index read-tree -u --reset "$1"
}

# HEAD is snapshotted separately from the tree because a commit can move it while leaving the
# working tree byte-identical.
head_snapshot() {  # prints the sha HEAD names, or nothing where there is no repo or no commit
  # --verify is load-bearing: without it, on a repo with no commits yet, git rev-parse prints
  # the literal string `HEAD` on stdout (and exits 128), so the caller would compare "HEAD"
  # against the first commit's sha rather than the empty string this promises.
  git rev-parse --verify HEAD 2>/dev/null || true
}

# The restore that pairs with it, beside it for the same reason restore_tree sits beside
# tree_snapshot: update-ref touches the ref alone, so the working tree restore_tree has already
# put back — the developer's uncommitted work in it included — is left exactly as it stands. It
# is a no-op in the two cases where there is nothing to put back: an empty <before> is a repo
# that had no commits when the verifier launched, so there is no sha to name, and a <before>
# equal to <after> is a HEAD that never moved.
restore_head() {  # points HEAD back at the sha $1 names, where it moved from it and $1 is a sha
  if [[ -n "$1" && "$1" != "$2" ]]; then
    git update-ref HEAD "$1"
  fi
}

# An empty $tree_before is "no repo here to guard" — the tests drive verify.sh in a bare
# temporary directory — and switches the comparison below off rather than failing the run.
# head_snapshot is empty the same way on a repo with no commits yet; an empty $head_before
# then compares unequal to the sha a verifier commit would create, which is the reading that
# reports it.
tree_before="$(tree_snapshot)"
head_before="$(head_snapshot)"

# How many times a leaf that exited cleanly with no VERDICT: line is relaunched (issue #219).
no_verdict_retries="${VERI_NO_VERDICT_RETRIES:-1}"
# Refused before the leaf launches: under `set -u` a word inside the `-lt` below is read as a
# variable name, so a bad value would otherwise surface only after a leaf had been paid for.
if [[ ! "$no_verdict_retries" =~ ^[0-9]+$ ]]; then
  echo "verify: VERI_NO_VERDICT_RETRIES must be a non-negative integer, got '$no_verdict_retries'" >&2
  exit 2
fi

# The context every event below is logged under — the relaunch marks and the verdict — comes from
# leaf-role.sh, the same derivation supervise.sh marks under (supervise.sh:141-157), so both halves
# of one verification file under the same actor and phase; a refusal leaves $role empty and nothing
# is logged, rather than a line whose actor was invented. $leaf_name never changes, so it is asked once.
role="$("$HERE/leaf-role.sh" "$leaf_name")" || role=""
mark() {  # mark <event> [key=value …] -> event.sh under $role, or nothing when leaf-role.sh refused
  if [[ -n "$role" ]]; then
    # shellcheck disable=SC2086  -- intentional word-split of leaf-role.sh's assignments
    env $role "$HERE/event.sh" "$@"
  fi
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

  # A killed-stuck verifier yields no verdict — surface it as malformed (the conductor
  # stops, just as it would on an unparseable verdict).
  if [[ "$scode" -eq 2 ]]; then
    echo "verifier leaf killed-stuck — no verdict rendered (see .tdd/$leaf_name.log)"
    exit 2
  fi

  # Compare the tree back (issue #172). A verifier that left anything behind is a SYSTEM failure
  # — exit 2 — whatever it decided, and its reason is not printed: the conductor's next move
  # after a PASS is `git add -A && git commit` (SKILL.md:526), so a verdict accepted here would
  # commit the verifier's edit as the developer's work, and an edit made before the leaf ran the
  # suite was judged along with the code it was judging. stdout carries what changed instead,
  # because the paths are what a human needs to see to know what the leaf touched.
  if [[ -n "$tree_before" ]]; then
    tree_after="$(tree_snapshot)"
    head_after="$(head_snapshot)"
    changed="$(git diff-tree -r --name-only --no-commit-id "$tree_before" "$tree_after" 2>/dev/null)" || changed=""
    [[ "$head_before" == "$head_after" ]] || changed="${changed:+$changed$'\n'}HEAD"
    if [[ -n "$changed" ]]; then
      # Put it back before bailing. Detecting the tampering and leaving it in place would still
      # lose the step: the conductor stops here, and the tree a human then inspects — and a
      # resumed run continues from — is whatever the verifier left. The two restores are the two
      # snapshots run backwards, in that order: HEAD is pointed back last so it moves against the
      # tree the first one has already put right.
      restore_tree "$tree_before"
      restore_head "$head_before" "$head_after"
      echo "verifier leaf modified the repository — verdict not accepted (see .tdd/$leaf_name.log); changed:"
      printf '%s\n' "$changed"
      exit 2
    fi
  fi

  # The verdict is the parse result of the captured output, not the leaf's process status.
  # parse-verdict.sh's diagnostic is kept rather than streamed, because it is what tells a leaf
  # that rendered no VERDICT: line at all apart from one that rendered a malformed one.
  set +e
  reason="$(printf '%s' "$out" | "$HERE/parse-verdict.sh" 2>"$parse_err")"
  vcode=$?
  set -e
  cat "$parse_err" >&2

  # A leaf that exited without being killed and printed no VERDICT: line at all broke the output
  # contract rather than the plumbing (issue #219): it is relaunched on a fresh attempt instead of
  # bailed. The verifier is blind and re-runs the suite itself, so the relaunch judges the same
  # tree from scratch with the same prompt file.
  #
  # Both the relaunch and the final exit 2 carry `cause=no-verdict` in the event log, a cause
  # supervise.sh never writes: its causes name the watchdog's kill, and this leaf was not killed.
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

# The `verdict` mark (issue #107, ADR-0014). This script is the only place that holds the
# phase and the verdict at once: supervise.sh watched a leaf called `verify-<phase>` succeed
# and knows nothing about what it decided, and parse-verdict.sh read a verdict out of text
# without ever learning which phase the text was about.
#
# The word is derived from $vcode rather than from the reason, because $vcode is what this
# script already turned the leaf's output into — one derivation, not two that must agree.
# `*` covers 2 and nothing else can reach here: parse-verdict.sh exits 0, 1 or 2 only.
case "$vcode" in
  0) word=PASS ;;
  1) word=REJECT ;;
  *) word=malformed ;;
esac

# The mark's other payload value, named beside $word above so the call below reads as the two
# things the event carries rather than as one name and one expression. `%%$'\n'*` strips the
# longest trailing match of newline-and-anything, leaving the first line — the whole of what the
# log takes. A model's justification runs to paragraphs and the log is one line per event; the
# full reason is already mirrored to the issue thread by the conductor, which is where a human
# reads it. A malformed verdict has no reason at all (parse-verdict.sh prints nothing), so this
# is the empty string it actually has.
reason_line="${reason%%$'\n'*}"

mark verdict verdict="$word" reason="$reason_line" ${cause:+cause="$cause"}

printf '%s\n' "$reason"
exit "$vcode"
