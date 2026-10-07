#!/usr/bin/env bash
# Unit tests for the `test` recipe in this repository's Makefile — what it does with a suite
# that stops asserting.
#
# Contract under test:
#   `make test` over a suite that dies from an unbound variable inside a numeric
#   comparison after its first case and exits 0 comes back non-zero, and says which suite
#   never reached its count line.
#   run-suite.sh over a tests/py/test_*.py file runs it under pytest: 0 green, 1 a failing case,
#   2 when pytest cannot be imported or the file does not exist.
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
source "$HERE/lib/plain.sh"

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
  mkdir -p "$tree/$TESTS_DIR" "$tree/skills/tdd/scripts/lib"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
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
  idiom="$(awk '/^## Testing idiom/ { f = 1; next } f && /^## / { exit } f' "$CLAUDE_MD" | plain --join)"
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

probe_tally() {
  local CLAUDE_MD="$1" idiom="" problems=()
  probe_idiom_records_the_check
  printf '%s\n' "${#problems[@]}" "${problems[@]}"
}

unpreempted="$(declare -f plain)"
eval "honest_plain${unpreempted#plain}"
barren="$(mktemp)" || {
  problems+=("could not write a document carrying neither fact, so half the criterion went unasked")
  barren=/dev/null
}
printf '## Testing idiom\nSuites live beside the scripts they cover and match the house style.\n\n## Next\n' > "$barren"

honest_match="$(probe_tally "$CLAUDE_MD")"
honest_miss="$(probe_tally "$barren")"
eval 'plain() { honest_plain; return 141; }'
preempted_match="$(probe_tally "$CLAUDE_MD")"
preempted_miss="$(probe_tally "$barren")"
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
  mkdir -p "$tree/$TESTS_DIR" "$tree/skills/tdd/scripts/lib"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
  rm "$tree/skills/tdd/scripts/lib/count-line-guard.sh"
  if [[ $# -lt 3 ]]; then
    cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
  elif [[ -n "$3" ]]; then
    printf '%s\n' "$3" > "$tree/skills/tdd/scripts/lib/count-line-guard.sh"
  fi
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

runner_passes_green() {
  local runner="$1" where="$2"
  direct "$runner" "$GREEN_FIXTURE_PATH"
  [[ "$direct_code" == 0 ]] ||
    problems+=("want exit 0 from the runner $where over a green suite; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx '1 passed, 0 failed' <<< "$direct_out" > /dev/null ||
    problems+=("want the green suite's own output, ending '1 passed, 0 failed'; it said: $(flat "$direct_out")")
}

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

  runner_passes_green "$tree/.claude/skills/tdd/scripts/run-suite.sh" "invoked through a symlinked skill dir"
}

probe_runner_through_symlinked_skill

report "$name"

name="run-suite.sh from a git-archive extraction of skills/tdd alone, with no Makefile in or above it, runs a green suite and exits 0 (#617)"
problems=()

probe_runner_from_archived_skill() {
  local tree skill_tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to extract the skill into, so the question went unasked")
    return 1
  }
  skill_tree="$(GIT_INDEX_FILE="$tree/index" git -C "$ROOT" add -A -- skills/tdd &&
    GIT_INDEX_FILE="$tree/index" git -C "$ROOT" write-tree)" || {
    problems+=("could not record the working tree's skills/tdd as a git tree to archive, so the question went unasked")
    return 1
  }
  mkdir -p "$tree/snapshot"
  git -C "$ROOT" archive "$skill_tree" skills/tdd | tar -x -C "$tree/snapshot" || {
    problems+=("could not extract a git archive of skills/tdd, so the question went unasked")
    return 1
  }

  runner_passes_green "$tree/snapshot/skills/tdd/scripts/run-suite.sh" "in a git-archive extraction of skills/tdd"
}

probe_runner_from_archived_skill

report "$name"

name="run-suite.sh over a green suite, run with the working directory inside a git repository that is not veri and has no Makefile, exits 0 (#617)"
problems=()

