#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   classify-bail.sh killed-stuck         → first stdout line `system`,  exit 0
#   classify-bail.sh <unrecognised>       → error on stderr, exit non-zero
#
# Run: scripts/tests/unit/classify-bail.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLASSIFY="$HERE/../../classify-bail.sh"
source "$HERE/../lib/harness.sh"

check() {
  local name="$1" cause="$2" exp_code="$3" exp_out="$4" out code first
  out="$("$CLASSIFY" "$cause")" && code=0 || code=$?
  first="$(head -n1 <<< "$out")"
  if [[ "$code" == "$exp_code" && "$first" == "$exp_out" ]]; then
    ok
  else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$first") | sed 's/^/    /'
  fi
}

check_nonzero() {
  local name="$1" cause="$2" code
  "$CLASSIFY" "$cause" >/dev/null 2>&1 && code=0 || code=$?
  if [[ "$code" != 0 ]]; then
    ok
  else
    no "$name (want non-zero exit, got $code)"
  fi
}

check "killed-stuck is system" killed-stuck 0 system

check_nonzero "unknown cause exits non-zero" wat

refuse_name="an unknown cause writes its refusal and the usage line on stderr, nothing on stdout, exit 2"
refuse_err="$(mktemp)"
refuse_out="$("$CLASSIFY" bogus 2>"$refuse_err")" && code=0 || code=$?
refuse_got="$(cat "$refuse_err")"
rm -f "$refuse_err"
refuse_want="classify-bail: unknown cause: bogus
usage: classify-bail.sh <cause>"
if [[ "$code" == 2 && -z "$refuse_out" && "$refuse_got" == "$refuse_want" ]]; then
  ok
else
  no "$refuse_name (want exit 2 and no stdout, got exit $code, stdout '$refuse_out')"
  diff <(printf '%s\n' "$refuse_want") <(printf '%s\n' "$refuse_got") | sed 's/^/    /'
fi

linked_name="classify-bail.sh run through a symlink to the skill directory and from another working directory answers killed-stuck and an unknown cause as it does in place"
linked_bad=""
linked_work="$(scratch_dir)"
ln -s "$(cd "$HERE/../../.." && pwd)" "$linked_work/linked-skill"
mkdir -p "$linked_work/elsewhere"
for cause in killed-stuck bogus; do
  in_place_out="$("$CLASSIFY" "$cause" 2>"$linked_work/in-place.err")" && in_place_code=0 || in_place_code=$?
  in_place_err="$(cat "$linked_work/in-place.err")"
  linked_out="$(cd "$linked_work/elsewhere" && "$linked_work/linked-skill/scripts/classify-bail.sh" "$cause" 2>"$linked_work/linked.err")" && linked_code=0 || linked_code=$?
  linked_err="$(cat "$linked_work/linked.err")"
  if [[ "$linked_out" != "$in_place_out" || "$linked_err" != "$in_place_err" || "$linked_code" != "$in_place_code" ]]; then
    linked_bad+="    $cause in place: exit $in_place_code, stdout '$in_place_out', stderr '$in_place_err'"$'\n'
    linked_bad+="    $cause through the symlink from elsewhere: exit $linked_code, stdout '$linked_out', stderr '$linked_err'"$'\n'
  fi
done
[[ "$in_place_code" == 2 ]] || linked_bad+="    bogus in place: want exit 2, got exit $in_place_code"$'\n'
rm -rf "$linked_work"
if [[ -z "$linked_bad" ]]; then
  ok
else
  no "$linked_name"
  printf '%s' "$linked_bad"
fi

finish
