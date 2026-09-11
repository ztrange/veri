#!/usr/bin/env bash
# Unit tests for scripts/solvable-issues.sh — rung 2's selection layer. Given a repo's
# issues and open PRs, print the numbers of the issues veri may take RIGHT NOW, one per
# line, lowest first, and exit 0; print nothing and exit 3 when there are none.
#
# Contract under test (issue #41):
#   solvable-issues.sh [--repo owner/name]
#   VERI_GH_JSON=<dir>   read <dir>/issues.json and <dir>/prs.json instead of shelling out
#                        to gh. That override is the whole reason this suite needs no
#                        network: the fixtures carry the exact shape of
#                          gh issue list --json number,title,labels,body,state
#                          gh pr list    --json body,state
#
# Run: scripts/tests/solvable-issues.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SOLVABLE="$HERE/../solvable-issues.sh"
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
run() {  # run <fixture-dir>; sets $out and $code
  out="$(VERI_GH_JSON="$1" "$SOLVABLE" 2>/dev/null)" && code=0 || code=$?
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
    "title": "the /solve-issues loop skill",
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
    "title": "the /solve-issues loop skill",
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
    "title": "the /solve-issues loop skill",
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
    "body": "Draft PR opened by a /solve-issue run.\n\nCloses #53\n"
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
    "title": "the /solve-issues loop skill",
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
    "title": "the /solve-issues loop skill",
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

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
