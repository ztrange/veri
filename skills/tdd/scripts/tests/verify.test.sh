#!/usr/bin/env bash
# Tests for scripts/verify.sh — the single "verify" verb the conductor calls. It chains
# the three tested units: build-verify-prompt.sh (blind prompt) → run-leaf.sh (launch a
# claude -p verifier leaf) → parse-verdict.sh (extract the verdict). Driven against a
# stub claude (via CLAUDE_BIN) that prints a canned verdict and records its argv.
#
# `claude -p` always exits 0 regardless of the verdict, so verify.sh's exit status must
# come from PARSING the leaf's output, not from the leaf's process status.
#
# Run: scripts/tests/verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
VERIFY="$HERE/../verify.sh"
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work"' EXIT

# No case here waits on the real clock. Every verification polls its leaf at 0.02 s instead of
# supervise.sh's default 1 s, pinned here rather than inherited (see hermetic-suites.test.sh);
# at 1 s each of this suite's ~40 verifications waited out one whole poll before it saw its
# leaf finish. And a hung leaf is found on the next poll instead of after a real heartbeat
# window, through the injected clock supervise.test.sh describes in full: supervise.sh reads
# now with `date +%s` and the heartbeat with `stat`, stubs of both come first on PATH, and a
# hanging stub leaf moves time with `clock-jump` — one second past its window, which the next
# poll sees as silence. The clock's history is kept in $TEST_CLOCK, outside the repository a
# verification runs in, because verify.sh reads any file a verifier leaves in the tree as
# tampering.
export VERI_POLL=0.02
# kill_tree's grace-loop poll (real sleep — it checks `kill -0`, an OS fact, not the injected
# clock below): every hung-verifier case here gets killed, so left at the 0.1s production
# default it would add up to 5 x 0.1s of real wall time per kill across this suite's several
# killed-stuck cases, for no observation any case makes.
export VERI_KILL_POLL=0.01
export TEST_CLOCK="$stubdir/clock"
clockbin="$stubdir/clockbin"; mkdir -p "$clockbin"
realdate="$(command -v date)"
realstat="$(command -v stat)"
cat > "$clockbin/date" <<D
#!/bin/sh
if [ "\$*" = "+%s" ]; then
  offset="\$(tail -n 1 "\$TEST_CLOCK" 2>/dev/null | cut -d' ' -f2)"
  printf '%s\n' "\$(( \$("$realdate" +%s) + \${offset:-0} ))"
else
  exec "$realdate" "\$@"
fi
D
cat > "$clockbin/stat" <<D
#!/bin/sh
if [ "\$#" -eq 3 ]; then
  if [ "\$1 \$2" = "-c %Y" ] || [ "\$1 \$2" = "-f %m" ]; then
    exec python3 -c '
import os, sys
try:
    m = os.stat(sys.argv[1]).st_mtime
except OSError:
    sys.exit(1)
offset = 0
try:
    for line in open(sys.argv[2]):
        at, value = line.split()
        if float(at) <= m:
            offset = int(value)
except OSError:
    pass
print(int(m) + offset)' "\$3" "\$TEST_CLOCK"
  fi
fi
exec "$realstat" "\$@"
D
cat > "$clockbin/clock-jump" <<'C'
#!/bin/sh
exec python3 -c '
import sys, time
offset = 0
try:
    offset = int(open(sys.argv[2]).read().split()[-1])
except (OSError, IndexError):
    pass
with open(sys.argv[2], "a") as f:
    f.write("%r %d\n" % (time.time(), offset + int(sys.argv[1])))' "$1" "$TEST_CLOCK"
C
chmod +x "$clockbin/date" "$clockbin/stat" "$clockbin/clock-jump"
export PATH="$clockbin:$PATH"
cat > "$stubdir/claude" <<'STUB'
#!/bin/sh
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 0
STUB
chmod +x "$stubdir/claude"

printf 'slugify must lowercase the title and join words with hyphens.' > "$work/spec.md"

# verify_in <dir> <phase> <fake-out-text> [<stub-claude>] [<step>] — one verification of $work/spec.md
# against a stub claude, run in <dir> with the stub's argv recorded at <dir>/argv. stdout is the
# verifier's reason and the exit status is verify.sh's, so a caller reads whichever of the two it
# is about. Every helper below is this call, so the stub wiring and the fixture arguments — the
# spec, the test path, the test id — are spelled once rather than once per helper. The stub
# defaults to the canned-verdict one; a caller wanting another passes it, and `env` (no `-i`)
# hands that stub the caller's own environment too, which is how the mutating stub below gets
# its mutation. A non-empty <step> is passed as `--step '<step>'` before the positionals (#223),
# which is the only way a step reaches verify.sh; an absent one leaves the call exactly what it
# was, so every caller written before the flag existed still spells the unscoped verification.
verify_in() {
  local slot4=test_lowercases; [[ "$2" == refactor ]] && slot4=0123abc  # refactor's is a base sha (#151)
  local flag_args=(); [[ -n "${5:-}" ]] && flag_args=( --step "$5" )
  [[ "$2" == green || "$2" == refactor ]] && flag_args+=( --fast-cmd "make unit" )  # both require it (#341)
  ( cd "$1" && env CLAUDE_BIN="${4:-$stubdir/claude}" ARGV_OUT="$1/argv" FAKE_OUT_TEXT="$3" \
      "$VERIFY" "${flag_args[@]+"${flag_args[@]}"}" "$2" "$work/spec.md" tests/test_slugify.py "$slot4" )
}

verify() {  # verify <fake-out-text> <phase> -> runs in $work, sets $out/$code
  out="$(verify_in "$work" "$2" "$1")"
  code=$?
}

# the second stub never finishes, so the supervisor's stuck-detection is what ends the run: it
# writes a line and then falls silent while the injected clock moves past its window
cat > "$stubdir/claude-hang" <<'STUB'
#!/bin/sh
echo "thinking..."; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60
STUB
chmod +x "$stubdir/claude-hang"

hung_leaf() {  # hung_leaf -> runs in $work, sets $out/$code, stderr in $work/err
  # VERI_STUCK_RETRIES=0 is pinned, not inherited: both hung-leaf cases here are about a
  # single attempt, so the caller's environment must not be able to add retries (each extra
  # attempt waits out the heartbeat window again, changing the suite's wall time).
  out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_STUCK_RETRIES=0 \
            VERI_HEARTBEAT=1 VERI_POLL=0.02 "$VERIFY" red "$work/spec.md" \
            tests/test_slugify.py test_lowercases 2>"$work/err" )"
  code=$?
}

# 1. a PASS verdict from the leaf → verify.sh exits 0 and surfaces the reason
verify 'I ran it.
VERDICT: PASS
REASON: Target test and full suite are green.' green
{ [[ "$code" == 0 ]] && [[ "$out" == *'full suite are green'* ]]; } && ok \
  || no "PASS verdict exits 0 with reason (code=$code)"

# 2. a REJECT verdict → exit 1, reason surfaced for mirroring to the issue
verify 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.' red
{ [[ "$code" == 1 ]] && [[ "$out" == *'private helper'* ]]; } && ok \
  || no "REJECT verdict exits 1 with reason (code=$code)"

# 3. malformed leaf output (no verdict) → exit 2, so the conductor never proceeds on a
#    verification it could not read
verify 'the leaf rambled and never rendered a verdict' green
[[ "$code" == 2 ]] && ok || no "malformed leaf output exits 2 (code=$code)"

# 4. the blind prompt actually reaches the leaf: the issue spec is in the leaf's argv,
#    end-to-end through build-verify-prompt.sh
verify 'VERDICT: PASS
REASON: ok' red
grep -q 'slugify must lowercase' "$work/argv" && ok || no "spec reaches the leaf (blind prompt built + passed)"

# 5. an unknown phase fails fast (exit non-zero), surfaced from the builder
out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$work/argv" \
          FAKE_OUT_TEXT='VERDICT: PASS' "$VERIFY" bogus "$work/spec.md" t x 2>/dev/null )"
code=$?
[[ "$code" -ne 0 ]] && ok || no "unknown phase exits non-zero (code=$code)"

# 6. a hung verifier leaf is killed by the supervisor → no verdict → exit 2, so the
#    conductor never proceeds on a verification it could not obtain
hung_leaf
{ [[ "$code" == 2 ]] && [[ "$out" == *'killed-stuck'* ]]; } && ok \
  || no "hung verifier leaf → killed-stuck exit 2 (code=$code)"

# 7. the `pin` phase (the "already satisfied" outcome, #31) speaks the same three exit
#    codes as red/green/refactor — 0 PASS, 1 REJECT, 2 no verdict — so the conductor can
#    branch on a verify-pin result with exactly the code it already uses for verify-red.
verify 'VERDICT: PASS
REASON: The test passes now and fails under the mutation I applied.' pin
pin_pass_code=$code pin_pass_out="$out"
verify 'VERDICT: REJECT
REASON: The test still passes with the behavior removed.' pin
pin_reject_code=$code
verify 'the pin verifier rambled and never rendered a verdict' pin
pin_none_code=$code
{ [[ "$pin_pass_code" == 0 ]] && [[ "$pin_pass_out" == *'fails under the mutation'* ]] \
  && [[ "$pin_reject_code" == 1 ]] && [[ "$pin_none_code" == 2 ]]; } && ok \
  || no "pin phase exit codes: PASS→0 REJECT→1 no verdict→2 (got $pin_pass_code/$pin_reject_code/$pin_none_code)"

