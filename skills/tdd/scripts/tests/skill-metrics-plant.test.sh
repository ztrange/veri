#!/usr/bin/env bash
# Unit tests for skill-metrics.test.sh — the suite that pins what skills/tdd/SKILL.md tells
# the conductor to do with the run's metrics report. Like docs-read-guard-plant.test.sh and
# count-line-guard.test.sh this suite has no script as its subject: its subject is another
# suite, and what that suite answers when the document it reads is wrong.
# Zero-dependency plain-shell asserts, same idiom as docs-read-guard-plant.test.sh.
#
# Why this exists (issue #267): #236 merged the Draft PR step's commands into one fenced
# block, which `records_of` folds into a single record — and that silently turned the two
# record-level order probes written before it into checks no command order could fail. #266
# replaced them with line-level ones and #267 removed the dead pair, so the whole of the
# Draft PR order is now pinned by checks that read the fenced block line by line. That those
# line-level checks can still fail is exactly what nobody watched the first time, so it is
# asked here rather than assumed.
#
# Contract under test (one criterion, one case):
#   Run against a SKILL.md whose Draft PR command block has its order broken — `gh pr create`
#   after the `metrics:` commit, `gh pr edit` before it, or a `gh pr edit` whose `--body`
#   does not carry the committed report — skill-metrics.test.sh fails, and says which
#   command sits in the wrong place. Against the unbroken document it passes, so each
#   failure below is the sabotage's and not the scratch tree's.
#
# The subject is run rather than read: whether a check can fail is a fact about what the
# suite does when the document is wrong, and reading the suite for a comparison of a
# particular shape would answer nothing about what that comparison is fed. So the document
# is copied into a scratch tree with one line moved or rewritten, the subject is copied in
# beside it at the path it resolves itself from, and the subject is run there.
# `probe_sabotage_is_real` asserts the copy actually differs, because a move whose anchor
# had drifted would leave every probe below reporting on an unbroken document.
#
# Run: skills/tdd/scripts/tests/skill-metrics-plant.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"

# The two files the scratch tree must carry, each at the path the subject resolves from its
# own location: the subject reads the document four directories up from itself, so a copy
# only behaves like the original if it stands in the same shape of tree.
TESTS_DIR='skills/tdd/scripts/tests'
SUBJECT_NAME='skill-metrics.test.sh'
SUBJECT_PATH="$ROOT/$TESTS_DIR/$SUBJECT_NAME"
SKILL_REL='skills/tdd/SKILL.md'
SKILL_PATH="$ROOT/$SKILL_REL"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which sabotage went unnoticed rather than only that one did.
report() {
  local name="$1"
  if [[ "${#problems[@]}" -eq 0 ]]; then
    pass=$((pass + 1))
  else
    fail=$((fail + 1))
    echo "FAIL - $name"
    printf '    %s\n' "${problems[@]}"
  fi
}

# flat <text> — one line of it, for a failure message: newlines become slashes so a run's
# output quoted inside an indented problem line stays one line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# plant_tree — stand the subject up in a fresh scratch tree beside a copy of the document,
# leaving the tree's path in `tree`, the subject's copy in `subject_copy` and the document's
# in `skill_copy`. The document is copied verbatim; a sabotage rewrites it afterwards.
plant_tree() {
  tree="$(mktemp -d)" || {
    problems+=("could not make a scratch tree to stand $SUBJECT_NAME up in, so the criterion went unasked")
    return 1
  }
  mkdir -p "$tree/$TESTS_DIR" "$tree/$(dirname "$SKILL_REL")"
  subject_copy="$tree/$TESTS_DIR/$SUBJECT_NAME"
  skill_copy="$tree/$SKILL_REL"
  cp "$SUBJECT_PATH" "$subject_copy"
  chmod 755 "$subject_copy"
  cp "$SKILL_PATH" "$skill_copy"
}

# sabotage_skill <kind> <a> <b> — rewrite the document copy one line at a time, the two ways
# a Draft PR order breaks. `before` moves the first line holding <a> to just before the first
# line holding <b>, which is how a command ends up on the wrong side of another; `sub`
# replaces the first line holding <a> with <b> verbatim, which is how a command keeps its
# place and stops carrying what it carried. Both are whole-line edits, so the sabotaged block
# is a block someone could have written.
sabotage_skill() {
  local kind="$1" a="$2" b="$3" out
  out="$(awk -v kind="$kind" -v a="$a" -v b="$b" '
    { line[NR] = $0 }
    END {
      for (i = 1; i <= NR; i++) if (!ai && index(line[i], a)) ai = i
      if (kind == "sub") {
        for (i = 1; i <= NR; i++) print (i == ai) ? b : line[i]
        exit
      }
      for (i = 1; i <= NR; i++) if (!bi && index(line[i], b)) bi = i
      for (i = 1; i <= NR; i++) {
        if (i == bi) print line[ai]
        if (i != ai) print line[i]
      }
    }' "$skill_copy")"
  printf '%s\n' "$out" > "$skill_copy"
}

