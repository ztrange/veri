# Plan for #487 — affected-suites.sh maps a lib file to no suite when its caller's source line ends in a continuation

- [x] A lib file whose caller's `source` line ends in a `\` continuation maps to that caller's suite ⟦criterion 1⟧
- [x] A caller whose `source` line ends at the lib path, with or without a trailing quote and trailing spaces, still maps to its suite ⟦criterion 2⟧
- [x] A comment line that names a lib file is still not a dependency: the commenting script's suite is not selected ⟦criterion 3⟧
- [x] In the real repo, a change to `lib/bug-section.sh` selects both `build-develop-prompt.test.sh` and `build-verify-prompt.test.sh` ⟦criterion 4⟧
- [x] Repair: `no-nested-suites.test.sh` is green again — `affected-suites.test.sh` names no real suite file in a shape that guard reads as launching it, while criterion 4 stays pinned ⟦added⟧ ⟦criterion 4⟧