# 8. how many attempts a hung verifier leaf gets is fixed by this suite, not by the shell
#    that ran `make test`: with VERI_STUCK_RETRIES=3 exported in the environment, the
#    hung-leaf launch must still run the leaf exactly once — one killed-stuck status line
#    on stderr and no `retry N/M` line — so both the verdict and the suite's wall time are
#    the suite's own answer. The assignment prefix puts the variable in hung_leaf()'s
#    environment for this call only, so no other case sees it; its `env` list overrides it.
VERI_STUCK_RETRIES=3 hung_leaf
stuck_lines="$(grep -c 'supervise\[verify-red\]: killed-stuck' "$work/err")"
retry_lines="$(grep -c 'retry [0-9][0-9]*/[0-9][0-9]*' "$work/err")"
{ [[ "$code" == 2 ]] && [[ "$stuck_lines" -eq 1 ]] && [[ "$retry_lines" -eq 0 ]]; } && ok \
  || no "ambient VERI_STUCK_RETRIES=3 → hung verifier leaf still runs exactly once (code=$code, killed-stuck lines=$stuck_lines, retry lines=$retry_lines)"

# 9. every verification leaves a `verdict` line in the run's event log — `.tdd/events.jsonl`,
#    written through event.sh — carrying the phase it judged, the verdict word and the first
#    line of the reason (issue #107, ADR-0014). This script is the only place that holds all
#    three at once: supervise.sh sees a leaf called `verify-<phase>` succeed and says nothing
#    about what it decided, and parse-verdict.sh reads a verdict out of text but never learns
#    which phase the text was about.
#
#    Three arms, one per verdict word — PASS, REJECT and the malformed output that yields
#    neither — because the criterion names all three, each in a directory of its own under
#    `$work` (so the suite's existing EXIT trap removes them). The event log accumulates
#    across a run and supervise.sh's own `launch` and `exit` marks land in this same file, so
#    a shared directory would leave `verdict_field` reading whichever arm wrote last; the
#    probe demanding exactly one `verdict` line then also pins this mark as written once per
#    verification rather than once per attempt.
#
#    Each arm judges a different phase — green, red, refactor — so a writer that hardcoded
#    one phase, or read it from somewhere other than this run's argv, cannot satisfy all
#    three. The phase is asserted on the line's `phase` field, the context key every event
#    carries (event.sh:49), not on a payload key of its own: a reader grouping a run's lines
#    by phase asks one question of every line, and a verdict filed under an empty phase is
#    exactly what that reader would miss.
#
#    The PASS and REJECT arms' reasons are two lines each, and the assertion is equality with
#    the first — so a writer that logged the whole reason is caught rather than read past.
#    The first line is what the criterion asks for because the log is a line-per-event file
#    and a model's multi-line justification would otherwise break the format the reader
#    depends on; the full reason is already mirrored to the issue thread by the conductor.
#    Only those two arms assert a reason: a malformed verdict has no reason to take a first
#    line of (parse-verdict.sh prints nothing and exits 2), so this case does not invent an
#    answer for what goes there.

verdict_work="$work/verdict"

# verdict_run <arm> <phase> <fake-out-text> — one verification in its own directory under
# $verdict_work. That directory is also where the stub records its argv, since verify_in writes
# it beside the run and the shared `$work/argv` is case 4's evidence. Nothing here reads the
# reason or the exit status: this case's whole subject is the line the run leaves in the log.
verdict_run() {
  # The arm's directory, named once: it is the one made and the one run in — two uses of a
  # single path rather than two expressions a reader has to compare. Absolute, since verify_in
  # both cd's into it and writes ARGV_OUT under it.
  local dir="$verdict_work/$1"
  mkdir -p "$dir"
  verify_in "$dir" "$2" "$3" >/dev/null 2>&1
}

# verdict_field_in <dir> <key> — the value of <key> on the one `verdict` line of the event log
# a verification run in <dir> wrote, or a diagnostic in `<<…>>` when there is no such line, more
# than one, or no log at all. python3 rather than jq, the dependency event.test.sh and
# extract-result.sh already rely on. <dir> names the verification's cwd, not a file: where the log
# lands under it — `.tdd/events.jsonl` — is said once here rather than at each call site.
verdict_field_in() {
  python3 -c '
import sys, json
hits = []
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("event") == "verdict":
        hits.append(obj)
if len(hits) != 1:
    print("<<%d verdict lines>>" % len(hits))
else:
    print(hits[0].get(sys.argv[2], "<<missing>>"))
' "$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo '<<no event log>>'
}

# verdict_field <arm> <key> — the same probe against one arm of the case below, whose directories
# all sit under $verdict_work.
verdict_field() {
  verdict_field_in "$verdict_work/$1" "$2"
}

verdict_run pass green 'I ran it.
VERDICT: PASS
REASON: Target test and full suite are green.
The mutation I applied turned the target test red.'
verdict_run reject red 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.
Rewrite it against the public function.'
verdict_run malformed refactor 'the leaf rambled and never rendered a verdict'

# Each field read once, into a variable the assertion and the failure message share — the
# capture-then-compare shape the cases above already use.
pass_verdict="$(verdict_field pass verdict)"
pass_phase="$(verdict_field pass phase)"
pass_reason="$(verdict_field pass reason)"
reject_verdict="$(verdict_field reject verdict)"
reject_phase="$(verdict_field reject phase)"
reject_reason="$(verdict_field reject reason)"
malformed_verdict="$(verdict_field malformed verdict)"
malformed_phase="$(verdict_field malformed phase)"

{ [[ "$pass_verdict"      == PASS ]] \
  && [[ "$pass_phase"     == green ]] \
  && [[ "$pass_reason"    == 'Target test and full suite are green.' ]] \
  && [[ "$reject_verdict" == REJECT ]] \
  && [[ "$reject_phase"   == red ]] \
  && [[ "$reject_reason"  == 'The test asserts on a private helper, not observable behavior.' ]] \
  && [[ "$malformed_verdict" == malformed ]] \
  && [[ "$malformed_phase"   == refactor ]]; } && ok \
  || no "a verification appends one verdict event carrying the phase, the verdict word and the reason's first line (PASS arm: verdict=$pass_verdict phase=$pass_phase reason=$pass_reason; REJECT arm: verdict=$reject_verdict phase=$reject_phase reason=$reject_reason; malformed arm: verdict=$malformed_verdict phase=$malformed_phase)"

