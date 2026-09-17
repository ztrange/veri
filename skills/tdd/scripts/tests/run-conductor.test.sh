#!/usr/bin/env bash
# Tests for scripts/run-conductor.sh — the CONDUCTOR invocation, driven against a stub
# `claude` on PATH (no real subprocess, no model call), the way run-leaf.test.sh drives the
# leaf one. Same stub, same seam: `CLAUDE_BIN` swaps the binary and the stub records its
# argv to $ARGV_OUT and its stdin to $PROMPT_OUT — and refuses an argv the binary would.
#
# Why a conductor is launched this way at all — the ~25,000 tokens of interactive harness
# surface it never touches, and why the stream flags are part of the criterion rather than a
# detail of how it is spelled — is run-conductor.sh's own header, which this suite does not
# restate.
#
# Contract under test (this step only):
#   `run-conductor.sh <issue>` launches the conductor binary in print mode — `-p` — with
#   `--output-format stream-json --verbose` and `--permission-mode bypassPermissions`, and
#   the issue it was asked for reaches the prompt that launch carries; the child it launches
#   inherits none of the parent session's eight handles while still inheriting every `VERI_*`
#   tunable; and whatever status that child exits with is the status the script exits with.
#
# The two halves of that second sentence are one criterion and not two: the severing is done
# by editing the environment the child is given, so a script that drops the handles by
# handing the child a scrubbed environment and one that drops them by handing it an empty one
# are indistinguishable until something asks what survived. `VERI_MODEL_VERIFIER` is what
# asks.
#
# Not asked here: what SKILL.md says about the two launch modes. That is a later step.
#
# Run: scripts/tests/run-conductor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CONDUCTOR="$HERE/../run-conductor.sh"
pass=0 fail=0

# The issue asked for. A number nothing else in an argv would carry, so a probe that finds
# it has found the one this script was given and not a version, a budget or a port.
issue=4242

stubdir="$(mktemp -d)"
work="$(mktemp -d)"
trap 'rm -rf "$stubdir" "$work"' EXIT

# The stub `claude`: parses its argv the way the binary does and dies on an option it does
# not know, then records its argv one argument per line to $ARGV_OUT and whatever arrives on
# stdin to $PROMPT_OUT, emits a minimal stream-json stream, and exits with $STUB_EXIT — 0
# unless a case asks for another status, which is the seam the exit-forwarding case below
# drives. Same shape as run-leaf.test.sh's, plus the option parsing case 4 is the reason for:
# a stub that accepts an argv the binary would reject makes an argv-shape bug invisible, so
# the strictness is the stub's and every case gets it rather than case 4 alone. Stdin is
# drained in every case, not only the ones that probe it: a prompt nobody reads fills the
# pipe and stalls the writer.
cat > "$stubdir/claude" <<'STUB'
#!/usr/bin/env bash
# A word beginning with a dash is an option, and an unknown one is fatal. Everything that is
# not an option is left alone, so a value like `stream-json` still passes.
for arg in "$@"; do
  case "$arg" in
    -p|--verbose|--output-format|--permission-mode) ;;
    -*) echo "error: unknown option '$arg'" >&2; exit 1 ;;
  esac
done
printf '%s\n' "$@" > "$ARGV_OUT"
cat > "${PROMPT_OUT:-/dev/null}"
[[ -n "${ENV_OUT:-}" ]] && env > "$ENV_OUT"
[[ -n "${BASE_OUT:-}" ]] && cp -R "$(sed -n 's/^Base directory for this skill: //p' "$PROMPT_OUT" | head -n 1)/." "$BASE_OUT"
[[ -n "${CONDUCTOR_HOOK:-}" ]] && "$CONDUCTOR_HOOK" "$(sed -n 's/^Base directory for this skill: //p' "$PROMPT_OUT" | head -n 1)"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit "${STUB_EXIT:-0}"
STUB
chmod +x "$stubdir/claude"

argv="$work/argv"
prompt="$work/prompt"
launch_err="$work/launch.err"

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output names the flag that is missing rather than just saying the launch was wrong.
# Same helper, same shape, as hermetic-suites.test.sh's.
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

# flag <name> — the launch carried <name> as an argument of its own. Whole lines, because
# the stub writes one argument per line: a substring match would accept `--verbose` found
# inside a prompt that merely mentions it.
flag() {
  grep -qx -- "$1" "$argv" ||
    problems+=("the launch does not carry $1")
}

# valued <flag> <value> — <flag> was passed with <value> as the argument right after it,
# which is what `claude` reads and what a bare `grep` for the two words separately cannot
# tell from them landing at opposite ends of the command line.
valued() {
  grep -A1 -x -- "$1" "$argv" | grep -qx -- "$2" ||
    problems+=("the launch does not carry $1 $2")
}

# prompt_base — the base directory the last launch's prompt handed the conductor, or
# nothing when the prompt names none.
prompt_base() {
  sed -n 's/^Base directory for this skill: //p' "$prompt" 2>/dev/null | head -n 1
}

# differing_files <expected> <copy> — the files under <expected>, one path per line, that
# <copy> does not hold byte for byte. Fails when <expected> cannot be entered.
differing_files() {
  (cd "$1" && find . -type f | while read -r f; do
    cmp -s "$f" "$2/$f" || echo "$f"; done)
}

