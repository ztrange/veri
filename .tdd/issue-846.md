# Plan for #846 — make test is red under uid 0: status.test.sh relies on chmod 000, which root bypasses

- [ ] status.test.sh's "exits 2 on a failure veri/status.py turns into exit 2" case forces the ledger read to fail by a means permission bits play no part in (e.g. `$run/.tdd/issue-9.md` made a directory, so the read raises IsADirectoryError), with no `chmod` and no skip when `$EUID` is 0, and asserts exit 2 with a non-empty stderr instead of the literal `PermissionError` ⟦criterion 1⟧
- [ ] A guard suite fails the run naming `<suite>:<line>` for a suite that forces a read or write failure through permission bits by `chmod 000`, `chmod a-r`, `chmod u-w` or `chmod -w`, and passes on today's tree ⟦criterion 2⟧
- [ ] The guard also fails naming `<suite>:<line>` for a suite that makes a directory read-only to force a write failure into it ⟦criterion 2⟧
- [ ] A line the guard's exemption table lists, with a reason, is not reported, and an exemption entry carrying no reason fails the guard ⟦criterion 2⟧
- [ ] Planting a permission-bit offender into a suite turns the guard red naming the planted `<suite>:<line>`, and removing the plant turns it green again ⟦criterion 2⟧
- [ ] CLAUDE.md's "Testing idiom" section, next to the SIGPIPE and job-spec rules, states that no suite relies on permission bits to make a path unreadable or unwritable, because the cloud runs as root and permission bits are a no-op there ⟦criterion 3⟧
- [ ] status.test.sh passes when run as uid 0, its exit-2 case included ⟦human-owed⟧ ⟦criterion 1⟧
- [ ] make test is green on the branch with the guard in it ⟦full-suite⟧ ⟦criterion 2⟧
