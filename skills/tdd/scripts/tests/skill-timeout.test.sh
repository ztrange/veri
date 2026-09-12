#!/usr/bin/env bash
# Unit tests for what skills/tdd/SKILL.md tells a conductor to do with the run's hard
# timeout. Like skill-identity.test.sh and workflow-timeouts.test.sh this suite belongs to
# no single script: its subject is the procedure, read as text, the way the session that
# follows it reads it.
# Zero-dependency plain-shell asserts, same idiom as skill-identity.test.sh.
#
# Why this exists (issue #121): `leaf-timeout.sh` derives the timeout, but a script nobody
# calls changes nothing. The derivation lives in the conductor's own procedure — there is
# no leaf and no script that could carry it, because the measurement it needs is taken by
# preflight and the value it produces has to be in the environment before the first leaf
# launches. On #71 that value was the fixed 900 s against a 140-250 s suite, and two leaves
# were killed as stuck while working; what fixes it is this document saying so.
#
# Contract under test (this step only):
#   SKILL.md's preflight section times the green-baseline run it already does, hands that
#   measurement to `leaf-timeout.sh`, and exports the result as `VERI_TIMEOUT` so every
#   leaf of the run is launched under it.
#   SKILL.md's plan-comment step says that comment states the timeout and the baseline it
#   was derived from, so a human reading the issue thread can see which number the run is
#   using and why — the fact that had to be reconstructed from bail timestamps on #71.
#
# Run: scripts/tests/skill-timeout.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
# The suite sits at skills/<skill>/scripts/tests, so four levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"

pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract is missing rather than just that it is.
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

# section <heading-regex> — the lines of the first `### ` section whose heading matches,
# up to the next `### `. The document says several things about timeouts in several
# places — the supervisor's default is described under `## The scripts`, and `## Bailing`
# names the killed-stuck it causes — so a file-wide read would answer "yes, it is in
# there" for a procedure that never derives anything. Each claim below is about what one
# STEP tells the session to do, so the step's section is cut out first.
section() {
  awk -v want="$1" '
    $0 ~ want { inside = 1; print; next }
    inside && /^### / { exit }
    inside' "$ROOT/$skill_md"
}

# paragraphs — markdown on stdin, one line per paragraph or numbered step, lowercased. A
# record runs from a `N. ` in column one, or from the first line after a blank, up to the
# next such line or the next blank; joining it onto one line is what lets a claim ask
# whether ONE step carries both halves of its pair, rather than two sentences several
# steps apart that happen to share a word. Both a numbered step and a plain paragraph
# count, because which of the two a conductor writes an instruction as is a choice about
# the document's shape and not about what it tells the session to do. Case is folded away
# last: the sentences are the writer's, and `VERI_TIMEOUT` must answer for `veri_timeout`.
paragraphs() {
  awk '/^[0-9]+\. / { if (rec != "") print rec; rec = $0; next }
       /^[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
       rec == "" { rec = $0; next }
       { rec = rec " " $0 }
       END { if (rec != "") print rec }' | tr '[:upper:]' '[:lower:]'
}

# claim <what one step must say> <regex>… — assert that a single line of the global
# `records` matches every <regex>, recording a problem naming <what> if none does. Each
# claim below is a pair or a triple — the measurement and what is done with it, the
# variable and who it reaches — and a pair split across two steps is not an instruction:
# it is two sentences that happen to share a word. `continue 2` leaves the regex loop and
# takes the next record, so a record matching some but not all of the group is simply not
# the one. Every regex accepts any wording that carries the fact, so a claim pins what the
# document says and not how it is phrased.
claim() {
  local what="$1" line re
  shift
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<< "$records"
  problems+=("$records_from: no step $what")
}

# A word about elapsed wall time, bounded on both sides so that `timeout` — and
# `leaf-timeout.sh`, which every claim here sits next to — cannot answer for `time`. The
# trailing class excludes the hyphen for that reason; the leading one keeps `sometimes`
# out. `sec` catches both `seconds` and the `secs` a shell variable holding the
# measurement is usually called.
elapsed_re='(^|[^a-z])(time|timed|times|timing|elapsed|wall|duration|sec)([^a-z-]|$)'

# 1. The whole of this step's criterion, as one case: the procedure has to measure, derive,
#    export and announce, and three of those four are individually useless. A timing step
#    whose number reaches nothing changes no leaf; a derivation nobody exports changes no
#    leaf either; and a run whose leaves get a number no comment states is #71 again, where
#    the timeout in force had to be reconstructed from the timestamps of two bails.
#
#    Each claim names the pair it is about, so a failure says which one is missing rather
#    than that the document as a whole is wrong.
name="$skill_md's preflight times the baseline run, derives the timeout with leaf-timeout.sh and exports it as VERI_TIMEOUT for every leaf, and the plan comment states it with the baseline it came from"
problems=()

# The preflight section, matched by the word rather than by its number, so renumbering the
# procedure does not fail this case. `[0-9]+\.` is what tells it from `### Loop 0.
# Preflight — none of its own`, the loop's section, which delegates every check to here.
records="$(section '^### [0-9]+\..*[Pp]reflight' | paragraphs)"
records_from="$skill_md preflight"
if [[ -z "$records" ]]; then
  # Fail closed: no records means the section was renamed or emptied and not one claim
  # below was tested, which must not read as three passes.
  problems+=("$skill_md has no numbered '### … Preflight' section — what preflight does with the timeout could not be read")
else
  claim 'times the green-baseline run it already does' \
    'baseline' "$elapsed_re"
  claim 'hands that measurement to leaf-timeout.sh' \
    'leaf-timeout\.sh' "$elapsed_re|baseline"
  claim 'exports the result as VERI_TIMEOUT so every leaf of the run is launched under it' \
    'veri_timeout' 'export|every leaf|each leaf|all leaves|every launch|rest of the run'
fi

# The plan section, matched the same way: the step that mirrors the plan to the issue
# thread lives in it, and the criterion is that THAT comment carry the number.
records="$(section '^### [0-9]+\..*[Pp]lan' | paragraphs)"
records_from="$skill_md plan"
if [[ -z "$records" ]]; then
  problems+=("$skill_md has no numbered '### … plan' section — what the plan comment states could not be read")
else
  claim 'has the plan comment state the timeout and the baseline it was derived from' \
    'timeout' 'baseline' 'comment'
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
