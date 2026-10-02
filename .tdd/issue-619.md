# Plan for #619 — Leaves restore a mutation with git checkout, wiping the step's uncommitted work

- [x] verify-green.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧
- [x] verify-pin.md tells the verifier to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧
- [x] develop-cover.md tells the cover leaf to run `cp <file> <file>.orig` before it mutates the code and `mv <file>.orig <file>` after the run under mutation ⟦criterion 1⟧
- [x] verify-green.md, verify-pin.md and develop-cover.md each confirm the restore by comparing `git diff` with what it printed before the probe, and none of them contains `git checkout --` or `git diff --exit-code` ⟦criterion 2⟧
- [x] _shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧
- [x] _develop-shared.md forbids `git checkout -- <file>` and `git restore` for undoing a probe and names `cp <file> <file>.orig` / `mv <file>.orig <file>` as the restore to use instead ⟦criterion 3⟧
- [x] _shared.md and _develop-shared.md still carry their "Never run `git stash`" rule unchanged and still recommend `git show HEAD:<path>` and `git worktree add --detach <scratch> HEAD` for reading the committed version ⟦criterion 4⟧
- [x] no file under skills/tdd/scripts/prompts/ contains `git stash push`, and `git checkout -- <file>` appears only in `_shared.md` and `_develop-shared.md`, inside the sentence that forbids it (criterion 3) — no prompt prescribes it as a restore ⟦criterion 5⟧
- [ ] verify-green.md check 4 and verify-pin.md check 2 still require the restore to happen before the verifier reports, and develop-cover.md step 4 still requires the working tree to be exactly as the leaf found it ⟦criterion 6⟧
