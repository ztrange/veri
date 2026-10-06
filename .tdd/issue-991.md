# Plan for #991 — skill-suite-runs.test.sh passes its \. section anchors through awk -v, which drops the backslash

- [x] skill-suite-runs.test.sh's `doc_text`, given a `from` regex `^5\. ` over a section holding the lines `5x y` and `5. y`, starts its output at `5. y`, not at `5x y` ⟦criterion 1⟧
- [x] skill-suite-runs.test.sh hands no `from` regex to awk through `-v`, so no backslash escape in it is processed by awk and gawk has no "escape sequence" warning to print on stderr ⟦diff-checked⟧ ⟦criterion 2⟧
