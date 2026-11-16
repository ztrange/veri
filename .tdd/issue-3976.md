# Plan for #3976 — PRD 022.5: a leaf's environment holds only named variables

- [x] `launch_spec` returns an env holding only allow-listed names (prefixes `VERI_`, `LC_`) and the names it sets itself: `GH_TOKEN`, `GITHUB_TOKEN`, `AWS_SECRET_ACCESS_KEY`, `SOME_UNLISTED` absent, every allow-listed name present ⟦criterion 1⟧
- [x] `VERI_LEAF_ENV` (a tunable, default empty) adds space-separated names: `JAVA_HOME` passes, `GH_TOKEN` still does not ⟦criterion 2⟧
- [x] a name `VERI_LEAF_ENV` adds that `VERI_REDACT_VARS` also names passes, and `run-leaf.sh` prints one stderr line naming it, never its value ⟦criterion 4⟧
- [x] a ratchet case fails when a veri module or the Makefile reads, by literal name, an environment variable the allow-list does not pass and no exemption names
- [ ] today's `launch_spec` cases stay green: set names keep their values, session stripping unchanged ⟦criterion 3⟧
- [ ] the `run-leaf.sh` entry of `skills/tdd/SCRIPTS.md` lists the allow-list and `VERI_LEAF_ENV`, graded ⟦criterion 5⟧
