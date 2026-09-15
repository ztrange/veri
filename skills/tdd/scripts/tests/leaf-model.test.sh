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

#   And where the script is called from, which is the other half of "a bad value stops the
#   run before any branch or leaf": skills/tdd/SKILL.md's preflight runs it once for a
#   developer name and once for a verifier name, and says its exit 2 stops the run. That
#   case reads the document as text, the way issue-worktree.test.sh's last case reads
#   SKILL.md's entry for its own script — a resolver called for the first time at launch
#   refuses a typo'd model only after the branch, the worktree and the plan already exist.
#
# The three names are cleared for every child below, for the reason hermetic-suites.test.sh
# exists (issue #87): a suite's answer is a fact about the script, not about whatever the
# shell that invoked `make test` had exported.
#
# Run: scripts/tests/leaf-model.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LEAF_MODEL="$HERE/../leaf-model.sh"
LEAF_ROLE="$HERE/../leaf-role.sh"
# The document once, as the path every failure message spells, read as "$ROOT/$skill_md" —
# the shape skill-event-marks.test.sh uses, and the one that makes a message unable to name
# a file the probe did not open. The suite sits at skills/<skill>/scripts/tests, so four
# levels up is the repo root.
ROOT="$(cd "$HERE/../../../.." && pwd)"
skill_md="skills/tdd/SKILL.md"
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

# model_call <run-wide> <developer> <verifier> <leaf-name> — make one call to the script under
# the three variables, and leave the whole of its answer in the caller's locals: `code`, the
# files `out` and `err`, and `label`, the line every problem message is prefixed with. Each
# value is given as its value or as the word `unset`. The two probes below differ only in what
# they then assert, so everything up to the call is written once here — and has to be: the
# question this suite asks is which of the three variables a leaf reads, so a probe that
# cleared one name the other did not would be answering about the caller's shell rather than
# about the script.
#
# `env -u` on all three names clears them for the child only, so a probe never depends on — nor
# disturbs — what the surrounding run exported; `env` applies its assignments after its `-u`s,
# so the pair says "these values, nothing ambient" in one list. Separate files per stream, since
# the contract is partly about which stream carries what. It writes into the caller's locals
# rather than printing, because the exit code and two streams cannot come back through one
# command substitution — and because a value with a space in it is exactly what case 3 probes.
# The caller owns the two files, and removes them.
model_call() {
  local -a envargs
  label="VERI_MODEL=$1 VERI_MODEL_DEVELOPER=$2 VERI_MODEL_VERIFIER=$3 $4"
  envargs=(-u VERI_MODEL -u VERI_MODEL_DEVELOPER -u VERI_MODEL_VERIFIER)
  [[ "$1" == unset ]] || envargs+=(VERI_MODEL="$1")
  [[ "$2" == unset ]] || envargs+=(VERI_MODEL_DEVELOPER="$2")
  [[ "$3" == unset ]] || envargs+=(VERI_MODEL_VERIFIER="$3")
  out="$(mktemp)" err="$(mktemp)"
  env "${envargs[@]}" "$LEAF_MODEL" "$4" >"$out" 2>"$err" && code=0 || code=$?
}