# 10. that verdict line carries the RUN's context too: the issue being solved and the step of
#     its plan the verification belongs to (issue #163). leaf-role.sh derives the actor and the
#     phase from the leaf's name, but nothing in the name `verify-green` says which issue or
#     which step — that context exists only in the environment the conductor launched this
#     verification in, and verify.sh's job is to pass it through, not to invent it. Without it a
#     reader can attribute a verdict to a step only by interleaving its timestamp with the
#     conductor's own `step-start` marks.
#
#     `VERI_ISSUE` and `VERI_STEP` are the names event.sh already reads (event.sh:47-50), so what
#     this pins is that they survive the hop from this suite's environment into the child of the
#     `env $role` line (verify.sh:115) — the one place a `-i`, an explicit variable list, or a
#     line that spelled the context itself would silently drop them.
#
#     `export` in a subshell rather than an assignment prefix on the function call: the two
#     values have to reach a grandchild — verify.sh's own child — and the subshell also keeps
#     them out of every case after this one, which the log of a shared `$work` would otherwise
#     see. The arm's directory is written inside it and outlives it, as case 9's arms do.
#
#     The values are deliberately unlike every other number a `verdict` line carries: the step is
#     5, not the attempt's 1, so a writer that read some other field into these keys is caught
#     rather than agreeing by coincidence. Each is written once, into a variable used both to
#     launch and to expect, so the expectation cannot drift off the launch.
ctx_issue=163
ctx_step=5
( export VERI_ISSUE="$ctx_issue" VERI_STEP="$ctx_step"
  verdict_run ctx green 'VERDICT: PASS
REASON: Target test and full suite are green.' )
ctx_field_issue="$(verdict_field ctx issue)"
ctx_field_step="$(verdict_field ctx step)"
{ [[ "$ctx_field_issue" == "$ctx_issue" ]] && [[ "$ctx_field_step" == "$ctx_step" ]]; } && ok \
  || no "VERI_ISSUE/VERI_STEP in verify.sh's environment reach its verdict event (issue=$ctx_field_issue want $ctx_issue, step=$ctx_field_step want $ctx_step)"

# 11 and 12 (issue #172) read off the same three verifications: what verify.sh DID about a
# verifier that left the repository changed, and what the repository looks like once it has,
# are two questions about one launch — so each arm is launched once and both cases assert on
# what it left behind.
#
# The verifier's sandbox is `--disallowedTools Write Edit MultiEdit NotebookEdit`
# (verify.sh:48-49): four editing TOOLS denied, and nothing said about Bash, through which a
# leaf can write any file. Nothing looked at the tree afterwards, and the conductor's next move
# after a PASS is `git add -A && git commit` (SKILL.md:526) — so whatever the verifier left was
# committed as the developer's work, and an edit made before the leaf ran the suite was judged
# along with the code it was judging. Detection alone is not enough either: the bail is what
# the conductor acts on, and the tree it leaves behind is the one a human then inspects and a
# resumed run continues from, so a step that bailed with the verifier's rewrite still in place
# has destroyed the developer's green code as surely as committing it would have.
#
# Three arms, one per way the repository can come back different, because the criteria name all
# three and each is invisible to a check written for only one of the others: a tracked file
# rewritten, an untracked non-ignored file created, and a commit that moves HEAD while leaving
# the working tree byte-identical to the one the developer produced. Putting each one back is a
# different move as well — a rewritten file's content has to be restored, a created file has to
# be removed, and a commit has to be undone WITHOUT taking the uncommitted work with it.
#
# Every arm's leaf renders PASS, the exit code that must not survive the mutation. A REJECT arm
# would exit 1 for its own reasons and could not tell a working check from an absent one.
#
# Each arm runs in a repo of its own under $work: one commit, and then the developer's
# uncommitted work on top of it — a tracked file edited and a new untracked file. That
# uncommitted half is the point of the fixture, because verify-green and verify-red run while
# the developer's work is still uncommitted; it is what makes `git checkout -- <file>` and `git
# reset --hard` wrong restores rather than merely blunt ones, since either one throws away the
# change the step exists to produce. The tracked arm's mutation rewrites that same edited file,
# so a restore from HEAD comes back with the committed content and is caught rather than looking
# right. Each repo also carries a .gitignore that ignores `.tdd/`, the rule
# ensure-run-state-ignored.sh installs in a real run: without it the supervisor's own prompt,
# log and event lines under `.tdd/` are untracked non-ignored files and every arm would report
# the run's own scratch as the verifier's tampering.
tamper_work="$work/tamper"

# The tampering leaf: it runs $FAKE_MUTATE in the repo before rendering its verdict, the way a
# verifier's Bash call does. The mutation's own output is dropped rather than printed, since
# run-leaf.sh captures this stub's stdout and parse-verdict.sh reads the verdict out of it.
cat > "$stubdir/claude-mutate" <<'STUB'
#!/bin/sh
eval "${FAKE_MUTATE:-}" >/dev/null 2>&1
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 0
STUB
chmod +x "$stubdir/claude-mutate"

# repo_state <dir> — everything case 12 says must come back unchanged, as one string: the sha
# HEAD names, then the path and content hash of every tracked and untracked non-ignored file,
# sorted. `ls-files -co --exclude-standard` is the same set the snapshot covers, so the run's
# own scratch under the fixture's gitignored `.tdd/` is outside both and no arm reads the
# supervisor's logs as a failure to restore. Content hashes rather than `status --porcelain`: a
# file put back with the wrong bytes is still unmodified-looking to status when the verifier's
# write matched what HEAD holds, which is exactly the bad restore the tracked arm is about.
repo_state() {
  printf 'HEAD %s\n' "$(git -C "$1" rev-parse HEAD)"
  ( cd "$1" && git ls-files -co --exclude-standard | LC_ALL=C sort \
      | while read -r f; do printf '%s %s\n' "$f" "$(git hash-object "$f")"; done )
}

# state_delta <before> <after> — the difference between two repo_state strings on one line, so
# a failing arm says which path came back wrong instead of printing two listings to compare by
# eye. Empty when they match, which is what case 12 asserts.
state_delta() {
  diff <(printf '%s\n' "$1") <(printf '%s\n' "$2") | tr '\n' ';'
}

# fixture_repo <dir> [<extra ignored path>…] — the repo every case that needs a real one starts
# from: one commit of src.txt as the developer committed it, with `.tdd/` ignored the way
# ensure-run-state-ignored.sh does it in a real run, plus whatever else the caller names.
#
# `git init <dir>` creates the directory and its leading ones, so the path is named once here and
# made by the same command that makes it a repo. The identity goes in the repo's own config: a
# repo made by `git init` under a test has none and git refuses to commit without one, and a case
# whose commit runs inside the leaf's stub is somewhere no helper of this suite reaches with a
# command line — one identity, set where every caller finds it.
fixture_repo() {
  local dir="$1" extra
  shift
  git init -q -b main "$dir" >/dev/null 2>&1
  git -C "$dir" config user.name veri
  git -C "$dir" config user.email veri@example.test
  printf 'the developer committed this\n' > "$dir/src.txt"
  printf '.tdd/\n' > "$dir/.gitignore"
  for extra in "$@"; do printf '%s\n' "$extra" >> "$dir/.gitignore"; done
  git -C "$dir" add -A >/dev/null 2>&1
  git -C "$dir" commit -q -m "initial" >/dev/null 2>&1
}

# tamper_run <arm> <mutation> — a fresh repo at $tamper_work/<arm> holding one commit and the
# developer's uncommitted work, then one PASS verification in it whose leaf runs <mutation>
# first. Sets $out and $code to verify.sh's stdout and exit status, and $delta to what
# repo_state says moved across the launch, so each assertion below reads whichever of the three
# it is about. The two states themselves stay local: no arm wants either one apart from their
# difference, and taking it here is what keeps the pairing of the before with the after from
# being respelled once per arm.
tamper_run() {
  local dir="$tamper_work/$1" before after
  fixture_repo "$dir"
  # The uncommitted half of the fixture, written after that commit so it is exactly what a
  # developer leaf would have left in the tree when the conductor called for verification.
  printf 'the developer is still editing this\n' > "$dir/src.txt"
  printf 'the developer has not committed this yet\n' > "$dir/new.txt"
  before="$(repo_state "$dir")"
  # The verification is verify_in's, with the mutating stub named as its claude and the
  # mutation put in that stub's environment — so this arm says what is particular to it and
  # nothing else, the spec and the test path and the test id included.
  out="$( FAKE_MUTATE="$2" verify_in "$dir" green 'VERDICT: PASS
REASON: Target test and full suite are green.' "$stubdir/claude-mutate" 2>/dev/null )"
  code=$?
  after="$(repo_state "$dir")"
  delta="$(state_delta "$before" "$after")"
}

tamper_run tracked 'printf "the verifier rewrote this\n" > src.txt'
tracked_code=$code tracked_out="$out" tracked_delta="$delta"
tamper_run untracked 'printf "the verifier left this behind\n" > leftover.txt'
untracked_code=$code untracked_out="$out" untracked_delta="$delta"
tamper_run head 'git commit -q -a -m "the verifier committed the developer'"'"'s work"'
head_code=$code head_out="$out" head_delta="$delta"

# 11. a verifier leaf that leaves the tree changed makes verify.sh exit 2 whatever its verdict,
#     with what changed on stdout.
{ [[ "$tracked_code" == 2 ]] && [[ "$tracked_out" == *src.txt* ]] \
  && [[ "$untracked_code" == 2 ]] && [[ "$untracked_out" == *leftover.txt* ]] \
  && [[ "$head_code" == 2 ]] && [[ "$head_out" == *HEAD* ]]; } && ok \
  || no "a verifier leaf that left the tree changed exits 2 naming what changed (tracked file: code=$tracked_code want 2, stdout='$tracked_out' want src.txt named; untracked file: code=$untracked_code want 2, stdout='$untracked_out' want leftover.txt named; moved HEAD: code=$head_code want 2, stdout='$head_out' want HEAD named)"

# 12. and after that exit 2 the repository is PUT BACK — the tree and HEAD exactly what they
#     were when the verifier launched, the developer's uncommitted work included.
{ [[ -z "$tracked_delta" ]] && [[ -z "$untracked_delta" ]] && [[ -z "$head_delta" ]]; } && ok \
  || no "after the exit 2 the tree and HEAD are back to what the verifier was handed, uncommitted work included (rewritten tracked file: delta='$tracked_delta' code=$tracked_code; created untracked file: delta='$untracked_delta' code=$untracked_code; verifier commit: delta='$head_delta' code=$head_code)"

# 13. a verifier that mutated a file and put it back before ending did not modify the
#     repository: the comparison is by CONTENT, so a tree that ends where it started carries the
#     verdict's own exit code out rather than the bail. That is what keeps verify-pin working —
#     verify-pin.md:17-22 tells the verifier to break the production code, run the test and
#     restore it, so the one phase whose whole method is a transient mutation must not be read as
#     a leaf that left the tree changed.
#
#     The arm is tamper_run's, so it is the same fixture the three tampering arms run in and the
#     only thing particular to it is a mutation that ends where it began. It rewrites src.txt —
#     the tracked file the developer is still editing, so the content restored is UNCOMMITTED and
#     a check comparing the tree against HEAD instead of against the snapshot would call this arm
#     changed. `git checkout -- src.txt`, the restore verify-pin.md actually spells, is for that
#     same reason not what the mutation uses: from HEAD it would throw the developer's edit away
#     and leave a genuinely different tree. The backup goes to mktemp's directory rather than
#     anywhere under the repo, since one left in the tree would be exactly the untracked file
#     case 11 bails on and this arm would then be green for the wrong reason.
tamper_run reverted 'b="$(mktemp)"; cp src.txt "$b"; printf "the verifier broke this\n" > src.txt; cp "$b" src.txt; rm -f "$b"'
{ [[ "$code" == 0 ]] && [[ "$out" == *'full suite are green'* ]]; } && ok \
  || no "a verifier that restored its own mutation gets its verdict's normal exit code (code=$code want 0, stdout='$out' want the verdict's reason)"

# 14. VERIFY_LEAF_ARGS changes the leaf's FLAGS, not what verify.sh accepts back (issue #172).
#     The variable exists so an environment that needs different permissions can say so
#     (verify.sh:28) — which means the one knob a caller has over the verifier's sandbox is also
#     the obvious place for the tree check to be switched off by accident, by a reading that
#     treats "the caller chose the leaf's permissions" as "the caller chose whether the tree is
#     checked". A leaf launched under caller-supplied flags that leaves the tree changed must
#     still bail exit 2 and still be put back, exactly as the three arms above do.
#
#     The arm is tamper_run's again, so the fixture — one commit, the developer's uncommitted
#     edit and untracked file, `.tdd/` ignored — is the tracked arm's and the only thing
#     particular to this one is the override in the launching environment. The prefix
#     assignments reach verify.sh because verify_in's `env` has no `-i`, and they are gone after
#     the call, so no case sees them.
#
#     The override is asserted to have REACHED the leaf rather than assumed: without that, an
#     implementation that ignored VERIFY_LEAF_ARGS entirely would satisfy this case while the
#     flags it names never applied, and the case would be about nothing. The evidence is the
#     leaf's own argv, which this arm's mutation writes out alongside its rewrite of src.txt —
#     `$@` inside the stub's `eval` is the stub's positional parameters, the argv run-leaf.sh
#     handed it. It is written OUTSIDE the repo, to a path named in the launching environment:
#     a dump under the fixture would be an untracked file the check bails on and the restore
#     then deletes, so the evidence would destroy itself. The flags chosen replace rather than
#     extend the default sandbox, so `--disallowedTools` present and `MultiEdit` absent is the
#     pair that says the default array was overridden and not merely echoed.
leafargs_out="$work/leafargs"
LEAFARGS_OUT="$leafargs_out" VERIFY_LEAF_ARGS='--permission-mode bypassPermissions --disallowedTools Write' \
  tamper_run leafargs 'printf "%s\n" "$@" > "$LEAFARGS_OUT"; printf "the verifier rewrote this\n" > src.txt'
leafargs_overridden=no
{ grep -qx -- '--disallowedTools' "$leafargs_out" && ! grep -qx -- 'MultiEdit' "$leafargs_out"; } \
  && leafargs_overridden=yes
{ [[ "$leafargs_overridden" == yes ]] && [[ "$code" == 2 ]] && [[ "$out" == *src.txt* ]] \
  && [[ -z "$delta" ]]; } && ok \
  || no "VERIFY_LEAF_ARGS overriding the leaf's flags does not switch the tree check off (override reached the leaf=$leafargs_overridden want yes; code=$code want 2; stdout='$out' want src.txt named; delta='$delta' want empty)"

# 15. VERIFY_LEAF_ARGS carrying its own `--model` alongside a role variable is refused, and the
#     refusal is the STATED rule the pair is resolved by (issue #171). Two things name a model
#     for the same leaf here: `VERI_MODEL_VERIFIER`, which supervise.sh resolves and run-leaf.sh
#     turns into `--model sonnet`, and the caller's own flags, which verify.sh passes through
#     verbatim. Both land on one `claude` command line, and which of the two the CLI honours is
#     flag order — a rule veri never chose and cannot see, so a run could report `model=sonnet`
#     in its `launch` mark while the leaf ran on the other one. That lie is the whole reason the
#     mark exists: #171's experiment joins verdicts and cost on that field.
#
#     So the pair is not ranked, it is refused: exit 2 — the plumbing speaking, no answer could
#     be obtained — with a diagnostic, and NO leaf launched, since a leaf paid for is the cost
#     the refusal exists to save. The assertion is that no `claude` ran at all, not merely that
#     the exit is 2: an implementation that launched the leaf and then rejected its verdict
#     would satisfy an exit-code-only case while still paying for the run it must not make.
#     Both streams are captured, so the diagnostic counts wherever the refusal writes it.
#
#     verify_in's, run in its OWN directory under $work, because the evidence is the ABSENCE of
#     the stub's argv dump and the shared $work/argv is written by every case above. The two
#     prefix assignments reach verify.sh the way case 14's do — verify_in's `env` has no `-i` —
#     and are gone after the call, so no case sees them.
model_clash_dir="$work/model-clash"
mkdir -p "$model_clash_dir"
model_clash_argv="$model_clash_dir/argv"
model_clash_out="$( VERI_MODEL_VERIFIER=sonnet \
    VERIFY_LEAF_ARGS='--permission-mode bypassPermissions --model opus' \
    verify_in "$model_clash_dir" red 'VERDICT: PASS
REASON: Target test and full suite are green.' 2>&1 )"
model_clash_code=$?
model_clash_launched=no
[[ -e "$model_clash_argv" ]] && model_clash_launched=yes
{ [[ "$model_clash_code" == 2 ]] && [[ "$model_clash_launched" == no ]] \
  && [[ "$model_clash_out" == *VERIFY_LEAF_ARGS* ]] && [[ "$model_clash_out" == *--model* ]]; } && ok \
  || no "VERIFY_LEAF_ARGS carrying its own --model alongside a role model variable is refused before any leaf launches (code=$model_clash_code want 2; leaf launched=$model_clash_launched want no; output='$model_clash_out' want VERIFY_LEAF_ARGS and --model named)"

# 16. a verifier leaf re-invoked after it answered (issue #228) writes a later result record with
#     no verdict in it — the stream below is #108's step-1 log in shape: a turn that ended waiting
#     on a background suite, the turn that rendered the verdict, and a task-notification turn that
#     said there was nothing left to do. The verdict in the middle record is the answer.
verify '{"type":"system","subtype":"init","session_id":"s"}
{"type":"result","subtype":"success","is_error":false,"num_turns":16,"result":"Waiting for the `make test` background task and its Monitor to report completion — will post the verdict once it finishes."}
{"type":"result","subtype":"success","is_error":false,"num_turns":2,"result":"VERDICT: PASS\nREASON: Target test and full suite are green."}
{"type":"result","subtype":"success","is_error":false,"num_turns":1,"duration_ms":1500,"duration_api_ms":1400,"total_cost_usd":0.01,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},"origin":{"kind":"task-notification"},"result":"No action needed — verdict already delivered for this verification."}' green
{ [[ "$code" == 0 ]] && [[ "$out" == 'Target test and full suite are green.' ]]; } && ok \
  || no "a verdict in an earlier result record is read when the last result record carries none (code=$code want 0; output='$out' want 'Target test and full suite are green.')"

