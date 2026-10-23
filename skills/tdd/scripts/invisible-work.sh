#!/bin/sh
# invisible-work.sh — report work that is not visible, naming the invariant each finding
# breaks: a shim over veri/invisible_work.py.
# Reads, never writes: it deletes nothing, pushes nothing, opens nothing.
#
# Invariant 2: a branch is never created without a PR. A branch on `origin` for which
# no PR was ever opened — not open, not closed, not merged — is reported with its tip, its
# commit count ahead of the default branch, and, when its name has the `tdd/<n>-<slug>`
# shape, the number and state of issue <n>: that is what tells a live run from an abandoned
# one. An issue the repository does not have — a typo'd number, a transferred or deleted
# issue — has its state named `unknown` rather than guessed.
#
# Invariant 1: work in progress never lives only in a local branch. A local branch
# `origin` does not carry is reported with its tip, how many of its commits no `origin` ref
# holds, and the worktree it is checked out in, when there is one. A local branch whose PR was
# merged or closed is residue — its branch on `origin` deleted after the decision, as GitHub's
# "delete branch on merge" leaves every clone — a cleanup question, not a finding.
#
# The default branch is never reported: it needs no PR, being where PRs land.
#
# A branch any PR was opened for, whatever that PR's state, is not an invariant-2 finding:
# invariant 2 is a branch with no PR at all. One whose PR is still open sits in GitHub's
# review queue already.
#
# The repository's issues and PRs are read as the JSON `gh` emits:
#   gh issue list --state all --limit 10000 --json number,state
#   gh pr list --state all --limit 10000 --json headRefName,state
# VERI_GH_JSON overrides both, naming a directory holding `issues.json` and `prs.json` in those shapes — the same override solvable-issues.sh establishes, so this runs with no
# network in its tests.
#
# Exit: 0 when at least one finding was printed, 3 with empty stdout when there is nothing
# to report, 2 with a diagnostic on stderr and empty stdout when `origin` cannot be reached
# or `gh` cannot be read — so a fetch failure never reads as a clean repository.
#
# usage: invisible-work.sh
#        VERI_GH_JSON=<dir> invisible-work.sh
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/invisible_work.py" "$@"
