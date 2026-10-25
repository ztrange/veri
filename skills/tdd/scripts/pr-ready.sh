#!/usr/bin/env bash
# pr-ready.sh — mark draft PR <pr-number> ready for review once <sha> is its head, via gh_pr_ready.
#
# Usage: pr-ready.sh <pr-number> <sha>
# Exit:  0 marked ready | 2 bad arguments, or no answer from GitHub
if [[ $# -ne 2 ]]; then
  echo "usage: pr-ready.sh <pr-number> <sha>" >&2
  exit 2
fi
. "$(dirname "$0")/lib/github.sh"
gh_pr_ready "$1" "$2"
