#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — rung 2's selection layer. Given a repo's
# issues and open PRs, print the numbers of the issues veri may take RIGHT NOW, one per
# line, lowest first, and exit 0; print nothing and exit 3 when there are none.
#
# Contract under test (issues #41, #91):
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh. That override is the whole reason this suite needs no
#                        network: the fixtures carry the exact shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#   VERI_LABEL=<name>    the opt-in label to select on, default `ready-for-agent`, so two
#                        loops against one repo can be pointed at two labels and drain
#                        disjoint pools. Set but EMPTY is refused with exit 2 rather than
#                        read as "any label", which would take every open issue.
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
# The repository root, four levels above `tests` — past `scripts`, `solve-issue` and
# `skills`. Only the cases that read a committed file reach for it — the documentation cases,
# and the one asserting the generated walkthrough still quotes this script as it stands — but
# it belongs beside the other path anchors: here the `..` are checkable against the `HERE`
# they climb from. Those cases are described rather than numbered on purpose: a comment that
# cites a case by number is wrong the moment one is inserted above it, which is the drift
# #91's own issue text catalogues in docs/tests/build-guards.test.sh.
REPO_ROOT="$(cd "$HERE/../../../.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The suite's own cwd from here down, and the reason it is not the one `make test` was typed in:
# `solvable-issues.sh` reads a run's claim off local disk, out of the MAIN working tree of the
# repository it is invoked in (`solvable-issues.sh:136-141, 202-212`). Invoked from here, that is
# this repository — so on a machine where veri is solving one of the numbers a fixture names, the
# live `.tdd/wt/<n>/.tdd/conductor.pid` of that run answers a question the case only asked of its
# fixture, and the suite goes red for what the run did by claiming its issue (#226). A repository
# the suite built and never claims anything in answers the same question with "nobody holds this",
# which is the fixture's own answer. The cases that DO have claims to pin cd into a repository of
# their own for the duration (cases 17, 18, 21); this is the floor under every other case.
#
# Done once here rather than per helper so that it holds for a case added later that invokes
# `$SOLVABLE` directly, which is the shape of the case the leak was found in. Every path the
# suite hands out is absolute — `$work` from `mktemp -d`, `$REPO_ROOT` and `$SOLVABLE` from
# `$HERE` — so nothing else reads differently from in here.
#
# A `git init` with no commit is enough: `git worktree list` prints this directory as the main
# tree, and there is no `.tdd` under it, so every lookup misses and `in_flight` is False.
no_claims="$work/no-claims"
git init -q -b main "$no_claims" >/dev/null 2>&1
cd "$no_claims" || exit 2

# A fixture directory for one case, printed so the caller can capture it. Both halves of
# the override's contract are seeded here: the directory itself, and an empty `prs.json` —
# the no-PR default — so a case writes only the files it actually varies. Most vary just
# `issues.json`; a case that turns on an open PR overwrites `prs.json` too.
fixture() {  # fixture <name> -> path
  local dir="$work/$1"
  mkdir -p "$dir"
  printf '[]\n' > "$dir/prs.json"
  echo "$dir"
}

# Run the script against one fixture directory, leaving its stdout in $out and its exit code
# in $code — the pair every case below asserts on. Neither is `local`, deliberately: the
# assertion lives at the call site, which is where the expected values belong. stderr is
# dropped; no case asserts on it.
#
# Anything after the directory is forwarded to the script as its own argv, the way `gh_run`
# below forwards its own: one case turns on `--repo owner/name`, and that flag belongs at its
# call site rather than in a second copy of this invocation. Most cases pass nothing, and
# `"$@"` then expands to no words at all.
run() {  # run <fixture-dir> [script args…]; sets $out and $code
  local fixture="$1"; shift
  out="$(VERI_GH_JSON="$fixture" "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

# The same run, for the cases whose criterion is what VERI_LABEL says. The settings are handed
# to `env` verbatim — `-u VERI_LABEL` to guarantee the variable is ABSENT rather than merely
# unset by this shell, `VERI_LABEL=<name>` to give it a value — so the one thing separating
# those cases stays at the call site, where it is the point, and only the invocation is shared.
label_run() {  # label_run <fixture-dir> <env setting…>; sets $out and $code
  local fixture="$1"; shift
  out="$(env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

# The same run once more, for the cases whose criterion is WHICH STREAM carried what: a label
# tunable set but empty is refused with a diagnostic on stderr and nothing on stdout, so the
# two must not be merged and `label_run`, which drops stderr, cannot serve them. Each stream
# goes to its own file inside the case's own fixture directory — the script reads only
# `issues.json` and `prs.json` out of it, so nothing else there is in its way — leaving the two
# paths in $refused_out and $refused_err and the exit code in $refused_code, all three asserted
# at the call site. The settings are forwarded to `env` exactly as `label_run` forwards them,
# so the one `VERI_…=` under test stays where it is the point.
refused_run() {  # refused_run <fixture-dir> <env setting…>; sets $refused_out/$refused_err/$refused_code
  local fixture="$1"; shift
  refused_out="$fixture/refused.out" refused_err="$fixture/refused.err"
  env "$@" VERI_GH_JSON="$fixture" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
    && refused_code=0 || refused_code=$?
}

# 1. The base case, and the one the VERI_GH_JSON override exists to make testable: a single
# open issue, carrying the ready-for-agent opt-in label, naming no blocker, with no open PR
# claiming it. Nothing stands between veri and a run on it, so it is listed on its own line.
#
# The body writes `None.` with a trailing period on purpose — that is how veri's own issues
# write the section (#41's own `## Blocked by` reads `None.`), so what makes an issue
# unblocked is the ABSENCE of a `#<n>` reference under the heading, not the literal string
# `None`. Asserting against the real format keeps the parser honest about veri's own repo.
fx="$(fixture unblocked)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 41,
    "title": "solvable-issues.sh: list the issues veri may take, in order",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA script that prints the numbers veri may take.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "41" ]]; } \
  && ok || no "open ready-for-agent issue with no blockers is listed (exit=$code want 0, stdout='$out' want '41')"

# 2. A blocker gates the issue, and only while it is open. Both halves are the same
# criterion observed twice, so they are one case: the same two issues are fed in twice,
# changing nothing but #49's state. While #49 is OPEN, #50 names it under `## Blocked by`
# and must not be listed — #49 itself still is, since it carries the label and names no
# blocker of its own. Close #49 and #50 becomes takeable; #49 drops out because a closed
# issue is never solvable, so the same fixture pair yields "49" then "50".
fx="$(fixture blocked)"
issues() {  # issues <state-of-49>
  cat <<JSON
[
  {
    "number": 50,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA loop over solvable-issues.sh.\n\n## Blocked by\n\n#49\n"
  },
  {
    "number": 49,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "$1",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
}

issues OPEN > "$fx/issues.json"
run "$fx"; while_open="$out" open_code="$code"

issues CLOSED > "$fx/issues.json"
run "$fx"; once_closed="$out" closed_code="$code"

{ [[ "$open_code" == 0 && "$while_open" == "49" ]] \
  && [[ "$closed_code" == 0 && "$once_closed" == "50" ]]; } \
  && ok || no "issue blocked by an open issue is withheld until that issue closes (blocker open: exit=$open_code want 0, stdout='$while_open' want '49'; blocker closed: exit=$closed_code want 0, stdout='$once_closed' want '50')"

# 3. The label is an opt-in gate, not a hint: without `ready-for-agent` an issue is never
# listed, however takeable it otherwise looks. #51 is fed in with the most favourable
# blocker state there is — `None.`, nothing standing in its way — so the ONLY thing
# withholding it is the missing label; an implementation that dropped that check would
# list it, and it sorts below #52 so the miss shows up as "51\n52" rather than a reorder.
# #52 is the labelled control: it keeps stdout non-empty and the exit 0, which is what
# isolates this case from the empty-result criterion (no solvable issue → exit 3).
fx="$(fixture unlabelled)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 51,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## What to build\n\nSomething, eventually.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 52,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "52" ]]; } \
  && ok || no "issue without the ready-for-agent label is never listed (exit=$code want 0, stdout='$out' want '52')"

# 4. An open PR that says `Closes #53` owns #53 — a run is already in flight on it, or one
# bailed and left the branch behind — so #53 is not veri's to take however takeable the
# issue itself looks. It is fed in at its most takeable: open, labelled, `None.` under
# `## Blocked by`, so the ONLY thing withholding it is the PR. This is the first case whose
# `prs.json` is not the empty list the fixture helper seeds, so it is overwritten below.
# #54 is the control, unclaimed and labelled: it keeps stdout non-empty and the exit 0,
# isolating this case from the empty-result criterion, and it sorts above #53 so an
# implementation ignoring PRs shows up as "53\n54" rather than a reorder.
fx="$(fixture claimed)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 53,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA script that prints the numbers veri may take.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 54,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run.\n\nCloses #53\n"
  }
]
JSON

run "$fx"

{ [[ "$code" == 0 ]] && [[ "$out" == "54" ]]; } \
  && ok || no "issue an open PR already Closes is not listed (exit=$code want 0, stdout='$out' want '54')"

