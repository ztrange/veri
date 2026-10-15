#!/usr/bin/env bash
# Tests for scripts/run-conductor.sh — the conductor invocation, driven against a stub
# `claude` that records its argv to $ARGV_OUT and its stdin to $PROMPT_OUT.
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
    -p|--verbose|--output-format|--permission-mode|--model) ;;
    -*) echo "error: unknown option '$arg'" >&2; exit 1 ;;
  esac
done
printf '%s\n' "$@" > "$ARGV_OUT"
cat > "${PROMPT_OUT:-/dev/null}"
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
  mkdir -p "$1/skills/tdd"
  git -C "$HERE/../.." ls-files -z |
    tar -C "$HERE/../.." --null -T - -cf - | tar -C "$1/skills/tdd" -xf -
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

name="run-conductor.sh sent SIGTERM while its claude runs keeps the snapshot until claude exits, then removes it and exits 143"
problems=()
source "$HERE/../lib/background.sh"

termstub="$(scratch_dir)"
termwork="$(scratch_dir)"
claude_stub "$termstub" "$(cat <<'STUB'
cat > "$PROMPT_OUT"
echo started > "$STARTED"
read -r _ < "$RELEASE"
exit 0
STUB
)"
mkdir -p "$termwork/caller"
mkfifo "$termwork/started" "$termwork/release"
exec {term_started}<>"$termwork/started" {term_release}<>"$termwork/release"
on_exit bg_kill "$termwork/record"
bg_start "$termwork/record" env CLAUDE_BIN="$termstub/claude" PROMPT_OUT="$termwork/prompt" \
  STARTED="$termwork/started" RELEASE="$termwork/release" \
  sh -c 'cd "$1" && exec "$2" "$3"' sh "$termwork/caller" "$CONDUCTOR" "$issue" \
  >/dev/null 2>"$termwork/err"
read -r term_pid _ < "$termwork/record"

if ! read -t 60 -r _ <&"$term_started"; then
  problems+=("claude never started: $(cat "$termwork/err")")
else
  term_snap="$(head -n 1 < <(sed -n 's/^Base directory for this skill: //p' "$termwork/prompt"))"
  kill -TERM "$term_pid"
  if [[ -z "$term_snap" ]]; then
    problems+=("the prompt names no 'Base directory for this skill: <dir>' line")
  elif [[ ! -d "$term_snap" ]]; then
    problems+=("the snapshot $term_snap was gone after SIGTERM while claude still ran")
  fi
fi
echo go >&"$term_release"
wait "$term_pid"
term_status=$?
bg_kill "$termwork/record"
exec {term_started}>&- {term_release}>&-

[[ "$term_status" -eq 143 ]] ||
  problems+=("the script exited $term_status, not 143: $(cat "$termwork/err")")
[[ -z "${term_snap:-}" || ! -e "$term_snap" ]] ||
  problems+=("the snapshot $term_snap was left behind after the script exited")

report "$name"

name="run-conductor.sh sent SIGINT alone while its claude runs waits for claude, removes the snapshot, prints no traceback and exits with claude's status (#1219)"
problems=()

intstub="$(scratch_dir)"
intwork="$(scratch_dir)"
claude_stub "$intstub" "$(cat <<'STUB'
cat > "$PROMPT_OUT"
echo started > "$STARTED"
read -r _ < "$RELEASE"
exit 5
STUB
)"
mkdir -p "$intwork/caller"
mkfifo "$intwork/started" "$intwork/release"
exec {int_started}<>"$intwork/started" {int_release}<>"$intwork/release"
on_exit bg_kill "$intwork/record"
# hazard: a non-interactive shell starts `&` children with SIGINT ignored, and an ignored-on-entry signal cannot be reset from sh.
bg_start "$intwork/record" env CLAUDE_BIN="$intstub/claude" PROMPT_OUT="$intwork/prompt" \
  STARTED="$intwork/started" RELEASE="$intwork/release" \
  python3 -c 'import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])' \
  sh -c 'cd "$1" && exec "$2" "$3"' sh "$intwork/caller" "$CONDUCTOR" "$issue" \
  >/dev/null 2>"$intwork/err"
read -r int_pid _ < "$intwork/record"

if ! read -t 60 -r _ <&"$int_started"; then
  problems+=("claude never started: $(cat "$intwork/err")")
else
  int_snap="$(head -n 1 < <(sed -n 's/^Base directory for this skill: //p' "$intwork/prompt"))"
  kill -INT "$int_pid"
fi
echo go >&"$int_release"
wait "$int_pid"
int_status=$?
bg_kill "$intwork/record"
exec {int_started}>&- {int_release}>&-

[[ "$int_status" -eq 5 ]] ||
  problems+=("the script exited $int_status, not claude's 5: $(cat "$intwork/err")")
! grep -F Traceback "$intwork/err" > /dev/null ||
  problems+=("stderr carries a traceback: $(cat "$intwork/err")")
[[ -n "${int_snap:-}" && ! -e "$int_snap" ]] ||
  problems+=("the snapshot '${int_snap:-}' was not named or was left behind after the script exited")

report "$name"

name="run-conductor.sh sent SIGHUP alone while its claude runs waits for claude, removes the snapshot, prints no traceback and exits with claude's status (#1219)"
problems=()

hupstub="$(scratch_dir)"
hupwork="$(scratch_dir)"
claude_stub "$hupstub" "$(cat <<'STUB'
cat > "$PROMPT_OUT"
echo started > "$STARTED"
read -r _ < "$RELEASE"
exit 5
STUB
)"
mkdir -p "$hupwork/caller"
mkfifo "$hupwork/started" "$hupwork/release"
exec {hup_started}<>"$hupwork/started" {hup_release}<>"$hupwork/release"
on_exit bg_kill "$hupwork/record"
bg_start "$hupwork/record" env CLAUDE_BIN="$hupstub/claude" PROMPT_OUT="$hupwork/prompt" \
  STARTED="$hupwork/started" RELEASE="$hupwork/release" \
  sh -c 'cd "$1" && exec "$2" "$3"' sh "$hupwork/caller" "$CONDUCTOR" "$issue" \
  >/dev/null 2>"$hupwork/err"
read -r hup_pid _ < "$hupwork/record"

if ! read -t 60 -r _ <&"$hup_started"; then
  problems+=("claude never started: $(cat "$hupwork/err")")
else
  hup_snap="$(head -n 1 < <(sed -n 's/^Base directory for this skill: //p' "$hupwork/prompt"))"
  kill -HUP "$hup_pid"
fi
echo go >&"$hup_release"
wait "$hup_pid"
hup_status=$?
bg_kill "$hupwork/record"
exec {hup_started}>&- {hup_release}>&-

[[ "$hup_status" -eq 5 ]] ||
  problems+=("the script exited $hup_status, not claude's 5: $(cat "$hupwork/err")")
! grep -F Traceback "$hupwork/err" > /dev/null ||
  problems+=("stderr carries a traceback: $(cat "$hupwork/err")")
[[ -n "${hup_snap:-}" && ! -e "$hup_snap" ]] ||
  problems+=("the snapshot '${hup_snap:-}' was not named or was left behind after the script exited")

report "$name"

finish
