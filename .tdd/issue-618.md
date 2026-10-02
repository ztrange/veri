# Plan for #618 — A launch supervise.sh refuses writes no completion file, so wait-leaf.sh answers "still running" forever

- [x] a launch refused because a leaf of the same name is alive writes no `.exit` for that name: `wait-leaf.sh <name>` keeps answering 3 while the live leaf runs, and the live leaf's own exit code is what lands in `.tdd/<name>.exit` when it finishes ⟦criterion 6⟧
- [x] when `supervise.sh` refuses a launch under a name different from the live leaf's, because the leaf recorded in `.tdd/leaf.owner` is alive, it exits 2 and `.tdd/<refused-name>.exit` holds `2` ⟦criterion 1⟧
- [x] after such a refusal, `wait-leaf.sh <refused-name>` exits 2, not 3 ⟦criterion 2⟧
- [x] a refused launch does not run its command and leaves `.tdd/leaf.owner` naming the live leaf, unchanged ⟦criterion 3⟧
- [x] a launch under a different name is not refused when the leaf recorded in `.tdd/leaf.owner` is alive but `.tdd/<owner-name>.exit` already exists: it runs its command and exits with that command's code ⟦criterion 4⟧
- [ ] a launch is still refused (exit 2, stderr naming the live leaf and its pid) when the recorded leaf is alive and `.tdd/<owner-name>.exit` does not exist ⟦criterion 5⟧
- [ ] the suites are green under `make test` ⟦full-suite⟧
