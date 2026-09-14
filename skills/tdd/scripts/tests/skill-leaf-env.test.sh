#!/usr/bin/env bash
# Unit tests for the environment a leaf inherits from the launch lines skills/tdd/SKILL.md
# prescribes. Like skill-timeout.test.sh and skill-test-command.test.sh this suite has no
# script as its subject — it is the procedure document those scripts are called from. Unlike
# them it does not read that document as text: it RUNS the launch lines it finds in it,
# against a stub `claude`, and asks the leaf at the far end what it can see.
# Zero-dependency plain-shell asserts, same idiom as skill-test-command.test.sh.
#
# Why this exists (issue #143): the four documentation targets now refuse when VERI_TEST_CMD
# names a command that is not itself a documentation target (docs-targets-refuse.test.sh),
# and that guard is worth exactly as far as the variable reaches. A leaf that cannot see
# VERI_TEST_CMD is a leaf the guard never fires for — and a leaf is where `make docs` gets
# typed, since CLAUDE.md's "one trap" tells any agent that touched the page to run it. The
# ~5.5 min the #106 conductor spent on a page build inside a run whose test command was
# `make test` is what that costs.
#
# Every Bash call a conductor makes is a fresh shell, so a one-off `export` in preflight
# cannot carry the variable to a launch three steps later: only a prefix on the launch line
# itself can. Whether the prefix is there is not a question about the text, because a prefix
# can be spelled and still not arrive — it travels through `nohup`, `supervise.sh`'s own
# process group and `run-leaf.sh` before anything reads it — so this suite runs the line
# rather than grepping it.
#
# The variable travels in the ENVIRONMENT and not in a prompt, which is what keeps the
# verifier blind: `build-verify-prompt.sh` takes no new argument, so there is still no
# parameter through which the developer's rationale could leak.
#
# Contract under test:
#   Every launch line in SKILL.md that sends a leaf through supervise.sh into run-leaf.sh,
#   run with the document's own variables supplied, gives the `claude` process at the far
#   end VERI_TEST_CMD carrying the run's test command.
#
# Run: skills/tdd/scripts/tests/skill-leaf-env.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root, and
# one up is the scripts directory the document calls `$S`.
ROOT="$(cd "$HERE/../../../.." && pwd)"
SCRIPTS="$(cd "$HERE/.." && pwd)"

# The document under test, twice: the path as every failure message quotes it, and the same
# path resolved for the probe to read. Both spellings come from one constant, so a message
# can never name a file the probe did not open.
skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which launch line is missing the variable rather than just that one is.
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

# problem <complaint> — record one launch line that failed the case. Every such message has
# the same three parts, and they are here rather than at each call site so the three cannot
# drift apart: where the line is, what is wrong with it, and the line itself **as the
# document spells it**, so a reader can find the text by searching for what the message
# quoted, and what they fix is the document rather than the probe's substituted copy.
# `lineno` and `line` are `scan_launches`'s, the way `problems` above is `report`'s.
problem() {
  problems+=("$skill_md:$lineno $1:$line")
}

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
stub="$WORK/stub"       # the fake `claude` every launch below ends in
run="$WORK/run"         # one tree per launch line, named for its leaf
mkdir -p "$stub" "$run"

# The test command this probe stands in for the conductor's. A command with a space in it,
# so a launch line that carries the value unquoted is caught here rather than in a real run,
# and one no recipe in this repository answers to, so nothing it reaches could act on it.
SENTINEL='make sentinel-test-cmd'

# The leaf, as far as run-leaf.sh can tell. Into the file its own launch names in `SEEN` it
# records the one thing this suite asks about — what VERI_TEST_CMD says in the leaf's own
# environment, or `<unset>` when it says nothing — and then emits the minimal stream-json for
# extract-result.sh to find a result in, the same shape run-leaf.test.sh's stub emits.
cat > "$stub/claude" <<'STUB'
#!/usr/bin/env bash
printf '%s\n' "${VERI_TEST_CMD-<unset>}" > "$SEEN"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
chmod +x "$stub/claude"

