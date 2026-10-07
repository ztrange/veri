# Plan for #1138 — affected-suites.sh lists suites the base added after the branch point, including ones that do not exist on the branch

- [x] on a branch whose base gains a test suite after the branch point, `affected-suites.sh <base>..HEAD` does not print the base's new suite, only the suites for the branch's own changes ⟦criterion 2⟧
- [x] a non-suite file `<base>` changed or deleted after the branch point contributes no suite to `affected-suites.sh <base>..HEAD`: only the suites of files the branch itself changed since the merge base are printed ⟦criterion 1⟧
- [x] a suite `<base>` added or deleted after the branch point does not make `affected-suites.sh <base>..HEAD` print `claude-md-counts.test.sh` when the branch itself added or deleted no suite or script ⟦criterion 1⟧
- [x] a suite the branch itself deleted is not printed by `affected-suites.sh <base>..HEAD`: no printed suite path is one that does not exist at `<head>` ⟦criterion 1⟧
