#!/bin/sh
# record-answer.sh — post the owner's answer to a question tied to an issue on that issue, as one comment: `Question:`
# and the question file's `#### Question` text, a blank line, `Owner's answer:` and its `## Answer` text, local paths,
# host and account names redacted. A shim over veri/record_answer.py.
#
# Usage: record-answer.sh <issue-number> <question-file>
# Exit:  0 posted | 2 bad arguments, an unreadable or incomplete file, or no answer from gh | 3 already posted
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/record_answer.py" "$@"