# 5. The shape of the output itself, observed at both ends of the range it can take. With
# three takeable issues fed in deliberately out of order (57, 55, 56), stdout is exactly
# "55\n56\n57": ascending, one number per line — separators other than a newline, or the
# input's own order, both show up as a mismatch against that single string. With nothing
# takeable — #58 is labelled but blocked by #59, which is open and unlabelled, so neither
# qualifies — there is no list to print, and the caller learns that from the exit code
# rather than from having to notice empty output: exit 3, veri's "nothing to do" (not an
# error), and stdout empty.
fx="$(fixture ordering)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 57,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 55,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 56,
    "title": "classify-bail.sh: label the bail a human reads",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"; many="$out" many_code="$code"

fx="$(fixture none)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 58,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#59\n"
  },
  {
    "number": 59,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx"; empty="$out" empty_code="$code"

{ [[ "$many_code" == 0 && "$many" == $'55\n56\n57' ]] \
  && [[ "$empty_code" == 3 && -z "$empty" ]]; } \
  && ok || no "output is one number per line ascending, and no solvable issue means exit 3 and empty stdout (three takeable: exit=$many_code want 0, stdout='$many' want '55\\n56\\n57'; none takeable: exit=$empty_code want 3, stdout='$empty' want empty)"

# 6. The override is an override: with VERI_GH_JSON unset the script must go and get the
# two JSON documents itself, from `gh issue list` and `gh pr list`, and must put a
# `--repo owner/name` it was given onto both of those calls — a wrong repo is silently
# wrong, so the flag reaching gh is the whole of the criterion.
#
# Driven against a stub `gh` first on PATH, the same way tick-issue-criterion.test.sh
# drives its wrapper: the stub appends its own argv to $ARGV_OUT and then prints the
# fixture the case wants for that subcommand, so the test observes both halves at once —
# what the script asked gh for, and what it did with the answer. The directory below is
# only the stub's pantry; the script never learns its path.
#
# The fixtures make BOTH calls load-bearing. #60 and #61 are equally takeable — open,
# labelled, `None.` under `## Blocked by` — and an open PR says `Closes #60`, so stdout is
# "61" only if the issues came from `gh issue list` AND the PRs from `gh pr list`. A script
# that skipped the PR call would print "60\n61".
#
# Both halves of "when given" are observed, one run each, changing nothing but the flag:
# without it neither gh call may carry `--repo` (an invented default is as wrong as a
# dropped flag), with it both must.
fx="$(fixture gh)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 60,
    "title": "solvable-issues.sh: list the issues veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 61,
    "title": "the /tdd loop skill",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run.\n\nCloses #60\n"
  }
]
JSON

stubdir="$work/bin"
mkdir -p "$stubdir"
cat > "$stubdir/gh" <<'STUB'
#!/bin/sh
printf '%s\n' "$*" >> "$ARGV_OUT"
case "$1 $2" in
  "issue list") cat "$GH_ISSUES" ;;
  "pr list")    cat "$GH_PRS" ;;
esac
STUB
chmod +x "$stubdir/gh"

# Run the script with VERI_GH_JSON explicitly removed from the environment and the stub
# first on PATH, leaving stdout in $out, the exit code in $code and one line per gh call in
# the named log. `env -u` is what guarantees the override is absent rather than merely
# unset here, since the script's whole behaviour under test hinges on that.
gh_run() {  # gh_run <argv-log> [script args...]; sets $out and $code
  local log="$1"; shift
  : > "$log"
  out="$(env -u VERI_GH_JSON PATH="$stubdir:$PATH" ARGV_OUT="$log" \
         GH_ISSUES="$fx/issues.json" GH_PRS="$fx/prs.json" \
         "$SOLVABLE" "$@" 2>/dev/null)" && code=0 || code=$?
}

gh_run "$work/argv-bare"; bare="$out" bare_code="$code"
bare_argv="$(cat "$work/argv-bare")"

gh_run "$work/argv-repo" --repo owner/name; scoped="$out" scoped_code="$code"
repo_argv="$(cat "$work/argv-repo")"

{ [[ "$bare_code" == 0 && "$bare" == "61" ]] \
  && grep -q '^issue list' <<<"$bare_argv" && grep -q '^pr list' <<<"$bare_argv" \
  && ! grep -q -- '--repo' <<<"$bare_argv" \
  && [[ "$scoped_code" == 0 && "$scoped" == "61" ]] \
  && [[ "$(grep -c -- '--repo owner/name' <<<"$repo_argv")" == 2 ]]; } \
  && ok || no "without VERI_GH_JSON the script reads gh issue list and gh pr list itself, forwarding --repo when given (no flag: exit=$bare_code want 0, stdout='$bare' want '61', gh calls=$(tr '\n' '|' <<<"$bare_argv") want an 'issue list' and a 'pr list', neither with --repo; --repo owner/name: exit=$scoped_code want 0, stdout='$scoped' want '61', gh calls=$(tr '\n' '|' <<<"$repo_argv") want --repo owner/name on both)"

# 7. `ready-for-agent` is the DEFAULT, not merely what the script happens to say: with
# VERI_LABEL absent from the environment the opt-in gate is exactly the one cases 1-3 pin.
# This is the criterion that keeps a loop launched with no VERI_LABEL draining the pool it
# has always drained, so the two issues fed in straddle the default from the side a
# parameterised implementation is most likely to get wrong. #62 carries `ready-for-agent`
# and must be listed; #63 carries `ready-for-agent:docs` and must NOT be, because the match
# is on the exact label name — a default that matched a prefix, a substring, or any label at
# all would take #63 too, and since it sorts below #62 that shows up as "62\n63" rather than
# a reorder. Both are otherwise maximally takeable (open, `None.` under `## Blocked by`, no
# open PR), so the label is the only thing separating them.
#
# `label_run "$fx" -u VERI_LABEL` rather than the plain `run` helper above: the criterion is
# the variable being UNSET, and a suite that merely never sets it would pass by accident in a
# shell that had VERI_LABEL exported for some other reason. Case 6's `gh_run` unsets
# VERI_GH_JSON the same way and for the same reason.
fx="$(fixture default-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 62,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 63,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "62" ]]; } \
  && ok || no "with VERI_LABEL unset the opt-in label is exactly ready-for-agent (exit=$code want 0, stdout='$out' want '62')"

# 8. VERI_LABEL set to another name MOVES the gate rather than widening it: the pool becomes
# exactly the issues carrying that label, and the default stops being special. The two issues
# fed in are the two halves of that, one each. #64 carries only `ready-for-agent` — the label
# the script hardcodes today — and must NOT be listed; #65 carries `ready-for-agent:docs`, the
# value the variable is set to, and must be. Nothing else separates them: both are open, both
# read `None.` under `## Blocked by`, and `prs.json` is the fixture helper's empty list, so the
# label is the only thing deciding either way.
#
# The pair is what makes both halves load-bearing at once. An implementation that ignored
# VERI_LABEL prints "64"; one that read it but kept the default as a second accepted label
# prints "64\n65"; one that treated the variable as "any label" prints "64\n65" too. Only a
# script matching the exact name it was given prints "65" alone — and since #64 sorts above
# #65, every one of those misses shows up as a different string rather than a reorder.
fx="$(fixture other-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 64,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 65,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" VERI_LABEL=ready-for-agent:docs

{ [[ "$code" == 0 ]] && [[ "$out" == "65" ]]; } \
  && ok || no "with VERI_LABEL set to another label only issues carrying that label are listed (exit=$code want 0, stdout='$out' want '65')"

