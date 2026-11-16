# Plan for #3982 — PRD 021.16: a tag that failed to publish is not left behind

- [x] when git push origin <tag> fails, queued-merge.sh deletes the local tag, stderr saying it was cut, not published, and removed, and exits 2 naming tag ⟦criterion 1⟧
- [x] when the git tag -d also fails, stderr names it and the exit stays 2 ⟦criterion 2⟧
- [x] the queued-merge.sh entry of SCRIPTS.md states both (SC159) ⟦criterion 3⟧
