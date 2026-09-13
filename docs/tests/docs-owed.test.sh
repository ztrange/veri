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
#   Given `--file` it also carries that list into the `ready-for-agent:docs` pool, as ONE
#   issue titled `Docs: catch the walkthrough up to <sha>`, edited again on a later run
#   rather than opened a second time. Both sides of that are injected: the pool it reads
#   through VERI_GH_JSON, the calls it makes through a stub `gh` on PATH.
#
# Where this suite lives: under docs/tests/, run by `make docs-test`, and not under `make
# test`. It started under `make test` for the auto-discovery `make test`'s glob gives, and
# cost every veri leaf ~13 s on every run of the suite to defend a docs tool; the docs are
# not functional and are brought up to date on their own cadence (ADR 0016), so nothing
# about them rides in veri's own development cycle. `make docs-test` names its suites one
# recipe line each — a new docs suite is run by nothing until it has one — and `make
# merge-gates` runs that target for any change under docs/tests/. It costs one copy of the
# tree per case and one sandboxed page build per case plus one per run of the subject,
# ~13 s measured.
#
# Run: docs/tests/docs-owed.test.sh
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
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

# ── --file: the debt filed as the one issue the docs pool drains ─────────────────
#
# The list alone still needs somebody to run it and read it. `--file` is what closes that
# loop: the same list, carried into the `ready-for-agent:docs` pool as ONE issue titled
# `Docs: catch the walkthrough up to <sha>`, re-edited on every later run rather than
# opened again — a pool that grew one issue per merge would be a worse report than no
# report, since draining it would mean reading N copies of the same debt.
#
# Two sources, two overrides, both already idioms here: what gh KNOWS is read through
# VERI_GH_JSON (the directory of fixtures solvable-issues.sh reads `issues.json` from, with
# the shape of `gh issue list --json number,title,state,labels`), and what gh is ASKED TO DO
# is caught by a stub `gh` on PATH (as tick-issue-criterion.test.sh does), which records the
# invocation instead of performing it. Between them the case needs no network and no repo.

# The stub: one line naming each invocation, then its arguments one per line, so a title
# with spaces in it survives to be read back. Any --body/--body-file, in either spelling,
# is resolved to its text in $GH_BODY — what the issue would actually say. `issue create`
# answers with a URL, since that is what gh prints and a caller may read it.
STUB="$WORK/bin"
mkdir -p "$STUB"
cat > "$STUB/gh" <<'STUB'
#!/usr/bin/env bash
{ printf '+++ %s %s\n' "${1:-}" "${2:-}"; printf '%s\n' "$@"; } >> "$GH_LOG"
prev=""
for a in "$@"; do
  case "$a" in
    --body=*)      printf '%s\n' "${a#--body=}" >> "$GH_BODY" ;;
    --body-file=*) cat "${a#--body-file=}"      >> "$GH_BODY" ;;
  esac
  case "$prev" in
    --body)      printf '%s\n' "$a" >> "$GH_BODY" ;;
    --body-file) cat "$a"           >> "$GH_BODY" ;;
  esac
  prev="$a"
done
[[ "${1:-}" == issue && "${2:-}" == create ]] && echo "https://github.com/veri/veri/issues/77"
exit 0
STUB
chmod +x "$STUB/gh"

# file_run <repo-dir> <fixture-dir> <name> — the subject with --file, over that repository,
# reading that pool and writing to the stub. Publishes `code` beside `log` and `body`: the
# record of what it asked gh to do, and the text it would have put in the issue.
file_run() {
  log="$WORK/gh.$3.log"; body="$WORK/gh.$3.body"
  : > "$log"; : > "$body"
  ( cd "$1" && env PATH="$STUB:$PATH" GH_LOG="$log" GH_BODY="$body" VERI_GH_JSON="$2" \
      "./$SUBJECT" --file >/dev/null 2>&1 ) && code=0 || code=$?
}