# 9. Cases 7 and 8 pin the two pools apart; this one pins the overlap between them. An issue
# carrying BOTH `ready-for-agent` and `ready-for-agent:docs` belongs to both pools at once —
# it is the shared work, the issue either loop may take — so it is listed under either value
# of VERI_LABEL. That is one criterion observed twice: the same single-issue fixture is run
# twice, changing nothing but the variable, and #66 must come back both times.
#
# Nothing else can account for either answer: #66 is the only issue fed in, it is open, it
# reads `None.` under `## Blocked by`, and `prs.json` is the fixture helper's empty list. So
# stdout is "66" exactly when the label matched and empty (with exit 3) when it did not.
#
# Feeding one issue two labels is what makes the case bite whichever way an implementation
# cuts corners: a script testing only the FIRST entry of `labels[]` answers one of the two
# runs and misses the other, whichever order the fixture lists them in, and a script that
# stopped at the first label it recognised would do the same.
fx="$(fixture both-labels)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 66,
    "title": "walkthrough: draw rung 2's selection layer",
    "labels": [{"name": "ready-for-agent"}, {"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## What to build\n\nA panel for solvable-issues.sh.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_LABEL; under_default="$out" default_code="$code"

label_run "$fx" VERI_LABEL=ready-for-agent:docs; under_docs="$out" docs_code="$code"

{ [[ "$default_code" == 0 && "$under_default" == "66" ]] \
  && [[ "$docs_code" == 0 && "$under_docs" == "66" ]]; } \
  && ok || no "an issue carrying both labels is listed under either VERI_LABEL value (VERI_LABEL unset: exit=$default_code want 0, stdout='$under_default' want '66'; VERI_LABEL=ready-for-agent:docs: exit=$docs_code want 0, stdout='$under_docs' want '66')"

# 10. VERI_LABEL set to the EMPTY STRING is not a label, and the script refuses rather than
# guessing which one was meant: exit 2 — veri's "no answer could be obtained", the system
# failure rather than the clean negative — a diagnostic on stderr, and nothing on stdout, the
# same fail-closed shape refactor-budget.sh gives a malformed VERI_REFACTOR_BUDGET. This is
# the one misconfiguration that must never fall through to a default or to "any label": an
# empty match would hand the loop every open issue, which is precisely what the opt-in exists
# to prevent, and a `VERI_LABEL="$some_unset_var"` in a launcher is how it gets there.
#
# The two issues fed in are what tells the failure modes apart in the message. #67 carries
# `ready-for-agent` and #68 carries `ready-for-agent:docs`; both are otherwise maximally
# takeable (open, `None.` under `## Blocked by`, the fixture helper's empty `prs.json`). So a
# script that quietly fell back to the default — `${VERI_LABEL:-ready-for-agent}` treats empty
# and unset alike — prints "67" and exits 0, while one that read the empty value as "any
# label" prints "67\n68" and exits 0. Both are visible against exit 2 with stdout empty.
#
# `refused_run` rather than `label_run`: which stream carries what IS the criterion here, and
# stdout's emptiness is asserted as well as stderr's content.
fx="$(fixture empty-label)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 67,
    "title": "solvable-issues.sh: take the opt-in label from VERI_LABEL",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA label parameter with ready-for-agent as the default.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 68,
    "title": "walkthrough: draw rung 2",
    "labels": [{"name": "ready-for-agent:docs"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

refused_run "$fx" VERI_LABEL=

{ [[ "$refused_code" == 2 ]] \
  && [[ ! -s "$refused_out" ]] \
  && [[ -s "$refused_err" ]]; } \
  && ok || no "VERI_LABEL set to the empty string is refused with exit 2 and a diagnostic on stderr, never treated as any label (exit=$refused_code want 2, stdout='$(tr '\n' '|' < "$refused_out")' want empty, stderr='$(tr '\n' ' ' < "$refused_err")' want a diagnostic)"

# The document that carries the loop procedure, relative to $REPO_ROOT. Both of the two cases
# below read it — case 11 for the knob it must document, case 12 for one bullet of it — so it
# is spelled once here rather than in each: since #105 the loop is part of the `/tdd` skill,
# and since #202 it is the sibling file `SCOPE-LOOP.md` rather than a section of `SKILL.md`,
# read only when the argument resolves to a scope — a move like either one should have a
# single line to edit in this suite.
skill_doc="skills/tdd/SCOPE-LOOP.md"
# The single-issue procedure, which stayed in SKILL.md when the loop left it: case 20 below
# reads *its* step 1, not the loop's.
procedure_doc="skills/tdd/SKILL.md"

# Two cases read one bullet out of `$skill_doc` rather than the whole document — case 12 the
# exit-3 instruction, case 28 the exit-0 one — for the same reason each states: a file-wide
# grep goes green on the words appearing anywhere else and pins nothing. They slice it the
# same way, so the slice is spelled once here: keep from the line that opens the bullet until
# the line that ends it. The regexes arrive as arguments and are therefore dynamic, which is
# why a caller writes `[*]` where a literal awk pattern would write `\*` — a backslash escape
# inside `awk -v` is the shell-to-awk string's, not the regex's, and what survives it differs
# between awks. The variables are `opens`/`ends` rather than the obvious `close`,
# which is an awk builtin and a syntax error as a variable name in the BSD awk this repository
# has to run under.
loop_bullet() {  # loop_bullet <opening-line regex> <line that ends it>
  awk -v opens="$1" -v ends="$2" '
    $0 ~ opens { keep = 1 }
    $0 ~ ends  { keep = 0 }
    keep
  ' "$REPO_ROOT/$skill_doc"
}

# 11. A knob nobody is told about is not a parameter, it is a secret, so the three documents a
# human reads before launching a loop must carry it: the loop's own procedure
# (`$skill_doc`, which is where `--repo` and `VERI_MAX_ISSUES` are already
# written down), the README's rung-2 paragraph, and CONTEXT.md, where *solvable* and the
# eligibility signal are defined. Each must name the variable AND say what it is for — one
# label per loop, so two loops on one repo draw from different pools. The variable name alone
# would leave a reader knowing a label can be changed and not why anyone would.
#
# This case lives in this suite rather than docs/tests/build-guards.test.sh because it is the
# contract of `solvable-issues.sh` that is being documented, and because `make docs-check` is
# deliberately not part of `make test` (Makefile, "Neither is part of `test` on purpose") — a
# documentation case parked there would not run in the suite this change is verified against.
#
# The wording is matched loosely on purpose: the exact sentence is the writer's, so the regex
# accepts spaces or hyphens between the four words that carry the claim, and the variable is
# matched literally because `VERI_LABEL` is the string a reader greps for. Every miss is named
# in the failure message, file by file, so one run says which document is short of what.
#
# One document, one claim: record a miss tagged `<doc>:<tag>` unless the document matches.
# The helper lives here rather than beside `run` and `label_run` at the top because only this
# case has documents to read, and the grep arguments stay at the call site, where the
# difference between a literal name and a loosely-matched sentence is the point. What it
# collapses is the accumulator: `$docs_missing $doc:` is spelled once, so the two claims
# cannot drift into reporting misses in two shapes.
doc_claims() {  # doc_claims <doc> <tag> <grep argument…>
  local doc="$1" tag="$2"; shift 2
  grep -q "$@" "$REPO_ROOT/$doc" || docs_missing="$docs_missing $doc:$tag"
}

docs_missing=""
for doc in "$skill_doc" README.md CONTEXT.md; do
  doc_claims "$doc" VERI_LABEL -e 'VERI_LABEL'
  doc_claims "$doc" one-label-per-loop -iE -e 'one[ -]label[ -]per[ -]loop'
done

[[ -z "$docs_missing" ]] \
  && ok || no "the three documents name VERI_LABEL and the one-label-per-loop partitioning use (missing:$docs_missing)"

# 12. Exit 3 is this script's "nothing to do", and what the loop says when it gets one has to
# name the pool it actually drained: a run launched on `ready-for-agent:docs` that reports `no
# ready-for-agent issue` sends the reader to a list that was never consulted, where issues are
# waiting and none of them explains the silence. So the loop's own instruction for exit
# 3 must name the label — `${VERI_LABEL:-ready-for-agent}` — rather than spelling the default
# unconditionally, which is what it did while the label was hardcoded.
#
# The claim is read out of the exit-3 bullet alone, not the whole document: case 11 already
# passes on `VERI_LABEL` appearing ANYWHERE in that document, and it appears in *Loop inputs*,
# so a file-wide grep here would be green against a bullet that still said `ready-for-agent`
# and pin nothing. The awk slice runs from the `- **Exit 3:**` line to the `- **Exit 0:**` that
# ends it, and the case asserts the slice is non-empty before asserting what is in it — an
# empty slice means the headings moved and the claim was never checked, which must read as a
# failure rather than as a pass.
exit3="$(loop_bullet '^- [*][*]Exit 3:' '^- [*][*]Exit 0:')"

{ [[ -n "$exit3" ]] && grep -q 'VERI_LABEL' <<<"$exit3"; } \
  && ok || no "the exit-3 instruction in $skill_doc names the label it drained (bullet='$(tr '\n' ' ' <<<"$exit3")' want a non-empty slice naming VERI_LABEL)"

# 13. was "the committed walkthrough quotes solvable-issues.sh as it now stands": it read the
# line count out of the page's own listing header and compared it to this script's length, so
# that editing the script without rebuilding the page failed here. That claim is the docs
# lane's (#143). It made every commit to solvable-issues.sh owe a `make docs` to keep
# `make test` green — the command preflight reads its baseline off, that every Green leaf
# runs and that both blind verifiers run — which is the coupling ADR 0016 rules out; a page
# behind the code is what `docs-owed.sh` reports and `docs-fresh` catches at a docs merge.
# The number is kept out of this suite, not renumbered away, so the case numbers below still
# match the ones the cases above cite. no-docs-reads.test.sh is what keeps it out.

# 14. A blocker written as a full GitHub URL blocks exactly as `#<n>` does. That spelling is
# not exotic: it is what GitHub's own autocomplete inserts and what a pasted link leaves
# behind, so `- https://github.com/ztrange/veri/issues/120` under `## Blocked by` is the same
# claim as `- #120` and must gate the issue the same way. Case 2 pins that gate for the `#<n>`
# spelling; this is the identical criterion observed through the other one, so the fixture pair
# below is built to case 2's shape and differs from it only in how the blocker is spelled. The
# numbers are the ones the miss was observed on — #125 carrying a URL-form blocker on #120,
# 2026-09-12 — rather than case 2's, so the case carries the incident that motivated it.
#
# One criterion observed twice, for case 2's reason: "blocks exactly as `#<n>` does" is a claim
# about both states, so the same two issues are fed in twice changing nothing but #120's. While
# #120 is OPEN, #125 must not be listed — #120 itself still is, labelled and naming no blocker
# of its own — and once #120 is CLOSED the two swap, #125 becoming takeable while #120 drops out
# for being closed. So the same fixture pair yields "120" then "125".
#
# The labelled blocker is what keeps both halves legible rather than collapsing one into the
# empty-result criterion case 5 owns: stdout is a number either way. A script that reads only
# `#(\d+)` finds nothing in a URL, so the section reads as empty and the issue reads as
# unblocked, and its first run prints "120\n125" — a different string, not a reorder.
fx="$(fixture url-blocked)"
url_issues() {  # url_issues <state-of-120>
  cat <<JSON
[
  {
    "number": 125,
    "title": "walkthrough: a line no commentary chunk claims is owed, not fatal",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nLet the build print what it owes.\n\n## Blocked by\n\n- https://github.com/ztrange/veri/issues/120\n"
  },
  {
    "number": 120,
    "title": "docs-owed.sh: file the commentary debt",
    "labels": [{"name": "ready-for-agent"}],
    "state": "$1",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
}

url_issues OPEN > "$fx/issues.json"
run "$fx"; url_while_open="$out" url_open_code="$code"

url_issues CLOSED > "$fx/issues.json"
run "$fx"; url_once_closed="$out" url_closed_code="$code"

{ [[ "$url_open_code" == 0 && "$url_while_open" == "120" ]] \
  && [[ "$url_closed_code" == 0 && "$url_once_closed" == "125" ]]; } \
  && ok || no "a blocker written as a github.com issue URL blocks exactly as #<n> does (blocker open: exit=$url_open_code want 0, stdout='$url_while_open' want '120'; blocker closed: exit=$url_closed_code want 0, stdout='$url_once_closed' want '125')"

# 15. A github.com issue URL blocks only when it names THIS repository. Case 14 makes the URL
# spelling count at all; the same reading applied to `https://github.com/<owner>/<other>/issues/<n>`
# would invent a blocker out of another project's issue number, and the collision is cheap rather
# than exotic — every low number exists in a fork, in a dependency, and in the demo repo veri's
# own unattended runs are pointed at. So the owner and name in a URL are part of the reference,
# not decoration around the digits.
#
# Which repository "this one" IS has to be told to the script, and `--repo owner/name` is the
# channel it already has — the flag case 6 pins onto both gh calls. It is spelled at this call
# site, through `run`'s argv pass-through, for that reason: this is the only case whose criterion
# turns on the script knowing which repository the numbers came from, and the two other cases
# reading URL-form blockers name no repository, so they must keep reading any owner as local.
#
# #131 is open, labelled, and names a blocker in ANOTHER repository whose number is #120 — which
# is also a real, open, labelled issue HERE. That collision is the whole of the case: a script
# matching the digits after `/issues/` without looking at what precedes them finds 120, sees it
# open, and withholds #131. Since #120 carries the label it is listed either way, so stdout is
# "120\n131" when the owner/name is read as part of the reference and "120" alone when it is
# ignored — a different string, not a reorder, and neither one the empty-result criterion case 5
# owns.
fx="$(fixture foreign-url)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 131,
    "title": "solve-issue: narrate each phase to the issue thread",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA comment per phase.\n\n## Blocked by\n\n- https://github.com/ztrange/veri-demo-node/issues/120\n"
  },
  {
    "number": 120,
    "title": "docs-owed.sh: file the commentary debt",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

run "$fx" --repo ztrange/veri

{ [[ "$code" == 0 ]] && [[ "$out" == $'120\n131' ]]; } \
  && ok || no "a URL naming another repository's issue is not read as a blocker in this one (exit=$code want 0, stdout='$out' want '120\\n131')"

# 16. What counts as a blocker is two spellings rather than one, and the script's own header
# comment is where a reader is told so: it is the paragraph that defines "unblocked", and a
# reader who finds only `#<n>` there writes `- https://github.com/ztrange/veri/issues/120` in an
# issue believing it decorative and gets exactly the miss cases 14 and 15 now pin. So the header
# must name both — the `#<n>` reference and the full `https://github.com/<owner>/<repo>/issues/<n>`
# URL GitHub's autocomplete inserts.
#
# The claim is read out of the header ALONE — everything above `set -euo pipefail`, the same slice
# a reader sees before any code — and not out of the whole file, for case 12's reason: the body
# already spells a github.com issue URL twice, in `blocker_ref` and in the comment above it, so a
# file-wide grep would be green against a header that still said only `#<n>` and pin nothing. The
# slice is asserted non-empty before it is read, so a script that ever stops carrying that `set`
# line reads as a failure rather than as two empty greps finding nothing to complain about.
#
# Both spellings are matched the way case 11 matches its documents: the `#<n>` reference
# literally, because that is the string a reader greps for, and the URL loosely, because whether
# the header writes `<owner>/<repo>`, `ztrange/veri` or `…` between the host and `/issues/` is the
# writer's call and none of the three is the criterion. Each miss is named in the failure message
# so one run says which spelling is short.
#
# One spelling, one claim, through the shape case 11's `doc_claims` already established: the
# helper collapses the accumulator — `$header_missing $tag` written in exactly one place, so two
# claims cannot drift into reporting misses in two shapes — while the grep arguments stay at the
# call site, where the difference between a literal reference and a loosely matched URL is the
# point. It is its own helper rather than `doc_claims` because the subject is a slice of text
# already in hand, not a file under $REPO_ROOT.
header="$(awk '/^set -euo pipefail$/ {exit} {print}' "$SOLVABLE")"

header_names() {  # header_names <tag> <grep argument…>
  local tag="$1"; shift
  grep -q "$@" <<<"$header" || header_missing="$header_missing $tag"
}

header_missing=""
header_names hash-form -e '#<n>'
header_names url-form -E -e 'https://github\.com/[^ ]*/issues/'

{ [[ -n "$header" ]] && [[ -z "$header_missing" ]]; } \
  && ok || no "the header comment of solvable-issues.sh names both blocker spellings (missing:$header_missing; header slice above 'set -euo pipefail' is $(grep -c '' <<<"$header") lines, want a non-empty slice naming '#<n>' and a github.com issues URL)"

# 17. A run in flight claims its issue from its FIRST step, not from the draft PR its conductor
# opens at its last — by writing its own PID into `.tdd/wt/<n>/.tdd/conductor.pid`, which this
# script probes with `kill -0`. What the window before that PR costs while nothing claims the
# issue, and why the signal is a PID rather than a `veri:in-flight` label, are argued once in the
# header comment of solvable-issues.sh; a second copy of that argument here is one that drifts
# (#170).
#
# Three issues, equally takeable in every other respect — open, labelled, `None.` under
# `## Blocked by`, and `prs.json` left at the empty list the fixture helper seeds — so the lock is
# the ONLY thing separating them, and each is one arm of the criterion: #170's worktree holds a
# lock naming a live process ($$, this suite's own shell, alive for as long as the script runs),
# #171's holds one naming a process already reaped, and #172 has no worktree at all. stdout is
# therefore "171\n172": a script still reading PRs alone prints all three, and one that reads any
# lock file as a claim prints "172" by itself.
#
# The two worktrees are made with `git worktree add` rather than `mkdir`, and the script is run
# from inside that throwaway repo, because a real registration is what a run leaves behind — so a
# reading that asks git's registry and one that only stats `.tdd/wt/<n>` both meet this fixture,
# and the case pins the claim rather than the way it is looked up.
fx="$(fixture in-flight)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 170,
    "title": "solvable-issues.sh lists an issue whose conductor is running",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nA run in flight claims its issue from its first step.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 171,
    "title": "a run that bailed and left its worktree behind",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 172,
    "title": "an issue nobody has started",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

# The repository those worktrees hang off: a throwaway `git init` carrying one commit, since
# `git worktree add` refuses a repo with no commit to check out, and given an identity of its own
# so the suite does not depend on whatever user.name/user.email the machine running it carries
# (CI carries none). Same fixture shape as issue-worktree.test.sh's `new_repo`.
flight_repo="$work/in-flight"
mkdir -p "$flight_repo"
git init -q -b main "$flight_repo" >/dev/null 2>&1
git -C "$flight_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1

# claim <n> <pid> — what a conductor leaves on disk for issue <n>: its worktree at
# `.tdd/wt/<n>`, registered with git, holding <pid> in the lock. Written once because the two
# arms differ by the pid alone, and a case that spelled the path twice could pin a claim at one
# path while seeding it at another.
claim() {  # claim <n> <pid>
  local wt="$flight_repo/.tdd/wt/$1"
  git -C "$flight_repo" worktree add -q -b "tdd/$1-slug" "$wt" main >/dev/null 2>&1
  mkdir -p "$wt/.tdd"
  printf '%s\n' "$2" > "$wt/.tdd/conductor.pid"
}

# A pid that is certainly not alive: a child started and reaped right here, so the number was a
# real process a moment ago and is not one now — which is exactly the state a killed conductor's
# lock is left in. Picking a large number out of the air instead would pin nothing, since the
# kernel could have handed it out.
sh -c 'exit 0' & dead_pid=$!
wait "$dead_pid" 2>/dev/null || true

claim 170 "$$"
claim 171 "$dead_pid"

# Run from inside the fixture repo rather than through `run`: which worktrees exist is a fact
# about the repository the script is called in, and every other case is indifferent to that.
out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == $'171\n172' ]]; } \
  && ok || no "an issue whose worktree holds a live conductor PID is withheld, one with a dead PID or no worktree is listed (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '171|172|'; live pid=$$, dead pid=$dead_pid)"

# 18. The other side of case 17's lock, on its own: a run that BAILED or was killed leaves its
# worktree and its lock behind, and the issue has to go back in the pool — a bail is exactly the
# state a later `/tdd <n>` resumes from, so an issue no live process holds staying claimed would
# make the lock a one-way door that only a human could open. Case 17 asserts this arm inside a
# three-issue stdout, where any one of its three arms failing reads the same; here the bailed
# run's issue is the ONLY issue in the fixture, so a reading that takes a stale lock for a live
# claim comes back "nothing to do" (exit 3, nothing on stdout) against this criterion alone
# (#170).
#
# The pid, the worktree and the empty `prs.json` are case 17's: `$dead_pid` is still the child
# this suite started and reaped, and `claim` registers the worktree the same way, because what a
# bailed run leaves on disk does not differ from what a killed one leaves.
fx="$(fixture bailed)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 173,
    "title": "a run that bailed before opening its draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

claim 173 "$dead_pid"

out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 0 ]] && [[ "$out" == 173 ]]; } \
  && ok || no "a bailed or killed run's issue — a dead conductor PID in its worktree's lock, no open PR — is listed again so a resume is still possible (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '173|'; dead pid=$dead_pid)"

