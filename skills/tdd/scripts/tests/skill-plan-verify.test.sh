#!/usr/bin/env bash
# Unit test for where skills/tdd/SKILL.md verifies the plan, read as text.
#
# Contract under test — three cases, one per criterion:
#   1. SKILL.md launches the `plan` verdict between the instruction that commits the ledger
#      and the heading that opens the cycle loop, and the prose in that same span says a
#      REJECT rewrites the plan and re-verifies it, rather than ending the run.
#   2. The same span sends the third outcome — exit 2, no verdict rendered at all — down the
#      **system** failure bail, rather than letting it read as a PASS.
#   3. The script inventory's own entries for `build-verify-prompt.sh`, `verify.sh` and
#      `run-verdict.sh` name `plan` among the phases they accept.
#
# Run: skills/tdd/scripts/tests/skill-plan-verify.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

commit_re='git commit -m "plan: scope'
loop_re='^### 3[.] The cycle loop'
plan_launch_re='(run-verdict|verify)[.]sh.* plan '
exit2_re='[(]exit 2[)]'


source "$HERE/lib/harness.sh"

line_of() {
  awk -v re="$1" 'n == 0 && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

span_text() {
  awk -v a="$1" -v b="$2" 'NR > a && NR < b' "$skill_path" |
    tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

line_in_span() {
  awk -v a="$1" -v b="$2" -v re="$3" \
    'n == 0 && NR > a && NR < b && match($0, re) { n = NR } END { print n + 0 }' "$skill_path"
}

bullet_text() {
  awk -v a="$1" -v b="$2" -v re="$3" '
    NR <= a || NR >= b { next }
    !inb && match($0, re) { inb = 1; print; next }
    inb && ($0 ~ /^[[:space:]]*$/ || $0 ~ /^- /) { inb = 0 }
    inb { print }
  ' "$skill_path" | tr '[:upper:]' '[:lower:]' | tr '\n' ' '
}

name="SKILL.md verifies the plan between the ledger commit and the first step, and a REJECT rewrites it and re-verifies"
problems=()

commit_line="$(line_of "$commit_re")"
loop_line="$(line_of "$loop_re")"

if [[ "$commit_line" -eq 0 ]]; then
  problems+=("$skill_md has no instruction committing the ledger (no line matching /$commit_re/), so there is no point in the run after which the plan exists to be read")
elif [[ "$loop_line" -eq 0 ]]; then
  problems+=("$skill_md has no cycle-loop heading (no line matching /$loop_re/), so there is no point in the run before which the plan has to have been verified")
else
  span_desc="the ledger commit (line $commit_line) and the cycle loop (line $loop_line)"
  launch_line="$(line_of "$plan_launch_re")"
  if [[ "$launch_line" -eq 0 ]]; then
    problems+=("$skill_md never launches the plan verifier: no line matching /$plan_launch_re/, so the plan phase is a prompt nothing runs")
  elif [[ "$launch_line" -le "$commit_line" || "$launch_line" -ge "$loop_line" ]]; then
    problems+=("$skill_md launches the plan verifier at line $launch_line, outside the span between $span_desc — before the commit there is no committed plan to verify, and after the loop opens the first step has already been paid for")
  fi

  span="$(span_text "$commit_line" "$loop_line")"
  for want in reject rewrit re-verif; do
    case "$span" in
      *"$want"*) ;;
      *) problems+=("$skill_md says nothing matching '$want' between $span_desc, so the span does not say that a REJECT rewrites the plan and re-verifies it rather than ending the run") ;;
    esac
  done
fi

report "$name"

name="SKILL.md bails as a system failure when the plan verification rendered no verdict"
problems=()

if [[ "$commit_line" -eq 0 || "$loop_line" -eq 0 ]]; then
  problems+=("$skill_md is missing a landmark of the plan-verification span (ledger commit line $commit_line, cycle loop line $loop_line), so there is no span in which to read what an unobtainable verdict does")
else
  exit2_line="$(line_in_span "$commit_line" "$loop_line" "$exit2_re")"
  if [[ "$exit2_line" -eq 0 ]]; then
    problems+=("$skill_md says nothing about /$exit2_re/ between the ledger commit (line $commit_line) and the cycle loop (line $loop_line), so a plan verification that rendered no verdict has no documented outcome and reads as the PASS the conductor falls through to")
  else
    bullet="$(bullet_text "$commit_line" "$loop_line" "$exit2_re")"
    for want in bail system; do
      case "$bullet" in
        *"$want"*) ;;
        *) problems+=("$skill_md's exit-2 outcome for the plan verdict (line $exit2_line) says nothing matching '$want', so a run whose plan verifier rendered no verdict is not sent down the system-failure bail: $bullet") ;;
      esac
    done
  fi
fi

report "$name"

entry_scripts=(build-verify-prompt.sh verify.sh run-verdict.sh)

want_phases=(red green refactor pin plan)

alternation_re='[<]([a-z|]*red[a-z|]*)[>]'

name="$skill_md's script entries for the verifier scripts name the plan phase beside the four cycle phases"
problems=()

for script in "${entry_scripts[@]}"; do
  entry_re='^- .[$]S/'"${script//./[.]}"' '
  entry_line="$(line_of "$entry_re")"
  if [[ "$entry_line" -eq 0 ]]; then
    problems+=("$skill_md has no script-inventory entry for $script (no line matching /$entry_re/), so there is nowhere a conductor reads which phases it accepts")
    continue
  fi
  line="$(sed -n "${entry_line}p" "$skill_path")"
  if [[ ! "$line" =~ $alternation_re ]]; then
    problems+=("$skill_md:$entry_line, the entry for $script, spells no phase alternation among its arguments: $line")
    continue
  fi
  alternation="${BASH_REMATCH[1]}"
  for phase in "${want_phases[@]}"; do
    case "|$alternation|" in
      *"|$phase|"*) ;;
      *) problems+=("$skill_md:$entry_line, the entry for $script, spells its phases <$alternation>, which does not name '$phase' — the inventory is where a conductor reads what the script takes, so a phase missing from it is a phase the procedure never tells anyone to ask for") ;;
    esac
  done
done

report "$name"

finish
