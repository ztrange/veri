# Plan for #4011 — PRD 024.5: developer and verifier leaves launch with one tool list

- [x] the write-ban hook command, given a `Write`, `Edit`, `MultiEdit` or `NotebookEdit` call on stdin, exits 2 with a line saying the verifier may not modify files, and exits 0 for a `Bash` or `Read` call ⟦criterion 3⟧
- [x] a `verify-*` leaf's `--settings` carries a `PreToolUse` hook matching `Write|Edit|MultiEdit|NotebookEdit` whose command is the write ban, in the one `--settings` run-leaf.sh passes; a `develop-*` or `revise-*` leaf's carries none ⟦criterion 2⟧
- [x] a `verify-*` leaf's argv carries the `--tools` value a `develop-*` leaf gets and no `--disallowedTools` ⟦criterion 1⟧
- [ ] a verifier that changes the tree through `Bash` is still restored, relaunched and refused ⟦criterion 4⟧
- [ ] with `VERIFY_LEAF_ARGS` set, the verifier's default arguments are replaced by it ⟦criterion 5⟧
- [ ] `SCRIPTS.md`'s `verify.sh` entry states the hook ⟦criterion 6⟧
