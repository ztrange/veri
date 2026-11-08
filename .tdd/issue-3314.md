# Plan for #3314 — add-ledger-step.sh accepts step text containing the refactor-pending delimiter, which ledger-growth.sh then reads as a mark

- [x] add-ledger-step.sh <ledger> after <anchor> with one text holding the refactor-pending delimiter (space, U+27C2, space) exits 2, its stderr names that token, and the ledger file is byte-identical to before ⟦criterion 1⟧ ⟂ refactor pending
- [ ] a batch of several texts, one of which holds the refactor-pending delimiter (space, U+27C2, space), exits 2 and inserts none of them: the ledger file is byte-identical to before ⟦criterion 2⟧
- [ ] texts without the refactor-pending delimiter are still inserted with exit 0, each carrying ⟦added⟧, and ledger-growth.sh counts them as added steps as before ⟦criterion 3⟧
- [ ] Go-red: with the refusal removed, the first criterion's case fails (the script exits 0 and rewrites the ledger) ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] skills/tdd/SCRIPTS.md's add-ledger-step.sh entry states the refusal of a text holding the refactor-pending delimiter (exit 2, naming the token, ledger untouched) ⟦skill-edit⟧ ⟦criterion 5⟧
