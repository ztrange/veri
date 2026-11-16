# Plan for #4169 — PRD 034.1a: a repository can name a stack branch, and /vinstall asks for one

- [x] stack-branch.sh prints the branch a `veri: stack branch: <name>` CLAUDE.md line names and exits 0; with no such line or no CLAUDE.md it prints nothing and exits 3; with no argument it reads the current directory's CLAUDE.md, given a repo-root that one's ⟦criterion 1⟧
- [x] it exits 2, stderr naming the line, when the named branch is empty ⟦criterion 2⟧
- [x] it exits 2, stderr naming the line, when the named branch is the repository's default branch ⟦criterion 2⟧
- [x] it exits 2, stderr naming the line, when `git check-ref-format --branch` refuses the name ⟦criterion 2⟧
- [x] stack-branch.sh is a /bin/sh shim over veri/stack_branch.py, its entry-point contract pinned by a process case ⟦criterion 3⟧
- [x] veri/README.md's module index lists stack_branch.py ⟦criterion 4⟧
- [x] SCRIPTS.md lists stack-branch.sh with its output and exit codes (SC195), graded ⟦criterion 5⟧
- [x] /vinstall asks for a stack branch during setup and writes the line on a name (VI5), graded ⟦criterion 6⟧
