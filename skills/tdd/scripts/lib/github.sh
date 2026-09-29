#!/usr/bin/env bash
# lib/github.sh — sourced, not run: defines `gh_pr_ready`.
#
# gh_pr_ready <n> — mark draft PR <n> ready for review.
#   0  marked ready
#   2  GitHub gave no answer on either route

gh_pr_ready() {
  gh pr ready "$1" ||
    gh api -X POST "repos/{owner}/{repo}/pulls/$1/ccr/ready_for_review" ||
    return 2
}