# 17. the same re-invoked shape with no verdict in ANY result record (issue #228) is still a
#     verification nobody answered: exit 2, no reason, and parse-verdict's own diagnostic — the
#     search for an earlier verdict must not turn an unanswered log into an answer.
out="$(verify_in "$work" green '{"type":"system","subtype":"init","session_id":"s"}
{"type":"result","subtype":"success","is_error":false,"num_turns":16,"result":"Waiting for the `make test` background task and its Monitor to report completion — will post the verdict once it finishes."}
{"type":"result","subtype":"success","is_error":false,"num_turns":1,"duration_ms":1500,"duration_api_ms":1400,"total_cost_usd":0.01,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},"origin":{"kind":"task-notification"},"result":"No action needed — verdict already delivered for this verification."}' 2>"$work/err17")"
code=$?
err17="$(cat "$work/err17")"
{ [[ "$code" == 2 ]] && [[ -z "$out" ]] && [[ "$err17" == *'parse-verdict: no VERDICT: line found'* ]]; } && ok \
  || no "a log with no VERDICT: line in any result record still exits 2 with the same diagnostic (code=$code want 2; output='$out' want empty; stderr='$err17' want 'parse-verdict: no VERDICT: line found')"

# 18. more than one result record carries a verdict (issue #228) — a REJECT answered, the leaf was
#     re-invoked and answered again with PASS, then a task-notification turn said nothing was left.
#     The newest verdict is the answer, not the first one found.
verify '{"type":"system","subtype":"init","session_id":"s"}
{"type":"result","subtype":"success","is_error":false,"num_turns":4,"result":"VERDICT: REJECT\nREASON: Missing edge case."}
{"type":"result","subtype":"success","is_error":false,"num_turns":2,"result":"VERDICT: PASS\nREASON: Revised: target and full suite green."}
{"type":"result","subtype":"success","is_error":false,"num_turns":1,"duration_ms":1500,"duration_api_ms":1400,"total_cost_usd":0.01,"usage":{"input_tokens":1,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},"origin":{"kind":"task-notification"},"result":"No action needed — verdict already delivered for this verification."}' green
{ [[ "$code" == 0 ]] && [[ "$out" == 'Revised: target and full suite green.' ]]; } && ok \
  || no "the newest VERDICT: wins when more than one result record carries one (code=$code want 0; output='$out' want 'Revised: target and full suite green.')"

