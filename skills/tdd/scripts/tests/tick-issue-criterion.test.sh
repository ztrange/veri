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
elif [ "$1" = "api" ]; then
  for a in "$@"; do
    case "$a" in body=@*) cp "${a#body=@}" "$FAKE_OUT" ;; esac
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

refuseddir="$stubdir/refused"
mkdir -p "$refuseddir"
python3 -c 'import json, sys; print(json.dumps({"number": 7, "body": sys.argv[1], "labels": []}))' \
  "$FAKE_BODY" > "$refuseddir/issue.json"
cat > "$refuseddir/gh" <<'STUB'
#!/bin/sh
refusal='GitHub GraphQL is not available from Claude Code sessions; use the REST API (gh api repos/{owner}/{repo}/...)'
unexpected() { echo "gh stub: unexpected call: gh $*" >&2; exit 1; }
case "$1" in
  issue|pr|repo) echo "HTTP 403: $refusal" >&2; exit 1 ;;
esac
case "$*" in
  "api graphql"*) echo "HTTP 403: $refusal" >&2; exit 1 ;;
  *-q*|*--jq*|*--template*) unexpected "$@" ;;
  "api "*"repos/"*"/issues/7"|"api "*"repos/"*"/issues/7 "*) ;;
  *) unexpected "$@" ;;
esac
case "$*" in
  *PATCH*)
    : > "$FAKE_OUT"
    prev=""
    for a in "$@"; do
      printf '%s\n' "$a" >> "$FAKE_OUT"
      case "$a" in
        *=@-) cat >> "$FAKE_OUT" ;;
        *=@*) cat "${a#*=@}" >> "$FAKE_OUT" ;;
      esac
      if [ "$prev" = "--input" ]; then
        if [ "$a" = "-" ]; then cat >> "$FAKE_OUT"; else cat "$a" >> "$FAKE_OUT"; fi
      fi
      prev="$a"
    done
    echo '{}' ;;
  *-f*|*-F*|*--field*|*--raw-field*|*--input*|*-X*|*--method*) unexpected "$@" ;;
  *) cat "$REFUSED_DIR/issue.json" ;;
esac
STUB
chmod +x "$refuseddir/gh"

working_out="$stubdir/working-out"; refused_out="$stubdir/refused-out"; edit="$stubdir/refused-edit"
working_err="$stubdir/working-err"; refused_err="$stubdir/refused-err"
rm -f "$stubdir/out" "$edit"
env PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$stubdir/out" \
  "$WRAP" 7 alpha > "$working_out" 2> "$working_err" && working_code=0 || working_code=$?
env PATH="$refuseddir:$PATH" REFUSED_DIR="$refuseddir" FAKE_OUT="$edit" \
  "$WRAP" 7 alpha > "$refused_out" 2> "$refused_err" && code=0 || code=$?

name="under a gh that refuses GraphQL and answers REST, ticks the criterion over REST with the same stdout and exit as a working gh (#568)"
ok=1
[[ "$working_code" == 0 && "$code" == "$working_code" ]] || ok=0
cmp -s "$working_out" "$refused_out" && same=yes || { same=no; ok=0; }
[[ -f "$edit" ]] && grep -F -- "- [x] alpha" "$edit" > /dev/null || ok=0
if [[ "$ok" == 1 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (exit want $working_code got $code; stdout same=$same; edit-written=$([[ -f "$edit" ]] && echo yes || echo no))"
fi

name="under a gh that refuses GraphQL, writes nothing to stderr, the same as against a working gh: the refusal is not passed through (#568)"
if [[ ! -s "$working_err" && ! -s "$refused_err" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (working gh stderr='$(tr '\n' '|' < "$working_err")' want ''; GraphQL refused stderr='$(tr '\n' '|' < "$refused_err")' want '')"
fi

silentdir="$stubdir/silent"
mkdir -p "$silentdir"
cp "$refuseddir/issue.json" "$silentdir/issue.json"
sed 's/^case "\$1" in$/[ "\$1 \$2" = "issue edit" ] \&\& exit 0\
case "$1" in/' "$refuseddir/gh" > "$silentdir/gh"
chmod +x "$silentdir/gh"

silent_edit="$stubdir/silent-edit"; rm -f "$silent_edit"
env PATH="$silentdir:$PATH" REFUSED_DIR="$silentdir" FAKE_OUT="$silent_edit" \
  "$WRAP" 7 alpha > /dev/null 2>&1 && code=0 || code=$?

name="under a gh whose issue subcommands succeed without doing anything, writes the ticked body through gh api only (#568)"
if [[ "$code" == 0 && -f "$silent_edit" ]] && grep -F -- "- [x] alpha" "$silent_edit" > /dev/null; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (exit want 0 got $code; edit-written=$([[ -f "$silent_edit" ]] && echo yes || echo no))"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