# probe_sabotage_is_real — the premise every probe below rests on, asserted rather than
# assumed: the rewrite matched its anchors and the copy differs from the document. An edit
# whose anchor had drifted off SKILL.md would leave the run below reporting on an unbroken
# Draft PR block, and the case would go green over the hole it exists to pin.
probe_sabotage_is_real() {
  cmp -s "$SKILL_PATH" "$skill_copy" &&
    problems+=("$1 left $SKILL_REL byte-identical, so the Draft PR order was never broken and nothing below asks the criterion")
  return 0
}

# run_subject — run the copy once against whatever document stands beside it, leaving what it
# said in `run_out` and how it exited in `run_code`. Taken on the spot with `&& … || …`,
# since this suite does not run under `set -e` and the subject is expected to fail.
run_subject() {
  run_out="$("$subject_copy" 2>&1)" && run_code=0 || run_code=$?
}

# probe_notices <what was broken> <expected problem text> — the criterion, asked of the one
# run above in the two ways a broken document must show: the exit status a runner reads, and
# a problem line naming the command that sits in the wrong place. The second is what makes
# the first mean something — a suite that failed for any other reason would satisfy an exit
# check alone, which is the shape the record-level probes had.
probe_notices() {
  [[ "$run_code" != 0 ]] ||
    problems+=("with $1, $SUBJECT_NAME exited 0: the broken Draft PR order went unnoticed. It said: $(flat "$run_out")")
  grep -Fq -- "$2" <<< "$run_out" ||
    problems+=("with $1, $SUBJECT_NAME reported no problem line saying \"$2\", so nothing it prints names the broken order. It said: $(flat "$run_out")")
}

# One criterion, one case: the line-level Draft PR checks still fail, and say what is wrong,
# for each way the step's command order breaks. The three sabotages are one criterion rather
# than three — they are the one contract #236 collapsed, and a case pinning only one of them
# would pass a suite whose other checks had gone vacuous the same way. The control run comes
# first and is part of the same criterion: without it a failure below says only that the
# subject fails in a scratch tree.
name="skill-metrics.test.sh fails, naming the misplaced command, when SKILL.md's Draft PR block runs gh pr create after the metrics: commit, gh pr edit before it, or a gh pr edit carrying no committed report"
problems=()
tree=""
subject_copy=""
skill_copy=""
run_out=""
run_code=0

if plant_tree; then
  run_subject
  [[ "$run_code" == 0 ]] ||
    problems+=("against an unbroken $SKILL_REL in the scratch tree, $SUBJECT_NAME exited $run_code, so no failure below can be read as the sabotage's. It said: $(flat "$run_out")")
fi
[[ -z "$tree" ]] || rm -rf "$tree"
tree=""

# The three ways the Draft PR order breaks, each as the whole-line edit that causes it and
# the problem line the subject owes for it, in the repository's `IFS='|' read` table idiom so
# a way, its edit and its expected answer are one row rather than three lists a loop rejoins.
# The first two move a command past another; the third leaves `gh pr edit` where it is and
# takes the committed report out of its `--body`, which is the break a record-level probe
# could never see. The expected texts are fixed strings the subject prints, not patterns.
while IFS='|' read -r label kind a b expected; do
  [[ -n "$label" ]] || continue
  if plant_tree; then
    sabotage_skill "$kind" "$a" "$b"
    probe_sabotage_is_real "$label"
    run_subject
    probe_notices "$label" "$expected"
  fi
  [[ -z "$tree" ]] || rm -rf "$tree"
  tree=""
done <<'SABOTAGES'
gh pr create after the metrics: commit|before|git commit -m "metrics:|gh pr create --draft|BEFORE gh pr create at SKILL.md:
gh pr edit before the metrics: commit|before|gh pr edit|git commit -m "metrics:|BEFORE the metrics: commit at SKILL.md:
gh pr edit carrying no committed report|sub|gh pr edit|   gh pr edit <pr-url> --body "<the body above>"|does not put the contents of .tdd/issue-<n>-metrics.md in its --body
SABOTAGES

report "$name"
echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
