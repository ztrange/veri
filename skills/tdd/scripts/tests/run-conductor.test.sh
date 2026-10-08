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
git -C "$caller3" commit -q --allow-empty -m base
git -C "$caller3" branch "tdd/$issue-past-preflight"

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
git -C "$caller4" commit -q --allow-empty -m base
git -C "$caller4" branch "tdd/$issue-past-preflight"

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
git -C "$caller10" commit -q --allow-empty -m base
git -C "$caller10" branch "tdd/$issue-past-preflight"

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
git -C "$caller12" commit -q --allow-empty -m base
git -C "$caller12" branch "tdd/$issue-past-preflight"
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
git -C "$caller13" commit -q --allow-empty -m base
git -C "$caller13" branch "tdd/$issue-past-preflight"
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
git -C "$caller24" commit -q --allow-empty -m base
git -C "$caller24" branch "tdd/$issue-past-preflight"

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

name="with no refs/remotes/origin/HEAD the launch pins to the remote's default branch tip, records it and runs pinned (#865)"
problems=()

remote31="$work/remote31-865"
clone31="$work/clone31-865"
cloned_skill "$remote31" "$clone31"
git -C "$clone31" remote set-head origin -d
git -C "$clone31" config remote.origin.followRemoteHEAD never
advance_clone "$remote31" "# a commit that landed on the remote after the clone was cut"
tip31="$(git -C "$remote31" rev-parse HEAD)"

tipdir31="$work/tip31-865"
skill_archive "$remote31" "$tip31" "$tipdir31"

caller31="$work/caller31-865"
caller_repo "$caller31"
git -C "$caller31" commit -q --allow-empty -m base
git -C "$caller31" branch "tdd/$issue-past-preflight"
base31="$work/base31-865"
mkdir -p "$base31"
env31="$work/env31-865"
rm -f "$env31"

( unset VERI_SKILL_UNPINNED; launch_from "$caller31" "$clone31" BASE_OUT="$base31" ENV_OUT="$env31" )
rc31=$?

record31="$caller31/.tdd/issue-$issue-skill-commit"
[[ "$rc31" == 0 ]] ||
  problems+=("the launch exited $rc31, not 0: $(cat "$launch_err")")
if [[ ! -f "$record31" ]]; then
  problems+=("no skill-commit record was written at $record31 — stderr was: '$(cat "$launch_err")'")
elif [[ "$(cat "$record31")" != "$tip31" ]]; then
  problems+=("the record holds '$(cat "$record31")', not the remote default branch's tip $tip31")
fi
holds_skill "$base31" "$tipdir31/skills/tdd" "launch's" "the remote default branch's tip $tip31"
if [[ ! -f "$env31" ]]; then
  problems+=("the conductor was never launched: $(cat "$launch_err")")
elif grep -q '^VERI_SKILL_UNPINNED=' "$env31"; then
  problems+=("the launch exported VERI_SKILL_UNPINNED to the conductor")
fi

report "$name"

name="with no refs/remotes/origin/HEAD and no resolvable remote default branch the launch exits 2 naming the ref and never runs unpinned (#865)"
problems=()

remote32="$work/remote32-865"
clone32="$work/clone32-865"
cloned_skill "$remote32" "$clone32"
git -C "$clone32" remote set-head origin -d
git -C "$clone32" config remote.origin.followRemoteHEAD never
git -C "$remote32" checkout -q --detach
git -C "$remote32" -c user.name=t -c user.email=t@t commit -q --allow-empty -m 'on no branch'

caller32="$work/caller32-865"
caller_repo "$caller32"
env32="$work/env32-865"
rm -f "$env32"

( unset VERI_SKILL_UNPINNED; launch_from "$caller32" "$clone32" ENV_OUT="$env32" )
rc32=$?

[[ "$rc32" == 2 ]] ||
  problems+=("the launch exited $rc32, not 2: $(cat "$launch_err")")
grep -F 'refs/remotes/origin/HEAD' "$launch_err" > /dev/null ||
  problems+=("stderr does not name refs/remotes/origin/HEAD: '$(cat "$launch_err")'")
[[ ! -f "$env32" ]] ||
  problems+=("the conductor was launched: $(grep '^VERI_SKILL_UNPINNED=' "$env32" || echo 'pinned')")

report "$name"

name="with no refs/remotes/origin/HEAD and the remote's named default branch absent locally the launch exits 2 naming the ref and never runs unpinned (#865)"
problems=()

remote33="$work/remote33-865"
clone33="$work/clone33-865"
cloned_skill "$remote33" "$clone33"
default33="$(git -C "$remote33" symbolic-ref --short HEAD)"
git -C "$remote33" branch -q side33
git -C "$clone33" remote set-head origin -d
git -C "$clone33" config remote.origin.followRemoteHEAD never
git -C "$clone33" config remote.origin.fetch '+refs/heads/side33:refs/remotes/origin/side33'
git -C "$clone33" update-ref -d "refs/remotes/origin/$default33"

caller33="$work/caller33-865"
caller_repo "$caller33"
env33="$work/env33-865"
rm -f "$env33"

( unset VERI_SKILL_UNPINNED; launch_from "$caller33" "$clone33" ENV_OUT="$env33" )
rc33=$?

[[ "$rc33" == 2 ]] ||
  problems+=("the launch exited $rc33, not 2: $(cat "$launch_err")")
grep -F 'refs/remotes/origin/HEAD' "$launch_err" > /dev/null ||
  problems+=("stderr does not name refs/remotes/origin/HEAD: '$(cat "$launch_err")'")
