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

name="a done run whose PR body holds an unticked checkbox that is not human-owed exits 0 and prints nothing"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
body='Closes #4242

- [ ] a follow-up someone may file later'
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

name="a stopped run with a clean ledger exits 1 and prints a not-done line naming the stopped state"
repo="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"stop","mode":"graceful"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
out="$(cd "$repo" && "$FINISHED" 4242 2>/dev/null)" && code=0 || code=$?
if [[ "$code" != 1 ]]; then
  no "$name (want exit 1, got $code: $out)"
elif [[ "$out" != "not-done stopped"* ]]; then
  no "$name (stdout: $out)"
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

name="a done run whose ledger has unchecked steps exits 1 and prints one unchecked line per unchecked step"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  '- [ ] second step ⟦criterion 2⟧' '- [ ] third step ⟦criterion 3⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
body='Closes #4242'
case " $* " in
  *" --json "*) printf '{"body": "%s"}\n' "$body" ;;
  *) printf '%s\n' "$body" ;;
esac
STUB
chmod +x "$bin/gh"
out="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>/dev/null)" && code=0 || code=$?
if [[ "$code" != 1 ]]; then
  no "$name (want exit 1, got $code: $out)"
elif [[ "$out" != $'unchecked '*"second step"*$'\n'"unchecked "*"third step"* || "$out" == *"first step"* ]]; then
  no "$name (stdout: $out)"
else
  ok
fi

name="a done run whose ledger has a step still refactor-pending exits 1 and prints one refactor-pending line per such step"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  '- [x] second step ⟦criterion 2⟧ ⟂ refactor pending' '- [x] third step ⟦criterion 3⟧ ⟂ refactor pending' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
body='Closes #4242'
case " $* " in
  *" --json "*) printf '{"body": "%s"}\n' "$body" ;;
  *) printf '%s\n' "$body" ;;
esac
STUB
chmod +x "$bin/gh"
out="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>/dev/null)" && code=0 || code=$?
if [[ "$code" != 1 ]]; then
  no "$name (want exit 1, got $code: $out)"
elif [[ "$out" != $'refactor-pending '*"second step"*$'\n'"refactor-pending "*"third step"* || "$out" == *"first step"* ]]; then
  no "$name (stdout: $out)"
else
  ok
fi

name="a done run whose PR body holds unticked human-owed lines exits 1 and prints one human-owed line per unticked line"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
body='Closes #4242

- [ ] a reviewer checks the page ⟦human-owed⟧ ⟦criterion 3⟧
- [x] a reviewer checks the ticked one ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] a reviewer reads the docs ⟦human-owed⟧ ⟦criterion 5⟧'
case " $* " in
  *" --json "*) printf '{"body": "%s"}\n' "$(printf '%s' "$body" | sed 's/$/\\n/' | tr -d '\n')" ;;
  *) printf '%s\n' "$body" ;;
esac
STUB
chmod +x "$bin/gh"
out="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>/dev/null)" && code=0 || code=$?
if [[ "$code" != 1 ]]; then
  no "$name (want exit 1, got $code: $out)"
elif [[ "$out" != $'human-owed '*"checks the page"*$'\n'"human-owed "*"reads the docs"* || "$out" == *"ticked one"* ]]; then
  no "$name (stdout: $out)"
else
  ok
fi

name="a done run whose PR body cannot be read exits 2 and says on stderr the PR body could not be read"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<'STUB'
#!/bin/sh
echo "gh: HTTP 502" >&2
exit 1
STUB
chmod +x "$bin/gh"
err="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" != 2 ]]; then
  no "$name (want exit 2, got $code: $err)"
elif [[ "$err" != *"PR body"* ]]; then
  no "$name (stderr: $err)"
else
  ok
fi

name="a run of it changes no file in the repository and every gh call it makes is a read"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
calls="$(scratch_dir)/calls"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":"https://github.com/o/r/pull/7"}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  '- [ ] second step ⟦criterion 2⟧' > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<STUB
#!/bin/sh
echo "\$*" >> "$calls"
printf '{"body": "Closes #4242"}\n'
STUB
chmod +x "$bin/gh"
tree_digest() {
  (cd "$repo" && find . -path ./.git -prune -o -path ./.tdd/wt/4242/.git -prune -o -type f -exec cksum {} + | sort)
  for g in "$repo" "$repo/.tdd/wt/4242"; do
    git -C "$g" for-each-ref
    git -C "$g" config --list --local
    git -C "$g" status --porcelain
  done
}
before="$(tree_digest)"
(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 >/dev/null 2>&1) || true
after="$(tree_digest)"
if [[ "$before" != "$after" ]]; then
  no "$name (files changed: $(diff <(echo "$before") <(echo "$after")))"
elif [[ ! -s "$calls" ]]; then
  no "$name (the stub gh was never called)"
elif grep -E -i -e 'POST|PATCH|PUT|DELETE|-X|--method|--input|-f |-F ' "$calls" > /dev/null \
  || grep -v -E '^pr view ' "$calls" > /dev/null; then
  no "$name (gh calls: $(cat "$calls"))"
else
  ok
fi

name="a done run with an empty recorded PR URL exits 2 with one stderr line saying no PR is recorded and never calls gh pr view (#1748)"
repo="$(scratch_dir)"
bin="$(scratch_dir)"
calls="$(scratch_dir)/calls"
new_repo "$repo"
mkdir -p "$repo/.tdd/wt/4242/.tdd"
git -C "$repo" commit -q --allow-empty -m init
new_repo "$repo/.tdd/wt/4242"
printf '%s\n' \
  '{"ts":1000,"event":"launch","step":"1","phase":"red","actor":"developer","name":"develop-red"}' \
  '{"ts":1001,"event":"done","pr":""}' > "$repo/.tdd/wt/4242/.tdd/events.jsonl"
printf '%s\n' '# Plan for #4242 — a title' '' '- [x] first step ⟦criterion 1⟧' \
  > "$repo/.tdd/wt/4242/.tdd/issue-4242.md"
cat > "$bin/gh" <<STUB
#!/bin/sh
echo "\$*" >> "$calls"
printf '{"body": "Closes #4242"}\n'
STUB
chmod +x "$bin/gh"
err="$(cd "$repo" && PATH="$bin:$PATH" "$FINISHED" 4242 2>&1 >/dev/null)" && code=0 || code=$?
if [[ "$code" != 2 ]]; then
  no "$name (want exit 2, got $code: $err)"
elif [[ "$err" != *"no PR"* || "$err" == *$'\n'* ]]; then
  no "$name (stderr: $err)"
elif [[ -s "$calls" ]]; then
  no "$name (gh was called: $(cat "$calls"))"
else
  ok
fi

finish
