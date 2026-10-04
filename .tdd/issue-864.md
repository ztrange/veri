# Plan for #864 — preflight checks GitHub with gh auth status, which fails in cloud sessions, and the conductor ignores the failure

- [x] SKILL.md preflight step 0.2 names `gh api user` as the GitHub check, and says a non-zero exit from it stops the run as a preflight failure ⟦criterion 1⟧ ⟂ refactor pending
- [ ] a suite fails naming `<file>:<line>` when a `gh auth status` call is planted in skills/tdd/SKILL.md or in a skills/tdd/scripts/*.sh, and passes on a tree holding none ⟦criterion 2⟧
- [ ] the `claude auth status` half of step 0.2 and the `leaf-launchable.sh` check that follows it are unchanged on this branch ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] no assertion of an existing SKILL.md prose suite or of `no-graphql-gh-calls.test.sh` is changed on this branch ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] every case the existing SKILL.md prose suites and `no-graphql-gh-calls.test.sh` hold passes ⟦full-suite⟧ ⟦criterion 4⟧
