#!/usr/bin/env bash
# Tests for scripts/run-conductor.sh — the conductor invocation, driven against a stub
# `claude` that records its argv to $ARGV_OUT and its stdin to $PROMPT_OUT.
#
# Contract under test:
#   `run-conductor.sh <issue>` launches the conductor binary in print mode — `-p` — with
#   `--output-format stream-json --verbose` and `--permission-mode bypassPermissions`, and
#   the issue it was asked for reaches the prompt that launch carries; the child it launches
#   inherits none of the parent session's eight handles while still inheriting every `VERI_*`
#   tunable; and whatever status that child exits with is the status the script exits with.
#
# Run: scripts/tests/run-conductor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"

issue=4242

stubdir="$(scratch_dir)"
work="$(scratch_dir)"

claude_stub "$stubdir" "$(cat <<'STUB'
for arg in "$@"; do
  case "$arg" in
    -p|--verbose|--output-format|--permission-mode) ;;
    -*) echo "error: unknown option '$arg'" >&2; exit 1 ;;
  esac
done
printf '%s\n' "$@" > "$ARGV_OUT"
cat > "${PROMPT_OUT:-/dev/null}"
[ -n "${ENV_OUT:-}" ] && env > "$ENV_OUT"
if [ -n "${BASE_OUT:-}" ] || [ -n "${CONDUCTOR_HOOK:-}" ]; then
  base="$(sed -n 's/^Base directory for this skill: //p' "${PROMPT_OUT:-/dev/null}" 2>/dev/null | head -n 1)"
  [ -n "$base" ] && [ -d "$base" ] || { echo "stub: the prompt names no base directory" >&2; exit 2; }
fi
[ -n "${BASE_OUT:-}" ] && cp -R "$base/." "$BASE_OUT"
[ -n "${CONDUCTOR_HOOK:-}" ] && "$CONDUCTOR_HOOK" "$base"
printf '%s\n' '{"type":"system","subtype":"init","session_id":"x"}'
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
exit "${STUB_EXIT:-0}"
STUB
)"

argv="$work/argv"
prompt="$work/prompt"
launch_err="$work/launch.err"

flag() {
  grep -qx -- "$1" "$argv" ||
    problems+=("the launch does not carry $1")
}

valued() {
  grep -qx -- "$2" < <(grep -A1 -x -- "$1" "$argv") ||
    problems+=("the launch does not carry $1 $2")
}

prompt_base() {
  head -n 1 < <(sed -n 's/^Base directory for this skill: //p' "$prompt" 2>/dev/null)
}

differing_files() {
  local expected="$1" copy="$2" exp_manifest cop_manifest out
  exp_manifest="$(cd "$expected" && find . -type f -print0 | xargs -0 cksum | sort)" || return 1
  cop_manifest="$(cd "$copy" 2>/dev/null && find . -type f -print0 | xargs -0 cksum | sort)"
  out="$(diff <(printf '%s\n' "$exp_manifest") <(printf '%s\n' "$cop_manifest") |
    grep '^< ' | sed -E 's/^< [0-9]+ [0-9]+ //')"
  printf '%s\n' "$out"
}

holds_skill() {
  if [[ ! -f "$1/SKILL.md" ]]; then
    problems+=("the $3 base directory held no skill while the conductor ran: $4")
  else
    diff_out="$(differing_files "$2" "$1")"
    [[ -z "$diff_out" ]] ||
      problems+=("the $3 base directory differs from $4: ${diff_out//$'\n'/ }")
  fi
}

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

loose_skill() {
  mkdir -p "$1/skills"
  cp -R "$HERE/../.." "$1/skills/tdd"
}

base_clone=""
skill_clone() {
  if [[ -z "$base_clone" ]]; then
    base_clone="$work/base-clone"
    loose_skill "$base_clone"
    commit_once "$base_clone"
  fi
  cp -R "$base_clone/." "$1"
}

commit_once() {
  new_repo "$1"
  git -C "$1" add -A
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm skill
}

