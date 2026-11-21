# Plan for #4550 — same-reject.sh exits 2 on every reason file parse-verdict.sh writes, so the same-reject shortcut never fires

- [x] same-reject.sh exits 0 for two identical reason files with no `REASON:` prefix, the format parse-verdict.sh writes ⟦criterion 1⟧
- [ ] same-reject.sh exits 1 for two such files whose reasons differ ⟦criterion 2⟧
