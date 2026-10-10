# Plan for #1421 — develop-exhausted leaf reverts the attempt's uncommitted test and answers neither split nor park on a claim it did not check under the test command

- [x] `build-develop-prompt.sh exhausted` prints a prompt that tells the leaf not to modify, revert or remove anything in the working tree ⟦criterion 1⟧ ⟂ refactor pending
- [ ] the `exhausted` prompt tells the leaf that any statement that the criterion already holds must cite a run of the test command it was given ⟦criterion 2⟧
