#!/usr/bin/env bash
# Unit tests for the `test` recipe in this repository's Makefile — what it does with a suite
# that stops asserting.
#
# Contract under test:
#   `make test` over a suite that dies from an unbound variable inside a numeric
#   comparison after its first case and exits 0 comes back non-zero, and says which suite
#   never reached its count line.
#
# Run: skills/tdd/scripts/tests/count-line-guard.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

FIXTURE='skills/tdd/scripts/tests/fixtures/silent-death/dies-silently.test.sh'
FIXTURE_PATH="$ROOT/$FIXTURE"
FIXTURE_NAME="$(basename "$FIXTURE")"

GREEN_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-green.test.sh'
GREEN_FIXTURE_PATH="$ROOT/$GREEN_FIXTURE"
RED_FIXTURE='skills/tdd/scripts/tests/fixtures/live-suites/ends-red.test.sh'
RED_FIXTURE_PATH="$ROOT/$RED_FIXTURE"

PAUSE_FIXTURE='skills/tdd/scripts/tests/fixtures/streaming/pauses-midway.test.sh'
PAUSE_LINE='FAIL - a suite says something before it is finished'

MAKEFILE="$ROOT/Makefile"
TESTS_DIR='skills/tdd/scripts/tests'
ADDED_NAME='newly-added.test.sh'

RUNNER="$ROOT/skills/tdd/scripts/run-suite.sh"

ENV_SUITE_NAME='reports-tests-var.test.sh'

GUARDLESS_SUITE_NAME='answers-green.test.sh'

GUARD_MESSAGE=': never reached its count line'
GUARD_PATTERN='passed, [0-9]+ failed'

COUNT_LINE='^[0-9]+ passed, [0-9]+ failed$'

CLAUDE_MD="$ROOT/CLAUDE.md"


source "$HERE/lib/harness.sh"

flat() { printf '%s' "$1" | tr '\n' '/'; }

blames() {
  local named
  named="$(grep -F "$2" <<< "$1")"
  grep -Eqi 'count[ -]line' <<< "$named" ||
    problems+=("no line of the run both names $2 and says it never reached its count line$3; the lines naming it were: $(flat "$named")")
}

recipe() {
  recipe_out="$(make -C "$ROOT" test TESTS="$1" UNIT_TESTS= 2>&1)" && recipe_code=0 || recipe_code=$?
}

direct() {
  direct_out="$("$@" 2>&1)" && direct_code=0 || direct_code=$?
}

have_runner() {
  [[ -x "$RUNNER" ]] && return 0
  problems+=("there is no executable single-suite runner at $RUNNER, $1")
  return 1
}

probe_fixture_dies_quietly() {
  direct "$FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("the fixture no longer exits 0 when it dies; got $direct_code, so nothing here pins a runner that trusts the exit code")
  grep -q 'unbound variable' <<< "$direct_out" ||
    problems+=("the fixture no longer dies from an unbound variable; its output was: $(flat "$direct_out")")
  ! grep -Eq "$COUNT_LINE" <<< "$direct_out" ||
    problems+=("the fixture reached its count line, so it did not die: $(flat "$direct_out")")
}

probe_make_fails() {
  recipe "$FIXTURE"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail over a suite that died; it exited 0 and said: $(flat "$recipe_out")")
}

name="make test over a suite that dies from an unbound variable after its first case and exits 0 fails and names it"
problems=()
recipe_out=""
recipe_code=0

probe_fixture_dies_quietly
probe_make_fails
blames "$recipe_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"

report "$name"

