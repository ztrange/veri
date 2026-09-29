#!/usr/bin/env bash
# Tests for scripts/capture-spec.sh — the script that writes the blind spec the verifier
# leaves read — driven against a stub `gh` on PATH (no network, no real issue).
# Zero-dependency plain-shell asserts, the idiom tick-issue-criterion.test.sh uses.
#
# Contract under test (issue #112): a bug's Red is a reproduction, and the bug reaches the
# developer and the blind verifier through the one channel that already exists, the spec.
# So when the issue carries the `bug` label the spec gains a `## Bug` section carrying the
# issue's what-happened, expected, steps to reproduce and environment.
#
# Case 3 is the other half of the same criterion: a script nobody calls changes nothing, and
# the one caller is prose — `SKILL.md` step 1, where the conductor writes the spec. It lives
# here rather than in one of the `skill-*` suites for refactor-triage.test.sh case 4's reason:
# the sentence under test is a statement *about this script*, and a reader repairing it comes
# here to find out what it actually writes.
#
# Run: scripts/tests/capture-spec.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../capture-spec.sh"
pass=0 fail=0

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

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
  env PATH="$dir/bin:$PATH" FIXTURES="$dir" LABELS="$labels" "$SCRIPT" "$issue" \
    > "$out" 2> "$err" || code=$?
  problems=()
  [[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$err")")
}

report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $1"
    printf '    %s\n' "${problems[@]}"
  fi
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

name='unlabelled issue: the spec carries no ## Bug section (#112)'
out="$tmp/plain-spec.md"
run_spec "$plaindir" '' 113 "$out"
section '## Bug' "$out" > "$tmp/plain-bug-section.md"
[[ ! -s "$tmp/plain-bug-section.md" ]] ||
  problems+=("spec has a '## Bug' section for an issue without the bug label: $(head -1 "$tmp/plain-bug-section.md")")
grep -qF -- 'tick-ledger.sh grows a `--dry-run` flag.' "$out" ||
  problems+=("spec is missing the issue's own body")

report "$name"

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

name='refactor-labelled issue: the spec carries a ## Refactor section naming the run kind, an unlabelled one none (#499)'
out="$tmp/refactor-spec.md"
run_spec "$plaindir" refactor 499 "$out"
section '## Refactor' "$out" | tail -n +2 > "$tmp/refactor-section.md"
if ! grep -qx '## Refactor' "$out"; then
  problems+=("no '## Refactor' section in the spec for a refactor-labelled issue")
elif ! grep -qi 'refactor' "$tmp/refactor-section.md"; then
  problems+=("'## Refactor' section does not name the refactor run kind: $(head -3 "$tmp/refactor-section.md")")
fi
grep -qF -- 'tick-ledger.sh grows a `--dry-run` flag.' "$out" ||
  problems+=("refactor spec is missing the issue's own body")
run_problems=("${problems[@]}")
run_spec "$plaindir" '' 113 "$tmp/unlabelled-spec.md"
problems=("${run_problems[@]}" "${problems[@]}")
! grep -qx '## Refactor' "$tmp/unlabelled-spec.md" ||
  problems+=("spec has a '## Refactor' section for an issue without the refactor label")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
