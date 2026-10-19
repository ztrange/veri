# Plan for #1743 — requirements.sh: claims refuses every malformed table under a declared unit, as units already does

- [x] claims on a unit whose first `|`-line is the header `| Key | Value |` exits 2, prints nothing on stdout and names that header line on stderr ⟦criterion 1⟧
- [x] claims on a unit whose header is `| ID | Requirement | Why | Extra |` exits 2, prints nothing on stdout and names that header line on stderr ⟦criterion 1⟧
- [x] claims on a unit with a later `| A | B |` line after its table (separated by a non-`|` line) exits 2, prints nothing on stdout and names that later line on stderr ⟦criterion 1⟧
- [x] claims on a unit with a second `| ID | Requirement | Why |` table after a blank line exits 2, prints nothing on stdout and names the second table's header line on stderr ⟦criterion 3⟧
- [x] claims accepts a fenced code block holding `ls | grep x` after the unit's table: exits 0 and prints only the table's rows ⟦criterion 1⟧
- [x] claims accepts a fenced code block after the unit's table holding a line that starts with `|`: exits 0 and prints only the table's rows, the fenced line never read as a table line ⟦criterion 1⟧
- [x] claims accepts a prose line `a | b` after the unit's table: exits 0 and prints only the table's rows ⟦criterion 1⟧
- [x] claims on a heading whose only table is `Key | Value` without leading pipes (no `|`-line under it) exits 2, prints nothing on stdout and names the heading line on stderr ⟦criterion 1⟧
- [x] an escaped `\|` inside a requirement cell stays inside it: claims prints the whole requirement with the pipe ⟦criterion 3⟧
- [x] units on a missing file exits 2 with exactly one stderr line naming the file and no traceback ⟦criterion 3⟧
- [x] units prints exactly the headings for which claims exits 0, pinned by one case running both commands over one file holding a valid unit and every malformed shape: headers `| Requirement | ID |`, `| Why | ID |`, `| Key | Requirement |`, `| Key | Value |`, `| ID | Requirement | Why | Extra |`, a table without leading pipes, a heading with prose and no table, a later `| A | B |` line, a second table ⟦criterion 2⟧ ⟂ refactor pending
