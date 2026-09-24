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

# The stub emulates `gh issue view <n> --json <fields> [-q <expr>]`: the field list and the
# jq expression decide what comes back, so any of the ways a script might ask for a body and
# a label list is answered rather than only one spelling of the call.
python3 - "$tmp" <<'PY'
import json, sys
tmp = sys.argv[1]
body = open(f"{tmp}/body.md").read()
labels = [{"name": "ready-for-agent"}, {"name": "bug"}]
open(f"{tmp}/full.json", "w").write(json.dumps({"body": body, "labels": labels}))
open(f"{tmp}/body.json", "w").write(json.dumps({"body": body}))
open(f"{tmp}/labels.json", "w").write(json.dumps({"labels": labels}))
open(f"{tmp}/labels.txt", "w").write("".join(f"{l['name']}\n" for l in labels))
PY

stubdir="$tmp/bin"; mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
fields=""; q=""
while [ $# -gt 0 ]; do
  case "$1" in
    --json) fields="$2"; shift 2 ;;
    -q|--jq) q="$2"; shift 2 ;;
    *) shift ;;
  esac
done
case "$q" in
  *label*) cat "$FIXTURES/labels.txt" ;;
  *body*)  cat "$FIXTURES/body.md" ;;
  "")
    case "$fields" in
      *body*label*|*label*body*) cat "$FIXTURES/full.json" ;;
      *label*)                   cat "$FIXTURES/labels.json" ;;
      *)                         cat "$FIXTURES/body.json" ;;
    esac ;;
  *) cat "$FIXTURES/full.json" ;;
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

if [[ "${#problems[@]}" -eq 0 ]]; then
  pass=$((pass + 1))
else
  fail=$((fail + 1))
  echo "FAIL - $name"
  printf '    %s\n' "${problems[@]}"
fi

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
