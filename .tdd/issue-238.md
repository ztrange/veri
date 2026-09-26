# Plan for #238 — Concurrent runs owe a rebase over each other's merges, and nothing re-verifies the rebased branch before it lands

- [x] rebase-onto-default.sh, run in a worktree whose branch already contains origin/<default>, exits 3 with empty stdout and leaves HEAD and the working tree unchanged ⟦criterion 1⟧
- [x] rebase-onto-default.sh, run on a branch behind origin/<default> with no conflict, rebases onto it, exits 0, prints the pre-rebase sha and the onto sha, and leaves HEAD containing origin/<default> with the branch's own commits on top ⟦criterion 1⟧
- [x] rebase-onto-default.sh on a rebase that conflicts aborts it, exits 1, leaves HEAD at the pre-rebase sha with a clean tree and no rebase in progress, and prints the conflicting files one per line ⟦criterion 4⟧
- [x] rebase-onto-default.sh exits 2, not 1, with nothing on stdout and HEAD unchanged when git rebase fails for a reason other than a conflict, such as a dirty working tree ⟦added⟧ ⟦criterion 4⟧
- [x] rebase-onto-default.sh, in a repo configured with rebase.backend=apply, still aborts a conflicted rebase, exits 1 and prints the conflicting files, leaving no rebase in progress ⟦added⟧ ⟦criterion 4⟧
- [x] rebase-onto-default.sh exits 2 with nothing on stdout when origin/<default> cannot be fetched or named, and never rebases onto a stale local branch ⟦criterion 1⟧
- [x] rebase-onto-default.sh exits 2 with nothing on stdout and HEAD unchanged when, after a successful fetch, origin/HEAD still names no branch ⟦added⟧ ⟦criterion 1⟧
- [x] build-develop-prompt.sh rebase renders prompts/develop-rebase.md naming the onto sha, the pre-rebase sha, every conflicting file and the test command, tells the leaf to resolve by rebasing onto the onto sha and to leave the ledger's ticks and marks untouched, ends with a REBASE: RESOLVED | FAILED report line, and exits 2 with no stdout on a missing argument ⟦criterion 3⟧
- [x] build-verify-prompt.sh rebase <spec-file> <onto-sha> <pre-rebase-sha> renders a blind verify-rebase prompt from the spec and the two shas alone, telling the verifier to run the full test command on HEAD and to judge that both the branch's changes and the default branch's changes survive the resolution; either sha that is not ^[0-9a-f]{7,40}$ exits 2 with no stdout ⟦criterion 3⟧
- [x] verify.sh and run-verdict.sh accept the rebase phase and return the verdict of a verify-rebase leaf launched through supervise.sh under the name verify-rebase: 0 PASS, 1 REJECT, 2 malformed ⟦criterion 3⟧
- [x] classify-bail.sh rebase-unresolved prints process and exits 0 ⟦criterion 4⟧
- [x] SKILL.md step 4 runs rebase-onto-default.sh after the dirty-tree and pending-refactor check and before the done mark, metrics commit and gh pr ready; exit 3 continues unchanged, exit 2 bails with no-verdict ⟦criterion 1⟧
- [x] push-branch.sh given --force-with-lease=<branch>:<sha> pushes the branch under that lease, replacing a remote copy that still points at <sha> and refusing, without replacing it, one that has moved on; called with no argument it pushes exactly as before, and it never pushes with a bare force ⟦added⟧ ⟦criterion 2⟧
- [x] SKILL.md step 4, after a rebase that changed the tree, runs the full test command once on the rebased tip, bails on a red result without readying the PR, and on green pushes with $S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force ⟦added⟧ ⟦criterion 2⟧
- [x] SKILL.md step 4 on rebase-onto-default.sh exit 1 launches a develop-rebase leaf through supervise.sh, then a blind verify-rebase through run-verdict.sh, runs the revise loop on REJECT within REVISE_BUDGET, and readies the PR only after a verify-rebase PASS ⟦criterion 3⟧
- [x] SKILL.md step 4 on a rebase not resolved within budget (REBASE: FAILED, revise-exhausted, or a killed leaf) resets the branch to the pre-rebase sha, leaves the PR a draft, and posts a bail comment naming every conflicting file ⟦criterion 4⟧
- [x] CLAUDE.md's script and suite counts include rebase-onto-default.sh and its suite
- [ ] no-job-spec-kills.test.sh passes on the branch: its exemption for skill-leaf-env.test.sh's kill %1 step-title fixture still matches that line after this branch's three added lines moved it from 972 to 975

## Owed steps

- push-branch.sh given --force-with-lease=<branch>:<sha> pushes the branch under that lease, replacing a remote copy that still points at <sha> and refusing, without replacing it, one that has moved on; called with no argument it pushes exactly as before, and it never pushes with a bare force
- SKILL.md step 4, after a rebase that changed the tree, runs the full test command once on the rebased tip, bails on a red result without readying the PR, and on green pushes with $S/push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>, never a bare force ⟦criterion 2⟧

## Owed steps

- SKILL.md step 4 bails a red rebased tip as a process failure, not no-verdict, with the PR left a draft
