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
#   And the same asked of `make test` itself: no suite that target would run ends a pipeline
#   that way either. That is the sentence the rule exists for — the baseline preflight reads,
#   the Green leaf runs and both blind verifiers run is the run that goes red on Linux while
#   the Mac that launched it stayed green — and the target's roster is not this directory's
#   glob: it descends into the fast tier under `unit/` too.
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

# The repository itself, four directories up: what case 2 asks `make` about, and what the
# repo-relative paths a roster line carries are resolved against.
ROOT="$(cd "$HERE/../../../.." && pwd)"

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

# A pipeline is not a line: the shell joins a line whose last token is a `|` to the one
# below it, so the ordinary way to write a long pipeline — the pipe ending one line and the
# reader opening the next — is the same offence written differently, and a guard that only
# reads a line on its own is one an author escapes by pressing return. The two halves are
# matched a line apart: this one is the trailing `|`, again not one of a `||`.
WRAPPING_PIPE='(^|[^|])\|[[:space:]]*$'
# And this one is the reader opening the line below it, with nothing but indentation before
# it — a reader further along that line is fed by something else on it, not by the pipe
# above.
READER_OPENS="^[[:space:]]*$READER"

# EXEMPT[<suite>:<line>]="<reason>" — a site where the reader's early exit is the point,
# each with the sentence that says why: what the writer is, and why its SIGPIPE cannot be
# mistaken for the answer there. The reason is what makes an entry an exemption; a bare key
# is a site someone once wanted quiet, and the next reader has no way to tell the two apart,
# so an entry with no reason fails the run instead of excusing anything.
declare -A EXEMPT=(
  # The one site this issue did not repair. It is not a line of the suite at all: it is a
  # line of the `#!/bin/sh` stub `claude` the suite writes out in a quoted heredoc, and that
  # stub declares no `pipefail` of its own — so the writer's SIGPIPE is the status of
  # nothing there, the `sed` feeding it is one `$(…)` whose value is then tested with
  # `[ -n "$base" ]`, and the repair this file prescribes is not available either, since
  # process substitution is bash's and the stub is POSIX sh by design. A text read cannot
  # tell a heredoc from the shell around it, which is why the entry is here rather than in
  # the pattern.
  [run-conductor.test.sh:66]="a line of the POSIX-sh stub \`claude\` the suite writes in a heredoc, not of the suite: that shell sets no pipefail, so the sed's SIGPIPE is never a status anything reads, and bash's process substitution is not available there to repair it with"
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

# wrapped_sites <file> — the lines of <file> that open with an early-exiting reader and are
# fed by a `|` ending the line above them, one `<lineno>:<text>` per line. Two greps and a
# lookup rather than a line-by-line read of the file: each half is a question grep answers
# over the whole file at once, and what makes the pair a pipeline is only that their line
# numbers are one apart.
wrapped_sites() {
  local file="$1" hit lineno
  local -A ends_in_pipe=()
  while IFS= read -r hit; do
    ends_in_pipe["${hit%%:*}"]=1
  done < <(grep -nE "$WRAPPING_PIPE" "$file")
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    [[ -n "${ends_in_pipe[$((lineno - 1))]:-}" ]] || continue
    printf '%s\n' "$hit"
  done < <(grep -nE "$READER_OPENS" "$file")
  return 0
}

# unexempted_sites <file> — the lines of <file> that feed a writer into a reader leaving
# before EOF and are neither a comment nor an exemption, one `<lineno>:<text>` per line.
# Both cases ask exactly this of a file and differ only in the consequence they then name,
# so the reading — the pipefail condition, the pattern, the comment skip and the table
# lookup keyed on the suite's basename — is written here once rather than in each of them.
# A file that declares no `pipefail` names no site: the writer's SIGPIPE is not the
# pipeline's status there, so there is nothing to report.
unexempted_sites() {
  local file="$1" name hit lineno text
  local -A seen=()
  declares_pipefail "$file" || return 0
  name="$(basename "$file")"
  while IFS= read -r hit; do
    lineno="${hit%%:*}"
    text="${hit#*:}"
    [[ "$text" =~ ^[[:space:]]*# ]] && continue
    [[ -n "${EXEMPT[$name:$lineno]:-}" ]] && continue
    # One site is one report however many of the two readings reached it: a line that is
    # both fed by the pipe above it and ends a pipeline of its own is still one line to
    # repair.
    [[ -n "${seen[$lineno]:-}" ]] && continue
    seen["$lineno"]=1
    printf '%s:%s\n' "$lineno" "$text"
  done < <(grep -nE "$PIPE_INTO_READER" "$file"; wrapped_sites "$file")
  return 0
}

# probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader — the criterion. Every
# suite in this directory that declares `pipefail` is asked for the lines that feed a writer
# into either early-exiting reader; a comment is not one, because a comment cannot run anything
# and the prose here discusses the shape at length.
#
# The suites are found by globbing this directory rather than by a list, because the list is
# what the next one would be added outside of; `make test` finds them the same way.
probe_no_pipefail_suite_ends_a_pipeline_in_an_early_exiting_reader() {
  local f name site
  for f in "$HERE"/*.test.sh; do
    [[ -e "$f" ]] || continue
    name="$(basename "$f")"
    while IFS= read -r site; do
      problems+=("$name:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so the status asserted on is the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done < <(unexempted_sites "$f")
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

# roster <target> — the suite paths <target> would run, one repo-relative path per line.
# `make -n` prints the recipe with the target's wildcards already expanded and executes none
# of it, which is the only way to ask this question: running `make test` to find out what
# `make test` runs is the recursion, and it costs ~154 s besides. Same idiom as
# no-docs-reads.test.sh's roster helper and suite-lanes.test.sh's, which read their targets'
# lists the same way.
roster() { make -C "$ROOT" -n "$1" 2>&1 | grep -o '[^ ]*\.test\.sh' | sort -u; }

# probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader — the same
# question asked of the roster `make test` would run rather than of this directory's glob,
# and answered the same way, line by line, through the same exemption table. A roster entry
# is exempted by its basename, as the table's `<suite>:<line>` key says: a site is one site
# whichever of the two probes reaches it, and one key per site is what keeps a reason from
# having to be written twice. What an empty roster means, and why it is said rather than
# failed over, is at the line that says it.
probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader() {
  local rel site
  local -a listed=()
  while IFS= read -r rel; do
    [[ -n "$rel" ]] || continue
    listed+=("$rel")
    while IFS= read -r site; do
      problems+=("$rel:${site%%:*} ends a pipeline in a reader that leaves before EOF, under a suite that declares pipefail, so \`make test\` — the baseline preflight reads, the Green leaf runs and both blind verifiers run — asserts on the writer's SIGPIPE rather than the reader's answer: $(flat "${site#*:}")")
    done < <(unexempted_sites "$ROOT/$rel")
  done < <(roster test)
  # An empty roster is something this case found, not an offence it discovered: a tree with
  # no Makefile — every scratch tree sigpipe-guard.test.sh plants — has no suite `make test`
  # would run, so nothing in it reads its own writer's SIGPIPE as an answer and there is
  # nothing to fail over. Failing there would make the guard's verdict about such a tree
  # unreadable: red whatever was planted in it. What replaces the failure is not silence —
  # the finding is said, naming the question that was asked, so an empty roster in a real
  # tree is still visible to whoever reads the output.
  [[ "${#listed[@]}" -gt 0 ]] ||
    echo "note: \`make -n test\` named no suite at all, so no roster was read: nothing this case could ask about"
  return 0
}

# 2. The same rule asked of the target instead of the directory. Case 1 is the rule an
#    author breaks, and it finds its suites by globbing the directory they are written in.
#    This case is the consequence the rule is for: `make test` is what preflight reads its
#    baseline off, what every Green leaf runs and what both blind verifiers run, and it is
#    the run that goes red on Linux while the Mac that launched it stayed green. So what has
#    to hold is that nothing *that target runs* reads its own writer's SIGPIPE as an answer.
#
#    The two are not the same file list: the target also runs the fast tier under `unit/`,
#    which case 1's glob does not descend into, and a suite named into the target from
#    outside this directory would reach the baseline the same way. Asking the target itself
#    costs one `make -n`.
name="no suite \`make test\` runs that declares pipefail ends a pipeline in a reader that leaves before EOF"
problems=()

probe_no_suite_the_target_runs_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

# probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader — the criterion asked of the
# repository's Makefile: every recipe line that ends a pipeline in either early-exiting reader
# is named as `Makefile:<line>`. No `pipefail` condition here: the recipe shell is `/bin/sh`,
# which declares none, and the hazard does not need it — a writer killed mid-write complains
# on stderr and exits non-zero, and a reader's early exit is what kills it (#524, where GNU
# tail's `Broken pipe` failed a green suite).
probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader() {
  local site
  while IFS= read -r site; do
    problems+=("Makefile:${site%%:*} ends a pipeline in a reader that leaves before EOF, so the writer feeding it can die of SIGPIPE, complain and fail the recipe over an answer the reader already had: $(flat "${site#*:}")")
  done < <(grep -nE "$PIPE_INTO_READER" "$ROOT/Makefile")
  return 0
}

# 3. The same rule asked of the recipes that enforce it (#524). The `make test` recipe's own
#    count-line check ended a pipeline in a reader leaving before EOF and failed a green suite
#    on CI, while cases 1 and 2 read only suites.
name="no Makefile recipe line ends a pipeline in a reader that leaves before EOF"
problems=()

probe_no_recipe_ends_a_pipeline_in_an_early_exiting_reader

report "$name"

# probe_count_line_check_lets_its_writer_finish — the recipe's own count-line check, run as
# make would run it, behind a stub `tail` that writes the count line and then 1 MB more —
# past any pipe buffer, on either runner — and records whether it got to write it all. A
# reader that consumes to EOF lets it finish; one that leaves at its first match closes the
# pipe under it, and the stub's write is cut, which is the SIGPIPE GNU tail complained of on
# CI (#524). The check is read out of the Makefile rather than restated, and its make
# variables are asked of make through the `count-line-guard` target, as run-suite.sh does.
probe_count_line_check_lets_its_writer_finish() {
  local check scratch status
  check="$(grep -m 1 'tail -n 1 "\$\$suite_out"' "$ROOT/Makefile")"
  if [[ -z "$check" ]]; then
    problems+=("no count-line check reading \"\$\$suite_out\" through tail was found in the Makefile, so the criterion went unasked")
    return 0
  fi
  eval "$(make -s -C "$ROOT" count-line-guard)"
  check="${check%%||*}"
  check="${check//\$\$/\$}"
  check="${check//\$(COUNT_LINE)/$COUNT_LINE}"
  scratch="$(mktemp -d)"
  cat > "$scratch/tail" <<'STUB'
#!/bin/sh
printf '13 passed, 0 failed\n'
if dd if=/dev/zero bs=65536 count=16 2>/dev/null; then echo finished > "$STUB_MARK"; else echo cut > "$STUB_MARK"; fi
STUB
  chmod 755 "$scratch/tail"
  STUB_MARK="$scratch/mark" PATH="$scratch:$PATH" suite_out=/dev/null sh -c "$check"
  status=$?
  [[ "$status" -eq 0 ]] ||
    problems+=("the count-line check exited $status over a writer whose first line is a count line: $(flat "$check")")
  [[ "$(cat "$scratch/mark" 2>/dev/null)" == finished ]] ||
    problems+=("the count-line check's writer was cut off mid-write ($(cat "$scratch/mark" 2>/dev/null || echo 'no mark')), so its reader left before EOF: $(flat "$check")")
  rm -rf "$scratch"
  return 0
}

# 4. The repair itself, as behaviour rather than text (#524): case 3 asks what the recipe
#    lines spell, this asks what the count-line check does to the writer feeding it.
name="make test's count-line check reads the suite's last line to EOF, so its writer is never cut off (#524)"
problems=()

probe_count_line_check_lets_its_writer_finish

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
