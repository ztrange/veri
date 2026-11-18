# Plan for #4319 — PRD 034.4c: stack-tag.sh tags the issues a landed slice changed

- [x] stack-tag.sh, a /bin/sh shim over veri/stack_tag.py, exits 2 with its usage line `usage: stack-tag.sh <slice-pr-url> [--message <n>=<text>]...` on no argument, a second url, or a --message not of the form <n>=<text> (process case for the shim, unit cases in tests/py/unit/test_stack_tag.py, no process) ⟦criterion 1⟧
- [x] stack_tag exits 2, nothing tagged and no lock taken, when the pull request does not read merged, when its base is not the default branch, and when GitHub gives no answer on the pull request or its commits (unit case, no process) ⟦criterion 2⟧
- [x] stack_tag exits 3, no lock taken, when every commit of every issue the subjects name is docs, test, refactor, chore or plan (unit case, no process) ⟦criterion 4⟧
- [x] a commit of an unknown type, or of no type, makes stack_tag exit 2 naming its subject, nothing tagged and no lock taken (unit case, no process; the go-red for KL35) ⟦criterion 4⟧
- [x] for an issue with a feat or fix commit, stack_tag takes the merge lock, fetches tags, cuts an annotated tag named the next vN.M after `git tag --sort=-v:refname`'s first (v0.10 over v0.9) on the last commit of the landed range whose subject names the issue, pushes it, frees the lock and exits 0 (unit case, no process) ⟦criterion 5⟧
- [x] several owing issues are tagged in the order of their last commit, each pushed before the next number is read (unit case, no process) ⟦criterion 3⟧
- [x] the tag's message is the issue's title as GitHub gives it, or the text of --message <n>=<text> for that issue; a title GitHub does not answer is exit 2 before the lock (unit case, no process) ⟦criterion 6⟧
- [x] an owing issue whose commit already carries a tag is skipped, and a run that finds every owed issue tagged exits 3 (unit case, no process) ⟦criterion 7⟧
- [x] a failed tag push exits 2 naming the issue, the local tag deleted, tags already pushed kept, the lock freed (unit case, no process) ⟦criterion 8⟧
- [x] a failed merge-lock take exits 2 with nothing fetched; a failed tag fetch exits 2 with the lock freed (unit case, no process)
- [x] the landed range on the default branch, the last <k> commits up to the merge commit, must carry the pull request's <k> subjects in order, else exit 2 naming the merge commit, nothing tagged, the lock freed (unit case, no process)
- [x] a repository with no vN.M tag to bump from makes stack_tag exit 2 saying so, nothing tagged, the lock freed (unit case, no process) ⟦added⟧
- [x] stack_land calls stack-tag.sh <slice-pr-url> after a landing it made; an exit other than 0 or 3 is exit 2 from the land naming the landed slice and the command owed (unit case, no process) ⟦criterion 9⟧
- [ ] `skills/tdd/SCRIPTS.md` lists stack-tag.sh with its exits and rules (row SC574), the veri README indexes it, graded ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] `skills/vmerge/SKILL.md` says a slice's tags are cut by $S/stack-tag.sh <slice-pr-url>, which stack-land.sh runs, by each issue's commit types, the operator rewording a failure-phrased title with --message (row M40), graded ⟦skill-edit⟧ ⟦criterion 10⟧
- [ ] no script or skill touched names a repository, issue, branch, label or person ⟦diff-checked⟧ ⟦criterion 11⟧
