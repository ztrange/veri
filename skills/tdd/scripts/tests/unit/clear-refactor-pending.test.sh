#!/usr/bin/env bash
# Tests for scripts/clear-refactor-pending.sh — the in-place removal of the
# ` ⟂ refactor pending` mark tick-ledger.sh --refactor-pending wrote with the green commit.
# Given a ledger file and a matcher, strip the mark from the FIRST checked step that both
# contains the matcher and carries the mark, in place, and exit 0; exit 3 with the file
# byte-identical when no such step matched. Operates on a real temp file.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/clear-refactor-pending.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CLEAR="$HERE/../../clear-refactor-pending.sh"
source "$HERE/../lib/harness.sh"

work="$(scratch_dir)"
led="$work/issue-42.md"

ledger='# Plan for #42

- [x] add the slugify lowercasing ⟂ refactor pending
- [x] collapse to single hyphen
- [x] collapse to single hyphen (again) ⟂ refactor pending
- [ ] percent-encode the remainder'

check() {  # check <name> <expected-exit> <matcher> <expected-ledger-text>
  local name="$1" exp_code="$2" matcher="$3" exp="$4" code want="$work/want.md"
  printf '%s\n' "$ledger" > "$led"
  printf '%s\n' "$exp" > "$want"
  "$CLEAR" "$led" "$matcher" 2>/dev/null && code=0 || code=$?
  if [[ "$code" == "$exp_code" ]] && cmp -s "$want" "$led"; then
    ok
  else
    no "$name (want exit $exp_code, got $code)"
    diff "$want" "$led" | sed 's/^/    /'
  fi
}

check "clears the first matching marked step" 0 "collapse to single hyphen" '# Plan for #42

- [x] add the slugify lowercasing ⟂ refactor pending
- [x] collapse to single hyphen
- [x] collapse to single hyphen (again)
- [ ] percent-encode the remainder'

check "no matching marked step exits 3, ledger untouched" 3 "percent-encode the remainder" "$ledger"

"$CLEAR" > "$work/out" 2> "$work/err" && code=0 || code=$?
printf '%s\n' 'usage: clear-refactor-pending.sh <ledger-file> <matcher>' > "$work/want-err"
if [[ "$code" == 2 && ! -s "$work/out" ]] && cmp -s "$work/want-err" "$work/err"; then
  ok
else
  no "no argument exits 2 with the usage line on stderr and nothing on stdout (want exit 2, got $code)"
  printf '    stdout: %s\n    stderr: %s\n' "$(cat "$work/out")" "$(cat "$work/err")"
fi

"$CLEAR" "$work/absent.md" "collapse to single hyphen" > "$work/out" 2>/dev/null && code=0 || code=$?
if [[ "$code" == 1 && ! -s "$work/out" ]]; then
  ok
else
  no "a ledger path that does not exist exits 1 with nothing on stdout (want exit 1, got $code)"
  printf '    stdout: %s\n' "$(cat "$work/out")"
fi

ln -s "$(cd "$HERE/../../.." && pwd)" "$work/skill-link"
mkdir -p "$work/caller" "$work/inplace"
printf '%s\n' "$ledger" > "$work/caller/issue-42.md"
printf '%s\n' "$ledger" > "$work/inplace/issue-42.md"
"$CLEAR" "$work/inplace/issue-42.md" "collapse to single hyphen" > "$work/in-out" 2> "$work/in-err" && in_code=0 || in_code=$?
(cd "$work/caller" && "$work/skill-link/scripts/clear-refactor-pending.sh" issue-42.md "collapse to single hyphen") \
  > "$work/ln-out" 2> "$work/ln-err" && ln_code=0 || ln_code=$?
printf '%s\n' '# Plan for #42

- [x] add the slugify lowercasing ⟂ refactor pending
- [x] collapse to single hyphen
- [x] collapse to single hyphen (again)
- [ ] percent-encode the remainder' > "$work/want.md"
if [[ "$ln_code" == "$in_code" && "$ln_code" == 0 ]] && cmp -s "$work/in-out" "$work/ln-out" \
  && cmp -s "$work/in-err" "$work/ln-err" && cmp -s "$work/want.md" "$work/caller/issue-42.md" \
  && cmp -s "$work/inplace/issue-42.md" "$work/caller/issue-42.md"; then
  ok
else
  no "through a symlinked skill directory from another working directory, a relative ledger is cleared as in place (in place exit $in_code, through link exit $ln_code)"
  diff "$work/want.md" "$work/caller/issue-42.md" | sed 's/^/    /'
  printf '    stdout: %s\n    stderr: %s\n' "$(cat "$work/ln-out")" "$(cat "$work/ln-err")"
fi

stub="$work/stub"
mkdir -p "$stub/lib"
cp "$CLEAR" "$stub/clear-refactor-pending.sh"
cp "$HERE/../.."/lib/*.sh "$stub/lib/"
cat > "$stub/lib/ledger.sh" <<'EOF'
ledger_clear_pending() {
  printf 'ledger_clear_pending [%s]\n' "$1"
  cat
}
EOF
printf '%s\n' "$ledger" > "$led"
"$stub/clear-refactor-pending.sh" "$led" "collapse to single hyphen" 2>/dev/null && code=0 || code=$?
want="$work/want.md"
{ echo 'ledger_clear_pending [collapse to single hyphen]'; printf '%s\n' "$ledger"; } > "$want"
if [[ "$code" == 0 ]] && cmp -s "$want" "$led"; then
  ok
else
  no "clears through lib/ledger.sh's ledger_clear_pending (want exit 0, got $code)"
  diff "$want" "$led" | sed 's/^/    /'
fi

finish
