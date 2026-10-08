# Plan for #873 — A verifier's mutate-and-revert can leave a stale .pyc that turns the next run of a Python module red

- [x] Under a leaf launched by run-leaf.sh, a Python module mutated and reverted at the same whole-second mtime and the same byte size is re-read from source on its next import: the reverted module answers as it did before the mutation ⟦criterion 1⟧ ⟂ refactor pending
- [ ] run-leaf.sh hands the leaf PYTHONDONTWRITEBYTECODE=1 whatever its own environment carries: unset, set to 0, or set to the empty string ⟦criterion 2⟧
- [ ] A Python process started under a leaf launched by run-leaf.sh writes no .pyc file into the directory tree it imports from ⟦criterion 3⟧
- [ ] Guard: with PYTHONDONTWRITEBYTECODE removed from the leaf's environment, the case pinning criterion 1 goes red — watched red, then put back ⟦human-owed⟧ ⟦criterion 4⟧
