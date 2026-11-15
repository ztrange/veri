"""The one reading of an issue body's `## Blocked by` section (#460), importable by any caller
rather than locked inside solvable-issues.sh's heredoc. The reading itself is issue_body's; this
module is the name solvable_issues, workqueue and park_issue call it by."""
import issue_body

blockers = issue_body.blockers
add = issue_body.add_blocker
