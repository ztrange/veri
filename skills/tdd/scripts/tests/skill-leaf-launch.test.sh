#!/usr/bin/env bash
# Unit test for how skills/tdd/SKILL.md launches a leaf, read as text.
#
# Contract under test:
#   5. Every launch line that reaches the verifier — by naming `verify.sh` or the verdict
#      launcher `run-verdict.sh` that execs it — names `supervise.sh` too.
#   7. Every verifier launch invokes the verdict launcher `run-verdict.sh` and inlines no
#      `bash -c` command string.
#   8. The document states in ONE place how the step's title reaches a command line, and
#      every fenced command carrying `<STEP>` follows that rule.
#   9. Every documented command line that passes a FRAGMENT of the step's title — the
#      `tick-ledger.sh`, `clear-refactor-pending.sh` and `tick-issue-criterion.sh` calls —
#      follows that same rule, read over the whole document, prose included.
#  10. That one rule says the title reaches a command line as data rather than hand-typed in
#      double quotes, and names every script the launch lines read it through.
#  11. Every line that builds the revise prompt with `build-develop-prompt.sh revise` hands
#      it the run's fast command, `'<fast-cmd>'`.
#
# Run: scripts/tests/skill-leaf-launch.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"

skill_md="skills/tdd/SKILL.md"
skill_path="$ROOT/$skill_md"

launcher="supervise.sh"
verifier="verify.sh"

verdict_launcher="run-verdict.sh"
verdict_leaf="verdict-"

step_ph="<STEP>"
double_quoted_step="\"$step_ph\""
single_quoted_step="'$step_ph'"

fragment_ph="<[^<>]*substring[^<>]*>"
double_quoted_fragment="\"$fragment_ph\""
single_quoted_fragment="'$fragment_ph'"

declare -A EXEMPT=(
)


source "$HERE/lib/harness.sh"
source "$HERE/lib/fenced-lines.sh"

fault() {
  faults="${faults:+$faults, and }$1"
}

faulted() {
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$1 $faults: $2")
}

read_quoted_lines() {
  local lines="$1" noun="$2" ph="$3" single="$4" double="$5"
  local lineno text
  while IFS=$'\t' read -r lineno text; do
    [[ -n "${EXEMPT[$skill_md:$lineno]:-}" ]] && continue
    faults=""
    if [[ "$text" =~ $single ]]; then
      fault "single-quotes $noun"
    elif [[ "$(sed -E "s|$double||g" <<< "$text")" =~ $ph ]]; then
      fault "carries $noun outside double quotes"
    fi
    faulted "$lineno" "$text"
  done <<< "$lines"
}

unreadable() {
  problems+=("$skill_md has no $1 — $2 could not be read")
}

lowered() {
  tr '[:upper:]' '[:lower:]'
}

name_re() {
  local out="" n
  for n in "$@"; do out+="|${n//./\\.}"; done
  printf '%s' "${out#|}"
}

launch_lines() {
  fenced_lines "$skill_path" "$(name_re "$launcher" "$verifier" "$verdict_launcher")"
}

name="$skill_md launches every verifier through $launcher, the way it launches a developer leaf"
problems=()

verifier_launches="$(launch_lines | grep -E -- "$(name_re "$verifier" "$verdict_launcher")" || true)"
if [[ -z "$verifier_launches" ]]; then
  unreadable "launch line naming $verifier or $verdict_launcher inside a fenced block" "how a verifier is launched"
else
  while IFS=$'\t' read -r lineno text; do
    [[ "$text" == *"$launcher"* ]] ||
      problems+=("$skill_md:$lineno reaches $verifier without $launcher: $text")
  done <<< "$verifier_launches"
fi

report "$name"

name="$skill_md invokes $verdict_launcher on every verifier launch, with no inlined bash -c command string"
problems=()

verdict_launches="$(launch_lines | grep -F "$launcher $verdict_leaf" || true)"
if [[ -z "$verdict_launches" ]]; then
  unreadable "launch line naming $launcher and a ${verdict_leaf}<phase> leaf inside a fenced block" "how a verdict is launched"
else
  while IFS=$'\t' read -r lineno text; do
    faults=""
    [[ "$text" == *"$verdict_launcher"* ]] || fault "does not invoke $verdict_launcher"
    [[ "$text" == *"bash -c"* ]] && fault "still inlines the verifier call in a bash -c command string"
    faulted "$lineno" "$text"
  done <<< "$verdict_launches"
fi

report "$name"

