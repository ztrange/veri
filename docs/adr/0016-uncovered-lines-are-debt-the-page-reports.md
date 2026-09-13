# A script line no commentary covers is debt the page reports, not a build failure

`docs/build-walkthrough.py` used to **fail** when `docs/wt/commentary.py` left any line of
any script uncovered: a run of lines no chunk claimed was a build problem, and `make docs`
exited 1. It no longer is. Those lines render exactly as every other line does, the note
column beside them says `commentary owed` in the reader's terms, and the build prints
`owed: <script> L<a>–<b>` on stderr and exits 0. What stays fatal is everything that
describes a listing which could not be rendered at all: a chunk that starts early and
claims lines another chunk already claimed, a chunk that runs past the end of the file,
and a `{{p-id|…}}` naming a reference entry that does not exist — that last one is a typo,
not debt, and a typo silently swallowed is a wrong page.

So the page's promise is now stated in two halves, and the second half is the change: the
source it shows is **always verbatim**, the file as it is today; the prose beside it **may
lag**, and where it lags the page says so rather than hiding it.

## Context

The old guard bought one thing — no reader ever meets an unexplained line — and charged
for it at merge time on every pull request that touched a script. A script change could
not land until somebody wrote prose for it, plus the `make docs` regen commit and the
amend-past-the-tag dance CLAUDE.md records, 15–25 min a PR; and because
the page is computed from git history, it went stale again on the next tag or `plan:`
commit anyway. The prose was never what made the page trustworthy: the generator reads the
scripts, so the listing cannot drift whether or not anyone has explained it. Coupling a
code change to an unwritten paragraph traded the guarantee people rely on for one nobody
asked for.

Rejected: **a per-script allow-list of "prose pending" files**, because it is a second
place to keep in sync and goes stale silently, where a gap derived from the chunks cannot.
**Leaving the failure and skipping the gate**, i.e. keeping the build strict but not
running it at merge — that hides the debt instead of reporting it, and the first person to
run `make docs` inherits a broken build they did not cause.

## Consequences

Development and documentation decouple. `docs/merge-gates.sh` owes no `docs-fresh` for a
change under `skills/` (it still owes the guard suite for a change to the docs pipeline
itself), and `docs/docs-owed.sh` is where the debt is filed rather than discovered: it
lists the scripts with uncovered lines, the scripts whose blame is newer than the page's
build, and the tags the capability index does not list, and with `--file` keeps one issue
in the `ready-for-agent:docs` pool holding that list. The cost is that the published page
can carry `commentary owed` marks in public, which is the honest state of it; the guard
that used to prevent that now names it in three places a human reads — the note column,
the build's stderr summary, and the docs-pool issue.
