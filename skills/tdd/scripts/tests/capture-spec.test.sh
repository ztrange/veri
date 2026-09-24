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
# Run: scripts/tests/capture-spec.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$HERE/../capture-spec.sh"
pass=0 fail=0

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# The issue body the stub serves: the four bug sections this case is about, plus the
# ordinary spec headings every issue carries, so the body is the shape a real one has.
cat > "$tmp/body.md" <<'BODY'
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

# The stub serves the one call the script makes: the issue body. A query it does not recognise
# is refused loudly rather than answered with the body anyway, so a script that starts asking
# for something else fails here instead of quietly reading the wrong fixture.
stubdir="$tmp/bin"; mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *body*) cat "$FIXTURES/body.md" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
chmod +x "$stubdir/gh"

# section <file> <heading> — the lines of one `## ` section of a markdown document, heading
# included, ending where the next `## ` heading starts. `### ` is not a section boundary, so
# a Bug section written with subheadings comes back whole.
section() {
  awk -v want="$1" '
    /^## / { inside = ($0 == want) ; if (!inside) next }
    inside { print }
  ' "$2"
}

# report <name> — one case's verdict, read off the `problems` array the case filled: a pass
# when it is empty, `FAIL - <name>` with every problem under it when it is not.
report() {
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $1"
    printf '    %s\n' "${problems[@]}"
  fi
}

# 1. The bug label puts a Bug section in the spec, carrying all four parts of the report.
name='bug-labelled issue: the spec carries a ## Bug section with what happened, expected, steps and environment (#112)'
out="$tmp/spec.md"; err="$tmp/spec.err"
code=0
env PATH="$stubdir:$PATH" FIXTURES="$tmp" "$SCRIPT" 112 > "$out" 2> "$err" || code=$?

problems=()
[[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$err")")
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

# The second fixture: an issue with no `bug` label. Its body is the ordinary shape an issue
# that reports no bug has — no what-happened, no steps — so nothing in it could be mistaken
# for the report a `## Bug` section carries.
plaindir="$tmp/plain"; mkdir -p "$plaindir"
cat > "$plaindir/body.md" <<'BODY'
## What to build

tick-ledger.sh grows a `--dry-run` flag.

## Acceptance criteria

- [ ] `--dry-run` prints the tick it would make and writes nothing
BODY

# The stub for that issue: the same two questions, answered for an issue whose labels do not
# include `bug`. `labels` is matched before `body` so a single call asking for both is answered
# as the label question; a query the script passes (`-q`/`--jq`) is answered with what gh would
# print after applying it — nothing, there being no label — and a raw `--json labels` with the
# JSON document gh would return. Anything else is refused loudly.
plainbin="$tmp/plain/bin"; mkdir -p "$plainbin"
cat > "$plainbin/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *labels*)
    case "$*" in
      *-q*|*--jq*) : ;;
      *) echo '{"labels":[]}' ;;
    esac ;;
  *body*) cat "$FIXTURES/body.md" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
chmod +x "$plainbin/gh"

# 2. No bug label, no Bug section: the spec is the issue's body and nothing more.
name='unlabelled issue: the spec carries no ## Bug section (#112)'
out="$tmp/plain-spec.md"; err="$tmp/plain-spec.err"
code=0
env PATH="$plainbin:$PATH" FIXTURES="$plaindir" "$SCRIPT" 113 > "$out" 2> "$err" || code=$?

problems=()
[[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$err")")
section '## Bug' "$out" > "$tmp/plain-bug-section.md"
[[ ! -s "$tmp/plain-bug-section.md" ]] ||
  problems+=("spec has a '## Bug' section for an issue without the bug label: $(head -1 "$tmp/plain-bug-section.md")")
grep -qF -- 'tick-ledger.sh grows a `--dry-run` flag.' "$out" ||
  problems+=("spec is missing the issue's own body")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
