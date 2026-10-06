#!/usr/bin/env bash
# Unit tests for scripts/refactor-owed.sh — the file that carries a run's structural
# leftovers from each step's refactor loop into the draft PR.
#
# Contract under test:
#   refactor-owed.sh appends a step's structural candidates to
#   `.tdd/issue-<n>-refactor-owed.md` and renders that file as a PR-body section.
#
# Run: scripts/tests/refactor-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OWED="$HERE/../refactor-owed.sh"

source "$HERE/lib/harness.sh"

line_of() {
  head -1 < <(grep -nF "$2" "$1") | cut -d: -f1
}

answers_none_on() {
  local verb="$1" owed_file="$2" what="$3" why="$4" out code printed
  out="$(mktemp)"
  "$OWED" "$verb" "$owed_file" >"$out" 2>/dev/null && code=0 || code=$?

  [[ "$code" == 3 ]] ||
    problems+=("want exit 3 from $verb on $what, got $code")

  printed="$(cat "$out")"
  [[ -z "$printed" ]] ||
    problems+=("$verb printed '$printed' on stdout for $what$why")

  rm -f "$out"
}

answers_none() {
  local verb="$1" why="$2" missing_file empty_file
  missing_file="$(mktemp)"
  rm -f "$missing_file"
  empty_file="$(mktemp)"

  answers_none_on "$verb" "$missing_file" "an absent file" "$why"
  answers_none_on "$verb" "$empty_file" "a file holding no candidate" "$why"

  rm -f "$empty_file"
}

under_step() {
  local file="$1" step="$2" transform="$3" step_at candidate_at
  step_at="$(line_of "$file" "$step")"
  candidate_at="$(line_of "$file" "$transform")"
  if [[ -z "$candidate_at" ]]; then
    problems+=("$file does not carry the candidate '$transform'")
  elif [[ -z "$step_at" ]]; then
    problems+=("$file carries '$transform' but never names the step '$step' that owes it")
  elif [[ "$step_at" -gt "$candidate_at" ]]; then
    problems+=("$file names the step '$step' on line $step_at, below its candidate '$transform' on line $candidate_at — the candidate is not under its step")
  fi
}

name="append writes only the structural candidates to the file, under the named step"
problems=()

owed_file="$(mktemp)"
step='refactor-owed.sh append writes only the structural CANDIDATES lines'
"$OWED" append "$owed_file" "$step" <<'REPORT' && code=0 || code=$?
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from append, got $code")

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

under_step "$owed_file" "$step" 'fold verify.sh'"'"'s two mktemp calls into one helper'

rm -f "$owed_file"
report "$name"

name="render exits 3 and prints nothing when the file is absent or holds no candidate"
problems=()

answers_none render "; a PR body must not carry a heading promising leftovers nobody left"
report "$name"


name="refactor-owed.sh, run through a symlink to the skill directory from another working directory, answers append, render and list as in place, the owed file read relative to the caller's working directory"
problems=()

work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/in-place" "$work/elsewhere"
cat >"$work/report.txt" <<'REPORT'
CANDIDATES: structural | extract the parser
CANDIDATES: cosmetic | rename a local
CANDIDATES: test-only | fold the fixtures
REPORT

for where in in-place elsewhere; do
  if [[ "$where" == in-place ]]; then script="$OWED"; else script="$work/linked-skill/scripts/refactor-owed.sh"; fi
  (cd "$work/$where" && "$script" append owed.md 'the step' < "$work/report.txt") \
    >"$work/$where.append.out" 2>/dev/null && echo 0 >"$work/$where.append.code" || echo $? >"$work/$where.append.code"
  for verb in render list; do
    (cd "$work/$where" && "$script" "$verb" owed.md) \
      >"$work/$where.$verb.out" 2>/dev/null && echo 0 >"$work/$where.$verb.code" || echo $? >"$work/$where.$verb.code"
  done
done

[[ -s "$work/elsewhere/owed.md" ]] ||
  problems+=("append through the symlink wrote no owed.md in the caller's working directory")