probe_live_fixtures_are_what_they_claim() {
  direct "$GREEN_FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("the green fixture no longer exits 0; got $direct_code, so nothing below pins the passing half")
  [[ "$(tail -n 1 <<< "$direct_out")" =~ ^[0-9]+' passed, 0 failed'$ ]] ||
    problems+=("the green fixture no longer ends in a count line reporting nothing failed: $(flat "$direct_out")")

  direct "$RED_FIXTURE_PATH"
  [[ "$direct_code" != 0 ]] ||
    problems+=("the red fixture no longer exits non-zero, so nothing below pins a runner that reads the count line instead of the exit code")
  [[ "$(tail -n 1 <<< "$direct_out")" =~ $COUNT_LINE ]] ||
    problems+=("the red fixture no longer reaches its count line, so it fails the way case 1's fixture does: $(flat "$direct_out")")
}

probe_make_passes_the_green_suite() {
  recipe "$GREEN_FIXTURE"
  [[ "$recipe_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite that ends in its count line with nothing failed; it exited $recipe_code and said: $(flat "$recipe_out")")
}

probe_make_fails_the_red_suite() {
  recipe "$RED_FIXTURE"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite that exits non-zero even though it reached its count line; it exited 0 and said: $(flat "$recipe_out")")
}

name="make test still passes a suite ending in its count line with nothing failed, and still fails one that prints its count line and exits non-zero"
problems=()

probe_live_fixtures_are_what_they_claim
probe_make_passes_the_green_suite
probe_make_fails_the_red_suite

report "$name"

probe_added_suite_gets_the_check() {
  local tree out code
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to add a suite to, so the criterion went unasked")
    return
  }
  mkdir -p "$tree/$TESTS_DIR"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$FIXTURE_PATH" "$tree/$TESTS_DIR/$ADDED_NAME"
  cmp -s "$MAKEFILE" "$tree/Makefile" ||
    problems+=("the runner under test is not this repository's Makefile, so nothing here says the check costs no edit to it")

  out="$(make -C "$tree" test 2>&1)" && code=0 || code=$?
  [[ "$code" != 0 ]] ||
    problems+=("want the recipe to refuse a suite added under $TESTS_DIR with no TESTS override and no edit to it; it exited 0 and said: $(flat "$out")")
  blames "$out" "$ADDED_NAME" ", so the added suite did not get the check"

  rm -rf "$tree"
}

name="a suite added under skills/tdd/scripts/tests/ gets the count-line check with no edit to the runner"
problems=()

probe_added_suite_gets_the_check

report "$name"

probe_run_showed_the_line_while_the_suite_ran() {
  local looks=0 mk
  stream_log="$(mktemp)" || {
    problems+=("could not make a file to collect a run's output into, so the criterion went unasked")
    return
  }

  local started="$EPOCHREALTIME"
  make -C "$ROOT" test TESTS="$PAUSE_FIXTURE" UNIT_TESTS= > "$stream_log" 2>&1 &
  mk=$!
  while :; do
    if grep -qF "$PAUSE_LINE" "$stream_log"; then
      grep -Eq "$COUNT_LINE" "$stream_log" || streamed=yes
      break
    fi
    grep -Eq "$COUNT_LINE" "$stream_log" && break
    looks=$((looks + 1))
    if [[ "$looks" -gt 1500 ]]; then
      problems+=("the run had still not printed the fixture's count line after 30s; gave up on it")
      kill "$mk" 2>/dev/null
      break
    fi
    sleep 0.02
  done
  wait "$mk" 2>/dev/null
  stream_elapsed="$(awk -v a="$started" -v b="$EPOCHREALTIME" 'BEGIN { printf "%.3f", b - a }')"

  [[ "$streamed" == yes ]] || {
    if grep -qF "$PAUSE_LINE" "$stream_log"; then
      problems+=("the suite's FAIL line was never there without its count line beside it, so the run had shown nothing until the suite was over; it said: $(flat "$(cat "$stream_log")")")
    else
      problems+=("the run never showed the suite's FAIL line at all; it said: $(flat "$(cat "$stream_log")")")
    fi
  }
}

