#!/usr/bin/env bash
# docs-owed.sh — what the committed walkthrough is behind on, one item per line.
#
# WHY THIS EXISTS (#125): the page used to be kept current by force. The build refused to
# emit a page with a script line no commentary chunk covered, and `make merge-gates` owed a
# fresh page for any PR that touched a script — so the prose could not lag, at the price of
# putting it on the critical path of every development PR. Both of those are gone: the
# build carries an uncovered line as debt, and a change under skills/ owes no page. That
# makes the lag real and deliberate, and leaves nobody holding the fact. This script is
# where that fact is held: run it after a merge and the debt is a list, not something
# somebody has to notice.
#
# WHAT COUNTS AS DEBT — four readings, one line each, because a merged PR can leave the
# page behind in four unrelated ways:
#   commentary  a run of script lines no chunk in docs/wt/commentary.py claims. Read from
#               the build itself (its `owed:` summary on stderr) rather than re-deriving
#               the rule here, so the page and this list cannot disagree about coverage.
#   page behind a script whose last commit is newer than the page's. Its listing is
#               verbatim as of the page's build, which is to say no longer verbatim; a
#               rebuild is what fixes it, and no coverage gap need be involved at all.
#   page        a listing header whose quoted line count disagrees with the script standing
#   misquotes   beside it. This one reads the page's own CONTENT, not its dates, which is
#               the only way a page that is wrong on its face with no later commit to date
#               it by gets reported at all (#146): one edited by hand — CLAUDE.md's one
#               trap — one committed in the same breath as the change it fails to reflect,
#               one built from a tree that was not this one.
#   tag         a version the committed capability index does not name. A tag is the one
#               input to the page that changes with no commit behind it, so nothing marks
#               the page stale when one is cut.
# The four are independent on purpose: a tree can owe any one of them alone, and which
# one it owes says what the fix is.
#
# OUTPUT is a list and nothing else — one item per line, no header, no totals — because
# what reads it turns lines into issue-body bullets. An empty list is zero lines.
#
# `--file` carries that same list into the `ready-for-agent:docs` pool, as ONE issue titled
# `Docs: catch the walkthrough up to <sha>`, edited again on a later run rather than opened
# a second time: a pool that grew an issue per merge would be a worse report than none,
# since draining it would mean reading N copies of the same debt. `/tdd docs` drains it.
#
# EXIT CODES, the repo-wide four: 0 = here is the debt (a list is an answer, not a
# failure); 3 = nothing to do, the page is current and stdout is empty; 2 = no answer
# could be obtained — not a git repository, no committed page to be behind, or a build
# that failed outright, which is a bug in the docs pipeline rather than debt.
set -uo pipefail

# die <message> [detail…] — say so on stderr and stop, at exit 2 always. Every failure this
# script can have is the same kind of failure: no answer could be obtained. The debt itself
# is never one — a list exits 0 and an empty list exits 3 — so 2 is not one option among
# the four here, it is the only code a failure ever carries, and putting it in one place is
# what keeps that true. Extra arguments print verbatim on the lines below, for the one
# caller that has a build's own complaint to pass on rather than a sentence of its own.
die() {
  echo "docs-owed: $1" >&2
  shift
  [ "$#" -eq 0 ] || printf '%s\n' "$@" >&2
  exit 2
}

# The only argument, and an unknown one is a misconfigured caller rather than a page with
# no debt: exit 2, not 3.
file=0
case "${1:-}" in
  "")      ;;
  --file)  file=1 ;;
  *)       die "usage: docs-owed.sh [--file]" ;;
esac

# The repository this script is IN, not the one the caller happens to stand in: the page,
# the scripts and the history being compared are all this tree's.
root="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)" ||
  die "cannot resolve the repository root from $0"
cd "$root" || exit 2
git rev-parse --git-dir >/dev/null 2>&1 ||
  die "$root is not a git repository"

PAGE=docs/walkthrough.html
SCRIPTS_DIR=skills/tdd/scripts

# What a version looks like, as an extended-regex fragment: vN.M and nothing else (CLAUDE.md
# — a version is an annotated tag vN.M, there is no other kind). Written once because the
# tag rule below compares two lists of versions read from two different places, the tags git
# knows about and the tags the committed page names, and a shape that changed on one side
# only would report every tag as missing from an index that lists them all.
VERSION_TAG='v[0-9]+\.[0-9]+'

