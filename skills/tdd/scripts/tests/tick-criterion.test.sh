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

floor_err="$(scratch_dir)/stderr"
floor_out="$(printf -- '- [ ] a\n- [ ] b' | "$TICK" 2> "$floor_err")" && floor_code=0 || floor_code=$?
problems=()
[[ "$floor_code" == 0 ]] || problems+=("exit: want 0, got $floor_code")
[[ "$floor_out" == $'- [x] a\n- [ ] b' ]] || problems+=("stdout: want [- [x] a\\n- [ ] b], got [$floor_out]")
[[ -s "$floor_err" ]] && problems+=("stderr: want empty, got [$(cat "$floor_err")]")
report "floor: no argument ticks the first open box, exit 0, nothing on stderr"

linkdir="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$linkdir/linked-skill"
mkdir "$linkdir/elsewhere"
problems=()
for pair in beta:0 zeta:3; do
  matcher="${pair%%:*}" want="${pair#*:}"
  in_place_out="$(printf -- '- [ ] alpha\n- [ ] beta\n' | "$TICK" "$matcher" 2> "$linkdir/in-place.err")" \
    && in_place_code=0 || in_place_code=$?
  linked_out="$(cd "$linkdir/elsewhere" && printf -- '- [ ] alpha\n- [ ] beta\n' \
    | "$linkdir/linked-skill/scripts/tick-criterion.sh" "$matcher" 2> "$linkdir/linked.err")" \
    && linked_code=0 || linked_code=$?
  [[ "$linked_out" == "$in_place_out" ]] || problems+=("$matcher stdout: in place [$in_place_out], linked [$linked_out]")
  [[ "$(cat "$linkdir/linked.err")" == "$(cat "$linkdir/in-place.err")" ]] \
    || problems+=("$matcher stderr: in place [$(cat "$linkdir/in-place.err")], linked [$(cat "$linkdir/linked.err")]")
  [[ "$linked_code" == "$in_place_code" ]] || problems+=("$matcher exit: in place $in_place_code, linked $linked_code")
  [[ "$in_place_code" == "$want" ]] || problems+=("$matcher in place: want exit $want, got $in_place_code")
done
report "tick-criterion.sh run through a symlink to the skill directory and from another working directory answers as it does when run in place"

finish
