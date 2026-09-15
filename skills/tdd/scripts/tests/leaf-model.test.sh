#!/usr/bin/env bash
# Unit tests for scripts/leaf-model.sh — says which model one leaf runs on, so a run can
# price the two leaf roles separately (issue #171). Why that is worth a script, and what
# no leaf can choose today, is in leaf-model.sh's own header.
# Zero-dependency plain-shell asserts, same idiom as leaf-timeout.test.sh.
#
# Contract under test (this step only):
#   VERI_MODEL=<x> leaf-model.sh <leaf-name>  → prints <x> and exits 0, for a leaf of
#                                 EITHER role: the run-wide variable is the one that
#                                 applies to every leaf, so a developer name and a
#                                 verifier name must answer the same.
#   leaf-model.sh <leaf-name>  with no model variable set
#                              → prints NOTHING and exits 0. Nothing, not a default: the
#                                caller turns a non-empty answer into `--model <value>`,
#                                so any word printed here would put a flag on a command
#                                line the issue requires to stay byte-identical to today's.
#
# The role variables `VERI_MODEL_DEVELOPER` / `VERI_MODEL_VERIFIER` are a later step's
# criterion and are not asserted here. They are still cleared for every child below, for
# the reason hermetic-suites.test.sh exists (issue #87): a suite's answer is a fact about
# the script, not about whatever the shell that invoked `make test` had exported.
#
# Run: scripts/tests/leaf-model.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_MODEL="$HERE/../leaf-model.sh"
pass=0 fail=0

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which probe broke rather than just that the case did.
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

# model_probe <veri-model> <leaf-name> <want> — one call the script must answer. <veri-model>
# is the value VERI_MODEL arrives with, or the word `unset` for a run that set none, and
# <want> is the exact stdout expected — the empty string for the unset run. Separate files
# per stream, since the case is partly about which stream carries what: a model resolved is
# not a diagnosable event, so stderr must stay empty in both branches.
#
# `env -u` on all three names clears them for the child only, so the probe never depends on
# — nor disturbs — what the surrounding run exported.
model_probe() {
  local model="$1" name="$2" want="$3" out err code label
  local -a envargs
  out="$(mktemp)" err="$(mktemp)"
  label="VERI_MODEL=$model $name"
  # The three names are cleared for every probe, and the one under test is then set back
  # for a probe that has a value to give: `env` applies its assignments after its `-u`s, so
  # the pair says "this value, nothing ambient" in one list. One invocation either way, so
  # the two branches cannot drift in how they call the script — only in what they export.
  envargs=(-u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER)
  [[ "$model" == unset ]] || envargs+=(VERI_MODEL="$model")
  env "${envargs[@]}" "$LEAF_MODEL" "$name" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 0 ]] ||
    problems+=("$label: want exit 0, got $code")
  # `$(cat …)` eats the trailing newline, so comparing against <want> is both "the right
  # value" and "nothing else printed alongside it" — and against "" it is the whole of the
  # unset contract, whether the script printed a word or just a bare newline.
  [[ "$(cat "$out")" == "$want" ]] ||
    problems+=("$label: want $(printf '%q' "$want") on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ ! -s "$err" ]] ||
    problems+=("$label: want nothing on stderr, got: $(printf '%q' "$(cat "$err")")")
  rm -f "$out" "$err"
}

# 1. The whole of this step's criterion, as one case: VERI_MODEL is the run-wide knob, so
#    it answers for a leaf of either role, and a run that set no model at all gets no model
#    back.
#
#    `develop-red` and `verify-green` are the two roles' real launch names (SKILL.md's
#    develop-* and verify-* leaves), which is what makes "either role" an observation rather
#    than a restatement: a script that only knew how to answer for one of them would print
#    for one probe and refuse or fall silent on the other.
#
#    The unset probes are asked of both names for the same reason, and they are the case
#    the issue's first acceptance criterion turns on: with nothing set, the `claude` argv
#    carries no `--model` at all.
name="VERI_MODEL is printed for a leaf of either role; with no model variable set, nothing is printed and the exit is still 0"
problems=()
model_probe sonnet develop-red sonnet
model_probe sonnet verify-green sonnet
model_probe unset develop-red ""
model_probe unset verify-green ""
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
