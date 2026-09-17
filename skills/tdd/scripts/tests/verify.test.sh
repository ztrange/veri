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
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$ARGV_OUT"
printf '%s' "${FAKE_OUT_TEXT:-}"
exit 0
STUB
chmod +x "$stubdir/claude"

printf 'slugify must lowercase the title and join words with hyphens.' > "$work/spec.md"

# verify_in <dir> <phase> <fake-out-text> [<stub-claude>] — one verification of $work/spec.md
# against a stub claude, run in <dir> with the stub's argv recorded at <dir>/argv. stdout is the
# verifier's reason and the exit status is verify.sh's, so a caller reads whichever of the two it
# is about. Every helper below is this call, so the stub wiring and the fixture arguments — the
# spec, the test path, the test id — are spelled once rather than once per helper. The stub
# defaults to the canned-verdict one; a caller wanting another passes it, and `env` (no `-i`)
# hands that stub the caller's own environment too, which is how the mutating stub below gets
# its mutation.
verify_in() {
  ( cd "$1" && env CLAUDE_BIN="${4:-$stubdir/claude}" ARGV_OUT="$1/argv" FAKE_OUT_TEXT="$3" \
      "$VERIFY" "$2" "$work/spec.md" tests/test_slugify.py test_lowercases )
}

verify() {  # verify <fake-out-text> <phase> -> runs in $work, sets $out/$code
  out="$(verify_in "$work" "$2" "$1")"
  code=$?
}

# the second stub never finishes, so the supervisor's stuck-detection is what ends the run
cat > "$stubdir/claude-hang" <<'STUB'
#!/usr/bin/env bash
echo "thinking..."; sleep 60
STUB
chmod +x "$stubdir/claude-hang"

hung_leaf() {  # hung_leaf -> runs in $work, sets $out/$code, stderr in $work/err
  # VERI_STUCK_RETRIES=0 is pinned, not inherited: both hung-leaf cases here are about a
  # single attempt, so the caller's environment must not be able to add retries (each extra
  # attempt waits out the heartbeat window again, changing the suite's wall time).
  out="$( cd "$work" && env CLAUDE_BIN="$stubdir/claude-hang" VERI_STUCK_RETRIES=0 \
            VERI_HEARTBEAT=1 VERI_POLL=0.2 "$VERIFY" red "$work/spec.md" \
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

# verdict_field <arm> <key> — the value of <key> on the one `verdict` line of the event log
# the arm's run wrote, or a diagnostic in `<<…>>` when there is no such line, more than one,
# or no log at all. python3 rather than jq, the dependency event.test.sh and extract-result.sh
# already rely on. The arm names a directory, not a file: where the log lands under it —
# `.tdd/events.jsonl`, relative to the verification's cwd — is said once here rather than in
# each assertion.
verdict_field() {
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
' "$verdict_work/$1/.tdd/events.jsonl" "$2" 2>/dev/null || echo '<<no event log>>'
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
#!/usr/bin/env bash
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

# tamper_run <arm> <mutation> — a fresh repo at $tamper_work/<arm> holding one commit and the
# developer's uncommitted work, then one PASS verification in it whose leaf runs <mutation>
# first. Sets $out and $code to verify.sh's stdout and exit status, and $delta to what
# repo_state says moved across the launch, so each assertion below reads whichever of the three
# it is about. The two states themselves stay local: no arm wants either one apart from their
# difference, and taking it here is what keeps the pairing of the before with the after from
# being respelled once per arm.
tamper_run() {
  # `git init <dir>` creates the directory and its leading ones, so the arm's path is named
  # once here and made by the same command that makes it a repo.
  local dir="$tamper_work/$1" before after
  git init -q -b main "$dir" >/dev/null 2>&1
  # An identity in the repo's own config: a repo made by `git init` under a test has none and
  # git refuses to commit without one. In the config rather than on each command line because
  # the arm whose mutation is a commit runs that commit inside the leaf's stub, where no helper
  # of this suite reaches it — one identity, set where every caller finds it.
  git -C "$dir" config user.name veri
  git -C "$dir" config user.email veri@example.test
  printf 'the developer committed this\n' > "$dir/src.txt"
  printf '.tdd/\n' > "$dir/.gitignore"
  git -C "$dir" add -A >/dev/null 2>&1
  git -C "$dir" commit -q -m "initial" >/dev/null 2>&1
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
#     stub counts its launches in its own directory and prints no verdict on the first, a PASS on
#     the second, so the case reads both the verdict returned and that it took two launches.
cat > "$stubdir/claude-verdict-second" <<'STUB'
#!/usr/bin/env bash
n=$(( $(cat "$LAUNCH_COUNT" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$LAUNCH_COUNT"
if [[ "$n" -eq 1 ]]; then
  printf '%s' 'Waiting for the background `make test` run to complete before rendering a verdict.'
else
  printf '%s' 'VERDICT: PASS
REASON: Target test and full suite are green.'
fi
exit 0
STUB
chmod +x "$stubdir/claude-verdict-second"
no_verdict_dir="$work/no-verdict-relaunch"
mkdir -p "$no_verdict_dir"
no_verdict_out="$( LAUNCH_COUNT="$no_verdict_dir/launches" \
    verify_in "$no_verdict_dir" green '' "$stubdir/claude-verdict-second" 2>/dev/null )"
no_verdict_code=$?
no_verdict_launches="$(cat "$no_verdict_dir/launches" 2>/dev/null || echo 0)"
{ [[ "$no_verdict_code" == 0 ]] && [[ "$no_verdict_launches" == 2 ]] \
  && [[ "$no_verdict_out" == *'full suite are green'* ]]; } && ok \
  || no "a verifier leaf that exited cleanly with no VERDICT: line is relaunched and its second verdict returned (code=$no_verdict_code want 0; launches=$no_verdict_launches want 2; output='$no_verdict_out' want the PASS reason)"

# 20. no-verdict relaunches stop after VERI_NO_VERDICT_RETRIES (default 1), issue #219: a leaf that
#     never prints a verdict is exit 2 after exactly 1 + VERI_NO_VERDICT_RETRIES launches. Read at
#     the default (the variable unset, not inherited from the caller), at 0 (one launch, no
#     relaunch) and at 2, so a budget hardcoded to the default cannot pass for the knob.
cat > "$stubdir/claude-never-verdict" <<'STUB'
#!/usr/bin/env bash
n=$(( $(cat "$LAUNCH_COUNT" 2>/dev/null || echo 0) + 1 ))
echo "$n" > "$LAUNCH_COUNT"
printf '%s' 'Waiting for the background `make test` run to complete before rendering a verdict.'
exit 0
STUB
chmod +x "$stubdir/claude-never-verdict"
never_verdict() {  # never_verdict <label> [<retries>] -> prints "<code> <launches>"
  local dir="$work/never-verdict-$1"
  mkdir -p "$dir"
  ( if [[ $# -ge 2 ]]; then export VERI_NO_VERDICT_RETRIES="$2"; else unset VERI_NO_VERDICT_RETRIES; fi
    LAUNCH_COUNT="$dir/launches" verify_in "$dir" green '' "$stubdir/claude-never-verdict" >/dev/null 2>&1
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
