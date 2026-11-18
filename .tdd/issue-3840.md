# Plan for #3840 — Five scripts' SCRIPTS.md synopses list every argument they take, and their shim usage headers match the module

- [x] comment.sh's shim usage header names `[--pr]` as its module's USAGE does, and its SCRIPTS.md synopsis lists `[--pr]` after `[--note-file <path>]`, so the shim-usage audit passes with no comment.sh exemption ⟦criterion 1⟧
- [x] pin-reject-route.sh's shim usage header names the `--recheck <reason-file> <ledger-file> <matcher>` form as its module's USAGE does, and its SCRIPTS.md synopsis gives that form beside the first, so the audit passes with no pin-reject-route.sh exemption ⟦criterion 1⟧
- [x] role-state.sh's shim usage header names every `set` field and `request-reset [--idle]` as its module's USAGE does, so the audit passes with no role-state.sh exemption ⟦criterion 1⟧
- [ ] status.sh's shim usage header names `--report` and `--recover dev [--lane <lane>]` as its module's USAGE does, and its SCRIPTS.md synopsis lists `--recover dev [--lane <lane>]` beside `--report`, so the audit passes with no status.sh exemption ⟦criterion 1⟧
- [ ] stop-reason.sh's module USAGE holds the invocation only, its first-line description kept in the docstring, so the audit passes with EXEMPT empty ⟦criterion 1⟧
- [ ] SCRIPTS.md is graded against its rows, the new synopsis rows included, so prose-owed.sh exits 0 ⟦criterion 3⟧
