# Plan for #427 — preserve-attempt.sh builds a git ref name from the step's prose, so no attempt is ever preserved

- [x] The attempt ref name carries the step index read from the committed ledger rather than the step prose ⟦criterion 2⟧
- [x] A step whose title contains spaces, apostrophes or slashes has its attempt preserved under a ref name git accepts ⟦criterion 1⟧
- [ ] The leaf log and output copied beside the ref are named from that same index, so a title carrying a slash writes no nested path
- [ ] A preserve that fails for any other reason reports the failure on stderr instead of passing silently ⟦criterion 3⟧
