# Plan for #3968 — PRD 022.18: a token-shaped string never reaches an issue or PR body veri writes

- [x] gh_issue_create hands gh the title and the body redacted ⟦criterion 1⟧
- [x] gh_issue_edit hands gh a body file whose contents are redacted, the caller's file left as it was ⟦criterion 2⟧
- [x] pr-body.sh hands gh the body it writes redacted ⟦criterion 3⟧
- [ ] the pr-body.sh entry of SCRIPTS.md says the body is redacted ⟦criterion 4⟧