probe_runner_from_foreign_repo() {
  local tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory for the foreign repository, so the question went unasked")
    return 1
  }
  new_repo "$tree/repo" || {
    problems+=("could not make a git repository to run from, so the question went unasked")
    return 1
  }
  cd "$tree/repo" || return 1
  runner_passes_green "$RUNNER" "run from inside a git repository that is not veri and has no Makefile"
  cd "$HERE" || return 1
}

probe_runner_from_foreign_repo

report "$name"

name="run-suite.sh over a red suite exits with the suite's own code, through a symlinked skills/tdd and from a git-archive extraction of it (#617)"
problems=()

runner_passes_red_code_through() {
  local runner="$1" where="$2" own_code
  direct "$RED_FIXTURE_PATH"
  own_code="$direct_code"
  direct "$runner" "$RED_FIXTURE_PATH"
  [[ "$direct_code" == "$own_code" ]] ||
    problems+=("want exit $own_code, the red suite's own, from the runner $where; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx '0 passed, 1 failed' <<< "$direct_out" > /dev/null ||
    problems+=("want the red suite's own output from the runner $where, ending '0 passed, 1 failed'; it said: $(flat "$direct_out")")
  ! grep -F "$GUARD_MESSAGE" <<< "$direct_out" > /dev/null ||
    problems+=("want no count-line refusal from the runner $where over a red suite that reached its count line; it said: $(flat "$direct_out")")
}

probe_runner_red_from_symlink_and_snapshot() {
  local tree skill_tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory for the symlink and the snapshot, so the question went unasked")
    return 1
  }
  mkdir -p "$tree/.claude/skills"
  ln -s "$ROOT/skills/tdd" "$tree/.claude/skills/tdd"
  runner_passes_red_code_through "$tree/.claude/skills/tdd/scripts/run-suite.sh" "invoked through a symlinked skill dir"

  skill_tree="$(GIT_INDEX_FILE="$tree/index" git -C "$ROOT" add -A -- skills/tdd &&
    GIT_INDEX_FILE="$tree/index" git -C "$ROOT" write-tree)" || {
    problems+=("could not record the working tree's skills/tdd as a git tree to archive, so the snapshot half went unasked")
    return 1
  }
  mkdir -p "$tree/snapshot"
  git -C "$ROOT" archive "$skill_tree" skills/tdd | tar -x -C "$tree/snapshot" || {
    problems+=("could not extract a git archive of skills/tdd, so the snapshot half went unasked")
    return 1
  }
  runner_passes_red_code_through "$tree/snapshot/skills/tdd/scripts/run-suite.sh" "in a git-archive extraction of skills/tdd"
}

probe_runner_red_from_symlink_and_snapshot

report "$name"

name="run-suite.sh over a suite that exits 0 without its count line exits 1 and names it, through a symlinked skills/tdd and from a git-archive extraction of it (#617)"
problems=()

runner_refuses_countless() {
  local runner="$1" where="$2"
  direct "$runner" "$FIXTURE_PATH"
  [[ "$direct_code" == 1 ]] ||
    problems+=("want exit 1 from the runner $where over a suite that exited 0 without its count line; it exited $direct_code and said: $(flat "$direct_out")")
  grep -Fx "$FIXTURE_NAME$GUARD_MESSAGE" <<< "$direct_out" > /dev/null ||
    problems+=("want the line '$FIXTURE_NAME$GUARD_MESSAGE' from the runner $where; it said: $(flat "$direct_out")")
}

