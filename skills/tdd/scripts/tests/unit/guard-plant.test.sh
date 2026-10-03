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

finish
