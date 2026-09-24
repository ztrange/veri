# Plan for #412 — Remove the solve-issue / solve-issues forwarding stubs and the exemptions the identity sweeps carry for them

- [ ] skills/solve-issue/ and skills/solve-issues/ are absent from the tree, and skill-identity.test.sh holds no case that reads a stub's frontmatter or requires a stub to exist ⟦criterion 1⟧
- [ ] skill-identity.test.sh's exempt no longer answers true for the two stub paths, and its old-home and old-command sweeps still fail a repository whose tracked file at one of those paths names the old home or invokes an old name ⟦criterion 2⟧
- [ ] a file under .tdd/ that names the old home as a path or invokes an old name as a command still passes both skill-identity sweeps ⟦criterion 3⟧
- [ ] both skill-identity sweeps pass with docs/adr/0013-issue-branch-in-its-own-worktree.md line 18 naming ~/.claude/skills/solve-issue as a path, unedited ⟦criterion 4⟧
- [ ] README.md's install step symlinks skills/tdd alone and no longer tells a new clone to symlink the two old names ⟦criterion 5⟧
- [ ] CLAUDE.md's opening paragraph names skills/tdd/ as the product rather than skills/solve-issue/ ⟦criterion 6⟧
- [ ] claude-md-counts.test.sh passes with CLAUDE.md's stated script and suite counts unchanged once the stubs are gone ⟦criterion 7⟧
