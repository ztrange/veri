# lib/leaf-role.sh — sourced, not run: defines `leaf_role`, the one place a leaf's NAME is
# turned into the role its events are logged under (issue #107, ADR-0014: observability is a
# per-run event log written by the scripts, not a service).
#
# Perf: this used to be a whole script, forked by every writer that needed the mapping —
# supervise.sh, verify.sh, harvest-usage.sh and leaf-model.sh, which asks it too — 330 times
# in one `make test` and once per leaf in every real run. Sourcing this file instead pays
# that once per process instead of once per leaf. `leaf-role.sh` (the CLI beside this file)
# is now a thin wrapper over the function below, kept for whatever still wants to shell out
# to it — its own suite calls it that way on purpose, to hold the CLI contract to the letter.
#
# The three name shapes the run launches are `develop-<phase>` (SKILL.md:415, 469 and 511),
# `revise-<phase>-<k>` (SKILL.md:643) and `verify-<phase>`. `develop` and `revise` are both the
# developer, since a revise leaf is a fresh developer answering the verifier's objection, not a
# third role — which is the one thing about these shapes the notation cannot show, so it is said
# here and the rest is said at the two cuts that perform it.
#
# leaf_role <leaf-name> — prints the role as environment assignments,
# `VERI_ACTOR=… VERI_PHASE=… VERI_ATTEMPT=…`, and returns 0; or prints a diagnostic on stderr
# and returns 2 with nothing on stdout, for a name none of the three shapes above cover. A
# caller writes `env $(leaf_role "$name") event.sh launch …` (a caller in THIS shell — no
# subprocess to word-split into), the same convention the CLI wrapper's header describes.
#
# `return`, never `exit`: unlike the old subprocess, this runs IN the caller's shell once
# sourced, so a caller that invokes it directly (not through a `$(...)` command substitution,
# which forks its own subshell regardless) would have that subshell — or, without one, the
# caller's whole process — torn down by an `exit`, where a failed subprocess used to just
# leave a non-zero $? for the caller to read. Every call site in this codebase still wraps
# this in `$(...)`, so `return` and `exit` are equivalent there; `return` is what stays safe
# if that ever stops being true.
leaf_role() {
  local name="$1"

  # A missing/empty name is a caller bug, not a name the mapping refused — the CLI wrapper
  # guards this with `${1:?...}` before ever calling in, so no call site in this codebase
  # reaches this branch. It is here anyway because a function, unlike the old subprocess,
  # can be called from somewhere this file's own header cannot see everything that reaches.
  if [[ -z "$name" ]]; then
    echo "leaf-role: usage: leaf-role.sh <leaf-name>" >&2
    return 2
  fi

  # The name splits at its first `-` into the two halves the role is read out of, and each
  # cut is made just above the arm that reads it. `%%-*` strips the longest trailing match of
  # `-*`, leaving the leading word, which is the actor's.
  local actor_word="${name%%-*}"
  local actor
  # The shapes both refusals below name, said once so the two cannot drift apart.
  local want='develop-*|revise-*|verify-*'

  # An unknown leading word is refused rather than guessed at, since either guess is a silent
  # wrong answer in a log whose purpose is telling the pipeline's two halves apart: an actor
  # defaulted to `developer` files the leaf's events under a role it never had, and an actor
  # left empty writes `"actor": ""` for a leaf that had one.
  case "$actor_word" in
    develop|revise) actor=developer ;;
    verify)         actor=verifier  ;;
    # parallel-conductors.sh supervises each conductor it launches as `conductor-<n>` (#102):
    # a fourth actor, the run itself rather than one of its leaves, whose "phase" is the issue.
    conductor)      actor=conductor ;;
    *)
      echo "leaf-role: leaf name '$name' has an unknown leading word (want $want)" >&2
      return 2
      ;;
  esac

  # The other half: everything past the leading word and the `-` that would end it, which is
  # the phase and, when the name carries one, the attempt — `red`, `green-2`, `refactor`. Cut
  # by length rather than by a second pattern, because a pattern invents a phase where there
  # is none: `${name#*-}` returns the WHOLE string when there is no `-` to strip, so `develop`
  # would read as phase `develop`, a phase no run has. Counting past the word runs off the end
  # of `develop` instead, and off the end of `develop-` too, so both say what they mean —
  # nothing.
  local phase_attempt="${name:${#actor_word}+1}"

  # A name that carries no phase is refused for the same reason the unknown word above is:
  # the answer would be invented rather than read. Neither `develop` (no `-` at all) nor
  # `develop-` (the `-` with nothing after it) may be logged in place of a refusal — event.sh
  # writes every context key whether or not it is known, so the empty phase would go down as
  # `"phase": ""`, which reads as a leaf that had no phase rather than one whose phase nobody
  # could read.
  if [[ -z "$phase_attempt" ]]; then
    echo "leaf-role: leaf name '$name' says no phase (want $want)" >&2
    return 2
  fi

  local phase attempt

  # A trailing `-<digits>` is the attempt the name carries, and what precedes it is the phase;
  # a name without one is attempt 1. One regex states the whole split and both halves are read
  # out of its captures — `(.*)` is greedy, so on `green-2` it takes `green` and leaves the
  # digits to `([0-9]+)`.
  if [[ "$phase_attempt" =~ ^(.*)-([0-9]+)$ ]]; then
    phase="${BASH_REMATCH[1]}"
    attempt="${BASH_REMATCH[2]}"
  else
    phase="$phase_attempt"
    attempt=1
  fi

  echo "VERI_ACTOR=$actor VERI_PHASE=$phase VERI_ATTEMPT=$attempt"
}