# 19. The signal cases 17 and 18 pin is a term of this project, so the glossary is where a
# reader is told it exists: CONTEXT.md's **Solvable** entry is the one paragraph that
# enumerates what makes an issue veri's to take right now, and it named a single claim — an
# open PR saying `Closes #<n>`. Someone who finds only that there learns the wrong rule twice
# over: that an issue with no PR is free (it is not — a run claims it from its first step), and
# that the way to tell is to ask GitHub (it is not — the answer is on local disk). So the entry
# has to name the lock, `conductor.pid`, and say that it counts only while the process it names
# is alive, which is the half that keeps a bailed run's issue solvable (#170).
#
# The claim is read out of the **Solvable** entry ALONE rather than the whole document, for case
# 12's reason: the glossary has other entries a sentence about a lock file could land in —
# **Bail**, **Conductor**, **Ledger** — and prose parked in one of those would answer a
# file-wide grep while leaving the definition of *solvable* still saying an open PR is the only
# claim. The slice runs from the entry's own heading to the next bold heading, and is asserted
# non-empty before it is read, so an entry renamed or moved reads as a failure here rather than
# as greps over nothing finding nothing to complain about.
#
# The lock is matched as a fixed string because `conductor.pid` is the name a reader greps for
# and the one both scripts write; the liveness is matched loosely, because whether the writer
# says `kill -0` or "while that process is alive" is their sentence rather than this suite's —
# case 11's protocol on this same question.
context_md="CONTEXT.md"

