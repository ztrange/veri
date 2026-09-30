# Plan for #591 — solvable-issues, workqueue, invisible-work and wait-ci pass GitHub JSON through argv, over Linux's 128 KiB per-argument limit

- [x] solvable-issues.sh prints the same numbers and exits 0 for a VERI_GH_JSON fixture whose issues.json is larger than 256 KiB as for the same issues with short bodies, and no argument it hands python3 carries the JSON document ⟦criterion 1⟧
- [x] workqueue.sh reads an issues document larger than 256 KiB and gives the same output and exit code as for a small one, and no argument it hands python3 carries the JSON document ⟦criterion 2⟧
- [x] invisible-work.sh reads issues and PR documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧ ⟂ refactor pending
- [ ] wait-ci.sh reads check-run and status documents larger than 256 KiB and gives the same output and exit code as for small ones, and no argument it hands python3 carries a JSON document ⟦criterion 2⟧
- [ ] a suite fails naming <file>:<line> when a script under skills/tdd/scripts/ passes a variable holding a gh JSON document as an argument to python3, against an exemption table carrying a reason per entry ⟦criterion 3⟧
- [ ] CI (Linux) stays green ⟦full-suite⟧ ⟦criterion 4⟧
