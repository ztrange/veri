# Plan for #1297 — SKILL.md: a resumed run rebases onto origin/main before its next step

- [x] SKILL.md says a resumed run — one whose worktree and ledger already exist — runs `rebase-onto-default.sh` before its preflight baseline, so the baseline runs on the rebased tip, and that a new branch's run does not rebase there ⟦criterion 1⟧
- [x] SKILL.md says the resume rebase's exit 3 goes on unchanged, its exit 1 goes on from the old base and leaves the conflict to the Draft PR step, and its exit 2 bails as the Draft PR step's does (`no-verdict`) ⟦criterion 1⟧
- [x] The Draft PR step's rebase text in SKILL.md is unchanged by this branch ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] SKILL.md says a resume rebase that moved the branch is published, once the baseline is green, with `push-branch.sh --force-with-lease=<branch>:<pre-rebase-sha>`, never a bare force ⟦criterion 2⟧
- [x] SKILL.md says a red baseline on the resume-rebased tip resets to `<pre-rebase-sha>` before the run bails ⟦criterion 2⟧
- [x] SKILL.md says a resume rebase that moved the branch is marked in the run log as its own event carrying the pre-rebase and rebased shas, under a name distinct from anything the Draft PR step's rebase records ⟦criterion 3⟧
- [x] fix the full-suite failure: no-sigpipe-pipelines.test.sh — FAIL - no suite under skills/tdd/scripts/tests/ that declares pipefail ends a pipeline in a reader that leaves before EOF (skill-preflight-launchable.test.sh:434 ends its pipeline in head -n 1) ⟦suite-repair⟧ ⟦criterion 3⟧
- [x] SKILL.md captures and resets a dirty resume worktree (a killed leaf's stray edit) before the resume rebase runs, and says `<pre-rebase-sha>` is `rebase-onto-default.sh`'s first stdout line before first using it; a case pins that order and goes red when the rebase is placed ahead of the capture-and-reset ⟦added⟧ ⟦criterion 4⟧
- [ ] The case pinning "never a bare force" goes red when that sentence's negation is removed (e.g. "It is a bare force"), whatever other negative words the sentence carries; watched red on that mutation first ⟦added⟧ ⟦criterion 5⟧
