#!/usr/bin/env bash
# Tests for scripts/capture-spec.sh — writes the blind spec the verifier leaves read — driven
# against a stub `gh` on PATH.
#
# Contract under test:
#   when the issue carries the `bug` label the spec gains a `## Bug` section carrying the
#   issue's what-happened, expected, steps to reproduce and environment, and SKILL.md step 1
#   says so.
#
# Run: scripts/tests/capture-spec.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib/harness.sh"
SCRIPT="$HERE/../capture-spec.sh"

tmp="$(scratch_dir)"

new_fixture() {
  mkdir -p "$1/bin"
  cat > "$1/body.md"
  cat > "$1/bin/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *labels*) for l in $LABELS; do echo "$l"; done ;;
  *body*) cat "$FIXTURES/body.md" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
  chmod +x "$1/bin/gh"
}

bugdir="$tmp/bug"
new_fixture "$bugdir" <<'BODY'
## What happened
tick-ledger.sh ticked the same step twice.

## Expected
tick-ledger.sh ticks a step once.

## Steps to reproduce
Run tick-ledger.sh twice against the same step text.

## Environment
bash 5.2 on macOS 15.6.

## Acceptance criteria

- [ ] a step is ticked once
BODY

section() {
  awk -v want="$1" '
    /^## / { inside = ($0 == want) ; if (!inside) next }
    inside { print }
  ' "$2"
}

run_spec() {
  local dir="$1" labels="$2" issue="$3" out="$4" err="$4.err" code=0
  env VERI_GH_DRIVER=auto PATH="$dir/bin:$PATH" FIXTURES="$dir" LABELS="$labels" "$SCRIPT" "$issue" \
    > "$out" 2> "$err" || code=$?
  problems=()
  [[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$err")")
}

name='bug-labelled issue: the spec carries a ## Bug section with what happened, expected, steps and environment (#112)'
out="$tmp/spec.md"
run_spec "$bugdir" bug 112 "$out"
section '## Bug' "$out" > "$tmp/bug-section.md"
if [[ ! -s "$tmp/bug-section.md" ]]; then
  problems+=("no '## Bug' section in the spec")
else
  while IFS= read -r want; do
    grep -qF -- "$want" "$tmp/bug-section.md" ||
      problems+=("'## Bug' section is missing: $want")
  done <<'WANT'
tick-ledger.sh ticked the same step twice.
tick-ledger.sh ticks a step once.
Run tick-ledger.sh twice against the same step text.
bash 5.2 on macOS 15.6.
WANT
fi

report "$name"

plaindir="$tmp/plain"
new_fixture "$plaindir" <<'BODY'
## What to build

tick-ledger.sh grows a `--dry-run` flag.

## Acceptance criteria

- [ ] `--dry-run` prints the tick it would make and writes nothing
BODY

ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

spec_writes() {
  grep -nE '(^|[[:space:]])>[[:space:]]*\.tdd/issue-<n>-spec\.md' "$skill_path" || true
}

name='SKILL.md writes the blind spec through capture-spec.sh, not a bare gh issue view (#112)'
problems=()
writes="$(spec_writes)"
if [[ -z "$writes" ]]; then
  problems+=("$skill_md has no command redirecting into .tdd/issue-<n>-spec.md, so where the conductor captures the spec could not be established")
else
  while IFS= read -r hit; do
    line="${hit%%:*}" text="${hit#*:}"
    grep -qF -- 'capture-spec.sh' <<<"$text" ||
      problems+=("$skill_md:$line writes the blind spec without capture-spec.sh, so no spec ever carries a ## Bug section:$text")
    ! grep -qE 'gh issue view' <<<"$text" ||
      problems+=("$skill_md:$line still captures the spec with a bare gh issue view:$text")
  done <<<"$writes"
fi

report "$name"

name='with no argument capture-spec.sh exits 2, prints nothing on stdout and its usage line on stderr'
problems=()
code=0
env VERI_GH_DRIVER=auto PATH="$plaindir/bin:$PATH" FIXTURES="$plaindir" LABELS='' "$SCRIPT" \
  > "$tmp/noarg.out" 2> "$tmp/noarg.err" || code=$?
[[ "$code" == 2 ]] || problems+=("exit want 2 got $code")
[[ ! -s "$tmp/noarg.out" ]] || problems+=("stdout want empty got: $(cat "$tmp/noarg.out")")
want_err='capture-spec: usage: capture-spec.sh <issue-number>'
[[ "$(cat "$tmp/noarg.err")" == "$want_err" && "$(wc -l < "$tmp/noarg.err" | tr -d ' ')" == 1 ]] ||
  problems+=("stderr want exactly '$want_err' got: $(cat "$tmp/noarg.err")")

report "$name"

name='against a gh that fails both gh issue view and gh api, capture-spec.sh exits 2 with nothing on stdout'
problems=()
faildir="$tmp/fail"
mkdir -p "$faildir/bin"
cat > "$faildir/bin/gh" <<'STUB'
#!/bin/sh
echo "gh stub: refused: gh $*" >&2
exit 1
STUB
chmod +x "$faildir/bin/gh"
code=0
env VERI_GH_DRIVER=auto PATH="$faildir/bin:$PATH" "$SCRIPT" 7 > "$tmp/fail.out" 2> "$tmp/fail.err" || code=$?
[[ "$code" == 2 ]] || problems+=("exit want 2 got $code; stderr: $(head -2 "$tmp/fail.err")")
[[ ! -s "$tmp/fail.out" ]] || problems+=("stdout want empty got: $(cat "$tmp/fail.out")")

report "$name"

name='capture-spec.sh, run through a symlink to the skill directory and from another working directory, prints the same spec and exit code as when run in place'
problems=()
ln -s "$(cd "$HERE/../.." && pwd)" "$tmp/linked-skill"
mkdir -p "$tmp/elsewhere"
in_code=0
(cd "$HERE/.." && env VERI_GH_DRIVER=auto PATH="$bugdir/bin:$PATH" FIXTURES="$bugdir" LABELS='bug refactor' ./capture-spec.sh 112) \
  > "$tmp/in-place.out" 2> "$tmp/in-place.err" || in_code=$?
linked_code=0
(cd "$tmp/elsewhere" && env VERI_GH_DRIVER=auto PATH="$bugdir/bin:$PATH" FIXTURES="$bugdir" LABELS='bug refactor' \
  "$tmp/linked-skill/scripts/capture-spec.sh" 112) > "$tmp/linked.out" 2> "$tmp/linked.err" || linked_code=$?
[[ "$in_code" == 0 ]] && grep -qx '## Bug' "$tmp/in-place.out" ||
  problems+=("in place: exit want 0 with a '## Bug' section got $in_code; stderr: $(head -2 "$tmp/in-place.err")")
[[ "$linked_code" == "$in_code" ]] ||
  problems+=("exit through the symlink want $in_code got $linked_code; stderr: $(head -2 "$tmp/linked.err")")
cmp -s "$tmp/in-place.out" "$tmp/linked.out" ||
  problems+=("stdout through the symlink differs: $(diff "$tmp/in-place.out" "$tmp/linked.out")")
cmp -s "$tmp/in-place.err" "$tmp/linked.err" ||
  problems+=("stderr through the symlink differs: $(diff "$tmp/in-place.err" "$tmp/linked.err")")

report "$name"

name='with VERI_GH_DRIVER unset capture-spec.sh reads the issue through gh api only, prints the spec and runs no gh issue view (#1114)'
problems=()
restdir="$tmp/rest"
mkdir -p "$restdir/bin"
cat > "$restdir/issue.json" <<'JSON'
{"labels":[],"body":"## What to build\n\ntick-ledger.sh grows a flag.\n"}
JSON
cat > "$restdir/bin/gh" <<'STUB'
#!/bin/sh
echo "gh $*" >> "$FIXTURES/calls"
case "$*" in
  'api repos/{owner}/{repo}/issues/7') cat "$FIXTURES/issue.json" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
