# Plan for #1743 — requirements.sh: claims refuses every malformed table under a declared unit, as units already does

- [x] `claims <file> <unit>` on a unit whose table header is `| Requirement | ID |` (columns other than exactly `| ID | Requirement | Why |`) exits 2, prints nothing on stdout, and names the header's line number on stderr ⟦criterion 1⟧
- [x] `claims <file> <unit>` on a unit whose table has no leading pipes (`ID | Requirement | Why` header and rows) exits 2, prints nothing on stdout, and names the offending line number on stderr ⟦criterion 1⟧
- [x] `claims <file> <unit>` on a `## U` heading followed by prose and no table exits 2, prints nothing on stdout, and names the heading's line number on stderr, so a heading `units` does not list is never a silently empty unit for `claims` ⟦criterion 1⟧
- [x] `claims <file> <unit>` on a unit holding a second `| ID | Requirement | Why |` table after its first exits 2, prints nothing on stdout, and names the second table's header line number on stderr ⟦criterion 2⟧ ⟂ refactor pending
- [ ] `claims <file> <unit>` keeps an escaped `\|` inside a requirement cell: the row `| A1 | Pipes a \| b. | Why. |` prints `A1<TAB>Pipes a \| b.` (the whole requirement, not cut at the escaped pipe) ⟦criterion 2⟧
- [ ] `units <file>` on a missing file exits 2 with exactly one stderr line naming the file, and no Python traceback ⟦criterion 2⟧