cmp -s "$work/in-place/owed.md" "$work/elsewhere/owed.md" ||
  problems+=("owed file through the symlink differs: $(diff "$work/in-place/owed.md" "$work/elsewhere/owed.md")")
for verb in append render list; do
  [[ "$(cat "$work/in-place.$verb.code")" == 0 ]] ||
    problems+=("$verb in place: want exit 0, got $(cat "$work/in-place.$verb.code")")
  [[ "$(cat "$work/elsewhere.$verb.code")" == "$(cat "$work/in-place.$verb.code")" ]] ||
    problems+=("$verb through the symlink: exit $(cat "$work/elsewhere.$verb.code"), in place $(cat "$work/in-place.$verb.code")")
  cmp -s "$work/in-place.$verb.out" "$work/elsewhere.$verb.out" ||
    problems+=("$verb stdout through the symlink differs: $(diff "$work/in-place.$verb.out" "$work/elsewhere.$verb.out")")
done

report "$name"


name="refactor-owed.sh out-of-scope prints the owed file's out-of-scope candidates not recorded as applied, one per line without the prefix, and exits 3 with nothing on stdout when none is left or the file is missing"
problems=()

work="$(scratch_dir)"
cat >"$work/owed.md" <<'OWED'
### step 2
- extract the parser
- out-of-scope | remove gh() from coverage_blocker.py
- out-of-scope | drop the subprocess import
- out-of-scope | fold the two loaders
applied | 1b4ed26e6 | out-of-scope | remove gh() from coverage_blocker.py
OWED
printf '%s\n' 'drop the subprocess import' 'fold the two loaders' >"$work/want.out"

"$OWED" out-of-scope "$work/owed.md" >"$work/got.out" 2>/dev/null && code=0 || code=$?
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from out-of-scope on a file with unapplied candidates, got $code")
diff "$work/want.out" "$work/got.out" >/dev/null ||
  problems+=("out-of-scope stdout differs from the two unapplied candidates:" "$(diff "$work/want.out" "$work/got.out")")

cat >"$work/all-applied.md" <<'OWED'
### step 2
- extract the parser
- out-of-scope | remove gh() from coverage_blocker.py
applied | 1b4ed26e6 | out-of-scope | remove gh() from coverage_blocker.py
OWED
answers_none_on out-of-scope "$work/all-applied.md" "a file whose every out-of-scope candidate is applied" ""
answers_none_on out-of-scope "$work/missing.md" "an absent file" ""

report "$name"


name="refactor-owed.sh with no argument, or with the unknown verb bogus and a file, exits 2 with nothing on stdout and the three usage lines on stderr"
problems=()

work="$(scratch_dir)"
cat >"$work/usage.want" <<'USAGE'
refactor-owed: usage: refactor-owed.sh append <file> '<STEP>' < leaf-report.txt
                      refactor-owed.sh render <file>
                      refactor-owed.sh list <file>
USAGE

for call in none bogus; do
  if [[ "$call" == none ]]; then args=(); else args=(bogus "$work/owed.md"); fi
  "$OWED" "${args[@]}" >"$work/$call.out" 2>"$work/$call.err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$call: want exit 2, got $code")
  [[ ! -s "$work/$call.out" ]] ||
    problems+=("$call: printed '$(cat "$work/$call.out")' on stdout")
  diff "$work/usage.want" "$work/$call.err" >/dev/null ||
    problems+=("$call: stderr differs from the three usage lines:" "$(diff "$work/usage.want" "$work/$call.err")")
done

report "$name"


name="refactor-owed.sh append whose owed file path is a directory, fed one structural candidate, exits 1 with nothing on stdout"
problems=()

work="$(scratch_dir)"
mkdir -p "$work/owed.md"
"$OWED" append "$work/owed.md" 'the step' >"$work/append.out" 2>/dev/null <<'REPORT' && code=0 || code=$?
CANDIDATES: structural | extract the parser
REPORT

[[ "$code" == 1 ]] ||
  problems+=("want exit 1 from append into a directory, got $code")
[[ ! -s "$work/append.out" ]] ||
  problems+=("append printed '$(cat "$work/append.out")' on stdout")

report "$name"


finish
