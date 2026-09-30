#!/usr/bin/env bash
# Unit tests for scripts/push-branch.sh — the script sourced, never executed, with every
# command it shells out to mocked as a same-named shell function.
#
# push-branch.sh is the script chosen as the first migration's worked example (#339), picked
# by a process-count proxy, not measured seconds: its integration suite
# (tests/push-branch.test.sh) builds a real git repository and pushes to a real bare remote,
# so every one of its 11 cases starts git processes, while the script itself is 85 lines of
# logic small enough to move behind functions in one issue.
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/push-branch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PUSH="$HERE/../../push-branch.sh"
source "$HERE/../lib/harness.sh"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

show_run() {  # show_run <exit> <stdout-file> <stderr-file> — print what a failing case got
  echo "    exit $1"; echo "    stdout: $(printf '%q' "$(cat "$2")")"
  echo "    stderr: $(printf '%q' "$(cat "$3")")"
}

# 1. sourcing the script runs nothing: no git call, no exit out of the sourcing shell, and a
#    `main` function left defined for a caller to run
name="sourcing push-branch.sh runs nothing and defines main"
calls="$scratch/calls"
: > "$calls"
got="$(
  git() { echo "git $*" >> "$calls"; return 0; }
  sleep() { echo "sleep $*" >> "$calls"; return 0; }
  source "$PUSH"
  echo "source returned"
  declare -F main >/dev/null && echo "main defined"
)"
want="source returned
main defined"
if [[ -s "$calls" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name (sourcing ran commands, want none):"; cat "$calls"
elif [[ "$got" != "$want" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name"; diff <(echo "$want") <(echo "$got")
else
  pass=$((pass + 1))
fi

# 2. executed directly, the guard still runs main and the CLI contract is byte-identical to
#    the one the integration suite (tests/push-branch.test.sh, left unmodified) holds the
#    script to: a bad tunable is caught before any push — nothing on stdout, exactly one
#    stderr line naming the tunable and the value, exit 2. No git, gh or sleep runs on this
#    path, which is why it can be checked here without a mock.
name="executed directly, push-branch.sh keeps its CLI contract: VERI_PUSH_RETRIES=x prints nothing on stdout, one exact stderr line, and exits 2"
out="$scratch/out" err="$scratch/err"
VERI_PUSH_RETRIES=x VERI_PUSH_BACKOFF=0 "$PUSH" > "$out" 2> "$err"
rc=$?
want_err="push-branch.sh: VERI_PUSH_RETRIES must be a non-negative integer, got 'x'"
if [[ "$rc" -ne 2 || -s "$out" || "$(cat "$err")" != "$want_err" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name (want exit 2, empty stdout, stderr '$want_err'):"
  show_run "$rc" "$out" "$err"
else
  pass=$((pass + 1))
fi

# 3. sourced, with git, sleep and the event recording mocked as same-named functions and PATH
#    an empty directory, main runs the whole failed-push path in-process: every attempt
#    pushes, one wait between the two, one push-failed event, one stderr line, exit 0 — and
#    no real process is started, since PATH holds nothing one could be started from
name="sourced with git, sleep and record mocked as functions and PATH empty, main runs a failed push to its push-failed event, starting no real process"
calls="$scratch/calls3" err="$scratch/err3" nobin="$scratch/nobin"
mkdir -p "$nobin"
: > "$calls"
(
  source "$PUSH"
  git() { echo "git $*" >> "$calls"; echo "fatal: unable to access origin"; return 128; }
  sleep() { echo "sleep $*" >> "$calls"; return 0; }
  record() { echo "record $*" >> "$calls"; return 0; }
  PATH="$nobin"
  VERI_PUSH_RETRIES=1
  unset VERI_PUSH_BACKOFF
  main
) > "$scratch/out3" 2> "$err"
rc=$?
want_calls="git push --set-upstream origin HEAD
sleep 2
git push --set-upstream origin HEAD
record push-failed error=fatal: unable to access origin attempts=2"
want_err="push-branch.sh: push failed after 2 attempts; the branch is not on the remote"
if [[ "$rc" -ne 0 || -s "$scratch/out3" || "$(cat "$err")" != "$want_err" || "$(cat "$calls")" != "$want_calls" ]]; then
  fail=$((fail + 1)); echo "FAIL - $name (want exit 0, empty stdout, stderr '$want_err'):"
  show_run "$rc" "$scratch/out3" "$err"
  diff <(echo "$want_calls") "$calls"
else
  pass=$((pass + 1))
fi

# 4. this suite's own header comment — the `#` lines between the shebang and the first line of
#    code — says why push-branch.sh is the script migrated first (#339): it was chosen by a
#    process-count proxy, not by measured seconds. Read with bash alone, so it starts nothing.
name="the unit suite's header comment records push-branch.sh as the chosen script, by a process-count proxy and not measured seconds"
header=""
{
  read -r _shebang
  while IFS= read -r line && [[ "$line" == \#* ]]; do header+="$line"$'\n'; done
} < "$HERE/push-branch.test.sh"
header="${header//$'\n'# / }"
missing=()
[[ "$header" =~ push-branch\.sh[^.]*chosen|chosen[^.]*push-branch\.sh ]] || missing+=("push-branch.sh named as the chosen script")
[[ "$header" == *"process-count proxy"* ]] || missing+=("'process-count proxy'")
[[ "$header" =~ not[[:space:]]+(by[[:space:]]+)?(a[[:space:]]+)?measured([[:space:]]+wall-clock)?[[:space:]]+second ]] || missing+=("'not measured seconds'")
if [[ "${#missing[@]}" -gt 0 ]]; then
  fail=$((fail + 1)); echo "FAIL - $name (header lacks: ${missing[*]}):"; printf '%s' "$header"
else
  pass=$((pass + 1))
fi

finish
