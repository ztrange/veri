#!/usr/bin/env bash
# Unit tests for scripts/classify-bail.sh — classifies a bail's <cause> into a category.
# Given a cause as $1, print the category on the first stdout line and exit 0.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Contract under test:
#   classify-bail.sh killed-stuck         → first stdout line `system`,  exit 0
#   classify-bail.sh no-verdict           → first stdout line `system`,  exit 0
#   classify-bail.sh revise-exhausted     → first stdout line `process`, exit 0
#   classify-bail.sh reconcile-failed     → first stdout line `system`,  exit 0
#   classify-bail.sh untestable-criterion → first stdout line `process`, exit 0
#   classify-bail.sh step-too-big         → first stdout line `process`, exit 0
#   classify-bail.sh rebase-unresolved    → first stdout line `process`, exit 0
#   classify-bail.sh uncovered            → first stdout line `process`, exit 0
#   classify-bail.sh suite-red            → first stdout line `process`, exit 0
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

check "no-verdict is system" no-verdict 0 system

check "revise-exhausted is process" revise-exhausted 0 process

check_nonzero "unknown cause exits non-zero" wat

check "reconcile-failed is system" reconcile-failed 0 system

check "untestable-criterion is process" untestable-criterion 0 process

check "step-too-big is process" step-too-big 0 process

check "rebase-unresolved is process" rebase-unresolved 0 process

stop_name="stop words are unknown causes, exit 2"
stop_bad=""
for cause in stopped stop at-ledger at-leaf now; do
  out="$("$CLASSIFY" "$cause" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 && -z "$out" ]] || stop_bad+="    $cause: want exit 2 and no stdout, got exit $code, stdout '$out'"$'\n'
done
if [[ -z "$stop_bad" ]]; then
  ok
else
  no "$stop_name"
  printf '%s' "$stop_bad"
fi

budget_name="budget crossing words are unknown causes, exit 2"
budget_bad=""
for cause in step-over-budget over-budget; do
  out="$("$CLASSIFY" "$cause" 2>/dev/null)" && code=0 || code=$?
  [[ "$code" == 2 && -z "$out" ]] || budget_bad+="    $cause: want exit 2 and no stdout, got exit $code, stdout '$out'"$'\n'
done
if [[ -z "$budget_bad" ]]; then
  ok
else
  no "$budget_name"
  printf '%s' "$budget_bad"
fi

check "uncovered is process" uncovered 0 process

check "suite-red is process" suite-red 0 process

conflict_name="ci-conflict is system, and SKILL.md's Bailing list names it as a system failure (#688)"
conflict_bad=""
out="$("$CLASSIFY" ci-conflict 2>/dev/null)" && code=0 || code=$?
[[ "$code" == 0 && "$(head -n1 <<< "$out")" == system ]] \
  || conflict_bad+="    classify-bail.sh ci-conflict: want exit 0 and 'system', got exit $code, stdout '$out'"$'\n'
bailing="$(awk '/^## Bailing/ { s = 1; next } s && /^## / { exit } s' "$HERE/../../../SKILL.md")"
entry="$(awk '/^- `ci-conflict` —/ { e = 1; print; next } e && /^- / { exit } e && NF { print } e && !NF { exit }' <<< "$bailing")"
[[ "$entry" == *'**system**'* ]] \
  || conflict_bad+="    SKILL.md's Bailing list has no \`ci-conflict\` entry calling it a **system** failure; entry: '$entry'"$'\n'
if [[ -z "$conflict_bad" ]]; then
  ok
else
  no "$conflict_name"
  printf '%s' "$conflict_bad"
fi

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