cloned_skill() {
  skill_clone "$1"
  git clone -q "$1" "$2"
}

advance_clone() {
  echo "$2" >> "$1/skills/tdd/scripts/supervise.sh"
  git -C "$1" -c user.name=t -c user.email=t@t commit -qam pulled
}

launch_from() {
  local caller="$1" clone="$2"
  shift 2
  ( unset VERI_NEW_SKILL; cd "$caller" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$argv" PROMPT_OUT="$prompt" "$@" \
      "$clone/skills/tdd/scripts/run-conductor.sh" "$issue" ) >/dev/null 2>"$launch_err"
}

caller_repo() {
  mkdir -p "$1"
  new_repo "$1"
}

skill_archive() {
  mkdir -p "$3"
  git -C "$1" archive "$2" skills/tdd | tar -x -C "$3"
}

tree_clone() {
  local root prefix
  root="$(cd "$HERE/../.." && git rev-parse --show-toplevel)"
  prefix="$(cd "$HERE/../.." && git rev-parse --show-prefix)"
  mkdir -p "$1"
  git -C "$root" archive --prefix=skills/tdd/ "HEAD:$prefix" | tar -x -C "$1"
  commit_once "$1"
  cp -R "$HERE/../../." "$1/skills/tdd"
}

tree_clone "$work/tree"
CONDUCTOR="$work/tree/skills/tdd/scripts/run-conductor.sh"

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


assert_case1() {
  local conductor="$1"

  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" PROMPT_OUT="$prompt" \
      "$conductor" "$issue" ) >/dev/null 2>&1

  if [[ ! -f "$argv" ]]; then
    problems+=("the conductor binary was never launched — $conductor recorded no argv")
  else
    flag -p
    valued --output-format stream-json
    flag --verbose
    grep -q -- "$issue" "$prompt" 2>/dev/null ||
      problems+=("issue $issue does not reach the prompt the launch carries")
  fi
}

assert_case2() {
  local conductor="$1"

  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$envfile" \
      "${handles[@]}" \
      VERI_MODEL_VERIFIER=probe-verifier-model \
      "$conductor" "$issue" ) >/dev/null 2>&1

  if [[ ! -f "$envfile" ]]; then
    problems+=("the conductor binary was never launched — $conductor recorded no environment")
  else
    for handle in "${handles[@]}"; do
      grep -q "^${handle%%=*}=" "$envfile" &&
        problems+=("${handle%%=*} is still in the child's environment")
    done
    grep -qx -- 'VERI_MODEL_VERIFIER=probe-verifier-model' "$envfile" ||
      problems+=("VERI_MODEL_VERIFIER did not reach the child's environment")
  fi
}

assert_case3() {
  local conductor="$1" status

  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" STUB_EXIT=17 \
      "$conductor" "$issue" ) >/dev/null 2>&1
  status=$?

  [[ "$status" -eq 17 ]] ||
    problems+=("the script exited $status, not the child's 17")
}

assert_case4() {
  local conductor="$1" status cwd
  local handed="$work/handed-skill"
  rm -rf "$prompt" "$handed"
  mkdir -p "$handed"
  local SKILL="$handed/SKILL.md"
  cwd="$(scratch_dir)"

  ( cd "$cwd" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$argv" PROMPT_OUT="$prompt" \
      BASE_OUT="$handed" "$conductor" "$issue" ) >/dev/null 2>&1
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
    problems+=("what reached the binary does not begin with $SKILL verbatim")
  fi
}

assert_case5() {
  local conductor="$1"

  ( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
      "$conductor" "$issue" ) >/dev/null 2>&1

  if [[ ! -f "$argv" ]]; then
    problems+=("the conductor binary was never launched — $conductor recorded no argv")
  else
    valued --permission-mode bypassPermissions
  fi
}

name="run-conductor.sh <issue> launches claude -p for that issue in stream-json"
problems=()
assert_case1 "$CONDUCTOR"
report "$name"

name="the launch severs the eight session handles and passes VERI_* through"
problems=()
assert_case2 "$CONDUCTOR"
report "$name"

name="a non-zero child exit is the script's exit"
problems=()
assert_case3 "$CONDUCTOR"
report "$name"

name="a frontmatter-fenced procedure launches and reaches the binary whole"
problems=()
assert_case4 "$CONDUCTOR"
report "$name"

name="the launch carries --permission-mode bypassPermissions"
problems=()
assert_case5 "$CONDUCTOR"
report "$name"

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

name="a leaf launched mid-run executes the snapshot's supervise.sh, run-leaf.sh and template, not the clone's"
problems=()

clone2="$work/clone2"
skill_clone "$clone2"

leafdir="$work/leaf"
mkdir -p "$leafdir"
echo "spec" > "$leafdir/spec.md"

cat > "$stubdir/leaf-claude" <<'STUB'
#!/bin/sh
while [ "$#" -gt 0 ]; do
  [ "$1" = "-p" ] && { printf '%s\n' "$2" > "$LEAF_PROMPT_OUT"; shift; }
  shift
done
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
chmod +x "$stubdir/leaf-claude"

cat > "$stubdir/hook" <<HOOK
#!/bin/sh
base="\$1"
src="$clone2/skills/tdd/scripts"
printf '#!/usr/bin/env bash\necho SABOTAGED; exit 42\n' > "\$src/supervise.sh"
rm -f "\$src/run-leaf.sh"
echo "SABOTAGED-TEMPLATE" > "\$src/prompts/develop-red.md"
cd "$leafdir" || exit 1
"\$base/scripts/build-develop-prompt.sh" red spec.md "the step" "make test" > leaf.prompt 2> build.err
env CLAUDE_BIN="$stubdir/leaf-claude" LEAF_PROMPT_OUT="$leafdir/leaf-received" VERI_POLL=0.02 \
  "\$base/scripts/supervise.sh" develop-red "\$base/scripts/run-leaf.sh" leaf.prompt > supervise.out 2> supervise.err
echo \$? > supervise.rc
HOOK
chmod +x "$stubdir/hook"

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

repin_in "$caller4/.tdd/wt/$issue/.tdd/events.jsonl" "$current" ||
  problems+=("no skill-repin event naming $current in $caller4/.tdd/wt/$issue/.tdd/events.jsonl")

report "$name"

name="with no resolvable skill commit the run proceeds unpinned and warns on stderr"
problems=()

loose="$work/loose"
loose_skill "$loose"
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
#!/bin/sh
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

name="a launch leaves the skill clone's HEAD, branch and working tree unchanged"
problems=()

remote7="$work/remote7"
clone7="$work/clone7"
cloned_skill "$remote7" "$clone7"
advance_clone "$remote7" "# a commit that landed on the remote after the clone was cut"
echo "# an uncommitted edit in the clone" >> "$clone7/skills/tdd/SKILL.md"

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

name="a failed fetch of origin exits 2 before any conductor is launched and names the fetch on stderr"
problems=()

remote8="$work/remote8"
clone8="$work/clone8"
skill_clone "$clone8"
new_repo --bare "$remote8"
git -C "$clone8" remote add origin "$remote8"
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
#!/bin/sh
base="\$1"
cd "$caller9" || exit 1
"\$base/scripts/event.sh" conductor-mark
VERI_POLL=0.02 "\$base/scripts/supervise.sh" develop-red echo ok > /dev/null 2>&1
HOOK
chmod +x "$stubdir/record-hook"

rm -f "$prompt"
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

name="an unpinned launch hands the conductor VERI_SKILL_UNPINNED=1, and SKILL.md's plan-comment step names it"
problems=()

loose14="$work/loose14"
loose_skill "$loose14"
env14="$work/env14"
rm -f "$env14"

( unset VERI_SKILL_UNPINNED; launch_from "$caller" "$loose14" GIT_CEILING_DIRECTORIES="$work" ENV_OUT="$env14" )

if [[ ! -f "$env14" ]]; then
  problems+=("the unpinned launch never reached the conductor: $(cat "$launch_err")")
elif ! grep -qx 'VERI_SKILL_UNPINNED=1' "$env14"; then
  problems+=("the unpinned launch handed the conductor no VERI_SKILL_UNPINNED=1 in its environment")
fi

plan_step14="$(awk '/^[0-9]+\. \*\*Mirror the plan\*\*/ {on=1} on && /^$/ {exit} on' "$HERE/../../SKILL.md")"
if [[ -z "$plan_step14" ]]; then
  problems+=("SKILL.md has no plan-comment step (2.4, **Mirror the plan**) to read")
elif ! grep -q 'VERI_SKILL_UNPINNED' <<< "$plan_step14"; then
  problems+=("SKILL.md's plan-comment step (2.4) does not name VERI_SKILL_UNPINNED")
fi

report "$name"

name="case 4 passes with an uncommitted edit to SKILL.md in the tree under test"
problems=()

clone21="$work/clone21"
skill_clone "$clone21"
echo "uncommitted edit to the procedure" >> "$clone21/skills/tdd/SKILL.md"

assert_case4 "$clone21/skills/tdd/scripts/run-conductor.sh"

report "$name"

name="case 4 fails when what reaches the binary differs from the committed SKILL.md"
problems=()

clone22="$work/clone22"
skill_clone "$clone22"
skill22="$clone22/skills/tdd/SKILL.md"
{ echo "uncommitted edit to the procedure"; cat "$skill22"; } > "$work/skill22.edited"
cat "$work/skill22.edited" > "$skill22"

conductor22="$clone22/skills/tdd/scripts/run-conductor.sh"
sed 's|^skill_file="\$base/SKILL.md"$|skill_file="$HERE/../SKILL.md"|' "$conductor22" \
  > "$work/conductor22.edited"
cat "$work/conductor22.edited" > "$conductor22"

if ! grep -qx 'skill_file="$HERE/../SKILL.md"' "$conductor22"; then
  problems+=("the clone's run-conductor.sh could not be made to read the working tree's SKILL.md")
else
  assert_case4 "$conductor22"
  case4_problems=("${problems[@]}")
  problems=()
  if [[ "${#case4_problems[@]}" -eq 0 ]]; then
    problems+=("case 4 did not fail when the binary got an edited SKILL.md")
  elif [[ "${#case4_problems[@]}" -ne 1 || "${case4_problems[0]}" != *"does not begin with"*"SKILL.md verbatim"* ]]; then
    problems+=("case 4 failed, but not on the comparison: ${case4_problems[*]}")
  fi
fi

report "$name"

name="cases 1-5 pass when the checkout under test has an unreachable origin"
problems=()

clone23="$work/clone23"
skill_clone "$clone23"
git -C "$clone23" remote add origin "https://127.0.0.1:1/veri.git"

suite23="$clone23/skills/tdd/scripts/tests/cases1-5-only.test.sh"
awk '/^name=/ && ++n == 6 {exit} 1' "$clone23/skills/tdd/scripts/tests/run-conductor.test.sh" > "$suite23"
printf '%s\n' 'echo "----"' 'echo "${pass:-0} passed, $fail failed"' '[[ "$fail" -eq 0 ]]' >> "$suite23"
chmod +x "$suite23"

if [[ "$(grep -c '^name=' "$suite23")" -ne 5 ]]; then
  problems+=("cases 1-5 could not be cut out of the clone's run-conductor.test.sh")
else
  out23="$(GIT_TERMINAL_PROMPT=0 "$suite23" 2>&1)"
  [[ "$(tail -n 1 <<< "$out23")" == "5 passed, 0 failed" ]] ||
    problems+=("cases 1-5 did not all pass with origin unreachable: ${out23//$'\n'/ | }")
fi

report "$name"

name="a re-pinning launch with VERI_NEW_SKILL=1 hands the conductor no VERI_NEW_SKILL"
problems=()

clone24="$work/clone24"
skill_clone "$clone24"

caller24="$work/caller24"
caller_repo "$caller24"

launch_from "$caller24" "$clone24"

advance_clone "$clone24" "# a commit the operator asks the run to take"
current24="$(git -C "$clone24" rev-parse HEAD)"

env24="$work/env24"
rm -f "$env24"
launch_from "$caller24" "$clone24" ENV_OUT="$env24" VERI_NEW_SKILL=1

if ! repin_in "$caller24/.tdd/wt/$issue/.tdd/events.jsonl" "$current24"; then
  problems+=("the launch with VERI_NEW_SKILL=1 did not re-pin to $current24: $(cat "$launch_err")")
elif [[ ! -f "$env24" ]]; then
  problems+=("the re-pinning launch never reached the conductor: $(cat "$launch_err")")
elif grep -q '^VERI_NEW_SKILL=' "$env24"; then
  problems+=("the re-pinning launch handed the conductor $(grep '^VERI_NEW_SKILL=' "$env24") in its environment")
fi

report "$name"

name="each phase's leaf is launched with its tier: red and refactor affected, green, verify-green and verify-refactor fast+affected"
problems=()

clone25="$work/clone25"
skill_clone "$clone25"

tiers="$work/tiers25"
mkdir -p "$tiers"
echo "spec" > "$tiers/spec.md"
fast25="make FAST-TIER-7781"
all25="make ALL-TIER-7781"

cat > "$stubdir/tier-claude" <<'STUB'
#!/bin/sh
while [ "$#" -gt 0 ]; do
  [ "$1" = "-p" ] && { printf '%s\n' "$2" > "$LEAF_PROMPT_OUT"; shift; }
  shift
done
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"VERDICT: PASS\nREASON: ok"}'
STUB
chmod +x "$stubdir/tier-claude"

cat > "$stubdir/hook25" <<HOOK
#!/bin/sh
S="\$1/scripts"
cd "$tiers" || exit 1
leaf() { # leaf <name> <command…> — run <command…> against the stub, its prompt to <name>.received
  n="\$1"; shift
  env CLAUDE_BIN="$stubdir/tier-claude" LEAF_PROMPT_OUT="$tiers/\$n.received" VERI_POLL=0.02 "\$@" > "\$n.out" 2> "\$n.err"
}
"\$S/build-develop-prompt.sh" red spec.md "the step" "$all25" > develop-red.prompt
"\$S/build-develop-prompt.sh" green spec.md "the step" "$all25" t.test.sh "the case" "$fast25" > develop-green.prompt
"\$S/build-develop-prompt.sh" refactor spec.md "the step" "$all25" src/a.sh > develop-refactor.prompt
for p in red green refactor; do
  leaf develop-\$p "\$S/supervise.sh" develop-\$p "\$S/run-leaf.sh" develop-\$p.prompt
done
leaf verify-red "\$S/verify.sh" --step "the step" --fast-cmd "$fast25" red spec.md t.test.sh "the case"
leaf verify-green "\$S/verify.sh" --step "the step" --fast-cmd "$fast25" green spec.md t.test.sh "the case"
leaf verify-refactor "\$S/verify.sh" --step "the step" --fast-cmd "$fast25" refactor spec.md t.test.sh abc1234
leaf verify-refactor-bare "\$S/verify.sh" --step "the step" refactor spec.md t.test.sh abc1234
echo "\$?" > verify-refactor-bare.exit
HOOK
chmod +x "$stubdir/hook25"

caller25="$work/caller25"
caller_repo "$caller25"
launch_from "$caller25" "$clone25" CONDUCTOR_HOOK="$stubdir/hook25"

tier_of() {
  local fast="" affected=""
  grep -qF -- "$fast25" "$1" && fast=fast
  grep -qF -- 'affected-suites.sh' "$1" && affected=affected
  if [[ -n "$fast" && -n "$affected" ]]; then echo fast+affected
  elif [[ -n "$fast$affected" ]]; then echo "$fast$affected"
  elif grep -qF -- "$all25" "$1"; then echo all
  else echo none
  fi
}

for want in develop-red=affected verify-red=affected develop-green=fast+affected \
            verify-green=fast+affected develop-refactor=affected verify-refactor=fast+affected; do
  leaf25="${want%%=*}" tier25="${want#*=}"
  if [[ ! -s "$tiers/$leaf25.received" ]]; then
    problems+=("$leaf25 never received a prompt: $(cat "$tiers/$leaf25.err" 2>/dev/null)")
  else
    got25="$(tier_of "$tiers/$leaf25.received")"
    [[ "$got25" == "$tier25" ]] || problems+=("$leaf25's launch was built with $got25, not $tier25")
  fi
done

bare25="$(cat "$tiers/verify-refactor-bare.exit" 2>/dev/null)"
if [[ "$bare25" != 2 || -e "$tiers/verify-refactor-bare.received" ]]; then
  problems+=("verify-refactor launched without --fast-cmd exited ${bare25:-nothing} and its leaf $([[ -e "$tiers/verify-refactor-bare.received" ]] && echo received || echo "never received") a prompt, want exit 2 and no prompt")
fi

report "$name"

name="a VERI_NEW_SKILL=1 re-pin that runs before .tdd/wt/<n> exists writes its skill-repin event to the run worktree's .tdd/events.jsonl and never to the caller's"
problems=()

clone26="$work/clone26"
skill_clone "$clone26"

caller26="$work/caller26"
caller_repo "$caller26"
launch_from "$caller26" "$clone26"

advance_clone "$clone26" "# a commit the operator asks the run to take"
head26="$(git -C "$clone26" rev-parse HEAD)"

[[ ! -e "$caller26/.tdd/wt/$issue" ]] ||
  problems+=("fixture: $caller26/.tdd/wt/$issue exists before the re-pin, so this is case 19")
launch_from "$caller26" "$clone26" VERI_NEW_SKILL=1

wt_log26="$caller26/.tdd/wt/$issue/.tdd/events.jsonl"
caller_log26="$caller26/.tdd/events.jsonl"

repin_in "$wt_log26" "$head26" ||
  problems+=("no skill-repin event naming $head26 in the run worktree's $wt_log26")
if repin_in "$caller_log26" "$head26"; then
  problems+=("the skill-repin event landed in the caller's $caller_log26")
fi

report "$name"

name="run-conductor.sh launched directly, with no orchestrator, exits 0 and hands the conductor a procedure naming nothing orchestrate.sh adds"
problems=()

caller27="$work/caller27"
caller_repo "$caller27"
rm -f "$argv" "$prompt"

( unset VERI_CONDUCTOR_CTX_BUDGET; launch_from "$caller27" "$work/tree" )
status=$?

if [[ "$status" -ne 0 ]]; then
  problems+=("the direct launch exited $status, not 0: $(cat "$launch_err")")
elif [[ ! -s "$argv" ]]; then
  problems+=("the direct launch never reached the conductor binary")
else
  for added in orchestrate.sh VERI_CONDUCTOR_CTX_BUDGET .tdd/parked/; do
    ! grep -F -- "$added" "$prompt" > /dev/null ||
      problems+=("the procedure a direct launch hands the conductor names '$added'")
  done
  [[ ! -e "$caller27/.tdd/parked" ]] ||
    problems+=("a direct launch created $caller27/.tdd/parked")
fi

report "$name"

name="run-conductor.sh, failing inside its own EXIT trap's lifetime, ends with exit 2"
problems=()

clone28="$work/clone28"
skill_clone "$clone28"
caller28="$work/caller28"
caller_repo "$caller28"
failing_tar="$(scratch_dir)"
printf '#!/bin/sh\nexit 5\n' > "$failing_tar/tar"
chmod +x "$failing_tar/tar"

launch_from "$caller28" "$clone28" PATH="$failing_tar:$PATH"
status=$?

[[ "$status" -eq 2 ]] ||
  problems+=("the launch exited $status, not 2: $(cat "$launch_err")")

report "$name"

finish
