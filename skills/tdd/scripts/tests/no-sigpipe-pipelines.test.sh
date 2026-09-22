#!/usr/bin/env bash
# Unit tests for the suites in this directory — a suite that declares `pipefail` must not
# end a pipeline in a reader that exits early. Like no-docs-reads.test.sh,
# hermetic-suites.test.sh and count-line-guard.test.sh this suite has no script as its
# subject: its subject is the tree it is run in. Zero-dependency plain-shell asserts, same
# idiom as no-docs-reads.test.sh.
#
# Why this exists (issue #422): `grep -q` exits on its first match. If the writer feeding it
# still has bytes to push, its next write lands on a closed pipe, it dies of SIGPIPE (141),
# `pipefail` hands that 141 up as the pipeline's status, and the assertion built on that
# status is inverted. The bug is green on the development Mac and red on CI — BSD grep
# buffers ~16 KB, so the writer needs one write and the race cannot happen, while glibc
# gives the pipe 4096 bytes — which is the worst shape it can take: the leaf and the blind
# verifier both run on the Mac, so a run reports green and the PR is red. It cost two
# consecutive runs, count-line-guard.test.sh (#418) and prompt-test-tiers.test.sh (#416).
# Repairing those sites fixes today; this suite is what stops the next one being written.
#
# Contract under test:
#   No suite under this directory that declares `pipefail` ends a pipeline in a reader that
#   leaves before EOF — a `grep` whose options carry `q`, or a `head`. A suite that does is
#   reported as `<suite>:<line>` — the address, not the file, because that is what sends the
#   next author to the site. A site where leaving before EOF is the point is exempted by
#   name in the table below, and only with the reason that says why; an entry carrying no
#   reason fails the run rather than silencing anything.
#
# `pipefail` is half of the condition, and the half that makes the shape a bug rather than a
# habit. Without it the pipeline's status is the reader's own, the writer's SIGPIPE never
# reaches the assertion, and there is nothing here to catch — so a suite that does not
# declare it is left alone. A check that refused every pipeline into a `grep -q` would be
# deleted by the first author it blocked, taking the real one with it.
#
# The repair, where this suite names a site, is per-site and small: let the reader consume
# to EOF (`grep -F … > /dev/null` in place of `grep -qF …`), or feed it by redirection
# rather than a pipe (`grep -qF … < <(…)`), which moves the status off the writer. Neither
# `trap '' PIPE` nor dropping `pipefail` is one: `pipefail` is what makes the rest of these
# suites honest, and #157 is the record of what an untrusted exit status costs here.
#
# This suite reads itself along with the rest, which is the discipline it asks for: no line
# below spells the shape it looks for — the pattern is assembled from two halves, and the
# failure message quotes the offending line rather than carrying one of its own.
#
# Run: skills/tdd/scripts/tests/no-sigpipe-pipelines.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

# The declaration that makes the shape a bug: `set -uo pipefail`, `set -o pipefail`, or any
# other spelling of the option on a `set` line.
PIPEFAIL_DECL='^[[:space:]]*set[[:space:]].*pipefail'

# One reader half: a grep whose short-option cluster carries `q`, which is `grep -q`,
# `grep -qF --`, `grep -Eqi` and `grep -vq` alike. The cluster has to be one of the option
# words that follow the command — everything before it is another option word — rather than
# a dash-word anywhere on the line, or `[[ "$(… | grep -c '^')" -eq 1 ]]` reads as one on
# the strength of its `-eq` (verify.test.sh:715, which counts lines and asserts on the
# count, so its reader consumes to EOF and there is nothing there to catch).
GREP_READER='(grep|egrep|fgrep)([[:space:]]+-[A-Za-z]*)*[[:space:]]+-[A-Za-z]*q'
# The other: `head`, which leaves as soon as it has the lines it was asked for, with the
# same consequence for the writer behind it — a closed pipe, SIGPIPE, and `pipefail`
# handing that 141 up as the pipeline's status. A different reason to leave, the same
# inversion. It has to be a whole command word, or `ahead`, `header` and `$HEAD_SHA` all
# read as one; no option list is required after it, because a bare `head` is `head -n 10`.
HEAD_READER='head([[:space:]]|$)'
# Either reader, for the one pattern below: what makes the shape a bug is that the reader
# leaves before EOF, not which of the two it is.
READER="($GREP_READER|$HEAD_READER)"
# The pipe half, prefixed to it: a `|` that is not one of a `||`, which is a boolean and not
# a pipeline at all. Written as two halves for the reason the header gives — a line of this
# file spelling the whole shape would be its own first offender.
PIPE_INTO_READER="(^|[^|])\\|[[:space:]]*[^|]*(^|[[:space:]])$READER"

# EXEMPT[<suite>:<line>]="<reason>" — a site where the reader's early exit is the point,
# each with the sentence that says why: what the writer is, and why its SIGPIPE cannot be
# mistaken for the answer there. The reason is what makes an entry an exemption; a bare key
# is a site someone once wanted quiet, and the next reader has no way to tell the two apart,
# so an entry with no reason fails the run instead of excusing anything.
declare -A EXEMPT=(
  # Nothing today: this issue repaired every site it found rather than listing them.
)

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which line broke the rule rather than just that some line did.
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

# flat <text> — one line of it, for a failure message: newlines become slashes so a quoted
# line stays one line. Pure parameter expansion rather than a pipe into `tr`, which is two
# processes per problem line.
flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

# declares_pipefail <file> — true when the suite turns the option on. Asked once per suite
# rather than once per line, because it is a property of the file.
declares_pipefail() { grep -Eq "$PIPEFAIL_DECL" "$1"; }

# probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader — the criterion. Every
# suite in this directory that declares `pipefail` is asked for the lines that feed a writer
# into either early-exiting reader; a comment is not one, because a comment cannot run anything
# and the prose here discusses the shape at length.
#
# The suites are found by globbing this directory rather than by a list, because the list is
# what the next one would be added outside of; `make test` finds them the same way.
probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader() {
  local f name hit lineno text
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    declares_pipefail "$f" || continue
    name="$(basename "$f")"
    while IFS= read -r hit; do
      lineno="${hit%%:*}"
      text="${hit#*:}"
      [[ "$text" =~ ^[[:space:]]*# ]] && continue
      [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
      problems+=("$name:$lineno ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so the status asserted on is the writer's SIGPIPE rather than the reader's answer: $(flat "$text")")
    done < <(grep -nE "$PIPE_INTO_READER" "$f")
  done
  return 0
}

# probe_every_exemption_carries_a_reason — the table's own contract. An entry whose value
# is empty exempts nothing: it is reported here, named by its key, and the complaint says
# that the reason is what is missing — so the author is told their exemption is not one
# rather than left reading a pipeline report they thought they had already answered.
probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing: an entry is an exemption only when it says why the reader's early exit is the point at that site")
  done
  return 0
}

# 1. One criterion, one case: nothing in this directory reads its own writer's SIGPIPE as an
#    answer. One case rather than one per suite, because the rule is about the directory — a
#    suite added tomorrow is covered by existing, and a per-suite roster would be the list
#    the glob above exists to avoid. The table's own contract is probed in the same case:
#    an entry with no reason is not an exemption, and saying so is part of saying the
#    directory is clean.
name="no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF"
problems=()

probe_every_exemption_carries_a_reason
probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
