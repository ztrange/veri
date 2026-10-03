#!/usr/bin/env bash
# Unit tests for scripts/tests/lib/guard-plant.sh — sourced, never executed: the planted
# scratch tree a guard suite runs its guard copy in, and the run over one document.
# Fast tier: no git, no network, no servers, no real sleep, no nested suites —
# by its own usage count: git 0, python3 0, server 0, sleep 0.
#
# Run: scripts/tests/unit/guard-plant.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/../lib/harness.sh"
scratch="$(scratch_dir)"

ROOT="$scratch/root"
GUARD='g/stub-guard.test.sh'
GUARD_PATH="$ROOT/$GUARD"
SKILL='d/DOC.md'
COMPANIONS=(c/COMPANION.md)

mkdir -p "$ROOT/g" "$ROOT/d" "$ROOT/c"
cat > "$GUARD_PATH" <<'EOF'
#!/bin/sh
here="$(cd "$(dirname "$0")" && pwd)"
echo "doc: $(cat "$here/../d/DOC.md")"
[ -f "$here/lib/harness.sh" ] && echo "harness: beside"
echo "companion: $(cat "$here/../c/COMPANION.md")"
case "$(cat "$here/../d/DOC.md")" in
  bare) exit 4 ;;
esac
echo "----"
echo "5 passed, 2 failed"
exit 3
EOF
chmod +x "$GUARD_PATH"
printf 'committed\n' > "$ROOT/$SKILL"
printf 'companion text\n' > "$ROOT/c/COMPANION.md"
printf 'planted\n' > "$scratch/planted.md"
printf 'bare\n' > "$scratch/bare.md"

source "$HERE/../lib/guard-plant.sh"

# 1. make_plant_tree plants the guard copy, the harness lib beside it and the named
#    companions; run_guard_over runs that copy over the given document, recording its exit
#    code and output; failures_in reads the failure count off its count line, or '<none>'
name="guard-plant: the planted tree carries the guard copy, harness lib and companions, run_guard_over records the copy's exit code and output over the given document, and failures_in reads its count line or '<none>'"
problems=()
make_plant_tree tree1
[[ "${tree:-}" == "$scratch/tree1" ]] || problems+=("tree is '${tree:-}', want $scratch/tree1")
[[ "${guard_copy:-}" == "$scratch/tree1/$GUARD" ]] || problems+=("guard_copy is '${guard_copy:-}', want $scratch/tree1/$GUARD")
[[ -x "$scratch/tree1/$GUARD" ]] || problems+=("no executable guard copy at $scratch/tree1/$GUARD")
cmp -s "$HERE/../lib/harness.sh" "$scratch/tree1/g/lib/harness.sh" ||
  problems+=("the harness lib is not beside the guard copy at $scratch/tree1/g/lib/harness.sh")
cmp -s "$ROOT/c/COMPANION.md" "$scratch/tree1/c/COMPANION.md" ||
  problems+=("the companion c/COMPANION.md was not copied into the tree")
run_guard_over "$scratch/planted.md"
[[ "${guard_code:-}" == 3 ]] || problems+=("guard_code over the planted document is '${guard_code:-}', want 3")
want="$(printf 'doc: planted\nharness: beside\ncompanion: companion text\n----\n5 passed, 2 failed')"
[[ "${guard_out:-}" == "$want" ]] || problems+=("guard_out over the planted document is '${guard_out:-}', want '$want'")
failures="$(failures_in "${guard_out:-}")"
[[ "$failures" == 2 ]] || problems+=("failures_in read '$failures' off the count line, want 2")
run_guard_over "$scratch/bare.md"
[[ "${guard_code:-}" == 4 ]] || problems+=("guard_code over the bare document is '${guard_code:-}', want 4")
failures="$(failures_in "${guard_out:-}")"
[[ "$failures" == '<none>' ]] || problems+=("failures_in read '$failures' off output with no count line, want '<none>'")
report "$name"

# 2. make_plant_tree, when the scratch tree cannot be made, appends that to $problems and
#    returns 1
name="guard-plant: make_plant_tree appends a problem and returns 1 when the scratch tree cannot be made"
printf 'not a directory\n' > "$scratch/blocked"
problems=()
make_plant_tree blocked 2>/dev/null && code=0 || code=$?
planted=(${problems[@]+"${problems[@]}"})
problems=()
[[ "$code" == 1 ]] || problems+=("make_plant_tree returned $code over a blocked tree, want 1")
want='could not make a scratch tree to plant the document in, so the criterion went unasked'
[[ "${#planted[@]}" == 1 && "${planted[0]:-}" == "$want" ]] ||
  problems+=("make_plant_tree left problems (${planted[*]:-}), want exactly '$want'")
report "$name"

# 3. probe_guard_is_there adds a problem and returns 1 over a missing or non-executable
#    guard; probe_guard_is_red adds one over a green run, or a red one with no count line; probe_guard_is_green_unplanted
#    adds one over a red run of the committed document — each naming the guard and the document
name="guard-plant: probe_guard_is_there, probe_guard_is_red and probe_guard_is_green_unplanted each add a problem naming the guard and the document, and none over the case it accepts"
cat > "$ROOT/g/switch-guard.test.sh" <<'EOF'
#!/bin/sh
here="$(cd "$(dirname "$0")" && pwd)"
case "$(cat "$here/../d/DOC.md")" in
  red) echo "3 passed, 1 failed"; exit 1 ;;
  uncounted) echo "died before its count line"; exit 1 ;;