probe_that_run_could_have_told_the_difference() {
  awk -v e="$stream_elapsed" 'BEGIN { exit !(e >= 0.15) }' ||
    problems+=("the whole run took under 0.15s (got ${stream_elapsed}s), so the fixture no longer pauses long enough and there was no window in which a streamed line and a buffered one differ")
  grep -Eq "$COUNT_LINE" "$stream_log" ||
    problems+=("the fixture's count line never matched the pattern the probe above waits for, so 'the FAIL line without the count line' was true of every look and says nothing: $(flat "$(cat "$stream_log")")")
  rm -f "$stream_log"
}

name="make test shows a suite's line while that suite is still running"
problems=()
stream_log=""
stream_elapsed=0
streamed=no

probe_run_showed_the_line_while_the_suite_ran
probe_that_run_could_have_told_the_difference

report "$name"

plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; }

says() {
  local fact="$1" re
  shift
  for re in "$@"; do
    [[ "$idiom" =~ $re ]] || {
      problems+=("CLAUDE.md's Testing idiom section does not say $fact")
      return
    }
  done
}

probe_idiom_records_the_check() {
  idiom="$(awk '/^## Testing idiom/ { f = 1; next } f && /^## / { exit } f' "$CLAUDE_MD" | plain | tr '\n' ' ')"
  [[ -n "${idiom// /}" ]] || {
    problems+=("CLAUDE.md has no '## Testing idiom' section to read, so neither half of the rule is recorded where an author writing a suite is sent")
    return
  }

  says "the runner itself fails a suite that never reached its count line" \
    'count[ -]line' 'fail|refus|reject|red'
  says "why a suite's exit code alone is not trusted — one that stops asserting partway can still come back 0" \
    'exit (code|status)|exits? 0|exit-code' \
    'alone|by itself|only|not enough|trust' \
    'die|dies|died|dying|stops? asserting|silen|unbound|set -u'
}

name="CLAUDE.md's Testing idiom section says the runner enforces the count line, and why an exit code alone is not trusted"
problems=()
idiom=""

probe_idiom_records_the_check

report "$name"

probe_reaching_suite_is_refused_and_named() {
  local tree suite reach tried
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to hold a suite that reaches the network, so the criterion went unasked")
    return
  }
  suite="$tree/reaches-network.test.sh"
  cat > "$suite" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
gh api --hostname example.invalid veri-gh-probe >/dev/null 2>&1
curl -s --max-time 2 https://example.invalid/veri-curl-probe >/dev/null 2>&1
echo "1 passed, 0 failed"
exit 0
SUITE
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite that tried the network; it exited 0 and said: $(flat "$recipe_out")")
  for reach in veri-gh-probe veri-curl-probe; do
    tried="$(grep -F 'reaches-network.test.sh' <<< "$recipe_out" | grep -F "$reach")"
    [[ -n "$tried" ]] ||
      problems+=("no line of the run names reaches-network.test.sh together with the attempt carrying $reach, so the refusal does not say which suite tried what")
  done

  rm -rf "$tree"
}

name="make test fails a suite that runs gh or curl, naming the suite and what it tried"
problems=()
recipe_out=""
recipe_code=0

probe_reaching_suite_is_refused_and_named

report "$name"

