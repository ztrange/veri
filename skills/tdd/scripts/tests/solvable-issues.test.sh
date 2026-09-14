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
#!/usr/bin/env bash
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
# The two streams go to separate files rather than through the `label_run` helper, which drops
# stderr: which stream carries what IS the criterion here, so they must not be merged, and
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

refused_out="$work/empty-label.out" refused_err="$work/empty-label.err"
env VERI_LABEL= VERI_GH_JSON="$fx" "$SOLVABLE" >"$refused_out" 2>"$refused_err" \
  && refused_code=0 || refused_code=$?

{ [[ "$refused_code" == 2 ]] \
  && [[ ! -s "$refused_out" ]] \
  && [[ -s "$refused_err" ]]; } \
  && ok || no "VERI_LABEL set to the empty string is refused with exit 2 and a diagnostic on stderr, never treated as any label (exit=$refused_code want 2, stdout='$(tr '\n' '|' < "$refused_out")' want empty, stderr='$(tr '\n' ' ' < "$refused_err")' want a diagnostic)"

# The document that carries the loop procedure, relative to $REPO_ROOT. Both of the two cases
# below read it — case 11 for the knob it must document, case 12 for one bullet of it — so it
# is spelled once here rather than in each: since #105 the loop is a section of the `/tdd`
# skill, and a move like that one should have a single line to edit in this suite.
skill_doc="skills/tdd/SKILL.md"

# 11. A knob nobody is told about is not a parameter, it is a secret, so the three documents a
# human reads before launching a loop must carry it: the loop's own procedure
# (`skills/tdd/SKILL.md`, which is where `--repo` and `VERI_MAX_ISSUES` are already
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
# passes on `VERI_LABEL` appearing ANYWHERE in SKILL.md, and it appears in the Inputs section,
# so a file-wide grep here would be green against a bullet that still said `ready-for-agent`
# and pin nothing. The awk slice runs from the `- **Exit 3:**` line to the `- **Exit 0:**` that
# ends it, and the case asserts the slice is non-empty before asserting what is in it — an
# empty slice means the headings moved and the claim was never checked, which must read as a
# failure rather than as a pass.
skill="$REPO_ROOT/$skill_doc"
exit3="$(awk '/^- \*\*Exit 3:/{keep = 1} /^- \*\*Exit 0:/{keep = 0} keep' "$skill")"

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
solvable_entry="$(awk '/^\*\*Solvable\*\*:/ { keep = 1; next } keep && /^\*\*/ { exit } keep' \
  "$REPO_ROOT/$context_md")"

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
  && ok || no "CONTEXT.md's Solvable entry names the conductor PID lock, and a live holder, as what marks a run in flight (missing:$entry_missing)"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