# solvable_entry_slice — the **Solvable** entry of CONTEXT.md, from its own heading to the next
# bold one. Cases 19 and 33 both read that one slice, and the awk that cuts it lives here once:
# a renamed or moved heading then moves one program rather than two that can drift into reading
# two different parts of the glossary.
solvable_entry_slice() {
  awk '/^\*\*Solvable\*\*:/ { keep = 1; next } keep && /^\*\*/ { exit } keep' \
    "$REPO_ROOT/$context_md"
}

solvable_entry="$(solvable_entry_slice)"

# One claim, one miss, tagged — case 11's `doc_claims` for a slice already in hand rather than
# a file under $REPO_ROOT. What it collapses is the same thing: the separator and the
# accumulator are spelled once, so the three misses below cannot drift into being reported in
# three shapes. The grep arguments stay at the call site, where the difference between the
# literal name and the loosely-matched sentence is the point.
entry_claims() {  # entry_claims <tag> <grep argument…>
  local tag="$1"; shift
  grep -q "$@" <<<"$solvable_entry" || entry_missing="$entry_missing $tag"
}

entry_missing=""
if [[ -z "${solvable_entry// /}" ]]; then
  entry_missing="$entry_missing the-Solvable-entry-itself"
else
  entry_claims the-lock-by-name -F -e 'conductor.pid'
  entry_claims that-only-a-live-process-claims -iE \
    -e 'kill -0|alive|still running|live (conductor|process|run)'
fi

[[ -z "$entry_missing" ]] \
  && ok || no "$context_md's Solvable entry names the conductor PID lock, and a live holder, as what marks a run in flight (missing:$entry_missing)"

# 20. The other end of cases 17 and 18: something has to WRITE the lock they read. No script
# does — `issue-worktree.sh` exits before the conductor exists, and its own `$$` would name a
# process that is gone the moment it returns — so the writer is the conductor, and the
# conductor's whole program is `skills/tdd/SKILL.md`. A lock nothing writes makes this script's
# in-flight exclusion and `issue-worktree.sh`'s refusal both true of fixtures and of nothing
# else, which is the state this case exists to keep the run out of (#170).
#
# Read out of step 1's section alone, not the whole document, for case 12's reason: `#170` and
# `conductor.pid` are argued in this script's header and in CONTEXT.md, and SKILL.md quotes
# neither, but a file-wide grep would be one paste away from passing on an aside somewhere in a
# document thousands of lines long while step 1 — the only place early enough to claim the issue
# from the run's FIRST step — still said nothing. The slice runs from the `### 1.` heading to the
# next `### ` one and is asserted non-empty before it is read, so a renamed or moved step reads
# as a failure here rather than as greps over nothing finding nothing to complain about.
step1="$(awk '/^### 1\./ { keep = 1; next } keep && /^### / { exit } keep' "$REPO_ROOT/$procedure_doc")"

# Two probes, and the second is not a spelling preference. `$PPID` inside a tool call is the
# agent's own process, which lives as long as the run; `$$` is the shell of that one command,
# reaped before anyone reads the lock — a conductor told to write that claims its issue for
# microseconds and then hands the pid back to the kernel to reissue. The failure is silent at
# the writer and shows up as cases 17 and 18 passing over a feature nobody has, so the value is
# pinned here rather than left to the wording. The redirection is matched loosely around the
# variable (`> .tdd/conductor.pid`, quoted or not, spaced or not) because how the line is
# written is the author's; that it writes THAT pid THERE is this suite's.
step1_missing=""
if [[ -z "${step1// /}" ]]; then
  step1_missing="$step1_missing step-1-itself"
else
  grep -qE '> *"?\.tdd/conductor\.pid' <<<"$step1" \
    || step1_missing="$step1_missing the-write-into-the-lock"
  grep -qE '\$PPID[^>]*> *"?\.tdd/conductor\.pid' <<<"$step1" \
    || step1_missing="$step1_missing the-pid-that-outlives-one-command"
fi

[[ -z "$step1_missing" ]] \
  && ok || no "$procedure_doc step 1 tells the conductor to write its own long-lived pid (\$PPID, not \$\$) into .tdd/conductor.pid, so the lock cases 17 and 18 read is one a real run leaves (missing:$step1_missing)"

# 21. The branch a step's push puts on the remote is DURABILITY, not a claim, and the two must
# not be confused: #191 makes the conductor push after every green commit, so from a run's first
# step onwards `origin` carries `tdd/<n>-<slug>` for hours before any PR exists. What says an
# issue is somebody's is the open PR saying `Closes #<n>` (case 4) and the live conductor pid
# (case 17) — never the branch. A reading that took the branch for a claim would make every
# interrupted run's issue permanently untakeable: the pid dies with the process, but a pushed
# branch outlives it and only a human deleting a remote ref would put the issue back in the pool,
# which is the one-way door case 18 exists to keep shut.
#
# The fixture is case 1's — one open, labelled issue with `None.` under `## Blocked by` and the
# empty `prs.json` the helper seeds — plus exactly the state a pushed step leaves and nothing
# else: the run's worktree, its branch, and that branch on a real remote. No lock is written, so
# the branch is the ONLY thing separating this from case 1 and the assertion is about the branch
# alone. The remote is a bare repo pushed to for real rather than a faked `refs/remotes/origin/*`
# ref, because `git ls-remote` — what a reading would ask — answers the remote, not the cache;
# and the push is asserted to have landed before the criterion is, so a push that quietly failed
# reads as a broken fixture here instead of as this case passing over nothing.
fx="$(fixture pushed-branch)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 191,
    "title": "a run's commits live on one disk until the draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nThe conductor pushes the branch after each step's green commit.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

pushed_repo="$work/pushed"
pushed_remote="$work/pushed-remote.git"
mkdir -p "$pushed_repo"
git init -q -b main "$pushed_repo" >/dev/null 2>&1
git -C "$pushed_repo" -c user.name=veri -c user.email=veri@example.test \
  commit -q --allow-empty -m initial >/dev/null 2>&1
git init -q --bare "$pushed_remote" >/dev/null 2>&1
git -C "$pushed_repo" remote add origin "$pushed_remote"

pushed_wt="$pushed_repo/.tdd/wt/191"
git -C "$pushed_repo" worktree add -q -b tdd/191-slug "$pushed_wt" main >/dev/null 2>&1
git -C "$pushed_wt" push -q --set-upstream origin HEAD >/dev/null 2>&1

on_remote="$(git -C "$pushed_repo" ls-remote --heads origin tdd/191-slug 2>/dev/null)"

out="$(cd "$pushed_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ -n "$on_remote" ]] && [[ "$code" == 0 ]] && [[ "$out" == 191 ]]; } \
  && ok || no "a branch on the remote, with no open PR and no live conductor pid, leaves its issue takeable (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '191|'; ls-remote tdd/191-slug='$on_remote', want non-empty)"


