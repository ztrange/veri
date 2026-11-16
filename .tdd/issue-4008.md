# Plan for #4008 — PRD 024.9: verify-green names the check a REJECT failed

- [x] a green `verdict` event carries `check=<n>` for a `CHECK: <n>` line with n 1 to 5, no `check` field for an absent or other value, the verdict and exit code unchanged ⟦criterion 1⟧
- [x] the reason verify.sh prints for a green verdict holds no `CHECK:` line ⟦criterion 2⟧
- [x] the `#### Green rejects` table has a `check` column, empty for an event with no `check` field ⟦criterion 3⟧
- [x] under the table, a line `Green rejects by check: <n> <count>, …, unnamed <count>` ⟦criterion 3⟧
- [x] `prompts/verify-green.md` tells the verifier, on a REJECT, to put one `CHECK: <n>` line before `VERDICT:`, the lowest-numbered failed check ⟦criterion 4⟧