# body_carries_list <what> — every item of `list` appears in the `body` the last file_run
# captured, one problem per item that does not. Both runs owe this, and for the same
# reason: what the pool holds has to be the debt as it stands, so an issue opened with the
# list and then edited to something else is as broken as one opened empty. <what> is the
# only thing that differs between the two, and it is there so a failure says which run's
# body came back short. Reads `list`, `body` and `problems` where they stand, the protocol
# the rest of this file already uses.
body_carries_list() {
  while IFS= read -r item; do
    [ -n "$item" ] || continue
    grep -Fq -- "$item" "$body" ||
      problems+=("want the $1 to be the list — it is missing '$item'; got: $(flat "$(cat "$body")")")
  done <<< "$list"
}

# 2. `--file` over a tree with debt and an empty pool opens exactly one issue — in the docs
#    pool, titled for the tree's own sha, carrying the list as its body — and over the same
#    tree with that issue already open edits it instead of opening a second.
#
#    One debt is enough here and the tag is the cheapest of the three: cutting it needs no
#    edit, no commit and no rebuild, so what the case pays for is the filing, not the
#    planting. The tree's HEAD does not move between the two runs, so the second run is the
#    first one repeated — which is exactly the run that must not open a second issue.
name="docs/docs-owed.sh --file opens one ready-for-agent:docs issue titled for the tree's sha, and edits that one on a later run"
problems=()
d="$(repo)"
git -C "$d" tag -a "$TAG" -m 'a capability the committed index does not list'
head_sha="$(git -C "$d" rev-parse HEAD)"

# The list itself, from the same tree, unfiled: what the issue body has to carry. Read from
# the subject rather than spelled out here so the body is pinned to be THE list and not a
# second rendering of it that could drift from the one a human reads.
list="$(cd "$d" && "./$SUBJECT" 2>/dev/null)"
[ -n "$list" ] ||
  problems+=("the case is vacuous: $SUBJECT reports no debt over a tree with $TAG cut after its page was built")

fx="$WORK/pool.empty"; mkdir -p "$fx"
printf '[]\n' > "$fx/issues.json"
file_run "$d" "$fx" create
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from $SUBJECT --file over a tree with debt and an empty docs pool; got $code")

created="$(grep -c '^+++ issue create$' "$log")"
[[ "$created" == 1 ]] ||
  problems+=("want exactly one \`gh issue create\` when the pool holds no such issue; got $created: $(flat "$(cat "$log")")")

grep -Fq 'ready-for-agent:docs' "$log" ||
  problems+=("want the issue opened in the ready-for-agent:docs pool — nothing drains it otherwise; got: $(flat "$(cat "$log")")")

# The title, read back from whichever argument carried it. `<sha>` is the tree the debt was
# measured over, so it must be HEAD's — abbreviated or whole, the implementer's call, but a
# prefix of it and long enough to name a commit.
title_line="$(grep -F 'Docs: catch the walkthrough up to' "$log" | head -1)"
sha="${title_line##*catch the walkthrough up to }"
if [[ -z "$title_line" ]]; then
  problems+=("want the issue titled 'Docs: catch the walkthrough up to <sha>'; nothing in the call says so: $(flat "$(cat "$log")")")
elif [[ "${#sha}" -lt 7 || "$head_sha" != "$sha"* ]]; then
  problems+=("want <sha> in the title to be the sha the debt was read at, $head_sha; got '$sha'")
fi

body_carries_list "issue body"

# The later run: the same tree, the same debt, and now the issue the first run opened is in
# the pool. The one that is already open is the one to edit.
filed_title="${sha:+Docs: catch the walkthrough up to $sha}"
filed_title="${filed_title:-Docs: catch the walkthrough up to $head_sha}"
fx="$WORK/pool.open"; mkdir -p "$fx"
cat > "$fx/issues.json" <<JSON
[
  {
    "number": 77,
    "title": "$filed_title",
    "state": "OPEN",
    "labels": [{"name": "ready-for-agent:docs"}]
  }
]
JSON
file_run "$d" "$fx" update
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from a second $SUBJECT --file, with the issue already open; got $code")

created="$(grep -c '^+++ issue create$' "$log")"
[[ "$created" == 0 ]] ||
  problems+=("want no second issue opened when one is already open in the docs pool; got $created \`gh issue create\`: $(flat "$(cat "$log")")")

