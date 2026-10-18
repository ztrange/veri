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
  [no-docs-reads.test.sh]="its exemption table is keyed by <suite>:<line text>, so its one key names no-product-caller.test.sh, the suite whose scratch-tree hooks path it exempts; a table key, not a launch of that suite"
  [no-awk-v-patterns.test.sh]="its exemption table is keyed by <suite>:<line text>, so each key names the suite whose awk -v line it exempts; a table key, not a launch of that suite"
  [docs-read-guard.test.sh]="copies no-docs-reads.test.sh (the guard #143 added) into a planted tree with a genuine documentation-tree read and asserts the guard still catches it; the guard's whole job is to catch that read, so only running it proves it still can"
  [sigpipe-guard.test.sh]="plants a suite that declares pipefail and ends a pipeline in grep -q, plus the same pipeline without pipefail, into a scratch tree and runs a copy of no-sigpipe-pipelines.test.sh (the guard #422 added) over it; after this issue's other steps the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [job-spec-guard.test.sh]="plants a script that kills a background process by a job spec, plus the same process killed by the pid it recorded, into a scratch tree and runs a copy of no-job-spec-kills.test.sh (the guard #424 added) over it; after this issue's other steps the real tree holds no live site, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [docs-read-guard-plant.test.sh]="the same plant-the-bug seam verification one level up: runs a scratch copy of docs-read-guard.test.sh against a stubbed no-docs-reads.test.sh to pin that IT still reports the guard's absence correctly"
  [unit-subprocess-guard.test.sh]="plants a unit-tier suite that runs status.sh, and an exemption entry with and without a reason, into a scratch tree and runs a copy of no-unit-subprocess.test.sh (the admission guard #1634 added) over it; the real unit/ holds no offender and no exemption today, so the guard answers the same way over it whether it still checks anything or not, and only running it over the plant says otherwise"
  [scanner-status-guards.test.sh]="copies no-awk-v-patterns.test.sh, no-docs-reads.test.sh and no-job-spec-kills.test.sh into clean scratch trees and runs each with only its grep scanner over that tree forced to exit 2; the real tree's scanners never fail, so each guard answers the same way over it whether it checks its scanner's status or not, and only the forced failure says otherwise"
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

scan_launches() {
  awk -v suites="$SUITE_LIST" -v dir="$suites_dir" '
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
' "$@"
}

problems=()

while IFS=$'\t' read -r suite lineno other text; do
  [[ -n "$lineno" ]] || continue
  problems+=("$suite:$lineno names $other outside a comment, in a shape this file treats as launching it, with no exemption recorded: $(flat "$text")")
done < <(scan_launches "${FILES[@]}")

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

mentions_reported no-report-copies.test.sh docs-read-guard.test.sh harness.test.sh
report "#595: no-report-copies.test.sh's exemption keys, planted-suite paths and case text naming other suites are not read as launching them"

mentions_reported affected-suites.test.sh run-suite-venv.test.sh
report "#1011: affected-suites.test.sh's no-same-named-suite fixture mentions of run-suite-venv.test.sh are not read as launching it"

mentions_reported affected-suites.test.sh "#1138"
report "#1138: affected-suites.test.sh's #1138 case names mentioning another suite are not read as launching it"

mentions_reported affected-suites.test.sh .test.sh
report "#538: affected-suites.test.sh's cp of SKILL.md and of the suites naming it into a scratch repo does not make its fixture mentions of other suites read as launching them"

plant="$(scratch_dir)"
cat "$ROOT/$suites_dir/affected-suites.test.sh" > "$plant/affected-suites.test.sh"
printf '%s\n' 'bash "$HERE/run-suite-offline.test.sh"' >> "$plant/affected-suites.test.sh"
planted_line="$(wc -l < "$plant/affected-suites.test.sh" | tr -d ' ')"
problems=()
scan_launches "$plant/affected-suites.test.sh" | grep -F "$(printf 'affected-suites.test.sh\t%s\trun-suite-offline.test.sh\t' "$planted_line")" > /dev/null \
  || problems+=("a planted 'bash \"\$HERE/run-suite-offline.test.sh\"' at affected-suites.test.sh:$planted_line was not reported")
report "#538: a real launch of another suite planted in affected-suites.test.sh is still read as launching it"

finish
