#!/usr/bin/env bash
# Unit tests for scripts/refactor-triage.sh — reads a finished refactor leaf's report on
# stdin and says whether another refactor leaf is worth launching.
#
# Contract under test:
#   report on stdin → exit 0, printing the structural candidates, when at least one is
#                     listed.
#                   → exit 3 when only cosmetic candidates or `none` remain.
#                   → exit 2, diagnostic on stderr and nothing on stdout, when a candidate
#                     line carries no class or an unknown one, or the report lists no
#                     `CANDIDATES:` line at all.
#   SKILL.md's *Refactor loop* runs the script and branches on each answer.
#
# Run: scripts/tests/refactor-triage.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TRIAGE="$HERE/../refactor-triage.sh"

source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"

name="a report listing structural candidates exits 0 and prints them"
problems=()

leaf_report="$(mktemp)"
cat > "$leaf_report" <<'REPORT'
RESULT: applied "fold verify.sh's two prompt paths into one", suite green
FLAGS: none
CANDIDATES: structural | fold verify.sh's two mktemp calls into one helper
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: structural | rename $tmp to $prompt_file, which is what it holds
REPORT

out="$(mktemp)"
"$TRIAGE" <"$leaf_report" >"$out" 2>/dev/null && code=0 || code=$?

[[ "$code" == 0 ]] ||
  problems+=("want exit 0 while structural candidates remain, got $code")

lines="$(grep -c '' "$out")"
[[ "$lines" == 2 ]] ||
  problems+=("want the 2 structural candidates on stdout, one per line, got $lines line(s): $(printf '%q' "$(cat "$out")")")

while IFS= read -r transform; do
  hits="$(grep -cF "$transform" "$out")"
  [[ "$hits" == 1 ]] ||
    problems+=("want the structural candidate '$transform' named on exactly 1 line of stdout, found on $hits")
done <<'STRUCTURAL'
fold verify.sh's two mktemp calls into one helper
rename $tmp to $prompt_file, which is what it holds
STRUCTURAL

cosmetic='reflow the header comment to ninety columns'
grep -qF "$cosmetic" "$out" &&
  problems+=("the cosmetic candidate '$cosmetic' is on stdout; only structural ones belong there")

rm -f "$leaf_report" "$out"
report "$name"

name="a report with no structural candidate left exits 3"
problems=()

cosmetic_only="$(mktemp)"
cat > "$cosmetic_only" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: cosmetic | reflow the header comment to ninety columns
CANDIDATES: cosmetic | re-cite SKILL.md's Refactor entry by section, not line
REPORT

nothing_left="$(mktemp)"
cat > "$nothing_left" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
FLAGS: none
CANDIDATES: none
REPORT

stops_probe() {
  local label="$1" fixture="$2" code
  "$TRIAGE" <"$fixture" >/dev/null 2>&1 && code=0 || code=$?
  [[ "$code" == 3 ]] ||
    problems+=("$label: want exit 3 — nothing worth another leaf — got $code")
}

stops_probe "only cosmetic candidates" "$cosmetic_only"
stops_probe "CANDIDATES: none" "$nothing_left"

rm -f "$cosmetic_only" "$nothing_left"
report "$name"

name="a malformed report exits 2 with a diagnostic on stderr and nothing on stdout"
problems=()

no_class="$(mktemp)"
cat > "$no_class" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: fold verify.sh's two prompt paths into one
REPORT

unknown_class="$(mktemp)"
cat > "$unknown_class" <<'REPORT'
RESULT: applied "extract the two mktemp calls into one helper", suite green
FLAGS: none
CANDIDATES: cosmic | reflow the header comment to ninety columns
REPORT

no_candidates="$(mktemp)"
cat > "$no_candidates" <<'REPORT'
RESULT: applied "inline the single-use $phase_label variable", suite green
FLAGS: none
REPORT

malformed_probe() {
  local label="$1" fixture="$2" out err code
  out="$(mktemp)" err="$(mktemp)"
  "$TRIAGE" <"$fixture" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2 — no answer could be obtained — got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
  rm -f "$out" "$err"
}

malformed_probe "a candidate line with no class" "$no_class"
malformed_probe "a candidate line with an unknown class" "$unknown_class"
malformed_probe "a report with no CANDIDATES: line" "$no_candidates"

rm -f "$no_class" "$unknown_class" "$no_candidates"
report "$name"

ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


refactor_loop() {
  awk -v h='#### Refactor loop' \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" | plain
}

loop_lines="$(refactor_loop)"

line_of() {
  head -1 < <(grep -nE "$1" <<<"$loop_lines") | cut -d: -f1
}

name="$skill_md's refactor loop calls refactor-triage.sh on each committed transform and stops on exit 3 and exit 2"
problems=()

if [[ -z "${loop_lines// /}" ]]; then
  problems+=("$skill_md has no '#### Refactor loop' section to read — where the conductor calls refactor-triage.sh could not be established")
