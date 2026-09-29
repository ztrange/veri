#!/usr/bin/env bash
# lib/github.sh — sourced, not run: defines `gh_pr_ready`.
#
# gh_pr_ready <n> — mark draft PR <n> ready for review; returns gh's own status.

gh_pr_ready() {
  gh pr ready "$1" ||
    gh api -X POST "repos/{owner}/{repo}/pulls/$1/ccr/ready_for_review"
}
