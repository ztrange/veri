#!/usr/bin/env bash
# Unit tests for scripts/parallel-conductors.sh — rung 3's selection layer. Run from a target
# repo's primary checkout, it launches up to VERI_PARALLEL supervised conductors at once over
# the issues solvable-issues.sh prints, and reports one line per issue it launched (#102).
#
# Contract under test (issue #102):
#   parallel-conductors.sh [--repo owner/name] [--continue-on-bail]
#   VERI_PARALLEL=<n>    conductors running at once, default 1. A whole number ≥ 1; anything
#                        else, set-but-empty included, is exit 2 before anything is launched,
#                        because N conductors are N concurrent `claude -p` sessions, billed as
#                        such — a value the script cannot read is never guessed into a spend.
#   VERI_GH_JSON=<dir>   passed through to solvable-issues.sh, so the solvable set is a
#                        fixture and no case reaches GitHub.
#   CLAUDE_BIN=<path>    passed through to every conductor: here a stub that records that it
#                        ran, which is what "a conductor was launched" means to these cases.
#
# Run: scripts/tests/parallel-conductors.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PARALLEL="$HERE/../parallel-conductors.sh"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
ok() { pass=$((pass + 1)); }
no() { fail=$((fail + 1)); echo "FAIL - $1"; }

# The target repo every case launches from: a fresh repository with one commit, standing in for
# the primary checkout of a repo that has never seen veri. The suite's cwd from here down, for
# the reason solvable-issues.test.sh gives for its own: a claim lock under THIS repository's
# `.tdd/wt/<n>` must never answer a question a case asked of its fixture.
target="$work/target"
git init -q -b main "$target" >/dev/null 2>&1
git -C "$target" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init >/dev/null 2>&1
cd "$target" || exit 2

# The solvable set: one open, opted-in, unblocked, unclaimed issue, so a launcher that ignored
# a bad VERI_PARALLEL would have something to launch.
gh_json="$work/gh"
mkdir -p "$gh_json"
printf '[]\n' > "$gh_json/prs.json"
cat > "$gh_json/issues.json" <<'JSON'
[
  {
    "number": 7,
    "title": "a solvable issue",
    "labels": [{"name": "ready-for-agent"}],
    "state": "OPEN",
    "body": "## What to build\n\nSomething.\n\n## Blocked by\n\nNone.\n"
  }
]
JSON

# The stub conductor: any launch that got as far as the model leaves a line in $launched.
launched="$work/launched"
stub="$work/claude"
printf '#!/bin/sh\necho "$*" >> "%s"\n' "$launched" > "$stub"
chmod +x "$stub"

# 1. VERI_PARALLEL that is not a whole number ≥ 1 — zero, a word, set-but-empty — is exit 2
# and launches nothing: the stub never ran, and the launcher wrote no `.tdd/conductor-<n>.*`
# file in the target. The three values are the criterion's three shapes of "not a whole number
# ≥ 1", observed as one case; every one that misbehaves is named in the single FAIL line.
bad=""
for value in 0 two ''; do
  rm -f "$launched"
  env -u VERI_LABEL -u VERI_PRIORITY_LABEL -u VERI_MAX_ISSUES \
    VERI_PARALLEL="$value" VERI_GH_JSON="$gh_json" CLAUDE_BIN="$stub" \
    "$PARALLEL" >/dev/null 2>&1 && code=0 || code=$?
  conductor_files="$(ls -d .tdd/conductor-* 2>/dev/null)"
  if [[ "$code" != 2 || -e "$launched" || -n "$conductor_files" ]]; then
    bad+=" [VERI_PARALLEL='$value': exit=$code want 2, stub ran: $([[ -e "$launched" ]] && echo yes || echo no), conductor files: '${conductor_files}']"
  fi
done

[[ -z "$bad" ]] \
  && ok || no "VERI_PARALLEL not a whole number >= 1 (0, a word, set-but-empty) is exit 2 with no conductor launched ($bad )"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