else
  triage_at="$(line_of 'refactor-triage\.sh')"
  commit_at="$(line_of 'git commit -m "refactor:')"

  if [[ -z "$triage_at" ]]; then
    problems+=("$skill_md's refactor loop never names refactor-triage.sh, so nothing asks whether another leaf is worth launching and the budget stays the only thing that ends the loop")
  elif [[ -z "$commit_at" ]]; then
    problems+=("$skill_md's refactor loop no longer commits the transform, so whether refactor-triage.sh is called on a committed one could not be established")
  elif [[ "$triage_at" -lt "$commit_at" ]]; then
    problems+=("$skill_md's refactor loop calls refactor-triage.sh (line $triage_at of the section) before it commits the transform (line $commit_at), so the report is triaged against a transform that is not in the history yet")
  fi

  # hazard: BSD grep refuses an interval bound over 255.
  windows="$(tr '\n' ' ' <<<"$loop_lines" | grep -oE 'refactor-triage\.sh.{0,250}')"

  grep -qE '(exits? 3.{0,120}stop|stop.{0,120}exits? 3)' <<<"$windows" ||
    problems+=("$skill_md's refactor loop never says refactor-triage.sh's exit 3 stops it, so the third stop condition is documented nowhere the conductor reads")
  grep -qE '(exits? 2.{0,160}narrat|narrat.{0,160}exits? 2)' <<<"$windows" ||
    problems+=("$skill_md's refactor loop never says a malformed report — refactor-triage.sh's exit 2 — is narrated, so the conductor is left to bail on one instead of finishing the step it has already committed")
fi

report "$name"

name="$skill_md's ### 🛠️ Refactor comment names which of the three stop conditions ended the loop and files the leftovers by class"
problems=()

narration="$(awk '!inside && /###/ && /refactor/ { inside = 1 }
                  inside && /^ *- pass:/ { exit }
                  inside' <<<"$loop_lines" | tr '\n' ' ')"

if [[ -z "${narration// /}" ]]; then
  problems+=("$skill_md's refactor loop names no ### comment to post, so what the ### 🛠️ Refactor comment must say could not be established")
else
  grep -qF 'nothing left to tidy' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to say the loop ran dry — 'nothing left to tidy', the first of the three stop conditions")
  grep -qF 'budget' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the budget — the second of the three stop conditions")
  grep -qE '(no|nothing|none)[ a-z]{0,14}structural|only cosmetic|refactor-triage' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to name the third stop condition — that no structural candidate was left — so a loop the triage ended is narrated as one of the other two")
  grep -qF 'cosmetic' <<<"$narration" ||
    problems+=("$skill_md's ### 🛠️ Refactor comment never mentions cosmetic leftovers, so the two classes of candidate go into one undifferentiated backlog")
  grep -qE 'separat|apart|split|by class|per class|each class|own list|own line|own heading|own group' <<<"$narration" ||
    problems+=("$skill_md never tells the ### 🛠️ Refactor comment to keep the structural leftovers apart from the cosmetic ones — a mixed list is a backlog nobody can size")
fi

report "$name"

name="refactor-triage.sh run through a symlink to the skill directory and from another working directory answers a structural, a cosmetic-only and an empty report as it does when run in place"
problems=()
work="$(scratch_dir)"
ln -s "$(cd "$HERE/../.." && pwd)" "$work/linked-skill"
mkdir -p "$work/elsewhere"
printf 'CANDIDATES: structural | extract the parser\nCANDIDATES: cosmetic | rename a local\n' >"$work/structural"
printf 'CANDIDATES: cosmetic | rename a local\n' >"$work/cosmetic"
: >"$work/empty"
while IFS='|' read -r fixture exp_code; do
  "$TRIAGE" <"$work/$fixture" >"$work/in-place.out" 2>"$work/in-place.err" && in_place_code=0 || in_place_code=$?
  (cd "$work/elsewhere" && "$work/linked-skill/scripts/refactor-triage.sh") <"$work/$fixture" \
    >"$work/linked.out" 2>"$work/linked.err" && linked_code=0 || linked_code=$?
  [[ "$linked_code" == "$exp_code" ]] ||
    problems+=("$fixture report linked: want exit $exp_code, got $linked_code, stderr $(printf '%q' "$(cat "$work/linked.err")")")
  [[ "$linked_code" == "$in_place_code" ]] ||
    problems+=("$fixture report: linked exit $linked_code, in place exit $in_place_code")
  cmp -s "$work/in-place.out" "$work/linked.out" ||
    problems+=("$fixture report: linked stdout $(printf '%q' "$(cat "$work/linked.out")"), in place $(printf '%q' "$(cat "$work/in-place.out")")")
  cmp -s "$work/in-place.err" "$work/linked.err" ||
    problems+=("$fixture report: linked stderr $(printf '%q' "$(cat "$work/linked.err")"), in place $(printf '%q' "$(cat "$work/in-place.err")")")
done <<'PROBES'
structural|0
cosmetic|3
empty|2
PROBES
report "$name"

name="refactor-triage.sh's two diagnostics are exact: an empty report and an unknown class each exit 2 with that one line on stderr and nothing on stdout"
problems=()
work="$(scratch_dir)"
: >"$work/empty"
printf 'CANDIDATES: cosmic | x\n' >"$work/cosmic"
while IFS='|' read -r fixture want_err; do
  "$TRIAGE" <"$work/$fixture" >"$work/out" 2>"$work/err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$fixture report: want exit 2, got $code")
  [[ -s "$work/out" ]] &&
    problems+=("$fixture report: want nothing on stdout, got $(printf '%q' "$(cat "$work/out")")")
  printf '%s\n' "$want_err" >"$work/want"
  cmp -s "$work/want" "$work/err" ||
    problems+=("$fixture report: want stderr $(printf '%q' "$(cat "$work/want")"), got $(printf '%q' "$(cat "$work/err")")")
done <<'PROBES'
empty|refactor-triage: the report has no CANDIDATES: line
cosmic|refactor-triage: candidate line has no class, or one that is neither structural nor cosmetic: CANDIDATES: cosmic | x
PROBES
report "$name"

finish