prose_paragraphs() {
  awk '
    /^[[:space:]]*```/ { flush(); fence = !fence; next }
    fence { next }
    /^[[:space:]]*$/ { flush(); next }
    { if (para == "") start = NR; para = para (para == "" ? "" : " ") $0 }
    END { flush() }
    function flush() { if (para != "") printf "%d\t%s\n", start, para; para = "" }
  ' "$skill_path"
}

step_lines() {
  fenced_lines "$skill_path" "$step_ph"
}

name="$skill_md states the step-title rule in one place, and every fenced command carrying the title follows it"
problems=()

step_title_rules() {
  prose_paragraphs | grep -i -E 'quot' | grep -F -e 'step title' -e "$step_ph" || true
}

rules="$(step_title_rules)"
rule_count="$(grep -c . <<< "$rules")"
if [[ "$rule_count" -eq 0 ]]; then
  problems+=("$skill_md states no rule for how a step title reaches a command line — no paragraph outside a fenced block says how the title is quoted")
elif [[ "$rule_count" -gt 1 ]]; then
  problems+=("$skill_md states the step-title rule in $rule_count places, at lines $(cut -f1 <<< "$rules" | paste -sd, -) — one rule, or the next edit moves one of them")
else
  ruleno="$(cut -f1 <<< "$rules")"
  ruletext="$(cut -f2- <<< "$rules")"
  ruletext_lc="$(lowered <<< "$ruletext")"
  faults=""
  [[ "$ruletext" == *"$double_quoted_step"* || "$ruletext_lc" == *"double quote"* ]] ||
    fault "does not say the title is carried in double quotes"
  [[ "$ruletext_lc" == *apostrophe* ]] ||
    fault "does not say why: a title carrying an apostrophe closes a single-quoted one early"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$ruleno states the step-title rule but $faults")
fi

steps="$(step_lines)"
if [[ -z "$steps" ]]; then
  unreadable "line carrying $step_ph inside a fenced block" "how the step's title reaches a command line"
else
  read_quoted_lines "$steps" "the step title" \
    "$step_ph" "$single_quoted_step" "$double_quoted_step"
fi

report "$name"

document_lines() {
  PAT="$1" awk '$0 ~ ENVIRON["PAT"] { printf "%d\t%s\n", NR, $0 }' "$skill_path"
}

fragment_lines() {
  document_lines "$fragment_ph" | grep -E "\\\$S/|$single_quoted_fragment|$double_quoted_fragment" || true
}

name="$skill_md double-quotes every documented command line that passes a fragment of the step's title"
problems=()

fragments="$(fragment_lines)"
if [[ -z "$fragments" ]]; then
  unreadable "command line passing a fragment of the step's title" "how a fragment of the step's title reaches a command line"
else
  read_quoted_lines "$fragments" "a fragment of the step title" \
    "$fragment_ph" "$single_quoted_fragment" "$double_quoted_fragment"
fi

report "$name"

step_readers() {
  fenced_lines "$skill_path" 'VERI_STEP="\$\(' |
    grep -o -E 'VERI_STEP="\$\([^)]*\)' |
    grep -o -E '\$S/[A-Za-z0-9_.-]+' | sed 's|^\$S/||' | sort -u || true
}

name="$skill_md's step-title rule says the title reaches a command line as data, not hand-typed in double quotes, and names what the launch lines read it through (#437)"
problems=()

rules="$(step_title_rules)"
readers="$(step_readers)"
if [[ "$(grep -c . <<< "$rules")" -ne 1 ]]; then
  unreadable "single paragraph stating the step-title rule" "how the step's title reaches a command line"
elif [[ -z "$readers" ]]; then
  unreadable "launch line reading VERI_STEP through a script inside a fenced block" "what the launch lines read the step's title through"
else
  ruleno="$(cut -f1 <<< "$rules")"
  ruletext="$(cut -f2- <<< "$rules")"
  faults=""
  [[ "$(lowered <<< "$ruletext")" =~ (^|[^a-z])data([^a-z]|$) ]] ||
    fault "does not say the title reaches a command line as data"
  while IFS= read -r reader; do
    [[ "$ruletext" == *"$reader"* ]] ||
      fault "does not name $reader, which a launch line reads the title through"
  done <<< "$readers"
  [[ -z "$faults" ]] ||
    problems+=("$skill_md:$ruleno states the step-title rule but $faults")
fi

report "$name"

title_guard() {
  local skill_path="$1"
  local problems=()
  read_quoted_lines "$(step_lines)" "the step title" \
    "$step_ph" "$single_quoted_step" "$double_quoted_step"
  [[ "${#problems[@]}" -eq 0 ]] || printf '%s\n' "${problems[@]}"
}

name="the #431 guard still refuses a single-quoted step title and its exemption table still holds over the rewritten $skill_md (#437)"
problems=()

title_linenos="$(step_lines | cut -f1)"
planted_line="$(sed -n '1p' <<< "$title_linenos")"
if [[ -z "$planted_line" ]]; then
  unreadable "fenced line carrying $step_ph" "where the #431 guard would meet a single-quoted title"
else
  planted_doc="$(mktemp)"
  sed "${planted_line}s|$double_quoted_step|$single_quoted_step|" "$skill_path" > "$planted_doc"
  refused="$(unset "EXEMPT[$skill_md:$planted_line]"; title_guard "$planted_doc")"
  [[ "$refused" == *"$skill_md:$planted_line single-quotes the step title"* ]] ||
    problems+=("the guard did not refuse $single_quoted_step planted at $skill_md:$planted_line — it reported: ${refused:-nothing}")
  answered="$(EXEMPT["$skill_md:$planted_line"]="planted by case 11"; title_guard "$planted_doc")"
  [[ "$answered" != *"$skill_md:$planted_line "* ]] ||
    problems+=("an EXEMPT entry for $skill_md:$planted_line did not answer the report: $answered")
  rm -f "$planted_doc"
fi
for key in "${!EXEMPT[@]}"; do
  grep -qxF -- "${key##*:}" <<< "$title_linenos" ||
    problems+=("EXEMPT[$key] names a line that no fenced command carrying $step_ph is on in the rewritten document")
done

report "$name"

name="$skill_md's revise launch hands build-develop-prompt.sh revise the run's fast command '<fast-cmd>' (#636)"
problems=()

revise_builds="$(fenced_lines "$skill_path" 'build-develop-prompt\.sh revise <phase>')"
if [[ -z "$revise_builds" ]]; then
  unreadable "line building the revise prompt with build-develop-prompt.sh revise inside a fenced block" "what the revise launch hands the prompt builder"
else
  while IFS=$'\t' read -r lineno text; do
    [[ "$text" == *"'<fast-cmd>'"* ]] ||
      problems+=("$skill_md:$lineno builds the revise prompt without the run's fast command '<fast-cmd>': $text")
  done <<< "$revise_builds"
fi

report "$name"

finish