[[ ! -f "$env33" ]] ||
  problems+=("the conductor was launched: $(grep '^VERI_SKILL_UNPINNED=' "$env33" || echo 'pinned')")

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
git -C "$caller26" commit -q --allow-empty -m base
git -C "$caller26" branch "tdd/$issue-past-preflight"
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

name="run-conductor.sh severs CLAUDE_AUTO_BACKGROUND_TASKS and the eight session handles (#621)"
problems=()
env29="$work/env29"

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$env29" \
    "${handles[@]}" CLAUDE_AUTO_BACKGROUND_TASKS=true \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$env29" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no environment")
else
  for handle in "${handles[@]}" CLAUDE_AUTO_BACKGROUND_TASKS=true; do
    ! grep "^${handle%%=*}=" "$env29" > /dev/null ||
      problems+=("${handle%%=*} is still in the child's environment")
  done
fi

report "$name"

name="VERI_GH_DRIVER set on the launch reaches the conductor child and a leaf it detaches through supervise.sh and run-leaf.sh (#848)"
problems=()

clone30="$work/clone30"
skill_clone "$clone30"
leaf30="$work/leaf30"
mkdir -p "$leaf30"
echo "the leaf prompt" > "$leaf30/leaf.prompt"
env30="$work/env30"
leafenv30="$leaf30/leaf-driver"

cat > "$stubdir/driver-claude" <<'STUB'
#!/bin/sh
printf '%s\n' "${VERI_GH_DRIVER-<unset>}" > "$LEAF_DRIVER_OUT"
printf '%s\n' '{"type":"result","subtype":"success","is_error":false,"result":"ok"}'
STUB
chmod +x "$stubdir/driver-claude"

cat > "$stubdir/driver-hook" <<HOOK
#!/bin/sh
base="\$1"
cd "$leaf30" || exit 1
env CLAUDE_BIN="$stubdir/driver-claude" LEAF_DRIVER_OUT="$leafenv30" VERI_POLL=0.02 \
  "\$base/scripts/detach-leaf.sh" "\$base/scripts/supervise.sh" develop-red "\$base/scripts/run-leaf.sh" leaf.prompt > supervise.out 2> supervise.err
VERI_POLL=0.02 "\$base/scripts/wait-leaf.sh" develop-red 5 > /dev/null 2>&1
HOOK
chmod +x "$stubdir/driver-hook"

caller30="$work/caller30"
caller_repo "$caller30"
launch_from "$caller30" "$clone30" CONDUCTOR_HOOK="$stubdir/driver-hook" ENV_OUT="$env30" VERI_GH_DRIVER=graphql

if [[ ! -f "$env30" ]]; then
  problems+=("the conductor binary was never launched — recorded no environment: $(cat "$launch_err")")
else
  conductor30="$(sed -n 's/^VERI_GH_DRIVER=//p' "$env30")"
  [[ "$conductor30" == graphql ]] ||
    problems+=("the conductor child saw VERI_GH_DRIVER=${conductor30:-<unset>}, not graphql")
fi
if [[ ! -s "$leafenv30" ]]; then
  problems+=("the detached leaf's claude never ran: $(cat "$leaf30/supervise.err" 2>/dev/null)")
else
  [[ "$(cat "$leafenv30")" == graphql ]] ||
    problems+=("the leaf's claude saw VERI_GH_DRIVER=$(cat "$leafenv30"), not graphql")
fi

report "$name"

name="a fetch of origin that loses a ref lock held by another process is retried once the lock is released, and the conductor starts (#886)"
problems=()

src31="$work/src31"
remote31="$work/remote31"
clone31="$work/clone31"
skill_clone "$src31"
git clone -q --bare "$src31" "$remote31"
git clone -q "$remote31" "$clone31"
branch31="$(git -C "$remote31" symbolic-ref --short HEAD)"
advance_clone "$src31" "# a commit another conductor's fetch is bringing in"
git -C "$src31" push -q "$remote31" "HEAD:$branch31"
tip31="$(git -C "$remote31" rev-parse HEAD)"

lock31="$clone31/.git/refs/remotes/origin/$branch31.lock"
: > "$lock31"

shim31="$work/shim31"
mkdir -p "$shim31"
cat > "$shim31/git" <<SHIM
#!/bin/sh
"$(command -v git)" "\$@"
status=\$?
case " \$* " in *" fetch "*) rm -f "$lock31" ;; esac
exit \$status
SHIM
chmod +x "$shim31/git"

caller31="$work/caller31"
caller_repo "$caller31"

rm -f "$argv" "$prompt"
launch_from "$caller31" "$clone31" PATH="$shim31:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0, although the ref lock was released after its first fetch — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ -f "$argv" ]] ||
  problems+=("no conductor was launched")
grep -F -- "$tip31" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip31 as the pinned skill commit")

report "$name"

name="a fetch of origin whose ref lock is still held when the second fetch runs keeps retrying until the lock is released, and the conductor starts (#886)"
problems=()

src32="$work/src32"
remote32="$work/remote32"
clone32="$work/clone32"
skill_clone "$src32"
git clone -q --bare "$src32" "$remote32"
git clone -q "$remote32" "$clone32"
branch32="$(git -C "$remote32" symbolic-ref --short HEAD)"
advance_clone "$src32" "# a commit another conductor's fetch is bringing in"
git -C "$src32" push -q "$remote32" "HEAD:$branch32"
tip32="$(git -C "$remote32" rev-parse HEAD)"

lock32="$clone32/.git/refs/remotes/origin/$branch32.lock"
: > "$lock32"

