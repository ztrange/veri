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
# The committed page, spelled once because four sites below read it, rewrite it or date it,
# and it is the one path the subject and this suite have to agree on (docs/docs-owed.sh:77).
# Relative, so it reads as the subject reads it: `git -C "$d" … -- "$PAGE"` inside the copy,
# `"$d/$PAGE"` from out here.
PAGE="docs/walkthrough.html"
# Where the scripts the page lists stand, likewise spelled once (docs/docs-owed.sh:78): the
# cases below reach into it to date a script and to measure one the page misquotes, and a
# copy that drifted would plant its debt beside the tree rather than in it. Relative for the
# same reason PAGE is — `git -C "$d" … -- "$SCRIPTS_DIR/…"` inside the copy, `"$d/$SCRIPTS_DIR/…"`
# from out here.
SCRIPTS_DIR="skills/tdd/scripts"
pass=0 fail=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# The debts the cases plant, named once here, by the string the list has to carry for
# each: the script that is owed prose, the script the page is behind, the tag the index
# never saw, and the script the committed page misquotes. Not a format — where each one
# appears on its line, and what sits beside it, is the implementer's to choose; that it is
# nameable is not.
UNCOVERED=supervise.sh
STALE=refactor-budget.sh
STALE_PATH="$SCRIPTS_DIR/$STALE"
MISQUOTED=next-unchecked.sh
TAG=v9.9