# holds_skill <base> <expected> <what> <detail> — <base>, the directory a launch was handed,
# holds a skill, and it is <expected>'s files byte for byte; <what> names the launch and
# <detail> the commit in the problem recorded otherwise.
holds_skill() {
  if [[ ! -f "$1/SKILL.md" ]]; then
    problems+=("the $3 base directory held no skill while the conductor ran: $4")
  else
    diff_out="$(differing_files "$2" "$1")"
    [[ -z "$diff_out" ]] ||
      problems+=("the $3 base directory differs from $4: ${diff_out//$'\n'/ }")
  fi
}

# repin_in <log> <commit> — exit 0 when the event log <log> holds a `skill-repin` line naming
# <commit>; exit 1 when it holds none, or cannot be read.
repin_in() {
  python3 - "$1" "$2" <<'PY'
import json, sys
try:
    lines = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
except OSError:
    sys.exit(1)
sys.exit(0 if any(l.get("event") == "skill-repin" and sys.argv[2] in l.values()
                  for l in lines) else 1)
PY
}

# skill_clone <dir> — a git clone at <dir> holding this skill under skills/tdd, committed
# once: the fixture a snapshot case launches run-conductor.sh from, so the skill commit it
# resolves is one the case controls. Prints nothing; read the commit with rev-parse.
skill_clone() {
  mkdir -p "$1/skills"
  cp -R "$HERE/../.." "$1/skills/tdd"
  git -C "$1" init -q
  git -C "$1" add -A
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm skill
}

# cloned_skill <remote> <clone> — a skill_clone at <remote> and a plain `git clone` of it at
# <clone>: a clone with an `origin`, which is what makes a launch fetch before it pins.
cloned_skill() {
  skill_clone "$1"
  git clone -q "$1" "$2"
}

# advance_clone <clone> <line> — a second skill commit on <clone>, appending <line> to its
# supervise.sh: the clone moving under a run, so the commit a launch pins is no longer HEAD.
advance_clone() {
  echo "$2" >> "$1/skills/tdd/scripts/supervise.sh"
  git -C "$1" -c user.name=t -c user.email=t@t commit -qam pulled
}

