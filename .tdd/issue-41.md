# Plan for #41 — solvable-issues.sh: list the issues veri may take, in order — rung 2's selection layer

- [x] an open ready-for-agent issue whose Blocked by is None is listed, read from VERI_GH_JSON fixtures instead of gh
- [x] an issue whose Blocked by names an open issue is not listed; once that issue is closed it is
- [x] an issue without the ready-for-agent label is never listed, whatever its blockers
- [x] an issue that an open PR already Closes is not listed
- [ ] output is one number per line ascending, and no solvable issue means exit 3 and empty stdout
- [ ] without VERI_GH_JSON the script reads gh issue list and gh pr list itself, forwarding --repo when given
