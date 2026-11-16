# Plan for #3932 — PRD 023.11: a skill-reader audit goes red when a reader is lost

- [x] `subsection_readers.lost_cases` names an allowed entry whose reading line was removed from a planted index, and every allowed entry when the index holds no reader ⟦criterion 1⟧
- [ ] every reader audit fails naming each lost allow-list entry, and the committed allow-lists hold no entry that does not read its subsection ⟦criterion 2⟧ ⟦criterion 3⟧