shim32="$work/shim32"
fetches32="$work/fetches32"
mkdir -p "$shim32"
cat > "$shim32/git" <<SHIM
#!/bin/sh
"$(command -v git)" "\$@"
status=\$?
case " \$* " in
  *" fetch "*)
    echo fetch >> "$fetches32"
    [ "\$(wc -l < "$fetches32")" -ge 2 ] && rm -f "$lock32" ;;
esac
exit \$status
SHIM
chmod +x "$shim32/git"

caller32="$work/caller32"
caller_repo "$caller32"

rm -f "$argv" "$prompt"
launch_from "$caller32" "$clone32" PATH="$shim32:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0, although the ref lock was released after its second fetch — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ -f "$argv" ]] ||
  problems+=("no conductor was launched")
grep -F -- "$tip32" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip32 as the pinned skill commit")

report "$name"

name="a fetch of origin whose URL is no remote is refused with exit 2 and the fetch-failed message after one fetch, not after the lock retries (#886)"
problems=()

clone33="$work/clone33"
skill_clone "$clone33"
git -C "$clone33" remote add origin "$work/no-remote33"

shim33="$work/shim33"
fetches33="$work/fetches33"
mkdir -p "$shim33"
: > "$fetches33"
cat > "$shim33/git" <<SHIM
#!/bin/sh
case " \$* " in *" fetch "*) echo fetch >> "$fetches33" ;; esac
exec "$(command -v git)" "\$@"
SHIM
chmod +x "$shim33/git"

caller33="$work/caller33"
caller_repo "$caller33"

rm -f "$argv"
launch_from "$caller33" "$clone33" PATH="$shim33:$PATH"
status=$?
count33="$(wc -l < "$fetches33" | tr -d ' ')"

[[ "$status" -eq 2 ]] ||
  problems+=("the launch exited $status, not 2")
[[ ! -f "$argv" ]] ||
  problems+=("a conductor was launched although origin is no remote")
grep -F 'fetch of origin failed' "$launch_err" > /dev/null 2>&1 ||
  problems+=("stderr does not say 'fetch of origin failed' — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ "$count33" == 1 ]] ||
  problems+=("origin was fetched $count33 times, not once, although the failure was no ref lock")

report "$name"

name="a ref lock that outlives five back-to-back fetches and is released only while the run waits between retries still lets the conductor start, pinned to origin's tip (#886)"
problems=()

src34="$work/src34"
remote34="$work/remote34"
clone34="$work/clone34"
skill_clone "$src34"
git clone -q --bare "$src34" "$remote34"
git clone -q "$remote34" "$clone34"
branch34="$(git -C "$remote34" symbolic-ref --short HEAD)"
advance_clone "$src34" "# a commit another conductor's fetch is bringing in"
git -C "$src34" push -q "$remote34" "HEAD:$branch34"
tip34="$(git -C "$remote34" rev-parse HEAD)"

lock34="$clone34/.git/refs/remotes/origin/$branch34.lock"
: > "$lock34"

shim34="$work/shim34"
mkdir -p "$shim34"
cat > "$shim34/sleep" <<SHIM
#!/bin/sh
rm -f "$lock34"
SHIM
chmod +x "$shim34/sleep"

caller34="$work/caller34"
caller_repo "$caller34"

rm -f "$argv" "$prompt"
launch_from "$caller34" "$clone34" PATH="$shim34:$PATH"
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0, although the ref lock was released while the run waited between fetches — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ -f "$argv" ]] ||
  problems+=("no conductor was launched")
grep -F -- "$tip34" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip34 as the pinned skill commit")

report "$name"

name="a locked fetch is retried after waiting the interval VERI_FETCH_RETRY_SLEEP names, so VERI_FETCH_RETRY_SLEEP=0 retries without waiting on the real clock (#900)"
problems=()

src35="$work/src35"
remote35="$work/remote35"
clone35="$work/clone35"
skill_clone "$src35"
git clone -q --bare "$src35" "$remote35"
git clone -q "$remote35" "$clone35"
branch35="$(git -C "$remote35" symbolic-ref --short HEAD)"
advance_clone "$src35" "# a commit another conductor's fetch is bringing in"
git -C "$src35" push -q "$remote35" "HEAD:$branch35"
tip35="$(git -C "$remote35" rev-parse HEAD)"

lock35="$clone35/.git/refs/remotes/origin/$branch35.lock"
: > "$lock35"

shim35="$work/shim35"
sleeps35="$work/sleeps35"
mkdir -p "$shim35"
: > "$sleeps35"
cat > "$shim35/sleep" <<SHIM
#!/bin/sh
printf '%s\\n' "\$*" >> "$sleeps35"
rm -f "$lock35"
SHIM
chmod +x "$shim35/sleep"

caller35="$work/caller35"
caller_repo "$caller35"

rm -f "$argv" "$prompt"
launch_from "$caller35" "$clone35" PATH="$shim35:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?
waits35="$(tr '\n' ' ' < "$sleeps35")"

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0 — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ "$waits35" == "0 " ]] ||
  problems+=("the run waited between fetches with sleep '${waits35:-<never>}', not once with sleep '0 ' as VERI_FETCH_RETRY_SLEEP=0 names")
grep -F -- "$tip35" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip35 as the pinned skill commit")

report "$name"

name="with VERI_FETCH_RETRY_SLEEP unset, a locked fetch is retried after waiting 1 s, the default interval (#900)"
problems=()

src36="$work/src36"
remote36="$work/remote36"
clone36="$work/clone36"
skill_clone "$src36"
git clone -q --bare "$src36" "$remote36"
git clone -q "$remote36" "$clone36"
branch36="$(git -C "$remote36" symbolic-ref --short HEAD)"
advance_clone "$src36" "# a commit another conductor's fetch is bringing in"
git -C "$src36" push -q "$remote36" "HEAD:$branch36"
tip36="$(git -C "$remote36" rev-parse HEAD)"

