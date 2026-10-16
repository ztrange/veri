#!/usr/bin/env bash
# Unit tests for what the conductor's Green section in skills/tdd/SKILL.md does with a
# developer leaf that answered `SPLIT:` instead of an implementation, read as text.
#
# Contract under test:
#   1. SKILL.md's Green section, on `SPLIT:`, restores the tree to `HEAD`, passes the
#      split criteria to ONE `add-ledger-step.sh … before '<STEP>'` call, commits the grown
#      ledger, emits `step-split`, and loops back to `next-unchecked.sh`, which hands over
#      the first split step.
#   2. When `add-ledger-step.sh` exits 1 on that branch, the run bails with cause
#      `step-too-big`, which SKILL.md's Bailing causes list classifies as a **process**
#      failure.
#   3. The three split calls pass no --criterion and say a split keeps its anchor's criterion;
#      the uncovered-spec call passes --criterion <k>, read from the issue's numbered
#      acceptance criteria, one call per criterion, bailing naming the cause on exit 2.
#   4. The ⟦suite-repair⟧ and ⟦ci-repair⟧ add-ledger-step.sh calls, which keep the anchor's
#      criterion on purpose, say beside them that they pass no --criterion because the repair
#      step serves its anchor's criterion.
#   5. The add-ledger-step.sh entry under The scripts says --criterion <k> tags the added steps
#      with criterion k for any whole number k ≥ 1, carried by a step or not, and its exit 2
#      cases include a k that is not a whole number ≥ 1.
#   6. The Green section judges a `⟦ci-repair⟧` step's green against a fresh CI run on the
#      pushed fix — `wait-ci.sh` on the pushed sha — not only a local `make test`, and a red
#      CI there is the second red that bails `ci-red`.
#
# Run: scripts/tests/skill-green-split.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/plain.sh"
source "$HERE/lib/window.sh"


green_heading='#### Green'

green_section() {
  awk -v h="$green_heading" \
    'index($0, h) == 1 { inside = 1; next } inside && /^#/ { exit } inside' "$skill_path" |
    plain --join
}
section="$(green_section)"

unreadable=""
[[ -n "${section// /}" ]] ||
  unreadable="$skill_md has no '$green_heading' section to read —"

add_ledger_step='\$s/add-ledger-step\.sh'

bailing_causes() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s {
      if (!want && $0 ~ /killed-stuck/) want = 1
      if (want) print
    }' "$skill_path" | plain --join
}


step_too_big_cause() {
  awk '
    !in_s && index($0, "## Bailing") == 1 { in_s = 1; next }
    in_s && /^#/ { exit }
    in_s && inside && (/^- / || /^$/) { exit }
    in_s && /^- `step-too-big`/ { inside = 1 }
    inside' "$skill_path" | plain --join
}

split_calls() {
  grep -nE '\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*(instead-of|before "\$\(\$S/next-unchecked\.sh)' "$skill_path"
}

uncovered_spec_call() {
  grep -nE '\$S/add-ledger-step\.sh (--criterion [^ ]+ )?\.tdd/.*after "\$\(\$S/next-pending-refactor\.sh' "$skill_path"
}

call_neighbourhood() {
  awk -v at="${1%%:*}" 'NR >= at - 20 && NR <= at + 20' "$skill_path" | plain --join
}

add_ledger_step_entry() {
  awk '
    inside && (/^- / || /^$/) { exit }
    /^- `\$S\/add-ledger-step\.sh/ { inside = 1 }
    inside' "$skill_path" | plain --join
}
entry="$(add_ledger_step_entry)"
no_entry="$skill_md has no '- \`\$S/add-ledger-step.sh' entry under The scripts"

repair_call_neighbourhood() {
  awk -v tag="$1" '
    { text[NR] = $0 }
    index($0, "$S/add-ledger-step.sh") && index($0, tag) { at = NR }
    END { if (at) for (i = at - 20; i <= at + 20; i++) if (i in text) print text[i] }
  ' "$skill_path" | plain --join
}

require() {
  grep -F -- "$1" > /dev/null <<<"$2" || problems+=("$3")
}

one_line() {
  tr -d '*`' | tr '\n' ' ' | tr -s ' '
}

green_paragraph() {
  awk 'index($0, "On a `⟦replaces-case⟧` step, a PASS is accepted") { inside = 1 }
       inside && /^3\. / { exit }
       inside' "$skill_path" | one_line
}
section="$(green_paragraph)"

pin_paragraph() {
  awk 'index($0, "A `⟦replaces-case⟧` step whose Red reports") == 1 { inside = 1 }
       inside && index($0, "Every other step takes the verdict") { exit }
       inside' "$skill_path" | one_line
}
section="$(pin_paragraph)"

finish
