#!/usr/bin/env bash
# Tests for scripts/tick-issue-criterion.sh — the thin gh wrapper — driven against a
# stub `gh` on PATH (no network, no real issue). Zero-dependency plain-shell asserts.
#
# Regression target: the wrapper must not crash when GH_REPO is unset (empty repo-args
# array under `set -u` on bash 3.2).
#
# Run: scripts/tests/tick-issue-criterion.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WRAP="$HERE/../tick-issue-criterion.sh"
pass=0 fail=0

stubdir="$(mktemp -d)"
trap 'rm -rf "$stubdir"' EXIT
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
if [ "$1" = "issue" ] && [ "$2" = "view" ]; then
  printf '%s' "$FAKE_BODY"
elif [ "$1" = "issue" ] && [ "$2" = "edit" ]; then
  prev=""
  for a in "$@"; do
    [ "$prev" = "--body-file" ] && cp "$a" "$FAKE_OUT"
    prev="$a"
  done
fi
STUB
chmod +x "$stubdir/gh"

FAKE_BODY='- [ ] alpha criterion
- [ ] beta criterion'

run() {  # run <name> <expected-exit> <expect-edit:yes|no> <env-assignment> <matcher>
  local name="$1" exp_code="$2" expect_edit="$3" envassign="$4" matcher="$5"
  local out="$stubdir/out"; rm -f "$out"
  local code
  env PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$out" $envassign \
    "$WRAP" 7 "$matcher" >/dev/null 2>&1 && code=0 || code=$?

  local ok=1
  [[ "$code" == "$exp_code" ]] || ok=0
  if [[ "$expect_edit" == "yes" ]]; then
    [[ -f "$out" ]] && grep -q -- "- \[x\] alpha" "$out" || ok=0
  else
    [[ -f "$out" ]] && ok=0   # no edit should have been written
  fi

  if [[ "$ok" == 1 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name (exit want $exp_code got $code; edit-written=$([[ -f "$out" ]] && echo yes || echo no))"
  fi
}

run "no GH_REPO ticks" 0 yes "" "alpha"

run "with GH_REPO ticks" 0 yes "GH_REPO=owner/name" "alpha"

run "no match no edit" 3 no "" "nonexistent"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
