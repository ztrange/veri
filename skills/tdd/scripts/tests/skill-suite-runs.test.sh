#!/usr/bin/env bash
# Unit test for what skills/tdd/SKILL.md and this repository's CLAUDE.md say about which
# leaves run the full test suite, read as text.
#
# Contract under test:
#   SKILL.md's Red phase says its leaf runs the suite holding the new case; its Refactor
#   loop says the transform leaf runs the suites covering the touched files.
#   CLAUDE.md names which leaves run the full suite, and no longer claims every leaf runs it
#   after every edit.
#
# Run: scripts/tests/skill-suite-runs.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"
claude_md="CLAUDE.md"
claude_path="$ROOT/$claude_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"


doc_text() {
  from="$3" awk -v h="$2" '
    BEGIN { from = ENVIRON["from"] }
    !in_s && index($0, h) == 1 { in_s = 1; want = (from == "" ? 1 : 0); next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ from) want = 1
      if (want) print
    }' "$1" | plain --join
}

text=""
need_text() {
  text="$(doc_text "$skill_path" "$1" "${2-}")"
  [[ -n "${text// /}" ]] && return 0
  problems+=("$skill_md has no '$1' section to read — what that phase's leaf runs could not be established")
  return 1
}

says() {
  [[ "$text" =~ $1 ]] || problems+=("$2")
}

paragraphs() {
  awk 'BEGIN { RS = "" } { gsub(/\n/, " "); print }' "$1" | plain
}

need_idiom() {
  text="$(paragraphs "$claude_path" | grep -E '^a suite whose subject is the docs pipeline')"
  [[ -n "$text" ]] && return 0
  problems+=("$claude_md has no paragraph opening 'a suite whose subject is the docs pipeline' to read")
  return 1
}


name="$claude_md's Testing idiom paragraph says a revise leaf runs the tiers of the phase it redoes"
problems=()
if need_idiom; then
  says 'revise[- ](leaf|leaves)|revise-(red|green|refactor)' \
    "$claude_md's Testing idiom paragraph never names the revise leaves"
  says '(tier|suites)[^.]*phase (it|they|the leaf) (redoes|redo|is redoing|are redoing)' \
    "$claude_md's Testing idiom paragraph never says a revise leaf runs the tiers of the phase it redoes"
fi
report "$name"

name="$skill_md names no full-suite run inside a step's cycle"
problems=()
text="$(awk 'index($0, "#### Red") == 1 { s = 1 } index($0, "### 4. Draft PR") == 1 { exit } s' "$skill_path" | plain | tr -s '\n ' ' ')"
if [[ -n "${text// /}" ]]; then
  negated='(^| )(not|neither|nor|never|no)( [a-z-]+){0,5} full suite'
  to_draft_pr='full[- ]suite run (in|at) (4\. )?draft pr'
  while [[ "$text" =~ $negated ]]; do text="${text/"${BASH_REMATCH[0]}"/}"; done
  while [[ "$text" =~ $to_draft_pr ]]; do text="${text/"${BASH_REMATCH[0]}"/}"; done
  [[ "$text" =~ [^.]{0,60}(full\ suite|full-suite\ run)[^.]{0,40} ]] &&
    problems+=("$skill_md names a full-suite run inside a step's cycle: ${BASH_REMATCH[0]}")
else
  problems+=("$skill_md has no text from '#### Red' to '### 4. Draft PR' to read")
fi
report "$name"

