# Plan for #4643 — pin-recheck replays a pin whose old text moved to another package, not only another file of its directory

- [ ] A mutation pin whose old text is gone from its recorded file and from every file of its directory, and occurs in exactly one tracked file outside `.tdd/` in another directory, is replayed in that file: `pin-recheck.sh` exits 0 and leaves the `.tdd/pin-recheck-ok` receipt ⟦criterion 1⟧
- [ ] A mutation pin whose old text is in no tracked file outside `.tdd/` is not counted as checked: `pin-recheck.sh` prints `not checked: <file> (old text in no tracked file)`, exits 1 and leaves no receipt ⟦criterion 2⟧
- [ ] A mutation pin whose old text is in no file of its directory but in more than one tracked file outside `.tdd/` is not counted as checked: `pin-recheck.sh` prints `not checked: <file> (old text in more than one tracked file)`, mutates none of them, exits 1 and leaves no receipt ⟦criterion 3⟧
- [ ] SCRIPTS.md's pin-recheck **Moved** paragraph and row SC624 state the repository-wide fallback, regraded