# lists <newline-separated list> <item> — is <item> one whole line of that list? Both of
# the rules below ask this, of a different list, and -F -x together are the load-bearing
# part: without -x, v0.1 reads as listed because v0.10 is, and without -F the dot in a
# version number matches any character.
lists() { printf '%s\n' "$1" | grep -Fqx -- "$2"; }

page_commit="$(git log -1 --format=%H -- "$PAGE")"
[ -n "$page_commit" ] ||
  die "no commit touches $PAGE — there is no committed page to be behind"

owed=()

# ── commentary: the runs of source no chunk claims ──────────────────────────────
# The build prints `  owed: <script> L<a>–<b>` per gap and still exits 0; a non-zero exit
# is a real problem (a dead {{p-id|…}} reference, a chunk claiming lines a script does not
# have) and is not this script's to report. --stdout so reading the tree's debt never
# rewrites the page being measured.
build_err="$(python3 docs/build-walkthrough.py --stdout 2>&1 >/dev/null)" ||
  die "the build failed, so what prose is missing cannot be read:" "$build_err"
while IFS= read -r gap; do
  [ -n "$gap" ] || continue
  owed+=("commentary owed: $gap")
done <<< "$(printf '%s\n' "$build_err" | sed -n 's/^ *owed: //p')"

# ── page behind: scripts whose last commit is newer than the page's ─────────────
# One `git log` over the commits after the page's, not one question per script: the paths
# those commits touched are the same fact either way, and gitmeta.py's budget rule (a
# build asks git a fixed handful of times) is worth keeping here too.
#
# Only the scripts the page actually lists count — commentary.py is the authority on that,
# and a script it does not carry is not a page the reader is missing. Imported with
# bytecode off for the reason build-walkthrough.py gives: a __pycache__ this script left
# behind would show up as an untracked file to the next `make merge-gates`.
listed="$(python3 - <<'PY'
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, "docs/wt")
import commentary
print("\n".join(s["file"] for s in commentary.SCRIPTS))
PY
)" || die "cannot read the page's script list from docs/wt/commentary.py"

touched="$(git log --format= --name-only "$page_commit..HEAD" -- "$SCRIPTS_DIR" | sort -u)"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  name="${path##*/}"
  lists "$listed" "$name" || continue
  owed+=("page behind: $name — its last commit is newer than the page's build")
done <<< "$touched"

# ── page misquotes: a listing header that disagrees with the script beside it ────
# The reading the two rules above cannot make, because both of them ask about HISTORY: one
# about which commits came after the page's, the other about what the build says of the
# tree as it stands now. A page whose content is simply wrong — a count edited by hand, a
# page committed alongside the change it does not reflect — is newer than everything it
# misquotes, so nothing dates it as stale. Its own text is the only witness left (#146).
#
# The line count is the page's central claim: every listing says `<n> lines · complete
# source`, so a count that disagrees with the script makes the page wrong on its face. Read
# out of the COMMITTED page, as the tag rule below reads it, because the debt being listed
# is the debt a reader of the repository would meet.
#
# Bytecode off and the header matched as the whole <span> pair docs/build-walkthrough.py:261
# writes, so the count taken is the one belonging to that name and not the first number that
# happens to follow it on a line running to thousands of characters. A name the page lists
# but the tree does not carry is a different failure, and not this rule's to report.
misquoted="$(python3 - "$PAGE" "$SCRIPTS_DIR" <<'PY'
import pathlib, re, subprocess, sys
sys.dont_write_bytecode = True

page_path, scripts_dir = sys.argv[1], pathlib.Path(sys.argv[2])
page = subprocess.run(["git", "show", "HEAD:" + page_path],
                      stdout=subprocess.PIPE, text=True, check=True).stdout
header = re.compile(r'<span class="fname">([^<]+)</span><span class="fmeta">([0-9]+) lines')
for fname, quoted in header.findall(page):
    path = scripts_dir / fname
    if not path.exists():
        continue
    # splitlines(), the count the build itself wrote (build-walkthrough.py:229), so the two
    # sides of this comparison are counting the same thing.
    total = len(path.read_text().splitlines())
    if int(quoted) != total:
        print("%s %s %s" % (fname, quoted, total))
