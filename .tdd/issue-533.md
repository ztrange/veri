# Plan for #533 — walkthrough: a fast docs case catches a commentary chunk that outruns its script

- [ ] commentary-figures.test.sh fails, naming the script, the chunk's range and the script's line count, when a chunk in docs/wt/commentary.py claims a line past the end of its script (compared as text, no page build) ⟦criterion 1⟧
- [ ] On the real tree the chunk-range case passes ⟦full-suite⟧ ⟦criterion 2⟧