# launched_test_cmd <leaf> <launch-line> <file>... — run one launch line to completion in a
# tree of its own and echo what VERI_TEST_CMD said inside the leaf, or `<no leaf ran>` when
# the line never reached one. Both cases below ask that one question, of the two launch
# shapes the document prescribes, so both come through here.
#
# The `<file>` arguments are what the tree must hold before the line can run, and they are
# the only thing the two shapes differ in: a developer launch names its own prompt file,
# while a verifier launch names the **spec** and the **test path** and lets verify.sh build
# the prompt from them. Each is created relative to the launch's tree; the stub reads none of
# them, so the content only says which fixture a reader is looking at.
#
# `$S` is supplied the way the document supplies it — as a variable in the launching shell
# (SKILL.md:61) — rather than substituted into the text, so the line is run as written.
# `CLAUDE_BIN` is how run-leaf.sh's own header says a test swaps the binary, and it has to
# come from here for the same reason the variable under test does: it can only reach the
# leaf by being inherited.
#
# `env -u VERI_TEST_CMD` is the load-bearing part. Once this issue lands, every `make test`
# of veri's own repository runs inside a development run and therefore already has the
# variable in its environment — so a leaf inheriting it from this suite's own caller would
# answer the question for a launch line that carries no prefix at all. A suite's answer must
# be a fact about the thing under test, not about the shell that ran it (#87).
#
# The supervisor's windows are shrunk the way supervise.test.sh shrinks them, so nothing
# here waits on wall time; retries are pinned off because a stub leaf that failed to record
# anything should be reported, not run again.
launched_test_cmd() {
  local leaf="$1" line="$2"
  shift 2
  local dir="$run/$leaf"
  # What this launch's leaf saw, in the tree that launch ran in rather than in one file every
  # run rewrites — so each answer keeps the tree that produced it. Cleared first because two
  # launch lines naming the same leaf share a tree, and the second reaching no leaf at all
  # would otherwise be answered with the first one's file.
  local seen="$dir/seen"
  mkdir -p "$dir/.tdd"
  rm -f "$seen"
  local file
  for file in "$@"; do
    printf 'the %s this launch names, which the stub never reads\n' "$file" > "$dir/$file"
  done
  # The line ends in `&` — it is launched detached — so `wait` on the next line is what
  # makes this probe foreground: without it the tree would be read while the leaf still ran.
  ( cd "$dir" && env -u VERI_TEST_CMD S="$SCRIPTS" CLAUDE_BIN="$stub/claude" SEEN="$seen" \
      VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.2 \
      bash -c "$line
wait" ) >/dev/null 2>&1
  cat "$seen" 2>/dev/null || echo '<no leaf ran>'
}

# runnable <line> — echo one launch line as a conductor types it, with the document's
# placeholders supplied; or echo nothing and return 1 when the line names one this probe
# cannot supply.
#
# Two spellings of the same launch are kept apart on purpose, and this is where the second
# one is made: the caller's `line` is what the document says, and is what every message
# quotes, while what comes back from here is the runnable copy. The substitutions are one
# table rather than one per case because a conductor supplies all of them from one place —
# the run's test command, the phase and revise attempt that name one revise leaf, the issue
# number, and the test under review with its target test id — and either launch shape is
# free to name any of them.
#
# The refusal is the load-bearing half. An unsubstituted `<…>` would be read by the shell as
# a redirection, so a case that ran it would go green while answering about nothing; the
# caller reports the line instead. `[target]` is the revise loop's spelling of an argument
# that is optional there, and is supplied the same way. The target test id is one word
# because the document leaves it unquoted, so a value with a space in it would arrive as two
# arguments and the probe would be testing its own fixture.
runnable() {
  local launch="$1"
  launch="${launch//<test-cmd>/$SENTINEL}"
  launch="${launch//<phase>/red}"
  launch="${launch//<k>/1}"
  launch="${launch//<n>/143}"
  launch="${launch//<test-path>/probe.test.sh}"
  launch="${launch//<target-test-id>/probe-target}"
  launch="${launch//\[target\]/probe-target}"
  [[ "$launch" != *'<'*'>'* ]] || return 1
  printf '%s\n' "$launch"
}

# scan_launches <pattern> <missing> <check> — find every launch line in the document matching
# <pattern> and hand each runnable one, substituted, to the shell function named <check>,
# which asks of it whatever its case is about. <missing> is the complaint recorded when the
# document holds no matching line at all, since a case that silently examined nothing would
# otherwise pass while asserting about no launch.
#
# Both cases scan the same way and differ only in what they then ask, so the scan is written
# once. Two halves of it are easy to lose in a copy and quiet when lost: the numbered-grep
# split into the `lineno` and `line` that every failure message quotes, and `runnable`'s
# refusal, without which an unsubstituted `<…>` reaches the shell as a redirection and the case
# goes green having run nothing. `lineno` and `line` are declared here and `problem` reads them
# from the check, which bash allows — a function sees the locals of the function that called
# it — so they stay out of the global scope the two cases share.
scan_launches() {
  local pattern="$1" missing="$2" check="$3"
  local lines numbered lineno line launch
  lines="$(grep -nE "$pattern" "$md")"
  if [[ -z "$lines" ]]; then
    problems+=("$missing")
    return
  fi
  while IFS= read -r numbered; do
    [[ -n "$numbered" ]] || continue
    lineno="${numbered%%:*}"
    line="${numbered#*:}"
    launch="$(runnable "$line")" || {
      problem "names a placeholder this probe cannot supply, so its launch could not be run"
      continue
    }
    "$check" "$launch"
  done <<< "$lines"
}

# 1. The criterion, asked of every launch line the document actually prescribes. One case,
#    because it is one wiring: the same prefix on each line, and a line that lost it is a
#    phase of the run whose leaf can type `make docs` unrefused.
#
#    The lines are found by what they do rather than by which section they sit in — a line
#    running supervise.sh over run-leaf.sh is a line a conductor copies as it stands. The
#    generic shape at the head of the document (`supervise.sh <name> <cmd> [args...]`,
#    SKILL.md:212) is deliberately not among them: it names no command to launch, so there
#    is nothing to run and nothing a leaf could see.
name="every leaf $skill_md launches through supervise.sh sees the run's test command as VERI_TEST_CMD"
problems=()

# The two fields the probe reads out of a developer launch: the leaf's name, which is also the
# tree the launch runs in and how a failure names itself, and the prompt file the leaf is
# pointed at. Both are read from the substituted copy, since a leaf named `revise-<phase>-<k>`
# in the document is `revise-red-1` when it runs.
check_developer_launch() {
  local launch="$1" leaf prompt got
  leaf="$(sed -E 's/.*supervise\.sh +([^ ]+).*/\1/' <<< "$launch")"
  prompt="$(grep -oE '\.tdd/[A-Za-z0-9_.-]+\.prompt' <<< "$launch" | head -1)"
  if [[ -z "$prompt" ]]; then
    problem "launches $leaf with no .tdd/<name>.prompt file to run, so its leaf could not be started"
    return
  fi
  got="$(launched_test_cmd "$leaf" "$launch" "$prompt")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
}

scan_launches '\$S/supervise\.sh .*run-leaf\.sh' \
  "$skill_md has no line launching a leaf through supervise.sh into run-leaf.sh — the launch this case is about could not be found" \
  check_developer_launch
report "$name"

# 2. The same criterion, asked of the verifier launches. A verifier is a leaf too — `claude
#    -p` in a tree, denied Write and Edit but free to run commands — so `make docs` is as
#    typeable there as in a developer leaf, and a guard the documentation targets carry is
#    worth nothing in a process that cannot see the variable it reads. It is a second case
#    rather than more lines in the first because it is a second wiring: the prefix goes on a
#    `nohup bash -c "…"` whose command is verify.sh, and the variable then has one more
#    process to cross — verify.sh itself — before supervise.sh and run-leaf.sh carry it the
#    rest of the way.
#
#    The variable still travels in the ENVIRONMENT, so `build-verify-prompt.sh` keeps the
#    four parameters it has and the verifier stays blind: there is still no argument through
#    which the developer's rationale could reach it.
#
#    The lines are found by what they do, the way case 1 finds its own: a detached launch of
#    verify.sh naming the spec file it judges against is a line a conductor copies as it
#    stands. The shape at the head of the document (SKILL.md:237) spells its arguments as an
#    ellipsis rather than naming a spec, so — like the generic `supervise.sh` shape above —
#    there is nothing there to run and no leaf that could see anything.
name="every verifier $skill_md launches through verify.sh sees the run's test command as VERI_TEST_CMD"
problems=()

# The phase is verify.sh's first argument, and `verify-<phase>` is both the leaf's name and the
# tree this launch runs in — read from the substituted copy, since the revise loop's line says
# `<phase>` where a run says `red`. The two files named are spelled as `runnable`'s table
# spells them, so the tree holds the spec and the test the line is about to hand verify.sh.
check_verifier_launch() {
  local launch="$1" leaf got
  leaf="verify-$(sed -E 's/.*verify\.sh +([^ ]+).*/\1/' <<< "$launch")"
  got="$(launched_test_cmd "$leaf" "$launch" ".tdd/issue-143-spec.md" "probe.test.sh")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
}

scan_launches 'nohup .*\$S/verify\.sh .*\.tdd/issue-<n>-spec\.md' \
  "$skill_md has no line launching a verifier through verify.sh against a spec file — the launch this case is about could not be found" \
  check_verifier_launch
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