PY
)" || die "cannot read the committed page's listing headers"
while IFS=' ' read -r name quoted total; do
  [ -n "$name" ] || continue
  owed+=("page misquotes: $name — its listing quotes $quoted lines, the script has $total")
done <<< "$misquoted"

# ── tags the committed capability index does not name ───────────────────────────
# Every tag the build knew about is written into the page as a quoted JSON token
# (window.__VERI_ORDER__, in git's version sort), so the tags the page names are the
# quoted vN.M tokens in it — the quotes are what make the token whole, so v0.10 is not read
# as a v0.1 the page names. A page built before any tag existed names none, and owes all.
index_tags="$(git show "HEAD:$PAGE" 2>/dev/null | grep -oE "\"$VERSION_TAG\"" | tr -d '"' | sort -u)"
while IFS= read -r tag; do
  [ -n "$tag" ] || continue
  lists "$index_tags" "$tag" && continue
  owed+=("tag missing from the index: $tag — the page was built before it was cut")
done <<< "$(git tag | grep -E "^${VERSION_TAG}$" | sort -u)"

[ "${#owed[@]}" -eq 0 ] && exit 3
printf '%s\n' "${owed[@]}"
[ "$file" -eq 1 ] || exit 0

# ── --file: the same list, as the one issue the docs pool drains ─────────────────
# The pool is named by its label, and the issue by the sha the debt was read at, so the
# title says which tree the page has to catch up TO. The pool is read the way
# solvable-issues.sh reads it — `gh issue list --json …`, or the `issues.json` fixture
# VERI_GH_JSON names instead, which is what makes filing testable with no network — and
# jq stays out of it for the reason that script gives: python3 is already a dependency.
DOCS_LABEL='ready-for-agent:docs'
TITLE_PREFIX='Docs: catch the walkthrough up to '
title="$TITLE_PREFIX$(git rev-parse --short=12 HEAD)"

if [ -n "${VERI_GH_JSON:-}" ]; then
  issues_json="$(cat "$VERI_GH_JSON/issues.json")"
else
  issues_json="$(gh issue list --label "$DOCS_LABEL" --state open \
    --json number,title,state,labels)"
fi || die "cannot read the $DOCS_LABEL pool"

# The issue to edit, if there is one: open, in this pool, and titled for SOME sha — the
# prefix, not the whole title, because the sha in an issue filed at an earlier merge is
# precisely the thing this run moves on. Matching the whole title would open a second
# issue per merge, which is the failure this is here to avoid.
existing="$(python3 - "$issues_json" "$DOCS_LABEL" "$TITLE_PREFIX" <<'PY'
import json, sys
issues, label, prefix = json.loads(sys.argv[1]), sys.argv[2], sys.argv[3]
for issue in issues:
    if issue.get("state", "").upper() != "OPEN":
        continue
    if not any(l.get("name") == label for l in issue.get("labels", [])):
        continue
    if not (issue.get("title") or "").startswith(prefix):
        continue
    print(issue["number"])
    break
PY
)" || die "cannot read the $DOCS_LABEL pool's issues"

# The body is the list, one bullet per item, with the sha it was read at above it. Through
# a file rather than --body: an item carries an em dash and newlines, and a file is the one
# spelling that cannot be mangled by a shell on the way to gh.
body="$(mktemp)"
trap 'rm -f "$body"' EXIT
{
  echo "The committed \`$PAGE\` is behind on the following, as of $(git rev-parse HEAD)."
  echo
  printf -- '- %s\n' "${owed[@]}"
  echo
  echo "Regenerated by \`docs/docs-owed.sh --file\`; this issue is edited in place, so"
  echo "what it says is the debt as of the last run, not as of when it was opened."
} > "$body"

if [ -n "$existing" ]; then
  gh issue edit "$existing" --title "$title" --body-file "$body" >/dev/null ||
    die "cannot edit issue #$existing"
else
  gh issue create --title "$title" --label "$DOCS_LABEL" --body-file "$body" >/dev/null ||
    die "cannot open the $DOCS_LABEL issue"
fi
exit 0
