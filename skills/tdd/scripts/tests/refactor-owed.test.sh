#!/usr/bin/env bash
# Unit tests for scripts/refactor-owed.sh — the file that carries a run's structural
# leftovers from each step's refactor loop into the draft PR. Zero-dependency plain-shell
# asserts, same idiom as refactor-triage.test.sh, the suite for the script whose answer
# ends that loop.
#
# Why this exists (issue #359, part of #354): when a step's refactor stops with structural
# candidates still listed, nothing records them. `.tdd/develop-refactor.out` is overwritten
# by the next step, so by the draft PR every step's leftovers but the last are gone. This
# script appends them to `.tdd/issue-<n>-refactor-owed.md`, which the ledger's .gitignore
# rule already tracks, and renders them as a PR-body section.
#
# Run: scripts/tests/refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OWED="$HERE/../refactor-owed.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did. Same helper
# refactor-triage.test.sh uses.
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

# 1. what `append` keeps. A develop-refactor report piped in carries both classes of
#    candidate — structural and cosmetic, as prompts/develop-refactor.md's *The two classes
#    of candidate* defines them — and only the structural ones are work a follow-up owes.
#    A cosmetic leftover written into the file would put a reflowed comment in front of the
#    human deciding the merge, which is the mixed backlog #149 already refused once.
#
#    The step name is the other half: the file accumulates across a whole run, so a
#    candidate that does not say which step left it behind cannot be acted on. "Under that
#    step" is pinned as order — the step's name appears before its candidates — not as a
#    heading syntax, which is the script's business.
#
#    The fixture is a whole report rather than bare candidate lines because that is what the
#    conductor pipes in: the leaf's last lines, verbatim (develop-refactor.md, *Report*).
#    It is written to a file rather than through `$(cat <<'REPORT' … )` for the reason
#    refactor-triage.test.sh records: a command substitution is scanned for its closing
#    paren without regard for the heredoc inside it, so the apostrophe in `verify.sh's`
#    below would read as an unterminated quote.
name="append writes only the structural candidates to the file, under the named step"
problems=()

leaf_report="$(mktemp)"
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

owed_file="$(mktemp)"
step='refactor-owed.sh append writes only the structural CANDIDATES lines'
"$OWED" append "$owed_file" "$step" <"$leaf_report" && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from append, got $code")

# -F so a transform is matched as the literal a leaf wrote, not as a pattern: `$` and `'`
# are ordinary characters in a candidate.
while IFS= read -r transform; do
  hits="$(grep -cF "$transform" "$owed_file")"
  [[ "$hits" == 1 ]] ||
    problems+=("want the structural candidate '$transform' on exactly 1 line of $owed_file, found on $hits")
done <<'STRUCTURAL'
fold verify.sh's two mktemp calls into one helper
rename $tmp to $prompt_file, which is what it holds
STRUCTURAL

cosmetic='reflow the header comment to ninety columns'
grep -qF "$cosmetic" "$owed_file" &&
  problems+=("the cosmetic candidate '$cosmetic' is in $owed_file; only structural leftovers are work a follow-up owes")

# Order rather than syntax: the step is named, and it is named before the candidates it
# left behind, which is the whole of what "under that step" means to a reader.
step_at="$(grep -nF "$step" "$owed_file" | head -1 | cut -d: -f1)"
first_candidate_at="$(grep -nF 'fold verify.sh'"'"'s two mktemp calls into one helper' "$owed_file" | head -1 | cut -d: -f1)"
if [[ -z "$step_at" ]]; then
  problems+=("$owed_file never names the step '$step', so nothing says which step owes these candidates")
elif [[ -n "$first_candidate_at" && "$step_at" -gt "$first_candidate_at" ]]; then
  problems+=("$owed_file names the step on line $step_at, after its first candidate on line $first_candidate_at — the candidates are not under the step")
fi

rm -f "$leaf_report" "$owed_file"
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
