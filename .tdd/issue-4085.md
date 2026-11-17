# Plan for #4085 — PRD 016.3b: the CLAUDE.md tier lines are the only per-repo test-command declaration

- [x] in a repo whose only declaration is a .veri/test-command file, detect-test-command.sh --tier fast and --tier all print what inference finds, and exit 3 printing nothing when inference finds nothing; the cases that planted the file to pin the retired precedence plant none ⟦criterion 1⟧
- [x] a tree_audit case names the file and line of each tracked file outside specs/, .tdd/ and the TF1 cases that contains .veri/test-command ⟦criterion 3⟧
- [x] the detect-test-command.sh header, skills/tdd/SKILL.md (DT8), skills/tdd/SCRIPTS.md (SC36) and README.md (RD4) state the precedence without the file, graded, so the guard passes ⟦criterion 2⟧ ⟦criterion 5⟧ ⟦criterion 6⟧ ⟦criterion 7⟧
- [ ] the guard goes red when broken on purpose: the file named in a tracked file under skills/, then restored ⟦criterion 4⟧
