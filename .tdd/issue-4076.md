# Plan for #4076 — PRD 013.21: a park comment holds the whole question

- [x] park-issue.sh --question-file <path> puts the file's content, verbatim, in the parked comment ⟦criterion 1⟧
- [x] park-issue.sh --question-file exits 2 and writes nothing when the file lacks one of the four headings ⟦criterion 2⟧
- [x] a question file too long for one comment is cut to fit, and the comment says what was cut
- [x] a --question-file that is missing, repeated or unreadable exits 2 and writes nothing
- [ ] *The procedure* says a park on a still-unclear question passes --question-file, options with costs, Found holding the investigation ⟦criterion 3⟧
