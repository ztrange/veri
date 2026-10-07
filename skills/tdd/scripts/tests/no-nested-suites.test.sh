#!/usr/bin/env bash
# Unit test: no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another
# real suite from this directory.
#
# Contract under test:
#   No suite in the roster below names another real suite, outside a comment and outside
#   the exemption table, in a shape that launches it:
#   - its basename right after a `$`-prefixed path on the same line;
#   - its basename bare, quoted or not (a bracketed `[name:<line>]` table key excepted);
#   - its full repo-relative path, when the same file also calls `cp` or `make … TESTS=`.
#   An offender is reported as `<suite>:<line>` with the suite it names. An exemption
#   carries a reason.
#
# Run: skills/tdd/scripts/tests/no-nested-suites.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
suites_dir="skills/tdd/scripts/tests"


source "$HERE/lib/harness.sh"

flat() { local s="$1"; printf '%s' "${s//$'\n'/\/}"; }

declare -A EXEMPT=(
  [no-nested-suites.test.sh]="its own exemption table and header name every suite below by basename outside a comment; that is the policy this file states, not a launch of any of them"
  [no-awk-v-patterns.test.sh]="its exemption table is keyed by <suite>:<line text>, so each key names the suite whose awk -v line it exempts; a table key, not a launch of that suite"

  [hermetic-suites.test.sh]="its subject is whether a REAL suite's own output changes under an ambient VERI_* variable — solvable-issues.test.sh, supervise-retry.test.sh, leaf-model.test.sh and run-conductor.test.sh are each launched with and without one set and diffed; a copy or a fixture would be a fact about the copy, not about hermeticity"
  [claude-md-guards-green.test.sh]="its subject is whether the four suites that hold CLAUDE.md to its own rules — claude-md-counts.test.sh, lane-rule-recorded.test.sh, count-line-guard.test.sh, docs-targets-refuse.test.sh — are still green against the document as committed; there is no product script to run in their place"
  [run-conductor-argv-guard.test.sh]="pins that run-conductor.test.sh's case 4 still catches the argv-shape regression #221 fixed; the criterion is what THAT SUITE reports over a broken product, which a static read cannot establish since more than one fix satisfies it (its own header says so)"
  [docs-read-guard.test.sh]="copies no-docs-reads.test.sh (the guard #143 added) into a planted tree with a genuine documentation-tree read and asserts the guard still catches it; the guard's whole job is to catch that read, so only running it proves it still can"
  [sigpipe-guard.test.sh]="plants a suite that declares pipefail and ends a pipeline in grep -q, plus the same pipeline without pipefail, into a scratch tree and runs a copy of no-sigpipe-pipelines.test.sh (the guard #422 added) over it; after this issue's other steps the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [job-spec-guard.test.sh]="plants a script that kills a background process by a job spec, plus the same process killed by the pid it recorded, into a scratch tree and runs a copy of no-job-spec-kills.test.sh (the guard #424 added) over it; after this issue's other steps the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [ported-python-guard.test.sh]="plants a script whose module exists under veri/ and that feeds python3 a heredoc and a -c string into a scratch tree and runs no-python-in-ported-scripts.test.sh (the guard #634 added) over it, then over the same tree with the plant removed; the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [docs-read-guard-plant.test.sh]="the same plant-the-bug seam verification one level up: runs a scratch copy of docs-read-guard.test.sh against a stubbed no-docs-reads.test.sh to pin that IT still reports the guard's absence correctly"
  [flag-class-amendment-guard.test.sh]="plants a SKILL.md whose Refactor section grants the plan amendment to a flag class other than uncovered-spec and runs skill-refactor-leaf.test.sh over it to pin that its case 7 still fails and still names that class; the document routes the amendment correctly today, so that case passes over this tree whether it checks anything or not, and only running it over the plant says otherwise"
  [beyond-spec-narration-guard.test.sh]="plants a SKILL.md whose Refactor section says a beyond-spec flag is planned and built in this run and runs skill-refactor-leaf.test.sh over it to pin that its case 8 still fails and still names that class; the document denies the planning correctly today, so that case passes over this tree whether it checks the denial or not — and running it over the plant is what said it does not, since case 8 answers on the bullet's rationale rather than on the denial"
  [verifier-launch-guard.test.sh]="plants the #297 bypass back into a copy of SKILL.md — a verifier launch line with the supervisor cut out of it — and runs skill-leaf-launch.test.sh over it to pin that its case 5 still fails and still names that line; every launch in the document is correct today, so that guard passes over this tree whether it checks anything or not, and only running it over the plant says otherwise"
  [prose-drift-red.test.sh]="its subject is the verdict \`make test\`'s own runner reaches over a tree — \`make -C \$planted test TESTS= UNIT_TESTS= PY_TESTS=test_refactor_budget.py\` — not the product; only the real recipe over the real suite produces that verdict"
)

mapfile -t SUITE_PATHS < <(cd "$ROOT" && printf '%s\n' "$suites_dir"/*.test.sh "$suites_dir"/unit/*.test.sh 2>/dev/null)
SUITES=()
for p in "${SUITE_PATHS[@]}"; do
  [[ -f "$ROOT/$p" ]] && SUITES+=("${p##*/}")
done
mapfile -t SUITES < <(printf '%s\n' "${SUITES[@]}" | sort -u)

SUITE_LIST="$(IFS='|'; echo "${SUITES[*]}")"

FILES=()
for suite in "${SUITES[@]}"; do
  [[ -n "${EXEMPT[$suite]+x}" ]] && continue
  f="$ROOT/$suites_dir/$suite"
  [[ -f "$f" ]] || f="$ROOT/$suites_dir/unit/$suite"
  [[ -f "$f" ]] || continue
  FILES+=("$f")
done

problems=()

while IFS=$'\t' read -r suite lineno other text; do
  [[ -n "$lineno" ]] || continue
  problems+=("$suite:$lineno names $other outside a comment, in a shape this file treats as launching it, with no exemption recorded: $(flat "$text")")
done < <(awk -v suites="$SUITE_LIST" -v dir="$suites_dir" '
  function flush_pending() {
    if (gate) {
      for (i = 1; i <= pending_n; i++)
        print self "\t" pending_line[i] "\t" pending_tok[i] "\t" pending_text[i]
    }
    gate = 0; pending_n = 0
  }
  BEGIN {
    n = split(suites, arr, "|")
    for (i = 1; i <= n; i++) is_suite[arr[i]] = 1
  }
  FNR == 1 {
    flush_pending()
    self = FILENAME
    sub(/^.*\//, "", self)
  }
  /^[ \t]*#/ { next }
  {
    line = $0
    if (line ~ /(^|[^A-Za-z0-9_])cp[ \t]/ || line ~ /(^|[^A-Za-z0-9_])(UNIT_)?TESTS=/) gate = 1
    rest = line
    while (match(rest, /[a-z0-9_-]+\.test\.sh/)) {
      tok = substr(rest, RSTART, RLENGTH)
      before = (RSTART > 1) ? substr(rest, RSTART - 1, 1) : ""
      rest = substr(rest, RSTART + RLENGTH)
      if (!(tok in is_suite) || tok == self) continue
      if (before == "[" && rest ~ /^:[0-9]+\]/) continue
      if (rest ~ /^:[0-9]+ / || index(line, "$plant/" tok) || index(line, "$plant/unit/" tok)) continue
      pathform = (index(line, dir "/" tok) > 0) || (index(line, dir "/unit/" tok) > 0)
      if (pathform) {
        pending_n++
        pending_line[pending_n] = FNR
        pending_tok[pending_n] = tok
        pending_text[pending_n] = line
      } else {
        print self "\t" FNR "\t" tok "\t" line
      }
    }
  }
  END { flush_pending() }
' "${FILES[@]}")

scanned=("${problems[@]}")
report "no suite under skills/tdd/scripts/tests/ (or its unit/ tier) launches another real suite outside the exemptions recorded here"

mentions_reported() {
  local from="$1" reported name
  shift
  problems=()
  for reported in "${scanned[@]}"; do
    for name in "$@"; do
      [[ "$reported" == "$from":*"$name"* ]] && { problems+=("$reported"); break; }
    done
  done
}

mentions_reported affected-suites.test.sh claude-md-counts.test.sh
report "affected-suites.test.sh's fixture and case-name mentions of claude-md-counts.test.sh are not read as launching it"

mentions_reported affected-suites.test.sh build-develop-prompt.test.sh build-verify-prompt.test.sh
report "#487: affected-suites.test.sh's mentions of build-develop-prompt.test.sh and build-verify-prompt.test.sh are not read as launching them"

mentions_reported claude-md-counts.test.sh "names gh-fixture.test.sh"
report "#588: claude-md-counts.test.sh's case name mentioning gh-fixture.test.sh is not read as launching it"

mentions_reported next-unchecked.test.sh claude-md-counts.test.sh
report "#590: next-unchecked.test.sh's ⟦suite-repair⟧ fixture and expected-step mentions of claude-md-counts.test.sh are not read as launching it"

mentions_reported no-report-copies.test.sh docs-read-guard.test.sh profile.test.sh skill-leaf-env.test.sh harness.test.sh model-knobs-recorded.test.sh
report "#595: no-report-copies.test.sh's exemption keys, planted-suite paths and case text naming other suites are not read as launching them"

mentions_reported ledger-steps.test.sh status.test.sh
report "#671: ledger-steps.test.sh's ⟦replaces-case⟧ fixture mention of status.test.sh is not read as launching it"

mentions_reported claude-md-counts.test.sh "names github.test.sh"
from_counts=("${problems[@]}")
mentions_reported unit-tier-recorded.test.sh "names github.test.sh"
problems=("${from_counts[@]}" "${problems[@]}")
report "#720: claude-md-counts.test.sh's and unit-tier-recorded.test.sh's case-text mentions of github.test.sh are not read as launching it"

mentions_reported refactor-owed.test.sh scratch-copy-libs.test.sh
report "#756: refactor-owed.test.sh's refactor-bounds fixture paths naming scratch-copy-libs.test.sh are not read as launching it"

mentions_reported affected-suites.test.sh run-suite-venv.test.sh
report "#1011: affected-suites.test.sh's no-same-named-suite fixture mentions of run-suite-venv.test.sh are not read as launching it"

mentions_reported no-awk-v-patterns.test.sh parallel-conductors.test.sh skill-draft-pr.test.sh skill-plan-verify.test.sh skill-red-prediction.test.sh solvable-issues.test.sh
report "#1050: no-awk-v-patterns.test.sh's content-keyed exemption keys naming parallel-conductors.test.sh, skill-draft-pr.test.sh, skill-plan-verify.test.sh, skill-red-prediction.test.sh and solvable-issues.test.sh are not read as launching them"

finish