# 22. Order is not "ascending by number" alone: a `bug`-labelled issue is taken ahead of every
# plain one, however much older the plain one is (#113). The thing that is BROKEN goes before
# the things that are merely wanted, and the /tdd loop gets that for free because it already
# takes the first line.
#
# Two issues per band, fed in so that neither band is in input order and the two bands
# interleave by number (#117 plain, #120 bug, #108 plain, #124 bug): the answer "120\n124\n
# 108\n117" is then the only string that says BOTH halves of the criterion at once. Today's
# plain `sorted(numbers)` prints "108\n117\n120\n124"; a sort that put bugs first but lost
# the ascending order inside a band prints "124\n120\n…"; a sort that read the input order
# prints it back. Each is a different string rather than a reorder that could pass by luck.
#
# Every one of the four is otherwise maximally takeable — open, opted in, `None.` under
# `## Blocked by`, and the helper's empty `prs.json` — so the ONLY thing this case varies is
# the `bug` label, and the only thing it can be observing is the order. `-u
# VERI_PRIORITY_LABEL` guarantees the band in front of this one is named by the DEFAULT
# rather than by whatever the calling shell exports: an operator steering a loop exports
# exactly that name, and `VERI_PRIORITY_LABEL=ready-for-agent` would put all four issues in
# the priority band and print them in plain ascending order.
fx="$(fixture bug-band)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 117,
    "title": "a capability somebody wants",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 120,
    "title": "a thing that is broken",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 108,
    "title": "an older capability somebody wants",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 124,
    "title": "a second thing that is broken",
    "labels": [{"name": "bug"}, {"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == $'120\n124\n108\n117' ]]; } \
  && ok || no "a bug-labelled issue is printed ahead of a lower-numbered plain one, each band ascending by number (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '120|124|108|117|')"

# 23. The band in FRONT of case 22's: `priority` says take this one sooner, and it beats `bug`
# the way `bug` beats plain (#113, folding in #215). It is the whole of veri's queue-level
# steering — `gh issue edit <n> --add-label priority` from a shell or a phone — so what it has
# to buy is exactly this: an issue jumping a lower-numbered BUG, which is already jumping every
# plain one. An issue carrying BOTH labels sorts in the priority band, because the bands are one
# sort key read left to right, not two independent questions.
#
# Three issues, fed in so no reading can pass by luck: #120 `bug`, #160 `priority`+`bug`,
# #150 `priority`, in that input order. The answer "150\n160\n120" says both halves at once —
# #150 ahead of the lower-numbered #120 is the priority band beating the bug band, and #160
# between them rather than last is the both-labelled issue landing in the priority band,
# ascending after #150. Today's bug-band-only key prints "120\n160\n150"; a key that put the
# both-labelled issue in the bug band prints "150\n120\n160"; the input order prints itself.
#
# Every one is otherwise maximally takeable — open, opted in, `None.` under `## Blocked by`,
# the helper's empty `prs.json` — so the only thing varying is the labels. `-u
# VERI_PRIORITY_LABEL` guarantees the label name is the DEFAULT rather than whatever the
# calling shell exports, which is the hermeticity the other tunables' cases already keep.
fx="$(fixture priority-band)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 120,
    "title": "a thing that is broken",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 160,
    "title": "a thing that is broken and wanted today",
    "labels": [{"name": "bug"}, {"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 150,
    "title": "a capability wanted today",
    "labels": [{"name": "priority"}, {"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == $'150\n160\n120' ]]; } \
  && ok || no "a priority-labelled issue is printed ahead of a lower-numbered bug, and one carrying both labels sorts in the priority band (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '150|160|120|')"

# 24. `priority` says take this one SOONER; it never says take this one AT ALL. The two labels
# answer different questions — `VERI_LABEL` is the human's explicit opt-in, `priority` only
# names a band in the print order — so an issue carrying the priority label and not the opt-in
# one is not solvable, and priority reorders the solvable set without ever enlarging it (#113).
# This is the case most likely to be got wrong, because the obvious wrong implementation is the
# tempting one: reading the priority label anywhere the opt-in label is read, or letting the
# band computation decide membership rather than order.
#
# #170 is fed in at its most takeable except for the one thing — open, `None.` under
# `## Blocked by`, no PR, and carrying `priority` — so the ONLY thing withholding it is the
# missing opt-in label. #180 is the opted-in control: it keeps stdout non-empty and the exit 0,
# isolating this case from the empty-result criterion, and it is PLAIN and higher-numbered, so
# an implementation that let `priority` opt an issue in prints "170\n180" — the miss shows up
# as an extra first line rather than a reorder that could be read two ways.
#
# `-u VERI_PRIORITY_LABEL` guarantees the label name is the DEFAULT rather than whatever the
# calling shell exports, the same hermeticity the other tunables' cases keep.
fx="$(fixture priority-without-opt-in)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 170,
    "title": "an unvetted idea somebody flagged as urgent",
    "labels": [{"name": "priority"}],
    "state": "OPEN",
    "body": "## What to build\n\nSomething, urgently.\n\n## Blocked by\n\nNone.\n"
  },
  {
    "number": 180,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "180" ]]; } \
  && ok || no "the priority label alone never opts an issue in (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '180|')"


# 25. Order never overrides the graph. Cases 22–24 pin where a `priority` or `bug` issue sorts;
# this one pins that sorting is ALL either label buys (#113). The four conditions run first and
# the sort runs on what survives, so a band is a position in the print order and never a way
# into it — the wrong implementation this catches is the one where the band computation decides
# membership, or where the sort is asked of every issue and the filter of only the plain ones.
#
# One fixture, the three ways an issue can be withheld, each carried by an issue that would
# otherwise sort FIRST: #190 `priority` blocked by the still-open #189, #191 `bug` claimed by an
# open PR saying `Closes #191`, #192 `priority` and CLOSED. Each is otherwise maximally takeable
# — opted in, and #191 and #192 name `None.` under `## Blocked by` — so the only thing
# withholding each is the one condition it fails. #189 is the blocker and carries no opt-in
# label, so it is not in the pool itself and cannot be mistaken for the answer. #195 is the
# opted-in plain control: it keeps stdout non-empty and the exit 0, isolating this case from the
# empty-result criterion, and it is the HIGHEST-numbered of the lot, so any issue that leaked
# through a band shows up ahead of it — the miss is an extra first line, not a reorder.
#
# `-u VERI_PRIORITY_LABEL` guarantees the label name is the DEFAULT rather than whatever the
# calling shell exports, the same hermeticity cases 23 and 24 keep.
fx="$(fixture band-never-enlarges)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 189,
    "title": "the open blocker",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 190,
    "title": "a capability wanted today, waiting on another",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#189\n"
  },
  {
    "number": 191,
    "title": "a thing that is broken, already in flight",
    "labels": [{"name": "ready-for-agent"}, {"name": "bug"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 192,
    "title": "a capability wanted today, already done",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "CLOSED",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 195,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Closes #191\n"
  }
]
JSON

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$code" == 0 ]] && [[ "$out" == "195" ]]; } \
  && ok || no "a priority or bug issue that is blocked, claimed or closed is still not printed (exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '195|')"


# 26. `VERI_PRIORITY_LABEL` names the band label, and it is read the way every other tunable
# here is read — but the one expansion that supplies a default cannot tell EMPTY from UNSET,
# so the two answers it owes are one criterion observed twice (#113). Set but empty is a
# misconfigured run, not a choice — a launcher writing `VERI_PRIORITY_LABEL="$some_unset_var"`
# is how it gets there — and an empty name matching every issue would put the whole solvable
# set in the priority band, which is the ordering equivalent of the failure case 10 prevents
# for the opt-in label. So it refuses in the same fail-closed shape: exit 2, veri's "no answer
# could be obtained", a diagnostic on stderr and nothing on stdout for a caller to read as a
# queue. Unset, on the same fixture, must still band on the default name `priority` — which is
# what says the refusal came from the emptiness rather than from the knob being consulted at
# all.
#
# The same two issues are fed in both times, so the only thing varying is the variable. #200
# carries `priority` and the opt-in label, #100 is plain and opted in and LOWER-numbered, so
# the default's answer is "200\n100" — the band visibly beating the number. That pair is also
# what tells the empty run's failure modes apart in the message: a script quietly falling back
# to the default prints "200\n100" and exits 0, and one reading the empty value as "matches
# everything" prints "100\n200" — both ascending-by-number bands of one — and exits 0 too.
# Either is visible against exit 2 with stdout empty.
#
# The empty run goes through `refused_run` rather than `label_run`: which stream carries what
# is half the criterion here, so the two must not be merged, and stdout's emptiness is asserted
# as well as stderr's content. The unset run keeps `label_run`'s `-u`, which guarantees the
# variable is ABSENT rather than merely unset by this shell.
fx="$(fixture priority-label-tunable)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 100,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 200,
    "title": "a capability wanted today",
    "labels": [{"name": "ready-for-agent"}, {"name": "priority"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON

refused_run "$fx" VERI_PRIORITY_LABEL=

label_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$refused_code" == 2 ]] \
  && [[ ! -s "$refused_out" ]] \
  && [[ -s "$refused_err" ]] \
  && [[ "$code" == 0 ]] && [[ "$out" == $'200\n100' ]]; } \
  && ok || no "VERI_PRIORITY_LABEL set to the empty string is refused with exit 2 and a diagnostic, while unset defaults to the priority label (set-but-empty: exit=$refused_code want 2, stdout='$(tr '\n' '|' < "$refused_out")' want empty, stderr='$(tr '\n' ' ' < "$refused_err")' want a diagnostic; unset: exit=$code want 0, stdout='$(tr '\n' '|' <<<"$out")' want '200|100|')"



# 27. The three bands are an addition to the order, not a replacement for it: a repository
# where NO issue carries either band label must get exactly the queue it got before #113 —
# plain ascending by number over the four conditions' survivors. That is the compatibility
# half of the change, and it is what says the band computation is inert when there is nothing
# to band rather than a second thing that can go wrong; the wrong implementations it catches
# are the one that groups the unlabelled issues into a band of its own and prints it out of
# turn, and the one that reorders whenever it sorts at all.
#
# The fixture is the whole selection layer with the labels taken away, so "unchanged" means
# unchanged about all four conditions and not just about two numbers: #208 and #210 are
# takeable and fed in out of order; #207 is claimed by an open PR saying `Closes #207`; #209
# is blocked by #212, which is open; #211 carries no opt-in label; #213 is opted in but
# CLOSED. None of the seven carries `priority` or `bug`. The survivors are #208 and #210, in
# that order.
#
# BYTE-identical is the criterion, so the comparison is against bytes on disk rather than a
# shell string: `$(…)` strips the trailing newline, and the final newline after the last
# number is part of what a caller reading this a line at a time depends on. `refused_run` is
# the one helper that keeps each stream in a file of its own — its name is about the case that
# first needed that, not about what it does — so it serves here, and `-u VERI_PRIORITY_LABEL`
# forwards through it exactly as it does through `label_run`, guaranteeing the band label is
# the default rather than whatever the calling shell exports.
fx="$(fixture no-band-labels)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 210,
    "title": "a capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 208,
    "title": "another capability veri may take",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 207,
    "title": "a capability already in flight",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 209,
    "title": "a capability waiting on another",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\n#212\n"
  },
  {
    "number": 211,
    "title": "an idea nobody has vetted for veri yet",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 212,
    "title": "the open blocker",
    "labels": [],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  },
  {
    "number": 213,
    "title": "a capability already done",
    "labels": [{"name": "ready-for-agent"}],
    "state": "CLOSED",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Closes #207\n"
  }
]
JSON

printf '208\n210\n' > "$work/no-band-labels.expected"

refused_run "$fx" -u VERI_PRIORITY_LABEL

{ [[ "$refused_code" == 0 ]] \
  && cmp -s "$refused_out" "$work/no-band-labels.expected"; } \
  && ok || no "with no issue carrying either band label the output is byte-identical to today's (exit=$refused_code want 0, stdout='$(tr '\n' '|' < "$refused_out")' want '208|210|')"


# 28. The order is only half of the steering; the other half is the loop SAYING it steered.
# A band jump is invisible in the loop's own report — `#150` on a line looks exactly like
# `#150` would have looked as the lowest number — so an operator who labelled #150 `priority`
# an hour ago cannot tell from the run whether the label was read, whether the label name was
# the one the run was configured with, or whether #150 simply came up next. The loop must
# therefore narrate the jump where it makes it: when the number it took is not the lowest one
# `solvable-issues.sh` printed, say so and name the band that did it — `#220 (priority) before
# #108`, `#120 (bug) before #117` (#113).
#
# The claim is read out of the exit-0 instruction alone, for case 12's reason: that bullet is
# where the loop takes the first number, so it is where the narration is owed, and a file-wide
# grep would go green on the words appearing in *Loop inputs* or in a guardrail and pin
# nothing. The awk slice runs from the `- **Exit 0:**` line to the `###` heading that ends the
# list, and the case asserts the slice is non-empty before asserting what is in it — an empty
# slice means the headings moved and the claim was never checked, which must read as a failure
# rather than as a pass.
#
# Three claims, matched loosely because the sentence is the writer's: the jump is described
# against a *lower-numbered* issue (spaces or hyphens between the two words), and both band
# names appear, since "which band did it" is unanswerable from a narration that only says the
# order was not by number. The variable name `VERI_PRIORITY_LABEL` is deliberately not what is
# matched — case 11 covers the knobs a launcher needs documented; this is about what one run
# tells the human reading it afterwards.
narration="$(loop_bullet '^- [*][*]Exit 0:' '^### ')"

{ [[ -n "$narration" ]] \
  && grep -qiE 'lower[ -]numbered' <<<"$narration" \
  && grep -qE 'priority' <<<"$narration" \
  && grep -qE 'bug' <<<"$narration"; } \
  && ok || no "the exit-0 instruction in $skill_doc says when it took an issue ahead of a lower-numbered one and which band did it (bullet='$(tr '\n' ' ' <<<"$narration")' want a non-empty slice naming a lower-numbered issue and both bands, priority and bug)"



# A `gh` stub that pages the way gh does: `paging_gh <dir>` writes <dir>/gh, which reads
# `--limit` (or `-L`, or `--limit=<n>`) into $limit — 30 when none is given — and then runs the
# `case` on "$1 $2" read from stdin, which answers each list with at most $limit items.
paging_gh() {  # paging_gh <dir> < <case body>
  mkdir -p "$1"
  { cat <<'STUB'
#!/bin/sh
limit=30
prev=""
for arg in "$@"; do
  case "$prev" in --limit|-L) limit="$arg" ;; esac
  case "$arg" in --limit=*) limit="${arg#--limit=}" ;; esac
  prev="$arg"
done
STUB
    cat; } > "$1/gh"
  chmod +x "$1/gh"
}

paged_run() {  # paged_run <dir of a paging_gh stub>; the real gh path, sets $out and $code
  out="$(env -u VERI_GH_JSON -u VERI_LABEL -u VERI_PRIORITY_LABEL PATH="$1:$PATH" \
         "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
}

# 29. `gh` does not return a repository's issues; it returns a PAGE of them — 30 by default,
# newest first, unless the caller says `--limit` (#244). On 2026-09-16 veri's own repo had 39
# open issues, and the 9 oldest were invisible to selection: #109 and #110 were opted in and
# unblocked, and no drain could ever take them. The VERI_GH_JSON fixtures hide that, because a
# fixture is complete by construction, so this case drives the real gh path against a stub that
# pages the way gh does: it answers `issue list` with the newest `--limit` issues (30 when no
# limit is given) and `pr list` with no PRs.
#
# Forty open issues, #101–#140. Only #101 — the OLDEST, so the one a 30-item page drops —
# carries `ready-for-agent`; every issue names no blocker and no PR claims any of them. So the
# script prints "101" only if it asked gh for more than the default page, and a script that
# took the default gets #111–#140, finds nothing opted in, and exits 3 with empty stdout.
pagedir="$work/paging-bin"
paging_gh "$pagedir" <<'STUB'
case "$1 $2" in
  "issue list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
issues = [
    {"number": n, "title": "issue %d" % n, "state": "OPEN",
     "labels": [{"name": "ready-for-agent"}] if n == 101 else [],
     "body": "## Blocked by\n\nNone.\n"}
    for n in range(140, 100, -1)
]
print(json.dumps(issues[:limit]))
' "$limit" ;;
  "pr list") echo '[]' ;;
