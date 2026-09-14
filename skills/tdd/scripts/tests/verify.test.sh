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

# verify_in <dir> <phase> <fake-out-text> — one verification of $work/spec.md against the stub
# claude, run in <dir> with the stub's argv recorded at <dir>/argv. stdout is the verifier's
# reason and the exit status is verify.sh's, so a caller reads whichever of the two it is about.
# Both helpers below are this call, so the stub wiring and the fixture arguments — the spec, the
# test path, the test id — are spelled once rather than once per helper.
verify_in() {
  ( cd "$1" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$1/argv" FAKE_OUT_TEXT="$3" \
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
