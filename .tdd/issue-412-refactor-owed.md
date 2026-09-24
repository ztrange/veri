### skills/solve-issue/ and skills/solve-issues/ are absent from the tree, and skill-identity.test.sh holds no case that reads a stub's frontmatter or requires a stub to exist ⟦criterion 1⟧
- drop the two stub paths from `exempt` and the comment on `stubs` that calls them forwarding stubs — owned by the next plan step (criterion 2), so out of this cycle's bounds
### skill-identity.test.sh's exempt no longer answers true for the two stub paths, and its old-home and old-command sweeps still fail a repository whose tracked file at one of those paths names the old home or invokes an old name ⟦criterion 2⟧
- case 2's exempt-filter loop could read from `offenders` rather than repeating the `while read … exempt` filter
- rename `stubs` (e.g. `former_stubs`) — the identifier now names files that no longer exist