esac
STUB

paged_run "$pagedir"

{ [[ "$code" == 0 && "$out" == "101" ]]; } \
  && ok || no "an opted-in, unblocked issue older than gh's default page of 30 is printed (40 open issues, only the oldest #101 opted in: exit=$code want 0, stdout='$out' want '101')"


# 30. The other half of the same page (#244): a blocker is read as closed when it is merely
# absent from the list, so an open blocker older than gh's newest 30 lets the issue it blocks be
# taken early — #118 was selectable while blocked by open #71. The same paging stub shape as the
# case above, with the roles moved: forty open issues, #101–#140, and only #140 — the NEWEST, so
# on every page — carries `ready-for-agent`, blocked by #101, the oldest and still open. A script
# that reads every issue sees #101 open and prints nothing (exit 3); one that took the default
# page never sees #101 and prints "140".
blockdir="$work/paging-blocker-bin"
paging_gh "$blockdir" <<'STUB'
case "$1 $2" in
  "issue list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
issues = [
    {"number": n, "title": "issue %d" % n, "state": "OPEN",
     "labels": [{"name": "ready-for-agent"}] if n == 140 else [],
     "body": "## Blocked by\n\n- #101\n" if n == 140 else "## Blocked by\n\nNone.\n"}
    for n in range(140, 100, -1)
]
print(json.dumps(issues[:limit]))
' "$limit" ;;
  "pr list") echo '[]' ;;
esac
STUB

paged_run "$blockdir"

{ [[ "$code" == 3 && -z "$out" ]]; } \
  && ok || no "an issue blocked by an open issue older than gh's default page of 30 is not printed (40 open issues, #140 opted in and blocked by the oldest #101: exit=$code want 3, stdout='$out' want '')"