chmod +x "$restdir/bin/gh"
: > "$restdir/calls"
code=0
env -u VERI_GH_DRIVER PATH="$restdir/bin:$PATH" FIXTURES="$restdir" "$SCRIPT" 7 \
  > "$tmp/rest.out" 2> "$tmp/rest.err" || code=$?
[[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$tmp/rest.err")")
want_out=$'## What to build\n\ntick-ledger.sh grows a flag.'
[[ "$(cat "$tmp/rest.out")" == "$want_out" ]] ||
  problems+=("stdout want the issue body got: $(cat "$tmp/rest.out")")
! grep -F 'gh issue view' "$restdir/calls" > /dev/null ||
  problems+=("gh issue view was called: $(grep -F 'gh issue view' "$restdir/calls")")

report "$name"

name='with VERI_GH_DRIVER=graphql a failing gh issue view makes capture-spec.sh exit 2 with nothing on stdout and no gh api call (#1114)'
problems=()
gqldir="$tmp/graphql"
mkdir -p "$gqldir/bin"
cat > "$gqldir/bin/gh" <<'STUB'
#!/bin/sh
echo "gh $*" >> "$FIXTURES/calls"
echo "gh stub: refused: gh $*" >&2
exit 1
STUB
chmod +x "$gqldir/bin/gh"
: > "$gqldir/calls"
code=0
env VERI_GH_DRIVER=graphql PATH="$gqldir/bin:$PATH" FIXTURES="$gqldir" "$SCRIPT" 7 \
  > "$tmp/graphql.out" 2> "$tmp/graphql.err" || code=$?
[[ "$code" == 2 ]] || problems+=("exit want 2 got $code; stderr: $(head -2 "$tmp/graphql.err")")
[[ ! -s "$tmp/graphql.out" ]] || problems+=("stdout want empty got: $(cat "$tmp/graphql.out")")
! grep -F 'gh api' "$gqldir/calls" > /dev/null ||
  problems+=("gh api was called: $(grep -F 'gh api' "$gqldir/calls")")

report "$name"

finish
