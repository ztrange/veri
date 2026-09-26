#!/usr/bin/env bash
# Unit tests for the files under skills/ — none of them may end a background process by a
# job spec. Like no-sigpipe-pipelines.test.sh and no-docs-reads.test.sh this suite has no
# script as its subject: its subject is the tree it is run in. Zero-dependency plain-shell
# asserts, same idiom as no-sigpipe-pipelines.test.sh.
#
# Why this exists (issue #424): a job spec names a row in the job table of the shell that
# started the process, and that table dies with the shell. Once it is gone the number means
# nothing, the child is reparented to PID 1, and nothing is left that knows its identity —
# so the kill reaches no one, and a redirection of its complaint to /dev/null makes that
# silent. Observed 2026-09-22 on this machine: ten orphaned busy-loops, all PPID 1, ~988% of
# CPU between them, twelve and thirteen hours old, quietly distorting every timing this
# repository measures. Two different shell snapshots were represented among them, so this is
# not one bad command but a shape that gets written more than once. `lib/background.sh` is
# the repair — it kills the pid it recorded, a system-wide name that works from any shell —
# and this suite is what stops the next site being written.
#
# Contract under test:
#   No file under skills/ ends a background process by a job spec. A file that does is
#   reported as `<file>:<line>` — the address, not the file, because that is what sends the
#   next author to the site. A site where the job spec is the point is exempted by name in
#   the table below, and only with the reason that says why; an entry carrying no reason
#   fails the run rather than silencing anything.
#
# Killing a background process is not the offence: killing it by a name that dies with the
# shell is. A check that refused every `kill` in the tree would be deleted by the first
# author it blocked, taking the real one with it — and `lib/background.sh`, the fix this
# issue shipped, would be its first victim. So a kill by a recorded pid is left alone.
#
# A comment is not a site: it runs nothing, and the prose here and in `lib/background.sh`
# discusses the shape at length. This suite reads itself along with the rest, which is the
# discipline it asks for: no line below spells the shape it looks for — the pattern is
# assembled from two halves, and a failure quotes the offending line rather than carrying
# one of its own.
#
# Run: skills/tdd/scripts/tests/no-job-spec-kills.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repository whose
# skills/ this reads — its own location, not a fixed path, so a copy of this guard run
# inside another tree answers about that tree.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The directory the rule is about. Everything under it, whatever skill it belongs to: the
# shape cost twelve hours in a script, and a suite writes the same line as readily.
SUBJECT='skills'

# The command half: `kill` as a word of its own, so `pkill`, `killall` and `$KILLED` are not
# one. Written apart from the half below for the reason the header gives — a line of this
# file spelling the whole shape would be its own first offender.
KILL_WORD='(^|[^[:alnum:]_.-])kill'
# The argument half: a job spec, which is a per cent sign and a job number. Any words
# between the two are the kill's own options — `-9`, `-s TERM` — and a word opening with a
# per cent sign is the job spec itself, so the options may not carry one.
JOB_ARGS='([[:space:]]+[^%[:space:]]+)*[[:space:]]+'
JOB_SPEC='%[0-9]'
# The whole shape, for one grep over the subject directory.
JOB_SPEC_KILL="$KILL_WORD$JOB_ARGS$JOB_SPEC"

# EXEMPT[<file>:<line>]="<reason>" — a site where the job spec is the right name, each with
# the sentence that says why the process cannot outlive the shell that holds the job table.
# The reason is what makes an entry an exemption; a bare key is a site someone once wanted
# quiet, and the next reader has no way to tell the two apart, so an entry with no reason
# fails the run instead of excusing anything. The key is the repository-relative path and
# the line, because a basename says which file only as long as no two of them share one.
declare -A EXEMPT=(
  [skills/tdd/scripts/tests/skill-leaf-env.test.sh:975]="a step title's text, single-quoted, that the case hands a launch line as data (#437): the backticks around it are the character under test, and a fixed launch never runs it; an unfixed one runs it in a bash -c with no job table, where it reaches no process at all"
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

# split_site <line> — a `<file>:<line>:<text>` line taken apart into `site_file`, `site_line`
# and `site_text`. Both readers of that shape go through here: the filter below, which needs
# the address to look an exemption up and the text to tell a comment from a kill, and the
# probe under it, which needs the same three to write its report. Counting the two colons in
# one place is what keeps those two readings from drifting apart — a grep hit whose path held
# a colon would otherwise be split one way here and another way there.
split_site() {
  local rest
  site_file="${1%%:*}"
  rest="${1#*:}"
  site_line="${rest%%:*}"
  site_text="${rest#*:}"
}

# kill_lines — every line under the subject directory that ends a background process by a
# job spec and is not a comment, one `<file>:<line>:<text>` per line. One recursive grep
# rather than a walk and a grep per file: the question is the same of every file, and the
# paths it prints are already the addresses a report quotes. `-I` because a compiled artefact
# under the tree — `__pycache__` — is not a file anyone writes a kill in. Both readers below
# start here — the offences, and the check that every exemption still names one of these —
# so the two can never disagree about what counts as a kill.
kill_lines() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ "$site_text" =~ ^[[:space:]]*# ]] && continue
    printf '%s\n' "$hit"
  done < <(cd "$ROOT" && grep -rInE -- "$JOB_SPEC_KILL" "$SUBJECT")
  return 0
}