# launch_from <caller> <clone> [VAR=value…] — run <clone>'s run-conductor.sh for the issue from
# inside <caller>, against the stub, with any extra VAR=value in its environment: the one way
# every snapshot case launches, so the cases differ only in what they add. The launch's stderr
# lands in $launch_err, and its exit status is the function's.
launch_from() {
  local caller="$1" clone="$2"
  shift 2
  ( cd "$caller" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$argv" PROMPT_OUT="$prompt" "$@" \
      "$clone/skills/tdd/scripts/run-conductor.sh" "$issue" ) >/dev/null 2>"$launch_err"
}

# caller_repo <dir> — an empty git repository at <dir>: the checkout a snapshot case launches
# run-conductor.sh from, whose `.tdd/` holds the run state the launch records.
caller_repo() {
  mkdir -p "$1"
  git -C "$1" init -q
}

# skill_archive <clone> <commit> <dir> — <commit>'s skills/tdd, extracted under <dir>, so
# <dir>/skills/tdd is what a snapshot of that commit must hold file for file.
skill_archive() {
  mkdir -p "$3"
  git -C "$1" archive "$2" skills/tdd | tar -x -C "$3"
}

# 1. The criterion: one conductor, launched as `claude -p` for the issue, streaming events.
name="run-conductor.sh <issue> launches claude -p for that issue in stream-json"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" PROMPT_OUT="$prompt" \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

# Fail closed: no argv file means the stub was never reached, so every probe below would be
# reading a file that does not exist and reporting four problems for one. One says it.
if [[ ! -f "$argv" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no argv")
else
  flag -p
  valued --output-format stream-json
  flag --verbose
  # The prompt travels on stdin, not argv — case 4 is why — so the issue is looked for where
  # it now goes.
  grep -q -- "$issue" "$prompt" 2>/dev/null ||
    problems+=("issue $issue does not reach the prompt the launch carries")
fi

report "$name"

# The eight handles a nested `claude` would otherwise inherit from the session that launched
# it — the messaging socket and token most of all, which wire a second session into the
# first one's IPC channel. Each carries the value it is set to, because the list that sets
# them and the list that then looks for them gone must be the same list: a name set here but
# probed under a second spelling is a probe that passes having watched nothing.
handles=(
  CLAUDECODE=1
  CLAUDE_CODE_SESSION_ID=parent-session
  CLAUDE_CODE_HOST_SESSION_ID=parent-host-session
  CLAUDE_CODE_MESSAGING_SOCKET=/tmp/parent.sock
  CLAUDE_CODE_MESSAGING_TOKEN=parent-token
  CLAUDE_PID=4141
  CLAUDE_CODE_CHILD_SESSION=1
  CLAUDE_CODE_ENTRYPOINT=cli
)

envfile="$work/env"

# 2. The environment the child is handed: the session handles severed, the tunables intact.
name="the launch severs the eight session handles and passes VERI_* through"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$envfile" \
    "${handles[@]}" \
    VERI_MODEL_VERIFIER=probe-verifier-model \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$envfile" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no environment")
else
  for handle in "${handles[@]}"; do
    grep -q "^${handle%%=*}=" "$envfile" &&
      problems+=("${handle%%=*} is still in the child's environment")
  done
  grep -qx -- 'VERI_MODEL_VERIFIER=probe-verifier-model' "$envfile" ||
    problems+=("VERI_MODEL_VERIFIER did not reach the child's environment")
fi

report "$name"

# 3. The status: a conductor that died is a conductor the caller must be able to see died,
# so the child's status is the script's and not a status the script invents. 17 because it is
# neither 0 nor one of the four codes this repository's scripts speak, so a script that
# forwards it cannot be a script that happens to produce the same number some other way.
name="a non-zero child exit is the script's exit"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" STUB_EXIT=17 \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1
status=$?

[[ "$status" -eq 17 ]] ||
  problems+=("the script exited $status, not the child's 17")

report "$name"

# 4. The procedure's first line is the frontmatter fence `---`, and to a real `claude` a
# word beginning with a dash is an option, not a prompt: the launch dies on `unknown option`
# before a conductor exists. The stub parses options for that reason, so a procedure passed
# by argv makes this case's launch exit non-zero the way the binary's does; what is left to
# ask is whether the whole procedure arrived anyway.
name="a frontmatter-fenced procedure launches and reaches the binary whole"
problems=()

# The procedure compared against is the SKILL.md in the directory the launch was handed, not
# the one beside this script: the run pins origin/<default>'s commit (#251), so a working
# tree whose SKILL.md differs from that commit — any branch that edits it — would otherwise
# fail here for a launch that handed over its own procedure whole.
handed="$work/handed-skill"
rm -rf "$prompt" "$handed"
mkdir -p "$handed"
SKILL="$handed/SKILL.md"

( cd "$work" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$argv" PROMPT_OUT="$prompt" \
    BASE_OUT="$handed" "$CONDUCTOR" "$issue" ) >/dev/null 2>&1
status=$?

if [[ "$status" -ne 0 ]]; then
  problems+=("the launch exited $status — the binary rejected the procedure it was handed")
elif [[ ! -f "$prompt" ]]; then
  problems+=("the launch started but no procedure reached the binary")
elif [[ ! -f "$SKILL" ]]; then
  problems+=("the directory the launch was handed holds no SKILL.md")
elif ! IFS= read -r fence < "$SKILL" || [[ "$fence" != "---" ]]; then
  problems+=("the procedure handed over does not open with the frontmatter fence this case is about")
elif [[ "$(cat "$prompt")" != "$(cat "$SKILL")"* ]]; then
  # Verbatim-prefix, compared as text rather than by taking the procedure's first N lines
  # off the front of what arrived: a line count is a size, and #202 forbids any suite here
  # from applying a size verb to SKILL.md. The tail the prefix leaves is the issue line,
  # which case 1 is the one that asserts on.
  problems+=("what reached the binary does not begin with $SKILL verbatim")
fi

report "$name"

# 5. Print mode has nobody to approve a tool call, so without this flag the `gh`, the `make`
# and the nested `claude` a conductor needs are all denied and it is a process that can read
# but cannot act. Asserted as a flag-with-value rather than as two words found anywhere,
# because `--permission-mode` reads whatever argument follows it: the pair landing at
# opposite ends of the command line is a different launch from this one.
name="the launch carries --permission-mode bypassPermissions"
problems=()

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$argv" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no argv")
else
  valued --permission-mode bypassPermissions
fi

report "$name"

# 6. The run pins its skill (issue #237). A conductor in print mode is not handed a base
# directory by a harness, so it is handed one in its prompt, in the harness's own words —
# `Base directory for this skill: …` — which is the phrase SKILL.md tells it to read `S` from.
# The fixture is a clone of this skill with one committed state and one uncommitted edit on
# top: a base directory that is the clone's own `skills/tdd` fails the first probe, and one
# that is a copy of the working tree rather than of the commit fails the second, on the edit.
name="the conductor's base directory is a snapshot of the skill commit, not the clone"
problems=()

clone="$work/clone"
skill_clone "$clone"
commit="$(git -C "$clone" rev-parse HEAD)"
echo "# uncommitted edit after the skill commit" >> "$clone/skills/tdd/scripts/supervise.sh"

committed="$work/committed"
skill_archive "$clone" "$commit" "$committed"

caller="$work/caller"
caller_repo "$caller"
rm -f "$prompt"
# The snapshot is the launch's to remove once the conductor returns, so its files are copied
# out by the stub while the conductor is still running, and compared from that copy.
live="$work/live-base"
mkdir -p "$live"

launch_from "$caller" "$clone" BASE_OUT="$live"

base="$(prompt_base)"
if [[ -z "$base" ]]; then
  problems+=("the prompt names no 'Base directory for this skill: <dir>' line")
elif [[ "$(cd "$base" 2>/dev/null && pwd -P)" == "$(cd "$clone/skills/tdd" && pwd -P)" ]]; then
  problems+=("the base directory is the clone's own skills/tdd: $base")
elif ! diff_out="$(differing_files "$committed/skills/tdd" "$live")" || [[ -n "$diff_out" ]]; then
  problems+=("the base directory's files differ from skill commit $commit: ${diff_out//$'\n'/ }")
elif [[ -e "$base" ]]; then
  problems+=("the snapshot is still on disk after the launch returned: $base")
fi

report "$name"

# 7. The pin holds for what a leaf executes, not only for what the conductor is told. While
# the conductor is running, the hook sabotages the clone the skill was launched from — its
# supervise.sh replaced by one that exits 42, its run-leaf.sh deleted, its develop-red
# template rewritten — and only then launches a leaf the way SKILL.md does, from the base
# directory's scripts: the prompt built by build-develop-prompt.sh, the leaf run by
# supervise.sh over run-leaf.sh. A leaf that runs, and is handed the committed template
# rather than the rewritten one, is a leaf that read none of the three from the clone.
name="a leaf launched mid-run executes the snapshot's supervise.sh, run-leaf.sh and template, not the clone's"
problems=()

clone2="$work/clone2"
skill_clone "$clone2"

leafdir="$work/leaf"
mkdir -p "$leafdir"
echo "spec" > "$leafdir/spec.md"

# The leaf's own `claude`: records the prompt it is handed with `-p` and emits a result.
cat > "$stubdir/leaf-claude" <<'STUB'
#!/usr/bin/env bash
while [[ $# -gt 0 ]]; do
  [[ "$1" == "-p" ]] && { printf '%s\n' "$2" > "$LEAF_PROMPT_OUT"; shift; }
  shift
done
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
chmod +x "$stubdir/leaf-claude"

cat > "$stubdir/hook" <<HOOK
#!/usr/bin/env bash
base="\$1"
src="$clone2/skills/tdd/scripts"
printf '#!/usr/bin/env bash\necho SABOTAGED; exit 42\n' > "\$src/supervise.sh"
rm -f "\$src/run-leaf.sh"
echo "SABOTAGED-TEMPLATE" > "\$src/prompts/develop-red.md"
cd "$leafdir" || exit 1
"\$base/scripts/build-develop-prompt.sh" red spec.md "the step" "make test" > leaf.prompt 2> build.err
env CLAUDE_BIN="$stubdir/leaf-claude" LEAF_PROMPT_OUT="$leafdir/leaf-received" \
  "\$base/scripts/supervise.sh" develop-red "\$base/scripts/run-leaf.sh" leaf.prompt > supervise.out 2> supervise.err
echo \$? > supervise.rc
HOOK
chmod +x "$stubdir/hook"

# A caller of its own: the shared one already holds a pin from case 6's clone, which clone2
# cannot resolve, and a resume over an unresolvable pin refuses (issue #253).
caller2="$work/caller2"
caller_repo "$caller2"
launch_from "$caller2" "$clone2" CONDUCTOR_HOOK="$stubdir/hook"

leaf_rc="$(cat "$leafdir/supervise.rc" 2>/dev/null)"
if [[ -z "$leaf_rc" ]]; then
  problems+=("the conductor never launched a leaf — no supervise.rc in $leafdir")
else
  [[ "$leaf_rc" == 0 ]] ||
    problems+=("the leaf launch through the base directory's supervise.sh exited $leaf_rc, not 0")
  if [[ ! -f "$leafdir/leaf-received" ]]; then
    problems+=("the leaf never received a prompt")
  else
    grep -q 'SABOTAGED-TEMPLATE' "$leafdir/leaf-received" &&
      problems+=("the leaf was handed the clone's rewritten develop-red template")
    grep -q '## Phase: develop-red' "$leafdir/leaf-received" ||
      problems+=("the leaf's prompt is not built from the committed develop-red template")
  fi
fi

report "$name"

# 8. A resume keeps its pin. The issue is launched once from a clone at commit A, then the
# clone moves to commit B — a `git pull` in another thread, as far as the run can tell — and
# the same issue is launched again from the same caller, which is a resume of that run. The
# first launch's snapshot is gone by then (the launch removes it on exit), so the second
# launch has to re-materialise one, and it has to be A's: a base directory holding B's
# supervise.sh is a resume that took the new skill as a side effect of the pull.
name="a resume of the run is handed a re-materialised snapshot of the recorded commit, not the clone's new HEAD"
problems=()

clone3="$work/clone3"
skill_clone "$clone3"
recorded="$(git -C "$clone3" rev-parse HEAD)"

pinned="$work/pinned"
skill_archive "$clone3" "$recorded" "$pinned"

caller3="$work/caller3"
caller_repo "$caller3"

first_base="$work/first-base"
mkdir -p "$first_base"
launch_from "$caller3" "$clone3" BASE_OUT="$first_base"
first_snapshot="$(prompt_base)"

advance_clone "$clone3" "# a commit pulled into the clone after the run started"

resumed_base="$work/resumed-base"
mkdir -p "$resumed_base"
rm -f "$prompt"
launch_from "$caller3" "$clone3" BASE_OUT="$resumed_base"

base="$(prompt_base)"
if [[ -z "$base" ]]; then
  problems+=("the resumed launch's prompt names no 'Base directory for this skill: <dir>' line")
elif [[ -n "$first_snapshot" && -e "$first_snapshot" ]]; then
  problems+=("the first launch's snapshot was never removed, so nothing was re-materialised: $first_snapshot")
else
  holds_skill "$resumed_base" "$pinned/skills/tdd" "resumed launch's" "recorded skill commit $recorded"
fi

report "$name"

# 9. Taking the new skill is an explicit act, and a recorded one. The run is launched from a
# clone at commit A, the clone moves to commit B, and the same issue is launched again with
# VERI_NEW_SKILL=1 — the operator asking for the new skill on this resume. That launch is
# handed B's files, not the recorded A's, and the caller's event log carries a `skill-repin`
# line naming B: a re-pin nobody can find in the log is the side effect the pin exists to stop.
name="a resume with VERI_NEW_SKILL=1 is re-pinned to the clone's current commit and logs a skill-repin event"
problems=()

clone4="$work/clone4"
skill_clone "$clone4"

caller4="$work/caller4"
caller_repo "$caller4"

launch_from "$caller4" "$clone4"

advance_clone "$clone4" "# a commit the operator asks the run to take"
current="$(git -C "$clone4" rev-parse HEAD)"

taken="$work/taken"
skill_archive "$clone4" "$current" "$taken"

repinned_base="$work/repinned-base"
mkdir -p "$repinned_base"
rm -f "$prompt"
launch_from "$caller4" "$clone4" BASE_OUT="$repinned_base" VERI_NEW_SKILL=1

holds_skill "$repinned_base" "$taken/skills/tdd" "re-pinned launch's" "current skill commit $current"

repin_in "$caller4/.tdd/events.jsonl" "$current" ||
  problems+=("no skill-repin event naming $current in $caller4/.tdd/events.jsonl")

report "$name"

# 10. A skill that is not in a git clone has no commit to pin. The run still proceeds, from
# the skill directory as it is, and says so on stderr: an unpinned run nobody was told about is
# the silent drift the pin exists to end. GIT_CEILING_DIRECTORIES stops git from finding a
# repository above the fixture, so "no resolvable commit" does not depend on where the
# scratch directory happens to live.
name="with no resolvable skill commit the run proceeds unpinned and warns on stderr"
problems=()

loose="$work/loose"
mkdir -p "$loose/skills"
cp -R "$HERE/../.." "$loose/skills/tdd"
rm -f "$prompt"

launch_from "$caller" "$loose" GIT_CEILING_DIRECTORIES="$work"
status=$?

base="$(prompt_base)"
if [[ "$status" -ne 0 ]]; then
  problems+=("the unpinned launch exited $status, not 0: $(cat "$launch_err")")
elif [[ "$(cd "$base" 2>/dev/null && pwd -P)" != "$(cd "$loose/skills/tdd" && pwd -P)" ]]; then
  problems+=("the unpinned run's base directory is not the skill directory itself: '$base'")
elif ! grep -qi 'unpinned' "$launch_err"; then
  problems+=("no warning on stderr that the run is unpinned — stderr was: '$(cat "$launch_err")'")
fi

report "$name"

# 11. The snapshot is run state, and run state is ignored. The caller is a checkout with one
# commit and nothing else, so `git status --porcelain` there is empty before the launch; the
# clone the skill is launched from is the same. Both are asked while the conductor is still
# running — the snapshot and the recorded commit exist then, whatever the launch removes on
# exit — and again once it has returned. Any line either prints is something the pin left
# behind in a tree a later `git add -A` would sweep up.
name="the snapshot leaves git status --porcelain empty in the caller's checkout and in the skill clone"
problems=()

clone5="$work/clone5"
skill_clone "$clone5"

caller5="$work/caller5"
caller_repo "$caller5"
echo "target" > "$caller5/README"
git -C "$caller5" add -A
git -C "$caller5" -c user.name=t -c user.email=t@t commit -qm target

statusdir="$work/status5"
mkdir -p "$statusdir"

cat > "$stubdir/status-hook" <<HOOK
#!/usr/bin/env bash
git -C "$caller5" status --porcelain > "$statusdir/caller-\${STATUS_WHEN:-during}" 2>&1
git -C "$clone5" status --porcelain > "$statusdir/clone-\${STATUS_WHEN:-during}" 2>&1
HOOK
chmod +x "$stubdir/status-hook"

launch_from "$caller5" "$clone5" CONDUCTOR_HOOK="$stubdir/status-hook"
STATUS_WHEN=after "$stubdir/status-hook"

if [[ ! -f "$statusdir/caller-during" ]]; then
  problems+=("the conductor never ran — no status was taken while it was running")
else
  for when in during after; do
    for tree in caller clone; do
      out="$(cat "$statusdir/$tree-$when")"
      [[ -z "$out" ]] ||
        problems+=("git status --porcelain in the $tree is not empty $when the run: ${out//$'\n'/ }")
    done
  done
fi

report "$name"

# 12. The pin is origin's tip, not the clone's HEAD (issue #251). The skill's clone is cut
# from a remote at commit A, then the remote moves to commit B — a PR landing on the default
# branch — and nobody pulls the clone. A launch from that clone is handed B's files: the
# base directory holding A's supervise.sh is a run executing a skill the remote has already
# replaced, which is the 50-commits-behind primary this issue was filed over.
name="a launch from a clone behind origin/<default> is handed a snapshot of origin's tip"
problems=()

remote6="$work/remote6"
clone6="$work/clone6"
cloned_skill "$remote6" "$clone6"
advance_clone "$remote6" "# a commit that landed on the remote after the clone was cut"
tip="$(git -C "$remote6" rev-parse HEAD)"

tipdir="$work/tip6"
skill_archive "$remote6" "$tip" "$tipdir"

caller6="$work/caller6"
caller_repo "$caller6"

tip_base="$work/tip-base"
mkdir -p "$tip_base"
rm -f "$prompt"
launch_from "$caller6" "$clone6" BASE_OUT="$tip_base"

holds_skill "$tip_base" "$tipdir/skills/tdd" "launch's" "origin's tip $tip: $(cat "$launch_err")"

report "$name"

# 13. Reaching origin's tip never moves the clone (issue #251). The clone is the primary other
# live runs share, so the launch that pins origin's tip must not get there by pulling or
# checking out: the clone is left behind the remote, on its branch, with an uncommitted edit
# to a file the remote's new commit does not touch — so a fast-forward pull would succeed and
# move HEAD rather than refusing — and its HEAD, branch and working tree are read before the
# launch and again after it.
name="a launch leaves the skill clone's HEAD, branch and working tree unchanged"
problems=()

remote7="$work/remote7"
clone7="$work/clone7"
cloned_skill "$remote7" "$clone7"
advance_clone "$remote7" "# a commit that landed on the remote after the clone was cut"
echo "# an uncommitted edit in the clone" >> "$clone7/skills/tdd/SKILL.md"

# clone_state <clone> — the clone's HEAD commit, its branch, its porcelain status and the
# bytes of every file it tracks as they sit in the working tree, one block.
clone_state() {
  git -C "$1" rev-parse HEAD
  git -C "$1" symbolic-ref -q HEAD || echo "detached"
  git -C "$1" status --porcelain
  git -C "$1" ls-files -z | (cd "$1" && xargs -0 cksum)
}

before7="$(clone_state "$clone7")"

caller7="$work/caller7"
caller_repo "$caller7"

rm -f "$argv"
launch_from "$caller7" "$clone7"

if [[ ! -f "$argv" ]]; then
  problems+=("the conductor was never launched: $(cat "$launch_err")")
else
  after7="$(clone_state "$clone7")"
  [[ "$after7" == "$before7" ]] ||
    problems+=("the clone changed across the launch: $(diff <(echo "$before7") <(echo "$after7") | grep '^[<>]' | tr '\n' ' ')")
fi

report "$name"

# 14. A fetch that fails is a launch that fails (issue #251). The clone's origin is a path
# that no longer holds a repository — a remote nobody can reach — so the tip the pin needs
# cannot be learned. The launch exits 2 without starting a conductor, and says on stderr that
# it was the fetch that failed: falling back to the clone's HEAD would be a run on a stale
# skill that nobody was told about, which is the defect this issue exists to end.
name="a failed fetch of origin exits 2 before any conductor is launched and names the fetch on stderr"
problems=()

remote8="$work/remote8"
clone8="$work/clone8"
cloned_skill "$remote8" "$clone8"
rm -rf "$remote8"

caller8="$work/caller8"
caller_repo "$caller8"

rm -f "$argv"
launch_from "$caller8" "$clone8"
status=$?

[[ "$status" -eq 2 ]] ||
  problems+=("the launch exited $status, not 2")
[[ ! -f "$argv" ]] ||
  problems+=("a conductor was launched although the fetch failed")
grep -qi 'fetch' "$launch_err" ||
  problems+=("stderr does not name the fetch — stderr was: '$(cat "$launch_err")'")

report "$name"

# 15. The pin is on the record (issue #251). The clone is behind a remote that moved, so the
# commit the run pinned is origin's tip and not the clone's HEAD. While the conductor runs, the
# hook does what a conductor does from its base directory — writes a mark through event.sh and
# launches a leaf through supervise.sh — in the caller's checkout; every line either writes to
# `.tdd/events.jsonl` must carry the tip as `skill_commit`, and the prompt the conductor was
# handed must name the tip for its plan comment. A sha asked of the snapshot's own git is no
# answer: the snapshot has none, so it reads empty or `unknown` rather than the commit pinned.
name="every event a launched run writes carries origin's tip as skill_commit, and the prompt names it"
problems=()

remote9="$work/remote9"
clone9="$work/clone9"
cloned_skill "$remote9" "$clone9"
advance_clone "$remote9" "# a commit that landed on the remote after the clone was cut"
tip9="$(git -C "$remote9" rev-parse HEAD)"

caller9="$work/caller9"
caller_repo "$caller9"

cat > "$stubdir/record-hook" <<HOOK
#!/usr/bin/env bash
base="\$1"
cd "$caller9" || exit 1
"\$base/scripts/event.sh" conductor-mark
"\$base/scripts/supervise.sh" develop-red echo ok > /dev/null 2>&1
HOOK
chmod +x "$stubdir/record-hook"

rm -f "$prompt"
# Launched with no VERI_SKILL_COMMIT of its own, so the sha a line carries is the one the launch
# put there and not one inherited from whatever session runs this suite.
( unset VERI_SKILL_COMMIT; launch_from "$caller9" "$clone9" CONDUCTOR_HOOK="$stubdir/record-hook" )

if [[ ! -s "$caller9/.tdd/events.jsonl" ]]; then
  problems+=("the run wrote no events: $(cat "$launch_err")")
else
  wrong="$(python3 - "$caller9/.tdd/events.jsonl" "$tip9" <<'PY'
import json, sys
for l in open(sys.argv[1]):
    if l.strip():
        e = json.loads(l)
        if e.get("skill_commit") != sys.argv[2]:
            print("%s=%r" % (e.get("event"), e.get("skill_commit")))
PY
)"
  [[ -z "$wrong" ]] ||
    problems+=("events whose skill_commit is not origin's tip $tip9: ${wrong//$'\n'/ }")
fi
grep -q -- "$tip9" "$prompt" 2>/dev/null ||
  problems+=("the conductor's prompt does not name the pinned skill commit $tip9")

report "$name"

# 16. A resume keeps its pin when origin moves (issue #251). The run is first launched from a
# clone whose origin is at commit A, so A is the pin recorded. Then the remote moves to B — a
# PR landing between the two launches — and the same issue is launched again from the same
# caller. That launch fetches and sees B as origin's tip, and must still be handed A's files
# and name A in its prompt: a resume that follows origin's tip is a run whose skill changed
# mid-run without anyone asking for it.
name="a resumed run keeps its recorded pin when origin/<default> has moved since the first launch"
problems=()

remote10="$work/remote10"
clone10="$work/clone10"
cloned_skill "$remote10" "$clone10"
first10="$(git -C "$remote10" rev-parse HEAD)"

pinned10="$work/pinned10"
skill_archive "$remote10" "$first10" "$pinned10"

caller10="$work/caller10"
caller_repo "$caller10"

launch_from "$caller10" "$clone10"

advance_clone "$remote10" "# a commit that landed on the remote after the run started"
moved10="$(git -C "$remote10" rev-parse HEAD)"

resumed10="$work/resumed10"
mkdir -p "$resumed10"
rm -f "$prompt"
launch_from "$caller10" "$clone10" BASE_OUT="$resumed10"

if [[ -z "$(prompt_base)" ]]; then
  problems+=("the resumed launch's prompt names no base directory: $(cat "$launch_err")")
else
  holds_skill "$resumed10" "$pinned10/skills/tdd" "resumed launch's" "recorded pin $first10 (origin moved to $moved10)"
  grep -q -- "$first10" "$prompt" ||
    problems+=("the resumed launch's prompt does not name the recorded pin $first10")
fi

report "$name"

# 17. Asking for the new skill takes origin's tip, not the clone's HEAD (issue #251). The run is
# first launched from a clone whose origin is at commit A. Then the remote moves to B — a PR
# landing — while the clone moves to a commit C of its own that origin never saw, so the two
# answers a re-pin could give are different files. The same issue is launched again with
# VERI_NEW_SKILL=1, and that launch must be handed B's files and name B in its prompt: a re-pin
# to the clone's HEAD is the operator asking for the new skill and getting a stale one.
name="a resume with VERI_NEW_SKILL=1 re-pins to origin/<default> as just fetched, not to the clone's HEAD"
problems=()

remote11="$work/remote11"
clone11="$work/clone11"
cloned_skill "$remote11" "$clone11"

caller11="$work/caller11"
caller_repo "$caller11"

launch_from "$caller11" "$clone11"

advance_clone "$remote11" "# a commit that landed on the remote after the run started"
tip11="$(git -C "$remote11" rev-parse HEAD)"
advance_clone "$clone11" "# a commit of the clone's own that origin never saw"
head11="$(git -C "$clone11" rev-parse HEAD)"

tipdir11="$work/tip11"
skill_archive "$remote11" "$tip11" "$tipdir11"

repinned11="$work/repinned11"
mkdir -p "$repinned11"
rm -f "$prompt"
launch_from "$caller11" "$clone11" BASE_OUT="$repinned11" VERI_NEW_SKILL=1

if [[ -z "$(prompt_base)" ]]; then
  problems+=("the re-pinned launch's prompt names no base directory: $(cat "$launch_err")")
else
  holds_skill "$repinned11" "$tipdir11/skills/tdd" "re-pinned launch's" "origin's tip $tip11 (clone HEAD $head11)"
  grep -q -- "$tip11" "$prompt" ||
    problems+=("the re-pinned launch's prompt does not name origin's tip $tip11")
fi

report "$name"

# 18. A recorded pin this clone cannot resolve is not a licence to re-pin (issue #253). The run
# is launched once, then its record is made to name a commit from another repository — what a
# second clone, a shallow one or a pruned branch looks like to `git cat-file -e`. A plain resume
# must refuse with exit 2 before any conductor exists; the same resume with VERI_NEW_SKILL=1 is
# the operator taking the new skill, and is re-pinned to HEAD with a `skill-repin` event naming
# it. Both logs a run may write are read, because which one holds the line is a later step's.
name="an unresolvable recorded skill commit refuses with exit 2 unless VERI_NEW_SKILL=1, which re-pins and logs a skill-repin event"
problems=()

clone12="$work/clone12"
skill_clone "$clone12"
head12="$(git -C "$clone12" rev-parse HEAD)"

foreign12="$work/foreign12"
caller_repo "$foreign12"
git -C "$foreign12" -c user.name=t -c user.email=t@t commit -q --allow-empty -m elsewhere
missing12="$(git -C "$foreign12" rev-parse HEAD)"

caller12="$work/caller12"
caller_repo "$caller12"
launch_from "$caller12" "$clone12"

printf '%s\n' "$missing12" > "$caller12/.tdd/issue-$issue-skill-commit"
rm -f "$argv"
launch_from "$caller12" "$clone12"
rc12=$?
[[ "$rc12" == 2 ]] ||
  problems+=("the launch without VERI_NEW_SKILL=1 exited $rc12, not 2")
[[ ! -f "$argv" ]] ||
  problems+=("the conductor was launched anyway over unresolvable recorded commit $missing12")

printf '%s\n' "$missing12" > "$caller12/.tdd/issue-$issue-skill-commit"
rm -f "$argv"
launch_from "$caller12" "$clone12" VERI_NEW_SKILL=1
rc12=$?
[[ "$rc12" == 0 ]] ||
  problems+=("the launch with VERI_NEW_SKILL=1 exited $rc12, not 0: $(cat "$launch_err")")
grep -qx -- "$head12" "$caller12/.tdd/issue-$issue-skill-commit" ||
  problems+=("the launch with VERI_NEW_SKILL=1 did not record HEAD $head12 as the pin")

repin_in "$caller12/.tdd/events.jsonl" "$head12" ||
  repin_in "$caller12/.tdd/wt/$issue/.tdd/events.jsonl" "$head12" ||
  problems+=("no skill-repin event naming $head12 in the run's event log")

report "$name"

# 19. The re-pin is logged where the run's other events are (issue #253). A re-pin is a resume,
# so the run's worktree `.tdd/wt/<n>` already exists; the `skill-repin` line must land in that
# worktree's `.tdd/events.jsonl` — the log metrics.sh reads — and not in the log of the
# directory the operator happened to launch from, which no reader of the run ever opens.
name="the skill-repin event lands in the run worktree's .tdd/wt/<n>/.tdd/events.jsonl, never the caller's .tdd/events.jsonl"
problems=()

clone13="$work/clone13"
skill_clone "$clone13"

caller13="$work/caller13"
caller_repo "$caller13"
launch_from "$caller13" "$clone13"

advance_clone "$clone13" "# a commit the operator asks the run to take"
head13="$(git -C "$clone13" rev-parse HEAD)"

mkdir -p "$caller13/.tdd/wt/$issue"
launch_from "$caller13" "$clone13" VERI_NEW_SKILL=1

wt_log13="$caller13/.tdd/wt/$issue/.tdd/events.jsonl"
caller_log13="$caller13/.tdd/events.jsonl"

repin_in "$wt_log13" "$head13" ||
  problems+=("no skill-repin event naming $head13 in the run worktree's $wt_log13")
if repin_in "$caller_log13" "$head13"; then
  problems+=("the skill-repin event landed in the caller's $caller_log13")
fi

report "$name"

# 20. The unpinned case reaches the conductor, and the plan comment says so (issue #253). A run
# with no resolvable skill commit warns on stderr, but stderr is the operator's terminal, not the
# thread a run is read back from: the conductor must be told in its environment — the one channel
# every process of the run inherits — as VERI_SKILL_UNPINNED=1, and SKILL.md's plan-comment step
# (2.3, the `### 🗺️ Plan` item) must name that variable, so the comment that names a pinned
# commit says "unpinned" instead of naming none. Launched with no VERI_SKILL_UNPINNED of its own,
# so a value the child holds is one the launch put there.
name="an unpinned launch hands the conductor VERI_SKILL_UNPINNED=1, and SKILL.md's plan-comment step names it"
problems=()

loose14="$work/loose14"
mkdir -p "$loose14/skills"
cp -R "$HERE/../.." "$loose14/skills/tdd"
env14="$work/env14"
rm -f "$env14"

( unset VERI_SKILL_UNPINNED; launch_from "$caller" "$loose14" GIT_CEILING_DIRECTORIES="$work" ENV_OUT="$env14" )

if [[ ! -f "$env14" ]]; then
  problems+=("the unpinned launch never reached the conductor: $(cat "$launch_err")")
elif ! grep -qx 'VERI_SKILL_UNPINNED=1' "$env14"; then
  problems+=("the unpinned launch handed the conductor no VERI_SKILL_UNPINNED=1 in its environment")
fi

plan_step14="$(awk '/^3\. \*\*Mirror the plan\*\*/ {on=1} on && /^$/ {exit} on' "$HERE/../../SKILL.md")"
if [[ -z "$plan_step14" ]]; then
  problems+=("SKILL.md has no plan-comment step (2.3, **Mirror the plan**) to read")
elif ! grep -q 'VERI_SKILL_UNPINNED' <<< "$plan_step14"; then
  problems+=("SKILL.md's plan-comment step (2.3) does not name VERI_SKILL_UNPINNED")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
