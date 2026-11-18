# Plan for #3839 — parallel-conductors.sh refuses any argument but --continue-on-bail, and no longer documents --repo

- [x] parallel-conductors.sh given any argument list other than none or the single `--continue-on-bail` (`--repo o/r --continue-on-bail` among them) exits 2 with its usage line on stderr and launches no conductor ⟦criterion 1⟧
- [ ] `parallel-conductors.sh --help` prints a usage line naming `[--continue-on-bail]` and no `--repo`, and the shim's `# Usage:` header agrees with it ⟦criterion 2⟧
- [ ] `skills/tdd/SCOPE-LOOP.md` names the invocation as `$S/parallel-conductors.sh [--continue-on-bail]`, its SL12 row reworded and the file regraded ⟦criterion 3⟧