probe_git_transport_allowlist() {
  local tree suite own_origin
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to hold the git-allowlist probe, so the criterion went unasked")
    return
  }
  new_repo -b main "$tree/src" >/dev/null 2>&1
  ( cd "$tree/src" && : > f && git add f && git -c user.email=a@b.c -c user.name=a commit -q -m init ) \
    >/dev/null 2>&1
  new_repo -b main "$tree/dest" >/dev/null 2>&1
  own_origin="$(git -C "$ROOT" remote get-url origin 2>/dev/null)"

  suite="$tree/checks-transport-allowlist.test.sh"
  {
    printf '#!/usr/bin/env bash\nset -uo pipefail\n'
    printf 'dest=%q\n' "$tree/dest"
    printf 'own_origin=%q\n' "$own_origin"
    cat <<'SUITE'
problems=()
blocked() {
  local label="$1" url="$2" err rc
  err="$(GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch "$url" 2>&1 >/dev/null)"; rc=$?
  [[ "$rc" -ne 0 ]] || problems+=("$label was not refused (exit 0)")
  grep -qi 'not allowed' <<< "$err" ||
    problems+=("$label's refusal carried no 'not allowed' message: $err")
}
for pair in \
  "https:https://example.invalid/veri-https-probe.git" \
  "ssh-scheme:ssh://example.invalid/veri-ssh-probe.git" \
  "git-scheme:git://example.invalid/veri-git-scheme-probe.git" \
  "scp-style:git@example.invalid:veri-scp-probe.git"; do
  blocked "${pair%%:*}" "${pair#*:}"
done
if [[ -n "$own_origin" ]]; then
  blocked "own-origin" "$own_origin"
fi
err="$(GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch --quiet ../src 2>&1 >/dev/null)"; rc=$?
[[ "$rc" -eq 0 ]] || problems+=("a local relative fetch was refused: $err")
if [[ "${#problems[@]}" -eq 0 ]]; then
  echo "1 passed, 0 failed"
  exit 0
else
  printf 'PROBLEM: %s\n' "${problems[@]}"
  echo "0 passed, 1 failed"
  exit 1
fi
SUITE
  } > "$suite"
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite whose every remote git form was refused and whose local fetch still worked; got exit $recipe_code: $(flat "$recipe_out")")
  [[ -n "$own_origin" ]] ||
    problems+=("this checkout has no origin, so the own-origin form of the probe checked nothing")

  rm -rf "$tree"
}

name="make test's git allows only local remotes: https, ssh, git and scp-style forms are refused, a local path still fetches"
problems=()
recipe_out=""
recipe_code=0

probe_git_transport_allowlist

report "$name"

probe_unswallowed_git_reach_fails_visibly() {
  local tree suite
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to hold the unswallowed-reach probe, so the criterion went unasked")
    return
  }
  new_repo -b main "$tree/dest" >/dev/null 2>&1
  suite="$tree/reach-not-swallowed.test.sh"
  {
    printf '#!/usr/bin/env bash\nset -uo pipefail\n'
    printf 'dest=%q\n' "$tree/dest"
    cat <<'SUITE'
GIT_TERMINAL_PROMPT=0 git -C "$dest" fetch https://example.invalid/veri-visible-probe.git
rc=$?
if [[ "$rc" -eq 0 ]]; then
  echo "1 passed, 0 failed"
  exit 0
else
  echo "0 passed, 1 failed"
  exit 1
fi
SUITE
  } > "$suite"
  chmod +x "$suite"

  recipe "$suite"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite whose git fetch of a remote URL it did not swallow; it exited 0 and said: $(flat "$recipe_out")")
  grep -qi 'not allowed' <<< "$recipe_out" ||
    problems+=("want git's own refusal text ('transport … not allowed') visible in the run's output; got: $(flat "$recipe_out")")
  ! grep -qF 'tried the network' <<< "$recipe_out" ||
    problems+=("a git reach is no longer caught by the reach log (that mechanism now covers only gh and curl); want no manufactured 'tried the network' line, got: $(flat "$recipe_out")")

  rm -rf "$tree"
}

name="make test fails a suite whose unswallowed git fetch of a remote URL is refused, visibly, with no manufactured reach-log line"
problems=()
recipe_out=""
recipe_code=0

probe_unswallowed_git_reach_fails_visibly

report "$name"

probe_runner_refuses_the_countless_suite() {
  have_runner "so a leaf that runs one suite has nothing to run it through and its count line goes unread" || return
  direct "$RUNNER" "$FIXTURE_PATH"
  [[ "$direct_code" != 0 ]] ||
    problems+=("want the runner to fail over a suite that died without reaching its count line; it exited 0 and said: $(flat "$direct_out")")
  blames "$direct_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"
}

