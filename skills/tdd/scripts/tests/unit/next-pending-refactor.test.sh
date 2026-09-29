#!/usr/bin/env bash
# Tests for scripts/next-pending-refactor.sh — the resume primitive for a step that is
# green but not yet tidied. Given a ledger (checkbox markdown) on stdin, print the
# description of the FIRST checked step whose line ends in ` ⟂ refactor pending` — without
# that mark, so the description is the substring the refactor loop hands back — and exit 0;
# exit 3 with no output when no step carries it.
#
# Admitted to the fast tier (#336) by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/next-pending-refactor.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PENDING="$HERE/../../next-pending-refactor.sh"
source "$HERE/../lib/harness.sh"
check() {  # check <name> <expected-exit> <input> <expected-stdout>
  local name="$1" exp_code="$2" input="$3" exp="$4" out code
  out="$(printf '%s' "$input" | "$PENDING")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp" ]]; then ok; else
    no "$name (want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

pending='# Plan for #42

- [x] add the slugify lowercasing
- [x] collapse non-alphanumerics to a single hyphen ⟂ refactor pending
- [x] strip leading and trailing hyphens ⟂ refactor pending
- [ ] percent-encode the remainder'
check "first pending description, mark stripped" 0 "$pending" \
  "collapse non-alphanumerics to a single hyphen"

settled='# Plan for #42

- [x] add the slugify lowercasing
- [ ] collapse non-alphanumerics to a single hyphen'
check "no pending step exits 3" 3 "$settled" ""

work="$(scratch_dir)"
mkdir "$work/lib"
cp "$PENDING" "$work/next-pending-refactor.sh"
cat > "$work/lib/ledger.sh" <<'EOF'
ledger_steps() {
  cat > /dev/null
  printf '1\tdone\tstep\t0\t0\t1\ttidied in the module ⟦criterion 1⟧\n'
  printf '2\topen\tstep\t0\t0\t2\tstill open in the module ⟦criterion 2⟧\n'
  printf '3\tdone\tstep\t1\t0\t3\tasked the module ⟦criterion 3⟧\n'
}
EOF
PENDING="$work/next-pending-refactor.sh"
check "the first pending step comes from lib/ledger.sh's ledger_steps (#495)" 0 \
  "- [x] found in the markdown ⟦criterion 1⟧ ⟂ refactor pending" "asked the module ⟦criterion 3⟧"

finish