# 31. The same page on the pull requests (#244): an open PR saying `Closes #<n>` is what claims an
# issue, and gh answers `pr list` with its newest 30 unless told `--limit`, so a claiming PR older
# than that is never read and its issue reads as free. The paging stub again, with PRs as the
# paged list: one issue, #7, open, opted in and unblocked, and forty open PRs, newest first,
# of which only the OLDEST — the one a 30-item page drops — says `Closes #7`. A script that reads
# every open PR sees the claim and prints nothing (exit 3); one that took the default page prints
# "7".
prpagedir="$work/paging-prs-bin"
paging_gh "$prpagedir" <<'STUB'
case "$1 $2" in
  "issue list")
    printf '%s\n' '[{"number": 7, "title": "issue 7", "state": "OPEN", "labels": [{"name": "ready-for-agent"}], "body": "## Blocked by\n\nNone.\n"}]' ;;
  "pr list")
    python3 -c '
import json, sys
limit = int(sys.argv[1])
prs = [
    {"state": "OPEN", "body": "Closes #7" if i == 39 else "Closes #%d" % (1000 + i)}
    for i in range(40)
]
print(json.dumps(prs[:limit]))
' "$limit" ;;
esac
STUB

paged_run "$prpagedir"

{ [[ "$code" == 3 && -z "$out" ]]; } \
  && ok || no "an open PR older than gh's default page of 30 saying Closes #<n> still claims its issue (40 open PRs, only the oldest says Closes #7: exit=$code want 3, stdout='$out' want '')"


# 32. The claim that crosses machines, on its own: an open PR saying `Closes #<n>` withholds its
# issue whether or not any conductor pid answers. The pid lock cases 17 and 18 read is local to
# one disk, so a bailed run whose lock names a reaped process — the very state case 18 puts back
# in the pool — must STAY out of it once its draft PR is open, or a scope drain on this machine
# or on another re-takes the issue a human has been asked to look at (#195).
#
# Case 4 pins the PR claim with no lock on disk, and case 18 pins the dead lock with no PR; this
# is the pair together, which is the state #195 leaves behind: the bailed run's worktree, its lock
# holding `$dead_pid` — case 17's reaped child, seeded through the same `claim` helper into the
# same throwaway repository, because what a bailed run leaves on disk is what a killed one leaves
# — and an open PR saying `Closes #175`. #175 is the only issue in the fixture, so a reading that
# let the dead pid decide the question prints "175" and exits 0, and the criterion is the whole of
# stdout rather than one arm of a longer list.
fx="$(fixture claimed-by-pr-dead-pid)"
cat > "$fx/issues.json" <<'JSON'
[
  {
    "number": 175,
    "title": "a run that bailed after opening its draft PR",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## Blocked by\n\nNone.\n"
  }
]
JSON
cat > "$fx/prs.json" <<'JSON'
[
  {
    "state": "OPEN",
    "body": "Draft PR opened by a /tdd run that bailed.\n\nCloses #175\n"
  }
]
JSON

claim 175 "$dead_pid"

out="$(cd "$flight_repo" && VERI_GH_JSON="$fx" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?

{ [[ "$code" == 3 ]] && [[ -z "$out" ]]; } \
  && ok || no "an issue an open PR Closes stays out of the pool though its conductor pid is dead (exit=$code want 3, stdout='$(tr '\n' '|' <<<"$out")' want ''; dead pid=$dead_pid)"


# 33. The two signals cases 4, 17, 18 and 32 pin behaviourally are now a division of labour, and
# a division of labour that lives only in the code is one the next reader re-derives from
# whichever branch they happen to open: the open PR saying `Closes #<n>` is the claim EVERY
# machine can see, and the `conductor.pid` lock is only the guard on ONE machine's worktree —
# what keeps a second conductor out of a live run's tree, where *Resume*'s `git reset --hard`
# would throw the running leaf's uncommitted work away (#170). Case 32 makes the dead lock stop
# freeing the issue; this case makes the documents say why, because the two sentences they
# carry today say the opposite. CONTEXT.md's **Solvable** entry calls the PR the *late* mark and
# the lock the *early* one, and this script's header argues that "a pid that no longer answers
# reads as free … which is what a bailed run needs" — the exact reading #195 reverses, and the
# one a reader repairing a red case 32 would restore if nothing here stopped them.
#
# Read out of the **Solvable** entry and out of this script's OWN header comment, each sliced
# and asserted non-empty first, for case 19's reason: the glossary has other entries a sentence
# about a lock could land in, and this script has comments further down that already name a
# worktree (`solvable-issues.sh:130, 189`), so a file-wide grep would pass on prose nowhere near
# the paragraphs that define the two signals. The header slice runs from the line after the
# shebang to the first line that is not a comment, split into records at its blank `#` lines,
# because a fact is carried by ONE paragraph: "a label is visible across machines" and "an open
# PR is not the only claim" are two paragraphs apart today, and a passage-wide match would read
# them as the sentence this case is asking for.
#
# The third claim is a pointer rather than a reading: the decision itself goes in a new ADR, and
# a suite under this directory may not open that tree — the development lane never puts the
# documentation lane's prose on every leaf's critical path (#143, no-docs-reads.test.sh), and an
# ADR's own text is `docs/tests/docs-gap-adr.test.sh`'s subject for exactly that reason (#137).
# What IS this lane's is that both documents cite the record, so a reader who finds the rule
# also finds where the three rejected options are argued.
#
# Every regex is loose on wording and literal only on the names a reader greps for, case 19's
# protocol: whether the author writes "every machine", "across machines" or "cross-machine" is
# their sentence, and that the record carries the claim is this suite's.
CLAIM_PR='closes #|pull request|open pr|draft pr'
CLAIM_ANY_MACHINE='every machine|any machine|other machine|another machine|all machines|across machines|cross-machine|machine-independent'
CLAIM_WORD='claim'
CLAIM_LOCK='conductor\.pid|pid lock|the lock|the pid'
CLAIM_WORKTREE='worktree'
CLAIM_GUARD='guard'
CLAIM_LOCAL='same[- ]machine|one machine|machine-local|local'
CLAIM_ADR='adr[ -]?[0-9]{4}'

# says_all <records> <regex>… — true when SOME ONE record of <records> matches every regex. A
# fact split across two records is not a statement, it is two sentences that happen to share a
# word, which is why the regexes are asked of a record rather than of the passage. The records
# reach here already case-folded, so the regexes are written in lower case once.
says_all() {
  local text="$1"; shift
  local line re
  while IFS= read -r line; do
    for re in "$@"; do
      [[ "$line" =~ $re ]] || continue 2
    done
    return 0
  done <<<"$text"
  return 1
}

# claim_says <passage> <tag> <records> <regex>… — one fact one passage owes, recorded as
# `<passage>:<tag>` when no record of it carries the fact. The accumulator is spelled once here
# so the six misses below cannot drift into being reported in six shapes — case 11's `doc_claims`
# for passages already in hand.
claim_says() {
  local passage="$1" tag="$2" text="$3"; shift 3
  says_all "$text" "$@" || claim_missing="$claim_missing $passage:$tag"
}

# The **Solvable** entry as one folded record, and this script's header as one record per
# paragraph. Both lower-cased on the way out, so `Closes #<n>` and `closes #7` are one string to
# every regex above.
claim_entry="$(solvable_entry_slice | tr '\n' ' ' | tr '[:upper:]' '[:lower:]')"
claim_header="$(awk 'NR == 1 { next }
                     !/^#/ { exit }
                     /^#[[:space:]]*$/ { if (rec != "") print rec; rec = ""; next }
                     { line = $0; sub(/^#[[:space:]]?/, "", line)
                       rec = (rec == "" ? line : rec " " line) }
                     END { if (rec != "") print rec }' "$SOLVABLE" | tr '[:upper:]' '[:lower:]')"

# claim_passage <passage> <empty-tag> <records> — the three facts a passage owes, asked of its
# records. The two passages owe the SAME three, which is the point of the case: a division of
# labour recorded in one document and not the other is still one the next reader re-derives. So
# the facts are spelled once here rather than once per passage, where a regex list added to the
# first and forgotten on the second would leave the case green over exactly that drift. An empty
# slice is the passage's own miss, reported before any regex is asked of nothing.
claim_passage() {
  local passage="$1" empty_tag="$2" text="$3"
  if [[ -z "${text// /}" ]]; then
    claim_missing="$claim_missing $passage:$empty_tag"
    return
  fi
  claim_says "$passage" the-open-PR-as-the-claim-every-machine-sees \
    "$text" "$CLAIM_PR" "$CLAIM_ANY_MACHINE" "$CLAIM_WORD"
  claim_says "$passage" the-lock-as-one-machines-worktree-guard \
    "$text" "$CLAIM_LOCK" "$CLAIM_WORKTREE" "$CLAIM_GUARD" "$CLAIM_LOCAL"
  claim_says "$passage" the-ADR-recording-the-decision "$text" "$CLAIM_ADR"
}

claim_missing=""
claim_passage "$context_md" the-Solvable-entry-itself "$claim_entry"
claim_passage solvable-issues.sh the-header-comment-itself "$claim_header"

[[ -z "$claim_missing" ]] \
  && ok || no "$context_md's Solvable entry and solvable-issues.sh's header say an open PR is the claim every machine sees and the conductor.pid lock is only that machine's worktree guard, each citing the ADR that records it (missing:$claim_missing)"


echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
