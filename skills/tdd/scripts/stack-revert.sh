#!/bin/sh
# stack-revert.sh — revert a culprit issue's commits, its hand fix included, on top of a red stack and lift its
# join claim: a shim over veri/stack_revert.py.
#
# usage:   stack-revert.sh <n>   (run in the target repository's clone)
#
# Under the merge lock, after a fetch, it reverts every commit of origin/<default>..origin/<stack> that belongs to
# issue <n> by stack-green.sh's subject rule, newest first, as one commit on the stack's tip whose subject ends (#<n>),
# in a detached worktree of its own under .tdd/, removed on every exit; runs the fast tier and prose-owed.sh there and
# pushes the revert as a fast-forward leased to the fetched tip, never forced, starting again from the fetch while
# origin's stack moves (5 attempts). After the push, each `Closes #<n>` in the body of a pull request merged into the
# stack becomes `Reverted from <stack> by <sha>`, and it comments once on issue <n> and once on the tracking pull
# request; it changes no label.
# Exit:    0 pushed: the revert's sha printed; 1 a revert conflict, a red fast tier or a unit owing a grade, nothing
#          pushed; 3 stack-red.sh exits 3, no commit of the stack belongs to <n>, or <n> is already reverted there;
#          2 no answer from git, GitHub, stack-red.sh or the lock, origin moving on every attempt, bad arguments, or
#          a merged pull request's body it cannot read or edit (named, the revert left pushed). The lock is freed on
#          every exit.
. "$(dirname "$0")/lib/shim-python.sh"
exec "$py" "$(dirname "$0")/veri/stack_revert.py" "$@"