lock36="$clone36/.git/refs/remotes/origin/$branch36.lock"
: > "$lock36"

shim36="$work/shim36"
sleeps36="$work/sleeps36"
mkdir -p "$shim36"
: > "$sleeps36"
cat > "$shim36/sleep" <<SHIM
#!/bin/sh
printf '%s\\n' "\$*" >> "$sleeps36"
rm -f "$lock36"
SHIM
chmod +x "$shim36/sleep"

caller36="$work/caller36"
caller_repo "$caller36"

rm -f "$argv" "$prompt"
( unset VERI_FETCH_RETRY_SLEEP; launch_from "$caller36" "$clone36" PATH="$shim36:$PATH" )
status=$?
waits36="$(tr '\n' ' ' < "$sleeps36")"

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0 — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ "$waits36" == "1 " ]] ||
  problems+=("the run waited between fetches with sleep '${waits36:-<never>}', not once with sleep '1 ', the default interval when VERI_FETCH_RETRY_SLEEP is unset")
grep -F -- "$tip36" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip36 as the pinned skill commit")

report "$name"

name="a ref lock still held when the fifth fetch runs, and released only after it, lets the conductor start pinned to origin's tip (#1012)"
problems=()

src1012="$work/src1012"
remote1012="$work/remote1012"
clone1012="$work/clone1012"
skill_clone "$src1012"
git clone -q --bare "$src1012" "$remote1012"
git clone -q "$remote1012" "$clone1012"
branch1012="$(git -C "$remote1012" symbolic-ref --short HEAD)"
advance_clone "$src1012" "# a commit a slow parallel fetch is bringing in"
git -C "$src1012" push -q "$remote1012" "HEAD:$branch1012"
tip1012="$(git -C "$remote1012" rev-parse HEAD)"

lock1012="$clone1012/.git/refs/remotes/origin/$branch1012.lock"
: > "$lock1012"

shim1012="$work/shim1012"
fetches1012="$work/fetches1012"
mkdir -p "$shim1012"
cat > "$shim1012/git" <<SHIM
#!/bin/sh
"$(command -v git)" "\$@"
status=\$?
case " \$* " in
  *" fetch "*)
    echo fetch >> "$fetches1012"
    [ "\$(wc -l < "$fetches1012")" -ge 5 ] && rm -f "$lock1012" ;;
esac
exit \$status
SHIM
chmod +x "$shim1012/git"

caller1012="$work/caller1012"
caller_repo "$caller1012"

rm -f "$argv" "$prompt"
launch_from "$caller1012" "$clone1012" PATH="$shim1012:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?

[[ "$status" -eq 0 ]] ||
  problems+=("the launch exited $status, not 0, although the ref lock was released after its fifth fetch — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ -f "$argv" ]] ||
  problems+=("no conductor was launched")
grep -F -- "$tip1012" "$prompt" > /dev/null 2>&1 ||
  problems+=("the conductor's prompt does not name origin's tip $tip1012 as the pinned skill commit")

report "$name"

name="a ref lock that is never released makes the launch refuse with exit 2 once the retry bound, past today's five fetches, is reached, launching no conductor and naming the ref lock (#1012)"
problems=()

src1012b="$work/src1012b"
remote1012b="$work/remote1012b"
clone1012b="$work/clone1012b"
skill_clone "$src1012b"
git clone -q --bare "$src1012b" "$remote1012b"
git clone -q "$remote1012b" "$clone1012b"
branch1012b="$(git -C "$remote1012b" symbolic-ref --short HEAD)"
advance_clone "$src1012b" "# a commit a parallel fetch that never finishes is bringing in"
git -C "$src1012b" push -q "$remote1012b" "HEAD:$branch1012b"

lock1012b="$clone1012b/.git/refs/remotes/origin/$branch1012b.lock"
: > "$lock1012b"

shim1012b="$work/shim1012b"
fetches1012b="$work/fetches1012b"
mkdir -p "$shim1012b"
: > "$fetches1012b"
cat > "$shim1012b/git" <<SHIM
#!/bin/sh
case " \$* " in *" fetch "*) echo fetch >> "$fetches1012b" ;; esac
exec "$(command -v git)" "\$@"
SHIM
chmod +x "$shim1012b/git"

caller1012b="$work/caller1012b"
caller_repo "$caller1012b"

rm -f "$argv"
launch_from "$caller1012b" "$clone1012b" PATH="$shim1012b:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?
count1012b="$(wc -l < "$fetches1012b" | tr -d ' ')"

[[ "$status" -eq 2 ]] ||
  problems+=("the launch exited $status, not 2, although the ref lock was never released")
[[ ! -f "$argv" ]] ||
  problems+=("a conductor was launched although the ref lock was never released")
grep -F 'cannot lock ref' "$launch_err" > /dev/null 2>&1 ||
  problems+=("stderr does not name the ref lock ('cannot lock ref') — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
(( count1012b > 5 )) ||
  problems+=("origin was fetched $count1012b times before the refusal, not more than today's 5")

report "$name"

name="a fetch of origin that fails for a reason other than a ref lock is refused with exit 2 after one fetch, without waiting for any retry (#1012)"
problems=()

clone1012c="$work/clone1012c"
skill_clone "$clone1012c"
git -C "$clone1012c" remote add origin "$work/remote1012c"

shim1012c="$work/shim1012c"
fetches1012c="$work/fetches1012c"
sleeps1012c="$work/sleeps1012c"
mkdir -p "$shim1012c"
: > "$fetches1012c"
: > "$sleeps1012c"
cat > "$shim1012c/git" <<SHIM
#!/bin/sh
case " \$* " in
  *" fetch "*)
    echo fetch >> "$fetches1012c"
    echo "fatal: unable to access '$work/remote1012c/': Could not resolve host: origin.invalid" >&2
    exit 128 ;;
