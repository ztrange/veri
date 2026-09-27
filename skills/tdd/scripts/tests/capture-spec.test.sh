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

# new_fixture <dir> — one issue for the script to be run against, built from the body on
# stdin: <dir>/body.md is that body, and <dir>/bin/gh is the stub `gh` run_spec puts first on
# PATH. The two questions the script asks are answered from the environment the case sets: the
# label question from $LABELS (the issue's label names, space-separated, or empty for an issue
# that carries none) and the body question from $FIXTURES/body.md. The label answer applies
# the script's own `-q` filter the one way the stub can: a label is printed when the call
# names it in quotes (`select(.name == "bug")`), and every label when the call names none
# (`.labels[].name`), so a question about `bug` is never answered `refactor`. `labels` is matched first, so a single call asking for both is
# answered as the label question. A call it does not recognise is refused loudly rather than
# answered with the body anyway, so a script that starts asking for something else fails here
# instead of quietly reading the wrong fixture.
new_fixture() {
  mkdir -p "$1/bin"
  cat > "$1/body.md"
  cat > "$1/bin/gh" <<'STUB'
#!/bin/sh
case "$*" in
  *labels*)
    for l in $LABELS; do
      case "$*" in
        *"\"$l\""*) echo "$l" ;;
        *\"*) ;;
        *) echo "$l" ;;
      esac
    done ;;
  *body*) cat "$FIXTURES/body.md" ;;
  *) echo "gh stub: unexpected call: gh $*" >&2; exit 1 ;;
esac
STUB
  chmod +x "$1/bin/gh"
}

# The issue body the stub serves: the four bug sections this case is about, plus the
# ordinary spec headings every issue carries, so the body is the shape a real one has.
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

# section <file> <heading> — the lines of one `## ` section of a markdown document, heading
# included, ending where the next `## ` heading starts. `### ` is not a section boundary, so
# a Bug section written with subheadings comes back whole.
section() {
  awk -v want="$1" '
    /^## / { inside = ($0 == want) ; if (!inside) next }
    inside { print }
  ' "$2"
}

# run_spec <fixture-dir> <labels> <issue> <out> — the script run against the stub written
# into <fixture-dir>, with <labels> as the issue's labels and <fixture-dir>/body.md as its
# body, stdout in <out> and stderr beside it. Opens the case's `problems` array, holding the
# one problem every case shares: the script did not exit 0.
run_spec() {
  local dir="$1" labels="$2" issue="$3" out="$4" err="$4.err" code=0
  env PATH="$dir/bin:$PATH" FIXTURES="$dir" LABELS="$labels" "$SCRIPT" "$issue" \
    > "$out" 2> "$err" || code=$?
  problems=()
  [[ "$code" == 0 ]] || problems+=("exit want 0 got $code; stderr: $(head -2 "$err")")
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

# The second fixture: an issue with no `bug` label. Its body is the ordinary shape an issue
# that reports no bug has — no what-happened, no steps — so nothing in it could be mistaken
# for the report a `## Bug` section carries.
plaindir="$tmp/plain"
new_fixture "$plaindir" <<'BODY'
## What to build

tick-ledger.sh grows a `--dry-run` flag.

## Acceptance criteria

- [ ] `--dry-run` prints the tick it would make and writes nothing
BODY

# 2. No bug label, no Bug section: the spec is the issue's body and nothing more.
name='unlabelled issue: the spec carries no ## Bug section (#112)'
out="$tmp/plain-spec.md"
run_spec "$plaindir" '' 113 "$out"
section '## Bug' "$out" > "$tmp/plain-bug-section.md"
[[ ! -s "$tmp/plain-bug-section.md" ]] ||
  problems+=("spec has a '## Bug' section for an issue without the bug label: $(head -1 "$tmp/plain-bug-section.md")")
grep -qF -- 'tick-ledger.sh grows a `--dry-run` flag.' "$out" ||
  problems+=("spec is missing the issue's own body")

report "$name"

# The document twice — the path as every problem message spells it, and the same path
# resolved for the probe to read — so a message can never name a file the probe did not open.
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

# spec_writes — every line of the procedure that redirects into the blind spec, `<line>:<text>`
# per match. The redirect is what identifies the write: the spec's path is named a dozen times
# in the document as an argument handed to a prompt builder or a verifier, and only the line
# that points a `>` at it is the one that creates the file. The `>` has to be a word of its own
# — preceded by a space or starting the line — because the document writes its placeholders in
# angle brackets, so `run-verdict.sh … <phase> .tdd/issue-<n>-spec.md` ends a placeholder in a
# `>` immediately before the path and reads as a redirect otherwise (SKILL.md:1219 does).
spec_writes() {
  grep -nE '(^|[[:space:]])>[[:space:]]*\.tdd/issue-<n>-spec\.md' "$skill_path" || true
}

# 3. The conductor writes the spec through this script. `gh issue view -q .body` is the issue's
#    body and nothing else, so a document that still types it captures no `## Bug` section
#    whatever the issue is labelled — the two cases above would pass and no run would produce
#    what they describe.
name='SKILL.md writes the blind spec through capture-spec.sh, not a bare gh issue view (#112)'
problems=()
writes="$(spec_writes)"
if [[ -z "$writes" ]]; then
  # Fail closed: a procedure with no write at all is reported as unreadable rather than probed
  # as an empty list, which would let "nothing captures the spec" read as a pass.
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

# 4. The refactor label puts a Refactor section in the spec naming the run kind, the way the
#    bug label puts a Bug section there: the kind reaches the blind verifier through the spec,
#    the one channel it reads. An issue without the label gets no such section.
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
