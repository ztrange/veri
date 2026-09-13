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
# WHAT COUNTS AS DEBT — three readings, one line each, because a merged PR can leave the
# page behind in three unrelated ways:
#   commentary  a run of script lines no chunk in docs/wt/commentary.py claims. Read from
#               the build itself (its `owed:` summary on stderr) rather than re-deriving
#               the rule here, so the page and this list cannot disagree about coverage.
#   page behind a script whose last commit is newer than the page's. Its listing is
#               verbatim as of the page's build, which is to say no longer verbatim; a
#               rebuild is what fixes it, and no coverage gap need be involved at all.
#   tag         a version the committed capability index does not name. A tag is the one
#               input to the page that changes with no commit behind it, so nothing marks
#               the page stale when one is cut.
# The three are independent on purpose: a tree can owe any one of them alone, and which
# one it owes says what the fix is.
#
# OUTPUT is a list and nothing else — one item per line, no header, no totals — because
# what reads it turns lines into issue-body bullets. An empty list is zero lines.
#
# EXIT CODES, the repo-wide four: 0 = here is the debt (a list is an answer, not a
# failure); 3 = nothing to do, the page is current and stdout is empty; 2 = no answer
# could be obtained — not a git repository, no committed page to be behind, or a build
# that failed outright, which is a bug in the docs pipeline rather than debt.
set -uo pipefail

# The repository this script is IN, not the one the caller happens to stand in: the page,
# the scripts and the history being compared are all this tree's.
root="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)" || {
  echo "docs-owed: cannot resolve the repository root from $0" >&2; exit 2; }
cd "$root" || exit 2
git rev-parse --git-dir >/dev/null 2>&1 || {
  echo "docs-owed: $root is not a git repository" >&2; exit 2; }

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
[ -n "$page_commit" ] || {
  echo "docs-owed: no commit touches $PAGE — there is no committed page to be behind" >&2
  exit 2; }

owed=()

# ── commentary: the runs of source no chunk claims ──────────────────────────────
# The build prints `  owed: <script> L<a>–<b>` per gap and still exits 0; a non-zero exit
# is a real problem (a dead {{p-id|…}} reference, a chunk claiming lines a script does not
# have) and is not this script's to report. --stdout so reading the tree's debt never
# rewrites the page being measured.
build_err="$(python3 docs/build-walkthrough.py --stdout 2>&1 >/dev/null)" || {
  echo "docs-owed: the build failed, so what prose is missing cannot be read:" >&2
  printf '%s\n' "$build_err" >&2
  exit 2; }
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
)" || { echo "docs-owed: cannot read the page's script list from docs/wt/commentary.py" >&2; exit 2; }

touched="$(git log --format= --name-only "$page_commit..HEAD" -- "$SCRIPTS_DIR" | sort -u)"
while IFS= read -r path; do
  [ -n "$path" ] || continue
  name="${path##*/}"
  lists "$listed" "$name" || continue
  owed+=("page behind: $name — its last commit is newer than the page's build")
done <<< "$touched"

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
exit 0