name="#1300: $skill_md runs suite-reported.sh before the verifier after develop-diff, revise-diff-<k> and each phase leaf, and bails report-missing on its exit 2"
problems=()
check_report_section() {
  local label="$1" section="$2" call="$3" body first_check first_verifier
  body="$(doc_text "$skill_path" "$section" "")"
  [[ "$body" == *'suite-reported.sh'* ]] || { problems+=("$label: never runs suite-reported.sh"); return; }
  [[ "$body" == *"$call"* ]] || problems+=("$label: never runs $call")
  [[ "$body" == *'report-missing'* ]] || problems+=("$label: never names the report-missing bail")
  first_check="${body%%suite-reported.sh*}"
  first_verifier="${body%%verify-*}"
  ((${#first_check} <= ${#first_verifier})) || problems+=("$label: the check comes after the verifier is launched")
}
check_report_section "diff-checked step" '#### A `⟦diff-checked⟧` step' 'suite-reported.sh develop-diff'
check_report_section "phases step" '#### A `⟦phases: …⟧` step' 'suite-reported.sh develop-<phase>'
report "$name"

name="#1300: $skill_md runs suite-reported.sh only after a leaf whose prompt asks for a SUITE: line, never after the refactor leaf or a revise of red, green or refactor"
problems=()
for pair in 'Refactor loop|#### Refactor loop' 'Revising on a REJECT|## Revising on a REJECT'; do
  body="$(doc_text "$skill_path" "${pair#*|}" "")"
  [[ "$body" != *'suite-reported.sh'* ]] || problems+=("${pair%%|*}: runs suite-reported.sh after a leaf whose prompt asks for no SUITE: line")
done
diff_checked="$(doc_text "$skill_path" '#### A `⟦diff-checked⟧` step' "")"
[[ "$diff_checked" == *'suite-reported.sh revise-diff-<k>'* ]] || problems+=("diff-checked step: never runs suite-reported.sh revise-diff-<k>, the leaf the conductor launches")
report "$name"

name="#1568: $skill_md runs suite-reported.sh develop-green between the leaf's wait and verify-green's launch, and keeps a looks-wrong green's REJECT rather than a report-missing bail"
problems=()
green="$(doc_text "$skill_path" '#### Green' "")"
if [[ "$green" != *'suite-reported.sh develop-green'* ]]; then
  problems+=("Green section: never runs suite-reported.sh develop-green")
else
  before_check="${green%%suite-reported.sh develop-green*}"
  [[ "$before_check" == *'wait-leaf.sh develop-green'* ]] || problems+=("Green section: the check does not come after develop-green's wait")
  [[ "$before_check" != *'supervise.sh verdict-green'* ]] || problems+=("Green section: the check comes after verify-green is launched")
  after_check="${green#*suite-reported.sh develop-green}"
  after_check="${after_check:0:1200}"
  [[ "$after_check" == *'report-missing'* ]] || problems+=("Green section: never names the report-missing bail for a missing SUITE: line")
  [[ "$after_check" =~ looks\ wrong ]] || problems+=("Green section: never says a green that stops because the test looks wrong is exempt")
  [[ "$after_check" == *reject* ]] || problems+=("Green section: never says that green keeps its verify-green REJECT outcome")
fi
report "$name"

name="#1568: $skill_md runs suite-reported.sh develop-structural between the transform leaf's wait and its transform verifier, and keeps an out-of-bounds skip's REJECT rather than a report-missing bail"
problems=()
whole="$(plain --join < "$skill_path")"
structural="${whole#*'build-develop-prompt.sh structural'}"
if [[ "$structural" == "$whole" ]]; then
  problems+=("structural pass: never launches develop-structural")
else
  structural="${structural:0:6000}"
  if [[ "$structural" != *'suite-reported.sh develop-structural'* ]]; then
    problems+=("structural pass: never runs suite-reported.sh develop-structural")
  else
    before_check="${structural%%suite-reported.sh develop-structural*}"
    [[ "$before_check" != *'supervise.sh verdict-transform'* ]] || problems+=("structural pass: the check comes after the transform verifier is launched")
    after_check="${structural#*suite-reported.sh develop-structural}"
    after_check="${after_check:0:1200}"
    [[ "$after_check" == *'report-missing'* ]] || problems+=("structural pass: never names the report-missing bail for a missing SUITE: line")
    [[ "$after_check" =~ out-of-bounds|leave\ the\ tree ]] || problems+=("structural pass: never says an out-of-bounds skip is exempt")
    [[ "$after_check" == *'transform reject and the next candidate'* ]] || problems+=("structural pass: never says that skip keeps its transform REJECT outcome")
  fi
fi
report "$name"

name="#1568: $skill_md runs suite-reported.sh develop-transform after the refactor-kind transform leaf and before its blind transform verifier"
problems=()
whole="$(plain --join < "$skill_path")"
cover_transform="${whole#*'refactor-kind step therefore runs'}"
if [[ "$cover_transform" == "$whole" ]]; then
  problems+=("Cover → Transform → Verify: the refactor-kind step's passage is missing")
else
  cover_transform="${cover_transform:0:2500}"
  if [[ "$cover_transform" != *'suite-reported.sh develop-transform'* ]]; then
    problems+=("Cover → Transform → Verify: never runs suite-reported.sh develop-transform")
  else
    before_check="${cover_transform%%suite-reported.sh develop-transform*}"
    [[ "$before_check" =~ transform\ +leaf\ +applies ]] || problems+=("Cover → Transform → Verify: the check does not come after the transform leaf")
    [[ ! "$before_check" =~ blind\ +transform\ +verifier ]] || problems+=("Cover → Transform → Verify: the check comes after the transform verifier")
  fi
fi
report "$name"

name="#991: doc_text given the from regex '^5\. ' starts at the line '5. y', not at '5x y'"
fixture="$(scratch_dir)/doc.md"
printf '## Section\n5x y\n5. y\n' > "$fixture"
expect_eq "$name" "5. y " "$(doc_text "$fixture" '## Section' '^5\. ')"

finish