esac
echo "3 passed, 0 failed"
EOF
chmod +x "$ROOT/g/switch-guard.test.sh"
printf 'green\n' > "$scratch/green.md"
printf 'red\n' > "$scratch/red.md"
printf 'uncounted\n' > "$scratch/uncounted.md"
outcomes=()
expect_case() {
  local label="$1" want_code="$2" want_count="$3" code one
  shift 3
  problems=()
  "$@" 2>/dev/null && code=0 || code=$?
  got=(${problems[@]+"${problems[@]}"})
  [[ -z "$want_code" || "$code" == "$want_code" ]] ||
    outcomes+=("$label: returned $code, want $want_code")
  [[ "${#got[@]}" == "$want_count" ]] ||
    outcomes+=("$label: added ${#got[@]} problems (${got[*]:-}), want $want_count")
  for one in ${got[@]+"${got[@]}"}; do
    [[ "$one" == *"$SKILL"* ]] ||
      outcomes+=("$label: the problem '$one' does not name the document $SKILL")
  done
}
probe_case() {
  local one
  expect_case "$@"
  for one in ${got[@]+"${got[@]}"}; do
    [[ "$one" == *"$GUARD"* || "$one" == *"${GUARD##*/}"* ]] ||
      outcomes+=("$1: the problem '$one' does not name the guard $GUARD")
  done
}
GUARD='g/absent-guard.test.sh'
GUARD_PATH="$ROOT/$GUARD"
probe_case 'probe_guard_is_there over a missing guard' 1 1 probe_guard_is_there
GUARD='g/plain-guard.test.sh'
GUARD_PATH="$ROOT/$GUARD"
printf '#!/bin/sh\n' > "$GUARD_PATH"
chmod -x "$GUARD_PATH"
probe_case 'probe_guard_is_there over a non-executable guard' 1 1 probe_guard_is_there
GUARD='g/switch-guard.test.sh'
GUARD_PATH="$ROOT/$GUARD"
probe_case 'probe_guard_is_there over an executable guard' 0 0 probe_guard_is_there
make_plant_tree tree3
run_guard_over "$scratch/green.md"
probe_case 'probe_guard_is_red over a green run' '' 2 probe_guard_is_red 'planted line is gone'
run_guard_over "$scratch/red.md"
probe_case 'probe_guard_is_red over a red run' '' 0 probe_guard_is_red 'planted line is gone'
run_guard_over "$scratch/uncounted.md"
probe_case 'probe_guard_is_red over a red run with no count line' '' 1 probe_guard_is_red 'planted line is gone'
SKILL_PATH="$scratch/red.md"
probe_case 'probe_guard_is_green_unplanted over a red committed document' '' 2 probe_guard_is_green_unplanted
SKILL_PATH="$scratch/green.md"
probe_case 'probe_guard_is_green_unplanted over a green committed document' '' 0 probe_guard_is_green_unplanted
problems=(${outcomes[@]+"${outcomes[@]}"})
report "$name"

# 4. probe_plant_is_what_it_claims <removed> <replacement> <planted> adds a problem naming the
#    document when the committed one carries no <removed> (returning 1), when the planted one
#    still carries <removed>, carries no <replacement>, or differs on any line but the carriers
name="guard-plant: probe_plant_is_what_it_claims adds a problem naming the document when the committed one lacks the removed text, the planted one keeps it or lacks the replacement, or the plant changed a line that carried neither — and none over a plant that rewrote exactly the carriers"
SKILL='d/DOC.md'
SKILL_PATH="$scratch/claims-committed.md"
printf 'one DENY here\nplain line\nDENY again\n' > "$SKILL_PATH"
printf 'one GRANT here\nplain line\nGRANT again\n' > "$scratch/claims-exact.md"
printf 'one GRANT here\nplain line\nDENY again\n' > "$scratch/claims-kept.md"
printf 'one OTHER here\nplain line\nOTHER again\n' > "$scratch/claims-elsewise.md"
printf 'one GRANT here\nplain line changed\nGRANT again\n' > "$scratch/claims-spread.md"
outcomes=()
claims_case() {
  local label="$1" want_text="$4" one
  expect_case "$1" "$2" "$3" probe_plant_is_what_it_claims "${@:5}"
  for one in ${got[@]+"${got[@]}"}; do
    [[ -z "$want_text" || "$one" == *"$want_text"* ]] ||
      outcomes+=("$label: the problem '$one' does not name '$want_text'")
  done
}
claims_case 'over a plant that rewrote exactly the carriers' 0 0 '' DENY GRANT "$scratch/claims-exact.md"
claims_case 'over a committed document with no removed text' 1 1 ABSENT ABSENT GRANT "$scratch/claims-exact.md"
claims_case 'over a planted document that keeps the removed text' '' 2 '' DENY GRANT "$scratch/claims-kept.md"
claims_case 'over a planted document with no replacement' '' 1 GRANT DENY GRANT "$scratch/claims-elsewise.md"
claims_case 'over a plant that changed a line no carrier was on' '' 1 '' DENY GRANT "$scratch/claims-spread.md"
problems=(${outcomes[@]+"${outcomes[@]}"})
report "$name"

finish
