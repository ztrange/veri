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
#     --step = the ledger's own line for the step under judgement (#223), passed straight
#              through to build-verify-prompt.sh
#     --fast-cmd = the fast tier's test command (#341), required for green, passed straight
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
# --fast-cmd (#341) rides alongside it, straight through: green's prompt names that command.
#
# The call this script accepts, spelled once: both refusals below quote it back.
USAGE="usage: verify.sh [--step '<STEP>'] [--fast-cmd '<CMD>'] <phase> <issue-spec-file> <test-path> [<target-test-id>]"

flag_args=()
while [[ "${1:-}" == --step || "${1:-}" == --fast-cmd ]]; do
  [[ -n "${2:-}" ]] || { echo "verify: $1 needs a value" >&2; echo "$USAGE" >&2; exit 2; }
  flag_args+=( "$1" "$2" )
  shift 2
done

# Every required positional is checked here, in one place, rather than each being read
# through a `${N:?…}` expansion: that expansion aborts the shell with status 1, the code
# CLAUDE.md's "Exit codes are the API" reserves for a real answer — the leaf ran and
# failed, the verifier said REJECT. A call missing an argument produced no answer at all,
# which is exit 2, and the conductor branches on exactly that difference (#270). The check
# covers <test-path> as well as <phase> and <issue-spec-file>, so `verify.sh green <spec>`
# refuses the way `verify.sh` with nothing does. `$#` is asked first and `[[ … && … ]]`
# stops at the first false operand, so the `$2` and `$3` below are only read once they
# exist and `set -u` has nothing to abort on.
[[ $# -ge 3 && -n "$1" && -n "$2" && -n "$3" ]] || { echo "$USAGE" >&2; exit 2; }
phase="$1"
spec_file="$2"
test_path="$3"
target="${4:-}"

HERE="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=lib/leaf-model.sh
source "$HERE/lib/leaf-model.sh"

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
  # $(...) still forks a subshell to run leaf_model in, so its `return 2` reaches this
  # `||` exactly the way the old subprocess's exit 2 did.
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

# Build the blind prompt (exits 2 on unknown phase / unreadable files — propagated).
prompt="$("$HERE/build-verify-prompt.sh" "${flag_args[@]+"${flag_args[@]}"}" "$phase" "$spec_file" "$test_path" "$target")"

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

# The operator's global git config, snapshotted the same way (issue #276). It lives under $HOME,
# outside the tree, so the comparison above cannot see it — yet a leaf that sets a key in it and
# is killed before its cleanup runs breaks git for every run on the machine. run-leaf.sh gives
# the leaf a private GIT_CONFIG_GLOBAL, the same `$HOME/.gitconfig` path it copies from, so only
# a write by path still reaches this file. Content, not mtime, and a missing file reads as empty.
operator_gitconfig="$HOME/.gitconfig"
gitconfig_snapshot() {  # prints the checksum of the operator's global git config, or nothing if absent
  if [[ -f "$operator_gitconfig" ]]; then cksum < "$operator_gitconfig"; fi
}
gitconfig_before="$(gitconfig_snapshot)"

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
role="$(leaf_role "$leaf_name")" || role=""
mark() {  # mark <event> [key=value …] -> event.sh under $role, or nothing when leaf_role refused
  if [[ -n "$role" ]]; then
    # shellcheck disable=SC2086  -- intentional word-split of leaf_role's assignments
    env $role "$HERE/event.sh" "$@"
  fi
}

# The one refusal both comparisons below end in: what the leaf modified, then the paths that
# changed on stdout, one per line, and exit 2 whatever the verdict was.
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
      refuse_modified "the repository" "$changed"
    fi
  fi

  # The operator's global git config is not restored: which of its lines the leaf wrote is not
  # something this script can tell apart from what the operator changed meanwhile, so it is named
  # for a human to put right rather than guessed at.
  if [[ "$(gitconfig_snapshot)" != "$gitconfig_before" ]]; then
    refuse_modified "the operator's global git config" "$operator_gitconfig"
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
# The mark that names the trouble is read out of the same branch (issue #409): a verification
# that did not PASS is one a human will want to read back, and what it is called must be one of
# the words the issue's list uses, not a second spelling of the verdict. REJECT is `reject`; a
# malformed verdict is `no-verdict` when that is what $cause already says it was — the leaf
# finished and printed no VERDICT: line — and `malformed` when the line was there and unreadable.
case "$vcode" in
  0) word=PASS ;;
  1) word=REJECT;    trouble=reject ;;
  *) word=malformed; trouble="${cause:-malformed}" ;;
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

# A verdict that was not a PASS is a troubled step, and a troubled step's evidence is about to be
# destroyed: the rejected tree is never committed (a green commit lands only after verify-green
# PASSes) and `.tdd/verify-<phase>.log` is reused by the next step's leaf of the same name. So the
# worktree as the developer left it goes to a side ref and the leaf's own output is copied beside
# it (issue #409). This script is where that can be decided, for the same reason the `verdict` mark
# above is: it is the only place the phase and the verdict are both known.
#
# The ref and the copies are named out of the very values the event above was written with — the
# run's VERI_ISSUE and VERI_STEP, and the attempt read back out of $role, which is what `mark` fed
# to event.sh — so a reader holding the `verdict` line gets to the preserved material by
# substituting its own fields, rather than by knowing a second naming convention.
if [[ "$word" != PASS ]]; then
  # Four things must hold before anything is written, and each says "there is nothing to pair":
  # $tree_before is this script's own spelling of "a repo here to guard" (the tests drive verify.sh
  # in a bare temporary directory, where there is no HEAD to hang a commit off), an empty $role
  # means no event was logged, and without the run's issue and step there is no name to file under.
  attempt="${role##*VERI_ATTEMPT=}"
  if [[ -n "$tree_before" && -n "$role" && -n "${VERI_ISSUE:-}" && -n "${VERI_STEP:-}" ]]; then
    # Preservation never changes a verdict: it runs after the verdict is decided and its failure is
    # reported, not propagated. A run that loses its evidence is worse off than one that does not,
    # but a run that loses its verdict to a failed `git update-ref` has lost the step itself.
    "$HERE/preserve-attempt.sh" "$VERI_ISSUE" "$VERI_STEP" "$leaf_name" "$attempt" "$trouble" \
      || echo "verify: could not preserve the $trouble attempt (issue $VERI_ISSUE step $VERI_STEP $leaf_name attempt $attempt)" >&2
  fi
fi

printf '%s\n' "$reason"
exit "$vcode"
