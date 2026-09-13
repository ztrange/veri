#!/usr/bin/env bash
# Unit tests for docs/docs-owed.sh — the script that says what the committed walkthrough
# is behind on. Zero-dependency plain-shell asserts, same idiom as docs-guard-filter.test.sh.
#
# Why this exists (issue #125): the page is no longer made to keep up with the code at
# merge time. The build carries a script line no commentary chunk covers as debt instead
# of refusing to build, and `make merge-gates` owes nothing for a change under skills/ —
# so the lag is real, deliberate, and until this script nothing reports it. This is the
# report: one line per thing the committed page is behind on, so the docs pool can be fed
# from a fact rather than from somebody noticing.
#
# Contract under test:
#   docs/docs-owed.sh, run at the root of the repository, prints one line per item of
#   debt — a script line no commentary chunk covers, a script whose last commit is newer
#   than the page's, a tag the capability index does not list — and exits 0. Over a tree
#   the page is current with it prints nothing and exits 3, the code every veri script
#   uses for nothing to do (CLAUDE.md: exit codes are the API).
#
# Where this suite lives, and why it is not under docs/tests/ beside the other two docs
# suites: `make docs-test` names its suites one recipe line each, so a new file there is
# run by nothing until the Makefile is edited too, while `make test` — the command veri's
# own preflight detects, and the only gate CI has run since docs-check left it on
# 2026-09-11 — globs skills/tdd/scripts/tests/*.test.sh and picks a new suite up by
# existing. It is not the first suite here whose subject sits outside skills/:
# workflow-timeouts.test.sh reads .github/workflows/ci.yml, and docs-guard-filter.test.sh
# runs a docs suite. It costs `make test` one copy of the tree and one sandboxed page
# build — ~2 s measured, against the ~140 s the whole guard suite takes, because the page
# is built once for the case rather than once per case.
#
# Run: scripts/tests/docs-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
SUBJECT="docs/docs-owed.sh"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The three debts the case plants, named once here, by the string the list has to carry
# for each: the script that is owed prose, the script the page is behind, and the tag the
# index never saw. Not a format — where each one appears on its line, and what sits beside
# it, is the implementer's to choose; that it is nameable is not.
UNCOVERED=classify-bail.sh
STALE=refactor-budget.sh
STALE_PATH=skills/tdd/scripts/refactor-budget.sh
TAG=v9.9

# report <name> — close a case whose probes collected into the `problems` array: an empty
# array is a pass, otherwise one FAIL line for the case and one indented line per problem,
# so the output says which half of the contract broke rather than just that the case did.
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

# flat <text> — one line of it, for a failure message. Newlines become slashes so a list
# that came back wrong is still readable inside an indented problem line.
flat() { printf '%s' "$1" | tr '\n' '/'; }

# repo — a disposable copy of this tree as a repository of its own, with a page that is
# current with it: everything committed once, the page built ON TOP of that history and
# committed second. Built inside the sandbox rather than copied from here because the
# committed page carries what git said at build time — the real repo's tags, the real
# repo's blame — and a page answering for another repository's history would be behind
# this one from its first breath, which is the very thing the case then plants on purpose.
#
# The build's own stdout is dropped and its stderr kept out of the way: this tree owes no
# commentary, so it has nothing to say, and a build that did would show up as debt the
# clean half of the case then reports.
repo() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  cp -R "$ROOT/docs" "$d/docs"
  cp -R "$ROOT/skills" "$d/skills"
  cp "$ROOT/Makefile" "$d/"
  rm -rf "$d/docs/wt/__pycache__"
  git -C "$d" -c init.defaultBranch=main init -q
  git -C "$d" config user.email veri@example.invalid
  git -C "$d" config user.name veri
  git -C "$d" config commit.gpgsign false
  git -C "$d" add -A
  git -C "$d" commit -qm 'feat: the tree (#1)'
  ( cd "$d" && python3 docs/build-walkthrough.py >/dev/null 2>&1 )
  git -C "$d" add -A
  git -C "$d" commit -qm 'docs: the page this tree builds (#1)' --allow-empty
  printf '%s' "$d"
}

# owed <dir> — run the subject at the root of that repository and publish what it said:
# `code`, `out` and `err`, read by the probes where they stand, the same protocol
# docs-guard-filter.test.sh uses for its runs. Run from the tree's own root, and from the
# copy inside it, because a script that finds the repository from its own path must find
# THAT repository and not this one.
owed() {
  out="$(cd "$1" && "./$SUBJECT" 2>"$WORK/err.txt")" && code=0 || code=$?
  err="$(cat "$WORK/err.txt" 2>/dev/null)"
}

