# Plan for #4078 — PRD 013.17: a pointer comment says where a run is

- [ ] `pointer-comment.sh <n>` posts one `### 📍 Run state` comment when the issue has none and edits it in place otherwise, so two calls leave exactly one ⟦criterion 1⟧
- [ ] the pointer comment states the branch, the PR URL or `none`, and the resume command `$S/run-conductor.sh <n>` ⟦criterion 2⟧
- [ ] the pointer comment states the step as `k/n` from the ledger and the phase of the issue's last journal event that names one ⟦criterion 2⟧
- [ ] the pointer comment states the last push time, ISO-8601 with offset, kept from the previous comment when the caller pushed nothing ⟦criterion 2⟧
- [ ] `VERI_MACHINE_NAME` is a `TUNABLES` entry parsed by `text`, default empty ⟦criterion 4⟧
- [ ] the pointer comment states the machine as `VERI_MACHINE_NAME`, or what `hostname -s` prints when that is unset or empty ⟦criterion 3⟧
- [ ] `unlabel-issue.sh <n>` writes the pointer comment after taking the claim ⟦criterion 5⟧
- [ ] `push-branch.sh` updates the pointer comment after a push that exits 0 with the branch pushed, and not after a failed one ⟦criterion 6⟧
- [ ] a `gh` failure writing the pointer comment is one stderr line naming the issue, and `unlabel-issue.sh` and `push-branch.sh` keep their exit codes ⟦criterion 7⟧
