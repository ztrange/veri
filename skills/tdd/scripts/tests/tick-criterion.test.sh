#!/usr/bin/env bash
# Unit tests for scripts/tick-criterion.sh — the pure text transform that ticks an
# acceptance-criterion checkbox in an issue body. Zero-dependency plain-shell asserts.
#
# Run: scripts/tests/tick-criterion.test.sh   (exits non-zero if any case fails)
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TICK="$HERE/../tick-criterion.sh"
source "$HERE/lib/harness.sh"

check() {
  local name="$1" exp_code="$2" matcher="$3" input="$4" exp_out="$5"
  local out code
  out="$(printf '%s' "$input" | "$TICK" "$matcher")" && code=0 || code=$?
  if [[ "$code" == "$exp_code" && "$out" == "$exp_out" ]]; then
    ok
  else
    no "$name (matcher=[$matcher] want exit $exp_code, got $code)"
    diff <(printf '%s\n' "$exp_out") <(printf '%s\n' "$out") | sed 's/^/    /'
  fi
}

body="## Acceptance criteria

- [ ] reads the issue and creates a branch
- [ ] a start comment is posted
- [ ] a draft PR is opened"

check "ticks matching box" 0 "start comment" "$body" "## Acceptance criteria

- [ ] reads the issue and creates a branch
- [x] a start comment is posted
- [ ] a draft PR is opened"

multi='- [ ] alpha shared
- [ ] beta shared'
check "first match only" 0 "shared" "$multi" '- [x] alpha shared
- [ ] beta shared'

check "empty matcher ticks first" 0 "" "$body" "## Acceptance criteria

- [x] reads the issue and creates a branch
- [ ] a start comment is posted
- [ ] a draft PR is opened"

check "no match exits 3" 3 "nonexistent criterion" "$body" "$body"

lit='- [ ] `/tdd <n>` creates branch `tdd/<n>-slug`
- [ ] other'
check "literal special chars" 0 '`/tdd <n>`' "$lit" '- [x] `/tdd <n>` creates branch `tdd/<n>-slug`
- [ ] other'

mixed='- [x] reads the issue and creates a branch
- [ ] reads the file and creates a branch'
check "skips already checked" 0 "creates a branch" "$mixed" '- [x] reads the issue and creates a branch
- [x] reads the file and creates a branch'

nested='  - [ ] nested criterion'
check "nested checkbox" 0 "nested" "$nested" '  - [x] nested criterion'

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir "$work/lib"
cp "$TICK" "$work/tick-criterion.sh"
cat > "$work/lib/ledger.sh" <<'EOF'
ledger_tick() {
  cat > /dev/null
  printf 'ticked by the module: %s\n' "$1"
}
EOF
TICK="$work/tick-criterion.sh"
check "the tick comes from lib/ledger.sh's ledger_tick (#495)" 0 "markdown" \
  "- [ ] found in the markdown" "ticked by the module: markdown"

finish
