#!/bin/sh
# solvable-issues.sh — print the numbers of the issues veri may take right now, one per
# line: the `priority`-labelled ones first, then the `bug`-labelled ones, then the rest,
# each band ascending by number.
#
# An issue is solvable when it is open, carries the opt-in label (`ready-for-agent`, or the
# name `VERI_LABEL` gives instead — the human's explicit opt-in, since nothing is taken
# because it merely exists), every issue it names under its `## Blocked by` heading is
# closed, and no open pull request already says `Closes #<n>` for it — such a PR means a run
# is in flight on that issue, or one bailed and left the branch behind, and either way the
# issue is not veri's to take. A body whose `## Blocked by` section reads `None.` names no
# issue at all, so the test for "unblocked" is the absence of any issue reference under that
# heading rather than the literal word. A reference is spelled either way GitHub writes one:
# `#<n>`, or the full `https://github.com/<owner>/<repo>/issues/<n>` URL its autocomplete
# inserts — and that URL blocks only when its `<owner>/<repo>` is this repository's, since
# another project's `#<n>` is not this one's.
#
# The open PR is the claim, and it is the only mark of a run every machine can see. The
# conductor pushes the branch and opens its draft PR as the first act after the plan commit, so
# an issue whose run is in flight — or whose run bailed and left the branch behind — carries an
# open PR saying `Closes #<n>` from then on, and is left out here for as long as it does. veri
# is developed from more than one computer and `origin` is all they share, so a claim recorded
# anywhere else is one the other machine cannot read (ADR-0024). A `veri:in-flight` label would
# be visible too, but it outlives the run that set it with nothing to clear it, and it
# duplicates what the PR already records.
#
# The lock `.tdd/wt/<n>/.tdd/conductor.pid`, written under the repository's main working tree,
# is NOT a second claim: it is the worktree guard, and it guards one machine's worktree only.
# While the pid in there still answers `kill -0`, no second conductor on that same machine may
# enter the live run's tree and follow *Resume*, whose `git reset --hard HEAD` throws the live
# leaf's uncommitted work away. A pid is a machine-local name — it means nothing on
# another computer — so a lock nobody answers for frees the worktree and never the issue: a
# bailed run's issue stays out of the pool on the strength of its still-open draft PR, whatever
# its pid says (ADR-0024).
#
# The repository's issues and pull requests are read as the JSON `gh` emits:
#   gh issue list --limit 10000 --json number,title,labels,body,state
#   gh pr list    --limit 10000 --json body,state
# gh returns a page, not the repository — 30 items unless told `--limit` — and has no
# "all", so the limit is a number no repository here comes near.
# VERI_GH_JSON overrides both calls at once: it names a directory holding `issues.json` and
# `prs.json` fixtures with those exact shapes, which is what makes this testable with no
# network. Selection itself never learns which of the two it got — the documents are read
# here and handed on as text.
#
# jq is NOT a dependency of any script in this suite — `grep -n jq scripts/*.sh` returns
# this note and nothing else — so the JSON is read with python3's json module, the same
# interpreter extract-result.sh and the docs generator already require.
#
# Usage:   solvable-issues.sh [--repo owner/name]
#          VERI_GH_JSON=<dir> solvable-issues.sh
#          VERI_LABEL=<name>  solvable-issues.sh
# Exit:    0 one or more numbers printed; 2 no answer could be obtained — VERI_LABEL or
#          VERI_PRIORITY_LABEL is set but empty; 3 nothing to do — no issue is takeable
# usage: solvable-issues.sh [--repo owner/name]
exec python3 "$(dirname "$0")/veri/solvable_issues.py" "$@"
