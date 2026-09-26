# Plan for #484 — next-unchecked.sh skips a ledger line that merely quotes ⟦full-suite⟧ or ⟦human-owed⟧

- [x] next-unchecked.sh prints an unchecked ledger line whose text quotes the full-suite or the human-owed marker mid-sentence, rather than skipping it ⟦criterion 2⟧
- [x] next-unchecked.sh still skips an unchecked ledger line carrying the full-suite or the human-owed marker in the written position, immediately before its criterion mark ⟦criterion 1⟧
- [x] next-unchecked.sh skips a line that carries a marker in the written position and also quotes one elsewhere in its text ⟦criterion 3⟧
- [x] next-unchecked.sh still prints the first unchecked line and exits 3 with no output when no unchecked line remains ⟦criterion 4⟧
