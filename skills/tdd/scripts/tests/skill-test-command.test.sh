#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells the conductor about the run's test command,
# read as text.
#
# Contract under test:
#   Preflight reads the issue body and hands it to detect-test-command.sh as `--issue`,
#   in that order, so the issue's own command is in hand before the baseline run.
#   The section that defines <test-cmd> for every leaf detects it the same way.
#   The plan comment states the test command the run will use.
#
# Run: scripts/tests/skill-test-command.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
md="$ROOT/$skill_md"


source "$HERE/lib/harness.sh"
source "$HERE/lib/section-end.sh"

sec_start=0 sec_end=0
section() {
  sec_start="$(h="$1" awk 'index($0, ENVIRON["h"]) == 1 { print NR; exit }' "$md")"
  [[ -n "$sec_start" ]] || { sec_end=0; return 1; }
  sec_end="$(section_end "$md" "$sec_start")"
  return 0
}

need_section() {
  section "$1" && return 0
  problems+=("$skill_md has no '$1' section — $2")
  return 1
}

at() {
  re="$1" awk -v s="$sec_start" -v e="$sec_end" \
    'NR >= s && NR <= e && $0 ~ ENVIRON["re"] { print NR; exit }' "$md"
}

line_at() { sed -n "${1}p" "$md"; }

items() {
  awk -v s="$sec_start" -v e="$sec_end" '
    NR < s || NR > e { next }
    /^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
    /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
    rec != "" { rec = rec " " $0 }
    END { if (rec != "") print rec }' "$md" | tr '[:upper:]' '[:lower:]'
}

name="$skill_md detects the run's test command from the issue body in preflight, gives it to every leaf, and names it in the plan comment"
problems=()

if need_section '### 0. Preflight' 'where the baseline reads its test command could not be read'; then
  detect_at="$(at 'detect-test-command\.sh')"
  body_at="$(at 'gh api repos/[{]owner[}]/[{]repo[}]/issues/<n> -q [.]body')"
  if [[ -z "$detect_at" ]]; then
    problems+=("$skill_md preflight never names detect-test-command.sh, so the baseline runs a command from nowhere")
  else
    detect_line="$(line_at "$detect_at")"
    [[ "$detect_line" == *--issue* ]] ||
      problems+=("$skill_md:$detect_at detects the test command without --issue, so the issue's own line cannot answer: $detect_line")
  fi
  if [[ -z "$body_at" ]]; then
    problems+=("$skill_md preflight never reads the issue body (no gh api read of issues/<n>), so there is no body file to pass as --issue")
  elif [[ -n "$detect_at" ]] && [[ "$body_at" -gt "$detect_at" ]]; then
    problems+=("$skill_md reads the issue body at line $body_at, after detecting the test command at line $detect_at — the baseline runs before the issue's line is known")
  fi
fi

if need_section '## Detecting the test command' 'how <test-cmd> is obtained could not be read'; then
  [[ -n "$(at '--issue')" ]] ||
    problems+=("$skill_md's 'Detecting the test command' section never names --issue, so <test-cmd> — what every leaf runs — is detected without the issue's line")
fi

if need_section '### 2. Scope & plan' 'what the plan comment states could not be read'; then
  plan_item="$(items | grep -E 'plan.*comment')"
  if [[ -z "$plan_item" ]]; then
    problems+=("$skill_md's 'Scope & plan' section has no numbered item posting the plan comment — what that comment states could not be read")
  elif ! grep -qE 'test command' <<< "$plan_item"; then
    problems+=("$skill_md's plan-comment item never names the test command, so a wrong one is invisible until the first leaf: $(printf '%.120s' "$plan_item")")
  fi
fi
report "$name"

name="$skill_md's preflight baseline runs and times detect-test-command.sh --tier fast's command"
problems=()
if need_section '### 0. Preflight' 'what the baseline runs could not be read'; then
  baseline_item="$(items | grep -E 'baseline' | grep -E 'time it')"
  if [[ -z "$baseline_item" ]]; then
    problems+=("$skill_md preflight has no numbered item that runs and times the baseline")
  elif ! grep -qE 'detect-test-command\.sh --tier fast' <<< "$baseline_item"; then
    problems+=("$skill_md's baseline item never runs detect-test-command.sh --tier fast, so the baseline times a command other than the fast tier: $(printf '%.120s' "$baseline_item")")
  fi
fi
report "$name"

name="#1037: at given 'run\\.sh' prints the line where run.sh stands, not the one where runXsh does"
fixture="$(scratch_dir)"
printf -- 'runXsh wrong\nrun.sh right\n' > "$fixture/SKILL.md"
expect_eq "$name" '2' "$(md="$fixture/SKILL.md" sec_start=1 sec_end=2 at 'run\.sh')"

finish