edited="$(grep -c '^+++ issue edit$' "$log")"
{ [[ "$edited" -ge 1 ]] && grep -Fqx -- '77' "$log"; } ||
  problems+=("want the open issue #77 edited instead — the debt moved on, the issue must too; got $edited \`gh issue edit\`: $(flat "$(cat "$log")")")

body_carries_list "edited body"

report "$name"

# 3. The run that moves the sha on: HEAD is past the commit the open issue was filed at, so
#    the issue in the pool is titled for an OLDER sha than the one this run measures. It is
#    still the one issue this pool gets — edited, and retitled to the sha the debt now
#    stands at — not a second one beside it.
#
#    This is the case case 2 cannot make. There both runs stand on the same HEAD, so the
#    open issue's title is character-for-character the one this run would write, and an
#    implementation that looked for the whole title in the pool passes it while opening a
#    fresh issue after every merge — the failure the single-issue rule exists to prevent.
#    Only a moved sha tells the two apart.
#
#    The older title is not spelled out here: it is read back from what the subject itself
#    filed at the older commit, so the pool holds the issue the previous merge really would
#    have left behind, whichever spelling of a sha the implementer puts in a title.
name="docs/docs-owed.sh --file at a newer commit retitles the open docs issue to the newer sha instead of opening a second"
problems=()
d="$(repo)"
git -C "$d" tag -a "$TAG" -m 'a capability the committed index does not list'
old_sha="$(git -C "$d" rev-parse HEAD)"

fx="$WORK/pool.empty2"; mkdir -p "$fx"
printf '[]\n' > "$fx/issues.json"
file_run "$d" "$fx" first
filed_title="$(grep -F 'Docs: catch the walkthrough up to' "$log" | head -1)"
[ -n "$filed_title" ] ||
  problems+=("the case is vacuous: the first $SUBJECT --file filed no titled issue to be found again: $(flat "$(cat "$log")")")
filed_title="${filed_title:-Docs: catch the walkthrough up to $old_sha}"

# HEAD moves. A file outside skills/ and outside the docs pipeline, so the tree's debt is
# the same tag it already owed and nothing about what is owed changes — only the sha the
# debt stands at, which is the whole point of the case.
printf 'a commit after the issue was filed\n' > "$d/scratch.txt"
git -C "$d" add scratch.txt
git -C "$d" commit -qm 'chore: a commit after the issue was filed (#4)'
new_sha="$(git -C "$d" rev-parse HEAD)"
[[ "$new_sha" != "$old_sha" ]] ||
  problems+=("the case is vacuous: HEAD did not move, so the open issue's sha is still current")

fx="$WORK/pool.older"; mkdir -p "$fx"
cat > "$fx/issues.json" <<JSON
[
  {
    "number": 77,
    "title": "$filed_title",
    "state": "OPEN",
    "labels": [{"name": "ready-for-agent:docs"}]
  }
]
JSON
file_run "$d" "$fx" retitle
[[ "$code" == 0 ]] ||
  problems+=("want exit 0 from $SUBJECT --file at a commit newer than the open issue's; got $code")

created="$(grep -c '^+++ issue create$' "$log")"
[[ "$created" == 0 ]] ||
  problems+=("want no second issue when the open one is titled for an older sha — the pool holds one; got $created \`gh issue create\`: $(flat "$(cat "$log")")")

edited="$(grep -c '^+++ issue edit$' "$log")"
{ [[ "$edited" -ge 1 ]] && grep -Fqx -- '77' "$log"; } ||
  problems+=("want the open issue #77 edited instead; got $edited \`gh issue edit\`: $(flat "$(cat "$log")")")

# And retitled: the title it is edited to names the sha this run measured, not the one the
# issue was opened with. An edit that left the old title standing would file the debt under
# a tree nobody is looking at any more.
title_line="$(grep -F 'Docs: catch the walkthrough up to' "$log" | head -1)"
sha="${title_line##*catch the walkthrough up to }"
if [[ -z "$title_line" ]]; then
  problems+=("want the edit to carry the title 'Docs: catch the walkthrough up to <sha>'; nothing in the call says so: $(flat "$(cat "$log")")")
elif [[ "${#sha}" -lt 7 || "$new_sha" != "$sha"* ]]; then
  problems+=("want the issue retitled to the sha this run read the debt at, $new_sha; got '$sha'")
fi

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
