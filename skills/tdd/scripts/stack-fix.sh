#!/bin/sh
# stack-fix.sh — push a reviewed hand fix on top of a red stack, once per culprit: a shim over veri/stack_fix.py.
#
# usage:   stack-fix.sh <n> <red-sha> <culprit-file>   (run in a fix worktree)
#
# A fix worktree is a detached worktree under the target repository's .tdd/, cut from origin/<stack>'s tip;
# <culprit-file> holds stack-culprit.sh's answer for <red-sha>. Under the merge lock, after a fetch, it pushes HEAD to the stack as a fast-forward leased to the fetched tip, never
# forced, only when <red-sha> is the commit stack-red.sh prints, <culprit-file> names issue <n> for <red-sha>, no stack
# commit already carries a Stack-fix: trailer and names <n>, every commit of origin/<stack>..HEAD ends its subject
# (#<n>) and carries `Stack-fix: <red-sha>`, no test file is added, changed, deleted or renamed, and at HEAD each named
# case passes alone through the `veri: one test file:` command and the fast tier and prose-owed.sh exit 0.
# Exit:    0 pushed: the pushed sha printed, then one comment on the tracking pull request and one on issue <n>;
#          1 a bound fails, a named case is red, absent or not collected, the fast tier is red, a unit owes a grade,
#          or origin's stack moved; 2 no answer from stack-red.sh, git, GitHub, the lock or an alone run, or bad
#          arguments; 3 stack-red.sh exits 3. On 1 or 2 nothing is pushed, the lock is freed and the fix worktree kept.
#          It calls no wait-ci.sh and lifts no freeze.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_fix.py" "$@"
