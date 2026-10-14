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

name="a ref lock that is never released makes the launch refuse with exit 2 once the retry bound, past today's five fetches, is reached, launching no conductor and naming the ref lock in the conductor's own line, whichever wording git used (#1012, #1306)"
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
grep -F 'run-conductor: another process holds the ref lock' "$launch_err" > /dev/null 2>&1 ||
  problems+=("stderr does not carry the conductor's line naming the ref lock ('another process holds the ref lock') — stderr was: '$(tr '\n' ' ' < "$launch_err")'")
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

name="loose_skill copies only the files git tracks under skills/tdd: an untracked or ignored cache never reaches the copy (#1169)"
problems=()

src44="$work/src44"
new_repo "$src44"
mkdir -p "$src44/skills/tdd/scripts/tests" "$src44/skills/tdd/scripts/veri/__pycache__"
echo skill > "$src44/skills/tdd/SKILL.md"
echo '__pycache__/' > "$src44/.gitignore"
git -C "$src44" add -A
git -C "$src44" commit -qm skill
echo stray > "$src44/skills/tdd/untracked.txt"
echo cache > "$src44/skills/tdd/scripts/veri/__pycache__/mod.pyc"

dest44="$work/dest44"
( HERE="$src44/skills/tdd/scripts/tests"; loose_skill "$dest44" )

if [[ ! -f "$dest44/skills/tdd/SKILL.md" ]]; then
  problems+=("the copy is missing the tracked SKILL.md")
fi
for stray44 in untracked.txt scripts/veri/__pycache__; do
  [[ ! -e "$dest44/skills/tdd/$stray44" ]] ||
    problems+=("the copy carries $stray44, which git does not track")
done

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
