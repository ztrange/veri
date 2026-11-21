# Plan for #4555 — A nothing-landed refactor leaves an earlier step's verdict-refactor.exit for rerecord-refactored to read

- [x] refactor-half.sh's nothing-landed skip writes `skipped` to `.tdd/verdict-refactor.exit`, replacing an earlier step's verdict, so rerecord-refactored reads this step's ⟦criterion 1⟧
