#!/usr/bin/env bash
# Unit tests for the suites themselves — a suite that asserts a script's DEFAULT must not
# inherit an override for that default from the shell that ran it.
# Zero-dependency plain-shell asserts, same idiom as refactor-budget.test.sh.
#
# Why this exists (issue #87): an unattended run exports VERI_STUCK_RETRIES for its outer
# supervisor, the inner `make test` inherits it, and veri's own preflight then reads a red
# baseline on veri's own repo and refuses to start. A suite's answer must be a fact about
# the script, not about the caller's environment.
#
# Contract under test:
#   VERI_STUCK_RETRIES=0 supervise-retry.test.sh → exit 0, "1 passed, 0 failed",
#   exactly as with the variable unset.
#   VERI_MODEL=<x> leaf-model.test.sh → the same exit and the same stdout as a run with
#   the three model variables cleared.
#
# Run: scripts/tests/hermetic-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem.
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

# same_both_ways <suite> <cleared env setting…> -- <ambient env setting…> — run one suite twice
# as a child process, once with the names cleared and once with one of them carrying an ambient
# value, and collect the difference into `problems` for `report`.
#
# Asked as "the same answer both ways" rather than against a hardcoded count line, which is what
# case 1 below can do with a suite holding a single case: a suite that has several cases and will
# grow would fail a count spelled here for a case added there rather than for a leak. The cleared
# arm is also probed for being green at all, since two identically red runs agree on nothing worth
# pinning. The settings are forwarded to `env` verbatim, so `-u NAME` and `NAME=value` both reach
# it as themselves and the one under test stays where it is the point.
same_both_ways() {
  local suite="$1"; shift
  local arg seen=0
  local cleared=() ambient=()
  for arg in "$@"; do
    if [[ "$arg" == "--" ]]; then
      seen=1
    elif [[ "$seen" == 0 ]]; then
      cleared+=("$arg")
    else
      ambient+=("$arg")
    fi
  done

  local cleared_out cleared_code ambient_out ambient_code
  cleared_out="$(env "${cleared[@]}" "$HERE/$suite" 2>/dev/null)" && cleared_code=0 || cleared_code=$?
  ambient_out="$(env "${ambient[@]}" "$HERE/$suite" 2>/dev/null)" && ambient_code=0 || ambient_code=$?

  problems=()
  [[ "$cleared_code" == 0 ]] ||
    problems+=("the cleared run is not green, so there is nothing to compare against: exit $cleared_code, stdout: $(printf '%q' "$cleared_out")")
  [[ "$ambient_code" == "$cleared_code" ]] ||
    problems+=("want the cleared run's exit $cleared_code, got $ambient_code")
  [[ "$ambient_out" == "$cleared_out" ]] ||
    problems+=("want the cleared run's stdout $(printf '%q' "$cleared_out"), got: $(printf '%q' "$ambient_out")")
}

# 1. The contract above, probed by running the whole suite as a child process: the leak is
#    in how supervise-retry.test.sh spawns the supervisor, so only a real run of it walks
#    that path — there is nothing to assert in-process.
name="supervise-retry.test.sh: ambient VERI_STUCK_RETRIES=0 still gives 1 passed, 0 failed"
problems=()
out="$(VERI_STUCK_RETRIES=0 "$HERE/supervise-retry.test.sh" 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0, got $code")
[[ "$out" == *'1 passed, 0 failed'* ]] ||
  problems+=("want '1 passed, 0 failed' on stdout, got: $(printf '%q' "$out")")
report "$name"

# 2. The same rule for the three model variables issue #171 adds, and the suite whose whole
#    subject is them: leaf-model.sh answers `sonnet` or nothing depending on VERI_MODEL,
#    VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER, so every case in leaf-model.test.sh that
#    asserts the unset contract — "no variable set prints NOTHING, and the `claude` command
#    line is byte-identical to today's" — is asserting it about whatever shell typed
#    `make test`, unless that suite clears the three names for itself.
#
#    One ambient name, VERI_MODEL, because it is the one that reaches BOTH roles: a leak of
#    the run-wide knob changes every probe in that suite, where a role variable could only
#    change half of them. The two role names are cleared in both arms so that a shell which
#    exported one cannot make the arms differ by something this case did not set.
#
#    leaf-model.test.sh (~0.3 s) and not supervise.test.sh, whose `sup_run_no_model` is the
#    other guard of the same rule: this file runs inside `make test`, which three leaves of
#    every step run, and supervising real leaves again as a child costs ~24 s of each of them
#    — the cost issue #171 exists to cut. That guard is left to the suite that owns it.
name="leaf-model.test.sh: an ambient VERI_MODEL gives the same exit and the same stdout as a cleared run"
same_both_ways leaf-model.test.sh \
  -u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER \
  -- -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER VERI_MODEL=sonnet
report "$name"

# 3. The same rule for the label tunables issue #113 adds, and the suite that owns them:
#    solvable-issues.sh reads `${VERI_PRIORITY_LABEL:-priority}` to decide which band an issue
#    sorts in, so every case in solvable-issues.test.sh that asserts the DEFAULT band order is
#    asserting it about whatever shell typed `make test`, unless that suite clears the name for
#    itself. An operator steering a loop exports exactly this variable, and the inner `make
#    test` of a run on veri's own repository inherits it — the shape of #87 again.
#
#    The ambient value is `ready-for-agent` because it is the one label the fixtures actually
#    carry: a name no fixture mentions renames the band to something nothing is in, changes no
#    answer, and would make this case pass while the leak it exists for stayed open.
name="solvable-issues.test.sh: an ambient VERI_PRIORITY_LABEL gives the same exit and the same stdout as a cleared run"
same_both_ways solvable-issues.test.sh \
  -u VERI_PRIORITY_LABEL \
  -- VERI_PRIORITY_LABEL=ready-for-agent
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