# 1. The contract above, and both of its halves in one case, because neither is worth
#    anything without the other: a script that exits 3 and prints nothing whatever the
#    tree looks like passes the empty half, and one that prints its three lines
#    unconditionally passes the listing half. Only the two together say the list is a
#    reading of the repository.
#
#    One tree, read twice — clean first, then with one debt of each kind planted on top —
#    so the second reading is the first tree plus exactly what was planted, and the page
#    the debt is measured against is the same page both times.
#
#    Each debt is planted so that only ONE of the three rules can find it, which is what
#    makes the three names below evidence that all three rules ran:
#      * moving one chunk's start off the lines it claimed leaves classify-bail.sh L12–13
#        claimed by nobody WITHOUT touching the script, so its last commit is still the
#        page's and the blame rule has nothing to say about it. (The same sed
#        docs/tests/build-guards.test.sh plants its interior-gap case with.)
#      * rewriting line 2 of refactor-budget.sh in place keeps the file's line count, so
#        the coverage rule has nothing to say about it, and lands it in a commit after the
#        page's.
#      * the tag is cut last, so the committed index was built before it existed.
name="docs/docs-owed.sh lists the page's debt one item per line, and exits 3 with nothing on stdout when there is none"
problems=()
d="$(repo)"

owed "$d"
[[ "$code" == 3 ]] ||
  problems+=("want exit 3 — nothing to do — from $SUBJECT over the tree its page was just built from; got $code: $(flat "$out$err")")
[[ -z "$out" ]] ||
  problems+=("want nothing on stdout when there is no debt — whoever runs this reads the list, and an empty list is no lines at all; got: $(flat "$out")")

( cd "$d" && sed -i.bak 's/lines=(12, 18)/lines=(14, 18)/' docs/wt/commentary.py && rm -f docs/wt/commentary.py.bak )
grep -q 'lines=(14, 18)' "$d/docs/wt/commentary.py" ||
  problems+=("the coverage debt did not land: no chunk claiming lines=(12, 18) in docs/wt/commentary.py to move off $UNCOVERED L12–13")
git -C "$d" commit -qam 'docs: move a chunk off the lines it claimed (#2)'

( cd "$d" && sed -i.bak '2s|.*|# refactor-budget.sh — rewritten in place, same line count|' "$STALE_PATH" && rm -f "$STALE_PATH.bak" )
git -C "$d" commit -qam "fix: rewrite a line of $STALE after the page was built (#3)"
[[ "$(git -C "$d" log -1 --format=%H -- "$STALE_PATH")" != "$(git -C "$d" log -1 --format=%H -- docs/walkthrough.html)" ]] ||
  problems+=("the blame debt did not land: $STALE_PATH is still answered for by the commit the page is")

git -C "$d" tag -a "$TAG" -m 'a capability the committed index does not list'

owed "$d"
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from $SUBJECT over a tree with debt — a list is an answer, not a failure; got $code: $(flat "$out$err")")

for want in "$UNCOVERED:a script line no commentary chunk covers" \
            "$STALE:a script whose last commit is newer than the page's" \
            "$TAG:a tag the capability index does not list"; do
  tok="${want%%:*}"; why="${want#*:}"
  printf '%s\n' "$out" | grep -Fq -- "$tok" ||
    problems+=("want a line naming $tok — $why; got: $(flat "$out")")
done

# One item per line, pinned from both ends: three debts must occupy at least three lines,
# and no two of them may share one. A single paragraph naming all three satisfies every
# probe above and is not a list — nothing downstream can turn it into issue body bullets
# or count what is outstanding.
for pair in "$UNCOVERED $STALE" "$UNCOVERED $TAG" "$STALE $TAG"; do
  a="${pair%% *}"; b="${pair##* }"
  printf '%s\n' "$out" | grep -F -- "$a" | grep -Fq -- "$b" &&
    problems+=("want one item per line — $a and $b are two debts sharing a line: $(flat "$(printf '%s\n' "$out" | grep -F -- "$a" | grep -F -- "$b")")")
done
got_lines="$(printf '%s\n' "$out" | grep -c '[^[:space:]]')"
(( got_lines >= 3 )) ||
  problems+=("want at least one line per item — three debts were planted, so at least three lines; got $got_lines: $(flat "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
