#!/usr/bin/env bash
# Tests for scripts/criterion-finished.sh — whether an issue acceptance criterion is done.
# Given a ledger (checkbox markdown) on stdin and a criterion number k, exit 0 when every
# step ending in ` ⟦criterion k⟧` is ticked with no ` ⟂ refactor pending` mark, and exit 3
# when some step serving k is still open or pending.
# Fast tier by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/criterion-finished.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
FINISHED="$HERE/../../criterion-finished.sh"
source "$HERE/../lib/harness.sh"
code_for() {  # code_for <criterion> <ledger> — print the script's exit code
  local code
  printf '%s' "$2" | "$FINISHED" "$1" >/dev/null && code=0 || code=$?
  echo "$code"
}

name="two steps serve criterion 1: exits 3 until both are ticked and verified, then 0"
half='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse non-alphanumerics to a single hyphen ⟦criterion 1⟧'
both='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] collapse non-alphanumerics to a single hyphen ⟦criterion 1⟧'
pending='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] collapse non-alphanumerics to a single hyphen ⟦criterion 1⟧ ⟂ refactor pending'
got_half="$(code_for 1 "$half")"
got_pending="$(code_for 1 "$pending")"
got_both="$(code_for 1 "$both")"
if [[ "$got_half" != 3 ]]; then
  no "$name (half-ticked: want exit 3, got $got_half)"
elif [[ "$got_pending" != 3 ]]; then
  no "$name (both ticked, second refactor pending: want exit 3, got $got_pending)"
elif [[ "$got_both" != 0 ]]; then
  no "$name (both ticked: want exit 0, got $got_both)"
else
  ok
fi

name="a step serving no criterion makes no criterion finished: criterion 2 served by no step exits 3"
all_done='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [x] reject an empty title'
got_unserved="$(code_for 2 "$all_done")"
if [[ "$got_unserved" != 3 ]]; then
  no "$name (criterion 2 served by no step: want exit 3, got $got_unserved)"
else
  ok
fi

name="an unchecked ⟦added⟧ step serving criterion 1 keeps it unfinished: exits 3"
with_added='# Plan for #42

- [x] lowercase the slug ⟦criterion 1⟧
- [ ] collapse a run of hyphens ⟦added⟧ ⟦criterion 1⟧
- [x] collapse non-alphanumerics to a single hyphen ⟦criterion 1⟧'
got_added="$(code_for 1 "$with_added")"
if [[ "$got_added" != 3 ]]; then
  no "$name (unchecked added step serving criterion 1: want exit 3, got $got_added)"
else
  ok
fi

name="criterion 1 is finished when lib/ledger.sh's ledger_steps says so: exits 0 (#495)"
work="$(scratch_dir)"
mkdir "$work/lib"
cp "$FINISHED" "$work/criterion-finished.sh"
cp "$(dirname "$FINISHED")"/lib/*.sh "$work/lib/"
{ printf '. %q\n' "$(dirname "$FINISHED")/lib/ledger.sh"; cat <<'EOF'; } > "$work/lib/ledger.sh"
ledger_steps() {
  cat > /dev/null
  printf '1\tdone\tstep\t0\t0\t1\tfinished in the module ⟦criterion 1⟧\n'
  printf '2\topen\tstep\t0\t0\t2\tstill open in the module ⟦criterion 2⟧\n'
}
EOF
markdown_open='# Plan for #42

- [ ] found open in the markdown ⟦criterion 1⟧'
got_module="$(FINISHED="$work/criterion-finished.sh" code_for 1 "$markdown_open")"
if [[ "$got_module" != 0 ]]; then
  no "$name (module says criterion 1 done: want exit 0, got $got_module)"
else
  ok
fi

name="a ticked untagged step whose text is 3 does not finish criterion 3: exits 3"
text_is_k='# Plan for #42

- [x] 3'
got_text_k="$(code_for 3 "$text_is_k")"
if [[ "$got_text_k" != 3 ]]; then
  no "$name (untagged ticked step with text 3: want exit 3, got $got_text_k)"
else
  ok
fi

name="no argument and an empty one exit 2 with nothing on stdout, stdin unread and the usage line alone on stderr"
work="$(scratch_dir)"
printf -- '- [x] a ⟦criterion 1⟧\n' > "$work/ledger"
usage='usage: criterion-finished.sh <k> < .tdd/issue-<n>.md'
verdict=""
for args in none empty; do
  { if [[ "$args" == none ]]; then "$FINISHED"; else "$FINISHED" ''; fi > "$work/out" 2> "$work/err" && code=0 || code=$?
    cat > "$work/rest"; } < "$work/ledger"
  if [[ "$code" != 2 ]]; then
    verdict="$args argument: want exit 2, got $code"
  elif [[ -s "$work/out" ]]; then
    verdict="$args argument: want nothing on stdout, got $(cat "$work/out")"
  elif ! cmp -s "$work/ledger" "$work/rest"; then
    verdict="$args argument: want stdin unread, got $(cat "$work/rest") left of it"
  elif [[ "$(cat "$work/err")" != "$usage" ]] || [[ "$(wc -l < "$work/err" | tr -d ' ')" != 1 ]]; then
    verdict="$args argument: want stderr '$usage', got '$(cat "$work/err")'"
  fi
  [[ -z "$verdict" ]] || break
done
if [[ -n "$verdict" ]]; then
  no "$name ($verdict)"
else
  ok
fi

finish