# sites — the lines kill_lines found that no exemption answers.
sites() {
  local hit
  while IFS= read -r hit; do
    split_site "$hit"
    [[ -n "${EXEMPT[$site_file:$site_line]:-}" ]] && continue
    printf '%s\n' "$hit"
  done < <(kill_lines)
  return 0
}

# probe_no_file_kills_by_job_spec — the criterion. Every site the read above found is one
# report, addressed `<file>:<line>`, quoting the line so the author sees what was matched
# rather than having to go and guess.
probe_no_file_kills_by_job_spec() {
  local site
  while IFS= read -r site; do
    split_site "$site"
    problems+=("$site_file:$site_line ends a background process by a job spec, which names it only in the job table of the shell that started it: once that shell is gone the kill reaches nobody and the process is left running, reparented to PID 1. Kill the pid it recorded instead — see skills/tdd/scripts/lib/background.sh: $(flat "$site_text")")
  done < <(sites)
  return 0
}

# probe_every_exemption_carries_a_reason — the table's own contract. An entry whose value is
# empty exempts nothing: it is reported here, named by its key, and the complaint says that
# the reason is what is missing — so the author is told their exemption is not one rather
# than left reading a report about a kill they thought they had already answered.
probe_every_exemption_carries_a_reason() {
  local key
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${EXEMPT[$key]}" ]] && continue
    problems+=("the exemption entry [$key] carries no reason, so it exempts nothing: an entry is an exemption only when it says why a name that dies with the shell is the right one at that site")
  done
  return 0
}

# 1. One criterion, one case: nothing under skills/ ends a background process by a name that
#    dies with the shell that started it. One case rather than one per file, because the rule
#    is about the directory — a file added tomorrow is covered by existing, and a per-file
#    roster would be the list the recursive read above exists to avoid. The table's own
#    contract is probed in the same case: an entry with no reason is not an exemption, and
#    saying so is part of saying the directory is clean.
name="no file under skills/ ends a background process by a job spec"
problems=()

probe_every_exemption_carries_a_reason
probe_no_file_kills_by_job_spec

report "$name"

# probe_every_exemption_still_names_its_site — an exemption is addressed by line, so a line
# added above its site moves the site out from under it: the key then excuses a line with no
# kill on it, and the kill it was written for is reported as an offence nobody answered. Every
# key must still name a line kill_lines prints.
probe_every_exemption_still_names_its_site() {
  local hit key
  local -A matched=()
  while IFS= read -r hit; do
    split_site "$hit"
    matched[$site_file:$site_line]=1
  done < <(kill_lines)
  for key in "${!EXEMPT[@]}"; do
    [[ -n "${matched[$key]:-}" ]] && continue
    # An exemption whose file is not in this tree at all is not an exemption about this tree.
    # This guard is copied into planted trees and run inside them — job-spec-guard.test.sh
    # plants two files and none of the repository's own — and there every key names a file
    # that was never there, which is not a key left behind by a moved site. The failure this
    # probe exists for leaves the file in place: a line ADDED above the site moves the site,
    # not the file, so `:972` against a fixture now at `:975` is still reported.
    [[ -e "$ROOT/${key%%:*}" ]] || continue
    problems+=("the exemption entry [$key] names a line that no longer ends a background process by a job spec, so it excuses nothing there: the site it was written for has moved, and its key must follow it")
  done
  return 0
}

# 2. The table's keys against the tree: every exemption still names the line it was written
#    for. Case 1 goes red when a site moves away from its key; this case says which key was
#    left behind.
name="every exemption names a line under skills/ that ends a background process by a job spec"
problems=()

probe_every_exemption_still_names_its_site

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