probe_runner_countless_from_symlink_and_snapshot() {
  local tree skill_tree
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory for the symlink and the snapshot, so the question went unasked")
    return 1
  }
  mkdir -p "$tree/.claude/skills"
  ln -s "$ROOT/skills/tdd" "$tree/.claude/skills/tdd"
  runner_refuses_countless "$tree/.claude/skills/tdd/scripts/run-suite.sh" "invoked through a symlinked skill dir"

  skill_tree="$(GIT_INDEX_FILE="$tree/index" git -C "$ROOT" add -A -- skills/tdd &&
    GIT_INDEX_FILE="$tree/index" git -C "$ROOT" write-tree)" || {
    problems+=("could not record the working tree's skills/tdd as a git tree to archive, so the snapshot half went unasked")
    return 1
  }
  mkdir -p "$tree/snapshot"
  git -C "$ROOT" archive "$skill_tree" skills/tdd | tar -x -C "$tree/snapshot" || {
    problems+=("could not extract a git archive of skills/tdd, so the snapshot half went unasked")
    return 1
  }
  runner_refuses_countless "$tree/snapshot/skills/tdd/scripts/run-suite.sh" "in a git-archive extraction of skills/tdd"
}

probe_fixture_dies_quietly
probe_runner_countless_from_symlink_and_snapshot

report "$name"

name="make test takes its count-line guard from skills/tdd/scripts/lib/count-line-guard.sh: a refusal reworded there is what it prints, and a tree without that file fails naming it (#617)"
problems=()

GUARD_LIB='skills/tdd/scripts/lib/count-line-guard.sh'
REWORDED=': stopped before its count line'