# 19. a verifier leaf that exited cleanly — not killed — with no VERDICT: line is relaunched, and
#     the relaunched attempt's verdict is the answer (issue #219). #212's step 1 bailed on exactly
#     this: the leaf backgrounded `make test`, ended its turn to wait, and printed no verdict. The
#     stub counts its launches in its own directory and prints a PASS only on the launch
#     VERDICT_ON_LAUNCH names (never, when unset) and no verdict on every other, so the case reads
#     both the verdict returned and that it took two launches.
cat > "$stubdir/claude-counting" <<'STUB'
#!/bin/sh
n=$(( $(cat "$LAUNCH_COUNT" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$LAUNCH_COUNT"
if [ "$n" -eq "${VERDICT_ON_LAUNCH:-0}" ]; then
  printf '%s' 'VERDICT: PASS
REASON: Target test and full suite are green.'
else
  printf '%s' 'Waiting for the background `make test` run to complete before rendering a verdict.'
fi
exit 0
STUB
chmod +x "$stubdir/claude-counting"
no_verdict_dir="$work/no-verdict-relaunch"
mkdir -p "$no_verdict_dir"
no_verdict_out="$( LAUNCH_COUNT="$no_verdict_dir/launches" VERDICT_ON_LAUNCH=2 \
    verify_in "$no_verdict_dir" green '' "$stubdir/claude-counting" 2>/dev/null )"
no_verdict_code=$?
no_verdict_launches="$(cat "$no_verdict_dir/launches" 2>/dev/null || echo 0)"
{ [[ "$no_verdict_code" == 0 ]] && [[ "$no_verdict_launches" == 2 ]] \
  && [[ "$no_verdict_out" == *'full suite are green'* ]]; } && ok \
  || no "a verifier leaf that exited cleanly with no VERDICT: line is relaunched and its second verdict returned (code=$no_verdict_code want 0; launches=$no_verdict_launches want 2; output='$no_verdict_out' want the PASS reason)"

# 20. no-verdict relaunches stop after VERI_NO_VERDICT_RETRIES (default 1), issue #219: a leaf that
#     never prints a verdict is exit 2 after exactly 1 + VERI_NO_VERDICT_RETRIES launches. Read at
#     the default (the variable unset, not inherited from the caller), at 0 (one launch, no
#     relaunch) and at 2, so a budget hardcoded to the default cannot pass for the knob.
never_verdict() {  # never_verdict <label> [<retries>] -> prints "<code> <launches>"
  local dir="$work/never-verdict-$1"
  mkdir -p "$dir"
  ( if [[ $# -ge 2 ]]; then export VERI_NO_VERDICT_RETRIES="$2"; else unset VERI_NO_VERDICT_RETRIES; fi
    LAUNCH_COUNT="$dir/launches" verify_in "$dir" green '' "$stubdir/claude-counting" >/dev/null 2>&1
    echo "$? $(cat "$dir/launches" 2>/dev/null || echo 0)" )
}
budget_default="$(never_verdict default)"
budget_zero="$(never_verdict zero 0)"
budget_two="$(never_verdict two 2)"
{ [[ "$budget_default" == '2 2' ]] && [[ "$budget_zero" == '2 1' ]] && [[ "$budget_two" == '2 3' ]]; } && ok \
  || no "no-verdict relaunches stop after VERI_NO_VERDICT_RETRIES (default 1): exit 2 after 1 + retries launches (code launches — default: '$budget_default' want '2 2'; =0: '$budget_zero' want '2 1'; =2: '$budget_two' want '2 3')"

# 21. a non-integer VERI_NO_VERDICT_RETRIES is refused before any leaf is paid for, issue #219:
#     exit 2 (no answer could be obtained — bad configuration) with zero launches.
budget_bad="$(never_verdict bad many)"
[[ "$budget_bad" == '2 0' ]] && ok \
  || no "a non-integer VERI_NO_VERDICT_RETRIES makes verify.sh exit 2 without launching any verifier leaf (code launches: '$budget_bad' want '2 0')"

# 22. a verifier killed by supervise.sh is not relaunched by verify.sh, issue #219: supervise.sh
#     already spent its own VERI_STUCK_RETRIES relaunches, so a no-verdict budget on top would be a
#     second liveness layer. The stub counts its launches and then hangs; with VERI_STUCK_RETRIES=1
#     supervise.sh makes two attempts, and a VERI_NO_VERDICT_RETRIES of 3 must add none to them.
cat > "$stubdir/claude-counting-hang" <<'STUB'
#!/bin/sh
echo $(( $(cat "$LAUNCH_COUNT" 2>/dev/null || echo 0) + 1 )) > "$LAUNCH_COUNT"
echo "thinking..."; clock-jump "$(( ${VERI_HEARTBEAT:-999} + 1 ))"; sleep 60
STUB
chmod +x "$stubdir/claude-counting-hang"
killed_dir="$work/killed-no-relaunch"
mkdir -p "$killed_dir"
( cd "$killed_dir" && env CLAUDE_BIN="$stubdir/claude-counting-hang" LAUNCH_COUNT="$killed_dir/launches" \
    VERI_STUCK_RETRIES=1 VERI_NO_VERDICT_RETRIES=3 VERI_HEARTBEAT=1 VERI_POLL=0.02 \
    "$VERIFY" red "$work/spec.md" tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
killed_code=$?
killed_launches="$(cat "$killed_dir/launches" 2>/dev/null || echo 0)"
{ [[ "$killed_code" == 2 ]] && [[ "$killed_launches" == 2 ]]; } && ok \
  || no "a verifier killed by supervise.sh is not relaunched by verify.sh, whatever VERI_NO_VERDICT_RETRIES is (code=$killed_code want 2; launches=$killed_launches want 2 — supervise.sh's own attempts only)"

# 23. the two relaunch budgets are separate knobs, issue #219: VERI_STUCK_RETRIES does not change
#     how many times a clean exit with no verdict is relaunched, and VERI_NO_VERDICT_RETRIES does
#     not change how many attempts supervise.sh makes on a hung leaf. Each half sets the OTHER
#     knob high and pins the count its own knob — at its default, or at 0 — decides.
axes_dir="$work/budget-axes"
mkdir -p "$axes_dir/no-verdict" "$axes_dir/stuck"
( cd "$axes_dir/no-verdict" && unset VERI_NO_VERDICT_RETRIES \
  && env CLAUDE_BIN="$stubdir/claude-counting" LAUNCH_COUNT="$axes_dir/no-verdict/launches" ARGV_OUT="$axes_dir/argv" \
      VERI_STUCK_RETRIES=3 "$VERIFY" --fast-cmd "make unit" green "$work/spec.md" tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
axes_no_verdict="$? $(cat "$axes_dir/no-verdict/launches" 2>/dev/null || echo 0)"
( cd "$axes_dir/stuck" && env CLAUDE_BIN="$stubdir/claude-counting-hang" LAUNCH_COUNT="$axes_dir/stuck/launches" \
    VERI_STUCK_RETRIES=0 VERI_NO_VERDICT_RETRIES=3 VERI_HEARTBEAT=1 VERI_POLL=0.02 \
    "$VERIFY" red "$work/spec.md" tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
axes_stuck="$? $(cat "$axes_dir/stuck/launches" 2>/dev/null || echo 0)"
{ [[ "$axes_no_verdict" == '2 2' ]] && [[ "$axes_stuck" == '2 1' ]]; } && ok \
  || no "VERI_STUCK_RETRIES does not change the no-verdict relaunch count and VERI_NO_VERDICT_RETRIES does not change supervise.sh's stuck retry count (code launches — never-verdict leaf, VERI_STUCK_RETRIES=3: '$axes_no_verdict' want '2 2'; hung leaf, VERI_STUCK_RETRIES=0 VERI_NO_VERDICT_RETRIES=3: '$axes_stuck' want '2 1')"

# 24. a clean exit with no VERDICT: line is recorded in the event log under a cause of its own,
#     issue #219: on each relaunch and on the final exit 2, a line carrying a `cause` — and that
#     cause is none of the ones a verifier killed before rendering a verdict is recorded under. A
#     run log showing only the exit code cannot tell the two apart; the cause is what does. The
#     never-verdict leaf at the default budget makes one relaunch and one final exit 2, so its log
#     must hold exactly two lines with a non-empty `cause`, both the same. supervise.sh writes
#     `cause=` only for a kill, so on this clean-exiting leaf it contributes none of the two. The
#     killed half is a hung leaf with no retries, whose causes are whatever supervise.sh wrote.
causes_in() {  # causes_in <dir> -> every non-empty `cause` in <dir>'s event log, one per line
  python3 -c '
import sys, json
for line in open(sys.argv[1]).read().splitlines():
    try:
        obj = json.loads(line)
    except Exception:
        continue
    if isinstance(obj, dict) and obj.get("cause"):
        print(obj["cause"])
' "$1/.tdd/events.jsonl" 2>/dev/null
}
cause_dir="$work/no-verdict-cause"
mkdir -p "$cause_dir/no-verdict" "$cause_dir/killed"
( cd "$cause_dir/no-verdict" && unset VERI_NO_VERDICT_RETRIES \
  && env CLAUDE_BIN="$stubdir/claude-counting" LAUNCH_COUNT="$cause_dir/no-verdict/launches" ARGV_OUT="$cause_dir/argv" \
      "$VERIFY" --fast-cmd "make unit" green "$work/spec.md" tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
( cd "$cause_dir/killed" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_STUCK_RETRIES=0 \
    VERI_HEARTBEAT=1 VERI_POLL=0.02 "$VERIFY" red "$work/spec.md" tests/test_slugify.py test_lowercases >/dev/null 2>&1 )
no_verdict_causes="$(causes_in "$cause_dir/no-verdict")"
killed_causes="$(causes_in "$cause_dir/killed")"
no_verdict_cause_count="$(printf '%s' "$no_verdict_causes" | grep -c '^' || true)"
no_verdict_distinct="$(printf '%s\n' "$no_verdict_causes" | sort -u)"
{ [[ "$no_verdict_cause_count" -eq 2 ]] && [[ "$(printf '%s\n' "$no_verdict_distinct" | grep -c '^')" -eq 1 ]] \
  && [[ -n "$killed_causes" ]] && ! printf '%s\n' "$killed_causes" | grep -qxF "$no_verdict_distinct"; } && ok \
  || no "a clean exit with no VERDICT: line is logged under a cause distinct from a killed verifier's, on the relaunch and on the final exit 2 (no-verdict causes: $no_verdict_cause_count lines '${no_verdict_causes//$'\n'/|}' want 2 lines of one cause; killed causes: '${killed_causes//$'\n'/|}' must be non-empty and not contain it)"

# 25. a relaunch leaves the blind-verifier guarantee where it was, issue #219: the relaunched
#     leaf's prompt is byte-identical to the first attempt's, and both are exactly what
#     build-verify-prompt.sh prints for the four arguments it already takes — so nothing the
#     failed attempt said, and no new parameter, reached the second one. The stub records the
#     prompt each launch was handed (the argument after `-p`), one file per launch.
cat > "$stubdir/claude-prompt-recording" <<'STUB'
#!/bin/sh
n=$(( $(cat "$LAUNCH_COUNT" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$LAUNCH_COUNT"
printf '%s' "$2" > "$PROMPT_DIR/prompt.$n"
printf '%s' 'Waiting for the background `make test` run to complete before rendering a verdict.'
exit 0
STUB
chmod +x "$stubdir/claude-prompt-recording"
prompt_dir="$work/no-verdict-prompt"
mkdir -p "$prompt_dir"
( unset VERI_NO_VERDICT_RETRIES
  LAUNCH_COUNT="$prompt_dir/launches" PROMPT_DIR="$prompt_dir" \
    verify_in "$prompt_dir" green '' "$stubdir/claude-prompt-recording" >/dev/null 2>&1 )
printf '%s' "$("$HERE/../build-verify-prompt.sh" --fast-cmd "make unit" green "$work/spec.md" tests/test_slugify.py test_lowercases)" \
  > "$prompt_dir/expected"
prompt_launches="$(cat "$prompt_dir/launches" 2>/dev/null || echo 0)"
{ [[ "$prompt_launches" == 2 ]] && cmp -s "$prompt_dir/prompt.1" "$prompt_dir/prompt.2" \
  && cmp -s "$prompt_dir/expected" "$prompt_dir/prompt.1"; } && ok \
  || no "a relaunched verifier's prompt is byte-identical to the first attempt's and to build-verify-prompt.sh's four-argument output (launches=$prompt_launches want 2; diff first→relaunch: $(diff "$prompt_dir/prompt.1" "$prompt_dir/prompt.2" 2>&1 | head -5 | tr '\n' '|'); diff builder→first: $(diff "$prompt_dir/expected" "$prompt_dir/prompt.1" 2>&1 | head -5 | tr '\n' '|'))"

# verify.sh refactor passes the base sha through to the verifier prompt (#151). The sha is the
# 4th positional, and what reaches the leaf is read off the stub's recorded argv — the prompt the
# verifier was actually handed — rather than off the builder, so a verify.sh that dropped or
# replaced the argument on its way to build-verify-prompt.sh is what fails here.
sha_dir="$(mktemp -d)"
verify_in "$sha_dir" refactor 'VERDICT: PASS
REASON: behaviour preserved.' >/dev/null 2>"$sha_dir/err"
sha_code=$?
{ [[ "$sha_code" == 0 ]] && grep -qF 'git diff 0123abc..HEAD' "$sha_dir/argv" 2>/dev/null; } && ok \
  || no "verify.sh refactor passes the base sha through to the verifier prompt (code=$sha_code; prompt lines naming a sha: $(grep -o 'git diff [^ ]*' "$sha_dir/argv" 2>/dev/null | head -1); stderr: $(head -1 "$sha_dir/err"))"
rm -rf "$sha_dir"

# verify.sh --step '<STEP>' hands the step to the verifier prompt, and only the flag does (#223).
# The flag comes before the positionals; an ambient VERI_STEP naming a different step is exported
# alongside it, and what reaches the leaf is read off the stub's recorded argv — so a verify.sh that
# dropped the flag, or scoped the verdict by reading the environment, is what fails here.
step_dir="$(mktemp -d)"
( export VERI_STEP='AMBIENT-STEP-must-not-appear'
  verify_in "$step_dir" green 'VERDICT: PASS
REASON: ok' '' 'FLAG-STEP slugify joins words with hyphens' >/dev/null 2>"$step_dir/err" )
step_code=$?
step_seen="$(grep -c 'FLAG-STEP slugify joins words with hyphens' "$step_dir/argv" 2>/dev/null)"
ambient_seen="$(grep -c 'AMBIENT-STEP-must-not-appear' "$step_dir/argv" 2>/dev/null)"
{ [[ "$step_code" == 0 ]] && [[ "${step_seen:-0}" -ge 1 ]] && [[ "${ambient_seen:-0}" -eq 0 ]]; } && ok \
  || no "verify.sh --step '<STEP>' reaches the verifier prompt and ambient VERI_STEP does not (code=$step_code; step in prompt: ${step_seen:-0}; ambient in prompt: ${ambient_seen:-0}; stderr: $(head -1 "$step_dir/err"))"
rm -rf "$step_dir"

# An existing run resumes unchanged: a conductor that passes no `--step` still gets a valid
# verifier prompt (#223). The flag is optional, and the run that most needs it to be is the one
# resumed from a ledger written before it existed — its conductor spells the four positionals and
# nothing else. What must then not happen is the template's `{{STEP}}` reaching the leaf as
# literal text where a heading belongs: an unfilled placeholder is what an edit that fills the
# slot only on the flagged path leaves behind, and the verifier would read it as part of the
# issue. Probed for all four phases off the stub's recorded argv — the prompt the leaf was
# actually handed — so both scripts on the path are asked at once: verify.sh built the call and
# build-verify-prompt.sh rendered it.
#
# `valid` is three claims, each its own miss, for the reason build-verify-prompt.test.sh case 12
# gives: a phase whose template kept the placeholder is named rather than covered for by its
# siblings. The exit status says a prompt was built at all, the placeholder probe is the
# criterion's own words, and the spec-plus-`VERDICT:` pair is what keeps an empty prompt from
# satisfying the placeholder probe by having nothing in it — grep matches no `{{…}}` in an empty
# file just as readily as in a fully substituted one.
problems=""
for phase in red green refactor pin; do
  nostep_dir="$work/nostep-$phase"
  mkdir -p "$nostep_dir"
  verify_in "$nostep_dir" "$phase" 'VERDICT: PASS
REASON: ok' >/dev/null 2>"$nostep_dir/err"
  nostep_code=$?
  [[ "$nostep_code" == 0 ]] \
    || problems="$problems; verify-$phase exits $nostep_code ($(head -1 "$nostep_dir/err"))"
  unfilled="$(grep -o '{{[A-Z_]*}}' "$nostep_dir/argv" 2>/dev/null | sort -u | tr '\n' ' ')"
  [[ -z "$unfilled" ]] || problems="$problems; verify-$phase leaves ${unfilled% } unfilled"
  { grep -q 'slugify must lowercase' "$nostep_dir/argv" 2>/dev/null \
    && grep -q 'VERDICT:' "$nostep_dir/argv" 2>/dev/null; } \
    || problems="$problems; verify-$phase carries no spec or no VERDICT: contract"
done
[[ -z "$problems" ]] && ok \
  || no "with no --step every phase still builds a valid verifier prompt with no unfilled step placeholder (${problems#; })"

# 26. a verifier leaf that changed the operator's global git config exits 2 naming the file,
#     whatever its verdict (issue #276). The repository check of case 11 cannot see it: the file
#     lives under $HOME, outside the tree. #258's verify-refactor leaf set `http.proxy` in
#     ~/.gitconfig and its cleanup trap never fired, breaking every network git operation on the
#     machine. run-leaf.sh hands the leaf a private GIT_CONFIG_GLOBAL, so a `git config --global`
#     no longer reaches the operator's file — which is why the mutation here writes it by path,
#     `git config --file`, the one route a leaf still has to it.
#
#     The arm is tamper_run's, so the tree is left untouched and the only thing that moved is the
#     operator's file. HOME is a fixture directory holding that file, passed through verify_in's
#     `env` like the prefix assignments of cases 14 and 15, so no real ~/.gitconfig is read or
#     written.
gitconfig_home="$work/operator-home"
mkdir -p "$gitconfig_home"
printf '[credential]\n\thelper = store\n' > "$gitconfig_home/.gitconfig"
HOME="$gitconfig_home" \
  tamper_run gitconfig 'git config --file "$HOME/.gitconfig" http.proxy http://127.0.0.1:1'
{ [[ "$code" == 2 ]] && [[ "$out" == *.gitconfig* ]]; } && ok \
  || no "a verifier leaf that changed the operator's global git config exits 2 naming the file (code=$code want 2; stdout='$out' want .gitconfig named)"

# 27. a REJECT verdict makes the verification preserve that attempt, and what it preserves pairs
#     with the verdict event (issue #409). A rejected tree is never committed to the work branch —
#     a green commit lands only after verify-green PASSes — so the side ref under
#     refs/veri/attempts/ is the only place the rejected file ever exists once the next step
#     overwrites `.tdd/verify-green.log`. verify.sh is the script that holds the verdict, so it is
#     the one that can know a verification is worth preserving.
#
#     "Pairs with the verdict event" is asserted as such rather than against hardcoded names: the
#     issue, step, phase and attempt are READ OFF the `verdict` line this verification wrote, and
#     the ref and the preserved copy are looked for under exactly those four values. A reader who
#     has the event in front of them gets to the preserved material by substitution, which is the
#     whole of the claim. The two launched values are also asserted for what they are, because an
#     event whose fields came back empty would otherwise let a path built out of them agree with
#     a preservation that recorded nothing.
#
#     The mark that ends the preserved name is deliberately not pinned here — criterion 3's own
#     case in preserve-attempt.test.sh covers the naming, and this case is about the pairing — so
#     the copy is matched by the step-phase-attempt prefix and identified by its contents being
#     the leaf's log byte for byte.
#
#     The fixture is a repo, since the subject is a real ref: one commit, then the rejected work
#     uncommitted on top of it, the shape verify-green is called in. Its .gitignore covers `.tdd/`
#     — the rule ensure-run-state-ignored.sh installs in a real run — and `argv`, which the stub
#     writes during the leaf's own run: without that second line the recorded argv is an untracked
#     file appearing mid-verification, and case 11's tamper check would exit 2 before any verdict.
pres_dir="$work/preserve-reject"
fixture_repo "$pres_dir" argv
printf 'the work the verifier rejected\n' > "$pres_dir/src.txt"
pres_issue=409
pres_step=4
( export VERI_ISSUE="$pres_issue" VERI_STEP="$pres_step"
  verify_in "$pres_dir" green 'VERDICT: REJECT
REASON: the helper it asserts on is still private.' >/dev/null 2>&1 )
pres_code=$?

event_issue="$(verdict_field_in "$pres_dir" issue)"
event_step="$(verdict_field_in "$pres_dir" step)"
event_phase="$(verdict_field_in "$pres_dir" phase)"
event_attempt="$(verdict_field_in "$pres_dir" attempt)"
pres_ref="refs/veri/attempts/$event_issue/$event_step/verify-$event_phase-$event_attempt"
git -C "$pres_dir" rev-parse --verify --quiet "$pres_ref^{commit}" >/dev/null 2>&1; pres_resolved=$?
pres_shown="$(git -C "$pres_dir" show "$pres_ref:src.txt" 2>&1)"
# The preserved copy, found by the prefix the event's own fields build. `ls` rather than a glob
# into an array: an unmatched glob comes back as the pattern itself, which reads as a found file.
pres_copy="$(ls "$pres_dir/.tdd/attempts/$event_step-verify-$event_phase-$event_attempt-"*.log 2>/dev/null | head -1)"
pres_paired="$(if [[ -n "$pres_copy" ]] && cmp -s "$pres_copy" "$pres_dir/.tdd/verify-green.log"; then echo yes; else echo no; fi)"
{ [[ "$pres_code" == 1 ]] \
  && [[ "$event_issue" == "$pres_issue" ]] && [[ "$event_step" == "$pres_step" ]] \
  && [[ "$pres_resolved" == 0 ]] \
  && [[ "$pres_shown" == "the work the verifier rejected" ]] \
  && [[ "$pres_paired" == yes ]]; } && ok \
  || no "a REJECT preserves the attempt under the ref and the copy name its own verdict event pairs with (code=$pres_code want 1; event issue=$event_issue step=$event_step phase=$event_phase attempt=$event_attempt; ref=$pres_ref resolved=$pres_resolved; git show said '$pres_shown'; log copy='${pres_copy:-<none>}' matches .tdd/verify-green.log: $pres_paired)"


# 28. the no-verdict half of the same criterion (issue #409): a verifier leaf that exits cleanly
#     and prints no VERDICT: line renders a malformed verdict, and that is a troubled step as
#     surely as a REJECT is — the tree it judged is still uncommitted and `.tdd/verify-green.log`
#     is still the only record of what it tried. So this attempt is preserved too, under its own
#     ref and its own copies. Case 27's arm cannot answer for this one: it reaches preservation
#     through a parsed REJECT, where this one reaches it with no verdict parsed at all.
#
#     "Its own" is what the mark says, so the mark is read here rather than left to
#     preserve-attempt.test.sh the way case 27 leaves it: a run that ended with no VERDICT: line
#     is filed under `no-verdict`, not under the `malformed` a garbled line gets, and the copy is
#     looked for under the very cause the verdict event carries — the same pairing-by-substitution
#     case 27 makes for the issue, step, phase and attempt.
#
#     VERI_NO_VERDICT_RETRIES=0 is pinned rather than inherited (see hermetic-suites.test.sh) and
#     spends one launch rather than the default's two: the relaunch axis is case 24's subject, and
#     this case is about what the verification preserves once it is out of retries.
nv_dir="$work/preserve-no-verdict"
fixture_repo "$nv_dir" argv
printf 'the work no verdict was rendered on\n' > "$nv_dir/src.txt"
nv_issue=409
nv_step=5
( export VERI_ISSUE="$nv_issue" VERI_STEP="$nv_step" VERI_NO_VERDICT_RETRIES=0
  verify_in "$nv_dir" green 'the leaf rambled and never rendered a verdict' >/dev/null 2>&1 )
nv_code=$?

nv_issue_seen="$(verdict_field_in "$nv_dir" issue)"
nv_step_seen="$(verdict_field_in "$nv_dir" step)"
nv_phase="$(verdict_field_in "$nv_dir" phase)"
nv_attempt="$(verdict_field_in "$nv_dir" attempt)"
nv_cause="$(verdict_field_in "$nv_dir" cause)"
nv_ref="refs/veri/attempts/$nv_issue_seen/$nv_step_seen/verify-$nv_phase-$nv_attempt"
git -C "$nv_dir" rev-parse --verify --quiet "$nv_ref^{commit}" >/dev/null 2>&1; nv_resolved=$?
nv_shown="$(git -C "$nv_dir" show "$nv_ref:src.txt" 2>&1)"
nv_copy="$nv_dir/.tdd/attempts/$nv_step_seen-verify-$nv_phase-$nv_attempt-$nv_cause.log"
nv_paired="$(if [[ -f "$nv_copy" ]] && cmp -s "$nv_copy" "$nv_dir/.tdd/verify-green.log"; then echo yes; else echo no; fi)"
{ [[ "$nv_code" == 2 ]] \
  && [[ "$nv_issue_seen" == "$nv_issue" ]] && [[ "$nv_step_seen" == "$nv_step" ]] \
  && [[ "$nv_cause" == no-verdict ]] \
  && [[ "$nv_resolved" == 0 ]] \
  && [[ "$nv_shown" == "the work no verdict was rendered on" ]] \
  && [[ "$nv_paired" == yes ]]; } && ok \
  || no "a malformed verdict with no VERDICT: line preserves the attempt under its own ref and copies (code=$nv_code want 2; event issue=$nv_issue_seen step=$nv_step_seen phase=$nv_phase attempt=$nv_attempt cause=$nv_cause want no-verdict; ref=$nv_ref resolved=$nv_resolved; git show said '$nv_shown'; log copy='$nv_copy' matches .tdd/verify-green.log: $nv_paired)"


# 29. the other side of the same criterion (issue #409): a step that recorded none of the marks
#     writes no ref and no preserved copy, so an untroubled run costs what it costs today. Cases
#     27 and 28 pin what a troubled verification keeps; nothing there says the keeping is
#     CONDITIONAL, and a preservation that fired on every verification would put a commit and two
#     copies on disk for every step of every green run — the "not a request to keep every log of
#     every run" the issue rules out.
#
#     Both halves of the criterion are exercised by one verification each, because one
#     verification drives both scripts that preserve: verify.sh decides on the verdict, and the
#     supervise.sh it launches the leaf through decides on the leaf's status. So the `pass` arm is
#     a PASS verdict whose leaf exited success, and the `failure` arm a leaf that exited a clean
#     failure — the status supervise.sh calls `failure` rather than `killed-stuck` — carrying the
#     same PASS text, so the two arms differ in exactly the thing under test and nothing else.
#     A third arm for a REJECT-with-failing-leaf would say nothing: cases 27 and 28 already have
#     the verdict half, and this one is about the status.
#
#     Each arm gets its own repository, so `verdict_field_in`'s one-verdict-line probe still reads
#     its own verification, and each is asked the same question: how much is under
#     refs/veri/attempts/ and how much under .tdd/attempts/. Zero and zero, not "the ref this
#     arm would have been filed under is missing" — the claim is that nothing was written at all,
#     under any name.
#
#     The verdict event is read back in both arms as the positive control: a verification that
#     died before it ever reached the preservation branch would leave the same empty ref space,
#     so what says the branch was reached and declined is that a PASS verdict was recorded with
#     this run's own issue and step in it. The `failure` arm's leaf rc is read off
#     `.tdd/verify-green.rc` for the same reason — it is what says the leaf really did exit 1
#     rather than 0, which is the only thing that arm adds.
cat > "$stubdir/claude-clean-failure" <<'STUB'
#!/bin/sh
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 1
STUB
chmod +x "$stubdir/claude-clean-failure"

# preserved_trace <dir> — everything preservation would have left in <dir>, as one line: the
# number of refs under refs/veri/attempts/ and the number of files under .tdd/attempts/. Counted
# rather than named, because the claim is about nothing existing under any name. `grep -c .`
# rather than `wc -l`, which answers 1 for the single empty line an empty listing prints.
preserved_trace() {
  local refs copies
  refs="$(git -C "$1" for-each-ref --format='%(refname)' 'refs/veri/attempts/' 2>/dev/null | grep -c . || true)"
  copies="$(ls -1 "$1/.tdd/attempts" 2>/dev/null | grep -c . || true)"
  echo "refs=$refs copies=$copies"
}

untroubled_verdict='VERDICT: PASS
REASON: the test pins the behaviour and the suite is green.'
quiet_issue=409
quiet_step=7

quiet_pass_dir="$work/preserve-none-pass"
fixture_repo "$quiet_pass_dir" argv
printf 'the work the verifier accepted\n' > "$quiet_pass_dir/src.txt"
( export VERI_ISSUE="$quiet_issue" VERI_STEP="$quiet_step"
  verify_in "$quiet_pass_dir" green "$untroubled_verdict" >/dev/null 2>&1 )
quiet_pass_code=$?

quiet_fail_dir="$work/preserve-none-failure"
fixture_repo "$quiet_fail_dir" argv
printf 'the work the verifier accepted\n' > "$quiet_fail_dir/src.txt"
( export VERI_ISSUE="$quiet_issue" VERI_STEP="$quiet_step"
  verify_in "$quiet_fail_dir" green "$untroubled_verdict" "$stubdir/claude-clean-failure" >/dev/null 2>&1 )
quiet_fail_code=$?

quiet_pass_trace="$(preserved_trace "$quiet_pass_dir")"
quiet_fail_trace="$(preserved_trace "$quiet_fail_dir")"
quiet_pass_word="$(verdict_field_in "$quiet_pass_dir" verdict)"
quiet_fail_word="$(verdict_field_in "$quiet_fail_dir" verdict)"
quiet_pass_issue="$(verdict_field_in "$quiet_pass_dir" issue)"
quiet_fail_issue="$(verdict_field_in "$quiet_fail_dir" issue)"
quiet_leaf_rc="$(cat "$quiet_fail_dir/.tdd/verify-green.rc" 2>/dev/null)"
{ [[ "$quiet_pass_code" == 0 ]] && [[ "$quiet_fail_code" == 0 ]] \
  && [[ "$quiet_pass_word" == PASS ]] && [[ "$quiet_fail_word" == PASS ]] \
  && [[ "$quiet_pass_issue" == "$quiet_issue" ]] && [[ "$quiet_fail_issue" == "$quiet_issue" ]] \
  && [[ "$quiet_leaf_rc" == 1 ]] \
  && [[ "$quiet_pass_trace" == "refs=0 copies=0" ]] \
  && [[ "$quiet_fail_trace" == "refs=0 copies=0" ]]; } && ok \
  || no "a PASS verdict and a leaf that exits success or clean failure write no ref and no preserved copy (pass arm: code=$quiet_pass_code want 0, verdict=$quiet_pass_word issue=$quiet_pass_issue want PASS/$quiet_issue, $quiet_pass_trace want refs=0 copies=0; clean-failure arm: code=$quiet_fail_code want 0, verdict=$quiet_fail_word issue=$quiet_fail_issue want PASS/$quiet_issue, leaf rc=${quiet_leaf_rc:-<none>} want 1, $quiet_fail_trace want refs=0 copies=0)"



# 30. the launch shape SKILL.md spells for a verifier, run end to end (issue #415). Routing the
#     verifier through the supervisor put a `supervise.sh verdict-<phase>` in front of the
#     `bash -c` wrapper that captures the verdict, and the wrapper's two outputs are what the
#     conductor reads: `.tdd/verify-<phase>.reason`, which it mirrors to the issue thread, and
#     `.tdd/verdict-<phase>.exit`, which `wait-leaf.sh` hands back as the verdict it branches on
#     — 1 REJECT (enter the revise loop), 2 malformed (bail as a system failure). Both must still
#     be verify.sh's own: a reason file carrying anything the supervisor printed would be
#     mirrored as the verifier's objection, and a code that is the wrapper's rather than the
#     verifier's would send a rejected step on as though it had passed.
#
# supervised_verdict <dir> <phase> <fake-out-text> — one verification launched that way, with
# the conductor's own wait on it; sets $sv_code to what the wait returned and $sv_reason to the
# reason file it left behind. `detach-leaf.sh` is left out of the shape: a detached launch and a
# foreground one differ only in who reaps the supervisor, and neither the reason file nor the
# recorded code is written by the reaping.
supervised_verdict() {
  local dir="$1" phase="$2" text="$3"
  mkdir -p "$dir/.tdd"
  ( cd "$dir"
    rm -f ".tdd/verdict-$phase.exit" ".tdd/verdict-$phase.pid"
    env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$dir/argv" FAKE_OUT_TEXT="$text" \
      "$HERE/../supervise.sh" "verdict-$phase" bash -c "$VERIFY --step '<STEP>' $phase '$work/spec.md' tests/test_slugify.py test_lowercases > .tdd/verify-$phase.reason 2> .tdd/verify-$phase.err; echo \$? > .tdd/verdict-$phase.exit" > /dev/null 2>&1
    "$HERE/../wait-leaf.sh" "verdict-$phase" 1 )
  sv_code=$?
  sv_reason="$(cat "$dir/.tdd/verify-$phase.reason" 2>/dev/null)"
}

supervised_verdict "$work/supervised-reject" red 'VERDICT: REJECT
REASON: The test asserts on a private helper, not observable behavior.'
sup_reject_code=$sv_code sup_reject_reason="$sv_reason"
supervised_verdict "$work/supervised-malformed" red 'the leaf rambled and never rendered a verdict'
sup_malformed_code=$sv_code
{ [[ "$sup_reject_code" == 1 ]] && [[ "$sup_malformed_code" == 2 ]] \
  && [[ "$sup_reject_reason" == 'The test asserts on a private helper, not observable behavior.' ]]; } && ok \
  || no "a supervised verification hands the conductor the verdict text and verify.sh's own code (REJECT arm: wait=$sup_reject_code want 1, reason='$sup_reject_reason' want the verifier's own line; malformed arm: wait=$sup_malformed_code want 2)"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