esac
exec "$(command -v git)" "\$@"
SHIM
cat > "$shim1012c/sleep" <<SHIM
#!/bin/sh
printf '%s\\n' "\$*" >> "$sleeps1012c"
SHIM
chmod +x "$shim1012c/git" "$shim1012c/sleep"

caller1012c="$work/caller1012c"
caller_repo "$caller1012c"

rm -f "$argv"
launch_from "$caller1012c" "$clone1012c" PATH="$shim1012c:$PATH" VERI_FETCH_RETRY_SLEEP=0
status=$?
count1012c="$(wc -l < "$fetches1012c" | tr -d ' ')"
waits1012c="$(tr '\n' ' ' < "$sleeps1012c")"

[[ "$status" -eq 2 ]] ||
  problems+=("the launch exited $status, not 2, although the fetch failed for no ref lock")
[[ ! -f "$argv" ]] ||
  problems+=("a conductor was launched although the fetch failed")
grep -F 'fetch of origin failed' "$launch_err" > /dev/null 2>&1 ||
  problems+=("stderr does not say 'fetch of origin failed' — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
[[ "$count1012c" == 1 ]] ||
  problems+=("origin was fetched $count1012c times, not once, although the failure was no ref lock")
[[ -z "$waits1012c" ]] ||
  problems+=("the run waited with sleep '$waits1012c' before refusing, although the failure was no ref lock")

report "$name"

name="a conductor that exits with .tdd/wt/<n> registered as a worktree keeps the skill record, and the next launch runs the recorded commit (#866)"
problems=()

remote37="$work/remote37"
clone37="$work/clone37"
cloned_skill "$remote37" "$clone37"
first37="$(git -C "$remote37" rev-parse HEAD)"

pinned37="$work/pinned37"
skill_archive "$remote37" "$first37" "$pinned37"

caller37="$work/caller37"
caller_repo "$caller37"
git -C "$caller37" commit -q --allow-empty -m base

cat > "$stubdir/worktree-hook" <<HOOK
#!/bin/sh
git -C "$caller37" worktree add -q --detach "$caller37/.tdd/wt/$issue"
HOOK
chmod +x "$stubdir/worktree-hook"

launch_from "$caller37" "$clone37" CONDUCTOR_HOOK="$stubdir/worktree-hook"
record37="$caller37/.tdd/issue-$issue-skill-commit"

if ! git -C "$caller37" worktree list --porcelain | grep -x "worktree $(cd "$caller37/.tdd/wt/$issue" 2>/dev/null && pwd -P)" > /dev/null; then
  problems+=("the conductor left no registered worktree at .tdd/wt/$issue: $(cat "$launch_err")")
elif [[ ! -f "$record37" ]]; then
  problems+=("the record $record37 is gone after a conductor that left .tdd/wt/$issue registered as a worktree")
else
  [[ "$(cat "$record37")" == "$first37" ]] ||
    problems+=("the record holds '$(cat "$record37")', not the launch's pin $first37")
fi

advance_clone "$remote37" "# a commit that landed on the remote after the run got past preflight"
moved37="$(git -C "$remote37" rev-parse HEAD)"

resumed37="$work/resumed37"
mkdir -p "$resumed37"
rm -f "$prompt"
launch_from "$caller37" "$clone37" BASE_OUT="$resumed37"

if [[ -z "$(prompt_base)" ]]; then
  problems+=("the next launch's prompt names no base directory: $(cat "$launch_err")")
else
  holds_skill "$resumed37" "$pinned37/skills/tdd" "next launch's" "recorded pin $first37 (origin moved to $moved37)"
  grep -q -- "$first37" "$prompt" ||
    problems+=("the next launch's prompt does not name the recorded pin $first37")
fi

report "$name"

name="a conductor that exits with a local tdd/<n>-* branch and no worktree keeps the skill record, and the next launch runs the recorded commit (#866)"
problems=()

remote38="$work/remote38"
clone38="$work/clone38"
cloned_skill "$remote38" "$clone38"
first38="$(git -C "$remote38" rev-parse HEAD)"

pinned38="$work/pinned38"
skill_archive "$remote38" "$first38" "$pinned38"

caller38="$work/caller38"
caller_repo "$caller38"
git -C "$caller38" commit -q --allow-empty -m base

cat > "$stubdir/branch-hook" <<HOOK
#!/bin/sh
git -C "$caller38" branch "tdd/$issue-past-preflight"
HOOK
chmod +x "$stubdir/branch-hook"

launch_from "$caller38" "$clone38" CONDUCTOR_HOOK="$stubdir/branch-hook"
record38="$caller38/.tdd/issue-$issue-skill-commit"

if ! git -C "$caller38" show-ref --verify -q "refs/heads/tdd/$issue-past-preflight"; then
  problems+=("the conductor left no local branch tdd/$issue-past-preflight: $(cat "$launch_err")")
elif [[ -n "$(git -C "$caller38" worktree list --porcelain | grep -F ".tdd/wt/$issue" || true)" ]]; then
  problems+=("the conductor left a worktree at .tdd/wt/$issue, so the branch alone is not what kept the record")
elif [[ ! -f "$record38" ]]; then
  problems+=("the record $record38 is gone after a conductor that left a local tdd/$issue-* branch and no worktree")
else
  [[ "$(cat "$record38")" == "$first38" ]] ||
    problems+=("the record holds '$(cat "$record38")', not the launch's pin $first38")
fi

advance_clone "$remote38" "# a commit that landed on the remote after the run got past preflight"
moved38="$(git -C "$remote38" rev-parse HEAD)"

resumed38="$work/resumed38"
mkdir -p "$resumed38"
rm -f "$prompt"
launch_from "$caller38" "$clone38" BASE_OUT="$resumed38"

if [[ -z "$(prompt_base)" ]]; then
  problems+=("the next launch's prompt names no base directory: $(cat "$launch_err")")
else
  holds_skill "$resumed38" "$pinned38/skills/tdd" "next launch's" "recorded pin $first38 (origin moved to $moved38)"
  grep -q -- "$first38" "$prompt" ||
    problems+=("the next launch's prompt does not name the recorded pin $first38")
fi

report "$name"

name="a conductor that exits, 0 or non-zero, with no registered .tdd/wt/<n> worktree and no local tdd/<n>-* branch leaves no skill record (#866)"
problems=()

remote39="$work/remote39"
clone39="$work/clone39"
cloned_skill "$remote39" "$clone39"

for exit39 in 0 1; do
  caller39="$work/caller39-$exit39"
  caller_repo "$caller39"
  git -C "$caller39" commit -q --allow-empty -m base
  launch_from "$caller39" "$clone39" STUB_EXIT="$exit39"
  rc39=$?
  record39="$caller39/.tdd/issue-$issue-skill-commit"
  if [[ "$rc39" != "$exit39" ]]; then
    problems+=("the launch whose conductor exits $exit39 exited $rc39: $(cat "$launch_err")")
  elif [[ -e "$record39" ]]; then
    problems+=("the record $record39 survived a conductor that exited $exit39 with no worktree and no tdd/$issue-* branch, holding '$(cat "$record39")'")
  fi
done

report "$name"

name="a local branch for another issue whose number starts with <n> (tdd/<n>6-*) does not count as a run past preflight: the skill record is removed (#866)"
problems=()

remote40="$work/remote40"
clone40="$work/clone40"
cloned_skill "$remote40" "$clone40"

caller40="$work/caller40"
caller_repo "$caller40"
git -C "$caller40" commit -q --allow-empty -m base

cat > "$stubdir/other-branch-hook" <<HOOK
#!/bin/sh
git -C "$caller40" branch "tdd/${issue}6-other-issue"
HOOK
chmod +x "$stubdir/other-branch-hook"

launch_from "$caller40" "$clone40" CONDUCTOR_HOOK="$stubdir/other-branch-hook"
record40="$caller40/.tdd/issue-$issue-skill-commit"

if ! git -C "$caller40" show-ref --verify -q "refs/heads/tdd/${issue}6-other-issue"; then
  problems+=("the conductor left no local branch tdd/${issue}6-other-issue: $(cat "$launch_err")")
elif [[ -e "$record40" ]]; then
  problems+=("the record $record40 survived a conductor that left only tdd/${issue}6-other-issue, another issue's branch, holding '$(cat "$record40")'")
fi

report "$name"

name="after a launch that left no worktree and no tdd/<n>-* branch, the next launch without VERI_NEW_SKILL pins the default branch's tip at that moment, not the earlier launch's commit (#866)"
problems=()

remote41="$work/remote41"
clone41="$work/clone41"
cloned_skill "$remote41" "$clone41"
first41="$(git -C "$remote41" rev-parse HEAD)"

caller41="$work/caller41"
caller_repo "$caller41"
git -C "$caller41" commit -q --allow-empty -m base
launch_from "$caller41" "$clone41"

advance_clone "$remote41" "# a commit that landed on the remote after the run stopped at preflight"
moved41="$(git -C "$remote41" rev-parse HEAD)"

pinned41="$work/pinned41"
skill_archive "$remote41" "$moved41" "$pinned41"

relaunched41="$work/relaunched41"
mkdir -p "$relaunched41"
rm -f "$prompt"
launch_from "$caller41" "$clone41" BASE_OUT="$relaunched41"

if [[ -z "$(prompt_base)" ]]; then
  problems+=("the next launch's prompt names no base directory: $(cat "$launch_err")")
else
  holds_skill "$relaunched41" "$pinned41/skills/tdd" "next launch's" "the tip $moved41 (the earlier launch pinned $first41)"
  grep -q -- "$moved41" "$prompt" ||
    problems+=("the next launch's prompt does not name the tip $moved41 (the earlier launch pinned $first41)")
fi

report "$name"

name="an unregistered .tdd/wt/<n> holding only .tdd/events.jsonl, as VERI_NEW_SKILL=1 leaves it, does not count as a run past preflight: with no worktree and no branch the skill record is removed (#866)"
problems=()

remote42="$work/remote42"
clone42="$work/clone42"
cloned_skill "$remote42" "$clone42"

caller42="$work/caller42"
caller_repo "$caller42"
git -C "$caller42" commit -q --allow-empty -m base
mkdir -p "$caller42/.tdd"
git -C "$remote42" rev-parse HEAD > "$caller42/.tdd/issue-$issue-skill-commit"

launch_from "$caller42" "$clone42" VERI_NEW_SKILL=1
record42="$caller42/.tdd/issue-$issue-skill-commit"
left42="$(cd "$caller42/.tdd/wt/$issue" 2>/dev/null && find . -type f)"

if [[ "$left42" != "./.tdd/events.jsonl" ]]; then
  problems+=("the re-pinning launch did not leave .tdd/wt/$issue holding only .tdd/events.jsonl, it held '$left42': $(cat "$launch_err")")
elif git -C "$caller42" worktree list --porcelain | grep -F ".tdd/wt/$issue" >/dev/null; then
  problems+=("the conductor registered .tdd/wt/$issue as a worktree")
elif [[ -e "$record42" ]]; then
  problems+=("the record $record42 survived a conductor that left only an unregistered .tdd/wt/$issue holding .tdd/events.jsonl, holding '$(cat "$record42")'")
fi

report "$name"

name="with no worktree and no tdd/<n>-* branch, an unresolvable recorded skill commit still exits 2 before launching any conductor (#866)"
problems=()

clone43="$work/clone43"
skill_clone "$clone43"

foreign43="$work/foreign43"
caller_repo "$foreign43"
git -C "$foreign43" -c user.name=t -c user.email=t@t commit -q --allow-empty -m elsewhere
missing43="$(git -C "$foreign43" rev-parse HEAD)"

caller43="$work/caller43"
caller_repo "$caller43"
git -C "$caller43" commit -q --allow-empty -m base
mkdir -p "$caller43/.tdd"
printf '%s\n' "$missing43" > "$caller43/.tdd/issue-$issue-skill-commit"

rm -f "$argv"
launch_from "$caller43" "$clone43"
rc43=$?
[[ "$rc43" == 2 ]] ||
  problems+=("the launch exited $rc43, not 2: $(cat "$launch_err")")
[[ ! -f "$argv" ]] ||
  problems+=("the conductor was launched anyway over unresolvable recorded commit $missing43")

report "$name"

name="with no worktree and no tdd/<n>-* branch, VERI_NEW_SKILL=1 still re-pins the record to the fresh tip for the conductor's run and writes its skill-repin event (#866)"
problems=()

remote44="$work/remote44"
clone44="$work/clone44"
cloned_skill "$remote44" "$clone44"
first44="$(git -C "$remote44" rev-parse HEAD)"

caller44="$work/caller44"
caller_repo "$caller44"
git -C "$caller44" commit -q --allow-empty -m base
mkdir -p "$caller44/.tdd"
printf '%s\n' "$first44" > "$caller44/.tdd/issue-$issue-skill-commit"

advance_clone "$remote44" "# a commit the operator asks the run to take"
moved44="$(git -C "$remote44" rev-parse HEAD)"

during44="$work/record-during44"
cat > "$stubdir/repin-hook" <<HOOK
#!/bin/sh
cp "$caller44/.tdd/issue-$issue-skill-commit" "$during44"
HOOK
chmod +x "$stubdir/repin-hook"

rm -f "$prompt"
launch_from "$caller44" "$clone44" CONDUCTOR_HOOK="$stubdir/repin-hook" VERI_NEW_SKILL=1

if [[ ! -f "$during44" ]]; then
  problems+=("the conductor ran with no skill record to read: $(cat "$launch_err")")
elif [[ "$(cat "$during44")" != "$moved44" ]]; then
  problems+=("the record held '$(cat "$during44")' while the conductor ran, not the fresh tip $moved44 (the earlier pin was $first44)")
fi
grep -q -- "$moved44" "$prompt" ||
  problems+=("the conductor's prompt does not name the fresh tip $moved44")
repin_in "$caller44/.tdd/wt/$issue/.tdd/events.jsonl" "$moved44" ||
  problems+=("no skill-repin event naming $moved44 in $caller44/.tdd/wt/$issue/.tdd/events.jsonl")

report "$name"

name="run-conductor.sh strips any variable whose value carries the session id (#933)"
problems=()
env933="$work/env933"

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$env933" \
    CLAUDE_CODE_SESSION_ID=sess-933-fake VERI_FAKE_CARRIER=x-sess-933-fake-y \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$env933" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no environment")
else
  for var in CLAUDE_CODE_SESSION_ID VERI_FAKE_CARRIER; do
    ! grep "^${var}=" "$env933" > /dev/null ||
      problems+=("$var is still in the child's environment: $(grep "^${var}=" "$env933")")
  done
fi

report "$name"

name="run-conductor.sh starts claude without CLAUDE_CODE_REMOTE_SESSION_ID, whose value need not contain the session id (#966)"
problems=()
env966="$work/env966"

( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" ENV_OUT="$env966" \
    CLAUDE_CODE_SESSION_ID=sess-966-fake CLAUDE_CODE_REMOTE_SESSION_ID=remote-unrelated-value \
    "$CONDUCTOR" "$issue" ) >/dev/null 2>&1

if [[ ! -f "$env966" ]]; then
  problems+=("the conductor binary was never launched — $CONDUCTOR recorded no environment")
elif grep "^CLAUDE_CODE_REMOTE_SESSION_ID=" "$env966" > /dev/null; then
  problems+=("CLAUDE_CODE_REMOTE_SESSION_ID is still in the child's environment: $(grep "^CLAUDE_CODE_REMOTE_SESSION_ID=" "$env966")")
fi

report "$name"

name="a pinned launch hands the conductor VERI_SKILL_CLONE and VERI_SKILL_REF naming the clone and ref it pinned from; an unpinned launch sets neither (#1016)"
problems=()

remote1016="$work/remote1016"
clone1016="$work/clone1016"
cloned_skill "$remote1016" "$clone1016"
caller1016="$work/caller1016"
caller_repo "$caller1016"
env1016="$work/env1016"
rm -f "$env1016"

( unset VERI_SKILL_UNPINNED VERI_SKILL_CLONE VERI_SKILL_REF
  launch_from "$caller1016" "$clone1016" ENV_OUT="$env1016" )

if [[ ! -f "$env1016" ]]; then
  problems+=("the pinned launch never reached the conductor: $(cat "$launch_err")")
else
  clone_seen1016="$(sed -n 's/^VERI_SKILL_CLONE=//p' "$env1016")"
  ref_seen1016="$(sed -n 's/^VERI_SKILL_REF=//p' "$env1016")"
  if [[ -z "$clone_seen1016" ]]; then
    problems+=("the pinned launch handed the conductor no VERI_SKILL_CLONE")
  elif [[ "$(cd "$clone_seen1016" 2>/dev/null && pwd -P)" != "$(cd "$clone1016/skills/tdd" && pwd -P)" ]]; then
    problems+=("VERI_SKILL_CLONE is '$clone_seen1016', not the clone archived from, $clone1016/skills/tdd")
  fi
  [[ "$ref_seen1016" == refs/remotes/origin/HEAD ]] ||
    problems+=("VERI_SKILL_REF is '$ref_seen1016', not the ref pinned against, refs/remotes/origin/HEAD")
fi

loose1016="$work/loose1016"
loose_skill "$loose1016"
envu1016="$work/envu1016"
rm -f "$envu1016"

( unset VERI_SKILL_UNPINNED VERI_SKILL_CLONE VERI_SKILL_REF
  launch_from "$caller" "$loose1016" GIT_CEILING_DIRECTORIES="$work" ENV_OUT="$envu1016" )

if [[ ! -f "$envu1016" ]]; then
  problems+=("the unpinned launch never reached the conductor: $(cat "$launch_err")")
elif ! grep -qx 'VERI_SKILL_UNPINNED=1' "$envu1016"; then
  problems+=("the second launch was not unpinned, so it says nothing about an unpinned launch")
else
  for var in VERI_SKILL_CLONE VERI_SKILL_REF; do
    ! grep "^${var}=" "$envu1016" > /dev/null ||
      problems+=("the unpinned launch set $(grep "^${var}=" "$envu1016")")
  done
fi

report "$name"

name="run-conductor.sh with no argument prints exactly its usage line on stderr, nothing on stdout, and exits 2"
problems=()

out_noarg="$work/noarg.out"
err_noarg="$work/noarg.err"
( cd "$work" && env PATH="$stubdir:$PATH" ARGV_OUT="$argv" \
    "$CONDUCTOR" ) > "$out_noarg" 2> "$err_noarg"
status_noarg=$?

[[ "$status_noarg" -eq 2 ]] ||
  problems+=("the script exited $status_noarg, not 2")
[[ ! -s "$out_noarg" ]] ||
  problems+=("stdout was not empty: $(cat "$out_noarg")")
printf 'usage: run-conductor.sh <issue>\n' | cmp -s - "$err_noarg" ||
  problems+=("stderr was not exactly the usage line and one newline: $(od -c "$err_noarg")")

report "$name"

name="run-conductor.sh run through a symlink to the skill directory, from another working directory, pins, snapshots and records exactly as run in place"
problems=()

remote_ln="$work/remote-ln"
clone_ln="$work/clone-ln"
cloned_skill "$remote_ln" "$clone_ln"
tip_ln="$(git -C "$clone_ln" rev-parse HEAD)"
echo "# uncommitted edit to the clone's SKILL.md" >> "$clone_ln/skills/tdd/SKILL.md"

link_ln="$work/link-ln"
ln -s "$clone_ln/skills/tdd" "$link_ln"

caller_ln="$work/caller-ln"
caller_repo "$caller_ln"
seen_ln="$work/record-ln"
rm -f "$seen_ln"
cat > "$stubdir/record-ln-hook" <<HOOK
#!/bin/sh
cp "$caller_ln/.tdd/issue-$issue-skill-commit" "$seen_ln"
HOOK
chmod +x "$stubdir/record-ln-hook"

base_ln="$work/base-ln"
mkdir -p "$base_ln"
rm -f "$prompt"
( unset VERI_NEW_SKILL; cd "$caller_ln" && env CLAUDE_BIN="$stubdir/claude" ARGV_OUT="$argv" PROMPT_OUT="$prompt" \
    BASE_OUT="$base_ln" CONDUCTOR_HOOK="$stubdir/record-ln-hook" \
    "$link_ln/scripts/run-conductor.sh" "$issue" ) >/dev/null 2>"$launch_err"

if [[ ! -f "$seen_ln" ]]; then
  problems+=("no record at $caller_ln/.tdd/issue-$issue-skill-commit while the conductor ran: $(cat "$launch_err")")
elif [[ "$(cat "$seen_ln")" != "$tip_ln" ]]; then
  problems+=("the record holds '$(cat "$seen_ln")', not the clone's tip $tip_ln")
fi

snap_ln="$(prompt_base)"
if [[ -z "$snap_ln" ]]; then
  problems+=("the prompt names no 'Base directory for this skill: <dir>' line: $(cat "$launch_err")")
elif [[ "$(cd "$snap_ln" 2>/dev/null && pwd -P)" == "$(cd "$clone_ln/skills/tdd" && pwd -P)" ]]; then
  problems+=("the base directory is the clone's own skills/tdd, not a snapshot: $snap_ln")
elif ! cmp -s <(git -C "$clone_ln" show "$tip_ln:skills/tdd/SKILL.md") "$base_ln/SKILL.md"; then
  problems+=("the snapshot's SKILL.md is not the one committed at $tip_ln")
fi
grep -q -- "$tip_ln" "$prompt" 2>/dev/null ||
  problems+=("the prompt does not name the pinned commit $tip_ln")

report "$name"

finish