# The fifth, and the one name here that is derived rather than written down: an old command,
# as a user types it, that the committed page may still be telling a reader to invoke. A
# forwarding stub is a skills/<name>/ carrying a SKILL.md and no scripts of its own — the
# live skill carries those — and the command is a slash followed by that directory's name.
# Assembled rather than spelled because skills/tdd/scripts/tests/skill-identity.test.sh
# sweeps every tracked file for exactly this string, and a suite that spelled it out would
# be that sweep's first offender; that suite assembles it from its `stubs` for the same
# reason. Empty if the repository has no stub left, which case 5 reports as a vacuous case
# rather than passing on a plant it never made.
OLD_CMD=""
for stub in "$ROOT"/skills/*/SKILL.md; do
  [ -f "$stub" ] || continue
  stub_dir="${stub%/SKILL.md}"
  [ -d "$stub_dir/scripts" ] && continue
  OLD_CMD="/$(basename "$stub_dir")"
  break
done

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

# cover_every_script_line <dir> — every script's last chunk stretched to the end of the
# file it claims, in that copy of the tree and only there, so the copy owes no commentary.
#
# What THIS repository owes in prose today is a fact about the development lane: a merged
# PR that grew a script leaves lines no chunk covers, and since #125 that is debt the build
# carries rather than refuses. The copy inherits it, and the clean half of case 1 — exit 3,
# nothing on stdout — would then be answering for whoever committed last rather than for
# the tree `repo` built. Grown, not clamped: a script that grew is the event being
# insulated against, and one that shrank past a chunk's end is a build failure in either
# tree, not debt.
#
# Appended as code rather than sed over the chunk table because the fix-up has to know each
# script's line count, and the module is imported by the build and by the subject both — so
# the one copy of commentary.py answers for the whole sandbox.
cover_every_script_line() {
  cat >> "$1/docs/wt/commentary.py" <<'PY'

# ── appended by docs/tests/docs-owed.test.sh in the disposable copy it builds ──
# Paths and the line count are spelled the way docs/build-walkthrough.py spells them
# (its HERE/ROOT/SCRIPTS_DIR, its len(read_text().splitlines())), so the end this
# stretches a chunk to is the same number the build compares it against.
import pathlib as _pathlib
_HERE = _pathlib.Path(__file__).resolve().parent.parent   # docs/wt/ -> docs/
_ROOT = _HERE.parent
_SCRIPTS_DIR = _ROOT / "skills" / "tdd" / "scripts"
for _spec in SCRIPTS:
    _path = _SCRIPTS_DIR / _spec["file"]
    if not _path.exists():
        continue
    _total = len(_path.read_text().splitlines())
    if not _spec["chunks"]:
        # a shim whose prose was dropped (#2710) claims nothing: claim it whole
        _spec["chunks"].append(dict(lines=(1, _total), html="<p>covered</p>"))
        continue
    _last = _spec["chunks"][-1]
    if _total > _last["lines"][1]:
        _last["lines"] = (_last["lines"][0], _total)
PY
}

# repo — a disposable copy of this tree as a repository of its own, with a page that is
# current with it: everything committed once, the page built ON TOP of that history and
# committed second. Built inside the sandbox rather than copied from here because the
# committed page carries what git said at build time — the real repo's tags, the real
# repo's blame — and a page answering for another repository's history would be behind
# this one from its first breath, which is the very thing the case then plants on purpose.
#
# The build's own stdout is dropped and its stderr kept out of the way: the copy is made to
# owe no commentary below, so it has nothing to say, and a build that did would show up as
# debt the clean half of the case then reports.
repo() {
  local d; d="$(mktemp -d "$WORK/case.XXXXXX")"
  cp -R "$ROOT/docs" "$d/docs"
  cp -R "$ROOT/skills" "$d/skills"
  cp "$ROOT/Makefile" "$d/"
  rm -rf "$d/docs/wt/__pycache__"
  cover_every_script_line "$d"

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

# answers_with_a_list <dir> <the tree it is run over, as a phrase> — run the subject there
# and pin the half of the contract every planted case shares: a tree with debt exits 0,
# because a list is an answer and not a failure (CLAUDE.md: exit codes are the API). Three
# cases below owe this, each right before it greps the list for what it planted, and the
# phrase is the only thing that differs between them — it is there so a failure says which
# tree came back as a failure rather than as a report. Runs `owed`, so it publishes `code`,
# `out` and `err` for those greps; reads `problems` where it stands, the protocol the rest
# of this file already uses.
answers_with_a_list() {
  owed "$1"
  [[ "$code" == 0 ]] ||
    problems+=("want exit 0 from $SUBJECT over $2 — a list is an answer, not a failure; got $code: $(flat "$out$err")")
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
#      * moving one chunk's start off the lines it claimed leaves supervise.sh L35–36
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

( cd "$d" && sed -i.bak 's/lines=(35, 43)/lines=(37, 43)/' docs/wt/commentary.py && rm -f docs/wt/commentary.py.bak )
grep -q 'lines=(37, 43)' "$d/docs/wt/commentary.py" ||
  problems+=("the coverage debt did not land: no chunk claiming lines=(35, 43) in docs/wt/commentary.py to move off $UNCOVERED L35–36")
git -C "$d" commit -qam 'docs: move a chunk off the lines it claimed (#2)'

( cd "$d" && sed -i.bak '2s|.*|# refactor-budget.sh — rewritten in place, same line count|' "$STALE_PATH" && rm -f "$STALE_PATH.bak" )
git -C "$d" commit -qam "fix: rewrite a line of $STALE after the page was built (#3)"
[[ "$(git -C "$d" log -1 --format=%H -- "$STALE_PATH")" != "$(git -C "$d" log -1 --format=%H -- "$PAGE")" ]] ||
  problems+=("the blame debt did not land: $STALE_PATH is still answered for by the commit the page is")

git -C "$d" tag -a "$TAG" -m 'a capability the committed index does not list'

answers_with_a_list "$d" "a tree with debt"

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

# pool_holding <fixture dir name> <issue title> — a VERI_GH_JSON fixture holding one open
# docs issue under that title, in the shape `gh issue list --json number,title,state,labels`
# answers with, and publishes its path in `fx` for the file_run that reads it. Two cases
# below build one and differ only in the directory's name and in the title the previous run
# left behind; everything else is the shape the subject has to recognise — open, in the docs
# pool, and numbered 77, which is the number those cases then watch the edit go to. Spelled
# twice, a fixture that drifted on one side would have the subject skipping an issue for a
# reason the case never meant to plant. The empty pool stays written out where it is used:
# `[]` is not a shape two sites have to agree on.
pool_holding() {
  fx="$WORK/$1"; mkdir -p "$fx"
  cat > "$fx/issues.json" <<JSON
[
  {
    "number": 77,
    "title": "$2",
    "state": "OPEN",
    "labels": [{"name": "ready-for-agent:docs"}]
  }
]
JSON
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
pool_holding pool.open "$filed_title"
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

pool_holding pool.older "$filed_title"
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

# ── the committed page's own content ─────────────────────────────────────────────
#
# Back to the plain list, for the reading none of the three above is: what the committed
# page SAYS, read out of the page itself rather than inferred from when it was committed.

# starts_clean <dir> <the line the plant below is to produce> — the subject has nothing to
# report over that tree yet, so whatever it says after the plant is the plant's. Both cases
# below owe this first read, and for the reason case 1 reads its tree twice: a script that
# listed every script it could see would pass the planted half while saying nothing about the
# tree it was pointed at. Named for the reason page_is_newest below is — spelled out it is two
# probes over one run, and the argument is the only thing that differs between the two call
# sites, there so a failure says which line the case failed to make evidence. Runs `owed`, so
# it publishes `code`, `out` and `err` for the probes that follow; reads `problems` where it
# stands, the protocol the rest of this file already uses.
starts_clean() {
  owed "$1"
  { [[ "$code" == 3 ]] && [[ -z "$out" ]]; } ||
    problems+=("the case is vacuous: $SUBJECT already has debt to report over the tree its page was just built from, so $2 below would not be this plant's; got $code: $(flat "$out$err")")
}

# page_is_newest <dir> <what a dated rule could have said instead> — the page is that tree's
# newest commit, so every rule that reads HISTORY is silent by construction and a line about
# the page can only have come from reading what the page SAYS. Both cases below plant in the
# committed page and both owe this check, which is why it is named: spelled out, it is two
# `git log -1` invocations a reader has to compare before seeing what is being claimed. The
# argument is the only thing that differs between the two call sites, and it is there so a
# failure says which dated rule the case failed to rule out. Reads `problems` where it
# stands, the protocol the rest of this file already uses.
page_is_newest() {
  [[ "$(git -C "$1" log -1 --format=%H)" == "$(git -C "$1" log -1 --format=%H -- "$PAGE")" ]] ||
    problems+=("the case is vacuous: the page is not the tree's newest commit, so $2")
}
#
# 4. A page that misquotes the tree is debt even when no commit is newer than it. The
#    `page behind` rule dates the page against the scripts, so it answers a question about
#    HISTORY — and comes up clean for a page whose content is wrong without a later commit
#    to date it against: a page edited by hand (CLAUDE.md's one trap), one committed in the
#    same breath as the change it fails to reflect, one built from a tree that was not this
#    one. The page's central claim is its own content — `<n> lines · complete source`
#    under each listing — so a quoted line count that disagrees with the script standing
#    beside it makes the page wrong on its face, whatever its dates say.
#
#    This is where that fact comes to live (#146). `make test` held it — solvable-issues.
#    test.sh case 13 read the committed page's count for solvable-issues.sh, and
#    skill-identity.test.sh case 8 swept the committed page for an old command name — which
#    put a claim about a generated artefact inside the command every veri leaf runs, so a
#    page nobody had rebuilt could stop a TDD cycle on a red the scripts did not cause (ADR
#    0016). It does not move to docs/tests/build-guards.test.sh either: that suite judges
#    only trees it builds itself, and judging the committed page there would make the
#    generator answer for a page it did not write. The committed page is debt to report
#    (#137), and this script is what reports debt.
#
#    The drift is planted in the page and committed, so the page is the newest commit in
#    the tree and every dated rule is silent by construction — which is what makes a line
#    naming the script here evidence of a reading of the page's content, and not of the
#    blame rule firing under another name. The tree is read clean first for the same
#    reason case 1 reads it twice: a script that lists every script it can see passes the
#    planted half and says nothing about the tree.
name="docs/docs-owed.sh reports what the committed page misquotes — a script's quoted line count — with no commit newer than the page's to date it by"
problems=()
d="$(repo)"

starts_clean "$d" "a line about $MISQUOTED"

# The listing header the build writes per script (docs/build-walkthrough.py:261), with its
# count rewritten to a figure no script has. The name is matched as the whole <span> pair
# the build emits, so the count moved is the one belonging to THIS script and not the first
# number that happens to follow its name somewhere else on a page whose lines run to
# thousands of characters.
#
# The header and the wrong count are each spelled once, because three sites below have to
# agree on them — the sed that plants the misquote, the grep that says it landed, and the
# vacuity check that the script is not really that long. Spelled out three times, the sed's
# two near-identical halves hide which part of the header the rewrite actually moves.
#
# `misquote` is the header as the page is to end up carrying it, named because the sed that
# writes it and the grep that reads it back are the two sides of one claim: a grep spelled
# out again could drift from the replacement and then confirm a landing that never happened.
# It leaves the sed reading as what it does — whatever count that header quotes, this one.
header="<span class=\"fname\">$MISQUOTED</span><span class=\"fmeta\">"
wrong_lines=9999
misquote="$header$wrong_lines lines"
( cd "$d" && sed -i.bak "s#$header[0-9]* lines#$misquote#" "$PAGE" && rm -f "$PAGE.bak" )
grep -Fq "$misquote" "$d/$PAGE" ||
  problems+=("the misquote did not land: no listing header for $MISQUOTED in the committed page to rewrite the line count of")
real_lines="$(awk 'END {print NR}' "$d/$SCRIPTS_DIR/$MISQUOTED")"
[[ "$real_lines" != "$wrong_lines" ]] ||
  problems+=("the case is vacuous: $MISQUOTED really is $wrong_lines lines long, so the page is not misquoting it")

# Committed alone, and last: HEAD's newest commit is now the page's own, so `page behind`
# has no script dated after it and the tag and commentary rules were answered by the clean
# read above. Nothing but a reading of the page's content is left to report this.
git -C "$d" commit -qam 'docs: a page that misquotes the tree it stands in (#4)'
page_is_newest "$d" "the blame rule could report $MISQUOTED without reading the page at all"

answers_with_a_list "$d" "a tree whose committed page misquotes it"
printf '%s\n' "$out" | grep -Fq -- "$MISQUOTED" ||
  problems+=("want a line naming $MISQUOTED — the committed page quotes its listing as $wrong_lines lines and the script is $real_lines; got: $(flat "$out")")

report "$name"

# 5. The committed page's other content fact, and the second half of what `make test` used
#    to hold about the page (#146): it still tells a reader to invoke a command that no
#    longer resolves to a procedure. skills/tdd/scripts/tests/skill-identity.test.sh case 8
#    held it, which put a claim about a generated artefact inside the command every veri
#    leaf runs — a page nobody had rebuilt could stop a TDD cycle on a red the scripts did
#    not cause (ADR 0016). Its sources are already swept by that suite's case 5 and are
#    clean; what is left is the ARTEFACT nobody has rebuilt, which is debt to report (#137)
#    and so belongs on this list beside the misquoted line count.
#
#    Not a reading the four rules above can make. `commentary` and `page behind` both ask
#    about history, and a page carrying prose that is merely out of date is newer than
#    everything it is out of date about; `page misquotes` reads the page's content but only
#    its listing headers, where a command name never appears. The name lives in the page's
#    prose, so only a reading of that prose finds it.
#
#    Planted after everything the build wrote, which puts it outside the capability index
#    for the reason skill-identity case 8 cuts that index out before sweeping: the index is
#    generated from annotated tag messages, which quote each issue's own words as they were
#    written, and a tag's message is history rather than documentation that can be brought
#    up to date. This repository's own page names an old command twice inside it today.
#
#    Committed alone and last, as case 4 does, so the page is the tree's newest commit and
#    every dated rule is silent by construction — a line naming the old command can then
#    only have come from reading what the page says.
name="docs/docs-owed.sh reports a committed page that still names a command which no longer resolves, with no commit newer than the page's to date it by"
problems=()
d="$(repo)"

[ -n "$OLD_CMD" ] ||
  problems+=("the case is vacuous: no forwarding stub under skills/ to read an old command name from, so nothing was planted")

starts_clean "$d" "a line naming $OLD_CMD"

# A line of the page's own prose, telling a reader to run the command. Appended rather than
# substituted in: the page's lines run to thousands of characters, and what this plants is a
# sentence that was true before the skill was renamed, not an edit to any particular one.
printf '<p class="note">Start a cycle by running %s on the issue.</p>\n' "$OLD_CMD" >> "$d/$PAGE"
grep -Fq -- "$OLD_CMD" "$d/$PAGE" ||
  problems+=("the plant did not land: the committed page does not name $OLD_CMD after appending a line that does")

git -C "$d" commit -qam 'docs: a page still naming a command that no longer resolves (#5)'
page_is_newest "$d" "a dated rule could report this without reading the page at all"

answers_with_a_list "$d" "a tree whose committed page names an old command"
printf '%s\n' "$out" | grep -Fq -- "$OLD_CMD" ||
  problems+=("want a line naming $OLD_CMD — the committed page tells a reader to run it and no such command resolves any more; got: $(flat "$out")")

report "$name"

echo "----"
echo "$pass passed, $fail failed"
[[ "$fail" -eq 0 ]]
