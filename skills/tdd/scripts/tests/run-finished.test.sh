#!/usr/bin/env bash
# Tests for scripts/run-finished.sh — whether a run is safe to merge.
#
# Run: scripts/tests/run-finished.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FINISHED="$HERE/../run-finished.sh"
source "$HERE/lib/harness.sh"

name="an issue with no run under .tdd/wt/ exits 2 and says on stderr there is no run for it"
repo="$(scratch_dir)"
git -C "$repo" init -q
mkdir -p "$repo/.tdd/wt"
err="$(cd "$repo" && "$FINISHED" 4242 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" != 2 ]]; then
  no "$name (want exit 2, got $code)"
elif [[ "$err" != *"no run for issue 4242"* ]]; then
  no "$name (stderr: $err)"
else
  ok
fi

name="a done run with every step ticked, none refactor-pending and its PR body's human-owed line ticked exits 0 and prints nothing"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' '- [x] second step ⟦criterion 2⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
body='Closes #4242

- [x] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧'
case " $* " in
  *" --json "*) printf '{"body": "%s"}\n' "$(printf '%s' "$body" | sed 's/$/\\n/' | tr -d '\n')" ;;
  *) printf '%s\n' "$body" ;;
esac
STUB
chmod +x "$bin/gh"
out="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>&1)" && code=0 || code=$?
if [[ "$code" != 0 ]]; then
  no "$name (want exit 0, got $code: $out)"
elif [[ -n "$out" ]]; then
  no "$name (want no output, got: $out)"
else
  ok
fi

name="a run whose state is not done exits 1 and prints a not-done line naming the state"
repo="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"bail","phase":"red","classification":"process"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
out="$(cd "$repo" && "$FINISHED" 4242 2>/dev/null)" && code=0 || code=$?
if [[ "$code" != 1 ]]; then
  no "$name (want exit 1, got $code: $out)"
elif [[ "$out" != "not-done bailed"* ]]; then
  no "$name (stdout: $out)"
else
  ok
fi

finish
