# Plan for #4208 — PRD 034.3d: stack-revert.sh reverts the culprit and its fix on top and lifts its claim

- [x] stack-revert.sh reverts every commit of <n> by KT5's rule, newest first, as one commit on the tip ending (#<n>) ⟦criterion 1⟧
- [x] it runs the fast tier and prose-owed.sh and pushes a fast-forward, starting again from the fetch when origin moved ⟦criterion 2⟧
- [x] a revert conflict, a red fast tier or a unit owing a grade is exit 1, nothing pushed, the lock freed ⟦criterion 3⟧
- [x] exit 3 on stack-red.sh exit 3 or no commit of <n>; 2 on no answer ⟦criterion 4⟧
- [x] after the push each merged pull request's Closes #<n> becomes Reverted from <stack> by <sha>; a body it cannot edit is exit 2 ⟦criterion 5⟧
- [x] it comments once on issue <n> and once on the tracking pull request, and changes no label ⟦criterion 6⟧
- [x] the shim, the module index entry and a process case ⟦criterion 7⟧
- [x] the module names no repository, issue or job ⟦criterion 8⟧
- [x] SCRIPTS.md lists stack-revert.sh, row SC258, graded ⟦criterion 9⟧
- [x] skills/vmerge/SKILL.md says when to run stack-revert.sh, row M36, graded ⟦criterion 10⟧
