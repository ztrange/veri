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
