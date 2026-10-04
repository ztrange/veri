#!/usr/bin/env bash
# Tests for scripts/tick-issue-criterion.sh — the thin gh wrapper — driven against a
# stub `gh` on PATH.
#
# Contract under test:
#   tick-issue-criterion.sh runs with GH_REPO unset without crashing on an empty
#   repo-args array under `set -u`.
#
# Run: scripts/tests/tick-issue-criterion.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
WRAP="$HERE/../tick-issue-criterion.sh"
source "$HERE/lib/harness.sh"

stubdir="$(scratch_dir)"
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
  env VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$out" $envassign \
    "$WRAP" 7 "$matcher" >/dev/null 2>&1 && code=0 || code=$?

  local ok=1
  [[ "$code" == "$exp_code" ]] || ok=0
  if [[ "$expect_edit" == "yes" ]]; then
    [[ -f "$out" ]] && grep -q -- "- \[x\] alpha" "$out" || ok=0
  else
    [[ -f "$out" ]] && ok=0   # no edit should have been written
  fi

  if [[ "$ok" == 1 ]]; then
    ok
  else
    no "$name (exit want $exp_code got $code; edit-written=$([[ -f "$out" ]] && echo yes || echo no))"
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
env VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$stubdir/out" \
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

badpatchdir="$stubdir/bad-patch"
mkdir -p "$badpatchdir"
cat > "$badpatchdir/gh" <<'STUB'
#!/bin/sh
if [ "$1" = "issue" ] && [ "$2" = "view" ]; then
  printf '%s' "$FAKE_BODY"
elif [ "$1" = "api" ]; then
  echo "HTTP 502: Bad Gateway (https://api.github.com/repos/o/r/issues/7)" >&2
  exit 1
fi
STUB
chmod +x "$badpatchdir/gh"

bad_out="$stubdir/bad-patch-out"
env VERI_GH_DRIVER=auto PATH="$badpatchdir:$PATH" FAKE_BODY="$FAKE_BODY" \
  "$WRAP" 7 alpha > "$bad_out" 2> /dev/null && code=0 || code=$?

name="when the body PATCH fails with an HTTP 502, exits 2 with nothing on stdout"
if [[ "$code" == 2 && ! -s "$bad_out" ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name (exit want 2 got $code; stdout='$(tr '\n' '|' < "$bad_out")' want '')"
fi

noargdir="$stubdir/no-arg"
mkdir -p "$noargdir"
cat > "$noargdir/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$GH_CALLS"
STUB
chmod +x "$noargdir/gh"

noarg_out="$stubdir/no-arg-out"; noarg_err="$stubdir/no-arg-err"; noarg_calls="$stubdir/no-arg-calls"
rm -f "$noarg_calls"
env PATH="$noargdir:$PATH" GH_CALLS="$noarg_calls" \
  "$WRAP" > "$noarg_out" 2> "$noarg_err" && code=0 || code=$?

name="with no argument, exits 2 with nothing on stdout, the usage line alone on stderr, and no gh call"
problems=()
[[ "$code" == 2 ]] || problems+=("exit want 2 got $code")
[[ ! -s "$noarg_out" ]] || problems+=("stdout='$(tr '\n' '|' < "$noarg_out")' want ''")
[[ "$(cat "$noarg_err")" == "usage: tick-issue-criterion.sh <issue-number> <matcher>" ]] \
  || problems+=("stderr='$(tr '\n' '|' < "$noarg_err")' want 'usage: tick-issue-criterion.sh <issue-number> <matcher>'")
[[ ! -e "$noarg_calls" ]] || problems+=("gh calls='$(tr '\n' '|' < "$noarg_calls")' want none")
report "$name"

ln -s "$(cd "$HERE/../.." && pwd)" "$stubdir/linked-skill"
mkdir -p "$stubdir/elsewhere"
in_place_edit="$stubdir/in-place-edit"; linked_edit="$stubdir/linked-edit"
rm -f "$in_place_edit" "$linked_edit"
in_place="$(env VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$in_place_edit" \
  "$WRAP" 7 alpha 2>&1)" && in_place_code=0 || in_place_code=$?
linked="$(cd "$stubdir/elsewhere" && env VERI_GH_DRIVER=auto PATH="$stubdir:$PATH" FAKE_BODY="$FAKE_BODY" FAKE_OUT="$linked_edit" \
  "$stubdir/linked-skill/scripts/tick-issue-criterion.sh" 7 alpha 2>&1)" && linked_code=0 || linked_code=$?

name="run through a symlink to the skill directory and from another working directory, ticks the box and PATCHes the same body with the same exit and output as when run in place"
problems=()
[[ "$in_place_code" == 0 ]] || problems+=("in place: exit want 0 got $in_place_code")
[[ "$linked_code" == "$in_place_code" ]] || problems+=("linked: exit want $in_place_code got $linked_code")
[[ "$linked" == "$in_place" ]] || problems+=("linked output='$(tr '\n' '|' <<< "$linked")' want '$(tr '\n' '|' <<< "$in_place")'")
[[ -f "$in_place_edit" ]] && grep -F -- "- [x] alpha" "$in_place_edit" > /dev/null \
  || problems+=("in place: no ticked body PATCHed")
[[ -f "$linked_edit" ]] && cmp -s "$in_place_edit" "$linked_edit" \
  || problems+=("linked: PATCHed body differs from in place (written=$([[ -f "$linked_edit" ]] && echo yes || echo no))")
report "$name"

faileditdir="$stubdir/failed-edit"
mkdir -p "$faileditdir"
cat > "$faileditdir/gh" <<'STUB'
#!/bin/sh
case "$*" in
  "issue view"*) cat "$REMOTE_BODY" ;;
  "issue edit"*) printf 'overwritten by issue edit\n' > "$REMOTE_BODY" ;;
  "api -X PATCH"*) exit "$FAKE_EDIT_STATUS" ;;
  "api "*) python3 -c 'import json, sys; print(json.dumps({"body": open(sys.argv[1]).read()}))' "$REMOTE_BODY" ;;
esac
STUB
chmod +x "$faileditdir/gh"

name="when gh fails on the body edit with status 1, 3 or 5, exits 2 and leaves the issue body unchanged (#775)"
problems=()
remote_body="$stubdir/failed-edit-body"
for status in 1 3 5; do
  printf '%s\n' "$FAKE_BODY" > "$remote_body"
  env PATH="$faileditdir:$PATH" REMOTE_BODY="$remote_body" FAKE_EDIT_STATUS="$status" \
    "$WRAP" 7 alpha > /dev/null 2>&1 && code=0 || code=$?
  [[ "$code" == 2 ]] || problems+=("gh edit exit $status: exit want 2 got $code")
  [[ "$(cat "$remote_body")" == "$FAKE_BODY" ]] \
    || problems+=("gh edit exit $status: body='$(tr '\n' '|' < "$remote_body")' want '$(tr '\n' '|' <<< "$FAKE_BODY")'")
done
report "$name"

finish