name="the suite runner over a suite that exits 0 without reaching its count line fails and names it"
problems=()

probe_fixture_dies_quietly
probe_runner_refuses_the_countless_suite

report "$name"

probe_suite_path() {
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to write a suite into, so the criterion went unasked")
    return 1
  }
  probe="$tree/$1"
}

probe_runner_runs_the_named_suite_with_no_TESTS() {
  local tree probe seen
  have_runner "so there is no invocation to ask this of" || return
  probe_suite_path "$ENV_SUITE_NAME" || return
  cat > "$probe" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
printf 'TESTS=%s\n' "${TESTS-<unset>}"
echo "1 passed, 0 failed"
SUITE
  chmod +x "$probe"

  direct env -u TESTS "$RUNNER" "$probe"
  seen="$(grep -E '^TESTS=' <<< "$direct_out" | tail -n 1)"
  [[ -n "$seen" ]] ||
    problems+=("the runner never ran the suite it was named, so nothing here says what its environment held; it exited $direct_code and said: $(flat "$direct_out")")
  [[ "$direct_code" == 0 ]] ||
    problems+=("want the runner to pass a suite that reaches its count line with nothing failed; it exited $direct_code and said: $(flat "$direct_out")")
  [[ -z "$seen" || "$seen" == 'TESTS=<unset>' ]] ||
    problems+=("the runner put TESTS in the named suite's environment ($seen), so a make nested inside that suite inherits it and runs that one suite instead of its own")

  rm -rf "$tree"
}

name="the suite runner runs the suite it is named with no TESTS in that suite's environment"
problems=()

probe_runner_runs_the_named_suite_with_no_TESTS

report "$name"

