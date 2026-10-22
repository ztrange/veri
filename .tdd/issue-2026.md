# Plan for #2026 — The requirements reader splits a cell on a | inside backticks, so P7 reaches the grader truncated

- [x] A requirement cell holding a backtick code span with `|` characters inside it (such as `` `| total |` ``) is read whole: `requirements.claims()` returns the full cell text as that row's claim, e.g. P7's ``A cost is read from a report's `| total |` row, never by summing phase rows.`` (small in-process unit case) ⟦criterion 1⟧
- [x] A `|` outside any code span still separates cells: in a row whose Requirement cell holds a code span with a `|` inside, the `|` after that cell still ends it, so the claim excludes the Why cell's text (small in-process unit case) ⟦criterion 2⟧
- [ ] An escaped `\|` outside a code span in a requirement cell is read as a literal pipe, as GFM renders it: the claim carries `|`, not `\|`, and the cell is not split there (small in-process unit case) ⟦criterion 2⟧
