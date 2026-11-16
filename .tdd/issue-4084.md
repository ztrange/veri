# Plan for #4084 — PRD 016.3a: /vinstall proposes the test commands and opens a PR that records them

- [x] record-test-commands.sh pushes a branch veri-install, cut from the default branch's tip, whose one commit changes only CLAUDE.md (created when absent), and on it detect-test-command.sh --tier fast and --tier all print the two commands exactly ⟦criterion 1⟧
- [x] an existing veri: fast tests: or veri: all tests: line is replaced where it stands, never duplicated, every other line byte-for-byte unchanged ⟦criterion 2⟧
- [ ] gh_pr_create opens a pull request from a head against a base through gh's REST route and answers its URL ⟦criterion 3⟧
- [ ] record-test-commands.sh opens the PR from veri-install against the default branch, prints its URL, exits 0, never merges, and leaves the checkout's branch, index and working tree as they were ⟦criterion 3⟧
- [ ] a default-branch tip already declaring both commands exactly is exit 3 with no branch or PR ⟦criterion 4⟧
- [ ] an origin already holding veri-install is exit 2 naming it on stderr, nothing written ⟦criterion 5⟧
- [ ] a missing or empty command argument, or a repo-root outside a git repository, is exit 2 with nothing written ⟦criterion 5⟧
- [ ] the record-test-commands.sh shim execs its module: an empty command through the shim is exit 2 ⟦criterion 6⟧
- [ ] skills/vinstall/SKILL.md gains ## Recording the test commands, graded ⟦criterion 7⟧