reworded_lib=""
if [[ -f "$ROOT/$GUARD_LIB" ]]; then
  reworded_lib="$(sed "s/${GUARD_MESSAGE#: }/${REWORDED#: }/" "$ROOT/$GUARD_LIB")"
  [[ "$reworded_lib" != "$(cat "$ROOT/$GUARD_LIB")" ]] ||
    problems+=("$GUARD_LIB does not carry the refusal text '${GUARD_MESSAGE#: }', so there was nothing to reword")
else
  problems+=("there is no $GUARD_LIB for make test to take its guard from")
fi

countless_name='countless-under-lib-guard.test.sh'
if scratch_suite_run "$countless_name" "echo 'a case ran'" "$reworded_lib"; then
  grep -Fx "$countless_name$REWORDED" <<< "$scratch_out" > /dev/null ||
    problems+=("want the line '$countless_name$REWORDED' once $GUARD_LIB's refusal is reworded; it said: $(flat "$scratch_out")")
fi

libless_name='green-without-lib-guard.test.sh'
if scratch_suite_run "$libless_name" "echo '1 passed, 0 failed'" ""; then
  [[ "$scratch_code" != 0 ]] ||
    problems+=("want 'make test' to fail in a tree without $GUARD_LIB; it exited 0 and said: $(flat "$scratch_out")")
  grep -F "$(basename "$GUARD_LIB")" <<< "$scratch_out" > /dev/null ||
    problems+=("want the run to name $(basename "$GUARD_LIB") when it is missing; it said: $(flat "$scratch_out")")
fi

report "$name"

name="make test over a suite that exits 0 without its count line fails, printing the refusal byte-identical to run-suite.sh's for that suite (#617)"
problems=()

probe_make_and_runner_refuse_alike() {
  local refused
  have_runner "so there is no runner's refusal to hold make test's against" || return
  direct "$RUNNER" "$FIXTURE_PATH"
  refused="$FIXTURE_NAME$GUARD_MESSAGE"
  grep -Fx -- "$refused" <<< "$direct_out" > /dev/null || {
    problems+=("want the runner to print '$refused' as a whole line; it said: $(flat "$direct_out")")
    return
  }
  recipe "$FIXTURE"
  [[ "$recipe_code" != 0 ]] ||
    problems+=("want 'make test' to fail over a suite that exited 0 without its count line; it exited 0 and said: $(flat "$recipe_out")")
  grep -Fx -- "$refused" <<< "$recipe_out" > /dev/null ||
    problems+=("want the runner's refusal '$refused' as a whole line of the make test run; it said: $(flat "$recipe_out")")
}

probe_fixture_dies_quietly
probe_make_and_runner_refuse_alike

report "$name"

name="make test and run-suite.sh both print the refusal reworded in skills/tdd/scripts/lib/count-line-guard.sh, the one file both read (#617)"
problems=()

probe_one_lib_rewords_both() {
  local tree probe made ran
  have_runner "so there is no runner to read the reworded guard" || return
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to reword the guard in, so the question went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR" "$tree/skills/tdd/scripts/lib"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
  sed "s/${GUARD_MESSAGE#: }/${REWORDED#: }/" "$ROOT/$GUARD_LIB" > "$tree/$GUARD_LIB"
  probe="$tree/$TESTS_DIR/countless-under-shared-guard.test.sh"
  printf '#!/bin/sh\necho "a case ran"\nexit 0\n' > "$probe"
  chmod +x "$probe"

  scratch_out="$(make -C "$tree" test 2>&1)" && scratch_code=0 || scratch_code=$?
  direct "$tree/skills/tdd/scripts/run-suite.sh" "$probe"
  rm -rf "$tree"

  made="$(grep -F "$REWORDED" <<< "$scratch_out" | awk 'NR==1')"
  ran="$(grep -F "$REWORDED" <<< "$direct_out" | awk 'NR==1')"
  [[ "$made" == "countless-under-shared-guard.test.sh$REWORDED" ]] ||
    problems+=("want make test to print 'countless-under-shared-guard.test.sh$REWORDED' once $GUARD_LIB is reworded; it said: $(flat "$scratch_out")")
  [[ "$ran" == "countless-under-shared-guard.test.sh$REWORDED" ]] ||
    problems+=("want run-suite.sh to print 'countless-under-shared-guard.test.sh$REWORDED' once $GUARD_LIB is reworded; it said: $(flat "$direct_out")")
}

probe_one_lib_rewords_both

report "$name"

name="make test over suites that all end in a count line with 0 failed, held to the guard in skills/tdd/scripts/lib/count-line-guard.sh, exits 0 (#617)"
problems=()

probe_all_green_suites_pass() {
  local tree suite
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch tree to hold the green suites, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR" "$tree/skills/tdd/scripts/lib"
  cp "$MAKEFILE" "$tree/Makefile"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
  for suite in first-green.test.sh second-green.test.sh; do
    printf '#!/bin/sh\necho "a case ran"\necho "2 passed, 0 failed"\nexit 0\n' > "$tree/$TESTS_DIR/$suite"
    chmod +x "$tree/$TESTS_DIR/$suite"
  done
  scratch_out="$(make -C "$tree" test 2>&1)" && scratch_code=0 || scratch_code=$?
  rm -rf "$tree"

  [[ "$scratch_code" == 0 ]] ||
    problems+=("want 'make test' to exit 0 over suites that all end in a count line with 0 failed; it exited $scratch_code and said: $(flat "$scratch_out")")
  ! grep -F "$GUARD_MESSAGE" <<< "$scratch_out" > /dev/null ||
    problems+=("want no suite refused for its count line when every one printed it; it said: $(flat "$scratch_out")")
}

probe_all_green_suites_pass

report "$name"

name="run-suite.sh runs a tests/py/test_*.py file under pytest: exit 0 when green, 1 when a case fails"
problems=()

py_tree="$(scratch_dir)"
mkdir -p "$py_tree/tests/py"
printf 'def test_holds():\n    assert 1 + 1 == 2\n' > "$py_tree/tests/py/test_green.py"
printf 'def test_breaks():\n    assert 1 + 1 == 3\n' > "$py_tree/tests/py/test_red.py"

direct "$RUNNER" "$py_tree/tests/py/test_green.py"
[[ "$direct_code" == 0 ]] ||
  problems+=("want exit 0 over a pytest file whose one case is green; got $direct_code, and it said: $(flat "$direct_out")")

direct "$RUNNER" "$py_tree/tests/py/test_red.py"
[[ "$direct_code" == 1 ]] ||
  problems+=("want exit 1 over a pytest file whose one case fails; got $direct_code, and it said: $(flat "$direct_out")")
grep -F 'test_breaks' <<< "$direct_out" > /dev/null ||
  problems+=("want pytest's report naming the failing case test_breaks; it said: $(flat "$direct_out")")

report "$name"

name="run-suite.sh runs a pytest file with \$VERI_VENV's python3, and with the python3 on PATH when that venv has none"
problems=()

python3_stub() {
  printf '#!/bin/sh\n%s\n' "$2" > "$1/python3"
  chmod +x "$1/python3"
}

venv="$(scratch_dir)"
mkdir -p "$venv/bin"
python3_stub "$venv/bin" 'echo "venv python3 $*"
exit 0'
direct env VERI_VENV="$venv" "$RUNNER" "$py_tree/tests/py/test_red.py"
[[ "$direct_code" == 0 && "$direct_out" == "venv python3 -m pytest $py_tree/tests/py/test_red.py" ]] ||
  problems+=("want \$VERI_VENV/bin/python3 to run the file (exit 0, 'venv python3 -m pytest …'); got $direct_code, and it said: $(flat "$direct_out")")

path_bin="$(scratch_dir)"
python3_stub "$path_bin" 'echo "path python3 $*"
exit 0'
direct env VERI_VENV="$(scratch_dir)" PATH="$path_bin:$PATH" "$RUNNER" "$py_tree/tests/py/test_red.py"
[[ "$direct_code" == 0 && "$direct_out" == "path python3 -m pytest $py_tree/tests/py/test_red.py" ]] ||
  problems+=("want the python3 on PATH when \$VERI_VENV has no bin/python3 (exit 0, 'path python3 -m pytest …'); got $direct_code, and it said: $(flat "$direct_out")")

report "$name"

name="run-suite.sh exits 2 over a pytest file when pytest cannot be imported, and when the file does not exist"
problems=()

real_python3="$(source "$ROOT/skills/tdd/scripts/lib/venv-python.sh" && venv_python)"
siteless="$(scratch_dir)"
mkdir -p "$siteless/bin"
python3_stub "$siteless/bin" "exec \"$real_python3\" -S \"\$@\""
direct env VERI_VENV="$siteless" "$RUNNER" "$py_tree/tests/py/test_green.py"
[[ "$direct_code" == 2 ]] ||
  problems+=("want exit 2 when the interpreter cannot import pytest; got $direct_code, and it said: $(flat "$direct_out")")

direct "$RUNNER" "$py_tree/tests/py/test_absent.py"
[[ "$direct_code" == 2 ]] ||
  problems+=("want exit 2 over a tests/py/test_*.py path that does not exist; got $direct_code, and it said: $(flat "$direct_out")")

report "$name"

name="run-suite.sh over a suite that prints its count line on stdout and then a line on stderr exits with the suite's own code, as make test does (#683)"
problems=()

probe_runner_passes_stderr_after_count() {
  local tree probe
  have_runner "so there is no invocation to ask this of" || return
  probe_suite_path stderr-after-count.test.sh || return
  printf '#!/bin/sh\necho "1 passed, 0 failed"\necho "late noise" >&2\nexit 0\n' > "$probe"
  chmod +x "$probe"

  direct "$RUNNER" "$probe"
  [[ "$direct_code" == 0 ]] ||
    problems+=("want exit 0, the suite's own, from the runner over a suite whose stdout ended in its count line before one stderr line; it exited $direct_code and said: $(flat "$direct_out")")
}

probe_runner_passes_stderr_after_count

report "$name"

name="run-suite.sh over a countless suite prints the same two refusal lines make test prints and exits 1 (#683)"
problems=()

probe_runner_names_what_the_countless_suite_left() {
  local tree probe suite want body last_line
  have_runner "so there is no invocation to ask this of" || return
  for body in 'echo "partial"' ':'; do
    suite="countless-$([[ "$body" == ':' ]] && echo empty || echo partial).test.sh"
    probe_suite_path "$suite" || return
    printf '#!/bin/sh\n%s\nexit 0\n' "$body" > "$probe"
    chmod +x "$probe"
    if [[ "$body" == ':' ]]; then
      want="$suite: never reached its count line/$suite: its output was empty"
    else
      want="partial/$suite: never reached its count line/$suite: its last line was: partial"
    fi

    direct "$RUNNER" "$probe"
    [[ "$direct_code" == 1 ]] ||
      problems+=("want exit 1 from the runner over $suite, which exits 0 without its count line; it exited $direct_code and said: $(flat "$direct_out")")
    [[ "$(flat "$direct_out")" == "$want" ]] ||
      problems+=("want the runner over $suite to say exactly '$want'; it said: '$(flat "$direct_out")'")
    rm -rf "$tree"
  done
}

probe_runner_names_what_the_countless_suite_left

report "$name"

name="run-suite.sh with no lib/count-line-guard.sh beside it exits 2 with a stderr line naming that file, and runs no make (#683)"
problems=()

probe_runner_without_guard_lib_refuses_without_make() {
  local tree probe err
  tree="$(scratch_dir)" || {
    problems+=("could not make a scratch directory to stand a runner up in, so the criterion went unasked")
    return 1
  }
  probe="$tree/$GUARDLESS_SUITE_NAME"
  mkdir -p "$tree/skills/tdd/scripts/lib" "$tree/bin"
  cp "$RUNNER" "$tree/skills/tdd/scripts/run-suite.sh"
  cp -R "$ROOT/skills/tdd/scripts/veri" "$tree/skills/tdd/scripts/"
  cp "$ROOT"/skills/tdd/scripts/lib/*.sh "$tree/skills/tdd/scripts/lib/"
  rm "$tree/$GUARD_LIB"
  printf '#!/bin/sh\necho "1 passed, 0 failed"\n' > "$probe"
  cat > "$tree/bin/make" <<MAKE
#!/bin/sh
echo "\$*" >> "$tree/make-ran"
echo "COUNT_LINE='^[0-9]+ passed, [0-9]+ failed\\\$'"
echo "COUNTLESS='%s: never reached its count line\\\\n'"
MAKE
  chmod +x "$probe" "$tree/bin/make"

  err="$tree/stderr"
  PATH="$tree/bin:$PATH" "$tree/skills/tdd/scripts/run-suite.sh" "$probe" > /dev/null 2> "$err" && direct_code=0 || direct_code=$?
  [[ "$direct_code" == 2 ]] ||
    problems+=("want exit 2 from a runner with no lib/count-line-guard.sh beside it; it exited $direct_code and its stderr said: $(flat "$(cat "$err")")")
  grep -F 'lib/count-line-guard.sh' "$err" > /dev/null ||
    problems+=("want a stderr line naming lib/count-line-guard.sh from a runner without it; its stderr said: $(flat "$(cat "$err")")")
  [[ "$(wc -l < "$err" | tr -d ' ')" == 1 ]] ||
    problems+=("want the refusal as the runner's only stderr line, with no shell noise about the missing file; its stderr said: $(flat "$(cat "$err")")")
  [[ ! -e "$tree/make-ran" ]] ||
    problems+=("want no make from a runner with no lib/count-line-guard.sh beside it; it ran: make $(flat "$(cat "$tree/make-ran")")")
}

probe_runner_without_guard_lib_refuses_without_make

report "$name"

name="make has no count-line-guard target to answer: asked for one, it says there is no rule for it (#683)"
problems=()

guard_target_out="$(make -n -C "$ROOT" count-line-guard 2>&1)" && guard_target_code=0 || guard_target_code=$?
[[ "$guard_target_code" != 0 ]] ||
  problems+=("want make to refuse the count-line-guard target as one it has no rule for; it exited 0 and said: $(flat "$guard_target_out")")
grep -F "No rule to make target" <<< "$guard_target_out" > /dev/null ||
  problems+=("want make to say it has no rule for count-line-guard; it exited $guard_target_code and said: $(flat "$guard_target_out")")

report "$name"

finish