guard_sites() {
  local text="$1" site sites=()
  while IFS= read -r site; do
    local body
    body="$(grep -v '^[[:space:]]*#' "$site")"
    grep -qF "$text" <<< "$body" && sites+=("$(basename "$site")")
  done < <(printf '%s\n' "$MAKEFILE"; find "$ROOT/skills/tdd/scripts" -name '*.sh' -not -path '*/tests/*' | sort)
  ((${#sites[@]})) && printf '%s\n' "${sites[@]}"
}

probe_one_guard_behind_both_invocations() {
  local pair text label sites n
  for pair in "$GUARD_MESSAGE|what a countless suite is told" "$GUARD_PATTERN|what a count line looks like"; do
    text="${pair%%|*}"
    label="${pair#*|}"
    mapfile -t sites < <(guard_sites "$text")
    n="${#sites[@]}"
    [[ "$n" -eq 1 ]] ||
      problems+=("$label is decided in $n place(s) — ${sites[*]:-nowhere} — so 'make test' and the suite runner do not share one guard and can drift apart about it")
  done
}

probe_both_invocations_word_it_the_same() {
  local made ran
  have_runner "so there is no second invocation to compare the recipe against" || return
  recipe "$FIXTURE"
  made="$(grep -F "$GUARD_MESSAGE" <<< "$recipe_out" | awk 'NR==1')"
  direct "$RUNNER" "$FIXTURE_PATH"
  ran="$(grep -F "$GUARD_MESSAGE" <<< "$direct_out" | awk 'NR==1')"
  [[ -n "$made" && -n "$ran" ]] || {
    problems+=("one of the two invocations did not report the countless suite at all; 'make test' said: $(flat "$recipe_out") and the runner said: $(flat "$direct_out")")
    return
  }
  [[ "$made" == "$ran" ]] ||
    problems+=("the two invocations word the refusal differently: 'make test' said '$made' and the runner said '$ran'")
}

name="the make target and the suite runner refuse a countless suite from one guard, in the same words"
problems=()
recipe_out=""
recipe_code=0

probe_one_guard_behind_both_invocations
probe_both_invocations_word_it_the_same

report "$name"

ran_in_root() {
  local tree body="$1" probe
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to stand a runner up in, so the question went unasked")
    return 1
  }
  probe="$tree/$GUARDLESS_SUITE_NAME"
  mkdir -p "$tree/skills/tdd/scripts/lib"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp "$ROOT/skills/tdd/scripts/lib/exit-contract.sh" "$tree/skills/tdd/scripts/lib/"
  printf '%s\n' "$body" > "$tree/Makefile"
  cat > "$probe" <<'SUITE'
#!/usr/bin/env bash
set -uo pipefail
echo "1 passed, 0 failed"
SUITE
  chmod +x "$probe"

  direct "$tree/skills/tdd/scripts/run-suite.sh" "$probe"
  rm -rf "$tree"
}

probe_root_that_answers_the_guard_runs_the_suite() {
  local body
  body="$(cat <<'MK'
count-line-guard:
	@printf "COUNT_LINE='%s'\nCOUNTLESS='%s'\n" '^[0-9]+ passed, [0-9]+ failed$$' '%s: never reached its count line\n'
MK
)"
  ran_in_root "$body" || return
  [[ "$direct_code" == 0 ]] ||
    problems+=("the runner does not pass a green suite even in a scratch root whose make answers for the guard; it exited $direct_code and said: $(flat "$direct_out") — so nothing below distinguishes a refused guard from a copy that cannot run at all")
}

probe_root_that_cannot_answer_the_guard_is_refused() {
  ran_in_root "count-line-guard:
	@:" || return
  [[ "$direct_code" == 2 ]] ||
    problems+=("want exit 2 from a runner whose root cannot answer for the guard — no answer could be obtained — got $direct_code, and it said: $(flat "$direct_out")")
  ! grep -Fq "$GUARD_MESSAGE" <<< "$direct_out" ||
    problems+=("the runner reported a verdict on the suite while holding no guard to judge it by: $(flat "$direct_out")")
  grep -Eqi 'could not read.*guard' <<< "$direct_out" ||
    problems+=("the runner did not say that it could not read the guard, so a caller cannot tell this 2 from any other; it said: $(flat "$direct_out")")
}

name="the suite runner whose root cannot answer for the guard reports no suite and exits 2"
problems=()

probe_root_that_answers_the_guard_runs_the_suite
probe_root_that_cannot_answer_the_guard_is_refused

report "$name"

probe_runner_refuses_the_countless_suite_as_a_clean_negative() {
  have_runner "so the one invocation a leaf is told to use for a single suite cannot be asked what a countless suite earns" || return
  direct "$RUNNER" "$FIXTURE_PATH"
  [[ "$direct_code" == 1 ]] ||
    problems+=("want exit 1 from the runner over a suite that died without its count line — the suite ran and the tree under it is not green — got $direct_code, and it said: $(flat "$direct_out")")
  blames "$direct_out" "$FIXTURE_NAME" ", so its refusal does not say which suite died"
}

name="the partially-dead fixture run directly through the suite runner is refused as a clean negative, named"
problems=()

probe_fixture_dies_quietly
probe_runner_refuses_the_countless_suite_as_a_clean_negative

name="the pipeline-fed matches give the same verdict on a matching and a non-matching input when the writer is preempted"
problems=()

verdict() {
  local CLAUDE_MD="$1" idiom="" problems=()
  probe_idiom_records_the_check
  printf '%s\n' "${#problems[@]}" "${problems[@]}"
}

unpreempted="$(declare -f plain)"
barren="$(mktemp)" || {
  problems+=("could not write a document carrying neither fact, so half the criterion went unasked")
  barren=/dev/null
}
printf '## Testing idiom\nSuites live beside the scripts they cover and match the house style.\n\n## Next\n' > "$barren"

honest_match="$(verdict "$CLAUDE_MD")"
honest_miss="$(verdict "$barren")"
plain() { tr -d '*`' | tr '[:upper:]' '[:lower:]'; return 141; }
preempted_match="$(verdict "$CLAUDE_MD")"
preempted_miss="$(verdict "$barren")"
eval "$unpreempted"
rm -f "$barren"

if [[ "$honest_match" != 0 ]]; then
  problems+=("with the fold intact the probe already objects to CLAUDE.md (${honest_match%%$'\n'*} problems), so a verdict that survives preemption would only be two wrong answers agreeing")
fi
if [[ "${honest_miss%%$'\n'*}" == 0 ]]; then
  problems+=("with the fold intact the probe accepts a document carrying neither fact, so a verdict that survives preemption would prove nothing")
fi
if [[ "$preempted_match" != "$honest_match" ]]; then
  problems+=("a preempted writer changes the pipeline-fed verdict on a matching input: ${honest_match%%$'\n'*} problems become ${preempted_match%%$'\n'*}")
fi
if [[ "$preempted_miss" != "$honest_miss" ]]; then
  problems+=("a preempted writer changes the pipeline-fed verdict on a non-matching input: ${honest_miss%%$'\n'*} problems become ${preempted_miss%%$'\n'*}")
fi

report "$name"

name="make test still fails a suite whose last line is not its count line, naming it exactly as before the repair (#524)"
problems=()

scratch_suite_run() {
  local tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to hold the suite, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR"
  cp "$MAKEFILE" "$tree/Makefile"
  printf '#!/bin/sh\n%s\nexit 0\n' "$2" > "$tree/$TESTS_DIR/$1"
  chmod +x "$tree/$TESTS_DIR/$1"
  scratch_out="$(make -C "$tree" test 2>&1)" && scratch_code=0 || scratch_code=$?
  rm -rf "$tree"
}

trailing_name='count-then-chatter.test.sh'
if scratch_suite_run "$trailing_name" 'echo "3 passed, 0 failed"
echo "one more line after the count"'; then
  [[ "$scratch_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite whose last line is not its count line; it exited 0 and said: $(flat "$scratch_out")")
  grep -Fx "$trailing_name$GUARD_MESSAGE" <<< "$scratch_out" > /dev/null ||
    problems+=("want the line '$trailing_name$GUARD_MESSAGE' in the run's output; it said: $(flat "$scratch_out")")
fi

report "$name"

name="make test passes a suite whose stderr outlives its stdout count line, and still fails one whose stdout never reaches it (#526)"
problems=()

stderr_suite_name='count-then-stderr.test.sh'
broken_pipe="echo \"tail: error writing 'standard output': Broken pipe\" >&2"
if scratch_suite_run "$stderr_suite_name" "echo '13 passed, 0 failed'
$broken_pipe"; then
  [[ "$scratch_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite whose stdout ended in its count line and exited 0 with a stderr line after it; it exited $scratch_code and said: $(flat "$scratch_out")")
fi
if scratch_suite_run "$stderr_suite_name" "echo 'a case ran'
$broken_pipe"; then
  [[ "$scratch_code" != 0 ]] ||
    problems+=("want 'make test' to fail a suite whose stdout never reached its count line; it exited 0 and said: $(flat "$scratch_out")")
  grep -Fx "$stderr_suite_name$GUARD_MESSAGE" <<< "$scratch_out" > /dev/null ||
    problems+=("want the line '$stderr_suite_name$GUARD_MESSAGE' for a suite whose stdout never reached its count line; it said: $(flat "$scratch_out")")
fi

report "$name"

refusal_from() {
  refusal="$(awk -v p="$1$GUARD_MESSAGE" 'index($0, p) == 1 { f = 1 } f' <<< "$scratch_out")"
  [[ -n "$refusal" ]] ||
    problems+=("want a line beginning '$1$GUARD_MESSAGE'; it said: $(flat "$scratch_out")")
}

called_empty() {
  scratch_suite_run "$1" "$2" || return 0
  refusal_from "$1"
  grep -E "^$1: .*: ?$" <<< "$refusal" > /dev/null &&
    problems+=("want no line quoting an empty last line; from the refusal on it said: $(flat "$refusal")")
  grep -E "^$1: .*empty" <<< "$refusal" > /dev/null ||
    problems+=("want a line naming the suite and saying its output was empty; from the refusal on it said: $(flat "$refusal")")
}

name="make test quotes a countless suite's last line verbatim in its refusal (#508)"
problems=()

quoted_name='count-then-rm.test.sh'
quoted_line="rm: cannot remove '/tmp/clone26/.git': Directory not empty"
if scratch_suite_run "$quoted_name" "echo '27 passed, 0 failed'
echo \"$quoted_line\""; then
  refusal_from "$quoted_name"
  grep -F "$quoted_line" <<< "$refusal" > /dev/null ||
    problems+=("want the refusal to quote the suite's last line '$quoted_line'; from the refusal on it said: $(flat "$refusal")")
fi

report "$name"

name="make test reports a suite that printed nothing as empty rather than quoting an empty line (#508)"
problems=()

called_empty 'prints-nothing.test.sh' ':'

report "$name"

name="make test reports a suite that printed only blank lines as empty rather than quoting an empty line (#508)"
problems=()

called_empty 'prints-blank-lines.test.sh' 'echo
echo'

report "$name"

name="make test prints no count-line refusal for a suite whose last line is its count line (#508)"
problems=()

counted_name='ends-in-count.test.sh'
if scratch_suite_run "$counted_name" "echo 'a case ran'
echo '4 passed, 0 failed'"; then
  [[ "$scratch_code" == 0 ]] ||
    problems+=("want 'make test' to pass a suite whose last line is its count line; it exited $scratch_code and said: $(flat "$scratch_out")")
  if said="$(grep -F "$counted_name:" <<< "$scratch_out")"; then
    problems+=("want no line reporting on $counted_name, which reached its count line; it said: $(flat "$said")")
  fi
fi

report "$name"

name="the recipe calls this suite makes run only the fixture they name, and no suite from tests/unit/"
problems=()

recipe "$GREEN_FIXTURE"
for u in "$HERE"/unit/*.test.sh; do
  grep -qxF "== $(basename "$u")" <<< "$recipe_out" &&
    problems+=("want the run over $GREEN_FIXTURE to name only it; it also ran $(basename "$u")")
done

report "$name"

name="run-suite.sh, terminated while its EXIT trap is armed, ends with exit 2"
problems=()

probe_runner_terminated_mid_suite() {
  local tree probe
  have_runner "so there is no invocation to ask this of" || return
  probe_suite_path terminates-its-runner.test.sh || return
  cat > "$probe" <<'SUITE'
#!/bin/sh
kill -TERM "$PPID"
echo "1 passed, 0 failed"
SUITE
  chmod +x "$probe"

  direct "$RUNNER" "$probe"
  [[ "$direct_code" == 2 ]] ||
    problems+=("want exit 2 from a runner terminated while its suite ran; it exited $direct_code and said: $(flat "$direct_out")")
}

probe_runner_terminated_mid_suite

report "$name"

name="run-suite.sh through a symlinked skills/tdd with no Makefile three levels up runs a green suite and exits 0 (#617)"
problems=()

probe_runner_through_symlinked_skill() {
  local tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to link the skill into, so the question went unasked")
    return 1
  }
  mkdir -p "$tree/.claude/skills"
  ln -s "$ROOT/skills/tdd" "$tree/.claude/skills/tdd"

  direct "$tree/.claude/skills/tdd/scripts/run-suite.sh" "$GREEN_FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("want exit 0 from the runner invoked through a symlinked skill dir over a green suite; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx '1 passed, 0 failed' <<< "$direct_out" > /dev/null ||
    problems+=("want the green suite's own output, ending '1 passed, 0 failed'; it said: $(flat "$direct_out")")
}

probe_runner_through_symlinked_skill

report "$name"

finish
