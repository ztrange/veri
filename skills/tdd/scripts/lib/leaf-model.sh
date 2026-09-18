# lib/leaf-model.sh — sourced, not run: defines `leaf_model`, which says which model one
# leaf runs on, so a run can price the two leaf roles separately (issue #171). See
# `leaf-model.sh`, the CLI beside this file, for the fuller rationale (why no leaf chooses a
# model today without this, why the value is printed verbatim and unvalidated against a list
# of the `claude` CLI's own vocabulary) — restating it here would leave two copies of the same
# reasoning for the file that changes to drift out of step with.
#
# Perf: sourced by supervise.sh and verify.sh in place of forking `leaf-model.sh` — 157 times
# in one `make test`, once per leaf model resolution in every real run — for the reason
# lib/leaf-role.sh's own header gives; `leaf-model.sh` is now a thin wrapper over the
# function below.
#
# Sources lib/leaf-role.sh itself, the same dependency the old subprocess had on
# `leaf-role.sh` (issue #107's actor/phase mapping lives in exactly one place either way), so
# a caller that sources this file gets `leaf_role` too without asking for it twice. Resolved
# relative to THIS file's own directory — `${BASH_SOURCE[0]}`, not `$0` — so it finds its
# neighbour whichever caller's `$HERE` sourced it from.
_veri_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/leaf-role.sh
source "$_veri_lib_dir/leaf-role.sh"
unset _veri_lib_dir

# leaf_model <leaf-name> — prints the resolved model on stdout and returns 0 (nothing printed
# when the run chose none, still exit 0 — not a default), or prints a diagnostic on stderr
# and returns 2 with nothing on stdout, for a value with whitespace in it or a leaf name
# leaf_role above refuses.
#
# `VERI_MODEL` is the run-wide knob: it applies to every leaf. `VERI_MODEL_DEVELOPER` and
# `VERI_MODEL_VERIFIER` each apply to one role's leaves only, and beat the run-wide knob
# there. The value is printed verbatim: aliases (`sonnet`, `opus`, `opus[1m]`) and full ids
# are the `claude` CLI's own vocabulary, not veri's, so this neither maps nor validates them.
#
# `return`, never `exit` — lib/leaf-role.sh's header gives the reason, and it applies here
# doubly: this function also calls `leaf_role`, so an `exit` inside THAT call would already
# be a problem if either ever ran outside a `$(...)` subshell.
leaf_model() {
  local name="$1"

  # Same "unreachable from any call site in this codebase" guard as lib/leaf-role.sh's own,
  # and for the same reason: the CLI wrapper validates before calling in.
  if [[ -z "$name" ]]; then
    echo "leaf-model: usage: leaf-model.sh <leaf-name>" >&2
    return 2
  fi

  # The role comes from leaf_role, the one place a leaf NAME is turned into the half of the
  # pipeline it belongs to. Asking it, rather than matching `develop-*|revise-*|verify-*`
  # here, is what stops two places disagreeing about what `revise-green-2` is — and it is
  # also why the variable name below ends in the actor word: the suffix IS leaf_role's
  # answer, uppercased, so the name→role mapping is spelled once.
  #
  # `$(...)` still forks a subshell to run `leaf_role` in, so a refusal inside it (`return 2`)
  # becomes this command substitution's exit status exactly the way it became the old
  # subprocess's — the `||` below catches it the same way callers already catch the CLI's
  # exit 2.
  local role_line
  role_line="$(leaf_role "$name")" || return 2

  # Only the actor is wanted here, so it is read out of the `VERI_ACTOR=… VERI_PHASE=…
  # VERI_ATTEMPT=…` line rather than evaluated. `tr` rather than `${var^^}`, which bash 3.2
  # does not have.
  local actor="${role_line#VERI_ACTOR=}"
  actor="${actor%% *}"
  local role_var="VERI_MODEL_$(printf '%s' "$actor" | tr '[:lower:]' '[:upper:]')"

  # `${!role_var:-}` reads the variable whose NAME is in role_var. The role's own value is
  # taken first and the run-wide one is the fallback, so precedence is the order of this one
  # expansion.
  local model="${!role_var:-${VERI_MODEL:-}}"

  # Whitespace in the value is the one thing this can refuse without asking a network what a
  # model id is: `claude --model "sonnet 5"` is a SINGLE argument, and no alias or id is
  # spelled with a space in it. Refused here rather than at launch because preflight calls
  # this once per role before any branch or leaf, so the run stops at the typo instead of
  # paying a whole leaf to discover it. Only whitespace: `opus[1m]` is what the development
  # machine actually runs on, so a guard written as "plain alphanumeric only" would take the
  # brackets with the spaces and break every leaf.
  if [[ "$model" =~ [[:space:]] ]]; then
    echo "leaf-model: model '$model' contains whitespace (a model id or alias is one word)" >&2
    return 2
  fi

  # The empty case prints nothing rather than an empty line, so "no model chosen" is the
  # absence of output — the caller turns a non-empty answer into `--model <value>` and must
  # not put a flag on a command line for a run that chose no model.
  if [[ -n "$model" ]]; then
    echo "$model"
  fi
}
