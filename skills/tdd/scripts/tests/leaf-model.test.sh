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
#   VERI_MODEL=<x> VERI_MODEL_VERIFIER=<y> leaf-model.sh <leaf-name>
#                              → the role variable wins for that role's leaves and for no
#                                others: <y> for `verify-*`, <x> still for `develop-*` and
#                                `revise-*`, and the mirror image for VERI_MODEL_DEVELOPER.
#
# The three names are cleared for every child below, for the reason hermetic-suites.test.sh
# exists (issue #87): a suite's answer is a fact about the script, not about whatever the
# shell that invoked `make test` had exported.
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

# model_env <run-wide> <developer> <verifier> <leaf-name> — fill the caller's `envargs` and
# `label` for one call: the argv that opens exactly the named variables for the child, and the
# line every problem message is prefixed with. Each value is given as its value or as the word
# `unset`. Both probes below need the identical list, and they need it to STAY identical — the
# whole question this suite asks is which variable a leaf reads, so a probe that cleared one
# name the other did not would answer about the caller's shell instead of about the script.
# Written once here, it cannot drift.
#
# `env -u` on all three names clears them for the child only, so a probe never depends on — nor
# disturbs — what the surrounding run exported; `env` applies its assignments after its `-u`s,
# so the pair says "these values, nothing ambient" in one list. It writes into the caller's
# locals rather than printing, because an array of assignments cannot survive a command
# substitution intact: a value with a space in it is exactly what case 3 probes.
model_env() {
  label="VERI_MODEL=$1 VERI_MODEL_DEVELOPER=$2 VERI_MODEL_VERIFIER=$3 $4"
  envargs=(-u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER)
  [[ "$1" == unset ]] || envargs+=(VERI_MODEL="$1")
  [[ "$2" == unset ]] || envargs+=(VERI_MODEL_DEVELOPER="$2")
  [[ "$3" == unset ]] || envargs+=(VERI_MODEL_VERIFIER="$3")
}

# model_probe <run-wide> <developer> <verifier> <leaf-name> <want> — one call the script
# must answer, under all three variables. Each is given as its value or as the word `unset`,
# and <want> is the exact stdout expected — the empty string for a run that chose no model.
# One probe for every case below: which of the three a leaf reads is the whole subject here,
# so a probe that could only open one of them could not pose the question, and two probes
# differing only in how many names they set would be free to drift in how they call the
# script. Separate files per stream, since the case is partly about which stream carries
# what: a model resolved is not a diagnosable event, so stderr must stay empty in every
# branch.
model_probe() {
  local wide="$1" dev="$2" ver="$3" name="$4" want="$5" out err code label
  local -a envargs
  out="$(mktemp)" err="$(mktemp)"
  model_env "$wide" "$dev" "$ver" "$name"
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

# model_refuses <run-wide> <developer> <verifier> <leaf-name> — the other half of the
# contract, and the only shape a refusal is allowed to take: exit 2 ("no answer could be
# obtained" — the plumbing speaking, not a clean negative), NOTHING on stdout, and a
# diagnostic on stderr so a human is told which value was wrong. Nothing on stdout is the
# load-bearing one: supervise.sh reads this script in a command substitution and turns a
# non-empty answer into `--model <value>`, so a refused value half-printed there would
# reach the `claude` command line anyway, which is the failure the refusal exists to stop.
# Arguments are model_probe's, and the environment is model_env's, for the same reasons.
model_refuses() {
  local wide="$1" dev="$2" ver="$3" name="$4" out err code label
  local -a envargs
  out="$(mktemp)" err="$(mktemp)"
  model_env "$wide" "$dev" "$ver" "$name"
  env "${envargs[@]}" "$LEAF_MODEL" "$name" >"$out" 2>"$err" && code=0 || code=$?
  [[ "$code" == 2 ]] ||
    problems+=("$label: want exit 2, got $code")
  [[ ! -s "$out" ]] ||
    problems+=("$label: want nothing on stdout, got: $(printf '%q' "$(cat "$out")")")
  [[ -s "$err" ]] ||
    problems+=("$label: want a diagnostic on stderr, got nothing")
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
model_probe sonnet unset unset develop-red  sonnet
model_probe sonnet unset unset verify-green sonnet
model_probe unset unset unset develop-red  ""
model_probe unset unset unset verify-green ""
report "$name"

# 2. One role variable is set alongside VERI_MODEL, and the leaves of both roles are asked.
#    Precedence alone would be half the criterion — a script that simply preferred whichever
#    role variable was set would pass a probe that only ever asked the overridden role — so
#    each half sets one role variable and asks all three launch shapes: the overridden role's
#    leaves must answer the role value, and the other role's must still answer VERI_MODEL.
#
#    `revise-green-2` is asked because it is the developer name that does not begin with
#    `develop`: it is a fresh developer answering the verifier, per leaf-role.sh's header, so
#    VERI_MODEL_DEVELOPER must reach it too.
name="a role variable beats VERI_MODEL for that role's leaves only"
problems=()
model_probe sonnet unset opus develop-red    sonnet
model_probe sonnet unset opus revise-green-2 sonnet
model_probe sonnet unset opus verify-green   opus
model_probe sonnet opus unset develop-red    opus
model_probe sonnet opus unset revise-green-2 opus
model_probe sonnet opus unset verify-green   sonnet
report "$name"

# 3. The two refusals this script can make without asking a network what a model id is, and
#    the alias that must survive them. A value with whitespace in it cannot be one model
#    name: `claude --model "sonnet 5"` is a single argument no alias matches, and left to
#    run it costs a whole leaf to find out, so it is refused here — in preflight, before any
#    branch or leaf — rather than at launch. Both variables are asked, because the refusal is
#    of the value that WON, not of a particular name: whitespace reaching `--model` through
#    the role variable is the same wrong command line as through VERI_MODEL.
#
#    A leaf name leaf-role.sh refuses is refused here too, and with no model variable set at
#    all as well as with one: this script's first act is to ask leaf-role.sh what role the
#    name is, so a name it cannot read leaves the role variable unreadable, and answering
#    VERI_MODEL anyway would be answering for a leaf nobody could place.
#
#    `opus[1m]` is probed alongside them because it is the model the development machine
#    actually runs on (issue #171): a guard written as "refuse anything not plain alphanumeric"
#    would take the brackets with the spaces and break every leaf, so the accepted case is
#    named here rather than left to be inferred from the two refusals.
name="a value containing whitespace and a leaf name leaf-role.sh refuses each exit 2 with a diagnostic, while opus[1m] is accepted"
problems=()
model_refuses 'sonnet 5' unset unset develop-red
model_refuses unset unset $'opus\t1m' verify-green
model_refuses sonnet unset unset frobnicate-red
model_refuses unset unset unset frobnicate-red
model_probe 'opus[1m]' unset unset develop-red  'opus[1m]'
model_probe unset unset 'opus[1m]' verify-green 'opus[1m]'
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
