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
# `lineno` and `line` are the loop's, the way `problems` above is `report`'s.
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

# launched_test_cmd <launch-line> <prompt-file> <leaf> — run one launch line to completion
# in a tree of its own and echo what VERI_TEST_CMD said inside the leaf, or `<no leaf ran>`
# when the line never reached one.
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
  local line="$1" prompt="$2" dir="$run/$3"
  # What this launch's leaf saw, in the tree that launch ran in rather than in one file every
  # run rewrites — so each answer keeps the tree that produced it. Cleared first because two
  # launch lines naming the same leaf share a tree, and the second reaching no leaf at all
  # would otherwise be answered with the first one's file.
  local seen="$dir/seen"
  mkdir -p "$dir/.tdd"
  rm -f "$seen"
  printf 'a prompt this stub never reads\n' > "$dir/$prompt"
  # The line ends in `&` — it is launched detached — so `wait` on the next line is what
  # makes this probe foreground: without it the tree would be read while the leaf still ran.
  ( cd "$dir" && env -u VERI_TEST_CMD S="$SCRIPTS" CLAUDE_BIN="$stub/claude" SEEN="$seen" \
      VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.2 \
      bash -c "$line
wait" ) >/dev/null 2>&1
  cat "$seen" 2>/dev/null || echo '<no leaf ran>'
}

# verifier_test_cmd <launch-line> <leaf> — the same probe for a verifier launch, which
# differs from the one above in what the tree has to hold before the line can run. A
# developer launch names its own prompt file, so the probe writes that; a verifier launch
# names the **spec** and the **test path** instead, and verify.sh builds the prompt from
# them, so the probe writes those two and lets verify.sh name the prompt. Everything else —
# the stub, the shrunk windows, and `env -u VERI_TEST_CMD` for the reason spelled at
# `launched_test_cmd` — is the same, because the question is the same.
verifier_test_cmd() {
  local line="$1" dir="$run/$2"
  local seen="$dir/seen"
  mkdir -p "$dir/.tdd"
  rm -f "$seen"
  printf 'a spec this stub never reads\n' > "$dir/.tdd/issue-143-spec.md"
  printf 'a test this stub never runs\n' > "$dir/probe.test.sh"
  ( cd "$dir" && env -u VERI_TEST_CMD S="$SCRIPTS" CLAUDE_BIN="$stub/claude" SEEN="$seen" \
      VERI_STUCK_RETRIES=0 VERI_HEARTBEAT=30 VERI_TIMEOUT=60 VERI_POLL=0.2 \
      bash -c "$line
wait" ) >/dev/null 2>&1
  cat "$seen" 2>/dev/null || echo '<no leaf ran>'
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

launch_lines="$(grep -nE '\$S/supervise\.sh .*run-leaf\.sh' "$md")"
[[ -n "$launch_lines" ]] ||
  problems+=("$skill_md has no line launching a leaf through supervise.sh into run-leaf.sh — the launch this case is about could not be found")

while IFS= read -r numbered; do
  [[ -n "$numbered" ]] || continue
  lineno="${numbered%%:*}"
  line="${numbered#*:}"
  # Two spellings of the same launch, kept apart on purpose: `line` is what the document
  # says, and is what every message quotes; `launch` is the runnable copy, with the
  # document's placeholders supplied as a conductor supplies them — the run's test command,
  # and the phase and revise attempt that name one revise leaf. Any other placeholder is
  # reported rather than run — an unsubstituted `<…>` would be read by the shell as a
  # redirection, and a case that went green on that would be answering about nothing.
  launch="${line//<test-cmd>/$SENTINEL}"
  launch="${launch//<phase>/red}"
  launch="${launch//<k>/1}"
  if [[ "$launch" == *'<'*'>'* ]]; then
    problem "names a placeholder this probe cannot supply, so its launch could not be run"
    continue
  fi
  # The two fields the probe reads out of a launch it has established is runnable: the
  # leaf's name, which is also the tree the launch runs in and how a failure names itself,
  # and the prompt file the leaf is pointed at. Both are read from the substituted copy,
  # since a leaf named `revise-<phase>-<k>` in the document is `revise-red-1` when it runs.
  leaf="$(sed -E 's/.*supervise\.sh +([^ ]+).*/\1/' <<< "$launch")"
  prompt="$(grep -oE '\.tdd/[A-Za-z0-9_.-]+\.prompt' <<< "$launch" | head -1)"
  if [[ -z "$prompt" ]]; then
    problem "launches $leaf with no .tdd/<name>.prompt file to run, so its leaf could not be started"
    continue
  fi
  got="$(launched_test_cmd "$launch" "$prompt" "$leaf")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
done <<< "$launch_lines"
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

verify_lines="$(grep -nE 'nohup .*\$S/verify\.sh .*\.tdd/issue-<n>-spec\.md' "$md")"
[[ -n "$verify_lines" ]] ||
  problems+=("$skill_md has no line launching a verifier through verify.sh against a spec file — the launch this case is about could not be found")

while IFS= read -r numbered; do
  [[ -n "$numbered" ]] || continue
  lineno="${numbered%%:*}"
  line="${numbered#*:}"
  # Two spellings again, for the reason given at case 1: `line` is what the document says
  # and what every message quotes, `launch` is the runnable copy with the placeholders a
  # conductor supplies — the run's test command, the issue number, the test under review and
  # the target test id, which the revise loop's line writes as `[target]` because there it is
  # optional. The id is one word because the document leaves it unquoted, so a value with a
  # space in it would arrive as two arguments and the probe would be testing its own fixture.
  launch="${line//<test-cmd>/$SENTINEL}"
  launch="${launch//<phase>/red}"
  launch="${launch//<n>/143}"
  launch="${launch//<test-path>/probe.test.sh}"
  launch="${launch//<target-test-id>/probe-target}"
  launch="${launch//\[target\]/probe-target}"
  if [[ "$launch" == *'<'*'>'* ]]; then
    problem "names a placeholder this probe cannot supply, so its launch could not be run"
    continue
  fi
  # The phase is verify.sh's first argument, and `verify-<phase>` is both the leaf's name and
  # the tree this launch runs in — read from the substituted copy, since the revise loop's
  # line says `<phase>` where a run says `red`.
  leaf="verify-$(sed -E 's/.*verify\.sh +([^ ]+).*/\1/' <<< "$launch")"
  got="$(verifier_test_cmd "$launch" "$leaf")"
  [[ "$got" == "$SENTINEL" ]] ||
    problem "launches $leaf, whose leaf saw VERI_TEST_CMD=$got, want $SENTINEL"
done <<< "$verify_lines"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
