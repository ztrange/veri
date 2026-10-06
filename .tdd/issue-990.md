# Plan for #990 — affected-suites.sh answers for the working tree, so a red or green leaf asks without building a commit, stash or worktree

- [x] `affected-suites.sh <base>` (one revision, no `..`) with an uncommitted edit to a script prints that script's suite, exits 0, and leaves `git stash list`, `git worktree list` and `HEAD` exactly as they were ⟦criterion 1⟧
- [x] `affected-suites.sh <base>` with a new, untracked `skills/tdd/scripts/tests/<name>.test.sh` prints that suite ⟦criterion 2⟧
- [x] `affected-suites.sh <base>` with a new, untracked suite also prints `claude-md-counts.test.sh`, as the `<base>..<head>` form does for a committed added suite
- [x] `affected-suites.sh <base>` with no committed and no uncommitted change since `<base>` exits 3 and prints nothing ⟦criterion 3⟧
- [x] `affected-suites.sh <base>` with an unresolvable `<base>` exits 2 with a diagnostic on stderr and nothing on stdout ⟦criterion 4⟧
- [ ] `affected-suites.sh <base>..<head>` prints what it printed before, for the existing cases in its suites ⟦full-suite⟧ ⟦criterion 5⟧
- [ ] `prompts/develop-red.md` spells the working-tree call `affected-suites.sh HEAD`, pinned as text in the style of the existing prompt suites ⟦criterion 6⟧
- [ ] `prompts/develop-green.md` spells the working-tree call `affected-suites.sh HEAD`, pinned as text in the style of the existing prompt suites ⟦criterion 6⟧
- [ ] `prompts/develop-revise.md` spells the working-tree call `affected-suites.sh HEAD`, pinned as text in the style of the existing prompt suites ⟦criterion 6⟧