# model_probe <run-wide> <developer> <verifier> <leaf-name> <want> — one call the script
# must answer, under all three variables. Each is given as its value or as the word `unset`,
# and <want> is the exact stdout expected — the empty string for a run that chose no model.
# One probe for every case below: which of the three a leaf reads is the whole subject here,
# so a probe that could only open one of them could not pose the question, and two probes
# differing only in how many names they set would be free to drift in how they call the
# script. A model resolved is not a diagnosable event, so stderr must stay empty in every
# branch.
model_probe() {
  local want="$5" out err code label
  model_call "$1" "$2" "$3" "$4"
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
# Arguments are model_probe's, and the call itself is model_call's, for the same reasons.
model_refuses() {
  local out err code label
  model_call "$1" "$2" "$3" "$4"
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

# 4. Where the script is called from. Cases 1-3 are the whole of what leaf-model.sh answers,
#    and a resolver nobody calls until a leaf launches still costs a branch, a worktree, a
#    plan and a cycle to tell a human that `VERI_MODEL="sonnet 5"` is not one model name —
#    which is the failure the exit 2 of case 3 exists to prevent. So the criterion is about
#    the caller: preflight runs it, beside the `refactor-budget.sh 0` of step 5, before
#    anything is created that a bail would have to revert.
#
#    Once for EACH role, because the three variables do not all reach both: a preflight that
#    only asked a developer name would pass a run whose VERI_MODEL_VERIFIER is the bad value,
#    and every verifier leaf of that run would then die at launch. Which role a name is, is
#    not spelled here either — each name found is handed to `leaf-role.sh`, the one place the
#    name→role mapping lives, so the case asks what the roles ARE rather than what they are
#    called.
#
#    Both cuts below are inline rather than behind a function, the way issue-worktree.test.sh
#    cuts SKILL.md's bullet for its own script: a no-argument helper called once, on the line
#    below its own body, is an indirection with a single reader — and the second of them read
#    `preflight` out of its caller, which is that indirection paying a leaked scope for itself.
name="$skill_md's preflight runs leaf-model.sh for a developer name and for a verifier name, and says its exit 2 stops the run"
problems=()
# `preflight` — the lines of SKILL.md's first `### ` section whose heading is a numbered
# Preflight, up to the next `### `. Cut the section out rather than reading the file: the
# document describes every script once more under `## The scripts`, and a file-wide grep
# would answer "yes, leaf-model.sh is in there" for a procedure whose preflight never runs
# it — which is the whole of what this case asks. Matched by the word and not by its number,
# so renumbering the procedure does not fail the case; `[0-9]+\.` is what tells it from
# `### Loop 0. Preflight — none of its own`, which delegates every check back to here.
preflight="$(awk '/^### [0-9]+\..*[Pp]reflight/ { inside = 1; print; next }
                  inside && /^### / { exit }
                  inside' "$ROOT/$skill_md")"
if [[ -z "$preflight" ]]; then
  problems+=("$skill_md: no numbered '### … Preflight' section — what preflight runs could not be read")
else
  # The loop is fed (at its `done`) the argument of every `leaf-model.sh <name>` in that
  # section, one per line, stripped of the backticks, quotes and trailing punctuation a
  # snippet in prose wraps it in. A name given as a shell variable resolves to nothing a role
  # can be read from and so counts as no name at all: the point of the call is that preflight
  # exercises BOTH roles for real, which a document can only show by naming them.
  roles=""
  while IFS= read -r leaf; do
    # A section with no call at all reaches here once with an empty line, which is the
    # "never runs it" failure and not a refused name: let the two role probes below say so.
    [[ -n "$leaf" ]] || continue
    role_line="$("$LEAF_ROLE" "$leaf" 2>/dev/null)" ||
      { problems+=("$skill_md preflight: leaf-model.sh is called with '$leaf', a name leaf-role.sh refuses"); continue; }
    roles="$roles $(printf '%s\n' "$role_line" | sed -n 's/.*VERI_ACTOR=\([a-z]*\).*/\1/p')"
  done <<< "$(printf '%s\n' "$preflight" \
    | grep -o 'leaf-model\.sh[[:space:]][^[:space:]]*' \
    | awk '{ print $2 }' \
    | tr -d '`"'"'"'' \
    | sed 's/[),;:.]*$//' \
    | grep -v '^$')"
  for want in developer verifier; do
    [[ "$roles" == *" $want"* ]] ||
      problems+=("$skill_md preflight: no leaf-model.sh call with a $want leaf name (names found:${roles:-" none"})")
  done
  # The stop itself, in the section that makes the call: a preflight that ran the resolver
  # and carried on would have paid for the answer and thrown it away. Case-folded once into
  # a variable and matched with `[[ ]]`, so the sentence's own capitalisation is the
  # writer's business and no pipeline's exit status is being read for an answer;
  # `verbatim|diagnostic` because what the bad value was is only legible from the script's
  # own stderr.
  lowered="$(printf '%s\n' "$preflight" | tr '[:upper:]' '[:lower:]')"
  [[ "$lowered" == *leaf-model.sh* && "$lowered" == *"exit 2"* \
     && "$lowered" =~ (verbatim|diagnostic) ]] ||
    problems+=("$skill_md preflight: does not say leaf-model.sh's exit 2 stops the run, reporting its stderr diagnostic")
fi
report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
